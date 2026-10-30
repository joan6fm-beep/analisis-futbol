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


def test_equipo360():
    at = run({"area": "juvenil", "view": "equipo"})
    check(not at.exception, "Equipo 360 sin excepciones" + (f": {at.exception[0].value[:120]}" if at.exception else ""))
    h = html_of(at)
    for txt in ["1 · Resumen de rendimiento", "Panel de rendimiento", "Posesión media", "Precisión de pase",
                "Intentos dentro del área", "Lectura rápida", "Producción por jornada", "Radiografía del juego",
                "Comparador de rendimiento", "Todas las métricas", "Pendiente de revisión"]:
        check(txt in h or any(txt in c.value for c in at.caption), f"Equipo 360 muestra «{txt}»")
    check("58%" in h and "65%" in h, "Indicadores medios con valores reales (posesión 58%, precisión 65%)")
    tabs = [t.label for t in at.tabs]
    check(len(tabs) == 6 and tabs[0].startswith("2") and tabs[-1].startswith("7"), f"6 pestañas de bloques 2–7: {tabs}")
    charts = at.get("plotly_chart")
    check(len(charts) >= 15, f"Gráficos Plotly renderizados: {len(charts)} (mínimo 15)")
    df = at.dataframe[0].value if at.dataframe else None
    check(df is not None and {"J2 Bétera", "J3 Manises", "J5 Alboraya", "J7 Salesianos"} <= set(df.columns),
          "Tabla completa con columnas J2, J3, J5 y J7")
    if df is not None:
        pos = df[df["Métrica"].str.startswith("Posesión")].iloc[0]
        check(pos["J2 Bétera"] == "67% · 33%" and pos["J7 Salesianos"] == "41% · 59%", "Posesión J2 67·33 y J7 41·59 en la tabla")
        duel = df[df["Métrica"].str.startswith("Duelos")].iloc[0]
        check(duel["J3 Manises"] == "124", "Duelos J3 = 124 (sin valor rival inventado)")
    metrics = {m.label: m.value for m in at.metric}
    check(metrics.get("Media Primer Toque") == "57.8" and metrics.get("Media rivales") == "42.2",
          f"Comparador por defecto (Posesión): {metrics}")
    at1 = run({"area": "juvenil", "view": "equipo"}, lambda a: a.selectbox(key="v83_metric").set_value("Tiros"))
    m1 = {m.label: m.value for m in at1.metric}
    check(m1 == {"Media Primer Toque": "13.2", "Media rivales": "11.0", "Diferencia comparable": "+2.3"}, f"Comparador con Tiros: {m1}")
    # Interacción: métrica propia de PT y comparación entre dos jornadas
    def interact(a):
        a.selectbox(key="v83_metric").set_value("Duelos")
        a.radio(key="v83_view").set_value("Comparar dos jornadas")
    at2 = run({"area": "juvenil", "view": "equipo"}, interact)
    m2 = {m.label: m.value for m in at2.metric}
    check(not at2.exception and m2.get("Mejor partido") == "124", f"Comparador con Duelos y dos jornadas: {m2}")
    check("cmp-table" in html_of(at2), "Tabla de comparación entre dos jornadas renderizada")


def test_otras_vistas():
    at = run({})
    check(not at.exception and "Selecciona tu equipo" in html_of(at), "Portada con selección de equipo")
    at = run({"area": "juvenil", "view": "rivales", "team": "Bétera C.F. 'A'"})
    check(not at.exception and len(at.get("plotly_chart")) >= 1 and at.get("download_button"),
          "Rivales: evolución de la clasificación (Plotly) y botón PDF")
    at = run({"area": "juvenil", "view": "jugadores", "player": "Bilal"})
    check(not at.exception and len(at.get("plotly_chart")) >= 2, "Ficha de jugador: minutos y evolución física")


def test_avanzado():
    """Análisis avanzado: medias recalculadas desde los CSV y radares sin valores inventados."""
    import pandas as pd
    import team360_advanced as A
    import team360_charts as T
    part = pd.read_csv(APP_DIR / "data" / "partidos_rivales.csv")
    adv = pd.read_csv(APP_DIR / "data" / "equipo_avanzado.csv")
    veo = T.prepare(adv[adv.jornada.isin([2, 3, 5, 7])], lambda x: x)
    pt = A.team_matches(part, A.TEAM)
    check(len(pt) == 7 and int(pt.pts.sum()) == 6, f"Primer Toque: 7 partidos y 6 puntos ({len(pt)}, {int(pt.pts.sum())})")
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
    # Cada modo se renderiza de verdad
    for mode, txt in [("Preparar partido", "cuatro referencias"), ("Análisis del rival", "Puntos por partido"),
                      ("Laboratorio", "Laboratorio de comparación"), ("Temporadas", "Comparador de temporadas")]:
        at = run({"area": "juvenil", "view": "equipo"}, lambda a: a.button_group(key="adv_mode").set_value(mode))
        check(not at.exception and txt in html_of(at), f"Modo «{mode}» renderizado" + (f": {at.exception[0].value[:100]}" if at.exception else ""))
    def lab(a):
        a.button_group(key="adv_mode").set_value("Laboratorio")
    for metric, mode in [("Goles a favor", "Local frente a visitante"), ("Posesión", "Primer Toque frente al rival"),
                         ("Duelos", "Jornada frente a la media"), ("Tiros", "Jornada frente a jornada"), ("Puntos", "Temporada frente a temporada")]:
        at = run({"area": "juvenil", "view": "equipo"}, lab)
        at.selectbox(key="lab_metric").set_value(metric); at.button_group(key="lab_mode").set_value(mode); at.run()
        check(not at.exception, f"Laboratorio · {metric} · {mode}")


def main():
    for t in (test_atributos, test_equipo360, test_avanzado, test_otras_vistas, test_modulo_obsoleto):
        print(f"\n— {t.__doc__.splitlines()[0] if t.__doc__ else t.__name__}")
        try:
            t()
        except Exception as e:  # una excepción en la propia prueba también es un fallo
            check(False, f"{t.__name__} lanzó {type(e).__name__}: {e}")
    print(f"\n{len(fallos)} comprobaciones fallidas" if fallos else "\nTodas las comprobaciones de integridad superadas")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
