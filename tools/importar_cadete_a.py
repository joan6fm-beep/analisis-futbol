"""Importa las actas del Cadete A (Lliga Autonòmica Cadet) y genera los CSV de la app.

Fuente única: futbol_streamlit/data/cadete_a/fuente/actas.txt (transcripción de la app FFCV)
             futbol_streamlit/data/cadete_a/fuente/resultados.txt (partidos con resultado sin acta)
             futbol_streamlit/data/cadete_a/fuente/clasificacion_oficial.txt (clasificación publicada)
Salida (data/cadete_a/): partidos.csv, alineaciones.csv, eventos.csv, minutos.csv,
                         plantillas.csv, equipos.csv, avisos.csv, clasificacion_oficial.csv

Para añadir una jornada: transcribir sus actas en actas.txt y ejecutar
    python tools/importar_cadete_a.py
Todos los apartados de la app se recalculan desde estos CSV (no hay cifras duplicadas a mano).
"""
from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "futbol_streamlit"
sys.path.insert(0, str(APP))
import league_core as lc  # noqa: E402

DIR = APP / "data" / "cadete_a"
SRC = DIR / "fuente"
MATCH_MINUTES = 80
TEAM = "Primer Toque C.F. 'A'"
LINE = {"POR": 1, "DEF": 2, "MED": 3, "DEL": 4, "SUP": 5, "SUPPOR": 5}
EVENT_TYPES = {"cambio", "gol", "penalti", "propia", "amarilla", "segunda_amarilla", "roja",
               "amarilla_tecnico", "roja_tecnico"}
TYPE_OUT = {"gol": "gol", "penalti": "penalti_gol", "propia": "gol_propia", "amarilla": "amarilla",
            "segunda_amarilla": "segunda_amarilla", "roja": "roja", "cambio": "cambio",
            "amarilla_tecnico": "amarilla_tecnico", "roja_tecnico": "roja_tecnico"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s).strip()


@dataclass
class Player:
    side: str
    rol: str
    dorsal: int
    nombre: str
    orden: int


@dataclass
class Match:
    jornada: int
    fecha: str
    hora: str
    local: str
    visitante: str
    gl: int
    gv: int
    campo: str
    sis_l: str
    sis_v: str
    line_no: int
    acta: bool = True
    players: list[Player] = field(default_factory=list)
    events: list[tuple] = field(default_factory=list)   # (side, minuto, tipo, texto, line_no)
    notas: list[str] = field(default_factory=list)

    def team(self, side):
        return self.local if side == "L" else self.visitante


def parse(path: Path) -> list[Match]:
    matches: list[Match] = []
    cur: Match | None = None
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("PARTIDO "):
            p = [x.strip() for x in line[len("PARTIDO "):].split("|")]
            j = int(p[0].lstrip("J"))
            fh = p[1].split()
            gl, gv = (int(x) for x in p[4].split("-"))
            cur = Match(j, fh[0] if fh else "", fh[1] if len(fh) > 1 else "", p[2], p[3], gl, gv, p[5],
                        p[6] if len(p) > 6 else "", p[7] if len(p) > 7 else "", n)
            matches.append(cur)
            continue
        if cur is None:
            raise ValueError(f"Línea {n}: dato fuera de un PARTIDO")
        if line == "SIN_ACTA":
            cur.acta = False
        elif line.startswith("NOTA "):
            cur.notas.append(line[5:])
        elif line.startswith("EV "):
            m = re.match(r"EV ([LV]) (\d+) (\w+) (.+)$", line)
            if not m or m.group(3) not in EVENT_TYPES:
                raise ValueError(f"Línea {n}: evento no válido: {line}")
            cur.events.append((m.group(1), int(m.group(2)), m.group(3), m.group(4).strip(), n))
        else:
            m = re.match(r"([LV]) (POR|DEF|MED|DEL|SUP|SUPPOR) (\d+) (.+)$", line)
            if not m:
                raise ValueError(f"Línea {n}: línea no reconocida: {line}")
            side = m.group(1)
            orden = sum(1 for p in cur.players if p.side == side) + 1
            cur.players.append(Player(side, m.group(2), int(m.group(3)), m.group(4).strip(), orden))
    return matches


def candidates(abbr: str, pool: list[Player]) -> list[Player]:
    """Jugadores que encajan con «X. Apellido» (o un nombre completo / único)."""
    a = norm(abbr)
    exact = [p for p in pool if norm(p.nombre) == a]
    if exact:
        return exact
    m = re.match(r"^([a-z])\s+(.+)$", a)
    if not m:  # un solo nombre (p. ej. «Velasco»)
        return [p for p in pool if a in norm(p.nombre).split() or norm(p.nombre).startswith(a)]
    ini, rest = m.group(1), m.group(2).split()
    out = []
    exact_tok = [p for p in pool if norm(p.nombre).split()[0][0] == ini
                 and any(norm(p.nombre).split()[1:][i:i + len(rest)] == rest for i in range(len(norm(p.nombre).split())))]
    if exact_tok:  # «A. Da» → apellido exacto «Da» antes que prefijos como «Adan»
        return exact_tok
    for p in pool:
        toks = norm(p.nombre).split()
        if not toks or toks[0][0] != ini:
            continue
        tail = toks[1:]
        # «A. De» → partícula: coincide con el primer apellido que empieza por ella; se exige la secuencia
        for i in range(len(tail)):
            if tail[i:i + len(rest)] == rest or (len(rest) == 1 and tail[i].startswith(rest[0]) and len(rest[0]) >= 3):
                out.append(p)
                break
        else:
            # nombres compuestos con guion: «X. Nieto-Guerrero»
            if " ".join(rest) in " ".join(tail):
                out.append(p)
    return out


def process(m: Match, avisos: list[dict]):
    def warn(kind, msg, line=None):
        avisos.append(dict(jornada=m.jornada, partido=f"{m.local} - {m.visitante}", tipo=kind, detalle=msg,
                           linea=line or m.line_no))

    al_rows, ev_rows = [], []
    if not m.acta:
        return al_rows, ev_rows, set()
    for side in "LV":
        pl = [p for p in m.players if p.side == side]
        starters = [p for p in pl if p.rol in ("POR", "DEF", "MED", "DEL")]
        if len(starters) != 11:
            warn("titulares", f"{m.team(side)}: {len(starters)} titulares")
        if sum(p.rol == "POR" for p in starters) != 1:
            warn("portero", f"{m.team(side)}: portero titular no único")
        sis = m.sis_l if side == "L" else m.sis_v
        if sis:
            parts = [int(x) for x in sis.split("-")[1:]]
            got = [sum(p.rol == r for p in starters) for r in ("DEF", "MED", "DEL")]
            if len(parts) == 3 and parts != got:
                warn("sistema", f"{m.team(side)}: sistema {sis} y líneas {got}")
        dorsales = [p.dorsal for p in pl]
        if len(set(dorsales)) != len(dorsales):
            warn("dorsal", f"{m.team(side)}: dorsal repetido")
        for p in pl:
            rol = "SUP_POR" if p.rol == "SUPPOR" else p.rol
            al_rows.append(dict(equipo=m.team(side), jornada=m.jornada, dorsal=p.dorsal, jugador=p.nombre, rol=rol,
                                linea=LINE[p.rol], orden=p.orden))
    on_field = {s: {p.nombre for p in m.players if p.side == s and p.rol in ("POR", "DEF", "MED", "DEL")} for s in "LV"}
    entered: dict[str, set] = {"L": set(), "V": set()}
    ambiguous: set[str] = set()
    goals = {"L": 0, "V": 0}
    for side, minute, tipo, txt, ln in sorted(m.events, key=lambda e: (e[1], e[2] != "cambio")):
        team = m.team(side)
        rival = m.team("V" if side == "L" else "L")
        pool = [p for p in m.players if p.side == side]
        if tipo.endswith("_tecnico"):
            ev_rows.append(dict(jornada=m.jornada, equipo=team, minuto=minute, tipo=TYPE_OUT[tipo], jugador=txt,
                                detalle=f"cuerpo técnico;rival={rival}"))
            continue
        if tipo == "cambio":
            inn_txt, out_txt = (x.strip() for x in txt.split(">"))
            subs = [p for p in pool if p.rol in ("SUP", "SUPPOR") and p.nombre not in entered[side]]
            ci = candidates(inn_txt, subs) or candidates(inn_txt, pool)
            co_field = [p for p in pool if p.nombre in on_field[side]]
            co = candidates(out_txt, co_field)
            if len(ci) != 1:
                warn("nombre", f"{minute}' entra «{inn_txt}»: {len(ci)} candidatos", ln)
            inn = ci[0].nombre if len(ci) == 1 else f"{inn_txt} (sin identificar)"
            if len(co) == 1:
                out = co[0].nombre
                on_field[side].discard(out)
                det = f"sale={out}"
            else:
                out = f"{out_txt} (sin identificar)"
                det = f"sale={out}"
                if len(co) > 1:
                    ambiguous.update(p.nombre for p in co)
                    det += ";candidatos=" + "|".join(p.nombre for p in co)
                    warn("ambiguo", f"{minute}' sale «{out_txt}»: puede ser {', '.join(p.nombre for p in co)}", ln)
                else:
                    warn("nombre", f"{minute}' sale «{out_txt}»: no estaba en el campo", ln)
            if len(ci) == 1:
                on_field[side].add(inn)
                entered[side].add(inn)
            ev_rows.append(dict(jornada=m.jornada, equipo=team, minuto=minute, tipo="cambio", jugador=inn, detalle=f"{det};rival={rival}"))
            continue
        cands = candidates(txt, [p for p in pool if p.nombre in on_field[side]]) or candidates(txt, pool)
        if len(cands) == 1:
            name = cands[0].nombre
        else:
            name = f"{txt} (sin identificar)"
            warn("ambiguo" if cands else "nombre",
                 f"{minute}' {tipo} «{txt}»: " + (", ".join(p.nombre for p in cands) if cands else "sin coincidencias"), ln)
        det = f"rival={rival}"
        ev_rows.append(dict(jornada=m.jornada, equipo=team, minuto=minute, tipo=TYPE_OUT[tipo], jugador=name, detalle=det))
        if tipo in ("gol", "penalti"):
            goals[side] += 1
        elif tipo == "propia":
            goals["V" if side == "L" else "L"] += 1
        if tipo in ("roja", "segunda_amarilla") and name in on_field[side]:
            on_field[side].discard(name)
    if (goals["L"], goals["V"]) != (m.gl, m.gv):
        warn("marcador", f"marcador {m.gl}-{m.gv} y goles en el acta {goals['L']}-{goals['V']}")
    for nota in m.notas:
        warn("nota", nota)
    return al_rows, ev_rows, ambiguous


def main() -> int:
    matches = parse(SRC / "actas.txt")
    extra = SRC / "resultados.txt"
    if extra.exists():
        matches += parse(extra)
    keys = set()
    avisos: list[dict] = []
    part_rows, al_all, ev_all, amb_all = [], [], [], []
    for m in matches:
        k = (m.jornada, m.local, m.visitante)
        if k in keys:
            avisos.append(dict(jornada=m.jornada, partido=f"{m.local} - {m.visitante}", tipo="duplicado",
                               detalle="partido repetido en la fuente", linea=m.line_no))
            continue
        keys.add(k)
        al, ev, amb = process(m, avisos)
        al_all += al
        ev_all += ev
        amb_all += [(m.jornada, m.team(s), n) for n in amb for s in "LV" if any(p.nombre == n and p.side == s for p in m.players)]
        part_rows.append(dict(jornada=m.jornada, fecha=m.fecha, hora=m.hora, local=m.local, visitante=m.visitante,
                              goles_local=m.gl, goles_visitante=m.gv, campo=m.campo, sistema_local=m.sis_l,
                              sistema_visitante=m.sis_v, estado="acta" if m.acta else "solo_resultado"))
    partidos = pd.DataFrame(part_rows).sort_values(["jornada", "fecha", "hora", "local"])
    alineaciones = pd.DataFrame(al_all)
    eventos = pd.DataFrame(ev_all, columns=["jornada", "equipo", "minuto", "tipo", "jugador", "detalle"])
    # Un mismo jugador puede aparecer con y sin tilde según el acta: se unifica dentro de su equipo
    # usando la forma con más apariciones (la identidad no cambia; solo la grafía).
    canon = {}
    for (team, key), grp in alineaciones.assign(k=alineaciones.jugador.map(norm)).groupby(["equipo", "k"]):
        forms = grp.jugador.value_counts()
        if len(forms) > 1:
            best = sorted(forms.index, key=lambda f: (-forms[f], -sum(ch != unicodedata.normalize("NFKD", ch)[0] for ch in f)))[0]
            for f in forms.index:
                if f != best:
                    canon[(team, f)] = best
                    avisos.append(dict(jornada=0, partido=team, tipo="nota", detalle=f"Nombre unificado: «{f}» → «{best}»", linea=0))
    if canon:
        def _fix(df, col="jugador"):
            df[col] = [canon.get((t, j), j) for t, j in zip(df.equipo, df[col])]
        _fix(alineaciones)
        _fix(eventos)
        eventos["detalle"] = [";".join((f"sale={canon.get((t, x[5:]), x[5:])}" if x.startswith("sale=") else x) for x in str(d).split(";"))
                              for t, d in zip(eventos.equipo, eventos.detalle)]
    minutos = lc.minutes_from_acta(alineaciones, eventos, MATCH_MINUTES, fuente="Acta FFCV (vídeo aportado por el usuario)")
    # minutos que dependen de un cambio ambiguo: no se inventan
    minutos["minutos"] = minutos["minutos"].astype("Float64")
    for j, team, name in amb_all:
        mask = (minutos.jornada == j) & (minutos.equipo == team) & (minutos.jugador == name)
        minutos.loc[mask, "minutos"] = pd.NA
        minutos.loc[mask, "fuente"] = "pendiente: cambio ambiguo en el acta"
    plantillas = (alineaciones.groupby(["equipo", "jugador"]).agg(dorsal=("dorsal", lambda s: s.mode().iat[0]))
                  .reset_index()[["equipo", "dorsal", "jugador"]].sort_values(["equipo", "dorsal", "jugador"]))
    teams = sorted(set(partidos.local) | set(partidos.visitante))
    equipos = pd.DataFrame({"orden": range(1, len(teams) + 1), "equipo": teams})

    DIR.mkdir(parents=True, exist_ok=True)
    partidos.to_csv(DIR / "partidos.csv", index=False)
    alineaciones.to_csv(DIR / "alineaciones.csv", index=False)
    eventos.to_csv(DIR / "eventos.csv", index=False)
    minutos.to_csv(DIR / "minutos.csv", index=False)
    plantillas.to_csv(DIR / "plantillas.csv", index=False)
    equipos.to_csv(DIR / "equipos.csv", index=False)
    pd.DataFrame(avisos, columns=["jornada", "partido", "tipo", "detalle", "linea"]).to_csv(DIR / "avisos.csv", index=False)
    clas = SRC / "clasificacion_oficial.txt"
    if clas.exists():
        rows = []
        for line in clas.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            j, fecha, pos, team, pts, pj, pg, pe, pp, *rest = [x.strip() for x in line.split("|")]
            rows.append(dict(jornada=int(j), fecha=fecha, posicion=int(pos), equipo=team, puntos=_int(pts), pj=_int(pj),
                             pg=_int(pg), pe=_int(pe), pp=_int(pp), gf=_int(rest[0]) if rest else None,
                             gc=_int(rest[1]) if len(rest) > 1 else None))
        pd.DataFrame(rows).to_csv(DIR / "clasificacion_oficial.csv", index=False)

    export_league_schema(partidos, alineaciones, eventos, minutos, plantillas)
    n_acta = int((partidos.estado == "acta").sum())
    print(f"{len(partidos)} partidos ({n_acta} con acta) · jornadas {sorted(partidos.jornada.unique().tolist())}")
    print(f"{len(teams)} equipos · {alineaciones.jugador.nunique() if not alineaciones.empty else 0} nombres de jugador · "
          f"{len(eventos)} eventos")
    serious = [a for a in avisos if a["tipo"] not in ("nota", "ambiguo")]
    print(f"Avisos: {len(avisos)} ({len(serious)} a revisar)")
    for a in avisos:
        if a["tipo"] != "nota":
            print(f"  J{a['jornada']} {a['partido']} · {a['tipo']}: {a['detalle']} (línea {a['linea']})")
    return 1 if serious else 0


def export_league_schema(partidos, alineaciones, eventos, minutos, plantillas):
    """Escribe data/cadete_a/liga/ con los mismos archivos y columnas que el Juvenil A
    (partidos_rivales, eventos_rivales, minutos_rivales, alineaciones_rivales, plantillas_rivales,
    clasificacion_liga, equipos_liga), para reutilizar Resumen de liga y Rivales sin duplicar código.

    Convención de eventos del Juvenil A: cada gol figura dos veces, «gol» en el equipo que marca y
    «gol_contra» en el que lo encaja (penalti_gol / penalti_contra_gol). Un gol en propia puerta es
    «gol» con jugador «G.P.» en el equipo beneficiado. Segunda amarilla = «doble_amarilla».
    """
    out = DIR / "liga"
    out.mkdir(parents=True, exist_ok=True)
    p = partidos.copy()
    p["estado"] = "validado"
    p[["jornada", "fecha", "local", "visitante", "goles_local", "goles_visitante", "campo", "sistema_local",
       "sistema_visitante", "estado"]].to_csv(out / "partidos_rivales.csv", index=False)
    rows = []
    for e in eventos.itertuples():
        rival = lc._kv(e.detalle, "rival")
        t = e.tipo
        if t in ("gol", "penalti_gol"):
            pen = t == "penalti_gol"
            rows.append(dict(jornada=e.jornada, equipo=e.equipo, minuto=e.minuto, tipo=t, jugador=e.jugador,
                             detalle="Gol de penalti" if pen else ""))
            rows.append(dict(jornada=e.jornada, equipo=rival, minuto=e.minuto,
                             tipo="penalti_contra_gol" if pen else "gol_contra", jugador=e.jugador,
                             detalle=f"Gol encajado ante {e.equipo}" + (" de penalti" if pen else "")))
        elif t == "gol_propia":
            rows.append(dict(jornada=e.jornada, equipo=rival, minuto=e.minuto, tipo="gol", jugador="G.P.",
                             detalle=f"Gol en propia rival: {e.jugador}"))
            rows.append(dict(jornada=e.jornada, equipo=e.equipo, minuto=e.minuto, tipo="gol_contra", jugador=e.jugador,
                             detalle="Gol en propia puerta"))
        elif t == "amarilla":
            rows.append(dict(jornada=e.jornada, equipo=e.equipo, minuto=e.minuto, tipo="amarilla", jugador=e.jugador, detalle=""))
        elif t == "segunda_amarilla":
            rows.append(dict(jornada=e.jornada, equipo=e.equipo, minuto=e.minuto, tipo="doble_amarilla", jugador=e.jugador,
                             detalle="Segunda amarilla / expulsión"))
        elif t == "roja":
            rows.append(dict(jornada=e.jornada, equipo=e.equipo, minuto=e.minuto, tipo="roja", jugador=e.jugador, detalle=""))
    pd.DataFrame(rows, columns=["jornada", "equipo", "minuto", "tipo", "jugador", "detalle"]).sort_values(
        ["jornada", "equipo", "minuto"], kind="stable").to_csv(out / "eventos_rivales.csv", index=False)
    m = minutos.copy()
    m["fuente"] = m["fuente"].fillna("Acta FFCV")
    m.to_csv(out / "minutos_rivales.csv", index=False)
    a = alineaciones[~alineaciones.rol.astype(str).str.startswith("SUP")].copy()
    a["rol"] = a["rol"].replace({"DEL": "ATA"})
    a[["equipo", "jornada", "dorsal", "jugador", "rol", "linea", "orden"]].to_csv(out / "alineaciones_rivales.csv", index=False)
    plantillas.to_csv(out / "plantillas_rivales.csv", index=False)
    teams = sorted(set(partidos.local) | set(partidos.visitante))
    clas = []
    for j in sorted(partidos.jornada.unique()):
        tab = lc.standings(partidos[partidos.jornada <= j], teams)
        fechas = pd.to_datetime(partidos[partidos.jornada == j].fecha, format="%d/%m/%Y", errors="coerce").dropna()
        fecha = fechas.max().strftime("%d/%m/%Y") if not fechas.empty else ""
        for r in tab.itertuples():
            clas.append(dict(jornada=int(j), fecha=fecha, posicion=r.pos, equipo=r.equipo, puntos=r.pts, pj=r.pj,
                             pg=r.pg, pe=r.pe, pp=r.pp))
    pd.DataFrame(clas).to_csv(out / "clasificacion_liga.csv", index=False)
    last = max(j for j in partidos.jornada.unique()
               if (partidos.jornada == j).sum() >= len(teams) // 2) if len(partidos) else 0
    order = lc.standings(partidos[partidos.jornada <= last], teams).equipo.tolist()
    pd.DataFrame({"orden": range(1, len(order) + 1), "equipo": order}).to_csv(out / "equipos_liga.csv", index=False)


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    sys.exit(main())
