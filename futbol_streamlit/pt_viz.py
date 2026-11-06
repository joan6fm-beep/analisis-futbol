"""Componentes visuales compartidos por Juvenil A y Cadete A.

Tarjetas de jugador (podio + ranking), duelos entre equipos, carrera de puntos, mapa
ataque/defensa (2D y 3D) y goles decisivos. Funciones puras: reciben datos ya calculados
y devuelven HTML o figuras Plotly. Nunca rellenan datos ausentes.
"""
from __future__ import annotations

from html import escape

import pandas as pd
import plotly.graph_objects as go

from ui_theme import MUTED, NEG, POS, PT, RIVAL, TOKENS, plotly_layout

GREY = "#3A465B"


def initials(name: str) -> str:
    parts = [p for p in str(name).replace(".", " ").split() if p[:1].isalpha()]
    if not parts:
        return "?"
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()


def _num(v, fmt):
    return fmt(v) if callable(fmt) else str(v)


_SINGULAR = {"goles": "gol", "decisivos": "decisivo"}


def _unit(v, unit):
    try:
        return _SINGULAR.get(unit, unit) if float(v) == 1 else unit
    except (TypeError, ValueError):
        return unit


def player_cards_html(items, accent=PT, value_fmt=lambda v: f"{v:g}", unit="", limit=8,
                      empty="Todavía no hay registros disponibles.", lower_is_better=False):
    """Podio (tres primeros) + ranking compacto con barra.

    items: lista de dict(name, value, sub='', badge='' (HTML, p. ej. escudo), tag='' (dorsal o equipo corto)).
    """
    items = [i for i in items if i.get("value") is not None and not pd.isna(i.get("value"))][:limit]
    if not items:
        return f"<div class='pv-empty'>{escape(empty)}</div>"
    vals = [float(i["value"]) for i in items]
    mx, mn = max(vals) or 1.0, min(vals)
    out = ["<div class='pv-podium'>"]
    medals = ("pv-gold", "pv-silver", "pv-bronze")
    for k, it in enumerate(items[:3]):
        tag = f"<em>{escape(str(it['tag']))}</em>" if it.get("tag") else ""
        out.append(
            f"<div class='pv-card {medals[k]}' style='--acc:{accent}'><span class='pv-rank'>{k + 1}</span>"
            f"<div class='pv-avatar'>{escape(initials(it['name']))}{tag}</div>"
            f"<div class='pv-name' title='{escape(str(it['name']))}'>{it.get('badge', '')}{escape(str(it['name']))}</div>"
            f"<div class='pv-value'>{escape(_num(it['value'], value_fmt))}<small>{escape(_unit(it['value'], unit))}</small></div>"
            f"<div class='pv-sub'>{escape(str(it.get('sub', '')))}</div></div>")
    out.append("</div>")
    if len(items) > 3:
        out.append("<div class='pv-list'>")
        for k, it in enumerate(items[3:], 4):
            v = float(it["value"])
            pct = ((mx - v) / (mx - mn) * 85 + 15) if lower_is_better and mx != mn else (v / mx * 100 if mx else 0)
            out.append(
                f"<div class='pv-row'><span class='pv-n'>{k}</span><span class='pv-mini'>{escape(initials(it['name']))}</span>"
                f"<div class='pv-body'><div class='pv-head'><b>{it.get('badge', '')}{escape(str(it['name']))}</b>"
                f"<strong>{escape(_num(it['value'], value_fmt))}<small> {escape(_unit(it['value'], unit))}</small></strong></div>"
                f"<div class='pv-track'><i style='width:{max(4, min(100, pct)):.0f}%;background:{accent}'></i></div>"
                f"<span class='pv-rsub'>{escape(str(it.get('sub', '')))}</span></div></div>")
        out.append("</div>")
    return "".join(out)


def duel_html(rows, name_a, name_b, color_a=PT, color_b=RIVAL, logo_a="", logo_b=""):
    """Comparación cara a cara: cada fila = (indicador, valor A, valor B, texto A, texto B, más_es_mejor)."""
    head = (f"<div class='pv-duel-head'><span style='color:{color_a}'>{logo_a}{escape(name_a)}</span>"
            f"<span style='color:{color_b}'>{escape(name_b)}{logo_b}</span></div>")
    body = []
    for lab, a, b, ta, tb, better in rows:
        tot = (abs(a) + abs(b)) or 1
        wa, wb = abs(a) / tot * 100, abs(b) / tot * 100
        if not better:  # menos es mejor: la barra larga es para el valor más bajo
            wa, wb = wb, wa
        win_a = (a > b) if better else (a < b)
        win_b = (b > a) if better else (b < a)
        body.append(
            f"<div class='pv-duel-row'><b class='{'w' if win_a else ''}' style='color:{color_a}'>{escape(ta)}</b>"
            f"<div class='pv-duel-mid'><span>{escape(lab)}</span><div class='pv-duel-bar'>"
            f"<i class='l' style='width:{wa:.1f}%;background:{color_a}'></i><i class='r' style='width:{wb:.1f}%;background:{color_b}'></i></div></div>"
            f"<b class='{'w' if win_b else ''}' style='color:{color_b}'>{escape(tb)}</b></div>")
    return f"<div class='pv-duel'>{head}{''.join(body)}</div>"


def fig_radar(axes, series, height=380, max_vals=None):
    """Radar normalizado 0–100 sobre el máximo de cada eje; el hover muestra el valor real.
    series: lista de (nombre, valores_reales, color, textos)."""
    fig = go.Figure()
    mx = max_vals or [max(abs(s[1][i]) for s in series) or 1 for i in range(len(axes))]
    for name, vals, color, texts in series:
        r = [v / m * 100 if m else 0 for v, m in zip(vals, mx)]
        fig.add_scatterpolar(r=r + r[:1], theta=axes + axes[:1], name=name, fill="toself", mode="lines+markers",
                             line=dict(color=color, width=2.5), marker=dict(size=7, color=color),
                             fillcolor=_alpha(color, .18), customdata=list(texts) + list(texts[:1]),
                             hovertemplate="<b>" + escape(name) + "</b><br>%{theta}: %{customdata}<extra></extra>")
    fig.update_layout(**plotly_layout(height=height, margin=dict(l=40, r=40, t=30, b=30), polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(range=[0, 105], showticklabels=False, gridcolor=TOKENS["line-soft"], linecolor=TOKENS["line"]),
        angularaxis=dict(gridcolor=TOKENS["line"], linecolor=TOKENS["line"], tickfont=dict(color=TOKENS["text"], size=11)))))
    return fig


def _alpha(hex_color, a):
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    return f"rgba({int(h[:2], 16)},{int(h[2:4], 16)},{int(h[4:], 16)},{a})"


def fig_points_race(evo, short, reference, selected=None, height=420):
    """Puntos acumulados de todos los equipos (gris), Primer Toque en naranja y el elegido en azul.
    evo: salida de league_core.position_evolution (jornada, equipo, pos, pts, ...)."""
    fig = go.Figure()
    days = sorted(evo.jornada.unique())
    last = evo[evo.jornada == days[-1]] if days else evo
    for team, g in evo.groupby("equipo"):
        g = g.sort_values("jornada")
        main = team in (reference, selected)
        if main:
            continue
        fig.add_scatter(x=[f"J{j}" for j in g.jornada], y=g.pts, mode="lines", showlegend=False,
                        line=dict(color=GREY, width=1.2, shape="spline", smoothing=.4),
                        customdata=list(zip([short(team)] * len(g), g.pos)),
                        hovertemplate="%{customdata[0]} · %{x}: %{y} pts · %{customdata[1]}º<extra></extra>")
    for team, color, width in ([(selected, RIVAL, 3)] if selected and selected != reference else []) + [(reference, PT, 4)]:
        g = evo[evo.equipo == team].sort_values("jornada")
        if g.empty:
            continue
        fig.add_scatter(x=[f"J{j}" for j in g.jornada], y=g.pts, mode="lines+markers", name=short(team),
                        line=dict(color=color, width=width, shape="spline", smoothing=.4),
                        marker=dict(size=8, color=color, line=dict(color=TOKENS["surface"], width=2)),
                        fill="tozeroy" if team == reference else None, fillcolor=_alpha(PT, .08) if team == reference else None,
                        customdata=g.pos, hovertemplate=f"<b>{escape(short(team))}</b> · %{{x}}: %{{y}} pts · %{{customdata}}º<extra></extra>")
    lead = last.sort_values("pts", ascending=False).head(1)
    for r in lead.itertuples():
        fig.add_annotation(x=f"J{r.jornada}", y=r.pts, text=f"Líder: {escape(short(r.equipo))} ({r.pts})", showarrow=False,
                           xanchor="right", yanchor="bottom", font=dict(color=MUTED, size=11))
    fig.update_layout(**plotly_layout(height=height, margin=dict(l=12, r=16, t=36, b=12), hovermode="closest"))
    fig.update_yaxes(title=dict(text="Puntos acumulados", font=dict(size=11, color=MUTED)), rangemode="tozero")
    fig.update_xaxes(showgrid=False, categoryorder="array", categoryarray=[f"J{d}" for d in days])
    return fig


def fig_attack_defense(tab, short, reference, selected=None, height=440):
    """Mapa ataque/defensa: goles a favor y en contra por partido (eje Y invertido: arriba = encaja menos)."""
    t = tab[tab.pj > 0].copy()
    t["gfp"], t["gcp"], t["ppp"] = t.gf / t.pj, t.gc / t.pj, t.pts / t.pj
    colors = [PT if e == reference else (RIVAL if e == selected else "#56647A") for e in t.equipo]
    sizes = [10 + 14 * p / 3 for p in t.ppp]
    fig = go.Figure()
    fig.add_hline(y=t.gcp.mean(), line=dict(color=TOKENS["line"], dash="dot"))
    fig.add_vline(x=t.gfp.mean(), line=dict(color=TOKENS["line"], dash="dot"))
    keep = set(t.sort_values("ppp", ascending=False).equipo.head(3)) | set(t.sort_values("ppp").equipo.head(2)) | {reference, selected}
    fig.add_scatter(x=t.gfp, y=t.gcp, mode="markers+text", text=[short(e) if e in keep else "" for e in t.equipo], textposition="top center",
                    textfont=dict(size=10, color=TOKENS["text"]), cliponaxis=False,
                    marker=dict(size=sizes, color=colors, line=dict(color=TOKENS["surface"], width=1.5), opacity=.95),
                    customdata=list(zip(t.equipo.map(short), t.pos, t.pts, t.pj, t.gf, t.gc)),
                    hovertemplate="<b>%{customdata[0]}</b> · %{customdata[1]}º · %{customdata[2]} pts en %{customdata[3]} PJ"
                                  "<br>GF %{customdata[4]} (%{x:.2f}/p) · GC %{customdata[5]} (%{y:.2f}/p)<extra></extra>")
    fig.update_layout(**plotly_layout(height=height, showlegend=False, margin=dict(l=12, r=12, t=24, b=12)))
    fig.update_xaxes(title=dict(text="Goles a favor por partido", font=dict(size=11, color=MUTED)))
    fig.update_yaxes(title=dict(text="Goles en contra por partido", font=dict(size=11, color=MUTED)), autorange="reversed")
    return fig


def fig_league_3d(tab, short, reference, selected=None, height=520):
    """Vista 3D: goles a favor, goles en contra y puntos por partido de cada equipo (rotable)."""
    t = tab[tab.pj > 0].copy()
    t["gfp"], t["gcp"], t["ppp"] = t.gf / t.pj, t.gc / t.pj, t.pts / t.pj
    colors = [PT if e == reference else (RIVAL if e == selected else "#7D8BA1") for e in t.equipo]
    fig = go.Figure()
    for r, c in zip(t.itertuples(), colors):  # "palos" hasta el suelo para leer la altura
        fig.add_scatter3d(x=[r.gfp, r.gfp], y=[r.gcp, r.gcp], z=[0, r.ppp], mode="lines", showlegend=False,
                          line=dict(color=c, width=3), hoverinfo="skip", opacity=.5)
    top = set(t.sort_values("ppp", ascending=False).equipo.head(3)) | {reference, selected}
    fig.add_scatter3d(x=t.gfp, y=t.gcp, z=t.ppp, mode="markers+text", text=[short(e) if e in top else "" for e in t.equipo],
                      textfont=dict(size=10, color=TOKENS["ink"]), showlegend=False,
                      marker=dict(size=[9 if e in (reference, selected) else 6 for e in t.equipo], color=colors,
                                  line=dict(color=TOKENS["surface"], width=1)),
                      customdata=list(zip(t.equipo.map(short), t.pos, t.pts, t.pj)),
                      hovertemplate="<b>%{customdata[0]}</b> · %{customdata[1]}º · %{customdata[2]} pts (%{customdata[3]} PJ)"
                                    "<br>GF/p %{x:.2f} · GC/p %{y:.2f} · Pts/p %{z:.2f}<extra></extra>")
    ax = dict(backgroundcolor="rgba(0,0,0,0)", gridcolor=TOKENS["line"], zerolinecolor=TOKENS["line"],
              tickfont=dict(color=MUTED, size=10), title=dict(font=dict(color=TOKENS["text"], size=11)))
    fig.update_layout(**plotly_layout(height=height, margin=dict(l=0, r=0, t=10, b=0)),
                      scene=dict(xaxis={**ax, "title": {**ax["title"], "text": "GF / partido"}},
                                 yaxis={**ax, "title": {**ax["title"], "text": "GC / partido"}},
                                 zaxis={**ax, "title": {**ax["title"], "text": "Pts / partido"}, "range": [0, 3]},
                                 camera=dict(eye=dict(x=1.25, y=-1.25, z=.75), center=dict(x=0, y=0, z=-.1)), aspectmode="manual",
                                 aspectratio=dict(x=1.2, y=1.2, z=.8)))
    return fig


def fig_rank_bars(labels, values, color=PT, hover=None, value_fmt="%{x}", height=None, highlight=None, reverse=False):
    """Barras horizontales de ranking (mayor arriba). `highlight`: etiquetas a destacar en naranja."""
    n = len(labels)
    cols = [PT if highlight and lab in highlight else color for lab in labels]
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker=dict(color=cols, cornerradius=6),
                           text=[value_fmt(v) if callable(value_fmt) else v for v in values], textposition="outside",
                           textfont=dict(color=TOKENS["ink"], size=12), cliponaxis=False,
                           customdata=hover if hover is not None else labels,
                           hovertemplate="%{customdata}<extra></extra>"))
    fig.update_layout(**plotly_layout(height=height or max(220, 34 * n + 40), margin=dict(l=8, r=40, t=10, b=10), bargap=.32, showlegend=False))
    fig.update_yaxes(autorange="reversed" if not reverse else True, showgrid=False, tickfont=dict(color=TOKENS["text"], size=12))
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig


# ------------------------------------------------------------------ goles decisivos

def decisive_goals(partidos, eventos, team, side_of):
    """Clasifica los goles a favor de `team` según su peso en el resultado final.

    side_of(evento) -> 'favor' / 'contra' / None. Solo se analizan los partidos cuyos goles
    registrados cuadran con el marcador oficial y tienen minuto (si no, el orden no es fiable).
    Devuelve (DataFrame por jugador, nº de partidos descartados).
      ganador  = gol que dejó la ventaja definitiva en una victoria (el gol nº GC+1)
      empate   = último gol que igualó en un partido terminado en empate
      cambia   = gol que empató o puso por delante en cualquier momento
    """
    rows, skipped = [], 0
    p = partidos.copy()
    p["goles_local"] = pd.to_numeric(p["goles_local"], errors="coerce")
    p["goles_visitante"] = pd.to_numeric(p["goles_visitante"], errors="coerce")
    p = p.dropna(subset=["goles_local", "goles_visitante"])
    p = p[(p.local == team) | (p.visitante == team)]
    ev = eventos.copy()
    ev["jornada"] = pd.to_numeric(ev["jornada"], errors="coerce")
    ev["minx"] = pd.to_numeric(ev["minuto"], errors="coerce")
    for m in p.itertuples():
        gf, gc = (m.goles_local, m.goles_visitante) if m.local == team else (m.goles_visitante, m.goles_local)
        gf, gc = int(gf), int(gc)
        if gf == 0:
            continue
        e = ev[ev.jornada == m.jornada].copy()
        e["sidex"] = [side_of(r) for r in e.to_dict("records")]
        e = e[e.sidex.notna()]
        if (e.sidex == "favor").sum() != gf or (e.sidex == "contra").sum() != gc or e.minx.isna().any():
            skipped += 1
            continue
        e["ordx"] = range(len(e))
        e = e.sort_values(["minx", "ordx"], kind="stable")
        sf = sa = 0
        last_eq = None
        for r in e.itertuples():
            if r.sidex == "favor":
                sf += 1
                changes = sf >= sa and sf - 1 <= sa  # iguala o se pone por delante
                kind = None
                if gf > gc and sf == gc + 1:
                    kind = "ganador"
                own = r.equipo != team or r.tipo == "gol_propia" or "propia" in str(getattr(r, "detalle", "")).lower()
                rows.append(dict(jugador="" if own else str(r.jugador), jornada=int(m.jornada), minuto=int(r.minx), cambia=changes, tipo=kind))
                if sf == sa:
                    last_eq = len(rows) - 1
            else:
                sa += 1
        if gf == gc and last_eq is not None and sf == sa:
            rows[last_eq]["tipo"] = "empate"
    df = pd.DataFrame(rows, columns=["jugador", "jornada", "minuto", "cambia", "tipo"])
    if df.empty:
        return pd.DataFrame(columns=["jugador", "decisivos", "ganadores", "empates", "cambian", "goles"]), skipped
    df = df[~df.jugador.isin(["", "nan", "None", "G.P.", "GP", "Autogol"])]
    agg = df.groupby("jugador").agg(ganadores=("tipo", lambda s: int((s == "ganador").sum())),
                                    empates=("tipo", lambda s: int((s == "empate").sum())),
                                    cambian=("cambia", "sum"), goles=("tipo", "size")).reset_index()
    agg["decisivos"] = agg.ganadores + agg.empates
    agg = agg.sort_values(["decisivos", "cambian", "goles", "jugador"], ascending=[False, False, False, True])
    return agg[(agg.cambian > 0) | (agg.decisivos > 0)].reset_index(drop=True), skipped


def decisive_items(dec):
    """Convierte la salida de decisive_goals en tarjetas de player_cards_html."""
    items = []
    for r in dec.itertuples():
        parts = []
        if r.ganadores:
            parts.append(f"{r.ganadores} de la victoria")
        if r.empates:
            parts.append(f"{r.empates} del empate final")
        n = int(r.cambian)
        parts.append(f"{n} {'iguala o adelanta' if n == 1 else 'igualan o adelantan'} · {r.goles} {'gol' if r.goles == 1 else 'goles'}")
        items.append(dict(name=r.jugador, value=int(r.decisivos),
                          sub=" · ".join(parts)))
    return items
