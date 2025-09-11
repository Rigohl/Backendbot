@echo off
echo Iniciando BackendBot completo...
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\Initialize-Backend.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\automation.ps1" -Parallel -Optimize -Test -Monitor
echo BackendBot iniciado. Abre el dashboard con Open-Dashboard.bat
pause
