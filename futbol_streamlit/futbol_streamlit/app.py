import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title='Joan Fortuño · Primer Toque CF', page_icon='⚽', layout='wide')
DATA = Path(__file__).parent / 'data'

@st.cache_data
def load(name):
    p = DATA / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

partidos = load('partidos.csv')
jugadores = load('jugadores_partido.csv')
equipo = load('equipo_partido.csv')
eventos = load('eventos.csv')

st.markdown("""<style>
:root {--navy:#18245b;--orange:#f04a0b;--soft:#f5f7fb;--muted:#6f7787;}
[data-testid="stAppViewContainer"] {background:#ffffff;}
[data-testid="stSidebar"] {background:#f4f7fa;border-right:1px solid #e5e9f0;}
.block-container {padding-top:2.2rem;max-width:1400px;}
h1,h2,h3 {color:var(--navy);}
.hero-kicker{color:#7d8799;font-weight:700;font-size:1.05rem;letter-spacing:.04em;margin-bottom:-.5rem}
.hero-title{color:var(--navy);font-size:3.2rem;font-weight:850;line-height:1.05;border-bottom:5px solid var(--orange);padding-bottom:.55rem;margin-bottom:.7rem}
.brand-name{font-weight:850;text-align:center;color:var(--navy);font-size:1.35rem;border-top:3px solid var(--orange);padding-top:.65rem;margin-top:.4rem}
.small-muted{color:var(--muted)}
[data-testid="stMetric"] {background:#fff;border:1px solid #e5e9f0;border-radius:12px;padding:18px;box-shadow:0 2px 10px rgba(24,36,91,.04)}
div[role="radiogroup"] label:has(input:checked){background:#fff0e9;border-left:4px solid var(--orange);border-radius:7px;padding-left:.45rem}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="hero-kicker">PLATAFORMA DE</div><div class="hero-title">ANÁLISIS DE FÚTBOL</div>', unsafe_allow_html=True)
st.caption('Primer Toque CF · BeOne / FFCV · Datos directos + métricas derivadas')

with st.sidebar:
    st.image(str(Path(__file__).parent / 'primer_toque_logo.png'), use_container_width=True)
    st.markdown('<div class="brand-name">JOAN FORTUÑO</div>', unsafe_allow_html=True)
    st.markdown('### Temporada')
    st.selectbox('Temporada', ['2026/27'], label_visibility='collapsed')
    st.markdown('### Partido')
    if not partidos.empty:
        labels = partidos['rival'].astype(str) + ' · ' + partidos['fecha'].astype(str)
        choice = st.selectbox('Partido', labels, label_visibility='collapsed')
        idx = labels[labels == choice].index[0]
        partido_id = partidos.loc[idx, 'partido_id']
    else:
        partido_id = None
    st.divider()
    page = st.radio('Módulo', ['Resumen', 'Individual', 'Posiciones', 'Colectivo', 'Rival / FFCV', 'Datos derivados'])

if partido_id is None:
    st.info('Añade el primer partido en data/partidos.csv')
    st.stop()

p = partidos[partidos.partido_id == partido_id].iloc[0]
st.subheader(f"{p['equipo']} vs {p['rival']}")
st.caption(f"{p['fecha']} · {p['condicion']} · {p['competicion']}")

if page == 'Resumen':
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Resultado', p.get('resultado','—'))
    c2.metric('GF', p.get('goles_favor','—'))
    c3.metric('GC', p.get('goles_contra','—'))
    ep = equipo[equipo.partido_id == partido_id]
    c4.metric('Jugadores registrados', len(jugadores[jugadores.partido_id == partido_id]))
    st.markdown('### Estado de carga')
    st.write('Esta primera versión conserva únicamente valores que podamos validar. Los campos pendientes quedan vacíos en vez de inventar datos.')
    st.dataframe(ep, use_container_width=True, hide_index=True)

elif page == 'Individual':
    df = jugadores[jugadores.partido_id == partido_id].copy()
    if df.empty:
        st.warning('Aún no hay registros individuales validados para este partido.')
    else:
        numeric = ['minutos','distancia_m','velocidad_max_kmh','aceleraciones','desaceleraciones','tiros']
        for c in numeric:
            if c in df: df[c] = pd.to_numeric(df[c], errors='coerce')
        if {'distancia_m','minutos'}.issubset(df.columns):
            df['m_por_min'] = df['distancia_m'] / df['minutos'].replace(0, pd.NA)
            df['distancia_90_m'] = df['m_por_min'] * 90
        if {'aceleraciones','minutos'}.issubset(df.columns):
            df['aceleraciones_90'] = df['aceleraciones'] / df['minutos'].replace(0, pd.NA) * 90
        if {'tiros','minutos'}.issubset(df.columns):
            df['tiros_90'] = df['tiros'] / df['minutos'].replace(0, pd.NA) * 90
        positions = ['Todas'] + sorted(df['posicion'].dropna().unique().tolist()) if 'posicion' in df else ['Todas']
        pos = st.selectbox('Posición', positions)
        if pos != 'Todas': df = df[df.posicion == pos]
        st.dataframe(df, use_container_width=True, hide_index=True)
        cols = [x for x in ['minutos','distancia_m','velocidad_max_kmh','aceleraciones','tiros','m_por_min','distancia_90_m'] if x in df.columns]
        if cols:
            metric = st.selectbox('Comparar métrica', cols)
            chart = df[['jugador',metric]].dropna().set_index('jugador')
            if not chart.empty: st.bar_chart(chart)

elif page == 'Posiciones':
    st.markdown('### Comparativa por posiciones')
    st.info('Este módulo comparará jugadores de la misma posición cuando incorporemos los datos completos de BeOne.')

elif page == 'Colectivo':
    df = equipo[equipo.partido_id == partido_id].copy()
    st.markdown('### Datos del equipo')
    st.dataframe(df, use_container_width=True, hide_index=True)
    if not df.empty:
        row = df.iloc[0]
        tiros = pd.to_numeric(pd.Series([row.get('tiros')]), errors='coerce').iloc[0]
        goles = pd.to_numeric(pd.Series([row.get('goles')]), errors='coerce').iloc[0]
        if pd.notna(tiros) and tiros > 0 and pd.notna(goles):
            st.metric('Conversión de tiro', f'{goles/tiros*100:.1f}%')
        st.markdown('### Próximas métricas')
        st.write('Conversión, tiros por gol, ratio de tiros, producción por posesión ofensiva, cadenas de pase, distribución territorial y comparativas por periodos.')

elif page == 'Rival / FFCV':
    ev = eventos[eventos.partido_id == partido_id].copy()
    st.markdown('### Eventos y acta')
    if ev.empty: st.warning('Pendiente de incorporar/validar el acta FFCV completa.')
    else: st.dataframe(ev, use_container_width=True, hide_index=True)
    st.markdown('### Cuando acumulemos jornadas')
    st.write('Calcularemos % de titularidad, % de minutos, XI más frecuente, sustituciones habituales, tarjetas, goleadores, tramos de gol, local/visitante y frecuencia reciente de aparición en el XI.')

else:
    st.markdown('### Motor de métricas derivadas')
    formulas = pd.DataFrame([
        ['Distancia / min','distancia_m ÷ minutos','Intensidad relativa'],
        ['Distancia / 90','distancia_m ÷ minutos × 90','Comparar jugadores con distinto tiempo'],
        ['Aceleraciones / 90','aceleraciones ÷ minutos × 90','Carga explosiva relativa'],
        ['Tiros / 90','tiros ÷ minutos × 90','Producción ofensiva individual'],
        ['Conversión','goles ÷ tiros × 100','Eficacia de finalización'],
        ['% titularidad','titularidades ÷ partidos disponibles × 100','Uso habitual del jugador'],
        ['% minutos','minutos jugados ÷ minutos disponibles × 100','Peso competitivo'],
        ['Ratio de tiros','tiros propios ÷ (propios + rival)','Dominio de finalización'],
    ], columns=['Métrica','Fórmula','Uso'])
    st.dataframe(formulas, use_container_width=True, hide_index=True)
    st.info('La filosofía será: conservar dato bruto + generar automáticamente métricas nuevas sin modificar el dato original.')
