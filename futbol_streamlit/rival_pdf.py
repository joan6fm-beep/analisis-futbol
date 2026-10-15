from __future__ import annotations

from io import BytesIO
from pathlib import Path
from datetime import datetime
import math
import re

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
    KeepTogether, Flowable, HRFlowable, LongTable
)
from reportlab.pdfbase.pdfmetrics import stringWidth

NAVY = HexColor('#0B3766')
NAVY_DARK = HexColor('#082F5B')
BLUE = HexColor('#1D63D8')
BLUE_SOFT = HexColor('#EAF2FF')
ORANGE = HexColor('#F59E0B')
ORANGE_SOFT = HexColor('#FFF3D6')
GREEN = HexColor('#20A46B')
GREEN_SOFT = HexColor('#E6F7EF')
RED = HexColor('#DF5263')
RED_SOFT = HexColor('#FDEBED')
GREY = HexColor('#64748B')
GREY2 = HexColor('#94A3B8')
LIGHT = HexColor('#F4F7FB')
BORDER = HexColor('#D9E2EC')
WHITE = colors.white
TEXT = HexColor('#172033')


def _short_team(name: str) -> str:
    out = str(name or '')
    for suffix in [" 'A'", " 'B'", " 'C'", " 'D'"]:
        out = out.replace(suffix, '')
    return out


def _clean_filename(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9À-ÿ_-]+", "_", _short_team(name)).strip('_')
    return s or 'Rival'


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


class KPIGrid(Flowable):
    def __init__(self, items, width=170*mm, cols=4, box_h=22*mm):
        Flowable.__init__(self)
        self.items = items; self.width = width; self.cols = cols; self.box_h = box_h
        self.rows = math.ceil(len(items)/cols); self.height = self.rows*box_h + max(0,self.rows-1)*3*mm
    def draw(self):
        c=self.canv; gap=3*mm; box_w=(self.width-gap*(self.cols-1))/self.cols
        for i,(value,label,sub) in enumerate(self.items):
            row=i//self.cols; col=i%self.cols
            x=col*(box_w+gap); y=self.height-(row+1)*self.box_h-row*gap
            c.setFillColor(LIGHT); c.setStrokeColor(BORDER); c.roundRect(x,y,box_w,self.box_h,4*mm,fill=1,stroke=1)
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',15); c.drawString(x+4*mm,y+self.box_h-8*mm,str(value))
            c.setFillColor(TEXT); c.setFont('Helvetica-Bold',7.8); c.drawString(x+4*mm,y+self.box_h-13*mm,str(label)[:35])
            c.setFillColor(GREY); c.setFont('Helvetica',6.8); c.drawString(x+4*mm,y+4*mm,str(sub)[:48])


class MatchStrip(Flowable):
    def __init__(self, rows, width=170*mm):
        Flowable.__init__(self); self.rows=rows; self.width=width; self.height=26*mm
    def draw(self):
        c=self.canv; n=max(1,len(self.rows)); gap=2*mm; bw=(self.width-gap*(n-1))/n
        for i,r in enumerate(self.rows):
            x=i*(bw+gap); y=0
            outcome = 'V' if r['gf']>r['gc'] else ('E' if r['gf']==r['gc'] else 'D')
            col = GREEN if outcome=='V' else (GREY2 if outcome=='E' else RED)
            c.setFillColor(WHITE); c.setStrokeColor(BORDER); c.roundRect(x,y,bw,self.height,3*mm,fill=1,stroke=1)
            c.setFillColor(col); c.roundRect(x,y+self.height-7*mm,bw,7*mm,3*mm,fill=1,stroke=0)
            c.setFillColor(WHITE); c.setFont('Helvetica-Bold',7); c.drawCentredString(x+bw/2,y+self.height-4.8*mm,f"J{r['j']} · {outcome}")
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',12); c.drawCentredString(x+bw/2,y+10*mm,f"{r['gf']} - {r['gc']}")
            c.setFillColor(GREY); c.setFont('Helvetica',5.8)
            opp=_short_team(r['opp'])
            if len(opp)>18: opp=opp[:17]+'…'
            c.drawCentredString(x+bw/2,y+5*mm,opp)
            c.setFont('Helvetica',5.2); c.drawCentredString(x+bw/2,y+2*mm,r.get('form','') or '-')


class BarChartFlow(Flowable):
    def __init__(self, labels, values, title, width=170*mm, height=62*mm, positive=True, suffix=''):
        Flowable.__init__(self); self.labels=labels; self.values=values; self.title=title; self.width=width; self.height=height; self.positive=positive; self.suffix=suffix
    def draw(self):
        c=self.canv; c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',10); c.drawString(0,self.height-5*mm,self.title)
        left=33*mm; top=self.height-12*mm; bottom=4*mm; h=top-bottom
        mx=max([1]+[abs(float(v)) for v in self.values]); row_h=h/max(1,len(self.values)); bar_max=self.width-left-12*mm
        for i,(lab,val) in enumerate(zip(self.labels,self.values)):
            yy=top-(i+0.72)*row_h
            c.setFillColor(TEXT); c.setFont('Helvetica',6.5); c.drawRightString(left-2*mm,yy,lab[:30])
            bw=max(1,bar_max*float(val)/mx)
            c.setFillColor(ORANGE if self.positive else RED); c.roundRect(left,yy-2.2*mm,bw,4.3*mm,1.5*mm,fill=1,stroke=0)
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',6.5); c.drawString(left+bw+2*mm,yy-0.7*mm,f"{val}{self.suffix}")


class GoalSlotsFlow(Flowable):
    def __init__(self, gf_slots, gc_slots, width=170*mm, height=58*mm):
        Flowable.__init__(self); self.gf=gf_slots; self.gc=gc_slots; self.width=width; self.height=height
    def draw(self):
        c=self.canv; c.setFont('Helvetica-Bold',10); c.setFillColor(NAVY_DARK); c.drawString(0,self.height-5*mm,'Distribución de goles por minuto')
        labels=["0-15'","16-30'","31-45+'","46-60'","61-75'","76-90+'"]
        x0=10*mm; y0=9*mm; chart_w=self.width-15*mm; chart_h=self.height-22*mm; group=chart_w/6
        mx=max([1]+self.gf+self.gc)
        c.setStrokeColor(BORDER); c.line(x0,y0,x0+chart_w,y0)
        for i,lab in enumerate(labels):
            x=x0+i*group; bw=group*0.28
            hg=chart_h*self.gf[i]/mx; hc=chart_h*self.gc[i]/mx
            c.setFillColor(ORANGE); c.roundRect(x+group*.15,y0,bw,max(1,hg),1*mm,fill=1,stroke=0)
            c.setFillColor(BLUE); c.roundRect(x+group*.52,y0,bw,max(1,hc),1*mm,fill=1,stroke=0)
            c.setFillColor(GREY); c.setFont('Helvetica',5.7); c.drawCentredString(x+group*.5,y0-4*mm,lab)
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',6); c.drawCentredString(x+group*.15+bw/2,y0+hg+2*mm,str(self.gf[i]))
            c.drawCentredString(x+group*.52+bw/2,y0+hc+2*mm,str(self.gc[i]))
        c.setFont('Helvetica',6.5); c.setFillColor(ORANGE); c.drawString(self.width-46*mm,self.height-5*mm,'A favor')
        c.setFillColor(BLUE); c.drawString(self.width-25*mm,self.height-5*mm,'En contra')


class GoalDiffFlow(Flowable):
    def __init__(self, rows, width=170*mm, height=67*mm):
        Flowable.__init__(self); self.rows=rows; self.width=width; self.height=height
    def draw(self):
        c=self.canv; c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',10); c.drawString(0,self.height-5*mm,'Diferencia de goles y acumulado')
        if not self.rows: return
        x0=10*mm; ymid=28*mm; chart_w=self.width-18*mm; max_abs=max(2,max(abs(r['diff']) for r in self.rows),max(abs(r['cum']) for r in self.rows)); scale=17*mm/max_abs
        step=chart_w/len(self.rows); pts=[]
        c.setStrokeColor(BORDER); c.line(x0,ymid,x0+chart_w,ymid)
        for i,r in enumerate(self.rows):
            xc=x0+(i+.5)*step; d=r['diff']; bh=abs(d)*scale
            c.setFillColor(GREEN if d>0 else (RED if d<0 else GREY2)); c.roundRect(xc-step*.22, ymid if d>=0 else ymid-bh, step*.44, max(1,bh),1.5*mm,fill=1,stroke=0)
            c.setFillColor(TEXT); c.setFont('Helvetica-Bold',6); c.drawCentredString(xc,ymid+(bh+2*mm if d>=0 else -bh-4*mm),f"{d:+d}")
            cy=ymid+r['cum']*scale; pts.append((xc,cy))
            c.setFillColor(GREY); c.setFont('Helvetica',5.4); c.drawCentredString(xc,4*mm,f"J{r['j']} {_short_team(r['opp'])[:9]}")
        c.setStrokeColor(ORANGE); c.setLineWidth(2)
        for a,b in zip(pts,pts[1:]): c.line(a[0],a[1],b[0],b[1])
        for (xc,cy),r in zip(pts,self.rows):
            c.setFillColor(ORANGE); c.circle(xc,cy,2.2*mm,fill=1,stroke=0); c.setFillColor(WHITE); c.setFont('Helvetica-Bold',5); c.drawCentredString(xc,cy-1.5,f"{r['cum']:+d}")


class BubbleMatrixFlow(Flowable):
    def __init__(self, records, side='favor', width=170*mm, height=79*mm):
        Flowable.__init__(self); self.records=records; self.side=side; self.width=width; self.height=height
    def draw(self):
        c=self.canv; against=self.side=='contra'; title='Tipos de gol - en contra' if against else 'Tipos de gol - a favor'
        c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',9.5); c.drawString(0,self.height-5*mm,title)
        cats=['Apertura de marcador','Victoria (1-0)','Ampliar ventaja','Ponerse por delante','Remontada','Igualar marcador','Reducir distancia']
        labs=["0-15'","16-30'","31-45+'","46-60'","61-75'","76-90+'"]
        left=36*mm; top=self.height-12*mm; bottom=8*mm; grid_w=self.width-left-4*mm; grid_h=top-bottom; cw=grid_w/6; rh=grid_h/7
        dd=self.records[self.records.lado==self.side] if not self.records.empty else pd.DataFrame()
        mx=max(1,int(dd.groupby(['meaning','slot']).size().max()) if not dd.empty else 1)
        for i,cat in enumerate(cats):
            yy=top-(i+.5)*rh; c.setFillColor(GREY); c.setFont('Helvetica',5.4); c.drawRightString(left-2*mm,yy-1.5,cat)
            for s in range(6):
                n=int(((dd.meaning==cat)&(dd.slot==s)).sum()) if not dd.empty else 0; xx=left+(s+.5)*cw
                if n:
                    rr=(2.6+2.0*math.sqrt(n/mx))*mm; c.setFillColor(RED if against else GREEN); c.circle(xx,yy,rr,fill=1,stroke=0); c.setFillColor(WHITE); c.setFont('Helvetica-Bold',5.5); c.drawCentredString(xx,yy-1.6,str(n))
                else:
                    c.setFillColor(HexColor('#DCE5EF')); c.circle(xx,yy,0.7*mm,fill=1,stroke=0)
        for s,lab in enumerate(labs): c.setFillColor(GREY); c.setFont('Helvetica',5.3); c.drawCentredString(left+(s+.5)*cw,2*mm,lab)


class PitchXIFlow(Flowable):
    def __init__(self, players, system, width=170*mm, height=73*mm):
        Flowable.__init__(self); self.players=players; self.system=system; self.width=width; self.height=height
    def draw(self):
        c=self.canv; c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',10); c.drawString(0,self.height-4*mm,f'Posible XI · {self.system}')
        x=9*mm; y=4*mm; w=self.width-18*mm; h=self.height-14*mm
        c.setFillColor(HexColor('#E9F7EF')); c.setStrokeColor(HexColor('#6BBE8D')); c.roundRect(x,y,w,h,3*mm,fill=1,stroke=1)
        c.setStrokeColor(WHITE); c.setLineWidth(1); c.line(x+w/2,y,x+w/2,y+h); c.circle(x+w/2,y+h/2,8*mm,fill=0,stroke=1)
        role_x={'POR':x+w*.08,'DEF':x+w*.28,'MED':x+w*.52,'ATA':x+w*.79}
        role_lists={r:[p for p in self.players if p['role']==r] for r in role_x}
        for role,plist in role_lists.items():
            n=len(plist)
            for i,p in enumerate(plist):
                yy=y+h*(.18 if n==1 else .14+i*(.72/max(1,n-1)))
                xx=role_x[role]
                c.setFillColor(NAVY_DARK); c.circle(xx,yy,4.2*mm,fill=1,stroke=0); c.setFillColor(WHITE); c.setFont('Helvetica-Bold',6); c.drawCentredString(xx,yy-1.7,str(p.get('dorsal','')))
                name=str(p.get('name','')).split(' ')[0][:10]; c.setFillColor(TEXT); c.setFont('Helvetica-Bold',5); c.drawCentredString(xx,yy-6.5*mm,name)
                c.setFillColor(GREY); c.setFont('Helvetica',4.8); c.drawCentredString(xx,yy-9.2*mm,f"{p.get('prob',0):.0f}%")


def _styles():
    ss=getSampleStyleSheet()
    return {
        'h1': ParagraphStyle('h1', parent=ss['Heading1'], fontName='Helvetica-Bold', fontSize=22, leading=25, textColor=NAVY_DARK, spaceAfter=5*mm),
        'h2': ParagraphStyle('h2', parent=ss['Heading2'], fontName='Helvetica-Bold', fontSize=13, leading=15, textColor=NAVY_DARK, spaceBefore=3*mm, spaceAfter=3*mm),
        'body': ParagraphStyle('body', parent=ss['BodyText'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=TEXT),
        'small': ParagraphStyle('small', parent=ss['BodyText'], fontName='Helvetica', fontSize=6.6, leading=8.3, textColor=GREY),
        'white': ParagraphStyle('white', parent=ss['BodyText'], fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=WHITE),
        'center': ParagraphStyle('center', parent=ss['BodyText'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=8, textColor=TEXT),
    }


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER); canvas.line(20*mm,12*mm,A4[0]-20*mm,12*mm)
    canvas.setFillColor(GREY); canvas.setFont('Helvetica',6.5)
    canvas.drawString(20*mm,7*mm,'Primer Toque C.F. · Informe de rival · Temporada 2026/2027')
    canvas.drawRightString(A4[0]-20*mm,7*mm,f'Página {doc.page}')
    canvas.restoreState()


def _table(data, widths, header=True, font=6.5, row_bg=None):
    t=LongTable(data, colWidths=widths, repeatRows=1 if header else 0, hAlign='LEFT')
    styles=[('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),0.35,BORDER),('FONTNAME',(0,0),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),font),('TEXTCOLOR',(0,0),(-1,-1),TEXT),('TOPPADDING',(0,0),(-1,-1),2.4*mm),('BOTTOMPADDING',(0,0),(-1,-1),2.4*mm)]
    if header:
        styles += [('BACKGROUND',(0,0),(-1,0),NAVY_DARK),('TEXTCOLOR',(0,0),(-1,0),WHITE),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')]
    for i in range(1 if header else 0,len(data)):
        if i%2==0: styles.append(('BACKGROUND',(0,i),(-1,i),LIGHT))
    t.setStyle(TableStyle(styles)); return t


def build_rival_pdf(team: str, partidos: pd.DataFrame, minutos: pd.DataFrame, eventos: pd.DataFrame,
                    clasificacion: pd.DataFrame, alineaciones: pd.DataFrame, plantillas: pd.DataFrame,
                    logo_path: str | Path | None = None, match_links: dict | None = None) -> bytes:
    """Genera un dossier PDF estático del rival seleccionado con los datos completos disponibles."""
    styles=_styles(); buf=BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=16*mm,bottomMargin=17*mm,title=f'Informe rival - {_short_team(team)}',author='Primer Toque C.F.')
    story=[]; avail=174*mm

    part=partidos[(partidos.local==team)|(partidos.visitante==team)].copy().sort_values('jornada')
    mdf=minutos[minutos.equipo==team].copy(); ev=eventos[eventos.equipo==team].copy(); al=alineaciones[alineaciones.equipo==team].copy(); roster=plantillas[plantillas.equipo==team].copy()
    scope_js=sorted(part.jornada.dropna().astype(int).unique().tolist())
    known=[]; match_rows=[]; formations=[]
    for _,r in part.iterrows():
        gf,gc,opp=_team_score(r,team)
        form=r.sistema_local if r.local==team else r.sistema_visitante
        if pd.notna(form) and str(form).strip() and str(form)!='PENDIENTE': formations.append((int(r.jornada),str(form)))
        if gf is not None:
            known.append((gf,gc)); match_rows.append({'j':int(r.jornada),'gf':gf,'gc':gc,'opp':opp,'form':str(form) if pd.notna(form) else '-'})
    V=sum(a>b for a,b in known); E=sum(a==b for a,b in known); D=sum(a<b for a,b in known); GF=sum(a for a,b in known); GC=sum(b for a,b in known)
    stand=clasificacion[clasificacion.equipo==team].sort_values('jornada').tail(1); pos='-'; pts='-'
    if not stand.empty:
        try: pos=f"{int(stand.iloc[0].posicion)}º"
        except: pass
        try: pts=str(int(float(stand.iloc[0].puntos)))
        except: pass
    vc=pd.Series([f for _,f in formations]).value_counts() if formations else pd.Series(dtype=int); main_form=vc.index[0] if len(vc) else '-'; main_pct=(vc.iloc[0]/len(formations)*100) if len(vc) else 0

    # Cover/header
    head_data=[]
    if logo_path and Path(logo_path).exists():
        try: head_data.append(Image(str(logo_path),width=25*mm,height=25*mm,kind='proportional'))
        except: head_data.append(Paragraph('',styles['body']))
    else: head_data.append(Paragraph('',styles['body']))
    title=Paragraph(f"<font color='#F59E0B'>INFORME DE RIVAL</font><br/><font size='20'>{_short_team(team)}</font><br/><font size='8' color='#64748B'>Lliga Comunitat Juvenil · Nord · Temporada 2026/2027</font>",styles['h1'])
    ht=Table([[head_data[0],title]],colWidths=[30*mm,144*mm]); ht.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LINEBELOW',(0,0),(-1,-1),2,ORANGE),('BOTTOMPADDING',(0,0),(-1,-1),5*mm)])); story += [ht,Spacer(1,5*mm)]
    story.append(KPIGrid([(len(known),'PJ','Partidos analizados'),(f'{V}-{E}-{D}','V-E-D','Balance'),(f'{GF}-{GC}','GF-GC',f'Diferencia {GF-GC:+d}'),(pos,'Clasificación',f'{pts} puntos'),(main_form,'Sistema más usado',f'{main_pct:.0f}% de partidos'),(f'{GF/max(1,len(known)):.2f}','GF / partido','Promedio ofensivo'),(f'{GC/max(1,len(known)):.2f}','GC / partido','Promedio defensivo'),(sum(1 for a,b in known if b==0),'Porterías a cero','Partidos sin encajar')],width=avail,cols=4))
    story += [Spacer(1,4*mm),Paragraph('Resultados recientes',styles['h2']),MatchStrip(match_rows,width=avail),Spacer(1,3*mm)]
    gen=datetime.now().strftime('%d/%m/%Y %H:%M'); story.append(Paragraph(f"Informe generado automáticamente el {gen}. El PDF usa los datos disponibles en la app en el momento de la descarga.",styles['small']))

    # Page 2: match profile + formations + XI
    story += [PageBreak(),Paragraph('1. Perfil competitivo',styles['h1'])]
    form_data=[['Sistema','Uso','Jornadas']]
    if len(vc):
        for form,count in vc.items():
            js=', '.join(f'J{j}' for j,f in formations if f==form); form_data.append([form,f'{int(count)} ({count/len(formations)*100:.0f}%)',js])
    else: form_data.append(['-','-','Sin datos'])
    story += [Paragraph('Sistemas utilizados',styles['h2']),_table(form_data,[35*mm,35*mm,104*mm],font=7),Spacer(1,4*mm)]
    # probable XI
    njs=max(1,len(scope_js)); starts=mdf.groupby('jugador')['titular'].sum()/njs*100 if not mdf.empty else pd.Series(dtype=float); recent_js=scope_js[-2:]; recent=mdf[mdf.jornada.isin(recent_js)].groupby('jugador')['titular'].sum()/max(1,len(recent_js))*100 if recent_js and not mdf.empty else pd.Series(dtype=float); idx=starts.index.union(recent.index); prob=.6*starts.reindex(idx,fill_value=0)+.4*recent.reindex(idx,fill_value=0)
    if not al.empty:
        rc=al.groupby(['rol','jugador']).size().reset_index(name='n').sort_values(['jugador','n'],ascending=[True,False]).drop_duplicates('jugador'); latest=al.sort_values('jornada').drop_duplicates('jugador',keep='last')[['jugador','dorsal']]; rc=rc.merge(latest,on='jugador',how='left'); rc['prob']=rc.jugador.map(prob).fillna(0)
        try:
            nums=[int(x) for x in main_form.split('-') if x.isdigit()]; outf=nums[1:] if nums and nums[0]==1 else nums
        except: outf=[4,3,3]
        if len(outf)!=3: outf=[4,3,3]
        needs={'POR':1,'DEF':outf[0],'MED':outf[1],'ATA':outf[2]}; chosen=[]
        for role,n in needs.items():
            for _,r in rc[rc.rol==role].sort_values(['n','prob'],ascending=False).head(n).iterrows(): chosen.append({'role':role,'name':r.jugador,'dorsal':int(r.dorsal) if pd.notna(r.dorsal) else '', 'prob':float(r.prob)})
        story += [PitchXIFlow(chosen,main_form,width=avail),Spacer(1,4*mm)]
    # results detailed
    rd=[['J','Fecha','Cond.','Rival','Res.','Sistema','Campo']]
    for _,r in part.iterrows():
        gf,gc,opp=_team_score(r,team); cond='Casa' if r.local==team else 'Fuera'; rd.append([f"J{int(r.jornada)}",str(r.fecha),cond,_short_team(opp),'-' if gf is None else f'{gf}-{gc}',str(r.sistema_local if r.local==team else r.sistema_visitante),str(r.campo)[:32]])
    story += [Paragraph('Partidos analizados',styles['h2']),_table(rd,[10*mm,20*mm,16*mm,38*mm,14*mm,22*mm,54*mm],font=5.8)]

    # Page 3: players
    story += [PageBreak(),Paragraph('2. Jugadores y carga competitiva',styles['h1'])]
    player_names=sorted(set(roster.jugador.dropna().astype(str)) | set(mdf.jugador.dropna().astype(str)))
    ptab=[]
    goals=ev[ev.tipo.isin(['gol','penalti_gol'])].groupby('jugador').size(); yell=ev[ev.tipo=='amarilla'].groupby('jugador').size(); red=ev[ev.tipo.isin(['roja','doble_amarilla'])].groupby('jugador').size()
    for name in player_names:
        d=mdf[mdf.jugador==name]; mins=int(pd.to_numeric(d.minutos,errors='coerce').fillna(0).sum()); startsn=int(pd.to_numeric(d.titular,errors='coerce').fillna(0).sum()); pj=int(d[d.minutos>0].jornada.nunique()); dors=roster[roster.jugador==name].dorsal.dropna().tolist(); dorsal='/'.join(str(int(x)) for x in sorted(set(dors))) if dors else ''
        ptab.append([dorsal,name,pj,startsn,mins,int(goals.get(name,0)),int(yell.get(name,0)),int(red.get(name,0))])
    ptab=sorted(ptab,key=lambda x:(-x[4],x[1])); data=[['#','Jugador','PJ','Tit.','Min','G','TA','TR']]+ptab
    story.append(_table(data,[12*mm,73*mm,12*mm,13*mm,16*mm,11*mm,11*mm,11*mm],font=6.1))
    # scorers chart
    scorer=ev[ev.tipo.isin(['gol','penalti_gol'])].jugador.value_counts().head(10)
    if not scorer.empty:
        story += [Spacer(1,5*mm),BarChartFlow([str(x).split(' ')[0]+' '+(str(x).split(' ')[1] if len(str(x).split(' '))>1 else '') for x in scorer.index],[int(x) for x in scorer.values],'Goleadores registrados',width=avail,height=55*mm,positive=True)]

    # Page 4 goals
    story += [PageBreak(),Paragraph('3. Goles y momentos del partido',styles['h1'])]
    gfslots=[0]*6; gcslots=[0]*6
    for _,r in ev.iterrows():
        sl=_goal_slot(r.minuto)
        if sl is None: continue
        if r.tipo in ['gol','penalti_gol']: gfslots[sl]+=1
        elif r.tipo in ['gol_contra','penalti_contra_gol']: gcslots[sl]+=1
    story += [GoalSlotsFlow(gfslots,gcslots,width=avail),Spacer(1,4*mm)]
    meanings=_goal_meanings(part,ev,team)
    story += [BubbleMatrixFlow(meanings,'favor',width=avail),Spacer(1,2*mm),BubbleMatrixFlow(meanings,'contra',width=avail)]

    # Page 5 diff, events and discipline
    story += [PageBreak(),Paragraph('4. Tendencia de resultados y disciplina',styles['h1'])]
    diffs=[]; cum=0
    for r in match_rows:
        d=r['gf']-r['gc']; cum+=d; diffs.append({**r,'diff':d,'cum':cum})
    story += [GoalDiffFlow(diffs,width=avail),Spacer(1,5*mm)]
    disc=[]
    for _,r in ev[ev.tipo.isin(['amarilla','doble_amarilla','roja'])].sort_values(['jornada','minuto']).iterrows(): disc.append([f"J{int(r.jornada)}",f"{int(r.minuto)}'",str(r.tipo).replace('_',' ').title(),str(r.jugador),str(r.detalle or '')])
    if disc:
        story += [Paragraph('Disciplina',styles['h2']),_table([['J','Min','Evento','Jugador','Detalle']]+disc,[12*mm,13*mm,29*mm,62*mm,58*mm],font=5.8)]
    pen=[]
    for _,r in ev[ev.tipo.isin(['penalti_gol','penalti_fallado'])].sort_values(['jornada','minuto']).iterrows(): pen.append([f"J{int(r.jornada)}",f"{int(r.minuto)}'",str(r.jugador),'Gol' if r.tipo=='penalti_gol' else 'Fallado'])
    if pen: story += [Spacer(1,4*mm),Paragraph('Penaltis',styles['h2']),_table([['J','Min','Lanzador','Resultado']]+pen,[15*mm,20*mm,100*mm,39*mm],font=6.5)]

    # Page 6 classification evolution + video sources
    story += [PageBreak(),Paragraph('5. Evolución y fuentes de vídeo',styles['h1'])]
    evo=clasificacion[(clasificacion.equipo==team)&(pd.to_numeric(clasificacion.jornada,errors='coerce').notna())].copy().sort_values('jornada')
    if not evo.empty:
        e_data=[['Jornada','Posición','Puntos']]
        for _,r in evo.iterrows():
            try: p=int(float(r.puntos)) if pd.notna(r.puntos) else '-'
            except: p='-'
            e_data.append([f"J{int(r.jornada)}",f"{int(r.posicion)}º",p])
        story += [Paragraph('Evolución de la clasificación',styles['h2']),_table(e_data,[40*mm,60*mm,74*mm],font=7),Spacer(1,5*mm)]
    links=[]
    if match_links:
        for r in match_rows:
            u=match_links.get((str(team),int(r['j'])))
            if u: links.append([f"J{r['j']}",_short_team(r['opp']),u])
    if links:
        linkdata=[[Paragraph('<b>J</b>',styles['white']),Paragraph('<b>Partido</b>',styles['white']),Paragraph('<b>Vídeo</b>',styles['white'])]]
        for j,opp,u in links:
            linkdata.append([j,opp,Paragraph(f"<link href='{u}' color='#1D63D8'>Abrir vídeo del partido</link>",styles['body'])])
        story += [Paragraph('Vídeos disponibles',styles['h2']),_table(linkdata,[15*mm,65*mm,94*mm],font=6.3)]
    story += [Spacer(1,6*mm),Paragraph('<b>Nota para el cuerpo técnico.</b> Este dossier es una exportación estática del análisis del rival. Los elementos interactivos de la app (hover, filtros y enlaces dinámicos) se convierten en gráficos y tablas estáticas para poder compartir el informe por WhatsApp o correo.',styles['small'])]

    doc.build(story,onFirstPage=_footer,onLaterPages=_footer)
    return buf.getvalue()


def rival_pdf_filename(team: str) -> str:
    return f"Informe_Rival_{_clean_filename(team)}_2026_27.pdf"
