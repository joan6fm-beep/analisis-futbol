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

import base64

import crests
import league_core as lc
import pt_viz
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
    lay = plotly_layout(height=h)
    for k, v in kw.items():  # combina con el tema (rejilla, colores) en vez de sustituirlo
        lay[k] = {**lay[k], **v} if isinstance(v, dict) and isinstance(lay.get(k), dict) else v
    if "title" in kw and "legend" not in kw:
        lay["legend"] = {**lay["legend"], "orientation": "h", "yanchor": "top", "y": -0.14, "x": 0}
    fig.update_layout(**lay)
    st.plotly_chart(fig, width="stretch", theme=None, config=PLOTLY_CONFIG, key=key)


def _fmt(v, d=2):
    return "—" if v is None or pd.isna(v) else f"{v:.{d}f}".replace(".", ",")


@st.cache_data(show_spinner=False)
def crest(team, size=22):
    """Escudo del equipo (crests.py) o marcador neutro si no hay escudo verificado."""
    pth = crests.crest_path(team)
    if not pth.exists():
        return (f"<span title='Escudo pendiente' style='display:inline-flex;align-items:center;justify-content:center;width:{size}px;"
                f"height:{size}px;border-radius:50%;border:1px dashed #3A465B;color:#8A97AB;font-size:10px;margin-right:6px;vertical-align:middle'>?</span>")
    b64 = base64.b64encode(pth.read_bytes()).decode()
    return (f"<img src='data:image/png;base64,{b64}' alt='' style='width:{size}px;height:{size}px;object-fit:contain;"
            "vertical-align:middle;margin-right:6px'>")


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
    return (f"<div class='cad-match'><span class='j'>J{int(r.jornada)}</span><span class='t'>{crest(r.local)}{escape(r.local)} — {crest(r.visitante)}{escape(r.visitante)}"
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
        body.append(f"<tr{cls}><td>{r.pos}</td><td class='l'>{crest(r.equipo, 20)}{escape(r.equipo)}</td><td>{r.pj}</td><td>{r.pg}</td><td>{r.pe}</td>"
                    f"<td>{r.pp}</td><td>{r.gf}</td><td>{r.gc}</td><td>{dg}</td><td class='pts'>{r.pts}</td></tr>")
    return f"<div class='cad-wrap'><table class='cad-table'>{head}{''.join(body)}</table></div>"



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
        "<a href='?area=cadete&view=equipo' target='_self'>Equipo</a>"
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




def render_comparator(team_a, logo=None):
    """Comparador de dos equipos de la liga (datos del Cadete A, unidades por 80')."""
    part, al, ev, mins, av = data()
    teams = teams_list(part)
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div><div class='section-title'>Comparador de equipos</div>"
                f"<div class='note'>Elige dos equipos de la liga. Valores por partido de {MM}'.</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    a = c1.selectbox("Equipo A", teams, index=teams.index(team_a) if team_a in teams else 0, key="cad_cmp_a")
    b = c2.selectbox("Equipo B", teams, index=teams.index(TEAM) if a != TEAM else 0, key="cad_cmp_b")
    tab = lc.standings(part, teams)
    ra, rb = tab[tab.equipo == a].iloc[0], tab[tab.equipo == b].iloc[0]

    def metr(r):
        return {"Posición": r.pos, "Puntos por partido": r.pts / r.pj, f"Goles marcados por {MM}'": r.gf / r.pj,
                f"Goles encajados por {MM}'": r.gc / r.pj, "Puntos por partido en casa": r.pts_casa / max(r.pj_casa, 1),
                "Puntos por partido fuera": r.pts_fuera / max(r.pj_fuera, 1)}
    ma, mb = metr(ra), metr(rb)
    # Primer Toque siempre naranja; los rivales en azul (y azul claro si se comparan dos rivales).
    ca = PT if a == TEAM else RIVAL
    cb = PT if b == TEAM else ("#A9C0E3" if a != TEAM else RIVAL)
    lg = logo or (lambda t, n: "")
    better = {"Posición": False, f"Goles encajados por {MM}'": False}
    fmtv = lambda k, v: f"{v}º" if k == "Posición" else _fmt(v)
    c_duel, c_radar = st.columns([1, 1], gap="medium")
    c_duel.markdown(pt_viz.duel_html([(k, float(ma[k]), float(mb[k]), fmtv(k, ma[k]), fmtv(k, mb[k]), better.get(k, True)) for k in ma],
                                 short(a), short(b), ca, cb, lg(a, 22), lg(b, 22)), unsafe_allow_html=True)
    ax = ["Pts/partido", "GF/partido", "Solidez (menos GC)", "Pts casa", "Pts fuera"]
    def _vals(r):
        return [r.pts / r.pj, r.gf / r.pj, None, r.pts_casa / max(r.pj_casa, 1), r.pts_fuera / max(r.pj_fuera, 1)]
    played_tab = tab[tab.pj > 0]
    gcmax = float((played_tab.gc / played_tab.pj).max()) or 1
    series = []
    for t, r, col in ((a, ra, ca), (b, rb, cb)):
        v = _vals(r); gcp = r.gc / r.pj
        v[2] = gcmax - gcp  # solidez: distancia al equipo que más encaja de la liga
        texts = [_fmt(v[0]), _fmt(v[1]), f"{_fmt(gcp)} GC/p", _fmt(v[3]), _fmt(v[4])]
        series.append((short(t), v, col, texts))
    mx = [3, max(float((played_tab.gf / played_tab.pj).max()), .01), max(gcmax - float((played_tab.gc / played_tab.pj).min()), .01), 3, 3]
    fig = pt_viz.fig_radar(ax, series, height=360, max_vals=mx)
    c_radar.plotly_chart(fig, width="stretch", theme=None, config=PLOTLY_CONFIG, key="cad_cmp_radar")
    c_radar.markdown("<div class='cad-note'>Radar: cada eje sobre el máximo posible o el mejor de la liga. Solidez = cuánto menos encaja que el equipo "
                "más goleado. Pasa el ratón para ver el valor real.</div>", unsafe_allow_html=True)
    evo = lc.position_evolution(part, teams)
    fig = go.Figure()
    for t, col in ((a, ca), (b, cb)):
        e = evo[evo.equipo == t]
        fig.add_scatter(x=[f"J{j}" for j in e.jornada], y=e.pts, mode="lines+markers", name=short(t), line=dict(color=col, width=2), marker=dict(size=8),
                        hovertemplate=f"{short(t)} · %{{x}}: %{{y}} pts<extra></extra>")
    _plot(fig, "cad_cmp_evo", title="Puntos acumulados por jornada")
    c3, c4 = st.columns(2)
    for col, t, color in ((c3, a, ca), (c4, b, cb)):
        with col:
            sc = lc.scorers(ev, mins, t).head(5)
            g, _ = lc.goalkeepers(al, mins, ev, part, t, MM)
            gk = g.iloc[0] if not g.empty else None
            st.markdown(f"<div class='q-title'>{lg(t, 24)}{escape(short(t))}</div><div class='q-sub'>Goleadores principales</div>"
                        + _ranking([(r.jugador, r.goles, "") for r in sc.itertuples()], color)
                        + (f"<div class='cad-note'>Portero con más minutos: <b style='color:var(--ink)'>{escape(gk.jugador)}</b> · {int(gk.minutos)}′ · "
                           f"{_fmt(gk.encajados_por_partido_reglamentario)} GC por {MM}'</div>" if gk is not None else ""),
                        unsafe_allow_html=True)


def render_match_library(team, jornada_sel="Total"):
    """Partidos del equipo con acceso al acta completa: alineaciones, sistemas, cambios, minutos,
    goles, porteros y tarjetas. Incluye las tarjetas por jornada."""
    part, al, ev, mins, av = data()
    st.markdown(CSS, unsafe_allow_html=True)
    rows = part[(part.local == team) | (part.visitante == team)].sort_values("jornada")
    if jornada_sel != "Total":
        rows = rows[rows.jornada == int(str(jornada_sel)[1:])]
    st.markdown("<div style='height:14px'></div><div class='section-title'>Partidos analizados · actas FFCV</div>"
                "<div class='note'>Abre cada partido para ver alineaciones, sistemas, cambios con su minuto, minutos de cada jugador "
                "(sobre 80'), goles y tarjetas. Datos confirmados del acta; no se completa nada que no figure en ella.</div>",
                unsafe_allow_html=True)
    for r in rows.itertuples():
        st.markdown(_match_row(r, team), unsafe_allow_html=True)
        with st.expander(f"J{int(r.jornada)} · acta: alineaciones, cambios, minutos, goles y tarjetas"):
            _match_detail(part, al, ev, mins, r)
    c = ev[(ev.equipo == team) & ev.tipo.isin(["amarilla", "segunda_amarilla", "roja"])]
    js = sorted(part[(part.local == team) | (part.visitante == team)].jornada.unique())
    am = c[c.tipo == "amarilla"].groupby("jornada").size().reindex(js, fill_value=0)
    ro = c[c.tipo.isin(["segunda_amarilla", "roja"])].groupby("jornada").size().reindex(js, fill_value=0)
    fig = go.Figure()
    fig.add_bar(x=[f"J{j}" for j in js], y=am.values, name="Amarillas", marker_color=TOKENS["warn"],
                hovertemplate="%{x}: %{y} amarillas<extra></extra>")
    fig.add_bar(x=[f"J{j}" for j in js], y=ro.values, name="Expulsiones", marker_color=NEG,
                hovertemplate="%{x}: %{y} expulsiones<extra></extra>")
    _plot(fig, f"cad_cards_{team}", h=260, title="Tarjetas por jornada (jugadores)", barmode="stack",
          legend=dict(orientation="h", yanchor="top", y=-0.15, x=0, bgcolor="rgba(0,0,0,0)"))
    tec = ev[(ev.equipo == team) & ev.tipo.str.endswith("_tecnico")]
    if not tec.empty:
        st.markdown(f"<div class='cad-note'>Además, {len(tec)} tarjeta(s) al cuerpo técnico (no se cuentan como jugadores).</div>",
                    unsafe_allow_html=True)


def _points_charts(part, teams, sel):
    """Puntos por jornada (barras por resultado) y puntos acumulados (Primer Toque, equipo elegido y líder)."""
    tm = lc.team_matches(part, TEAM)
    evo = lc.position_evolution(part, teams)
    c1, c2 = st.columns(2)
    with c1:
        col = [POS if r == "V" else (TOKENS["warn"] if r == "E" else NEG) for r in tm.resultado]
        # Las derrotas (0 puntos) se dibujan como una barra mínima para que se vean; el marcador va en la etiqueta.
        fig = go.Figure(go.Bar(x=[f"J{j}" for j in tm.jornada], y=[max(p, 0.08) for p in tm.puntos], marker_color=col,
                               marker_line_width=0, text=[f"{a}–{b}" for a, b in zip(tm.gf, tm.gc)], textposition="outside",
                               textfont=dict(color=TOKENS["ink"], size=12), cliponaxis=False,
                               customdata=list(zip(tm.rival.map(short), tm.condicion, tm.puntos)),
                               hovertemplate="%{x} · %{customdata[1]} vs %{customdata[0]}<br>%{text} · %{customdata[2]} pts<extra></extra>"))
        _plot(fig, "cad_eq_ppj", h=300, title="Puntos por jornada", bargap=0.35,
              yaxis=dict(range=[0, 3.8], tickvals=[0, 1, 3], ticktext=["0", "1", "3"]))
    with c2:
        fig = go.Figure()
        lead = evo[evo.pos == 1].sort_values("jornada")
        fig.add_scatter(x=[f"J{j}" for j in lead.jornada], y=lead.pts, name="Líder de cada jornada", mode="lines",
                        line=dict(color=MUTED, width=1.5, dash="dot"), customdata=lead.equipo.map(short),
                        hovertemplate="%{x} · líder %{customdata}: %{y} pts<extra></extra>")
        for t, color in ([(sel, RIVAL)] if sel != TEAM else []) + [(TEAM, PT)]:
            e = evo[evo.equipo == t]
            fig.add_scatter(x=[f"J{j}" for j in e.jornada], y=e.pts, name=short(t), mode="lines+markers",
                            line=dict(color=color, width=3 if t == TEAM else 2),
                            marker=dict(size=8, line=dict(width=1.5, color=TOKENS["surface"])),
                            fill="tozeroy" if t == TEAM else None, fillcolor="rgba(255,138,30,0.10)" if t == TEAM else None,
                            customdata=e.pos, hovertemplate=f"{short(t)} · %{{x}}: %{{y}} pts · %{{customdata}}º<extra></extra>")
        _plot(fig, "cad_eq_acum", h=300, title="Puntos acumulados")


def render_team(logo=None):
    """Equipo · Cadete A: evolución, puntos por jornada y acumulados, comparación con la liga y estadísticas propias.
    Reutiliza el gráfico de clasificación del Juvenil A (team360_charts.fig_standings)."""
    import team360_charts as t360
    st.markdown(CSS, unsafe_allow_html=True)
    part, al, ev, mins, av = data()
    teams = teams_list(part)
    st.markdown("<div class='league-hero'><div><div class='league-eyebrow'>CADETE A · PRIMER TOQUE C.F.</div>"
                "<div class='league-title'>👥 Equipo · Cadete A</div><div class='league-subtitle'>Evolución, puntos por jornada, comparación con "
                f"los equipos de la liga y estadísticas propias. Todos los indicadores por partido usan {MM} minutos.</div></div>"
                "<div class='league-badge'>Datos de actas FFCV</div></div>", unsafe_allow_html=True)
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

    st.markdown("<div style='height:6px'></div><div class='section-title league-section-title'>Evolución y comparación de equipos</div>"
                "<div class='note'>Elige un equipo: se destaca en azul; Primer Toque siempre en naranja como referencia.</div>",
                unsafe_allow_html=True)
    others = [t for t in teams if t != TEAM]
    sel = st.selectbox("Equipo a destacar", [TEAM] + others, index=0, key="cad_lg_evo_team", format_func=lambda t: short(t))
    _points_charts(part, teams, sel)
    clas = pd.read_csv(DIR / "liga" / "clasificacion_liga.csv")
    st.plotly_chart(t360.fig_standings(clas, sel), width="stretch", theme=None, config=PLOTLY_CONFIG, key="cad_lg_standings")
    ts = lc.team_matches(part, sel)
    fig = go.Figure()
    fig.add_bar(x=[f"J{j}" for j in ts.jornada], y=ts.gf, name="Goles a favor", marker_color=PT if sel == TEAM else RIVAL,
                customdata=ts.rival.map(short), hovertemplate="%{x} vs %{customdata}: %{y} marcados<extra></extra>")
    fig.add_bar(x=[f"J{j}" for j in ts.jornada], y=-ts.gc, name="Goles en contra", marker_color=NEG,
                customdata=list(zip(ts.rival.map(short), ts.gc)), hovertemplate="%{x} vs %{customdata[0]}: %{customdata[1]} encajados<extra></extra>")
    fig.add_scatter(x=[f"J{j}" for j in ts.jornada], y=(ts.gf - ts.gc).cumsum(), name="Diferencia acumulada", mode="lines+markers",
                    line=dict(color=TOKENS["warn"], width=2), hovertemplate="%{x}: %{y:+d} acumulado<extra></extra>")
    fig.add_hline(y=0, line_color=MUTED, line_width=1)
    _plot(fig, "cad_lg_gfgc", title=f"Goles a favor (arriba), en contra (abajo) y diferencia acumulada · {short(sel)}", barmode="relative")
    last5 = ts.tail(5)
    st.markdown(f"<div class='cad-note'>Tendencia reciente de {escape(short(sel))}: "
                + " ".join(f"<span class='res {r}'>{r}</span>" for r in last5.resultado)
                + f" · {int(last5.puntos.sum())} de {3 * len(last5)} puntos en sus últimos {len(last5)} partidos.</div>",
                unsafe_allow_html=True)
    render_comparator(sel if sel != TEAM else (others[0] if others else TEAM), logo=logo)

    st.markdown("<div style='height:14px'></div><div class='section-title league-section-title'>Estadísticas del Cadete A</div>",
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
        st.markdown("<div class='cad-note'>" + " · ".join(
            f"<b style='color:var(--ink)'>{r.Campo}</b>: {r.PJ} PJ, {r.V}-{r.E}-{r.D}, {r.Puntos} pts, {r.GF}–{r.GC}" for r in df.itertuples())
            + "</div>", unsafe_allow_html=True)
    with t[2]:
        pa = lc.participation(mins, TEAM, MM, pj)
        st.markdown(f"<div class='q-title'>Participación de la plantilla</div><div class='q-sub'>% sobre {MM}' × {pj} partidos. "
                    f"Un partido completo = {MM}'; 40' = 50 %.</div>", unsafe_allow_html=True)
        st.markdown("<div class='pv-panel-title'><span>🧱</span>Quién sostiene</div>" + pt_viz.player_cards_html(
            [dict(name=r.jugador, value=int(r.minutos), tag=f"#{int(r.dorsal)}" if pd.notna(r.dorsal) else "",
                  sub=f"{int(r.titular)} tit. · {int(r.suplente)} supl. · {r.pct:.0f} %") for r in pa.itertuples()],
            accent=RIVAL, unit="min", limit=len(pa)), unsafe_allow_html=True)
        mt = mins[mins.equipo == TEAM].pivot_table(index="jugador", columns="jornada", values="minutos", aggfunc="sum").loc[pa.jugador]
        fig = go.Figure(go.Heatmap(z=mt.values, x=[f"J{c}" for c in mt.columns], y=mt.index, colorscale=[[0, TOKENS["surface-2"]], [1, PT]],
                                   zmin=0, zmax=MM, hovertemplate="%{y} · %{x}: %{z}′<extra></extra>", colorbar=dict(title="min")))
        _plot(fig, "cad_st_heat", h=120 + 22 * len(mt), title="Minutos por jornada", yaxis=dict(autorange="reversed"))
    with t[3]:
        sc = lc.scorers(ev, mins, TEAM)
        dec, dec_skip = pt_viz.decisive_goals(part, ev, TEAM, lambda e: lc.goal_side(e, TEAM))
        g1, g2 = st.columns(2, gap="medium")
        g1.markdown("<div class='pv-panel-title'><span>⚽</span>Quién marca</div><div class='pv-panel-sub'>Goles de las actas (sin propia puerta).</div>"
                    + pt_viz.player_cards_html([dict(name=r.jugador, value=int(r.goles),
                                                     sub=f"{r.minutos_gol} · {r.pct_equipo:.0f} % de los goles · {_fmt(r.goles_partido)} por partido jugado"
                                                     + (f" · {int(r.penaltis)} de penalti" if r.penaltis else ""))
                                                for r in sc.itertuples()], unit="goles", limit=len(sc)), unsafe_allow_html=True)
        g2.markdown("<div class='pv-panel-title'><span>🎯</span>Quién decide</div><div class='pv-panel-sub'>Goles que dieron puntos: el de la victoria "
                    "(deja la ventaja definitiva) y el último empate en partidos igualados.</div>"
                    + pt_viz.player_cards_html(pt_viz.decisive_items(dec), accent=POS, unit="decisivos", limit=len(dec),
                                               empty="Ningún gol decisivo con el orden de goles completo."), unsafe_allow_html=True)
        if dec_skip:
            g2.caption(f"{dec_skip} partido(s) sin el orden completo de goles en el acta no se analizan aquí.")
        g = ev[(ev.equipo == TEAM) & ev.tipo.isin(lc.GOAL_TYPES_FOR)].groupby("jornada").size().reindex(tm.jornada, fill_value=0).cumsum()
        fig = go.Figure(go.Scatter(x=[f"J{j}" for j in g.index], y=g.values, mode="lines+markers", line=dict(color=PT, width=2),
                                   marker=dict(size=8), hovertemplate="%{x}: %{y} goles acumulados<extra></extra>"))
        _plot(fig, "cad_st_gevo", title="Goles acumulados")
        st.markdown("<div class='cad-note'>Asistencias: las actas no las registran. No se muestran para no inventar datos.</div>", unsafe_allow_html=True)
    with t[4]:
        g, w = lc.goalkeepers(al, mins, ev, part, TEAM, MM)
        st.markdown(f"<div class='pv-panel-title'><span>🧤</span>Porteros</div><div class='pv-panel-sub'>Ordenados por minutos jugados · valor = goles encajados por {MM}' en el campo.</div>" + pt_viz.player_cards_html(
            [dict(name=r.jugador, value=round(float(r.encajados_por_partido_reglamentario), 2) if pd.notna(r.encajados_por_partido_reglamentario) else None,
                  sub=f"{int(r.minutos)}′ · {int(r.partidos)} PJ · {int(r.encajados)} GC · {int(r.porterias_cero)} a cero")
             for r in g.sort_values("minutos", ascending=False).itertuples()], accent=POS, unit=f"GC/{MM}'", value_fmt=lambda v: _fmt(v), limit=len(g), lower_is_better=True),
            unsafe_allow_html=True)
        with st.expander("Tabla completa de porteros"):
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
