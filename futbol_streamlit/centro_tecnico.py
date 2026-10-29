"""Sala técnica de Primer Toque: evidencia, revisión de vídeo y plan semanal.
No atribuye causas tácticas a los resultados sin etiquetado manual.
"""
from pathlib import Path
from datetime import datetime
from io import BytesIO
import pandas as pd
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from xml.sax.saxutils import escape

BASE = Path(__file__).resolve().parent
REVIEWS = BASE / 'data' / 'revisiones_tecnicas.csv'
FIELDS = ['jornada','fase','subfase','minuto','resultado','jugadores','observacion','correccion','prioridad','fecha_registro']
PHASES = {
  'Salida de balón':['Apoyos y alturas','Fijar y progresar','Pase interior','Salida exterior','Juego directo / segunda jugada'],
  'Ataque organizado':['Ocupación de carriles','Tercer hombre','Ataque de área','Finalización','Cambio de orientación'],
  'Defensa organizada':['Protección interior','Altura de línea','Presión en banda','Coberturas','Defensa del área'],
  'Transición ofensiva':['Primer pase','Ataque al espacio','Ocupación de área'],
  'Transición defensiva':['Presión tras pérdida','Balance defensivo','Repliegue','Duelos'],
  'ABP':['Córner a favor','Córner en contra','Falta a favor','Falta en contra','Saque de banda'],
}

def reviews_read():
    if not REVIEWS.exists():return pd.DataFrame(columns=FIELDS)
    try:
        d=pd.read_csv(REVIEWS,dtype={'jornada':str,'minuto':str}).fillna('')
        for c in FIELDS:
            if c not in d.columns:d[c]=''
        return d[FIELDS]
    except Exception as exc:
        st.error(f'No se han podido leer las revisiones: {exc}')
        return pd.DataFrame(columns=FIELDS)

def reviews_save(d):
    try:
        REVIEWS.parent.mkdir(parents=True,exist_ok=True)
        d.to_csv(REVIEWS,index=False,encoding='utf-8-sig')
        return True
    except OSError as exc:
        st.error(f'No se puede guardar en el servidor: {exc}. Descarga el CSV como copia de seguridad.')
        return False

def _pct(n,d):return f'{100*n/d:.0f} %' if d else '—'

def _pdf(md, recommendations, annotations):
    buffer=BytesIO();doc=SimpleDocTemplate(buffer,pagesize=(595,842),rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42)
    s=getSampleStyleSheet();s['Title'].textColor=colors.HexColor('#13365e');s['Heading2'].textColor=colors.HexColor('#13365e')
    story=[Paragraph('PRIMER TOQUE · INFORME TÉCNICO',s['Title']),Paragraph('Temporada 2026/27 · corte J'+str(int(md.jornada.max())),s['Normal']),Spacer(1,14)]
    pj=len(md);pts=int(md.pts.sum()); gf=int(md.gf.sum());gc=int(md.gc.sum())
    story.append(Paragraph(f'{pj} PJ · {pts} puntos · {gf} GF · {gc} GC · {pts/pj:.2f} puntos/PJ',s['Heading2']))
    rows=[['J','Rival','C/F','GF','GC','Pts']]
    for r in md.itertuples():rows.append([str(r.jornada),str(r.rival)[:39],str(r.condicion),str(r.gf),str(r.gc),str(r.pts)])
    table=Table(rows, colWidths=[26,270,51,42,42,42],repeatRows=1)
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#143b69')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTSIZE',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,1),(-1,-1),.2,colors.lightgrey)]))
    story.extend([table,Spacer(1,16),Paragraph('Prioridades para revisar (hipótesis)',s['Heading2'])])
    for p in recommendations:story.append(Paragraph('• '+escape(p),s['BodyText']))
    story.extend([Spacer(1,12),Paragraph('Etiquetas aportadas por el cuerpo técnico',s['Heading2'])])
    if annotations.empty:story.append(Paragraph('No hay secuencias etiquetadas. Pendiente de análisis visual.',s['Normal']))
    else:
        for _,r in annotations.tail(30).iterrows():
            line=f"J{r.jornada} · {r.fase} / {r.subfase} · min {r.minuto or '?'} · {r.resultado}: {r.observacion}. Corrección: {r.correccion}"
            story.append(Paragraph(escape(line),s['BodyText']));story.append(Spacer(1,4))
    story.extend([Spacer(1,14),Paragraph('Nota metodológica: los resultados oficiales no identifican por sí solos fallos tácticos. Las etiquetas de vídeo son observaciones manuales, no verificadas automáticamente.',s['Italic'])])
    doc.build(story);return buffer.getvalue()

def render(md, eventos, avanzado, minutos):
    d=md.sort_values('jornada').copy().reset_index(drop=True)
    st.markdown('''<style>
    .tech-hero{padding:24px;border-radius:20px;color:#fff;background:linear-gradient(110deg,#092744,#15528a);margin:17px 0}
    .tech-hero h2{font-size:1.65rem;color:white;margin:0 0 6px;font-weight:850}.tech-hero p{margin:0;color:#d9e7f6}
    .tech-callout{padding:12px 15px;border-radius:11px;background:#fff8ed;border-left:4px solid #f0911b;margin:10px 0}
    </style><div class="tech-hero"><h2>⚽ SALA TÉCNICA · PERFORMANCE HUB</h2><p>De los datos a las decisiones: contexto competitivo, secuencias etiquetadas y microciclo.</p></div>''',unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(['📊 Inteligencia competitiva','🎬 Laboratorio de vídeo','🧠 Plan de partido','📑 Informe técnico'])
    with t1:
        st.markdown('#### Mapa de rendimiento · evidencia oficial')
        c1,c2,c3,c4,c5=st.columns(5)
        c1.metric('Puntos / partido',f'{d.pts.mean():.2f}')
        c2.metric('Victorias',f'{int((d.pts==3).sum())}/{len(d)}')
        c3.metric('Porterías a cero',f'{int((d.gc==0).sum())}/{len(d)}')
        c4.metric('Sin marcar',f'{int((d.gf==0).sum())}/{len(d)}')
        c5.metric('Balance',f'{int(d.gf.sum()-d.gc.sum()):+d}')
        period=st.select_slider('Ventana de análisis',options=list(range(1,len(d)+1)),value=min(5,len(d)),format_func=lambda x:f'Últimos {x} partidos',key='tech_rolling')
        focus=d.tail(period)
        st.bar_chart(focus.set_index('jornada')[['gf','gc']].rename(columns={'gf':'Goles a favor','gc':'Goles encajados'}))
        c1,c2=st.columns(2)
        with c1:
            st.markdown('**Comparador contextual · casa / fuera**')
            context=[]
            for cond,g in d.groupby('condicion'):
                context.append({'Campo':cond,'PJ':len(g),'Pts/PJ':round(g.pts.mean(),2),'GF/PJ':round(g.gf.mean(),2),'GC/PJ':round(g.gc.mean(),2),'% victorias':_pct(int((g.pts==3).sum()),len(g))})
            st.dataframe(pd.DataFrame(context),hide_index=True,use_container_width=True)
        with c2:
            st.markdown('**Estado según el primer gol**')
            ev=eventos[eventos.equipo.astype(str)=="Primer Toque C.F. 'A'"].copy()
            ev['minuto']=pd.to_numeric(ev.minuto,errors='coerce')
            first=[]
            for j in d.jornada:
                g=ev[(ev.jornada==j)&ev.tipo.isin(['gol','penalti_gol','gol_contra'])].sort_values('minuto')
                if g.empty: state='Sin gol registrado'
                elif g.iloc[0].tipo=='gol_contra':state='Encajamos primero'
                else:state='Marcamos primero'
                first.append(state)
            fd=d[['jornada','pts']].copy();fd['Primer gol']=first
            st.dataframe(fd.groupby('Primer gol',as_index=False).agg(PJ=('jornada','count'),Puntos=('pts','sum')).assign(**{'Pts/PJ':lambda x:(x.Puntos/x.PJ).round(2)}),hide_index=True,use_container_width=True)
            st.caption('Basado en eventos con minuto; sin evento no se presupone marcador inicial.')
        st.markdown('**Control de cobertura del dato**')
        av=avanzado.copy();av['jornada']=pd.to_numeric(av.jornada,errors='coerce')
        cov=[]
        for col,label in [('tiros_favor','Tiros propios'),('tiros_contra','Tiros rivales'),('posesion_favor_pct','Posesión'),('ocasiones_favor','Ocasiones')]:
            if col in av:
                cover=av[av.jornada.isin(d.jornada)].dropna(subset=[col]);cov.append({'Indicador':label,'Partidos cubiertos':f'{len(cover)}/{len(d)}','Cobertura':_pct(len(cover),len(d))})
        if cov:st.dataframe(pd.DataFrame(cov),hide_index=True,use_container_width=True)
        st.info('No se estiman xG, mapas de calor ni causas tácticas sin eventos espaciales o etiquetado específico.')
    with t2:
        st.markdown('#### Etiquetado de situaciones de partido')
        st.caption('Registra lo que realmente observas en Veo/YouTube. Las etiquetas se guardan en CSV y alimentan el informe y el plan semanal.')
        with st.form('new_video_tag',clear_on_submit=True):
            a,b,c=st.columns(3)
            j=a.selectbox('Jornada',d.jornada.tolist(),index=len(d)-1)
            phase=b.selectbox('Fase',list(PHASES))
            subphase=c.selectbox('Concepto',PHASES[phase])
            a,b,c=st.columns([1,2,2])
            minute=a.text_input('Minuto (ej. 64:30)',max_chars=8)
            verdict=b.selectbox('Valoración',['A mejorar','Correcto','Destacado'])
            priority=c.selectbox('Prioridad',['Alta','Media','Baja'])
            players=st.text_input('Jugadores implicados (opcional)')
            note=st.text_area('Observación: ¿qué ocurre exactamente?',max_chars=500)
            coaching=st.text_area('Consigna concreta para corregir/reforzar',max_chars=500)
            ok=st.form_submit_button('➕ Guardar secuencia',type='primary',use_container_width=True)
        if ok:
            if len(note.strip())<8:st.warning('Describe la secuencia con al menos 8 caracteres.')
            else:
                r=reviews_read();new=dict(zip(FIELDS,[str(j),phase,subphase,minute,verdict,players,note.strip(),coaching.strip(),priority,datetime.now().strftime('%Y-%m-%d %H:%M')]))
                if reviews_save(pd.concat([r,pd.DataFrame([new])],ignore_index=True)):st.success('Secuencia guardada.');st.rerun()
        tags=reviews_read()
        if not tags.empty:
            one,two=st.columns(2)
            jfilter=one.multiselect('Filtrar jornadas',sorted(tags.jornada.unique().tolist()),default=sorted(tags.jornada.unique().tolist()))
            pfilter=two.multiselect('Filtrar fases',sorted(tags.fase.unique().tolist()),default=sorted(tags.fase.unique().tolist()))
            shown=tags[tags.jornada.isin(jfilter)&tags.fase.isin(pfilter)].copy()
            st.dataframe(shown[['jornada','minuto','fase','subfase','resultado','prioridad','jugadores','observacion','correccion']],hide_index=True,use_container_width=True,height=300)
            st.download_button('⬇️ Exportar etiquetado (CSV)',tags.to_csv(index=False).encode('utf-8-sig'),file_name='secuencias_video.csv',mime='text/csv')
            with st.expander('Administrar etiquetas'):
                options=[f"{i} · J{r.jornada} · {r.fase} · {str(r.observacion)[:45]}" for i,r in tags.iterrows()]
                selection=st.selectbox('Registro a eliminar',options)
                if st.button('Eliminar registro seleccionado',key='tech_remove'):
                    idx=int(selection.split(' · ',1)[0]);reviews_save(tags.drop(idx).reset_index(drop=True));st.rerun()
        else:st.info('Sin secuencias anotadas todavía. Empieza por los goles encajados y las pérdidas en salida.')
        st.caption('Los enlaces a los vídeos de los partidos se encuentran en las fichas de rivales. No se importan automáticamente clips protegidos de Veo.')
    tags=reviews_read()
    problems=tags[tags.resultado=='A mejorar'] if not tags.empty else tags
    priorities=[]
    if d.gc.mean()>=1.4:priorities.append('Revisar origen de goles encajados: transición, organización o ABP (clasificar en vídeo).')
    if d.gf.mean()<1.4:priorities.append('Evaluar finalización y entradas al área: separar volumen de llegadas y calidad de ocasión.')
    if int((d.gf==0).sum())>=2:priorities.append('Comparar salidas de balón en partidos sin marcar frente a partidos con gol.')
    if not problems.empty:
        counts=problems.groupby(['fase','subfase']).size().sort_values(ascending=False)
        for (p,s),count in counts.head(3).items():priorities.append(f'{p} · {s}: {count} secuencias etiquetadas «A mejorar» por el cuerpo técnico.')
    if not priorities:priorities.append('Priorizar revisión cualitativa de los últimos partidos antes de fijar cambios tácticos.')
    with t3:
        st.markdown('#### Decisiones del cuerpo técnico')
        st.markdown('**Prioridades derivadas de los datos**')
        for item in priorities:st.markdown(f'<div class="tech-callout">{escape(item)}</div>',unsafe_allow_html=True)
        st.caption('Indicadores de revisión, no diagnósticos causales automáticos.')
        selected=st.selectbox('Objetivo de microciclo',['Salida de balón','Protección interior','Transiciones defensivas','Finalización','ABP'],key='tech_micro')
        plans={
          'Salida de balón':['Activación: rondos orientados 5v3 · identificar tercer hombre.','Tarea 1: 1P+4+2 exteriores vs presión alta, progresar por fuera o encontrar interior.','Tarea 2: salida 8v7 en campo real; fijar, atraer y cambiar orientación.','Transferencia: partido 10v10, puntuar progresión limpia y segunda jugada.'],
          'Protección interior':['Activación: 4v4+comodín, cerrar línea de pase interior.','Tarea 1: orientar a banda con ayudas 2v1 y cobertura interior.','Tarea 2: bloque medio 8v8+porteros, distancias y protección del área.','Transferencia: partido con bonificación por recuperación exterior.'],
          'Transiciones defensivas':['Activación: posesión 6v6+2 con reacción a pérdida.','Tarea 1: transición 4v3 tras robo, balance de seguridad.','Tarea 2: 8v8 en tres zonas, 5 segundos de presión tras pérdida.','Transferencia: partido real enfatizando reajuste de línea y ayudas.'],
          'Finalización':['Activación: tercer hombre y remate con oposición progresiva.','Tarea 1: centros y llegada de segunda línea, atacar zonas distintas.','Tarea 2: 7v6 en último tercio, elegir pase interior / exterior.','Transferencia: partido con registro de tiros y ocasiones reales.'],
          'ABP':['Activación: repaso de referencias de zona y marcajes.','Tarea 1: córner ofensivo, bloqueos legales y segunda jugada.','Tarea 2: defensa de faltas laterales y córneres, rechace y salida.','Transferencia: 6 repeticiones por situación, checklist de roles.']
        }
        st.markdown(f'**Propuesta de microciclo · {selected}**')
        for i,task in enumerate(plans[selected],1):st.write(f'**{i}.** {task}')
        st.caption('Propuesta de entrenamiento adaptable a disponibilidad, estado físico y observaciones del staff; no es prescripción automática.')
        st.markdown('**Registro de incidencias por jornada**')
        if not tags.empty:
            st.dataframe(tags.groupby(['jornada','fase','resultado']).size().rename('Secuencias').reset_index(),hide_index=True,use_container_width=True)
        else:st.info('Al etiquetar vídeos aquí aparecerán patrones repetidos por jornada y fase.')
    with t4:
        st.markdown('#### Informe para reunión del cuerpo técnico')
        st.write('El PDF incluye marcadores, prioridades objetivas y las secuencias clasificadas manualmente.')
        st.download_button('📑 Descargar informe PDF',data=_pdf(d,priorities,tags),file_name='primer_toque_informe_tecnico.pdf',mime='application/pdf',type='primary')
        st.download_button('📊 Exportar resultados por jornada',d.to_csv(index=False).encode('utf-8-sig'),file_name='primer_toque_resultados.csv',mime='text/csv')
        st.write(f'**Cobertura visual:** {len(tags)} secuencias etiquetadas; {tags.jornada.nunique() if not tags.empty else 0} jornadas revisadas de {len(d)} disputadas.')
        st.caption('Persistencia: CSV local en data/. En Streamlit Cloud, los archivos guardados en disco pueden perderse al reiniciar/desplegar; para varios entrenadores se recomienda una base de datos persistente.')
