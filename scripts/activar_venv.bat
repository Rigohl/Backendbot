@echo off
REM Script para activar el entorno virtual de BackendBot
echo Activando entorno virtual de BackendBot...
cd /d "%~dp0"
venv\Scripts\activate
echo Entorno virtual activado. Puedes ejecutar comandos de Python ahora.
echo Para ejecutar BackendBot: python src\backendbot\main_ui_launcher.py
echo.
cmd /k