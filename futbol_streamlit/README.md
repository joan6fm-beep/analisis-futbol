# Fútbol Data Joan · V15.12.19

Análisis de rivales y seguimiento individual para el Juvenil A (Lliga Comunitat Juvenil · Nord, temporada 2026/2027). Hecho con Streamlit.

## Ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

En GitHub la ruta debe ser `analisis-futbol/futbol_streamlit/app.py`.

## Qué incluye

- **Inicio**: acceso a Juvenil A e Infantil D (fotos clicables).
- **Resumen liga**: clasificación, goles por minutos y disciplina y penaltis de toda la liga.
- **Rivales** (16 equipos): resultados, posible XI, minutos, titularidad, goleadores, disciplina, goles por tramo, penaltis, conversión G/90, evolución en la clasificación y enlaces al vídeo de cada partido. Con filtro Total/Casa/Fuera.
- **Individual**: ficha por jugador con datos de vídeo (J2, J3, J5), mapas de calor y de tiros.

Perfiles completos J1–J5: Primer Toque, Salesianos, Villarreal, Alboraya, Històrics. Completos J1–J4: Bétera y Acero. El resto de equipos muestran partidos y quedan listos para cargar sus actas.

## Estructura

| Ruta | Contenido |
|---|---|
| `app.py` | La aplicación. Los nombres de equipo, logos, colores y enlaces de vídeo están al principio del fichero (`T_*`, `TEAM_LOGOS`, `TEAM_ACCENT`, `_VIDEO_LINKS`). |
| `data/equipos_liga.csv` | Los 16 equipos y su orden. |
| `data/partidos_rivales.csv` | Resultados y sistemas por jornada. |
| `data/minutos_rivales.csv` | Minutos y titularidad por jugador y jornada. |
| `data/alineaciones_rivales.csv` | Alineaciones por jornada. |
| `data/eventos_rivales.csv` | Goles, penaltis y tarjetas con minuto. |
| `data/plantillas_rivales.csv` | Plantillas (dorsal y nombre). |
| `data/clasificacion_liga.csv` | Clasificación por jornada. |
| `data/individual_video_j*.csv` | Datos de vídeo individuales (J2, J3, J5). |
| `individual_maps/` | Mapas `heat_j{J}_{dorsal}.png` y `shots_j{J}_{dorsal}.png`. |
| `*_logo.png`, `*_portada*.jpeg` | Logos (≤164 px) y fotos de portada. |
| `validar_datos.py` | Comprobación de integridad de los datos. |

## Convenciones de datos

- **No se inventa nada**: lo que no se ve o no está confirmado queda pendiente.
- Tipos de evento en `eventos_rivales.csv`: `gol`, `gol_contra` (gol encajado), `penalti_gol`, `penalti_contra_gol`, `amarilla`, `doble_amarilla`, `roja`. La app también reconoce `penalti_fallado` (aún sin casos). Los goles en propia puerta se registran como `G.P.` y nunca se asignan a un jugador rival.
- **Tres relojes que no se mezclan** (`VEO_GOAL_SYNC`): minuto del acta FFCV, reloj de partido de Veo y timestamp absoluto del vídeo.
- Cada jornada suma **990 minutos** por equipo (11 × 90), menos los minutos perdidos por expulsiones.

## Añadir una jornada

1. Añade el partido a `partidos_rivales.csv`, y minutos, alineaciones y eventos a sus CSV.
2. Si hay enlace de vídeo, añádelo en `_VIDEO_LINKS` dentro de `app.py`.
3. Ejecuta `python validar_datos.py` (solo necesita pandas). Debe terminar con 0 errores.

## Diagnóstico de rendimiento

Añade `?debug=1` a la URL de la app: al pie aparece el tiempo de ejecución en el servidor y las versiones de Streamlit, Python y pandas. Sin ese parámetro no se muestra nada.

## Pendiente de revisar

- Acero J1: roja directa a Aaron Madrid (#33, 26') con 0 minutos jugados. Probablemente un jugador del banquillo; confirmar con el acta.
- Dorsal 1 de Bétera: aparece como Alex en las capturas FFCV; faltan los apellidos.

Historial de cambios: ver `CHANGELOG.md`.
