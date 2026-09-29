@echo off
title Subir Proyecto a GitHub - Marco Antonio Oroza Ortega
cd /d "%~dp0"
echo =====================================================================
echo  Subiendo Proyecto a GitHub: MarcoOroza/motor-decisiones-comportamentales
echo =====================================================================
echo.

"C:\Program Files\Git\cmd\git.exe" push -u origin main

echo.
echo =====================================================================
echo Si te abrio una ventana del navegador, autoriza el inicio de sesion.
echo =====================================================================
pause
