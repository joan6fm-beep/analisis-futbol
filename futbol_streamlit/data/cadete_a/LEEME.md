# Cadete A · Lliga Autonòmica Cadet (Grup Únic) 2026/27

Partidos de **80 minutos** (2 × 40). Todos los cálculos del Cadete A usan 80' (`teams.py`).

## Origen de los datos
- `fuente/actas.txt`: transcripción de las actas de la app de la FFCV que aparecen en la grabación
  `DATOS VEO/CADETE A/WhatsApp Video 2026-11-01 at 19.19.56.mp4` (aportada por el usuario).
  Contiene alineaciones (titulares, suplentes, porteros), sistemas, cambios, goles, penaltis,
  goles en propia puerta y tarjetas, con su minuto. Las notas `NOTA` explican cada duda.
- Foto del equipo: `DATOS VEO/CADETE A/WhatsApp Image 2026-11-01 at 19.19.57.jpeg`,
  copiada sin cambios a `futbol_streamlit/cadete_a_portada.jpeg`.

## Generar los CSV
```
python tools/importar_cadete_a.py
```
Genera `partidos.csv`, `alineaciones.csv`, `eventos.csv`, `minutos.csv`, `plantillas.csv`,
`equipos.csv` y `avisos.csv`. La clasificación, resultados, goleadores, porteros, tramos de goles,
minutos y fichas de rivales se calculan en la app a partir de estos archivos (`league_core.py`):
no hay cifras duplicadas a mano.

Para añadir una jornada: transcribir sus actas en `fuente/actas.txt` con el mismo formato
y volver a ejecutar el importador. El importador comprueba que cada marcador coincide con los
goles del acta, que hay 11 titulares y un portero, que el sistema coincide con las líneas y que
cada nombre abreviado de la cronología corresponde a un único jugador; si no, lo indica.

## Reglas de cálculo
- Minutos: titular de 0' a su cambio o expulsión; suplente desde su entrada. El tiempo añadido no
  suma: máximo 80' por partido. % de participación = minutos ÷ (80 × partidos del equipo).
- Porteros: cada gol encajado se atribuye al portero que estaba en el campo en ese minuto.
  Si hay dos porteros en el campo o falta el minuto, el gol queda «sin atribuir».
  GC por 80' = encajados ÷ minutos × 80.
- Goles por tramos: 1–10 … 71–80. Un gol en el añadido cuenta en el último tramo de su parte
  y conserva su minuto real.
- Clasificación: 3-1-0, ordenada por puntos, diferencia de goles y goles a favor. Los desempates
  oficiales (enfrentamiento directo) pueden diferir.

## Datos pendientes o no disponibles
- J7 Celtic Elche – C.D. Roda: no jugado en la grabación (programado el 10/11/2026).
- J8: solo el acta de C.D. Castellón 3-1 Patacona (1 de 9 partidos).
- Asistencias, estadísticas de vídeo: las actas no las incluyen.
- Alboraya tiene dos titulares «C. Garcia» (Cayetano Garcia Soriano y Cayetano Garcia Villar):
  algunas tarjetas y cambios no se pueden atribuir; sus minutos en esos partidos quedan pendientes.
- Algunas fechas u horas no se veían en la grabación (se indica en `NOTA`).
