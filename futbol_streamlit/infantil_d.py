"""Infantil D · 2ª Regional 2026/27: datos, Inicio y Minutos.

Fuente: Excel «SEGUIMIENTO INFANTIL D 2ª REGIONAL TEMP. 26-27», importado con
tools/importar_infantil_d.py a data/infantil_d/. Reglas del Excel respetadas:
«-» = no participó (0 minutos explícitos); celda vacía = jornada sin dato (no es 0).
"""
from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui_theme import TOKENS, PT, RIVAL, MUTED, plotly_layout, PLOTLY_CONFIG

DIR = Path(__file__).parent / "data" / "infantil_d"
MATCH_MINUTES = 70  # fila TOTAL del Excel: 770 = 11 × 70
TEAM_LABEL = "Infantil D"

CSS = """<style>
.q-title{font-size:1rem;font-weight:800;color:var(--ink);margin:2px 0 2px;letter-spacing:-.01em}
.q-sub{font-size:.76rem;color:var(--muted);margin-bottom:8px}
.inf-hero{display:grid;grid-template-columns:1.25fr 1fr;gap:18px;align-items:stretch;margin:4px 0 14px}
.inf-photo{border-radius:18px;overflow:hidden;border:1px solid var(--line);background:#0D131C;position:relative}
.inf-photo .bg{position:absolute;inset:-30px;width:calc(100% + 60px);height:calc(100% + 60px);object-fit:cover;filter:blur(22px);opacity:.4}
.inf-photo .ph{position:relative;width:100%;height:auto;display:block}
.inf-card{background:linear-gradient(180deg,#141C2A,#101620);border:1px solid var(--line);box-shadow:inset 0 2px 0 var(--pt);border-radius:18px;padding:20px 22px;display:flex;flex-direction:column;justify-content:center}
.inf-card .k{font-size:.7rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--pt)}
.inf-card h2{margin:6px 0 4px!important;font-size:2rem!important;font-weight:900!important;color:var(--ink)!important;letter-spacing:-.03em}
.inf-card p{color:var(--muted);font-size:.86rem;margin:0}
.inf-links{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.inf-links a{background:var(--surface-2);border:1px solid var(--line);color:var(--ink)!important;text-decoration:none!important;font-weight:700;font-size:.8rem;padding:8px 12px;border-radius:10px}
.inf-links a.main{background:var(--pt);color:#1A0E02!important;border-color:var(--pt)}
.inf-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0 0 14px}
.inf-kpi{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
.inf-kpi small{display:block;font-size:.66rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.inf-kpi b{display:block;font-size:1.6rem;font-weight:900;color:var(--ink);letter-spacing:-.02em;margin-top:2px}
.inf-kpi span{font-size:.7rem;color:var(--muted)}
.inf-match{display:grid;grid-template-columns:48px 1fr auto;gap:12px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:10px 14px;margin-bottom:8px}
.inf-match .j{background:var(--surface-3);color:var(--ink);font-weight:800;border-radius:9px;text-align:center;padding:6px 0}
.inf-match .t{color:var(--ink);font-weight:700;font-size:.86rem} .inf-match .t small{display:block;color:var(--muted);font-weight:500;font-size:.7rem}
.inf-badge{font-size:.66rem;font-weight:800;border-radius:999px;padding:3px 9px}
.inf-badge.ok{color:var(--pos);background:rgba(43,196,138,.12)} .inf-badge.part{color:var(--warn);background:rgba(242,193,78,.12)} .inf-badge.pend{color:var(--muted);background:var(--surface-2)}
.xl-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:14px;background:var(--surface);-webkit-overflow-scrolling:touch}
.xl{border-collapse:separate;border-spacing:0;font-size:.8rem;min-width:100%}
.xl th{background:var(--surface-2);color:var(--muted);font-size:.68rem;font-weight:800;letter-spacing:.05em;padding:9px 10px;text-align:center;white-space:nowrap;position:sticky;top:0}
.xl td{padding:7px 10px;text-align:center;border-top:1px solid var(--line-soft);white-space:nowrap;color:var(--text);min-width:46px}
.xl .d{position:sticky;left:0;background:var(--surface);z-index:2;color:var(--muted);font-weight:800;min-width:38px}
.xl .n{position:sticky;left:38px;background:var(--surface);z-index:2;text-align:left;color:var(--ink);font-weight:700;min-width:130px;box-shadow:1px 0 0 var(--line)}
.xl th.d,.xl th.n{z-index:3;background:var(--surface-2)}
.xl .tot{font-weight:900;color:var(--ink);background:var(--pt-soft)}
.xl .no{color:#5A6880}
.xl tfoot td{font-weight:900;color:var(--ink);background:var(--surface-2)}
.xl tfoot td.n,.xl tfoot td.d{background:var(--surface-2)}
.xl-legend{display:flex;gap:14px;flex-wrap:wrap;font-size:.72rem;color:var(--text);margin:0 0 6px}
.xl-legend i{display:inline-block;width:14px;height:10px;border-radius:3px;margin-right:5px;vertical-align:middle}
@media(max-width:760px){.inf-hero{grid-template-columns:1fr}.inf-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.inf-card h2{font-size:1.5rem!important}}
</style>"""


# ---------------------------------------------------------------- datos
def _stamp():
    return tuple((p.name, p.stat().st_mtime_ns) for p in sorted(DIR.glob("*.csv")))


@st.cache_data(show_spinner=False)
def _load(stamp):
    jug = pd.read_csv(DIR / "jugadores.csv")
    wide = pd.read_csv(DIR / "minutos.csv", dtype=str).fillna("")
    part = pd.read_csv(DIR / "partidos.csv").fillna("")
    form = pd.read_csv(DIR / "formaciones_excel.csv").fillna("")
    jcols = [c for c in wide.columns if c.startswith("J")]
    long = wide.melt(id_vars=["dorsal", "jugador"], value_vars=jcols, var_name="col", value_name="raw")
    long["jornada"] = long["col"].str[1:].astype(int)
    long["dorsal"] = long["dorsal"].astype(int)
    long["minutos"] = pd.to_numeric(long["raw"].replace("-", "0"), errors="coerce")  # «-» = 0 explícito; vacío = NaN
    long["no_jugo"] = long["raw"].eq("-")
    return jug, wide, part, form, long, jcols


def data():
    return _load(_stamp())


def played_jornadas(long):
    return sorted(long.loc[long.minutos.notna(), "jornada"].unique().tolist())


def player_summary(long, jornadas, form):
    d = long[long.jornada.isin(jornadas)]
    g = d.groupby(["dorsal", "jugador"], as_index=False).agg(minutos=("minutos", "sum"),
                                                             pj=("minutos", lambda s: int((s > 0).sum())),
                                                             con_dato=("minutos", lambda s: int(s.notna().sum())))
    g["posibles"] = g.con_dato * MATCH_MINUTES
    g["participacion"] = (100 * g.minutos / g.posibles).where(g.posibles > 0)
    starts = form[(form.momento == "inicio") & (form.estado == "ok") & form.jornada.isin(jornadas)].groupby("jugador").size()
    g["titular"] = g.jugador.map(starts).fillna(0).astype(int)
    return g.sort_values(["minutos", "dorsal"], ascending=[False, True]).reset_index(drop=True)


# ---------------------------------------------------------------- vistas
def _kpi(label, value, sub):
    return f"<div class='inf-kpi'><small>{escape(label)}</small><b>{value}</b><span>{escape(sub)}</span></div>"


def render_home(photo_uri):
    st.markdown(CSS, unsafe_allow_html=True)
    jug, wide, part, form, long, jcols = data()
    pj = played_jornadas(long)
    photo = (f"<div class='inf-photo'><img class='bg' src='{photo_uri}' alt=''><img class='ph' src='{photo_uri}' alt='Infantil D'></div>"
             if photo_uri else "<div class='inf-photo'></div>")
    st.markdown(f"<div class='inf-hero'>{photo}<div class='inf-card'><span class='k'>Primer Toque C.F. · 2ª Regional · 2026/27</span>"
                "<h2>Infantil D</h2><p>Seguimiento de minutos, formaciones, calendario y comunicación del equipo.</p>"
                "<div class='inf-links'><a class='main' href='?area=infantil&view=minutos' target='_self'>Minutos →</a>"
                "<a href='?area=infantil&view=seguimiento' target='_self'>Seguimiento</a>"
                "<a href='?area=infantil&view=calendario' target='_self'>Calendario</a>"
                "<a href='?area=infantil&view=muro' target='_self'>Muro</a></div></div></div>", unsafe_allow_html=True)
    tot = long.minutos.sum()
    used = long[long.minutos > 0].jugador.nunique()
    st.markdown("<div class='inf-kpis'>" + _kpi("Jugadores", len(jug), "en la plantilla del Excel")
                + _kpi("Jornadas con minutos", len(pj), ", ".join(f"J{j}" for j in pj) or "—")
                + _kpi("Minutos repartidos", f"{int(tot)}", f"{MATCH_MINUTES}' por partido · 11 jugadores")
                + _kpi("Jugadores utilizados", used, f"de {len(jug)}") + "</div>", unsafe_allow_html=True)
    st.markdown("<div class='q-title'>Jornadas del Excel</div><div class='q-sub'>Datos de la cabecera de cada hoja y estado de las formaciones.</div>",
                unsafe_allow_html=True)
    cls = {"completa": ("ok", "Formación completa"), "parcial": ("part", "Formación parcial"), "pendiente": ("pend", "Formación pendiente")}
    rows = []
    for r in part.itertuples():
        c, txt = cls.get(r.estado_formacion, ("pend", r.estado_formacion))
        sub = " · ".join(x for x in (r.fecha, f"Inicio {r.sistema_inicio}" if r.sistema_inicio else "", f"Final {r.sistema_final}" if r.sistema_final else "") if x)
        mins = "con minutos" if int(r.jornada) in pj else "sin minutos en el Excel"
        rows.append(f"<div class='inf-match'><span class='j'>J{int(r.jornada)}</span><span class='t'>{escape(r.partido_excel or 'Partido sin datos en la hoja')}"
                    f"<small>{escape(sub)} · {mins}</small></span><span class='inf-badge {c}'>{txt}</span></div>")
    st.markdown("".join(rows), unsafe_allow_html=True)
    notes = [f"J{int(r.jornada)}: {r.notas}" for r in part.itertuples() if r.notas]
    pend = form[form.estado != "ok"]
    notes += [f"J{int(r.jornada)} {r.momento}: «{r.texto_excel}» ({r.celda}) — {r.estado}" for r in pend.itertuples()]
    if notes:
        with st.expander(f"Datos del Excel pendientes de revisar ({len(notes)})"):
            st.markdown("\n".join(f"- {escape(n)}" for n in notes))


def _cell_color(v):
    """Escala secuencial naranja según los minutos sobre el máximo del partido."""
    a = .12 + .7 * min(v, MATCH_MINUTES) / MATCH_MINUTES
    return f"background:rgba(245,135,31,{a:.2f});color:{'#1A0E02' if a > .5 else TOKENS['ink']}"


def excel_table_html(wide, jcols):
    head = "<tr><th class='d'>Nº</th><th class='n'>Jugador</th><th>TOTAL</th>" + "".join(f"<th>{c}</th>" for c in jcols) + "</tr>"
    body, col_tot = [], {c: 0.0 for c in jcols}
    col_has = {c: False for c in jcols}
    for r in wide.itertuples(index=False):
        cells, tot = [], 0.0
        for c in jcols:
            v = getattr(r, c)
            if v == "-":
                cells.append("<td class='no' title='No participó'>–</td>"); col_has[c] = True
            elif v == "":
                cells.append("<td></td>")
            else:
                n = float(v); tot += n; col_tot[c] += n; col_has[c] = True
                cells.append(f"<td style='{_cell_color(n)}'>{int(n)}</td>")
        body.append(f"<tr><td class='d'>{escape(str(r.dorsal))}</td><td class='n'>{escape(r.jugador)}</td><td class='tot'>{int(tot)}</td>{''.join(cells)}</tr>")
    grand = int(sum(col_tot.values()))
    foot = ("<tr><td class='d'></td><td class='n'>TOTAL</td><td class='tot'>" + str(grand) + "</td>"
            + "".join(f"<td>{int(col_tot[c]) if col_has[c] else ''}</td>" for c in jcols) + "</tr>")
    legend = ("<div class='xl-legend'><span><i style='background:rgba(245,135,31,.82)'></i>70'</span>"
              "<span><i style='background:rgba(245,135,31,.42)'></i>35'</span><span><i style='background:var(--surface-2)'></i>– no participó</span>"
              "<span>vacío = jornada sin dato · desliza en horizontal para ver todas las jornadas</span></div>")
    return legend + f"<div class='xl-wrap'><table class='xl'><thead>{head}</thead><tbody>{''.join(body)}</tbody><tfoot>{foot}</tfoot></table></div>"


def _fig(h, **kw):
    f = go.Figure(); f.update_layout(**plotly_layout(height=h, **kw)); return f


def _plot(fig, key):
    st.plotly_chart(fig, width="stretch", theme=None, config=PLOTLY_CONFIG, key=key)


def render_minutes():
    st.markdown(CSS, unsafe_allow_html=True)
    jug, wide, part, form, long, jcols = data()
    pj = played_jornadas(long)
    st.markdown("<div class='q-title' style='font-size:1.25rem'>Minutos · Infantil D</div>"
                f"<div class='q-sub'>Hoja «Minutos» del Excel. Partidos de {MATCH_MINUTES}'. Jornadas con datos: {', '.join(f'J{j}' for j in pj) or '—'}.</div>",
                unsafe_allow_html=True)
    summ = player_summary(long, pj, form)
    st.markdown("<div class='inf-kpis'>" + _kpi("Minutos repartidos", int(summ.minutos.sum()), f"{len(pj)} jornadas × 11 × {MATCH_MINUTES}'")
                + _kpi("Máximo de minutos", int(summ.minutos.max()), " · ".join(summ[summ.minutos == summ.minutos.max()].jugador))
                + _kpi("Media por jugador", f"{summ.minutos.mean():.0f}", f"{len(summ)} jugadores")
                + _kpi("Sin minutos", int((summ.minutos == 0).sum()), " · ".join(summ[summ.minutos == 0].jugador) or "—") + "</div>", unsafe_allow_html=True)

    tabs = st.tabs(["Tabla del Excel", "Tabla interactiva", "Gráficos", "Comparador"])
    with tabs[0]:
        st.markdown(excel_table_html(wide, jcols), unsafe_allow_html=True)
    with tabs[1]:
        sel = st.multiselect("Jornadas", [f"J{j}" for j in pj], default=[f"J{j}" for j in pj], key="infd_jsel")
        js = [int(x[1:]) for x in sel] or pj
        s = player_summary(long, js, form).merge(jug[["dorsal", "demarcacion"]], on="dorsal", how="left")
        show = s[["dorsal", "jugador", "demarcacion", "minutos", "pj", "titular", "participacion"]]
        st.dataframe(show, hide_index=True, width="stretch", height=min(40 + 35 * len(show), 720),
                     column_config={
                         "dorsal": st.column_config.NumberColumn("Nº", width="small"),
                         "jugador": st.column_config.TextColumn("Jugador"),
                         "demarcacion": st.column_config.TextColumn("Demarcación"),
                         "minutos": st.column_config.ProgressColumn("Minutos", format="%d'", min_value=0, max_value=MATCH_MINUTES * len(js)),
                         "pj": st.column_config.NumberColumn("PJ", help="Jornadas con minutos > 0"),
                         "titular": st.column_config.NumberColumn("Titular", help="Según la formación inicial de las hojas de jornada (solo J1 y J2 tienen jugadores colocados)"),
                         "participacion": st.column_config.ProgressColumn("% participación", format="%.0f%%", min_value=0, max_value=100,
                                                                          help=f"Minutos ÷ ({MATCH_MINUTES}' × jornadas con dato)"),
                     })
        st.caption("Pulsa en el encabezado de una columna para ordenar. Titularidades: solo J1 y J2 tienen la formación inicial en el Excel.")
    with tabs[2]:
        c1, c2 = st.columns(2, gap="medium")
        with c1.container(border=True):
            st.markdown("<div class='q-title'>¿Quién acumula más minutos?</div><div class='q-sub'>Total de las jornadas con datos.</div>", unsafe_allow_html=True)
            r = summ.iloc[::-1]
            f = _fig(40 + 26 * len(r), margin=dict(l=12, r=40, t=10, b=12), showlegend=False, barcornerradius=4, bargap=.25)
            f.add_bar(y=r.jugador, x=r.minutos, orientation="h", marker_color=PT, text=[f"{int(v)}'" for v in r.minutos],
                      textposition="outside", cliponaxis=False, textfont=dict(color=TOKENS["text"]),
                      hovertemplate="%{y}: %{x}' en " + str(len(pj)) + " jornadas<extra></extra>")
            f.update_xaxes(showgrid=False, showticklabels=False); f.update_yaxes(showgrid=False)
            _plot(f, "infd_rank")
        with c2.container(border=True):
            st.markdown("<div class='q-title'>¿Qué porcentaje de los minutos posibles juega cada uno?</div>"
                        f"<div class='q-sub'>Minutos ÷ ({MATCH_MINUTES}' × jornadas con dato). La línea marca el 50 %.</div>", unsafe_allow_html=True)
            r = summ.sort_values("participacion").reset_index(drop=True)
            f = _fig(40 + 26 * len(r), margin=dict(l=12, r=40, t=10, b=12), showlegend=False, barcornerradius=4, bargap=.25)
            f.add_bar(y=r.jugador, x=r.participacion, orientation="h", marker_color=RIVAL, text=[f"{v:.0f}%" for v in r.participacion],
                      textposition="outside", cliponaxis=False, textfont=dict(color=TOKENS["text"]),
                      customdata=r.minutos, hovertemplate="%{y}: %{x:.0f}% (%{customdata}')<extra></extra>")
            f.add_vline(x=50, line=dict(color=TOKENS["ink"], dash="dot", width=1))
            f.update_xaxes(range=[0, 112], showgrid=False, showticklabels=False); f.update_yaxes(showgrid=False)
            _plot(f, "infd_pct")
        with st.container(border=True):
            st.markdown("<div class='q-title'>¿Cómo se reparten los minutos jornada a jornada?</div>"
                        "<div class='q-sub'>Cada casilla son los minutos de ese jugador en esa jornada. Gris = no participó (–). Vacío = sin dato.</div>",
                        unsafe_allow_html=True)
            order = summ.jugador.tolist()[::-1]
            piv = long[long.jornada.isin(pj)].pivot_table(index="jugador", columns="jornada", values="minutos", aggfunc="first").reindex(order)
            z = piv.values
            text = [[("–" if v == 0 else f"{int(v)}") if pd.notna(v) else "" for v in row] for row in z]
            f = _fig(60 + 26 * len(order), margin=dict(l=12, r=12, t=10, b=12))
            f.add_heatmap(z=z, x=[f"J{j}" for j in piv.columns], y=order, text=text, texttemplate="%{text}", zmin=0, zmax=MATCH_MINUTES,
                          colorscale=[[0, TOKENS["surface-2"]], [0.001, "#4A2A0C"], [1, PT]], showscale=False, xgap=3, ygap=3,
                          textfont=dict(color=TOKENS["ink"], size=12), hovertemplate="%{y} · %{x}: %{text}'<extra></extra>")
            f.update_xaxes(side="top", showgrid=False); f.update_yaxes(showgrid=False)
            _plot(f, "infd_heat")
    with tabs[3]:
        names = summ.sort_values("dorsal").jugador.tolist()
        a, b = st.columns(2)
        p1 = a.selectbox("Jugador A", names, index=0, key="infd_p1")
        p2 = b.selectbox("Jugador B", names, index=min(1, len(names) - 1), key="infd_p2")
        sa, sb = summ.set_index("jugador").loc[p1], summ.set_index("jugador").loc[p2]
        st.markdown("<div class='inf-kpis'>" + _kpi(p1, f"{int(sa.minutos)}'", f"{int(sa.pj)} PJ · {sa.participacion:.0f}% · {int(sa.titular)} tit.")
                    + _kpi(p2, f"{int(sb.minutos)}'", f"{int(sb.pj)} PJ · {sb.participacion:.0f}% · {int(sb.titular)} tit.")
                    + _kpi("Diferencia", f"{int(sa.minutos - sb.minutos):+d}'", f"{p1} frente a {p2}")
                    + _kpi("Jornadas comparadas", len(pj), ", ".join(f"J{j}" for j in pj)) + "</div>", unsafe_allow_html=True)
        with st.container(border=True):
            f = _fig(320, margin=dict(l=12, r=12, t=40, b=12), barmode="group", barcornerradius=4, bargap=.3)
            for name, color in ((p1, PT), (p2, RIVAL)):
                d = long[(long.jugador == name) & long.jornada.isin(pj)].sort_values("jornada")
                f.add_bar(x=[f"J{j}" for j in d.jornada], y=d.minutos, name=name, marker_color=color, cliponaxis=False,
                          text=[("no jugó" if r.no_jugo else f"{int(r.minutos)}'") for r in d.itertuples()], textposition="outside",
                          textfont=dict(color=TOKENS["text"]), hovertemplate=name + " · %{x}: %{y}'<extra></extra>")
            f.update_yaxes(range=[0, MATCH_MINUTES * 1.2], ticksuffix="'", title=dict(text="Minutos", font=dict(size=11, color=MUTED)))
            f.update_xaxes(showgrid=False)
            _plot(f, "infd_cmp")


# ---------------------------------------------------------------- calendario: edición (solo almacenes que lo activan)
def render_calendar_editor(cal_path):
    try:
        cal = pd.read_csv(cal_path, dtype=str).fillna("")
    except Exception:
        return
    if cal.empty:
        return
    with st.expander("✏️ Editar o eliminar un evento", expanded=False):
        labels = [f"{r.fecha} · {r.hora_inicio} · {r.titulo}" for r in cal.itertuples()]
        i = st.selectbox("Evento", range(len(cal)), format_func=lambda k: labels[k], key="infd_cal_edit_sel")
        r = cal.iloc[i]
        with st.form(f"infd_cal_edit_{r['id']}"):
            a, b = st.columns(2)
            with a:
                fecha = st.date_input("Fecha", value=pd.to_datetime(r.fecha, errors="coerce") if r.fecha else None)
                hini = st.text_input("Hora inicio", value=r.hora_inicio)
                tipos = ["Entrenamiento", "Partido", "Reunión", "Fisio", "Descanso", "Vídeo", "Otro"]
                tipo = st.selectbox("Tipo", tipos, index=tipos.index(r.tipo) if r.tipo in tipos else len(tipos) - 1)
            with b:
                hfin = st.text_input("Hora fin", value=r.hora_fin)
                lugar = st.text_input("Lugar", value=r.lugar)
                estado = st.selectbox("Estado", ["Activo", "Aplazado", "Cancelado"], index=["Activo", "Aplazado", "Cancelado"].index(r.estado) if r.estado in ("Activo", "Aplazado", "Cancelado") else 0)
            titulo = st.text_input("Título", value=r.titulo)
            desc = st.text_area("Descripción", value=r.descripcion, height=80)
            c1, c2 = st.columns(2)
            save = c1.form_submit_button("Guardar cambios", use_container_width=True)
            delete = c2.form_submit_button("Eliminar evento", use_container_width=True)
        if save:
            cal.loc[cal.index[i], ["fecha", "hora_inicio", "hora_fin", "tipo", "titulo", "lugar", "descripcion", "estado"]] = [
                str(fecha) if fecha else r.fecha, hini, hfin, tipo, titulo.strip(), lugar, desc, estado]
            cal.to_csv(cal_path, index=False); st.success("Evento actualizado."); st.rerun()
        if delete:
            cal.drop(index=cal.index[i]).to_csv(cal_path, index=False); st.success("Evento eliminado."); st.rerun()


def tracking_notes():
    """Avisos del Excel para el apartado Seguimiento."""
    _, _, part, form, _, _ = data()
    out = [f"J{int(r.jornada)}: {r.notas}" for r in part.itertuples() if r.notas]
    out += [f"J{int(r.jornada)} {r.momento}: «{r.texto_excel}» en la casilla {r.celda} ({r.puesto}) — {r.estado}; puesto vacío hasta confirmarlo"
            for r in form[form.estado != "ok"].itertuples()]
    return out


def tracking_matches():
    _, _, part, _, _, _ = data()
    return pd.DataFrame({"jornada": part.jornada, "condicion": part.fecha, "rival": part.partido_excel.replace("", "Partido sin datos en la hoja"),
                         "gf": float("nan"), "gc": float("nan")})


def roster_names():
    jug = data()[0]
    return jug.jugador.astype(str).tolist()


# ---------------------------------------------------------------- resultados, goles y asistencias
RES_CSS = """<style>
.res-card{display:grid;grid-template-columns:52px 1fr auto auto;gap:14px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:12px 16px;margin-bottom:8px}
.res-card .j{background:var(--surface-3);color:var(--ink);font-weight:800;border-radius:10px;text-align:center;padding:8px 0}
.res-card .r{color:var(--ink);font-weight:800;font-size:.95rem} .res-card .r small{display:block;color:var(--muted);font-weight:500;font-size:.72rem;margin-top:2px}
.res-card .s{font-size:1.6rem;font-weight:900;color:var(--ink);letter-spacing:-.02em;min-width:70px;text-align:center}
.res-card .s.pend{font-size:.8rem;font-weight:700;color:var(--muted)}
.res-pill2{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-weight:900;font-size:.8rem;color:#0A0E14}
.rk{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:6px 16px}
.rk-row{display:grid;grid-template-columns:28px 1fr 2fr 40px;gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--line-soft)}
.rk-row:last-child{border-bottom:0}
.rk-row .p{color:var(--muted);font-weight:800;font-size:.8rem}.rk-row .n{color:var(--ink);font-weight:700;font-size:.88rem}
.rk-row .b{height:10px;background:var(--surface-2);border-radius:5px;overflow:hidden}.rk-row .b i{display:block;height:100%;border-radius:5px}
.rk-row .v{text-align:right;font-weight:900;font-size:1.05rem;color:var(--ink)}
.min-status{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--warn);border-radius:14px;padding:12px 16px;font-size:.84rem;color:var(--text);margin:4px 0 12px}
.min-status b{color:var(--ink)}
@media(max-width:700px){.res-card{grid-template-columns:44px 1fr auto}.res-card .res-pill2{display:none}}
</style>"""


@st.cache_data(show_spinner=False)
def _load_results(stamp):
    res = pd.read_csv(DIR / "resultados.csv").fillna({"rival": "", "notas": "", "fuente": ""})
    ev = pd.read_csv(DIR / "eventos.csv")
    ev["minuto"] = pd.to_numeric(ev["minuto"], errors="coerce")
    ev["jornada"] = pd.to_numeric(ev["jornada"], errors="coerce")
    return res, ev


def results_data():
    return _load_results(_stamp())


def balance(res):
    r = res.dropna(subset=["goles_favor", "goles_contra"])
    v = int((r.goles_favor > r.goles_contra).sum()); e = int((r.goles_favor == r.goles_contra).sum()); d = len(r) - v - e
    return dict(pj=len(r), v=v, e=e, d=d, gf=int(r.goles_favor.sum()), gc=int(r.goles_contra.sum()), pts=3 * v + e)


def _ranking_html(series, color):
    if series.empty:
        return "<div class='rk'><div class='rk-row'><span></span><span class='n'>Sin registros</span></div></div>"
    top = series.max()
    rows = [f"<div class='rk-row'><span class='p'>{i}</span><span class='n'>{escape(str(n))}</span>"
            f"<span class='b'><i style='width:{100 * v / top:.0f}%;background:{color}'></i></span><span class='v'>{int(v)}</span></div>"
            for i, (n, v) in enumerate(series.items(), 1)]
    return f"<div class='rk'>{''.join(rows)}</div>"


TRAMOS = [(0, 10), (10, 20), (20, 35), (35, 45), (45, 55), (55, 70)]


def _tramo(m):
    for a, b in TRAMOS:
        if a < m <= b or (m == 0 and a == 0):
            return f"{a}–{b}'"
    return "70'+"


def render_results():
    st.markdown(CSS + RES_CSS, unsafe_allow_html=True)
    res, ev = results_data()
    b = balance(res)
    st.markdown("<div class='q-title' style='font-size:1.25rem'>Resultados · Infantil D</div>"
                "<div class='q-sub'>Solo resultados y goles confirmados. Lo pendiente se indica sin inventar datos.</div>", unsafe_allow_html=True)
    st.markdown("<div class='inf-kpis'>" + _kpi("Partidos con resultado", b["pj"], f"de {len(res)} jornadas registradas")
                + _kpi("Balance", f"{b['v']}V · {b['e']}E · {b['d']}D", f"{b['pts']} puntos")
                + _kpi("Goles", f"{b['gf']} – {b['gc']}", "a favor – en contra")
                + _kpi("Diferencia", f"{b['gf'] - b['gc']:+d}", "goles") + "</div>", unsafe_allow_html=True)
    cards = []
    for r in res.sort_values("jornada").itertuples():
        rival = r.rival or "Rival pendiente de identificar"
        if pd.notna(r.goles_favor) and pd.notna(r.goles_contra):
            gf, gc = int(r.goles_favor), int(r.goles_contra)
            res_l = "V" if gf > gc else ("E" if gf == gc else "D")
            col = {"V": TOKENS["pos"], "E": MUTED, "D": TOKENS["neg"]}[res_l]
            score, pill = f"<span class='s'>{gf} – {gc}</span>", f"<span class='res-pill2' style='background:{col}'>{res_l}</span>"
        else:
            score, pill = "<span class='s pend'>Resultado pendiente</span>", "<span></span>"
        sub = escape(r.notas or r.fuente)
        cards.append(f"<div class='res-card'><span class='j'>J{int(r.jornada)}</span><span class='r'>Infantil D – {escape(rival)}<small>{sub}</small></span>{score}{pill}</div>")
    st.markdown("".join(cards), unsafe_allow_html=True)

    goals, assists = ev[ev.tipo == "gol"], ev[ev.tipo == "asistencia"]
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown(f"<div class='q-title'>⚽ Goleadores · {len(goals)} goles</div><div class='q-sub'>Ranking acumulado de la temporada.</div>", unsafe_allow_html=True)
        st.markdown(_ranking_html(goals.jugador.value_counts(), PT), unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='q-title'>🅰️ Asistencias · {len(assists)}</div><div class='q-sub'>Ranking acumulado de la temporada.</div>", unsafe_allow_html=True)
        st.markdown(_ranking_html(assists.jugador.value_counts(), RIVAL), unsafe_allow_html=True)

    st.markdown("<div class='q-title' style='margin-top:16px'>Goles y asistencias por minuto</div>"
                "<div class='q-sub'>Tramos de un partido de 70' (dos partes de 35').</div>", unsafe_allow_html=True)
    known_g, known_a, known_j = int(goals.minuto.notna().sum()), int(assists.minuto.notna().sum()), int(goals.jornada.notna().sum())
    pending = ("Ni las hojas del Excel ni los datos confirmados indican el minuto ni la jornada de cada gol: se mostrarán aquí cuando se registren."
               if known_g < len(goals) else "")
    st.markdown(f"<div class='min-status'><b>Minuto registrado:</b> {known_g} de {len(goals)} goles · {known_a} de {len(assists)} asistencias. "
                f"<b>Jornada registrada:</b> {known_j} de {len(goals)} goles. {pending}</div>", unsafe_allow_html=True)
    if known_g:
        order = [f"{a}–{b}'" for a, b in TRAMOS] + ["70'+"]
        cnt = goals.dropna(subset=["minuto"]).minuto.map(_tramo).value_counts().reindex(order, fill_value=0)
        f = go.Figure(); f.update_layout(**plotly_layout(height=260, margin=dict(l=12, r=12, t=20, b=12), showlegend=False, barcornerradius=4))
        f.add_bar(x=cnt.index, y=cnt.values, marker_color=PT, text=cnt.values, textposition="outside", cliponaxis=False)
        f.update_yaxes(showgrid=False, showticklabels=False); f.update_xaxes(showgrid=False)
        _plot(f, "infd_goal_tramos")
    with st.container(border=True):
        st.markdown("<div class='q-title'>Goles por jornada</div><div class='q-sub'>Marcadores confirmados: a favor (naranja) y en contra (azul).</div>", unsafe_allow_html=True)
        r = res.dropna(subset=["goles_favor"]).sort_values("jornada")
        f = go.Figure(); f.update_layout(**plotly_layout(height=240, margin=dict(l=12, r=12, t=30, b=12), barmode="group", barcornerradius=4, bargap=.35))
        lab = [f"J{int(j)} · {rv or 'rival pendiente'}" for j, rv in zip(r.jornada, r.rival)]
        f.add_bar(x=lab, y=r.goles_favor, name="A favor", marker_color=PT, text=r.goles_favor.astype(int), textposition="outside", cliponaxis=False)
        f.add_bar(x=lab, y=r.goles_contra, name="En contra", marker_color=RIVAL, text=r.goles_contra.astype(int), textposition="outside", cliponaxis=False)
        f.update_yaxes(showgrid=False, showticklabels=False, rangemode="tozero"); f.update_xaxes(showgrid=False)
        _plot(f, "infd_goals_j")
