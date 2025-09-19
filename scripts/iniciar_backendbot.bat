@echo off
REM Script para iniciar BackendBot usando el entorno virtual
echo Iniciando BackendBot con entorno virtual...
cd /d "%~dp0"
call venv\Scripts\activate
start "BackendBot" /min pythonw.exe src\backendbot\main_ui_launcher.py
