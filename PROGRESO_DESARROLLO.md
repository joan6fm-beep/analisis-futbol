# Progreso de desarrollo · App Primer Toque C.F.

Rama de trabajo: `dev` (app de pruebas). `main` = producción (V15.12.84, etiqueta `v15.12.84`), sin cambios.

Antes de publicar: `python futbol_streamlit/validar_datos.py` y `python tests/smoke_test.py`
(incluye `tests/test_integridad.py`).

## Hecho
- Sistema de diseño oscuro (`ui_theme.py`), Plotly, portada con fotos completas.
- Equipo 360: tres niveles (resumen del partido, áreas, análisis avanzado) + temporada; datos Veo J2/J3/J5/J7.
- Rivales y Resumen de liga con J8 parcial (4 de 8 partidos, clasificación provisional);
  porteros con atribución de goles por minutos.
- **Infantil D** (bloque completo, noviembre 2026):
  - Navegación propia: Inicio · Muro · Calendario · Minutos · Seguimiento.
  - Datos en `futbol_streamlit/data/infantil_d/`, importados del Excel con
    `tools/importar_infantil_d.py` (ver `data/infantil_d/LEEME.md`).
  - Minutos: tabla con la estructura del Excel, tabla interactiva, 3 gráficos y comparador.
  - Seguimiento: el mismo editor de formaciones que Juvenil A, con J1 y J2 precargadas del Excel.
  - Muro y Calendario propios (archivos separados); el calendario del Infantil D permite editar y eliminar eventos.

## Pendiente / datos a revisar
- J8 Juvenil A: faltan los 4 partidos del domingo 1/11.
- J7 Juvenil A: ocasiones 14 frente a 13; zonas de pase 8/82/10 frente a 41/48/11.
- Paterna J5: «Oscar Rubio Montoro» duplicado (dorsales 7 y 8).
- Infantil D (Excel):
  - J2 inicio: «SEBAS» no está en la plantilla (casilla I16, delantero centro). Puesto vacío.
  - J1 tiene fecha 17/10/2026 y J2 03/10/2026 (orden cronológico invertido).
  - J2: el texto del partido es «CD RODA C - 1 INFANTIL B - 1».
  - J3: solo sistema (sin jugadores colocados) y sin fecha ni rival.
  - J4: la hoja es una copia de J3 (título «JORNADA 3») y no tiene minutos.
  - J1: el portero final es Martin (65') aunque Alex jugó 5'; revisar quién terminó.
- Persistencia: Muro, Calendario y Seguimiento escriben CSV en el servidor de Streamlit Cloud,
  que se pierden al reiniciar o redesplegar. Opciones gratuitas a valorar con el usuario:
  guardar en GitHub mediante la API (token en `st.secrets`) o Google Sheets (cuenta de servicio).
- Iconos emoji en títulos; gráfico «Diferencia de goles y acumulado» de Rivales (dos escalas).
