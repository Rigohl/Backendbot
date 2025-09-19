@echo off
REM BackendBot API Service - Windows Service Script
REM ================================================
REM
REM Este script permite iniciar, detener y gestionar el servicio API de BackendBot
REM de manera profesional en Windows.
REM
REM Uso:
REM   api_service.bat start    - Iniciar el servicio
REM   api_service.bat stop     - Detener el servicio
REM   api_service.bat status   - Ver estado del servicio
REM   api_service.bat restart  - Reiniciar el servicio
REM   api_service.bat logs     - Ver logs del servicio
REM
REM Autor: BackendBot Team
REM Version: 0.1.0

setlocal enabledelayedexpansion

REM Configuración
set "SERVICE_NAME=BackendBotAPI"
set "SCRIPT_DIR=%~dp0"
set "API_SCRIPT=%SCRIPT_DIR%api_server.py"
set "LOG_DIR=%SCRIPT_DIR%logs"
set "PID_FILE=%SCRIPT_DIR%backendbot_api.pid"
set "SERVICE_LOG=%LOG_DIR%api_service.log"

REM Crear directorio de logs si no existe
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Función para obtener timestamp
:timestamp
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set datetime=%%i
set "TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%"
goto :eof

REM Función para escribir log
:log
call :timestamp
echo [%TIMESTAMP%] %~1 >> "%SERVICE_LOG%"
goto :eof

REM Función para verificar si el servicio está ejecutándose
:check_service
if exist "%PID_FILE%" (
    set /p SERVICE_PID=<"%PID_FILE%"
    tasklist /FI "PID eq !SERVICE_PID!" 2>NUL | find /I /N "python.exe">NUL
    if !ERRORLEVEL! EQU 0 (
        echo Servicio ejecutándose (PID: !SERVICE_PID!)
        exit /b 0
    ) else (
        echo Servicio detenido (PID obsoleto encontrado)
        del "%PID_FILE%" 2>NUL
        exit /b 1
    )
) else (
    echo Servicio detenido
    exit /b 1
)

REM Comando start
if "%1"=="start" (
    call :check_service
    if !ERRORLEVEL! EQU 0 (
        echo El servicio ya está ejecutándose
        exit /b 1
    )

    echo Iniciando BackendBot API Service...
    call :log "Iniciando servicio API"

    REM Iniciar el servicio en segundo plano con HTTPS
    start /B python "%API_SCRIPT%" --https > "%LOG_DIR%\api_output.log" 2>&1
    timeout /t 2 /nobreak >nul

    REM Obtener PID del proceso
    for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO TABLE ^| find "python.exe"') do (
        set "SERVICE_PID=%%i"
        goto :found_pid
    )
    :found_pid

    if defined SERVICE_PID (
        echo !SERVICE_PID! > "%PID_FILE%"
        echo Servicio iniciado correctamente (PID: !SERVICE_PID!)
        call :log "Servicio iniciado (PID: !SERVICE_PID!)"
        echo.
        echo URLs de acceso:
        echo   Documentación: https://127.0.0.1:48732/docs
        echo   Health Check:  https://127.0.0.1:48732/api/v1/health
        echo   Login:         https://127.0.0.1:48732/token
        echo.
        echo NOTA: Acepta el certificado auto-firmado en tu navegador
    ) else (
        echo Error: No se pudo obtener el PID del servicio
        call :log "Error al iniciar servicio - PID no encontrado"
        exit /b 1
    )
    goto :eof
)

REM Comando stop
if "%1"=="stop" (
    call :check_service
    if !ERRORLEVEL! EQU 1 (
        echo El servicio ya está detenido
        exit /b 1
    )

    echo Deteniendo BackendBot API Service...
    call :log "Deteniendo servicio (PID: !SERVICE_PID!)"

    REM Detener el proceso
    taskkill /PID !SERVICE_PID! /F >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        del "%PID_FILE%" 2>NUL
        echo Servicio detenido correctamente
        call :log "Servicio detenido correctamente"
    ) else (
        echo Error al detener el servicio
        call :log "Error al detener servicio"
        exit /b 1
    )
    goto :eof
)

REM Comando status
if "%1"=="status" (
    echo === BackendBot API Service Status ===
    call :check_service
    if !ERRORLEVEL! EQU 0 (
        echo Estado: Ejecutándose
        echo PID: !SERVICE_PID!
        echo Log: %SERVICE_LOG%
        echo Output: %LOG_DIR%\api_output.log
    ) else (
        echo Estado: Detenido
        echo Log: %SERVICE_LOG%
    )
    goto :eof
)

REM Comando restart
if "%1"=="restart" (
    echo Reiniciando BackendBot API Service...
    call :log "Reiniciando servicio"

    REM Detener si está ejecutándose
    call :check_service
    if !ERRORLEVEL! EQU 0 (
        taskkill /PID !SERVICE_PID! /F >nul 2>&1
        del "%PID_FILE%" 2>NUL
        timeout /t 1 /nobreak >nul
    )

    REM Iniciar nuevamente
    goto :start_service
    :start_service
    start /B python "%API_SCRIPT%" --https > "%LOG_DIR%\api_output.log" 2>&1
    timeout /t 2 /nobreak >nul

    REM Obtener nuevo PID
    for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO TABLE ^| find "python.exe"') do (
        set "SERVICE_PID_NEW=%%i"
        goto :found_pid_restart
    )
    :found_pid_restart

    if defined SERVICE_PID_NEW (
        echo !SERVICE_PID_NEW! > "%PID_FILE%"
        echo Servicio reiniciado correctamente (PID: !SERVICE_PID_NEW!)
        call :log "Servicio reiniciado (PID: !SERVICE_PID_NEW!)"
    ) else (
        echo Error: No se pudo reiniciar el servicio
        call :log "Error al reiniciar servicio"
        exit /b 1
    )
    goto :eof
)

REM Comando logs
if "%1"=="logs" (
    if exist "%SERVICE_LOG%" (
        echo === Service Logs ===
        type "%SERVICE_LOG%"
    ) else (
        echo No hay logs del servicio disponibles
    )

    if exist "%LOG_DIR%\api_output.log" (
        echo.
        echo === API Output Logs ===
        type "%LOG_DIR%\api_output.log"
    )
    goto :eof
)

REM Comando help
if "%1"=="" (
    echo BackendBot API Service Manager
    echo ===============================
    echo.
    echo Uso: %0 {start^|stop^|status^|restart^|logs}
    echo.
    echo Comandos:
    echo   start   - Iniciar el servicio API
    echo   stop    - Detener el servicio API
    echo   status  - Ver estado del servicio
    echo   restart - Reiniciar el servicio
    echo   logs    - Ver logs del servicio
    echo.
    echo El servicio se ejecuta en:
    echo   Host: 127.0.0.1 (localhost only)
    echo   Puerto: 48732
    echo   HTTPS: Certificado auto-firmado
    goto :eof
)

REM Comando desconocido
echo Comando desconocido: %1
echo Use %0 sin parámetros para ver la ayuda
exit /b 1