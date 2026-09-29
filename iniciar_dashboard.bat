@echo off
title Motor de Decisiones Comportamentales - TESE Informática
cd /d "%~dp0"
set PYTHONPATH=%CD%

echo =====================================================================
echo  Iniciando Motor de Decisiones Comportamentales (Mini-PowerCurve)
echo  Proyecto de Residencia Profesional - TESE Division de Informatica
echo  Autor / Residente: Marco Antonio Oroza Ortega
echo =====================================================================
echo.
echo Activando entorno virtual y levantando la aplicacion en el navegador...
echo.

call .venv\Scripts\activate.bat
streamlit run src\app\dashboard.py

pause
