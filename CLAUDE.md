# App Primer Toque C.F. · Instrucciones permanentes

App Streamlit en `futbol_streamlit/` (entrada `app.py`). Estado y pendientes: `PROGRESO_DESARROLLO.md` (leer al empezar sesión).

## Reglas obligatorias
- Trabajar solo en la rama `dev`. No tocar `main` sin autorización expresa del usuario.
- No eliminar datos existentes (CSV, actas, muro, calendario, adjuntos).
- Conservar los tres equipos: Juvenil A, Cadete A e Infantil D.
- Duraciones (`futbol_streamlit/teams.py`): Juvenil A 90', Cadete A 80', Infantil D según su configuración (hoy 70').
- Antes de publicar, ejecutar las pruebas:
  `python futbol_streamlit/validar_datos.py` y `python tests/smoke_test.py`
  (en Windows con `PYTHONIOENCODING=utf-8` y el venv `~/venvs/analisis-futbol`; sin UTF-8 aparecen fallos falsos).
- Si pasan: commit y push a `dev`. Si fallan: no publicar y avisar.
- Nunca relajar comprobaciones de seguridad, integridad de datos ni pruebas para ahorrar tokens.

## Forma de trabajar (eficiencia)
- No leer el proyecto entero. Localizar con búsquedas concretas (grep de funciones, claves, textos) y leer solo los fragmentos necesarios. `app.py` es grande: leer por rangos de líneas.
- No imprimir archivos completos, trazas enormes ni salidas repetidas: filtrar con `head`, `tail` o `grep`.
- Ignorar `V15_*_CAMBIOS.txt`, logos, imágenes, PDF y `__pycache__` salvo que la tarea los requiera.
- Reutilizar lo existente: `league_core.py` (cálculos de liga por duración), `teams.py`, `crests.py`, `ui_theme.py`, `team360_*`, `player_charts.py`, `pdf_export_v63.py`, importadores en `tools/`.
- Cambio sencillo: editar directamente. Cambio complejo: plan breve primero, luego implementar.
- Respuesta final corta: cambios, pruebas ejecutadas y resultado, publicación (commit/push).
- Al cerrar un bloque de trabajo importante, actualizar `PROGRESO_DESARROLLO.md` (hecho / pendiente) de forma concisa.
