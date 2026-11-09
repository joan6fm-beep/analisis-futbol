"""Pruebas de integridad entre app.py y sus módulos (ui_theme, team360_charts, player_charts).

Uso (desde la raíz del repositorio):

    python tests/test_integridad.py

1. Estática: todo atributo que app.py usa de un módulo propio existe en ese módulo.
2. Regresión: si Streamlit conserva en memoria una versión antigua de un módulo
   (lo que ocurre en Streamlit Cloud tras un push), la app la recarga y no falla.
3. Renderizado: Equipo 360 y otras vistas clave pintan sus componentes principales
   con valores reales, no solo arrancan.
Devuelve código 1 si alguna comprobación falla.
"""
import ast
import importlib
import logging
import sys
from pathlib import Path

sys.dont_write_bytecode = True
APP_DIR = Path(__file__).resolve().parents[1] / "futbol_streamlit"
APP = APP_DIR / "app.py"
sys.path.insert(0, str(APP_DIR))
logging.getLogger("streamlit").setLevel(logging.ERROR)

from streamlit.testing.v1 import AppTest  # noqa: E402

ALIASES = {"t360": "team360_charts", "T": "team360_charts", "ui_theme": "ui_theme",
           "player_charts": "player_charts", "pdf_export_v63": "pdf_export_v63",
           "t360adv": "team360_advanced", "A": "team360_advanced", "infd": "infantil_d", "cad": "cadete_a"}
fallos = []


def check(cond, msg):
    print(("OK    " if cond else "FALLO ") + msg)
    if not cond:
        fallos.append(msg)


def run(params, setup=None):
    at = AppTest.from_file(str(APP), default_timeout=180)
    for k, v in params.items():
        at.query_params[k] = v
    at.run()
    if setup:
        setup(at)
        at.run()
    return at


def html_of(at):
    """Texto de st.markdown y de st.html (este último no tiene accesor propio en AppTest)."""
    return " ".join([m.value for m in at.markdown] + [str(h.proto) for h in at.get("html")])


def test_atributos():
    tree = ast.parse(APP.read_text(encoding="utf-8"))
    usados = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in ALIASES:
            usados.setdefault(ALIASES[node.value.id], set()).add(node.attr)
    for mod_name, attrs in sorted(usados.items()):
        mod = importlib.import_module(mod_name)
        faltan = sorted(a for a in attrs if not hasattr(mod, a))
        check(not faltan, f"app.py usa {len(attrs)} atributos de {mod_name}" + (f"; faltan: {faltan}" if faltan else ""))


def test_modulo_obsoleto():
    """Reproduce el fallo de Streamlit Cloud: módulo antiguo en memoria sin una función nueva."""
    import team360_charts
    del team360_charts.kpi_tiles_html          # versión 'antigua' sin la función
    team360_charts._loaded_mtime = -1          # marca de carga distinta del archivo en disco
    at = run({"area": "juvenil", "view": "equipo"})
    check(not at.exception, "Equipo 360 se recupera con un módulo obsoleto en memoria"
          + (f": {at.exception[0].value[:120]}" if at.exception else ""))


def nav(view=None, area=None, tool=None, extra=None):
    """Navega Equipo 360: vista principal → área o herramienta → interacción extra."""
    def setup(a):
        if view:
            a.button_group(key="eq_view").set_value(view)
            a.run()
        if area:
            a.button_group(key="area_sel").set_value(area)
            a.run()
        if tool:
            a.button_group(key="adv_tool").set_value(tool)
            a.run()
        if extra:
            extra(a)
    return run({"area": "juvenil", "view": "equipo"}, setup if (view or area or tool or extra) else None)


def test_equipo360():
    """Equipo 360: tres niveles de lectura con datos reales."""
    # Nivel 1 · Resumen del partido (vista por defecto, J7)
    at = nav()
    check(not at.exception, "Resumen del partido sin excepciones" + (f": {at.exception[0].value[:120]}" if at.exception else ""))
    h = html_of(at)
    check("sum-card" in h and "Resumen del partido" in h, "Nivel 1: tarjetas de indicadores del partido")
    check("41 %" in h and "Media en casa: 57,8 %" in h and "−16,8 p.p." in h and "Menos posesión que su media habitual" in h,
          "J7 posesión: 41 %, media 57,8 %, −16,8 p.p. y lectura sencilla")
    check("Partido más disputado" in h or "Partido menos disputado" in h or "Duelos" in h, "Duelos con lectura neutra (no «mejor defensa»)")
    check(any("Pendiente de revisión" in c.value for c in at.caption), "Aviso pendiente de J7 (ocasiones 14 frente a 13)")
    check("mr-board" in h and "Derrota 1–2" in h and "Núñez" in h and "Jorge Agustina Llopis" in h,
          "Ficha de J7: marcador, resumen escrito y cronología con goleadores de ambos equipos")
    check(h.count("class='h2h-row'") >= 6, "Cara a cara de J7 con al menos 6 estadísticas de ambos equipos")
    opts = at.selectbox(key="sum_j").options
    check(any("Media en casa" in str(o) for o in opts), f"El desplegable de partido incluye la media en casa")
    at_m = nav(extra=lambda a: (a.selectbox(key="sum_j").set_value("media"), a.run()))
    hm = html_of(at_m)
    check(not at_m.exception and "Cara a cara medio" in hm and "Indicadores medios" in hm and "57,8 %" in hm,
          "Vista «Media en casa»: cara a cara medio e indicadores medios (posesión 57,8 %)")
    # Nivel 2 · Análisis por áreas
    expected = {"Posesión y control": "¿Quién tuvo más el balón?", "Construcción y pases": "¿Cuánto pasamos y con qué acierto?",
                "Ataque y finalización": "¿Desde dónde intentamos marcar?", "Duelos y defensa": "¿Cuánta actividad defensiva tuvimos?",
                "Balón parado": "¿Cuántas jugadas a balón parado generamos y concedimos?"}
    for area, q in expected.items():
        at = nav("Análisis por áreas", area)
        check(not at.exception and q in html_of(at) and len(at.get("plotly_chart")) >= 1, f"Área «{area}»: pregunta y gráfico principal")
    h = html_of(at)
    check("<table class='mt'>" in h and all(c in h for c in ("J2 · Bétera", "J3 · Manises", "J5 · Alboraya", "J7 · Salesianos")),
          "Tabla visual de todas las métricas con J2, J3, J5 y J7")
    import re as _re
    rows = {_re.sub("<[^>]+>", "", m.group(1)).strip(): m.group(2) for m in _re.finditer(r"<tr><td class='m'>(.*?)<small>.*?</small></td>(.*?)</tr>", h)}
    pos = rows.get("Posesión", "")
    cells = _re.findall(r"<td><div class='mc'>(.*?)</div></td>", pos)
    check(len(cells) == 4 and "67%" in cells[0] and "33%" in cells[0] and "width:100%" in cells[0] and "width:49%" in cells[0],
          "Posesión J2: 67 % y 33 % con barras a la misma escala (100 % y 49 %)")
    check("41%" in cells[3] and "59%" in cells[3] and "width:69%" in cells[3], "Posesión J7: barra PT al 69 % de la del rival (41 ÷ 59)")
    tiros = _re.findall(r"<td><div class='mc'>(.*?)</div></td>", rows.get("Tiros", ""))
    check(len(tiros) == 4 and "sin dato" in tiros[3] and tiros[3].count("<i ") == 1, "Tiros J7: rival «sin dato», sin barra (no se trata como cero)")
    duel = _re.findall(r"<td><div class='mc'>(.*?)</div></td>", rows.get("Duelos", ""))
    check(len(duel) == 4 and "124" in duel[1] and "class='rv'" not in duel[1], "Duelos J3 = 124, solo barra de Primer Toque")
    import pandas as _pd
    _adv = _pd.read_csv(APP_DIR / "data" / "equipo_avanzado.csv")
    check(float(_adv.loc[_adv.jornada == 2, "penaltis_contra"].iloc[0]) == 1 and float(_adv.loc[_adv.jornada == 2, "penaltis_favor"].iloc[0]) == 0,
          "Penaltis J2: 1 en contra y 0 a favor (corrección confirmada)")
    at_bp = nav("Análisis por áreas", "Balón parado")
    check(any("J2: 1 penalti en contra, no convertido" in c.value for c in at_bp.caption), "Nota de penaltis: J2 1 en contra, no convertido")
    # Nivel 3 · Análisis avanzado: comparador jornada contra jornada
    at = nav("Análisis avanzado", tool="Jornada contra jornada")
    metrics = {m.label: m.value for m in at.metric}
    check(metrics.get("Media Primer Toque") == "57.8" and metrics.get("Media rivales") == "42.2", f"Comparador por defecto (Posesión): {metrics}")
    at = nav("Análisis avanzado", tool="Jornada contra jornada", extra=lambda a: (a.selectbox(key="v83_metric").set_value("Tiros"), a.run()))
    m1 = {m.label: m.value for m in at.metric}
    check(m1 == {"Media Primer Toque": "13.2", "Media rivales": "11.0", "Diferencia comparable": "+2.3"}, f"Comparador con Tiros: {m1}")
    def two(a):
        a.selectbox(key="v83_metric").set_value("Duelos")
        a.radio(key="v83_view").set_value("Comparar dos jornadas")
        a.run()
    at = nav("Análisis avanzado", tool="Jornada contra jornada", extra=two)
    m2 = {m.label: m.value for m in at.metric}
    check(not at.exception and m2.get("Mejor partido") == "124", f"Comparador con Duelos y dos jornadas: {m2}")
    check("cmp-table" in html_of(at), "Tabla de comparación entre dos jornadas renderizada")
    # Vista Temporada: resultados, protagonistas y lectura de la temporada
    at = nav("Temporada")
    h = html_of(at)
    check(not at.exception and "Pulso de la temporada" in h and "Los protagonistas" in h and "Lectura rápida" in h
          and "58%" in h and len(at.get("plotly_chart")) >= 3, "Temporada: resultados, gráficos, protagonistas e indicadores de vídeo")


def test_otras_vistas():
    at = run({})
    check(not at.exception and "Selecciona tu equipo" in html_of(at), "Portada con selección de equipo")
    at = run({"area": "juvenil", "view": "rivales", "team": "Bétera C.F. 'A'"})
    check(not at.exception and len(at.get("plotly_chart")) >= 1 and at.get("download_button"),
          "Rivales: evolución de la clasificación (Plotly) y botón PDF")
    at = run({"area": "juvenil", "view": "jugadores", "player": "Bilal"})
    check(not at.exception and len(at.get("plotly_chart")) >= 2, "Ficha de jugador: minutos y evolución física")
    import pandas as _pd
    equipos = _pd.read_csv(APP_DIR / "data" / "equipos_liga.csv", encoding="utf-8-sig")["equipo"].tolist()
    dark = ("fill='#102a43'", "fill='#0b6b2e'", "fill='#334155'", "fill='#0b3766'")
    bad = []
    for team in equipos:
        a_ = run({"area": "juvenil", "view": "rivales", "team": team})
        hh = html_of(a_)
        if a_.exception or any(x in hh for x in dark) or ("Conversión de gol por jugador" in hh and "fill='#FFFFFF'" not in hh):
            bad.append(team)
    check(not bad, f"Rivales: nombres de goleadores y textos legibles (blanco) en los {len(equipos)} equipos" + (f"; revisar {bad}" if bad else ""))


def test_avanzado():
    """Análisis avanzado: medias recalculadas desde los CSV y radares sin valores inventados."""
    import pandas as pd
    import team360_advanced as A
    import team360_charts as T
    part = pd.read_csv(APP_DIR / "data" / "partidos_rivales.csv")
    adv = pd.read_csv(APP_DIR / "data" / "equipo_avanzado.csv")
    veo = T.prepare(adv[adv.jornada.isin([2, 3, 5, 7])], lambda x: x)
    pt = A.team_matches(part, A.TEAM)
    _ptp = part.dropna(subset=["goles_local"])
    _ptp = _ptp[(_ptp.local == A.TEAM) | (_ptp.visitante == A.TEAM)]
    check(len(pt) == len(_ptp), f"Primer Toque: {len(pt)} partidos con resultado oficial ({int(pt.pts.sum())} puntos)")
    # Media de Alboraya como visitante, calculada a mano desde el CSV
    alb = "Alboraya U.D. 'B'"
    raw = part[(part.visitante == alb)].dropna(subset=["goles_visitante"])
    rows = A.four_refs(veo, pt, A.team_matches(part, alb), 5, exclude=True).set_index("metrica")
    check(abs(rows.loc["Goles a favor", "d"] - raw.goles_visitante.mean()) < 1e-9 and rows.loc["Goles a favor", "nd"] == len(raw),
          f"D · goles de Alboraya fuera = {raw.goles_visitante.mean():.2f} con n = {len(raw)}")
    pos_ref = adv[adv.jornada.isin([2, 3, 7])].posesion_favor_pct.mean()
    check(abs(rows.loc["Posesión", "b"] - pos_ref) < 1e-9 and rows.loc["Posesión", "nb"] == 3,
          f"B · posesión media PT en casa sin J5 = {pos_ref:.2f} (n = 3)")
    check(rows.loc["Posesión", "a"] == 70 and rows.loc["Posesión", "c"] == 30, "A/C · posesión J5 70 / 30")
    vid = rows[rows.grupo.str.startswith("Vídeo")]
    check(vid.d.isna().all(), "D · ninguna estadística de vídeo del rival fuera de casa (no se inventa)")
    home_res = pt[(pt.condicion == "Casa") & (pt.jornada != 5)]
    check(abs(rows.loc["Puntos", "b"] - home_res.pts.mean()) < 1e-9, f"B · puntos por partido en casa sin J5 = {home_res.pts.mean():.2f}")
    # Radares: cada valor real coincide con el CSV y el índice es valor ÷ máximo × 100
    for j in (2, 3, 5, 7):
        fig, tbl = A.radar_vs_average(veo, j)
        ok = True
        for _, r in tbl.iterrows():
            col = T.METRIC_BY_LABEL[r.metrica][1]
            ok &= r.valor == adv.loc[adv.jornada == j, col].iloc[0] and r.maximo == adv[adv.jornada.isin([2, 3, 5, 7])][col].max()
        if fig is not None:
            idx = [v for tr in fig.data for v in tr.r]
            ok &= all(0 <= v <= 100.0001 for v in idx)
        check(ok and tbl.notna().all(axis=None), f"Radar J{j} frente a su media: {len(tbl)} ejes con datos reales e índice 0–100")
        fig, tbl = A.radar_vs_rival(veo, j)
        both = all(pd.notna(adv.loc[adv.jornada == j, T.METRIC_BY_LABEL[m][2]].iloc[0]) for m in tbl.metrica)
        check(both, f"Radar J{j} frente al rival: {list(tbl.metrica)} (todas con dato de ambos)")
    check("Tiros" not in list(A.radar_vs_rival(veo, 7)[1].metrica), "Radar J7 frente al rival excluye Tiros (sin dato del rival)")
    check(list(A.load_seasons(APP_DIR / "data")) == ["2026/2027"], "Temporadas registradas: solo 2026/2027 (no se inventan otras)")
    # Cada herramienta avanzada se renderiza de verdad
    for tool, txt in [("Partido contra media", "cuatro referencias"), ("Análisis del rival", "Puntos por partido"),
                      ("Laboratorio", "Laboratorio de comparación"), ("Temporadas", "Comparador de temporadas"),
                      ("Radares", "Radares de rendimiento"), ("Primer Toque contra rival", "Primer Toque contra el rival"),
                      ("Casa PT vs rival fuera", "Media de Primer Toque en casa")]:
        at = nav("Análisis avanzado", tool=tool)
        check(not at.exception and txt in html_of(at), f"Herramienta «{tool}» renderizada" + (f": {at.exception[0].value[:100]}" if at.exception else ""))
    for metric, mode in [("Goles a favor", "Local frente a visitante"), ("Posesión", "Primer Toque frente al rival"),
                         ("Duelos", "Jornada frente a la media"), ("Tiros", "Jornada frente a jornada"), ("Puntos", "Temporada frente a temporada")]:
        def lab(a, metric=metric, mode=mode):
            a.selectbox(key="lab_metric").set_value(metric)
            a.button_group(key="lab_mode").set_value(mode)
            a.run()
        at = nav("Análisis avanzado", tool="Laboratorio", extra=lab)
        check(not at.exception, f"Laboratorio · {metric} · {mode}")


def test_datos_liga():
    """Datos de liga: sin duplicados, minutos coherentes, porteros, clasificación y nada perdido."""
    import subprocess, io
    import pandas as pd
    import team360_advanced as A
    D = APP_DIR / "data"
    part = pd.read_csv(D / "partidos_rivales.csv"); ev = pd.read_csv(D / "eventos_rivales.csv")
    mn = pd.read_csv(D / "minutos_rivales.csv"); al = pd.read_csv(D / "alineaciones_rivales.csv"); cl = pd.read_csv(D / "clasificacion_liga.csv")
    # Sin duplicados
    check(not part.duplicated(["jornada", "local", "visitante"]).any(), "Partidos sin duplicar")
    check(not ev.duplicated(["jornada", "equipo", "minuto", "tipo", "jugador"]).any(), "Eventos (goles y tarjetas) sin duplicar")
    _dup = mn[mn.duplicated(["equipo", "jornada", "jugador"], keep=False)]
    check(not (_dup.jornada == 8).any(), "Minutos J8: un registro por jugador")
    _old = sorted({f"{r.equipo} J{r.jornada} {r.jugador}" for r in _dup.itertuples() if r.jornada != 8})
    check(_old == ["Paterna C.F. 'A' J5 Oscar Rubio Montoro"], f"Duplicado histórico conocido (pendiente de revisar, no se modifica): {_old}")
    # Goles coherentes con el resultado, en cada partido y por cada lado
    bad = []
    for r in part.dropna(subset=["goles_local"]).itertuples():
        for team, gf, gc in ((r.local, r.goles_local, r.goles_visitante), (r.visitante, r.goles_visitante, r.goles_local)):
            e = ev[(ev.jornada == r.jornada) & (ev.equipo == team)]
            nf = e.tipo.isin(["gol", "penalti_gol"]).sum(); nc = e.tipo.isin(["gol_contra", "penalti_contra_gol"]).sum()
            if (nf or nc) and (nf != gf or nc != gc):
                bad.append(f"J{r.jornada} {team} {nf}-{nc} vs {int(gf)}-{int(gc)}")
    j8 = [b for b in bad if b.startswith("J8")]
    check(not j8, "J8: goles de cada equipo coinciden con el resultado" + (f": {j8}" if j8 else ""))
    # Minutos J8: 11 titulares y 990 menos los minutos perdidos por expulsión
    m8 = mn[mn.jornada == 8]
    tit_ok = (m8.groupby("equipo").titular.sum() == 11).all()
    check(len(m8) and tit_ok and (m8.minutos.between(0, 90)).all(), "J8: 11 titulares por equipo y minutos entre 0 y 90")
    # Porteros: cada gol encajado atribuido a un portero o marcado como pendiente (nunca perdido)
    t, pend = A.keeper_stats(mn, al, ev)
    tot = int(ev.tipo.isin(["gol_contra", "penalti_contra_gol"]).sum())
    check(int(t.gc.sum()) + len(pend) == tot, f"Porteros: {int(t.gc.sum())} goles atribuidos + {len(pend)} pendientes = {tot} encajados")
    jordi = t[(t.equipo == A.TEAM) & (t.jugador == "Jordi")]
    _j8 = ev[(ev.jornada == 8) & (ev.equipo == A.TEAM) & ev.tipo.eq("gol_contra")]
    t7, _ = A.keeper_stats(mn, al, ev, jmax=7)
    j7 = t7[(t7.equipo == A.TEAM) & (t7.jugador == "Jordi")]
    check(len(jordi) == 1 and len(j7) == 1 and int(jordi.pj.iloc[0]) == int(j7.pj.iloc[0]) + 1
          and int(jordi.gc.iloc[0]) == int(j7.gc.iloc[0]) + len(_j8) == 7,
          f"Jordi: J8 suma 1 partido y {len(_j8)} goles encajados (total {jordi[['pj', 'gc']].values.tolist()})")
    # Clasificación = resultados oficiales en todas las jornadas con puntos registrados
    p = part.dropna(subset=["goles_local"]); mism = []
    for j in sorted(cl.dropna(subset=["puntos"]).jornada.unique()):
        for r in cl[(cl.jornada == j)].dropna(subset=["puntos"]).itertuples():
            d = p[(p.jornada <= j) & ((p.local == r.equipo) | (p.visitante == r.equipo))]
            w = (((d.local == r.equipo) & (d.goles_local > d.goles_visitante)) | ((d.visitante == r.equipo) & (d.goles_visitante > d.goles_local))).sum()
            e = (d.goles_local == d.goles_visitante).sum()
            if 3 * w + e != r.puntos or len(d) != r.pj:
                mism.append(f"J{j} {r.equipo}")
    check(not mism, "Clasificación coincide con los resultados en todas las jornadas" + (f": {mism[:4]}" if mism else ""))
    played, expected, missing = A.jornada_status(part, 8)
    check(played == 8 and expected == 8 and not missing, f"J8 completa: {played}/{expected} partidos; pendientes {len(missing)} equipos")
    check(set(part[part.jornada == 8].local) | set(part[part.jornada == 8].visitante) == set(m8.equipo),
          "J8: minutos solo de los equipos que han jugado (no se inventan partidos)")
    # Rankings actualizados con J8
    sc = ev[ev.tipo.isin(["gol", "penalti_gol"])].groupby(["equipo", "jugador"]).size()
    check(sc.get(("C.D. Acero 'A'", "Aaron Madrid Garcia"), 0) >= 2 and sc.get((A.TEAM, "Ian"), 0) >= 1
          and sc.get(("Villarreal C.F. 'C'", "Gabriel Duarte Santacruz"), 0) >= 3, "Goleadores de J8 incorporados al ranking")
    # J9 (vídeo FFCV 09/11/2026): completa, sin duplicados, goles = resultado, 11 titulares, clasificación
    m9 = mn[mn.jornada == 9]
    check(not (_dup.jornada == 9).any() and not [b for b in bad if b.startswith("J9")], "J9: un registro por jugador y goles = resultado")
    check(len(m9) and (m9.groupby("equipo").titular.sum() == 11).all() and m9.minutos.between(0, 90).all()
          and len(al[al.jornada == 9]) == 176, "J9: 11 titulares por equipo y minutos entre 0 y 90")
    p9, e9, miss9 = A.jornada_status(part, 9)
    check(p9 == 8 and e9 == 8 and not miss9 and len(cl[cl.jornada == 9]) == 16, f"J9 completa: {p9}/{e9} partidos y clasificación de 16")
    g9 = ev[(ev.jornada == 9) & (ev.equipo == A.TEAM) & (ev.tipo == "gol")]
    check(sorted(g9.jugador) == ["Mois", "Pedro"] and int(g9[g9.jugador == "Pedro"].minuto.iloc[0]) == 90,
          f"J9: goles del Primer Toque = Mois 20' y Pedro 90' ({g9.jugador.tolist()})")
    # Nada perdido: todas las filas de la versión base siguen presentes
    root = APP_DIR.parent
    lost = []
    for f in ("partidos_rivales", "minutos_rivales", "eventos_rivales", "alineaciones_rivales", "clasificacion_liga", "plantillas_rivales"):
        try:
            old = subprocess.run(["git", "show", f"v15.12.84:futbol_streamlit/data/{f}.csv"], cwd=root, capture_output=True, check=True).stdout
        except Exception:
            continue
        o = pd.read_csv(io.BytesIO(old)).astype(str); n = pd.read_csv(D / f"{f}.csv").astype(str)
        o = o[[c for c in o.columns if c in n.columns]]
        miss = len(o.merge(n[o.columns].drop_duplicates(), how="left", indicator=True).query("_merge == 'left_only'"))
        if miss:
            lost.append(f"{f}: {miss}")
    check(not lost, "No se ha perdido ninguna fila de la versión base v15.12.84" + (f": {lost}" if lost else ""))


def test_infantil_d():
    """Infantil D: minutos del Excel, formaciones, vistas y datos independientes del Juvenil A."""
    import hashlib
    import pandas as pd
    import infantil_d as I
    D = APP_DIR / "data" / "infantil_d"
    wide = pd.read_csv(D / "minutos.csv", dtype=str).fillna("")
    check(len(wide) == 19 and list(wide.columns[2:]) == [f"J{i}" for i in range(1, 15)], f"Minutos: 19 jugadores y columnas J1–J14 como en el Excel ({len(wide)})")
    num = wide.iloc[:, 2:].replace("-", "0").apply(pd.to_numeric, errors="coerce")
    played = [c for c in num.columns if num[c].notna().any()]
    check(played == ["J1", "J2", "J3"] and all(int(num[c].sum()) == 770 for c in played),
          f"Jornadas con minutos {played}: cada una suma 770 (11 × 70'), igual que la fila TOTAL del Excel")
    tot = dict(zip(wide.jugador, num.sum(axis=1).astype(int)))
    expected = {"Alex Martinez": 140, "Alejandro": 210, "Oliver Ayala": 210, "Nico Becerra": 210, "Elian Cheta": 15, "Ali Oulad": 0, "Thiago": 65}
    check(all(tot[k] == v for k, v in expected.items()), "Totales por jugador iguales a la columna TOTAL (=SUMA) del Excel")
    jug, w2, part, form, long, jcols = I.data()
    th = long[(long.jugador == "Thiago") & (long.jornada.isin([1, 4]))].set_index("jornada")
    check(th.loc[1, "no_jugo"] and th.loc[1, "minutos"] == 0 and pd.isna(th.loc[4, "minutos"]),
          "«-» = no participó (0 explícito) y celda vacía = sin dato (no se convierte en 0)")
    ok = form[form.estado == "ok"].groupby(["jornada", "momento"]).size().to_dict()
    check(ok == {(1, "final"): 11, (1, "inicio"): 11, (2, "final"): 11, (2, "inicio"): 10},
          f"Formaciones del Excel: J1 11+11, J2 10+11 jugadores identificados ({ok})")
    pend = form[form.estado != "ok"]
    check(len(pend) == 1 and pend.texto_excel.iloc[0] == "SEBAS", "«SEBAS» (J2 inicio) queda pendiente: no figura en la plantilla")
    seg = pd.read_csv(D / "seguimiento_formaciones.csv").fillna("")
    sp = seg[(seg.jornada == 2) & (seg.momento == "inicio") & (seg.slot == "DC")]
    j1 = seg[(seg.jornada == 1) & (seg.momento == "inicio")].set_index("slot").jugador.to_dict()
    check(len(sp) == 1 and sp.jugador.iloc[0] == "" and j1.get("POR") == "Martin Ortiz" and j1.get("DC") == "Fabian Castillo",
          "Seguimiento precargado del Excel: J1 inicio (POR Martin Ortiz, DC Fabian Castillo) y J2 DC vacío")
    check(set(part.estado_formacion) == {"completa", "parcial", "pendiente"} and "JORNADA 3" in part.loc[part.jornada == 4, "notas"].iloc[0],
          "Estado de las jornadas: J1 completa, J2 parcial, J3–J4 pendientes (J4 con título «JORNADA 3»)")
    # Vistas y aislamiento de datos
    base = APP_DIR
    juv = [base / "muro.csv", base / "calendario.csv", APP_DIR / "data" / "seguimiento_formaciones.csv"]
    before = {f: hashlib.md5(f.read_bytes()).hexdigest() for f in juv if f.exists()}
    for view, txt in [("inicio", "Infantil D"), ("minutos", "Minutos · Infantil D"), ("seguimiento", "INFANTIL D"), ("muro", ""), ("calendario", "")]:
        at = run({"area": "infantil", "view": view})
        h = html_of(at)
        check(not at.exception and (txt in h if txt else True), f"Infantil D · {view} renderizado" + (f": {at.exception[0].value[:100]}" if at.exception else ""))
        if view == "minutos":
            check(len(at.get("plotly_chart")) >= 4 and h.count("<td class='n'>") == 20, "Minutos: tabla del Excel (19 jugadores + TOTAL) y 4 gráficos")
            check("Resumen liga" not in h, "Navegación de Infantil D sin apartados del Juvenil A")
    after = {f: hashlib.md5(f.read_bytes()).hexdigest() for f in juv if f.exists()}
    check(before == after, "Muro, Calendario y Seguimiento del Juvenil A intactos tras usar Infantil D")
    check((D / "muro.csv").exists() and (D / "calendario.csv").exists(), "Muro y Calendario del Infantil D en data/infantil_d (archivos propios)")


def test_navegacion():
    """Navegación entre equipos: portada en la raíz, menús separados y botón «Cambiar equipo»."""
    import re
    at = run({})
    h = html_of(at)
    home = " ".join(str(x.proto) for x in at.get("html"))
    areas = sorted(set(re.findall(r"\?area=(juvenil|infantil|cadete)", home)))
    check(not at.exception and "Selecciona tu equipo" in h and "pt-home-card" in home and areas == ["cadete", "infantil", "juvenil"],
          f"Raíz sin parámetros: portada con las tres tarjetas, Juvenil A, Infantil D y Cadete A ({areas})")
    css = " ".join(m.value for m in at.markdown)
    check("[data-testid=\"stSidebar\"]" in css and ".mobile-bottom-nav" in css and "display:none!important" in css,
          "Portada sin menús de equipo visibles (barra lateral y menú móvil ocultos; no hay redirección)")
    juv = ["inicio", "muro", "calendario", "liga", "rivales", "equipo", "seguimiento", "individual", "jugadores"]
    inf = ["inicio", "muro", "calendario", "resultados", "minutos", "seguimiento"]
    cad = ["inicio", "liga", "rivales", "equipo", "calendario", "muro"]
    for area, view, expected in (("juvenil", "liga", juv), ("infantil", "inicio", inf), ("cadete", "inicio", cad)):
        a = run({"area": area, "view": view})
        hh = html_of(a)
        side = re.search(r"<div class='side-nav-v3'>(.*?)</div>", hh, re.S)
        got = re.findall(r"href='\?area=(\w+)&view=(\w+)'", side.group(1)) if side else []
        check(not a.exception and [v for _, v in got] == expected and {x for x, _ in got} == {area},
              f"Menú de {area}: solo sus apartados {expected}")
        check("class='switch-team' href='?'" in hh and "class='tb-home' href='?'" in hh and "class='switch' href='?'" in hh,
              f"{area}: botón «Inicio / Cambiar equipo» en barra lateral, barra superior y menú móvil (vuelve a la raíz sin parámetros)")


def test_resultados_infantil():
    """Resultados del Infantil D: marcadores, goleadores y asistencias confirmados."""
    import pandas as pd
    import infantil_d as I
    res, ev = I.results_data()
    b = I.balance(res)
    r = res.set_index("jornada")
    check(r.loc[2, "goles_favor"] == 3 and r.loc[2, "goles_contra"] == 2 and r.loc[2, "rival"] == ""
          and r.loc[3, "rival"] == "San Lorenzo" and r.loc[3, "goles_favor"] == 2 == r.loc[3, "goles_contra"],
          "J2 victoria 3-2 (rival pendiente) y J3 empate 2-2 ante San Lorenzo")
    check(b == dict(pj=2, v=1, e=1, d=0, gf=5, gc=4, pts=4), f"Balance: {b}")
    g = ev[ev.tipo == "gol"].jugador.value_counts().to_dict()
    check(g == {"Alejandro": 2, "Fabian Castillo": 1, "Marc Capilla": 1, "Dani Lacasta": 1} and sum(g.values()) == b["gf"],
          f"Goleadores: 5 goles = goles a favor de los resultados ({g})")
    plantilla = set(pd.read_csv(APP_DIR / "data" / "infantil_d" / "jugadores.csv").jugador)
    check(set(ev.jugador) <= plantilla, "Goleadores y asistentes con el nombre exacto de la plantilla del Excel")
    check(ev[ev.tipo == "asistencia"].jugador.tolist() == ["Mauro"], "Asistencias: 1 (Mauro)")
    check(ev.minuto.isna().all(), "Minutos de gol sin registrar: no se inventan")
    at = run({"area": "infantil", "view": "resultados"})
    h = html_of(at)
    check(not at.exception and "3 – 2" in h and "2 – 2" in h and "Rival pendiente de identificar" in h and "0 de 5 goles" in h,
          "Vista Resultados: marcadores, rival pendiente y estado de los minutos")
    j = run({"area": "juvenil", "view": "jugadores"})
    check("Fabian Castillo" not in html_of(j), "Los jugadores del Infantil D no aparecen en Juvenil A")


def test_formaciones_infantil():
    """Seguimiento del Infantil D: recuperar del CSV y guardar (con restauración del archivo)."""
    f = APP_DIR / "data" / "infantil_d" / "seguimiento_formaciones.csv"
    juv = APP_DIR / "data" / "seguimiento_formaciones.csv"
    original, juv_before = f.read_bytes(), juv.read_bytes()
    try:
        a = run({"area": "infantil", "view": "seguimiento"}, lambda x: x.selectbox[0].set_value(1))
        h = " ".join(str(b.label) for b in a.button) + html_of(a)
        check(not a.exception and "Martin Ortiz" in h and "Fabian Castillo" in h, "J1 recuperada: Martin Ortiz y Fabian Castillo en el campo")
        a.button(key="copy_start_end_1").click().run()
        import pandas as pd
        d = pd.read_csv(f).fillna("")
        fin = d[(d.jornada == 1) & (d.momento == "final")].set_index("slot").jugador.to_dict()
        ini = d[(d.jornada == 1) & (d.momento == "inicio")].set_index("slot").jugador.to_dict()
        check(fin == ini and fin.get("DC") == "Fabian Castillo", "Guardar formación: el final de J1 se guarda en el CSV del Infantil D")
        check(juv.read_bytes() == juv_before, "El seguimiento del Juvenil A no cambia al guardar en Infantil D")
    finally:
        f.write_bytes(original)


def test_cadete_a():
    """Cadete A: 80 minutos, clasificación, goleadores, porteros, tramos, rivales y datos independientes."""
    import re
    import pandas as pd
    import cadete_a as C
    import league_core as lc
    from teams import TEAMS
    part, al, ev, mins, av = C.data()
    T = C.TEAM
    check(C.MM == 80 and TEAMS["cadete"]["match_minutes"] == 80 and TEAMS["juvenil"]["match_minutes"] == 90
          and TEAMS["infantil"]["match_minutes"] == 70, "Duración por equipo: Cadete A 80', Juvenil A 90', Infantil D 70'")
    at = run({})
    home = " ".join(str(x.proto) for x in at.get("html"))
    check(len(re.findall(r"img class=[^ ]*photo", home)) == 4 and "?area=scouting" in home
          and "object-fit:contain" in home and "OneDrive" not in home,
          "Portada: tres equipos + SCOUTING (object-fit: contain) incrustados desde el repositorio")
    check((APP_DIR / "cadete_a_portada.jpeg").exists(), "Foto del Cadete A en los recursos estáticos del proyecto")
    bad = []
    for r in part.itertuples():
        e = ev[(ev.jornada == r.jornada) & ev.equipo.isin([r.local, r.visitante])]
        gl = sum(lc.goal_side(x, r.local) == "favor" for _, x in e.iterrows())
        gv = sum(lc.goal_side(x, r.visitante) == "favor" for _, x in e.iterrows())
        if (gl, gv) != (r.goles_local, r.goles_visitante):
            bad.append(f"J{r.jornada} {r.local}")
    check(not bad and len(part) == 79 and len(part[part.jornada <= 7]) == 62, f"79 actas (J1–J9): cada marcador coincide con los goles del acta {bad[:3]}")
    p7 = part[part.jornada <= 7]
    tab = lc.standings(p7, C.teams_list(part))
    exp_pts = sum(3 if a != b else 2 for a, b in zip(p7.goles_local, p7.goles_visitante))
    check(tab.pts.sum() == exp_pts and tab.gf.sum() == tab.gc.sum() and (tab.pg + tab.pe + tab.pp == tab.pj).all(),
          "Clasificación: puntos, goles y partidos cuadran con los resultados")
    pt = tab[tab.equipo == T].iloc[0]
    got = (pt.pj, pt.pg, pt.pe, pt.pp, pt.gf, pt.gc, pt.pts)
    check(got == (7, 4, 1, 2, 14, 15, 13), f"Primer Toque hasta J7: 7 PJ, 4-1-2, 14-15, 13 pts {got}")
    m = mins.dropna(subset=["minutos"])
    check(m.minutos.max() == 80 and (m.minutos >= 0).all(), "Minutos por partido entre 0 y 80 (nunca 90)")
    tot = m.groupby(["equipo", "jornada"]).minutos.sum()
    check((tot <= 11 * 80).all(), "Ningún equipo suma más de 11 × 80 minutos en un partido")
    pa = lc.participation(mins[mins.jornada <= 7], T, 80, 7)
    r = pa[pa.jugador == "Pere Tomas Ribes"].iloc[0]
    check(r.minutos == 560 and round(r.pct) == 100, "Participación: 7 partidos completos = 560' = 100 % sobre 80'")
    toy = pd.DataFrame([dict(equipo="X", jornada=1, dorsal=1, jugador="A", minutos=40, titular=1)])
    check(round(lc.participation(toy, "X", 80, 1).pct.iat[0]) == 50, "40 minutos de 80 = 50 %")
    s7 = lambda d: d[d.jornada <= 7]  # cifras de control comprobadas a mano hasta la J7
    g, w = lc.goalkeepers(s7(al), s7(mins), s7(ev), s7(part), T, 80)
    check(int(g.encajados.sum()) == 15 and not w
          and all(abs(x.encajados / x.minutos * 80 - x.encajados_por_partido_reglamentario) < 1e-9 for x in g.itertuples()),
          "Porteros del Cadete A (J1–J7): 15 encajados atribuidos; GC por 80' = encajados ÷ minutos × 80")
    g2, w2 = lc.goalkeepers(al, mins, ev, part, "C.D. Castellón 'A'", 80)
    gc_cas = int(lc.standings(part, C.teams_list(part)).set_index("equipo").loc["C.D. Castellón 'A'"].gc)
    check(int(g2.encajados.sum()) == gc_cas - 2 and any("2 gol(es) encajado(s) sin portero atribuible" in x for x in w2),
          f"Castellón J3: dos porteros en el campo → 2 goles sin atribuir (no se inventa); {gc_cas - 2} de {gc_cas} atribuidos")
    labels = [b[2] for b in lc.minute_bins(80)]
    gb = lc.goals_by_bin(s7(ev), T, 80)
    check(labels[0] == "0–10" and labels[-1] == "70–80" and len(labels) == 8 and gb.a_favor.sum() == 14
          and gb.en_contra.sum() == 15 and lc.bin_label(83, 80) == "70–80+" and lc.bin_label(10, 80) == "0–10"
          and lc.bin_label(11, 80) == "10–20" and lc.bin_label(0, 80) == "0–10",
          "Tramos 0–10 … 70–80 (sin 80–90): (lo, hi], el 10' en 0–10 y el añadido en 70–80+ conservando el minuto")
    sc = lc.scorers(ev, mins)
    check(not sc.duplicated(["equipo", "jugador"]).any() and sc.goles.sum() == int(ev.tipo.isin(lc.GOAL_TYPES_FOR).sum()),
          "Goleadores: una fila por jugador y equipo; propia puerta por separado")
    errs = []
    full = lc.standings(part, C.teams_list(part)).set_index("equipo")
    for t in C.teams_list(part):
        tm = lc.team_matches(part, t)
        if (tm.gf.sum(), tm.gc.sum(), tm.puntos.sum()) != (full.loc[t].gf, full.loc[t].gc, full.loc[t].pts):
            errs.append(t)
    check(not errs and len(full) == 18, f"18 equipos: ficha de cada rival coherente con la clasificación {errs}")
    src = (APP_DIR / "app.py").read_text(encoding="utf-8")
    check('DATA / "cadete_a" / "muro.csv"' in src and 'DATA / "cadete_a" / "calendario.csv"' in src
          and 'DATA / "cadete_a" / "muro_adjuntos"' in src, "Muro, calendario y adjuntos propios del Cadete A (data/cadete_a/)")
    for v in ("inicio", "liga", "rivales", "equipo", "estadisticas", "calendario", "muro"):
        a = run({"area": "cadete", "view": v})
        hh = html_of(a)
        check(not a.exception and "CADETE A" in hh, f"Cadete A · {v}: sin errores y con su propia cabecera")
    a = run({"area": "cadete", "view": "liga"})
    hh = html_of(a)
    jlast = int(part.jornada.max())
    check(a.selectbox[0].value == f"J{jlast}" and f"J1–J{jlast}" in hh and "Lucas Serra" in hh and "Marc Menezo Perez" in hh,
          f"Resumen de liga del Cadete A abre en la última jornada (J{jlast}) con sus goleadores y porteros")
    src = (APP_DIR / "app.py").read_text(encoding="utf-8")
    check('_league_snapshot(jmax, LG["key"], _league_data_stamp())' in src,
          "Resumen de liga: el caché se renueva cuando cambian los CSV de la liga (no se quedan jornadas antiguas)")
    check("Resumen de liga · Cadete A" in hh and "Lliga Autonòmica Cadet" in hh and "GC/80" in hh and "GC/90" not in hh
          and "70–80" in hh and "75–90" not in hh and "Comparador de equipos" not in hh and "Equipo · Cadete A" not in hh,
          "Resumen de liga del Cadete A: componentes del Juvenil A con 80' y tramos de 10', sin los análisis propios del equipo")
    for v in ("equipo", "estadisticas"):
        a = run({"area": "cadete", "view": v})
        hh = html_of(a)
        check(not a.exception and "Equipo · Cadete A" in hh and "Comparador de equipos" in hh and "Estadísticas del Cadete A" in hh
              and "GC/90" not in hh and hh.count("Comparador de equipos") == 1,
              f"Cadete A · {v}: Equipo con evolución, comparador y estadísticas propias (una sola vez)")
    test_cadete_rivales_y_escudos()


def test_cadete_rivales_y_escudos():
    """Cadete A: ficha de Rivales del Juvenil A con datos del Cadete A, escudos y archivos de liga."""
    import pandas as pd
    import crests
    import team360_advanced as A
    L = APP_DIR / "data" / "cadete_a" / "liga"
    part = pd.read_csv(L / "partidos_rivales.csv"); ev = pd.read_csv(L / "eventos_rivales.csv")
    mins = pd.read_csv(L / "minutos_rivales.csv"); al = pd.read_csv(L / "alineaciones_rivales.csv")
    goals = int(part.goles_local.sum() + part.goles_visitante.sum())
    check(int(ev.tipo.isin(["gol", "penalti_gol"]).sum()) == goals == int(ev.tipo.isin(["gol_contra", "penalti_contra_gol"]).sum()),
          f"Liga del Cadete A en formato Juvenil A: {goals} goles = goles marcados = goles encajados en los eventos")
    juv = set(pd.read_csv(APP_DIR / "data" / "equipos_liga.csv", encoding="utf-8-sig").equipo)
    cad = set(pd.read_csv(L / "equipos_liga.csv").equipo)
    check(len(cad) == 18 and not (cad & juv) - {"Primer Toque C.F. 'A'", "C.F. Torre Levante 'A'"},
          "Equipos del Cadete A propios (solo comparten nombre con el Juvenil A Primer Toque y Torre Levante)")
    check(set(al.rol) <= {"POR", "DEF", "MED", "ATA"} and al.groupby(["equipo", "jornada"]).size().eq(11).all(),
          "Alineaciones: 11 titulares por equipo y partido con los roles del Juvenil A")
    t, pend = A.keeper_stats(mins, al, ev, match_minutes=80)
    t7, _ = A.keeper_stats(mins[mins.jornada <= 7], al[al.jornada <= 7], ev[ev.jornada <= 7], match_minutes=80)
    pt = t7[t7.equipo == "Primer Toque C.F. 'A'"]
    check(int(pt.gc.sum()) == 15 and (abs(t.gc * 80 / t.minutos - t.gc90) < 1e-9).all()
          and t.minutos.max() <= 80 * int(part.jornada.max()),
          "Porteros (cálculo del Juvenil A con 80'): Primer Toque 15 GC hasta J7; GC por 80' = GC × 80 ÷ minutos")
    pt_all = t[t.equipo == "Primer Toque C.F. 'A'"]
    ptm = part[(part.local == "Primer Toque C.F. 'A'") | (part.visitante == "Primer Toque C.F. 'A'")]
    gc_all = int(ptm.apply(lambda r: r.goles_visitante if r.local == "Primer Toque C.F. 'A'" else r.goles_local, axis=1).sum())
    check(int(pt_all.gc.sum()) == gc_all == 18, f"Porteros J1–J9: los {gc_all} goles encajados por Primer Toque atribuidos a sus porteros")
    t90, _ = A.keeper_stats(pd.read_csv(APP_DIR / "data" / "minutos_rivales.csv"), pd.read_csv(APP_DIR / "data" / "alineaciones_rivales.csv"),
                            pd.read_csv(APP_DIR / "data" / "eventos_rivales.csv"))
    check(not t90.empty and (abs(t90.gc * 90 / t90.minutos - t90.gc90) < 1e-9).all(), "Juvenil A: porteros siguen por 90' (valor por defecto)")
    missing = [x for x in cad | juv if not crests.has_crest(x)]
    check(not missing, f"Escudo verificado para los 34 equipos de las dos ligas {missing}")
    same = crests.crest_path("Villarreal C.F. 'A'") == crests.crest_path("Villarreal C.F. 'C'")
    diff = len({crests.crest_path(x) for x in ("Levante U.D. 'A'", "C.F. Torre Levante 'A'")}) == 2 and         len({crests.crest_path(x) for x in ("Elche C.F. 'A'", "Celtic Elche C.F. 'A'", "S.C.D. Intangco 'A'")}) == 3 and         crests.crest_path("Valencia C.F. 'A'") != crests.crest_path("C.F. Fundació VCF 'A'")
    check(same and diff and not crests.has_crest("Equipo inventado 'Z'"),
          "Escudos: mismo club → mismo archivo; clubes parecidos → escudos distintos; sin escudo → marcador neutro")
    for team in ("Valencia C.F. 'A'", "Primer Toque C.F. 'A'", "C.D. Roda 'A'"):
        a = run({"area": "cadete", "view": "rivales", "team": team})
        hh = html_of(a)
        check(not a.exception and "partidos de 80'" in hh and "GC/80" in hh and "70–80+'" in hh and "Goles / 90" not in hh
              and "GC/90" not in hh and "ANÁLISIS REAL" in hh and "Partidos analizados · actas FFCV" in hh
              and len(a.get("download_button")) == 1, f"Rivales del Cadete A · {team}: ficha del Juvenil A a 80' con botón de informe PDF")
    test_pdf_cadete()
    a = run({"area": "juvenil", "view": "rivales", "team": "Bétera C.F. 'A'"})
    hh = html_of(a)
    check(not a.exception and "GC/90" in hh and "76–90+'" in hh and a.get("download_button"),
          "Juvenil A sin cambios: GC/90, tramos de 15' y PDF del rival")


def test_pdf_cadete():
    """Informe PDF de rival: mismo generador del Juvenil A, adaptado al Cadete A (80', 10', 18 equipos)."""
    import re
    import pandas as pd
    import pdf_export_v63 as P
    try:
        import pymupdf  # solo para leer el texto del PDF en la prueba (pip install pymupdf)
    except ImportError:
        print("AVISO pymupdf no instalado: se omite la lectura del PDF del Cadete A")
        return
    L = APP_DIR / "data" / "cadete_a" / "liga"
    rd = lambda n: pd.read_csv(L / n)
    args = [rd(n) for n in ("partidos_rivales.csv", "minutos_rivales.csv", "eventos_rivales.csv", "clasificacion_liga.csv",
                            "alineaciones_rivales.csv", "plantillas_rivales.csv")]
    bins = [(i, i + 10) for i in range(0, 80, 10)]
    per = [f"{a}–{b}’" for a, b in bins[:-1]] + ["70–80+’"]
    bad = []
    for t in rd("equipos_liga.csv").equipo:
        d = pymupdf.open(stream=P.generate(t, *args, match_minutes=80, bins=bins, period_labels=per,
                                           league_label="Lliga Autonòmica Cadet · Grup Únic", show_videos=False))
        txt = " ".join(p.get_text() for p in d)
        if len(d) != 4 or re.search(r"90[’']|/90|–90|0–15|Vídeos de los partidos", txt) or "70–80+" not in txt                 or "Partidos de 80" not in txt or "Lliga Autonòmica Cadet" not in txt:
            bad.append(t)
    check(not bad, f"PDF del Cadete A para los 18 equipos: 4 páginas, 80', tramos 0–10 … 70–80+, sin vídeos {bad}")
    J = APP_DIR / "data"
    jargs = [pd.read_csv(J / n, encoding="utf-8-sig") for n in ("partidos_rivales.csv", "minutos_rivales.csv", "eventos_rivales.csv",
                                                                 "clasificacion_liga.csv", "alineaciones_rivales.csv", "plantillas_rivales.csv")]
    txt = " ".join(p.get_text() for p in pymupdf.open(stream=P.generate("Bétera C.F. 'A'", *jargs)))
    check("Lliga Comunitat Juvenil · Nord" in txt and "76–90+" in txt and "Vídeos de los partidos" in txt,
          "PDF del Juvenil A sin cambios: liga juvenil, tramos de 15' y vídeos")


def main():
    for t in (test_atributos, test_navegacion, test_cadete_a, test_datos_liga, test_infantil_d, test_resultados_infantil, test_formaciones_infantil, test_equipo360, test_avanzado, test_otras_vistas, test_modulo_obsoleto):
        print(f"\n— {t.__doc__.splitlines()[0] if t.__doc__ else t.__name__}")
        try:
            t()
        except Exception as e:  # una excepción en la propia prueba también es un fallo
            check(False, f"{t.__name__} lanzó {type(e).__name__}: {e}")
    print(f"\n{len(fallos)} comprobaciones fallidas" if fallos else "\nTodas las comprobaciones de integridad superadas")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
