@echo off
title Pruebas Unitarias - Motor de Decisiones Comportamentales
cd /d "%~dp0"
set PYTHONPATH=%CD%

echo =====================================================================
echo  Ejecutando Suite de Pruebas Automatizadas (Pytest)
echo  Proyecto de Residencia - Marco Antonio Oroza Ortega (TESE Informática)
echo =====================================================================
echo.

call .venv\Scripts\activate.bat
pytest -v

echo.
echo =====================================================================
pause
