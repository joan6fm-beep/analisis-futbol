"""SCOUTING FFCV · estructura de la competición e importación de archivos.

Uso:
  python tools/importar_scouting_ffcv.py --estructura          # (re)crea temporadas, competición, grupos y equipos
  python tools/importar_scouting_ffcv.py --equipo <equipo_id> <archivo.html|csv|xlsx>
  python tools/importar_scouting_ffcv.py --actualizar          # reprocesa data/scouting/fuente/
  python tools/importar_scouting_ffcv.py --listar              # ids de equipo y estado

Equipos: transcritos de las 6 imágenes oficiales de la publicación de la FFCV
«Estos son los grupos de Segona Infantil Castelló para la temporada 2026/2027» (03/10/2026).
La FFCV publica 6 grupos para esta competición y temporada (no 7).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "futbol_streamlit"))
import scouting_data as sd  # noqa: E402

TEMPORADA = ("2026-2027", "Temporada 2026/2027")
COMPETICION = ("2627-segona-infantil-castello", "Segona Infantil Castelló", "Infantil", "Castelló")
IMG = "https://ffcv.es/wp/wp-content/uploads/2026/10/{}"

GRUPOS = {
    1: ("1-6-763x1024.png", [
        "CF BENICARLÓ BF B", "ACD PEÑÍSCOLA", "CD CABANES", "ORPESA CF", "RENOMAR ELS PORTS FC",
        "CF TORREBLANCA", "CD VALL D'ALBA", "CD L'ALCORA B", "CF AT. BAIX MAESTRAT", "CF ALCALÀ",
        "UD SANT MATEU", "CD BENICÀSIM B", "VINARÒS CF B"]),
    2: ("2-9-763x1024-png.webp", [
        "CF BENICARLÓ BF C", "CD DRAC CASTELLÓN B", "PRIMER TOQUE CF D", "CD SAN LORENZO DE CASTELLÓN",
        "ORPESA CF B", "CF FOMENTO CASTELLÓN", "CD MORERES B", "CD CABANES B", "CE NOU SEQUIOL",
        "VINARÒS CF C", "CD CASTELLÓN SAD C", "CD BENICÀSIM C", "ACD PEÑÍSCOLA B", "CF ALCALÀ B"]),
    3: ("3-9-763x1024-png.webp", [
        "DEPORTES TONÍN B", "CF SAN PEDRO B", "CF RAFALAFENA DE CASTELLÓN C", "CD SAN LORENZO DE CASTELLÓN B",
        "PRIMER TOQUE CF E", "CF FOMENTO CASTELLÓN B", "CD MORERES", "CD LA MAGDALENA", "CD DRAC CASTELLÓN C",
        "CD RODA F", "VINARÒS CF D", "CF NOU JOVE CASTELLÓ-INSTALACIONES RA 2021 C", "CD BENICÀSIM D",
        "CF RACING DE CASTELLÓN B"]),
    4: ("4-8-763x1024-png.webp", [
        "CF SAN PEDRO", "ESPORTIU VILA-REAL C", "DEPORTES TONÍN", "SP. DE CASTELLÓ B", "UD VALL DE UXÓ E",
        "CD SAN LORENZO DE CASTELLÓN C", "CF JOVENTUT ALMASSORA C", "CE NOU SEQUIOL B", "CD ONDA E",
        "CD ALMAZORA D", "CD DRAC CASTELLÓN D", "CD BURRIANA FB C", "CD BENICÀSIM E",
        "CF NOU JOVE CASTELLÓ-INSTALACIONES RA 2021 D"]),
    5: ("5-9-763x1024-png.webp", [
        "CD ONDA B", "CD ALMAZORA B", "CF RAFALAFENA DE CASTELLÓN B", "ESPORTIU VILA-REAL D",
        "CF JOVENTUT ALMASSORA", "CD RODA E", "CF NOU JOVE CASTELLÓ-INSTALACIONES RA 2021 B", "CD BURRIANA FB B",
        "UD VALL DE UXÓ D", "CF RACING DE CASTELLÓN", "CF AT. BURRIANA - SALESIANOS D", "CF SAN PEDRO C",
        "ANDIAMO VILA-REAL CF C", "DEPORTES TONÍN C"]),
    6: ("6-10-763x1024.png", [
        "CD ALMAZORA C", "UD VALL DE UXÓ B", "VILLARREAL CF C", "CE VILA D'ONDA", "ANDIAMO VILA-REAL CF B",
        "CD ONDA D", "CF AT. BURRIANA - SALESIANOS C", "CF HURACÁN VILA-REAL", "CF JOVENTUT ALMASSORA B",
        "CD L'ALCORA C", "ESPORTIU VILA-REAL E", "CD SEGORBE C", "CF NULES C", "CD BURRIANA FB D"]),
}


def estructura():
    cid = COMPETICION[0]
    sd.upsert("temporadas", [{"temporada_id": TEMPORADA[0], "nombre": TEMPORADA[1]}])
    sd.upsert("competiciones", [{"competicion_id": cid, "temporada_id": TEMPORADA[0], "nombre": COMPETICION[1],
                                 "categoria": COMPETICION[2], "ambito": COMPETICION[3], "fuente_url": sd.POST_GRUPOS}])
    grupos, equipos = [], []
    for n, (img, teams) in GRUPOS.items():
        gid = f"{cid}-g{n}"
        grupos.append({"grupo_id": gid, "competicion_id": cid, "numero": n, "nombre": f"Grupo {n}",
                       "fuente_url": IMG.format(img)})
        old = sd.load("equipos").set_index("equipo_id")["cod_ffcv"].to_dict()
        for t in teams:
            eid = f"{gid}-{sd.slug(t)}"
            equipos.append({"equipo_id": eid, "grupo_id": gid, "nombre": t, "cod_ffcv": old.get(eid, ""),
                            "fuente": "FFCV · publicación oficial de grupos (03/10/2026)"})
    sd.upsert("grupos", grupos)
    sd.upsert("equipos", equipos)
    print(f"{len(grupos)} grupos, {len(equipos)} equipos")


def main(argv):
    if not argv or argv[0] == "--estructura":
        estructura()
    elif argv[0] == "--equipo" and len(argv) == 3:
        p = Path(argv[2])
        print(sd.importar(argv[1], p.name, p.read_bytes()))
    elif argv[0] == "--actualizar":
        print(sd.actualizar_desde_fuente())
    elif argv[0] == "--listar":
        print(sd.estado_equipos()[["equipo_id", "estado", "jugadores"]].to_string(index=False))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
