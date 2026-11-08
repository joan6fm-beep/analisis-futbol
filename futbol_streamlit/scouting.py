"""SCOUTING FFCV · Segona Infantil Castelló 2026/2027.

Vistas: Equipos y jugadores (grupo → equipo → jugador), ficha individual, comparador,
ranking general y gestión de datos FFCV. Nunca se muestran valores inventados: lo que no
consta en la fuente aparece como «N/D».
"""
from __future__ import annotations

import base64
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import scouting_data as sd
from pt_viz import initials
from ui_theme import NEG, PLOTLY_CONFIG, POS, PT, RIVAL, TOKENS, plotly_layout

ND = "N/D"
TODOS = "Todos los equipos"
SERIES = [PT, RIVAL, POS, TOKENS["warn"]]

# Escudos ya presentes en la app y verificados para el club (el resto: insignia con iniciales).
_ESCUDOS = {
    "primer toque": sd.BASE / "primer_toque_logo.png",
    "villarreal cf": sd.BASE / "villarreal_logo.png",
    "cd castellon sad": sd.BASE / "escudos" / "castellon_logo.png",
    "cd roda": sd.BASE / "escudos" / "roda_logo.png",
}

CSS = """<style>
.sc-hero{display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:linear-gradient(120deg,var(--surface) 0%,#1a1410 100%);
 border:1px solid var(--line);border-left:4px solid var(--pt);border-radius:16px;padding:16px 20px;margin-bottom:14px}
.sc-hero h2{margin:0;font-size:1.35rem;color:var(--ink);letter-spacing:.02em}
.sc-hero p{margin:2px 0 0;color:var(--muted);font-size:.84rem}
.sc-chips{display:flex;gap:8px;flex-wrap:wrap}
.sc-chip{background:var(--surface-2);border:1px solid var(--line);border-radius:999px;padding:5px 11px;font-size:.76rem;color:var(--text)}
.sc-chip b{color:var(--pt)}
.sc-note{background:var(--pt-soft);border:1px solid rgba(245,135,31,.35);border-radius:12px;padding:10px 14px;color:var(--text);font-size:.84rem;margin:6px 0 12px}
.sc-teams{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin:6px 0 14px}
.sc-team{display:flex;align-items:center;gap:10px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.sc-team.pt{border-color:var(--pt)}
.sc-team .nm{color:var(--ink);font-weight:700;font-size:.85rem;line-height:1.15}
.sc-team .st{font-size:.72rem;color:var(--muted)}
.sc-team .st.ok{color:var(--pos)}
.sc-badge{flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;border-radius:50%;background:var(--surface-3);
 border:1px solid var(--line);color:var(--text);font-weight:800;overflow:hidden}
.sc-badge img{width:100%;height:100%;object-fit:contain}
.sc-card{display:flex;gap:18px;align-items:center;flex-wrap:wrap;background:radial-gradient(120% 140% at 0% 0%,rgba(245,135,31,.18) 0%,var(--surface) 55%);
 border:1px solid var(--line);border-radius:18px;padding:18px 20px;margin:8px 0 14px}
.sc-avatar{width:92px;height:92px;border-radius:50%;background:linear-gradient(145deg,var(--pt),#b35b0c);display:flex;align-items:center;
 justify-content:center;font-size:2rem;font-weight:900;color:#fff;box-shadow:0 8px 22px rgba(245,135,31,.25);position:relative}
.sc-avatar em{position:absolute;right:-4px;bottom:-4px;background:var(--bg);border:2px solid var(--pt);color:var(--ink);font-style:normal;
 font-size:.8rem;border-radius:999px;padding:1px 7px}
.sc-id h3{margin:0;color:var(--ink);font-size:1.35rem}
.sc-id .tm{display:flex;align-items:center;gap:8px;color:var(--text);margin-top:4px;font-size:.9rem}
.sc-id .mt{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.sc-stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:10px;margin:4px 0 14px}
.sc-stat{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
.sc-stat .v{font-size:1.6rem;font-weight:900;color:var(--ink);line-height:1.1}
.sc-stat .v.nd{color:var(--muted);font-size:1.15rem}
.sc-stat .l{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-top:3px}
.sc-stat.hl{border-color:var(--pt)} .sc-stat.hl .v{color:var(--pt)}
.sc-stat.y .v{color:var(--warn)} .sc-stat.r .v{color:var(--neg)} .sc-stat.g .v{color:var(--pos)}
@media (max-width:640px){.sc-avatar{width:70px;height:70px;font-size:1.5rem}.sc-stat .v{font-size:1.3rem}.sc-hero h2{font-size:1.1rem}}
</style>"""


# ---------------------------------------------------------------- helpers
def _fmt(v, dec=0, suf=""):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ND
    return f"{v:.{dec}f}{suf}" if dec else f"{int(round(v))}{suf}"


def _club_key(nombre):
    n = sd.norm(nombre)
    return next((k for k in _ESCUDOS if n.startswith(k) or k in n), None)


@st.cache_data(show_spinner=False)
def _img_b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()


def badge(nombre, size=34):
    p = sd.crest_path(nombre)
    if p is None:
        k = _club_key(nombre)
        p = _ESCUDOS.get(k) if k else None
    if p is not None and p.exists():
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "webp": "webp"}.get(p.suffix.lower().lstrip("."), "png")
        return (f"<span class='sc-badge' style='width:{size}px;height:{size}px;background:transparent;border:0'>"
                f"<img src='data:image/{mime};base64,{_img_b64(str(p))}' alt=''></span>")
    txt = escape(initials(sd.nombre_visible(nombre).replace("«", "").replace("»", "")))
    return f"<span class='sc-badge' style='width:{size}px;height:{size}px;font-size:{size * .36:.0f}px'>{txt}</span>"


def _styled(df, cols_fmt):
    return df.style.format({c: (lambda v, f=f: ND if pd.isna(v) else f.format(v)) for c, f in cols_fmt.items()}, na_rep=ND)


def _donut(valor, titulo, color):
    nd = valor is None or pd.isna(valor)
    v = 0 if nd else max(0.0, min(100.0, float(valor)))
    fig = go.Figure(go.Pie(values=[v, 100 - v] if not nd else [1], hole=.74, sort=False, direction="clockwise",
                           marker=dict(colors=[color, TOKENS["surface-2"]] if not nd else [TOKENS["surface-2"]]),
                           textinfo="none", hoverinfo="skip"))
    fig.update_layout(**plotly_layout(height=190, margin=dict(l=6, r=6, t=34, b=6), showlegend=False,
                                      title=dict(text=titulo, x=.5, xanchor="center", font=dict(size=13, color=TOKENS["text"])),
                                      annotations=[dict(text=ND if nd else f"<b>{v:.0f}%</b>", showarrow=False,
                                                        font=dict(size=22, color=TOKENS["muted"] if nd else TOKENS["ink"]))]))
    return fig


def _opciones_jugador(df):
    return {f"{r.nombre} · {r.equipo} · {r.grupo}": (r.jugador_id, r.equipo_id) for r in df.itertuples()}


# ---------------------------------------------------------------- vistas
def render(modulo="Equipos"):
    st.markdown(CSS, unsafe_allow_html=True)
    if sd.load("equipos").empty:
        st.error("No hay estructura de competición. Ejecuta `python tools/importar_scouting_ffcv.py --estructura`.")
        return
    comp = sd.load("competiciones").iloc[0]
    est = sd.estado_equipos()
    df = sd.tabla_jugadores()
    m = sd.meta()
    n_imp = int((est.estado == "importado").sum())
    ult = m.get("ultima_actualizacion", "")
    st.markdown(
        f"<div class='sc-hero'><div><h2>SCOUTING FFCV</h2><p>{escape(comp.nombre)} · Temporada 2026/2027 · "
        f"fuente oficial FFCV</p></div><div class='sc-chips'>"
        f"<span class='sc-chip'><b>{est.grupo_id.nunique()}</b> grupos</span>"
        f"<span class='sc-chip'><b>{len(est)}</b> equipos</span>"
        f"<span class='sc-chip'><b>{df.jugador_id.nunique()}</b> jugadores</span>"
        f"<span class='sc-chip'>Datos de <b>{n_imp}</b>/{len(est)} equipos</span>"
        f"<span class='sc-chip'>Última actualización: <b>{escape(ult.replace('T', ' ')[:16]) if ult else 'pendiente'}</b></span>"
        "</div></div>", unsafe_allow_html=True)
    if modulo == "Comparador":
        _vista_comparador(df)
    elif modulo == "Ranking":
        _vista_ranking(df, est)
    elif modulo == "Datos FFCV":
        _vista_datos(est)
    else:
        _vista_equipos(df, est)


def _vista_equipos(df, est):
    gr = sd.load("grupos").sort_values("numero", key=lambda s: s.astype(int))
    c1, c2, c3 = st.columns(3)
    g_nom = c1.selectbox("Grupo", gr.nombre.tolist(), key="sc_grupo")
    gid = gr.loc[gr.nombre == g_nom, "grupo_id"].iloc[0]
    eqg = est[est.grupo_id == gid].copy()
    eqg["vis"] = eqg.nombre.map(sd.nombre_visible)
    eqg = eqg.sort_values("vis")
    e_vis = c2.selectbox("Equipo", [TODOS] + eqg.vis.tolist(), key=f"sc_eq_{gid}")
    if e_vis == TODOS:
        sel = df[df.grupo_id == gid]
        eid = None
    else:
        eid = eqg.loc[eqg.vis == e_vis, "equipo_id"].iloc[0]
        sel = df[df.equipo_id == eid]
    jug_opts = sorted(sel.nombre.dropna().unique().tolist())
    j_nom = c3.selectbox("Jugador", ["—"] + jug_opts, key=f"sc_j_{gid}_{eid}",
                         help="Sin jugadores: el equipo aún no tiene datos importados (pestaña «Datos FFCV»).")

    if e_vis == TODOS:
        cards = ["<div class='sc-teams'>"]
        for r in eqg.itertuples():
            ok = r.estado == "importado"
            pt = " pt" if "primer toque" in sd.norm(r.nombre) else ""
            cards.append(f"<div class='sc-team{pt}'>{badge(r.nombre)}<div><div class='nm'>{escape(r.vis)}</div>"
                         f"<div class='st{' ok' if ok else ''}'>{f'{r.jugadores} jugadores' if ok else 'Pendiente de importar'}</div></div></div>")
        cards.append("</div>")
        st.markdown("".join(cards), unsafe_allow_html=True)
        if sel.empty:
            st.markdown("<div class='sc-note'>Ningún equipo de este grupo tiene todavía estadísticas importadas. "
                        "Los equipos son los oficiales de la FFCV; las estadísticas se añaden desde «Datos FFCV».</div>",
                        unsafe_allow_html=True)
            return
        st.markdown(f"**Estadísticas conjuntas · {escape(g_nom)}** (solo equipos con datos: "
                    f"{(eqg.estado == 'importado').sum()} de {len(eqg)})")
        agg = sel.groupby("equipo")[sd.STATS].sum(min_count=1).reset_index()
        _tabla(agg.rename(columns={"equipo": "Equipo"}), por_equipo=True)
    else:
        if sel.empty:
            st.markdown(f"<div class='sc-note'>{badge(eqg.loc[eqg.equipo_id == eid, 'nombre'].iloc[0], 26)} "
                        f"<b>{escape(e_vis)}</b>: pendiente de importar (ni ficha de temporada ni acta). Abre su página en "
                        f"<a href='{sd.FFCV_COMPETICIONES}' target='_blank'>FFCV · Competiciones</a>, guárdala "
                        "(Ctrl+S, «solo HTML») y súbela en «Datos FFCV».</div>", unsafe_allow_html=True)
            return
        st.markdown("**Totales de temporada** (ficha pública FFCV)")
        ev = _tabla(sel, key=f"sc_tab_{eid}")
        if ev is not None and j_nom == "—":
            j_nom = ev
        _bloque_acta(eid)
    if j_nom and j_nom != "—":
        fila = sel[sel.nombre == j_nom].iloc[0]
        _ficha(fila)


def _tabla(sel, por_equipo=False, key=None):
    if por_equipo:
        t = sel.rename(columns=sd.STAT_LABEL)
        cols = {sd.STAT_LABEL[c]: "{:.0f}" for c in sd.STATS}
        st.dataframe(_styled(t, cols), hide_index=True, width="stretch")
        return None
    t = sel[["nombre", "edad", "posicion", "convocatorias", "titularidades", "suplencias", "jugados", "goles",
             "amarillas", "dobles_amarillas", "rojas"]].copy()
    t["posicion"] = t.posicion.replace("", ND)
    t = t.sort_values(["jugados", "nombre"], ascending=[False, True], na_position="last").reset_index(drop=True)
    t.columns = ["Jugador", "Edad", "Posición", "Convocados", "Titular", "Suplente", "Jugados", "Goles",
                 "Amarillas", "Dobles amarillas", "Rojas"]
    fmt = {c: "{:.0f}" for c in t.columns if c not in ("Jugador", "Posición")}
    st.caption("Ordena pulsando en la cabecera · selecciona una fila para abrir la ficha · N/D = no consta en la fuente FFCV")
    ev = st.dataframe(_styled(t, fmt), hide_index=True, width="stretch", on_select="rerun",
                      selection_mode="single-row", key=key)
    rows = getattr(getattr(ev, "selection", None), "rows", []) if ev is not None else []
    return t.Jugador.iloc[rows[0]] if rows else None


def _ficha(r):
    meta_chips = []
    meta_chips.append(f"<span class='sc-chip'>Posición: <b>{escape(r.posicion) if r.posicion else ND}</b></span>")
    meta_chips.append(f"<span class='sc-chip'>Edad: <b>{_fmt(r.edad)}</b></span>")
    anio = r.anio_nacimiento if r.anio_verificado == "si" and r.anio_nacimiento else None
    meta_chips.append(f"<span class='sc-chip'>Año de nacimiento: <b>{anio or 'no verificado'}</b></span>")
    meta_chips.append(f"<span class='sc-chip'>{escape(r.grupo)}</span>")
    dorsal = f"<em>{int(r.dorsal)}</em>" if pd.notna(r.dorsal) else ""
    st.markdown(
        f"<div class='sc-card'><div class='sc-avatar'>{escape(initials(r.nombre))}{dorsal}</div>"
        f"<div class='sc-id'><h3>{escape(r.nombre)}</h3><div class='tm'>{badge(r.equipo_oficial, 28)}{escape(r.equipo)}</div>"
        f"<div class='mt'>{''.join(meta_chips)}</div></div></div>", unsafe_allow_html=True)
    tarjetas = [("convocatorias", "Convocatorias", ""), ("titularidades", "Titularidades", "hl"),
                ("suplencias", "Suplencias", ""), ("jugados", "Partidos jugados", "hl"), ("goles", "Goles", "g"),
                ("goles_partido", "Goles / partido", "g"), ("amarillas", "Amarillas", "y"),
                ("dobles_amarillas", "Dobles amarillas", "y"), ("rojas", "Rojas", "r"), ("verdes", "Verdes", "g")]
    h = ["<div class='sc-stats'>"]
    for c, lab, cls in tarjetas:
        v = r[c]
        txt = _fmt(v, 2) if c == "goles_partido" else _fmt(v)
        h.append(f"<div class='sc-stat {cls}'><div class='v{' nd' if txt == ND else ''}'>{txt}</div><div class='l'>{lab}</div></div>")
    h.append("</div>")
    st.markdown("".join(h), unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.plotly_chart(_donut(r.pct_titular, "Titularidad", PT), config=PLOTLY_CONFIG, key=f"d1_{r.jugador_id}")
    c2.plotly_chart(_donut(r.pct_participacion, "Participación", RIVAL), config=PLOTLY_CONFIG, key=f"d2_{r.jugador_id}")
    c3.plotly_chart(_donut(r.pct_sin_sancion, "Partidos sin sanción", POS), config=PLOTLY_CONFIG, key=f"d3_{r.jugador_id}")
    st.caption("Titularidad = titularidades / convocatorias · Participación = jugados / convocatorias · "
               "Partidos sin sanción: solo con datos por jornada verificables.")
    _acta_jugador(r)
    jor = sd.load("jornadas")
    jor = jor[(jor.jugador_id == r.jugador_id) & (jor.equipo_id == r.equipo_id)]
    if jor.empty:
        st.markdown("<div class='sc-note'>Evolución por jornadas: sin datos históricos verificables para este jugador.</div>",
                    unsafe_allow_html=True)
        return
    jor = jor.assign(**{c: pd.to_numeric(jor[c], errors="coerce") for c in sd.STATS + ["jornada"]}).sort_values("jornada")
    fig = go.Figure()
    fig.add_bar(x=jor.jornada, y=jor.goles, name="Goles", marker_color=PT)
    fig.add_scatter(x=jor.jornada, y=jor.titularidades, name="Titular (1/0)", mode="markers+lines", line=dict(color=RIVAL))
    fig.update_layout(**plotly_layout(height=300, title="Evolución por jornadas"))
    fig.update_xaxes(title="Jornada", dtick=1)
    st.plotly_chart(fig, config=PLOTLY_CONFIG, key=f"evo_{r.jugador_id}")


def _nombre_eq(eid):
    eq = sd.load("equipos").set_index("equipo_id").nombre
    return sd.nombre_visible(eq.get(eid, eid))


def _bloque_acta(eid):
    p, filas = sd.ultima_acta(eid)
    if p is None:
        st.markdown("<div class='sc-note'>Último partido con acta: pendiente de incorporar.</div>", unsafe_allow_html=True)
        return
    st.markdown(f"**Último partido con acta · J{p.jornada} · {escape(p.fecha)}** — "
                f"{escape(_nombre_eq(p.local_id))} {p.goles_local or '?'}-{p.goles_visitante or '?'} "
                f"{escape(_nombre_eq(p.visitante_id))}")
    st.caption("Datos de un único partido: no son los acumulados de la temporada.")
    j = sd.load("jugadores").set_index("jugador_id").nombre
    t = filas.assign(Jugador=filas.jugador_id.map(j))
    t = t[["dorsal", "Jugador", "rol", "demarcacion", "participa", "minutos", "goles", "amarillas", "dobles_amarillas", "rojas"]]
    t = t.replace("", ND).rename(columns={"dorsal": "Dorsal", "rol": "Titular/Suplente", "demarcacion": "Demarcación",
                                         "participa": "Jugó", "minutos": "Minutos", "goles": "Goles", "amarillas": "Amarillas",
                                         "dobles_amarillas": "Dobles amarillas", "rojas": "Rojas"})
    t["_o"] = pd.to_numeric(t.Dorsal, errors="coerce")
    t = t.sort_values(["Titular/Suplente", "_o"], ascending=[False, True]).drop(columns="_o")
    st.dataframe(t, hide_index=True, width="stretch")


def _acta_jugador(r):
    aj = sd.load("actas_jugadores")
    aj = aj[(aj.jugador_id == r.jugador_id) & (aj.equipo_id == r.equipo_id)]
    if aj.empty:
        return
    pa = sd.load("partidos").set_index("partido_id")
    h = ["<div class='sc-note'><b>Partidos con acta</b> (datos por partido, no acumulados):<br>"]
    for a in aj.itertuples():
        p = pa.loc[a.partido_id]
        riv = p.visitante_id if p.local_id == r.equipo_id else p.local_id
        extra = [a.rol, f"{a.minutos}'" if a.minutos else f"minutos {ND}"]
        extra += [f"{a.goles} gol(es)"] if a.goles not in ("", "0") else []
        extra += [f"{a.amarillas} amarilla(s)"] if a.amarillas not in ("", "0") else []
        extra += ["roja"] if a.rojas not in ("", "0") else []
        h.append(f"J{p.jornada} vs {escape(_nombre_eq(riv))} · dorsal {escape(a.dorsal)} · {escape(' · '.join(extra))}<br>")
    h.append("</div>")
    st.markdown("".join(h), unsafe_allow_html=True)


def _vista_comparador(df):
    if df.empty:
        st.markdown("<div class='sc-note'>El comparador se activa cuando haya jugadores importados.</div>", unsafe_allow_html=True)
        return
    pos = sorted(p for p in df.posicion.dropna().unique() if p)
    c1, c2 = st.columns([1, 3])
    misma = c1.toggle("Misma posición", key="sc_cmp_pos", disabled=not pos)
    base = df
    if misma and pos:
        p = c1.selectbox("Posición", pos, key="sc_cmp_posv")
        base = df[df.posicion == p]
    opts = _opciones_jugador(base)
    elegidos = c2.multiselect("Jugadores (2 a 4, de cualquier equipo o grupo)", list(opts), max_selections=4, key="sc_cmp")
    if len(elegidos) < 2:
        st.caption("Selecciona al menos 2 jugadores.")
        return
    idx = [opts[k] for k in elegidos]
    sel = pd.concat([df[(df.jugador_id == j) & (df.equipo_id == e)] for j, e in idx])
    met = [("edad", "Edad"), ("convocatorias", "Convocatorias"), ("titularidades", "Titularidades"),
           ("suplencias", "Suplencias"), ("jugados", "Jugados"), ("goles", "Goles")]
    fig = go.Figure()
    for k, r in enumerate(sel.itertuples()):
        vals = [getattr(r, c) for c, _ in met]
        fig.add_bar(y=[l for _, l in met], x=vals, name=r.nombre, orientation="h", marker_color=SERIES[k],
                    text=[_fmt(v) for v in vals], textposition="outside", cliponaxis=False)
    fig.update_layout(**plotly_layout(height=430, barmode="group", bargap=.25, title="Comparativa"))
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, config=PLOTLY_CONFIG, key="cmp_bars")
    ratios = [("pct_titular", "% titularidad"), ("pct_participacion", "% participación"),
              ("goles_partido", "Goles/partido"), ("tarjetas", "Tarjetas (A+R)")]
    cols = st.columns(len(ratios))
    for (c, lab), col in zip(ratios, cols):
        f = go.Figure(go.Bar(x=[initials(n) + " " + n.split()[0] for n in sel.nombre], y=sel[c],
                             marker_color=SERIES[:len(sel)], text=[_fmt(v, 2 if c == "goles_partido" else 0) for v in sel[c]],
                             textposition="outside", cliponaxis=False, hovertext=sel.nombre))
        f.update_layout(**plotly_layout(height=260, title=lab, showlegend=False))
        col.plotly_chart(f, config=PLOTLY_CONFIG, key=f"cmp_{c}")
    t = sel[["nombre", "equipo", "grupo", "posicion", "edad", "convocatorias", "titularidades", "suplencias",
             "jugados", "goles", "goles_partido", "amarillas", "dobles_amarillas", "rojas"]]
    st.dataframe(_styled(t, {c: "{:.0f}" for c in t.columns[4:] if c != "goles_partido"} | {"goles_partido": "{:.2f}"}),
                 hide_index=True, width="stretch")


RANKINGS = {"Más titularidades": ("titularidades", 0), "Más partidos jugados": ("jugados", 0),
            "Más goles": ("goles", 0), "Mayor % de titularidad": ("pct_titular", 0),
            "Mayor promedio goleador": ("goles_partido", 2)}


def _vista_ranking(df, est):
    n_imp, n_tot = int((est.estado == "importado").sum()), len(est)
    if df.empty:
        st.markdown(f"<div class='sc-note'>Ranking sin datos: 0 de {n_tot} equipos importados.</div>", unsafe_allow_html=True)
        return
    c1, c2, c3, c4 = st.columns(4)
    gr = c1.selectbox("Grupo", ["Todos"] + sorted(df.grupo.dropna().unique(), key=lambda s: int(s.split()[-1])), key="sc_rk_g")
    d = df if gr == "Todos" else df[df.grupo == gr]
    eq = c2.selectbox("Equipo", ["Todos"] + sorted(d.equipo.dropna().unique()), key="sc_rk_e")
    d = d if eq == "Todos" else d[d.equipo == eq]
    pos = c3.selectbox("Posición", ["Todas"] + sorted(p for p in d.posicion.dropna().unique() if p), key="sc_rk_p")
    d = d if pos == "Todas" else d[d.posicion == pos]
    rk = c4.selectbox("Ranking", list(RANKINGS), key="sc_rk_t")
    q = st.text_input("Buscar jugador por nombre", key="sc_rk_q")
    if q:
        d = d[d.nombre.map(sd.norm).str.contains(sd.norm(q), regex=False)]
    col, dec = RANKINGS[rk]
    d = d.dropna(subset=[col]).sort_values([col, "nombre"], ascending=[False, True])
    alcance = (f"Todos los equipos del ámbito ({n_tot})" if n_imp == n_tot
               else f"Solo datos recopilados: {n_imp} de {n_tot} equipos importados")
    st.markdown(f"<div class='sc-note'><b>Alcance:</b> {alcance}. Jugadores sin el dato ({ND}) no entran en el ranking.</div>",
                unsafe_allow_html=True)
    items = [dict(name=r.nombre, value=getattr(r, col), sub=f"{r.equipo} · {r.grupo}", badge=badge(r.equipo_oficial, 18),
                  tag=_fmt(r.dorsal) if pd.notna(r.dorsal) else "") for r in d.head(10).itertuples()]
    from pt_viz import player_cards_html
    st.markdown(player_cards_html(items, value_fmt=lambda v: f"{v:.{dec}f}" if dec else f"{v:.0f}", limit=10,
                                  unit="%" if col == "pct_titular" else ""), unsafe_allow_html=True)
    t = d[["nombre", "equipo", "grupo", "posicion", "edad", "convocatorias", "titularidades", "jugados", "goles",
           "pct_titular", "goles_partido"]].rename(columns={"pct_titular": "% titular", "goles_partido": "Goles/partido"})
    st.dataframe(_styled(t, {c: "{:.0f}" for c in t.columns[4:9]} | {"% titular": "{:.0f}%", "Goles/partido": "{:.2f}"}),
                 hide_index=True, width="stretch")


def _vista_datos(est):
    m = sd.meta()
    st.markdown(
        "<div class='sc-note'><b>Cómo se obtienen los datos.</b> La FFCV sirve las estadísticas de jugador desde "
        "<code>ffcv.es/competiciones/api/</code>, ruta que su <code>robots.txt</code> prohíbe a programas automáticos. "
        "Por eso la app no las descarga sola: abre la página pública del equipo en tu navegador, guárdala "
        "(Ctrl+S → «Página web, solo HTML») o exporta la tabla a CSV/XLSX, y súbela aquí. Se guarda una copia local, "
        "no se duplican jugadores y lo que no figure en la fuente queda como N/D. No se guardan fotos ni fechas de "
        "nacimiento completas (menores).</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("**Importar página de un equipo**")
        gr = sd.load("grupos").sort_values("numero", key=lambda s: s.astype(int))
        g = st.selectbox("Grupo", gr.nombre.tolist(), key="sc_imp_g")
        gid = gr.loc[gr.nombre == g, "grupo_id"].iloc[0]
        eqg = est[est.grupo_id == gid].assign(vis=lambda x: x.nombre.map(sd.nombre_visible)).sort_values("vis")
        e = st.selectbox("Equipo", eqg.vis.tolist(), key=f"sc_imp_e_{gid}")
        eid = eqg.loc[eqg.vis == e, "equipo_id"].iloc[0]
        f = st.file_uploader("Archivo FFCV (HTML, CSV o XLSX)", type=["html", "htm", "csv", "xlsx"], key="sc_imp_f")
        if f is not None and st.button("Importar", type="primary", key="sc_imp_btn"):
            try:
                r = sd.importar(eid, f.name, f.getvalue())
                (st.success if r["ok"] else st.error)(
                    f"{r['mensaje']} · {r.get('jugadores', 0)} jugadores · columnas: {', '.join(r['columnas']) or '—'}")
            except Exception as ex:
                st.error(f"No se pudo importar: {ex}")
    with c2:
        st.markdown("**Actualizar FFCV**")
        ult = m.get("ultima_actualizacion", "")
        st.caption(f"Última actualización de datos: {ult.replace('T', ' ') if ult else 'pendiente'} · "
                   f"última comprobación: {m.get('ultima_comprobacion', '—').replace('T', ' ')}")
        if st.button("Actualizar FFCV", key="sc_upd"):
            r = sd.actualizar_desde_fuente()
            msg = f"Archivos nuevos o modificados: {r['nuevos']} · sin cambios: {r['sin_cambios']} · errores: {r['errores']}"
            try:
                p = sd.comprobar_publicacion_grupos()
                msg += (" · ⚠ La FFCV ha modificado la publicación de grupos: revisar equipos."
                        if p["cambiada"] else f" · Publicación oficial de grupos sin cambios ({p['grupos_anunciados']} grupos).")
            except Exception as ex:
                msg += f" · No se pudo consultar la publicación de grupos ({type(ex).__name__})."
            st.info(msg)
            for d in r["detalles"]:
                st.caption(d)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Importar actas transcritas**")
        st.caption("Archivo .txt con el formato de las actas del Cadete A (cabecera «PARTIDO G<n> J<n> | fecha | local | "
                   "visitante | resultado»). Añade los jugadores del partido sin mezclarlos con los totales de temporada.")
        fa = st.file_uploader("Actas (.txt)", type=["txt"], key="sc_act_f")
        if fa is not None and st.button("Importar actas", key="sc_act_btn"):
            r = sd.importar_actas_texto(fa.getvalue().decode("utf-8", errors="replace"), fa.name)
            dst = sd.FUENTE / "actas"
            dst.mkdir(parents=True, exist_ok=True)
            (dst / fa.name).write_bytes(fa.getvalue())
            (st.success if r["partidos"] else st.error)(f"{r['partidos']} actas · {r['jugadores']} jugadores")
            for a in r["avisos"][:20]:
                st.caption(f"Aviso: {a}")
    with c4:
        st.markdown("**Escudo oficial de un club**")
        st.caption("Imagen del escudo (PNG/JPG/WEBP) guardada desde la FFCV o la web oficial del club. "
                   "Se aplica a todos los equipos del club.")
        clubes = sorted({sd.club_slug(n): sd.nombre_visible(" ".join(n.split()[:-1]) if sd.club_slug(n) != sd.slug(n) else n)
                         for n in est.nombre}.items(), key=lambda x: x[1])
        ck = st.selectbox("Club", [c for c, _ in clubes], format_func=dict(clubes).get, key="sc_esc_c")
        fe = st.file_uploader("Escudo", type=["png", "jpg", "jpeg", "webp"], key="sc_esc_f")
        if fe is not None and st.button("Guardar escudo", key="sc_esc_btn"):
            sd.ESCUDOS.mkdir(parents=True, exist_ok=True)
            for old in sd.ESCUDOS.glob(f"{ck}.*"):
                old.unlink()
            ext = fe.name.rsplit(".", 1)[-1].lower()
            (sd.ESCUDOS / f"{ck}.{'jpg' if ext == 'jpeg' else ext}").write_bytes(fe.getvalue())
            st.success("Escudo guardado.")
        st.caption(f"Clubes con escudo propio: {sum(1 for c, _ in clubes if any(sd.ESCUDOS.glob(c + '.*')))} de {len(clubes)}")
    st.markdown("**Estado por equipo**")
    t = est.assign(Equipo=est.nombre.map(sd.nombre_visible),
                   Grupo=est.grupo_id.str.extract(r"g(\d+)$")[0].astype(int))[["Grupo", "Equipo", "estado", "jugadores", "cod_ffcv"]]
    t = t.rename(columns={"estado": "Estado", "jugadores": "Jugadores", "cod_ffcv": "Código FFCV"}).sort_values(["Grupo", "Equipo"])
    st.dataframe(t, hide_index=True, width="stretch", height=320)
    with st.expander("Plantilla CSV para introducir datos copiados de la FFCV"):
        st.download_button("Descargar plantilla CSV",
                           ("Jugador;Dorsal;Posición;Edad;Fecha nacimiento;Convocatorias;Titularidades;Suplencias;"
                            "Jugados;Goles;Amarillas;Dobles amarillas;Rojas;Verdes\n").encode("utf-8-sig"),
                           file_name="plantilla_scouting_ffcv.csv", key="sc_tpl")
        st.caption("Deja en blanco lo que la FFCV no muestre (se verá como N/D). Para la evolución por jornadas, añade una "
                   "columna «Jornada» con una fila por jugador y jornada.")
