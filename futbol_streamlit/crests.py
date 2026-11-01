"""Escudos de los equipos (compartido por Juvenil A, Cadete A y el resto de la app).

Cada nombre de equipo de cada competición apunta al escudo de SU club. Un mismo club
(p. ej. Villarreal C.F. 'C' en juvenil y 'A' en cadete) reutiliza el mismo archivo.
Clubes distintos con nombres parecidos tienen escudos distintos:
  Levante U.D. ≠ C.F. Torre Levante · Elche C.F. ≠ Celtic Elche C.F. ≠ S.C.D. Intangco
  Valencia C.F. ≠ C.F. Fundació VCF (escudo propio con el texto «Fundació»).

Origen de los archivos:
  futbol_streamlit/*_logo.png        → escudos ya existentes del Juvenil A.
  futbol_streamlit/escudos/*.png     → escudos tomados de la app oficial de la FFCV
                                       (grabación de actas del Cadete A aportada por el usuario).
Si un equipo no tiene escudo verificado se muestra un marcador neutro.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).parent
ESC = BASE / "escudos"

_CLUB_FILE = {
    # Escudos existentes (Juvenil A)
    "betera": BASE / "betera_logo.png",
    "acero": BASE / "acero_logo.png",
    "primer_toque": BASE / "primer_toque_logo.png",
    "salesianos": BASE / "salesianos_logo.png",
    "villarreal": BASE / "villarreal_logo.png",
    "alboraya": BASE / "alboraya_logo.png",
    "historics": BASE / "historics_logo.png",
    "massamagrell": BASE / "massamagrell_logo.png",
    "torre_levante": BASE / "torre_levante_logo.png",
    "inter_san_jose": BASE / "inter_san_jose_logo.png",
    "salgui": BASE / "salgui_logo.png",
    "cracks": BASE / "cracks_logo.png",
    "paterna": BASE / "paterna_logo.png",
    "manises": BASE / "manises_logo.png",
    "patacona": BASE / "patacona_logo.png",
    "canet": BASE / "canet_logo.png",
    # Escudos nuevos (FFCV, Cadete A)
    "levante_ud": ESC / "levante_ud_logo.png",
    "fundacio_vcf": ESC / "fundacio_vcf_logo.png",
    "celtic_elche": ESC / "celtic_elche_logo.png",
    "elche_cf": ESC / "elche_cf_logo.png",
    "la_nucia": ESC / "la_nucia_logo.png",
    "intangco": ESC / "intangco_logo.png",
    "kelme": ESC / "kelme_logo.png",
    "castellon": ESC / "castellon_logo.png",
    "valencia_cf": ESC / "valencia_cf_logo.png",
    "elda": ESC / "elda_logo.png",
    "roda": ESC / "roda_logo.png",
    "benidorm": ESC / "benidorm_logo.png",
}

# Nombre exacto del equipo en la competición → club.
TEAM_CLUB = {
    # Lliga Comunitat Juvenil · Nord
    "Bétera C.F. 'A'": "betera",
    "C.D. Acero 'A'": "acero",
    "Primer Toque C.F. 'A'": "primer_toque",
    "C.F. At. Burriana - Salesianos 'A'": "salesianos",
    "Villarreal C.F. 'C'": "villarreal",
    "Alboraya U.D. 'B'": "alboraya",
    "C.F. Històrics de València 'A'": "historics",
    "Ath. Massamagrell C.F. 'A'": "massamagrell",
    "C.F. Torre Levante 'A'": "torre_levante",
    "C.F. Inter San José Valencia 'B'": "inter_san_jose",
    "Col. Salgui E.D.E. 'A'": "salgui",
    "C.F. Cracks 'A'": "cracks",
    "Paterna C.F. 'A'": "paterna",
    "Manises C.F. 'A'": "manises",
    "Patacona C.F. 'B'": "patacona",
    "C.D.F. Canet 'A'": "canet",
    # Lliga Autonòmica Cadet · Grup Únic (clubes ya existentes)
    "Villarreal C.F. 'A'": "villarreal",
    "Alboraya U.D. 'A'": "alboraya",
    "Patacona C.F. 'A'": "patacona",
    "C.F. Inter San José Valencia 'A'": "inter_san_jose",
    # Lliga Autonòmica Cadet (escudos FFCV)
    "Levante U.D. 'A'": "levante_ud",
    "C.F. Fundació VCF 'A'": "fundacio_vcf",
    "Celtic Elche C.F. 'A'": "celtic_elche",
    "Elche C.F. 'A'": "elche_cf",
    "C.F. La Nucía 'A'": "la_nucia",
    "S.C.D. Intangco 'A'": "intangco",
    "Kelme C.F. 'A'": "kelme",
    "C.D. Castellón 'A'": "castellon",
    "Valencia C.F. 'A'": "valencia_cf",
    "Elda Unión Cableworld C.F. 'A'": "elda",
    "C.D. Roda 'A'": "roda",
    "C.F. Benidorm 'A'": "benidorm",
}

MISSING = Path("__missing__")


def crest_path(team) -> Path:
    """Ruta del escudo del equipo, o una ruta inexistente si no hay escudo verificado."""
    club = TEAM_CLUB.get(str(team).strip())
    p = _CLUB_FILE.get(club) if club else None
    return p if p is not None and p.exists() else MISSING


def has_crest(team) -> bool:
    return crest_path(team).exists()
