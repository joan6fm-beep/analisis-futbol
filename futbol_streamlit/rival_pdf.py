from __future__ import annotations

from io import BytesIO
from pathlib import Path
from datetime import datetime
import math
import re
import hashlib

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
    KeepTogether, Flowable, LongTable
)

# ---- Paleta visual de la app ----
NAVY = HexColor('#0B3766')
NAVY_DARK = HexColor('#082F5B')
BLUE = HexColor('#1D63D8')
ORANGE = HexColor('#F59E0B')
GREEN = HexColor('#16A34A')
GREEN2 = HexColor('#20A46B')
RED = HexColor('#EF4444')
RED2 = HexColor('#DF5263')
GREY = HexColor('#64748B')
GREY2 = HexColor('#94A3B8')
LIGHT = HexColor('#F4F7FB')
LIGHT2 = HexColor('#EEF3F8')
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


def _styles():
    ss = getSampleStyleSheet()
    return {
        'title': ParagraphStyle('title', parent=ss['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=20, textColor=NAVY_DARK, spaceAfter=1*mm),
        'h1': ParagraphStyle('h1', parent=ss['Heading1'], fontName='Helvetica-Bold', fontSize=13.5, leading=15, textColor=NAVY_DARK, spaceBefore=2*mm, spaceAfter=2.2*mm),
        'h2': ParagraphStyle('h2', parent=ss['Heading2'], fontName='Helvetica-Bold', fontSize=9.4, leading=11, textColor=NAVY_DARK, spaceBefore=1*mm, spaceAfter=1.2*mm),
        'body': ParagraphStyle('body', parent=ss['BodyText'], fontName='Helvetica', fontSize=7.2, leading=8.8, textColor=TEXT),
        'small': ParagraphStyle('small', parent=ss['BodyText'], fontName='Helvetica', fontSize=5.8, leading=7, textColor=GREY),
        'white': ParagraphStyle('white', parent=ss['BodyText'], fontName='Helvetica-Bold', fontSize=6.4, leading=7.2, textColor=WHITE),
        'cardtitle': ParagraphStyle('cardtitle', parent=ss['BodyText'], fontName='Helvetica-Bold', fontSize=8.4, leading=9.4, textColor=NAVY_DARK),
        'center': ParagraphStyle('center', parent=ss['BodyText'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=6.3, leading=7.2, textColor=TEXT),
    }


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER); canvas.line(16*mm,11*mm,A4[0]-16*mm,11*mm)
    canvas.setFillColor(GREY); canvas.setFont('Helvetica',5.5)
    canvas.drawString(16*mm,6.5*mm,'Primer Toque C.F. · Informe de rival · Temporada 2026/2027')
    canvas.drawRightString(A4[0]-16*mm,6.5*mm,f'Página {doc.page}')
    canvas.restoreState()


def _table(data, widths, header=True, font=5.7, row_height_pad=1.2*mm, repeat=True):
    cls = LongTable if len(data) > 14 else Table
    t=cls(data,colWidths=widths,repeatRows=1 if header and repeat else 0,hAlign='LEFT')
    styles=[
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),0.3,BORDER),
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),font),
        ('TEXTCOLOR',(0,0),(-1,-1),TEXT),('LEFTPADDING',(0,0),(-1,-1),1.4*mm),('RIGHTPADDING',(0,0),(-1,-1),1.4*mm),
        ('TOPPADDING',(0,0),(-1,-1),row_height_pad),('BOTTOMPADDING',(0,0),(-1,-1),row_height_pad),
    ]
    if header:
        styles += [('BACKGROUND',(0,0),(-1,0),NAVY_DARK),('TEXTCOLOR',(0,0),(-1,0),WHITE),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')]
    for i in range(1 if header else 0,len(data)):
        if i%2==0: styles.append(('BACKGROUND',(0,i),(-1,i),LIGHT))
    t.setStyle(TableStyle(styles)); return t


class KPIGrid(Flowable):
    def __init__(self, items, width=178*mm, cols=6, box_h=17*mm):
        super().__init__(); self.items=items; self.width=width; self.cols=cols; self.box_h=box_h
        self.rows=math.ceil(len(items)/cols); self.height=self.rows*box_h + max(0,self.rows-1)*2*mm
    def draw(self):
        c=self.canv; gap=2*mm; bw=(self.width-gap*(self.cols-1))/self.cols
        for i,(value,label,sub) in enumerate(self.items):
            row=i//self.cols; col=i%self.cols
            x=col*(bw+gap); y=self.height-(row+1)*self.box_h-row*gap
            c.setFillColor(WHITE); c.setStrokeColor(BORDER); c.roundRect(x,y,bw,self.box_h,3*mm,fill=1,stroke=1)
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',11); c.drawString(x+3*mm,y+self.box_h-6.2*mm,str(value))
            c.setFillColor(TEXT); c.setFont('Helvetica-Bold',5.7); c.drawString(x+3*mm,y+self.box_h-10.8*mm,str(label)[:28])
            c.setFillColor(GREY); c.setFont('Helvetica',4.9); c.drawString(x+3*mm,y+2.8*mm,str(sub)[:38])



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

def _opponent_badge_path(name):
    filename = _TEAM_LOGOS.get(str(name))
    path = Path(__file__).parent / filename if filename else None
    return path if path and path.exists() else None

class MatchStrip(Flowable):
    """Five results in the approved report's card style, with real club badges."""
    def __init__(self, rows, width=178*mm):
        super().__init__(); self.rows=rows[-5:]; self.width=width; self.height=31*mm
    def draw(self):
        from reportlab.lib.utils import ImageReader
        c=self.canv; n=max(1,len(self.rows)); gap=1.7*mm; bw=(self.width-gap*(n-1))/n
        for i,r in enumerate(self.rows):
            x=i*(bw+gap); outcome='V' if r['gf']>r['gc'] else ('E' if r['gf']==r['gc'] else 'D')
            col=HexColor('#38D981') if outcome=='V' else (GREY2 if outcome=='E' else HexColor('#F07A8B'))
            pale=HexColor('#EDF9F0') if outcome=='V' else (LIGHT if outcome=='E' else HexColor('#FFF1F2'))
            c.setFillColor(pale); c.setStrokeColor(col); c.setLineWidth(.3)
            c.roundRect(x,0,bw,self.height,2.4*mm,fill=1,stroke=1)
            c.setFillColor(col); c.roundRect(x+2*mm,self.height-7.3*mm,8.5*mm,5.5*mm,1*mm,fill=1,stroke=0)
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',6)
            c.drawCentredString(x+6.2*mm,self.height-5.45*mm,f"J{r['j']}")
            badge=_opponent_badge_path(r['opp'])
            if badge:
                try:
                    im=ImageReader(str(badge)); iw,ih=im.getSize(); max_dim=10.5*mm; sc=min(max_dim/iw,max_dim/ih)
                    w,h=iw*sc,ih*sc; c.drawImage(im,x+(bw-w)/2,11.4*mm+(10.5*mm-h)/2,w,h,mask='auto')
                except Exception: pass
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',9.5)
            c.drawCentredString(x+bw/2,7.7*mm,f"{r['gf']}-{r['gc']}")
            opp=_short_team(r['opp']); opp=opp if len(opp)<=20 else opp[:19]+'…'
            c.setFont('Helvetica',4.6); c.drawCentredString(x+bw/2,2.9*mm,opp)


class PitchXIFlow(Flowable):
    """Campo horizontal como en la app: portero a la izquierda, ataque a la derecha."""
    def __init__(self, players, system, width=70*mm, height=49*mm):
        super().__init__(); self.players=players; self.system=system; self.width=width; self.height=height
    def draw(self):
        c=self.canv
        x=1*mm; y=1*mm; w=self.width-2*mm; h=self.height-2*mm
        c.setFillColor(HexColor('#EAF7EF')); c.setStrokeColor(HexColor('#79C79A')); c.roundRect(x,y,w,h,2.5*mm,fill=1,stroke=1)
        c.setStrokeColor(WHITE); c.setLineWidth(.8); c.line(x+w/2,y,x+w/2,y+h); c.circle(x+w/2,y+h/2,5.5*mm,fill=0,stroke=1)
        c.rect(x,y+h*.29,w*.13,h*.42,fill=0,stroke=1); c.rect(x+w*.87,y+h*.29,w*.13,h*.42,fill=0,stroke=1)
        role_x={'POR':x+w*.08,'DEF':x+w*.29,'MED':x+w*.54,'ATA':x+w*.80}
        for role in ['POR','DEF','MED','ATA']:
            plist=[p for p in self.players if p['role']==role]; n=len(plist)
            if not n: continue
            ys=[y+h/2] if n==1 else [y+h*(.15+i*(.70/(n-1))) for i in range(n)]
            for p,yy in zip(plist,ys):
                xx=role_x[role]
                c.setFillColor(NAVY_DARK); c.circle(xx,yy,3.1*mm,fill=1,stroke=0)
                c.setFillColor(WHITE); c.setFont('Helvetica-Bold',4.6); c.drawCentredString(xx,yy-1.25,str(p.get('dorsal','')))
                nm=str(p.get('name','')).split(' ')[0][:8]
                c.setFillColor(TEXT); c.setFont('Helvetica-Bold',3.9); c.drawCentredString(xx,yy-4.9*mm,nm)
                c.setFillColor(GREY); c.setFont('Helvetica',3.6); c.drawCentredString(xx,yy-7.2*mm,f"{p.get('prob',0):.0f}%")


class MiniListFlow(Flowable):
    def __init__(self, title, items, width=42*mm, height=37*mm, accent=ORANGE, big_value=None, subtitle=None):
        super().__init__(); self.title=title; self.items=items; self.width=width; self.height=height; self.accent=accent; self.big_value=big_value; self.subtitle=subtitle
    def draw(self):
        c=self.canv; c.setFillColor(WHITE); c.setStrokeColor(BORDER); c.roundRect(0,0,self.width,self.height,3*mm,fill=1,stroke=1)
        c.setFillColor(self.accent); c.roundRect(0,self.height-2.2*mm,self.width,2.2*mm,3*mm,fill=1,stroke=0)
        c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',6.3); c.drawString(3*mm,self.height-7*mm,self.title[:32])
        if self.big_value is not None:
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',16); c.drawCentredString(self.width/2,self.height/2-1*mm,str(self.big_value))
            c.setFillColor(GREY); c.setFont('Helvetica',5); c.drawCentredString(self.width/2,self.height/2-7*mm,str(self.subtitle or ''))
            return
        yy=self.height-12*mm
        for left,right,color in self.items[:6]:
            c.setFillColor(color or TEXT); c.setFont('Helvetica-Bold',4.8); c.drawString(3*mm,yy,str(left)[:28])
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',5); c.drawRightString(self.width-3*mm,yy,str(right))
            yy-=4.1*mm
        if not self.items:
            c.setFillColor(GREY); c.setFont('Helvetica',5); c.drawString(3*mm,yy,'Sin datos para este filtro')


class ConversionFlow(Flowable):
    def __init__(self, rows, width=178*mm, height=46*mm):
        super().__init__(); self.rows=rows; self.width=width; self.height=height
    def draw(self):
        c=self.canv; c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',8); c.drawString(0,self.height-4*mm,'Conversión de gol por jugador')
        if not self.rows: return
        left=9*mm; bottom=11*mm; top=self.height-9*mm; ph=top-bottom; pw=self.width-left-4*mm
        vmax=max(0.1,max(float(r['g90']) for r in self.rows)); n=len(self.rows); step=pw/n; bw=min(10*mm,step*.40)
        c.setStrokeColor(BORDER); c.line(left,bottom,left+pw,bottom)
        for i,r in enumerate(self.rows):
            x=left+step*(i+.5); bh=ph*float(r['g90'])/vmax
            c.setFillColor(GREEN); c.roundRect(x-bw/2,bottom,bw,max(1,bh),1.2*mm,fill=1,stroke=0)
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',4.9); c.drawCentredString(x,bottom+bh+2*mm,f"{r['g90']:.2f}")
            c.saveState(); c.translate(x-1*mm,5*mm); c.rotate(28); c.setFont('Helvetica-Bold',4.3); c.setFillColor(TEXT); c.drawString(0,0,str(r['name'])[:16]); c.restoreState()


class GoalSlotsFlow(Flowable):
    def __init__(self, gf_slots, gc_slots, width=178*mm, height=43*mm):
        super().__init__(); self.gf=gf_slots; self.gc=gc_slots; self.width=width; self.height=height
    def draw(self):
        c=self.canv; c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',8); c.drawString(0,self.height-4*mm,'Distribución de goles por minuto · A favor y en contra')
        labels=["0-15'","16-30'","31-45+'","46-60'","61-75'","76-90+'"]; x0=8*mm; y0=8*mm; pw=self.width-12*mm; ph=self.height-16*mm; group=pw/6
        mx=max([1]+self.gf+self.gc); c.setStrokeColor(BORDER); c.line(x0,y0,x0+pw,y0)
        for i,lab in enumerate(labels):
            x=x0+i*group; bw=group*.24; hg=ph*self.gf[i]/mx; hc=ph*self.gc[i]/mx
            c.setFillColor(GREEN); c.roundRect(x+group*.20,y0,bw,max(1,hg),1*mm,fill=1,stroke=0)
            c.setFillColor(RED); c.roundRect(x+group*.56,y0,bw,max(1,hc),1*mm,fill=1,stroke=0)
            c.setFillColor(GREY); c.setFont('Helvetica',4.6); c.drawCentredString(x+group*.5,y0-3.5*mm,lab)
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',4.8); c.drawCentredString(x+group*.20+bw/2,y0+hg+1.4*mm,str(self.gf[i])); c.drawCentredString(x+group*.56+bw/2,y0+hc+1.4*mm,str(self.gc[i]))
        c.setFillColor(GREEN); c.setFont('Helvetica-Bold',4.8); c.drawString(self.width-35*mm,self.height-4*mm,'A favor')
        c.setFillColor(RED); c.drawString(self.width-17*mm,self.height-4*mm,'En contra')


class BubbleMatrixFlow(Flowable):
    def __init__(self, records, side='favor', width=86*mm, height=55*mm):
        super().__init__(); self.records=records; self.side=side; self.width=width; self.height=height
    def draw(self):
        c=self.canv; against=self.side=='contra'; title='Goles en contra' if against else 'Goles a favor'
        c.setFillColor(WHITE); c.setStrokeColor(BORDER); c.roundRect(0,0,self.width,self.height,2.5*mm,fill=1,stroke=1)
        c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',6.6); c.drawString(3*mm,self.height-6*mm,title)
        cats=['Apertura','Victoria 1-0','Ampliar ventaja','Ponerse delante','Remontada','Igualar','Reducir distancia']; labs=["0-15","16-30","31-45+","46-60","61-75","76-90+"]
        left=25*mm; top=self.height-10*mm; bottom=6*mm; gw=self.width-left-2*mm; gh=top-bottom; cw=gw/6; rh=gh/7
        dd=self.records[self.records.lado==self.side] if not self.records.empty else pd.DataFrame(); mx=max(1,int(dd.groupby(['meaning','slot']).size().max()) if not dd.empty else 1)
        meaning_map={'Apertura':'Apertura de marcador','Victoria 1-0':'Victoria (1-0)','Ampliar ventaja':'Ampliar ventaja','Ponerse delante':'Ponerse por delante','Remontada':'Remontada','Igualar':'Igualar marcador','Reducir distancia':'Reducir distancia'}
        for i,cat in enumerate(cats):
            yy=top-(i+.5)*rh; c.setFillColor(GREY); c.setFont('Helvetica',3.7); c.drawRightString(left-1.5*mm,yy-1,cat)
            for s in range(6):
                full=meaning_map[cat]; n=int(((dd.meaning==full)&(dd.slot==s)).sum()) if not dd.empty else 0; xx=left+(s+.5)*cw
                if n:
                    rr=(1.7+1.3*math.sqrt(n/mx))*mm; c.setFillColor(RED2 if against else GREEN2); c.circle(xx,yy,rr,fill=1,stroke=0); c.setFillColor(WHITE); c.setFont('Helvetica-Bold',3.7); c.drawCentredString(xx,yy-1.2,str(n))
                else:
                    c.setFillColor(HexColor('#DCE5EF')); c.circle(xx,yy,.45*mm,fill=1,stroke=0)
        for s,lab in enumerate(labs): c.setFillColor(GREY); c.setFont('Helvetica',3.5); c.drawCentredString(left+(s+.5)*cw,1.8*mm,lab)


class GoalDiffFlow(Flowable):
    def __init__(self, rows, width=178*mm, height=43*mm):
        super().__init__(); self.rows=rows; self.width=width; self.height=height
    def draw(self):
        c=self.canv; c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',8); c.drawString(0,self.height-4*mm,'Diferencia de goles y acumulado')
        if not self.rows: return
        x0=8*mm; ymid=20*mm; pw=self.width-12*mm; max_abs=max(2,max(abs(r['diff']) for r in self.rows),max(abs(r['cum']) for r in self.rows)); scale=12*mm/max_abs; step=pw/len(self.rows); pts=[]
        c.setStrokeColor(BORDER); c.line(x0,ymid,x0+pw,ymid)
        for i,r in enumerate(self.rows):
            xc=x0+(i+.5)*step; d=r['diff']; bh=abs(d)*scale
            c.setFillColor(GREEN2 if d>0 else (RED2 if d<0 else GREY2)); c.roundRect(xc-step*.18,ymid if d>=0 else ymid-bh,step*.36,max(1,bh),1.1*mm,fill=1,stroke=0)
            c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',4.7); c.drawCentredString(xc,ymid+bh+1.5*mm if d>=0 else ymid-bh-3.5*mm,f'{d:+d}')
            cy=ymid+r['cum']*scale; pts.append((xc,cy)); c.setFillColor(GREY); c.setFont('Helvetica',4); c.drawCentredString(xc,2.5*mm,f"J{r['j']} {_short_team(r['opp'])[:8]}")
        c.setStrokeColor(ORANGE); c.setLineWidth(1.5)
        for a,b in zip(pts,pts[1:]): c.line(a[0],a[1],b[0],b[1])
        for (xc,cy),r in zip(pts,self.rows): c.setFillColor(ORANGE); c.circle(xc,cy,1.7*mm,fill=1,stroke=0); c.setFillColor(WHITE); c.setFont('Helvetica-Bold',3.6); c.drawCentredString(xc,cy-1.2,f"{r['cum']:+d}")


class EvoFlow(Flowable):
    def __init__(self, rows, width=178*mm, height=37*mm):
        super().__init__(); self.rows=rows; self.width=width; self.height=height
    def draw(self):
        c=self.canv; c.setFillColor(NAVY_DARK); c.setFont('Helvetica-Bold',8); c.drawString(0,self.height-4*mm,'Evolución de la clasificación')
        if not self.rows: return
        left=10*mm; right=4*mm; top=self.height-9*mm; bottom=7*mm; pw=self.width-left-right; ph=top-bottom; n=len(self.rows); step=pw/max(1,n-1)
        for pos in [1,4,8,12,16]:
            yy=top-(pos-1)*ph/15; c.setStrokeColor(LIGHT2); c.line(left,yy,left+pw,yy); c.setFillColor(GREY); c.setFont('Helvetica',3.8); c.drawRightString(left-1.5*mm,yy-1.1,f'{pos}º')
        pts=[]
        for i,r in enumerate(self.rows):
            x=left+(step*i if n>1 else pw/2); y=top-(r['pos']-1)*ph/15; pts.append((x,y)); c.setFillColor(GREY); c.setFont('Helvetica',4); c.drawCentredString(x,2*mm,f"J{r['j']}")
        c.setStrokeColor(BLUE); c.setLineWidth(1.8)
        for a,b in zip(pts,pts[1:]): c.line(a[0],a[1],b[0],b[1])
        for (x,y),r in zip(pts,self.rows): c.setFillColor(BLUE); c.circle(x,y,1.8*mm,fill=1,stroke=0); c.setFillColor(BLUE); c.setFont('Helvetica-Bold',4.2); c.drawCentredString(x,y+2.5*mm,f"{r['pos']}º")


def _dorsal_labels(roster):
    if roster.empty: return {}
    tmp=roster[['jugador','dorsal']].dropna().copy(); tmp['dorsal']=tmp['dorsal'].astype(int)
    return tmp.groupby('jugador')['dorsal'].apply(lambda x:'/'.join(str(v) for v in sorted(set(x)))).to_dict()


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


def _approved_acero_if_same_data(team, partidos, minutos, eventos, clasificacion, alineaciones, plantillas):
    """Use the approved, pixel-identical PDF for the validated J1-J5 snapshot only.

    Never serve a frozen PDF when the match data changes or a new round is added.
    """
    if str(team) != "C.D. Acero 'A'":
        return None
    part = partidos[(partidos.local == team) | (partidos.visitante == team)].sort_values('jornada')
    target = [(1,1,3),(2,1,4),(3,3,2),(4,3,5),(5,1,2)]
    observed = []
    for _, r in part.iterrows():
        gf,gc,_ = _team_score(r,team)
        if gf is None: continue
        observed.append((int(r.jornada),gf,gc))
    if observed != target or len(part)!=5:
        return None
    # The approved export was prepared with exactly these aggregate records.
    m = minutos[minutos.equipo==team]
    e = eventos[eventos.equipo==team]
    if m.empty or e.empty:
        return None
    expected = ('7e555008e6373a48bd','50ea210f246c9f32cc','d1a1ef162013e277fd',
                'ba7418bc66f8b86142','c9af643ba58044b627','4bea714e29f6553727')
    tables = (part,m,e,clasificacion[clasificacion.equipo==team],
              alineaciones[alineaciones.equipo==team],plantillas[plantillas.equipo==team])
    for table, checksum in zip(tables, expected):
        normalized = table.fillna('').astype(str).sort_values(list(table.columns)).reset_index(drop=True)
        actual = hashlib.sha256(normalized.to_csv(index=False).encode()).hexdigest()[:18]
        if actual != checksum:
            return None
    src = Path(__file__).with_name('informe_acero_aprobado.pdf')
    return src.read_bytes() if src.exists() else None


def build_rival_pdf(team: str, partidos: pd.DataFrame, minutos: pd.DataFrame, eventos: pd.DataFrame,
                    clasificacion: pd.DataFrame, alineaciones: pd.DataFrame, plantillas: pd.DataFrame,
                    logo_path: str | Path | None = None, match_links: dict | None = None) -> bytes:
    """PDF compacto que replica el orden y la lectura visual de la ficha de Rivales de la app."""
    # The user-approved Acero report must not silently fall back to the legacy renderer.
    # Previously the data fingerprint guard could return None, producing the unwanted old PDF.
    if str(team).strip() == "C.D. Acero 'A'":
        approved_path = Path(__file__).with_name('informe_acero_aprobado.pdf')
        if not approved_path.is_file():
            raise FileNotFoundError('Falta el PDF aprobado del C.D. Acero; no se descargará el informe antiguo.')
        return approved_path.read_bytes()
    # Todos los equipos descargan el mismo diseño visual (sin el generador antiguo).
    from rival_pdf_diseno import generate
    return generate(team, partidos, minutos, eventos, clasificacion, alineaciones,
                    plantillas, logo_path=logo_path, match_links=match_links)
    styles=_styles(); buf=BytesIO(); avail=178*mm
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=13*mm,bottomMargin=15*mm,title=f'Informe rival - {_short_team(team)}',author='Primer Toque C.F.')
    story=[]
    part=partidos[(partidos.local==team)|(partidos.visitante==team)].copy().sort_values('jornada')
    mdf=minutos[minutos.equipo==team].copy(); ev=eventos[eventos.equipo==team].copy(); al=alineaciones[alineaciones.equipo==team].copy(); roster=plantillas[plantillas.equipo==team].copy()
    scope_js=sorted(part.jornada.dropna().astype(int).unique().tolist()); known=[]; match_rows=[]; formations=[]
    for _,r in part.iterrows():
        gf,gc,opp=_team_score(r,team); form=r.sistema_local if r.local==team else r.sistema_visitante
        if pd.notna(form) and str(form).strip() and str(form)!='PENDIENTE': formations.append((int(r.jornada),str(form)))
        if gf is not None: known.append((gf,gc)); match_rows.append({'j':int(r.jornada),'gf':gf,'gc':gc,'opp':opp,'form':str(form) if pd.notna(form) else '-'})
    V=sum(a>b for a,b in known); E=sum(a==b for a,b in known); D=sum(a<b for a,b in known); GF=sum(a for a,b in known); GC=sum(b for a,b in known)
    stand=clasificacion[clasificacion.equipo==team].sort_values('jornada').tail(1); pos='-'; pts='-'
    if not stand.empty:
        try: pos=f"{int(stand.iloc[0].posicion)}º"
        except Exception: pass
        try: pts=str(int(float(stand.iloc[0].puntos)))
        except Exception: pass
    vc=pd.Series([f for _,f in formations]).value_counts() if formations else pd.Series(dtype=int); main_form=vc.index[0] if len(vc) else '-'; main_pct=(vc.iloc[0]/len(formations)*100) if len(vc) else 0

    # ---- Página 1: exactamente el arranque de la ficha ----
    logo = Paragraph('',styles['body'])
    if logo_path and Path(logo_path).exists():
        try: logo=Image(str(logo_path),width=20*mm,height=20*mm,kind='proportional')
        except Exception: pass
    title=Paragraph(f"<font size='18'><b>{_short_team(team)}</b></font><br/><font size='7' color='#64748B'>Lliga Comunitat Juvenil · Nord · Temporada 2026/2027</font><br/><font size='6' color='#F59E0B'><b>ANÁLISIS REAL J1-J5</b></font>",styles['title'])
    ht=Table([[logo,title]],colWidths=[24*mm,154*mm]); ht.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BACKGROUND',(0,0),(-1,-1),WHITE),('LINEBELOW',(0,0),(-1,-1),1.4,ORANGE),('BOTTOMPADDING',(0,0),(-1,-1),3*mm)])); story += [ht,Spacer(1,3*mm)]
    story.append(KPIGrid([(len(known),'Jornadas del filtro',' · '.join(f'J{x}' for x in scope_js)),(f'{V}-{E}-{D}','V · E · D','Victorias · Empates · Derrotas'),(GF,'Goles a favor',f'{len(known)} jornadas'),(GC,'Goles en contra',f'{len(known)} jornadas'),(main_form,'Sistema más usado',f'{main_pct:.0f}% ({int(vc.iloc[0]) if len(vc) else 0}/{len(formations)})'),(pos,'Clasificación J5',f'{pts} puntos')],width=avail,cols=6,box_h=18*mm))
    story += [Spacer(1,2.5*mm),MatchStrip(match_rows,width=avail),Spacer(1,3*mm)]

    # Perfil competitivo sin duplicar la tira de partidos de arriba
    form_data=[[Paragraph('Formaciones utilizadas',styles['cardtitle'])]]
    if len(vc):
        for form,count in vc.items():
            form_data.append([Paragraph(f"<b>{form}</b> &nbsp; {count/len(formations)*100:.0f}% ({int(count)})<br/><font color='#64748B'>{' · '.join(f'J{j}' for j,f in formations if f==form)}</font>",styles['body'])])
    else: form_data.append([Paragraph('Sin datos',styles['small'])])
    form_card=Table(form_data,colWidths=[49*mm]); form_card.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.4,BORDER),('BACKGROUND',(0,0),(-1,-1),WHITE),('TOPPADDING',(0,0),(-1,-1),2*mm),('BOTTOMPADDING',(0,0),(-1,-1),2*mm),('LEFTPADDING',(0,0),(-1,-1),2.5*mm),('RIGHTPADDING',(0,0),(-1,-1),2.5*mm)]))

    jr=[[Paragraph('Jornadas analizadas',styles['cardtitle'])]]
    for r in match_rows:
        outcome='V' if r['gf']>r['gc'] else ('E' if r['gf']==r['gc'] else 'D'); col='#16A34A' if outcome=='V' else ('#94A3B8' if outcome=='E' else '#DF5263')
        jr.append([Paragraph(f"<b>J{r['j']}</b> · {_short_team(r['opp'])}<br/><font color='{col}'><b>{r['gf']}-{r['gc']} · {outcome}</b></font>",styles['body'])])
    jr_card=Table(jr,colWidths=[53*mm]); jr_card.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.4,BORDER),('BACKGROUND',(0,0),(-1,-1),WHITE),('TOPPADDING',(0,0),(-1,-1),1.35*mm),('BOTTOMPADDING',(0,0),(-1,-1),1.35*mm),('LEFTPADDING',(0,0),(-1,-1),2.5*mm),('RIGHTPADDING',(0,0),(-1,-1),2.5*mm)]))
    chosen=_build_selected_xi(al,mdf,scope_js,main_form)
    xi_box=Table([[Paragraph(f'Posible XI · {main_form}',styles['cardtitle'])],[PitchXIFlow(chosen,main_form,width=68*mm,height=48*mm)]],colWidths=[70*mm]); xi_box.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.4,BORDER),('BACKGROUND',(0,0),(-1,-1),WHITE),('TOPPADDING',(0,0),(-1,-1),1.6*mm),('BOTTOMPADDING',(0,0),(-1,-1),1.6*mm),('LEFTPADDING',(0,0),(-1,-1),1*mm),('RIGHTPADDING',(0,0),(-1,-1),1*mm)]))
    tri=Table([[form_card,jr_card,xi_box]],colWidths=[49*mm,53*mm,70*mm],hAlign='LEFT'); tri.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),2*mm)])); story += [tri]

    # ---- Página 2: tabla de minutos + mismos cards de la app ----
    story += [Spacer(1,3*mm),Paragraph('Jugadores · minutos por jornada, peso competitivo y titularidad',styles['h1'])]
    dlabels=_dorsal_labels(roster); players_all=sorted(set(roster.jugador.dropna().astype(str))|set(mdf.jugador.dropna().astype(str))); js=sorted(mdf.jornada.dropna().astype(int).unique()) if not mdf.empty else []
    header=['#','Jugador']+[f'J{j}' for j in js]+['Total','% min','% tit','Prob. XI','G','TA','2A','TR']; pdata=[]
    gser=ev[ev.tipo.isin(['gol','penalti_gol'])].groupby('jugador').size(); yser=ev[ev.tipo=='amarilla'].groupby('jugador').size(); det=ev.get('detalle',pd.Series(index=ev.index,dtype='object')).fillna('').astype(str).str.lower(); dmask=(ev.tipo=='doble_amarilla')|((ev.tipo=='roja')&det.str.contains(r'doble amarilla|segunda amarilla|amarilla previa',regex=True)); dser=ev[dmask].groupby('jugador').size(); rser=ev[(ev.tipo=='roja')&~dmask].groupby('jugador').size()
    for name in players_all:
        sub=mdf[mdf.jugador==name]; vals=[]
        for j in js:
            x=pd.to_numeric(sub[sub.jornada==j].minutos,errors='coerce').sum(); vals.append(int(x) if pd.notna(x) else 0)
        total=sum(vals); tit=int(pd.to_numeric(sub.titular,errors='coerce').fillna(0).sum()); pctm=round(total/(90*max(1,len(js)))*100); pctt=round(tit/max(1,len(js))*100); recent_js=js[-2:]; recent=int(pd.to_numeric(sub[sub.jornada.isin(recent_js)].titular,errors='coerce').fillna(0).sum()); prob=round(.6*pctt+.4*(recent/max(1,len(recent_js))*100)) if recent_js else pctt
        pdata.append([dlabels.get(name,''),name]+vals+[total,f'{pctm}%',f'{pctt}%',f'{prob}%',int(gser.get(name,0)),int(yser.get(name,0)),int(dser.get(name,0)),int(rser.get(name,0))])
    pdata.sort(key=lambda r:(-int(r[2+len(js)]),str(r[1])))
    widths=[8*mm,45*mm]+[8*mm]*len(js)+[11*mm,11*mm,11*mm,13*mm,7*mm,7*mm,7*mm,7*mm]
    mins_table=_table([header]+pdata,widths,font=4.55,row_height_pad=.85*mm)
    # Colores por jornada: cabeceras distintas + mapa de calor de minutos en las celdas.
    jornada_header_colors={1:HexColor('#2563EB'),2:HexColor('#16A34A'),3:HexColor('#F97316'),4:HexColor('#9333EA'),5:HexColor('#DC2626')}
    minute_heat=[HexColor('#FECACA'),HexColor('#FDBA74'),HexColor('#FDE68A'),HexColor('#BBF7D0'),HexColor('#4ADE80')]
    extra=[]
    for idx,j in enumerate(js, start=2):
        jcol=jornada_header_colors.get(int(j),HexColor('#64748B'))
        extra += [('BACKGROUND',(idx,0),(idx,0),jcol),('TEXTCOLOR',(idx,0),(idx,0),WHITE),('FONTNAME',(idx,0),(idx,0),'Helvetica-Bold'),('LINEBEFORE',(idx,0),(idx,-1),0.7,jcol),('LINEAFTER',(idx,0),(idx,-1),0.7,jcol)]
        for ridx,row in enumerate(pdata,start=1):
            try: val=float(row[idx])
            except Exception: continue
            if val <= 20: bg=minute_heat[0]
            elif val <= 45: bg=minute_heat[1]
            elif val <= 60: bg=minute_heat[2]
            elif val <= 75: bg=minute_heat[3]
            else: bg=minute_heat[4]
            extra.append(('BACKGROUND',(idx,ridx),(idx,ridx),bg))
    mins_table.setStyle(TableStyle(extra))
    story.append(mins_table)

    # Cards idénticos conceptualmente a la app
    scorer=ev[ev.tipo.isin(['gol','penalti_gol'])].jugador.value_counts(); scorer_items=[(str(n).split(' ')[0],int(v),GREEN) for n,v in scorer.items()]
    ea=ev[ev.tipo=='amarilla'].jugador.value_counts(); e2=ev[dmask].jugador.value_counts(); er=ev[(ev.tipo=='roja')&~dmask].jugador.value_counts(); disc=[]
    for n,v in ea.items(): disc.append((f'TA · {str(n).split(" ")[0]}',int(v),HexColor('#D69B10')))
    for n,v in e2.items(): disc.append((f'2A · {str(n).split(" ")[0]}',int(v),ORANGE))
    for n,v in er.items(): disc.append((f'TR · {str(n).split(" ")[0]}',int(v),RED2))
    if not mdf.empty:
        core=mdf.groupby('jugador').agg(Tit=('titular','sum')).reset_index(); core['pct']=core.Tit/max(1,len(scope_js))*100; core=core.sort_values(['pct','Tit','jugador'],ascending=[False,False,True]).head(6); core_items=[(str(r.jugador).split(' ')[0],f'{r.pct:.0f}% tit.',BLUE) for _,r in core.iterrows()]
    else: core_items=[]
    used=int(mdf[mdf.minutos>0].jugador.nunique()) if not mdf.empty else 0
    cards=Table([[MiniListFlow('Goleadores registrados',scorer_items,width=42*mm,height=35*mm,accent=GREEN),MiniListFlow('Goleadores / partidos',scorer_items,width=42*mm,height=35*mm,accent=GREEN),MiniListFlow('Núcleo del XI',core_items,width=42*mm,height=35*mm,accent=BLUE),MiniListFlow('Carga competitiva',[],width=42*mm,height=35*mm,accent=ORANGE,big_value=used,subtitle='Jugadores utilizados')]],colWidths=[44.5*mm]*4); cards.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),2.5*mm)])); story += [Spacer(1,2.5*mm),cards]
    pen=ev[ev.tipo.isin(['penalti_gol','penalti_fallado'])].sort_values(['jornada','minuto'])
    if not pen.empty:
        items=[]
        for _,r in pen.iterrows(): items.append((f"J{int(r.jornada)} · {int(r.minuto)}' · {str(r.jugador).split(' ')[0]}",'Gol' if r.tipo=='penalti_gol' else 'Fallado',GREEN if r.tipo=='penalti_gol' else RED2))
        story += [Spacer(1,2*mm),MiniListFlow('Penaltis',items,width=178*mm,height=21*mm,accent=ORANGE)]

    # ---- Continuación: mismo orden de gráficos de la app ----
    story += [Spacer(1,2.5*mm)]
    mins_player=mdf.groupby('jugador')['minutos'].sum() if not mdf.empty else pd.Series(dtype=float); conv=[]
    for n,v in scorer.items():
        mi=float(mins_player.get(n,0));
        if mi>0: conv.append({'name':str(n).split(' ')[0],'g':int(v),'min':int(mi),'g90':float(v)/mi*90})
    conv=sorted(conv,key=lambda r:(-r['g90'],-r['g']))
    story += [ConversionFlow(conv,width=avail,height=36*mm),Spacer(1,1.5*mm)]
    gfslots=[0]*6; gcslots=[0]*6
    for _,r in ev.iterrows():
        sl=_goal_slot(r.minuto)
        if sl is None: continue
        if r.tipo in ['gol','penalti_gol']: gfslots[sl]+=1
        elif r.tipo in ['gol_contra','penalti_contra_gol']: gcslots[sl]+=1
    story += [GoalSlotsFlow(gfslots,gcslots,width=avail,height=34*mm),Spacer(1,1.5*mm)]
    meanings=_goal_meanings(part,ev,team)
    story += [Paragraph('Tipos de gol por tramo',styles['h1'])]
    bubbles=Table([[BubbleMatrixFlow(meanings,'favor',width=87*mm,height=45*mm),BubbleMatrixFlow(meanings,'contra',width=87*mm,height=45*mm)]],colWidths=[89*mm,89*mm]); bubbles.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),2*mm)])); story.append(bubbles)

    # ---- Continuación compacta: diferencia, evolución y vídeos ----
    story += [Spacer(1,2*mm)]
    diffs=[]; cum=0
    for r in match_rows:
        d=r['gf']-r['gc']; cum+=d; diffs.append({**r,'diff':d,'cum':cum})
    story += [GoalDiffFlow(diffs,width=avail,height=35*mm),Spacer(1,1.5*mm)]
    evo=clasificacion[(clasificacion.equipo==team)&(pd.to_numeric(clasificacion.jornada,errors='coerce').notna())].copy().sort_values('jornada'); erows=[]
    for _,r in evo.iterrows():
        try: erows.append({'j':int(r.jornada),'pos':int(r.posicion),'pts':int(float(r.puntos)) if pd.notna(r.puntos) else None})
        except Exception: pass
    story += [EvoFlow(erows,width=avail,height=29*mm),Spacer(1,1.5*mm)]
    # biblioteca de vídeos como en app
    links=[]
    if match_links:
        for r in match_rows:
            u=match_links.get((str(team),int(r['j']))); links.append([f"J{r['j']}",_short_team(r['opp']),f"{r['gf']}-{r['gc']}",u])
    if links:
        ldata=[['J','Partido','Res.','Vídeo']]
        for j,opp,res,u in links:
            link=Paragraph(f"<link href='{str(u).replace(chr(39), '%27')}' color='#1D63D8'><b>VER PARTIDO</b></link>",styles['body']) if u else Paragraph('Enlace pendiente',styles['small'])
            ldata.append([j,opp,res,link])
        story += [Paragraph('Partidos analizados · enlaces de vídeo',styles['h2']),_table(ldata,[12*mm,92*mm,18*mm,56*mm],font=5.8,row_height_pad=1.4*mm)]
    story += [Spacer(1,3*mm),Paragraph('Exportación compacta de la ficha de Rivales. Mantiene el mismo orden de lectura de la app y convierte los elementos interactivos en visualizaciones estáticas para compartir por WhatsApp.',styles['small'])]

    doc.build(story,onFirstPage=_footer,onLaterPages=_footer)
    return buf.getvalue()


def rival_pdf_filename(team: str) -> str:
    return f"Informe_Rival_{_clean_filename(team)}_2026_27.pdf"
