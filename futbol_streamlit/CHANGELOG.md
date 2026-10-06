# Historial de cambios

Las versiones más recientes primero.

## V15.12.19 · Limpieza
- Nombres de equipo, logos, colores de acento, rangos de análisis (J1–J5 / J1–J4) y enlaces de vídeo centralizados al inicio de `app.py` (los nombres pasan de ~55 apariciones sueltas a 7 definiciones).
- Eliminado código muerto: `team_formations()` (solo alimentaba una variable sin uso), `top3_shot_pct` y una regla CSS sin uso. Eliminadas las cadenas `if/elif` de logo y de color.
- La cabecera de Villarreal ahora muestra su logo (antes aparecía un escudo genérico porque faltaba en la cadena `if/elif`).
- Eliminados ficheros sin uso: `partidos.csv`, `equipo_partido.csv`, `eventos.csv`, `jugadores_partido.csv` (plantillas vacías de la app original), `equipo_primer_toque.csv` (100 % duplicado de `partidos_rivales.csv`) y `juvenil_a_portada.jpeg` (Inicio usa la miniatura `_home`).
- README reescrito (describe el estado actual) y el historial se mueve a este fichero.
- Comprobado: las 20 vistas de la app (4 módulos + 16 equipos) producen el mismo resultado que antes de la limpieza, salvo el logo de Villarreal.

## V15.12.18
- Inicio usa miniaturas propias (`juvenil_a_portada_home.jpeg` e `infantil_d_portada_home.jpeg`, 900 px): ~325 KB por carga frente a 1.268 KB en la V15.12.15. Las fotos grandes se siguen usando en la página de Infantil D.
- Panel de diagnóstico: añade `?debug=1` a la URL y al pie aparecerá el tiempo de ejecución en el servidor y las versiones de Streamlit, Python y pandas. Sin ese parámetro no se muestra nada.
- Etiquetas de versión actualizadas.

## V15.12.17 · Menos peso por clic
- Medido en el servidor: la lógica Python tarda <0,5 s en todos los módulos; el peso estaba en lo que se envía al navegador en cada clic.
- Inicio enviaba ~1,25 MB de fotos (2048×1536 y 1290×951 mostradas a media pantalla). Redimensionadas a 1100/1200 px: ahora ~0,5 MB.
- Resumen liga enviaba ~707 KB (logos completos dentro de dos tablas). Los logos de tabla se generan ahora como miniaturas 2x cacheadas: ~74 KB (-90 %).
- Logos (≤164 px) y mapas de calor (paleta de 192 colores) optimizados. Mismos nombres de fichero; el código no cambia.

## V15.12.16
- **Dato corregido:** Primer Toque J4, 83' → la segunda amarilla/expulsión es de **Blázquez** (amarilla previa en el 77'), no de Bilal (que estaba sancionado y no tiene minutos en J4). Esto ya era así en la versión embebida anterior, pero el CSV tenía a Bilal y la V15.12.15 lo mostraba mal.
- Cacheados los CSV de vídeo individual (`individual_video_j*.csv`), los mapas de calor/tiros, el logo de la ficha individual y el escudo de cabecera de Rivales: antes se leían del disco y se recodificaban en base64 en cada clic.
- Nuevo `validar_datos.py` (solo pandas): comprueba que los minutos de cada jornada cuadran con las expulsiones y que cada jugador con tarjeta tiene minutos. Ejecutar con `python validar_datos.py` antes de subir datos nuevos.
- Pendiente de revisar: Acero J1, roja directa a Aaron Madrid (#33, 26') con 0 minutos jugados (¿jugador del banquillo?).

## V15.12.15 · Rápida real
- Eliminados los DataFrames embebidos de Villarreal, Primer Toque y Salesianos que se reconstruían y concatenaban en cada clic; los datos J1–J5 viven solo en `data/*.csv`.
- Logos e imágenes de Inicio cacheados. `app.py` baja de 237 KB a ~151 KB.

## V14.8.4
- Enlaces de partidos integrados para los equipos ya analizados.
- Primer Toque J3: Toni roja directa 56'; Bilal amarilla 82' y doble amarilla 86'.
- Villarreal J1: gol de penalti de Adrián Díaz en 83'.

## V14.4 · Salesianos
- Añadido **C.F. At. Burriana - Salesianos 'A'** con J1–J5 completas en Rivales.
- Resultados: J1 Paterna 3–0 Salesianos; J2 Salesianos 3–1 Patacona; J3 Inter San José 4–3 Salesianos; J4 Salesianos 2–0 Cracks; J5 Torre Levante 0–0 Salesianos.
- 990 minutos de jugadores validados en cada jornada (11 × 90).
- 8 goles a favor y 8 en contra cargados por minuto para alimentar la distribución macro→micro.
- Mismo motor que Bétera, Acero y Primer Toque: Total/Casa/Fuera, posible XI, minutos, titularidad, goleadores, disciplina, conversión G/90, distribución por tramos y evolución.
- Nuevo bloque **Penaltis** debajo de Carga competitiva. Los goles de penalti se guardan como `penalti_gol` y los fallados como `penalti_fallado`, mostrando jornada, minuto y lanzador. En Salesianos J1–J5 no se ha confirmado visualmente ningún penalti, por lo que el bloque lo indica expresamente sin inventar datos.
- Los goles en propia se siguen registrando como `G.P.` y nunca se asignan a un jugador rival.

## V14.2
- Conversión de gol por jugador en SVG, ordenada de mayor a menor G/90, con columnas más finas.
- Distribución de goles por tramo con porcentaje sobre el total de GF y GC del filtro.

## V9
Versión completa de la sección **Rivales** con los 16 equipos de liga y Bétera C.F. desarrollado con J1–J4.

### Novedades V9
- resultados J1–J4 corregidos y mostrados respetando local/visitante;
- V-E-D, goles a favor y goles en contra recalculados automáticamente por filtro;
- Total/Casa/Fuera recalcula posible XI, minutos, goles y disciplina;
- eliminado el bloque duplicado "Detalle por jornada";
- nuevo bloque de goles por tramos 0–15, 15–30, 30–45, 45–60, 60–75 y 75–90 con círculos proporcionales;
- nuevo gráfico de evolución de clasificación J1–J4 con los 16 equipos y Bétera destacado en verde;
- tabla de minutos ordenada de mayor a menor;
- posible XI orientado con el portero en área propia y ataque hacia la derecha;
- goleadores y disciplina muestran nombre + dorsal;
- Carga competitiva muestra jugadores utilizados.

Resultados Bétera J1–J4:
- J1 Bétera 1–1 Col. Salgui
- J2 Primer Toque 2–0 Bétera
- J3 Bétera 2–2 Villarreal
- J4 Manises 0–1 Bétera

Evolución Bétera: 8.º → 14.º → 15.º → 10.º.

Los datos no visibles/confirmados no se inventan. El dorsal 1 aparece como Alex en las capturas FFCV; sus apellidos quedan pendientes de validar.

