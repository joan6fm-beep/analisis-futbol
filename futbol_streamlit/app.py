import base64
import html
from urllib.parse import quote

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
    # Villarreal C.F. 'C'
    ("Villarreal C.F. 'C'", 1): 'https://youtu.be/45hlhA5vbIc',
    ("Villarreal C.F. 'C'", 2): 'https://app.veo.co/matches/20260912-partido-12-sept-2026-v2488402/',
    ("Villarreal C.F. 'C'", 3): 'https://app.veo.co/matches/20260920-juvenil-a-vs-villareal-cf-v78c4164/',
    ("Villarreal C.F. 'C'", 4): 'https://youtu.be/rUAjYCPcnrI',

    # Alboraya U.D. 'B'
    ("Alboraya U.D. 'B'", 1): 'https://app.veo.co/matches/20260905-jb-vs-alboraia-j1-v1d91d14/',
    ("Alboraya U.D. 'B'", 2): 'https://app.veo.co/matches/20260913-partido-13-sept-2026-v84b4593/',
    ("Alboraya U.D. 'B'", 3): 'https://youtu.be/VXg1XHfeXBA',
    ("Alboraya U.D. 'B'", 4): 'https://youtu.be/QdextLfB2Y0',

    # C.F. Històrics de València 'A'
    ("C.F. Històrics de València 'A'", 1): 'https://youtu.be/45hlhA5vbIc',
    ("C.F. Històrics de València 'A'", 2): 'https://www.hudl.com/notifications-tracking/tracker/BulkDownloadReady-6aa6a4ebec2e6f1b03b0fb2c-c02e9996-8d7e-42ea-a026-e8cc6a5d6803-31946963/email/landing?forward=https%3a%2f%2fvtemp-euw1.hudl.com%2f537691%2f948842%2f3ec%2f6aa65b95b424c17d15c013ec%2f6aa65b95b424c17d15c013ec.mp4%3fv%3d3C8DA47E00000000',
    ("C.F. Històrics de València 'A'", 3): 'https://app.veo.co/matches/20260920-juvenil-b-vs-historics-a-v747c6e4/',
    ("C.F. Històrics de València 'A'", 4): 'https://youtu.be/NdCd04TX9ds',
    ("C.F. Històrics de València 'A'", 5): 'https://app.veo.co/matches/20261004-juvenil-a-b-vs-historics-vf5592c8/',

    # Ath. Massamagrell C.F. 'A'
    ("Ath. Massamagrell C.F. 'A'", 2): 'https://youtu.be/_P_58Dwq4A4?is=93xVEHUBNP4ClMvg',
    ("Ath. Massamagrell C.F. 'A'", 3): 'https://app.veo.co/matches/20260920-juvenil-vs-canet-v2262ac0/',
    ("Ath. Massamagrell C.F. 'A'", 4): 'https://youtu.be/QdextLfB2Y0',
    ("Ath. Massamagrell C.F. 'A'", 5): 'https://app.veo.co/matches/20261004-juvenil-vs-acero-v9528b48/#t=00:06',

    # C.F. Torre Levante 'A'
    ("C.F. Torre Levante 'A'", 1): 'https://youtu.be/jTHRXREAaR4?is=n9rfm2up6QvzUTQT',
    ("C.F. Torre Levante 'A'", 2): 'https://app.veo.co/matches/20260912-partido-12-sept-2026-v9d177d3',
    ("C.F. Torre Levante 'A'", 3): 'https://youtu.be/VXg1XHfeXBA',
    ("C.F. Torre Levante 'A'", 4): 'https://app.veo.co/matches/20260927-untitled-recording-2026-09-27_17-16-26-v42537de/',
    ("C.F. Torre Levante 'A'", 5): 'https://app.veo.co/matches/20261003-ja-vs-burriana-vb158a93/',

    # Primer Toque C.F. 'A'
    ("Primer Toque C.F. 'A'", 1): 'https://app.veo.co/matches/20260906-juvenil-vs-primer-toque-v69cf952/',
    ("Primer Toque C.F. 'A'", 2): 'https://app.veo.co/matches/20260912-juvenil-a-betera-ve022cb5/',
    ("Primer Toque C.F. 'A'", 3): 'https://app.veo.co/matches/20260919-juvenil-a-manises-v678eca9/',
    ("Primer Toque C.F. 'A'", 4): 'https://app.veo.co/matches/20260927-partido-cdf-canet-vae71aeb',
    ("Primer Toque C.F. 'A'", 5): 'https://app.veo.co/matches/20261003-juvenil-a-alboraya-v1bf5286/',

    # C.F. At. Burriana - Salesianos 'A'
    ("C.F. At. Burriana - Salesianos 'A'", 1): 'https://app.veo.co/matches/20260905-juvenil-a-burriana-v4434b85/',
    ("C.F. At. Burriana - Salesianos 'A'", 2): 'https://app.veo.co/matches/20260913-juvenil-a-contra-patacona-v7ea2f8f/',
    ("C.F. At. Burriana - Salesianos 'A'", 3): 'https://app.veo.co/matches/20260919-jb-vs-at-burriana-salesianos-v00500cf',
    ("C.F. At. Burriana - Salesianos 'A'", 4): 'https://app.veo.co/matches/20260927-untitled-recording-2026-09-27_17-07-43-v157dcb5',
    ("C.F. At. Burriana - Salesianos 'A'", 5): 'https://app.veo.co/matches/20261003-ja-vs-burriana-vb158a93/',

    # C.F. Inter San José Valencia 'B'
    ("C.F. Inter San José Valencia 'B'", 1): 'https://app.veo.co/matches/20260905-jb-vs-alboraia-j1-v1d91d14/',
    ("C.F. Inter San José Valencia 'B'", 2): 'https://app.veo.co/matches/20260913-untitled-recording-2026-09-13_17-14-50-va669c7b',
    ("C.F. Inter San José Valencia 'B'", 3): 'https://app.veo.co/matches/20260919-jb-vs-at-burriana-salesianos-v00500cf',
    ("C.F. Inter San José Valencia 'B'", 4): 'https://youtu.be/NdCd04TX9ds',
    ("C.F. Inter San José Valencia 'B'", 5): 'https://app.veo.co/matches/20261003-jb-cf-inter-san-jose-v9869d5c',

    # Col. Salgui E.D.E. 'A'
    ("Col. Salgui E.D.E. 'A'", 1): 'https://app.veo.co/matches/20260906-juvenil-a-vs-col-salgui-v9022f29/',
    ("Col. Salgui E.D.E. 'A'", 2): 'https://app.veo.co/matches/20260912-partido-12-sept-2026-v2488402/',
    ("Col. Salgui E.D.E. 'A'", 3): 'https://live.veo.co/web-app/matches/20260920-juvenil-a-salgui-v501c2b2/',
    ("Col. Salgui E.D.E. 'A'", 4): 'https://app.veo.co/matches/20260926-salgui-a-vs-pcf-juvenil-b-v189bc7b/',
    ("Col. Salgui E.D.E. 'A'", 5): 'https://app.veo.co/matches/20261003-jb-cf-inter-san-jose-v9869d5c',

    # Bétera C.F. 'A'
    ("Bétera C.F. 'A'", 1): 'https://app.veo.co/matches/20260906-juvenil-a-vs-col-salgui-v9022f29/',
    ("Bétera C.F. 'A'", 2): 'https://app.veo.co/matches/20260912-juvenil-a-betera-ve022cb5/',
    ("Bétera C.F. 'A'", 3): 'https://app.veo.co/matches/20260920-juvenil-a-vs-villareal-cf-v78c4164/',
    ("Bétera C.F. 'A'", 4): 'https://youtu.be/FwkojfoAnAs?is=a3cp8o-yYGS8kTXm',
    ("Bétera C.F. 'A'", 5): 'https://app.veo.co/matches/20261004-betera-club-de-futbol-vs-paterna-cf-v008edcc',

    # C.F. Cracks 'A'
    ("C.F. Cracks 'A'", 1): 'https://c.veocdn.com/8fc1ea5f-3004-405f-861c-69625be31349/standard/machine/21e3ada9/video.mp4',
    ("C.F. Cracks 'A'", 2): 'https://app.veo.co/matches/20260913-partido-13-sept-2026-v84b4593/',
    ("C.F. Cracks 'A'", 3): 'https://app.veo.co/matches/20260919-juvenil-a-b-vs-ja-cd-acero-v3e5feb3/#t=05:45',
    ("C.F. Cracks 'A'", 4): 'https://app.veo.co/matches/20260927-untitled-recording-2026-09-27_17-07-43-v157dcb5',
    ("C.F. Cracks 'A'", 5): 'https://app.veo.co/matches/20261004-juvenil-a-b-vs-historics-vf5592c8/',

    # Paterna C.F. 'A'
    ("Paterna C.F. 'A'", 1): 'https://app.veo.co/matches/20260905-juvenil-a-burriana-v4434b85/',
    ("Paterna C.F. 'A'", 2): 'https://www.hudl.com/notifications-tracking/tracker/BulkDownloadReady-6aa6a4ebec2e6f1b03b0fb2c-c02e9996-8d7e-42ea-a026-e8cc6a5d6803-31946963/email/landing?forward=https%3a%2f%2fvtemp-euw1.hudl.com%2f537691%2f948842%2f3ec%2f6aa65b95b424c17d15c013ec%2f6aa65b95b424c17d15c013ec.mp4%3fv%3d3C8DA47E00000000',
    ("Paterna C.F. 'A'", 3): 'https://live.veo.co/web-app/matches/20260920-juvenil-a-salgui-v501c2b2/',
    ("Paterna C.F. 'A'", 4): 'https://youtu.be/rUAjYCPcnrI',
    ("Paterna C.F. 'A'", 5): 'https://app.veo.co/matches/20261004-betera-club-de-futbol-vs-paterna-cf-v008edcc',

    # Manises C.F. 'A'
    ("Manises C.F. 'A'", 1): 'https://youtu.be/jTHRXREAaR4?is=n9rfm2up6QvzUTQT',
    ("Manises C.F. 'A'", 2): 'https://youtu.be/_P_58Dwq4A4?is=93xVEHUBNP4ClMvg',
    ("Manises C.F. 'A'", 4): 'https://youtu.be/FwkojfoAnAs?is=a3cp8o-yYGS8kTXm',
    ("Manises C.F. 'A'", 5): 'https://youtu.be/_vzhitDWnfQ?is=yqDzdU5SNdsnwhbo',

    # Patacona C.F. 'B'
    ("Patacona C.F. 'B'", 1): 'https://app.veo.co/matches/20260906-patacona-cf-jb-vs-acero-v97c8cc3/',
    ("Patacona C.F. 'B'", 2): 'https://app.veo.co/matches/20260913-juvenil-a-contra-patacona-v7ea2f8f/',
    ("Patacona C.F. 'B'", 3): 'https://app.veo.co/matches/20260920-juvenil-b-vs-historics-a-v747c6e4/',
    ("Patacona C.F. 'B'", 4): 'https://app.veo.co/matches/20260926-salgui-a-vs-pcf-juvenil-b-v189bc7b/',

    # C.D. Acero 'A'
    ("C.D. Acero 'A'", 1): 'https://app.veo.co/matches/20260906-patacona-cf-jb-vs-acero-v97c8cc3/',
    ("C.D. Acero 'A'", 2): 'https://app.veo.co/matches/20260913-untitled-recording-2026-09-13_17-14-50-va669c7b',
    ("C.D. Acero 'A'", 3): 'https://app.veo.co/matches/20260919-juvenil-a-b-vs-ja-cd-acero-v3e5feb3/#t=05:45',
    ("C.D. Acero 'A'", 4): 'https://app.veo.co/matches/20260927-untitled-recording-2026-09-27_17-16-26-v42537de/',
    ("C.D. Acero 'A'", 5): 'https://app.veo.co/matches/20261004-juvenil-vs-acero-v9528b48/#t=00:06',

    # C.D.F. Canet 'A'
    ("C.D.F. Canet 'A'", 1): 'https://c.veocdn.com/8fc1ea5f-3004-405f-861c-69625be31349/standard/machine/21e3ada9/video.mp4',
    ("C.D.F. Canet 'A'", 2): 'https://app.veo.co/matches/20260912-partido-12-sept-2026-v9d177d3',
    ("C.D.F. Canet 'A'", 3): 'https://app.veo.co/matches/20260920-juvenil-vs-canet-v2262ac0/',
    ("C.D.F. Canet 'A'", 5): 'https://youtu.be/_vzhitDWnfQ?is=yqDzdU5SNdsnwhbo',
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
    "jugadores_perfil.csv": ["jugador", "altura_cm", "peso_kg", "course_navette", "fecha_medicion"],
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
[data-testid="stSidebar"] {{background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border-right:1px solid #dfe8f2;}}
[data-testid="stSidebar"] .block-container {{padding-top:.9rem;padding-left:.8rem;padding-right:.8rem;}}

.brand-box {{position:relative;overflow:hidden;display:flex;align-items:center;gap:13px;background:linear-gradient(145deg,#062d5a 0%,#0a467f 100%);color:white;border-radius:19px;padding:15px 14px;margin-bottom:16px;box-shadow:0 12px 28px rgba(6,45,90,.20);border:1px solid rgba(255,255,255,.08)}}
.brand-box:after {{content:"";position:absolute;width:110px;height:110px;border-radius:50%;right:-48px;top:-55px;background:rgba(255,255,255,.08)}}
.brand-logo {{position:relative;z-index:1;width:54px;height:54px;flex:0 0 54px;border-radius:15px;background:#fff;display:flex;align-items:center;justify-content:center;padding:5px;box-sizing:border-box;box-shadow:0 7px 18px rgba(0,0,0,.14)}}
.brand-logo img {{width:100%;height:100%;object-fit:contain;display:block}}
.brand-copy {{position:relative;z-index:1;min-width:0}}
.brand-kicker {{font-size:.60rem;font-weight:900;letter-spacing:.13em;text-transform:uppercase;color:#bcd5ef;margin-bottom:3px}}
.brand-main {{font-weight:950;line-height:1.05;font-size:.98rem;letter-spacing:.01em}} .brand-main span {{color:#ffcc57}}
.brand-sub {{font-size:.68rem;opacity:.82;margin-top:5px;line-height:1.25}}
.brand-chip {{display:inline-block;margin-top:7px;background:rgba(245,158,11,.18);border:1px solid rgba(255,204,87,.42);color:#ffd166;border-radius:999px;padding:3px 7px;font-size:.56rem;font-weight:900;letter-spacing:.05em}}
.side-label {{font-size:.70rem;font-weight:950;color:#708399;text-transform:uppercase;letter-spacing:.07em;margin:.7rem .25rem .28rem}}
.team-count {{font-size:.75rem;color:#7c8ea4;margin-top:.35rem}}

/* Navegación lateral: apariencia de menú, no de formulario */
[data-testid="stSidebar"] [role="radiogroup"] {{display:flex;flex-direction:column;gap:6px;}}
[data-testid="stSidebar"] [role="radiogroup"] label {{position:relative;margin:0!important;padding:0!important;border-radius:12px;transition:.16s ease;}}
[data-testid="stSidebar"] [role="radiogroup"] label > div {{width:100%;}}
[data-testid="stSidebar"] [role="radiogroup"] label p {{font-size:.82rem!important;font-weight:820!important;color:#304b68!important;margin:0!important;line-height:1.2!important;}}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input) {{background:#fff;border:1px solid #e6edf5;box-shadow:0 2px 7px rgba(15,42,68,.035);padding:9px 11px!important;}}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input):hover {{transform:translateX(2px);border-color:#cbdcec;background:#f7fbff;box-shadow:0 5px 12px rgba(15,42,68,.06);}}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{background:linear-gradient(90deg,#eef6ff 0%,#ffffff 100%);border-color:#a9c8e8;box-shadow:inset 4px 0 0 #f59e0b,0 5px 14px rgba(29,99,216,.08);}}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{color:#062d5a!important;font-weight:950!important;}}
[data-testid="stSidebar"] [role="radiogroup"] input {{display:none!important;}}

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
.goaltype-wrap {{margin:14px 0 4px}}
.goaltype-head {{border-left:3px solid #f4b51c;padding-left:12px;margin:4px 0 10px}}
.goaltype-head .gt-title {{font-size:1rem;font-weight:950;color:{NAVY}}}
.goaltype-head .gt-sub {{font-size:.72rem;color:{MUTED};margin-top:2px}}
.goaltype-card {{background:#fff;border:1px solid #e3e9f0;border-radius:15px;padding:13px 14px 10px;margin:10px 0;box-shadow:0 5px 16px rgba(16,42,67,.04)}}
.goaltype-card .gt-side {{font-size:.78rem;font-weight:950;color:{NAVY};margin-bottom:8px}}
.goaltype-grid {{display:grid;grid-template-columns:150px repeat(6,minmax(58px,1fr)) 34px;align-items:center;gap:0;width:100%}}
.gt-top {{font-size:.7rem;font-weight:950;text-align:center;padding:2px 2px 5px;color:#16a36a}}
.gt-top.against {{color:#e05263}}
.gt-rowlab {{font-size:.68rem;font-weight:850;color:{NAVY};padding:7px 6px 7px 0;white-space:nowrap}}
.gt-cell {{min-height:35px;border-left:1px dashed #d8e1eb;display:flex;align-items:center;justify-content:center;position:relative}}
.gt-cell:nth-child(even) {{background:rgba(234,241,249,.35)}}
.gt-dot {{width:4px;height:4px;border-radius:50%;background:#cbd5e1}}
.gt-bubble {{border-radius:50%;display:grid;place-items:center;color:#fff;font-size:.7rem;font-weight:950;border:1px solid rgba(255,255,255,.9);box-shadow:0 3px 10px rgba(0,0,0,.12);cursor:help}}
.gt-bubble.for {{background:#38a879}} .gt-bubble.against {{background:#dc6075}}
.gt-total {{text-align:right;font-size:.72rem;font-weight:950;color:{NAVY};padding-left:5px}}
.gt-foot {{font-size:.66rem;font-weight:850;color:#51657e;text-align:center;padding-top:7px;border-top:1px solid #e6ebf1}}
.gt-foot.blank {{border-top-color:transparent}}
.goal-diff-card {{background:#fff;border:1px solid #e3e9f0;border-radius:15px;padding:12px 14px;margin:14px 0;box-shadow:0 5px 16px rgba(16,42,67,.04)}}
.goal-diff-title {{font-size:.8rem;font-weight:950;color:{NAVY};margin-bottom:6px}}
@media (max-width:900px) {{.goaltype-grid {{grid-template-columns:120px repeat(6,minmax(48px,1fr)) 28px}} .gt-rowlab {{font-size:.61rem}}}}
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
.league-subrank-title{{font-size:1rem;font-weight:950;color:#082f5b;margin:16px 0 8px;display:flex;align-items:center;gap:8px}}
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
.ranking-scroll {{max-height:690px;overflow-y:auto;overflow-x:hidden;border:1px solid #e7ecf2;border-radius:12px;background:white}}
.ranking-scroll table {{margin:0!important;border:0!important;width:100%!important;min-width:0!important;table-layout:fixed!important}}
.ranking-scroll thead th {{position:sticky;top:0;z-index:3;background:#f7f9fc!important}}
.ranking-scroll th,.ranking-scroll td {{padding-left:5px!important;padding-right:5px!important}}
.ranking-scroll .rank-pos {{width:38px!important;min-width:38px!important;max-width:38px!important}}
.ranking-scroll .rank-goals {{width:46px!important;min-width:46px!important;max-width:46px!important;text-align:center!important}}
.ranking-scroll .rank-min {{width:54px!important;min-width:54px!important;max-width:54px!important;text-align:center!important}}
.ranking-scroll .rank-rate {{width:64px!important;min-width:64px!important;max-width:64px!important;text-align:center!important}}
.ranking-scroll .rank-player {{width:38%!important;min-width:0!important;white-space:normal!important;overflow-wrap:anywhere}}
.ranking-scroll .rank-team {{width:auto!important;min-width:0!important;white-space:normal!important}}
.ranking-scroll .rank-team span {{white-space:normal!important;overflow-wrap:anywhere;line-height:1.05}}
.ranking-scroll .rank-team img {{flex:0 0 auto}}
.ranking-pair-title {{margin-top:6px!important}}
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

/* ===== MOBILE BETA / PWA-LIKE EXPERIENCE ===== */
.mobile-bottom-nav {{display:none}}
.mobile-rival-strip {{display:none}}
.mobile-install-note {{display:none}}
@media (max-width: 768px) {{
  html, body {{overflow-x:hidden!important}}
  [data-testid="stSidebar"] {{display:none!important}}
  [data-testid="stHeader"] {{height:2.35rem;background:rgba(245,247,251,.92)!important;backdrop-filter:blur(10px);}}
  .block-container {{padding:.45rem .62rem 6.7rem!important;max-width:100%!important}}
  .topbar {{border-radius:13px;padding:10px 12px;margin:0 0 9px;min-height:48px}}
  .topbar .title {{font-size:.78rem;line-height:1.2;letter-spacing:.01em}}
  .topbar .nav {{display:none!important}}
  .section-title {{font-size:1rem;margin:.12rem 0 .5rem}}
  .team-head {{padding:12px 13px;gap:11px;border-radius:14px}}
  .team-head img {{width:58px;height:58px}}
  .team-name {{font-size:1.28rem}}
  .team-sub {{font-size:.78rem}}
  .badge {{font-size:.68rem;padding:4px 8px}}
  .card {{padding:12px;border-radius:13px}}
  .kpi {{min-height:88px}}
  .kpi .v {{font-size:1.38rem}}
  .kpi .l {{font-size:.70rem;margin-top:5px}}
  [data-testid="stMetric"] {{padding:8px 10px;border-radius:12px}}
  [data-testid="stMetricValue"] {{font-size:1.35rem!important}}
  [data-testid="stMetricLabel"] {{font-size:.68rem!important}}
  [data-testid="stHorizontalBlock"] {{gap:.45rem!important}}
  [data-testid="column"] {{min-width:0!important}}
  .league-hero {{padding:13px!important;border-radius:14px!important}}
  .league-kpis,.league-kpis-6 {{gap:7px!important}}
  .league-kpi {{padding:9px 10px;border-radius:12px}}
  .league-kpi .v {{font-size:1rem}}
  .league-kpi .k,.league-kpi .s {{font-size:.64rem}}
  .league-table {{min-width:0!important;width:100%!important;table-layout:fixed!important;font-size:.65rem!important}}
  .league-table th,.league-table td {{padding:5px 2px!important;overflow:hidden;text-overflow:ellipsis}}
  .league-table .team-col {{width:auto!important;min-width:0!important;max-width:none!important;white-space:normal!important;line-height:1.05}}
  .league-table .pos-col {{width:25px!important;min-width:25px!important}}
  .league-table .stat-col {{width:28px!important;min-width:28px!important}}
  .main-standings .team-col,.performance-table .team-col {{min-width:0!important;width:auto!important;font-size:.70rem!important}}
  .main-standings td,.main-standings th,.performance-table td,.performance-table th {{font-size:.66rem!important}}
  .ranking-scroll {{max-height:520px;border-radius:10px}}
  .ranking-scroll table {{font-size:.67rem!important}}
  .ranking-scroll th,.ranking-scroll td {{padding:5px 3px!important}}
  .ranking-scroll .rank-pos {{width:27px!important;min-width:27px!important;max-width:27px!important}}
  .ranking-scroll .rank-goals {{width:36px!important;min-width:36px!important;max-width:36px!important}}
  .ranking-scroll .rank-min {{width:42px!important;min-width:42px!important;max-width:42px!important}}
  .ranking-scroll .rank-rate {{width:49px!important;min-width:49px!important;max-width:49px!important}}
  .ranking-scroll .rank-player {{width:39%!important}}
  .match-links-grid {{grid-template-columns:1fr!important;gap:8px}}
  .match-link-card {{padding:11px}}
  .venue-kpi-grid {{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}}
  .venue-kpi {{padding:9px 10px;gap:7px}}
  .vk-value {{font-size:1.18rem}}
  .goaltype-card {{padding:10px 7px;overflow:hidden}}
  .goaltype-grid {{grid-template-columns:82px repeat(6,minmax(32px,1fr)) 22px;font-size:.57rem}}
  .gt-rowlab {{font-size:.54rem;white-space:normal;line-height:1.05}}
  .gt-top,.gt-foot,.gt-total {{font-size:.55rem}}
  .gt-cell {{min-height:31px}}
  .goal-diff-card {{padding:9px 8px}}
  .home-photo-card img {{height:210px}}
  .pitch {{border-radius:9px}}
  .pchip {{font-size:.53rem;min-width:43px}}
  .shirt {{width:28px;height:25px;font-size:.68rem}}
  .heat-wrap {{border-radius:11px;padding:7px;max-width:100%;overflow-x:auto}}
  table.heat {{font-size:.64rem}}
  .mobile-install-note {{display:flex;align-items:center;gap:10px;background:linear-gradient(135deg,#062d5a,#0a467f);color:#fff;border-radius:14px;padding:11px 12px;margin:4px 0 10px;box-shadow:0 7px 20px rgba(6,45,90,.16)}}
  .mobile-install-note .mi-icon {{width:38px;height:38px;border-radius:11px;background:#fff;display:grid;place-items:center;flex:0 0 38px}}
  .mobile-install-note .mi-icon img {{width:30px;height:30px;object-fit:contain}}
  .mobile-install-note .mi-copy {{font-size:.68rem;line-height:1.25}}
  .mobile-install-note .mi-copy b {{font-size:.78rem;display:block;margin-bottom:2px}}
  .mobile-rival-strip {{display:flex;gap:7px;overflow-x:auto;scrollbar-width:none;padding:2px 1px 8px;margin:0 0 4px;-webkit-overflow-scrolling:touch}}
  .mobile-rival-strip::-webkit-scrollbar {{display:none}}
  .mobile-rival-chip {{flex:0 0 auto;display:flex;align-items:center;gap:5px;padding:6px 8px;border:1px solid #dfe7f0;border-radius:999px;background:#fff;text-decoration:none!important;color:#294863!important;font-size:.65rem;font-weight:850;box-shadow:0 2px 7px rgba(16,42,67,.04)}}
  .mobile-rival-chip.active {{background:#062d5a;color:#fff!important;border-color:#062d5a}}
  .mobile-rival-chip img {{width:20px!important;height:20px!important;object-fit:contain}}
  .mobile-bottom-nav {{display:grid;grid-template-columns:repeat(6,1fr);position:fixed;left:8px;right:8px;bottom:8px;z-index:999999;background:rgba(255,255,255,.97);border:1px solid #dbe4ee;border-radius:18px;padding:6px 4px calc(6px + env(safe-area-inset-bottom));box-shadow:0 12px 32px rgba(6,45,90,.18);backdrop-filter:blur(16px)}}
  .mobile-bottom-nav a {{text-decoration:none!important;color:#6a7d91!important;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-height:44px;border-radius:12px;font-size:.55rem;font-weight:850;line-height:1.05}}
  .mobile-bottom-nav a .mn-icon {{font-size:1.05rem;line-height:1}}
  .mobile-bottom-nav a.active {{background:#eef6ff;color:#062d5a!important;box-shadow:inset 0 -3px 0 #f59e0b}}
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

    # ---------------- Rankings individuales de liga ----------------
    min_scope = minutos[pd.to_numeric(minutos.get("jornada"), errors="coerce").le(jmax)].copy()
    ali_scope = alineaciones[pd.to_numeric(alineaciones.get("jornada"), errors="coerce").le(jmax)].copy()
    if not min_scope.empty:
        min_scope["minutos"] = pd.to_numeric(min_scope["minutos"], errors="coerce").fillna(0)
        min_scope["titular"] = pd.to_numeric(min_scope["titular"], errors="coerce").fillna(0)

    # Goles propios: los autogoles rivales cuentan en el marcador, pero no se atribuyen
    # a un goleador del equipo.
    gf_player_events = ev[ev["tipo"].astype(str).isin(["gol", "penalti_gol"])].copy()
    if not gf_player_events.empty:
        own_mask = gf_player_events.get("detalle", pd.Series(index=gf_player_events.index, dtype=object)).astype(str).str.contains("propia", case=False, na=False)
        placeholder_mask = gf_player_events.get("jugador", pd.Series(index=gf_player_events.index, dtype=object)).astype(str).str.strip().isin(["", "G.P.", "GP", "Autogol", "nan", "None"])
        gf_player_events = gf_player_events[~own_mask & ~placeholder_mask].copy()

    # 1) Máximos goleadores.
    scorer_rows = []
    if not gf_player_events.empty:
        goals = (gf_player_events.groupby(["equipo", "jugador"], as_index=False)
                 .agg(goles=("tipo", "size")))
        goals = goals.sort_values(["goles", "jugador"], ascending=[False, True]).reset_index(drop=True)
        for pos, r in goals.iterrows():
            scorer_rows.append(
                "<tr>"
                f"<td class='pos-col rank-pos'><b>{pos+1}</b></td>"
                f"<td class='team-col rank-player'><b>{_safe_html(str(r.jugador))}</b></td>"
                f"<td class='team-col rank-team'>{_team_logo_tag(str(r.equipo),24)}<span>{_safe_html(clean_name(str(r.equipo)))}</span></td>"
                f"<td class='stat-num rank-goals'><b>{int(r.goles)}</b></td>"
                "</tr>"
            )

    # 2) Eficacia goleadora por minutos.
    efficiency_rows = []
    if not gf_player_events.empty and not min_scope.empty:
        goals_simple = gf_player_events.groupby(["equipo", "jugador"], as_index=False).size().rename(columns={"size":"goles"})
        mins_simple = min_scope.groupby(["equipo", "jugador"], as_index=False)["minutos"].sum()
        eff = goals_simple.merge(mins_simple, on=["equipo", "jugador"], how="left")
        eff["minutos"] = pd.to_numeric(eff["minutos"], errors="coerce").fillna(0)
        eff = eff[eff["minutos"] > 0].copy()
        if not eff.empty:
            eff["min_gol"] = eff["minutos"] / eff["goles"]
            eff = eff.sort_values(["min_gol", "goles", "minutos", "jugador"], ascending=[True, False, True, True]).reset_index(drop=True)
            for pos, r in eff.iterrows():
                efficiency_rows.append(
                    "<tr>"
                    f"<td class='pos-col rank-pos'><b>{pos+1}</b></td>"
                    f"<td class='team-col rank-player'><b>{_safe_html(str(r.jugador))}</b></td>"
                    f"<td class='team-col rank-team'>{_team_logo_tag(str(r.equipo),24)}<span>{_safe_html(clean_name(str(r.equipo)))}</span></td>"
                    f"<td class='stat-num rank-goals'><b>{int(r.goles)}</b></td>"
                    f"<td class='stat-num rank-min'>{int(round(float(r.minutos)))}</td>"
                    f"<td class='stat-num rank-rate'><b>{float(r.min_gol):.1f}</b></td>"
                    "</tr>"
                )

    st.markdown("<div class='section-title league-section-title'>Rankings individuales</div>", unsafe_allow_html=True)
    rank_col1, rank_col2 = st.columns(2, gap="medium")
    with rank_col1:
        st.markdown("<div class='league-subrank-title ranking-pair-title'>⚽ Goleadores</div>", unsafe_allow_html=True)
        if scorer_rows:
            st.markdown(
                "<div class='goal-time-note'>Ranking por goles marcados. Desliza dentro de la tabla para ver el resto.</div>"
                "<div class='ranking-scroll'><table class='heat league-table premium-table performance-table'>"
                "<thead><tr><th class='rank-pos'>Pos.</th><th class='team-col rank-player'>Jugador</th><th class='team-col rank-team'>Equipo</th><th class='rank-goals'>Goles</th></tr></thead>"
                "<tbody>" + "".join(scorer_rows) + "</tbody></table></div>", unsafe_allow_html=True)
        else:
            st.info("No hay goles individuales cargados para este filtro.")

    with rank_col2:
        st.markdown("<div class='league-subrank-title ranking-pair-title'>⏱️ Eficacia goleadora</div>", unsafe_allow_html=True)
        if efficiency_rows:
            st.markdown(
                "<div class='goal-time-note'>Menos Min/Gol = mayor eficacia. Desliza dentro de la tabla para ver el resto.</div>"
                "<div class='ranking-scroll'><table class='heat league-table premium-table performance-table'>"
                "<thead><tr><th class='rank-pos'>Pos.</th><th class='team-col rank-player'>Jugador</th><th class='team-col rank-team'>Equipo</th><th class='rank-goals'>G</th><th class='rank-min'>Min</th><th class='rank-rate'>Min/Gol</th></tr></thead>"
                "<tbody>" + "".join(efficiency_rows) + "</tbody></table></div>", unsafe_allow_html=True)
        else:
            st.info("No hay goleadores con minutos registrados para este filtro.")

    # 3) Porteros: goles encajados durante sus minutos reales/reconstruidos.
    keeper_rows = []
    if not ali_scope.empty and not min_scope.empty:
        keeper_names = ali_scope[ali_scope.get("rol", pd.Series(dtype=object)).astype(str).eq("POR")][["equipo", "jugador"]].drop_duplicates()
        kmins = min_scope.merge(keeper_names.assign(es_portero=1), on=["equipo", "jugador"], how="inner")
        if not kmins.empty:
            # Asignamos cada gol encajado al portero que estaba sobre el campo según titularidad y minutos.
            gc_events = ev[ev["tipo"].astype(str).isin(["gol_contra", "penalti_contra_gol"])].copy()
            conceded = {}
            for _, ge in gc_events.iterrows():
                try:
                    gj = int(float(ge.jornada)); gm = int(float(ge.minuto)); gt = str(ge.equipo)
                except Exception:
                    continue
                cand = kmins[(kmins["equipo"].astype(str) == gt) & (pd.to_numeric(kmins["jornada"], errors="coerce") == gj) & (kmins["minutos"] > 0)].copy()
                on_pitch = []
                for _, kr in cand.iterrows():
                    km = float(kr.minutos); starter = int(float(kr.titular)) == 1
                    start = 0.0 if starter else max(0.0, 90.0-km)
                    end = min(90.0, km) if starter else 90.0
                    if start < gm <= end or (gm == 0 and start == 0):
                        on_pitch.append(str(kr.jugador))
                if len(on_pitch) == 1:
                    key = (gt, on_pitch[0])
                    conceded[key] = conceded.get(key, 0) + 1

            kg = kmins.groupby(["equipo", "jugador"], as_index=False)["minutos"].sum()
            kg = kg[kg["minutos"] > 0].copy()
            kg["gc"] = [conceded.get((str(r.equipo), str(r.jugador)), 0) for _, r in kg.iterrows()]
            kg["min_gc"] = kg.apply(lambda r: (float(r.minutos)/int(r.gc)) if int(r.gc) > 0 else float("inf"), axis=1)
            kg["gc90"] = kg["gc"] * 90.0 / kg["minutos"]
            kg = kg.sort_values(["gc90", "minutos", "gc", "jugador"], ascending=[True, False, True, True]).reset_index(drop=True)
            for pos, r in kg.iterrows():
                min_gc_txt = "—" if int(r.gc) == 0 else f"{float(r.min_gc):.1f}"
                keeper_rows.append(
                    "<tr>"
                    f"<td class='pos-col rank-pos'><b>{pos+1}</b></td>"
                    f"<td class='team-col rank-player'><b>{_safe_html(str(r.jugador))}</b></td>"
                    f"<td class='team-col rank-team'>{_team_logo_tag(str(r.equipo),24)}<span>{_safe_html(clean_name(str(r.equipo)))}</span></td>"
                    f"<td class='stat-num rank-min'>{int(round(float(r.minutos)))}</td>"
                    f"<td class='stat-num rank-goals'><b>{int(r.gc)}</b></td>"
                    f"<td class='stat-num rank-rate'>{min_gc_txt}</td>"
                    f"<td class='stat-num rank-rate'><b>{float(r.gc90):.2f}</b></td>"
                    "</tr>"
                )

    st.markdown("<div class='league-subrank-title'>🧤 Porteros · goles encajados por minutos jugados</div>", unsafe_allow_html=True)
    if keeper_rows:
        st.markdown(
            "<div class='goal-time-note'>GC/90 más bajo = mejor registro. La tabla muestra unas 20 filas y permite desplazarse dentro para ver todos los porteros.</div>"
            "<div class='ranking-scroll'><table class='heat league-table premium-table performance-table'>"
            "<thead><tr><th class='rank-pos'>Pos.</th><th class='team-col rank-player'>Portero</th><th class='team-col rank-team'>Equipo</th><th class='rank-min'>Min</th><th class='rank-goals'>GC</th><th class='rank-rate'>Min/GC</th><th class='rank-rate'>GC/90</th></tr></thead>"
            "<tbody>" + "".join(keeper_rows) + "</tbody></table></div>", unsafe_allow_html=True)
    else:
        st.info("No hay minutaje de porteros suficiente para este filtro.")

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
    st.markdown(f"<div class='section-title league-section-title'>Rendimiento · casa y fuera · J1–J{jmax}</div>", unsafe_allow_html=True)
    tab_casa, tab_fuera = st.tabs(["🏠 Casa", "✈️ Fuera"])

    def _perf_rows(side):
        ranking = []
        # La tabla casa/fuera se construye directamente desde los partidos cargados.
        # Esto evita que quede desactualizada si la clasificación manual todavía no se ha refrescado.
        teams_perf = sorted(
            set(tab["equipo"].astype(str).tolist())
            | set(valid["local"].astype(str).tolist())
            | set(valid["visitante"].astype(str).tolist()),
            key=lambda x: clean_name(x).lower(),
        )
        for team in teams_perf:
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
            "<div class='perf-explainer'><b>Clasificación como local</b> · calculada con todos los partidos cargados hasta la jornada seleccionada. Orden: puntos, diferencia de goles y goles a favor.</div>",
            unsafe_allow_html=True,
        )
        st.markdown(_small_result_table(_perf_rows("casa")), unsafe_allow_html=True)

    with tab_fuera:
        st.markdown(
            "<div class='perf-explainer'><b>Clasificación como visitante</b> · calculada con todos los partidos cargados hasta la jornada seleccionada. Orden: puntos, diferencia de goles y goles a favor.</div>",
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


def render_team_360():
    """Dashboard 360º de Primer Toque: rendimiento propio + qué hacen los rivales contra nosotros."""
    TEAM = "Primer Toque C.F. 'A'"
    partidos_t = load_csv("partidos_rivales.csv")
    eventos_t = load_csv("eventos_rivales.csv")
    minutos_t = load_csv("minutos_rivales.csv")
    clasif_t = load_csv("clasificacion_liga.csv")
    avanzado_t = load_csv("equipo_avanzado.csv")

    tp = partidos_t[(partidos_t["local"] == TEAM) | (partidos_t["visitante"] == TEAM)].copy()
    tp = tp.sort_values("jornada")
    if tp.empty:
        st.info("Todavía no hay partidos de Primer Toque cargados.")
        return

    rows = []
    for _, r in tp.iterrows():
        is_home = str(r["local"]) == TEAM
        gf = int(r["goles_local"] if is_home else r["goles_visitante"])
        gc = int(r["goles_visitante"] if is_home else r["goles_local"])
        rival = str(r["visitante"] if is_home else r["local"])
        pts = 3 if gf > gc else (1 if gf == gc else 0)
        res = "V" if gf > gc else ("E" if gf == gc else "D")
        rows.append({
            "jornada": int(r["jornada"]), "rival": rival, "condicion": "Casa" if is_home else "Fuera",
            "gf": gf, "gc": gc, "dg": gf-gc, "pts": pts, "res": res,
            "sistema": str(r["sistema_local"] if is_home else r["sistema_visitante"]),
        })
    md = pd.DataFrame(rows)
    md["pts_acum"] = md["pts"].cumsum()
    md["dg_acum"] = md["dg"].cumsum()

    pj = len(md); pg = int((md.res == "V").sum()); pe = int((md.res == "E").sum()); pp = int((md.res == "D").sum())
    gf_tot = int(md.gf.sum()); gc_tot = int(md.gc.sum()); pts_tot = int(md.pts.sum()); dg_tot = gf_tot-gc_tot
    porterias_cero = int((md.gc == 0).sum()); sin_marcar = int((md.gf == 0).sum())

    # Posición actual desde la última jornada disponible.
    pos = "—"
    try:
        cc = clasif_t[(clasif_t["equipo"] == TEAM) & (clasif_t["jornada"] == clasif_t["jornada"].max())]
        if not cc.empty:
            pos = str(int(cc.iloc[0]["posicion"])) + "º"
    except Exception:
        pass

    ev = eventos_t[eventos_t["equipo"] == TEAM].copy()
    ev["minuto"] = pd.to_numeric(ev["minuto"], errors="coerce")
    goals_for = ev[ev["tipo"].isin(["gol", "penalti_gol"])].copy()
    goals_against = ev[ev["tipo"] == "gol_contra"].copy()
    yellows = int(ev["tipo"].isin(["amarilla", "doble_amarilla"]).sum())
    reds = int(ev["tipo"].isin(["roja", "doble_amarilla"]).sum())

    # Primer gol por jornada.
    first_for = first_against = 0
    first_labels = {}
    for j in md.jornada.tolist():
        fg = goals_for[goals_for.jornada == j]["minuto"].dropna().tolist()
        ag = goals_against[goals_against.jornada == j]["minuto"].dropna().tolist()
        if fg or ag:
            mf = min(fg) if fg else 999
            ma = min(ag) if ag else 999
            if mf < ma:
                first_for += 1; first_labels[j] = "Marcamos primero"
            elif ma < mf:
                first_against += 1; first_labels[j] = "Encajamos primero"
            else:
                first_labels[j] = "Gol inicial simultáneo"
        else:
            first_labels[j] = "Sin goles"

    # Tramos de gol.
    slots = [(0,15,"0–15'"),(16,30,"16–30'"),(31,45,"31–45+'"),(46,60,"46–60'"),(61,75,"61–75'"),(76,999,"76–90+'")]
    timing = []
    for a,b,label in slots:
        f = int(((goals_for.minuto >= a) & (goals_for.minuto <= b)).sum())
        c = int(((goals_against.minuto >= a) & (goals_against.minuto <= b)).sum())
        timing.append((label,f,c))
    max_t = max([max(f,c) for _,f,c in timing] + [1])

    st.markdown("""
    <style>
    .t360-hero{border:1px solid #d9e4f2;border-radius:20px;padding:18px 20px;background:linear-gradient(135deg,#0b315f,#134b86);color:white;margin:4px 0 16px}
    .t360-hero-row{display:flex;align-items:center;gap:14px}.t360-hero img{width:54px;height:54px;object-fit:contain;background:white;border-radius:14px;padding:5px}
    .t360-hero h2{font-size:1.35rem;margin:0;font-weight:900}.t360-hero p{margin:3px 0 0;opacity:.85;font-size:.88rem}
    .t360-kpis{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:9px;margin:0 0 18px}
    .t360-kpi{border:1px solid #dde6f0;border-radius:14px;background:#fff;padding:12px 10px;text-align:center}.t360-kpi b{display:block;font-size:1.22rem;color:#092f5b}.t360-kpi span{font-size:.72rem;color:#66778b;font-weight:700;text-transform:uppercase;letter-spacing:.03em}
    .t360-section{margin:18px 0 8px}.t360-title{font-weight:950;color:#092f5b;font-size:1.05rem}.t360-sub{font-size:.78rem;color:#6b7b8e;margin-top:2px}
    .t360-grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}.t360-card{border:1px solid #dde6f0;border-radius:16px;background:#fff;padding:14px;min-width:0}
    .t360-match{display:grid;grid-template-columns:42px 1fr 60px 58px;align-items:center;gap:8px;padding:9px 0;border-bottom:1px solid #edf1f6}.t360-match:last-child{border-bottom:0}
    .t360-j{font-weight:900;color:#6c7b8d}.t360-opp{font-weight:800;color:#163b65;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.t360-score{font-weight:950;text-align:center}.t360-badge{font-weight:950;text-align:center;border-radius:999px;padding:4px 7px;font-size:.75rem}
    .t360-V{background:#dcf7e8;color:#087443}.t360-E{background:#e7edf4;color:#607086}.t360-D{background:#ffe2e4;color:#ba2935}
    .t360-timing-row{display:grid;grid-template-columns:68px 1fr 1fr;gap:8px;align-items:center;margin:9px 0}.t360-time{font-size:.75rem;font-weight:800;color:#56677a}.t360-barbox{height:24px;background:#f1f4f8;border-radius:7px;overflow:hidden;position:relative}.t360-bar-f,.t360-bar-a{height:100%;display:flex;align-items:center;padding-left:7px;color:white;font-size:.72rem;font-weight:900;min-width:0}.t360-bar-f{background:linear-gradient(90deg,#f28c18,#f59e0b)}.t360-bar-a{background:#df5b69}.t360-bar-zero{font-size:.7rem;color:#9aa7b4;padding:4px 7px}
    .t360-mini{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.t360-mini>div{background:#f5f8fc;border-radius:12px;padding:10px;text-align:center}.t360-mini b{display:block;font-size:1.15rem;color:#0c3765}.t360-mini span{font-size:.7rem;color:#718095;font-weight:700}
    .t360-table-wrap{max-height:480px;overflow-y:auto;overflow-x:hidden;border:1px solid #e1e8f0;border-radius:13px}.t360-table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:.78rem}.t360-table th{position:sticky;top:0;background:#f4f7fb;color:#35516f;z-index:1;font-size:.69rem;text-transform:uppercase}.t360-table th,.t360-table td{padding:8px 7px;border-bottom:1px solid #edf1f5;overflow-wrap:anywhere}.t360-table td.num,.t360-table th.num{text-align:center;width:60px}.t360-table td.small,.t360-table th.small{width:54px;text-align:center}
    .t360-duel{display:flex;align-items:center;gap:8px;margin:8px 0}.t360-duel .label{width:128px;font-size:.75rem;font-weight:800;color:#4b5f76}.t360-duel .track{flex:1;height:10px;background:#eef2f6;border-radius:99px;overflow:hidden}.t360-duel .fill{height:100%;background:#1d7dd8;border-radius:99px}.t360-duel .val{width:52px;text-align:right;font-weight:900;color:#153b65;font-size:.75rem}
    .t360-note{border:1px dashed #b9c8d8;background:#f8fbff;border-radius:14px;padding:12px 14px;color:#53677d;font-size:.8rem}
    .metric-panel{border:1px solid #dde6f0;border-radius:16px;background:#fff;padding:13px;margin-bottom:12px}.metric-head{display:flex;gap:9px;align-items:center;margin-bottom:8px}.metric-head>span{font-size:1.15rem}.metric-head b{display:block;color:#123e69;font-size:.86rem}.metric-head small{display:block;color:#7a899b;font-size:.62rem;margin-top:1px}.metric-row{display:grid;grid-template-columns:82px 1fr 58px;gap:8px;align-items:center;padding:7px 0;border-top:1px solid #eef2f6}.metric-j{font-weight:950;color:#274a6c;font-size:.72rem}.metric-j small{display:block;font-weight:700;color:#8290a0;font-size:.58rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.metric-bars{display:grid;gap:4px}.metric-track{height:17px;background:#f1f4f8;border-radius:6px;overflow:hidden;position:relative}.metric-track i{position:absolute;left:0;top:0;bottom:0;border-radius:6px}.metric-track i.ours{background:linear-gradient(90deg,#e97808,#f59e0b)}.metric-track i.theirs{background:linear-gradient(90deg,#486581,#6f88a2)}.metric-track span{position:relative;z-index:1;display:block;padding:1px 6px;font-size:.65rem;font-weight:950;color:#173a5d}.metric-diff{text-align:right;font-size:.68rem}.metric-diff small{display:block;font-size:.55rem;margin-top:2px}.metric-diff .up{color:#15976a}.metric-diff .down{color:#d65363}.metric-diff .flat{color:#8b98a7}.bal{font-weight:950}.bal.ok{color:#15976a}.bal.bad{color:#d65363}.metric-legend{display:flex;gap:13px;justify-content:flex-end;margin-top:6px;font-size:.58rem;color:#738297}.dot{display:inline-block;width:8px;height:8px;border-radius:3px;margin-right:4px}.dot.ours{background:#f59e0b}.dot.theirs{background:#5f7892}.trend-cards{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}.trend-card{border-radius:14px;padding:11px;border:1px solid #e2e9f1;background:#fff}.trend-card small,.trend-card b,.trend-card span{display:block}.trend-card small{font-size:.62rem;color:#75869a;font-weight:850}.trend-card b{font-size:1rem;color:#0d3d69;margin:3px 0}.trend-card span{font-size:.58rem;font-weight:850}.trend-card.positive span{color:#15976a}.trend-card.negative span{color:#d65363}.trend-card.neutral span{color:#8492a2}.visual-placeholder,.pitch-placeholder{border:1px dashed #b9c8d8;border-radius:16px;background:linear-gradient(180deg,#f9fcff,#f3f8fd);padding:22px;text-align:center;color:#5a6e83;min-height:180px;display:flex;flex-direction:column;align-items:center;justify-content:center}.visual-placeholder b,.pitch-placeholder b{color:#17456f;margin:6px 0}.visual-placeholder span,.pitch-placeholder span{font-size:.72rem;max-width:560px}.vp-icon{font-size:2rem}.pitch-placeholder{position:relative;overflow:hidden;background:#eaf7ef}.pitch-lines{position:absolute;inset:12px;border:2px solid rgba(28,112,68,.28);border-radius:6px}.pitch-lines:before{content:'';position:absolute;left:50%;top:0;bottom:0;border-left:2px solid rgba(28,112,68,.22)}.pitch-lines:after{content:'';position:absolute;width:58px;height:58px;border:2px solid rgba(28,112,68,.22);border-radius:50%;left:50%;top:50%;transform:translate(-50%,-50%)}.heat-dot{position:absolute;border-radius:50%;filter:blur(10px);opacity:.38;background:#f59e0b}.heat-dot.d1{width:72px;height:72px;left:18%;top:35%}.heat-dot.d2{width:90px;height:90px;left:52%;top:22%;background:#ef4444}.heat-dot.d3{width:58px;height:58px;right:15%;bottom:18%;background:#fbbf24}.pitch-placeholder b,.pitch-placeholder span{position:relative;z-index:2}.report-periods{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
    @media(max-width:900px){.trend-cards{grid-template-columns:repeat(3,1fr)}}
    @media(max-width:700px){.trend-cards{grid-template-columns:repeat(2,1fr)}.metric-row{grid-template-columns:68px 1fr 50px}.t360-kpis{grid-template-columns:repeat(3,1fr)}.t360-grid2{grid-template-columns:1fr}.t360-match{grid-template-columns:34px 1fr 52px 50px}.t360-hero{padding:14px}.t360-hero h2{font-size:1.12rem}.t360-table{font-size:.72rem}.t360-table th,.t360-table td{padding:7px 5px}.t360-duel .label{width:105px}}
    .progress-board{border:1px solid #dde6f0;border-radius:18px;background:#fff;padding:14px;margin:8px 0 14px}.progress-board-head{display:flex;justify-content:space-between;gap:10px;align-items:end;margin-bottom:10px}.progress-board-head b{color:#103d68;font-size:.9rem}.progress-board-head span,.panel-sub{color:#75869a;font-size:.65rem}.acc-metric{padding:11px 0;border-top:1px solid #eef2f6}.acc-title{display:flex;gap:7px;align-items:center;margin-bottom:8px;color:#173f68}.acc-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.acc-step{border:1px solid #edf1f5;border-radius:12px;padding:8px;background:#fbfcfe}.acc-j{font-size:.66rem;font-weight:950;color:#3b5875}.acc-j small{display:block;color:#8997a6;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.acc-values{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin:6px 0}.acc-values>div{display:flex;align-items:baseline;gap:4px}.acc-values b{font-size:1.02rem}.acc-values span{font-size:.58rem;color:#8190a0}.ours-txt{color:#e97808}.theirs-txt{color:#516d89}.acc-tracks{display:grid;gap:3px}.acc-tracks i{display:block;height:5px;border-radius:99px;min-width:2px}.acc-tracks .ours{background:#f59e0b}.acc-tracks .theirs{background:#607b96}.progress-split{display:grid;grid-template-columns:1.35fr .85fr;gap:12px;margin:10px 0 16px}.stack-panel,.donut-panel{border:1px solid #dde6f0;border-radius:17px;background:#fff;padding:14px}.panel-title{font-size:.84rem;font-weight:950;color:#123e69;margin-bottom:2px}.share-row{display:grid;grid-template-columns:72px 1fr 78px;gap:8px;align-items:center;margin-top:10px}.share-label b{display:block;color:#21496f;font-size:.7rem}.share-label span{display:block;color:#8493a4;font-size:.57rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.share-bar{height:28px;border-radius:8px;overflow:hidden;display:flex;position:relative;background:#eef2f6}.share-bar i{height:100%}.share-bar .ours{background:#f59e0b}.share-bar .theirs{background:#627d98}.share-bar b{position:absolute;left:8px;top:5px;color:#fff;font-size:.68rem;text-shadow:0 1px 2px rgba(0,0,0,.28)}.share-total{text-align:right;font-size:.72rem;font-weight:950;color:#314f6d}.share-total small{display:block;font-size:.53rem;color:#8996a5;font-weight:700}.donut-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:14px}.donut-item{text-align:center}.donut{--p:50;width:82px;height:82px;border-radius:50%;margin:auto;background:conic-gradient(#f59e0b calc(var(--p)*1%),#627d98 0);display:grid;place-items:center;position:relative}.donut:after{content:'';position:absolute;width:58px;height:58px;background:#fff;border-radius:50%}.donut>div{position:relative;z-index:2}.donut b{display:block;color:#173e65;font-size:.9rem}.donut span{display:block;color:#8390a0;font-size:.48rem}.donut-item>b{display:block;color:#294b6c;font-size:.66rem;margin-top:5px}.donut-item>small{display:block;color:#8a98a7;font-size:.51rem}.derived-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin:8px 0 16px}.derived-card{border:1px solid #e3eaf1;background:#fff;border-radius:14px;padding:11px 12px;border-top:4px solid #94a3b8}.derived-card.up{border-top-color:#f59e0b}.derived-card.down{border-top-color:#627d98}.derived-card small,.derived-card b,.derived-card span{display:block}.derived-card small{font-size:.61rem;color:#718296;font-weight:900}.derived-card b{font-size:1.08rem;color:#103e69;margin:3px 0}.derived-card span{font-size:.58rem;color:#738498;font-weight:800}.derived-card.up span{color:#d86f00}.derived-card.down span{color:#526c86}
    @media(max-width:900px){.progress-split{grid-template-columns:1fr}.derived-grid{grid-template-columns:repeat(2,1fr)}}
    @media(max-width:700px){.acc-steps{grid-template-columns:1fr}.share-row{grid-template-columns:58px 1fr 64px}.donut-grid{grid-template-columns:repeat(3,1fr)}.donut{width:68px;height:68px}.donut:after{width:48px;height:48px}.derived-grid{grid-template-columns:1fr 1fr}.progress-board-head{display:block}.progress-board-head span{display:block;margin-top:2px}}

    </style>
    """, unsafe_allow_html=True)

    logo_uri = _image_data_uri(BASE / "primer_toque_logo.png")
    st.markdown(
        f"<div class='t360-hero'><div class='t360-hero-row'><img src='{logo_uri}' alt='Primer Toque'>"
        f"<div><h2>Primer Toque · Equipo 360º</h2><p>Qué hacemos nosotros, cuándo lo hacemos y qué consiguen los rivales contra nosotros · J1–J{int(md.jornada.max())}</p></div></div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='t360-kpis'>"
        f"<div class='t360-kpi'><b>{pos}</b><span>Posición</span></div>"
        f"<div class='t360-kpi'><b>{pts_tot}</b><span>Puntos</span></div>"
        f"<div class='t360-kpi'><b>{pg}-{pe}-{pp}</b><span>V-E-D</span></div>"
        f"<div class='t360-kpi'><b>{gf_tot}-{gc_tot}</b><span>GF-GC</span></div>"
        f"<div class='t360-kpi'><b>{dg_tot:+d}</b><span>Diferencia</span></div>"
        f"<div class='t360-kpi'><b>{porterias_cero}</b><span>Porterías a 0</span></div>"
        "</div>", unsafe_allow_html=True,
    )

    st.markdown("<div class='t360-section'><div class='t360-title'>📈 Pulso de la temporada</div><div class='t360-sub'>Resultado, rival y cómo crecen los puntos y la diferencia de goles jornada a jornada.</div></div>", unsafe_allow_html=True)
    c1,c2 = st.columns([1.15,.85])
    with c1:
        html_rows=["<div class='t360-card'>"]
        for _,r in md.iterrows():
            html_rows.append(
                f"<div class='t360-match'><div class='t360-j'>J{int(r.jornada)}</div>"
                f"<div class='t360-opp'>{_team_logo_tag(r.rival,22)} {_safe_html(short_team_name(r.rival))}<br><span style='font-size:.68rem;color:#8491a1'>{r.condicion} · {r.sistema}</span></div>"
                f"<div class='t360-score'>{int(r.gf)}–{int(r.gc)}</div><div class='t360-badge t360-{r.res}'>{r.res} · {int(r.pts_acum)} pts</div></div>"
            )
        html_rows.append("</div>")
        st.markdown("".join(html_rows), unsafe_allow_html=True)
    with c2:
        st.markdown(
            "<div class='t360-card'><div style='font-weight:900;color:#163b65;margin-bottom:10px'>Radiografía rápida</div>"
            f"<div class='t360-mini'><div><b>{first_for}</b><span>Marcamos primero</span></div><div><b>{first_against}</b><span>Encajamos primero</span></div><div><b>{sin_marcar}</b><span>Partidos sin marcar</span></div></div>"
            f"<div class='t360-mini' style='margin-top:8px'><div><b>{gf_tot/pj:.2f}</b><span>GF / partido</span></div><div><b>{gc_tot/pj:.2f}</b><span>GC / partido</span></div><div><b>{pts_tot/pj:.2f}</b><span>Pts / partido</span></div></div>"
            f"<div class='t360-mini' style='margin-top:8px'><div><b>{yellows}</b><span>Amarillas</span></div><div><b>{reds}</b><span>Expulsiones</span></div><div><b>{porterias_cero}</b><span>Sin encajar</span></div></div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='t360-section'><div class='t360-title'>⏱️ Cuándo marcamos y cuándo sufrimos</div><div class='t360-sub'>Distribución de los goles por tramos de 15 minutos. Verde = nuestros goles; rojo = goles rivales.</div></div>", unsafe_allow_html=True)
    timing_html=["<div class='t360-card'>"]
    for label,f,c in timing:
        fw = int(100*f/max_t); cw=int(100*c/max_t)
        fhtml=f"<div class='t360-bar-f' style='width:{fw}%'>{f}</div>" if f else "<div class='t360-bar-zero'>0</div>"
        chtml=f"<div class='t360-bar-a' style='width:{cw}%'>{c}</div>" if c else "<div class='t360-bar-zero'>0</div>"
        timing_html.append(f"<div class='t360-timing-row'><div class='t360-time'>{label}</div><div class='t360-barbox'>{fhtml}</div><div class='t360-barbox'>{chtml}</div></div>")
    timing_html.append("<div style='display:grid;grid-template-columns:68px 1fr 1fr;gap:8px;font-size:.68rem;color:#7b8897;margin-top:6px'><span></span><span>NOSOTROS</span><span>RIVALES</span></div></div>")
    st.markdown("".join(timing_html), unsafe_allow_html=True)

    # Casa / fuera y primera acción decisiva.
    st.markdown("<div class='t360-section'><div class='t360-title'>🏠 Casa vs ✈️ fuera</div><div class='t360-sub'>Dónde estamos convirtiendo el rendimiento en puntos y dónde se nos escapan.</div></div>", unsafe_allow_html=True)
    cc1,cc2 = st.columns(2)
    for col,cond,icon in [(cc1,"Casa","🏠"),(cc2,"Fuera","✈️")]:
        d=md[md.condicion==cond]
        p=len(d); pt=int(d.pts.sum()); gff=int(d.gf.sum()); gcc=int(d.gc.sum())
        wins=int((d.res=="V").sum())
        with col:
            st.markdown(f"<div class='t360-card'><div style='font-weight:950;color:#143c68'>{icon} {cond}</div><div class='t360-mini' style='margin-top:10px'><div><b>{pt}</b><span>Puntos</span></div><div><b>{wins}/{p}</b><span>Victorias</span></div><div><b>{gff}-{gcc}</b><span>GF-GC</span></div></div></div>",unsafe_allow_html=True)

    # Goleadores y minutos.
    minpt = minutos_t[minutos_t["equipo"] == TEAM].copy()
    minpt["minutos"] = pd.to_numeric(minpt["minutos"], errors="coerce").fillna(0)
    minagg = minpt.groupby("jugador",as_index=False).agg(minutos=("minutos","sum"), titularidades=("titular","sum"), partidos=("jornada","nunique")) if not minpt.empty else pd.DataFrame(columns=["jugador","minutos","titularidades","partidos"])
    scorers = goals_for.groupby("jugador").size().reset_index(name="goles") if not goals_for.empty else pd.DataFrame(columns=["jugador","goles"])
    scorers = scorers.merge(minagg[["jugador","minutos"]],on="jugador",how="left").fillna({"minutos":0})
    scorers["min_gol"] = scorers.apply(lambda r: (r.minutos/r.goles) if r.goles else None,axis=1)
    scorers = scorers.sort_values(["goles","minutos"],ascending=[False,True])

    st.markdown("<div class='t360-section'><div class='t360-title'>⚽ Quién decide y quién sostiene al equipo</div><div class='t360-sub'>Goleadores a la izquierda; carga competitiva real por minutos y titularidades a la derecha.</div></div>", unsafe_allow_html=True)
    g1,g2=st.columns(2)
    with g1:
        h=["<div class='t360-table-wrap'><table class='t360-table'><thead><tr><th>Jugador</th><th class='small'>G</th><th class='num'>Min</th><th class='num'>Min/Gol</th></tr></thead><tbody>"]
        for _,r in scorers.iterrows():
            mg="—" if not r.goles else f"{r.min_gol:.0f}"
            h.append(f"<tr><td><b>{_safe_html(r.jugador)}</b></td><td class='small'>{int(r.goles)}</td><td class='num'>{int(r.minutos)}</td><td class='num'>{mg}</td></tr>")
        h.append("</tbody></table></div>")
        st.markdown("".join(h),unsafe_allow_html=True)
    with g2:
        topm=minagg.sort_values(["minutos","titularidades"],ascending=[False,False]).head(20)
        h=["<div class='t360-table-wrap'><table class='t360-table'><thead><tr><th>Jugador</th><th class='small'>PJ</th><th class='small'>Tit.</th><th class='num'>Min</th></tr></thead><tbody>"]
        for _,r in topm.iterrows():
            h.append(f"<tr><td><b>{_safe_html(r.jugador)}</b></td><td class='small'>{int(r.partidos)}</td><td class='small'>{int(r.titularidades)}</td><td class='num'>{int(r.minutos)}</td></tr>")
        h.append("</tbody></table></div>")
        st.markdown("".join(h),unsafe_allow_html=True)

    # Qué nos hace cada rival.
    st.markdown("<div class='t360-section'><div class='t360-title'>🎯 Lo que nos hacen los rivales</div><div class='t360-sub'>Cada partido visto desde el otro lado: cuándo nos marcaron, si golpearon primero y cuánto daño nos hicieron.</div></div>", unsafe_allow_html=True)
    h=["<div class='t360-table-wrap'><table class='t360-table'><thead><tr><th class='small'>J</th><th>Rival</th><th class='small'>Res.</th><th class='num'>Gol(es) rival</th><th>Minutos GC</th><th>Primer golpe</th></tr></thead><tbody>"]
    for _,r in md.iterrows():
        ga=goals_against[goals_against.jornada==r.jornada].sort_values("minuto")
        mins=", ".join([f"{int(x)}'" for x in ga.minuto.dropna().tolist()]) or "—"
        first=first_labels.get(int(r.jornada),"—")
        h.append(f"<tr><td class='small'>J{int(r.jornada)}</td><td>{_team_logo_tag(r.rival,20)} <b>{_safe_html(short_team_name(r.rival))}</b></td><td class='small'>{int(r.gf)}–{int(r.gc)}</td><td class='num'>{int(r.gc)}</td><td>{mins}</td><td>{_safe_html(first)}</td></tr>")
    h.append("</tbody></table></div>")
    st.markdown("".join(h),unsafe_allow_html=True)

    # Perfil del daño rival por jornada: intensidad relativa de goles encajados.
    st.markdown("<div class='t360-section'><div class='t360-title'>🧱 Presión rival convertida en gol</div><div class='t360-sub'>No mide todavía todos los tiros: muestra el daño que sí terminó en gol y en qué minuto llegó.</div></div>", unsafe_allow_html=True)
    for _,r in md.iterrows():
        ga=goals_against[goals_against.jornada==r.jornada]
        mins=ga.minuto.dropna().tolist()
        intensity=min(100,25*len(mins))
        detail=" · ".join([f"{int(x)}'" for x in mins]) if mins else "Sin goles encajados"
        st.markdown(f"<div class='t360-duel'><div class='label'>J{int(r.jornada)} · {_safe_html(short_team_name(r.rival))}</div><div class='track'><div class='fill' style='width:{intensity}%'></div></div><div class='val'>{_safe_html(detail)}</div></div>",unsafe_allow_html=True)

    # Datos avanzados de vídeo: visual y comparable entre jornadas.
    st.markdown("<div class='t360-section'><div class='t360-title'>🎥 Evolución del juego · vídeo</div><div class='t360-sub'>J2 = Bétera · J3 = Manises · J5 = Alboraya. Cada bloque compara nuestro valor con el rival y muestra si el equipo mejora o retrocede respecto al partido anterior.</div></div>", unsafe_allow_html=True)
    video_cols = ["tiros_favor","tiros_contra","corners_favor","corners_contra","ocasiones_favor","ocasiones_contra","faltas_favor","faltas_contra","entradas_favor","entradas_contra","saques_banda_favor","saques_banda_contra","faltas_lanzadas_favor","faltas_lanzadas_contra"]
    real_rows = pd.DataFrame()
    if not avanzado_t.empty and any(c in avanzado_t.columns for c in video_cols):
        present=[c for c in video_cols if c in avanzado_t.columns]
        real_rows = avanzado_t.dropna(subset=present, how="all").copy().sort_values('jornada')
    if real_rows.empty:
        st.markdown("<div class='t360-note'><b>Preparado, sin inventar datos.</b> Aquí aparecerán tiros, ocasiones, córners, faltas, entradas, posesión y mapas a medida que se carguen partidos.</div>",unsafe_allow_html=True)
    else:
        def _num(row, col):
            v=row.get(col)
            return None if pd.isna(v) else float(v)
        def _visual_metric(title, icon, fav_col, con_col, good_high=True):
            vals=[]
            mx=1.0
            for _,rr in real_rows.iterrows():
                f=_num(rr,fav_col); c=_num(rr,con_col)
                if f is not None: mx=max(mx,f)
                if c is not None: mx=max(mx,c)
                vals.append((rr,f,c))
            parts=[f"<div class='metric-panel'><div class='metric-head'><span>{icon}</span><div><b>{title}</b><small>Nosotros vs rival · por jornada</small></div></div>"]
            prev=None
            for rr,f,c in vals:
                if f is None and c is None: continue
                fw=0 if f is None else int(100*f/mx); cw=0 if c is None else int(100*c/mx)
                delta=None if prev is None or f is None else f-prev
                trend='•' if delta is None else ('▲' if delta>0 else ('▼' if delta<0 else '＝'))
                trend_cls='flat' if delta is None or delta==0 else ('up' if delta>0 else 'down')
                diff=(f-c) if (f is not None and c is not None) else None
                if diff is None: balance='sin comparación'
                else:
                    positive = diff>=0 if good_high else diff<=0
                    balance=('+' if diff>0 else '')+str(int(diff))
                    balance=f"<span class='bal {'ok' if positive else 'bad'}'>{balance}</span>"
                parts.append(f"<div class='metric-row'><div class='metric-j'>J{int(rr.jornada)}<small>{_safe_html(short_team_name(rr.rival))}</small></div><div class='metric-bars'><div class='metric-track'><i class='ours' style='width:{fw}%'></i><span>{'—' if f is None else int(f)}</span></div><div class='metric-track'><i class='theirs' style='width:{cw}%'></i><span>{'—' if c is None else int(c)}</span></div></div><div class='metric-diff'>{balance}<small class='{trend_cls}'>{trend} {'inicio' if delta is None else (('+' if delta>0 else '')+str(int(delta)))} vs ant.</small></div></div>")
                if f is not None: prev=f
            parts.append("<div class='metric-legend'><span><i class='dot ours'></i>Primer Toque</span><span><i class='dot theirs'></i>Rival</span></div></div>")
            return ''.join(parts)

        m1,m2=st.columns(2)
        with m1:
            st.markdown(_visual_metric('Tiros','🎯','tiros_favor','tiros_contra',True),unsafe_allow_html=True)
            st.markdown(_visual_metric('Córners','🚩','corners_favor','corners_contra',True),unsafe_allow_html=True)
        with m2:
            st.markdown(_visual_metric('Ocasiones','⚡','ocasiones_favor','ocasiones_contra',True),unsafe_allow_html=True)
            st.markdown(_visual_metric('Entradas','🧱','entradas_favor','entradas_contra',True),unsafe_allow_html=True)

        st.markdown("<div class='t360-section'><div class='t360-title'>📍 Territorio, reanudaciones y contacto</div><div class='t360-sub'>Más visual que una tabla: el ancho de la barra indica volumen y la flecha muestra la variación respecto al partido anterior.</div></div>", unsafe_allow_html=True)
        t1,t2,t3=st.columns(3)
        with t1: st.markdown(_visual_metric('Saques de banda','↔️','saques_banda_favor','saques_banda_contra',True),unsafe_allow_html=True)
        with t2: st.markdown(_visual_metric('Faltas lanzadas','🎯','faltas_lanzadas_favor','faltas_lanzadas_contra',True),unsafe_allow_html=True)
        with t3: st.markdown(_visual_metric('Faltas cometidas','🟨','faltas_favor','faltas_contra',False),unsafe_allow_html=True)

        # Progresión acumulada y nuevos indicadores derivados de datos reales.
        st.markdown("<div class='t360-section'><div class='t360-title'>📈 ¿Estamos avanzando?</div><div class='t360-sub'>La progresión combina valores reales por jornada, acumulados y porcentajes de participación. Naranja = Primer Toque · azul = rival. Los porcentajes derivados siempre muestran su fórmula.</div></div>",unsafe_allow_html=True)

        # 1) Acumulados: cuánto se suma en cada partido y a qué total llegamos.
        progress_metrics=[
            ('Tiros','tiros_favor','tiros_contra','🎯'),
            ('Ocasiones','ocasiones_favor','ocasiones_contra','⚡'),
            ('Córners','corners_favor','corners_contra','🚩'),
        ]
        acc_html=["<div class='progress-board'><div class='progress-board-head'><b>Acumulado jornada a jornada</b><span>El número grande es el total acumulado; debajo aparece lo que añadió cada jornada.</span></div>"]
        for label,fcol,ccol,icon in progress_metrics:
            ours=pd.to_numeric(real_rows.get(fcol,pd.Series(dtype=float)),errors='coerce').fillna(0)
            theirs=pd.to_numeric(real_rows.get(ccol,pd.Series(dtype=float)),errors='coerce').fillna(0)
            if ours.empty and theirs.empty: continue
            c_ours=ours.cumsum(); c_theirs=theirs.cumsum()
            max_total=max(float(c_ours.max() if not c_ours.empty else 0),float(c_theirs.max() if not c_theirs.empty else 0),1.0)
            cards=[]
            for i,(_,rr) in enumerate(real_rows.iterrows()):
                ov=float(ours.iloc[i]); tv=float(theirs.iloc[i]); oa=float(c_ours.iloc[i]); ta=float(c_theirs.iloc[i])
                ow=int(100*oa/max_total); tw=int(100*ta/max_total)
                cards.append(
                    f"<div class='acc-step'><div class='acc-j'>J{int(rr.jornada)}<small>{_safe_html(short_team_name(rr.rival))}</small></div>"
                    f"<div class='acc-values'><div><b class='ours-txt'>{int(oa)}</b><span>+{int(ov)}</span></div><div><b class='theirs-txt'>{int(ta)}</b><span>+{int(tv)}</span></div></div>"
                    f"<div class='acc-tracks'><i class='ours' style='width:{ow}%'></i><i class='theirs' style='width:{tw}%'></i></div></div>"
                )
            acc_html.append(f"<div class='acc-metric'><div class='acc-title'><span>{icon}</span><b>{label}</b></div><div class='acc-steps'>{''.join(cards)}</div></div>")
        acc_html.append("</div>")
        st.markdown(''.join(acc_html),unsafe_allow_html=True)

        # 2) Barras 100% apiladas: cuota del volumen de ataque por jornada.
        stack=[]
        for _,rr in real_rows.iterrows():
            of=sum(float(_num(rr,c) or 0) for c in ['tiros_favor','ocasiones_favor'])
            oc=sum(float(_num(rr,c) or 0) for c in ['tiros_contra','ocasiones_contra'])
            total=of+oc
            share=50 if total<=0 else 100*of/total
            stack.append(
                f"<div class='share-row'><div class='share-label'><b>J{int(rr.jornada)}</b><span>{_safe_html(short_team_name(rr.rival))}</span></div>"
                f"<div class='share-bar'><i class='ours' style='width:{share:.1f}%'></i><i class='theirs' style='width:{100-share:.1f}%'></i><b>{share:.0f}%</b></div>"
                f"<div class='share-total'>{int(of)}–{int(oc)}<small>tiros + ocasiones</small></div></div>"
            )
        # 3) Círculos de dominio acumulado: proporción a favor sobre el total registrado.
        donut_specs=[('Tiros','tiros_favor','tiros_contra'),('Ocasiones','ocasiones_favor','ocasiones_contra'),('Córners','corners_favor','corners_contra')]
        donuts=[]
        for label,fcol,ccol in donut_specs:
            fav=float(pd.to_numeric(real_rows.get(fcol,pd.Series(dtype=float)),errors='coerce').fillna(0).sum())
            con=float(pd.to_numeric(real_rows.get(ccol,pd.Series(dtype=float)),errors='coerce').fillna(0).sum())
            total=fav+con
            pct=0 if total<=0 else 100*fav/total
            donuts.append(f"<div class='donut-item'><div class='donut' style='--p:{pct:.1f}'><div><b>{pct:.0f}%</b><span>nuestro</span></div></div><b>{label}</b><small>{int(fav)} a favor · {int(con)} rival</small></div>")
        split_html=("<div class='progress-split'><div class='stack-panel'><div class='panel-title'>🟧 Cuota de iniciativa ofensiva</div><div class='panel-sub'>% de <b>tiros + ocasiones</b> que fueron nuestros en cada partido. Es un indicador de volumen, no posesión.</div>"+''.join(stack)+"</div>"
                    +"<div class='donut-panel'><div class='panel-title'>⭕ Peso acumulado de Primer Toque</div><div class='panel-sub'>Qué parte del volumen total registrado pertenece a nuestro equipo.</div><div class='donut-grid'>"+''.join(donuts)+"</div></div></div>")
        st.markdown(split_html,unsafe_allow_html=True)

        # 4) Indicadores nuevos, calculados solo con datos existentes y fórmula visible.
        derived=[]
        # Evolución primer→último para métricas de volumen.
        for label,col in [('Tiros','tiros_favor'),('Ocasiones','ocasiones_favor'),('Córners','corners_favor'),('Bandas','saques_banda_favor')]:
            ser=pd.to_numeric(real_rows.get(col,pd.Series(dtype=float)),errors='coerce').dropna()
            if len(ser)<2: continue
            first=float(ser.iloc[0]); last=float(ser.iloc[-1]); delta=last-first
            pct=None if first==0 else (delta/first)*100
            cls='up' if delta>0 else ('down' if delta<0 else 'flat')
            ptxt='—' if pct is None else f"{pct:+.0f}%"
            derived.append(f"<div class='derived-card {cls}'><small>{label}</small><b>{int(first)} → {int(last)}</b><span>{ptxt} · cambio {delta:+.0f}</span></div>")

        # Eficacia de tiro por jornada = goles / tiros.
        md_lookup={int(r.jornada):r for _,r in md.iterrows()}
        eff=[]
        for _,rr in real_rows.iterrows():
            j=int(rr.jornada); shots=float(_num(rr,'tiros_favor') or 0); goals=float(md_lookup[j].gf) if j in md_lookup else 0
            pct=0 if shots<=0 else 100*goals/shots
            eff.append((j,pct,goals,shots,short_team_name(rr.rival)))
        if eff:
            latest=eff[-1]
            avg=100*sum(x[2] for x in eff)/max(1,sum(x[3] for x in eff))
            derived.append(f"<div class='derived-card neutral'><small>Eficacia de tiro</small><b>{avg:.1f}%</b><span>{int(sum(x[2] for x in eff))} goles / {int(sum(x[3] for x in eff))} tiros</span></div>")

        # Índice territorial proxy = (córners + bandas) propios / total de ambas acciones.
        tf=float(pd.to_numeric(real_rows.get('corners_favor',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()+pd.to_numeric(real_rows.get('saques_banda_favor',pd.Series(dtype=float)),errors='coerce').fillna(0).sum())
        tc=float(pd.to_numeric(real_rows.get('corners_contra',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()+pd.to_numeric(real_rows.get('saques_banda_contra',pd.Series(dtype=float)),errors='coerce').fillna(0).sum())
        terr=0 if tf+tc<=0 else 100*tf/(tf+tc)
        derived.append(f"<div class='derived-card neutral'><small>Territorio · proxy</small><b>{terr:.0f}%</b><span>(córners + bandas) nuestros / total</span></div>")

        st.markdown("<div class='t360-section'><div class='t360-title'>🧮 Nuevos indicadores con los datos que ya tenemos</div><div class='t360-sub'>No son datos inventados: son cálculos transparentes construidos a partir de tiros, ocasiones, goles, córners y bandas.</div></div>",unsafe_allow_html=True)
        st.markdown("<div class='derived-grid'>"+''.join(derived)+"</div>",unsafe_allow_html=True)

    # Posesión y mapas: estructura lista para datos reales de equipo.
    st.markdown("<div class='t360-section'><div class='t360-title'>🗺️ Dónde jugamos</div><div class='t360-sub'>Posesión por parte, mapas de calor, mapa de tiros y mapa de goles. Se mostrarán cuando dispongamos del dato agregado del equipo; nunca se inventan zonas o porcentajes.</div></div>", unsafe_allow_html=True)
    map_tabs=st.tabs(['🧭 Posesión 1ª/2ª parte','🔥 Mapas de calor','🎯 Mapa de tiros','⚽ Mapa de goles'])
    with map_tabs[0]:
        pcols=['posesion_1p_favor','posesion_1p_rival','posesion_2p_favor','posesion_2p_rival']
        have=not avanzado_t.empty and any(c in avanzado_t.columns and pd.to_numeric(avanzado_t[c],errors='coerce').notna().any() for c in pcols)
        if not have:
            st.markdown("<div class='visual-placeholder'><div class='vp-icon'>🧭</div><b>Posesión por partes preparada</b><span>Cuando carguemos % de 1ª y 2ª parte aparecerá una comparación jornada a jornada y el territorio dominante.</span></div>",unsafe_allow_html=True)
    with map_tabs[1]:
        st.markdown("<div class='pitch-placeholder'><div class='pitch-lines'></div><div class='heat-dot d1'></div><div class='heat-dot d2'></div><div class='heat-dot d3'></div><b>Mapa de calor de equipo</b><span>Se construirá con ubicaciones reales agregadas; de momento solo se muestra la estructura.</span></div>",unsafe_allow_html=True)
    with map_tabs[2]:
        st.markdown("<div class='pitch-placeholder shot'><div class='pitch-lines'></div><b>Mapa de tiros</b><span>Tiros a favor y en contra por zona, diferenciando gol, a puerta y fuera cuando tengamos coordenadas.</span></div>",unsafe_allow_html=True)
    with map_tabs[3]:
        st.markdown("<div class='pitch-placeholder goal'><div class='pitch-lines'></div><b>Mapa de goles</b><span>Origen de nuestros goles y de los goles recibidos, con filtros por jornada, casa/fuera y parte.</span></div>",unsafe_allow_html=True)

st.markdown("""<style>

/* ---------- Navegación lateral V15.12.45 ---------- */
.side-nav-v3{display:flex;flex-direction:column;gap:7px;margin:3px 0 14px}
.side-nav-v3 a{display:flex;align-items:center;gap:10px;min-height:46px;padding:8px 10px;border:1px solid #e2eaf3;border-radius:13px;background:#fff;color:#2f4d6c!important;text-decoration:none!important;font-size:.82rem;font-weight:850;box-shadow:0 2px 8px rgba(15,42,68,.035);transition:.16s ease}
.side-nav-v3 a:hover{transform:translateX(2px);border-color:#bdd2e8;background:#f7fbff;box-shadow:0 6px 16px rgba(15,42,68,.06)}
.side-nav-v3 a.active{background:linear-gradient(90deg,#edf6ff 0%,#fff 100%);border-color:#a9c8e8;color:#062d5a!important;box-shadow:inset 4px 0 0 #f59e0b,0 5px 14px rgba(29,99,216,.08)}
.side-nav-v3 .sni{width:31px;height:31px;display:grid;place-items:center;border-radius:10px;background:#f0f5fb;color:#315b83;flex:0 0 31px}
.side-nav-v3 a.active .sni{background:#0b4b84;color:#fff}
.side-nav-v3 .sni svg{width:17px;height:17px;stroke:currentColor;stroke-width:2;fill:none;stroke-linecap:round;stroke-linejoin:round}
.side-nav-v3 .sn-label{min-width:0;white-space:nowrap}

/* ---------- Jugadores ---------- */
.players-head{display:flex;align-items:end;justify-content:space-between;gap:12px;margin:2px 0 15px}.players-title{font-size:2rem;font-weight:950;letter-spacing:-.04em;color:#062d5a}.players-sub{font-size:.78rem;color:#6b7c93;margin-top:3px}
.players-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:10px}.player-card-link{text-decoration:none!important;color:inherit!important;display:block;min-width:0}.player-card-v3{position:relative;min-height:202px;padding:18px;border-radius:19px;background:linear-gradient(145deg,#073766 0%,#0b4b84 100%);color:#fff;border:1px solid rgba(255,255,255,.08);box-shadow:0 10px 24px rgba(6,45,90,.16);overflow:hidden;transition:.16s ease}.player-card-v3:hover{transform:translateY(-2px);box-shadow:0 14px 30px rgba(6,45,90,.22)}.player-card-v3:after{content:'';position:absolute;width:120px;height:120px;right:-58px;bottom:-58px;border-radius:50%;background:rgba(255,255,255,.055)}
.pc-no{font-size:2.4rem;line-height:1;font-weight:950;letter-spacing:-.04em}.pc-name{font-size:1.24rem;font-weight:950;margin-top:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.pc-pos{display:inline-flex;margin-top:10px;padding:5px 9px;border-radius:999px;background:#1d63d8;font-size:.68rem;font-weight:900}.pc-logo{position:absolute;right:15px;top:15px;width:47px;height:47px;background:#fff;border-radius:12px;padding:5px;display:grid;place-items:center}.pc-logo img{width:100%;height:100%;object-fit:contain}.pc-foot{position:absolute;left:18px;right:18px;bottom:16px;font-size:.68rem;line-height:1.55;color:#d8e7f6;font-weight:750}.pc-foot b{color:#fff}
.player-detail-hero{display:grid;grid-template-columns:120px 1fr auto;gap:18px;align-items:center;background:linear-gradient(145deg,#062d5a,#0b4b84);color:#fff;border-radius:21px;padding:20px 22px;margin-bottom:14px;box-shadow:0 12px 30px rgba(6,45,90,.18)}.pd-badge{width:100px;height:100px;border-radius:22px;background:#fff;padding:12px;display:grid;place-items:center}.pd-badge img{width:100%;height:100%;object-fit:contain}.pd-no{font-size:1.05rem;font-weight:900;color:#9dc7ed}.pd-name{font-size:2rem;font-weight:950;letter-spacing:-.04em;line-height:1.05}.pd-meta{margin-top:7px;font-size:.78rem;color:#d4e4f2}.pd-kpis{display:grid;grid-template-columns:repeat(3,minmax(74px,1fr));gap:8px}.pd-kpi{background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.12);border-radius:13px;padding:10px;text-align:center}.pd-kpi b{display:block;font-size:1.25rem}.pd-kpi span{font-size:.62rem;color:#d8e7f6;font-weight:800}
.player-stat-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:9px;margin:10px 0 14px}.ps-card{background:#fff;border:1px solid #e5ebf2;border-radius:14px;padding:12px;text-align:center}.ps-card .v{font-size:1.25rem;font-weight:950;color:#062d5a}.ps-card .l{font-size:.64rem;color:#72849a;font-weight:850;margin-top:3px}
.player-table-wrap{overflow-x:hidden;overflow-y:auto;max-height:520px;border:1px solid #e5ebf2;border-radius:14px;background:#fff}.player-table{width:100%;border-collapse:collapse;table-layout:fixed}.player-table th,.player-table td{padding:9px 8px;border-bottom:1px solid #edf1f5;font-size:.72rem;text-align:center;white-space:normal;word-break:break-word}.player-table th{position:sticky;top:0;background:#f7fafc;color:#4a6179;font-weight:950;z-index:1}.player-table td:first-child,.player-table th:first-child{text-align:left;width:23%}
.report-card{background:#fff;border:1px solid #e5ebf2;border-radius:16px;padding:15px;margin:9px 0}.report-card h4{margin:0 0 8px;color:#0a3b69;font-size:.9rem}.report-card p,.report-card li{font-size:.76rem;color:#53687e;line-height:1.55}.report-auto{display:inline-flex;padding:5px 8px;border-radius:999px;background:#eef6ff;color:#1d63d8;border:1px solid #d6e8fb;font-size:.64rem;font-weight:900;margin-bottom:9px}
.phys-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:9px;margin:10px 0 14px}.phys-card{background:linear-gradient(180deg,#fff,#f7fbff);border:1px solid #e3eaf2;border-radius:14px;padding:12px}.phys-card .v{font-size:1.18rem;font-weight:950;color:#073866}.phys-card .l{font-size:.62rem;color:#718096;font-weight:850;margin-top:3px}.phys-card .s{font-size:.59rem;color:#1d63d8;font-weight:850;margin-top:5px}
.history-strip{display:grid;grid-template-columns:1fr auto 1.5fr;align-items:center;gap:10px;border:1px solid #dce8f4;background:linear-gradient(90deg,#f6fbff,#fff);border-radius:14px;padding:11px 13px;margin:0 0 13px}.history-strip b{display:block;color:#093b6b;font-size:.8rem}.history-strip span{font-size:.65rem;color:#718096}.history-arrow{font-weight:950;color:#1d63d8}.report-periods{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}.report-periods>div{padding:10px;border-radius:12px;background:#f5f8fc}.report-periods b,.report-periods span{display:block}.report-periods span{font-size:.64rem;color:#7d8da0;margin-top:3px}.physical-profile-title{font-size:.82rem;font-weight:950;color:#0a3b69;margin:4px 0 7px}
@media(max-width:1050px){.players-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.player-stat-grid,.phys-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:700px){.players-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.player-card-v3{min-height:175px;padding:14px}.pc-no{font-size:2rem}.pc-name{font-size:1rem}.pc-logo{width:39px;height:39px}.pc-foot{left:14px;right:14px;bottom:12px}.player-detail-hero{grid-template-columns:74px 1fr;padding:15px;gap:12px}.pd-badge{width:68px;height:68px;border-radius:16px;padding:8px}.pd-name{font-size:1.45rem}.pd-kpis{grid-column:1/-1;grid-template-columns:repeat(3,1fr)}.player-stat-grid,.phys-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.players-title{font-size:1.6rem}}
</style>""", unsafe_allow_html=True)


def render_players():
    """Plantilla visual + fichas individuales. Fran se excluye por petición del usuario."""
    team = "Primer Toque C.F. 'A'"
    roster = plantillas[(plantillas.equipo == team) & (plantillas.jugador.astype(str).str.strip().str.lower() != 'fran')].copy()
    mins = minutos[(minutos.equipo == team) & (minutos.jugador.astype(str).str.strip().str.lower() != 'fran')].copy()
    evs = eventos[(eventos.equipo == team) & (eventos.jugador.astype(str).str.strip().str.lower() != 'fran')].copy()
    als = alineaciones[(alineaciones.equipo == team) & (alineaciones.jugador.astype(str).str.strip().str.lower() != 'fran')].copy()
    adv = load_individual_video()
    perfiles = load_csv("jugadores_perfil.csv")

    role_map = {}
    if not als.empty:
        for p, grp in als.groupby('jugador'):
            vals = grp['rol'].dropna().astype(str)
            if not vals.empty:
                role_map[p] = vals.mode().iloc[0]
    role_name = {'POR':'Portero','DEF':'Defensa','MED':'Mediocentro','ATA':'Delantero','DEL':'Delantero'}
    role_order = {'POR':0,'DEF':1,'MED':2,'ATA':3,'DEL':3}
    roster['rol'] = roster['jugador'].map(role_map).fillna('MED')
    roster['posicion'] = roster['rol'].map(role_name).fillna('Jugador')
    roster['rord'] = roster['rol'].map(role_order).fillna(9)
    roster['dorsal'] = pd.to_numeric(roster['dorsal'], errors='coerce').fillna(0).astype(int)
    roster = roster.sort_values(['rord','dorsal','jugador']).reset_index(drop=True)

    try:
        player_q = str(st.query_params.get('player','')).strip()
    except Exception:
        try: player_q = str((st.experimental_get_query_params().get('player') or [''])[0]).strip()
        except Exception: player_q = ''

    # Resumen por jugador para tarjetas y fichas.
    rows=[]
    for _,r in roster.iterrows():
        p=str(r.jugador); d=int(r.dorsal)
        pm=mins[mins.jugador==p]
        pe=evs[evs.jugador==p]
        pj=int((pd.to_numeric(pm['minutos'],errors='coerce').fillna(0)>0).sum()) if not pm.empty else 0
        tit=int(pd.to_numeric(pm['titular'],errors='coerce').fillna(0).sum()) if not pm.empty else 0
        mn=int(pd.to_numeric(pm['minutos'],errors='coerce').fillna(0).sum()) if not pm.empty else 0
        goals=int(pe['tipo'].isin(['gol','penalti_gol']).sum()) if not pe.empty else 0
        rows.append({**r.to_dict(),'pj':pj,'tit':tit,'minutos':mn,'goles':goals})
    rdf=pd.DataFrame(rows)

    if not player_q or player_q not in set(rdf.jugador.astype(str)):
        st.markdown("<div class='players-head'><div><div class='players-title'>Jugadores</div><div class='players-sub'>Plantilla Primer Toque · fichas individuales de rendimiento, informes y aspecto físico</div></div><div class='data-note'>19 jugadores · Fran eliminado</div></div>",unsafe_allow_html=True)
        logo_uri=_image_data_uri(BASE/'primer_toque_logo.png')
        cards=["<div class='players-grid'>"]
        for _,r in rdf.iterrows():
            href='?view=jugadores&player='+quote(str(r.jugador))
            cards.append(
                f"<a class='player-card-link' href='{href}' target='_self'><div class='player-card-v3'>"
                f"<div class='pc-logo'><img src='{logo_uri}' alt='Primer Toque'></div>"
                f"<div class='pc-no'>#{int(r.dorsal)}</div><div class='pc-name'>{_safe_html(str(r.jugador))}</div>"
                f"<div class='pc-pos'>{_safe_html(str(r.posicion))}</div>"
                f"<div class='pc-foot'><b>{int(r.pj)}</b> apariciones · <b>{int(r.tit)}</b> titularidades<br><b>{int(r.minutos)}</b> min · <b>{int(r.goles)}</b> goles</div>"
                f"</div></a>"
            )
        cards.append('</div>')
        st.markdown(''.join(cards),unsafe_allow_html=True)
        st.caption('Pulsa sobre cualquier ficha para abrir Estadísticas, Informes y Físico.')
        return

    r=rdf[rdf.jugador.astype(str)==player_q].iloc[0]
    player=str(r.jugador); dorsal=int(r.dorsal); pos=str(r.posicion)
    pm=mins[mins.jugador==player].copy().sort_values('jornada')
    pe=evs[evs.jugador==player].copy().sort_values(['jornada','minuto'])
    goals=int(pe['tipo'].isin(['gol','penalti_gol']).sum()) if not pe.empty else 0
    yc=int((pe['tipo']=='amarilla').sum()) if not pe.empty else 0
    reds=int(pe['tipo'].isin(['roja','doble_amarilla']).sum()) if not pe.empty else 0
    apps=int((pd.to_numeric(pm['minutos'],errors='coerce').fillna(0)>0).sum()) if not pm.empty else 0
    starts=int(pd.to_numeric(pm['titular'],errors='coerce').fillna(0).sum()) if not pm.empty else 0
    total_min=int(pd.to_numeric(pm['minutos'],errors='coerce').fillna(0).sum()) if not pm.empty else 0
    logo_uri=_image_data_uri(BASE/'primer_toque_logo.png')
    back='?view=jugadores'
    st.markdown(f"<a href='{back}' target='_self' style='text-decoration:none;color:#1d63d8;font-weight:900;font-size:.78rem'>← Volver a jugadores</a>",unsafe_allow_html=True)
    st.markdown(
        f"<div class='player-detail-hero'><div class='pd-badge'><img src='{logo_uri}' alt='Primer Toque'></div>"
        f"<div><div class='pd-no'>#{dorsal} · {_safe_html(pos)}</div><div class='pd-name'>{_safe_html(player)}</div><div class='pd-meta'>Primer Toque C.F. · Temporada 2026/2027</div></div>"
        f"<div class='pd-kpis'><div class='pd-kpi'><b>{apps}</b><span>Partidos</span></div><div class='pd-kpi'><b>{starts}</b><span>Titular</span></div><div class='pd-kpi'><b>{total_min}</b><span>Minutos</span></div></div></div>",unsafe_allow_html=True)

    tab_stats,tab_reports,tab_phys=st.tabs(['📊 Estadísticas','📝 Informes','💪 Físico'])
    with tab_stats:
        min_goal='—' if goals<=0 else str(round(total_min/goals))
        cards=[('Goles',goals),('Minutos',total_min),('Min/Gol',min_goal),('Titularidades',starts),('Amarillas',yc),('Expulsiones',reds)]
        st.markdown("<div class='player-stat-grid'>"+''.join([f"<div class='ps-card'><div class='v'>{_safe_html(str(v))}</div><div class='l'>{_safe_html(k)}</div></div>" for k,v in cards])+"</div>",unsafe_allow_html=True)
        st.markdown("<div class='history-strip'><div><b>2026/27</b><span>Temporada activa</span></div><div class='history-arrow'>→</div><div><b>Histórico</b><span>Las próximas temporadas se añadirán sin borrar las anteriores</span></div></div>",unsafe_allow_html=True)
        # Qué hizo en cada partido: minutos, titularidad y eventos.
        all_js=sorted(set(pm.jornada.dropna().astype(int).tolist()) | set(pe.jornada.dropna().astype(int).tolist()))
        h=["<div class='player-table-wrap'><table class='player-table'><thead><tr><th>Partido</th><th>Min</th><th>Tit.</th><th>Gol</th><th>Tarjetas</th><th>Eventos</th></tr></thead><tbody>"]
        for j in all_js:
            mr=pm[pm.jornada.astype(int)==j]
            er=pe[pe.jornada.astype(int)==j]
            mn=int(pd.to_numeric(mr['minutos'],errors='coerce').fillna(0).sum()) if not mr.empty else 0
            ti='Sí' if (not mr.empty and pd.to_numeric(mr['titular'],errors='coerce').fillna(0).max()>0) else 'No'
            gg=int(er['tipo'].isin(['gol','penalti_gol']).sum()) if not er.empty else 0
            cardsj=int(er['tipo'].isin(['amarilla','roja','doble_amarilla']).sum()) if not er.empty else 0
            evtxt=', '.join([f"{str(x.tipo).replace('_',' ')} {int(x.minuto)}'" for _,x in er.iterrows()]) if not er.empty else '—'
            h.append(f"<tr><td><b>J{j}</b></td><td>{mn}</td><td>{ti}</td><td>{gg}</td><td>{cardsj}</td><td>{_safe_html(evtxt)}</td></tr>")
        h.append('</tbody></table></div>')
        st.markdown(''.join(h),unsafe_allow_html=True)

    with tab_reports:
        st.markdown("<div class='report-card'><div class='report-auto'>RESUMEN AUTOMÁTICO · datos cargados</div><h4>Informe de temporada</h4>",unsafe_allow_html=True)
        notes=[]
        if apps: notes.append(f"Ha participado en {apps} partidos y suma {total_min} minutos, con {starts} titularidades.")
        if goals: notes.append(f"Ha marcado {goals} gol{'es' if goals!=1 else ''}; promedio de {round(total_min/goals)} minutos por gol.")
        else: notes.append('No tiene goles registrados en los eventos oficiales cargados.')
        if yc or reds: notes.append(f"Disciplina: {yc} amarillas y {reds} expulsiones/dobles amarillas registradas.")
        else: notes.append('Sin tarjetas registradas en los eventos cargados.')
        st.markdown('<ul>'+''.join([f'<li>{_safe_html(x)}</li>' for x in notes])+'</ul></div>',unsafe_allow_html=True)
        st.markdown("<div class='report-card'><h4>Informes del entrenador</h4><p>La ficha queda preparada para conservar informes de cada temporada. Los dos hitos principales serán <b>mitad de temporada</b> y <b>final de temporada</b>; podrán mostrarse a familias según permisos de usuario.</p><div class='report-periods'><div><b>Mitad 2026/27</b><span>Pendiente</span></div><div><b>Final 2026/27</b><span>Pendiente</span></div></div></div>",unsafe_allow_html=True)
        st.markdown("<div class='report-card'><h4>Seguimiento por partido</h4><p>Este bloque resume lo que ha hecho el jugador en cada jornada y quedará archivado por temporada para construir su histórico.</p></div>",unsafe_allow_html=True)
        if not pm.empty:
            for _,mr in pm.sort_values('jornada').iterrows():
                j=int(mr.jornada); mn=int(mr.minutos); ti='titular' if int(mr.titular)==1 else 'suplente'
                er=pe[pe.jornada.astype(int)==j]
                extra=[]
                if not er.empty:
                    for _,e in er.iterrows(): extra.append(f"{str(e.tipo).replace('_',' ')} {int(e.minuto)}'")
                ext=(' · '+', '.join(extra)) if extra else ''
                st.markdown(f"<div class='report-card'><h4>J{j}</h4><p>{mn} minutos · {ti}{_safe_html(ext)}</p></div>",unsafe_allow_html=True)

    with tab_phys:
        prof = perfiles[perfiles['jugador'].astype(str)==player] if not perfiles.empty else pd.DataFrame()
        def _profval(col, suffix=''):
            if prof.empty or col not in prof.columns or pd.isna(prof.iloc[0].get(col)) or str(prof.iloc[0].get(col)).strip()=='' : return '—'
            v=prof.iloc[0].get(col)
            try:
                fv=float(v)
                txt=f"{fv:.1f}" if abs(fv-round(fv))>1e-9 else str(int(round(fv)))
            except Exception: txt=str(v)
            return txt+suffix
        st.markdown("<div class='physical-profile-title'>Mediciones de crecimiento y condición</div>", unsafe_allow_html=True)
        st.markdown("<div class='phys-grid'>"+
                    f"<div class='phys-card'><div class='v'>{_profval('altura_cm',' cm')}</div><div class='l'>Altura</div><div class='s'>Última medición</div></div>"+
                    f"<div class='phys-card'><div class='v'>{_profval('peso_kg',' kg')}</div><div class='l'>Peso</div><div class='s'>Última medición</div></div>"+
                    f"<div class='phys-card'><div class='v'>{_profval('course_navette')}</div><div class='l'>Course Navette</div><div class='s'>Palier / nivel</div></div>"+
                    f"<div class='phys-card'><div class='v'>{_profval('fecha_medicion')}</div><div class='l'>Fecha control</div><div class='s'>Seguimiento</div></div>"+
                    "</div>", unsafe_allow_html=True)
        pa=adv[pd.to_numeric(adv.get('dorsal'),errors='coerce').fillna(-1).astype(int)==dorsal].copy() if not adv.empty else pd.DataFrame()
        if pa.empty:
            st.info('Todavía no hay tracking físico de vídeo cargado para este jugador.')
        else:
            for c in ['distancia_km','velocidad_media_kmh','minutos_rastreados','velocidad_max_kmh','sprints','carreras_alta_intensidad','eventos_totales','tiros','ocasiones']:
                if c in pa.columns: pa[c]=pd.to_numeric(pa[c],errors='coerce')
            dist=float(pa['distancia_km'].sum(skipna=True)) if 'distancia_km' in pa else 0
            track=float(pa['minutos_rastreados'].sum(skipna=True)) if 'minutos_rastreados' in pa else 0
            vmax=float(pa['velocidad_max_kmh'].max(skipna=True)) if ('velocidad_max_kmh' in pa and pa['velocidad_max_kmh'].notna().any()) else 0
            vavg=float((pa['velocidad_media_kmh']*pa['minutos_rastreados']).sum(skipna=True)/track) if ('velocidad_media_kmh' in pa and track>0) else 0
            spr=float(pa['sprints'].sum(skipna=True)) if 'sprints' in pa else 0
            hi=float(pa['carreras_alta_intensidad'].sum(skipna=True)) if 'carreras_alta_intensidad' in pa else 0
            phys=[('Distancia',f"{dist:.1f} km"),('Min rastreados',f"{int(track)}"),('V. máxima',('—' if vmax<=0 else f"{vmax:.1f} km/h")),('V. media',('—' if vavg<=0 else f"{vavg:.1f} km/h")),('Sprints',f"{int(spr)}"),('Alta intensidad',f"{int(hi)}")]
            st.markdown("<div class='phys-grid'>"+''.join([f"<div class='phys-card'><div class='v'>{_safe_html(v)}</div><div class='l'>{_safe_html(k)}</div><div class='s'>J2 · J3 · J5 cuando hay datos</div></div>" for k,v in phys])+"</div>",unsafe_allow_html=True)
            h=["<div class='player-table-wrap'><table class='player-table'><thead><tr><th>Jornada</th><th>Distancia</th><th>Track min</th><th>V. media</th><th>V. máx</th><th>Sprints</th></tr></thead><tbody>"]
            for _,x in pa.sort_values('jornada').iterrows():
                def fmt(col,suf='',dec=1):
                    v=x.get(col)
                    if pd.isna(v): return '—'
                    return f"{float(v):.{dec}f}{suf}"
                h.append(f"<tr><td><b>J{int(x.jornada)}</b></td><td>{fmt('distancia_km',' km')}</td><td>{fmt('minutos_rastreados','',0)}</td><td>{fmt('velocidad_media_kmh','',1)}</td><td>{fmt('velocidad_max_kmh','',1)}</td><td>{fmt('sprints','',0)}</td></tr>")
            h.append('</tbody></table></div>')
            st.markdown(''.join(h),unsafe_allow_html=True)


with st.sidebar:
    _pt_logo_uri = _image_data_uri(BASE / "primer_toque_logo.png")
    st.markdown(
        f"""<div class='brand-box'>
        <div class='brand-logo'><img src='{_pt_logo_uri}' alt='Primer Toque C.F.'></div>
        <div class='brand-copy'>
            <div class='brand-kicker'>Análisis de rendimiento</div>
            <div class='brand-main'>PRIMER TOQUE C.F.</div>
            <div class='brand-sub'>Temporada <b>2026/2027</b></div>
            <div class='brand-chip'>JUVENIL A</div>
        </div>
        </div>""",
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
    try:
        _view = st.query_params.get("view", "")
    except Exception:
        try:
            _view = (st.experimental_get_query_params().get("view") or [""])[0]
        except Exception:
            _view = ""
    _view = str(_view).lower().strip()
    _view_to_mod = {
        "inicio": "Inicio",
        "liga": "Resumen liga",
        "resumen": "Resumen liga",
        "rivales": "Rivales",
        "equipo": "Equipo",
        "jugadores": "Jugadores",
        "individual": "Individual",
    }
    modulo = _view_to_mod.get(_view, "Resumen liga" if _area == "juvenil" else "Inicio")
    _icons = {
      "Inicio":"<svg viewBox='0 0 24 24'><path d='M3 11.5 12 4l9 7.5'/><path d='M5 10.5V20h14v-9.5'/></svg>",
      "Resumen liga":"<svg viewBox='0 0 24 24'><path d='M4 20V10'/><path d='M10 20V4'/><path d='M16 20v-7'/><path d='M22 20H2'/></svg>",
      "Rivales":"<svg viewBox='0 0 24 24'><circle cx='12' cy='12' r='8'/><circle cx='12' cy='12' r='3'/><path d='M12 4V2M20 12h2M12 20v2M4 12H2'/></svg>",
      "Equipo":"<svg viewBox='0 0 24 24'><path d='M12 3 20 6v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z'/><path d='m9 12 2 2 4-4'/></svg>",
      "Jugadores":"<svg viewBox='0 0 24 24'><circle cx='9' cy='8' r='3'/><circle cx='17' cy='9' r='2.5'/><path d='M3 20c0-4 2.5-6 6-6s6 2 6 6'/><path d='M14 15c3.4-.4 6 1.5 6 5'/></svg>",
      "Individual":"<svg viewBox='0 0 24 24'><circle cx='12' cy='8' r='3.5'/><path d='M5 21c.3-5 2.8-8 7-8s6.7 3 7 8'/></svg>",
    }
    _nav_info=[('Inicio','inicio'),('Resumen liga','liga'),('Rivales','rivales'),('Equipo','equipo'),('Individual','individual'),('Jugadores','jugadores')]
    _nh=["<div class='side-nav-v3'>"]
    for _nm,_slug in _nav_info:
        _ac=' active' if modulo==_nm else ''
        _nh.append(f"<a class='{_ac.strip()}' href='?view={_slug}' target='_self'><span class='sni'>{_icons[_nm]}</span><span class='sn-label'>{_safe_html(_nm)}</span></a>")
    _nh.append('</div>')
    st.markdown(''.join(_nh),unsafe_allow_html=True)

    seleccionado = None
    if modulo == "Rivales":
        equipos = load_csv("equipos_liga.csv")
        st.markdown("<div class='side-label'>Rivales · 16 equipos</div>", unsafe_allow_html=True)
        lista = equipos.sort_values("orden")["equipo"].tolist() if not equipos.empty else []
        try:
            _team_q = st.query_params.get("team", "")
        except Exception:
            try:
                _team_q = (st.experimental_get_query_params().get("team") or [""])[0]
            except Exception:
                _team_q = ""
        _team_q = str(_team_q)
        if _team_q in lista:
            default_idx = lista.index(_team_q)
        else:
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
    minutos = load_csv("minutos_rivales.csv")
    alineaciones = load_csv("alineaciones_rivales.csv")
elif modulo in ["Individual", "Jugadores"]:
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
    "<div class='topbar'><div class='title'>⚽ TEMPORADA 2026/2027 · V15.12.46 VISUAL 360</div><div class='nav'>Inicio &nbsp;&nbsp; Liga &nbsp;&nbsp; Rivales &nbsp;&nbsp; Equipo &nbsp;&nbsp; Individual &nbsp;&nbsp; <b>Jugadores</b></div></div>",
    unsafe_allow_html=True,
)

# Navegación inferior para móvil. Funciona con query params para no depender del sidebar.
_mobile_nav = [
    ("Inicio", "inicio", "⌂", "Inicio"),
    ("Resumen liga", "liga", "▦", "Liga"),
    ("Rivales", "rivales", "◈", "Rivales"),
    ("Equipo", "equipo", "◉", "Equipo"),
    ("Individual", "individual", "◎", "Individual"),
    ("Jugadores", "jugadores", "♟", "Jugadores"),
]
_mobile_nav_html = ["<nav class='mobile-bottom-nav' aria-label='Navegación móvil'>"]
for _mod_name, _view_slug, _icon, _label in _mobile_nav:
    _active = " active" if modulo == _mod_name else ""
    _extra = f"&team={quote(str(seleccionado))}" if (_mod_name == "Rivales" and seleccionado) else ""
    _mobile_nav_html.append(
        f"<a class='{_active.strip()}' href='?view={_view_slug}{_extra}' target='_self'>"
        f"<span class='mn-icon'>{_icon}</span><span>{_label}</span></a>"
    )
_mobile_nav_html.append("</nav>")
st.markdown("".join(_mobile_nav_html), unsafe_allow_html=True)

if modulo == "Inicio":
    _pt_mobile_logo = _image_data_uri(BASE / "primer_toque_logo.png")
    st.markdown(
        f"<div class='mobile-install-note'><div class='mi-icon'><img src='{_pt_mobile_logo}' alt='Primer Toque'></div>"
        "<div class='mi-copy'><b>Prueba móvil</b>En iPhone: Safari → Compartir → Añadir a pantalla de inicio. "
        "Esta versión ya está preparada para usarse como acceso tipo app.</div></div>",
        unsafe_allow_html=True,
    )

if modulo == "Rivales" and seleccionado:
    _equipos_mobile = load_csv("equipos_liga.csv")
    if not _equipos_mobile.empty:
        _chips = ["<div class='mobile-rival-strip' aria-label='Selector rápido de rival'>"]
        for _, _er in _equipos_mobile.sort_values("orden").iterrows():
            _tm = str(_er.equipo)
            _ac = " active" if _tm == seleccionado else ""
            _logo = _team_logo_tag(_tm, 20)
            _short = _safe_html(short_team_name(_tm))
            _chips.append(
                f"<a class='mobile-rival-chip{_ac}' href='?view=rivales&team={quote(_tm)}' target='_self'>"
                f"{_logo}<span>{_short}</span></a>"
            )
        _chips.append("</div>")
        st.markdown("".join(_chips), unsafe_allow_html=True)

if _area == "infantil":
    render_infantil()
    st.stop()
elif modulo == "Inicio":
    render_home()
    st.stop()
elif modulo == "Resumen liga":
    render_league_summary()
    st.stop()
elif modulo == "Jugadores":
    render_players()
    st.stop()
elif modulo == "Individual":
    render_individual()
    st.stop()
elif modulo == "Equipo":
    render_team_360()
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


def goal_time_slot(minute):
    """Devuelve uno de los seis tramos de 15 minutos usados en la ficha rival."""
    try:
        m = float(minute)
    except Exception:
        return None
    if m <= 15:
        return 0
    if m <= 30:
        return 1
    if m <= 45:
        return 2
    if m <= 60:
        return 3
    if m <= 75:
        return 4
    return 5


def build_goal_meaning_records(part_df, ev_df, team):
    """
    Reconstruye el marcador de cada partido y clasifica cada gol por lo que
    significó en ese momento. Las categorías son excluyentes para que el total
    de la matriz cuadre con el total de goles del filtro.
    """
    out = []
    goal_types_for = {"gol", "penalti_gol"}
    goal_types_against = {"gol_contra", "penalti_contra_gol"}
    for _, rr in part_df.sort_values("jornada").iterrows():
        if pd.isna(rr.goles_local) or pd.isna(rr.goles_visitante):
            continue
        j = int(rr.jornada)
        gf_final, gc_final, opp = team_score(rr, team)
        e = ev_df[(ev_df.jornada == j) & (ev_df.tipo.isin(goal_types_for | goal_types_against))].copy()
        if e.empty:
            continue
        e["_ord"] = range(len(e))
        e["_min"] = pd.to_numeric(e.minuto, errors="coerce")
        e = e.sort_values(["_min", "_ord"], kind="stable")
        sf = sa = 0
        had_trailed_for = False
        had_trailed_against = False
        for _, er in e.iterrows():
            is_for = er.tipo in goal_types_for
            scorer_before = sf if is_for else sa
            other_before = sa if is_for else sf
            scorer_final = gf_final if is_for else gc_final
            other_final = gc_final if is_for else gf_final
            had_trailed = had_trailed_for if is_for else had_trailed_against

            if scorer_before == 0 and other_before == 0:
                # Separamos los 1-0/0-1 definitivos porque son goles de victoria
                # y dejan una lectura distinta a una mera apertura de marcador.
                if scorer_final == 1 and other_final == 0:
                    meaning = "Victoria (1-0)"
                else:
                    meaning = "Apertura de marcador"
            elif scorer_before < other_before:
                if scorer_before + 1 == other_before:
                    meaning = "Igualar marcador"
                else:
                    meaning = "Reducir distancia"
            elif scorer_before == other_before:
                meaning = "Remontada" if had_trailed else "Ponerse por delante"
            else:
                meaning = "Ampliar ventaja"

            if is_for:
                sf += 1
            else:
                sa += 1
            if sf < sa:
                had_trailed_for = True
            if sa < sf:
                had_trailed_against = True

            slot = goal_time_slot(er.minuto)
            if slot is None:
                continue
            out.append({
                "jornada": j,
                "oponente": str(opp),
                "minuto": int(float(er.minuto)) if pd.notna(er.minuto) else None,
                "lado": "favor" if is_for else "contra",
                "tipo_marcador": meaning,
                "tramo": slot,
                "jugador": str(er.jugador) if pd.notna(er.jugador) else "",
            })
    return pd.DataFrame(out)


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
    f"""<div class='team-head'>{image_html(logo_path)}<div><div class='team-name'>{_safe_html(seleccionado)}</div><div class='team-sub'>Lliga Comunitat Juvenil · Nord · Temporada 2026/2027</div><span class='badge'>{'ANÁLISIS REAL J1–J5' if seleccionado in ["Primer Toque C.F. 'A'", "C.F. At. Burriana - Salesianos 'A'", "Villarreal C.F. 'C'", "Alboraya U.D. 'B'", "C.F. Històrics de València 'A'", "C.F. Torre Levante 'A'", "Ath. Massamagrell C.F. 'A'", "C.F. Inter San José Valencia 'B'", "Col. Salgui E.D.E. 'A'", "C.F. Cracks 'A'", "Paterna C.F. 'A'", "Manises C.F. 'A'", "Patacona C.F. 'B'", "C.D.F. Canet 'A'", "Bétera C.F. 'A'", "C.D. Acero 'A'"] else 'PERFIL PREPARADO · DATOS PENDIENTES'}</span></div></div>""",
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


if seleccionado == "Manises C.F. 'A'":
    st.markdown(
        """<div class='card' style='margin:8px 0 12px'>
        <div class='section-title'>Manises · actas J1–J5 completas</div>
        <div class='note'><b>Balance:</b> 5 PJ · 2 V · 1 E · 2 D · 6 GF · 6 GC · 7 puntos.
        <br><b>Datos cargados:</b> XI inicial de las 5 jornadas · dorsales utilizados · convocatorias · sistema 1-4-3-3 en las cinco jornadas · minutos reconstruidos desde los cambios del acta · goles · tarjetas · expulsiones y goles encajados.
        <br><b>Goleadores:</b> Hugo Albiach Serrano (2), Alvaro Mateo Canovas (1), Martin Rodriguez De Guzman (1), Hugo Pastor Femenia (1) y David Lopez Garcia (1).
        <br><b>Incidencias:</b> Izan Saiz Escobar fue expulsado en J1; Hugo Albiach Serrano fue expulsado en J4 y marcó en propia puerta en J2.
        <br><b>Fuente:</b> actas FFCV mostradas en el vídeo aportado por el usuario.</div>
        </div>""",
        unsafe_allow_html=True,
    )


if seleccionado == "Patacona C.F. 'B'":
    st.markdown(
        """<div class='card' style='margin:8px 0 12px'>
        <div class='section-title'>Patacona · actas J1–J5 completas</div>
        <div class='note'><b>Balance:</b> 5 PJ · 1 V · 0 E · 4 D · 5 GF · 12 GC · 3 puntos.
        <br><b>Datos cargados:</b> XI inicial de las 5 jornadas · 90 convocatorias/minutajes · dorsales utilizados · sistema 1-5-4-1 en J1–J5 · cambios reconstruidos desde el acta · goles · tarjetas · expulsiones y goles encajados.
        <br><b>Goleadores:</b> Miron Saliakhov (1), Rayan Bououd Mazouz (1), Mario Garcia Fernando (1) y Julio Casero Girona (1), más 1 autogol rival en J1.
        <br><b>Incidencias:</b> Daniel Cano Navarro fue expulsado en J1. Lucas Ferrandis Paredes vio amarilla en J3 y J5; Antonio Gallur Valencia, en J4.
        <br><b>Fuente:</b> actas FFCV mostradas en el vídeo aportado por el usuario.</div>
        </div>""",
        unsafe_allow_html=True,
    )



if seleccionado == "C.D.F. Canet 'A'":
    st.markdown(
        """<div class='card' style='margin:8px 0 12px'>
        <div class='section-title'>Canet · actas J1–J5 completas</div>
        <div class='note'><b>Balance:</b> 5 PJ · 1 V · 0 E · 4 D · 2 GF · 10 GC · 3 puntos.
        <br><b>Datos cargados:</b> XI inicial de las 5 jornadas · convocatorias y minutajes · dorsales utilizados · sistemas · cambios reconstruidos desde el acta · goles · tarjetas · expulsiones y goles encajados.
        <br><b>Goleadores:</b> Xavi Salvador Granell (1) y Alejandro David Julia Zalvez (1).
        <br><b>Sistemas:</b> J1 1-4-4-2; J2-J5 1-4-3-3.
        <br><b>Incidencias:</b> Eric Romero Campos fue expulsado por doble amarilla en J4 y Pau Bernet Sanchez vio roja en el 90' de esa misma jornada.
        <br><b>Fuente:</b> actas FFCV mostradas en el vídeo aportado por el usuario.</div>
        </div>""",
        unsafe_allow_html=True,
    )

# Perfiles ya desarrollados con jornadas completas.
analizados = ["Bétera C.F. 'A'", "C.D. Acero 'A'", "Primer Toque C.F. 'A'", "C.F. At. Burriana - Salesianos 'A'", "Villarreal C.F. 'C'", "Alboraya U.D. 'B'", "C.F. Històrics de València 'A'", "C.F. Torre Levante 'A'", "Ath. Massamagrell C.F. 'A'", "C.F. Inter San José Valencia 'B'", "Col. Salgui E.D.E. 'A'", "C.F. Cracks 'A'", "Paterna C.F. 'A'", "Manises C.F. 'A'", "Patacona C.F. 'B'", "C.D.F. Canet 'A'"]
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

# ---------------- Tipos de gol por tramo ----------------
_goal_meanings = build_goal_meaning_records(part, ev_scope, seleccionado)
_goal_meaning_order = [
    "Apertura de marcador",
    "Victoria (1-0)",
    "Ampliar ventaja",
    "Ponerse por delante",
    "Remontada",
    "Igualar marcador",
    "Reducir distancia",
]
_goal_slot_labels = ["0–15'", "16–30'", "31–45+'", "46–60'", "61–75'", "76–90+'"][0:6]

st.markdown(
    "<div class='goaltype-wrap'><div class='goaltype-head'>"
    "<div class='gt-title'>Tipos de gol por tramo</div>"
    "<div class='gt-sub'>Qué significó cada gol para el marcador y en qué momento llegó. Círculo más grande = más goles; pasa el ratón para ver las jornadas.</div>"
    "</div></div>",
    unsafe_allow_html=True,
)

def _goaltype_matrix(side):
    dd = _goal_meanings[_goal_meanings.lado == side].copy() if not _goal_meanings.empty else pd.DataFrame()
    against = side == "contra"
    top = []
    for slot in range(6):
        n = int((dd.tramo == slot).sum()) if not dd.empty else 0
        top.append(n)
    max_n = max([1] + top)
    side_title = "Goles en contra" if against else "Goles a favor"
    html = [f"<div class='goaltype-card'><div class='gt-side'>{side_title}</div><div class='goaltype-grid'>"]
    html.append("<div></div>")
    for n in top:
        html.append(f"<div class='gt-top{' against' if against else ''}'>{n}</div>")
    html.append("<div></div>")
    for meaning in _goal_meaning_order:
        html.append(f"<div class='gt-rowlab'>{_safe_html(meaning)}</div>")
        row_total = 0
        for slot in range(6):
            if dd.empty:
                cell = dd
                n = 0
            else:
                cell = dd[(dd.tipo_marcador == meaning) & (dd.tramo == slot)]
                n = len(cell)
            row_total += n
            if n:
                sz = 24 + 15 * (n / max_n) ** 0.5
                tips = []
                for _, z in cell.sort_values(["jornada", "minuto"]).iterrows():
                    player = f" · {z.jugador}" if str(z.jugador).strip() else ""
                    tips.append(f"J{int(z.jornada)} vs {short_team_name(z.oponente)} · {int(z.minuto)}'{player}")
                title = _safe_html(" | ".join(tips), quote=True)
                klass = "against" if against else "for"
                html.append(f"<div class='gt-cell'><div class='gt-bubble {klass}' title='{title}' style='width:{sz:.0f}px;height:{sz:.0f}px'>{n}</div></div>")
            else:
                html.append("<div class='gt-cell'><span class='gt-dot'></span></div>")
        html.append(f"<div class='gt-total'>{row_total if row_total else '·'}</div>")
    html.append("<div class='gt-foot blank'></div>")
    for lab in _goal_slot_labels:
        html.append(f"<div class='gt-foot'>{lab}</div>")
    html.append("<div class='gt-foot blank'></div></div></div>")
    return "".join(html)

st.markdown(_goaltype_matrix("favor"), unsafe_allow_html=True)
st.markdown(_goaltype_matrix("contra"), unsafe_allow_html=True)

# ---------------- Diferencia de goles por partido + acumulado ----------------
_diff_rows = []
_cum = 0
for _, _rr in part.sort_values("jornada").iterrows():
    _gf, _gc, _opp = team_score(_rr, seleccionado)
    if _gf is None:
        continue
    _d = int(_gf - _gc)
    _cum += _d
    _diff_rows.append({
        "j": int(_rr.jornada), "gf": int(_gf), "gc": int(_gc), "opp": str(_opp),
        "diff": _d, "cum": _cum,
    })

if not _diff_rows:
    st.markdown("<div class='goal-diff-card'><div class='goal-diff-title'>Diferencia de goles y acumulado</div><div class='note'>Sin partidos con marcador para este filtro.</div></div>", unsafe_allow_html=True)
else:
    _w, _h = 1120, 330
    _l, _r, _t, _b = 62, 64, 26, 72
    _pw, _ph = _w - _l - _r, _h - _t - _b
    _vals = [abs(x["diff"]) for x in _diff_rows] + [abs(x["cum"]) for x in _diff_rows]
    _lim = max(3, max(_vals) if _vals else 3)
    _y0 = _t + _ph / 2
    _yscale = (_ph / 2 - 8) / _lim
    _n = len(_diff_rows)
    _step = _pw / max(1, _n)
    _barw = min(150, _step * .62)
    _svg = [f"<svg viewBox='0 0 {_w} {_h}' style='width:100%;height:auto;display:block'>"]
    # grid and axes
    for val in range(-_lim, _lim + 1):
        if val == 0 or val in (-_lim, _lim):
            yy = _y0 - val * _yscale
            dash = "4 4" if val == 0 else "0"
            stroke = "#b9c5d3" if val == 0 else "#e9edf2"
            _svg.append(f"<line x1='{_l}' y1='{yy:.1f}' x2='{_w-_r}' y2='{yy:.1f}' stroke='{stroke}' stroke-width='1' stroke-dasharray='{dash}'/>")
            _svg.append(f"<text x='{_l-10}' y='{yy+4:.1f}' text-anchor='end' font-size='11' fill='#64748b'>{val}</text>")
            _svg.append(f"<text x='{_w-_r+10}' y='{yy+4:.1f}' font-size='11' fill='#d69b10'>{val}</text>")
    _pts = []
    for i, row in enumerate(_diff_rows):
        xx = _l + _step * (i + .5)
        d = row["diff"]
        yy = _y0 - d * _yscale
        bar_y = min(_y0, yy)
        bar_h = max(2, abs(d) * _yscale)
        color = "#4eae83" if d > 0 else ("#df627b" if d < 0 else "#94a3b8")
        _svg.append(f"<rect x='{xx-_barw/2:.1f}' y='{bar_y:.1f}' width='{_barw:.1f}' height='{bar_h:.1f}' rx='6' fill='{color}' opacity='.95'/>")
        lab_y = yy - 8 if d >= 0 else yy + 16
        _svg.append(f"<text x='{xx:.1f}' y='{lab_y:.1f}' text-anchor='middle' font-size='12' font-weight='900' fill='#0b3766'>{d:+d}</text>")
        cy = _y0 - row["cum"] * _yscale
        _pts.append((xx, cy, row["cum"]))
        opp = _safe_html(short_team_name(row["opp"]))
        _svg.append(f"<text x='{xx:.1f}' y='{_h-38}' text-anchor='middle' font-size='11' font-weight='800' fill='#334155'>J{row['j']} · {opp}</text>")
        _svg.append(f"<text x='{xx:.1f}' y='{_h-22}' text-anchor='middle' font-size='10' font-weight='800' fill='#64748b'>{row['gf']}–{row['gc']}</text>")
    if _pts:
        points = " ".join(f"{x:.1f},{y:.1f}" for x,y,_ in _pts)
        _svg.append(f"<polyline points='{points}' fill='none' stroke='#e2a91c' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/>")
        for x,y,cval in _pts:
            _svg.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5.5' fill='#e2a91c' stroke='white' stroke-width='2'/>")
            _svg.append(f"<text x='{x:.1f}' y='{y-10:.1f}' text-anchor='middle' font-size='11' font-weight='900' fill='#c88d00'>{cval:+d}</text>")
    _svg.append(f"<text x='18' y='{_t+_ph/2:.1f}' transform='rotate(-90 18 {_t+_ph/2:.1f})' text-anchor='middle' font-size='11' font-weight='800' fill='#334155'>Diferencia</text>")
    _svg.append(f"<text x='{_w-18}' y='{_t+_ph/2:.1f}' transform='rotate(90 {_w-18} {_t+_ph/2:.1f})' text-anchor='middle' font-size='11' font-weight='800' fill='#b77d00'>Acumulado</text>")
    _svg.append("<g><rect x='450' y='5' width='10' height='10' rx='2' fill='#4eae83'/><text x='466' y='14' font-size='10' font-weight='800' fill='#334155'>Diferencia por partido</text><line x1='592' y1='10' x2='616' y2='10' stroke='#e2a91c' stroke-width='3'/><circle cx='604' cy='10' r='4' fill='#e2a91c' stroke='white' stroke-width='1'/><text x='622' y='14' font-size='10' font-weight='800' fill='#334155'>Acumulado temporada</text></g>")
    _svg.append("</svg>")
    st.markdown("<div class='goal-diff-card'><div class='goal-diff-title'>Diferencia de goles y acumulado</div>" + "".join(_svg) + "</div>", unsafe_allow_html=True)

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

st.caption("V15.12.46 · Equipo 360 visual + evolución por jornadas + jugadores históricos/informes/físico ampliado.")
