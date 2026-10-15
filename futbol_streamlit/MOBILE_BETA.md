# V15.12.41 MOBILE BETA

Prueba móvil basada en la V15.12.40.

## Qué cambia
- Navegación inferior para pantallas <= 768 px.
- Sidebar oculto en móvil; selector rápido de rivales mediante chips.
- Tablas, KPIs, tarjetas y gráficas compactadas para móvil.
- Barra inferior con Inicio, Liga, Rivales, Equipo e Individual.
- Iconos y manifest PWA preparados en `static/`.

## Cómo probar en iPhone
1. Publica esta carpeta en el mismo repositorio de GitHub/Streamlit.
2. Abre la URL con Safari.
3. Pulsa Compartir.
4. Pulsa “Añadir a pantalla de inicio”.

Nota: Streamlit Cloud controla el HTML raíz; el manifest queda preparado para una fase PWA completa, pero la instalación mediante “Añadir a pantalla de inicio” funciona como acceso web-app incluso sin App Store.
