# Plataforma de análisis de fútbol (V1)

## Ejecutar
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estructura
- `data/partidos.csv`: ficha del partido.
- `data/jugadores_partido.csv`: datos individuales por jugador/partido.
- `data/equipo_partido.csv`: datos colectivos.
- `data/eventos.csv`: goles, tarjetas, sustituciones y otros eventos FFCV.

Los campos no validados se mantienen vacíos/PENDIENTE deliberadamente.
