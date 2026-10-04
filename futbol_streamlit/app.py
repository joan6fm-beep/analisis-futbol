import base64
import html
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Fútbol Data Joan",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent
DATA = BASE / "data"

@st.cache_data
def load_csv(name):
    p = DATA / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

equipos = load_csv("equipos_liga.csv")
plantillas = load_csv("plantillas_rivales.csv")
minutos = load_csv("minutos_rivales.csv")
partidos = load_csv("partidos_rivales.csv")
eventos = load_csv("eventos_rivales.csv")
clasificacion = load_csv("clasificacion_liga.csv")
alineaciones = load_csv("alineaciones_rivales.csv")

NAVY = "#062d5a"
BLUE = "#1d63d8"
ORANGE = "#f59e0b"
BG = "#f5f7fb"
TEXT = "#102a43"
MUTED = "#6b7c93"
RED = "#ef4444"
DGREEN = "#16a34a"

st.markdown(
    f"""
<style>
html, body, [class*="css"] {{font-family: Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}}
[data-testid="stAppViewContainer"] {{background:{BG};color:{TEXT};}}
[data-testid="stHeader"] {{background:transparent;}}
.block-container {{padding-top:.7rem;max-width:1540px;padding-bottom:3rem;}}
[data-testid="stSidebar"] {{background:#fff;border-right:1px solid #e6eaf0;}}
[data-testid="stSidebar"] .block-container {{padding-top:1rem;}}

.brand-box {{display:flex;align-items:center;gap:11px;background:{NAVY};color:white;border-radius:14px;padding:13px 14px;margin-bottom:14px;box-shadow:0 8px 24px rgba(6,45,90,.18)}}
.brand-ball {{width:38px;height:38px;border-radius:12px;background:{ORANGE};display:flex;align-items:center;justify-content:center;font-size:21px}}
.brand-main {{font-weight:900;line-height:1;font-size:1.05rem}} .brand-main span {{color:#ffd166}}
.brand-sub {{font-size:.73rem;opacity:.75;margin-top:4px}}
.side-label {{font-size:.76rem;font-weight:900;color:#6b7c93;text-transform:uppercase;letter-spacing:.04em;margin:.55rem 0 .2rem}}
.team-count {{font-size:.75rem;color:#7c8ea4;margin-top:.25rem}}

.topbar {{background:{NAVY};color:white;border-radius:15px;padding:15px 20px;margin-bottom:13px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 8px 20px rgba(6,45,90,.14)}}
.topbar .title {{font-size:1.05rem;font-weight:800}} .topbar .nav {{opacity:.82;font-size:.88rem}}
.team-head {{background:#fff;border:1px solid #e6eaf0;border-radius:16px;padding:18px 20px;display:flex;align-items:center;gap:18px;box-shadow:0 6px 20px rgba(16,42,67,.05)}}
.team-head img {{width:82px;height:82px;object-fit:contain;border-radius:12px}}
.team-name {{font-size:2rem;font-weight:900;color:{NAVY};line-height:1.05}}
.team-sub {{color:#406080;font-size:.96rem;margin-top:5px}}
.badge {{display:inline-block;background:#eef4ff;color:{BLUE};font-weight:800;border-radius:999px;padding:5px 10px;font-size:.78rem;margin-top:8px}}

.section-title {{font-size:1.08rem;font-weight:900;color:{NAVY};margin:.2rem 0 .65rem}}
.card {{background:#fff;border:1px solid #e6eaf0;border-radius:15px;padding:16px;box-shadow:0 5px 16px rgba(16,42,67,.045);height:100%}}
.kpi {{text-align:center;min-height:112px;display:flex;flex-direction:column;justify-content:center}}
.kpi .v {{font-size:1.78rem;font-weight:900;color:{NAVY};line-height:1}} .kpi .l {{font-size:.79rem;color:{MUTED};margin-top:8px;font-weight:700}} .kpi .s {{font-size:.72rem;color:#8b9bb0;margin-top:4px}}

.form-row {{display:grid;grid-template-columns:90px 1fr 80px;gap:10px;align-items:center;margin:12px 0;font-size:.83rem;font-weight:800}}
.bar {{height:12px;background:#edf1f5;border-radius:999px;overflow:hidden}} .fill {{height:100%;background:linear-gradient(90deg,{BLUE},#57a4ff);border-radius:999px}}
.match-row {{display:grid;grid-template-columns:40px 1fr 70px 14px;gap:9px;align-items:center;padding:9px 0;border-bottom:1px solid #edf0f4;font-size:.82rem}} .match-row:last-child {{border-bottom:0}} .jtag {{font-weight:900;color:{NAVY}}}
.dot {{width:10px;height:10px;border-radius:50%}}

.pitch {{position:relative;width:100%;aspect-ratio:1.42/1;background:linear-gradient(90deg,#21823d,#2d9849);border-radius:12px;overflow:hidden;border:3px solid #fff;box-shadow:inset 0 0 0 2px rgba(255,255,255,.7)}}
.pitch:before {{content:'';position:absolute;left:50%;top:0;bottom:0;border-left:2px solid rgba(255,255,255,.75)}}
.pitch:after {{content:'';position:absolute;width:18%;aspect-ratio:1;left:41%;top:40%;border:2px solid rgba(255,255,255,.75);border-radius:50%}}
.box-l,.box-r {{position:absolute;top:23%;height:54%;width:17%;border:2px solid rgba(255,255,255,.75)}} .box-l {{left:0;border-left:0}} .box-r {{right:0;border-right:0}}
.pchip {{position:absolute;transform:translate(-50%,-50%);text-align:center;color:white;font-size:.68rem;font-weight:800;text-shadow:0 1px 2px rgba(0,0,0,.35);min-width:58px}}
.shirt {{width:35px;height:31px;background:#fff;border:2px solid {NAVY};border-radius:8px 8px 5px 5px;color:{NAVY};display:flex;align-items:center;justify-content:center;margin:0 auto 3px;font-size:.83rem;font-weight:900;box-shadow:0 2px 5px rgba(0,0,0,.2)}}
.ppct {{font-size:.58rem;background:rgba(0,0,0,.28);border-radius:999px;padding:1px 5px;display:inline-block;margin-top:2px}}

.heat-wrap {{background:#fff;border:1px solid #e6eaf0;border-radius:15px;padding:13px;overflow:auto;box-shadow:0 5px 16px rgba(16,42,67,.045)}}
table.heat {{width:100%;border-collapse:separate;border-spacing:0;font-size:.77rem;min-width:980px}} table.heat th {{position:sticky;top:0;background:#f7f9fc;color:#4d6078;padding:8px 7px;border-bottom:1px solid #e7ebf0;text-align:center}} table.heat td {{padding:7px;border-bottom:1px solid #eef1f4;text-align:center}} table.heat td.name {{text-align:left;font-weight:700;color:{NAVY}}} table.heat td.num {{font-weight:900;color:{NAVY};width:34px}}
.m0 {{background:#fecaca}} .m1 {{background:#fdba74}} .m2 {{background:#fde68a}} .m3 {{background:#bbf7d0}} .m4 {{background:#4ade80;color:#073b1e;font-weight:900}} .mx {{background:#f1f5f9;color:#94a3b8}}
.mini-list {{display:flex;flex-direction:column;gap:9px}} .mini-item {{display:flex;justify-content:space-between;gap:10px;align-items:center;border-bottom:1px solid #eef1f4;padding-bottom:8px;font-size:.82rem}} .mini-item:last-child {{border:0}}
.note {{font-size:.78rem;color:{MUTED};margin-top:8px}}
.pending {{color:#94a3b8;font-weight:700}}
.goal-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(115px,1fr));gap:12px;align-items:stretch}}
.goal-bin {{background:#fff;border:1px solid #e6eaf0;border-radius:15px;padding:14px 8px;text-align:center;min-height:148px;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;box-shadow:0 5px 16px rgba(16,42,67,.045)}}
.goal-range {{font-size:.78rem;font-weight:900;color:{NAVY};margin-bottom:10px}}
.goal-bubble-wrap {{height:86px;display:flex;align-items:center;justify-content:center}}
.goal-bubble {{border-radius:50%;background:rgba(22,163,74,.88);color:white;display:flex;align-items:center;justify-content:center;font-weight:900;box-shadow:0 5px 14px rgba(22,163,74,.22)}}
.goal-bubble.against {{background:rgba(239,68,68,.9);box-shadow:0 5px 14px rgba(239,68,68,.2)}}
.goal-bubble.zero {{background:#e8edf3;color:#8292a8;box-shadow:none}}
.goal-pair {{height:88px;display:flex;align-items:center;justify-content:center;gap:10px}}
.goal-legend {{display:flex;gap:16px;align-items:center;font-size:.76rem;color:#6b7c93;margin:-2px 0 10px}}
.legend-dot {{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:5px}}
.goal-count {{font-size:.7rem;color:{MUTED};margin-top:7px;font-weight:700}}
[data-testid="stMetric"] {{background:#fff;border:1px solid #e6eaf0;border-radius:14px;padding:10px 13px;box-shadow:0 5px 16px rgba(16,42,67,.04)}}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------- Sidebar / menú desplegable de rivales ----------------
with st.sidebar:
    st.markdown(
        """<div class='brand-box'><div class='brand-ball'>⚽</div><div><div class='brand-main'>FÚTBOL DATA <span>JOAN</span></div><div class='brand-sub'>Temporada 2026/27</div></div></div>""",
        unsafe_allow_html=True,
    )
    modulo = st.radio("Navegación", ["Rivales", "Equipo", "Individual"], label_visibility="collapsed")

    seleccionado = None
    if modulo == "Rivales":
        st.markdown("<div class='side-label'>Rivales · 16 equipos</div>", unsafe_allow_html=True)
        lista = equipos.sort_values("orden")["equipo"].tolist() if not equipos.empty else []
        default_idx = lista.index("Bétera C.F. 'A'") if "Bétera C.F. 'A'" in lista else 0
        seleccionado = st.selectbox(
            "Selecciona rival",
            lista,
            index=default_idx,
            help="Elige cualquiera de los 16 equipos. Bétera y C.D. Acero ya tienen análisis J1–J4 cargado.",
        )
        st.markdown(f"<div class='team-count'>Equipo seleccionado: <b>{html.escape(seleccionado)}</b></div>", unsafe_allow_html=True)
        with st.expander("Ver los 16 equipos"):
            for _, row in equipos.sort_values("orden").iterrows():
                mark = "✅" if row.equipo == seleccionado else "•"
                st.write(f"{mark} {int(row.orden)}. {row.equipo}")

st.markdown(
    "<div class='topbar'><div class='title'>⚽ FÚTBOL DATA JOAN</div><div class='nav'>Inicio &nbsp;&nbsp; Nuestro equipo &nbsp;&nbsp; <b>Rivales</b> &nbsp;&nbsp; Competición &nbsp;&nbsp; Informes</div></div>",
    unsafe_allow_html=True,
)

if modulo != "Rivales":
    st.markdown(
        f"<div class='team-head'><div><div class='team-name'>{html.escape(modulo)}</div><div class='team-sub'>Este módulo se desarrollará después de completar la base de Rivales.</div></div></div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------- Helpers ----------------
def team_formations(team):
    tp = partidos[(partidos.local == team) | (partidos.visitante == team)].copy()
    arr = []
    for _, r in tp.sort_values("jornada").iterrows():
        f = r.sistema_local if r.local == team else r.sistema_visitante
        if pd.notna(f) and str(f).strip() and str(f) != "PENDIENTE":
            arr.append((int(r.jornada), str(f)))
    return arr


def team_score(row, team):
    if pd.isna(row.goles_local) or pd.isna(row.goles_visitante):
        opp = row.visitante if row.local == team else row.local
        return None, None, opp
    if row.local == team:
        return int(row.goles_local), int(row.goles_visitante), row.visitante
    return int(row.goles_visitante), int(row.goles_local), row.local


def minute_class(v):
    if pd.isna(v):
        return "mx"
    x = float(v)
    if x <= 20:
        return "m0"
    if x <= 45:
        return "m1"
    if x <= 60:
        return "m2"
    if x <= 75:
        return "m3"
    return "m4"


def short_name(name):
    bits = str(name).split()
    return bits[0] if bits else ""


def display_name(name, dorsal=None):
    # El dorsal 1 figura únicamente como "Alex" en las capturas FFCV aportadas.
    # No inventamos apellidos: lo marcamos como pendiente hasta disponer del nombre completo.
    if dorsal == 1 and str(name).strip() == "Alex":
        return "Alex (apellidos pendientes)"
    return str(name)


def name_with_number(name, dorsal):
    return f"{display_name(name, int(dorsal))} ({int(dorsal)})"


def image_html(path):
    if not path.exists():
        return "<div style='font-size:54px'>🛡️</div>"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"<img src='data:image/png;base64,{b64}'>"

# ---------------- Rival elegido ----------------
team_parts = partidos[(partidos.local == seleccionado) | (partidos.visitante == seleccionado)].copy()
roster = plantillas[plantillas.equipo == seleccionado].copy()
forms = team_formations(seleccionado)

if seleccionado == "Bétera C.F. 'A'":
    logo_path = BASE / "betera_logo.png"
elif seleccionado == "C.D. Acero 'A'":
    logo_path = BASE / "acero_logo.png"
elif seleccionado == "Primer Toque C.F. 'A'":
    logo_path = BASE / "primer_toque_logo.png"
else:
    logo_path = Path("__missing__")

st.markdown(
    f"""<div class='team-head'>{image_html(logo_path)}<div><div class='team-name'>{html.escape(seleccionado)}</div><div class='team-sub'>Lliga Comunitat Juvenil · Nord · Temporada 2026/27</div><span class='badge'>{'ANÁLISIS REAL J1–J4' if seleccionado in ["Bétera C.F. 'A'", "C.D. Acero 'A'"] else 'PERFIL PREPARADO · DATOS PENDIENTES'}</span></div></div>""",
    unsafe_allow_html=True,
)

# Perfiles ya desarrollados con jornadas completas.
analizados = ["Bétera C.F. 'A'", "C.D. Acero 'A'"]
if seleccionado not in analizados:
    st.info(
        "Este equipo ya está dentro del menú de Rivales. Todavía no hemos cargado sus actas y jornadas. "
        "Bétera C.F. y C.D. Acero son los primeros perfiles completos y sirven como plantilla para el resto."
    )
    st.markdown("### Próximo paso cuando carguemos este rival")
    st.write("Alineaciones por jornada · minutos · % titularidad · posible XI · sistemas · goles · tarjetas · cambios · casa/fuera.")
    st.stop()

# ---------------- Filtros del rival ----------------
st.markdown("<div class='note' style='margin:8px 0 6px'><b>Todos los paneles de la ficha responden al mismo filtro:</b> Total / Casa / Fuera y, opcionalmente, a una jornada concreta.</div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.1, 1, 1])
with c1:
    ambito = st.radio("Ámbito", ["Total", "Casa", "Fuera"], horizontal=True, index=0)
with c2:
    js_all = sorted(minutos.loc[minutos.equipo == seleccionado, "jornada"].dropna().astype(int).unique().tolist())
    jornada_sel = st.selectbox("Jornada", ["Total"] + [f"J{x}" for x in js_all])
with c3:
    st.selectbox("Temporada", ["2026/27"])

part = team_parts.copy()
if ambito == "Casa":
    part = part[part.local == seleccionado]
elif ambito == "Fuera":
    part = part[part.visitante == seleccionado]
if jornada_sel != "Total":
    part = part[part.jornada == int(jornada_sel[1:])]

m = minutos[minutos.equipo == seleccionado].copy()
if ambito != "Total":
    valid_js = []
    for _, r in team_parts.iterrows():
        if ambito == "Casa" and r.local == seleccionado:
            valid_js.append(int(r.jornada))
        if ambito == "Fuera" and r.visitante == seleccionado:
            valid_js.append(int(r.jornada))
    m = m[m.jornada.isin(valid_js)]
if jornada_sel != "Total":
    m = m[m.jornada == int(jornada_sel[1:])]

# Jornadas activas del filtro: todos los paneles inferiores usan exactamente el mismo ámbito.
scope_js = sorted(part.jornada.dropna().astype(int).unique().tolist()) if not part.empty else []
mm = minutos[(minutos.equipo == seleccionado) & (minutos.jornada.isin(scope_js))].copy()
al_scope = alineaciones[(alineaciones.equipo == seleccionado) & (alineaciones.jornada.isin(scope_js))].copy()
ev_scope = eventos[(eventos.equipo == seleccionado) & (eventos.jornada.isin(scope_js))].copy()

# ---------------- KPIs ----------------
stand = clasificacion[clasificacion.equipo == seleccionado].sort_values("jornada").tail(1)
pos, pts = "—", "—"
if not stand.empty:
    pos = f"{int(stand.iloc[0].posicion)}º"
    pts = str(int(stand.iloc[0].puntos))

scores = []
for _, r in part.sort_values("jornada").iterrows():
    gf, gc, opp = team_score(r, seleccionado)
    scores.append((gf, gc, opp, int(r.jornada), str(r.estado)))

known_scores = [(gf, gc) for gf, gc, _, _, _ in scores if gf is not None]
V = sum(gf > gc for gf, gc in known_scores)
E = sum(gf == gc for gf, gc in known_scores)
D = sum(gf < gc for gf, gc in known_scores)
GF = sum(gf for gf, _ in known_scores)
GC = sum(gc for _, gc in known_scores)

forms_scope = []
for _, r in part.sort_values("jornada").iterrows():
    f = r.sistema_local if r.local == seleccionado else r.sistema_visitante
    if pd.notna(f) and str(f).strip() and str(f) != "PENDIENTE":
        forms_scope.append((int(r.jornada), str(f)))
vc = pd.Series([f for _, f in forms_scope]).value_counts() if forms_scope else pd.Series(dtype=int)
main_form = vc.index[0] if len(vc) else "—"
main_pct = (vc.iloc[0] / len(forms_scope) * 100) if len(vc) else 0

cols = st.columns(6)
kpis = [
    (len(scope_js), "Jornadas del filtro", " · ".join(f"J{x}" for x in scope_js) if scope_js else "Sin jornadas"),
    (f"{V}-{E}-{D}", "V · E · D", "Victorias · Empates · Derrotas"),
    (GF if known_scores else "—", "Goles a favor", f"{len(scope_js)} jornadas" if scope_js else "Sin jornadas"),
    (GC if known_scores else "—", "Goles en contra", f"{len(scope_js)} jornadas" if scope_js else "Sin jornadas"),
    (main_form, "Sistema más usado", f"{main_pct:.0f}% ({int(vc.iloc[0]) if len(vc) else 0}/{len(forms_scope)})"),
    (pos, "Clasificación J5", f"{pts} puntos · 04/10/2026"),
]
for c, (v, l, s) in zip(cols, kpis):
    c.markdown(f"<div class='card kpi'><div class='v'>{v}</div><div class='l'>{l}</div><div class='s'>{s}</div></div>", unsafe_allow_html=True)

# Control de coherencia: el total de eventos de gol debe cuadrar con el marcador agregado.
_ev_gf = int((ev_scope.tipo == 'gol').sum()) if not ev_scope.empty else 0
_ev_gc = int((ev_scope.tipo == 'gol_contra').sum()) if not ev_scope.empty else 0
if known_scores and (_ev_gf != GF or _ev_gc != GC):
    st.warning(f"Revisión de datos: marcador agregado {GF}-{GC}, eventos cargados {_ev_gf}-{_ev_gc}. Hay que revisar algún minuto de gol.")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ---------------- Formaciones / partidos / posible XI ----------------
a, b, c = st.columns([1.05, .95, 1.35])
with a:
    rows = ""
    for form, count in vc.items():
        pct = count / len(forms_scope) * 100
        rows += f"<div class='form-row'><div>{form}</div><div class='bar'><div class='fill' style='width:{pct:.0f}%'></div></div><div>{pct:.0f}% ({count})</div></div>"
    st.markdown(
        f"<div class='card'><div class='section-title'>Formaciones utilizadas</div>{rows}<div class='note'>{' · '.join(f'J{j}: {f}' for j, f in forms_scope) if forms_scope else 'Sin formaciones para este filtro.'}</div></div>",
        unsafe_allow_html=True,
    )

with b:
    rows = ""
    for _, rr in part.sort_values("jornada").iterrows():
        j = int(rr.jornada)
        gf, gc, opp = team_score(rr, seleccionado)
        local_name = str(rr.local).replace(" 'A'", "").replace(" 'B'", "").replace(" 'C'", "")
        away_name = str(rr.visitante).replace(" 'A'", "").replace(" 'B'", "").replace(" 'C'", "")
        fixture = f"{local_name} - {away_name}"
        if pd.isna(rr.goles_local) or pd.isna(rr.goles_visitante):
            col = "#cbd5e1"
            result_html = "<span class='pending'>Pendiente</span>"
        else:
            gl, gv = int(rr.goles_local), int(rr.goles_visitante)
            col = DGREEN if gf > gc else ("#9ca3af" if gf == gc else RED)
            result_html = f"<b>{gl} - {gv}</b>"
        rows += f"<div class='match-row' style='grid-template-columns:40px 1fr 70px 14px'><div class='jtag'>J{j}</div><div>{html.escape(fixture)}</div><div>{result_html}</div><div class='dot' style='background:{col}'></div></div>"
    st.markdown(
        f"<div class='card'><div class='section-title'>Jornadas analizadas</div>{rows}</div>",
        unsafe_allow_html=True,
    )

with c:
    # XI dinámico: cambia con Total/Casa/Fuera y también con la jornada elegida.
    al = al_scope.copy()
    xi_m = mm.copy()
    njs = max(1, len(scope_js))
    starts = xi_m.groupby("dorsal")["titular"].sum() / njs * 100 if not xi_m.empty else pd.Series(dtype=float)
    recent_js = scope_js[-2:]
    recent = (
        xi_m[xi_m.jornada.isin(recent_js)].groupby("dorsal")["titular"].sum() / max(1, len(recent_js)) * 100
        if recent_js else pd.Series(dtype=float)
    )
    prob = (0.6 * starts.add(recent, fill_value=0) + 0.4 * recent.add(starts, fill_value=0)).fillna(0)
    # La fórmula anterior preserva la ponderación cuando un jugador solo aparece en una de las series.
    if not starts.empty:
        prob = (0.6 * starts.reindex(starts.index.union(recent.index), fill_value=0) +
                0.4 * recent.reindex(starts.index.union(recent.index), fill_value=0))

    rc = al.groupby(["rol", "dorsal", "jugador"]).size().reset_index(name="n") if not al.empty else pd.DataFrame(columns=["rol","dorsal","jugador","n"])
    rc["prob"] = rc.dorsal.map(prob).fillna(0) if not rc.empty else pd.Series(dtype=float)

    # El sistema del XI se adapta al sistema más usado dentro del filtro.
    system_for_xi = main_form if main_form != "—" else "1-4-3-3"
    try:
        nums = [int(x) for x in system_for_xi.split("-") if x.isdigit()]
        outfield = nums[1:] if nums and nums[0] == 1 else nums
    except Exception:
        outfield = [4, 3, 3]
    if len(outfield) != 3:
        outfield = [4, 3, 3]
    needs = {"POR": 1, "DEF": outfield[0], "MED": outfield[1], "ATA": outfield[2]}

    selected = []
    for role, n in needs.items():
        selected += rc[rc.rol == role].sort_values(["n", "prob"], ascending=False).head(n).to_dict("records")

    def line_coords(x, n):
        if n <= 1:
            ys = [50]
        else:
            ys = [18 + i * (64 / (n - 1)) for i in range(n)]
        return [(x, y) for y in ys]

    # Sentido correcto: portero dentro del área izquierda y equipo atacando hacia la derecha.
    coords = {
        "POR": line_coords(7, 1),
        "DEF": line_coords(27, needs["DEF"]),
        "MED": line_coords(51, needs["MED"]),
        "ATA": line_coords(78, needs["ATA"]),
    }
    used = {k: 0 for k in coords}
    chips = []
    for r in selected:
        role = r["rol"]
        i = used[role]
        if i >= len(coords[role]):
            continue
        used[role] += 1
        x, y = coords[role][i]
        player_label = display_name(r["jugador"], int(r["dorsal"]))
        chips.append(
            f"<div class='pchip' style='left:{x}%;top:{y}%'><div class='shirt'>{int(r['dorsal'])}</div>{html.escape(short_name(player_label))}<br><span class='ppct'>{float(r['prob']):.0f}%</span></div>"
        )
    pitch = "<div class='pitch'><div class='box-l'></div><div class='box-r'></div>" + "".join(chips) + "</div>"
    filter_label = ambito if jornada_sel == "Total" else f"{ambito} · {jornada_sel}"
    st.markdown(
        f"<div class='card'><div class='section-title'>Posible XI · {system_for_xi} · {filter_label}</div>{pitch}<div class='note'>El XI se recalcula automáticamente al cambiar Total/Casa/Fuera. Portero en su área y ataque hacia la derecha.</div></div>",
        unsafe_allow_html=True,
    )

# ---------------- Tabla de minutos ----------------
st.markdown("<div style='height:10px'></div><div class='section-title'>Jugadores · minutos por jornada, peso competitivo y titularidad</div>", unsafe_allow_html=True)

js = sorted(m.jornada.astype(int).unique()) if not m.empty else []
table = roster[["dorsal", "jugador"]].copy()
for j in js:
    d = m[m.jornada == j][["dorsal", "minutos"]].rename(columns={"minutos": f"J{j}"})
    table = table.merge(d, on="dorsal", how="left")

jcols = [f"J{j}" for j in js]
if jcols:
    table["Total"] = table[jcols].sum(axis=1, skipna=True)
    avail = 90 * len(js)
    table["% min"] = (table.Total / avail * 100).round(0)
    starts_m = m.groupby("dorsal")["titular"].sum()
    table["% tit"] = (table.dorsal.map(starts_m).fillna(0) / max(1, len(js)) * 100).round(0)
    recent_js = js[-2:]
    recent_m = m[m.jornada.isin(recent_js)].groupby("dorsal")["titular"].sum()
    recent_pct = table.dorsal.map(recent_m).fillna(0) / max(1, len(recent_js)) * 100
    table["Prob. XI"] = (0.60 * table["% tit"] + 0.40 * recent_pct).round(0)

    evg = ev_scope[ev_scope.tipo == "gol"].groupby("jugador").size()
    eva = ev_scope[ev_scope.tipo == "amarilla"].groupby("jugador").size()
    evr = ev_scope[ev_scope.tipo == "roja"].groupby("jugador").size()
    table["G"] = table.jugador.map(evg).fillna(0).astype(int)
    table["🟨"] = table.jugador.map(eva).fillna(0).astype(int)
    table["🟥"] = table.jugador.map(evr).fillna(0).astype(int)
    table = table.sort_values(["Total", "% tit", "dorsal"], ascending=[False, False, True]).reset_index(drop=True)

    head = "<tr><th>#</th><th style='text-align:left'>Jugador</th>" + "".join(f"<th>{x}</th>" for x in jcols) + "<th>Total</th><th>% min</th><th>% tit</th><th>Prob. XI</th><th>G</th><th>🟨</th><th>🟥</th></tr>"
    body = []
    for _, r in table.iterrows():
        cells = "".join(f"<td class='{minute_class(r[x])}'>{'—' if pd.isna(r[x]) else int(r[x])}</td>" for x in jcols)
        body.append(
            f"<tr><td class='num'>{int(r.dorsal)}</td><td class='name'>{html.escape(display_name(r.jugador, int(r.dorsal)))}</td>{cells}<td><b>{int(r.Total)}</b></td><td>{int(r['% min'])}%</td><td>{int(r['% tit'])}%</td><td><b>{int(r['Prob. XI'])}%</b></td><td>{int(r.G)}</td><td>{int(r['🟨'])}</td><td>{int(r['🟥'])}</td></tr>"
        )
    st.markdown(
        f"<div class='heat-wrap'><table class='heat'>{head}{''.join(body)}</table><div class='note'>Colores: 0–20 rojo · 21–45 naranja · 46–60 amarillo · 61–75 verde claro · 76–90 verde oscuro.</div></div>",
        unsafe_allow_html=True,
    )
else:
    st.info("Sin minutos cargados para este filtro.")

# ---------------- Goles, disciplina, núcleo del XI y carga ----------------
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
d1, d2, d3, d4 = st.columns(4)

with d1:
    ev = ev_scope[ev_scope.tipo == "gol"]
    vcg = ev.jugador.value_counts()
    dorsal_map = roster.set_index("jugador")["dorsal"].to_dict()
    items = "".join(
        f"<div class='mini-item'><span>⚽ {html.escape(name_with_number(n, dorsal_map.get(n, 0)))}</span><b>{int(v)}</b></div>"
        if dorsal_map.get(n) else f"<div class='mini-item'><span>⚽ {html.escape(str(n))}</span><b>{int(v)}</b></div>"
        for n, v in vcg.items()
    ) or "<div class='note'>Sin goles cargados para este filtro</div>"
    st.markdown(f"<div class='card'><div class='section-title'>Goleadores registrados</div><div class='mini-list'>{items}</div></div>", unsafe_allow_html=True)

with d2:
    ea = ev_scope[ev_scope.tipo == "amarilla"].jugador.value_counts()
    er = ev_scope[ev_scope.tipo == "roja"].jugador.value_counts()
    def discipline_items(series, icon):
        out = []
        for n, v in series.items():
            dorsal = dorsal_map.get(n)
            label = name_with_number(n, dorsal) if dorsal else str(n)
            out.append(f"<div class='mini-item'><span>{icon} {html.escape(label)}</span><b>{int(v)}</b></div>")
        return "".join(out)
    items = discipline_items(ea, "🟨") + discipline_items(er, "🟥")
    if not items:
        items = "<div class='note'>Sin tarjetas para este filtro</div>"
    st.markdown(f"<div class='card'><div class='section-title'>Disciplina</div><div class='mini-list'>{items}</div></div>", unsafe_allow_html=True)

with d3:
    # Más útil que el banquillo: identifica el núcleo que el entrenador repite de inicio.
    if not mm.empty:
        core = mm.groupby(["dorsal", "jugador"]).agg(Titularidades=("titular", "sum"), Partidos=("jornada", "nunique")).reset_index()
        core["pct"] = core["Titularidades"] / max(1, len(scope_js)) * 100
        core = core.sort_values(["pct", "Titularidades", "dorsal"], ascending=[False, False, True]).head(7)
        items = "".join(
            f"<div class='mini-item'><span>⭐ {html.escape(name_with_number(r.jugador, r.dorsal))}</span><b>{r.pct:.0f}% tit.</b></div>"
            for _, r in core.iterrows()
        )
    else:
        items = "<div class='note'>Sin datos para este filtro</div>"
    st.markdown(f"<div class='card'><div class='section-title'>Núcleo del XI</div><div class='mini-list'>{items}</div></div>", unsafe_allow_html=True)

with d4:
    players = int(mm[mm.minutos > 0].dorsal.nunique()) if not mm.empty else 0
    st.markdown(
        f"<div class='card'><div class='section-title'>Carga competitiva</div><div class='kpi' style='min-height:125px'><div class='v'>{players}</div><div class='l'>Jugadores utilizados</div><div class='s'>{html.escape(ambito)}{' · ' + html.escape(jornada_sel) if jornada_sel != 'Total' else ''}</div></div></div>",
        unsafe_allow_html=True,
    )

# ---------------- Conversión de gol por jugador ----------------
st.markdown("<div style='height:10px'></div><div class='section-title'>Conversión de gol por jugador</div>", unsafe_allow_html=True)

# Solo jugadores del equipo seleccionado que han marcado. Los autogoles no cuentan como goleador propio.
scorer_goals = ev_scope[(ev_scope.tipo == "gol") & (~ev_scope.jugador.isin(["Autogol rival", "G.P."]))].groupby("jugador").size().reset_index(name="goles")
if not scorer_goals.empty and not mm.empty:
    mins_player = mm.groupby("jugador", as_index=False)["minutos"].sum()
    conv = scorer_goals.merge(mins_player, on="jugador", how="left")
    conv = conv[conv.minutos.fillna(0) > 0].copy()
    if not conv.empty:
        dorsal_map = roster.set_index("jugador")["dorsal"].to_dict()
        conv["Jugador"] = conv["jugador"].apply(lambda n: name_with_number(n, dorsal_map.get(n, 0)) if dorsal_map.get(n) else str(n))
        conv["Goles / 90"] = (conv["goles"] / conv["minutos"] * 90).round(2)
        conv["Minutos por gol"] = (conv["minutos"] / conv["goles"]).round(0)
        conv = conv.sort_values(["Goles / 90", "goles"], ascending=[False, False])
        # Gráfico nativo de Streamlit: evita problemas de validación de esquemas Altair en despliegues cloud.
        chart_df = conv.set_index("Jugador")[["Goles / 90"]]
        st.bar_chart(chart_df, use_container_width=True, height=250)
        st.dataframe(conv[["Jugador", "goles", "minutos", "Goles / 90", "Minutos por gol"]], use_container_width=True, hide_index=True)
        st.markdown("<div class='note'>La altura de la barra expresa los goles por 90 minutos. La tabla muestra también goles, minutos y minutos por gol.</div>", unsafe_allow_html=True)
    else:
        st.info("No hay goleadores con minutos registrados para este filtro.")
else:
    st.info("No hay goleadores registrados para este filtro.")

# ---------------- Goles por tramo ----------------
st.markdown("<div style='height:10px'></div><div class='section-title'>Distribución de goles por minuto · A favor y en contra</div>", unsafe_allow_html=True)
st.markdown("<div class='goal-legend'><span><span class='legend-dot' style='background:#16a34a'></span>A favor</span><span><span class='legend-dot' style='background:#ef4444'></span>En contra</span></div>", unsafe_allow_html=True)

goals_for = ev_scope[ev_scope.tipo == "gol"].copy()
goals_against = ev_scope[ev_scope.tipo == "gol_contra"].copy()
bins = [(0, 15), (15, 30), (30, 45), (45, 60), (60, 75), (75, 90)]

def count_bins(df):
    vals = []
    for lo, hi in bins:
        if lo == 0:
            n = int(((df.minuto >= lo) & (df.minuto <= hi)).sum())
        else:
            n = int(((df.minuto > lo) & (df.minuto <= hi)).sum())
        vals.append(n)
    return vals

counts_for = count_bins(goals_for)
counts_against = count_bins(goals_against)
max_goals = max(counts_for + counts_against) if (counts_for or counts_against) else 0
blocks = []
for (lo, hi), gf, gc in zip(bins, counts_for, counts_against):
    def bubble(n, against=False):
        if n == 0:
            size = 32
            klass = "goal-bubble zero"
        else:
            size = 36 + (44 * n / max(1, max_goals))
            klass = "goal-bubble against" if against else "goal-bubble"
        return f"<div class='{klass}' style='width:{size:.0f}px;height:{size:.0f}px'>{n}</div>"
    blocks.append(
        f"<div class='goal-bin'><div class='goal-range'>{lo}–{hi}'</div>"
        f"<div class='goal-pair'>{bubble(gf)}{bubble(gc, True)}</div>"
        f"<div class='goal-count'><span style='color:#15803d;font-weight:800'>{gf} GF</span> · <span style='color:#dc2626;font-weight:800'>{gc} GC</span></div></div>"
    )
st.markdown("<div class='goal-grid'>" + "".join(blocks) + "</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='note'>Verde = goles a favor · rojo = goles en contra. El tamaño de cada círculo aumenta con el número de goles. El bloque responde a Total/Casa/Fuera y a la jornada seleccionada.</div>",
    unsafe_allow_html=True,
)

# Los círculos rojos de FFCV en el lado del propio equipo se guardan como G.P. (gol en propia), nunca como goleador rival.
gp_count = int(((ev_scope.tipo == "gol_contra") & (ev_scope.jugador == "G.P.")).sum()) if not ev_scope.empty else 0
if gp_count:
    st.markdown(f"<div class='note'><b>G.P.</b> · goles en propia registrados en este filtro: {gp_count}.</div>", unsafe_allow_html=True)

# ---------------- Evolución de la clasificación ----------------
st.markdown("<div style='height:14px'></div><div class='section-title'>Evolución de la clasificación · J1–J4</div>", unsafe_allow_html=True)

evo = clasificacion[clasificacion.jornada.isin([1, 2, 3, 4])].copy()
if evo.empty:
    st.info("Sin clasificación histórica cargada.")
else:
    evo["Jornada"] = "J" + evo.jornada.astype(int).astype(str)
    pivot = evo.pivot_table(index="Jornada", columns="equipo", values="posicion", aggfunc="first").reindex(["J1", "J2", "J3", "J4"])
    # Usamos gráfico nativo por compatibilidad. Debajo se destaca explícitamente la secuencia del rival seleccionado.
    st.line_chart(pivot, use_container_width=True, height=390)
    sel = evo[evo.equipo == seleccionado].sort_values("jornada")
    if not sel.empty:
        seq = " → ".join(f"J{int(r.jornada)}: {int(r.posicion)}º" for _, r in sel.iterrows())
        accent = "#16a34a" if seleccionado == "Bétera C.F. 'A'" else ("#b91c1c" if seleccionado == "C.D. Acero 'A'" else "#1d63d8")
        st.markdown(f"<div class='card' style='border-left:6px solid {accent};margin-top:8px'><b>{html.escape(seleccionado)}</b> · {seq}</div>", unsafe_allow_html=True)
        st.markdown("<div class='note'>El gráfico compara los 16 equipos. La tarjeta inferior deja resaltada la evolución exacta del rival seleccionado.</div>", unsafe_allow_html=True)

st.caption("V12.1 · Bétera y C.D. Acero con el mismo motor completo: Total/Casa/Fuera, jornadas, minutos, XI, goleadores, disciplina, goles por tramo y evolución.")
