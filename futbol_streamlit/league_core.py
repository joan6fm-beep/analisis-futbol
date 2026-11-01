"""Cálculos de liga reutilizables y parametrizados por la duración del partido.

Traslada la lógica de Resumen de liga / Rivales del Juvenil A (clasificación a partir de
resultados, minutos por jugador, atribución de goles al portero que estaba en el campo,
distribución de goles por tramos) a funciones puras que reciben `match_minutes`.
Las usa el Cadete A (80'); el código del Juvenil A no se modifica.

Todas las funciones trabajan con los mismos esquemas CSV que el Juvenil A:
  partidos:     jornada, fecha, local, visitante, goles_local, goles_visitante, ..., estado
  eventos:      jornada, equipo, minuto, tipo, jugador, detalle
  minutos:      equipo, jornada, dorsal, jugador, minutos, titular, fuente
  alineaciones: equipo, jornada, dorsal, jugador, rol, linea, orden
                (rol: POR/DEF/MED/DEL titulares; SUP suplente; SUP_POR portero suplente)
"""
from __future__ import annotations

import math

import pandas as pd

GOAL_TYPES_FOR = {"gol", "penalti_gol"}          # gol del jugador para su propio equipo
OWN_GOAL_TYPES = {"gol_propia"}                  # gol en propia puerta: suma al rival
CARD_TYPES = {"amarilla", "doble_amarilla", "segunda_amarilla", "roja"}


# --------------------------------------------------------------------------- partidos

def played(partidos: pd.DataFrame) -> pd.DataFrame:
    """Partidos con marcador conocido."""
    p = partidos.copy()
    p["goles_local"] = pd.to_numeric(p["goles_local"], errors="coerce")
    p["goles_visitante"] = pd.to_numeric(p["goles_visitante"], errors="coerce")
    p["jornada"] = pd.to_numeric(p["jornada"], errors="coerce")
    return p.dropna(subset=["goles_local", "goles_visitante", "jornada"])


def team_matches(partidos: pd.DataFrame, team: str) -> pd.DataFrame:
    """Una fila por partido del equipo con gf/gc, condición y puntos."""
    p = played(partidos)
    rows = []
    for _, r in p.iterrows():
        if r["local"] == team:
            gf, gc, cond, rival = r["goles_local"], r["goles_visitante"], "Casa", r["visitante"]
        elif r["visitante"] == team:
            gf, gc, cond, rival = r["goles_visitante"], r["goles_local"], "Fuera", r["local"]
        else:
            continue
        res = "V" if gf > gc else ("E" if gf == gc else "D")
        rows.append(dict(jornada=int(r["jornada"]), fecha=r.get("fecha"), rival=rival, condicion=cond,
                         gf=int(gf), gc=int(gc), resultado=res, puntos={"V": 3, "E": 1, "D": 0}[res]))
    return pd.DataFrame(rows, columns=["jornada", "fecha", "rival", "condicion", "gf", "gc", "resultado", "puntos"]
                        ).sort_values("jornada").reset_index(drop=True)


def standings(partidos: pd.DataFrame, teams: list[str] | None = None, upto: int | None = None) -> pd.DataFrame:
    """Clasificación calculada a partir de los resultados (3-1-0).

    Desempate aplicado: puntos, diferencia de goles, goles a favor, nombre. Es un orden de
    referencia: los desempates oficiales (p. ej. enfrentamiento directo) pueden diferir y por eso
    la app muestra la clasificación oficial cuando está disponible.
    """
    p = played(partidos)
    if upto is not None:
        p = p[p["jornada"] <= upto]
    names = set(teams or []) | set(p["local"]) | set(p["visitante"])
    tab = {t: dict(equipo=t, pj=0, pg=0, pe=0, pp=0, gf=0, gc=0, pts=0,
                   pj_casa=0, pts_casa=0, gf_casa=0, gc_casa=0, pj_fuera=0, pts_fuera=0, gf_fuera=0, gc_fuera=0)
           for t in names}
    for _, r in p.iterrows():
        gl, gv = int(r["goles_local"]), int(r["goles_visitante"])
        for team, gf, gc, side in ((r["local"], gl, gv, "casa"), (r["visitante"], gv, gl, "fuera")):
            s = tab[team]
            pts = 3 if gf > gc else (1 if gf == gc else 0)
            s["pj"] += 1; s["gf"] += gf; s["gc"] += gc; s["pts"] += pts
            s["pg"] += gf > gc; s["pe"] += gf == gc; s["pp"] += gf < gc
            s[f"pj_{side}"] += 1; s[f"pts_{side}"] += pts; s[f"gf_{side}"] += gf; s[f"gc_{side}"] += gc
    df = pd.DataFrame(tab.values())
    if df.empty:
        return df
    df["dg"] = df["gf"] - df["gc"]
    df = df.sort_values(["pts", "dg", "gf", "equipo"], ascending=[False, False, False, True]).reset_index(drop=True)
    df.insert(0, "pos", range(1, len(df) + 1))
    return df


def position_evolution(partidos: pd.DataFrame, teams: list[str]) -> pd.DataFrame:
    """Posición y puntos de cada equipo al cierre de cada jornada (calculado)."""
    p = played(partidos)
    out = []
    for j in sorted(p["jornada"].unique()):
        t = standings(p, teams, upto=int(j))
        t["jornada"] = int(j)
        out.append(t[["jornada", "equipo", "pos", "pts", "dg", "gf", "gc"]])
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=["jornada", "equipo", "pos", "pts", "dg", "gf", "gc"])


# --------------------------------------------------------------------------- tramos de goles

def minute_bins(match_minutes: int, step: int = 10) -> list[tuple[int, int, str]]:
    """Tramos reglamentarios (lo, hi]: 0–10, 10–20 … hasta match_minutes. No hay tramo posterior."""
    return [(a, min(a + step, match_minutes), f"{a}–{min(a + step, match_minutes)}") for a in range(0, match_minutes, step)]


def bin_label(minute, match_minutes: int, step: int = 10) -> str | None:
    """Tramo de un gol con una convención única, sin duplicados en los límites:
    el minuto m va al tramo (lo, hi] que lo contiene (un gol en el 10' cuenta en 0–10; el minuto 0 también).
    Un minuto posterior al reglamentario (tiempo añadido) va al último tramo con '+'; el minuto real se conserva."""
    try:
        m = float(minute)
    except (TypeError, ValueError):
        return None
    bins = minute_bins(match_minutes, step)
    if m > match_minutes:
        return bins[-1][2] + "+"
    for lo, hi, lab in bins:
        if m <= hi:
            return lab
    return None


def goals_by_bin(eventos: pd.DataFrame, team: str, match_minutes: int, step: int = 10) -> pd.DataFrame:
    """Goles a favor y en contra de `team` por tramos (incluye propia puerta del rival)."""
    labels = [b[2] for b in minute_bins(match_minutes, step)]
    rows = {lab: dict(tramo=lab, a_favor=0, en_contra=0, a_favor_añadido=0, en_contra_añadido=0) for lab in labels}
    for _, e in eventos.iterrows():
        side = goal_side(e, team)
        if side is None:
            continue
        lab = bin_label(e["minuto"], match_minutes, step)
        if lab is None:
            continue
        extra = lab.endswith("+")
        lab = lab.rstrip("+")
        key = "a_favor" if side == "favor" else "en_contra"
        rows[lab][key] += 1
        if extra:
            rows[lab][key + "_añadido"] += 1
    return pd.DataFrame(rows.values())


def goal_side(e, team: str) -> str | None:
    """'favor' / 'contra' / None para un evento respecto a `team`.

    Convención: `equipo` es el equipo del jugador y `detalle` incluye 'rival=<equipo>' (el
    importador lo escribe en todos los eventos). Un gol en propia puerta (gol_propia) suma al rival.
    """
    t = e["tipo"]
    if t in GOAL_TYPES_FOR:
        return "favor" if e["equipo"] == team else ("contra" if _rival_of(e) == team else None)
    if t in OWN_GOAL_TYPES:
        return "contra" if e["equipo"] == team else ("favor" if _rival_of(e) == team else None)
    return None


def _rival_of(e) -> str | None:
    d = str(e.get("detalle") or "")
    for part in d.split(";"):
        if part.strip().startswith("rival="):
            return part.strip()[6:]
    return None


# --------------------------------------------------------------------------- minutos

def participation(minutos: pd.DataFrame, team: str, match_minutes: int, partidos_jugados: int | None = None) -> pd.DataFrame:
    """Minutos, titularidades y % sobre los minutos reglamentarios disponibles del equipo."""
    m = minutos[minutos["equipo"] == team].copy()
    if m.empty:
        return pd.DataFrame(columns=["dorsal", "jugador", "partidos", "titular", "suplente", "minutos", "pct", "media"])
    m["minutos"] = pd.to_numeric(m["minutos"], errors="coerce").fillna(0)
    m["titular"] = pd.to_numeric(m["titular"], errors="coerce").fillna(0).astype(int)
    n = partidos_jugados if partidos_jugados is not None else m["jornada"].nunique()
    g = m.groupby("jugador").agg(dorsal=("dorsal", lambda s: s.mode().iat[0] if not s.mode().empty else None),
                                 partidos=("minutos", lambda s: int((s > 0).sum())),
                                 titular=("titular", "sum"), minutos=("minutos", "sum")).reset_index()
    g["suplente"] = g["partidos"] - g["titular"]
    g["pct"] = g["minutos"] / (match_minutes * max(n, 1)) * 100
    g["media"] = g.apply(lambda r: r["minutos"] / r["partidos"] if r["partidos"] else 0, axis=1)
    return g.sort_values(["minutos", "jugador"], ascending=[False, True]).reset_index(drop=True)


def minutes_from_acta(alineaciones: pd.DataFrame, eventos: pd.DataFrame, match_minutes: int,
                      fuente: str = "acta") -> pd.DataFrame:
    """Minutos de cada jugador calculados desde el acta (titulares, cambios y expulsiones).

    Reglas (las mismas que el registro de minutos de las actas):
      * titular: juega desde 0 hasta su sustitución o expulsión; si no, hasta `match_minutes`.
      * suplente que entra en el minuto m: juega `match_minutes - m` (si sale o es expulsado después, hasta ese minuto).
      * el tiempo añadido no suma minutos: el máximo por partido es `match_minutes`.
      * un minuto de evento mayor que la duración (añadido) se trata como el final del partido.
    Suplentes que no entran: 0 minutos (convocados sin participar).
    """
    rows = []
    al = alineaciones.copy()
    al["jornada"] = pd.to_numeric(al["jornada"], errors="coerce")
    ev = eventos.copy()
    ev["jornada"] = pd.to_numeric(ev["jornada"], errors="coerce")
    ev["minuto"] = pd.to_numeric(ev["minuto"], errors="coerce")
    for (team, j), lineup in al.groupby(["equipo", "jornada"]):
        e = ev[(ev["equipo"] == team) & (ev["jornada"] == j)]
        start = {r["jugador"]: 0 for _, r in lineup.iterrows() if not str(r["rol"]).startswith("SUP")}
        end: dict[str, float] = {}
        for _, s in e[e["tipo"] == "cambio"].iterrows():
            m = min(float(s["minuto"]), match_minutes)
            start.setdefault(s["jugador"], m)
            out = _kv(s.get("detalle"), "sale")
            if out:
                end[out] = m
        for _, s in e[e["tipo"].isin({"roja", "doble_amarilla", "segunda_amarilla"})].iterrows():
            if pd.notna(s["minuto"]):
                end[s["jugador"]] = min(float(s["minuto"]), match_minutes)
        for _, r in lineup.iterrows():
            n = r["jugador"]
            if n in start:
                mins = max(0.0, end.get(n, match_minutes) - start[n])
            else:
                mins = 0.0
            rows.append(dict(equipo=team, jornada=int(j), dorsal=r["dorsal"], jugador=n, minutos=int(round(mins)),
                             titular=int(not str(r["rol"]).startswith("SUP")), fuente=fuente))
    return pd.DataFrame(rows, columns=["equipo", "jornada", "dorsal", "jugador", "minutos", "titular", "fuente"])


# --------------------------------------------------------------------------- porteros

def goalkeepers(alineaciones: pd.DataFrame, minutos: pd.DataFrame, eventos: pd.DataFrame, partidos: pd.DataFrame,
                team: str, match_minutes: int) -> tuple[pd.DataFrame, list[str]]:
    """Estadísticas de porteros con goles encajados atribuidos por minuto.

    Un gol encajado en el minuto m se atribuye al portero que estaba en el campo en ese minuto
    (según su tramo [entrada, salida] de minutos). Si no se puede determinar (falta el minuto del gol
    o el tramo del portero es desconocido) se cuenta como «sin atribuir», nunca se adivina.
    Devuelve (tabla, avisos).
    """
    warnings: list[str] = []
    al = alineaciones[(alineaciones["equipo"] == team) & (alineaciones["rol"].isin(["POR", "SUP_POR"]))]
    mins = minutos[minutos["equipo"] == team].copy()
    mins["minutos"] = pd.to_numeric(mins["minutos"], errors="coerce").fillna(0)
    stats: dict[str, dict] = {}
    unattributed = 0
    tm = team_matches(partidos, team)
    for _, match in tm.iterrows():
        j = match["jornada"]
        gks = player_intervals(team, j, alineaciones, eventos, minutos, match_minutes)
        gk_names = set(al[al["jornada"] == j]["jugador"]) | {n for n in gks if gks[n]["portero"]}
        gk_iv = {n: gks[n] for n in gk_names if n in gks and gks[n]["minutos"] > 0}
        for n, iv in gk_iv.items():
            s = stats.setdefault(n, dict(jugador=n, partidos=0, titular=0, minutos=0, encajados=0, porterias_cero=0))
            s["partidos"] += 1
            s["titular"] += int(iv["titular"])
            s["minutos"] += iv["minutos"]
            s["_conceded_this"] = 0
        ev = eventos[pd.to_numeric(eventos["jornada"], errors="coerce") == j]
        conceded = [e for _, e in ev.iterrows() if goal_side(e, team) == "contra"]
        if len(conceded) != match["gc"]:
            warnings.append(f"J{j}: {match['gc']} goles encajados en el marcador y {len(conceded)} en los eventos.")
        for e in conceded:
            try:
                m = int(float(e["minuto"]))
            except (TypeError, ValueError):
                unattributed += 1
                continue
            # quien termina el partido (sale >= duración) cubre también el tiempo añadido
            owner = [n for n, iv in gk_iv.items()
                     if iv["entra"] <= m <= (10**6 if iv["sale"] >= match_minutes else iv["sale"])]
            if len(owner) == 1:
                stats[owner[0]]["encajados"] += 1
                stats[owner[0]]["_conceded_this"] += 1
            else:
                unattributed += 1
        for n, iv in gk_iv.items():
            s = stats[n]
            if iv["titular"] and iv["sale"] >= match_minutes and s["_conceded_this"] == 0 and match["gc"] == 0:
                s["porterias_cero"] += 1
            s.pop("_conceded_this", None)
    df = pd.DataFrame(stats.values(), columns=["jugador", "partidos", "titular", "minutos", "encajados", "porterias_cero"])
    if not df.empty:
        df["encajados_por_partido_reglamentario"] = df.apply(
            lambda r: r["encajados"] / r["minutos"] * match_minutes if r["minutos"] else math.nan, axis=1)
        df["pct_minutos"] = df["minutos"] / (match_minutes * max(len(tm), 1)) * 100
        df = df.sort_values(["minutos", "jugador"], ascending=[False, True]).reset_index(drop=True)
    if unattributed:
        warnings.append(f"{unattributed} gol(es) encajado(s) sin portero atribuible.")
    return df, warnings


def player_intervals(team: str, jornada: int, alineaciones: pd.DataFrame, eventos: pd.DataFrame,
                     minutos: pd.DataFrame, match_minutes: int) -> dict[str, dict]:
    """Tramo [entra, sale] de cada jugador del equipo en un partido.

    Usa los cambios del acta (eventos tipo 'cambio' con jugador=entra y detalle 'sale=<nombre>')
    y las expulsiones. Si no hay cambios registrados, usa minutos_rivales: titular → [0, minutos],
    suplente → [match_minutes - minutos, match_minutes].
    """
    al = alineaciones[(alineaciones["equipo"] == team) & (pd.to_numeric(alineaciones["jornada"], errors="coerce") == jornada)]
    ev = eventos[(eventos["equipo"] == team) & (pd.to_numeric(eventos["jornada"], errors="coerce") == jornada)]
    mins = minutos[(minutos["equipo"] == team) & (pd.to_numeric(minutos["jornada"], errors="coerce") == jornada)]
    out: dict[str, dict] = {}
    for _, r in mins.iterrows():
        m = float(pd.to_numeric(r["minutos"], errors="coerce") or 0)
        tit = int(pd.to_numeric(r["titular"], errors="coerce") or 0) == 1
        out[r["jugador"]] = dict(titular=tit, entra=0 if tit else match_minutes - m,
                                 sale=m if tit else match_minutes, minutos=m, portero=False)
    subs = ev[ev["tipo"] == "cambio"]
    for _, s in subs.iterrows():
        mm = int(float(s["minuto"]))
        inn = s["jugador"]
        outp = _kv(s.get("detalle"), "sale")
        if inn in out:
            out[inn]["entra"] = mm
        if outp and outp in out:
            out[outp]["sale"] = mm
    for _, r in al.iterrows():
        if r["jugador"] in out and r["rol"] in ("POR", "SUP_POR"):
            out[r["jugador"]]["portero"] = True
    for n in out:
        if _kv_list(ev, n, "portero"):
            out[n]["portero"] = True
    return out


def _kv(detalle, key):
    for part in str(detalle or "").split(";"):
        part = part.strip()
        if part.startswith(key + "="):
            return part[len(key) + 1:]
    return None


def _kv_list(ev: pd.DataFrame, name: str, key: str) -> bool:
    return any(_kv(d, key) == name for d in ev.get("detalle", []))


# --------------------------------------------------------------------------- goleadores

def scorers(eventos: pd.DataFrame, minutos: pd.DataFrame | None = None, team: str | None = None) -> pd.DataFrame:
    """Ranking de goleadores (sin propia puerta), con minutos de gol y % sobre los goles del equipo."""
    g = eventos[eventos["tipo"].isin(GOAL_TYPES_FOR)].copy()
    if team:
        g = g[g["equipo"] == team]
    if g.empty:
        return pd.DataFrame(columns=["equipo", "jugador", "goles", "penaltis", "minutos_gol", "pct_equipo", "partidos", "goles_partido"])
    g["minuto"] = pd.to_numeric(g["minuto"], errors="coerce")
    team_tot = g.groupby("equipo").size()
    rows = []
    for (eq, jug), d in g.groupby(["equipo", "jugador"]):
        pj = None
        if minutos is not None:
            mm = minutos[(minutos["equipo"] == eq) & (minutos["jugador"] == jug)]
            pj = int((pd.to_numeric(mm["minutos"], errors="coerce") > 0).sum())
        rows.append(dict(equipo=eq, jugador=jug, goles=len(d), penaltis=int((d["tipo"] == "penalti_gol").sum()),
                         minutos_gol=", ".join(f"{int(x)}'" for x in sorted(d["minuto"].dropna())),
                         pct_equipo=len(d) / team_tot[eq] * 100, partidos=pj,
                         goles_partido=(len(d) / pj) if pj else math.nan))
    return pd.DataFrame(rows).sort_values(["goles", "jugador"], ascending=[False, True]).reset_index(drop=True)


def discipline(eventos: pd.DataFrame, team: str | None = None) -> pd.DataFrame:
    c = eventos[eventos["tipo"].isin(CARD_TYPES)].copy()
    if team:
        c = c[c["equipo"] == team]
    if c.empty:
        return pd.DataFrame(columns=["equipo", "jugador", "amarillas", "rojas"])
    c["am"] = c["tipo"].isin({"amarilla", "segunda_amarilla", "doble_amarilla"}).astype(int)
    c["ro"] = c["tipo"].isin({"roja", "doble_amarilla", "segunda_amarilla"}).astype(int)
    return (c.groupby(["equipo", "jugador"]).agg(amarillas=("am", "sum"), rojas=("ro", "sum")).reset_index()
            .sort_values(["rojas", "amarillas"], ascending=False))
