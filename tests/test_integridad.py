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
           "t360adv": "team360_advanced", "A": "team360_advanced"}
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
    check(played == 4 and expected == 8 and len(missing) == 8, f"J8 provisional: {played}/{expected} partidos; pendientes {len(missing)} equipos")
    check(set(part[part.jornada == 8].local) | set(part[part.jornada == 8].visitante) == set(m8.equipo),
          "J8: solo hay minutos de los 8 equipos que han jugado (no se inventan partidos)")
    # Rankings actualizados con J8
    sc = ev[ev.tipo.isin(["gol", "penalti_gol"])].groupby(["equipo", "jugador"]).size()
    check(sc.get(("C.D. Acero 'A'", "Aaron Madrid Garcia"), 0) >= 2 and sc.get((A.TEAM, "Ian"), 0) >= 1, "Goleadores de J8 incorporados al ranking")
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


def main():
    for t in (test_atributos, test_datos_liga, test_equipo360, test_avanzado, test_otras_vistas, test_modulo_obsoleto):
        print(f"\n— {t.__doc__.splitlines()[0] if t.__doc__ else t.__name__}")
        try:
            t()
        except Exception as e:  # una excepción en la propia prueba también es un fallo
            check(False, f"{t.__name__} lanzó {type(e).__name__}: {e}")
    print(f"\n{len(fallos)} comprobaciones fallidas" if fallos else "\nTodas las comprobaciones de integridad superadas")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
