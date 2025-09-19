@echo off
REM BackendBot API Service Control Script
REM ====================================
REM
REM Script para controlar el servicio API de BackendBot
REM Ejecuta la API de manera invisible en segundo plano
REM
REM Uso:
REM     api_control.bat start    - Iniciar servicio
REM     api_control.bat stop     - Detener servicio
REM     api_control.bat status   - Ver estado
REM     api_control.bat restart  - Reiniciar servicio
REM
REM Autor: BackendBot Team
REM Version: 0.1.0

setlocal enabledelayedexpansion

REM Configuración
set "PYTHON_EXE=python"
set "SERVICE_SCRIPT=%~dp0api_service_launcher.py"
set "SCRIPT_DIR=%~dp0"

REM Verificar que el script de servicio existe
if not exist "%SERVICE_SCRIPT%" (
    echo ❌ Error: No se encuentra api_service_launcher.py
    echo Asegúrate de que el archivo esté en el mismo directorio
    pause
    exit /b 1
)

REM Función para mostrar ayuda
:show_help
if "%1"=="" (
    echo.
    echo BackendBot API Service Control
    echo ==============================
    echo.
    echo Uso: %0 {start^|stop^|status^|restart}
    echo.
    echo   start   - Iniciar el servicio API de manera invisible
    echo   stop    - Detener el servicio API
    echo   status  - Mostrar estado del servicio
    echo   restart - Reiniciar el servicio API
    echo.
    pause
    exit /b 0
)

REM Procesar argumentos
if "%1"=="start" goto start_service
if "%1"=="stop" goto stop_service
if "%1"=="status" goto status_service
if "%1"=="restart" goto restart_service

echo ❌ Comando desconocido: %1
echo Usa %0 sin parámetros para ver la ayuda
pause
exit /b 1

:start_service
echo.
echo 🚀 Iniciando BackendBot API Service...
echo.
cd /d "%SCRIPT_DIR%"
"%PYTHON_EXE%" "%SERVICE_SCRIPT%" start
if errorlevel 1 (
    echo.
    echo ❌ Error al iniciar el servicio
    pause
    exit /b 1
)
echo.
echo ✅ Servicio iniciado correctamente
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
goto :eof

:stop_service
echo.
echo 🛑 Deteniendo BackendBot API Service...
echo.
cd /d "%SCRIPT_DIR%"
"%PYTHON_EXE%" "%SERVICE_SCRIPT%" stop
if errorlevel 1 (
    echo.
    echo ❌ Error al detener el servicio
    pause
    exit /b 1
)
echo.
echo ✅ Servicio detenido correctamente
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
goto :eof

:status_service
echo.
echo 📊 Estado del BackendBot API Service:
echo.
cd /d "%SCRIPT_DIR%"
"%PYTHON_EXE%" "%SERVICE_SCRIPT%" status
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
goto :eof

:restart_service
echo.
echo 🔄 Reiniciando BackendBot API Service...
echo.
cd /d "%SCRIPT_DIR%"

REM Detener servicio
echo Deteniendo servicio actual...
"%PYTHON_EXE%" "%SERVICE_SCRIPT%" stop
timeout /t 2 /nobreak >nul

REM Iniciar servicio
echo Iniciando servicio...
"%PYTHON_EXE%" "%SERVICE_SCRIPT%" start
if errorlevel 1 (
    echo.
    echo ❌ Error al reiniciar el servicio
    pause
    exit /b 1
)
echo.
echo ✅ Servicio reiniciado correctamente
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
goto :eof