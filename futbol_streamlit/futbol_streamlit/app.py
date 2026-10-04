import streamlit as st
import pandas as pd
from pathlib import Path
import html

st.set_page_config(page_title='Joan Fortuño · Análisis de Fútbol', page_icon='⚽', layout='wide')
BASE = Path(__file__).parent
DATA = BASE / 'data'

@st.cache_data
def load_csv(name):
    p = DATA / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

equipos = load_csv('equipos_liga.csv')
plantillas = load_csv('plantillas_rivales.csv')
minutos = load_csv('minutos_rivales.csv')
partidos = load_csv('partidos_rivales.csv')
eventos = load_csv('eventos_rivales.csv')
clasificacion = load_csv('clasificacion_liga.csv')
alineaciones = load_csv('alineaciones_rivales.csv')

NAVY='#0a2a52'; NAVY2='#14265b'; ORANGE='#f15a24'; RED='#ff3348'; ORANGE2='#ff9f1c'; YELLOW='#ffd447'; LGREEN='#7ee56b'; DGREEN='#08783f'; GREY='#8ca0b3'

st.markdown(f"""<style>
:root{{--navy:{NAVY};--orange:{ORANGE};--muted:#6f7787;}}
[data-testid="stAppViewContainer"]{{background:#fff;}}
[data-testid="stSidebar"]{{background:#f4f7fa;border-right:1px solid #e2e7ef;}}
.block-container{{padding-top:1.4rem;max-width:1500px;}}
.hero-kicker{{color:#8790a0;font-weight:800;font-size:1rem;letter-spacing:.06em;margin-bottom:-.25rem}}
.hero-title{{color:{NAVY2};font-size:3rem;font-weight:900;line-height:1.05;border-bottom:5px solid var(--orange);padding-bottom:.5rem;margin-bottom:.5rem}}
.brand{{font-size:1.3rem;font-weight:900;color:{NAVY2};text-align:center;border-top:3px solid var(--orange);padding-top:.6rem;margin-top:.2rem}}
[data-testid="stMetric"]{{border:1px solid #e2e7ef;border-radius:12px;padding:14px;background:#fff;}}
.team-summary{{border:1px solid #e3e8ef;border-radius:16px;padding:18px;background:linear-gradient(135deg,#fbfcfe,#f3f7fb);margin:.5rem 0 1rem}}
.pitch{{position:relative;width:100%;max-width:700px;aspect-ratio:68/105;margin:0 auto;background:#278a43;border:3px solid white;border-radius:12px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.12);background-image:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0,rgba(255,255,255,.035) 10%,rgba(0,0,0,.025) 10%,rgba(0,0,0,.025) 20%);}}
.pitch:before{{content:'';position:absolute;left:0;right:0;top:50%;border-top:2px solid rgba(255,255,255,.85);}}
.pitch:after{{content:'';position:absolute;width:18%;aspect-ratio:1;left:41%;top:41%;border:2px solid rgba(255,255,255,.85);border-radius:50%;}}
.penalty-top,.penalty-bottom{{position:absolute;left:25%;width:50%;height:14%;border:2px solid rgba(255,255,255,.85)}}
.penalty-top{{top:-2px;border-top:0}} .penalty-bottom{{bottom:-2px;border-bottom:0}}
.player-chip{{position:absolute;transform:translate(-50%,-50%);background:white;color:{NAVY};border:3px solid {ORANGE};border-radius:14px;padding:6px 8px;min-width:105px;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,.2);font-size:.78rem;font-weight:800;line-height:1.15;}}
.player-chip .num{{display:inline-flex;align-items:center;justify-content:center;background:{NAVY};color:white;border-radius:50%;width:26px;height:26px;margin-right:4px}}
.player-chip .pct{{display:block;color:{DGREEN};font-size:.72rem;margin-top:2px}}
.small-note{{font-size:.82rem;color:#6f7787}}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    logo = BASE/'primer_toque_logo.png'
    if logo.exists(): st.image(str(logo), use_container_width=True)
    st.markdown('<div class="brand">JOAN FORTUÑO</div>', unsafe_allow_html=True)
    st.caption('JA 2026/27')
    st.divider()
    modulo = st.radio('Sección', ['Rivales','Equipo','Individual'])
    if modulo == 'Rivales':
        st.markdown('#### Equipos de la liga')
        lista = equipos.sort_values('orden')['equipo'].tolist() if not equipos.empty else []
        default_idx = lista.index("Bétera C.F. 'A'") if "Bétera C.F. 'A'" in lista else 0
        seleccionado = st.radio('Equipo', lista, index=default_idx, label_visibility='collapsed')
    else:
        seleccionado = None

st.markdown('<div class="hero-kicker">PLATAFORMA DE</div><div class="hero-title">ANÁLISIS DE FÚTBOL</div>', unsafe_allow_html=True)

if modulo != 'Rivales':
    st.subheader(modulo)
    st.info('Este bloque se desarrollará después. Ahora estamos centrados en construir toda la base de RIVALES.')
    st.stop()

st.subheader(f'Rivales · {seleccionado}')
st.caption('V5 · Rivales. Bétera ya dispone de J1–J4 para minutos, titularidad, formaciones, goles y disciplina.')

f1,f2,f3 = st.columns([1.3,1,1.2])
with f1:
    ambito = st.segmented_control('Ámbito', ['Total','Casa','Fuera'], default='Total')
with f2:
    jornadas_disponibles = sorted(minutos.loc[minutos.equipo==seleccionado,'jornada'].dropna().astype(int).unique().tolist()) if not minutos.empty else []
    opciones_j = ['Total'] + [f'J{x}' for x in jornadas_disponibles]
    jornada_sel = st.selectbox('Jornada', opciones_j)
with f3:
    st.selectbox('Temporada', ['2026/27'])

part = partidos.copy()
if not part.empty:
    part = part[(part.local==seleccionado) | (part.visitante==seleccionado)]
    if ambito=='Casa': part = part[part.local==seleccionado]
    if ambito=='Fuera': part = part[part.visitante==seleccionado]
    if jornada_sel!='Total': part = part[part.jornada==int(jornada_sel[1:])]

# --- Ficha rápida del rival ---
roster_all = plantillas[plantillas.equipo==seleccionado].copy()
stand_row = clasificacion[clasificacion.equipo==seleccionado].sort_values('jornada').tail(1) if not clasificacion.empty else pd.DataFrame()
team_parts_all = partidos[(partidos.local==seleccionado)|(partidos.visitante==seleccionado)].copy() if not partidos.empty else pd.DataFrame()

formation_label='—'; formation_pct=None; formation_n=0
if not team_parts_all.empty:
    formations=[]
    for _,r in team_parts_all.iterrows():
        s=r.sistema_local if r.local==seleccionado else r.sistema_visitante
        if pd.notna(s) and str(s).strip(): formations.append(str(s))
    if formations:
        vc=pd.Series(formations).value_counts()
        formation_label=vc.index[0]
        formation_n=int(vc.iloc[0]); formation_pct=formation_n/len(formations)*100

k1,k2,k3,k4,k5,k6 = st.columns(6)
if not stand_row.empty:
    sr=stand_row.iloc[0]
    k1.metric('Clasificación',f"{int(sr.posicion)}º / {len(clasificacion[clasificacion.jornada==sr.jornada])}")
    k2.metric('Puntos',int(sr.puntos))
    k3.metric('PJ liga',int(sr.pj))
else:
    k1.metric('Clasificación','—'); k2.metric('Puntos','—'); k3.metric('PJ liga','—')
k4.metric('Jugadores',len(roster_all))
k5.metric('Partidos cargados',len(team_parts_all))
k6.metric('Formación más usada', formation_label if formation_pct is None else f'{formation_label} · {formation_pct:.0f}%')
if seleccionado=="Bétera C.F. 'A'":
    st.caption('Clasificación tomada de FFCV en J5 (04/10/2026). J1–J4 ya están cargadas para minutos y titularidades; los resultados marcados como pendientes/parciales se irán validando con nuevas capturas.')
    st.markdown('#### Base cargada de Bétera')
    b1,b2,b3,b4=st.columns(4)
    b1.metric('Jornadas con minutos','4 / 4')
    b2.metric('Jugadores observados',len(roster_all))
    b3.metric('Sistema más usado','1-4-3-3','50% (2 de 4)')
    b4.metric('Último sistema','1-5-3-2','J4')

if part.empty:
    st.info('Equipo creado en la base de Rivales. Aún no hemos cargado jornadas para este equipo.')
else:
    gf=[]; gc=[]
    for _,r in part.iterrows():
        if r['local']==seleccionado: gf.append(r.goles_local); gc.append(r.goles_visitante)
        else: gf.append(r.goles_visitante); gc.append(r.goles_local)
    pj=len(part); GF=int(sum(gf)); GC=int(sum(gc)); V=sum(a>b for a,b in zip(gf,gc)); E=sum(a==b for a,b in zip(gf,gc)); D=sum(a<b for a,b in zip(gf,gc))
    cols=st.columns(7)
    vals=[pj,GF,GC,GF-GC,V,E,D]
    labels=['PJ cargados','GF','GC','DG','Victorias','Empates','Derrotas']
    for col,label,val in zip(cols,labels,vals): col.metric(label,val)

jug_tab,res_tab,gol_tab,form_tab,disc_tab,comp_tab = st.tabs(['👥 Jugadores','📊 Resumen','⚽ Goles','🧩 Formación','🟨 Disciplina','📈 Comparativa'])

with jug_tab:
    roster = roster_all.copy()
    if roster.empty:
        st.info('Plantilla pendiente de cargar para este equipo.')
    else:
        roster = roster.sort_values('dorsal')
        m = minutos[minutos.equipo==seleccionado].copy()
        if ambito!='Total' and not partidos.empty:
            js=[]
            for _,r in partidos.iterrows():
                if ambito=='Casa' and r.local==seleccionado: js.append(int(r.jornada))
                if ambito=='Fuera' and r.visitante==seleccionado: js.append(int(r.jornada))
            m=m[m.jornada.isin(js)]
        if jornada_sel!='Total': m=m[m.jornada==int(jornada_sel[1:])]
        if m.empty:
            st.dataframe(roster, hide_index=True, use_container_width=True)
            st.warning('Tenemos la plantilla, pero aún no hay minutos cargados para este filtro.')
        else:
            js=sorted(m.jornada.astype(int).unique())
            table=roster[['dorsal','jugador']].copy()
            for j in js:
                d=m[m.jornada==j][['dorsal','minutos']].rename(columns={'minutos':f'J{j}'})
                table=table.merge(d,on='dorsal',how='left')
            minute_cols=[f'J{j}' for j in js]
            table['Minutos totales']=table[minute_cols].sum(axis=1,skipna=True)
            possible_minutes=90*len(js) if js else 0
            table['% minutos']=(table['Minutos totales']/possible_minutes*100).round(0) if possible_minutes else 0
            starts=m.groupby('dorsal')['titular'].sum()
            table['% titularidad']=(table.dorsal.map(starts).fillna(0)/len(js)*100).round(0) if js else 0
            # Estimación transparente: 60% frecuencia global + 40% frecuencia en las 2 jornadas más recientes.
            recent_js=js[-2:]
            recent=m[m.jornada.isin(recent_js)].groupby('dorsal')['titular'].sum() if recent_js else pd.Series(dtype=float)
            recent_pct=table.dorsal.map(recent).fillna(0)/max(1,len(recent_js))*100
            table['Prob. once estimada']=(0.60*table['% titularidad']+0.40*recent_pct).round(0)
            table['Posible titularidad']=table['Prob. once estimada'].map(lambda x:f'{x:.0f}%')

            def color_min(v):
                if pd.isna(v): return f'background-color:{GREY};color:white;font-weight:700'
                x=float(v)
                if x<=20: bg=RED
                elif x<=45: bg=ORANGE2
                elif x<=60: bg=YELLOW
                elif x<=75: bg=LGREEN
                else: bg=DGREEN
                fg='white' if x<=20 or x>75 else '#111'
                return f'background-color:{bg};color:{fg};font-weight:800;text-align:center'

            styler=table.style
            if minute_cols: styler=styler.map(color_min,subset=minute_cols)
            styler=styler.format({c:'{:.0f} min' for c in minute_cols},na_rep='—').format({'% minutos':'{:.0f}%','% titularidad':'{:.0f}%'})
            st.dataframe(styler,hide_index=True,use_container_width=True,height=min(780,120+35*len(table)))
            st.caption('Minutos: rojo 0–20 · naranja 21–45 · amarillo 46–60 · verde claro 61–75 · verde oscuro 76–90. La probabilidad de once es una estimación: 60% frecuencia de titularidad en J1–J4 + 40% titularidad en las 2 jornadas más recientes. No incluye lesiones, sanciones ni decisiones técnicas futuras.')

with res_tab:
    left,right = st.columns([1.1,1])
    with left:
        st.markdown('### Clasificación de liga')
        if clasificacion.empty:
            st.info('Clasificación pendiente.')
        else:
            latest=int(clasificacion.jornada.max())
            cl=clasificacion[clasificacion.jornada==latest][['posicion','equipo','puntos','pj','pg','pe','pp']].copy()
            cl.columns=['Pos','Equipo','PTS','PJ','PG','PE','PP']
            def highlight_team(row):
                if row['Equipo']==seleccionado:
                    return [f'background-color:#fff1e9;font-weight:800;color:{NAVY2}']*len(row)
                return ['']*len(row)
            st.dataframe(cl.style.apply(highlight_team,axis=1),hide_index=True,use_container_width=True,height=620)
            sr=clasificacion[clasificacion.jornada==latest].iloc[0]
            st.caption(f"FFCV · J{latest} · {sr.fecha}")
    with right:
        st.markdown('### Partidos cargados')
        if part.empty: st.info('Sin partidos cargados todavía.')
        else:
            shown=part.copy()
            shown['Partido']=shown.apply(lambda r:f"{r['local']} {int(r['goles_local'])}-{int(r['goles_visitante'])} {r['visitante']}",axis=1)
            st.dataframe(shown[['jornada','fecha','Partido','campo']],hide_index=True,use_container_width=True)

with gol_tab:
    ev=eventos[(eventos.equipo==seleccionado)&(eventos.tipo=='gol')].copy()
    if jornada_sel!='Total': ev=ev[ev.jornada==int(jornada_sel[1:])]
    if ev.empty: st.info('No hay goles cargados para este filtro.')
    else:
        st.dataframe(ev[['jornada','minuto','jugador','detalle']],hide_index=True,use_container_width=True)
        bins=[0,15,30,45,60,75,999]; labels=['0–15','16–30','31–45+','46–60','61–75','76–90+']
        ev['tramo']=pd.cut(ev.minuto,bins=bins,labels=labels,include_lowest=True,right=True)
        counts=ev['tramo'].value_counts().reindex(labels,fill_value=0)
        st.bar_chart(counts)

with form_tab:
    st.markdown('### Formaciones utilizadas')
    team_forms=[]
    if not team_parts_all.empty:
        for _,r in team_parts_all.sort_values('jornada').iterrows():
            s=r.sistema_local if r.local==seleccionado else r.sistema_visitante
            team_forms.append({'Jornada':f"J{int(r.jornada)}",'Sistema':str(s)})
    if team_forms:
        ff=pd.DataFrame(team_forms)
        counts=ff['Sistema'].value_counts().rename_axis('Sistema').reset_index(name='Partidos')
        counts['% uso']=(counts['Partidos']/len(ff)*100).round(0).astype(int).astype(str)+'%'
        cfa,cfb=st.columns([1,1.5])
        with cfa:
            st.dataframe(ff,hide_index=True,use_container_width=True)
            st.dataframe(counts,hide_index=True,use_container_width=True)
        with cfb:
            st.markdown('### Posible XI · 1-4-3-3')
            st.caption('Se usa el sistema más frecuente en J1–J4. El jugador mostrado en cada línea se elige por frecuencia de titularidad dentro del rol observado.')
            al=alineaciones[alineaciones.equipo==seleccionado].copy()
            mm=minutos[minutos.equipo==seleccionado].copy()
            if not al.empty and not mm.empty:
                starts=mm.groupby('dorsal')['titular'].sum()/4*100
                recent=mm[mm.jornada.isin([3,4])].groupby('dorsal')['titular'].sum()/2*100
                prob=(0.6*starts+0.4*recent).fillna(0)
                # choose 4-3-3 by role frequencies; tie break by estimated probability
                role_counts=al.groupby(['rol','dorsal','jugador']).size().reset_index(name='role_starts')
                role_counts['prob']=role_counts.dorsal.map(prob).fillna(0)
                selected=[]
                needs={'POR':1,'DEF':4,'MED':3,'ATA':3}
                for role,nneed in needs.items():
                    rr=role_counts[role_counts.rol==role].sort_values(['role_starts','prob'],ascending=False).head(nneed)
                    selected.extend(rr.to_dict('records'))
                # positions for a vertical pitch (left/top percentages)
                coords={'POR':[(50,89)],'DEF':[(18,70),(39,73),(61,73),(82,70)],'MED':[(25,48),(50,52),(75,48)],'ATA':[(20,23),(50,18),(80,23)]}
                html_players=[]
                used={k:0 for k in coords}
                for r in selected:
                    role=r['rol']; idx=used[role]; used[role]+=1
                    x,y=coords[role][idx]
                    p=float(r['prob'])
                    nm=str(r['jugador']).split()[0]
                    html_players.append(f"<div class='player-chip' style='left:{x}%;top:{y}%'><span class='num'>{int(r['dorsal'])}</span>{html.escape(nm)}<span class='pct'>{p:.0f}% estimado</span></div>")
                pitch='<div class="pitch"><div class="penalty-top"></div><div class="penalty-bottom"></div>'+''.join(html_players)+'</div>'
                st.markdown(pitch,unsafe_allow_html=True)
            else:
                st.info('Faltan alineaciones para dibujar el XI.')
    else:
        st.info('Formaciones pendientes de cargar.')

with disc_tab:
    ev=eventos[(eventos.equipo==seleccionado)&(eventos.tipo.isin(['amarilla','roja']))].copy()
    if jornada_sel!='Total': ev=ev[ev.jornada==int(jornada_sel[1:])]
    if ev.empty: st.info('Sin tarjetas cargadas para este filtro.')
    else: st.dataframe(ev[['jornada','minuto','tipo','jugador']],hide_index=True,use_container_width=True)

with comp_tab:
    st.info('La comparativa entre equipos se activará a medida que carguemos más jornadas. Los 16 equipos ya están creados en la base.')
