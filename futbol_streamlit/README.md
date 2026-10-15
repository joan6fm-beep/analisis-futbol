# Fútbol Data Joan · V15.12.27

## V15.12.27 · San José completo
- C.F. Inter San José Valencia 'B': actas J1–J5 transcritas desde el vídeo FFCV aportado por el usuario.
- Cargados XI, dorsales utilizados, minutos, sistemas, goles, tarjetas y expulsiones de las cinco jornadas.
- Balance de eventos comprobado: 11 goles a favor y 10 en contra.
- J4 y J5 actualizadas a sistema 1-4-4-2.
- Se incorpora el autogol de Pablo Siñuela en J5 como gol encajado y la doble amarilla de Rafael Hernández en J3.


Versión completa de la sección **Rivales** con los 16 equipos de liga y Bétera C.F. desarrollado con J1–J5.

Novedades V9:
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

Resultados Bétera J1–J5:
- J1 Bétera 1–1 Col. Salgui
- J2 Primer Toque 2–0 Bétera
- J3 Bétera 2–2 Villarreal
- J4 Manises 0–1 Bétera
- J5 Bétera 1–1 Paterna

Evolución Bétera: 8.º → 14.º → 15.º → 10.º.

Los datos no visibles/confirmados no se inventan. El dorsal 1 aparece como Alex en las capturas FFCV; sus apellidos quedan pendientes de validar.


## V14.2
- Conversión de gol por jugador en SVG, ordenada de mayor a menor G/90, con columnas más finas.
- Distribución de goles por tramo con porcentaje sobre el total de GF y GC del filtro.

## V14.4 · Salesianos
- Añadido **C.F. At. Burriana - Salesianos 'A'** con J1–J5 completas en Rivales.
- Resultados: J1 Paterna 3–0 Salesianos; J2 Salesianos 3–1 Patacona; J3 Inter San José 4–3 Salesianos; J4 Salesianos 2–0 Cracks; J5 Torre Levante 0–0 Salesianos.
- 990 minutos de jugadores validados en cada jornada (11 × 90).
- 8 goles a favor y 8 en contra cargados por minuto para alimentar la distribución macro→micro.
- Mismo motor que Bétera, Acero y Primer Toque: Total/Casa/Fuera, posible XI, minutos, titularidad, goleadores, disciplina, conversión G/90, distribución por tramos y evolución.
- Nuevo bloque **Penaltis** debajo de Carga competitiva. Los goles de penalti se guardan como `penalti_gol` y los fallados como `penalti_fallado`, mostrando jornada, minuto y lanzador. En Salesianos J1–J5 no se ha confirmado visualmente ningún penalti, por lo que el bloque lo indica expresamente sin inventar datos.
- Los goles en propia se siguen registrando como `G.P.` y nunca se asignan a un jugador rival.


## V14.8.4
- Enlaces de partidos integrados para los equipos ya analizados.
- Primer Toque J3: Toni roja directa 56'; Bilal amarilla 82' y doble amarilla 86'.
- Villarreal J1: gol de penalti de Adrián Díaz en 83'.


## V15.12.15 · Rápida real
- Eliminados los DataFrames embebidos de Villarreal, Primer Toque y Salesianos que se reconstruían y concatenaban en cada clic; los datos J1–J5 viven solo en `data/*.csv`.
- Logos e imágenes de Inicio cacheados. `app.py` baja de 237 KB a ~151 KB.

## V15.12.16
- **Dato corregido:** Primer Toque J4, 83' → la segunda amarilla/expulsión es de **Blázquez** (amarilla previa en el 77'), no de Bilal (que estaba sancionado y no tiene minutos en J4). Esto ya era así en la versión embebida anterior, pero el CSV tenía a Bilal y la V15.12.15 lo mostraba mal.
- Cacheados los CSV de vídeo individual (`individual_video_j*.csv`), los mapas de calor/tiros, el logo de la ficha individual y el escudo de cabecera de Rivales: antes se leían del disco y se recodificaban en base64 en cada clic.
- Nuevo `validar_datos.py` (solo pandas): comprueba que los minutos de cada jornada cuadran con las expulsiones y que cada jugador con tarjeta tiene minutos. Ejecutar con `python validar_datos.py` antes de subir datos nuevos.
- Pendiente de revisar: Acero J1, roja directa a Aaron Madrid (#33, 26') con 0 minutos jugados (¿jugador del banquillo?).


## V15.12.27 · Colegio Salgui completo
- Actas FFCV J1–J5 transcritas desde vídeo aportado por el usuario.
- 5 partidos, 55 titulares, convocatorias, minutos, sistemas, goles y tarjetas.
- Balance: 1V-2E-2D, 8 GF, 7 GC, 5 puntos.


## V15.12.27 · Cracks completo
- Actas FFCV J1–J5 transcritas desde vídeo aportado por el usuario.
- 5 partidos, 55 titulares, convocatorias, minutos, sistemas, goles, tarjetas y expulsión.
- Balance: 1V-1E-3D, 6 GF, 10 GC, 4 puntos.
- Daniel Saez Barber, máximo goleador del tramo, con 2 goles.


## V15.12.27 · Paterna completo
- Actas FFCV J1–J5 transcritas desde vídeo aportado por el usuario.
- 5 partidos, 55 titulares, sistemas, cambios/minutos, goles y tarjetas.
- Balance: 1V-2E-2D, 9 GF, 10 GC, 5 puntos.
- Oscar Rubio Montoro, máximo goleador del tramo, con 3 goles.


## V15.12.27 · Manises completo
- Actas FFCV J1–J5 transcritas desde vídeo aportado por el usuario.
- 5 partidos, 55 titulares, convocatorias, minutos, sistemas, goles, tarjetas y expulsiones.
- Balance: 2V-1E-2D, 6 GF, 6 GC, 7 puntos.
- Hugo Albiach Serrano, máximo goleador del tramo, con 2 goles.


## V15.12.27 · Patacona completo
- Actas FFCV J1–J5 transcritas desde vídeo aportado por el usuario.
- 5 partidos, 55 titulares, 90 convocatorias/minutajes, sistema 1-5-4-1, goles, tarjetas y expulsiones.
- Balance: 1V-0E-4D, 5 GF, 12 GC, 3 puntos.
- Goles: Miron Saliakhov, Rayan Bououd Mazouz, Mario Garcia Fernando y Julio Casero Girona; más un autogol rival.


## V15.12.31
- Añadida biblioteca de enlaces J1-J5 facilitados por el usuario para ambos equipos de cada partido.
- Corregido Aaron Madrid (Acero J5) como gol de penalti.
