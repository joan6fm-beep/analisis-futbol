# Fútbol Data Joan · V9

Versión completa de la sección **Rivales** con los 16 equipos de liga y Bétera C.F. desarrollado con J1–J4.

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

Resultados Bétera J1–J4:
- J1 Bétera 1–1 Col. Salgui
- J2 Primer Toque 2–0 Bétera
- J3 Bétera 2–2 Villarreal
- J4 Manises 0–1 Bétera

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
