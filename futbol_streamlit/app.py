import base64
import html

def _safe_html(value, quote=True):
    """Escapa valores para HTML de forma segura."""
    if value is None:
        value = ""
    return html.escape(str(value), quote=quote)


from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Temporada 2026/2027",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent
DATA = BASE / "data"

MATCH_LINKS = {
    # Villarreal
    ("Villarreal C.F. 'C'", 1): "https://youtu.be/45hlhA5vbIc",
    ("Villarreal C.F. 'C'", 2): "https://app.veo.co/matches/20260912-partido-12-sept-2026-v2488402/",
    ("Villarreal C.F. 'C'", 3): "https://app.veo.co/matches/20260920-juvenil-a-vs-villareal-cf-v78c4164/",
    ("Villarreal C.F. 'C'", 4): "https://youtu.be/rUAjYCPcnrI",

    # Primer Toque
    ("Primer Toque C.F. 'A'", 1): "https://app.veo.co/matches/20260906-juvenil-vs-primer-toque-v69cf952/",
    ("Primer Toque C.F. 'A'", 2): "https://app.veo.co/matches/20260912-juvenil-a-betera-ve022cb5/",
    ("Primer Toque C.F. 'A'", 3): "https://app.veo.co/matches/20260919-juvenil-a-manises-v678eca9/",
    ("Primer Toque C.F. 'A'", 4): "https://app.veo.co/matches/20260927-partido-cdf-canet-vae71aeb",
    ("Primer Toque C.F. 'A'", 5): "https://app.veo.co/matches/20261003-juvenil-a-alboraya-v1bf5286/",

    # Bétera
    ("Bétera C.F. 'A'", 1): "https://app.veo.co/matches/20260906-juvenil-a-vs-col-salgui-v9022f29/",
    ("Bétera C.F. 'A'", 2): "https://app.veo.co/matches/20260912-juvenil-a-betera-ve022cb5/",
    ("Bétera C.F. 'A'", 3): "https://app.veo.co/matches/20260920-juvenil-a-vs-villareal-cf-v78c4164/",
    ("Bétera C.F. 'A'", 4): "https://youtu.be/FwkojfoAnAs?is=a3cp8o-yYGS8kTXm",

    # C.D. Acero
    ("C.D. Acero 'A'", 1): "https://app.veo.co/matches/20260906-patacona-cf-jb-vs-acero-v97c8cc3/",
    ("C.D. Acero 'A'", 2): "https://app.veo.co/matches/20260913-untitled-recording-2026-09-13_17-14-50-va669c7b",
    ("C.D. Acero 'A'", 3): "https://app.veo.co/matches/20260919-juvenil-a-b-vs-ja-cd-acero-v3e5feb3/#t=05:45",
    ("C.D. Acero 'A'", 4): "https://app.veo.co/matches/20260927-untitled-recording-2026-09-27_17-16-26-v42537de/",

    # Burriana - Salesianos
    ("C.F. At. Burriana - Salesianos 'A'", 1): "https://app.veo.co/matches/20260905-juvenil-a-burriana-v4434b85/",
    ("C.F. At. Burriana - Salesianos 'A'", 2): "https://app.veo.co/matches/20260913-juvenil-a-contra-patacona-v7ea2f8f/",
    ("C.F. At. Burriana - Salesianos 'A'", 3): "https://app.veo.co/matches/20260919-jb-vs-at-burriana-salesianos-v00500cf",
    ("C.F. At. Burriana - Salesianos 'A'", 4): "https://app.veo.co/matches/20260927-untitled-recording-2026-09-27_17-07-43-v157dcb5",
}

# Sincronización validada de goles entre acta FFCV, reloj de partido en Veo y
# timestamp absoluto del vídeo. Son tres relojes distintos y NO se deben mezclar.
# - ffcv_min: minuto del acta oficial usado en los eventos de la app.
# - veo_match_clock: reloj de partido/evento que muestra Veo.
# - video_timestamp: posición absoluta dentro del vídeo completo de Veo.
# - event_url: enlace específico al evento cuando se ha podido validar.
VEO_GOAL_SYNC = {
    (2, "Sebas"): {
        "ffcv_min": 62,
        "veo_match_clock": "66:40",
        "veo_event_min": 67,
        "video_timestamp": "87:47",
        "event_url": "https://app.veo.co/matches/20260912-juvenil-a-betera-ve022cb5/?event_type=FootballShotGoal&event=5e990f44-af76-11f1-b212-0708876e5205#/events/",
    },
    (2, "Núñez"): {
        "ffcv_min": 87,
        "veo_match_clock": "90:00",
        "veo_event_min": 90,
        "video_timestamp": "110:46",
        "event_url": None,
    },
}

def match_link(team, jornada):
    try:
        return MATCH_LINKS.get((str(team), int(jornada)))
    except Exception:
        return None

def short_team_name(name):
    out = str(name)
    for suffix in [" 'A'", " 'B'", " 'C'"]:
        out = out.replace(suffix, "")
    return out


EXPECTED_COLUMNS = {
    "equipos_liga.csv": ["orden", "equipo"],
    "plantillas_rivales.csv": ["equipo", "dorsal", "jugador"],
    "minutos_rivales.csv": ["equipo", "jornada", "dorsal", "jugador", "minutos", "titular", "fuente"],
    "partidos_rivales.csv": ["jornada", "fecha", "local", "visitante", "goles_local", "goles_visitante", "campo", "sistema_local", "sistema_visitante", "estado"],
    "eventos_rivales.csv": ["jornada", "equipo", "minuto", "tipo", "jugador", "detalle"],
    "clasificacion_liga.csv": ["jornada", "fecha", "posicion", "equipo", "puntos", "pj", "pg", "pe", "pp"],
    "alineaciones_rivales.csv": ["equipo", "jornada", "dorsal", "jugador", "rol", "linea", "orden"],
}

@st.cache_data(show_spinner=False)
def _load_csv_cached(name, file_stamp):
    """Carga defensiva cacheada. file_stamp obliga a refrescar cuando cambia el CSV."""
    p = DATA / name
    cols = EXPECTED_COLUMNS.get(name, [])
    try:
        df = pd.read_csv(p) if p.exists() else pd.DataFrame(columns=cols)
    except Exception:
        df = pd.DataFrame(columns=cols)
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df


def load_csv(name):
    """Carga un CSV y refresca automáticamente el caché si cambia el archivo."""
    p = DATA / name
    try:
        stat = p.stat()
        file_stamp = (stat.st_mtime_ns, stat.st_size)
    except Exception:
        file_stamp = (-1, -1)
    return _load_csv_cached(name, file_stamp)


@st.cache_data(show_spinner=False)
def load_individual_video():
    """Datos avanzados de vídeo J2/J3/J5. Cacheado: antes se releían del disco en cada clic."""
    frames = []
    for j in (2, 3, 5):
        p = DATA / f"individual_video_j{j}.csv"
        if p.exists():
            d = pd.read_csv(p)
            if "jornada" not in d.columns:
                d["jornada"] = j
            frames.append(d)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


@st.cache_data(show_spinner=False, max_entries=64)
def _b64_file(path_str):
    """Base64 de un fichero (logos, mapas de calor). Cacheado para no recodificar en cada clic."""
    return base64.b64encode(Path(path_str).read_bytes()).decode()


# Los CSV ya NO se cargan aquí. Se cargan solo al entrar en cada módulo.\n
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
.league-table {{min-width:760px!important;font-size:.78rem!important}}
.league-table th,.league-table td {{padding:7px 6px!important}}
.league-table .pos-col {{width:38px;min-width:38px;max-width:38px}}
.league-table .team-col {{text-align:left!important;width:190px;min-width:150px;max-width:205px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.league-table .stat-col {{width:46px;min-width:46px}}
.league-kpis {{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:8px 0 14px}}
.league-kpi {{background:#fff;border:1px solid #e6eaf0;border-radius:14px;padding:12px 14px;box-shadow:0 4px 12px rgba(16,42,67,.04)}}
.league-kpi .k {{font-size:.72rem;color:#6b7b90;font-weight:800;text-transform:uppercase}}
.league-kpi .v {{font-size:1.12rem;color:{NAVY};font-weight:950;margin-top:3px}}
.league-kpi .s {{font-size:.72rem;color:#7f8da0;margin-top:2px}}
@media (max-width:900px) {{.league-kpis {{grid-template-columns:repeat(2,minmax(0,1fr))}}}}

.m0 {{background:#fecaca}} .m1 {{background:#fdba74}} .m2 {{background:#fde68a}} .m3 {{background:#bbf7d0}} .m4 {{background:#4ade80;color:#073b1e;font-weight:900}} .mx {{background:#f1f5f9;color:#94a3b8}}
.mini-list {{display:flex;flex-direction:column;gap:9px}} .mini-item {{display:flex;justify-content:space-between;gap:10px;align-items:center;border-bottom:1px solid #eef1f4;padding-bottom:8px;font-size:.82rem}} .mini-item:last-child {{border:0}}
.note {{font-size:.78rem;color:{MUTED};margin-top:8px}}
.pending {{color:#94a3b8;font-weight:700}}
.video-callout {{background:#fff;border:1px solid #dbe6f1;border-left:6px solid #e11d48;border-radius:14px;padding:13px 15px;margin:10px 0 14px;box-shadow:0 5px 16px rgba(16,42,67,.04)}}
.video-callout .vt {{font-size:.86rem;font-weight:900;color:{NAVY};margin-bottom:5px}}
.video-callout .vs {{font-size:.76rem;color:{MUTED};margin-bottom:8px}}
.video-link {{display:inline-block;text-decoration:none!important;background:{NAVY};color:#fff!important;font-weight:900;font-size:.78rem;padding:8px 12px;border-radius:10px}}
.match-links-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-top:8px}}
.match-link-card {{background:#fff;border:1px solid #e6eaf0;border-radius:14px;padding:14px;box-shadow:0 5px 16px rgba(16,42,67,.04)}}
.match-link-card .mj {{font-size:.72rem;font-weight:900;color:#64748b;margin-bottom:4px}}
.match-link-card .mf {{font-size:.88rem;font-weight:900;color:{NAVY};margin-bottom:5px}}
.match-link-card .mr {{font-size:.78rem;color:{MUTED};margin-bottom:10px}}
.match-link-card a {{text-decoration:none!important;font-weight:900;color:#fff!important;background:{NAVY};border-radius:9px;padding:7px 10px;display:inline-block;font-size:.76rem}}
.match-link-card .no-link {{font-size:.76rem;color:#94a3b8;font-weight:800}}
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
.goal-pctbox {{width:100%;margin-top:9px;background:#f7f9fc;border-radius:10px;padding:8px 8px 6px;box-sizing:border-box}}
.goal-pctrow {{display:grid;grid-template-columns:34px 1fr 70px;gap:6px;align-items:center;margin:5px 0;font-size:.66rem;font-weight:800;color:{NAVY}}}
.goal-pcttrack {{height:8px;background:#e9eef4;border-radius:999px;overflow:hidden}}
.goal-pctfill-gf {{height:100%;background:#16a34a;border-radius:999px}}
.goal-pctfill-gc {{height:100%;background:#ef4444;border-radius:999px}}
.goal-macro-grid {{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin:6px 0 14px}}
.goal-macro {{border:1px solid #e4eaf1;border-radius:15px;padding:13px 14px;min-height:118px;box-shadow:0 5px 16px rgba(16,42,67,.045);background:#fff}}
.goal-macro .t {{font-size:.74rem;font-weight:900;color:{NAVY};margin-bottom:4px}}
.goal-macro .big {{font-size:1.52rem;font-weight:950;line-height:1;color:{NAVY};margin:4px 0}}
.goal-macro .sub {{font-size:.69rem;color:{MUTED};line-height:1.35}}
.goal-macro.blue {{background:#eef7ff}} .goal-macro.green {{background:#f0fbf1}} .goal-macro.red {{background:#fff1f1}} .goal-macro.purple {{background:#f5f1ff}} .goal-macro.pink {{background:#fff0f5}}
.goal-activity {{display:flex;align-items:center;justify-content:center;margin:2px 0 7px}}
.goal-ring {{width:58px;height:58px;border-radius:50%;display:grid;place-items:center}}
.goal-ring-inner {{width:42px;height:42px;border-radius:50%;background:#fff;display:grid;place-items:center;font-weight:950;font-size:.82rem;color:{NAVY}}}
.goal-detail-wrap {{background:#fff;border:1px solid #e6eaf0;border-radius:14px;padding:10px 12px;margin-top:12px;box-shadow:0 5px 16px rgba(16,42,67,.04);overflow:auto}}
.goal-detail-title {{font-size:.83rem;font-weight:900;color:{NAVY};margin:0 0 8px}}
table.goal-detail {{width:100%;border-collapse:collapse;font-size:.72rem;min-width:760px}}
table.goal-detail th {{background:#f7f9fc;color:{NAVY};font-weight:900;padding:7px;border:1px solid #e6ebf1;text-align:center}}
table.goal-detail td {{padding:7px;border:1px solid #e6ebf1;text-align:center}} table.goal-detail td:first-child {{text-align:left;font-weight:800;color:{NAVY};background:#fbfcfe}}
.diff-pos {{background:#ecfdf3!important;color:#15803d;font-weight:900}} .diff-neg {{background:#fff1f2!important;color:#dc2626;font-weight:900}} .diff-zero {{background:#f8fafc!important;color:#64748b;font-weight:900}}
@media (max-width: 1050px) {{.goal-macro-grid {{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
[data-testid="stMetric"] {{background:#fff;border:1px solid #e6eaf0;border-radius:14px;padding:10px 13px;box-shadow:0 5px 16px rgba(16,42,67,.04)}}

.home-photo-link {{text-decoration:none!important;color:inherit!important;display:block}}
.home-photo-card {{position:relative;border-radius:22px;overflow:hidden;background:#fff;border:1px solid #e5eaf1;box-shadow:0 12px 32px rgba(15,42,68,.10);transition:.18s ease}}
.home-photo-card:hover {{transform:translateY(-3px);box-shadow:0 18px 42px rgba(15,42,68,.16)}}
.home-photo-card img {{width:100%;height:390px;object-fit:cover;display:block;transition:.25s ease}}
.home-photo-card:hover img {{transform:scale(1.015)}}
.home-photo-overlay {{position:absolute;left:0;right:0;bottom:0;padding:22px 22px 20px;display:flex;align-items:flex-end;justify-content:space-between;background:linear-gradient(transparent,rgba(3,31,61,.90));color:white}}
.home-photo-title {{font-size:1.45rem;font-weight:950}}
.home-photo-sub {{font-size:.78rem;opacity:.85;margin-top:3px}}
.home-photo-arrow {{font-size:2rem;font-weight:900}}
.back-home-link {{display:inline-block;text-decoration:none!important;font-weight:900;color:#0b3766!important;background:white;border:1px solid #dce5ef;border-radius:10px;padding:8px 12px}}
.league-hero {{display:flex;justify-content:space-between;gap:20px;align-items:center;background:linear-gradient(135deg,#082f5c,#0b4b83);padding:24px 28px;border-radius:22px;color:white;margin-bottom:16px;box-shadow:0 14px 34px rgba(7,43,79,.18)}}
.league-eyebrow {{font-size:.72rem;font-weight:900;letter-spacing:.13em;opacity:.72}}
.league-title {{font-size:1.8rem;font-weight:950;margin-top:4px}}
.league-subtitle {{font-size:.88rem;opacity:.82;margin-top:5px}}
.league-badge {{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.20);padding:10px 14px;border-radius:999px;font-size:.78rem;font-weight:850;white-space:nowrap}}
.league-kpis-6 {{grid-template-columns:repeat(6,minmax(0,1fr))!important}}
.league-kpi.featured {{background:linear-gradient(145deg,#fff7e7,#ffffff);border-color:#ffd987}}
.league-highlight-grid {{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:0 0 18px}}
.league-highlight {{display:flex;align-items:center;gap:12px;background:white;border:1px solid #e8edf3;border-radius:16px;padding:14px 16px}}
.hi-icon {{font-size:1.6rem}}.hi-label{{font-size:.68rem;text-transform:uppercase;color:#718096;font-weight:900}}.hi-team{{font-size:.95rem;font-weight:950;color:#0b3766;margin-top:2px}}.hi-value{{font-size:.76rem;color:#69788d;margin-top:2px}}
.league-section-title {{margin-top:18px!important;margin-bottom:9px!important}}
.premium-table th {{font-size:.68rem!important;text-transform:uppercase;letter-spacing:.02em}}
.premium-table td {{font-size:.77rem!important}}
.top-pos {{background:#e8f7ee!important;color:#137a3d!important}}.danger-pos {{background:#fff0f0!important;color:#b42318!important}}
.positive {{color:#138a46!important}}.negative{{color:#d33b3b!important}}.pts-cell{{background:#f4f8fc!important;font-size:.9rem!important}}.form-cell{{white-space:nowrap}}
.form-dot {{display:inline-flex;width:20px;height:20px;border-radius:50%;align-items:center;justify-content:center;color:white;font-size:.60rem;font-weight:950;margin-right:3px}}
.form-dot.win{{background:#20a464}}.form-dot.draw{{background:#8a98a8}}.form-dot.loss{{background:#df4b4b}}
.goal-time-note {{font-size:.76rem;color:#718096;margin:-2px 0 9px}}
.goal-time-grid {{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:9px}}
.goal-time-card {{background:white;border:1px solid #e7ecf2;border-radius:15px;padding:12px}}
.goal-time-head {{font-size:.88rem;font-weight:950;color:#0b3766;margin-bottom:8px}}
.goal-line {{display:grid;grid-template-columns:22px 1fr 20px 34px;align-items:center;gap:5px;font-size:.68rem;margin:6px 0}}
.goal-line span{{font-weight:900}}.goal-line em{{font-style:normal;color:#7a8797;text-align:right}}
.goal-track {{height:7px;border-radius:8px;background:#edf1f5;overflow:hidden}}.goal-fill{{height:100%;border-radius:8px}}.goal-fill.gf{{background:#22a764}}.goal-fill.gc{{background:#e45b5b}}
.goal-diff {{font-size:.66rem;color:#748195;border-top:1px solid #eef1f4;padding-top:7px;margin-top:7px}}
.discipline-grid {{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}}
.discipline-card {{display:flex;align-items:center;gap:10px;background:white;border:1px solid #e8edf3;border-radius:15px;padding:13px}}
.discipline-card span{{font-size:1.35rem}}.discipline-card b{{display:block;font-size:1.15rem;color:#0b3766}}.discipline-card small{{display:block;color:#718096;font-size:.66rem;margin-top:1px}}
.league-match-card {{display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center;background:white;border:1px solid #e8edf3;border-radius:11px;padding:9px 12px;margin:5px 0;font-size:.78rem}}
.league-match-card span:last-child{{text-align:right}}.league-match-card b{{font-size:.92rem;color:#0b3766}}.matchday-title{{font-size:.78rem;font-weight:950;color:#0b3766;margin:12px 0 5px}}
@media (max-width:1100px){{.league-kpis-6{{grid-template-columns:repeat(3,minmax(0,1fr))!important}}.goal-time-grid{{grid-template-columns:repeat(3,minmax(0,1fr))}}.discipline-grid{{grid-template-columns:repeat(3,minmax(0,1fr))}}}}
@media (max-width:700px){{.league-hero{{align-items:flex-start;flex-direction:column}}.league-badge{{white-space:normal}}.league-kpis-6{{grid-template-columns:repeat(2,minmax(0,1fr))!important}}.league-highlight-grid{{grid-template-columns:1fr}}.goal-time-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.discipline-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.home-photo-card img{{height:280px}}}}


.main-standings th {{font-size:.74rem!important}}
.main-standings td {{font-size:.84rem!important}}
.main-standings tbody tr:nth-child(even) {{background:#fbfcfe}}
.main-standings tbody tr {{transition:background .12s ease, transform .12s ease}}
.main-standings tbody tr:hover {{background:#eef6ff!important}}
.main-standings .stat-num {{font-weight:900!important;color:#102a43}}
.main-standings .team-col {{font-size:.86rem!important;min-width:215px!important;width:215px!important}}
.main-standings .pts-cell {{font-size:.94rem!important;background:#edf5ff!important}}
.performance-table td {{font-size:.82rem!important}}
.performance-table .stat-num {{font-weight:900!important;color:#102a43}}
.performance-table tbody tr:hover {{background:#f3f8ff!important}}
.performance-table .team-col {{min-width:220px!important;width:220px!important}}
.perf-explainer {{font-size:.80rem;color:#64748b;margin:2px 0 9px}}
.yellow-kpi {{border-top:4px solid #f2c94c!important}}
.red-kpi {{border-top:4px solid #df4b4b!important}}
.match-team {{display:flex;align-items:center;gap:4px;font-weight:850}}
.match-team.away {{justify-content:flex-end}}
.league-match-card {{font-size:.84rem!important}}
.league-match-card b {{font-size:1rem!important}}


.rival-list-row {{display:flex;align-items:center;gap:7px;padding:6px 4px;border-bottom:1px solid #edf1f5;font-size:.82rem}}
.venue-kpi-grid {{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:10px 0 4px}}
.venue-kpi {{background:#fff;border:1px solid #e4e9f0;border-radius:14px;padding:13px 14px;display:flex;align-items:center;gap:11px;box-shadow:0 3px 12px rgba(16,42,67,.05)}}
.venue-kpi.home {{border-top:4px solid #16a34a}}
.venue-kpi.home-against {{border-top:4px solid #f59e0b}}
.venue-kpi.away {{border-top:4px solid #1d63d8}}
.venue-kpi.away-against {{border-top:4px solid #ef4444}}
.vk-icon {{font-size:1.35rem}}
.vk-label {{font-size:.70rem;font-weight:850;color:#64748b;text-transform:uppercase;letter-spacing:.02em}}
.vk-value {{font-size:1.55rem;font-weight:950;color:#102a43;line-height:1.05;margin-top:2px}}
.vk-sub {{font-size:.76rem;color:#6b7c93;font-weight:700;margin-top:2px}}
.venue-readout {{font-size:.76rem;color:#64748b;margin:3px 0 11px;padding-left:2px}}
.performance-table .pos-col {{font-weight:900}}
.performance-table .pts-cell {{background:#eef6ff!important;font-size:.92rem!important}}
@media (max-width: 900px) {{
  .venue-kpi-grid {{grid-template-columns:repeat(2,minmax(0,1fr))}}
}}

</style>
""",
    unsafe_allow_html=True,
)


st.markdown(
    """
<style>
.ind-hero{background:linear-gradient(135deg,#052b56 0%,#0b4079 100%);color:#fff;border-radius:18px;padding:18px 20px;box-shadow:0 10px 28px rgba(6,45,90,.18);min-height:210px}
.ind-hero .shirt-no{font-size:3rem;font-weight:950;line-height:.95}.ind-hero .pname{font-size:1.65rem;font-weight:950;line-height:1.05;margin-top:8px}.ind-hero .pos{display:inline-block;background:#1d63d8;padding:5px 10px;border-radius:999px;font-size:.76rem;font-weight:900;margin-top:10px}.ind-hero .meta{font-size:.8rem;opacity:.82;margin-top:12px;line-height:1.7}
.ind-panel{background:#fff;border:1px solid #e6eaf0;border-radius:16px;padding:15px;box-shadow:0 5px 16px rgba(16,42,67,.045);height:100%}.ind-title{font-size:.92rem;font-weight:950;color:#062d5a;margin-bottom:10px}.ind-sub{font-size:.72rem;color:#6b7c93}
.ind-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.ind-mini{background:#f7f9fc;border:1px solid #edf1f5;border-radius:12px;padding:11px 8px;text-align:center}.ind-mini .v{font-size:1.28rem;font-weight:950;color:#062d5a}.ind-mini .l{font-size:.67rem;color:#6b7c93;font-weight:800;margin-top:3px}.ind-mini.warn .v{color:#d97706}.ind-mini.red .v{color:#dc2626}.ind-mini.green .v{color:#16a34a}
.ind-stat{display:grid;grid-template-columns:1fr auto;gap:10px;padding:7px 0;border-bottom:1px solid #edf1f5;font-size:.78rem}.ind-stat:last-child{border-bottom:0}.ind-stat b{color:#062d5a}.ind-stat .muted{color:#94a3b8}
.pos-tabs{display:flex;gap:7px;flex-wrap:wrap;margin:4px 0 12px}.pos-pill{border:1px solid #dce5ef;background:#fff;color:#31506f;padding:7px 11px;border-radius:999px;font-size:.75rem;font-weight:900}.pos-pill.active{background:#eaf2ff;color:#1d63d8;border-color:#b7cff7}
.player-strip{display:flex;gap:8px;overflow:auto;padding-bottom:6px}.player-chip{min-width:110px;background:#fff;border:1px solid #e5eaf0;border-radius:12px;padding:8px 10px}.player-chip .n{font-weight:950;color:#062d5a;font-size:.8rem}.player-chip .r{font-size:.65rem;color:#7b8da4}.player-chip.active{border:2px solid #1d63d8;background:#f2f7ff}
.ind-bar-row{display:grid;grid-template-columns:1fr 80px;gap:10px;align-items:center;margin:9px 0;font-size:.77rem}.ind-bar-bg{height:8px;background:#edf2f7;border-radius:999px;overflow:hidden}.ind-bar-fill{height:100%;background:linear-gradient(90deg,#1d63d8,#5aa2ff);border-radius:999px}.ind-rank{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.rank-card{background:#f7f9fc;border:1px solid #edf1f5;border-radius:12px;padding:11px;text-align:center}.rank-card .place{font-size:1.25rem;font-weight:950;color:#1d63d8}.rank-card .desc{font-size:.67rem;color:#66788e;line-height:1.3;margin-top:3px}
.timeline{position:relative;height:48px;margin:10px 2px 3px}.timeline:before{content:'';position:absolute;left:0;right:0;top:18px;height:8px;border-radius:999px;background:#dbeafe}.timeline .played{position:absolute;left:0;top:18px;height:8px;border-radius:999px;background:#60a5fa}.timeline .ev{position:absolute;top:9px;transform:translateX(-50%);font-size:15px}.timeline-labels{display:flex;justify-content:space-between;font-size:.62rem;color:#8494a8}
.video-badge{display:inline-block;background:#fef3c7;color:#92400e;border:1px solid #fde68a;padding:5px 8px;border-radius:999px;font-size:.67rem;font-weight:900}.verified-badge{display:inline-block;background:#ecfdf3;color:#166534;border:1px solid #bbf7d0;padding:5px 8px;border-radius:999px;font-size:.67rem;font-weight:900}
@media(max-width:900px){.ind-kpis,.ind-rank{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
""",
    unsafe_allow_html=True,
)


def render_individual():
    team = "Primer Toque C.F. 'A'"
    pt_min = minutos[minutos.equipo == team].copy()
    pt_ev = eventos[eventos.equipo == team].copy()
    pt_al = alineaciones[alineaciones.equipo == team].copy()
    pt_roster = plantillas[plantillas.equipo == team].copy()

    # Datos avanzados: solo partidos de casa. La arquitectura queda lista para J2/J3/J5.
    adv_all = load_individual_video()
    advanced_available = sorted(adv_all.jornada.dropna().astype(int).unique().tolist()) if not adv_all.empty else []

    # Posición principal a partir de las alineaciones reales.
    role_map = {}
    if not pt_al.empty:
        for p, grp in pt_al.groupby("jugador"):
            vals = grp["rol"].dropna().astype(str)
            if not vals.empty:
                role_map[p] = vals.mode().iloc[0]
    role_name = {"POR":"Portero", "DEF":"Defensa", "MED":"Mediocentro", "ATA":"Delantero"}
    role_group = {"POR":"Porteros", "DEF":"Defensas", "MED":"Mediocentros", "ATA":"Delanteros"}

    roster = pt_roster.copy()
    if roster.empty:
        roster = pt_min[["dorsal","jugador"]].drop_duplicates()
    roster["rol"] = roster["jugador"].map(role_map).fillna("MED")
    roster["grupo"] = roster["rol"].map(role_group).fillna("Mediocentros")
    roster = roster.sort_values(["rol","dorsal","jugador"]).reset_index(drop=True)

    st.markdown("""
    <style>
    .ind-v2-head{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;margin:2px 0 12px}.ind-v2-title{font-size:2rem;font-weight:950;color:#062d5a;letter-spacing:-.04em}.ind-v2-sub{font-size:.8rem;color:#6b7c93;margin-top:2px}.data-note{display:inline-flex;align-items:center;gap:6px;background:#eef6ff;color:#195ea8;border:1px solid #d6e8fb;padding:6px 10px;border-radius:999px;font-size:.68rem;font-weight:900}
    .global-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px;margin:8px 0 12px}.global-card{background:#fff;border:1px solid #e6ebf1;border-radius:15px;padding:13px 12px;box-shadow:0 5px 16px rgba(16,42,67,.04)}.global-card .big{font-size:1.55rem;font-weight:950;color:#062d5a}.global-card .small{font-size:.66rem;color:#718096;font-weight:800;margin-top:2px}.global-card .accent{font-size:.67rem;color:#1d63d8;font-weight:900;margin-top:6px}
    .rank-list{display:grid;gap:8px}.rank-row{display:grid;grid-template-columns:28px 1fr auto;gap:8px;align-items:center}.rank-num{width:26px;height:26px;border-radius:8px;background:#edf4ff;color:#1d63d8;display:grid;place-items:center;font-size:.72rem;font-weight:950}.rank-name{font-size:.75rem;font-weight:900;color:#17324d}.rank-value{font-size:.74rem;font-weight:950;color:#062d5a}.microbar{height:6px;background:#edf2f7;border-radius:999px;overflow:hidden;margin-top:4px}.microbar span{display:block;height:100%;background:linear-gradient(90deg,#1d63d8,#78b1ff);border-radius:999px}
    .minute-card{background:#fff;border:1px solid #e7ebf1;border-radius:13px;padding:10px 11px}.minute-card .top{display:flex;justify-content:space-between;gap:8px;font-size:.74rem;font-weight:900;color:#17324d}.minute-card .mins{font-size:.75rem;font-weight:950}.minbar{height:8px;background:#edf1f5;border-radius:99px;overflow:hidden;margin-top:7px}.minbar span{display:block;height:100%;border-radius:99px}.minutes-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
    .visual-insights{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin:10px 0 12px}.donut-card{background:#fff;border:1px solid #e5ebf2;border-radius:16px;padding:12px;display:flex;align-items:center;gap:10px;min-width:0;box-shadow:0 5px 16px rgba(16,42,67,.035)}.donut{--p:0;--c:#1d63d8;width:66px;height:66px;border-radius:50%;background:conic-gradient(var(--c) calc(var(--p)*1%),#edf2f7 0);position:relative;flex:0 0 66px}.donut:after{content:'';position:absolute;inset:8px;background:#fff;border-radius:50%}.donut .dv{position:absolute;inset:0;display:grid;place-items:center;z-index:2;font-size:.78rem;font-weight:950;color:#062d5a}.donut-copy{min-width:0}.donut-label{font-size:.69rem;font-weight:950;color:#17324d;line-height:1.15}.donut-sub{font-size:.58rem;color:#718096;font-weight:750;margin-top:4px;line-height:1.25}.leader-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:8px 0 14px}.leader-card{background:linear-gradient(145deg,#fff,#f7fbff);border:1px solid #e5ebf2;border-radius:16px;padding:14px;position:relative;overflow:hidden}.leader-kicker{font-size:.6rem;text-transform:uppercase;letter-spacing:.07em;font-weight:950;color:#6b7c93}.leader-name{font-size:1rem;font-weight:950;color:#062d5a;margin-top:4px}.leader-value{font-size:1.35rem;font-weight:950;color:#1d63d8;margin-top:7px}.leader-meta{font-size:.62rem;color:#718096;font-weight:750;margin-top:2px}.leader-icon{position:absolute;right:12px;top:12px;font-size:1.35rem;opacity:.8}
    .map-shell{background:#fff;border:1px solid #e5eaf0;border-radius:16px;padding:11px;box-shadow:0 5px 16px rgba(16,42,67,.04);overflow:hidden}.map-label{font-size:.82rem;font-weight:950;color:#062d5a;margin-bottom:7px}.map-img-wrap{width:100%;overflow:hidden;border-radius:12px;background:#fff}.map-img-wrap img{display:block;width:100%;height:auto;max-width:100%;object-fit:contain;object-position:center}.map-empty{min-height:215px;display:grid;place-items:center;text-align:center;background:linear-gradient(135deg,#f8fafc,#eef4f8);border:1px dashed #cfdae6;border-radius:12px;color:#8292a6;font-size:.75rem;padding:18px}
    .per90-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;margin-top:9px}.per90-card{background:linear-gradient(180deg,#fbfdff,#f4f8fc);border:1px solid #e0e8f1;border-radius:13px;padding:11px 10px}.per90-card .v{font-size:1.05rem;font-weight:950;color:#073866}.per90-card .l{font-size:.62rem;font-weight:900;color:#72849a;text-transform:uppercase;letter-spacing:.03em;margin-top:3px}.per90-card .adj{font-size:.66rem;font-weight:900;color:#1d63d8;margin-top:6px}.sample-note{display:inline-flex;align-items:center;gap:6px;margin-top:9px;padding:6px 9px;border-radius:999px;font-size:.68rem;font-weight:900}.sample-low{background:#fff1f2;color:#b91c1c;border:1px solid #fecdd3}.sample-mid{background:#fff7ed;color:#c2410c;border:1px solid #fed7aa}.sample-ok{background:#fefce8;color:#a16207;border:1px solid #fde68a}.sample-good{background:#ecfdf3;color:#166534;border:1px solid #bbf7d0}.conversion-pill{display:inline-flex;align-items:center;gap:7px;background:#eaf8ef;color:#17733b;border:1px solid #cdebd7;padding:6px 9px;border-radius:999px;font-weight:950;font-size:.7rem}.video-day{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:13px;padding:11px;margin-top:9px}.video-day-title{font-size:.78rem;font-weight:950}.video-goal{font-size:.7rem;line-height:1.45;margin-top:7px;padding-top:7px;border-top:1px solid rgba(255,255,255,.14)}
    .source-card{background:linear-gradient(135deg,#061f3e,#0d4074);color:white;border-radius:16px;padding:15px}.source-card a{display:inline-block;text-decoration:none;background:white;color:#063565;padding:8px 11px;border-radius:10px;font-size:.72rem;font-weight:950;margin:5px 5px 0 0}.source-muted{font-size:.69rem;opacity:.78;line-height:1.5}
    .compare-wrap{background:#fff;border:1px solid #e4eaf1;border-radius:17px;padding:14px;margin:10px 0 14px;box-shadow:0 6px 18px rgba(16,42,67,.04)}.compare-head{display:flex;justify-content:space-between;align-items:end;gap:12px;margin-bottom:12px}.compare-title{font-size:.95rem;font-weight:950;color:#062d5a}.compare-sub{font-size:.68rem;color:#77899e;font-weight:750}.compare-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}.compare-card{border:1px solid #e7ecf2;border-radius:14px;padding:11px;background:linear-gradient(180deg,#fff,#f8fbfe)}.compare-label{font-size:.66rem;font-weight:950;color:#657a91;text-transform:uppercase;letter-spacing:.04em}.compare-row{display:grid;grid-template-columns:34px 1fr auto;gap:8px;align-items:center;margin-top:8px}.compare-j{font-size:.68rem;font-weight:950;color:#17324d}.compare-val{font-size:.72rem;font-weight:950;color:#062d5a}.compare-bar{height:8px;background:#edf2f7;border-radius:999px;overflow:hidden}.compare-bar span{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#1d63d8,#7cb7ff)}.delta-up{color:#15803d}.delta-down{color:#b91c1c}.delta-flat{color:#64748b}.compare-foot{margin-top:9px;font-size:.66rem;color:#718096;font-weight:750}.day-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin-top:10px}.day-card{border:1px solid #e6ebf1;border-radius:15px;padding:12px;background:#fff}.day-card .j{font-size:.76rem;font-weight:950;color:#1d63d8}.day-card .fixture{font-size:.68rem;color:#718096;font-weight:750;margin-top:2px}.day-card .vals{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-top:10px}.day-mini{background:#f6f9fc;border-radius:10px;padding:8px}.day-mini b{display:block;font-size:.9rem;color:#062d5a}.day-mini span{font-size:.58rem;color:#718096;font-weight:850;text-transform:uppercase}.compare-table{width:100%;border-collapse:separate;border-spacing:0 6px}.compare-table th{font-size:.62rem;text-align:left;color:#718096;text-transform:uppercase;padding:0 8px}.compare-table td{background:#f8fafc;padding:8px;font-size:.7rem;font-weight:800;color:#17324d}.compare-table td:first-child{border-radius:9px 0 0 9px}.compare-table td:last-child{border-radius:0 9px 9px 0}
    .section-kicker{font-size:.7rem;color:#6f8095;font-weight:900;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px}.section-title{font-size:1.05rem;color:#062d5a;font-weight:950;margin-bottom:9px}
    .summary-panel{background:linear-gradient(135deg,#ffffff 0%,#f6faff 100%);border:1px solid #e4ebf3;border-radius:18px;padding:15px;box-shadow:0 8px 22px rgba(16,42,67,.055)}
    .summary-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px}.summary-kpi{position:relative;overflow:hidden;border-radius:15px;padding:13px 12px;border:1px solid #e8edf3;background:#fff}.summary-kpi:after{content:"";position:absolute;inset:auto -24px -28px auto;width:64px;height:64px;border-radius:50%;background:rgba(37,99,235,.07)}.summary-kpi .ico{font-size:1.05rem}.summary-kpi .sv{font-size:1.45rem;font-weight:950;color:#082f5b;line-height:1.1;margin-top:5px}.summary-kpi .sl{font-size:.62rem;text-transform:uppercase;letter-spacing:.06em;color:#77899e;font-weight:900;margin-top:3px}.summary-kpi.green{background:linear-gradient(135deg,#f1fff7,#ffffff)}.summary-kpi.orange{background:linear-gradient(135deg,#fff8ec,#ffffff)}.summary-kpi.red{background:linear-gradient(135deg,#fff2f3,#ffffff)}.summary-kpi.blue{background:linear-gradient(135deg,#eef6ff,#ffffff)}
    .per90-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.per90-card{position:relative;overflow:hidden;padding:14px 13px;border-radius:15px;min-height:104px}.per90-card .pi{font-size:1.15rem;margin-bottom:7px}.per90-card .v{font-size:1.18rem}.per90-card .l{font-size:.61rem}.per90-card .meter{height:7px;background:rgba(148,163,184,.22);border-radius:99px;overflow:hidden;margin-top:10px}.per90-card .meter span{display:block;height:100%;border-radius:99px}.p90-dist{background:linear-gradient(135deg,#effcf5,#ffffff);border-color:#d9f3e4}.p90-dist .meter span{background:#16a34a}.p90-hi{background:linear-gradient(135deg,#fff8e8,#ffffff);border-color:#f7e6bb}.p90-hi .meter span{background:#f59e0b}.p90-sprint{background:linear-gradient(135deg,#fff1f4,#ffffff);border-color:#f8d5de}.p90-sprint .meter span{background:#e11d48}.p90-shot{background:linear-gradient(135deg,#eef6ff,#ffffff);border-color:#d7e8ff}.p90-shot .meter span{background:#2563eb}.p90-goal{background:linear-gradient(135deg,#f4efff,#ffffff);border-color:#e5dafd}.p90-goal .meter span{background:#7c3aed}.p90-event{background:linear-gradient(135deg,#f5f7fb,#ffffff);border-color:#e3e8ef}.p90-event .meter span{background:#64748b}
    .metric-panel{height:100%;background:#fff;border:1px solid #e4eaf1;border-radius:18px;padding:0 14px 13px;box-shadow:0 7px 20px rgba(16,42,67,.045);overflow:hidden}.metric-head{margin:0 -14px 7px;padding:12px 14px;font-size:.9rem;font-weight:950;color:#082f5b}.metric-head.tech{background:linear-gradient(90deg,#eaf4ff,#f7fbff)}.metric-head.phys{background:linear-gradient(90deg,#eafaf0,#f8fffb)}.metric-head.events{background:linear-gradient(90deg,#f5efff,#fbf9ff)}.metric-row{display:grid;grid-template-columns:26px 1fr auto;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid #edf1f5}.metric-row:last-child{border-bottom:0}.metric-ico{width:24px;height:24px;border-radius:8px;display:grid;place-items:center;font-size:.72rem;background:#f2f6fb}.metric-name{font-size:.75rem;color:#334155;font-weight:800}.metric-val{font-size:.78rem;color:#082f5b;font-weight:950}.metric-subbar{grid-column:2/4;height:5px;border-radius:99px;background:#edf2f7;overflow:hidden;margin-top:-2px}.metric-subbar span{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#3b82f6,#8bbcff)}.metric-panel.phys .metric-subbar span{background:linear-gradient(90deg,#16a34a,#86efac)}.event-timeline{position:relative;margin-top:4px}.event-row{display:grid;grid-template-columns:30px 1fr auto;gap:8px;align-items:center;padding:8px 0}.event-dot{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;background:#f3efff;font-size:.72rem}.event-text{font-size:.74rem;font-weight:850;color:#334155}.event-min{font-size:.78rem;font-weight:950;color:#082f5b}.event-line{height:1px;background:#eceff4;margin-left:13px}
    [data-testid="stButton"] button{border-radius:12px!important;font-weight:850!important;border:1px solid #dfe7ef!important;min-height:42px}.player-label{font-size:.64rem;color:#77899e;text-align:center;margin-top:-8px;margin-bottom:7px}
    .impact-wrap{background:#fff;border:1px solid #e5ebf2;border-radius:18px;padding:14px;margin:10px 0 14px;overflow-x:auto;box-shadow:0 5px 18px rgba(16,42,67,.035)}
    .impact-head{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;margin-bottom:10px}.impact-title{font-size:.92rem;font-weight:950;color:#062d5a}.impact-sub{font-size:.62rem;color:#718096;font-weight:750;margin-top:3px}.impact-legend{font-size:.58rem;color:#718096;font-weight:800;white-space:nowrap}
    table.impact-table{width:100%;border-collapse:separate;border-spacing:0;min-width:980px;font-size:.66rem}.impact-table th{padding:8px 7px;text-align:center;color:#6b7c93;text-transform:uppercase;letter-spacing:.04em;font-size:.55rem;border-bottom:1px solid #e5ebf2;background:#f8fafc}.impact-table th:first-child,.impact-table td:first-child{text-align:left;position:sticky;left:0;z-index:2;background:#fff}.impact-table td{padding:7px;border-bottom:1px solid #edf2f7;text-align:center;font-weight:850;color:#17324d}.impact-table tr:last-child td{border-bottom:0}.impact-player{font-weight:950;color:#062d5a;white-space:nowrap}.impact-pos{display:inline-flex;align-items:center;justify-content:center;min-width:27px;height:22px;border-radius:8px;background:#edf5ff;color:#1d63d8;font-weight:950;margin-right:7px}.impact-cell{border-radius:8px;padding:5px 6px;display:inline-block;min-width:44px}.trend-mini{display:flex;gap:3px;justify-content:center;align-items:end;height:26px}.trend-mini span{width:8px;border-radius:3px 3px 1px 1px;background:#60a5fa;min-height:3px}.activity-pill{display:inline-flex;align-items:center;gap:5px;padding:4px 7px;border-radius:999px;background:#f1f5f9}.activity-dot{width:7px;height:7px;border-radius:50%}
    .journey-strip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:8px 0 14px}.journey-card{background:linear-gradient(145deg,#fff,#f8fbff);border:1px solid #e5ebf2;border-radius:16px;padding:13px}.journey-k{font-size:.57rem;text-transform:uppercase;letter-spacing:.05em;color:#718096;font-weight:950}.journey-v{font-size:1.2rem;font-weight:950;color:#062d5a;margin-top:3px}.journey-meta{font-size:.62rem;color:#718096;font-weight:750;margin-top:2px}.journey-row{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:9px}.journey-stat{background:#f7faff;border-radius:10px;padding:7px;text-align:center}.journey-stat b{display:block;font-size:.8rem;color:#17324d}.journey-stat span{font-size:.52rem;color:#718096;font-weight:800}
    @media(max-width:1000px){.global-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.minutes-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.compare-metrics{grid-template-columns:1fr}.day-cards{grid-template-columns:1fr}.summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.per90-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.visual-insights{grid-template-columns:repeat(2,minmax(0,1fr))}.leader-grid{grid-template-columns:1fr}.journey-strip{grid-template-columns:1fr}}
    </style>
    """, unsafe_allow_html=True)

    def map_image_html(path_obj, alt_text):
        """Render a full-width image without Streamlit clipping/cropping."""
        if not path_obj.exists():
            return ""
        mime = "image/png" if path_obj.suffix.lower() == ".png" else "image/jpeg"
        b64 = _b64_file(str(path_obj))
        return f"<div class='map-img-wrap'><img src='data:{mime};base64,{b64}' alt='{_safe_html(alt_text, quote=True)}'></div>"

    # Cabecera + jornada. No se usa "Periodo": solo jornadas con tracking de casa + Total.
    h1,h2 = st.columns([3.0,1.0])
    with h1:
        st.markdown("<div class='ind-v2-head'><div><div class='ind-v2-title'>Individual</div><div class='ind-v2-sub'>Rendimiento por jugador y posición · acta oficial + tracking de partidos de casa</div></div></div>", unsafe_allow_html=True)
    with h2:
        jornada_ui = st.selectbox("Jornada", ["J2","J3","J5","Total"], index=0)
    if jornada_ui == "Total":
        js = [2,3,5]
        advanced_js = [j for j in js if j in advanced_available]
        view_label = "Total · partidos de casa"
    else:
        j = int(jornada_ui[1:])
        js = [j]
        advanced_js = [j] if j in advanced_available else []
        view_label = jornada_ui
    avail_txt = " + ".join(f"J{x}" for x in advanced_available) if advanced_available else "ninguna"
    st.markdown(f"<span class='data-note'>● Tracking avanzado disponible: {_safe_html(avail_txt)} · Total solo suma jornadas cargadas</span>", unsafe_allow_html=True)

    if "ind_group" not in st.session_state:
        st.session_state.ind_group = "Todos"
    if "ind_selected_player" not in st.session_state:
        st.session_state.ind_selected_player = None

    # Protección frente a estado antiguo del navegador tras publicar una versión nueva.
    valid_groups = {"Todos", "Porteros", "Defensas", "Mediocentros", "Delanteros"}
    if st.session_state.ind_group not in valid_groups:
        st.session_state.ind_group = "Todos"
        st.session_state.ind_selected_player = None
    valid_players = set(roster["jugador"].dropna().astype(str).tolist())
    if st.session_state.ind_selected_player is not None and str(st.session_state.ind_selected_player) not in valid_players:
        st.session_state.ind_selected_player = None

    # Posiciones como botones, no desplegable.
    st.markdown("<div style='height:8px'></div><div class='section-kicker'>Explorar plantilla</div>", unsafe_allow_html=True)
    groups = ["Todos","Porteros","Defensas","Mediocentros","Delanteros"]
    gcols = st.columns(5)
    for col,g in zip(gcols,groups):
        with col:
            icon = {"Todos":"◉","Porteros":"🧤","Defensas":"🛡️","Mediocentros":"⚙️","Delanteros":"⚡"}[g]
            if st.button(f"{icon} {g}", key=f"grp_{g}", width="stretch"):
                st.session_state.ind_group = g
                st.session_state.ind_selected_player = None

    group = st.session_state.ind_group
    roster_view = roster if group == "Todos" else roster[roster.grupo == group]
    roster_view = roster_view.sort_values(["dorsal","jugador"]).reset_index(drop=True)

    # En "Todos" mostramos un dashboard-resumen limpio. Los jugadores aparecen solo al pulsar una posición.
    st.markdown(f"<div class='section-title'>{_safe_html(group)}</div>", unsafe_allow_html=True)
    if group != "Todos":
        rows = [roster_view.iloc[i:i+5] for i in range(0,len(roster_view),5)]
        for chunk in rows:
            cols = st.columns(5)
            for idx,(_,r) in enumerate(chunk.iterrows()):
                with cols[idx]:
                    label = f"#{int(r.dorsal)} · {r.jugador}"
                    if st.button(label, key=f"pl_{int(r.dorsal)}_{r.jugador}", width="stretch"):
                        st.session_state.ind_selected_player = str(r.jugador)
                    st.markdown(f"<div class='player-label'>{_safe_html(role_name.get(r.rol,'Jugador'))}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='data-note'>Resumen global · elige una posición para abrir jugadores individuales ordenados por dorsal</div>", unsafe_allow_html=True)

    # Helpers compartidos por resumen e individual.
    # Se definen antes de la bifurcación para que abrir directamente un jugador no falle.
    def _num(frame, col, how='sum'):
        if frame is None or frame.empty or col not in frame.columns:
            return None
        x=pd.to_numeric(frame[col], errors='coerce').dropna()
        if x.empty:
            return None
        if how=='max': return float(x.max())
        if how=='mean': return float(x.mean())
        return float(x.sum())

    def _fmt(v, suffix='', decimals=1):
        if v is None: return '—'
        if decimals == 0 or abs(v-round(v)) < 1e-9:
            txt=str(int(round(v)))
        else:
            txt=str(round(float(v),decimals)).replace('.',',')
        return txt+suffix

    def compare_metric_card(label, values, suffix='', decimals=1):
        clean=[float(v) for _,v in values if v is not None]
        mx=max(clean) if clean else 1.0
        if mx <= 0: mx=1.0
        rows=[]
        for j,v in values:
            width=0 if v is None else min(100,float(v)/mx*100)
            rows.append(f"<div class='compare-row'><div class='compare-j'>J{j}</div><div class='compare-bar'><span style='width:{width:.1f}%'></span></div><div class='compare-val'>{_fmt(v,suffix,decimals)}</div></div>")
        delta=''
        if len(values)>=2 and values[0][1] is not None and values[-1][1] is not None:
            a=float(values[0][1]); b=float(values[-1][1])
            if abs(a) > 1e-9:
                pct=(b-a)/a*100
                cls='delta-up' if pct>0.05 else ('delta-down' if pct<-0.05 else 'delta-flat')
                arrow='▲' if pct>0.05 else ('▼' if pct<-0.05 else '→')
                delta=f"<div class='compare-foot {cls}'>{arrow} {abs(pct):.1f}% de J{values[0][0]} a J{values[-1][0]}</div>".replace('.',',')
        return f"<div class='compare-card'><div class='compare-label'>{_safe_html(label)}</div>{''.join(rows)}{delta}</div>"

    # ---------- VISTA TODOS / POSICIÓN ----------
    player = st.session_state.ind_selected_player
    if player is None:
        sub_roster = roster_view.copy()
        dorsals = sub_roster.dorsal.astype(int).tolist()
        official = pt_min[(pt_min.jornada.isin(js)) & (pt_min.jugador.isin(sub_roster.jugador))].copy()
        advv = adv_all[(adv_all.jornada.isin(advanced_js)) & (adv_all.dorsal.astype(int).isin(dorsals))].copy() if advanced_js and not adv_all.empty else pd.DataFrame()

        total_minutes = int(official.minutos.sum()) if not official.empty else 0
        players_used = int(official.loc[official.minutos>0,"jugador"].nunique()) if not official.empty else 0
        goals = int(pt_ev[(pt_ev.jornada.isin(js)) & (pt_ev.jugador.isin(sub_roster.jugador)) & (pt_ev.tipo.isin(["gol","penalti_gol"]))].shape[0])
        shots = int(pd.to_numeric(advv.get("tiros", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not advv.empty else 0
        distance = float(pd.to_numeric(advv.get("distancia_km", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not advv.empty else 0

        st.markdown(f"""
        <div class='global-grid'>
          <div class='global-card'><div class='big'>{players_used}</div><div class='small'>Jugadores utilizados</div><div class='accent'>{_safe_html(view_label)}</div></div>
          <div class='global-card'><div class='big'>{total_minutes}</div><div class='small'>Minutos oficiales acumulados</div><div class='accent'>acta</div></div>
          <div class='global-card'><div class='big'>{goals}</div><div class='small'>Goles del grupo</div><div class='accent'>acta validada</div></div>
          <div class='global-card'><div class='big'>{shots if advanced_js else '—'}</div><div class='small'>Tiros detectados</div><div class='accent'>{'tracking' if advanced_js else 'pendiente de datos'}</div></div>
          <div class='global-card'><div class='big'>{str(round(distance,1)).replace('.',',') if advanced_js else '—'}{(' km' if advanced_js else '')}</div><div class='small'>Distancia rastreada</div><div class='accent'>{'tracking' if advanced_js else 'pendiente de datos'}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Comparativa entre jornadas con tracking (especialmente útil en Total).
        if jornada_ui == "Total" and len(advanced_js) >= 2:
            comp_days=sorted(advanced_js)
            metric_defs=[
                ('Distancia recorrida','distancia_km',' km','sum',1),
                ('Tiros detectados','tiros','','sum',0),
                ('Eventos detectados','eventos_totales','','sum',0),
                ('Ocasiones detectadas','ocasiones','','sum',0),
                ('Goles detectados','goles_video','','sum',0),
            ]
            cards=[]
            for lab,col,suf,how,dec in metric_defs:
                vals=[]
                for jj in comp_days:
                    fd=adv_all[(adv_all.jornada==jj)&(adv_all.dorsal.astype(int).isin(dorsals))].copy()
                    vals.append((jj,_num(fd,col,how)))
                cards.append(compare_metric_card(lab,vals,suf,dec))
            st.markdown("<div class='compare-wrap'><div class='compare-head'><div><div class='compare-title'>↔ Comparar jornadas</div><div class='compare-sub'>J2 vs Bétera · J3 vs Manises · J5 vs Alboraya. Misma escala dentro de cada métrica.</div></div></div><div class='compare-metrics'>"+''.join(cards)+"</div><div class='compare-foot'>Los valores son totales reales rastreados por partido. No se rellenan con cero las métricas que faltan y el /90 solo se calcula para jugadores con más de 70 minutos.</div></div>", unsafe_allow_html=True)

        # Rankings visuales.
        r1,r2,r3 = st.columns(3)
        def ranking_html(frame, col, label, suffix="", topn=5):
            if frame.empty or col not in frame.columns:
                return "<div class='ind-sub'>Sin datos avanzados todavía.</div>"
            t=frame.copy(); t[col]=pd.to_numeric(t[col],errors='coerce'); t=t.dropna(subset=[col])
            if t.empty: return "<div class='ind-sub'>Sin datos avanzados todavía.</div>"
            t=t.groupby('dorsal',as_index=False)[col].sum().sort_values(col,ascending=False).head(topn)
            mx=max(float(t[col].max()),1)
            rr=[]
            for pos,(_,x) in enumerate(t.iterrows(),1):
                d=int(x.dorsal); name=roster.loc[roster.dorsal.astype(int)==d,'jugador']
                nm=name.iloc[0] if not name.empty else f"#{d}"
                val=float(x[col]); vtxt=str(round(val,1)).replace('.',',') if not float(val).is_integer() else str(int(val))
                rr.append(f"<div class='rank-row'><div class='rank-num'>{pos}</div><div><div class='rank-name'>#{d} · {_safe_html(str(nm))}</div><div class='microbar'><span style='width:{min(100,val/mx*100):.1f}%'></span></div></div><div class='rank-value'>{vtxt}{suffix}</div></div>")
            return "<div class='rank-list'>"+''.join(rr)+"</div>"
        with r1:
            st.markdown(f"<div class='ind-panel'><div class='ind-title'>🏃 Distancia</div>{ranking_html(advv,'distancia_km','Distancia',' km')}</div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='ind-panel'><div class='ind-title'>🎯 Tiros</div>{ranking_html(advv,'tiros','Tiros')}</div>", unsafe_allow_html=True)
        with r3:
            st.markdown(f"<div class='ind-panel'><div class='ind-title'>📊 Eventos</div>{ranking_html(advv,'eventos_totales','Eventos')}</div>", unsafe_allow_html=True)

        # Comparación /90 solo para jugadores con más de 70 minutos.
        # No se aplican ponderaciones ni ajustes de muestra: simplemente se normaliza a 90 minutos.
        def ranking_per90_html(frame, col, suffix="", topn=5):
            if frame.empty or col not in frame.columns or official.empty:
                return "<div class='ind-sub'>Sin datos suficientes para calcular /90.</div>"
            vals = frame.copy()
            vals[col] = pd.to_numeric(vals[col], errors='coerce')
            vals = vals.dropna(subset=[col])
            if vals.empty:
                return "<div class='ind-sub'>Sin datos suficientes para calcular /90.</div>"
            vals = vals.groupby('dorsal', as_index=False)[col].sum()
            mins = official.groupby('jugador', as_index=False)['minutos'].sum()
            map_df = sub_roster[['dorsal','jugador']].copy()
            map_df['dorsal'] = map_df['dorsal'].astype(int)
            map_df = map_df.merge(mins, on='jugador', how='left')
            vals['dorsal'] = vals['dorsal'].astype(int)
            vals = vals.merge(map_df[['dorsal','minutos']], on='dorsal', how='left')
            vals['minutos'] = pd.to_numeric(vals['minutos'], errors='coerce').fillna(0)
            vals = vals[vals['minutos'] > 70].copy()
            if vals.empty:
                return "<div class='ind-sub'>Ningún jugador supera 70 minutos en esta selección.</div>"
            vals['per90'] = vals[col] * 90.0 / vals['minutos']
            vals = vals.sort_values('per90', ascending=False).head(topn)
            mx = max(float(vals['per90'].max()), 1e-9)
            rr=[]
            for pos,(_,x) in enumerate(vals.iterrows(),1):
                d=int(x.dorsal); name=roster.loc[roster.dorsal.astype(int)==d,'jugador']
                nm=name.iloc[0] if not name.empty else f"#{d}"
                val=float(x.per90); mins_i=int(round(float(x.minutos)))
                vtxt=str(round(val,1)).replace('.',',')
                rr.append(f"<div class='rank-row'><div class='rank-num'>{pos}</div><div><div class='rank-name'>#{d} · {_safe_html(str(nm))}</div><div class='microbar'><span style='width:{min(100,val/mx*100):.1f}%'></span></div><div class='ind-sub'>{mins_i}' jugados</div></div><div class='rank-value'>{vtxt}{suffix}<div class='ind-sub'>/90</div></div></div>")
            return "<div class='rank-list'>"+''.join(rr)+"</div>"

        # Minutos en formato heatmap visual, solo en Individual.
        st.markdown("<div style='height:10px'></div><div class='section-title'>Carga de minutos</div>", unsafe_allow_html=True)
        minute_cards=[]
        for _,r in sub_roster.iterrows():
            m=int(official.loc[official.jugador==r.jugador,'minutos'].sum()) if not official.empty else 0
            cap=90*len(js)
            pct=min(100,m/cap*100) if cap else 0
            avg=m/len(js) if js else 0
            if avg < 25: color='#ef4444'
            elif avg < 45: color='#f59e0b'
            elif avg < 60: color='#facc15'
            elif avg < 75: color='#86efac'
            else: color='#15803d'
            minute_cards.append(f"<div class='minute-card'><div class='top'><span>#{int(r.dorsal)} {_safe_html(str(r.jugador))}</span><span class='mins' style='color:{color}'>{m}'</span></div><div class='minbar'><span style='width:{pct:.1f}%;background:{color}'></span></div></div>")
        st.markdown("<div class='minutes-grid'>"+''.join(minute_cards)+"</div>", unsafe_allow_html=True)

        # Indicadores visuales del grupo: sustituyen la antigua tabla plana.
        st.markdown("<div style='height:12px'></div><div class='section-title'>Lectura rápida del grupo</div>", unsafe_allow_html=True)
        n_group=max(len(sub_roster),1)
        used_players=int(official.loc[official.minutos>0,'jugador'].nunique()) if not official.empty else 0
        starters_distinct=int(official.loc[official.titular==1,'jugador'].nunique()) if not official.empty else 0
        eligible70=int(official.groupby('jugador')['minutos'].sum().gt(70).sum()) if not official.empty else 0
        used_pct=used_players/n_group*100
        starter_pct=starters_distinct/n_group*100
        eligible_pct=(eligible70/used_players*100) if used_players else 0
        conv_pct=(goals/shots*100) if shots else 0

        def top3_share(frame,col):
            if frame.empty or col not in frame.columns:
                return 0.0
            x=frame.copy(); x[col]=pd.to_numeric(x[col],errors='coerce').fillna(0)
            g=x.groupby('dorsal')[col].sum().sort_values(ascending=False)
            total=float(g.sum())
            return float(g.head(3).sum()/total*100) if total>0 else 0.0

        min_by_player=official.groupby('jugador')['minutos'].sum().sort_values(ascending=False) if not official.empty else pd.Series(dtype=float)
        total_m=float(min_by_player.sum()) if not min_by_player.empty else 0.0
        top3_min_pct=float(min_by_player.head(3).sum()/total_m*100) if total_m>0 else 0.0
        top3_shot_pct=top3_share(advv,'tiros')
        top3_dist_pct=top3_share(advv,'distancia_km')

        donuts=[
            ('Plantilla utilizada',used_pct,'#1d63d8',f'{used_players}/{len(sub_roster)} jugadores con minutos'),
            ('Titulares distintos',starter_pct,'#7c3aed',f'{starters_distinct} jugadores han sido titulares'),
            ("Muestra >70'",eligible_pct,'#16a34a',f'{eligible70}/{used_players or 0} usados entran en /90'),
            ('Conversión',conv_pct,'#f59e0b',f'{goals} goles · {shots} tiros'),
            ('Núcleo de minutos',top3_min_pct,'#0ea5e9','% de minutos concentrado en los 3 que más juegan'),
            ('Núcleo físico',top3_dist_pct,'#ef4444','% de km concentrado en los 3 con más distancia'),
        ]
        donut_html=[]
        for lab,pct,col,sub in donuts:
            pct=max(0,min(100,float(pct)))
            donut_html.append(f"<div class='donut-card'><div class='donut' style='--p:{pct:.1f};--c:{col}'><div class='dv'>{pct:.0f}%</div></div><div class='donut-copy'><div class='donut-label'>{_safe_html(lab)}</div><div class='donut-sub'>{_safe_html(sub)}</div></div></div>")
        st.markdown("<div class='visual-insights'>"+''.join(donut_html)+"</div>",unsafe_allow_html=True)

        # Líderes del bloque seleccionado: lectura directa, sin tabla.
        def leader_from_official(metric='minutos'):
            if official.empty:
                return None,None,None
            if metric=='minutos':
                g=official.groupby('jugador')['minutos'].sum().sort_values(ascending=False)
                if g.empty:return None,None,None
                name=str(g.index[0]); val=float(g.iloc[0]); suffix="'"
            else:
                return None,None,None
            rr=sub_roster[sub_roster.jugador==name]
            d=int(rr.iloc[0].dorsal) if not rr.empty else 0
            return d,name,f"{int(val)}{suffix}"

        def leader_from_adv(col,suffix='',dec=0):
            if advv.empty or col not in advv.columns:return None,None,None
            t=advv.copy(); t[col]=pd.to_numeric(t[col],errors='coerce').fillna(0)
            g=t.groupby('dorsal')[col].sum().sort_values(ascending=False)
            if g.empty or float(g.iloc[0])<=0:return None,None,None
            d=int(g.index[0]); nm=roster.loc[roster.dorsal.astype(int)==d,'jugador']; name=str(nm.iloc[0]) if not nm.empty else f'#{d}'
            val=float(g.iloc[0]); txt=(f"{val:.{dec}f}" if dec else str(int(round(val)))).replace('.',',')+suffix
            return d,name,txt

        lm=leader_from_official('minutos'); ld=leader_from_adv('distancia_km',' km',1); ls=leader_from_adv('tiros','',0)
        leader_specs=[('Más minutos','⏱️',lm,'Continuidad competitiva'),('Más distancia','🏃',ld,'Carga física acumulada'),('Más tiros','🎯',ls,'Amenaza ofensiva')]
        leader_cards=[]
        for title,ico,item,meta in leader_specs:
            d,nm,val=item
            if nm is None:
                nm='Sin datos'; val='—'; d=0
            leader_cards.append(f"<div class='leader-card'><div class='leader-icon'>{ico}</div><div class='leader-kicker'>{_safe_html(title)}</div><div class='leader-name'>{('#'+str(d)+' · ') if d else ''}{_safe_html(str(nm))}</div><div class='leader-value'>{_safe_html(str(val))}</div><div class='leader-meta'>{_safe_html(meta)}</div></div>")
        st.markdown("<div class='leader-grid'>"+''.join(leader_cards)+"</div>",unsafe_allow_html=True)

        # Matriz visual de impacto: heatmap interno del grupo seleccionado.
        st.markdown("<div class='section-title'>Matriz de impacto</div>", unsafe_allow_html=True)
        mdf=sub_roster[['dorsal','jugador','rol']].copy()
        mdf['dorsal']=mdf['dorsal'].astype(int)
        if not official.empty:
            mo=official.groupby('jugador',as_index=False).agg(Min=('minutos','sum'),Tit=('titular','sum'))
            mdf=mdf.merge(mo,on='jugador',how='left')
        else:
            mdf['Min']=0; mdf['Tit']=0
        mdf[['Min','Tit']]=mdf[['Min','Tit']].fillna(0)
        if not advv.empty:
            aa=advv.copy()
            for cc in ['distancia_km','tiros','goles_video','eventos_totales','velocidad_max_kmh','minutos_rastreados']:
                if cc not in aa.columns: aa[cc]=pd.NA
                aa[cc]=pd.to_numeric(aa[cc],errors='coerce')
            ag=aa.groupby('dorsal',as_index=False).agg(Km=('distancia_km','sum'),Tiros=('tiros','sum'),Goles=('goles_video','sum'),Eventos=('eventos_totales','sum'),Vmax=('velocidad_max_kmh','max'),TrackMin=('minutos_rastreados','sum'))
            ag['dorsal']=ag['dorsal'].astype(int)
            mdf=mdf.merge(ag,on='dorsal',how='left')
        for cc in ['Km','Tiros','Goles','Eventos','Vmax','TrackMin']:
            if cc not in mdf.columns: mdf[cc]=0
            mdf[cc]=pd.to_numeric(mdf[cc],errors='coerce').fillna(0)
        mdf['Conv']=mdf.apply(lambda r:(r.Goles/r.Tiros*100) if r.Tiros>0 else 0,axis=1)
        mdf['Km90']=mdf.apply(lambda r:(r.Km*90/(r.TrackMin if r.TrackMin>70 else r.Min)) if ((r.TrackMin>70 or r.Min>70) and r.Km>0) else None,axis=1)
        # Índice de actividad interno: promedio de percentiles de minutos, km y eventos. No es una nota de rendimiento.
        for cc in ['Min','Km','Eventos']:
            mdf[cc+'_pct']=mdf[cc].rank(pct=True,method='average')*100 if len(mdf)>1 else 100
        mdf['Actividad']=(mdf['Min_pct']+mdf['Km_pct']+mdf['Eventos_pct'])/3

        def cell_bg(v, series, hue='blue'):
            try: v=float(v)
            except: return '#f8fafc'
            vals=pd.to_numeric(series,errors='coerce').dropna()
            if vals.empty or float(vals.max())==float(vals.min()): q=.45
            else: q=(v-float(vals.min()))/(float(vals.max())-float(vals.min()))
            q=max(0,min(1,q))
            palettes={
                'blue':(239,246,255,29,99,216), 'green':(240,253,244,22,163,74),
                'orange':(255,247,237,234,88,12), 'purple':(250,245,255,124,58,237),
                'red':(254,242,242,220,38,38)
            }
            a,b,c,d,e,f=palettes[hue]
            t=.10+.28*q
            rr=int(a+(d-a)*t); gg=int(b+(e-b)*t); bb=int(c+(f-c)*t)
            return f'rgb({rr},{gg},{bb})'

        role_short={'POR':'POR','DEF':'DEF','MED':'MED','DEL':'DEL'}

        # Orden interactivo de la matriz. El usuario puede cambiar el criterio sin salir del resumen.
        sort_labels={
            'Dorsal':'dorsal',
            'Jugador':'jugador',
            'Posición':'rol',
            'Minutos':'Min',
            'Km':'Km',
            'Km/90':'Km90',
            'Tiros':'Tiros',
            'Goles':'Goles',
            'Conversión':'Conv',
            'Eventos':'Eventos',
            'Vel. máxima':'Vmax',
            'Actividad':'Actividad',
        }
        sc1,sc2=st.columns([2.2,1.1])
        with sc1:
            sort_label=st.selectbox('Ordenar matriz por', list(sort_labels.keys()), index=3, key='impact_sort_by')
        with sc2:
            sort_dir=st.radio('Orden', ['Mayor → menor','Menor → mayor'], horizontal=True, key='impact_sort_dir')
        sort_col=sort_labels[sort_label]
        ascending=(sort_dir=='Menor → mayor')
        # NaN (por ejemplo Km/90 con <=70 min) siempre al final para no distorsionar la lectura.
        mdf_sorted=mdf.sort_values(sort_col, ascending=ascending, na_position='last', kind='mergesort')

        rows=[]
        for _,r in mdf_sorted.iterrows():
            d=int(r.dorsal)
            # mini tendencia de km J2/J3/J5
            vals=[]
            for jj in [2,3,5]:
                z=advv[(advv.dorsal.astype(int)==d)&(advv.jornada.astype(int)==jj)] if not advv.empty else pd.DataFrame()
                vv=float(pd.to_numeric(z['distancia_km'],errors='coerce').sum()) if (not z.empty and 'distancia_km' in z.columns) else 0.0
                vals.append(vv)
            vmax=max(vals+[0.01])
            bars=''.join([f"<span title='J{jj}: {vv:.1f} km' style='height:{max(3,vv/vmax*24):.1f}px'></span>" for jj,vv in zip([2,3,5],vals)])
            km90='—' if pd.isna(r.Km90) else f"{r.Km90:.1f}".replace('.',',')
            act=float(r.Actividad); acol='#16a34a' if act>=67 else ('#f59e0b' if act>=40 else '#ef4444')
            rows.append(
                f"<tr><td class='impact-player'><span class='impact-pos'>#{d}</span>{_safe_html(str(r.jugador))}</td>"
                f"<td>{_safe_html(role_short.get(str(r.rol),str(r.rol)))}</td>"
                f"<td><span class='impact-cell' style='background:{cell_bg(r.Min,mdf.Min,'blue')}'>{int(r.Min)}</span></td>"
                f"<td><span class='impact-cell' style='background:{cell_bg(r.Km,mdf.Km,'green')}'>{str(round(r.Km,1)).replace('.',',')}</span></td>"
                f"<td>{km90}</td>"
                f"<td><span class='impact-cell' style='background:{cell_bg(r.Tiros,mdf.Tiros,'orange')}'>{int(r.Tiros)}</span></td>"
                f"<td><span class='impact-cell' style='background:{cell_bg(r.Goles,mdf.Goles,'green')}'>{int(r.Goles)}</span></td>"
                f"<td>{str(round(r.Conv,1)).replace('.',',')}%</td>"
                f"<td><span class='impact-cell' style='background:{cell_bg(r.Eventos,mdf.Eventos,'purple')}'>{int(r.Eventos)}</span></td>"
                f"<td>{('—' if r.Vmax<=0 else str(round(r.Vmax,1)).replace('.',','))}</td>"
                f"<td><div class='trend-mini'>{bars}</div></td>"
                f"<td><span class='activity-pill'><span class='activity-dot' style='background:{acol}'></span>{act:.0f}</span></td></tr>"
            )
        matrix_html=("<div class='impact-wrap'><div class='impact-head'><div><div class='impact-title'>Mapa comparativo del grupo</div><div class='impact-sub'>El color compara a los jugadores dentro de la selección actual. Km/90 aparece solo con más de 70 minutos; para carga física usa minutos rastreados cuando están disponibles.</div></div><div class='impact-legend'>Actividad = percentiles de minutos + km + eventos</div></div>"
                     "<table class='impact-table'><thead><tr><th>Jugador</th><th>Pos.</th><th>Min</th><th>Km</th><th>Km/90</th><th>Tiros</th><th>Goles</th><th>Conv.</th><th>Eventos</th><th>V. máx</th><th>Km J2·J3·J5</th><th>Actividad</th></tr></thead><tbody>"+''.join(rows)+"</tbody></table></div>")
        st.markdown(matrix_html,unsafe_allow_html=True)

        # Resumen por jornada con J2, J3 y J5 presentes.
        st.markdown("<div class='section-title'>Pulso de las jornadas</div>", unsafe_allow_html=True)
        jc=[]
        for jj,label in [(2,'Bétera'),(3,'Manises'),(5,'Alboraya')]:
            a=advv[advv.jornada.astype(int)==jj].copy() if not advv.empty else pd.DataFrame()
            km=float(pd.to_numeric(a['distancia_km'],errors='coerce').sum()) if (not a.empty and 'distancia_km' in a.columns) else 0
            tirosj=int(pd.to_numeric(a['tiros'],errors='coerce').sum()) if (not a.empty and 'tiros' in a.columns) else 0
            evj=int(pd.to_numeric(a['eventos_totales'],errors='coerce').sum()) if (not a.empty and 'eventos_totales' in a.columns) else 0
            gj=int(pd.to_numeric(a['goles_video'],errors='coerce').sum()) if (not a.empty and 'goles_video' in a.columns) else 0
            mj=int(official.loc[official.jornada.astype(int)==jj,'minutos'].sum()) if (not official.empty and 'jornada' in official.columns) else 0
            jc.append(f"<div class='journey-card'><div class='journey-k'>Jornada {jj} · vs {label}</div><div class='journey-v'>{str(round(km,1)).replace('.',',')} km</div><div class='journey-meta'>Carga total rastreada del grupo seleccionado</div><div class='journey-row'><div class='journey-stat'><b>{mj}</b><span>min</span></div><div class='journey-stat'><b>{tirosj}</b><span>tiros</span></div><div class='journey-stat'><b>{gj}</b><span>goles</span></div><div class='journey-stat'><b>{evj}</b><span>eventos</span></div></div></div>")
        st.markdown("<div class='journey-strip'>"+''.join(jc)+"</div>",unsafe_allow_html=True)

        st.caption("Pulsa directamente sobre un jugador para abrir su ficha individual. La matriz usa datos reales cargados; el índice de actividad es una comparación interna de volumen, no una nota de rendimiento.")
        return

    # ---------- FICHA INDIVIDUAL ----------
    pr = roster[roster.jugador==player]
    if pr.empty:
        st.session_state.ind_selected_player=None
        st.rerun()
    dorsal=int(pr.iloc[0].dorsal); rol=str(pr.iloc[0].rol); pos_label=role_name.get(rol,'Jugador')
    pm=pt_min[(pt_min.jugador==player)&(pt_min.jornada.isin(js))].copy()
    pe=pt_ev[(pt_ev.jugador==player)&(pt_ev.jornada.isin(js))].copy()
    minutes=int(pm.minutos.sum()) if not pm.empty else 0
    starts=int(pm.titular.sum()) if not pm.empty else 0
    appearances=int((pm.minutos>0).sum()) if not pm.empty else 0
    goals=int(pe.tipo.isin(['gol','penalti_gol']).sum()) if not pe.empty else 0
    yellows=int((pe.tipo=='amarilla').sum()) if not pe.empty else 0
    expulsions=int(pe.tipo.isin(['doble_amarilla','segunda_amarilla','roja']).sum()) if not pe.empty else 0
    av=adv_all[(adv_all.jornada.isin(advanced_js))&(adv_all.dorsal.astype(int)==dorsal)].copy() if advanced_js and not adv_all.empty else pd.DataFrame()

    if st.button("← Volver al resumen", key="back_individual"):
        st.session_state.ind_selected_player=None
        st.rerun()

    left,right=st.columns([1.0,2.35])
    with left:
        logo=BASE/'primer_toque_logo.png'; logo_tag=''
        if logo.exists():
            b64=_b64_file(str(logo)); logo_tag=f"<img src='data:image/png;base64,{b64}' style='width:58px;height:58px;object-fit:contain;float:right;background:white;border-radius:12px;padding:5px'>"
        status='Titular' if starts else ('Suplente utilizado' if minutes else 'Sin minutos')
        st.markdown(f"<div class='ind-hero'>{logo_tag}<div class='shirt-no'>#{dorsal}</div><div class='pname'>{_safe_html(player)}</div><span class='pos'>{_safe_html(pos_label)}</span><div class='meta'><b>{_safe_html(view_label)}</b><br>{status} · {minutes} min oficiales<br>{appearances} apariciones · {starts} titularidades</div></div>",unsafe_allow_html=True)
    with right:
        def metric_available(col, how='sum'):
            # Usa todos los valores realmente disponibles en la vista actual.
            # No exige que la métrica exista en todas las jornadas: así los cuadros
            # superiores reflejan exactamente lo mismo que los paneles Técnico/Físico.
            if av.empty or col not in av.columns:
                return None
            x = pd.to_numeric(av[col], errors='coerce')
            valid = x.dropna()
            if valid.empty:
                return None
            if how == 'max':
                return float(valid.max())
            if how == 'mean':
                return float(valid.mean())
            return float(valid.sum())

        def metric_sample_minutes(col):
            """Minutos oficiales solo de las jornadas donde existe esa métrica."""
            if av.empty or col not in av.columns or pm.empty:
                return 0
            vv = av.copy()
            vv['_metric'] = pd.to_numeric(vv[col], errors='coerce')
            days = sorted(set(pd.to_numeric(vv.loc[vv['_metric'].notna(), 'jornada'], errors='coerce').dropna().astype(int).tolist()))
            if not days:
                return 0
            return int(pd.to_numeric(pm.loc[pm.jornada.astype(int).isin(days), 'minutos'], errors='coerce').fillna(0).sum())

        def weighted_speed_mean():
            if av.empty or 'velocidad_media_kmh' not in av.columns:
                return None
            vals = pd.to_numeric(av['velocidad_media_kmh'], errors='coerce')
            ok = vals.notna()
            if not ok.any():
                return None
            if 'minutos_rastreados' in av.columns:
                w = pd.to_numeric(av['minutos_rastreados'], errors='coerce')
                wok = ok & w.notna() & (w > 0)
                if wok.any() and float(w[wok].sum()) > 0:
                    return float((vals[wok] * w[wok]).sum() / w[wok].sum())
            return float(vals[ok].mean())

        dist=metric_available('distancia_km','sum')
        shots_raw=metric_available('tiros','sum')
        shots=int(shots_raw) if shots_raw is not None else None
        occasions_raw=metric_available('ocasiones','sum')
        occasions=int(occasions_raw) if occasions_raw is not None else None
        hi_raw=metric_available('carreras_alta_intensidad','sum')
        hi=int(hi_raw) if hi_raw is not None else None
        sprints_raw=metric_available('sprints','sum')
        sprints=int(sprints_raw) if sprints_raw is not None else None
        events_raw=metric_available('eventos_totales','sum')
        events_track=int(events_raw) if events_raw is not None else None
        vmax=metric_available('velocidad_max_kmh','max')
        vavg=weighted_speed_mean()
        pass_ok=int(pd.to_numeric(av.get('pases_exitosos',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av.empty and 'pases_exitosos' in av.columns and pd.to_numeric(av['pases_exitosos'],errors='coerce').notna().any() else None
        conversion = (goals / shots * 100.0) if shots not in (None,0) else None

        # /90: cada métrica usa solo los minutos de las jornadas donde esa métrica
        # está realmente disponible. Así no dividimos, por ejemplo, sprints de J2+J5
        # entre minutos de J2+J3+J5 si J3 no trae sprints.
        def per90_metric(value, col):
            if value is None:
                return None
            sample_min = metric_sample_minutes(col)
            if sample_min <= 70:
                return None
            return float(value) * 90.0 / sample_min

        eligible90 = minutes > 70
        dist90 = per90_metric(dist, 'distancia_km')
        hi90 = per90_metric(hi, 'carreras_alta_intensidad')
        sprints90 = per90_metric(sprints, 'sprints')
        shots90 = per90_metric(shots, 'tiros')
        occasions90 = per90_metric(occasions, 'ocasiones')
        events90 = per90_metric(events_track, 'eventos_totales')
        goals90 = (goals * 90.0 / minutes) if minutes > 70 else None
        st.markdown(f"""<div class='summary-panel'><div class='ind-title'>Resumen del jugador</div><div class='summary-grid'>
        <div class='summary-kpi blue'><div class='ico'>⏱️</div><div class='sv'>{minutes}'</div><div class='sl'>Minutos</div></div>
        <div class='summary-kpi green'><div class='ico'>⚽</div><div class='sv'>{goals}</div><div class='sl'>Goles</div></div>
        <div class='summary-kpi blue'><div class='ico'>🎯</div><div class='sv'>{shots if shots is not None else '—'}</div><div class='sl'>Tiros</div></div>
        <div class='summary-kpi blue'><div class='ico'>◎</div><div class='sv'>{occasions if occasions is not None else '—'}</div><div class='sl'>Ocasiones</div></div>
        <div class='summary-kpi green'><div class='ico'>🏃</div><div class='sv'>{(str(round(dist,1)).replace('.',',')+' km') if dist is not None else '—'}</div><div class='sl'>Distancia</div></div>
        <div class='summary-kpi red'><div class='ico'>💨</div><div class='sv'>{sprints if sprints is not None else '—'}</div><div class='sl'>Sprints</div></div>
        <div class='summary-kpi orange'><div class='ico'>🔥</div><div class='sv'>{hi if hi is not None else '—'}</div><div class='sl'>Alta intensidad</div></div>
        <div class='summary-kpi blue'><div class='ico'>📊</div><div class='sv'>{events_track if events_track is not None else '—'}</div><div class='sl'>Eventos</div></div>
        <div class='summary-kpi green'><div class='ico'>🧭</div><div class='sv'>{(str(round(vavg,1)).replace('.',',')+' km/h') if vavg is not None else '—'}</div><div class='sl'>Vel. media</div></div>
        <div class='summary-kpi green'><div class='ico'>⚡</div><div class='sv'>{(str(round(vmax,1)).replace('.',',')+' km/h') if vmax is not None else '—'}</div><div class='sl'>Vel. máxima</div></div>
        <div class='summary-kpi orange'><div class='ico'>🟨</div><div class='sv'>{yellows}</div><div class='sl'>Amarillas</div></div>
        <div class='summary-kpi red'><div class='ico'>🟥</div><div class='sv'>{expulsions}</div><div class='sl'>Expulsiones</div></div>
        <div class='summary-kpi green'><div class='ico'>📈</div><div class='sv'>{(str(round(conversion,1)).replace('.',',')+'%') if conversion is not None else '—'}</div><div class='sl'>Conversión</div></div>
        </div></div>""",unsafe_allow_html=True)

        def fmt90(v, suffix=''):
            if v is None:
                return '—'
            txt = str(round(float(v),1)).replace('.',',')
            return txt + suffix

        if eligible90:
            st.markdown(f"""<div class='ind-panel' style='margin-top:9px'><div class='ind-title'>Por 90 minutos</div><div class='ind-sub'>Cada métrica usa solo los minutos de las jornadas donde ese dato está disponible. Se muestra cuando esa muestra supera 70 minutos.</div><div class='per90-grid'>
            <div class='per90-card p90-dist'><div class='pi'>🏃</div><div class='v'>{fmt90(dist90,' km')}</div><div class='l'>Distancia /90</div><div class='meter'><span style='width:{min(100,(dist90 or 0)/12*100):.1f}%'></span></div></div>
            <div class='per90-card p90-hi'><div class='pi'>🔥</div><div class='v'>{fmt90(hi90)}</div><div class='l'>Alta intensidad /90</div><div class='meter'><span style='width:{min(100,(hi90 or 0)/50*100):.1f}%'></span></div></div>
            <div class='per90-card p90-sprint'><div class='pi'>💨</div><div class='v'>{fmt90(sprints90)}</div><div class='l'>Sprints /90</div><div class='meter'><span style='width:{min(100,(sprints90 or 0)/30*100):.1f}%'></span></div></div>
            <div class='per90-card p90-shot'><div class='pi'>🎯</div><div class='v'>{fmt90(shots90)}</div><div class='l'>Tiros /90</div><div class='meter'><span style='width:{min(100,(shots90 or 0)/6*100):.1f}%'></span></div></div>
            <div class='per90-card p90-shot'><div class='pi'>◎</div><div class='v'>{fmt90(occasions90)}</div><div class='l'>Ocasiones /90</div><div class='meter'><span style='width:{min(100,(occasions90 or 0)/8*100):.1f}%'></span></div></div>
            <div class='per90-card p90-goal'><div class='pi'>⚽</div><div class='v'>{fmt90(goals90)}</div><div class='l'>Goles /90</div><div class='meter'><span style='width:{min(100,(goals90 or 0)/2*100):.1f}%'></span></div></div>
            <div class='per90-card p90-event'><div class='pi'>📊</div><div class='v'>{fmt90(events90)}</div><div class='l'>Eventos /90</div><div class='meter'><span style='width:{min(100,(events90 or 0)/20*100):.1f}%'></span></div></div>
            </div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ind-panel' style='margin-top:9px'><div class='ind-title'>Por 90 minutos</div><div class='ind-sub'>No se muestra /90: {minutes}' jugados. Se requiere superar 70 minutos para evitar proyecciones poco representativas.</div></div>", unsafe_allow_html=True)

    # Resumen técnico, físico y de eventos justo debajo del bloque /90.
    c1,c2,c3=st.columns([1.1,1.1,1])
    with c1:
        tech_rows=[]
        if not av.empty:
            tech_vals=[('🎯','Ocasiones',occasions,6),('🥅','Tiros',shots,6),('📊','Eventos',events_track,20),('✅','Pases exitosos',pass_ok,80)]
            for ico,lab,val,scale in tech_vals:
                if val is not None:
                    fval=float(val)
                    txt=str(int(fval)) if fval.is_integer() else str(round(fval,1)).replace('.',',')
                    w=min(100,fval/scale*100) if scale else 0
                    tech_rows.append(f"<div class='metric-row'><div class='metric-ico'>{ico}</div><div class='metric-name'>{lab}</div><div class='metric-val'>{txt}</div><div class='metric-subbar'><span style='width:{w:.1f}%'></span></div></div>")
            tech_rows.append(f"<div class='metric-row'><div class='metric-ico'>⚽</div><div class='metric-name'>Goles detectados</div><div class='metric-val'>{goals}</div><div class='metric-subbar'><span style='width:{min(100,goals/3*100):.1f}%'></span></div></div>")
            conv_txt=(str(round(conversion,1)).replace('.',',')+'%') if conversion is not None else '—'
            conv_w=min(100,conversion or 0)
            tech_rows.append(f"<div class='metric-row'><div class='metric-ico'>📈</div><div class='metric-name'>Conversión tiros → gol</div><div class='metric-val'>{conv_txt}</div><div class='metric-subbar'><span style='width:{conv_w:.1f}%'></span></div></div>")
        body=''.join(tech_rows) if tech_rows else "<div class='ind-sub' style='padding:10px 0'>Sin métricas técnicas de tracking para esta jornada.</div>"
        st.markdown(f"<div class='metric-panel'><div class='metric-head tech'>⚽ Técnico</div>{body}</div>",unsafe_allow_html=True)
    with c2:
        phys_rows=[]
        if not av.empty:
            phys_vals=[('🏃','Distancia',dist,' km',12),('🧭','Vel. media',vavg,' km/h',12),('⚡','Vel. máxima',vmax,' km/h',36),('💨','Sprints',sprints,'',35),('🔥','Alta intensidad',hi,'',50)]
            for ico,lab,val,suf,scale in phys_vals:
                if val is not None:
                    fval=float(val)
                    txt=(str(int(fval)) if fval.is_integer() else str(round(fval,1)).replace('.',','))+suf
                    w=min(100,fval/scale*100) if scale else 0
                    phys_rows.append(f"<div class='metric-row'><div class='metric-ico'>{ico}</div><div class='metric-name'>{lab}</div><div class='metric-val'>{txt}</div><div class='metric-subbar'><span style='width:{w:.1f}%'></span></div></div>")
        body=''.join(phys_rows) if phys_rows else "<div class='ind-sub' style='padding:10px 0'>Sin métricas físicas todavía.</div>"
        st.markdown(f"<div class='metric-panel phys'><div class='metric-head phys'>🏃 Físico</div>{body}</div>",unsafe_allow_html=True)
    with c3:
        evrows=[]
        if not pe.empty:
            ico={'gol':'⚽','penalti_gol':'⚽','amarilla':'🟨','doble_amarilla':'🟨🟥','segunda_amarilla':'🟨🟥','roja':'🟥'}
            for _,e in pe.sort_values(['jornada','minuto']).iterrows():
                evrows.append(f"<div class='event-row'><div class='event-dot'>{ico.get(str(e.tipo),'•')}</div><div class='event-text'>J{int(e.jornada)} · {_safe_html(str(e.tipo).replace('_',' '))}</div><div class='event-min'>{int(e.minuto)}'</div></div><div class='event-line'></div>")
        body=''.join(evrows) if evrows else "<div class='ind-sub' style='padding:10px 0'>Sin goles o tarjetas en esta vista.</div>"
        st.markdown(f"<div class='metric-panel'><div class='metric-head events'>🧾 Eventos</div><div class='event-timeline'>{body}</div></div>",unsafe_allow_html=True)


    # Comparativa del jugador jornada a jornada.
    if jornada_ui == "Total" and len(advanced_js) >= 2:
        comp_days=sorted(advanced_js)
        fixtures={2:'vs Bétera',3:'vs Manises',5:'vs Alboraya'}
        day_cards=[]
        metric_rows=[]
        metric_defs=[
            ('Distancia','distancia_km',' km','sum',1),
            ('Tiros','tiros','', 'sum',0),
            ('Eventos','eventos_totales','', 'sum',0),
            ('Ocasiones','ocasiones','', 'sum',0),
            ('Goles detectados','goles_video','', 'sum',0),
        ]
        # Tarjeta compacta por jornada.
        for jj in comp_days:
            fd=adv_all[(adv_all.jornada==jj)&(adv_all.dorsal.astype(int)==dorsal)].copy()
            mm_df=pt_min[(pt_min.jornada==jj)&(pt_min.jugador==player)]
            mm=int(mm_df.minutos.sum()) if not mm_df.empty else 0
            dist_j=_num(fd,'distancia_km','sum'); shots_j=_num(fd,'tiros','sum'); ev_j=_num(fd,'eventos_totales','sum')
            day_cards.append(f"<div class='day-card'><div class='j'>Jornada {jj}</div><div class='fixture'>{_safe_html(fixtures.get(jj,''))} · {mm}' oficiales</div><div class='vals'><div class='day-mini'><b>{_fmt(dist_j,' km',1)}</b><span>Distancia</span></div><div class='day-mini'><b>{_fmt(shots_j,'',0)}</b><span>Tiros</span></div><div class='day-mini'><b>{_fmt(ev_j,'',0)}</b><span>Eventos</span></div></div></div>")
        for lab,col,suf,how,dec in metric_defs:
            vals=[]
            for jj in comp_days:
                fd=adv_all[(adv_all.jornada==jj)&(adv_all.dorsal.astype(int)==dorsal)].copy()
                vals.append((jj,_num(fd,col,how)))
            metric_rows.append(compare_metric_card(lab,vals,suf,dec))
        st.markdown("<div class='compare-wrap'><div class='compare-head'><div><div class='compare-title'>📈 Evolución entre jornadas</div><div class='compare-sub'>Compara J2, J3 y J5 con la misma escala por métrica y sin inventar valores ausentes.</div></div></div><div class='day-cards'>"+''.join(day_cards)+"</div><div class='compare-metrics' style='margin-top:10px'>"+''.join(metric_rows)+"</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    maps_dir=BASE/'individual_maps'
    map_days = advanced_js if jornada_ui == "Total" else advanced_js
    if jornada_ui == "Total":
        st.markdown("<div class='section-title'>Mapas por jornada</div>", unsafe_allow_html=True)
    for map_j in map_days:
        if jornada_ui == "Total":
            st.markdown(f"<div class='section-kicker'>Jornada {map_j}</div>", unsafe_allow_html=True)
        m1,m2=st.columns(2)
        heat=maps_dir/f"heat_j{map_j}_{dorsal}.png"
        shot=maps_dir/f"shots_j{map_j}_{dorsal}.png"
        av_day=adv_all[(adv_all.jornada==map_j)&(adv_all.dorsal.astype(int)==dorsal)] if not adv_all.empty else pd.DataFrame()
        shots_day=int(pd.to_numeric(av_day.get('tiros',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av_day.empty else None
        with m1:
            st.markdown("<div class='map-shell'><div class='map-label'>🔥 Mapa de calor</div>",unsafe_allow_html=True)
            if heat.exists():
                st.markdown(map_image_html(heat, f"Mapa de calor J{map_j} {player}"), unsafe_allow_html=True)
                st.caption(f"Captura del tracking Veo · J{map_j}")
            else:
                st.markdown("<div class='map-empty'>Mapa todavía no extraído para este jugador/jornada.</div>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with m2:
            st.markdown("<div class='map-shell'><div class='map-label'>🎯 Mapa de tiros</div>",unsafe_allow_html=True)
            if shot.exists():
                st.markdown(map_image_html(shot, f"Mapa de tiros J{map_j} {player}"), unsafe_allow_html=True)
                st.caption(f"Campo completo · portería de ataque visible · J{map_j}")
            elif shots_day == 0:
                st.markdown("<div class='map-empty'>0 tiros detectados en esta jornada.</div>",unsafe_allow_html=True)
            else:
                st.markdown("<div class='map-empty'>Hay acciones registradas, pero el mapa específico todavía no está extraído.</div>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
    if not map_days:
        st.markdown("<div class='map-empty'>Sin tracking avanzado para esta jornada.</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    a,b=st.columns([1.2,1])
    with a:
        # Evolución de minutos solo J2/J3/J5, con color por carga.
        cards=[]
        for jj in [2,3,5]:
            rr=pt_min[(pt_min.jugador==player)&(pt_min.jornada==jj)]
            mm=int(rr.minutos.sum()) if not rr.empty else 0
            if mm <25: col='#ef4444'
            elif mm<45: col='#f59e0b'
            elif mm<60: col='#facc15'
            elif mm<75: col='#86efac'
            else: col='#15803d'
            cards.append(f"<div class='minute-card'><div class='top'><span>J{jj}</span><span class='mins' style='color:{col}'>{mm}'</span></div><div class='minbar'><span style='width:{min(100,mm/90*100):.1f}%;background:{col}'></span></div></div>")
        st.markdown("<div class='ind-panel'><div class='ind-title'>⏱️ Minutos · partidos de casa</div><div class='minutes-grid'>"+''.join(cards)+"</div><div class='ind-sub' style='margin-top:8px'>Rojo 0–25 · naranja 25–45 · amarillo 45–60 · verde claro 60–75 · verde oscuro 75–90.</div></div>",unsafe_allow_html=True)
    with b:
        day_blocks=''
        fixture_names={2:'Primer Toque C.F. 2–0 Bétera C.F.',3:'Primer Toque C.F. 2–1 Manises C.F.',5:'Primer Toque C.F. 1–2 Alboraya U.D.'}
        for link_j in js:
            link=match_link(team,link_j)
            if not link:
                continue
            goals_day=pt_ev[(pt_ev.jornada==link_j)&(pt_ev.jugador==player)&(pt_ev.tipo.isin(['gol','penalti_gol']))].sort_values('minuto')
            goal_html=''
            if not goals_day.empty:
                for _,e in goals_day.iterrows():
                    sync = VEO_GOAL_SYNC.get((int(link_j), str(player)))
                    if sync is not None:
                        ffcv_min = int(sync.get("ffcv_min", int(e.minuto)))
                        veo_clock = str(sync.get("veo_match_clock", "—"))
                        video_ts = str(sync.get("video_timestamp", "—"))
                        event_url = sync.get("event_url")
                        # Si tenemos URL específica del evento, abrimos el evento. Si no, abrimos el partido completo
                        # y mostramos el timestamp absoluto validado para localizar el gol sin inventar un enlace de salto.
                        clip_url = event_url or link
                        goal_html += (
                            f"<div class='video-goal'>⚽ <b>{_safe_html(player)}</b><br>"
                            f"<span>Acta FFCV: <b>{ffcv_min}'</b> · reloj Veo: <b>{_safe_html(veo_clock)}</b> · vídeo: <b>{_safe_html(video_ts)}</b></span><br>"
                            f"<a href='{_safe_html(clip_url,quote=True)}' target='_blank'>▶ {'Ver evento del gol' if event_url else 'Abrir partido en Veo'} · vídeo {_safe_html(video_ts)}</a></div>"
                        )
                    else:
                        goal_html += (
                            f"<div class='video-goal'>⚽ <b>{_safe_html(player)}</b> · acta FFCV {int(e.minuto)}' "
                            f"<span style='opacity:.72'>· sincronización Veo pendiente</span></div>"
                        )
            else:
                goal_html="<div class='video-goal' style='opacity:.72'>Sin gol del jugador en esta jornada.</div>"
            day_blocks+=f"<div class='video-day'><div class='video-day-title'>Jornada {link_j} · {fixture_names.get(link_j,'Partido')}</div><a href='{_safe_html(link,quote=True)}' target='_blank'>▶ Ver partido completo</a>{goal_html}</div>"
        if not day_blocks:
            day_blocks="<span class='source-muted'>Sin enlaces específicos en esta vista.</span>"
        st.markdown(f"<div class='source-card'><div style='font-weight:950;font-size:.92rem'>🎥 Fuentes de vídeo</div><div class='source-muted'>Cada jornada muestra el partido y, debajo, los goles del jugador. Distinguimos: minuto del acta FFCV, reloj/evento de partido en Veo y timestamp absoluto del vídeo completo. El timestamp absoluto es la referencia para localizar el gol dentro del vídeo.</div>{day_blocks}</div>",unsafe_allow_html=True)


# ---------------- Resumen de liga / portadas ----------------
def clean_name(name):
    """Nombre corto y seguro para HTML. Evita el NameError de versiones anteriores."""
    out = str(name or "").strip()
    for suffix in [" 'A'", " 'B'", " 'C'", " 'D'"]:
        out = out.replace(suffix, "")
    return out


def _team_logo_path(team):
    logos = {
        "Bétera C.F. 'A'": BASE / "betera_logo.png",
        "C.D. Acero 'A'": BASE / "acero_logo.png",
        "Primer Toque C.F. 'A'": BASE / "primer_toque_logo.png",
        "C.F. At. Burriana - Salesianos 'A'": BASE / "salesianos_logo.png",
        "Villarreal C.F. 'C'": BASE / "villarreal_logo.png",
        "Alboraya U.D. 'B'": BASE / "alboraya_logo.png",
        "C.F. Històrics de València 'A'": BASE / "historics_logo.png",
        "Ath. Massamagrell C.F. 'A'": BASE / "massamagrell_logo.png",
        "C.F. Torre Levante 'A'": BASE / "torre_levante_logo.png",
        "C.F. Inter San José Valencia 'B'": BASE / "inter_san_jose_logo.png",
        "Col. Salgui E.D.E. 'A'": BASE / "salgui_logo.png",
        "C.F. Cracks 'A'": BASE / "cracks_logo.png",
        "Paterna C.F. 'A'": BASE / "paterna_logo.png",
        "Manises C.F. 'A'": BASE / "manises_logo.png",
        "Patacona C.F. 'B'": BASE / "patacona_logo.png",
        "C.D.F. Canet 'A'": BASE / "canet_logo.png",
    }
    return logos.get(str(team), Path("__missing__"))


@st.cache_data(show_spinner=False)
def _team_logo_tag(team, size=26):
    lp = _team_logo_path(team)
    if not lp or not lp.exists():
        return "<span style='display:inline-block;width:%dpx;text-align:center'>⚽</span>" % size
    b64 = base64.b64encode(lp.read_bytes()).decode()
    return (
        f"<img src='data:image/png;base64,{b64}' "
        f"style='width:{size}px;height:{size}px;object-fit:contain;vertical-align:middle;margin-right:8px'>"
    )


@st.cache_data(show_spinner=False)
def _image_data_uri(path):
    path = Path(path)
    if not path.exists():
        return ""
    ext = path.suffix.lower().lstrip('.')
    mime = 'jpeg' if ext in ('jpg','jpeg') else ext
    return f"data:image/{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def render_home():
    st.markdown(
        "<div class='team-head'><div><div class='team-name'>⚽ Temporada 2026/2027</div>"
        "<div class='team-sub'>Pulsa directamente sobre una fotografía para entrar.</div></div></div>",
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2, gap="large")
    cards = [
        (c1, "Juvenil A", BASE/"juvenil_a_portada.jpeg", "juvenil",
         "Competición · Rivales · Equipo · Individual"),
        (c2, "Infantil D", BASE/"infantil_d_portada.jpeg", "infantil",
         "Acceso al espacio del Infantil D"),
    ]
    for col, title, img, area, subtitle in cards:
        uri = _image_data_uri(str(img))
        with col:
            if uri:
                html_card = (
                    f"<a href='?area={area}' target='_self' class='home-photo-link'>"
                    f"<div class='home-photo-card'>"
                    f"<img src='{uri}' alt='{_safe_html(title)}'>"
                    f"<div class='home-photo-overlay'>"
                    f"<div><div class='home-photo-title'>{_safe_html(title)}</div>"
                    f"<div class='home-photo-sub'>{_safe_html(subtitle)}</div></div>"
                    f"<div class='home-photo-arrow'>→</div>"
                    f"</div></div></a>"
                )
                st.html(html_card)
            else:
                st.warning(f"No se ha encontrado la fotografía de {title}.")


def render_infantil():
    uri = _image_data_uri(str(BASE/"infantil_d_portada.jpeg"))
    st.markdown(
        "<div class='team-head'><div><div class='team-name'>⚽ Infantil D</div>"
        "<div class='team-sub'>Temporada 2026/2027</div></div></div>",
        unsafe_allow_html=True,
    )
    st.html("<a href='?area=' target='_self' class='back-home-link'>← Volver a Inicio</a>")
    if uri:
        st.html(
            f"<div class='card' style='padding:0;overflow:hidden;margin-top:12px'>"
            f"<img src='{uri}' style='width:100%;height:440px;object-fit:cover;display:block'></div>"
        )
    st.markdown(
        "<div class='card' style='margin-top:12px'><div class='section-title'>Infantil D</div>"
        "<div style='color:#64748b'>Este acceso está separado del menú del Juvenil A.</div></div>",
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _league_snapshot(jmax):
    tab = clasificacion[pd.to_numeric(clasificacion.get("jornada"), errors="coerce").eq(jmax)].copy()
    tab = tab.sort_values(["posicion", "equipo"]) if not tab.empty else tab

    pp = partidos[pd.to_numeric(partidos.get("jornada"), errors="coerce").le(jmax)].copy()
    ev = eventos[pd.to_numeric(eventos.get("jornada"), errors="coerce").le(jmax)].copy()
    valid = pp.dropna(subset=["goles_local", "goles_visitante"]).copy()

    stats = {}
    form = {}

    def _blank():
        return {
            "pj":0,"pg":0,"pe":0,"pp":0,"pts":0,"gf":0,"gc":0,
            "pc":0,"pgcasa":0,"pecasa":0,"ppcasa":0,"ptscasa":0,"gfc":0,"gcc":0,
            "pf":0,"pgfuera":0,"pefuera":0,"ppfuera":0,"ptsfuera":0,"gff":0,"gcf":0,
        }

    for _, m in valid.sort_values("jornada").iterrows():
        loc, vis = str(m.local), str(m.visitante)
        gl, gv = int(m.goles_local), int(m.goles_visitante)
        for t in (loc, vis):
            if t not in stats:
                stats[t] = _blank()
                form[t] = []

        # local
        dl = stats[loc]
        dl["pj"] += 1; dl["gf"] += gl; dl["gc"] += gv
        dl["pc"] += 1; dl["gfc"] += gl; dl["gcc"] += gv
        if gl > gv:
            dl["pg"] += 1; dl["pts"] += 3; dl["pgcasa"] += 1; dl["ptscasa"] += 3
            form[loc].append("V")
        elif gl == gv:
            dl["pe"] += 1; dl["pts"] += 1; dl["pecasa"] += 1; dl["ptscasa"] += 1
            form[loc].append("E")
        else:
            dl["pp"] += 1; dl["ppcasa"] += 1
            form[loc].append("D")

        # visitante
        dv = stats[vis]
        dv["pj"] += 1; dv["gf"] += gv; dv["gc"] += gl
        dv["pf"] += 1; dv["gff"] += gv; dv["gcf"] += gl
        if gv > gl:
            dv["pg"] += 1; dv["pts"] += 3; dv["pgfuera"] += 1; dv["ptsfuera"] += 3
            form[vis].append("V")
        elif gv == gl:
            dv["pe"] += 1; dv["pts"] += 1; dv["pefuera"] += 1; dv["ptsfuera"] += 1
            form[vis].append("E")
        else:
            dv["pp"] += 1; dv["ppfuera"] += 1
            form[vis].append("D")

    # Goles por minuto registrados
    goal_rows = ev[ev["tipo"].astype(str).isin(["gol","penalti_gol","gol_contra","penalti_contra_gol"])].copy()
    minute_blocks = ["0–15","15–30","30–45","45–60","60–75","75–90"]
    timing = {b: {"gf":0,"gc":0} for b in minute_blocks}
    for _, e in goal_rows.iterrows():
        try:
            minute = int(float(e.minuto))
        except Exception:
            continue
        if minute <= 15: block = "0–15"
        elif minute <= 30: block = "15–30"
        elif minute <= 45: block = "30–45"
        elif minute <= 60: block = "45–60"
        elif minute <= 75: block = "60–75"
        else: block = "75–90"
        if str(e.tipo) in ("gol","penalti_gol"):
            timing[block]["gf"] += 1
        else:
            timing[block]["gc"] += 1

    return tab, pp, ev, valid, stats, form, timing


def _form_html(seq):
    dots = []
    for r in seq[-5:]:
        cls = "win" if r == "V" else ("draw" if r == "E" else "loss")
        dots.append(f"<span class='form-dot {cls}'>{r}</span>")
    return "".join(dots) if dots else "—"


def _fmt_rate(num, den):
    return f"{num/den:.2f}" if den else "—"


def _small_result_table(rows):
    return (
        "<div class='heat-wrap league-table-wrap'>"
        "<table class='heat league-table premium-table performance-table'>"
        + rows +
        "</table></div>"
    )


def render_league_summary():
    st.markdown(
        "<div class='league-hero'><div>"
        "<div class='league-eyebrow'>TEMPORADA 2026/2027</div>"
        "<div class='league-title'>🏆 Resumen de liga · Juvenil A</div>"
        "<div class='league-subtitle'>Clasificación, forma, producción ofensiva, disciplina, goles por minuto y rendimiento casa/fuera.</div>"
        "</div><div class='league-badge'>Lliga Comunitat Juvenil · Nord</div></div>",
        unsafe_allow_html=True,
    )

    jornadas = sorted(
        pd.to_numeric(clasificacion.get("jornada", pd.Series(dtype=float)), errors="coerce")
        .dropna().astype(int).unique().tolist()
    )
    opts = ["Total"] + [f"J{x}" for x in jornadas]
    jornada_label = st.selectbox("Vista acumulada", opts, index=0, key="league_summary_jornada")
    jmax = max(jornadas) if jornada_label == "Total" and jornadas else (
        int(jornada_label[1:]) if jornada_label != "Total" else None
    )
    if jmax is None:
        st.info("Sin clasificación cargada.")
        return

    tab, pp, ev, valid, team_stats, form, timing = _league_snapshot(jmax)
    if tab.empty:
        st.info(f"Sin clasificación cargada para J{jmax}.")
        return

    partidos_cargados = len(valid)
    goles_totales = int(valid["goles_local"].sum() + valid["goles_visitante"].sum()) if partidos_cargados else 0
    goles_partido = goles_totales / partidos_cargados if partidos_cargados else 0.0
    amarillas = int(ev["tipo"].isin(["amarilla","doble_amarilla"]).sum()) if not ev.empty else 0
    rojas = int(ev["tipo"].isin(["roja","doble_amarilla"]).sum()) if not ev.empty else 0
    penaltis = int(ev["tipo"].astype(str).str.contains("penalti", case=False, na=False).sum()) if not ev.empty else 0
    amarillas_pp = amarillas / partidos_cargados if partidos_cargados else 0.0
    rojas_pp = rojas / partidos_cargados if partidos_cargados else 0.0

    goles_locales = int(valid["goles_local"].sum()) if partidos_cargados else 0
    goles_visitantes = int(valid["goles_visitante"].sum()) if partidos_cargados else 0
    gf_local_pp = goles_locales / partidos_cargados if partidos_cargados else 0.0
    gc_local_pp = goles_visitantes / partidos_cargados if partidos_cargados else 0.0
    gf_visitante_pp = goles_visitantes / partidos_cargados if partidos_cargados else 0.0
    gc_visitante_pp = goles_locales / partidos_cargados if partidos_cargados else 0.0

    leader = tab.iloc[0]
    leader_name = clean_name(str(leader.equipo))

    complete_stats = [(t,d) for t,d in team_stats.items() if d["pj"] > 0]
    best_attack = max(complete_stats, key=lambda x: x[1]["gf"]) if complete_stats else None
    best_defense = min(complete_stats, key=lambda x: x[1]["gc"]) if complete_stats else None

    # KPI principales
    st.markdown(
        "<div class='league-kpis league-kpis-6'>"
        f"<div class='league-kpi featured'><div class='k'>Líder</div><div class='v'>{_safe_html(leader_name)}</div><div class='s'>Clasificación cargada hasta J{jmax}</div></div>"
        f"<div class='league-kpi'><div class='k'>Partidos cargados</div><div class='v'>{partidos_cargados}</div><div class='s'>Resultados disponibles</div></div>"
        f"<div class='league-kpi'><div class='k'>Goles</div><div class='v'>{goles_totales}</div><div class='s'>{goles_partido:.2f} goles por partido</div></div>"
        f"<div class='league-kpi yellow-kpi'><div class='k'>Amarillas</div><div class='v'>{amarillas}</div><div class='s'>{amarillas_pp:.2f} tarjetas por partido</div></div>"
        f"<div class='league-kpi red-kpi'><div class='k'>Rojas</div><div class='v'>{rojas}</div><div class='s'>{rojas_pp:.2f} rojas por partido</div></div>"
        f"<div class='league-kpi'><div class='k'>Penaltis</div><div class='v'>{penaltis}</div><div class='s'>A favor + en contra</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='venue-kpi-grid'>"
        f"<div class='venue-kpi home'><div class='vk-icon'>🏠⚽</div><div><div class='vk-label'>GF equipos locales</div><div class='vk-value'>{goles_locales}</div><div class='vk-sub'>{gf_local_pp:.2f} por partido</div></div></div>"
        f"<div class='venue-kpi home-against'><div class='vk-icon'>🏠🛡️</div><div><div class='vk-label'>GC equipos locales</div><div class='vk-value'>{goles_visitantes}</div><div class='vk-sub'>{gc_local_pp:.2f} por partido</div></div></div>"
        f"<div class='venue-kpi away'><div class='vk-icon'>✈️⚽</div><div><div class='vk-label'>GF equipos visitantes</div><div class='vk-value'>{goles_visitantes}</div><div class='vk-sub'>{gf_visitante_pp:.2f} por partido</div></div></div>"
        f"<div class='venue-kpi away-against'><div class='vk-icon'>✈️🛡️</div><div><div class='vk-label'>GC equipos visitantes</div><div class='vk-value'>{goles_locales}</div><div class='vk-sub'>{gc_visitante_pp:.2f} por partido</div></div></div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='venue-readout'>Comparativa directa: los GF de los locales son los GC de los visitantes, y viceversa. "
        "Se muestran las dos perspectivas para leer rápidamente si la liga favorece más al equipo local o al visitante.</div>",
        unsafe_allow_html=True,
    )

    ba_name = clean_name(best_attack[0]) if best_attack else "—"
    ba_val = best_attack[1]["gf"] if best_attack else "—"
    bd_name = clean_name(best_defense[0]) if best_defense else "—"
    bd_val = best_defense[1]["gc"] if best_defense else "—"
    st.markdown(
        "<div class='league-highlight-grid'>"
        f"<div class='league-highlight'><div class='hi-icon'>⚽</div><div><div class='hi-label'>Mejor ataque cargado</div><div class='hi-team'>{_safe_html(ba_name)}</div><div class='hi-value'>{ba_val} GF</div></div></div>"
        f"<div class='league-highlight'><div class='hi-icon'>🛡️</div><div><div class='hi-label'>Mejor defensa cargada</div><div class='hi-team'>{_safe_html(bd_name)}</div><div class='hi-value'>{bd_val} GC</div></div></div>"
        f"<div class='league-highlight'><div class='hi-icon'>📊</div><div><div class='hi-label'>Ritmo goleador</div><div class='hi-team'>{goles_partido:.2f}</div><div class='hi-value'>goles / partido</div></div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ---------------- Clasificación ----------------
    st.markdown("<div class='section-title league-section-title'>Clasificación</div>", unsafe_allow_html=True)
    rows = []
    for _, r in tab.iterrows():
        team = str(r.equipo)
        d = team_stats.get(team, {
            "pj":0,"pg":0,"pe":0,"pp":0,"pts":0,"gf":0,"gc":0,
            "pc":0,"pf":0,"gfc":0,"gcc":0,"gff":0,"gcf":0
        })

        loaded_pj = int(d["pj"])
        official_pj = int(r.pj) if pd.notna(r.get("pj")) else 0

        # Si tenemos MÁS partidos cargados que la clasificación base (caso J5),
        # toda la fila se recalcula con esos mismos partidos para que PJ y Forma coincidan.
        if loaded_pj > official_pj:
            pj_disp = loaded_pj
            pg_disp, pe_disp, pp_disp = int(d["pg"]), int(d["pe"]), int(d["pp"])
            pts_disp = int(d["pts"])
        else:
            pj_disp = official_pj if official_pj else loaded_pj
            pg_disp = int(r.pg) if pd.notna(r.get("pg")) else (int(d["pg"]) if loaded_pj == pj_disp else "—")
            pe_disp = int(r.pe) if pd.notna(r.get("pe")) else (int(d["pe"]) if loaded_pj == pj_disp else "—")
            pp_disp = int(r.pp) if pd.notna(r.get("pp")) else (int(d["pp"]) if loaded_pj == pj_disp else "—")
            pts_disp = int(r.puntos) if pd.notna(r.get("puntos")) else (int(d["pts"]) if loaded_pj == pj_disp else "—")

        gf = int(d["gf"]) if loaded_pj else "—"
        gc = int(d["gc"]) if loaded_pj else "—"
        dg = int(d["gf"] - d["gc"]) if loaded_pj else None
        gf_p = d["gf"]/loaded_pj if loaded_pj else None
        gc_p = d["gc"]/loaded_pj if loaded_pj else None
        pos = int(r.posicion) if pd.notna(r.posicion) else 0

        pos_cls = "top-pos" if pos <= 3 else ("danger-pos" if pos >= max(1, len(tab)-2) else "")
        dg_txt = f"{dg:+d}" if dg is not None else "—"
        dg_cls = "positive" if dg is not None and dg > 0 else ("negative" if dg is not None and dg < 0 else "")

        rows.append(
            "<tr>"
            f"<td class='pos-col {pos_cls}'><b>{pos or '—'}</b></td>"
            f"<td class='team-col'>{_team_logo_tag(team,28)}<b>{_safe_html(clean_name(team))}</b></td>"
            f"<td class='stat-num'>{pj_disp}</td>"
            f"<td class='stat-num'>{pg_disp}</td>"
            f"<td class='stat-num'>{pe_disp}</td>"
            f"<td class='stat-num'>{pp_disp}</td>"
            f"<td class='stat-num'>{gf}</td><td class='stat-num'>{gc}</td>"
            f"<td class='stat-num {dg_cls}'>{dg_txt}</td>"
            f"<td class='stat-num'>{f'{gf_p:.2f}' if gf_p is not None else '—'}</td>"
            f"<td class='stat-num'>{f'{gc_p:.2f}' if gc_p is not None else '—'}</td>"
            f"<td class='form-cell'>{_form_html(form.get(team, []))}</td>"
            f"<td class='pts-cell stat-num'>{pts_disp}</td>"
            "</tr>"
        )

    st.markdown(
        "<div class='heat-wrap league-table-wrap'><table class='heat league-table premium-table main-standings'>"
        "<thead><tr><th>Pos.</th><th class='team-col'>Equipo</th><th>PJ</th><th>PG</th><th>PE</th><th>PP</th>"
        "<th>GF</th><th>GC</th><th>DG</th><th>GF/P</th><th>GC/P</th><th>Forma</th><th>Pts</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='goal-time-note'>Cuando hay un 5.º partido cargado, PJ/PG/PE/PP/Pts se sincronizan con la misma secuencia que aparece en Forma.</div>",
        unsafe_allow_html=True,
    )

    # ---------------- Goles por minutos ----------------
    st.markdown("<div class='section-title league-section-title'>Goles por minutos</div>", unsafe_allow_html=True)
    total_gf_events = sum(x["gf"] for x in timing.values())
    total_gc_events = sum(x["gc"] for x in timing.values())
    max_evt = max([x["gf"] for x in timing.values()] + [x["gc"] for x in timing.values()] + [1])
    blocks = []
    for block, vals in timing.items():
        gf_count, gc_count = vals["gf"], vals["gc"]
        gf_pct = (gf_count/total_gf_events*100) if total_gf_events else 0
        gc_pct = (gc_count/total_gc_events*100) if total_gc_events else 0
        gf_w = max(4, gf_count/max_evt*100) if gf_count else 0
        gc_w = max(4, gc_count/max_evt*100) if gc_count else 0
        diff = gf_count - gc_count
        blocks.append(
            f"<div class='goal-time-card'><div class='goal-time-head'>{block}</div>"
            f"<div class='goal-line'><span>GF</span><div class='goal-track'><div class='goal-fill gf' style='width:{gf_w:.0f}%'></div></div><b>{gf_count}</b><em>{gf_pct:.0f}%</em></div>"
            f"<div class='goal-line'><span>GC</span><div class='goal-track'><div class='goal-fill gc' style='width:{gc_w:.0f}%'></div></div><b>{gc_count}</b><em>{gc_pct:.0f}%</em></div>"
            f"<div class='goal-diff'>Diferencia: <b>{diff:+d}</b></div></div>"
        )
    st.markdown(
        "<div class='goal-time-note'>Distribución de los goles cargados por tramos de partido.</div>"
        "<div class='goal-time-grid'>" + "".join(blocks) + "</div>",
        unsafe_allow_html=True,
    )

    # ---------------- Disciplina ----------------
    st.markdown("<div class='section-title league-section-title'>Disciplina y penaltis</div>", unsafe_allow_html=True)
    dobles = int(ev["tipo"].eq("doble_amarilla").sum()) if not ev.empty else 0
    st.markdown(
        "<div class='discipline-grid'>"
        f"<div class='discipline-card yellow'><span>🟨</span><div><b>{amarillas}</b><small>{amarillas_pp:.2f} amarillas / partido</small></div></div>"
        f"<div class='discipline-card red'><span>🟥</span><div><b>{rojas}</b><small>{rojas_pp:.2f} rojas / partido</small></div></div>"
        f"<div class='discipline-card double'><span>🟨🟥</span><div><b>{dobles}</b><small>Dobles amarillas</small></div></div>"
        f"<div class='discipline-card penalty'><span>🥅</span><div><b>{penaltis}</b><small>Penaltis registrados</small></div></div>"
        f"<div class='discipline-card rate'><span>⚽</span><div><b>{goles_partido:.2f}</b><small>Goles / partido</small></div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ---------------- Rendimiento casa / fuera ----------------
    st.markdown("<div class='section-title league-section-title'>Rendimiento · casa y fuera</div>", unsafe_allow_html=True)
    tab_casa, tab_fuera = st.tabs(["🏠 Casa", "✈️ Fuera"])

    def _perf_rows(side):
        ranking = []
        for _, r in tab.iterrows():
            team = str(r.equipo)
            d = team_stats.get(team, {})
            if side == "casa":
                pj = int(d.get("pc",0)); pg = int(d.get("pgcasa",0)); pe = int(d.get("pecasa",0)); pper = int(d.get("ppcasa",0))
                pts = int(d.get("ptscasa",0)); gf = int(d.get("gfc",0)); gc = int(d.get("gcc",0))
            else:
                pj = int(d.get("pf",0)); pg = int(d.get("pgfuera",0)); pe = int(d.get("pefuera",0)); pper = int(d.get("ppfuera",0))
                pts = int(d.get("ptsfuera",0)); gf = int(d.get("gff",0)); gc = int(d.get("gcf",0))
            ranking.append({
                "team": team, "pj": pj, "pg": pg, "pe": pe, "pp": pper,
                "pts": pts, "gf": gf, "gc": gc, "dg": gf-gc,
            })

        # Clasificación específica del ámbito: puntos > diferencia > goles a favor > nombre.
        ranking = sorted(
            ranking,
            key=lambda x: (-x["pts"], -x["dg"], -x["gf"], clean_name(x["team"]).lower())
        )

        parts = [
            "<thead><tr><th>Pos.</th><th class='team-col'>Equipo</th><th>PJ</th><th>PG</th><th>PE</th><th>PP</th><th>Pts</th>"
            "<th>GF</th><th>GC</th><th>DG</th><th>GF/P</th><th>GC/P</th></tr></thead><tbody>"
        ]
        for pos, d in enumerate(ranking, start=1):
            dg_cls = "positive" if d["dg"] > 0 else ("negative" if d["dg"] < 0 else "")
            parts.append(
                "<tr>"
                f"<td class='pos-col'><b>{pos}</b></td>"
                f"<td class='team-col'>{_team_logo_tag(d['team'],24)}<b>{_safe_html(clean_name(d['team']))}</b></td>"
                f"<td class='stat-num'>{d['pj']}</td><td class='stat-num'>{d['pg']}</td><td class='stat-num'>{d['pe']}</td>"
                f"<td class='stat-num'>{d['pp']}</td><td class='pts-cell stat-num'>{d['pts']}</td>"
                f"<td class='stat-num'>{d['gf']}</td><td class='stat-num'>{d['gc']}</td>"
                f"<td class='stat-num {dg_cls}'>{d['dg']:+d}</td>"
                f"<td class='stat-num'>{_fmt_rate(d['gf'],d['pj'])}</td><td class='stat-num'>{_fmt_rate(d['gc'],d['pj'])}</td>"
                "</tr>"
            )
        parts.append("</tbody>")
        return "".join(parts)

    with tab_casa:
        st.markdown(
            "<div class='perf-explainer'><b>Clasificación como local</b> · ordenada por los puntos conseguidos en casa. Desempate: diferencia de goles y goles a favor.</div>",
            unsafe_allow_html=True,
        )
        st.markdown(_small_result_table(_perf_rows("casa")), unsafe_allow_html=True)

    with tab_fuera:
        st.markdown(
            "<div class='perf-explainer'><b>Clasificación como visitante</b> · ordenada por los puntos conseguidos fuera de casa. Desempate: diferencia de goles y goles a favor.</div>",
            unsafe_allow_html=True,
        )
        st.markdown(_small_result_table(_perf_rows("fuera")), unsafe_allow_html=True)

    # ---------------- Resultados por jornada ----------------
    st.markdown("<div class='section-title league-section-title'>Resultados por jornada</div>", unsafe_allow_html=True)
    available_days = sorted(pd.to_numeric(pp.jornada, errors="coerce").dropna().astype(int).unique().tolist())
    if not available_days:
        st.info("Sin resultados cargados.")
    else:
        selected_day = st.selectbox(
            "Selecciona jornada",
            available_days,
            index=len(available_days)-1,
            format_func=lambda x: f"Jornada {x}",
            key="league_results_day",
        )
        grp = pp[pd.to_numeric(pp.jornada, errors="coerce").eq(selected_day)].copy()
        st.markdown(f"<div class='matchday-title'>Jornada {selected_day}</div>", unsafe_allow_html=True)
        cards = []
        for _, rr in grp.iterrows():
            gl = "—" if pd.isna(rr.goles_local) else int(rr.goles_local)
            gv = "—" if pd.isna(rr.goles_visitante) else int(rr.goles_visitante)
            cards.append(
                f"<div class='league-match-card'>"
                f"<span class='match-team'>{_team_logo_tag(str(rr.local),22)}{_safe_html(clean_name(rr.local))}</span>"
                f"<b>{gl} – {gv}</b>"
                f"<span class='match-team away'>{_safe_html(clean_name(rr.visitante))}{_team_logo_tag(str(rr.visitante),22)}</span>"
                f"</div>"
            )
        st.markdown("".join(cards), unsafe_allow_html=True)


# ---------------- Sidebar / menú desplegable de rivales ----------------
with st.sidebar:
    st.markdown(
        """<div class='brand-box'><div class='brand-ball'>⚽</div><div><div class='brand-main'>TEMPORADA <span>2026/2027</span></div><div class='brand-sub'>Temporada 2026/2027</div></div></div>""",
        unsafe_allow_html=True,
    )
    _area = ""
    try:
        _area = st.query_params.get("area", "")
    except Exception:
        try:
            _area = (st.experimental_get_query_params().get("area") or [""])[0]
        except Exception:
            _area = ""
    _area = str(_area).lower().strip()

    _nav_options = ["Inicio", "Resumen liga", "Rivales", "Equipo", "Individual"]
    _default_mod = "Resumen liga" if _area == "juvenil" else "Inicio"
    modulo = st.radio(
        "Navegación",
        _nav_options,
        index=_nav_options.index(_default_mod),
        label_visibility="collapsed",
    )

    seleccionado = None
    if modulo == "Rivales":
        equipos = load_csv("equipos_liga.csv")
        st.markdown("<div class='side-label'>Rivales · 16 equipos</div>", unsafe_allow_html=True)
        lista = equipos.sort_values("orden")["equipo"].tolist() if not equipos.empty else []
        default_idx = lista.index("Bétera C.F. 'A'") if "Bétera C.F. 'A'" in lista else 0
        seleccionado = st.selectbox(
            "Selecciona rival",
            lista,
            index=default_idx,
            help="Elige cualquiera de los 16 equipos. Los perfiles con minutos y eventos cargados se muestran completos; los demás conservan partidos y clasificación sin inventar datos individuales.",
        )
        st.markdown(
            f"<div class='team-count' style='display:flex;align-items:center;gap:8px'>"
            f"{_team_logo_tag(seleccionado,30)}"
            f"<span>Equipo seleccionado: <b>{_safe_html(seleccionado)}</b></span></div>",
            unsafe_allow_html=True,
        )
        with st.expander("Ver los 16 equipos"):
            for _, row in equipos.sort_values("orden").iterrows():
                mark = "✅" if row.equipo == seleccionado else "•"
                st.markdown(
                    f"<div class='rival-list-row'>{mark} <b>{int(row.orden)}.</b> "
                    f"{_team_logo_tag(row.equipo,24)}<span>{_safe_html(row.equipo)}</span></div>",
                    unsafe_allow_html=True,
                )

# ---------------- Carga perezosa por módulo ----------------
# Inicio / Infantil: 0 CSV.
# Resumen: solo clasificación, partidos y eventos.
# Individual: solo sus tablas necesarias.
# Rivales: solo al entrar en Rivales se cargan las seis tablas del análisis.
if modulo == "Resumen liga":
    partidos = load_csv("partidos_rivales.csv")
    eventos = load_csv("eventos_rivales.csv")
    clasificacion = load_csv("clasificacion_liga.csv")
elif modulo == "Individual":
    plantillas = load_csv("plantillas_rivales.csv")
    minutos = load_csv("minutos_rivales.csv")
    eventos = load_csv("eventos_rivales.csv")
    alineaciones = load_csv("alineaciones_rivales.csv")
elif modulo == "Rivales":
    plantillas = load_csv("plantillas_rivales.csv")
    minutos = load_csv("minutos_rivales.csv")
    partidos = load_csv("partidos_rivales.csv")
    eventos = load_csv("eventos_rivales.csv")
    clasificacion = load_csv("clasificacion_liga.csv")
    alineaciones = load_csv("alineaciones_rivales.csv")

st.markdown(
    "<div class='topbar'><div class='title'>⚽ TEMPORADA 2026/2027 · V15.12.25</div><div class='nav'>Inicio &nbsp;&nbsp; Nuestro equipo &nbsp;&nbsp; <b>Rivales</b> &nbsp;&nbsp; Competición &nbsp;&nbsp; Informes</div></div>",
    unsafe_allow_html=True,
)

if _area == "infantil":
    render_infantil()
    st.stop()
elif modulo == "Inicio":
    render_home()
    st.stop()
elif modulo == "Resumen liga":
    render_league_summary()
    st.stop()
elif modulo == "Individual":
    render_individual()
    st.stop()
elif modulo == "Equipo":
    st.markdown(
        "<div class='team-head'><div><div class='team-name'>Equipo</div><div class='team-sub'>Módulo de Primer Toque preparado para la siguiente fase.</div></div></div>",
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
    try:
        d_int = int(dorsal)
        d_label = str(d_int)
        shown = display_name(name, d_int)
    except (TypeError, ValueError):
        d_label = str(dorsal)
        shown = display_name(name, None)
    return f"{shown} ({d_label})"


def dorsal_labels(roster_df):
    if roster_df.empty:
        return {}
    tmp = roster_df[["jugador", "dorsal"]].dropna().copy()
    tmp["dorsal"] = tmp["dorsal"].astype(int)
    return tmp.groupby("jugador")["dorsal"].apply(lambda x: "/".join(str(v) for v in sorted(set(x)))).to_dict()


def image_html(path):
    if not path.exists():
        return "<div style='font-size:54px'>🛡️</div>"
    b64 = _b64_file(str(path))
    return f"<img src='data:image/png;base64,{b64}'>"

# ---------------- Rival elegido ----------------
team_parts = partidos[(partidos.local == seleccionado) | (partidos.visitante == seleccionado)].copy()
roster = plantillas[plantillas.equipo == seleccionado].copy()
forms = team_formations(seleccionado)

logo_path = _team_logo_path(seleccionado)

st.markdown(
    f"""<div class='team-head'>{image_html(logo_path)}<div><div class='team-name'>{_safe_html(seleccionado)}</div><div class='team-sub'>Lliga Comunitat Juvenil · Nord · Temporada 2026/2027</div><span class='badge'>{'ANÁLISIS REAL J1–J5' if seleccionado in ["Primer Toque C.F. 'A'", "C.F. At. Burriana - Salesianos 'A'", "Villarreal C.F. 'C'", "Alboraya U.D. 'B'", "C.F. Històrics de València 'A'", "C.F. Torre Levante 'A'", "Ath. Massamagrell C.F. 'A'", "C.F. Inter San José Valencia 'B'", "Col. Salgui E.D.E. 'A'", "C.F. Cracks 'A'", "Paterna C.F. 'A'"] else ('ANÁLISIS REAL J1–J4' if seleccionado in ["Bétera C.F. 'A'", "C.D. Acero 'A'"] else 'PERFIL PREPARADO · DATOS PENDIENTES')}</span></div></div>""",
    unsafe_allow_html=True,
)

if seleccionado == "C.F. Inter San José Valencia 'B'":
    st.markdown(
        """<div class='card' style='margin:8px 0 12px'>
        <div class='section-title'>San José · actas J1–J5 completas</div>
        <div class='note'><b>Balance:</b> 5 PJ · 3 V · 0 E · 2 D · 11 GF · 10 GC · 9 puntos · 5º.
        <br><b>Datos cargados:</b> plantilla y dorsales utilizados · XI inicial de las 5 jornadas · sistemas · minutos · cambios reconstruidos por minutaje · goles · tarjetas · expulsiones y goles encajados.
        <br><b>Máximos goleadores:</b> Alejandro Vidal Castillo (3) · Erik Da Silva Canobbio (3).
        <br><b>Fuente:</b> actas FFCV mostradas en el vídeo aportado por el usuario. Los datos de esta ficha se han transcrito jornada a jornada sin completar información no visible en las actas.</div>
        </div>""",
        unsafe_allow_html=True,
    )


if seleccionado == "Col. Salgui E.D.E. 'A'":
    st.markdown(
        """<div class='card' style='margin:8px 0 12px'>
        <div class='section-title'>Colegio Salgui · actas J1–J5 completas</div>
        <div class='note'><b>Balance:</b> 5 PJ · 1 V · 2 E · 2 D · 8 GF · 7 GC · 5 puntos · 9º.
        <br><b>Datos cargados:</b> plantilla y dorsales utilizados · XI inicial de las 5 jornadas · convocatorias · sistemas · minutos · cambios reconstruidos por minutaje · goles · tarjetas y goles encajados.
        <br><b>Máximo goleador:</b> Jorge Blanco Martinez (2). El 2.º gol de J5 fue un gol en propia de Pablo Siñuela Lara y no se atribuye a un jugador del Salgui.
        <br><b>Fuente:</b> actas FFCV mostradas en el vídeo aportado por el usuario. Datos transcritos jornada a jornada sin completar información no visible.</div>
        </div>""",
        unsafe_allow_html=True,
    )


if seleccionado == "C.F. Cracks 'A'":
    st.markdown(
        """<div class='card' style='margin:8px 0 12px'>
        <div class='section-title'>Cracks · actas J1–J5 completas</div>
        <div class='note'><b>Balance:</b> 5 PJ · 1 V · 1 E · 3 D · 6 GF · 10 GC · 4 puntos · 11º.
        <br><b>Datos cargados:</b> plantilla y dorsales utilizados · XI inicial de las 5 jornadas · convocatorias · sistema 1-4-4-2 en las cinco jornadas · minutos · cambios reconstruidos por acta · goles · tarjetas · expulsión y goles encajados.
        <br><b>Máximo goleador:</b> Daniel Saez Barber (2). También marcaron Angel Chulia Izquierdo, Rodrigo Gijon Martinez, Nikolas Elijah Hiler y Zander Delano Grant.
        <br><b>Incidencias:</b> Angel Chulia Izquierdo fue expulsado en J3. El cuarto gol encajado en J5 fue en propia puerta de Jorge Benavent Cervera.
        <br><b>Fuente:</b> actas FFCV mostradas en el vídeo aportado por el usuario.</div>
        </div>""",
        unsafe_allow_html=True,
    )


if seleccionado == "Paterna C.F. 'A'":
    st.markdown(
        """<div class='card' style='margin:8px 0 12px'>
        <div class='section-title'>Paterna · actas J1–J5 completas</div>
        <div class='note'><b>Balance:</b> 5 PJ · 1 V · 2 E · 2 D · 9 GF · 10 GC · 5 puntos.
        <br><b>Datos cargados:</b> XI inicial de las 5 jornadas · dorsales usados · sistemas · minutos reconstruidos desde los cambios del acta · goles · tarjetas · goles encajados.
        <br><b>Máximo goleador:</b> Oscar Rubio Montoro (3). Ayomide Oluwapelumi Oguns Alabebe suma 2; Byron Beycker, Samuel Ebitu y Alvaro Josep, 1 cada uno; además hubo un autogol rival en J2.
        <br><b>Sistemas:</b> J1 1-3-5-2; J2-J5 1-5-4-1.
        <br><b>Fuente:</b> actas FFCV mostradas en el vídeo aportado por el usuario.</div>
        </div>""",
        unsafe_allow_html=True,
    )

# Perfiles ya desarrollados con jornadas completas.
analizados = ["Bétera C.F. 'A'", "C.D. Acero 'A'", "Primer Toque C.F. 'A'", "C.F. At. Burriana - Salesianos 'A'", "Villarreal C.F. 'C'", "Alboraya U.D. 'B'", "C.F. Històrics de València 'A'", "C.F. Torre Levante 'A'", "Ath. Massamagrell C.F. 'A'", "C.F. Inter San José Valencia 'B'", "Col. Salgui E.D.E. 'A'", "C.F. Cracks 'A'", "Paterna C.F. 'A'"]
if seleccionado not in analizados:
    st.info(
        "Este equipo ya está dentro del menú de Rivales. Todavía no hemos cargado sus actas y jornadas. "
        "Los equipos ya cargados con actas completas aparecen con la etiqueta ANÁLISIS REAL. El resto queda preparado para incorporar sus jornadas."
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
    if not js_all:
        js_all = sorted(team_parts.jornada.dropna().astype(int).unique().tolist())
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

# Jornada concreta: acceso directo al partido arriba de la ficha.
if jornada_sel != "Total" and not part.empty:
    _rr = part.sort_values("jornada").iloc[0]
    _j = int(_rr.jornada)
    _fixture = f"{short_team_name(_rr.local)} – {short_team_name(_rr.visitante)}"
    _url = match_link(seleccionado, _j)
    if _url:
        st.markdown(
            f"<div class='video-callout'><div class='vt'>🎥 J{_j} · {_safe_html(_fixture)}</div><div class='vs'>Acceso directo al partido analizado de esta jornada.</div><a class='video-link' href='{_safe_html(_url, quote=True)}' target='_blank'>▶ Ver partido</a></div>",
            unsafe_allow_html=True,
        )
    elif seleccionado == "Villarreal C.F. 'C'":
        st.markdown(
            f"<div class='video-callout'><div class='vt'>🎥 J{_j} · {_safe_html(_fixture)}</div><div class='vs'>Enlace del partido todavía pendiente de incorporar.</div></div>",
            unsafe_allow_html=True,
        )

# Control de coherencia: el total de eventos de gol debe cuadrar con el marcador agregado.
_ev_gf = int(ev_scope.tipo.isin(['gol','penalti_gol']).sum()) if not ev_scope.empty else 0
_ev_gc = int(ev_scope.tipo.isin(['gol_contra','penalti_contra_gol']).sum()) if not ev_scope.empty else 0
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
        rows += f"<div class='match-row' style='grid-template-columns:40px 1fr 70px 14px'><div class='jtag'>J{j}</div><div>{_safe_html(fixture)}</div><div>{result_html}</div><div class='dot' style='background:{col}'></div></div>"
    st.markdown(
        f"<div class='card'><div class='section-title'>Jornadas analizadas</div>{rows}</div>",
        unsafe_allow_html=True,
    )

with c:
    # XI dinámico: cambia con Total/Casa/Fuera y también con la jornada elegida.
    al = al_scope.copy()
    xi_m = mm.copy()
    njs = max(1, len(scope_js))
    # La identidad del jugador se calcula por nombre, no por dorsal:
    # en FFCV algunos jugadores cambian de número entre jornadas.
    starts = xi_m.groupby("jugador")["titular"].sum() / njs * 100 if not xi_m.empty else pd.Series(dtype=float)
    recent_js = scope_js[-2:]
    recent = (
        xi_m[xi_m.jornada.isin(recent_js)].groupby("jugador")["titular"].sum() / max(1, len(recent_js)) * 100
        if recent_js else pd.Series(dtype=float)
    )
    if not starts.empty or not recent.empty:
        _idx = starts.index.union(recent.index)
        prob = (0.6 * starts.reindex(_idx, fill_value=0) +
                0.4 * recent.reindex(_idx, fill_value=0))
    else:
        prob = pd.Series(dtype=float)

    if not al.empty:
        # Rol dominante dentro del filtro y dorsal más reciente para mostrar en el XI.
        rc = al.groupby(["rol", "jugador"]).size().reset_index(name="n")
        rc = rc.sort_values(["jugador", "n"], ascending=[True, False]).drop_duplicates("jugador", keep="first")
        latest_dorsal = (
            al.sort_values("jornada")
              .drop_duplicates("jugador", keep="last")[["jugador", "dorsal"]]
        )
        rc = rc.merge(latest_dorsal, on="jugador", how="left")
        rc["prob"] = rc.jugador.map(prob).fillna(0)
    else:
        rc = pd.DataFrame(columns=["rol","jugador","n","dorsal","prob"])

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
            f"<div class='pchip' style='left:{x}%;top:{y}%'><div class='shirt'>{int(r['dorsal'])}</div>{_safe_html(short_name(player_label))}<br><span class='ppct'>{float(r['prob']):.0f}%</span></div>"
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
# Una misma persona puede llevar dorsales distintos entre jornadas (p. ej. Ibrahim Zahidi 2/18).
# La tabla se agrupa por jugador para no partir sus minutos en dos filas.
dlabels = dorsal_labels(roster)
players_all = sorted(set(roster.jugador.dropna().astype(str)) | set(m.jugador.dropna().astype(str)))
table = pd.DataFrame({"jugador": players_all})
table["dorsal"] = table.jugador.map(dlabels).fillna("")
for j in js:
    d = m[m.jornada == j].groupby("jugador", as_index=False)["minutos"].sum().rename(columns={"minutos": f"J{j}"})
    table = table.merge(d, on="jugador", how="left")

jcols = [f"J{j}" for j in js]
if jcols:
    table["Total"] = table[jcols].sum(axis=1, skipna=True)
    avail = 90 * len(js)
    table["% min"] = (table.Total / avail * 100).round(0)
    starts_m = m.groupby("jugador")["titular"].sum()
    table["% tit"] = (table.jugador.map(starts_m).fillna(0) / max(1, len(js)) * 100).round(0)
    recent_js = js[-2:]
    recent_m = m[m.jornada.isin(recent_js)].groupby("jugador")["titular"].sum()
    recent_pct = table.jugador.map(recent_m).fillna(0) / max(1, len(recent_js)) * 100
    table["Prob. XI"] = (0.60 * table["% tit"] + 0.40 * recent_pct).round(0)

    evg = ev_scope[ev_scope.tipo.isin(["gol", "penalti_gol"])].groupby("jugador").size()
    eva = ev_scope[ev_scope.tipo == "amarilla"].groupby("jugador").size()
    # Distingue expulsión por doble amarilla de roja directa.
    det = ev_scope.get("detalle", pd.Series(index=ev_scope.index, dtype="object")).fillna("").astype(str).str.lower()
    double_mask = (ev_scope.tipo == "doble_amarilla") | ((ev_scope.tipo == "roja") & det.str.contains(r"doble amarilla|segunda amarilla|amarilla previa", regex=True))
    ev2a = ev_scope[double_mask].groupby("jugador").size()
    evr = ev_scope[(ev_scope.tipo == "roja") & ~double_mask].groupby("jugador").size()
    table["G"] = table.jugador.map(evg).fillna(0).astype(int)
    table["🟨"] = table.jugador.map(eva).fillna(0).astype(int)
    table["🟨🟥"] = table.jugador.map(ev2a).fillna(0).astype(int)
    table["🟥"] = table.jugador.map(evr).fillna(0).astype(int)
    table = table.sort_values(["Total", "% tit", "jugador"], ascending=[False, False, True]).reset_index(drop=True)

    head = "<tr><th>#</th><th style='text-align:left'>Jugador</th>" + "".join(f"<th>{x}</th>" for x in jcols) + "<th>Total</th><th>% min</th><th>% tit</th><th>Prob. XI</th><th>G</th><th>🟨</th><th>🟨🟥</th><th>🟥</th></tr>"
    body = []
    for _, r in table.iterrows():
        cells = "".join(f"<td class='{minute_class(r[x])}'>{'—' if pd.isna(r[x]) else int(r[x])}</td>" for x in jcols)
        body.append(
            f"<tr><td class='num'>{_safe_html(str(r.dorsal))}</td><td class='name'>{_safe_html(display_name(r.jugador))}</td>{cells}<td><b>{int(r.Total)}</b></td><td>{int(r['% min'])}%</td><td>{int(r['% tit'])}%</td><td><b>{int(r['Prob. XI'])}%</b></td><td>{int(r.G)}</td><td>{int(r['🟨'])}</td><td>{int(r['🟨🟥'])}</td><td>{int(r['🟥'])}</td></tr>"
        )
    st.markdown(
        f"<div class='heat-wrap'><table class='heat'>{head}{''.join(body)}</table><div class='note'>Colores: 0–20 rojo · 21–45 naranja · 46–60 amarillo · 61–75 verde claro · 76–90 verde oscuro. &nbsp; 🟨🟥 = expulsión por doble amarilla · 🟥 = roja directa.</div></div>",
        unsafe_allow_html=True,
    )
else:
    st.info("Sin minutos cargados para este filtro.")

# ---------------- Goles, disciplina, núcleo del XI y carga ----------------
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
d1, d2, d3, d4 = st.columns(4)

with d1:
    ev = ev_scope[ev_scope.tipo.isin(["gol", "penalti_gol"])]
    vcg = ev.jugador.value_counts()
    dorsal_map = dorsal_labels(roster)
    items = "".join(
        f"<div class='mini-item'><span>⚽ {_safe_html(name_with_number(n, dorsal_map.get(n, 0)))}</span><b>{int(v)}</b></div>"
        if dorsal_map.get(n) else f"<div class='mini-item'><span>⚽ {_safe_html(str(n))}</span><b>{int(v)}</b></div>"
        for n, v in vcg.items()
    ) or "<div class='note'>Sin goles cargados para este filtro</div>"
    st.markdown(f"<div class='card'><div class='section-title'>Goleadores registrados</div><div class='mini-list'>{items}</div></div>", unsafe_allow_html=True)

with d2:
    ea = ev_scope[ev_scope.tipo == "amarilla"].jugador.value_counts()
    det_disc = ev_scope.get("detalle", pd.Series(index=ev_scope.index, dtype="object")).fillna("").astype(str).str.lower()
    double_disc_mask = (ev_scope.tipo == "doble_amarilla") | ((ev_scope.tipo == "roja") & det_disc.str.contains(r"doble amarilla|segunda amarilla|amarilla previa", regex=True))
    e2a = ev_scope[double_disc_mask].jugador.value_counts()
    er = ev_scope[(ev_scope.tipo == "roja") & ~double_disc_mask].jugador.value_counts()
    def discipline_items(series, icon):
        out = []
        for n, v in series.items():
            dorsal = dorsal_map.get(n)
            label = name_with_number(n, dorsal) if dorsal else str(n)
            out.append(f"<div class='mini-item'><span>{icon} {_safe_html(label)}</span><b>{int(v)}</b></div>")
        return "".join(out)
    items = discipline_items(ea, "🟨") + discipline_items(e2a, "🟨🟥") + discipline_items(er, "🟥")
    if not items:
        items = "<div class='note'>Sin tarjetas para este filtro</div>"
    st.markdown(f"<div class='card'><div class='section-title'>Disciplina</div><div class='mini-list'>{items}</div></div>", unsafe_allow_html=True)

with d3:
    # Más útil que el banquillo: identifica el núcleo que el entrenador repite de inicio.
    if not mm.empty:
        core = mm.groupby("jugador").agg(Titularidades=("titular", "sum"), Partidos=("jornada", "nunique")).reset_index()
        core["pct"] = core["Titularidades"] / max(1, len(scope_js)) * 100
        core = core.sort_values(["pct", "Titularidades", "jugador"], ascending=[False, False, True]).head(7)
        dmap_core = dorsal_labels(roster)
        items = "".join(
            f"<div class='mini-item'><span>⭐ {_safe_html(name_with_number(r.jugador, dmap_core.get(r.jugador, '')))}</span><b>{r.pct:.0f}% tit.</b></div>"
            for _, r in core.iterrows()
        )
    else:
        items = "<div class='note'>Sin datos para este filtro</div>"
    st.markdown(f"<div class='card'><div class='section-title'>Núcleo del XI</div><div class='mini-list'>{items}</div></div>", unsafe_allow_html=True)

with d4:
    players = int(mm[mm.minutos > 0].jugador.nunique()) if not mm.empty else 0
    st.markdown(
        f"<div class='card'><div class='section-title'>Carga competitiva</div><div class='kpi' style='min-height:125px'><div class='v'>{players}</div><div class='l'>Jugadores utilizados</div><div class='s'>{_safe_html(ambito or '')}{' · ' + _safe_html(jornada_sel or '') if jornada_sel and jornada_sel != 'Total' else ''}</div></div></div>",
        unsafe_allow_html=True,
    )

    # Penaltis: icono de balón con portería en FFCV. Se guarda jornada, minuto, lanzador y resultado.
    pen = ev_scope[ev_scope.tipo.isin(["penalti_gol", "penalti_fallado"])].sort_values(["jornada", "minuto"]) if not ev_scope.empty else pd.DataFrame()
    if not pen.empty:
        pen_items = []
        for _, pr in pen.iterrows():
            result = "Gol" if pr.tipo == "penalti_gol" else "Fallado"
            icon = "✅" if pr.tipo == "penalti_gol" else "❌"
            dorsal = dorsal_map.get(pr.jugador)
            label = name_with_number(pr.jugador, dorsal) if dorsal else str(pr.jugador)
            pen_items.append(f"<div class='mini-item'><span>{icon} J{int(pr.jornada)} · {int(pr.minuto)}' · {_safe_html(label)}</span><b>{result}</b></div>")
        pen_html = "".join(pen_items)
    else:
        pen_html = "<div class='note'>Sin penaltis a favor registrados en este filtro</div>"
    st.markdown(f"<div style='height:10px'></div><div class='card'><div class='section-title'>Penaltis</div><div class='mini-list'>{pen_html}</div></div>", unsafe_allow_html=True)

# ---------------- Conversión de gol por jugador ----------------
st.markdown("<div style='height:10px'></div><div class='section-title'>Conversión de gol por jugador</div>", unsafe_allow_html=True)

# Solo jugadores del equipo seleccionado que han marcado. Los autogoles no cuentan como goleador propio.
scorer_goals = ev_scope[(ev_scope.tipo.isin(["gol", "penalti_gol"])) & (~ev_scope.jugador.isin(["Autogol rival", "G.P."]))].groupby("jugador").size().reset_index(name="goles")
if not scorer_goals.empty and not mm.empty:
    mins_player = mm.groupby("jugador", as_index=False)["minutos"].sum()
    conv = scorer_goals.merge(mins_player, on="jugador", how="left")
    conv = conv[conv.minutos.fillna(0) > 0].copy()
    if not conv.empty:
        dorsal_map = dorsal_labels(roster)
        conv["Jugador"] = conv["jugador"].apply(lambda n: name_with_number(n, dorsal_map.get(n, 0)) if dorsal_map.get(n) else str(n))
        conv["Goles / 90"] = (conv["goles"] / conv["minutos"] * 90).round(2)
        conv["Minutos por gol"] = (conv["minutos"] / conv["goles"]).round(0)
        conv = conv.sort_values(["Goles / 90", "goles"], ascending=[False, False])
        # SVG propio: orden estricto de mayor a menor y columnas finas.
        n = len(conv)
        width = max(900, 105 * n)
        height = 315
        left, right, top, bottom = 58, 24, 28, 92
        plot_w, plot_h = width - left - right, height - top - bottom
        vmax = max(float(conv["Goles / 90"].max()), 0.1)
        step = plot_w / max(1, n)
        bar_w = min(24, max(12, step * 0.24))
        svg = []
        svg.append(f"<svg viewBox='0 0 {width} {height}' style='width:100%;height:auto;background:#fff;border:1px solid #e6eaf0;border-radius:14px;padding:4px'>")
        for frac in [0, .25, .5, .75, 1.0]:
            yy = top + plot_h * (1-frac)
            val_tick = vmax * frac
            svg.append(f"<line x1='{left}' y1='{yy:.1f}' x2='{width-right}' y2='{yy:.1f}' stroke='#e8edf3' stroke-width='1'/>")
            svg.append(f"<text x='{left-9}' y='{yy+4:.1f}' text-anchor='end' font-size='10' fill='#6b7c93'>{val_tick:.2f}</text>")
        for i, (_, r) in enumerate(conv.iterrows()):
            x = left + step * (i + .5)
            val = float(r["Goles / 90"])
            bh = (val / vmax) * plot_h if vmax else 0
            y0 = top + plot_h - bh
            label = _safe_html(str(r["Jugador"]))
            meta = f"{int(r['goles'])} gol{'es' if int(r['goles']) != 1 else ''} · {int(r['minutos'])}'"
            svg.append(f"<rect x='{x-bar_w/2:.1f}' y='{y0:.1f}' width='{bar_w:.1f}' height='{bh:.1f}' rx='4' fill='#16a34a'/>")
            svg.append(f"<text x='{x:.1f}' y='{max(14,y0-7):.1f}' text-anchor='middle' font-size='11' font-weight='800' fill='#0b6b2e'>{val:.2f}</text>")
            svg.append(f"<text x='{x:.1f}' y='{top+plot_h+22:.1f}' text-anchor='middle' font-size='10' font-weight='700' fill='#102a43' transform='rotate(-28 {x:.1f} {top+plot_h+22:.1f})'>{label}</text>")
            svg.append(f"<text x='{x:.1f}' y='{height-14:.1f}' text-anchor='middle' font-size='9' fill='#6b7c93'>{_safe_html(meta)}</text>")
        svg.append(f"<text x='16' y='{top+plot_h/2:.1f}' transform='rotate(-90 16 {top+plot_h/2:.1f})' text-anchor='middle' font-size='11' font-weight='700' fill='#64748b'>Goles / 90</text>")
        svg.append("</svg>")
        st.markdown("".join(svg), unsafe_allow_html=True)
        st.dataframe(conv[["Jugador", "goles", "minutos", "Goles / 90", "Minutos por gol"]], width="stretch", hide_index=True)
        st.markdown("<div class='note'>Ordenado de mayor a menor eficacia: el mejor G/90 aparece a la izquierda. Las columnas son deliberadamente finas para facilitar la comparación.</div>", unsafe_allow_html=True)
    else:
        st.info("No hay goleadores con minutos registrados para este filtro.")
else:
    st.info("No hay goleadores registrados para este filtro.")

# ---------------- Goles por tramo ----------------
st.markdown("<div style='height:10px'></div><div class='section-title'>Distribución de goles por minuto · A favor y en contra</div>", unsafe_allow_html=True)
st.markdown("<div class='goal-legend'><span><span class='legend-dot' style='background:#16a34a'></span>A favor</span><span><span class='legend-dot' style='background:#ef4444'></span>En contra</span></div>", unsafe_allow_html=True)

goals_for = ev_scope[ev_scope.tipo.isin(["gol", "penalti_gol"])].copy()
goals_against = ev_scope[ev_scope.tipo.isin(["gol_contra", "penalti_contra_gol"])].copy()
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
total_gf = sum(counts_for)
total_gc = sum(counts_against)
total_situations = total_gf + total_gc
activity = [gf + gc for gf, gc in zip(counts_for, counts_against)]
diffs = [gf - gc for gf, gc in zip(counts_for, counts_against)]
pct_for = [(gf / total_gf * 100) if total_gf else 0.0 for gf in counts_for]
pct_against = [(gc / total_gc * 100) if total_gc else 0.0 for gc in counts_against]
pct_activity = [(n / total_situations * 100) if total_situations else 0.0 for n in activity]

def tramo_label(idx):
    lo, hi = bins[idx]
    return f"{lo}–{hi}'"

def fmt_pct(v):
    return f"{v:.1f}%".replace(".0%", "%")

# Macro: primero responder dónde sucede lo importante.
if total_situations:
    idx_activity = max(range(len(bins)), key=lambda i: activity[i])
    idx_favourable = max(range(len(bins)), key=lambda i: (diffs[i], counts_for[i]))
    idx_vulnerable = min(range(len(bins)), key=lambda i: (diffs[i], -counts_against[i]))
    idx_pct_gf = max(range(len(bins)), key=lambda i: pct_for[i])
    idx_pct_gc = max(range(len(bins)), key=lambda i: pct_against[i])
    macro = (
        f"<div class='goal-macro-grid'>"
        f"<div class='goal-macro blue'><div class='t'>🎯 Tramo con más actividad</div><div class='big'>{tramo_label(idx_activity)}</div><div class='big' style='font-size:1.18rem'>{fmt_pct(pct_activity[idx_activity])}</div><div class='sub'>{activity[idx_activity]} situaciones de {total_situations} · {counts_for[idx_activity]} GF · {counts_against[idx_activity]} GC</div></div>"
        f"<div class='goal-macro green'><div class='t'>↗ Tramo más favorable</div><div class='big'>{tramo_label(idx_favourable)}</div><div class='big' style='font-size:1.18rem;color:#15803d'>{diffs[idx_favourable]:+d}</div><div class='sub'>{counts_for[idx_favourable]} GF · {counts_against[idx_favourable]} GC · diferencia</div></div>"
        f"<div class='goal-macro red'><div class='t'>🛡 Tramo más vulnerable</div><div class='big'>{tramo_label(idx_vulnerable)}</div><div class='big' style='font-size:1.18rem;color:#dc2626'>{diffs[idx_vulnerable]:+d}</div><div class='sub'>{counts_for[idx_vulnerable]} GF · {counts_against[idx_vulnerable]} GC · diferencia</div></div>"
        f"<div class='goal-macro purple'><div class='t'>▥ Mayor % de goles a favor</div><div class='big'>{tramo_label(idx_pct_gf)}</div><div class='big' style='font-size:1.18rem'>{fmt_pct(pct_for[idx_pct_gf])}</div><div class='sub'>{counts_for[idx_pct_gf]} de {total_gf} goles a favor</div></div>"
        f"<div class='goal-macro pink'><div class='t'>▥ Mayor % de goles en contra</div><div class='big'>{tramo_label(idx_pct_gc)}</div><div class='big' style='font-size:1.18rem;color:#dc2626'>{fmt_pct(pct_against[idx_pct_gc])}</div><div class='sub'>{counts_against[idx_pct_gc]} de {total_gc} goles en contra</div></div>"
        f"</div>"
    )
    st.markdown(macro, unsafe_allow_html=True)
else:
    st.markdown("<div class='note'>No hay goles registrados en este filtro para calcular patrones por tramo.</div>", unsafe_allow_html=True)

# Nivel medio: seis tramos, primero actividad total y después detalle GF/GC.
blocks = []
for i, ((lo, hi), gf, gc) in enumerate(zip(bins, counts_for, counts_against)):
    def bubble(n, against=False):
        if n == 0:
            size = 32
            klass = "goal-bubble zero"
        else:
            size = 36 + (44 * n / max(1, max_goals))
            klass = "goal-bubble against" if against else "goal-bubble"
        return f"<div class='{klass}' style='width:{size:.0f}px;height:{size:.0f}px'>{n}</div>"
    pa = pct_activity[i]
    pgf, pgc = pct_for[i], pct_against[i]
    blocks.append(
        f"<div class='goal-bin'><div class='goal-range'>{lo}–{hi}'</div>"
        f"<div class='goal-activity'><div class='goal-ring' style='background:conic-gradient(#1d63d8 {pa:.1f}%,#e8edf3 0)'><div class='goal-ring-inner'>{fmt_pct(pa)}</div></div></div>"
        f"<div class='goal-count' style='margin-top:0'>{activity[i]} de {total_situations} situaciones</div>"
        f"<div class='goal-pair'>{bubble(gf)}{bubble(gc, True)}</div>"
        f"<div class='goal-count'><span style='color:#15803d;font-weight:800'>{gf} GF</span> · <span style='color:#dc2626;font-weight:800'>{gc} GC</span></div>"
        f"<div class='goal-pctbox'>"
        f"<div class='goal-pctrow'><span>% GF</span><div class='goal-pcttrack'><div class='goal-pctfill-gf' style='width:{pgf:.1f}%'></div></div><span>{fmt_pct(pgf)} ({gf}/{total_gf})</span></div>"
        f"<div class='goal-pctrow'><span>% GC</span><div class='goal-pcttrack'><div class='goal-pctfill-gc' style='width:{pgc:.1f}%'></div></div><span>{fmt_pct(pgc)} ({gc}/{total_gc})</span></div>"
        f"</div></div>"
    )
st.markdown("<div class='goal-grid'>" + "".join(blocks) + "</div>", unsafe_allow_html=True)

# Micro: tabla corta, solo GF, GC y diferencia como pidió el usuario.
headers = "".join(f"<th>{lo}–{hi}'</th>" for lo, hi in bins) + "<th>Total</th>"
gf_cells = "".join(f"<td>{v}</td>" for v in counts_for) + f"<td><b>{total_gf}</b></td>"
gc_cells = "".join(f"<td>{v}</td>" for v in counts_against) + f"<td><b>{total_gc}</b></td>"
diff_cells_parts = []
for v in diffs:
    cls = "diff-pos" if v > 0 else ("diff-neg" if v < 0 else "diff-zero")
    diff_cells_parts.append(f"<td class='{cls}'>{v:+d}</td>")
total_diff = total_gf - total_gc
cls_total = "diff-pos" if total_diff > 0 else ("diff-neg" if total_diff < 0 else "diff-zero")
diff_cells = "".join(diff_cells_parts) + f"<td class='{cls_total}'><b>{total_diff:+d}</b></td>"
advanced = (
    "<div class='goal-detail-wrap'><div class='goal-detail-title'>⌄ Detalle avanzado por tramo de partido</div>"
    "<table class='goal-detail'><thead><tr><th></th>" + headers + "</tr></thead><tbody>"
    "<tr><td>Goles a favor (GF)</td>" + gf_cells + "</tr>"
    "<tr><td>Goles en contra (GC)</td>" + gc_cells + "</tr>"
    "<tr><td>Diferencia (GF − GC)</td>" + diff_cells + "</tr>"
    "</tbody></table></div>"
)
st.markdown(advanced, unsafe_allow_html=True)
st.markdown(
    "<div class='note'>Lectura de macro a micro: primero se identifica dónde se concentra la actividad; después se compara cada tramo y, por último, se muestra el balance exacto GF/GC. Todo responde a Total/Casa/Fuera y a la jornada seleccionada.</div>",
    unsafe_allow_html=True,
)

# Los círculos rojos de FFCV en el lado del propio equipo se guardan como G.P. (gol en propia), nunca como goleador rival.
gp_count = int(((ev_scope.tipo == "gol_contra") & (ev_scope.jugador == "G.P.")).sum()) if not ev_scope.empty else 0
if gp_count:
    st.markdown(f"<div class='note'><b>G.P.</b> · goles en propia registrados en este filtro: {gp_count}.</div>", unsafe_allow_html=True)

# ---------------- Evolución de la clasificación ----------------
_evo_days = sorted(
    pd.to_numeric(clasificacion.get("jornada"), errors="coerce")
    .dropna().astype(int).unique().tolist()
)
_evo_days = [j for j in _evo_days if j <= 5]
_evo_label = f"J{_evo_days[0]}–J{_evo_days[-1]}" if _evo_days else "Sin jornadas"
st.markdown(
    f"<div style='height:14px'></div><div class='section-title'>Evolución de la clasificación · {_evo_label}</div>",
    unsafe_allow_html=True,
)

evo = clasificacion[clasificacion.jornada.isin(_evo_days)].copy() if _evo_days else pd.DataFrame()
if evo.empty:
    st.info("Sin clasificación histórica cargada.")
else:
    width, height = 1100, 390
    left, right, top, bottom = 70, 30, 28, 50
    plot_w, plot_h = width-left-right, height-top-bottom

    if len(_evo_days) == 1:
        xmap = {_evo_days[0]: left + plot_w/2}
    else:
        xmap = {j: left + i * plot_w/(len(_evo_days)-1) for i, j in enumerate(_evo_days)}

    y = lambda pos: top + (float(pos)-1) * plot_h/15
    accent = (
        "#16a34a" if seleccionado == "Bétera C.F. 'A'" else
        "#991b1b" if seleccionado == "C.D. Acero 'A'" else
        "#c2414b" if seleccionado == "C.F. At. Burriana - Salesianos 'A'" else
        "#f2c400" if seleccionado == "Villarreal C.F. 'C'" else
        "#1d63d8"
    )

    parts = [f"<svg viewBox='0 0 {width} {height}' style='width:100%;height:auto;background:white;border-radius:14px'>"]
    for pos in [1,4,8,12,16]:
        yy = y(pos)
        parts.append(
            f"<line x1='{left}' y1='{yy}' x2='{width-right}' y2='{yy}' stroke='#e5e7eb' stroke-width='1'/>"
            f"<text x='18' y='{yy+5}' font-size='13' fill='#64748b'>{pos}º</text>"
        )
    for j in _evo_days:
        xx = xmap[j]
        parts.append(
            f"<text x='{xx}' y='{height-16}' text-anchor='middle' font-size='14' font-weight='700' fill='#334155'>J{j}</text>"
        )

    for team, g in evo[evo.equipo != seleccionado].groupby("equipo"):
        g = g.sort_values("jornada")
        pts = " ".join(
            f"{xmap[int(r.jornada)]:.1f},{y(r.posicion):.1f}"
            for _, r in g.iterrows() if int(r.jornada) in xmap
        )
        if pts:
            parts.append(f"<polyline points='{pts}' fill='none' stroke='#cbd5e1' stroke-width='1.4' opacity='0.72'/>")

    sel = evo[evo.equipo == seleccionado].sort_values("jornada")
    if not sel.empty:
        pts = " ".join(
            f"{xmap[int(r.jornada)]:.1f},{y(r.posicion):.1f}"
            for _, r in sel.iterrows() if int(r.jornada) in xmap
        )
        parts.append(
            f"<polyline points='{pts}' fill='none' stroke='{accent}' stroke-width='5' "
            f"stroke-linecap='round' stroke-linejoin='round'/>"
        )
        for _, r in sel.iterrows():
            if int(r.jornada) not in xmap:
                continue
            xx, yy = xmap[int(r.jornada)], y(r.posicion)
            parts.append(
                f"<circle cx='{xx}' cy='{yy}' r='6' fill='{accent}'/>"
                f"<text x='{xx}' y='{yy-12}' text-anchor='middle' font-size='14' "
                f"font-weight='800' fill='{accent}'>{int(r.posicion)}º</text>"
            )
    parts.append("</svg>")
    st.markdown("<div class='card'>" + "".join(parts) + "</div>", unsafe_allow_html=True)

    if not sel.empty:
        seq = " → ".join(
            f"J{int(r.jornada)}: {int(r.posicion)}º"
            for _, r in sel.iterrows() if int(r.jornada) in xmap
        )
        st.markdown(
            f"<div class='card' style='border-left:7px solid {accent};margin-top:8px'>"
            f"<b>{_safe_html(seleccionado)}</b> · {seq}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='note'>El equipo seleccionado aparece destacado y la evolución incluye también la J5.</div>",
            unsafe_allow_html=True,
        )

# En vista Total, biblioteca de todos los partidos del equipo con sus enlaces.
if ambito == "Total" and jornada_sel == "Total":
    st.markdown("<div style='height:14px'></div><div class='section-title'>Partidos analizados · enlaces de vídeo</div>", unsafe_allow_html=True)
    _cards = []
    for _, _rr in team_parts.sort_values("jornada").iterrows():
        _j = int(_rr.jornada)
        _fixture = f"{short_team_name(_rr.local)} – {short_team_name(_rr.visitante)}"
        if pd.notna(_rr.goles_local) and pd.notna(_rr.goles_visitante):
            _res = f"{int(_rr.goles_local)}–{int(_rr.goles_visitante)}"
        else:
            _res = "Resultado pendiente"
        _url = match_link(seleccionado, _j)
        _action = (f"<a href='{_safe_html(_url, quote=True)}' target='_blank'>▶ Ver partido</a>" if _url else "<span class='no-link'>Enlace pendiente</span>")
        _cards.append(
            f"<div class='match-link-card'><div class='mj'>Jornada {_j}</div><div class='mf'>{_safe_html(_fixture)}</div><div class='mr'>{_safe_html(_res)}</div>{_action}</div>"
        )
    st.markdown("<div class='match-links-grid'>" + "".join(_cards) + "</div>", unsafe_allow_html=True)

st.caption("V15.12.25 · San José + Colegio Salgui + Cracks + Paterna J1–J5 completos · actas FFCV cargadas · resumen de liga premium.")
