"""Generador dinámico de informes con el diseño de cuatro secciones del Acero.
Usa datos del rival y escudos ya incluidos en la app; no contiene resultados precargados.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
from html import escape
from datetime import date
import math
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    FONT='D'; BOLD='DB'
except Exception:
    FONT='Helvetica'; BOLD='Helvetica-Bold'

W,H=A4; M=30; IW=W-2*M
navy=HexColor('#102F55'); blue=HexColor('#1A426C'); muted=HexColor('#64748B'); border=HexColor('#D9E2EC'); pale=HexColor('#F2F6FB')
green=HexColor('#40D980'); red=HexColor('#F8CACA'); orange=HexColor('#FFBA76'); yellow=HexColor('#FFE58D'); mint=HexColor('#B9F3D1'); grey=HexColor('#EDF1F6')


# Helpers privados de este generador; sin dependencia del PDF antiguo.
_TEAM_LOGOS = {
    "Bétera C.F. 'A'":"betera_logo.png", "C.D. Acero 'A'":"acero_logo.png",
    "Primer Toque C.F. 'A'":"primer_toque_logo.png", "C.F. At. Burriana - Salesianos 'A'":"salesianos_logo.png",
    "Villarreal C.F. 'C'":"villarreal_logo.png", "Alboraya U.D. 'B'":"alboraya_logo.png",
    "C.F. Històrics de València 'A'":"historics_logo.png", "Ath. Massamagrell C.F. 'A'":"massamagrell_logo.png",
    "C.F. Torre Levante 'A'":"torre_levante_logo.png", "C.F. Inter San José Valencia 'B'":"inter_san_jose_logo.png",
    "Col. Salgui E.D.E. 'A'":"salgui_logo.png", "C.F. Cracks 'A'":"cracks_logo.png",
    "Paterna C.F. 'A'":"paterna_logo.png", "Manises C.F. 'A'":"manises_logo.png",
    "Patacona C.F. 'B'":"patacona_logo.png", "C.D.F. Canet 'A'":"canet_logo.png",
}

def _short_team(name: str) -> str:
    out = str(name or '')
    for suffix in [" 'A'", " 'B'", " 'C'", " 'D'"]:
        out = out.replace(suffix, '')
    return out

def _team_score(row, team):
    if pd.isna(row.goles_local) or pd.isna(row.goles_visitante):
        opp = row.visitante if row.local == team else row.local
        return None, None, opp
    if row.local == team:
        return int(row.goles_local), int(row.goles_visitante), row.visitante
    return int(row.goles_visitante), int(row.goles_local), row.local

def _goal_slot(minute):
    try:
        m = float(minute)
    except Exception:
        return None
    if m <= 15: return 0
    if m <= 30: return 1
    if m <= 45: return 2
    if m <= 60: return 3
    if m <= 75: return 4
    return 5

def _goal_meanings(part_df, ev_df, team):
    out = []
    goal_for = {'gol','penalti_gol'}
    goal_against = {'gol_contra','penalti_contra_gol'}
    for _, rr in part_df.sort_values('jornada').iterrows():
        if pd.isna(rr.goles_local) or pd.isna(rr.goles_visitante):
            continue
        j = int(rr.jornada)
        gf_final, gc_final, opp = _team_score(rr, team)
        e = ev_df[(ev_df.jornada == j) & (ev_df.tipo.isin(goal_for | goal_against))].copy()
        if e.empty:
            continue
        e['_ord'] = range(len(e)); e['_min'] = pd.to_numeric(e.minuto, errors='coerce')
        e = e.sort_values(['_min','_ord'], kind='stable')
        sf = sa = 0; trail_for = trail_against = False
        for _, er in e.iterrows():
            is_for = er.tipo in goal_for
            scorer_before = sf if is_for else sa
            other_before = sa if is_for else sf
            scorer_final = gf_final if is_for else gc_final
            other_final = gc_final if is_for else gf_final
            had_trailed = trail_for if is_for else trail_against
            if scorer_before == 0 and other_before == 0:
                meaning = 'Victoria (1-0)' if scorer_final == 1 and other_final == 0 else 'Apertura de marcador'
            elif scorer_before < other_before:
                meaning = 'Igualar marcador' if scorer_before + 1 == other_before else 'Reducir distancia'
            elif scorer_before == other_before:
                meaning = 'Remontada' if had_trailed else 'Ponerse por delante'
            else:
                meaning = 'Ampliar ventaja'
            if is_for: sf += 1
            else: sa += 1
            if sf < sa: trail_for = True
            if sa < sf: trail_against = True
            sl = _goal_slot(er.minuto)
            if sl is not None:
                out.append({'jornada':j,'oponente':str(opp),'minuto':int(float(er.minuto)),
                            'lado':'favor' if is_for else 'contra','meaning':meaning,'slot':sl,
                            'jugador':str(er.jugador or '')})
    return pd.DataFrame(out)

def _opponent_badge_path(name):
    filename = _TEAM_LOGOS.get(str(name))
    path = Path(__file__).parent / filename if filename else None
    return path if path and path.exists() else None

def _build_selected_xi(al, mdf, scope_js, main_form):
    njs=max(1,len(scope_js)); starts=mdf.groupby('jugador')['titular'].sum()/njs*100 if not mdf.empty else pd.Series(dtype=float); recent_js=scope_js[-2:]; recent=mdf[mdf.jornada.isin(recent_js)].groupby('jugador')['titular'].sum()/max(1,len(recent_js))*100 if recent_js and not mdf.empty else pd.Series(dtype=float); idx=starts.index.union(recent.index); prob=.6*starts.reindex(idx,fill_value=0)+.4*recent.reindex(idx,fill_value=0)
    if al.empty: return []
    rc=al.groupby(['rol','jugador']).size().reset_index(name='n').sort_values(['jugador','n'],ascending=[True,False]).drop_duplicates('jugador'); latest=al.sort_values('jornada').drop_duplicates('jugador',keep='last')[['jugador','dorsal']]; rc=rc.merge(latest,on='jugador',how='left'); rc['prob']=rc.jugador.map(prob).fillna(0)
    try: nums=[int(x) for x in main_form.split('-') if x.isdigit()]; outf=nums[1:] if nums and nums[0]==1 else nums
    except Exception: outf=[4,3,3]
    if len(outf)!=3: outf=[4,3,3]
    needs={'POR':1,'DEF':outf[0],'MED':outf[1],'ATA':outf[2]}; chosen=[]
    for role,n in needs.items():
        sub=rc[rc.rol==role].sort_values(['n','prob'],ascending=[False,False]).head(n)
        for _,r in sub.iterrows(): chosen.append({'role':role,'name':r.jugador,'dorsal':int(r.dorsal) if pd.notna(r.dorsal) else '', 'prob':float(r.prob)})
    return chosen

def generate(team,partidos,minutos,eventos,clasificacion,alineaciones,plantillas,logo_path=None,match_links=None):
    buf=BytesIO(); c=canvas.Canvas(buf,pagesize=A4); c.setTitle('Informe de rival · '+str(team)); c.setAuthor('Primer Toque C.F.')
    P=partidos[(partidos.local==team)|(partidos.visitante==team)].copy().sort_values('jornada')
    m=minutos[minutos.equipo==team].copy(); ev=eventos[eventos.equipo==team].copy(); a=alineaciones[alineaciones.equipo==team].copy(); roster=plantillas[plantillas.equipo==team].copy()
    matches=[]; form=[]
    for _,r in P.iterrows():
        gf,gc,opp=_team_score(r,team)
        if gf is None:continue
        j=int(r.jornada); f=r.sistema_local if r.local==team else r.sistema_visitante
        f=str(f) if pd.notna(f) and str(f)!='PENDIENTE' else '-'
        matches.append({'j':j,'gf':gf,'gc':gc,'opp':str(opp),'form':f})
        if f!='-':form.append(f)
    js=sorted(set(x['j'] for x in matches))
    gf=sum(x['gf'] for x in matches); gc=sum(x['gc'] for x in matches); n=len(matches)
    wins=sum(x['gf']>x['gc'] for x in matches); draws=sum(x['gf']==x['gc'] for x in matches); losses=n-wins-draws
    most=pd.Series(form).value_counts() if form else pd.Series(dtype=int); system=str(most.index[0]) if len(most) else '-'
    stand=clasificacion[clasificacion.equipo==team].sort_values('jornada')
    pos=f"{int(stand.iloc[-1].posicion)}º" if len(stand) and pd.notna(stand.iloc[-1].posicion) else '-'
    def text(x,y,s,size=8,col=navy,bold=False,maxwidth=None):
        s=str(s); font=BOLD if bold else FONT
        if maxwidth is not None:
            while pdfmetrics.stringWidth(s,font,size)>maxwidth and size>4.7: size-=.3
            if pdfmetrics.stringWidth(s,font,size)>maxwidth:
                while s and pdfmetrics.stringWidth(s+'…',font,size)>maxwidth:s=s[:-1]
                s+='…'
        c.setFont(font,size);c.setFillColor(col);c.drawString(x,y,s)
    def centered(x,y,s,size=8,col=navy,bold=False,maxwidth=None):
        s=str(s); font=BOLD if bold else FONT
        if maxwidth:
            while pdfmetrics.stringWidth(s,font,size)>maxwidth and size>4.5:size-=.3
            if pdfmetrics.stringWidth(s,font,size)>maxwidth:
                while s and pdfmetrics.stringWidth(s+'…',font,size)>maxwidth:s=s[:-1]
                s+='…'
        c.setFillColor(col);c.setFont(font,size);c.drawCentredString(x,y,s)
    def rect(x,y,w,h,fill,stroke=None,r=0):
        c.setFillColor(fill);c.setStrokeColor(stroke or fill);c.roundRect(x,y,w,h,r,fill=1,stroke=bool(stroke))
    def line(x,y,x2,y2,col=border,width=.5):c.setStrokeColor(col);c.setLineWidth(width);c.line(x,y,x2,y2)
    def heading(y,name):text(M,y,name,12,navy,True);return y-20
    def sub(y,name):text(M,y,name,8.6,blue,True);return y-14
    pages=4
    def header(number):
        rect(0,H-66,W,66,navy)
        text(M,H-34,'INFORME DE RIVAL  ·  '+_short_team(team).upper(),14,HexColor('#FFFFFF'),True,maxwidth=IW)
        text(M,H-51,'Lliga Comunitat Juvenil · Nord · Temporada 2026/2027',8,HexColor('#C9D9EB'))
        line(M,30,W-M,30);text(M,17,'Primer Toque C.F.  |  Informe de rival',7,muted)
        text(W-M-68,17,f'Página {number}',7,muted)
    def crest(path,x,y,w,h):
        try:
            if not path or not Path(path).is_file():return
            im=ImageReader(str(path));iw,ih=im.getSize();scale=min(w/iw,h/ih)
            nw=iw*scale;nh=ih*scale;c.drawImage(im,x+(w-nw)/2,y+(h-nh)/2,nw,nh,mask='auto')
        except Exception:pass
    def page():c.showPage()
    # PAGE 1: headline -> last five fixtures with official crests -> profile & XI.
    header(1);y=H-89
    cards=[(str(n),'PARTIDOS'),(f'{wins}-{draws}-{losses}','V-E-D'),(f'{gf} - {gc}','GOLES'),(pos,'CLASIFICACIÓN'),(system,'SISTEMA')]
    gap=7;cw=(IW-4*gap)/5
    for i,(value,label) in enumerate(cards):
        x=M+i*(cw+gap);rect(x,y-58,cw,58,pale,r=6);text(x+8,y-29,value,12.4,navy,True,maxwidth=cw-13);text(x+8,y-46,label,6.4,muted,True)
    y-=72;y=sub(y,'Últimos 5 partidos')
    recent=matches[-5:]
    for i,r in enumerate(recent):
        ww=(IW-4*6)/5;xx=M+i*(ww+6);bottom=y-85;win=r['gf']>r['gc'];tie=r['gf']==r['gc']
        bg=HexColor('#EFF9F2') if win else (grey if tie else HexColor('#FFF1F2'))
        co=green if win else (muted if tie else HexColor('#EC7380'))
        rect(xx,bottom,ww,85,bg,r=5);rect(xx+6,bottom+62,26,17,co,r=3)
        text(xx+10,bottom+67,'J'+str(r['j']),7,navy,True)
        crest(_opponent_badge_path(r['opp']),xx+ww/2-14,bottom+40,28,26)
        centered(xx+ww/2,bottom+26,f"{r['gf']}-{r['gc']}",12,navy,True)
        centered(xx+ww/2,bottom+11,_short_team(r['opp']),5.7,navy,maxwidth=ww-5)
    y-=102;y=heading(y,'1. Perfil competitivo');y=sub(y,'Posible XI  |  '+system)
    fieldtop=y; fh=206;fx=M+23;fw=IW-46;rect(fx,y-fh,fw,fh,HexColor('#E8F6EE'),HexColor('#7AC79D'),7)
    line(fx+fw/2,y-8,fx+fw/2,y-fh+8,HexColor('#C1E5D0'))
    c.setStrokeColor(HexColor('#C1E5D0'));c.circle(fx+fw/2,y-fh/2,30,stroke=1,fill=0)
    xi=_build_selected_xi(a,m,js,system) if js else []
    role_x={'POR':.075,'DEF':.29,'MED':.55,'ATA':.81}
    for role in ('POR','DEF','MED','ATA'):
        ppl=[r for r in xi if r['role']==role];count=len(ppl)
        for i,p in enumerate(ppl):
            px=role_x[role];py=(i+1)/(count+1) if role!='POR' else .5
            xx=fx+px*fw; yy=y-py*fh
            c.setFillColor(navy);c.circle(xx,yy+8,10,fill=1,stroke=0)
            centered(xx,yy+5,str(p['dorsal']),7,HexColor('#FFFFFF'),True)
            centered(xx,yy-8,str(p['name']).split()[0],6,navy,True,maxwidth=67)
            centered(xx,yy-18,f"{p['prob']:.0f}%",5.5)
    y-=fh+19;rect(M,y-50,IW,50,pale,r=5)
    text(M+11,y-16,'SISTEMA MÁS UTILIZADO',7,muted,True)
    text(M+11,y-36,f'{system} · {int(most.iloc[0]) if len(most) else 0} jornadas ({(most.iloc[0]/len(form)*100) if len(form) else 0:.0f}%)',9,navy,True)
    text(M+290,y-16,'PROMEDIOS',7,muted,True)
    text(M+290,y-36,f'{gf/max(n,1):.2f} GF/partido   ·   {gc/max(n,1):.2f} GC/partido',8,navy,True)
    page()
    # PAGE 2: minutes heat map (same scale and 5 columns), goalscorers.
    header(2);y=H-91;y=heading(y,'2. Jugadores y carga competitiva')
    text(M,y,'Minutos por jornada · escala de colores de la aplicación',8,muted);y-=20
    js_m=sorted(set(int(j) for j in m.jornada.dropna().unique())) if len(m) else js
    display_js=js_m[-5:]  # últimos cinco encuentros visibles, sin cambiar el resto de datos.
    mins=m.copy();mins['minutos']=pd.to_numeric(mins.minutos,errors='coerce').fillna(0)
    totals=mins.groupby('jugador').minutos.sum().to_dict() if len(mins) else {}
    pjs=mins[mins.minutos>0].groupby('jugador').jornada.nunique().to_dict() if len(mins) else {}
    tits=mins.groupby('jugador').titular.sum().to_dict() if len(mins) else {}
    
    _goal_ev = ev[ev.tipo.isin(['gol','penalti_gol'])].copy()
    if len(_goal_ev):
        _own = _goal_ev.get('detalle', pd.Series(index=_goal_ev.index, dtype=object)).astype(str).str.contains('propia', case=False, na=False)
        _ph = _goal_ev.get('jugador', pd.Series(index=_goal_ev.index, dtype=object)).astype(str).str.strip().isin(['', 'G.P.', 'GP', 'Autogol', 'Autogol rival', 'nan', 'None'])
        _goal_ev = _goal_ev[~_own & ~_ph]
    sgs=_goal_ev.jugador.value_counts().to_dict()
    labels={}
    for _,r in roster.iterrows():
        nm=str(r.jugador)
        if pd.notna(r.dorsal):
            try: d=str(int(r.dorsal))
            except: d=str(r.dorsal)
            if d not in labels.get(nm,[]): labels.setdefault(nm,[]).append(d)
    players=sorted(set(totals)|set(roster.jugador.dropna().astype(str)),key=lambda p:(-totals.get(p,0),p))
    # Cabe más de 30 jugadores sin cortar tablas; en clubes grandes se reducen filas.
    rowh=min(21,max(13,515/max(1,len(players))))
    cols=['#','Jugador','PJ','Tit.','Min','G']+[f'J{j}' for j in display_js]
    base=[26,178,25,25,36,23];cw=(IW-sum(base))/max(1,len(display_js));ws=base+[cw]*len(display_js)
    xs=[M]
    for w in ws:xs.append(xs[-1]+w)
    rect(M,y-22,IW,22,navy)
    for i,l in enumerate(cols):text(xs[i]+3,y-15,l,6.7,HexColor('#FFFFFF'),True)
    y-=22
    for idx,p in enumerate(players):
        lower=y-rowh;rect(M,lower,IW,rowh,HexColor('#FFFFFF') if idx%2==0 else pale)
        name_values=['/'.join(labels.get(p,[])),p,int(pjs.get(p,0)),int(tits.get(p,0)),int(totals.get(p,0)),int(sgs.get(p,0))]
        for k,v in enumerate(name_values): text(xs[k]+3,lower+rowh*.33,v,6.0 if k==1 else 6.7,navy,k in (4,5),maxwidth=ws[k]-5)
        for k,j in enumerate(display_js):
            psub=mins[(mins.jugador==p)&(mins.jornada==j)];v=int(psub.minutos.sum()) if len(psub) else None
            bg=grey if v is None else (red if v<=20 else orange if v<=45 else yellow if v<=60 else mint if v<80 else green)
            rect(xs[k+6]+1,lower+1,ws[k+6]-2,rowh-2,bg,r=2)
            centered(xs[k+6]+ws[k+6]/2,lower+rowh*.33,'—' if v is None else str(v),6.7,navy,True)
        y-=rowh
    y-=15;text(M,y,'Colores:',7,navy,True)
    lg=[('80–90',green),('61–79',mint),('46–60',yellow),('21–45',orange),('0–20',red),('Sin registro',grey)]
    x=M+50
    for t,col in lg:
        rect(x,y-2,9,9,col);text(x+11,y,t,6,muted);x+=72 if t!='Sin registro' else 85
    y-=28;y=sub(y,'Goleadores registrados')
    scorers=sorted(sgs.items(),key=lambda z:(-z[1],z[0]));columns=3
    for k,(name,g) in enumerate(scorers[:15]):
        col=k%columns;row=k//columns; xx=M+col*IW/3; yy=y-row*23
        text(xx,yy,str(name).split()[0]+' '+str(name).split()[1] if len(str(name).split())>1 else name,6.7,navy,maxwidth=93)
        rect(xx+100,yy-2,min(44,g*15),8,green,r=3);text(xx+147,yy,str(g),7,navy,True)
    page()
    # PAGE 3: goals by minute, situation matrices, goal difference.
    header(3);y=H-91;y=heading(y,'3. Goles y momentos del partido');y=sub(y,'Distribución de goles por minuto')
    periods=['0–15’','16–30’','31–45+’','46–60’','61–75’','76–90+’'];gfslots=[0]*6;gcslots=[0]*6
    for _,r in ev.iterrows():
        s=_goal_slot(r.minuto)
        if s is None:continue
        if r.tipo in ('gol','penalti_gol'):gfslots[s]+=1
        if r.tipo in ('gol_contra','penalti_contra_gol'):gcslots[s]+=1
    ht=147;bottom=y-ht+24;maxval=max(1,*gfslots,*gcslots);barh=ht-50
    for k,p in enumerate(periods):
        xx=M+22+k*(IW-44)/6;a=gfslots[k]/maxval*barh;b=gcslots[k]/maxval*barh
        if a:rect(xx,bottom,21,a,green)
        if b:rect(xx+25,bottom,21,b,HexColor('#EF6171'))
        text(xx+6,bottom+a+5,gfslots[k],7,navy,True);text(xx+29,bottom+b+5,gcslots[k],7,navy,True)
        text(xx-5,bottom-16,p,7,muted)
    text(W-M-150,y+10,'■ A favor',7,green,True);text(W-M-76,y+10,'■ En contra',7,HexColor('#EF6171'),True)
    y=bottom-43;meaning=_goal_meanings(P,ev,team)
    categories=['Apertura de marcador','Victoria (1-0)','Ampliar ventaja','Ponerse por delante','Remontada','Igualar marcador','Reducir distancia']
    for side,title in [('favor','Tipos de gol - a favor'),('contra','Tipos de gol - en contra')]:
        y=sub(y,title);rect(M,y-18,IW,18,navy);text(M+5,y-12,'Situación del gol',6.7,HexColor('#FFFFFF'),True)
        for j,p in enumerate(periods):text(M+213+j*52,y-12,p,6.1,HexColor('#FFFFFF'),True)
        y-=18
        for i,cat in enumerate(categories):
            rect(M,y-17,IW,17,HexColor('#FFFFFF') if i%2==0 else pale)
            text(M+5,y-12,cat,6.8)
            for j in range(6):
                val=int(((meaning.lado==side)&(meaning.meaning==cat)&(meaning.slot==j)).sum()) if not meaning.empty else 0
                if val:
                    rect(M+214+j*52,y-15,43,13,HexColor('#C9F2DC') if side=='favor' else HexColor('#F9DADD'),r=2)
                    text(M+233+j*52,y-12,val,7,navy,True)
            y-=17
        y-=16
    y=heading(y,'4. Tendencia de resultados');y=sub(y,'Diferencia por jornada (barras) y acumulada (línea)')
    recent=matches[-8:]; nplot=len(recent)
    if nplot:
        deltas=[z['gf']-z['gc'] for z in recent];running=[];running_total=sum(z['gf']-z['gc'] for z in matches[:-nplot])
        for d in deltas:running_total+=d;running.append(running_total)
        zero=y-36;wid=(IW-100)/max(1,nplot-1);factor=min(9,65/max(1,max(abs(z) for z in running+deltas)))
        line(M+22,zero,W-M-12,zero)
        coords=[]
        for i,(r,d,acc) in enumerate(zip(recent,deltas,running)):
            xx=M+52+i*wid;bh=abs(d)*factor
            rect(xx-13,zero-bh if d<0 else zero,26,max(1,bh),HexColor('#DE5269') if d<0 else HexColor('#21A675'),r=3)
            centered(xx,zero+bh+5 if d>=0 else zero-bh-11,f'{d:+d}',6,navy,True)
            cy=zero-12+acc*factor;coords.append((xx,cy))
            centered(xx,y-113,'J'+str(r['j'])+' '+_short_team(r['opp']),5.3,maxwidth=wid-3)
        c.setStrokeColor(HexColor('#EFA521'));c.setLineWidth(2)
        for u,v in zip(coords,coords[1:]):c.line(u[0],u[1],v[0],v[1])
        for (xx,yy),acc in zip(coords,running):
            c.setFillColor(HexColor('#EFA521'));c.circle(xx,yy,7,fill=1,stroke=0)
            centered(xx,yy-2,str(acc),5.6,HexColor('#FFFFFF'),True)
    page()
    # PAGE 4: penalties, evolution, clickable links.
    header(4);y=H-92;y=heading(y,'5. Penaltis')
    pen=ev[ev.tipo.isin(['penalti_gol','penalti_fallado','penalti_contra_gol','penalti_contra_fallado'])].sort_values(['jornada','minuto'])
    widths=[79,79,257,IW-415]; headers=['Jornada','Minuto','Lanzador','Resultado']
    for i,row in enumerate([headers]+[(f'J{int(r.jornada)}',f"{int(r.minuto)}’",str(r.jugador),'Gol' if 'gol' in r.tipo else 'Fallado') for _,r in pen.iterrows()]):
        x=M;rh=24 if i else 21;rect(M,y-rh,IW,rh,navy if not i else (pale if i%2==0 else HexColor('#FFFFFF')))
        for val,w in zip(row,widths):text(x+6,y-rh*.67,val,7.5 if i else 7,HexColor('#FFFFFF') if not i else navy,i==0,maxwidth=w-10);x+=w
        y-=rh
    if pen.empty: text(M+8,y-16,'No se han registrado penaltis.',7,muted);y-=23
    y-=30;y=heading(y,'6. Evolución de la clasificación');y=sub(y,'Posición tras cada jornada · una posición menor es mejor')
    standings=stand[pd.to_numeric(stand.jornada,errors='coerce').notna()].sort_values('jornada').tail(8)
    values=[]
    for _,r in standings.iterrows():
        if pd.notna(r.posicion): values.append((int(r.jornada),int(r.posicion)))
    ctop=y-15;cbottom=y-170
    for rank in [1,4,8,12,16]:
        yy=ctop-(rank-1)*(ctop-cbottom)/15;line(M+30,yy,W-M-15,yy);text(M+5,yy-3,str(rank)+'º',7,muted)
    points=[]
    for i,(j,p) in enumerate(values):
        xx=M+52+i*(IW-103)/max(1,len(values)-1)
        yy=ctop-(p-1)*(ctop-cbottom)/15;points.append((xx,yy))
    c.setStrokeColor(HexColor('#2475B8'));c.setLineWidth(2.5)
    for u,v in zip(points,points[1:]):c.line(u[0],u[1],v[0],v[1])
    for (xx,yy),(j,p) in zip(points,values):
        c.setFillColor(HexColor('#2475B8'));c.circle(xx,yy,5,fill=1,stroke=0)
        centered(xx,yy-17,str(p)+'º',7,navy,True);centered(xx,cbottom-12,'J'+str(j),7)
    y=cbottom-46;y=heading(y,'7. Vídeos de los partidos')
    text(M,y,'Pulsa «VER PARTIDO» para abrir el vídeo disponible.',8,muted);y-=14
    show=matches[-6:]  # URLs de los seis últimos para no recortar la hoja.
    for i,r in enumerate(show):
        yy=y-36;rect(M,yy,IW,31,pale if i%2 else HexColor('#FFFFFF'),border,3)
        text(M+10,yy+10,'J'+str(r['j']),8,navy,True)
        text(M+55,yy+10,_short_team(r['opp']),7.5,navy,maxwidth=224)
        text(M+307,yy+10,f"{r['gf']}-{r['gc']}",8.5,navy,True)
        u=(match_links or {}).get((str(team),int(r['j'])))
        bx=W-M-105
        if u:
            rect(bx,yy+5,99,22,blue,r=4);text(bx+10,yy+12,'VER PARTIDO  ›',7.5,HexColor('#FFFFFF'),True)
            c.linkURL(str(u),(bx,yy+5,bx+99,yy+27),relative=0,thickness=0)
        else:text(bx+5,yy+12,'Sin vídeo disponible',7,muted)
        y-=37
    c.save();return buf.getvalue()
