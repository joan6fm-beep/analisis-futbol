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
        out.append(f"<b>Muestra pequeña</b>: la media de referencia usa {n} partido(s). Las diferencias son orientativas, no conclusiones.")
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
            txt = f"{abs(diff):.0f} p.p. {'por encima' if diff > 0 else 'por debajo'} de su media ({T._fmt(cur[f], unit)} frente a {m:.0f}%, n = {len(r)})"
        else:
            pct = 100 * diff / m if m else 0
            if abs(pct) < 10:
                continue
            txt = f"{abs(pct):.0f}% {'más' if diff > 0 else 'menos'} que su media ({T._fmt(cur[f], unit)} frente a {m:.1f}, n = {len(r)})"
        extra = " Más volumen indica un partido más disputado, no necesariamente una mejor defensa." if lab in NEUTRAL_NOTE else ""
        out.append(f"<b>{escape(lab)}</b>: {txt}.{extra}")
    if pd.notna(cur.get("intentos_favor")) and eff_goals is not None:
        g = eff_goals.get(int(jornada))
        if g is not None and cur["intentos_favor"] > 0:
            out.append(f"<b>Eficacia</b>: {g[0]} gol(es) con {int(cur['intentos_favor'])} intentos "
                       f"({100 * g[0] / cur['intentos_favor']:.0f}% de conversión de intentos).")
    pos = veo.dropna(subset=["posesion_favor_pct"])
    if len(pos) >= 3:
        seq = " → ".join(f"J{int(j)} {v:.0f}%" for j, v in zip(pos.jornada, pos.posesion_favor_pct))
        out.append(f"<b>Evolución de la posesión</b>: {seq}. Con {len(pos)} partidos es una tendencia orientativa.")
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


def render_prepare(veo, pt_tm, partidos, short_name, goals):
    st.markdown(T.section("Preparar partido · cuatro referencias",
                          "A: Primer Toque en la jornada · B: su media en casa · C: el rival en la jornada · D: la media del rival como visitante."),
                unsafe_allow_html=True)
    opts = [int(j) for j in veo.jornada]
    c1, c2 = st.columns([1.2, 1])
    with c1:
        j = st.selectbox("Jornada", opts, index=len(opts) - 1, key="adv_j",
                         format_func=lambda x: veo.loc[veo.jornada == x, "etiqueta"].iloc[0])
    with c2:
        excl = st.toggle("Excluir esta jornada de la media de Primer Toque", value=True, key="adv_excl",
                         help="Recomendado: compara el partido con el resto de partidos en casa, no consigo mismo.")
    rival = veo.loc[veo.jornada == j, "rival"].iloc[0]
    rshort = T.club_short(rival)
    rtm = team_matches(partidos, rival)
    away = rtm[rtm.condicion == "Fuera"]
    home_pt = pt_tm[(pt_tm.condicion == "Casa") & ((pt_tm.jornada != j) if excl else True)]
    st.markdown(
        "<div class='adv-ref'>"
        f"<div class='a'><b>A · Primer Toque</b><span>J{j} frente a {escape(rshort)}</span><small>Partido seleccionado</small></div>"
        f"<div class='b'><b>B · Media PT en casa</b><span>{len(home_pt)} partidos (resultados)</span><small>Vídeo: hasta {len(veo) - (1 if excl else 0)} partidos</small></div>"
        f"<div class='c'><b>C · {escape(rshort)}</b><span>J{j} en nuestro campo</span><small>Lo que hizo contra nosotros</small></div>"
        f"<div class='d'><b>D · {escape(rshort)} fuera</b><span>{len(away)} partidos (resultados)</span><small>Sin estadísticas de vídeo</small></div></div>",
        unsafe_allow_html=True)
    rows = four_refs(veo, pt_tm, rtm, j, excl)
    groups = list(dict.fromkeys(rows.grupo))
    shown = st.pills("Bloques de métricas", groups, selection_mode="multi", default=groups[:3], key="adv_groups") or groups
    st.markdown(four_refs_html(rows[rows.grupo.isin(shown)], j, rshort), unsafe_allow_html=True)
    st.markdown(f"<div class='adv-note'><b>Referencia D</b>: solo existen resultados oficiales de {escape(rshort)} fuera de casa "
                f"({len(away)} partidos: {', '.join(f'J{x}' for x in away.jornada)}). Sus estadísticas avanzadas de vídeo fuera de casa "
                "no están disponibles: solo tenemos el vídeo de su partido contra Primer Toque (columna C).</div>", unsafe_allow_html=True)
    st.caption("Diferencias: ▲/▼ con valor absoluto y, debajo, la variación porcentual respecto a la referencia (no se calcula sobre porcentajes: "
               "ahí se indica en puntos porcentuales, p.p.). Verde/rojo solo en métricas con dirección clara; en volúmenes neutros, gris.")

    st.markdown(T.section("Radares comparativos", NORM_TEXT), unsafe_allow_html=True)
    r1, r2 = st.columns(2, gap="medium")
    with r1.container(border=True):
        st.markdown(f"<div class='eq-panel-title'>Primer Toque J{j} frente a su media en casa</div>"
                    "<div class='eq-panel-sub'>Escala de cada eje: máximo de Primer Toque en casa en esa métrica.</div>", unsafe_allow_html=True)
        fig, tbl = radar_vs_average(veo, j, excl)
        if fig is None:
            st.info("No hay al menos tres métricas con dato en esta jornada y en dos partidos de referencia.")
        else:
            _plot(fig, "adv_radar_avg")
            st.caption("Ejes: " + " · ".join(f"{r.metrica} (máx. {T._fmt(r.maximo, '')}; media n = {r.n})" for _, r in tbl.iterrows()))
    with r2.container(border=True):
        st.markdown(f"<div class='eq-panel-title'>Primer Toque frente a {escape(rshort)} · J{j}</div>"
                    "<div class='eq-panel-sub'>Solo métricas que Veo ofrece de ambos equipos. Escala: máximo de ambos equipos en los partidos medidos.</div>",
                    unsafe_allow_html=True)
        fig, tbl = radar_vs_rival(veo, j)
        if fig is None:
            st.info("En esta jornada no hay al menos tres métricas con dato de ambos equipos.")
        else:
            _plot(fig, "adv_radar_vs")
            st.caption("Ejes: " + " · ".join(f"{r.metrica} (máx. {T._fmt(r.maximo, '')})" for _, r in tbl.iterrows()))
    lines = interpret(veo, j, goals)
    if lines:
        st.markdown("<div class='eq-insights adv-insight'><div class='eq-insights-title'>Interpretación del partido</div><ul>"
                    + "".join(f"<li>{x}</li>" for x in lines) + "</ul></div>", unsafe_allow_html=True)


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
    st.markdown(T.section("Análisis del rival", "Resultados oficiales de toda la temporada y, si existe, el vídeo de su partido contra Primer Toque."),
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
    st.caption("La etiqueta n indica cuántos partidos intervienen en cada media: una media con n = 3 es mucho menos estable que una con n = 10.")
    c1, c2 = st.columns([1.3, 1], gap="medium")
    with c1.container(border=True):
        st.markdown("<div class='eq-panel-title'>Evolución en la clasificación</div><div class='eq-panel-sub'>Color del punto: verde victoria · gris empate · rojo derrota (también en el texto al pasar el ratón).</div>", unsafe_allow_html=True)
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
        st.info("No hay estadísticas de vídeo de este rival: solo se graban con Veo los partidos de Primer Toque en casa.")
    else:
        vr = v.iloc[0]
        items = [(lab, vr[f], vr[a], unit) for lab, f, a, unit, *_ in T.METRICS if a != T.NONE and pd.notna(vr[a])]
        with st.container(border=True):
            st.markdown(f"<div class='eq-panel-title'>Estadísticas de vídeo de {escape(short_name(rival))} · J{int(vr.jornada)} en nuestro campo</div>"
                        "<div class='eq-panel-sub'>Un solo partido: describe lo que hizo contra nosotros, no su media.</div>", unsafe_allow_html=True)
            rows = [f"<div class='vs-row vs-head'><span>Métrica</span><span>Primer Toque</span><span>{escape(short_name(rival))}</span></div>"]
            for lab, pv, rvv, unit in items:
                top = max(pv if pd.notna(pv) else 0, rvv, 1e-9)
                bar = lambda v, cls: (f"<div class='vs-bar {cls}'><b>{T._fmt(v, unit)}</b>"
                                      + ("" if pd.isna(v) else f"<i style='width:{100 * v / top * .7:.0f}%'></i>") + "</div>")
                rows.append(f"<div class='vs-row'><span class='m'>{escape(lab)}</span>{bar(pv, 'pt')}{bar(rvv, 'rv')}</div>")
            st.markdown("<div class='adv-tbl'>" + "".join(rows) + "</div>", unsafe_allow_html=True)
            st.caption("Cada fila tiene su propia escala (la barra más larga es el valor mayor de los dos).")


def _metric_options():
    return [m[0] for m in RESULT_METRICS] + [m[0] for m in T.METRICS]


def render_lab(veo, pt_tm, seasons):
    st.markdown(T.section("Laboratorio de comparación", "Elige una métrica y el tipo de comparación. Las opciones se adaptan a los datos que existen para esa métrica."),
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
    st.markdown(T.section("Comparador de temporadas", "Estructura preparada para varias temporadas. Solo se muestran temporadas con datos importados."),
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
        st.markdown("<div class='adv-note'><b>Solo hay una temporada con datos (2026/2027).</b> Para comparar, añade otra temporada en "
                    "<code>data/temporadas.csv</code> y copia sus CSV en <code>data/temporadas/&lt;carpeta&gt;/</code> con los mismos nombres "
                    "(<code>partidos_rivales.csv</code>, <code>clasificacion_liga.csv</code>, <code>equipo_avanzado.csv</code>). "
                    "Las instrucciones están en <code>data/temporadas/LEEME.md</code>.</div>", unsafe_allow_html=True)
