# Datos del Infantil D

Independientes del Juvenil A. Fuente: Excel «SEGUIMIENTO INFANTIL D 2ª REGIONAL TEMP. 26-27».

| archivo | contenido | quién lo escribe |
|---|---|---|
| `jugadores.csv` | dorsal, jugador, año, demarcación | importador |
| `minutos.csv` | hoja «Minutos» tal cual (J1..J14). `-` = no participó; vacío = sin dato | importador |
| `partidos.csv` | cabecera de cada hoja de jornada y estado de la formación | importador |
| `formaciones_excel.csv` | jugadores colocados en el campo de cada hoja, con la celda de origen | importador |
| `seguimiento_formaciones.csv` | formaciones del apartado Seguimiento | importador (solo si no existe) y la app |
| `resultados.csv` | resultado por jornada (vacío = pendiente) y su fuente | a mano |
| `eventos.csv` | goles y asistencias: jornada y minuto vacíos si no se conocen | a mano |
| `muro.csv`, `muro_adjuntos/` | publicaciones del Muro del Infantil D | la app |
| `calendario.csv` | eventos del Calendario del Infantil D | la app |

## Actualizar con un Excel nuevo

```
python tools/importar_infantil_d.py "ruta/SEGUIMIENTO INFANTIL D ... .xlsx"
```

Regenera jugadores, minutos, partidos y formaciones del Excel. **No toca** `seguimiento_formaciones.csv`
si ya existe (para no perder lo editado en la app): para volver a cargar las formaciones del Excel,
renómbralo antes de ejecutar el importador. Necesita `openpyxl` solo en local.

Los partidos duran 70 minutos (fila TOTAL del Excel: 770 = 11 × 70).
