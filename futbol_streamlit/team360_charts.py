"""Visualizaciones de Equipo 360 (Primer Toque).

Funciones puras: reciben DataFrames ya filtrados y devuelven figuras Plotly o HTML.
Reglas: los datos ausentes nunca se convierten en cero; las medias rival/PT solo
se comparan sobre partidos con ambos valores; los porcentajes indican su base.
"""
from html import escape

import pandas as pd
import plotly.graph_objects as go

from ui_theme import TOKENS, PT, RIVAL, POS, NEG, MUTED, plotly_layout

# (etiqueta, columna PT, columna rival, unidad, más_es_mejor para PT, bloque)
METRICS = [
    ("Tiros", "tiros_favor", "tiros_contra", "tiros", True, "Ataque"),
    ("Tiros a puerta", "tiros_puerta_favor", "tiros_puerta_contra", "tiros", True, "Ataque"),
    ("Ocasiones", "ocasiones_favor", "ocasiones_contra", "ocasiones", True, "Ataque"),
    ("Córneres", "corners_favor", "corners_contra", "córneres", True, "Ataque"),
    ("Saques de banda", "saques_banda_favor", "saques_banda_contra", "saques", None, "Territorio"),
    ("Recuperaciones", "recuperaciones_favor", "recuperaciones_rival", "recuperaciones", True, "Territorio"),
    ("Pérdidas", "perdidas_favor", "perdidas_rival", "pérdidas", False, "Territorio"),
    ("Posesión", "posesion_favor_pct", "posesion_rival_pct", "%", True, "Territorio"),
    ("Entradas / contactos", "entradas_favor", "entradas_contra", "acciones", None, "Contacto"),
    ("Faltas cometidas", "faltas_favor", "faltas_contra", "faltas", False, "Contacto"),
    ("Faltas lanzadas", "faltas_lanzadas_favor", "faltas_lanzadas_contra", "faltas", True, "Contacto"),
]
METRIC_BY_LABEL = {m[0]: m for m in METRICS}
# Métricas de volumen de juego propio: su cuota PT/(PT+rival) es comparable entre sí.
SHARE_METRICS = ["Tiros", "Ocasiones", "Córneres", "Faltas lanzadas", "Saques de banda", "Entradas / contactos"]

BAR = dict(barcornerradius=4, bargap=.28, bargroupgap=.12, uniformtext=dict(minsize=11, mode="show"))
_PREFIXES = {"C.F.", "U.D.", "C.D.F.", "C.D.", "At.", "Ath.", "Col.", "E.D.E.", "Mpal.", "F.C."}


def club_short(name):
    """'C.F. At. Burriana - Salesianos' -> 'Salesianos'; 'Bétera C.F.' -> 'Bétera'."""
    s = str(name).split(" - ")[-1]
    words = [w for w in s.replace("'", "").split() if w not in _PREFIXES and not (len(w) == 1 and w.isupper())]
    return " ".join(words) or str(name)


def _num(df, col):
    return pd.to_numeric(df[col], errors="coerce") if col in df.columns else pd.Series(float("nan"), index=df.index)


def prepare(adv, rival_short):
    """Normaliza el CSV avanzado: jornada entera, etiqueta 'J2 · Rival' y columnas numéricas."""
    d = adv.copy()
    d["jornada"] = pd.to_numeric(d["jornada"], errors="coerce").astype("Int64")
    d = d.dropna(subset=["jornada"]).sort_values("jornada")
    d["rival_corto"] = d["rival"].astype(str).map(rival_short)
    d["etiqueta"] = "J" + d["jornada"].astype(str) + " · " + d["rival_corto"]
    d["eje"] = "J" + d["jornada"].astype(str) + "<br>" + d["rival"].map(club_short)
    for _, f, a, *_ in METRICS:
        d[f] = _num(d, f); d[a] = _num(d, a)
    return d


def available_metrics(d):
    """Métricas con al menos un dato real (propio o rival)."""
    return [m for m in METRICS if d[m[1]].notna().any() or d[m[2]].notna().any()]


def _fmt(v, unit=""):
    if pd.isna(v):
        return "—"
    s = f"{v:.1f}".rstrip("0").rstrip(".") if abs(v - round(v)) > 1e-9 else f"{int(round(v))}"
    return s + ("%" if unit == "%" else "")


def _fig(height, **kw):
    fig = go.Figure()
    fig.update_layout(**plotly_layout(height=height, **kw))
    return fig


# ---------------------------------------------------------------- temporada (resultados)
def fig_points(md):
    """Puntos acumulados J1..Jn. Marcador coloreado por resultado + letra V/E/D (no solo color)."""
    colors = {"V": POS, "E": MUTED, "D": NEG}
    fig = _fig(250, margin=dict(l=12, r=12, t=14, b=12), showlegend=False)
    x = [f"J{j}" for j in md.jornada]
    fig.add_scatter(x=x, y=md.pts_acum, mode="lines", line=dict(color=PT, width=2.5, shape="linear"), hoverinfo="skip")
    fig.add_scatter(
        x=x, y=md.pts_acum, mode="markers+text", text=md.res, textposition="top center",
        textfont=dict(color=TOKENS["text"], size=11),
        marker=dict(size=13, color=[colors[r] for r in md.res], line=dict(color=TOKENS["surface"], width=2)),
        customdata=list(zip(md.rival, md.gf, md.gc, md.condicion, md.pts)),
        hovertemplate="<b>%{x} · %{customdata[0]}</b><br>%{customdata[3]} · %{customdata[1]}–%{customdata[2]}"
                      "<br>+%{customdata[4]} pts · %{y} acumulados<extra></extra>",
    )
    fig.update_yaxes(title=dict(text="Puntos acumulados", font=dict(size=11, color=MUTED)), rangemode="tozero", dtick=3)
    return fig


def fig_position(rows, n_teams=16):
    """Posición en la clasificación por jornada (1 = arriba)."""
    fig = _fig(250, margin=dict(l=12, r=12, t=14, b=12), showlegend=False)
    x = [f"J{int(j)}" for j in rows.jornada]
    fig.add_scatter(
        x=x, y=rows.posicion, mode="lines+markers+text", text=[f"{int(p)}º" for p in rows.posicion],
        textposition="top center", textfont=dict(color=TOKENS["text"], size=11),
        line=dict(color=RIVAL, width=2.5), marker=dict(size=10, color=RIVAL, line=dict(color=TOKENS["surface"], width=2)),
        hovertemplate="<b>%{x}</b><br>Posición %{y}º<extra></extra>",
    )
    fig.update_yaxes(autorange="reversed", range=[n_teams + .5, .5], dtick=3, title=dict(text="Posición", font=dict(size=11, color=MUTED)))
    fig.update_yaxes(autorange=False, range=[n_teams + .5, .5])
    return fig


def fig_goal_timing(timing):
    """Mariposa: goles a favor (derecha, naranja) y en contra (izquierda, azul) por tramo de 15'."""
    labels = [t[0] for t in timing][::-1]
    gf = [t[1] for t in timing][::-1]
    gc = [t[2] for t in timing][::-1]
    m = max(gf + gc + [1])
    fig = _fig(300, margin=dict(l=12, r=12, t=34, b=12), barmode="relative", **BAR)
    fig.add_bar(y=labels, x=[-v for v in gc], orientation="h", name="Encajados", marker_color=RIVAL,
                text=[v if v else "" for v in gc], textposition="outside", textfont=dict(color=TOKENS["text"]),
                customdata=gc, hovertemplate="%{y}: %{customdata} goles encajados<extra></extra>")
    fig.add_bar(y=labels, x=gf, orientation="h", name="Marcados", marker_color=PT,
                text=[v if v else "" for v in gf], textposition="outside", textfont=dict(color=TOKENS["text"]),
                hovertemplate="%{y}: %{x} goles marcados<extra></extra>")
    ticks = list(range(-m, m + 1))
    fig.update_xaxes(range=[-m - 1, m + 1], tickvals=ticks, ticktext=[str(abs(t)) for t in ticks],
                     title=dict(text="← encajados · goles · marcados →", font=dict(size=11, color=MUTED)), zeroline=True, zerolinewidth=1.5)
    fig.update_yaxes(showgrid=False)
    return fig


# ---------------------------------------------------------------- estadísticas Veo (partidos en casa)
def fig_metric_by_match(d, label, jornadas=None):
    """Barras agrupadas PT vs rival por partido para una métrica. Las ausencias se anotan, no se dibujan."""
    _, f, a, unit, *_ = METRIC_BY_LABEL[label]
    s = d if jornadas is None else d[d.jornada.isin(jornadas)]
    fig = _fig(330, margin=dict(l=12, r=12, t=40, b=12), barmode="group", **BAR)
    for name, col, color in (("Primer Toque", f, PT), ("Rival", a, RIVAL)):
        vals = s[col]
        fig.add_bar(x=s.eje, y=vals, name=name, marker_color=color,
                    text=[_fmt(v, unit) if pd.notna(v) else "" for v in vals], textposition="outside",
                    textfont=dict(color=TOKENS["text"], size=12), cliponaxis=False,
                    customdata=s.etiqueta, hovertemplate=f"<b>%{{customdata}}</b><br>{name}: %{{y}} {escape(unit)}<extra></extra>")
    for _, r in s.iterrows():
        miss = [n for n, c in (("PT", f), ("rival", a)) if pd.isna(r[c])]
        if miss and len(miss) < 2:
            fig.add_annotation(x=r.eje, y=0, yref="y", text="sin<br>dato", showarrow=False, xshift=22 if miss[0] == "rival" else -22,
                               yshift=4, yanchor="bottom", font=dict(size=10, color=MUTED))
    fig.update_yaxes(title=dict(text=f"{label} ({unit})", font=dict(size=11, color=MUTED)), rangemode="tozero")
    fig.update_xaxes(showgrid=False)
    return fig


def share_table(d, labels):
    """Media PT y rival por métrica sobre partidos con ambos valores; cuota PT del total."""
    rows = []
    for lab in labels:
        _, f, a, unit, better, block = METRIC_BY_LABEL[lab]
        both = d.dropna(subset=[f, a])
        if both.empty:
            continue
        pt, rv = both[f].mean(), both[a].mean()
        tot = pt + rv
        rows.append(dict(metric=lab, unit=unit, better=better, block=block, n=len(both), pt=pt, rival=rv,
                         share=100 * pt / tot if tot else float("nan"), jornadas=", ".join(f"J{j}" for j in both.jornada)))
    return pd.DataFrame(rows)


def fig_share(tbl):
    """Barras 100% horizontales: cuota de cada equipo sobre el total de la métrica (medias comparables)."""
    t = tbl.iloc[::-1]
    fig = _fig(max(150, 54 * len(t) + 60), margin=dict(l=12, r=12, t=38, b=12), barmode="stack", **BAR)
    fig.update_layout(legend_traceorder="normal")
    fig.add_bar(y=t.metric, x=t.share, orientation="h", name="Primer Toque", marker_color=PT,
                text=[f"{_fmt(v, u)}" for v, u in zip(t.pt, t.unit)], textposition="inside", insidetextanchor="start",
                textfont=dict(color="#1A0E02", size=12),
                customdata=list(zip(t.pt.round(1), t.rival.round(1), t.n, t.jornadas, t.unit)),
                hovertemplate="<b>%{y}</b><br>Primer Toque %{customdata[0]} · Rival %{customdata[1]} %{customdata[4]}"
                              "<br>Cuota PT %{x:.0f}% · %{customdata[2]} partidos (%{customdata[3]})<extra></extra>")
    fig.add_bar(y=t.metric, x=100 - t.share, orientation="h", name="Rival", marker_color=RIVAL,
                text=[f"{_fmt(v, u)}" for v, u in zip(t.rival, t.unit)], textposition="inside", insidetextanchor="end",
                textfont=dict(color="#0A1426", size=12),
                customdata=list(zip(t.pt.round(1), t.rival.round(1), t.n, t.jornadas, t.unit)),
                hovertemplate="<b>%{y}</b><br>Rival %{customdata[1]} · Primer Toque %{customdata[0]} %{customdata[4]}"
                              "<br>Cuota rival %{x:.0f}% · %{customdata[2]} partidos<extra></extra>")
    fig.add_vline(x=50, line=dict(color=TOKENS["ink"], width=1, dash="dot"))
    fig.update_xaxes(range=[0, 100], ticksuffix="%", dtick=25, showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig


def fig_radar(d, jornada=None):
    """Radar de cuota de volumen PT/(PT+rival) en %, 50% = igualdad.

    Solo usa métricas de volumen con ambos valores en TODOS los partidos considerados,
    para que cada eje se calcule sobre la misma base. Devuelve (fig, ejes, partidos) o (None, ...).
    """
    s = d if jornada is None else d[d.jornada == jornada]
    cols = {lab: METRIC_BY_LABEL[lab][1:3] for lab in SHARE_METRICS}
    if not s.empty:  # partidos con al menos 3 métricas completas; ejes completos en todos ellos
        s = s[pd.DataFrame({lab: s[list(fa)].notna().all(axis=1) for lab, fa in cols.items()}).sum(axis=1) >= 3]
    axes = [lab for lab in SHARE_METRICS if not s.empty and s[list(cols[lab])].notna().all(axis=None)]
    if len(axes) < 3 or s.empty:
        return None, axes, []
    vals = []
    for lab in axes:
        f, a = METRIC_BY_LABEL[lab][1:3]
        pt, rv = s[f].sum(), s[a].sum()
        vals.append(100 * pt / (pt + rv) if (pt + rv) else 50)
    theta = axes + axes[:1]
    fig = _fig(380, margin=dict(l=84, r=84, t=40, b=30), showlegend=True)
    fig.add_scatterpolar(r=[50] * len(theta), theta=theta, mode="lines", name="Igualdad (50%)",
                         line=dict(color=MUTED, width=1, dash="dot"), hoverinfo="skip")
    fig.add_scatterpolar(r=vals + vals[:1], theta=theta, mode="lines+markers", name="Primer Toque", fill="toself",
                         fillcolor="rgba(245,135,31,.22)", line=dict(color=PT, width=2), marker=dict(size=8, color=PT),
                         hovertemplate="<b>%{theta}</b><br>Cuota PT %{r:.0f}%<extra></extra>")
    fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                 radialaxis=dict(range=[0, 100], ticksuffix="%", tickvals=[25, 50, 75], gridcolor=TOKENS["line"],
                                                 tickfont=dict(color=MUTED, size=10), linecolor=TOKENS["line"]),
                                 angularaxis=dict(gridcolor=TOKENS["line"], linecolor=TOKENS["line"], tickfont=dict(color=TOKENS["text"], size=11))))
    return fig, axes, [int(j) for j in s.jornada]


def efficiency(d, goals):
    """Eficacia por partido: goles / tiros y goles / ocasiones (goles oficiales del resultado)."""
    rows = []
    for _, r in d.iterrows():
        g = goals.get(int(r.jornada))
        if not g:
            continue
        gf, gc = g
        rows.append(dict(jornada=int(r.jornada), etiqueta=r.etiqueta, eje=r.eje, gf=gf, gc=gc,
                         tiros_pt=r.tiros_favor, tiros_rv=r.tiros_contra, oc_pt=r.ocasiones_favor, oc_rv=r.ocasiones_contra))
    e = pd.DataFrame(rows)
    if e.empty:
        return e
    e["conv_pt"] = 100 * e.gf / e.tiros_pt.where(e.tiros_pt > 0)
    e["conv_rv"] = 100 * e.gc / e.tiros_rv.where(e.tiros_rv > 0)
    return e


def fig_efficiency(e):
    fig = _fig(300, margin=dict(l=12, r=12, t=40, b=12), barmode="group", **BAR)
    for name, col, g, t, color in (("Primer Toque", "conv_pt", "gf", "tiros_pt", PT), ("Rival", "conv_rv", "gc", "tiros_rv", RIVAL)):
        fig.add_bar(x=e.eje, y=e[col], name=name, marker_color=color, cliponaxis=False,
                    text=[f"{v:.0f}%" if pd.notna(v) else "" for v in e[col]], textposition="outside",
                    textfont=dict(color=TOKENS["text"], size=12),
                    customdata=list(zip(e[g], e[t].map(lambda v: "—" if pd.isna(v) else int(v)), e.etiqueta)),
                    hovertemplate=f"<b>%{{customdata[2]}}</b><br>{name}: %{{customdata[0]}} goles / %{{customdata[1]}} tiros"
                                  "<br>Conversión %{y:.1f}%<extra></extra>")
    fig.update_yaxes(title=dict(text="Conversión (goles / tiros, %)", font=dict(size=11, color=MUTED)), ticksuffix="%", rangemode="tozero")
    fig.update_xaxes(showgrid=False)
    return fig


def fig_zones(d):
    """Distribución por zonas (defensa / medio / ataque) de pases y posesión, cuando Veo la aporta."""
    specs = [("Pases", "pases_zona_{}_pct"), ("Posesión", "posesion_zona_{}_pct")]
    zones = [("defensa", "Defensa", "#7A4A1C"), ("medio", "Medio", "#B8661E"), ("ataque", "Ataque", PT)]
    rows = []
    for _, r in d.iterrows():
        for lab, pat in specs:
            vals = [pd.to_numeric(r.get(pat.format(z)), errors="coerce") for z, *_ in zones]
            if all(pd.notna(v) for v in vals):
                rows.append((f"{r.etiqueta.split(' · ')[0]} · {lab}", vals))
    if not rows:
        return None
    fig = _fig(90 + 50 * len(rows), margin=dict(l=12, r=12, t=38, b=12), barmode="stack", **BAR)
    fig.update_layout(legend_traceorder="normal")
    for i, (z, zl, color) in enumerate(zones):
        fig.add_bar(y=[r[0] for r in rows][::-1], x=[r[1][i] for r in rows][::-1], orientation="h", name=zl,
                    marker=dict(color=color, line=dict(color=TOKENS["surface"], width=2)),
                    text=[f"{r[1][i]:.0f}%" if r[1][i] >= 12 else "" for r in rows][::-1], textposition="inside", textangle=0,
                    insidetextanchor="middle", textfont=dict(color=TOKENS["ink"], size=12),
                    hovertemplate=f"%{{y}}<br>{zl}: %{{x:.0f}}%<extra></extra>")
    fig.update_xaxes(range=[0, 100], ticksuffix="%", showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig


# ---------------------------------------------------------------- comparación entre dos jornadas
def _delta_html(v, better):
    if pd.isna(v):
        return "<span class='cmp-delta flat'>—</span>"
    if abs(v) < 1e-9:
        return "<span class='cmp-delta flat'>= 0</span>"
    good = None if better is None else ((v > 0) == better)
    cls = "flat" if good is None else ("up" if good else "down")
    return f"<span class='cmp-delta {cls}'>{'▲' if v > 0 else '▼'} {abs(v):g}</span>"


def compare_two_html(d, ja, jb):
    """Tabla compacta J-a vs J-b para PT y rival, con barras por fila y variación con flecha y signo."""
    A, B = d[d.jornada == ja], d[d.jornada == jb]
    if A.empty or B.empty:
        return ""
    A, B = A.iloc[0], B.iloc[0]
    la, lb = (f"J{int(x.jornada)} · {club_short(x.rival)}" for x in (A, B))
    head = (f"<div class='cmp-row cmp-head'><span>Métrica</span><span>{escape(la)}</span><span>{escape(lb)}</span>"
            f"<span>Variación PT</span><span>Rival {escape(A.etiqueta.split(' · ')[0])} → {escape(B.etiqueta.split(' · ')[0])}</span></div>")
    body = []
    for lab, f, a, unit, better, _ in METRICS:
        va, vb, ra, rb = A[f], B[f], A[a], B[a]
        if all(pd.isna(x) for x in (va, vb, ra, rb)):
            continue
        top = max([x for x in (va, vb, ra, rb) if pd.notna(x)] + [1])
        bar = lambda v, cls: (f"<div class='cmp-cell'><b>{_fmt(v, unit)}</b>"
                              + ("" if pd.isna(v) else f"<i class='{cls}' style='width:{100 * v / top:.0f}%'></i>") + "</div>")
        rival_txt = f"{_fmt(ra, unit)} → {_fmt(rb, unit)}"
        body.append(f"<div class='cmp-row'><span class='cmp-metric'>{escape(lab)}<small>{escape(unit)}</small></span>"
                    f"{bar(va, 'pt')}{bar(vb, 'pt')}{_delta_html(vb - va if pd.notna(va) and pd.notna(vb) else float('nan'), better)}"
                    f"<span class='cmp-rival'>{rival_txt}</span></div>")
    return "<div class='cmp-table'>" + head + "".join(body) + "</div>"


def trend_cards_html(d, labels=("Tiros", "Ocasiones", "Córneres", "Faltas lanzadas")):
    """Último partido con dato frente al anterior con dato, por métrica (solo PT)."""
    cards = []
    for lab in labels:
        _, f, _, unit, better, _ = METRIC_BY_LABEL[lab]
        s = d.dropna(subset=[f])
        if len(s) < 2:
            continue
        prev, last = s.iloc[-2], s.iloc[-1]
        cards.append(f"<div class='trend-tile'><small>{escape(lab)}</small><b>{_fmt(last[f], unit)}</b>"
                     f"{_delta_html(last[f] - prev[f], better)}<span>J{int(last.jornada)} frente a J{int(prev.jornada)}</span></div>")
    return "<div class='trend-row'>" + "".join(cards) + "</div>" if cards else ""


def insights(d, tbl, e):
    """Lecturas automáticas, todas derivadas de los datos mostrados."""
    out = []
    for _, r in tbl.iterrows():
        f, a = METRIC_BY_LABEL[r.metric][1:3]
        both = d.dropna(subset=[f, a])
        wins = int((both[f] > both[a]).sum())
        if r.metric in ("Tiros", "Ocasiones", "Córneres"):
            out.append(f"<b>{escape(r.metric)}</b>: Primer Toque supera al rival en {wins} de {len(both)} partidos comparables "
                       f"(media {_fmt(r.pt)} frente a {_fmt(r.rival)}).")
    t = d.dropna(subset=["tiros_favor"])
    if not t.empty:
        best = t.loc[t.tiros_favor.idxmax()]
        out.append(f"<b>Mayor volumen ofensivo</b>: {escape(best.etiqueta)} con {_fmt(best.tiros_favor)} tiros.")
    if e is not None and not e.empty and e.conv_pt.notna().any():
        tot_g, tot_t = e.loc[e.tiros_pt.notna(), "gf"].sum(), e.tiros_pt.sum()
        out.append(f"<b>Conversión global</b>: {int(tot_g)} goles con {int(tot_t)} tiros en casa "
                   f"({100 * tot_g / tot_t:.1f}%, un gol cada {tot_t / tot_g:.1f} tiros)." if tot_g else
                   f"<b>Conversión global</b>: 0 goles con {int(tot_t)} tiros en casa.")
    return "".join(f"<li>{x}</li>" for x in out)


CSS = """
<style>
.eq-section{margin:26px 0 10px;display:flex;align-items:flex-end;justify-content:space-between;gap:12px;flex-wrap:wrap}
.eq-section h3{margin:0!important;font-size:1.15rem!important;font-weight:800!important;color:var(--ink)!important;letter-spacing:-.015em}
.eq-section p{margin:3px 0 0;font-size:.8rem;color:var(--muted)}
.eq-scope{display:inline-flex;align-items:center;gap:6px;font-size:.7rem;font-weight:700;color:var(--text);background:var(--surface-2);border:1px solid var(--line);border-radius:999px;padding:5px 10px}
.eq-scope i{width:7px;height:7px;border-radius:50%;background:var(--pt);display:inline-block}
.eq-panel{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:14px 16px 6px;margin-bottom:12px}
.eq-panel-title{font-size:.82rem;font-weight:800;color:var(--ink);margin-bottom:2px}
.eq-panel-sub{font-size:.7rem;color:var(--muted);margin-bottom:4px}
.eq-insights{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--pt);border-radius:14px;padding:12px 16px;margin:4px 0 12px}
.eq-insights b{color:var(--ink)} .eq-insights ul{margin:6px 0 0;padding-left:18px} .eq-insights li{font-size:.8rem;color:var(--text);margin:4px 0;line-height:1.45}
.eq-insights-title{font-size:.72rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--pt)}
.trend-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:4px 0 12px}
.trend-tile{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
.trend-tile small{display:block;font-size:.68rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.trend-tile b{font-size:1.6rem;font-weight:850;color:var(--ink);margin-right:8px;letter-spacing:-.02em}
.trend-tile span:last-child{display:block;font-size:.66rem;color:var(--muted);margin-top:2px}
.cmp-delta{justify-self:start;display:inline-flex;align-items:center;gap:3px;font-size:.74rem;font-weight:800;border-radius:999px;padding:2px 8px}
.cmp-delta.up{color:var(--pos);background:rgba(43,196,138,.12)} .cmp-delta.down{color:var(--neg);background:rgba(240,89,106,.12)} .cmp-delta.flat{color:var(--muted);background:var(--surface-2)}
.cmp-table{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:6px 14px;margin:6px 0 12px}
.cmp-row{display:grid;grid-template-columns:1.35fr 1fr 1fr .8fr 1fr;gap:12px;align-items:center;padding:9px 0;border-bottom:1px solid var(--line-soft);font-size:.8rem}
.cmp-row:last-child{border-bottom:0}
.cmp-head{font-size:.66rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.cmp-metric{font-weight:700;color:var(--ink)} .cmp-metric small{display:block;font-size:.64rem;font-weight:500;color:var(--muted)}
.cmp-cell b{display:block;color:var(--ink);font-size:.95rem;font-weight:800}
.cmp-cell i{display:block;height:5px;border-radius:4px;margin-top:4px;min-width:2px} .cmp-cell i.pt{background:var(--pt)}
.cmp-rival{color:var(--text);font-weight:600}
.pro84-match header em{margin-left:auto;font-style:normal;font-weight:800;color:var(--ink);font-size:.95rem}
@media(max-width:760px){.trend-row{grid-template-columns:repeat(2,minmax(0,1fr))}
  .cmp-row{grid-template-columns:1.1fr .8fr .8fr .8fr;gap:8px;font-size:.72rem}.cmp-rival{display:none}.cmp-head span:last-child{display:none}}
</style>
"""


def section(title, sub="", scope=""):
    s = f"<span class='eq-scope'><i></i>{escape(scope)}</span>" if scope else ""
    return f"<div class='eq-section'><div><h3>{escape(title)}</h3><p>{escape(sub)}</p></div>{s}</div>"


def fig_standings(evo, selected, reference="Primer Toque C.F. 'A'"):
    """Evolución de la clasificación de los 16 equipos; destaca el seleccionado y Primer Toque como referencia."""
    evo = evo.assign(jornada=pd.to_numeric(evo.jornada, errors="coerce"), posicion=pd.to_numeric(evo.posicion, errors="coerce")).dropna(subset=["jornada", "posicion"])
    n = int(evo.groupby("jornada").equipo.nunique().max() or 16)
    days = sorted(evo.jornada.astype(int).unique())
    fig = _fig(380, margin=dict(l=12, r=12, t=40, b=12))
    for team, g in evo.groupby("equipo"):
        if team in (selected, reference):
            continue
        g = g.sort_values("jornada")
        fig.add_scatter(x=[f"J{int(j)}" for j in g.jornada], y=g.posicion, mode="lines", showlegend=False,
                        line=dict(color="#3A465B", width=1.2), customdata=[team] * len(g),
                        hovertemplate="%{customdata} · %{x}: %{y}º<extra></extra>")
    styles = [(reference, "Primer Toque", PT, "dash", 2.5)] if reference != selected else []
    styles.append((selected, selected, PT if selected == reference else RIVAL, "solid", 4))
    for team, label, color, dash, width in styles:
        g = evo[evo.equipo == team].sort_values("jornada")
        if g.empty:
            continue
        main = team == selected
        fig.add_scatter(x=[f"J{int(j)}" for j in g.jornada], y=g.posicion, name=label, mode="lines+markers+text" if main else "lines+markers",
                        line=dict(color=color, width=width, dash=dash), marker=dict(size=9 if main else 6, color=color, line=dict(color=TOKENS["surface"], width=2)),
                        text=[f"{int(p)}º" for p in g.posicion] if main else None, textposition="top center",
                        textfont=dict(color=TOKENS["ink"], size=12), hovertemplate=label + " · %{x}: %{y}º<extra></extra>")
    fig.update_yaxes(autorange=False, range=[n + .6, .4], tickvals=[1, 4, 8, 12, n], ticksuffix="º", title=dict(text="Posición", font=dict(size=11, color=MUTED)))
    fig.update_xaxes(categoryorder="array", categoryarray=[f"J{d}" for d in days], showgrid=False)
    return fig
