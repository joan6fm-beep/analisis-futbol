"""Centro de decisiones deportivas basado únicamente en datos comprobables."""
import pandas as pd
import streamlit as st


def _n(v):
    try:
        return float(v) if pd.notna(v) else None
    except (TypeError, ValueError):
        return None


def _trend(df):
    return pd.DataFrame({
        'Jornada':df.jornada.astype(int), 'Rival':df.rival,
        'Condición':df.condicion,'GF':df.gf,'GC':df.gc,
        'Diferencia':df.gf-df.gc,'Puntos':df.pts,
        'Puntos acumulados':df.pts.cumsum(), 'DG acumulada':(df.gf-df.gc).cumsum(),
        'Puntos últimos 3':df.pts.rolling(3,min_periods=1).sum(),
        'GF últimos 3':df.gf.rolling(3,min_periods=1).sum(),
        'GC últimos 3':df.gc.rolling(3,min_periods=1).sum(),
    })


def render(md, avanzado, clasif):
    md=md.sort_values('jornada').reset_index(drop=True).copy()
    last=int(md.jornada.max())
    st.markdown('## 🧠 Centro de análisis · decisiones para el cuerpo técnico')
    st.caption('Análisis competitivo cuantitativo. Las conclusiones tácticas que requieren vídeo o coordenadas se identifican como hipótesis, no como hechos.')
    window=st.segmented_control('Periodo', ['Temporada','Últimos 5','Últimos 3'], default='Temporada', key='team_pro_window')
    n={'Temporada':len(md),'Últimos 5':5,'Últimos 3':3}.get(window,len(md))
    d=md.tail(n)
    pj=len(d)
    gf=int(d.gf.sum());gc=int(d.gc.sum());pts=int(d.pts.sum())
    a,b,c,e=st.columns(4)
    a.metric('Puntos / partido',f'{pts/pj:.2f}',help='3 por victoria, 1 por empate')
    b.metric('Goles a favor / partido',f'{gf/pj:.2f}')
    c.metric('Goles encajados / partido',f'{gc/pj:.2f}')
    e.metric('Diferencia / partido',f'{(gf-gc)/pj:+.2f}')
    tabs=st.tabs(['📈 Rendimiento y tendencias','🏟️ Contexto y rivales','🎯 Producción y eficacia','🧩 Informe del entrenador','📥 Exportación'])
    t=_trend(md)
    with tabs[0]:
        st.markdown('#### Evolución acumulada, partido a partido')
        st.line_chart(t.set_index('Jornada')[['Puntos acumulados','DG acumulada']],height=280)
        st.markdown('#### Producción ofensiva y defensiva')
        st.bar_chart(d.set_index('jornada')[['gf','gc']].rename(columns={'gf':'Goles a favor','gc':'Goles en contra'}), height=240)
        if len(md)>=3:
            st.markdown('#### Media móvil de 3 encuentros')
            r=pd.DataFrame({'Jornada':md.jornada,'GF / partido (3J)':md.gf.rolling(3,min_periods=3).mean(),
                            'GC / partido (3J)':md.gc.rolling(3,min_periods=3).mean()}).dropna()
            st.line_chart(r.set_index('Jornada'),height=230)
            recent=md.tail(3); prior=md.iloc[-6:-3]
            if len(prior)==3:
                for title,col in [('Puntos','pts'),('Goles marcados','gf'),('Goles encajados','gc')]:
                    now=int(recent[col].sum());before=int(prior[col].sum());
                    st.write(f'**{title}:** {now} últimos 3 vs {before} tres anteriores ({now-before:+d}).')
        st.caption('Los gráficos reflejan resultados reales; no permiten atribuir causas tácticas sin revisión del vídeo.')
    with tabs[1]:
        for name,subset in [('En casa',d[d.condicion=='Casa']),('Fuera',d[d.condicion=='Fuera'])]:
            if subset.empty:continue
            p=len(subset); points=int(subset.pts.sum())
            st.write(f'**{name} · {p} PJ:** {points/p:.2f} puntos/PJ · {subset.gf.sum()/p:.2f} GF/PJ · {subset.gc.sum()/p:.2f} GC/PJ')
        scope=clasif[pd.to_numeric(clasif.get('jornada'), errors='coerce')==last].copy() if not clasif.empty else pd.DataFrame()
        if not scope.empty:
            lookup=dict(zip(scope.equipo.astype(str),pd.to_numeric(scope.posicion, errors='coerce')))
            comp=d[['jornada','rival','condicion','gf','gc','pts']].copy()
            comp['Posición rival (J'+str(last)+')']=comp.rival.map(lookup)
            comp.columns=['J','Rival','Campo','GF','GC','Pts','Posición actual del rival']
            st.dataframe(comp,hide_index=True,use_container_width=True)
            st.caption(f'Posición de los rivales tomada de la clasificación de J{last}: es una foto actual, no la posición que tenían cuando se disputó cada partido.')
        else:
            st.info('No hay clasificación de la jornada actual para contextualizar los rivales.')
    with tabs[2]:
        if avanzado.empty:
            st.info('No hay métricas avanzadas cargadas.')
        else:
            av=avanzado.copy()
            av['jornada']=pd.to_numeric(av.jornada,errors='coerce')
            av=av[av.jornada.isin(d.jornada)].sort_values('jornada')
            names=[('tiros_favor','Tiros propios'),('tiros_contra','Tiros rivales'),('ocasiones_favor','Ocasiones propias'),('ocasiones_contra','Ocasiones rivales'),('posesion_favor_pct','Posesión %'),('corners_favor','Córneres propios')]
            available=[(key,title) for key,title in names if key in av and pd.to_numeric(av[key],errors='coerce').notna().any()]
            if available:
                view=av[['jornada','rival']+[k for k,_ in available]].copy()
                view=view.rename(columns={'jornada':'J','rival':'Rival',**dict(available)})
                st.dataframe(view,hide_index=True,use_container_width=True)
            else: st.info('No se han registrado todavía métricas avanzadas en este periodo.')
            if 'tiros_favor' in av:
                valid=av.dropna(subset=['tiros_favor']).copy()
                valid=valid[valid.tiros_favor>0]
                if not valid.empty:
                    results=d[['jornada','gf']].merge(valid[['jornada','tiros_favor']],on='jornada')
                    shots=float(results.tiros_favor.sum());goals=float(results.gf.sum())
                    st.metric('Conversión de tiro (solo partidos con tiros registrados)',f'{100*goals/shots:.1f}%',help=f'{int(goals)} goles oficiales en {int(shots)} tiros registrados; {len(results)} jornadas con cobertura.')
                    st.caption(f'Cobertura del indicador: {len(results)}/{pj} jornadas del periodo. No se extrapolan los partidos sin tiros.')
            if 'ocasiones_favor' in av:
                sub=av.dropna(subset=['ocasiones_favor'])
                if len(sub):
                    st.caption(f'Ocasiones registradas en {len(sub)}/{pj} jornadas. Las definiciones de ocasión pueden variar según proveedor.')
    with tabs[3]:
        st.markdown('#### Diagnóstico de resultados — indicadores y preguntas de vídeo')
        prompts=[]
        if gc/pj>=1.5:
            prompts.append(('🔴 Prioridad defensiva',f'{gc} goles encajados en {pj} partidos ({gc/pj:.2f}/PJ).',
                            'Revisar origen del primer pase que rompe líneas, coberturas, defensa del área y transiciones tras pérdida.'))
        else:
            prompts.append(('🟢 Protección de portería',f'{gc/pj:.2f} goles encajados por partido.',
                            'Separar goles a balón parado, transición y ataque posicional antes de elegir un ajuste.'))
        if gf/pj<1.2:
            prompts.append(('🟠 Producción ofensiva',f'{gf/pj:.2f} goles marcados por partido.',
                            'Revisar ocupación del área, último pase, llegadas de segunda línea y recuperación tras pérdida.'))
        else:
            prompts.append(('⚽ Ataque',f'{gf/pj:.2f} goles marcados por partido.',
                            'Contrastar volumen de llegadas con precisión de tiro y calidad de ocasiones, cuando haya datos.'))
        blanks=int((d.gf==0).sum()); clean=int((d.gc==0).sum())
        if blanks:prompts.append(('🟠 Partidos sin gol',f'{blanks}/{pj} partidos sin marcar.',
                                  'Comparar salida de balón, progresiones por fuera y recepciones interiores con los partidos con gol.'))
        if not clean:prompts.append(('🔴 Porterías a cero',f'0/{pj} partidos sin encajar.',
                                     'Evaluar situaciones evitables y cómo reacciona el bloque tras marcar y tras perder balón.'))
        for heading,evidence,question in prompts:
            with st.container(border=True):
                st.markdown(f'**{heading}**')
                st.write(f'**Dato:** {evidence}')
                st.write(f'**Vídeo / intervención propuesta:** {question}')
        st.markdown('#### Guion de revisión por partido')
        st.write('1. Salida de balón: alternativas al primer pase, apoyos y tercer hombre.')
        st.write('2. Ataque: amplitud, fijaciones, rupturas, ocupación del área y segunda jugada.')
        st.write('3. Defensa: altura de bloque, protección del carril central, ayudas en banda y distancia entre líneas.')
        st.write('4. Transiciones: 5 segundos tras pérdida, coberturas y recuperación de la estructura.')
        st.write('5. ABP: remates a favor/en contra y organización de la segunda jugada.')
        st.caption('Estas son pautas de observación; no se ha inferido automáticamente que el equipo falle en cada aspecto.')
    with tabs[4]:
        st.download_button('⬇️ Descargar evolución por jornadas (CSV)',t.to_csv(index=False).encode('utf-8-sig'),file_name='primer_toque_analisis_evolucion.csv',mime='text/csv',key='pro_evolucion_csv')
        export=d[['jornada','rival','condicion','gf','gc','dg','pts','res','sistema']]
        st.download_button('⬇️ Descargar periodo seleccionado (CSV)',export.to_csv(index=False).encode('utf-8-sig'),file_name='primer_toque_periodo.csv',mime='text/csv',key='pro_periodo_csv')
    st.divider()
