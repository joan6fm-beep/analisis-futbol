"""Sistema de diseño de Primer Toque: tokens, capa CSS global y plantilla de gráficos.

Todos los colores de la app se expresan con estas variables CSS (--surface, --ink,
--muted, --pt, --rival...). Para cambiar la identidad visual basta con tocar TOKENS.
"""
import streamlit as st

TOKENS = {
    "bg": "#0A0E14",          # fondo de la aplicación
    "surface": "#111722",     # tarjetas y paneles
    "surface-2": "#18202E",   # pistas de barras, filas alternas, chips
    "surface-3": "#202A3B",   # hover y elementos elevados
    "line": "#263247",        # bordes
    "line-soft": "#1C2535",   # separadores internos
    "ink": "#F2F5FA",         # texto principal
    "text": "#C8D1DE",        # texto secundario
    "muted": "#8A97AB",       # etiquetas y notas
    "pt": "#F5871F",          # Primer Toque / dato favorable
    "pt-soft": "rgba(245,135,31,.14)",
    "rival": "#6F93C6",       # rival / referencia
    "rival-soft": "rgba(111,147,198,.16)",
    "pos": "#2BC48A",         # positivo
    "neg": "#F0596A",         # negativo
    "warn": "#F2C14E",        # aviso / amarilla
    "navy": "#0E2B4F",        # azul corporativo
}

ROOT_CSS = ":root{" + "".join(f"--{k}:{v};" for k, v in TOKENS.items()) + "}"

# Secuencias para gráficos (Plotly / Altair). PT siempre naranja, rival siempre azul acero.
PT, RIVAL, POS, NEG, MUTED, INK, LINE = (TOKENS[k] for k in ("pt", "rival", "pos", "neg", "muted", "ink", "line"))
FONT = "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"

GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
__ROOT__
html, body, .stApp, [class*="css"], .stMarkdown, button, input, select, textarea {font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif!important;font-feature-settings:"tnum" 1,"cv11" 1}
.stApp, [data-testid="stAppViewContainer"] {background:var(--bg)!important;color:var(--text)}
.stApp [data-testid="stHeader"] {background:rgba(10,14,20,.72)!important;backdrop-filter:blur(10px)}
.stApp .block-container {max-width:1480px;padding-top:1rem}
.stApp h1,.stApp h2,.stApp h3,.stApp h4 {color:var(--ink);letter-spacing:-.02em}
.stApp a {color:var(--pt)}
.stApp hr {border-color:var(--line)}
::-webkit-scrollbar {width:9px;height:9px} ::-webkit-scrollbar-thumb {background:var(--surface-3);border-radius:9px} ::-webkit-scrollbar-track {background:transparent}

/* ---------- Barra lateral ---------- */
.stApp [data-testid="stSidebar"] {background:#0C1119!important;border-right:1px solid var(--line-soft)!important}
.stApp .brand-box {background:var(--surface)!important;border:1px solid var(--line)!important;box-shadow:none!important;border-radius:16px!important}
.stApp .brand-box:after {display:none}
.stApp .brand-kicker {color:var(--muted)!important}
.stApp .brand-main {color:var(--ink)!important}
.stApp .brand-sub {color:var(--text)!important;opacity:1!important}
.stApp .brand-chip {background:var(--pt-soft)!important;border-color:rgba(245,135,31,.45)!important;color:var(--pt)!important}
.stApp .side-nav-v3 a {background:transparent!important;border:1px solid transparent!important;box-shadow:none!important;color:var(--text)!important;min-height:42px!important;font-weight:650!important}
.stApp .side-nav-v3 a:hover {background:var(--surface)!important;border-color:var(--line-soft)!important;transform:none!important}
.stApp .side-nav-v3 a.active {background:var(--surface)!important;border-color:var(--line)!important;color:var(--ink)!important;box-shadow:inset 3px 0 0 var(--pt)!important}
.stApp .side-nav-v3 .sni {background:var(--surface-2)!important;color:var(--muted)!important}
.stApp .side-nav-v3 a.active .sni {background:var(--pt)!important;color:#1A0E02!important}
.stApp .side-label {color:var(--muted)!important}

/* ---------- Barra superior ---------- */
.stApp .topbar {background:var(--surface)!important;border:1px solid var(--line)!important;box-shadow:none!important;border-radius:14px!important;padding:12px 18px!important}
.stApp .topbar .title {color:var(--ink);font-weight:800;letter-spacing:.04em;font-size:.86rem!important}
.stApp .topbar .nav {color:var(--muted);font-size:.78rem!important;opacity:1!important;display:flex!important;align-items:center;gap:10px}
.stApp .topbar .title {display:flex;align-items:center;gap:10px;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.stApp .topbar .tb-home {color:var(--muted)!important;text-decoration:none!important;font-weight:700;letter-spacing:0;padding:4px 10px;border:1px solid var(--line);border-radius:999px}
.stApp .topbar .tb-home:hover {color:var(--ink)!important;border-color:var(--pt)}
.stApp .topbar .tb-crumb {color:var(--muted);font-weight:700;letter-spacing:0}
.stApp .topbar .tb-sep {color:var(--line)}
.stApp .topbar .tb-current {color:var(--ink);font-weight:800;letter-spacing:0;overflow:hidden;text-overflow:ellipsis}
.stApp .topbar .tb-chip {background:var(--pt-soft);color:var(--pt);border:1px solid rgba(245,135,31,.4);border-radius:999px;padding:4px 10px;font-weight:800;font-size:.7rem}
.stApp .topbar .tb-ver {color:var(--muted);font-size:.7rem}
@media (max-width:768px){.stApp .topbar .nav{display:none!important}.stApp .topbar .tb-home{padding:3px 8px}}

/* ---------- Cabeceras de sección (hero) ---------- */
.stApp .t360-hero,.stApp .league-hero,.stApp .tracking-hero,.stApp .ind-hero,.stApp .wall-hero,.stApp .cal-hero,
.stApp .player-detail-hero {background:linear-gradient(180deg,#141C2A 0%,#101620 100%)!important;border:1px solid var(--line)!important;
  box-shadow:inset 0 2px 0 var(--pt)!important;color:var(--ink)!important}
.stApp .league-badge {background:var(--surface-2)!important;border-color:var(--line)!important;color:var(--text)!important}
.stApp .tracking-kicker,.stApp .league-eyebrow {color:var(--pt)!important;opacity:1!important}

/* ---------- Tarjetas ---------- */
.stApp .card,.stApp .t360-card,.stApp .league-kpi,.stApp .t360-kpi,.stApp .ind-panel,.stApp .metric-panel,.stApp .venue-kpi,
.stApp .goal-bin,.stApp .goal-macro,.stApp .goaltype-card,.stApp .goal-diff-card,.stApp .match-link-card,.stApp .heat-wrap,
.stApp .league-highlight,.stApp .discipline-card,.stApp .goal-time-card,.stApp .report-card,.stApp .ps-card,.stApp .phys-card,
.stApp .pro84-match,.stApp .v83-panel,.stApp .v83-compare,.stApp .team-head,.stApp .video-callout,.stApp .goal-detail-wrap {
  box-shadow:none!important;border-color:var(--line)!important}
.stApp .goal-macro.blue,.stApp .goal-macro.green,.stApp .goal-macro.red,.stApp .goal-macro.purple,.stApp .goal-macro.pink {background:var(--surface)!important}
.stApp .goal-macro.blue {box-shadow:inset 0 2px 0 var(--rival)!important}.stApp .goal-macro.green {box-shadow:inset 0 2px 0 var(--pos)!important}
.stApp .goal-macro.red {box-shadow:inset 0 2px 0 var(--neg)!important}.stApp .goal-macro.purple {box-shadow:inset 0 2px 0 #9B87F5!important}.stApp .goal-macro.pink {box-shadow:inset 0 2px 0 #E879B9!important}
.stApp .league-kpi.featured {background:var(--surface)!important;box-shadow:inset 0 2px 0 var(--pt)!important}
.stApp .player-card-v3 {background:linear-gradient(160deg,#162034 0%,#111722 100%)!important;border:1px solid var(--line)!important;box-shadow:none!important}
.stApp .player-card-v3:hover {border-color:rgba(245,135,31,.55)!important}
.stApp .pc-pos,.stApp .ind-hero .pos {background:var(--pt-soft)!important;color:var(--pt)!important;border:1px solid rgba(245,135,31,.4)}
.stApp .section-title,.stApp .t360-title,.stApp .league-subrank-title,.stApp .ind-title,.stApp .panel-title {color:var(--ink)!important;letter-spacing:-.01em}
.stApp .video-callout {border-left-color:var(--neg)!important}
.stApp .video-link,.stApp .match-link-card a {background:var(--pt)!important;color:#1A0E02!important}

.stApp .badge {background:var(--pt-soft)!important;color:var(--pt)!important;border:1px solid rgba(245,135,31,.4)}
.stApp .match-row .fx {display:flex;flex-direction:column;gap:2px;min-width:0;font-size:.76rem;color:var(--muted);line-height:1.2}
.stApp .match-row .fx span {white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.stApp .match-row .fx b {color:var(--ink)}
.stApp .res-pill {width:22px;height:22px;border-radius:7px;display:grid;place-items:center;font-size:.66rem;font-weight:900;color:#0A0E14}
/* ---------- Tablas ---------- */
.stApp table {color:var(--text)}
.stApp table.heat th,.stApp .ranking-scroll thead th,.stApp table.goal-detail th,.stApp .t360-table th,.stApp .player-table th {background:var(--surface-2)!important;color:var(--muted)!important}
.stApp table.heat td {border-bottom-color:var(--line-soft)!important}
.stApp .main-standings tbody tr:nth-child(even) {background:rgba(255,255,255,.015)!important}
.stApp .main-standings tbody tr:hover,.stApp .performance-table tbody tr:hover {background:var(--surface-3)!important}
.stApp .main-standings .pts-cell,.stApp .performance-table .pts-cell,.stApp .pts-cell {background:var(--pt-soft)!important;color:var(--ink)!important}
.stApp .main-standings .stat-num,.stApp .performance-table .stat-num {color:var(--ink)!important}
.stApp .top-pos {background:rgba(43,196,138,.12)!important;color:var(--pos)!important}
.stApp .danger-pos {background:rgba(240,89,106,.12)!important;color:var(--neg)!important}
.stApp .positive {color:var(--pos)!important}.stApp .negative {color:var(--neg)!important}
/* Mapa de minutos: misma semántica que su leyenda (0–20 rojo … 76–90 verde oscuro), adaptada a fondo oscuro */
.stApp .m0 {background:rgba(240,89,106,.22)!important;color:#F7A1AB!important}
.stApp .m1 {background:rgba(245,135,31,.24)!important;color:#F9BE86!important}
.stApp .m2 {background:rgba(242,193,78,.24)!important;color:#F6D78C!important}
.stApp .m3 {background:rgba(43,196,138,.22)!important;color:#8FE3C0!important}
.stApp .m4 {background:rgba(43,196,138,.62)!important;color:#04241A!important;font-weight:900}
.stApp .mx {background:transparent!important;color:#4F5B6E!important}
.stApp table.heat th.j1,.stApp table.heat th.j2,.stApp table.heat th.j3,.stApp table.heat th.j4,.stApp table.heat th.j5 {color:var(--ink)!important}

/* ---------- Widgets nativos ---------- */
.stApp [data-testid="stMetric"] {background:var(--surface)!important;border:1px solid var(--line)!important;box-shadow:none!important;border-radius:14px}
.stApp [data-testid="stMetricValue"] {color:var(--ink)}
.stApp [data-testid="stMetricLabel"] p {color:var(--muted)!important;font-weight:650}
.stApp [data-testid="stExpander"] details {background:var(--surface);border-color:var(--line)!important;border-radius:14px}
.stApp [data-testid="stTabs"] button[aria-selected="true"] p {color:var(--pt)!important}
.stApp [data-baseweb="tab-highlight"] {background:var(--pt)!important}
.stApp [data-testid="stCaptionContainer"] {color:var(--muted)!important}
.stApp [data-testid="stAlert"] {background:var(--surface)!important;border:1px solid var(--line)!important;color:var(--text)!important}
.stApp .stDownloadButton button,.stApp .stButton button[kind="primary"] {background:var(--pt)!important;color:#1A0E02!important;border:0!important;font-weight:800!important}
.stApp .stButton button[kind="secondary"] {background:var(--surface)!important;border:1px solid var(--line)!important;color:var(--ink)!important}

/* ---------- Escudos sobre fondo oscuro ---------- */
.stApp img[alt][src^="data:image"].team-logo,.stApp .rival-list-row img,.stApp .t360-opp img,.stApp .match-team img,.stApp .rank-team img,
.stApp .mobile-rival-chip img,.stApp .hi-team img,.stApp .team-col img {background:#fff;border-radius:50%;padding:2px;box-sizing:border-box}

/* ---------- Navegación móvil ---------- */
@media (max-width:768px){
  .stApp [data-testid="stHeader"] {background:rgba(10,14,20,.9)!important}
  .stApp .mobile-bottom-nav {background:rgba(17,23,34,.96)!important;border-color:var(--line)!important;box-shadow:0 10px 30px rgba(0,0,0,.45)!important}
  .stApp .mobile-bottom-nav a {color:var(--muted)!important}
  .stApp .mobile-bottom-nav a.active {background:var(--pt-soft)!important;color:var(--pt)!important;box-shadow:inset 0 -2px 0 var(--pt)!important}
  .stApp .mobile-rival-chip {background:var(--surface)!important;border-color:var(--line)!important;color:var(--text)!important}
  .stApp .mobile-rival-chip.active {background:var(--pt)!important;color:#1A0E02!important;border-color:var(--pt)!important}
  .stApp .mobile-install-note {background:var(--surface)!important;border:1px solid var(--line);box-shadow:none!important}
}
""".replace("__ROOT__", ROOT_CSS)


def inject():
    """Inyecta tokens y capa global. Llamar una vez, al inicio del script."""
    st.markdown(f"<style>{GLOBAL_CSS}</style>", unsafe_allow_html=True)


def plotly_layout(**overrides):
    """Layout base de Plotly coherente con el tema (fondo transparente, tipografía, rejilla)."""
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=TOKENS["text"], size=12),
        margin=dict(l=12, r=12, t=36, b=12),
        hoverlabel=dict(bgcolor=TOKENS["surface-3"], bordercolor=TOKENS["line"], font=dict(family=FONT, color=TOKENS["ink"], size=12)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)", font=dict(color=TOKENS["text"])),
        xaxis=dict(automargin=True, gridcolor=TOKENS["line-soft"], zerolinecolor=TOKENS["line"], linecolor=TOKENS["line"], tickfont=dict(color=TOKENS["muted"], size=11)),
        yaxis=dict(automargin=True, gridcolor=TOKENS["line-soft"], zerolinecolor=TOKENS["line"], linecolor=TOKENS["line"], tickfont=dict(color=TOKENS["muted"], size=11)),
    )
    base.update(overrides)
    return base


PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}
