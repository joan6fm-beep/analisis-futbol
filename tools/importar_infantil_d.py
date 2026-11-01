"""Importa el Excel de seguimiento del Infantil D a CSV para la app.

Uso (desde la raíz del repositorio; necesita openpyxl, solo en local):

    python tools/importar_infantil_d.py "ruta/al/SEGUIMIENTO INFANTIL D ... .xlsx"

Genera en futbol_streamlit/data/infantil_d/:
- jugadores.csv           plantilla (dorsal, jugador, año, demarcación) de la hoja J1
- minutos.csv             hoja «Minutos» tal cual: jugadores en filas, J1..J14 en columnas.
                          «-» = no participó (explícito en el Excel); vacío = jornada sin dato.
- partidos.csv            cabecera de cada hoja de jornada (fecha, texto del partido, sistemas)
- formaciones_excel.csv   jugadores colocados en el campo de cada hoja (celda de origen incluida)
- seguimiento_formaciones.csv  formaciones iniciales para el apartado Seguimiento.
                          Solo se crea si NO existe: nunca sobrescribe lo editado en la app.
"""
import csv
import sys
from datetime import datetime
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "futbol_streamlit" / "data" / "infantil_d"
MATCH_MINUTES = 70  # fila TOTAL del Excel: 770 = 11 jugadores × 70 minutos

# Nombre corto usado en el campo del Excel -> jugador de la plantilla.
SHORT = {"MARTIN": "Martin Ortiz", "OLIVER": "Oliver Ayala", "DANI": "Dani Lacasta", "ALBESA": "Marc Albesa",
         "ELIAN": "Elian Cheta", "NICO": "Nico Becerra", "ALEJANDRO": "Alejandro", "ALE": "Alejandro", "MAURO": "Mauro",
         "IKER": "Iker Castillo", "BONET": "Alex Bonet", "FABI": "Fabian Castillo", "SERGI": "Sergi Cobos", "ANDER": "Ander",
         "DIEGO": "Diego", "MARC CAPILLA": "Marc Capilla", "RAUL": "Raul Montoro", "ALEX": "Alex Martinez", "THIAGO": "Thiago"}

# Casilla del Excel -> puesto de la plantilla táctica de la app, por sistema.
# Filas relativas al bloque (0 = fila del portero) y columnas F..L.
SLOTS = {
    "1-4-3-3": {(0, "I"): "POR", (2, "H"): "DFC-I", (2, "J"): "DFC-D", (3, "F"): "LI", (3, "L"): "LD",
                (5, "I"): "MC", (8, "H"): "MC-I", (8, "J"): "MC-D", (10, "F"): "EI", (10, "L"): "ED", (12, "I"): "DC"},
    "1-3-4-2-1": {(0, "I"): "POR", (3, "G"): "DFC-I", (3, "I"): "DFC", (3, "K"): "DFC-D",
                  (7, "H"): "MC-I", (7, "J"): "MC-D", (8, "F"): "CAI", (8, "L"): "CAD",
                  (10, "H"): "MP-I", (10, "J"): "MP-D", (12, "I"): "DC"},
}


def write(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


def main(xlsx):
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    OUT.mkdir(parents=True, exist_ok=True)

    # Plantilla (hoja J1, filas 6..)
    ws = wb["J1"]
    players = []
    for r in range(6, 40):
        d, n = ws.cell(r, 1).value, ws.cell(r, 2).value
        if d is None or not n:
            continue
        players.append([int(d), str(n).strip(), int(ws.cell(r, 3).value or 0) or "", str(ws.cell(r, 4).value or "").strip()])
    write(OUT / "jugadores.csv", ["dorsal", "jugador", "anio", "demarcacion"], players)

    # Minutos (hoja tal cual)
    wm = wb["Minutos"]
    heads = [wm.cell(1, c).value for c in range(1, wm.max_column + 1)]
    jcols = [(c, h) for c, h in enumerate(heads, 1) if isinstance(h, str) and h.startswith("J")]
    rows = []
    for r in range(2, wm.max_row + 1):
        d, n = wm.cell(r, 1).value, wm.cell(r, 2).value
        if d is None or not n:
            continue
        vals = []
        for c, _ in jcols:
            v = wm.cell(r, c).value
            vals.append("" if v is None else ("-" if str(v).strip() == "-" else str(int(float(v)))))
        rows.append([int(d), str(n).strip()] + vals)
    write(OUT / "minutos.csv", ["dorsal", "jugador"] + [h for _, h in jcols], rows)

    # Partidos y formaciones de cada hoja de jornada
    match_rows, form_rows, seed = [], [], []
    for name in [s for s in wb.sheetnames if s.startswith("J") and s[1:].isdigit()]:
        ws = wb[name]; j = int(name[1:])
        title = str(ws["A1"].value or "")
        fecha = ws["B1"].value
        fecha = fecha.strftime("%d/%m/%Y") if isinstance(fecha, datetime) else ""
        partido = str(ws["C1"].value or "")
        s_ini = str(ws["H2"].value or "").strip(); s_fin = str(ws["H19"].value or "").strip().rstrip("-")
        notes = []
        if title and title.upper() != f"JORNADA {j}":
            notes.append(f"el título de la hoja dice «{title}»")
        placed = {"inicio": [], "final": []}
        for momento, r0, r1, sistema in (("inicio", 4, 17, s_ini), ("final", 22, 35, s_fin)):
            for r in range(r0, r1 + 1):
                for col in "FGHIJKL":
                    v = ws[f"{col}{r}"].value
                    if v in (None, ""):
                        continue
                    txt = str(v).strip()
                    jug = SHORT.get(txt.upper(), "")
                    slot = SLOTS.get(sistema, {}).get((r - r0, col), "")
                    estado = "ok" if jug and slot else ("jugador no identificado en la plantilla" if not jug else "casilla sin puesto equivalente")
                    form_rows.append([j, momento, sistema, f"{col}{r}", txt, jug, slot, estado])
                    placed[momento].append((slot, jug, estado))
        for momento, sistema in (("inicio", s_ini), ("final", s_fin)):
            if placed[momento]:
                for slot, jug, estado in placed[momento]:
                    if slot:
                        seed.append([j, momento, sistema, slot, jug if estado == "ok" else ""])
        filled = {m: sum(1 for s, jg, e in placed[m] if e == "ok") for m in placed}
        if not placed["inicio"] and not placed["final"]:
            notes.append("solo figura el sistema; jugadores sin colocar en el Excel")
        estado = "completa" if filled["inicio"] == 11 and filled["final"] == 11 else ("parcial" if any(filled.values()) else "pendiente")
        match_rows.append([j, fecha, partido, s_ini, s_fin, filled["inicio"], filled["final"], estado, "; ".join(notes)])
    write(OUT / "partidos.csv", ["jornada", "fecha", "partido_excel", "sistema_inicio", "sistema_final",
                                 "jugadores_inicio", "jugadores_final", "estado_formacion", "notas"], match_rows)
    write(OUT / "formaciones_excel.csv", ["jornada", "momento", "sistema", "celda", "texto_excel", "jugador", "puesto", "estado"], form_rows)
    seg = OUT / "seguimiento_formaciones.csv"
    if not seg.exists():
        write(seg, ["jornada", "momento", "formacion", "slot", "jugador"], seed)
        print("seguimiento_formaciones.csv creado con las formaciones del Excel")
    else:
        print("seguimiento_formaciones.csv ya existe: no se modifica")
    for f in ("jugadores", "minutos", "partidos", "formaciones_excel"):
        print(f, sum(1 for _ in open(OUT / f"{f}.csv", encoding="utf-8")) - 1, "filas")


if __name__ == "__main__":
    main(sys.argv[1])
