# Progreso de desarrollo · App Primer Toque C.F.

Rama de trabajo: `dev` (app de pruebas). `main` = producción (V15.12.84, etiqueta `v15.12.84`), sin cambios.

Antes de publicar: `python futbol_streamlit/validar_datos.py` y `python tests/smoke_test.py`
(incluye `tests/test_integridad.py`).

## Hecho
- Sistema de diseño oscuro (`ui_theme.py`), Plotly, portada con fotos completas.
- Equipo 360: tres niveles (resumen del partido, áreas, análisis avanzado) + temporada; datos Veo J2/J3/J5/J7.
- Rivales y Resumen de liga con J8 completa (8 de 8 partidos; los 4 del 1/11 desde vídeo FFCV);
  porteros con atribución de goles por minutos.
- **Infantil D** (bloque completo, noviembre 2026):
  - Navegación propia: Inicio · Muro · Calendario · Resultados · Minutos · Seguimiento.
  - Resultados (data/infantil_d/resultados.csv y eventos.csv, mantenidos a mano): J2 3-2 (rival pendiente),
    J3 2-2 San Lorenzo; 5 goles y 1 asistencia confirmados, sin jornada ni minuto.
- Navegación: la URL raíz muestra siempre la portada; botón «Inicio / Cambiar equipo» en barra lateral,
  barra superior y menú móvil.
  - Datos en `futbol_streamlit/data/infantil_d/`, importados del Excel con
    `tools/importar_infantil_d.py` (ver `data/infantil_d/LEEME.md`).
  - Minutos: tabla con la estructura del Excel, tabla interactiva, 3 gráficos y comparador.
  - Seguimiento: el mismo editor de formaciones que Juvenil A, con J1 y J2 precargadas del Excel.
  - Muro y Calendario propios (archivos separados); el calendario del Infantil D permite editar y eliminar eventos.

- **Cadete A** (Lliga Autonòmica Cadet, noviembre 2026):
  - Portada con tres equipos; navegación propia: Inicio · Resumen liga · Rivales · Equipo · Calendario · Muro.
  - Equipo (`cad.render_team`): puntos por jornada, puntos acumulados (con el líder), evolución de la clasificación, goles a favor/en contra,
    comparador y estadísticas propias. Resumen liga solo con la información general; `view=estadisticas` abre Equipo.
  - 79 actas FFCV transcritas de dos grabaciones del usuario (J1–J7 completas salvo Celtic–Roda; J8 completa; J9: 8 de 9, Kelme–Intangco suspendido)
    en `data/cadete_a/fuente/actas.txt`; `tools/importar_cadete_a.py` genera los CSV.
  - Cálculos en `league_core.py`, parametrizados por duración (`teams.py`: Juvenil 90', Cadete 80', Infantil 70').
  - Muro, calendario y adjuntos propios en `data/cadete_a/`.
  - Resumen de liga y Rivales del Cadete A = los del Juvenil A parametrizados por liga (`LEAGUES` en app.py:
    datos, 80', tramos de 10', sin vídeos/PDF). Comprobado que las 17 vistas del Juvenil A quedan idénticas.
  - Escudos compartidos en `crests.py` (16 del Juvenil A + 12 FFCV del Cadete A).
- **Rediseño visual v16** (noviembre 2026, Juvenil A y Cadete A):
  - `pt_viz.py`: tarjetas de jugador (podio + ranking), duelo entre equipos, radar, carrera de puntos, mapa ataque/defensa,
    vista 3D de la liga y goles decisivos (victoria / último empate; solo partidos con orden de goles completo).
  - `ui_theme.py`: plantilla Plotly por defecto `primer_toque` y estilos de tarjetas/pestañas/gráficos (móvil incluido).
  - Juvenil A · Temporada: «Quién marca / Quién decide / Quién sostiene». Cadete A · Equipo: mismas tarjetas en Minutos y
    Goleadores, porteros en tarjetas (tabla completa en desplegable), comparador con duelo + radar, escudos en clasificación.
  - Resumen de liga (ambos): carrera de puntos, ataque frente a defensa y vista 3D; goleadores, eficacia y porteros en
    tarjetas (tablas completas en desplegables). Sin fotos individuales en los datos: avatar con iniciales y dorsal.

- **SCOUTING FFCV** (noviembre 2026, Segona Infantil Castelló 2026/27; en los menús de los tres equipos):
  - La FFCV publica **6 grupos** (no 7) para esta competición: 83 equipos transcritos de la publicación oficial del blog
    (03/10/2026) con `tools/importar_scouting_ffcv.py --estructura`. Datos en `data/scouting/` (temporadas, competiciones,
    grupos, equipos, jugadores, plantillas, estadísticas, jornadas; ids estables, sin duplicados).
  - Estadísticas de jugador: la FFCV solo las sirve por `/competiciones/api/`, prohibida en su robots.txt → no se descargan
    automáticamente. Importación de la página del equipo guardada (HTML) o CSV/XLSX desde la pestaña «Datos FFCV» o el script.
    «Actualizar FFCV» reprocesa copias locales y comprueba si cambió la publicación oficial de grupos. N/D = sin dato.
  - Menores: sin fotos ni fechas de nacimiento completas; año solo si la fuente lo publica.

## Pendiente / datos a revisar
- Scouting: importar las páginas FFCV de los 83 equipos (0 importados). Validar el lector con una página real guardada.
- Cadete A: J7 Celtic Elche–Roda (10/11) y J9 Kelme–Intangco (suspendido); asistencias no registradas en actas;
  dos «C. Garcia» en Alboraya (tarjetas y cambios sin atribuir); fechas/horas no visibles en algunas actas.
- J8 Juvenil A: gol de A. Urbina (Inter SJ, 38') con icono distinto en el acta (¿penalti?), registrado como gol;
  tarjetas a técnicos (V. Felipe, R. Hervas) no registradas.
- J7 Juvenil A: ocasiones 14 frente a 13; zonas de pase 8/82/10 frente a 41/48/11.
- Paterna J5: «Oscar Rubio Montoro» duplicado (dorsales 7 y 8).
- Infantil D: rival de J2; marcador de J1 (Fomento Castellón); jornada y minuto de cada gol y de la asistencia.
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
