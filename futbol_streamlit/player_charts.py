"""Gráficos de la ficha individual (Jugadores). Solo datos cargados; ausencias = sin punto."""
import pandas as pd
import plotly.graph_objects as go

from ui_theme import TOKENS, PT, RIVAL, MUTED, plotly_layout

# etiqueta -> (columna o cálculo, unidad, descripción)
PHYS_METRICS = {
    "Distancia": ("distancia_km", "km", "Distancia total rastreada en el partido"),
    "Distancia por 90'": ("dist90", "km/90'", "Distancia ÷ minutos rastreados × 90: compara jugadores con minutos distintos"),
    "Velocidad máxima": ("velocidad_max_kmh", "km/h", "Pico de velocidad registrado"),
    "Velocidad media": ("velocidad_media_kmh", "km/h", "Velocidad media durante los minutos rastreados"),
    "Sprints": ("sprints", "sprints", "Número de sprints"),
    "Alta intensidad": ("carreras_alta_intensidad", "carreras", "Carreras de alta intensidad"),
}


def prepare_video(adv):
    d = adv.copy()
    for c in ["jornada", "dorsal", "distancia_km", "minutos_rastreados", "velocidad_max_kmh", "velocidad_media_kmh",
              "sprints", "carreras_alta_intensidad"]:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    d["dist90"] = d["distancia_km"] / d["minutos_rastreados"].where(d["minutos_rastreados"] > 0) * 90
    return d.dropna(subset=["jornada", "dorsal"])


def fig_minutes(rows):
    """rows: DataFrame con jornada, minutos, titular, goles, tarjetas."""
    fig = go.Figure()
    fig.update_layout(**plotly_layout(height=240, margin=dict(l=12, r=12, t=36, b=12), barcornerradius=4, bargap=.35))
    x = [f"J{int(j)}" for j in rows.jornada]
    for flag, name, color in ((1, "Titular", PT), (0, "Suplente", RIVAL)):
        s = rows[rows.titular == flag]
        fig.add_bar(x=[f"J{int(j)}" for j in s.jornada], y=s.minutos, name=name, marker_color=color,
                    text=[f"{int(m)}'" for m in s.minutos], textposition="outside", textfont=dict(color=TOKENS["text"], size=11),
                    cliponaxis=False, hovertemplate="%{x}: %{y} min · " + name.lower() + "<extra></extra>")
    marks = [("⚽" * int(g) + "🟨" * int(c)) for g, c in zip(rows.goles, rows.tarjetas)]
    fig.add_scatter(x=x, y=[113] * len(x), mode="text", text=marks, showlegend=False, hoverinfo="skip")
    fig.update_yaxes(range=[0, 122], tickvals=[0, 45, 90], ticksuffix="'", title=dict(text="Minutos", font=dict(size=11, color=MUTED)))
    fig.update_xaxes(showgrid=False, categoryorder="array", categoryarray=x)
    return fig


def fig_physical(d, dorsal, metric, compare=None):
    """Evolución por jornada: jugador, media del equipo (jugadores con dato) y comparado opcional."""
    col, unit, _ = PHYS_METRICS[metric]
    team = d.dropna(subset=[col]).groupby("jornada")[col].agg(["mean", "count"]).reset_index()
    fig = go.Figure()
    fig.update_layout(**plotly_layout(height=300, margin=dict(l=12, r=12, t=40, b=12)))
    if not team.empty:
        fig.add_scatter(x=[f"J{int(j)}" for j in team.jornada], y=team["mean"], name="Media del equipo", mode="lines+markers",
                        line=dict(color=MUTED, width=2, dash="dot"), marker=dict(size=7, color=MUTED),
                        customdata=team["count"], hovertemplate="%{x} · media equipo %{y:.1f} " + unit + " (%{customdata} jugadores)<extra></extra>")
    series = [(dorsal, "Jugador", PT)] + ([(compare[0], compare[1], RIVAL)] if compare else [])
    for dn, name, color in series:
        s = d[(d.dorsal == dn)].dropna(subset=[col]).sort_values("jornada")
        if s.empty:
            continue
        fig.add_scatter(x=[f"J{int(j)}" for j in s.jornada], y=s[col], name=name, mode="lines+markers+text",
                        line=dict(color=color, width=2.5), marker=dict(size=10, color=color, line=dict(color=TOKENS["surface"], width=2)),
                        text=[f"{v:.1f}".rstrip("0").rstrip(".") for v in s[col]], textposition="top center",
                        textfont=dict(color=TOKENS["text"], size=11),
                        hovertemplate="%{x} · " + name + " %{y:.1f} " + unit + "<extra></extra>")
    js = sorted(d.dropna(subset=[col]).jornada.unique())
    fig.update_xaxes(categoryorder="array", categoryarray=[f"J{int(j)}" for j in js], showgrid=False)
    fig.update_yaxes(title=dict(text=f"{metric} ({unit})", font=dict(size=11, color=MUTED)), rangemode="tozero")
    return fig
