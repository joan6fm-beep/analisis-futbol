import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title='Análisis Fútbol', page_icon='⚽', layout='wide')
DATA = Path(__file__).parent / 'data'

@st.cache_data
def load(name):
    p = DATA / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

partidos = load('partidos.csv')
jugadores = load('jugadores_partido.csv')
equipo = load('equipo_partido.csv')
eventos = load('eventos.csv')

st.title('⚽ Plataforma de Análisis de Fútbol')
st.caption('V1 · BeOne / FFCV · Datos directos + métricas derivadas')

with st.sidebar:
    st.header('Filtros')
    if not partidos.empty:
        labels = partidos['rival'].astype(str) + ' · ' + partidos['fecha'].astype(str)
        choice = st.selectbox('Partido', labels)
        idx = labels[labels == choice].index[0]
        partido_id = partidos.loc[idx, 'partido_id']
    else:
        partido_id = None
    st.divider()
    page = st.radio('Módulo', ['Resumen', 'Individual', 'Colectivo', 'Rival / FFCV', 'Datos derivados'])

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
