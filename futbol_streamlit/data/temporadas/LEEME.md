# Temporadas

La app compara temporadas a partir del registro `data/temporadas.csv`:

| columna | significado |
|---|---|
| `temporada` | nombre visible, por ejemplo `2025/2026` |
| `carpeta` | `.` para la temporada actual (usa `data/`); para las demás, el nombre de la carpeta dentro de `data/temporadas/` |
| `equipo` | nombre exacto de nuestro equipo en los CSV de esa temporada, por ejemplo `Primer Toque C.F. 'A'` |
| `estado` | `activa` o `cerrada` |
| `notas` | texto libre |

## Añadir una temporada anterior

1. Crea la carpeta `data/temporadas/2025-2026/`.
2. Copia en ella los CSV de esa temporada con **los mismos nombres y columnas** que los actuales:
   - `partidos_rivales.csv` (obligatorio: jornadas, local, visitante y goles)
   - `clasificacion_liga.csv` (opcional: evolución de la posición)
   - `equipo_avanzado.csv` (opcional: estadísticas de vídeo de los partidos en casa)
3. Añade una línea al registro:

```
2025/2026,2025-2026,Primer Toque C.F. 'A',cerrada,Datos importados de ...
```

Una temporada sin `partidos_rivales.csv` no aparece en la app. No se inventan datos:
las métricas que falten en una temporada se muestran como no disponibles.
