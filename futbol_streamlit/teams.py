"""Configuración por equipo. Cada equipo usa SU duración reglamentaria en todos los cálculos.

Juvenil A: 90' (2 × 45). Su código histórico usa 90 directamente y no se modifica.
Infantil D: 70' (2 × 35), verificado en el Excel del equipo (fila TOTAL = 11 × 70).
Cadete A:  80' (2 × 40), Lliga Autonòmica Cadet.
"""
TEAMS = {
    "juvenil": dict(label="Juvenil A", match_minutes=90, half=45),
    "infantil": dict(label="Infantil D", match_minutes=70, half=35),
    "cadete": dict(label="Cadete A", match_minutes=80, half=40),
}


def match_minutes(area: str) -> int:
    return TEAMS[area]["match_minutes"]
