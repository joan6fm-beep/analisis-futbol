"""Análisis avanzado de Equipo 360: preparar partido, rival, laboratorio y temporadas.

Principios:
- Solo datos reales. Lo que no existe se muestra como «no disponible», nunca como 0.
- Toda media indica cuántos partidos intervienen (n).
- Estadísticas de vídeo (Veo, solo partidos de Primer Toque en casa) y resultados
  oficiales (todos los partidos de la liga) se presentan por separado.
- Radares con índice 0–100 explícito: valor ÷ máximo de referencia × 100.
"""
from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import team360_charts as T
from ui_theme import TOKENS, PT, RIVAL, POS, NEG, MUTED, plotly_layout, PLOTLY_CONFIG

TEAM = "Primer Toque C.F. 'A'"
SEASONS_FILE = Path(__file__).parent / "data" / "temporadas.csv"

# Métricas de resultados oficiales por partido (disponibles para cualquier equipo).
RESULT_METRICS = [("Goles a favor", "gf", "goles", True), ("Goles en contra", "gc", "goles", False),
                  ("Puntos", "pts", "puntos", True), ("Diferencia de goles", "dg", "goles", True)]
# Radar 1 (Primer Toque frente a su media): volumen y calidad propios.
RADAR_PT = ["Posesión", "Pases completados", "Precisión de pase", "Pases hacia delante acertados", "Intentos de tiro",
            "Intentos dentro del área", "Ocasiones", "Córneres", "Regates", "Recuperaciones", "Intercepciones"]
# Radar 2 (Primer Toque frente al rival): solo métricas que Veo da de ambos equipos.
RADAR_VS = ["Posesión", "Pases totales", "Pases completados", "Precisión de pase", "Tiros", "Ocasiones",
            "Córneres", "Faltas lanzadas", "Saques de banda"]
NEUTRAL_NOTE = {"Duelos", "Entradas / contactos", "Saques de banda", "Faltas cometidas"}

CSS = """
<style>
.adv-ref{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:6px 0 12px}
.adv-ref>div{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:11px 13px}
.adv-ref b{display:block;font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.adv-ref span{display:block;font-size:.95rem;font-weight:800;color:var(--ink);margin-top:3px}
.adv-ref small{display:block;font-size:.68rem;color:var(--muted);margin-top:2px}
.adv-ref .a{box-shadow:inset 0 3px 0 var(--pt)}.adv-ref .b{box-shadow:inset 0 3px 0 #B8661E}
.adv-ref .c{box-shadow:inset 0 3px 0 var(--rival)}.adv-ref .d{box-shadow:inset 0 3px 0 #3E5F8A}
.adv-tbl{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:4px 14px;margin:4px 0 12px;overflow-x:auto}
.adv-row{display:grid;grid-template-columns:1.5fr .8fr .9fr .9fr .8fr .9fr .9fr;gap:10px;align-items:center;padding:8px 0;border-bottom:1px solid var(--line-soft);font-size:.8rem;min-width:720px}
.adv-row:last-child{border-bottom:0}
.adv-head{font-size:.62rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.adv-group{font-size:.68rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--pt);padding:12px 0 4px;min-width:720px}
.adv-m{font-weight:700;color:var(--ink)} .adv-m small{display:block;font-weight:500;color:var(--muted);font-size:.64rem}
.adv-v{font-weight:800;color:var(--ink)} .adv-v small{display:block;font-weight:500;color:var(--muted);font-size:.62rem}
.adv-na{color:var(--muted);font-size:.7rem;font-style:italic}
.adv-d{font-size:.74rem;font-weight:800} .adv-d small{display:block;font-weight:600;font-size:.62rem;color:var(--muted)}
.adv-d.up{color:var(--pos)} .adv-d.down{color:var(--neg)} .adv-d.flat{color:var(--text)}
.adv-note{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--rival);border-radius:12px;padding:10px 14px;font-size:.76rem;color:var(--text);margin:6px 0 12px}
.adv-note b{color:var(--ink)}
.adv-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:6px 0 12px}
.adv-kpi{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
.adv-kpi small{display:block;font-size:.66rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.adv-kpi b{display:block;font-size:1.45rem;font-weight:850;color:var(--ink);letter-spacing:-.02em;margin:2px 0}
.adv-kpi span{display:block;font-size:.66rem;color:var(--muted)}
.adv-kpi .n{display:inline-block;background:var(--surface-2);border:1px solid var(--line);border-radius:999px;padding:1px 7px;font-size:.62rem;font-weight:700;color:var(--text);margin-left:4px}
.adv-insight li{margin:5px 0}
@media(max-width:760px){.adv-ref,.adv-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
.vs-row{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:12px;align-items:center;padding:7px 0;border-bottom:1px solid var(--line-soft);font-size:.78rem}
.vs-row:last-child{border-bottom:0}.vs-row .m{color:var(--ink);font-weight:700}
.vs-bar{display:flex;align-items:center;gap:8px}.vs-bar i{display:block;height:10px;border-radius:5px;min-width:2px}
.vs-bar b{color:var(--ink);font-size:.82rem;min-width:38px}.vs-bar.pt i{background:var(--pt)}.vs-bar.rv i{background:var(--rival)}
.vs-head{font-size:.62rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
</style>
"""


# ---------------------------------------------------------------- resultados oficiales
def team_matches(partidos, team):
    """Partidos jugados de un equipo con goles, puntos y condición. Solo partidos con resultado."""
    p = partidos.dropna(subset=["goles_local", "goles_visitante"])
    p = p[(p.local == team) | (p.visitante == team)].copy()
    if p.empty:
        return pd.DataFrame(columns=["jornada", "rival", "condicion", "gf", "gc", "pts", "res", "dg"])
    home = p.local == team
    out = pd.DataFrame({
        "jornada": pd.to_numeric(p.jornada, errors="coerce").astype(int).values,
        "rival": p.visitante.where(home, p.local).values,
        "condicion": home.map({True: "Casa", False: "Fuera"}).values,
        "gf": p.goles_local.where(home, p.goles_visitante).astype(int).values,
        "gc": p.goles_visitante.where(home, p.goles_local).astype(int).values,
    })
    out["pts"] = (out.gf > out.gc) * 3 + (out.gf == out.gc) * 1
    out["res"] = out.apply(lambda r: "V" if r.gf > r.gc else ("E" if r.gf == r.gc else "D"), axis=1)
    out["dg"] = out.gf - out.gc
    return out.sort_values("jornada").reset_index(drop=True)


def split_summary(tm):
    """Resumen Total / Casa / Fuera con n explícito."""
    res = {}
    for k, d in (("Total", tm), ("Casa", tm[tm.condicion == "Casa"]), ("Fuera", tm[tm.condicion == "Fuera"])):
        n = len(d)
        res[k] = dict(n=n, pts=int(d.pts.sum()), gf=int(d.gf.sum()), gc=int(d.gc.sum()),
                      v=int((d.res == "V").sum()), e=int((d.res == "E").sum()), dd=int((d.res == "D").sum()),
                      ppg=d.pts.mean() if n else float("nan"), gf_pg=d.gf.mean() if n else float("nan"),
                      gc_pg=d.gc.mean() if n else float("nan"), dg=int(d.dg.sum()))
    return res


# ---------------------------------------------------------------- comparador de cuatro referencias
def _pct(a, b, unit):
    """Diferencia porcentual solo cuando tiene sentido (base > 0 y no es ya un porcentaje)."""
    if pd.isna(a) or pd.isna(b) or unit == "%" or b <= 0 or a < 0:  # sin sentido con bases nulas o valores negativos
        return None
    return 100 * (a - b) / b


def four_refs(veo, pt_tm, rival_tm, jornada, exclude=True):
    """Filas del comparador A (PT jornada) · B (media PT en casa) · C (rival jornada) · D (media rival fuera)."""
    rows = []
    a_res = pt_tm[pt_tm.jornada == jornada]
    home = pt_tm[pt_tm.condicion == "Casa"]
    if exclude:
        home = home[home.jornada != jornada]
    away = rival_tm[rival_tm.condicion == "Fuera"]
    for lab, col, unit, better in RESULT_METRICS:
        a = float(a_res[col].iloc[0]) if len(a_res) else float("nan")
        b = home[col].mean() if len(home) else float("nan")
        rc = {"gf": "gc", "gc": "gf", "pts": None, "dg": None}[col]
        if col == "pts":
            c = float({0: 3, 1: 1, 3: 0}[int(a_res.pts.iloc[0])]) if len(a_res) else float("nan")
        elif col == "dg":
            c = -a
        else:
            c = float(a_res[rc].iloc[0]) if len(a_res) else float("nan")
        d = away[col].mean() if len(away) else float("nan")
        rows.append(dict(grupo="Resultados oficiales", metrica=lab, unidad=unit, better=better, a=a, b=b, nb=len(home),
                         c=c, d=d, nd=len(away)))
    v = veo[veo.jornada == jornada]
    vh = veo if not exclude else veo[veo.jornada != jornada]
    for lab, f, rcol, unit, better, block in T.METRICS:
        a = v[f].iloc[0] if len(v) else float("nan")
        c = v[rcol].iloc[0] if len(v) and rcol != T.NONE else float("nan")
        if pd.isna(a) and pd.isna(c):
            continue
        hb = vh[f].dropna()
        rows.append(dict(grupo=f"Vídeo · {block}", metrica=lab, unidad=unit, better=better, a=a,
                         b=hb.mean() if len(hb) else float("nan"), nb=len(hb), c=c, d=float("nan"), nd=0))
    return pd.DataFrame(rows)


def _cell(v, unit, n=None):
    if pd.isna(v):
        return "<span class='adv-na'>no disponible</span>"
    txt = T._fmt(round(v, 2), unit)
    return f"<div class='adv-v'>{txt}" + (f"<small>n = {n}</small>" if n is not None else "") + "</div>"


def _delta(a, b, unit, better):
    if pd.isna(a) or pd.isna(b):
        return "<span class='adv-na'>—</span>"
    diff = a - b
    if abs(diff) < 1e-9:
        return "<div class='adv-d flat'>= 0</div>"
    good = None if better is None else ((diff > 0) == better)
    cls = "flat" if good is None else ("up" if good else "down")
    pct = _pct(a, b, unit)
    sign = "▲" if diff > 0 else "▼"
    absu = f"{abs(diff):.1f}".rstrip("0").rstrip(".") + (" p.p." if unit == "%" else "")
    return f"<div class='adv-d {cls}'>{sign} {absu}" + (f"<small>{pct:+.0f}%</small>" if pct is not None else "") + "</div>"


def four_refs_html(rows, jornada, rival_short):
    head = (f"<div class='adv-row adv-head'><span>Métrica</span><span>A · PT J{jornada}</span><span>B · Media PT casa</span>"
            f"<span>A frente a B</span><span>C · {escape(rival_short)} J{jornada}</span><span>D · Media {escape(rival_short)} fuera</span>"
            f"<span>C frente a D</span></div>")
    out = [head]
    for grupo, g in rows.groupby("grupo", sort=False):
        out.append(f"<div class='adv-group'>{escape(grupo)}</div>")
        for _, r in g.iterrows():
            out.append(f"<div class='adv-row'><span class='adv-m'>{escape(r.metrica)}<small>{escape(r.unidad)}</small></span>"
                       f"{_cell(r.a, r.unidad)}{_cell(r.b, r.unidad, r.nb if pd.notna(r.b) else None)}{_delta(r.a, r.b, r.unidad, r.better)}"
                       f"{_cell(r.c, r.unidad)}{_cell(r.d, r.unidad, r.nd if pd.notna(r.d) else None)}"
                       f"{_delta(r.c, r.d, r.unidad, None)}</div>")
    return "<div class='adv-tbl'>" + "".join(out) + "</div>"


# ---------------------------------------------------------------- radares (índice explícito)
NORM_TEXT = ("Índice 0–100 = valor ÷ valor máximo de referencia de esa métrica × 100. 100 es el máximo observado en los "
             "partidos de referencia, no un ideal; 50 es la mitad de ese máximo, no igualdad. Al pasar el ratón se ve el valor real.")


RADAR_SHORT = {"Pases hacia delante acertados": "Pases adelante", "Intentos dentro del área": "Intentos en área",
               "Pases completados": "Pases compl.", "Precisión de pase": "Precisión", "Intentos de tiro": "Intentos",
               "Faltas lanzadas": "Faltas lanz.", "Saques de banda": "Saques banda", "Recuperaciones": "Recuperac.",
               "Intercepciones": "Intercepc."}


def _radar_fig(axes, traces, height=460):
    fig = go.Figure()
    fig.update_layout(**plotly_layout(height=height, margin=dict(l=88, r=88, t=24, b=24), showlegend=True,
                                      legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=.5, bgcolor="rgba(0,0,0,0)")))
    axes = [RADAR_SHORT.get(a, a) for a in axes]
    theta = axes + axes[:1]
    for name, idx, raw, units, color, fill, dash in traces:
        fig.add_scatterpolar(r=idx + idx[:1], theta=theta, name=name, mode="lines+markers", fill="toself" if fill else None,
                             fillcolor=fill, line=dict(color=color, width=2.4, dash=dash), marker=dict(size=7, color=color),
                             customdata=[[f"{T._fmt(v, u)} {'' if u == '%' else u}".strip()] for v, u in zip(raw + raw[:1], units + units[:1])],
                             hovertemplate="<b>%{theta}</b><br>" + name + ": %{customdata[0]}<br>Índice %{r:.0f}/100<extra></extra>")
    fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                 radialaxis=dict(range=[0, 105], tickvals=[25, 50, 75, 100], gridcolor=TOKENS["line"], linecolor=TOKENS["line"],
                                                 tickfont=dict(color=MUTED, size=9)),
                                 angularaxis=dict(gridcolor=TOKENS["line"], linecolor=TOKENS["line"], tickfont=dict(color=TOKENS["text"], size=11))))
    return fig


def radar_vs_average(veo, jornada, exclude=True, min_ref=2):
    """PT en la jornada frente a su media en casa. Escala: máximo de PT en casa en esa métrica."""
    axes, a_idx, a_raw, b_idx, b_raw, units, rows = [], [], [], [], [], [], []
    for lab in RADAR_PT:
        _, f, _, unit, *_ = T.METRIC_BY_LABEL[lab]
        allv = veo[f].dropna()
        val = veo.loc[veo.jornada == jornada, f]
        ref = veo.loc[(veo.jornada != jornada) if exclude else veo.index == veo.index, f].dropna()
        if val.empty or pd.isna(val.iloc[0]) or len(ref) < min_ref or allv.max() <= 0:
            continue
        mx = allv.max()
        axes.append(lab); units.append(unit)
        a_raw.append(float(val.iloc[0])); a_idx.append(100 * float(val.iloc[0]) / mx)
        b_raw.append(float(ref.mean())); b_idx.append(100 * float(ref.mean()) / mx)
        rows.append(dict(metrica=lab, valor=float(val.iloc[0]), media=float(ref.mean()), n=len(ref), maximo=float(mx)))
    if len(axes) < 3:
        return None, pd.DataFrame(rows)
    fig = _radar_fig(axes, [("Media PT en casa", b_idx, b_raw, units, "#B8661E", None, "dot"),
                            (f"Primer Toque J{jornada}", a_idx, a_raw, units, PT, "rgba(245,135,31,.20)", "solid")])
    return fig, pd.DataFrame(rows)


def radar_vs_rival(veo, jornada):
    """PT frente al rival en la jornada. Escala: máximo de ambos equipos en esa métrica en los partidos medidos."""
    axes, p_idx, p_raw, r_idx, r_raw, units, rows = [], [], [], [], [], [], []
    s = veo[veo.jornada == jornada]
    for lab in RADAR_VS:
        _, f, a, unit, *_ = T.METRIC_BY_LABEL[lab]
        if s.empty or pd.isna(s[f].iloc[0]) or pd.isna(s[a].iloc[0]):
            continue
        mx = max(veo[f].max(skipna=True), veo[a].max(skipna=True))
        if not mx or mx <= 0:
            continue
        pv, rv = float(s[f].iloc[0]), float(s[a].iloc[0])
        axes.append(lab); units.append(unit)
        p_raw.append(pv); p_idx.append(100 * pv / mx); r_raw.append(rv); r_idx.append(100 * rv / mx)
        rows.append(dict(metrica=lab, primer_toque=pv, rival=rv, maximo=float(mx)))
    if len(axes) < 3:
        return None, pd.DataFrame(rows)
    fig = _radar_fig(axes, [("Rival", r_idx, r_raw, units, RIVAL, "rgba(111,147,198,.18)", "solid"),
                            ("Primer Toque", p_idx, p_raw, units, PT, "rgba(245,135,31,.20)", "solid")])
    return fig, pd.DataFrame(rows)


# ---------------------------------------------------------------- interpretación prudente
def interpret(veo, jornada, eff_goals=None):
    """Lecturas de la jornada frente a la media del resto de partidos en casa, con cautela por muestra."""
    out = []
    ref = veo[veo.jornada != jornada]
    n = len(ref)
    cur = veo[veo.jornada == jornada]
    if cur.empty:
        return out
    cur = cur.iloc[0]
    if n < 3:
        out.append(f"<b>Muestra pequeña</b> (n = {n}): lectura orientativa.")
    for lab in ["Posesión", "Pases completados", "Precisión de pase", "Intentos de tiro", "Intentos dentro del área",
                "Recuperaciones", "Intercepciones", "Duelos", "Entradas / contactos"]:
        _, f, _, unit, *_ = T.METRIC_BY_LABEL[lab]
        r = ref[f].dropna()
        if pd.isna(cur[f]) or len(r) < 2:
            continue
        m = r.mean(); diff = cur[f] - m
        if unit == "%":
            if abs(diff) < 3:
                continue
            txt = f"{T._fmt(cur[f], unit)}, {abs(diff):.0f} p.p. {'por encima' if diff > 0 else 'por debajo'} de su media"
        else:
            pct = 100 * diff / m if m else 0
            if abs(pct) < 10:
                continue
            txt = f"{T._fmt(cur[f], unit)}, {abs(pct):.0f}% {'más' if diff > 0 else 'menos'} que su media"
        extra = " (partido más disputado, no necesariamente mejor defensa)" if lab in NEUTRAL_NOTE and diff > 0 else ""
        out.append(f"<b>{escape(lab)}</b>: {txt}.{extra}")
    if pd.notna(cur.get("intentos_favor")) and eff_goals is not None:
        g = eff_goals.get(int(jornada))
        if g is not None and cur["intentos_favor"] > 0:
            out.append(f"<b>Eficacia</b>: {g[0]} gol(es) con {int(cur['intentos_favor'])} intentos "
                       f"({100 * g[0] / cur['intentos_favor']:.0f}% de conversión de intentos).")
    pos = veo.dropna(subset=["posesion_favor_pct"])
    if len(pos) >= 3:
        seq = " → ".join(f"J{int(j)} {v:.0f}%" for j, v in zip(pos.jornada, pos.posesion_favor_pct))
        out.append(f"<b>Posesión</b>: {seq}.")
    return out


# ---------------------------------------------------------------- temporadas
def load_seasons(data_dir):
    """Registro de temporadas. Si no existe el archivo, solo la temporada actual (datos en data/)."""
    if SEASONS_FILE.exists():
        reg = pd.read_csv(SEASONS_FILE, dtype=str).fillna("")
    else:
        reg = pd.DataFrame([dict(temporada="2026/2027", carpeta=".", equipo=TEAM, estado="activa", notas="")])
    seasons = {}
    for _, r in reg.iterrows():
        base = Path(data_dir) if r.carpeta in ("", ".") else Path(data_dir) / "temporadas" / r.carpeta
        part = base / "partidos_rivales.csv"
        if not part.exists():
            continue
        adv = base / "equipo_avanzado.csv"
        clas = base / "clasificacion_liga.csv"
        seasons[r.temporada] = dict(equipo=r.equipo or TEAM, partidos=pd.read_csv(part),
                                    avanzado=pd.read_csv(adv) if adv.exists() else pd.DataFrame(),
                                    clasificacion=pd.read_csv(clas) if clas.exists() else pd.DataFrame(),
                                    estado=r.estado, notas=r.notas)
    return seasons


def season_summary(season):
    tm = team_matches(season["partidos"], season["equipo"])
    sp = split_summary(tm)
    adv = season["avanzado"]
    video = {}
    if not adv.empty:
        home_j = set(tm[tm.condicion == "Casa"].jornada)
        a = adv[pd.to_numeric(adv.jornada, errors="coerce").isin(home_j)]
        for lab in ["Posesión", "Pases completados", "Precisión de pase", "Intentos de tiro", "Ocasiones", "Córneres"]:
            f = T.METRIC_BY_LABEL[lab][1]
            if f in a.columns:
                s = pd.to_numeric(a[f], errors="coerce").dropna()
                if len(s):
                    video[lab] = (s.mean(), len(s), T.METRIC_BY_LABEL[lab][3])
    return tm, sp, video


# ---------------------------------------------------------------- renderizado
def _plot(fig, key):
    st.plotly_chart(fig, width="stretch", theme=None, config=PLOTLY_CONFIG, key=key)


def _kpi(label, value, sub, n=None):
    nn = f"<span class='n'>n = {n}</span>" if n is not None else ""
    return f"<div class='adv-kpi'><small>{escape(label)}{nn}</small><b>{value}</b><span>{escape(sub)}</span></div>"


def _f(v, d=2):
    return "—" if pd.isna(v) else f"{v:.{d}f}"


def _bullet_rows(rows, val, ref, nref, color, marker_color, stacked=False):
    """Filas visuales: barra = valor, marca = referencia, píldora = diferencia."""
    out = []
    for _, r in rows.iterrows():
        v, m = r[val], r[ref]
        if pd.isna(v) and pd.isna(m):
            continue
        top = max([x for x in (v, m) if pd.notna(x) and x > 0] + [1e-9]) * 1.15
        bar = "" if pd.isna(v) or v <= 0 else f"<i class='bl-bar' style='width:{100 * v / top:.0f}%;background:{color}'></i>"
        mk = "" if pd.isna(m) or m < 0 else f"<i class='bl-mark' style='left:{100 * m / top:.0f}%;background:{marker_color}'></i>"
        vtxt = "—" if pd.isna(v) else T._fmt(v, r.unidad)
        mtxt = "sin media" if pd.isna(m) else f"media {T._fmt(round(m, 1), r.unidad)} · n {int(r[nref])}"
        out.append(f"<div class='bl-row'><div class='bl-name'>{escape(r.metrica)}<small>{mtxt}</small></div>"
                   f"<div class='bl-val'>{vtxt}</div><div class='bl-track'>{bar}{mk}</div>{_delta(v, m, r.unidad, r.better if val == 'a' else None)}</div>")
    return f"<div class='bl-list{' stack' if stacked else ''}'>" + "".join(out) + "</div>"


BL_CSS = """<style>
.ref-chips{display:flex;flex-wrap:wrap;gap:8px;margin:2px 0 12px}
.ref-chips span{display:inline-flex;align-items:center;gap:6px;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 11px;font-size:.74rem;color:var(--text)}
.ref-chips i{width:9px;height:9px;border-radius:3px;display:inline-block}
.bl-list{display:flex;flex-direction:column}
.bl-row{display:grid;grid-template-columns:minmax(120px,1.3fr) 64px 2fr 78px;gap:12px;align-items:center;padding:9px 0;border-bottom:1px solid var(--line-soft)}
.bl-row:last-child{border-bottom:0}
.bl-name{font-size:.8rem;font-weight:700;color:var(--ink)} .bl-name small{display:block;font-size:.64rem;font-weight:500;color:var(--muted);margin-top:1px}
.bl-val{font-size:1.05rem;font-weight:850;color:var(--ink);text-align:right}
.bl-track{position:relative;height:12px;background:var(--surface-2);border-radius:6px}
.bl-bar{position:absolute;left:0;top:0;bottom:0;border-radius:6px}
.bl-mark{position:absolute;top:-4px;bottom:-4px;width:3px;border-radius:2px;margin-left:-1px}
.bl-list.stack .bl-row{grid-template-columns:1fr 54px 70px}.bl-list.stack .bl-track{grid-column:1/-1;order:5}
@media(max-width:760px){.bl-row{grid-template-columns:1fr 54px 70px}.bl-track{grid-column:1/-1;order:5}}
</style>"""


def render_prepare(veo, pt_tm, partidos, short_name, goals, show_radars=True):
    st.markdown(BL_CSS, unsafe_allow_html=True)
    st.markdown(T.section("Preparar partido · cuatro referencias", "El partido elegido frente a las medias de cada equipo."), unsafe_allow_html=True)
    opts = [int(j) for j in veo.jornada]
    c1, c2 = st.columns([1.4, 1])
    with c1:
        j = st.selectbox("Jornada", opts, index=len(opts) - 1, key="adv_j",
                         format_func=lambda x: veo.loc[veo.jornada == x, "etiqueta"].iloc[0])
    with c2:
        excl = st.toggle("Media sin esta jornada", value=True, key="adv_excl",
                         help="Compara el partido con el resto de partidos en casa, no consigo mismo.")
    rival = veo.loc[veo.jornada == j, "rival"].iloc[0]
    rshort = T.club_short(rival)
    rtm = team_matches(partidos, rival)
    away = rtm[rtm.condicion == "Fuera"]
    rows = four_refs(veo, pt_tm, rtm, j, excl)
    st.markdown(f"<div class='ref-chips'><span><i style='background:{PT}'></i>A · Primer Toque J{j}</span>"
                f"<span><i style='background:{TOKENS['ink']}'></i>B · media PT en casa</span>"
                f"<span><i style='background:{RIVAL}'></i>C · {escape(rshort)} J{j}</span>"
                f"<span><i style='background:{TOKENS['ink']}'></i>D · media {escape(rshort)} fuera ({len(away)} partidos)</span></div>",
                unsafe_allow_html=True)
    groups = [g for g in dict.fromkeys(rows.grupo) if g != "Resultados oficiales"]
    k1, k2 = st.columns([1.35, 1], gap="medium")
    with k1.container(border=True):
        st.markdown(f"<div class='eq-panel-title'>Primer Toque · J{j} frente a su media</div>"
                    "<div class='eq-panel-sub'>Barra = partido · marca blanca = media</div>", unsafe_allow_html=True)
        blocks = ["Resultados"] + [x.replace("Vídeo · ", "") for x in groups]
        g = st.segmented_control("Bloque", blocks, default="Resultados", key="adv_block") or "Resultados"
        sel = rows[rows.grupo == ("Resultados oficiales" if g == "Resultados" else f"Vídeo · {g}")]
        st.markdown(_bullet_rows(sel, "a", "b", "nb", PT, TOKENS["ink"]), unsafe_allow_html=True)
    with k2.container(border=True):
        st.markdown(f"<div class='eq-panel-title'>{escape(rshort)} · J{j} frente a su media fuera</div>"
                    "<div class='eq-panel-sub'>Resultados oficiales · sin vídeo del rival fuera de casa</div>", unsafe_allow_html=True)
        st.markdown(_bullet_rows(rows[rows.grupo == "Resultados oficiales"], "c", "d", "nd", RIVAL, TOKENS["ink"], stacked=True), unsafe_allow_html=True)
    with st.expander("Ver tabla detallada (A · B · C · D)"):
        st.markdown(four_refs_html(rows, j, rshort), unsafe_allow_html=True)

    if show_radars:
        st.markdown(T.section("Radares comparativos", "Índice 0–100 sobre el máximo registrado · pasa el ratón para ver el valor real."), unsafe_allow_html=True)
        r1, r2 = st.columns(2, gap="medium")
        with r1.container(border=True):
            st.markdown(f"<div class='eq-panel-title'>J{j} frente a su media en casa</div>", unsafe_allow_html=True)
            fig, _ = radar_vs_average(veo, j, excl)
            if fig is None:
                st.info("Datos insuficientes para el radar.")
            else:
                _plot(fig, "adv_radar_avg")
        with r2.container(border=True):
            st.markdown(f"<div class='eq-panel-title'>Primer Toque frente a {escape(rshort)}</div>", unsafe_allow_html=True)
            fig2, _ = radar_vs_rival(veo, j)
            if fig2 is None:
                st.info("Datos insuficientes para el radar.")
            else:
                _plot(fig2, "adv_radar_vs")
        with st.expander("¿Cómo se calcula?"):
            st.markdown(f"- **Radares:** {NORM_TEXT}\n"
                        "- **Diferencias:** ▲▼ valor absoluto y % sobre la referencia; en porcentajes, puntos porcentuales (p.p.). "
                        "Verde/rojo solo en métricas con dirección clara.\n"
                        "- **Muestras:** n = partidos de cada media. Del rival solo hay resultados fuera de casa ("
                        + ", ".join(f"J{x}" for x in away.jornada) + "); su vídeo existe solo del partido contra nosotros.")
    lines = interpret(veo, j, goals)
    if lines:
        st.markdown("<div class='eq-insights adv-insight'><div class='eq-insights-title'>Claves del partido</div><ul>"
                    + "".join(f"<li>{x}</li>" for x in lines[:4]) + "</ul></div>", unsafe_allow_html=True)


def fig_rival_evolution(rtm, clas, team):
    rows = clas[clas.equipo == team][["jornada", "posicion"]].apply(pd.to_numeric, errors="coerce").dropna().sort_values("jornada")
    fig = go.Figure()
    fig.update_layout(**plotly_layout(height=290, margin=dict(l=12, r=12, t=30, b=12), showlegend=False))
    if not rows.empty:
        res = rtm.set_index("jornada").reindex(rows.jornada.astype(int))
        colors = [POS if r == "V" else (MUTED if r == "E" else (NEG if r == "D" else TOKENS["line"])) for r in res.res]
        txt = [f"{int(p)}º" for p in rows.posicion]
        fig.add_scatter(x=[f"J{int(j)}" for j in rows.jornada], y=rows.posicion, mode="lines+markers+text", text=txt, textposition="top center",
                        textfont=dict(color=TOKENS["ink"], size=11), line=dict(color=RIVAL, width=2.5),
                        marker=dict(size=12, color=colors, line=dict(color=TOKENS["surface"], width=2)),
                        customdata=[[r if isinstance(r, str) else "—", c if isinstance(c, str) else "—", f"{g}–{h}" if pd.notna(g) else "—"]
                                    for r, c, g, h in zip(res.res, res.rival, res.gf, res.gc)],
                        hovertemplate="%{x} · %{y}º<br>%{customdata[0]} frente a %{customdata[1]} (%{customdata[2]})<extra></extra>")
        n = int(clas.groupby("jornada").equipo.nunique().max() or 16)
        fig.update_yaxes(autorange=False, range=[n + .6, .4], tickvals=[1, 4, 8, 12, n], ticksuffix="º")
    fig.update_xaxes(showgrid=False)
    return fig


def render_rival(veo, partidos, clas, short_name, default_rival=None):
    st.markdown(T.section("Análisis del rival", "Toda su temporada en resultados oficiales."),
                unsafe_allow_html=True)
    teams = sorted(t for t in set(partidos.local) | set(partidos.visitante) if t != TEAM)
    idx = teams.index(default_rival) if default_rival in teams else 0
    rival = st.selectbox("Rival", teams, index=idx, key="adv_rival", format_func=short_name)
    rtm = team_matches(partidos, rival)
    sp = split_summary(rtm)
    t, c, f = sp["Total"], sp["Casa"], sp["Fuera"]
    small = " · muestra pequeña" if t["n"] < 5 else ""
    st.markdown("<div class='adv-kpis'>"
                + _kpi("Puntos por partido", _f(t["ppg"]), f"{t['pts']} pts · {t['v']}V-{t['e']}E-{t['dd']}D{small}", t["n"])
                + _kpi("Goles marcados / partido", _f(t["gf_pg"]), f"{t['gf']} goles en total", t["n"])
                + _kpi("Goles encajados / partido", _f(t["gc_pg"]), f"{t['gc']} goles en total", t["n"])
                + _kpi("Diferencia de goles", f"{t['dg']:+d}", "Toda la temporada", t["n"])
                + _kpi("Como local · pts/partido", _f(c["ppg"]), f"{c['v']}V-{c['e']}E-{c['dd']}D · GF {_f(c['gf_pg'])} · GC {_f(c['gc_pg'])}", c["n"])
                + _kpi("Como visitante · pts/partido", _f(f["ppg"]), f"{f['v']}V-{f['e']}E-{f['dd']}D · GF {_f(f['gf_pg'])} · GC {_f(f['gc_pg'])}", f["n"])
                + "</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.3, 1], gap="medium")
    with c1.container(border=True):
        st.markdown("<div class='eq-panel-title'>Evolución en la clasificación</div><div class='eq-panel-sub'>Verde victoria · gris empate · rojo derrota</div>", unsafe_allow_html=True)
        _plot(fig_rival_evolution(rtm, clas, rival), "adv_rival_evo")
    with c2.container(border=True):
        st.markdown("<div class='eq-panel-title'>Resultados de la temporada</div>", unsafe_allow_html=True)
        rows = "".join(f"<div class='mini-item'><span><b>J{r.jornada}</b> · {'🏠' if r.condicion == 'Casa' else '✈️'} {escape(short_name(r.rival))}</span>"
                       f"<span><b>{r.gf}–{r.gc}</b> <span class='res-pill' style='display:inline-grid;background:{POS if r.res == 'V' else (MUTED if r.res == 'E' else NEG)}'>{r.res}</span></span></div>"
                       for r in rtm.itertuples())
        st.markdown(f"<div class='mini-list'>{rows}</div>", unsafe_allow_html=True)
    vs = rtm[rtm.rival == TEAM]
    txt = " · ".join(f"J{r.jornada} ({'en su campo' if r.condicion == 'Casa' else 'en nuestro campo'}): {r.gf}–{r.gc} para {escape(short_name(rival))}" for r in vs.itertuples())
    st.markdown(f"<div class='adv-note'><b>Contra Primer Toque</b>: {txt or 'todavía no se han enfrentado esta temporada.'}</div>", unsafe_allow_html=True)
    v = veo[veo.rival == rival]
    if v.empty:
        st.caption("Sin vídeo de este rival (solo se graban nuestros partidos en casa).")
    else:
        vr = v.iloc[0]
        items = [(lab, vr[f], vr[a], unit) for lab, f, a, unit, *_ in T.METRICS if a != T.NONE and pd.notna(vr[a])]
        with st.container(border=True):
            st.markdown(f"<div class='eq-panel-title'>Estadísticas de vídeo de {escape(short_name(rival))} · J{int(vr.jornada)} en nuestro campo</div>"
                        "<div class='eq-panel-sub'>Un solo partido, no es su media.</div>", unsafe_allow_html=True)
            rows = [f"<div class='vs-row vs-head'><span>Métrica</span><span>Primer Toque</span><span>{escape(short_name(rival))}</span></div>"]
            for lab, pv, rvv, unit in items:
                top = max(pv if pd.notna(pv) else 0, rvv, 1e-9)
                bar = lambda v, cls: (f"<div class='vs-bar {cls}'><b>{T._fmt(v, unit)}</b>"
                                      + ("" if pd.isna(v) else f"<i style='width:{100 * v / top * .7:.0f}%'></i>") + "</div>")
                rows.append(f"<div class='vs-row'><span class='m'>{escape(lab)}</span>{bar(pv, 'pt')}{bar(rvv, 'rv')}</div>")
            st.markdown("<div class='adv-tbl'>" + "".join(rows) + "</div>", unsafe_allow_html=True)


def _metric_options():
    return [m[0] for m in RESULT_METRICS] + [m[0] for m in T.METRICS]


def render_lab(veo, pt_tm, seasons):
    st.markdown(T.section("Laboratorio de comparación", "Una métrica, cinco formas de compararla."),
                unsafe_allow_html=True)
    metric = st.selectbox("Métrica", _metric_options(), key="lab_metric")
    is_result = metric in [m[0] for m in RESULT_METRICS]
    modes = ["Jornada frente a jornada", "Jornada frente a la media", "Primer Toque frente al rival", "Local frente a visitante", "Temporada frente a temporada"]
    mode = st.pills("Comparación", modes, default=modes[1], key="lab_mode") or modes[1]
    if is_result:
        _, col, unit, better = next(m for m in RESULT_METRICS if m[0] == metric)
        data = pt_tm.assign(eje=lambda d: "J" + d.jornada.astype(str) + "<br>" + d.rival.map(T.club_short), etiqueta=lambda d: "J" + d.jornada.astype(str))
        val, rv = data[col], None
        if col in ("gf", "gc"):
            rv = data["gc" if col == "gf" else "gf"]
        scope = f"Resultados oficiales · {len(data)} partidos"
    else:
        _, f, a, unit, better, _ = T.METRIC_BY_LABEL[metric]
        data = veo.dropna(subset=[f])
        val, rv = data[f], (data[a] if a != T.NONE and data[a].notna().any() else None)
        scope = f"Estadística de vídeo · {len(data)} partidos en casa"
    st.caption(scope)
    if data.empty:
        st.info("No hay datos de esta métrica.")
        return
    fig = go.Figure()
    fig.update_layout(**plotly_layout(height=340, margin=dict(l=12, r=12, t=40, b=12), barcornerradius=4, bargap=.3))
    if mode == "Jornada frente a jornada":
        js = list(data.jornada.astype(int))
        k1, k2 = st.columns(2)
        ja = k1.selectbox("Jornada A", js, index=0, key="lab_ja")
        jb = k2.selectbox("Jornada B", js, index=len(js) - 1, key="lab_jb")
        sel = data[data.jornada.isin([ja, jb])]
        fig.add_bar(x=sel.eje, y=val[sel.index], name="Primer Toque", marker_color=PT, text=[T._fmt(v, unit) for v in val[sel.index]], textposition="outside", cliponaxis=False)
        if rv is not None:
            fig.add_bar(x=sel.eje, y=rv[sel.index], name="Rival", marker_color=RIVAL, text=[T._fmt(v, unit) for v in rv[sel.index]], textposition="outside", cliponaxis=False)
        a_, b_ = val[data.jornada == ja].iloc[0], val[data.jornada == jb].iloc[0]
        st.markdown(f"<div class='adv-note'>Primer Toque: J{ja} {T._fmt(a_, unit)} → J{jb} {T._fmt(b_, unit)} · "
                    f"variación {_delta(b_, a_, unit, better)}</div>", unsafe_allow_html=True)
    elif mode == "Jornada frente a la media":
        m = val.mean()
        colors = [PT if v >= m else "#8A4A12" for v in val]
        fig.add_bar(x=data.eje, y=val, name="Primer Toque", marker_color=colors, text=[T._fmt(v, unit) for v in val], textposition="outside", cliponaxis=False,
                    customdata=[f"{v - m:+.1f} frente a la media" for v in val], hovertemplate="%{x}<br>%{y} · %{customdata}<extra></extra>")
        fig.add_hline(y=m, line=dict(color=TOKENS["ink"], dash="dot", width=1.2), annotation_text=f"Media {m:.1f} (n = {len(val)})",
                      annotation_font=dict(color=TOKENS["ink"], size=11), annotation_position="top left")
        fig.update_layout(showlegend=False)
    elif mode == "Primer Toque frente al rival":
        if rv is None or rv.dropna().empty:
            st.info("Esta métrica no tiene dato del rival: Veo solo la ofrece para Primer Toque.")
            return
        lab = data.eje
        fig.add_bar(y=lab, x=-rv, orientation="h", name="Rival", marker_color=RIVAL, text=[T._fmt(v, unit) for v in rv], textposition="outside", cliponaxis=False,
                    customdata=rv, hovertemplate="%{y}<br>Rival: %{customdata}<extra></extra>")
        fig.add_bar(y=lab, x=val, orientation="h", name="Primer Toque", marker_color=PT, text=[T._fmt(v, unit) for v in val], textposition="outside", cliponaxis=False,
                    hovertemplate="%{y}<br>Primer Toque: %{x}<extra></extra>")
        mx = float(max(val.max(), rv.max())) * 1.3
        fig.update_layout(barmode="relative", height=110 + 60 * len(data))
        fig.update_xaxes(range=[-mx, mx], showticklabels=False, zeroline=True, zerolinewidth=1.5)
        fig.update_yaxes(autorange="reversed")
    elif mode == "Local frente a visitante":
        if not is_result:
            st.info("Las estadísticas de vídeo solo existen de los partidos en casa: no hay base para comparar local frente a visitante. "
                    "Elige una métrica de resultados (goles, puntos o diferencia).")
            return
        g = data.groupby("condicion")[col].agg(["mean", "count"]).reindex(["Casa", "Fuera"])
        fig.add_bar(x=[f"{i}<br>n = {int(c)}" for i, c in zip(g.index, g["count"].fillna(0))], y=g["mean"], marker_color=[PT, "#8A4A12"],
                    text=[_f(v) for v in g["mean"]], textposition="outside", cliponaxis=False, showlegend=False)
        st.caption("Media por partido en cada condición; n = partidos que intervienen.")
    else:
        if len(seasons) < 2:
            st.info(f"Solo hay datos de la temporada {', '.join(seasons) or '2026/2027'}. La comparación entre temporadas se activará al importar otra temporada.")
            return
        rows = []
        for name, s in seasons.items():
            tm, sp, video = season_summary(s)
            if is_result:
                rows.append((name, tm[col].mean(), len(tm)))
            elif metric in video:
                rows.append((name, video[metric][0], video[metric][1]))
        fig.add_bar(x=[f"{r[0]}<br>n = {r[2]}" for r in rows], y=[r[1] for r in rows], marker_color=PT, text=[_f(r[1]) for r in rows],
                    textposition="outside", cliponaxis=False, showlegend=False)
    fig.update_yaxes(rangemode="tozero")
    _plot(fig, "lab_fig")


def render_seasons(seasons, short_name):
    st.markdown(T.section("Comparador de temporadas", "Elige una o dos temporadas."),
                unsafe_allow_html=True)
    names = list(seasons)
    sel = st.multiselect("Temporadas", names, default=names[-2:], max_selections=2, key="adv_seasons")
    if not sel:
        st.info("Selecciona una o dos temporadas.")
        return
    cols = st.columns(len(sel), gap="medium")
    summaries = {}
    for c, name in zip(cols, sel):
        tm, sp, video = season_summary(seasons[name])
        summaries[name] = (tm, sp, video)
        t, h, a = sp["Total"], sp["Casa"], sp["Fuera"]
        with c:
            st.markdown(f"<div class='eq-panel-title'>Temporada {escape(name)}</div>", unsafe_allow_html=True)
            st.markdown("<div class='adv-kpis' style='grid-template-columns:repeat(2,minmax(0,1fr))'>"
                        + _kpi("Puntos por partido", _f(t["ppg"]), f"{t['pts']} pts · {t['v']}V-{t['e']}E-{t['dd']}D", t["n"])
                        + _kpi("Diferencia de goles", f"{t['dg']:+d}", f"{t['gf']} marcados · {t['gc']} encajados", t["n"])
                        + _kpi("Goles marcados / partido", _f(t["gf_pg"]), "Rendimiento ofensivo", t["n"])
                        + _kpi("Goles encajados / partido", _f(t["gc_pg"]), "Rendimiento defensivo", t["n"])
                        + _kpi("En casa", f"{h['v']}V-{h['e']}E-{h['dd']}D", f"{_f(h['ppg'])} pts/partido", h["n"])
                        + _kpi("Fuera", f"{a['v']}V-{a['e']}E-{a['dd']}D", f"{_f(a['ppg'])} pts/partido", a["n"])
                        + "</div>", unsafe_allow_html=True)
            if video:
                st.markdown("<div class='eq-panel-sub'>Estadísticas de vídeo (media en casa)</div>"
                            + "<div class='adv-kpis' style='grid-template-columns:repeat(3,minmax(0,1fr))'>"
                            + "".join(_kpi(k, T._fmt(round(v[0], 1), v[2]), "por partido" if v[2] != "%" else "media", v[1]) for k, v in video.items())
                            + "</div>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.update_layout(**plotly_layout(height=300, margin=dict(l=12, r=12, t=40, b=12)))
    for i, (name, (tm, sp, video)) in enumerate(summaries.items()):
        fig.add_scatter(x=[f"J{j}" for j in tm.jornada], y=tm.pts.cumsum(), name=name, mode="lines+markers",
                        line=dict(color=PT if i == len(summaries) - 1 else "#B8661E", width=2.5, dash="solid" if i == len(summaries) - 1 else "dot"),
                        hovertemplate=name + " · %{x}: %{y} pts<extra></extra>")
    fig.update_yaxes(title=dict(text="Puntos acumulados", font=dict(size=11, color=MUTED)), rangemode="tozero")
    with st.container(border=True):
        st.markdown("<div class='eq-panel-title'>Evolución del equipo</div><div class='eq-panel-sub'>Puntos acumulados jornada a jornada.</div>", unsafe_allow_html=True)
        _plot(fig, "adv_season_evo")
    if len(names) < 2:
        st.caption("Solo hay datos de 2026/2027. La comparación se activará al importar otra temporada (ver data/temporadas/LEEME.md).")


# ================================================================ NIVELES DE LECTURA (UX)
LEVEL_CSS = """<style>
.sum-head{display:flex;align-items:center;gap:12px;flex-wrap:wrap;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:12px 16px;margin:4px 0 14px}
.sum-head .j{background:var(--surface-3);color:var(--ink);font-weight:800;border-radius:9px;padding:4px 10px;font-size:.85rem}
.sum-head .t{font-size:1.05rem;font-weight:800;color:var(--ink)} .sum-head .s{font-size:1.4rem;font-weight:900;color:var(--ink);margin-left:auto}
.sum-head .r{font-weight:900;border-radius:8px;padding:3px 9px;font-size:.8rem;color:#0A0E14}
.sum-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:0 0 12px}
.sum-card{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:13px 14px;display:flex;flex-direction:column;gap:4px}
.sum-card .l{font-size:.68rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.sum-card .v{font-size:1.75rem;font-weight:900;color:var(--ink);letter-spacing:-.02em;line-height:1.1}
.sum-card .m{font-size:.72rem;color:var(--text)}
.sum-card .d{align-self:flex-start;font-size:.78rem;font-weight:800;border-radius:999px;padding:2px 9px}
.sum-card .d.up{color:var(--pos);background:rgba(43,196,138,.12)} .sum-card .d.down{color:var(--neg);background:rgba(240,89,106,.12)}
.sum-card .d.flat{color:var(--text);background:var(--surface-2)}
.sum-card .i{font-size:.74rem;color:var(--ink);line-height:1.35;border-top:1px solid var(--line-soft);padding-top:6px;margin-top:2px}
.q-title{font-size:1rem;font-weight:800;color:var(--ink);margin:2px 0 2px}
.q-sub{font-size:.76rem;color:var(--muted);margin-bottom:6px}
@media(max-width:1100px){.sum-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:700px){.sum-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.sum-card .v{font-size:1.45rem}}
</style>"""

# (etiqueta, frase si sube, frase si baja); None en dirección = métrica neutra
SUMMARY = [
    ("Posesión", "Más posesión que su media habitual", "Menos posesión que su media habitual"),
    ("Precisión de pase", "Pase más preciso que su media", "Pase menos preciso que su media"),
    ("Pases completados", "Más pases completados que su media", "Menos pases completados que su media"),
    ("Pases hacia delante acertados", "Más progresión con pase que su media", "Menos progresión con pase que su media"),
    ("Intentos de tiro", "Más intentos de tiro que su media", "Menos intentos de tiro que su media"),
    ("Intentos dentro del área", "Más intentos dentro del área que su media", "Menos intentos dentro del área que su media"),
    ("Ocasiones", "Más ocasiones que su media", "Menos ocasiones que su media"),
    ("Córneres", "Más córneres a favor que su media", "Menos córneres a favor que su media"),
    ("Recuperaciones", "Más recuperaciones que su media", "Menos recuperaciones que su media"),
    ("Duelos", "Partido más disputado que la media (más duelos)", "Partido menos disputado que la media (menos duelos)"),
]


def _es(v, d=1):
    """Número con coma decimal y sin ceros sobrantes."""
    s = f"{v:.{d}f}".rstrip("0").rstrip(".") if d else f"{v:.0f}"
    return s.replace(".", ",")


def summary_rows(veo, jornada, exclude=True):
    """Indicadores del nivel 1: valor, media en casa (n), diferencia y lectura."""
    out = []
    cur = veo[veo.jornada == jornada]
    ref = veo[veo.jornada != jornada] if exclude else veo
    for lab, up_txt, down_txt in SUMMARY:
        _, f, _, unit, better, _ = T.METRIC_BY_LABEL[lab]
        v = cur[f].iloc[0] if len(cur) else float("nan")
        r = ref[f].dropna()
        if pd.isna(v):
            continue
        m = r.mean() if len(r) else float("nan")
        row = dict(metrica=lab, unidad=unit, better=better, valor=v, media=m, n=len(r), diff=float("nan"), pct=None, texto="Sin media suficiente para comparar")
        if len(r) >= 2:
            diff = v - m
            row["diff"] = diff
            row["pct"] = None if unit == "%" or m <= 0 else 100 * diff / m
            small = abs(diff) < 3 if unit == "%" else (m > 0 and abs(100 * diff / m) < 10)
            row["texto"] = "En línea con su media habitual" if small else (up_txt if diff > 0 else down_txt)
        out.append(row)
    return out


def summary_cards_html(rows):
    cards = []
    for r in rows:
        unit = r["unidad"]
        val = _es(r["valor"], 0 if unit != "%" else 0) + (" %" if unit == "%" else "")
        if pd.isna(r["diff"]):
            mtxt, dtxt, cls = "Sin media de referencia", "", "flat"
        else:
            mtxt = f"Media en casa: {_es(r['media'])}{' %' if unit == '%' else ''} · {r['n']} partidos"
            sign = "+" if r["diff"] > 0 else "−"
            if unit == "%":
                dtxt = f"{sign}{_es(abs(r['diff']))} p.p."
            else:
                dtxt = f"{sign}{_es(abs(r['diff']))}" + (f" ({sign}{_es(abs(r['pct']), 0)} %)" if r["pct"] is not None else "")
            small = r["texto"].startswith("En línea")
            good = None if r["better"] is None or small else ((r["diff"] > 0) == r["better"])
            cls = "flat" if good is None else ("up" if good else "down")
        cards.append(f"<div class='sum-card'><span class='l'>{escape(r['metrica'])}</span><span class='v'>{val}</span>"
                     f"<span class='m'>{escape(mtxt)}</span>" + (f"<span class='d {cls}'>{dtxt}</span>" if dtxt else "")
                     + f"<span class='i'>{escape(r['texto'])}</span></div>")
    return "<div class='sum-grid'>" + "".join(cards) + "</div>"


def _jornada_picker(veo, key):
    opts = [int(j) for j in veo.jornada]
    return st.selectbox("Partido", opts, index=len(opts) - 1, key=key, format_func=lambda x: veo.loc[veo.jornada == x, "etiqueta"].iloc[0])


SUMMARY_CSS = """<style>
.mr-board{background:linear-gradient(180deg,#141C2A,#101620);border:1px solid var(--line);box-shadow:inset 0 2px 0 var(--pt);border-radius:18px;padding:16px 18px;margin:4px 0 12px}
.mr-top{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:14px}
.mr-team{font-size:1.05rem;font-weight:850;color:var(--ink)} .mr-team.r{text-align:right}
.mr-team small{display:block;font-size:.68rem;font-weight:600;color:var(--muted);letter-spacing:.06em;text-transform:uppercase}
.mr-score{font-size:2.3rem;font-weight:900;color:var(--ink);letter-spacing:-.02em;text-align:center;line-height:1}
.mr-score small{display:block;font-size:.66rem;font-weight:800;letter-spacing:.1em;margin-top:6px}
.mr-ev{display:grid;grid-template-columns:1fr 1fr;gap:6px 18px;margin-top:14px;padding-top:12px;border-top:1px solid var(--line-soft)}
.mr-ev div{font-size:.78rem;color:var(--text)} .mr-ev .r{text-align:right}
.mr-ev b{color:var(--ink);font-weight:800;margin-right:4px}
.mr-text{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--pt);border-radius:14px;padding:12px 16px;margin:0 0 12px;font-size:.88rem;line-height:1.55;color:var(--text)}
.mr-text b{color:var(--ink)}
.h2h{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:10px 16px;margin:0 0 12px}
.h2h-head{display:flex;justify-content:space-between;font-size:.7rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;padding:4px 0 8px}
.h2h-head .pt{color:var(--pt)} .h2h-head .rv{color:var(--rival)}
.h2h-row{display:grid;grid-template-columns:52px 1fr 150px 1fr 52px;align-items:center;gap:10px;padding:6px 0}
.h2h-row .v{font-size:.95rem;font-weight:850;color:var(--ink)} .h2h-row .v.r{text-align:right}
.h2h-row .lab{text-align:center;font-size:.74rem;font-weight:700;color:var(--text)}
.h2h-row .lab small{display:block;font-size:.6rem;font-weight:500;color:var(--muted)}
.h2h-bar{height:9px;background:var(--surface-2);border-radius:5px;display:flex;overflow:hidden}
.h2h-bar.l{justify-content:flex-end} .h2h-bar i{display:block;height:100%;border-radius:5px}
@media(max-width:700px){.h2h-row{grid-template-columns:40px 1fr 92px 1fr 40px;gap:6px}.mr-score{font-size:1.8rem}.mr-team{font-size:.86rem}}
</style>"""

H2H = ["Posesión", "Pases totales", "Pases completados", "Precisión de pase", "Tiros", "Ocasiones",
       "Córneres", "Faltas lanzadas", "Faltas cometidas", "Saques de banda"]


def h2h_html(pairs, left="Primer Toque", right="Rival", note=None):
    """Cara a cara estilo retransmisión: cada fila reparte la barra según el peso de cada equipo."""
    rows = [f"<div class='h2h-head'><span class='pt'>{escape(left)}</span><span class='rv'>{escape(right)}</span></div>"]
    for lab, unit, pv, rv, n in pairs:
        tot = pv + rv
        lp, rp = (100 * pv / tot, 100 * rv / tot) if tot else (0, 0)
        sub = f"<small>{escape(note.format(n=n))}</small>" if note else ""
        rows.append(f"<div class='h2h-row'><span class='v'>{T._fmt(round(pv, 1), unit)}</span>"
                    f"<div class='h2h-bar l'><i style='width:{lp:.0f}%;background:{PT}'></i></div>"
                    f"<span class='lab'>{escape(lab)}{sub}</span>"
                    f"<div class='h2h-bar'><i style='width:{rp:.0f}%;background:{RIVAL}'></i></div>"
                    f"<span class='v r'>{T._fmt(round(rv, 1), unit)}</span></div>")
    return "<div class='h2h'>" + "".join(rows) + "</div>"


def _match_pairs(row):
    out = []
    for lab in H2H:
        _, f, a, unit, *_ = T.METRIC_BY_LABEL[lab]
        if pd.notna(row[f]) and pd.notna(row[a]):
            out.append((lab, unit, float(row[f]), float(row[a]), 1))
    return out


def _avg_pairs(veo):
    out = []
    for lab in H2H:
        _, f, a, unit, *_ = T.METRIC_BY_LABEL[lab]
        both = veo.dropna(subset=[f, a])
        if len(both):
            out.append((lab, unit, both[f].mean(), both[a].mean(), len(both)))
    return out


def _events_html(events, jornada, rival):
    ev = events[(events.equipo == TEAM) & (pd.to_numeric(events.jornada, errors="coerce") == jornada)].copy()
    ev["minuto"] = pd.to_numeric(ev.minuto, errors="coerce")
    cells = []  # cronología única: Primer Toque a la izquierda, rival a la derecha
    for _, e in ev.sort_values("minuto").iterrows():
        m = f"{int(e.minuto)}'" if pd.notna(e.minuto) else ""
        if e.tipo in ("gol", "penalti_gol"):
            cells.append(f"<div>⚽ <b>{m}</b>{escape(str(e.jugador))}{' (pen.)' if e.tipo == 'penalti_gol' else ''}</div><div class='r'></div>")
        elif e.tipo == "gol_contra":
            who = str(e.jugador)
            who = "" if (who == rival or "C.F." in who or "U.D." in who) else who
            cells.append(f"<div></div><div class='r'>{escape(who)} <b>{m}</b> ⚽</div>")
        elif e.tipo in ("amarilla", "roja", "doble_amarilla"):
            icon = {"amarilla": "🟨", "roja": "🟥", "doble_amarilla": "🟨🟥"}[e.tipo]
            cells.append(f"<div>{icon} <b>{m}</b>{escape(str(e.jugador))}</div><div class='r'></div>")
    return "<div class='mr-ev'>" + "".join(cells) + "</div>" if cells else ""


def match_text(rows, row, result, rshort):
    """Resumen escrito con datos reales: resultado, balón, finalización y lo más destacado frente a la media."""
    by = {r["metrica"]: r for r in rows}
    gf, gc = result
    res = "Victoria" if gf > gc else ("Empate" if gf == gc else "Derrota")
    parts = [f"<b>{res} {gf}–{gc}</b> ante {escape(rshort)}."]
    if pd.notna(row.posesion_favor_pct) and pd.notna(row.posesion_rival_pct):
        rel = "más balón que" if row.posesion_favor_pct > row.posesion_rival_pct else ("el mismo balón que" if row.posesion_favor_pct == row.posesion_rival_pct else "menos balón que")
        txt = f"Primer Toque tuvo {rel} el rival ({T._fmt(row.posesion_favor_pct, '%')} frente a {T._fmt(row.posesion_rival_pct, '%')})"
        p = by.get("Posesión")
        if p and pd.notna(p["diff"]) and not p["texto"].startswith("En línea"):
            txt += f", {'por encima' if p['diff'] > 0 else 'por debajo'} de su media en casa ({_es(p['media'])} %)"
        parts.append(txt + ".")
    if pd.notna(row.intentos_favor):
        inside = f", {int(row.intentos_dentro_area_favor)} dentro del área" if pd.notna(row.intentos_dentro_area_favor) else ""
        parts.append(f"Generó <b>{int(row.intentos_favor)} intentos</b>{inside}, y marcó {gf} gol{'es' if gf != 1 else ''}.")
    scored = [r for r in rows if r["better"] is not None and pd.notna(r["diff"]) and not r["texto"].startswith("En línea")
              and r["metrica"] not in ("Posesión",)]
    rel = lambda r: abs(r["diff"]) / 10 if r["unidad"] == "%" else abs(r["pct"] or 0) / 100
    ups = sorted([r for r in scored if (r["diff"] > 0) == r["better"]], key=rel, reverse=True)[:2]
    downs = sorted([r for r in scored if (r["diff"] > 0) != r["better"]], key=rel, reverse=True)[:2]
    fmt = lambda r: f"{r['metrica'].lower()} ({'+' if r['diff'] > 0 else '−'}{_es(abs(r['diff']))}{' p.p.' if r['unidad'] == '%' else ''})"
    if ups:
        parts.append("Mejor que su media en " + " y ".join(fmt(r) for r in ups) + ".")
    if downs:
        parts.append("Por debajo en " + " y ".join(fmt(r) for r in downs) + ".")
    return " ".join(parts)


def avg_cards_html(veo):
    cards = []
    for lab, *_ in SUMMARY:
        _, f, _, unit, *_ = T.METRIC_BY_LABEL[lab]
        s = veo.dropna(subset=[f])
        if s.empty:
            continue
        best = s.loc[s[f].idxmax()]
        val = _es(s[f].mean()) + (" %" if unit == "%" else "")
        rng = f"Rango: {_es(s[f].min())}–{_es(s[f].max())}{' %' if unit == '%' else ''} · {len(s)} partidos"
        cards.append(f"<div class='sum-card'><span class='l'>{escape(lab)}</span><span class='v'>{val}</span>"
                     f"<span class='m'>{escape(rng)}</span><span class='i'>Máximo en J{int(best.jornada)} ({escape(T.club_short(best.rival))})</span></div>")
    return "<div class='sum-grid'>" + "".join(cards) + "</div>"


def render_match_summary(veo, pt_tm, goals, pending_note, events=None):
    """Nivel 1: ficha del partido (o de la media en casa) y comparación con la media habitual."""
    st.markdown(LEVEL_CSS + SUMMARY_CSS, unsafe_allow_html=True)
    jors = [int(j) for j in veo.jornada]
    opts = jors + ["media"]
    label = lambda x: (f"Media en casa · {len(jors)} partidos ({', '.join(f'J{j}' for j in jors)})" if x == "media"
                       else veo.loc[veo.jornada == x, "etiqueta"].iloc[0])
    c1, c2 = st.columns([1.5, 1])
    with c1:
        j = st.selectbox("Partido", opts, index=len(jors) - 1, key="sum_j", format_func=label)
    if j == "media":
        home = pt_tm[(pt_tm.condicion == "Casa") & pt_tm.jornada.isin(jors)]
        v, e, d = (home.res == "V").sum(), (home.res == "E").sum(), (home.res == "D").sum()
        st.markdown(f"<div class='mr-board'><div class='mr-top'><div class='mr-team'><small>Media en casa</small>Primer Toque</div>"
                    f"<div class='mr-score'>{_es(home.gf.mean(), 2)}–{_es(home.gc.mean(), 2)}<small>GOLES POR PARTIDO</small></div>"
                    f"<div class='mr-team r'><small>{len(home)} partidos</small>{v}V · {e}E · {d}D</div></div></div>", unsafe_allow_html=True)
        st.markdown("<div class='q-title'>Cara a cara medio</div><div class='q-sub'>Media por partido de cada equipo en los partidos con dato de ambos.</div>",
                    unsafe_allow_html=True)
        st.markdown(h2h_html(_avg_pairs(veo), "Primer Toque", "Rivales", note="n = {n}"), unsafe_allow_html=True)
        st.markdown("<div class='q-title'>Indicadores medios</div><div class='q-sub'>Media, rango y mejor partido de Primer Toque.</div>", unsafe_allow_html=True)
        st.markdown(avg_cards_html(veo), unsafe_allow_html=True)
        return
    with c2:
        excl = st.toggle("Excluir este partido de la media", value=False, key="sum_excl",
                         help="Por defecto, la media incluye todos los partidos en casa con vídeo.")
    row = veo[veo.jornada == j].iloc[0]
    rshort = T.club_short(row.rival)
    res = pt_tm[pt_tm.jornada == j]
    rows = summary_rows(veo, j, excl)
    if len(res):
        r = res.iloc[0]
        col = {"V": POS, "E": MUTED, "D": NEG}[r.res]
        word = {"V": "VICTORIA", "E": "EMPATE", "D": "DERROTA"}[r.res]
        ev = _events_html(events, j, row.rival) if events is not None else ""
        st.markdown(f"<div class='mr-board'><div class='mr-top'><div class='mr-team'><small>J{j} · en casa</small>Primer Toque</div>"
                    f"<div class='mr-score'>{r.gf}–{r.gc}<small style='color:{col}'>{word}</small></div>"
                    f"<div class='mr-team r'><small>Rival</small>{escape(rshort)}</div></div>{ev}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='mr-text'>{match_text(rows, row, (int(r.gf), int(r.gc)), rshort)}</div>", unsafe_allow_html=True)
    pairs = _match_pairs(row)
    if pairs:
        st.markdown("<div class='q-title'>Cara a cara</div><div class='q-sub'>Estadísticas de vídeo de los dos equipos en este partido.</div>", unsafe_allow_html=True)
        st.markdown(h2h_html(pairs, "Primer Toque", rshort), unsafe_allow_html=True)
    st.markdown("<div class='q-title'>Frente a su media en casa</div><div class='q-sub'>Valor del partido, media habitual, diferencia y lectura.</div>",
                unsafe_allow_html=True)
    st.markdown(summary_cards_html(rows), unsafe_allow_html=True)
    if j == 7:
        st.caption(pending_note)
    with st.expander("¿Cómo leer este resumen?"):
        st.markdown("- **Media en casa**: media de Primer Toque en sus partidos en casa con vídeo (n = partidos); "
                    "el interruptor permite excluir el partido elegido. En el desplegable puedes elegir también la **media**.\n"
                    "- **p.p.** (puntos porcentuales) se usa en métricas que ya son porcentajes (posesión, precisión). "
                    "En el resto, la diferencia va en unidades y entre paréntesis en %.\n"
                    "- **Verde/rojo** solo cuando la dirección es clara; **gris** en métricas neutras (duelos) o diferencias pequeñas.\n"
                    "- **Cara a cara**: la barra de cada fila se reparte según el peso de cada equipo en esa estadística.\n"
                    "- Con 3–4 partidos, las medias son orientativas.")


def _q(title, sub=""):
    st.markdown(f"<div class='q-title'>{escape(title)}</div>" + (f"<div class='q-sub'>{escape(sub)}</div>" if sub else ""), unsafe_allow_html=True)


def render_areas(veo, goals, eff, share_all, pending_note, production_html):
    """Nivel 2: una pregunta y un gráfico principal por área; el resto en «Más indicadores»."""
    st.markdown(LEVEL_CSS, unsafe_allow_html=True)
    areas = ["Posesión y control", "Construcción y pases", "Ataque y finalización", "Duelos y defensa", "Balón parado"]
    area = st.segmented_control("Área", areas, default=areas[0], key="area_sel") or areas[0]

    def share(block, key, title):
        tbl = share_all[share_all.block == block]
        if tbl.empty:
            return
        _q(title, "Media por partido de cada equipo · la línea marca el 50 %.")
        _plot(T.fig_share(tbl), key)

    with st.container(border=True):
        if area == "Posesión y control":
            _q("¿Quién tuvo más el balón?", "Posesión de cada equipo según Veo, partido a partido. La línea marca el 50 %.")
            _plot(T.fig_possession(veo), "eq_possession")
            with st.expander("Más indicadores de posesión"):
                zf = T.fig_zones(veo)
                if zf is not None:
                    _q("¿Por qué zonas circula nuestro pase?", "Pases completados por tercio del campo (y posesión por zonas cuando Veo la aporta).")
                    _plot(zf, "eq_zones")
                share("Posesión", "eq_share_pos", "Media de posesión de cada equipo")
        elif area == "Construcción y pases":
            _q("¿Cuánto pasamos y con qué acierto?", "Pases totales, completados y precisión de cada equipo. Cada panel tiene su propia escala.")
            _plot(T.fig_multiples(veo, ["Pases totales", "Pases completados", "Precisión de pase"], cols=3), "eq_pass_multi")
            with st.expander("Más indicadores de pase"):
                f = T.fig_forward(veo)
                if f is not None:
                    _q("¿Progresamos con el pase?", "Pases hacia delante acertados sobre intentados (Primer Toque).")
                    _plot(f, "eq_forward")
                share("Pase", "eq_share_pass", "Qué parte del pase fue nuestra")
        elif area == "Ataque y finalización":
            _q("¿Desde dónde intentamos marcar?", "Intentos de tiro dentro y fuera del área (incluyen los goles) y goles del partido.")
            f = T.fig_attempts(veo, goals)
            if f is None:
                st.info("Sin registros de intentos.")
            else:
                _plot(f, "eq_attempts")
            with st.expander("Más indicadores de ataque"):
                if not eff.empty and (eff.conv_pt.notna().any() or eff.conv_rv.notna().any()):
                    _q("¿Cuántos goles conseguimos por cada tiro?", "Conversión = goles ÷ tiros × 100.")
                    _plot(T.fig_efficiency(eff), "eq_eff")
                _q("¿Cuánto producimos en ataque?", "Tiros, ocasiones, regates y asistencias. Cada panel tiene su propia escala.")
                _plot(T.fig_multiples(veo, ["Tiros", "Ocasiones", "Regates", "Asistencias"], cols=2), "eq_att_multi")
                st.caption(pending_note)
                share("Ataque", "eq_share_att", "Qué parte del ataque fue nuestra")
        elif area == "Duelos y defensa":
            _q("¿Cuánta actividad defensiva tuvimos?", "Volumen por partido. Más duelos o entradas no significa defender mejor: depende del partido.")
            _plot(T.fig_multiples(veo, ["Duelos", "Entradas / contactos", "Recuperaciones", "Intercepciones"], cols=2), "eq_def_multi")
            with st.expander("Más indicadores defensivos"):
                _q("¿Cuántas faltas cometimos?", "Faltas cometidas por cada equipo (y pérdidas cuando Veo las aporta).")
                _plot(T.fig_multiples(veo, ["Faltas cometidas", "Pérdidas"], cols=2), "eq_def_multi2")
                share("Defensa", "eq_share_def", "Reparto de entradas y faltas")
        else:
            _q("¿Cuántas jugadas a balón parado generamos y concedimos?", "Córneres y faltas lanzadas de cada equipo.")
            _plot(T.fig_multiples(veo, ["Córneres", "Faltas lanzadas"], cols=2), "eq_sp_multi")
            with st.expander("Más indicadores de balón parado"):
                _q("Saques de banda y penaltis", "Cada panel tiene su propia escala.")
                _plot(T.fig_multiples(veo, ["Saques de banda", "Penaltis"], cols=2), "eq_sp_multi2")
                share("Balón parado", "eq_share_sp", "Reparto del balón parado")
    with st.expander("Todas las métricas, partido a partido"):
        st.markdown(T.section("Producción por jornada", "Primer Toque, partido a partido."), unsafe_allow_html=True)
        st.markdown(production_html, unsafe_allow_html=True)
        st.markdown(T.section("Todas las métricas", "Primer Toque · rival."), unsafe_allow_html=True)
        st.dataframe(T.data_table(veo), hide_index=True, width="stretch")
        st.caption(pending_note + " Gol de Sebas en J2 (62'): dentro del área (corrección confirmada).")


def render_comparator(veo):
    """Jornada contra jornada: cualquier métrica por partido o dos jornadas cara a cara."""
    st.markdown(T.section("Comparador de rendimiento", "Cualquier métrica, jornada a jornada o dos jornadas cara a cara."), unsafe_allow_html=True)
    st.markdown(T.trend_cards_html(veo), unsafe_allow_html=True)
    avail = [m[0] for m in T.available_metrics(veo)]
    a, b = st.columns([1.25, 1], gap="medium")
    with a:
        sel = st.selectbox("Indicador", avail, key="v83_metric")
    with b:
        view = st.radio("Visualización", ["Jornada a jornada", "Comparar dos jornadas"], horizontal=True, key="v83_view")
    _, fav, against, unit, better, _ = T.METRIC_BY_LABEL[sel]
    adv = veo.dropna(subset=[fav, against], how="all")
    jornadas = [int(x) for x in veo.jornada]
    shown = None
    if view == "Comparar dos jornadas" and len(jornadas) >= 2:
        p1, p2 = st.columns(2)
        fmt = lambda j: veo.loc[veo.jornada == j, "etiqueta"].iloc[0]
        with p1:
            ja = st.selectbox("Primera jornada", jornadas, index=0, key="v83_ja", format_func=fmt)
        with p2:
            jb = st.selectbox("Segunda jornada", jornadas, index=len(jornadas) - 1, key="v83_jb", format_func=fmt)
        shown = [ja, jb]
        st.markdown(T.compare_two_html(veo, ja, jb), unsafe_allow_html=True)
    if adv.empty:
        st.info("Aún no existen mediciones de este indicador.")
        return
    _plot(T.fig_metric_by_match(adv, sel, shown), "eq_metric")
    own, riv = adv[fav].dropna(), adv[against].dropna()
    joint = adv.dropna(subset=[fav, against])
    m1, m2, m3 = st.columns(3)
    m1.metric("Media Primer Toque", f"{own.mean():.1f}" if len(own) else "—", help=f"Media sobre {len(own)} partidos con dato")
    if against == T.NONE:
        best = adv.loc[adv[fav].idxmax()] if len(own) else None
        m2.metric("Mejor partido", f"{best[fav]:g}" if best is not None else "—", best.etiqueta if best is not None else None, delta_color="off")
        m3.metric("Partidos con dato", f"{len(own)}")
    else:
        m2.metric("Media rivales", f"{riv.mean():.1f}" if len(riv) else "—", help=f"Media sobre {len(riv)} partidos con dato del rival")
        m3.metric("Diferencia comparable", f"{(joint[fav] - joint[against]).mean():+.1f}" if len(joint) else "—",
                  help=f"Diferencia promedio solo en {len(joint)} partidos con ambos valores")
        st.caption(f"{len(joint)} partidos comparables.")


def render_vs_rival_tool(veo, share_all):
    st.markdown(T.section("Primer Toque contra el rival", "Solo métricas que Veo ofrece de ambos equipos."), unsafe_allow_html=True)
    j = _jornada_picker(veo, "vs_j")
    c1, c2 = st.columns([1, 1], gap="medium")
    with c1.container(border=True):
        _q(f"¿Cómo nos comparamos con {T.club_short(veo.loc[veo.jornada == j, 'rival'].iloc[0])}?",
           "Radar: índice 0–100 sobre el máximo registrado por cualquiera de los dos equipos en esa métrica. Pasa el ratón para ver el valor real.")
        fig, _ = radar_vs_rival(veo, j)
        if fig is None:
            st.info("Datos insuficientes para el radar.")
        else:
            _plot(fig, "adv_radar_vs")
    with c2.container(border=True):
        _q("¿Qué parte del juego fue nuestra en la temporada?", "Media por partido de cada equipo · la línea marca el 50 %.")
        _plot(T.fig_share(share_all), "vs_share_all")


def render_avg_vs_avg(pt_tm, partidos, short_name, default_rival):
    st.markdown(T.section("Media de Primer Toque en casa frente a la media del rival fuera", "Resultados oficiales · n = partidos de cada media."),
                unsafe_allow_html=True)
    teams = sorted(t for t in set(partidos.local) | set(partidos.visitante) if t != TEAM)
    rival = st.selectbox("Rival", teams, index=teams.index(default_rival) if default_rival in teams else 0, key="avg_rival", format_func=short_name)
    home = pt_tm[pt_tm.condicion == "Casa"]
    away = team_matches(partidos, rival)
    away = away[away.condicion == "Fuera"]
    rows = [("Goles marcados por partido", home.gf.mean(), away.gf.mean()), ("Goles encajados por partido", home.gc.mean(), away.gc.mean()),
            ("Puntos por partido", home.pts.mean(), away.pts.mean())]
    fig = go.Figure()
    fig.update_layout(**plotly_layout(height=300, margin=dict(l=12, r=12, t=40, b=12), barmode="group", barcornerradius=4, bargap=.3))
    fig.add_bar(x=[r[0] for r in rows], y=[r[1] for r in rows], name=f"Primer Toque en casa (n = {len(home)})", marker_color=PT,
                text=[_f(r[1]) for r in rows], textposition="outside", cliponaxis=False, textfont=dict(color=TOKENS["text"]))
    fig.add_bar(x=[r[0] for r in rows], y=[r[2] for r in rows], name=f"{T.club_short(rival)} fuera (n = {len(away)})", marker_color=RIVAL,
                text=[_f(r[2]) for r in rows], textposition="outside", cliponaxis=False, textfont=dict(color=TOKENS["text"]))
    fig.update_yaxes(rangemode="tozero")
    with st.container(border=True):
        _q("¿Qué suele pasar cuando jugamos en casa y cuando ellos juegan fuera?",
           "Cada barra es una media por partido. Muestras pequeñas: tómalo como tendencia, no como predicción.")
        _plot(fig, "avg_vs_avg")
    st.caption("No hay estadísticas de vídeo del rival fuera de casa; por eso solo se comparan resultados.")


def render_radars(veo):
    st.markdown(T.section("Radares de rendimiento", "Tres radares, tres preguntas distintas."), unsafe_allow_html=True)
    j = _jornada_picker(veo, "rad_j")
    c1, c2 = st.columns(2, gap="medium")
    with c1.container(border=True):
        _q(f"¿J{j} estuvo por encima o por debajo de lo habitual?",
           "Naranja: el partido · línea punteada: media en casa. Escala 0–100 = valor ÷ máximo de Primer Toque en casa.")
        fig, _ = radar_vs_average(veo, j)
        if fig is None:
            st.info("Datos insuficientes para el radar.")
        else:
            _plot(fig, "adv_radar_avg")
    with c2.container(border=True):
        _q("¿Cómo fue el partido frente al rival?", "Naranja: Primer Toque · azul: rival. Escala 0–100 = valor ÷ máximo de ambos equipos.")
        fig, _ = radar_vs_rival(veo, j)
        if fig is None:
            st.info("Datos insuficientes para el radar.")
        else:
            _plot(fig, "adv_radar_vs")
    with st.container(border=True):
        _q("¿Qué parte del volumen de juego fue nuestra?",
           "Cuota de Primer Toque = PT ÷ (PT + rival). Aquí sí, 50 % significa reparto igualado.")
        opts = ["Todos los partidos comparables"] + [f"J{int(x)}" for x in veo.jornada]
        rsel = st.selectbox("Partidos", opts, key="eq_radar_sel")
        rfig, _, rjs = T.fig_radar(veo, None if rsel == opts[0] else int(rsel[1:]))
        if rfig is None:
            st.info("Este partido no tiene al menos tres métricas de volumen con dato de ambos equipos.")
        else:
            _plot(rfig, "eq_radar")
            st.caption("Partidos incluidos: " + ", ".join(f"J{x}" for x in rjs))
    st.caption("Los radares de partido usan un índice 0–100 (100 = máximo registrado), no una cuota: en ellos 50 no significa igualdad.")


def render_advanced(veo, pt_tm, partidos, clas, short_name, goals, share_all, seasons):
    """Nivel 3: herramientas de comparación elegidas con un selector."""
    tools = ["Partido contra media", "Jornada contra jornada", "Primer Toque contra rival", "Casa PT vs rival fuera",
             "Radares", "Análisis del rival", "Laboratorio", "Temporadas"]
    st.markdown(LEVEL_CSS, unsafe_allow_html=True)
    tool = st.pills("Herramienta", tools, default=tools[0], key="adv_tool") or tools[0]
    last_rival = veo.rival.iloc[-1]
    if tool == "Partido contra media":
        render_prepare(veo, pt_tm, partidos, short_name, goals, show_radars=False)
    elif tool == "Jornada contra jornada":
        render_comparator(veo)
    elif tool == "Primer Toque contra rival":
        render_vs_rival_tool(veo, share_all)
    elif tool == "Casa PT vs rival fuera":
        render_avg_vs_avg(pt_tm, partidos, short_name, last_rival)
    elif tool == "Radares":
        render_radars(veo)
    elif tool == "Análisis del rival":
        render_rival(veo, partidos, clas, short_name, last_rival)
    elif tool == "Laboratorio":
        render_lab(veo, pt_tm, seasons)
    else:
        render_seasons(seasons, short_name)
