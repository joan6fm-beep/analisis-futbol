"""Cadete A · Lliga Autonòmica Cadet (Grup Únic) 2026/27.

Datos: data/cadete_a/*.csv, generados por tools/importar_cadete_a.py desde las actas FFCV
transcritas en data/cadete_a/fuente/actas.txt. Todo se recalcula desde esos CSV.
Duración reglamentaria: 80 minutos (2 × 40). Ninguna métrica de este módulo usa 90'.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import league_core as lc
from teams import match_minutes
from ui_theme import MUTED, NEG, PLOTLY_CONFIG, POS, PT, RIVAL, TOKENS, plotly_layout

DIR = Path(__file__).parent / "data" / "cadete_a"
MM = match_minutes("cadete")          # 80
TEAM = "Primer Toque C.F. 'A'"
LEAGUE = "Lliga Autonòmica Cadet · Grup Únic"
AREA = "cadete"

CSS = """<style>
.cad-hero{display:grid;grid-template-columns:1.25fr 1fr;gap:18px;align-items:stretch;margin:4px 0 14px}
.cad-photo{border-radius:18px;overflow:hidden;border:1px solid var(--line);background:#0D131C;position:relative}
.cad-photo .bg{position:absolute;inset:-30px;width:calc(100% + 60px);height:calc(100% + 60px);object-fit:cover;filter:blur(22px);opacity:.4}
.cad-photo .ph{position:relative;width:100%;height:auto;display:block}
.cad-card{background:linear-gradient(180deg,#141C2A,#101620);border:1px solid var(--line);box-shadow:inset 0 2px 0 var(--pt);border-radius:18px;padding:20px 22px;display:flex;flex-direction:column;justify-content:center;gap:4px}
.cad-card .k{font-size:.7rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--pt)}
.cad-card h2{margin:4px 0!important;font-size:2rem!important;font-weight:900!important;color:var(--ink)!important;letter-spacing:-.03em}
.cad-card p{color:var(--muted);font-size:.86rem;margin:0}
.cad-links{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.cad-links a{background:var(--surface-2);border:1px solid var(--line);color:var(--ink)!important;text-decoration:none!important;font-weight:700;font-size:.8rem;padding:8px 12px;border-radius:10px}
.cad-links a.main{background:var(--pt);color:#1A0E02!important;border-color:var(--pt)}
.cad-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0 0 14px}
.cad-kpis.k6{grid-template-columns:repeat(6,minmax(0,1fr))}
.cad-kpi{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
.cad-kpi small{display:block;font-size:.66rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.cad-kpi b{display:block;font-size:1.55rem;font-weight:900;color:var(--ink);letter-spacing:-.02em;margin-top:2px}
.cad-kpi span{font-size:.72rem;color:var(--muted)}
.cad-kpi.pt{box-shadow:inset 0 2px 0 var(--pt)}
.q-title{font-size:1rem;font-weight:800;color:var(--ink);margin:14px 0 2px;letter-spacing:-.01em}
.q-sub{font-size:.76rem;color:var(--muted);margin-bottom:8px}
.cad-match{display:grid;grid-template-columns:44px 1fr auto auto;gap:12px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:9px 13px;margin-bottom:6px}
.cad-match .j{background:var(--surface-3);color:var(--ink);font-weight:800;border-radius:8px;text-align:center;padding:5px 0;font-size:.8rem}
.cad-match .t{color:var(--ink);font-weight:700;font-size:.86rem}.cad-match .t small{display:block;color:var(--muted);font-weight:500;font-size:.7rem}
.cad-match .sc{font-weight:900;font-size:1.05rem;color:var(--ink);font-variant-numeric:tabular-nums}
.res{font-size:.68rem;font-weight:900;border-radius:7px;padding:4px 8px;min-width:22px;text-align:center}
.res.V{background:rgba(43,196,138,.16);color:var(--pos)}.res.E{background:rgba(242,193,78,.16);color:var(--warn)}.res.D{background:rgba(240,89,106,.16);color:var(--neg)}
.cad-table{width:100%;border-collapse:separate;border-spacing:0;font-size:.82rem;background:var(--surface);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.cad-table th{background:var(--surface-2);color:var(--muted);font-size:.66rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;padding:8px 8px;text-align:center}
.cad-table th.l,.cad-table td.l{text-align:left}
.cad-table td{padding:7px 8px;text-align:center;border-top:1px solid var(--line-soft);color:var(--text);font-variant-numeric:tabular-nums}
.cad-table tr.me td{background:var(--pt-soft);color:var(--ink);font-weight:800}
.cad-table td.pts{font-weight:900;color:var(--ink)}
.cad-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
.cad-note{font-size:.74rem;color:var(--muted);margin:6px 0 10px}
.cad-badge{display:inline-block;font-size:.64rem;font-weight:800;border-radius:999px;padding:2px 8px;margin-left:6px;vertical-align:middle}
.cad-badge.est{background:rgba(111,147,198,.18);color:#AFC6E8}.cad-badge.ok{background:rgba(43,196,138,.14);color:var(--pos)}
.cad-badge.pend{background:var(--surface-2);color:var(--muted)}
.rank-row{display:grid;grid-template-columns:24px 1fr 56px;gap:8px;align-items:center;margin:5px 0}
.rank-row .n{color:var(--muted);font-weight:800;font-size:.78rem;text-align:right}
.rank-row .nm{color:#FFFFFF;font-weight:700;font-size:.84rem}.rank-row .nm small{color:var(--muted);font-weight:500;margin-left:6px}
.rank-row .bar{height:6px;background:var(--surface-2);border-radius:4px;margin-top:4px;overflow:hidden}
.rank-row .bar span{display:block;height:100%;border-radius:4px}
.rank-row .v{color:var(--ink);font-weight:900;text-align:right;font-variant-numeric:tabular-nums}
.lineup{display:grid;gap:6px;margin:6px 0}
.lineup .line{display:flex;gap:6px;flex-wrap:wrap}
.lineup .pl{background:var(--surface-2);border:1px solid var(--line);border-radius:9px;padding:5px 9px;font-size:.78rem;color:var(--ink)}
.lineup .pl b{color:var(--pt);margin-right:5px}.lineup .pl small{color:var(--muted);margin-left:5px}
.lineup .lbl{font-size:.64rem;font-weight:800;letter-spacing:.08em;color:var(--muted);text-transform:uppercase;min-width:42px;align-self:center}
@media(max-width:760px){.cad-hero{grid-template-columns:1fr}.cad-kpis,.cad-kpis.k6{grid-template-columns:repeat(2,minmax(0,1fr))}.cad-card h2{font-size:1.5rem!important}
.cad-match{grid-template-columns:40px 1fr auto}.cad-match .res{display:none}}
</style>"""


# ------------------------------------------------------------------ datos

def _stamp():
    out = []
    for f in ("partidos", "alineaciones", "eventos", "minutos", "avisos"):
        p = DIR / f"{f}.csv"
        out.append(p.stat().st_mtime_ns if p.exists() else 0)
    return tuple(out)


@st.cache_data(show_spinner=False)
def _load(stamp):
    def rd(n):
        p = DIR / f"{n}.csv"
        return pd.read_csv(p) if p.exists() else pd.DataFrame()
    part, al, ev, mins, av = (rd(n) for n in ("partidos", "alineaciones", "eventos", "minutos", "avisos"))
    if not ev.empty:
        ev["minuto"] = pd.to_numeric(ev["minuto"], errors="coerce")
        ev["detalle"] = ev["detalle"].fillna("")
    return part, al, ev, mins, av


def data():
    return _load(_stamp())


def teams_list(part):
    return sorted(set(part["local"]) | set(part["visitante"]))


def short(name: str) -> str:
    return str(name).replace(" 'A'", "").replace("C.F. ", "").replace("U.D. ", "").replace("C.D. ", "").replace("S.C.D. ", "") or str(name)


def jornada_status(part, j):
    """(jugados, esperados) en la jornada j. Con 18 equipos se juegan 9 partidos por jornada."""
    n_teams = len(teams_list(part))
    return int((part["jornada"] == j).sum()), n_teams // 2


def last_complete(part):
    js = sorted(part["jornada"].unique())
    done = [j for j in js if jornada_status(part, j)[0] >= jornada_status(part, j)[1]]
    return max(done) if done else (max(js) if js else 0)


def _kpi(label, value, sub="", cls=""):
    return f"<div class='cad-kpi {cls}'><small>{escape(str(label))}</small><b>{escape(str(value))}</b><span>{escape(str(sub))}</span></div>"


def _plot(fig, key, h=320, **kw):
    fig.update_layout(**plotly_layout(height=h, **kw))
    st.plotly_chart(fig, width="stretch", theme=None, config=PLOTLY_CONFIG, key=key)


def _fmt(v, d=2):
    return "—" if v is None or pd.isna(v) else f"{v:.{d}f}".replace(".", ",")


def _match_row(r, team=None, link=True):
    """Fila visual de un partido. Si `team`, se muestra desde su perspectiva."""
    sc = f"{int(r.goles_local)}–{int(r.goles_visitante)}"
    res = ""
    if team:
        tm = r.local == team
        gf, gc = (r.goles_local, r.goles_visitante) if tm else (r.goles_visitante, r.goles_local)
        letter = "V" if gf > gc else ("E" if gf == gc else "D")
        res = f"<span class='res {letter}'>{letter}</span>"
    fecha = r.fecha if isinstance(r.fecha, str) and r.fecha else "fecha no visible"
    return (f"<div class='cad-match'><span class='j'>J{int(r.jornada)}</span><span class='t'>{escape(r.local)} — {escape(r.visitante)}"
            f"<small>{escape(fecha)} · {escape(str(r.campo) if isinstance(r.campo, str) else '')}</small></span>"
            f"<span class='sc'>{sc}</span>{res}</div>")


def _ranking(rows, color, value_fmt=lambda v: str(v), max_v=None):
    if not rows:
        return "<div class='cad-note'>Sin datos.</div>"
    mx = max_v or max(v for _, v, _ in rows) or 1
    out = []
    for i, (name, v, sub) in enumerate(rows, 1):
        out.append(f"<div class='rank-row'><span class='n'>{i}</span><div><div class='nm'>{escape(name)}<small>{escape(sub)}</small></div>"
                   f"<div class='bar'><span style='width:{min(100, v / mx * 100):.1f}%;background:{color}'></span></div></div>"
                   f"<span class='v'>{value_fmt(v)}</span></div>")
    return "".join(out)


def _standings_html(tab, highlight=TEAM):
    head = ("<tr><th>Pos</th><th class='l'>Equipo</th><th>PJ</th><th>V</th><th>E</th><th>D</th><th>GF</th><th>GC</th>"
            "<th>DG</th><th>Pts</th></tr>")
    body = []
    for r in tab.itertuples():
        cls = " class='me'" if r.equipo == highlight else ""
        dg = f"+{r.dg}" if r.dg > 0 else str(r.dg)
        body.append(f"<tr{cls}><td>{r.pos}</td><td class='l'>{escape(r.equipo)}</td><td>{r.pj}</td><td>{r.pg}</td><td>{r.pe}</td>"
                    f"<td>{r.pp}</td><td>{r.gf}</td><td>{r.gc}</td><td>{dg}</td><td class='pts'>{r.pts}</td></tr>")
    return f"<div class='cad-wrap'><table class='cad-table'>{head}{''.join(body)}</table></div>"


def _team_selector(label, key, default=None, exclude=None):
    part, *_ = data()
    tl = [t for t in teams_list(part) if t != exclude]
    q = str(st.query_params.get("team", "")) if key == "cad_rival" else ""
    d = q if q in tl else (default if default in tl else tl[0])
    return st.selectbox(label, tl, index=tl.index(d), key=key)


# ------------------------------------------------------------------ inicio

def _next_match():
    cal = DIR / "calendario.csv"
    if not cal.exists():
        return None
    try:
        c = pd.read_csv(cal)
        c["f"] = pd.to_datetime(c["fecha"], errors="coerce", dayfirst=False)
        c = c[(c["tipo"].astype(str).str.lower() == "partido") & (c["f"] >= pd.Timestamp.today().normalize())].sort_values("f")
        return c.iloc[0] if not c.empty else None
    except Exception:
        return None


def render_home(photo_uri):
    st.markdown(CSS, unsafe_allow_html=True)
    part, al, ev, mins, av = data()
    if part.empty:
        st.info("Aún no hay actas importadas del Cadete A.")
        return
    jc = last_complete(part)
    tm = lc.team_matches(part, TEAM)
    tab = lc.standings(part[part.jornada <= jc], teams_list(part))
    me = tab[tab.equipo == TEAM].iloc[0]
    photo = (f"<div class='cad-photo'><img class='bg' src='{photo_uri}' alt=''><img class='ph' src='{photo_uri}' alt='Cadete A'></div>"
             if photo_uri else "<div class='cad-photo'></div>")
    last = tm.iloc[-1]
    nxt = _next_match()
    nxt_txt = (f"{nxt['fecha']} · {nxt.get('titulo', '')}" if nxt is not None else "Pendiente: añádelo en Calendario")
    st.markdown(
        f"<div class='cad-hero'>{photo}<div class='cad-card'><span class='k'>Primer Toque C.F. · {LEAGUE} · 2026/27</span>"
        "<h2>Cadete A</h2><p>Partidos de 80 minutos (2 × 40). Datos de las actas oficiales de la FFCV.</p>"
        f"<p style='margin-top:8px;color:var(--text)'><b>Último resultado:</b> J{last.jornada} · {escape(short(TEAM) if last.condicion == 'Casa' else short(last.rival))} "
        f"{(last.gf if last.condicion == 'Casa' else last.gc)}–{(last.gc if last.condicion == 'Casa' else last.gf)} "
        f"{escape(short(last.rival) if last.condicion == 'Casa' else short(TEAM))}</p>"
        f"<p style='color:var(--text)'><b>Próximo partido:</b> {escape(nxt_txt)}</p>"
        "<div class='cad-links'><a class='main' href='?area=cadete&view=liga' target='_self'>Resumen de liga →</a>"
        "<a href='?area=cadete&view=rivales' target='_self'>Rivales</a>"
        "<a href='?area=cadete&view=estadisticas' target='_self'>Estadísticas</a>"
        "<a href='?area=cadete&view=calendario' target='_self'>Calendario</a></div></div></div>", unsafe_allow_html=True)
    st.markdown("<div class='cad-kpis k6'>"
                + _kpi("Posición", f"{me.pos}º", f"de {len(tab)} equipos", "pt")
                + _kpi("Puntos", me.pts, f"{me.pj} partidos jugados", "pt")
                + _kpi("Balance", f"{me.pg}-{me.pe}-{me.pp}", "victorias · empates · derrotas")
                + _kpi("Goles a favor", me.gf, f"{me.gf / me.pj:.2f} por partido".replace(".", ","))
                + _kpi("Goles en contra", me.gc, f"{me.gc / me.pj:.2f} por partido".replace(".", ","))
                + _kpi("Diferencia", f"{me.dg:+d}", f"clasificación tras J{jc} (última completa)") + "</div>", unsafe_allow_html=True)
    st.markdown("<div class='q-title'>Resultados del Cadete A</div><div class='q-sub'>Verde: victoria · amarillo: empate · rojo: derrota.</div>",
                unsafe_allow_html=True)
    rows = part[(part.local == TEAM) | (part.visitante == TEAM)].sort_values("jornada")
    st.markdown("".join(_match_row(r, TEAM) for r in rows.itertuples()), unsafe_allow_html=True)
    _provisional_note(part)


def _provisional_note(part):
    msgs = []
    for j in sorted(part["jornada"].unique()):
        got, exp = jornada_status(part, j)
        if got < exp:
            msgs.append(f"J{j}: {got} de {exp} partidos con acta")
    if msgs:
        st.markdown(f"<div class='cad-note'>⚠️ Clasificación provisional · {escape('; '.join(msgs))}. "
                    "Orden calculado por puntos, diferencia de goles y goles a favor (los desempates oficiales "
                    "por enfrentamiento directo pueden diferir).</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------ resumen de liga

def render_league():
    st.markdown(CSS, unsafe_allow_html=True)
    part, al, ev, mins, av = data()
    teams = teams_list(part)
    st.markdown(f"<div class='league-hero'><div><div class='league-eyebrow'>TEMPORADA 2026/2027 · PARTIDOS DE {MM}'</div>"
                "<div class='league-title'>🏆 Resumen de liga · Cadete A</div>"
                "<div class='league-subtitle'>Clasificación, resultados, evolución, casa/fuera, goleadores, porteros y goles por tramos de 10'.</div>"
                f"</div><div class='league-badge'>{LEAGUE}</div></div>", unsafe_allow_html=True)
    js = sorted(int(j) for j in part["jornada"].unique())
    opt = st.selectbox("Clasificación acumulada hasta", [f"J{j}" for j in js], index=js.index(last_complete(part)), key="cad_lg_j",
                       help="Por defecto, la última jornada con todos sus partidos documentados.")
    jmax = int(opt[1:])
    pp = part[part.jornada <= jmax]
    evj = ev[ev.jornada <= jmax]
    tab = lc.standings(pp, teams)
    got, exp = jornada_status(part, jmax)
    if got < exp:
        st.warning(f"Clasificación provisional en J{jmax}: {got} de {exp} partidos con acta en los documentos.")
    n = len(pp)
    goals = int(pp.goles_local.sum() + pp.goles_visitante.sum())
    yel = int(evj.tipo.isin(["amarilla", "segunda_amarilla"]).sum())
    red = int(evj.tipo.isin(["roja", "segunda_amarilla"]).sum())
    pens = int((evj.tipo == "penalti_gol").sum())
    st.markdown("<div class='cad-kpis k6'>"
                + _kpi("Líder", short(tab.iloc[0].equipo), f"{tab.iloc[0].pts} puntos", "pt")
                + _kpi("Partidos", n, f"hasta J{jmax}")
                + _kpi("Goles", goals, f"{goals / n:.2f} por partido".replace(".", ","))
                + _kpi("Amarillas", yel, f"{yel / n:.2f} por partido".replace(".", ","))
                + _kpi("Expulsiones", red, "rojas directas y segundas amarillas")
                + _kpi("Penaltis marcados", pens, "según el icono del acta") + "</div>", unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs(["Clasificación", "Resultados", "Evolución", "Goleadores", "Porteros y tramos"])
    with t1:
        st.markdown(_standings_html(tab), unsafe_allow_html=True)
        _provisional_note(pp)
        st.markdown("<div class='q-title'>Rendimiento en casa y fuera</div><div class='q-sub'>Puntos por partido de cada equipo según dónde juega.</div>",
                    unsafe_allow_html=True)
        d = tab.copy()
        d["ppp_casa"] = d.pts_casa / d.pj_casa.replace(0, pd.NA)
        d["ppp_fuera"] = d.pts_fuera / d.pj_fuera.replace(0, pd.NA)
        d = d.sort_values("pos", ascending=False)
        fig = go.Figure()
        fig.add_bar(y=d.equipo.map(short), x=d.ppp_casa, name="Casa", orientation="h", marker_color=PT,
                    hovertemplate="%{y} · casa: %{x:.2f} pts/partido<extra></extra>")
        fig.add_bar(y=d.equipo.map(short), x=d.ppp_fuera, name="Fuera", orientation="h", marker_color=RIVAL,
                    hovertemplate="%{y} · fuera: %{x:.2f} pts/partido<extra></extra>")
        _plot(fig, "cad_lg_cf", h=80 + 26 * len(d), barmode="group", xaxis=dict(title="Puntos por partido", range=[0, 3.05]))
    with t2:
        sel = st.selectbox("Jornada", [f"J{j}" for j in js if j <= jmax][::-1], key="cad_lg_res")
        jj = int(sel[1:])
        rows = part[part.jornada == jj].sort_values(["fecha", "local"])
        st.markdown("".join(_match_row(r) for r in rows.itertuples()), unsafe_allow_html=True)
        got, exp = jornada_status(part, jj)
        if got < exp:
            st.markdown(f"<div class='cad-note'>Faltan {exp - got} partido(s) de esta jornada en los documentos.</div>", unsafe_allow_html=True)
        st.markdown("<div class='q-title'>Resultados del Cadete A</div>", unsafe_allow_html=True)
        tm = lc.team_matches(pp, TEAM)
        st.dataframe(tm.rename(columns={"jornada": "J", "rival": "Rival", "condicion": "Campo", "gf": "GF", "gc": "GC",
                                        "resultado": "Res.", "puntos": "Pts", "fecha": "Fecha"}), hide_index=True, width="stretch")
    with t3:
        evo = lc.position_evolution(pp, teams)
        cmp_team = st.selectbox("Comparar con", ["(ninguno)"] + [t for t in teams if t != TEAM], key="cad_lg_cmp")
        show = [TEAM] + ([cmp_team] if cmp_team != "(ninguno)" else [])
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            for t, col in zip(show, (PT, RIVAL)):
                e = evo[evo.equipo == t]
                fig.add_scatter(x=e.jornada, y=e.pos, mode="lines+markers", name=short(t), line=dict(color=col, width=2),
                                marker=dict(size=8), hovertemplate=f"{short(t)} · J%{{x}}: %{{y}}º<extra></extra>")
            _plot(fig, "cad_lg_pos", title="Posición tras cada jornada", yaxis=dict(autorange="reversed", dtick=1, title="Posición"),
                  xaxis=dict(dtick=1, title="Jornada"))
        with c2:
            fig = go.Figure()
            for t, col in zip(show, (PT, RIVAL)):
                e = evo[evo.equipo == t]
                fig.add_scatter(x=e.jornada, y=e.pts, mode="lines+markers", name=short(t), line=dict(color=col, width=2),
                                marker=dict(size=8), hovertemplate=f"{short(t)} · J%{{x}}: %{{y}} pts<extra></extra>")
            _plot(fig, "cad_lg_pts", title="Puntos acumulados", xaxis=dict(dtick=1, title="Jornada"))
        tm = lc.team_matches(pp, TEAM)
        c3, c4 = st.columns(2)
        with c3:
            fig = go.Figure()
            fig.add_bar(x=tm.jornada, y=tm.gf, name="Marcados", marker_color=PT, hovertemplate="J%{x}: %{y} marcados<extra></extra>")
            fig.add_bar(x=tm.jornada, y=tm.gc, name="Encajados", marker_color=RIVAL, hovertemplate="J%{x}: %{y} encajados<extra></extra>")
            _plot(fig, "cad_lg_g", title="Goles por jornada · Cadete A", barmode="group", xaxis=dict(dtick=1, title="Jornada"))
        with c4:
            dg = (tm.gf - tm.gc).cumsum()
            fig = go.Figure(go.Scatter(x=tm.jornada, y=dg, mode="lines+markers", line=dict(color=PT, width=2), marker=dict(size=8),
                                       hovertemplate="J%{x}: diferencia acumulada %{y:+d}<extra></extra>"))
            fig.add_hline(y=0, line_color=TOKENS["line"])
            _plot(fig, "cad_lg_dg", title="Diferencia de goles acumulada", xaxis=dict(dtick=1, title="Jornada"))
        last5 = tm.tail(5)
        st.markdown("<div class='q-title'>Rendimiento reciente</div><div class='q-sub'>Últimos 5 partidos del Cadete A.</div>"
                    + " ".join(f"<span class='res {r}'>{r}</span>" for r in last5.resultado)
                    + f"<div class='cad-note'>{int(last5.puntos.sum())} de {3 * len(last5)} puntos posibles · "
                      f"{int(last5.gf.sum())} goles marcados y {int(last5.gc.sum())} encajados.</div>", unsafe_allow_html=True)
    with t4:
        sc = lc.scorers(evj, mins)
        top = sc.head(15)
        st.markdown("<div class='q-title'>Máximos goleadores de la liga</div><div class='q-sub'>Sin goles en propia puerta. Entre paréntesis, penaltis.</div>"
                    + _ranking([(f"{r.jugador}", r.goles, f"{short(r.equipo)}" + (f" ({r.penaltis} pen.)" if r.penaltis else ""))
                                for r in top.itertuples()], PT), unsafe_allow_html=True)
        og = evj[evj.tipo == "gol_propia"]
        if not og.empty:
            st.markdown("<div class='q-title'>Goles en propia puerta</div>" + "".join(
                f"<div class='cad-note'>J{int(r.jornada)} · {int(r.minuto)}' · {escape(r.jugador)} ({escape(short(r.equipo))})</div>"
                for r in og.itertuples()), unsafe_allow_html=True)
        st.markdown("<div class='q-title'>Asistencias</div><div class='cad-note'>Las actas de la FFCV no registran asistencias: "
                    "no hay datos de asistencias para el Cadete A ni para los rivales.</div>", unsafe_allow_html=True)
        with st.expander("Tabla completa de goleadores"):
            st.dataframe(sc.rename(columns={"equipo": "Equipo", "jugador": "Jugador", "goles": "Goles", "penaltis": "Pen.",
                                            "minutos_gol": "Minutos de gol", "pct_equipo": "% goles del equipo",
                                            "partidos": "PJ", "goles_partido": "Goles/partido"}),
                         hide_index=True, width="stretch",
                         column_config={"% goles del equipo": st.column_config.NumberColumn(format="%.0f %%"),
                                        "Goles/partido": st.column_config.NumberColumn(format="%.2f")})
    with t5:
        _goalkeepers_league(al, mins, evj, pp, teams)
        _bins_chart(evj, None, key="cad_lg_bins", title="Goles de toda la liga por tramos de 10'")


def _goalkeepers_league(al, mins, ev, part, teams):
    rows, warns = [], []
    for t in teams:
        g, w = lc.goalkeepers(al, mins, ev, part, t, MM)
        if not g.empty:
            g.insert(0, "equipo", t)
            rows.append(g)
        warns += [f"{short(t)}: {x}" for x in w]
    if not rows:
        return
    gk = pd.concat(rows)
    gk = gk[gk.minutos >= MM * 2]
    gk = gk.sort_values("encajados_por_partido_reglamentario")
    st.markdown(f"<div class='q-title'>Ranking de porteros · goles encajados por {MM}'</div>"
                f"<div class='q-sub'>Fórmula: goles encajados con el portero en el campo ÷ minutos jugados × {MM}. "
                f"Solo porteros con al menos {MM * 2} minutos. Menos es mejor.</div>", unsafe_allow_html=True)
    st.markdown(_ranking([(r.jugador, r.encajados_por_partido_reglamentario,
                           f"{short(r.equipo)} · {int(r.minutos)}' · {int(r.encajados)} GC · {int(r.porterias_cero)} a cero")
                          for r in gk.head(15).itertuples()], RIVAL, value_fmt=lambda v: _fmt(v), max_v=max(gk.head(15).encajados_por_partido_reglamentario.max(), .1)),
                unsafe_allow_html=True)
    if warns:
        with st.expander(f"Goles no atribuibles a un portero ({len(warns)})"):
            st.markdown("\n".join(f"- {escape(w)}" for w in warns))


def _bins_chart(ev, team, key, title):
    labels = [b[2] for b in lc.minute_bins(MM)]
    if team:
        g = lc.goals_by_bin(ev, team, MM)
        fig = go.Figure()
        fig.add_bar(x=labels, y=g.a_favor, name="Marcados", marker_color=PT,
                    customdata=g.a_favor_añadido, hovertemplate="%{x}': %{y} marcados (%{customdata} en el añadido)<extra></extra>")
        fig.add_bar(x=labels, y=g.en_contra, name="Encajados", marker_color=RIVAL,
                    customdata=g.en_contra_añadido, hovertemplate="%{x}': %{y} encajados (%{customdata} en el añadido)<extra></extra>")
    else:
        gl = ev[ev.tipo.isin(["gol", "penalti_gol", "gol_propia"])]
        cnt = {lab: 0 for lab in labels}
        for m in gl.minuto:
            lab = lc.bin_label(m, MM)
            if lab:
                cnt[lab.rstrip("+")] += 1
        fig = go.Figure(go.Bar(x=labels, y=list(cnt.values()), marker_color=PT, hovertemplate="%{x}': %{y} goles<extra></extra>"))
    fig.add_vline(x=3.5, line_dash="dot", line_color=MUTED)
    _plot(fig, key, title=title, barmode="group", margin=dict(l=12, r=12, t=48, b=48),
          legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"))
    st.markdown(f"<div class='cad-note'>Tramos de 10 minutos sobre {MM}' (la línea punteada marca el descanso, tras el 40'). Los goles en el tiempo añadido se cuentan en el último tramo de "
                "su parte y conservan su minuto real en el acta.</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------ rivales

def _team_profile(part, team):
    tm = lc.team_matches(part, team)
    tab = lc.standings(part, teams_list(part))
    me = tab[tab.equipo == team].iloc[0]
    return tm, me, tab


def _lineup_html(al_m, mins_m, ev_m):
    lines = []
    m_by = dict(zip(mins_m.jugador, mins_m.minutos))
    goals = ev_m[ev_m.tipo.isin(["gol", "penalti_gol"])].groupby("jugador").size().to_dict()
    cards = ev_m[ev_m.tipo.isin(["amarilla", "segunda_amarilla", "roja"])]
    card_of = {}
    for r in cards.itertuples():
        card_of.setdefault(r.jugador, []).append("🟨" if r.tipo == "amarilla" else ("🟨🟥" if r.tipo == "segunda_amarilla" else "🟥"))
    for rol, lbl in (("POR", "POR"), ("DEF", "DEF"), ("MED", "MED"), ("DEL", "DEL")):
        pl = al_m[al_m.rol == rol]
        items = []
        for r in pl.itertuples():
            mm = m_by.get(r.jugador)
            extra = ("⚽" * goals.get(r.jugador, 0)) + "".join(card_of.get(r.jugador, []))
            items.append(f"<span class='pl'><b>{int(r.dorsal)}</b>{escape(r.jugador)}<small>{'—' if pd.isna(mm) else f'{int(mm)}′'} {extra}</small></span>")
        lines.append(f"<div class='line'><span class='lbl'>{lbl}</span>{''.join(items)}</div>")
    subs = al_m[al_m.rol.str.startswith("SUP")]
    items = []
    for r in subs.itertuples():
        mm = m_by.get(r.jugador)
        extra = ("⚽" * goals.get(r.jugador, 0)) + "".join(card_of.get(r.jugador, [])) + (" 🧤" if r.rol == "SUP_POR" else "")
        items.append(f"<span class='pl'><b>{int(r.dorsal)}</b>{escape(r.jugador)}<small>{'—' if pd.isna(mm) else f'{int(mm)}′'}{extra}</small></span>")
    lines.append(f"<div class='line'><span class='lbl'>SUP</span>{''.join(items)}</div>")
    return "<div class='lineup'>" + "".join(lines) + "</div>"


def _match_detail(part, al, ev, mins, row):
    j = int(row.jornada)
    for side, team in (("Local", row.local), ("Visitante", row.visitante)):
        al_m = al[(al.equipo == team) & (al.jornada == j)]
        mins_m = mins[(mins.equipo == team) & (mins.jornada == j)]
        ev_m = ev[(ev.equipo == team) & (ev.jornada == j)]
        sis = row.sistema_local if side == "Local" else row.sistema_visitante
        st.markdown(f"<div class='q-title'>{side}: {escape(team)} <span class='cad-badge ok'>Acta</span>"
                    f"<span class='cad-badge pend'>{escape(str(sis) if isinstance(sis, str) else 's/ sistema')}</span></div>", unsafe_allow_html=True)
        st.markdown(_lineup_html(al_m, mins_m, ev_m), unsafe_allow_html=True)
    evm = ev[ev.jornada == j]
    evm = evm[(evm.equipo == row.local) | (evm.equipo == row.visitante)].sort_values("minuto")
    icons = {"gol": "⚽", "penalti_gol": "⚽ (pen.)", "gol_propia": "⚽ (p.p.)", "amarilla": "🟨", "segunda_amarilla": "🟨🟥",
             "roja": "🟥", "cambio": "🔁", "amarilla_tecnico": "🟨 banquillo", "roja_tecnico": "🟥 banquillo"}
    lines = []
    for r in evm.itertuples():
        txt = r.jugador
        if r.tipo == "cambio":
            txt = f"entra {r.jugador} · {str(r.detalle).split(';')[0].replace('sale=', 'sale ')}"
        lines.append(f"<div class='cad-note' style='margin:2px 0'><b style='color:var(--ink)'>{int(r.minuto)}'</b> · {icons.get(r.tipo, r.tipo)} · "
                     f"{escape(txt)} <span style='color:var(--muted)'>({escape(short(r.equipo))})</span></div>")
    with st.expander("Cronología del acta"):
        st.markdown("".join(lines), unsafe_allow_html=True)


def _possible_eleven(al, mins, team):
    a = al[(al.equipo == team) & (~al.rol.str.startswith("SUP"))]
    if a.empty:
        return ""
    nj = a.jornada.nunique()
    starts = a.groupby(["jugador", "rol"]).size().reset_index(name="tit")
    mm = mins[mins.equipo == team].groupby("jugador").minutos.sum()
    starts["min"] = starts.jugador.map(mm).fillna(0)
    part = data()[0]
    sis = []
    for r in part.itertuples():
        if r.local == team and isinstance(r.sistema_local, str):
            sis.append(r.sistema_local)
        elif r.visitante == team and isinstance(r.sistema_visitante, str):
            sis.append(r.sistema_visitante)
    formation = pd.Series(sis).mode().iat[0] if sis else "1-4-4-2"
    need = dict(zip(("POR", "DEF", "MED", "DEL"), [1] + [int(x) for x in formation.split("-")[1:]]))
    used, lines = set(), []
    for rol in ("POR", "DEF", "MED", "DEL"):
        c = starts[(starts.rol == rol) & (~starts.jugador.isin(used))].sort_values(["tit", "min"], ascending=False).head(need[rol])
        used |= set(c.jugador)
        items = "".join(f"<span class='pl'>{escape(r.jugador)}<small>{r.tit}/{nj} tit.</small></span>" for r in c.itertuples())
        lines.append(f"<div class='line'><span class='lbl'>{rol}</span>{items}</div>")
    freq = pd.Series(sis).value_counts()
    ftxt = ", ".join(f"{k} ({v})" for k, v in freq.items())
    return (f"<div class='q-title'>Posible once <span class='cad-badge est'>Estimación, no confirmada</span></div>"
            f"<div class='q-sub'>Sistema más usado: {escape(formation)} · sistemas en sus actas: {escape(ftxt)}. Se eligen, por línea, los jugadores con más "
            "titularidades (y minutos para desempatar).</div><div class='lineup'>" + "".join(lines) + "</div>")


def render_rivals():
    st.markdown(CSS, unsafe_allow_html=True)
    part, al, ev, mins, av = data()
    teams = teams_list(part)
    st.markdown(f"<div class='league-hero'><div><div class='league-eyebrow'>CADETE A · PARTIDOS DE {MM}'</div>"
                "<div class='league-title'>🎯 Rivales</div><div class='league-subtitle'>Ficha, partidos con alineaciones de las actas, plantilla y minutos, "
                "goleadores, porteros, disciplina, posible once y comparador.</div></div>"
                f"<div class='league-badge'>{len(teams) - 1} rivales</div></div>", unsafe_allow_html=True)
    team = _team_selector("Equipo", "cad_rival", default=sorted(t for t in teams if t != TEAM)[0])
    tm, me, tab = _team_profile(part, team)
    home, away = tm[tm.condicion == "Casa"], tm[tm.condicion == "Fuera"]
    st.markdown("<div class='cad-kpis k6'>"
                + _kpi("Posición", f"{me.pos}º", f"{me.pts} puntos", "pt")
                + _kpi("Balance", f"{me.pg}-{me.pe}-{me.pp}", f"{me.pj} partidos")
                + _kpi("Goles", f"{me.gf}–{me.gc}", f"diferencia {me.dg:+d}")
                + _kpi("En casa", f"{int(home.puntos.sum())} pts", f"{len(home)} PJ · {int(home.gf.sum())}–{int(home.gc.sum())}")
                + _kpi("Fuera", f"{int(away.puntos.sum())} pts", f"{len(away)} PJ · {int(away.gf.sum())}–{int(away.gc.sum())}")
                + _kpi(f"Goles por {MM}'", _fmt(me.gf / me.pj), f"encaja {_fmt(me.gc / me.pj)} por partido") + "</div>",
                unsafe_allow_html=True)
    tabs = st.tabs(["Partidos", "Plantilla y minutos", "Goleadores", "Porteros", "Disciplina", "Posible once", "Comparador"])
    with tabs[0]:
        rows = part[(part.local == team) | (part.visitante == team)].sort_values("jornada")
        for r in rows.itertuples():
            st.markdown(_match_row(r, team), unsafe_allow_html=True)
            with st.expander(f"J{int(r.jornada)} · alineaciones, cambios, minutos, goles y tarjetas"):
                _match_detail(part, al, ev, mins, r)
    with tabs[1]:
        pj = len(tm)
        pa = lc.participation(mins, team, MM, pj)
        pend = mins[(mins.equipo == team) & mins.minutos.isna()]
        st.markdown(f"<div class='q-title'>Minutos y participación</div><div class='q-sub'>% sobre {MM}' × {pj} partidos = "
                    f"{MM * pj} minutos posibles. Convocados según el acta.</div>", unsafe_allow_html=True)
        st.markdown(_ranking([(f"{int(r.dorsal) if pd.notna(r.dorsal) else '—'} · {r.jugador}", r.minutos,
                               f"{int(r.titular)} tit. · {int(r.suplente)} supl. · {r.pct:.0f} %") for r in pa.head(20).itertuples()],
                             PT, value_fmt=lambda v: f"{int(v)}′", max_v=MM * pj), unsafe_allow_html=True)
        conv = al[al.equipo == team].groupby("jugador").size()
        pa["convocado"] = pa.jugador.map(conv).fillna(0).astype(int)
        with st.expander(f"Tabla completa ({len(pa)} jugadores)"):
            st.dataframe(pa.rename(columns={"dorsal": "Dorsal", "jugador": "Jugador", "convocado": "Convocado", "partidos": "Jugados",
                                            "titular": "Titular", "suplente": "Suplente", "minutos": "Minutos", "pct": "% minutos",
                                            "media": "Media por partido"})[["Dorsal", "Jugador", "Convocado", "Jugados", "Titular", "Suplente", "Minutos", "% minutos", "Media por partido"]],
                         hide_index=True, width="stretch",
                         column_config={"% minutos": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f %%"),
                                        "Media por partido": st.column_config.NumberColumn(format="%.0f′")})
        if not pend.empty:
            st.markdown(f"<div class='cad-note'>Minutos pendientes ({len(pend)}): el acta no permite saber cuál de dos jugadores con la misma "
                        f"abreviatura fue sustituido ({', '.join(sorted(set(pend.jugador)))}).</div>", unsafe_allow_html=True)
        mt = mins[mins.equipo == team].pivot_table(index="jugador", columns="jornada", values="minutos", aggfunc="sum")
        mt = mt.loc[pa.jugador.head(18)]
        fig = go.Figure(go.Heatmap(z=mt.values, x=[f"J{c}" for c in mt.columns], y=mt.index, colorscale=[[0, TOKENS["surface-2"]], [1, PT]],
                                   zmin=0, zmax=MM, hovertemplate="%{y} · %{x}: %{z}′<extra></extra>", colorbar=dict(title="min")))
        _plot(fig, "cad_rv_heat", h=120 + 22 * len(mt), title="Evolución de minutos por jornada", yaxis=dict(autorange="reversed"))
    with tabs[2]:
        sc = lc.scorers(ev, mins, team)
        st.markdown("<div class='q-title'>Goleadores</div>" + _ranking(
            [(r.jugador, r.goles, f"{r.minutos_gol} · {r.pct_equipo:.0f} % de los goles del equipo") for r in sc.itertuples()], PT),
            unsafe_allow_html=True)
        _bins_chart(ev, team, key="cad_rv_bins", title=f"Goles marcados y encajados por tramos · {short(team)}")
    with tabs[3]:
        g, w = lc.goalkeepers(al, mins, ev, part, team, MM)
        if g.empty:
            st.info("Sin porteros identificados en las actas.")
        else:
            st.dataframe(g.rename(columns={"jugador": "Portero", "partidos": "PJ", "titular": "Titular", "minutos": "Minutos",
                                           "encajados": "Goles encajados", "porterias_cero": "Porterías a cero",
                                           "encajados_por_partido_reglamentario": f"GC por {MM}'", "pct_minutos": "% minutos"}),
                         hide_index=True, width="stretch",
                         column_config={f"GC por {MM}'": st.column_config.NumberColumn(format="%.2f"),
                                        "% minutos": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f %%")})
            st.markdown(f"<div class='cad-note'>Cada gol se atribuye al portero que estaba en el campo en ese minuto (cambios del acta). "
                        f"GC por {MM}' = encajados ÷ minutos × {MM}. Portería a cero: titular que juega el partido completo sin encajar.</div>",
                        unsafe_allow_html=True)
            for x in w:
                st.markdown(f"<div class='cad-note'>⚠️ {escape(x)}</div>", unsafe_allow_html=True)
    with tabs[4]:
        d = lc.discipline(ev, team)
        if d.empty:
            st.info("Sin tarjetas registradas.")
        else:
            st.markdown("<div class='q-title'>Tarjetas por jugador</div>" + _ranking(
                [(r.jugador, r.amarillas + 2 * r.rojas, f"{int(r.amarillas)} 🟨 · {int(r.rojas)} 🟥") for r in d.itertuples()],
                TOKENS["warn"], value_fmt=lambda v: ""), unsafe_allow_html=True)
        tec = ev[(ev.equipo == team) & ev.tipo.str.endswith("_tecnico")]
        if not tec.empty:
            st.markdown(f"<div class='cad-note'>Además, {len(tec)} tarjeta(s) al cuerpo técnico (no cuentan como jugadores).</div>", unsafe_allow_html=True)
        tt = lc.discipline(ev).groupby("equipo")[["amarillas", "rojas"]].sum().reset_index()
        tt = tt.sort_values("amarillas")
        fig = go.Figure()
        fig.add_bar(y=tt.equipo.map(short), x=tt.amarillas, orientation="h", name="Amarillas", marker_color=TOKENS["warn"],
                    hovertemplate="%{y}: %{x} amarillas<extra></extra>")
        fig.add_bar(y=tt.equipo.map(short), x=tt.rojas, orientation="h", name="Expulsiones", marker_color=NEG,
                    hovertemplate="%{y}: %{x} expulsiones<extra></extra>")
        _plot(fig, "cad_rv_disc", h=80 + 24 * len(tt), title="Disciplina por equipo (jugadores)", barmode="stack")
    with tabs[5]:
        st.markdown(_possible_eleven(al, mins, team), unsafe_allow_html=True)
        last = part[(part.local == team) | (part.visitante == team)].sort_values("jornada").iloc[-1]
        st.markdown(f"<div class='q-title'>Último once confirmado <span class='cad-badge ok'>Acta J{int(last.jornada)}</span></div>",
                    unsafe_allow_html=True)
        st.markdown(_lineup_html(al[(al.equipo == team) & (al.jornada == last.jornada)],
                                 mins[(mins.equipo == team) & (mins.jornada == last.jornada)],
                                 ev[(ev.equipo == team) & (ev.jornada == last.jornada)]), unsafe_allow_html=True)
        subs = ev[(ev.equipo == team) & (ev.tipo == "cambio")]
        if not subs.empty:
            st.markdown(f"<div class='cad-note'>Cambios habituales: primer cambio de media en el minuto {subs.groupby('jornada').minuto.min().mean():.0f}; "
                        f"{len(subs) / subs.jornada.nunique():.1f} cambios por partido.</div>", unsafe_allow_html=True)
    with tabs[6]:
        _comparator(part, ev, mins, al, team)


def _comparator(part, ev, mins, al, team_a):
    teams = teams_list(part)
    c1, c2 = st.columns(2)
    a = c1.selectbox("Equipo A", teams, index=teams.index(team_a), key="cad_cmp_a")
    b = c2.selectbox("Equipo B", teams, index=teams.index(TEAM) if a != TEAM else 0, key="cad_cmp_b")
    tab = lc.standings(part, teams)
    ra, rb = tab[tab.equipo == a].iloc[0], tab[tab.equipo == b].iloc[0]

    def metr(r):
        return {"Posición": r.pos, "Puntos por partido": r.pts / r.pj, f"Goles marcados por {MM}'": r.gf / r.pj,
                f"Goles encajados por {MM}'": r.gc / r.pj, "Puntos por partido en casa": r.pts_casa / max(r.pj_casa, 1),
                "Puntos por partido fuera": r.pts_fuera / max(r.pj_fuera, 1)}
    ma, mb = metr(ra), metr(rb)
    rows = "".join(f"<tr><td class='l'>{k}</td><td style='color:{PT};font-weight:800'>{_fmt(ma[k]) if k != 'Posición' else f'{ma[k]}º'}</td>"
                   f"<td style='color:{RIVAL};font-weight:800'>{_fmt(mb[k]) if k != 'Posición' else f'{mb[k]}º'}</td></tr>" for k in ma)
    st.markdown(f"<div class='cad-wrap'><table class='cad-table'><tr><th class='l'>Indicador</th><th>{escape(short(a))}</th><th>{escape(short(b))}</th></tr>{rows}</table></div>",
                unsafe_allow_html=True)
    evo = lc.position_evolution(part, teams)
    fig = go.Figure()
    for t, col in ((a, PT), (b, RIVAL)):
        e = evo[evo.equipo == t]
        fig.add_scatter(x=e.jornada, y=e.pts, mode="lines+markers", name=short(t), line=dict(color=col, width=2), marker=dict(size=8),
                        hovertemplate=f"{short(t)} · J%{{x}}: %{{y}} pts<extra></extra>")
    _plot(fig, "cad_cmp_evo", title="Puntos acumulados por jornada", xaxis=dict(dtick=1, title="Jornada"))
    c3, c4 = st.columns(2)
    for col, t, color in ((c3, a, PT), (c4, b, RIVAL)):
        with col:
            sc = lc.scorers(ev, mins, t).head(5)
            g, _ = lc.goalkeepers(al, mins, ev, part, t, MM)
            gk = g.iloc[0] if not g.empty else None
            st.markdown(f"<div class='q-title'>{escape(short(t))}</div><div class='q-sub'>Goleadores principales</div>"
                        + _ranking([(r.jugador, r.goles, "") for r in sc.itertuples()], color)
                        + (f"<div class='cad-note'>Portero con más minutos: <b style='color:var(--ink)'>{escape(gk.jugador)}</b> · {int(gk.minutos)}′ · "
                           f"{_fmt(gk.encajados_por_partido_reglamentario)} GC por {MM}'</div>" if gk is not None else ""),
                        unsafe_allow_html=True)


# ------------------------------------------------------------------ estadísticas

def render_stats():
    st.markdown(CSS, unsafe_allow_html=True)
    part, al, ev, mins, av = data()
    st.markdown(f"<div class='league-hero'><div><div class='league-eyebrow'>CADETE A · PRIMER TOQUE C.F.</div>"
                "<div class='league-title'>📊 Estadísticas</div><div class='league-subtitle'>Resultados, goles por tramos, casa/fuera, porteros, minutos y goleadores. "
                f"Todos los indicadores por partido usan {MM} minutos.</div></div><div class='league-badge'>Datos de actas FFCV</div></div>",
                unsafe_allow_html=True)
    tm = lc.team_matches(part, TEAM)
    pj = len(tm)
    home, away = tm[tm.condicion == "Casa"], tm[tm.condicion == "Fuera"]
    st.markdown("<div class='cad-kpis k6'>"
                + _kpi("Partidos", pj, f"{int((tm.resultado == 'V').sum())} V · {int((tm.resultado == 'E').sum())} E · {int((tm.resultado == 'D').sum())} D", "pt")
                + _kpi("Puntos", int(tm.puntos.sum()), f"{tm.puntos.mean():.2f} por partido".replace(".", ","), "pt")
                + _kpi(f"Goles por {MM}'", _fmt(tm.gf.mean()), f"{int(tm.gf.sum())} marcados")
                + _kpi(f"Encajados por {MM}'", _fmt(tm.gc.mean()), f"{int(tm.gc.sum())} encajados")
                + _kpi("En casa", f"{int(home.puntos.sum())} pts", f"{len(home)} PJ · {int(home.gf.sum())}–{int(home.gc.sum())}")
                + _kpi("Fuera", f"{int(away.puntos.sum())} pts", f"{len(away)} PJ · {int(away.gf.sum())}–{int(away.gc.sum())}") + "</div>",
                unsafe_allow_html=True)
    t = st.tabs(["Resultados y goles", "Casa / fuera", "Minutos", "Goleadores", "Porteros", "Comparar jornadas"])
    with t[0]:
        c1, c2 = st.columns(2)
        with c1:
            col = [POS if r == "V" else (TOKENS["warn"] if r == "E" else NEG) for r in tm.resultado]
            fig = go.Figure(go.Bar(x=[f"J{j}" for j in tm.jornada], y=tm.gf - tm.gc, marker_color=col,
                                   text=[f"{a}–{b}" for a, b in zip(tm.gf, tm.gc)], textposition="outside",
                                   textfont=dict(color=TOKENS["ink"]), cliponaxis=False,
                                   customdata=tm[["rival", "gf", "gc"]], hovertemplate="%{x} vs %{customdata[0]}: %{customdata[1]}–%{customdata[2]}<extra></extra>"))
            _plot(fig, "cad_st_res", title="Diferencia de goles en cada partido")
        with c2:
            _bins_chart(ev, TEAM, key="cad_st_bins", title="Goles marcados y encajados por tramos de 10'")
        st.markdown("<div class='q-title'>Rendimiento por partes</div>", unsafe_allow_html=True)
        h1f = h1c = h2f = h2c = 0
        for r in ev.itertuples():
            side = lc.goal_side(r._asdict(), TEAM) if r.tipo in lc.GOAL_TYPES_FOR | lc.OWN_GOAL_TYPES else None
            if side is None or pd.isna(r.minuto):
                continue
            first_half = r.minuto <= MM // 2
            if side == "favor":
                h1f += first_half; h2f += not first_half
            else:
                h1c += first_half; h2c += not first_half
        st.markdown("<div class='cad-kpis'>" + _kpi("1ª parte · marcados", h1f, f"minutos 1–{MM // 2}") + _kpi("1ª parte · encajados", h1c, "")
                    + _kpi("2ª parte · marcados", h2f, f"minutos {MM // 2 + 1}–{MM}") + _kpi("2ª parte · encajados", h2c, "") + "</div>"
                    "<div class='cad-note'>Un gol en el minuto 40 se cuenta en la 1ª parte; el acta no distingue el añadido de la 1ª parte "
                    "del inicio de la 2ª cuando el minuto es 41.</div>", unsafe_allow_html=True)
    with t[1]:
        rows = []
        for nm, d in (("Casa", home), ("Fuera", away)):
            n = max(len(d), 1)
            rows.append(dict(Campo=nm, PJ=len(d), V=int((d.resultado == "V").sum()), E=int((d.resultado == "E").sum()),
                             D=int((d.resultado == "D").sum()), Puntos=int(d.puntos.sum()), GF=int(d.gf.sum()), GC=int(d.gc.sum()),
                             **{"Pts/partido": d.puntos.sum() / n, "GF/partido": d.gf.sum() / n, "GC/partido": d.gc.sum() / n}))
        df = pd.DataFrame(rows)
        fig = go.Figure()
        for k, col in (("Pts/partido", PT), ("GF/partido", POS), ("GC/partido", RIVAL)):
            fig.add_bar(x=df.Campo, y=df[k], name=k, marker_color=col, hovertemplate="%{x} · " + k + ": %{y:.2f}<extra></extra>")
        _plot(fig, "cad_st_cf", title="Casa frente a fuera (valores por partido)", barmode="group")
        st.dataframe(df, hide_index=True, width="stretch",
                     column_config={k: st.column_config.NumberColumn(format="%.2f") for k in ("Pts/partido", "GF/partido", "GC/partido")})
    with t[2]:
        pa = lc.participation(mins, TEAM, MM, pj)
        st.markdown(f"<div class='q-title'>Participación de la plantilla</div><div class='q-sub'>% sobre {MM}' × {pj} partidos. "
                    f"Un partido completo = {MM}'; 40' = 50 %.</div>", unsafe_allow_html=True)
        st.markdown(_ranking([(f"{int(r.dorsal) if pd.notna(r.dorsal) else '—'} · {r.jugador}", r.minutos,
                               f"{int(r.titular)} tit. · {int(r.suplente)} supl. · {r.pct:.0f} %") for r in pa.itertuples()],
                             PT, value_fmt=lambda v: f"{int(v)}′", max_v=MM * pj), unsafe_allow_html=True)
        mt = mins[mins.equipo == TEAM].pivot_table(index="jugador", columns="jornada", values="minutos", aggfunc="sum").loc[pa.jugador]
        fig = go.Figure(go.Heatmap(z=mt.values, x=[f"J{c}" for c in mt.columns], y=mt.index, colorscale=[[0, TOKENS["surface-2"]], [1, PT]],
                                   zmin=0, zmax=MM, hovertemplate="%{y} · %{x}: %{z}′<extra></extra>", colorbar=dict(title="min")))
        _plot(fig, "cad_st_heat", h=120 + 22 * len(mt), title="Minutos por jornada", yaxis=dict(autorange="reversed"))
    with t[3]:
        sc = lc.scorers(ev, mins, TEAM)
        st.markdown("<div class='q-title'>Goleadores del Cadete A</div>" + _ranking(
            [(r.jugador, r.goles, f"{r.minutos_gol} · {r.pct_equipo:.0f} % de los goles · "
                                  f"{_fmt(r.goles_partido)} por partido jugado") for r in sc.itertuples()], PT), unsafe_allow_html=True)
        g = ev[(ev.equipo == TEAM) & ev.tipo.isin(lc.GOAL_TYPES_FOR)].groupby("jornada").size().reindex(tm.jornada, fill_value=0).cumsum()
        fig = go.Figure(go.Scatter(x=[f"J{j}" for j in g.index], y=g.values, mode="lines+markers", line=dict(color=PT, width=2),
                                   marker=dict(size=8), hovertemplate="%{x}: %{y} goles acumulados<extra></extra>"))
        _plot(fig, "cad_st_gevo", title="Goles acumulados")
        st.markdown("<div class='cad-note'>Asistencias: las actas no las registran. No se muestran para no inventar datos.</div>", unsafe_allow_html=True)
    with t[4]:
        g, w = lc.goalkeepers(al, mins, ev, part, TEAM, MM)
        st.dataframe(g.rename(columns={"jugador": "Portero", "partidos": "PJ", "titular": "Titular", "minutos": "Minutos",
                                       "encajados": "Goles encajados", "porterias_cero": "Porterías a cero",
                                       "encajados_por_partido_reglamentario": f"GC por {MM}'", "pct_minutos": "% minutos"}),
                     hide_index=True, width="stretch",
                     column_config={f"GC por {MM}'": st.column_config.NumberColumn(format="%.2f"),
                                    "% minutos": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f %%")})
        st.markdown(f"<div class='cad-note'>GC por {MM}' = goles encajados con el portero en el campo ÷ minutos × {MM}.</div>", unsafe_allow_html=True)
        for x in w:
            st.markdown(f"<div class='cad-note'>⚠️ {escape(x)}</div>", unsafe_allow_html=True)
    with t[5]:
        js = [f"J{j}" for j in tm.jornada]
        c1, c2 = st.columns(2)
        a = c1.selectbox("Jornada A", js, index=0, key="cad_st_ja")
        b = c2.selectbox("Jornada B", js, index=len(js) - 1, key="cad_st_jb")
        for col, lab in ((c1, a), (c2, b)):
            j = int(lab[1:])
            r = tm[tm.jornada == j].iloc[0]
            row = part[(part.jornada == j) & ((part.local == TEAM) | (part.visitante == TEAM))].iloc[0]
            with col:
                st.markdown(_match_row(row, TEAM), unsafe_allow_html=True)
                sub = mins[(mins.equipo == TEAM) & (mins.jornada == j)]
                st.markdown("<div class='cad-kpis'>" + _kpi("Resultado", f"{r.gf}–{r.gc}", r.condicion) + _kpi("Jugadores usados", int((sub.minutos > 0).sum()), "")
                            + _kpi("Cambios", int(((ev.equipo == TEAM) & (ev.jornada == j) & (ev.tipo == "cambio")).sum()), "")
                            + _kpi("Tarjetas", int(((ev.equipo == TEAM) & (ev.jornada == j) & ev.tipo.isin(["amarilla", "segunda_amarilla", "roja"])).sum()), "")
                            + "</div>", unsafe_allow_html=True)
    st.markdown("<div class='cad-note'>Estadísticas avanzadas de vídeo (posesión, pases, tiros…): no hay datos de vídeo del Cadete A. "
                "No se muestran para no inventar datos.</div>", unsafe_allow_html=True)
