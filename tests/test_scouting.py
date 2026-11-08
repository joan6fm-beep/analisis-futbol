"""Pruebas de SCOUTING FFCV: estructura oficial, importación idempotente, N/D y datos de menores.

Los datos de importación son un archivo de prueba en una carpeta temporal: nunca tocan data/scouting.
"""
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "futbol_streamlit"))
import scouting_data as sd  # noqa: E402

HTML = """<html><head><title>Equipo prueba</title></head><body><h1>PRUEBA</h1>
<a href="equipo.php?cod_equipo=999">x</a><table>
<tr><th>Dorsal</th><th>Jugador</th><th>Posición</th><th>Edad</th><th>Convocatorias</th><th>Titular</th>
<th>Suplente</th><th>Jugados</th><th>Goles</th><th>Amarillas</th><th>Dobles amarillas</th><th>Rojas</th></tr>
<tr><td>9</td><td><a href="j.php?cod_jugador=111">Ana Prueba</a></td><td>Delantera</td><td>13</td><td>6</td><td>4</td>
<td>2</td><td>6</td><td>3</td><td>1</td><td>0</td><td>0</td></tr>
<tr><td>5</td><td>Beto Prueba</td><td></td><td>-</td><td>5</td><td>0</td><td>3</td><td>3</td><td>0</td><td></td><td>0</td><td>0</td></tr>
</table></body></html>"""


def main():
    fallos = []

    def check(cond, msg):
        print(("OK   " if cond else "FALLO"), msg)
        if not cond:
            fallos.append(msg)

    eq = sd.load("equipos")
    gr = sd.load("grupos")
    check(len(gr) == 6, f"6 grupos oficiales 2026/27 (hay {len(gr)})")
    check(len(eq) == 83 and eq.equipo_id.is_unique, f"83 equipos sin duplicados (hay {len(eq)})")
    check(any("PRIMER TOQUE CF D" == n for n in eq.nombre), "Primer Toque CF D presente")

    orig_dir, orig_fuente = sd.DIR, sd.FUENTE
    tmp = Path(tempfile.mkdtemp())
    try:
        for f in orig_dir.glob("*.csv"):
            shutil.copy(f, tmp / f.name)
        sd.DIR, sd.FUENTE = tmp, tmp / "fuente"
        eid = sd.load("equipos").equipo_id.iloc[0]
        r = sd.importar(eid, "prueba.html", HTML.encode())
        check(r["ok"] and r["jugadores"] == 2, "Importa 2 jugadores de una tabla HTML")
        sd.importar(eid, "prueba.html", HTML.encode())
        df = sd.tabla_jugadores()
        check(len(df) == 2, "Reimportar no duplica jugadores ni estadísticas")
        a = df[df.nombre == "Ana Prueba"].iloc[0]
        b = df[df.nombre == "Beto Prueba"].iloc[0]
        check(a.jugador_id == "ffcv-111", "Usa el código FFCV del jugador como id estable")
        check(a.goles == 3 and abs(a.pct_titular - 66.67) < .1 and abs(a.goles_partido - .5) < 1e-9, "Métricas derivadas")
        check(sd.pd.isna(b.amarillas) and sd.pd.isna(b.edad), "Celdas vacías o '-' quedan N/D (no 0)")
        check(sd.pd.isna(a.verdes), "Columna ausente (verdes) queda N/D")
        check(a.anio_verificado == "no" and not a.anio_nacimiento, "Con solo la edad, el año de nacimiento no se deduce")
        check(sd.pd.isna(a.pct_sin_sancion), "% sin sanción N/D sin datos por jornada")
        check(sd.load("equipos").set_index("equipo_id").cod_ffcv[eid] == "999", "Guarda el código FFCV del equipo")
        csv = "Jugador;Fecha nacimiento;Convocatorias\nCarla Prueba;15/03/2013;4\n".encode()
        eid2 = sd.load("equipos").equipo_id.iloc[1]
        sd.importar(eid2, "p.csv", csv)
        c = sd.load("jugadores").set_index("nombre").loc["Carla Prueba"]
        check(c.anio_nacimiento == "2013" and c.anio_verificado == "si", "Fecha publicada -> año verificado")
        txt = "".join(p.read_text(encoding="utf-8") for p in tmp.glob("*.csv"))
        check("15/03/2013" not in txt and "2013-03-15" not in txt, "No se guarda la fecha de nacimiento completa")
        r2 = sd.actualizar_desde_fuente()
        check(r2["nuevos"] == 0 and r2["sin_cambios"] == 2, "«Actualizar FFCV» no reprocesa archivos sin cambios")
        sd.borrar_importacion_equipo(eid)
        check(len(sd.tabla_jugadores()) == 1, "Borrar la importación de un equipo")
    finally:
        sd.DIR, sd.FUENTE = orig_dir, orig_fuente
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nScouting: {len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
