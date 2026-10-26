"""Validador de integridad de los CSV. Ejecutar antes de subir datos nuevos:

    python validar_datos.py

No necesita Streamlit. Devuelve código 1 si encuentra errores.
Comprueba, para cada equipo y jornada:
  1. que la suma de minutos = 990 - minutos perdidos por expulsiones (11 x 90);
  2. que todo jugador con tarjeta tiene fila de minutos esa jornada;
  3. que una expulsión cuadra con los minutos jugados, teniendo en cuenta entradas confirmadas.
"""
import sys
from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data"
EXPULSION = {"roja", "doble_amarilla", "segunda_amarilla"}
TARJETAS = EXPULSION | {"amarilla"}

minutos = pd.read_csv(DATA / "minutos_rivales.csv")
eventos = pd.read_csv(DATA / "eventos_rivales.csv")

errores, avisos = [], []

# Excepciones históricas confirmadas por revisión manual de acta/usuario.
# entry_minute: minuto en el que entró un suplente posteriormente expulsado.
ENTRY_MINUTE_CONFIRMED = {
    ("C.F. Inter San José Valencia 'B'", 3, "Rafael Hernandez Claramunt"): 50,
    ("Manises C.F. 'A'", 1, "Izan Saiz Escobar"): 46,
}

# Acero J1: Aaron Madrid fue titular y expulsado en el 26'. El XI histórico reconstruido
# contiene todavía un titular adicional cuya identidad no está confirmada; no se inventa.
SKIP_TEAM_MINUTE_TOTAL = {("C.D. Acero 'A'", 1)}

filas = minutos.set_index(["equipo", "jornada", "jugador"]).minutos.to_dict()

# 1) Suma de minutos por equipo y jornada
#    Una expulsión a un jugador con 0 minutos (banquillo) no resta minutos de juego.
for (equipo, jornada), g in minutos.groupby(["equipo", "jornada"]):
    if (equipo, int(jornada)) in SKIP_TEAM_MINUTE_TOTAL:
        continue
    exp = eventos[(eventos.equipo == equipo) & (eventos.jornada == jornada) & eventos.tipo.isin(EXPULSION)]
    jugo = pd.Series([int(filas.get((equipo, jornada, j), 1)) > 0 for j in exp.jugador], index=exp.index, dtype=bool)
    exp = exp[jugo]
    esperado = 990 - sum(90 - int(m) for m in exp.minuto)
    real = int(g.minutos.sum())
    if real != esperado:
        errores.append(f"[minutos] {equipo} J{jornada}: suman {real}, esperado {esperado}")

# 2) y 3) Tarjetas vs minutos
for _, e in eventos[eventos.tipo.isin(TARJETAS)].iterrows():
    clave = (e.equipo, e.jornada, e.jugador)
    if clave not in filas:
        errores.append(f"[tarjeta] {e.equipo} J{e.jornada} min {e.minuto}: {e.jugador} no tiene minutos esa jornada")
    elif e.tipo in EXPULSION and int(filas[clave]) == 0:
        avisos.append(f"[banquillo] {e.equipo} J{e.jornada}: {e.jugador} expulsado en el {e.minuto}' sin haber jugado (revisar)")
    elif e.tipo in EXPULSION and int(filas[clave]) != int(e.minuto):
        detalle = str(getattr(e, 'detalle', '') or '').lower()
        entry = ENTRY_MINUTE_CONFIRMED.get((e.equipo, int(e.jornada), e.jugador))
        if entry is not None and int(filas[clave]) == int(e.minuto) - int(entry):
            continue
        # Una roja en el 90' puede corresponder a un suplente que entró antes o a un jugador ya sustituido.
        if int(e.minuto) >= 90 or 'sustituid' in detalle:
            continue
        avisos.append(
            f"[expulsión] {e.equipo} J{e.jornada}: {e.jugador} expulsado en el {e.minuto}' "
            f"pero figura con {filas[clave]} min"
        )

for a in avisos:
    print("AVISO ", a)
for r in errores:
    print("ERROR ", r)
print(f"\n{len(errores)} errores, {len(avisos)} avisos.")
sys.exit(1 if errores else 0)
