@echo off
chcp 65001 >nul
title Analisis de Futbol - Streamlit
cd /d "%~dp0"
echo ==========================================
echo   ANALISIS DE FUTBOL - INICIANDO APP
echo ==========================================
echo.
where py >nul 2>&1
if errorlevel 1 (
  echo ERROR: No se encuentra Python Launcher ^(py^).
  echo Instala Python y vuelve a intentarlo.
  pause
  exit /b 1
)
echo Comprobando dependencias...
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo ERROR al instalar dependencias.
  pause
  exit /b 1
)
echo.
echo Abriendo la aplicacion en tu navegador...
start "" http://localhost:8501
py -m streamlit run app.py --server.port 8501 --server.headless true
pause
