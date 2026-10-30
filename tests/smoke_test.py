"""Prueba de humo: abre cada vista de la app y comprueba que no lanza excepciones.

Uso (desde la raíz del repositorio):

    python tests/smoke_test.py

Prueba la portada, Infantil D, los módulos de Juvenil A, los 16 rivales
(incluido el botón de descarga del PDF) y la ficha de cada jugador. Devuelve código 1 si alguna vista falla.
No escribe en los CSV. Ejecutar junto con futbol_streamlit/validar_datos.py
antes de cada push. Al final ejecuta también tests/test_integridad.py
(atributos entre módulos, módulos obsoletos en memoria y renderizado real).
"""
import logging
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

import pandas as pd
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "futbol_streamlit" / "app.py"
VISTAS_JUVENIL = ["inicio", "muro", "calendario", "liga", "equipo",
                  "seguimiento", "individual", "jugadores"]

logging.getLogger("streamlit").setLevel(logging.ERROR)


def casos():
    equipos = pd.read_csv(APP.parent / "data" / "equipos_liga.csv",
                          encoding="utf-8-sig")["equipo"].tolist()
    yield "Portada (selección de equipo)", {}
    yield "Infantil D", {"area": "infantil"}
    for v in VISTAS_JUVENIL:
        yield f"Juvenil A · {v}", {"area": "juvenil", "view": v}
    for t in equipos:
        yield f"Rivales · {t}", {"area": "juvenil", "view": "rivales", "team": t}
    pl = pd.read_csv(APP.parent / "data" / "plantillas_rivales.csv")
    pl = pl[(pl.equipo == "Primer Toque C.F. 'A'") & (pl.jugador.astype(str).str.lower() != "fran")]
    for j in pl.jugador.drop_duplicates():
        yield f"Jugador · {j}", {"area": "juvenil", "view": "jugadores", "player": j}


def main():
    total = fallos = 0
    for nombre, qp in casos():
        at = AppTest.from_file(str(APP), default_timeout=120)
        for k, v in qp.items():
            at.query_params[k] = v
        t0 = time.time()
        try:
            at.run()
            errs = [e.value for e in at.exception]
        except Exception as e:  # fallo al ejecutar la vista
            errs = [repr(e)]
        if "Rivales" in nombre and not errs and not at.get("download_button"):
            errs = ["Falta el botón de descarga del PDF"]
        total += 1
        fallos += bool(errs)
        print(f"{'ERROR' if errs else 'OK':5} {time.time() - t0:5.1f}s  {nombre}")
        for e in errs:
            print("      ", str(e)[:300])
    print(f"\n{total} vistas probadas, {fallos} con error")
    # Además de arrancar, los componentes principales deben renderizarse bien.
    sys.path.insert(0, str(Path(__file__).parent))
    import test_integridad
    print("\n== Integridad de módulos y renderizado ==")
    return 1 if (test_integridad.main() or fallos) else 0


if __name__ == "__main__":
    sys.exit(main())
