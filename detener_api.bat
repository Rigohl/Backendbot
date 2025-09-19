@echo off
REM BackendBot API Server - Detener Servidor Seguro
REM ===============================================
REM Detiene el servidor API de forma segura

echo.
echo 🛑 Deteniendo BackendBot API Server...
echo.

REM Buscar y terminar procesos de Python que estén ejecutando api_server.py
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
    REM Verificar si este proceso Python está ejecutando nuestro servidor
    for /f %%j in ('wmic process where "ProcessId=%%i" get CommandLine /value ^| find "api_server.py"') do (
        echo 🔍 Encontrado proceso del servidor API (PID: %%i)
        taskkill /PID %%i /F >nul 2>&1
        if errorlevel 0 (
            echo ✅ Servidor detenido correctamente
        ) else (
            echo ❌ Error al detener el servidor
        )
        goto :end
    )
)

REM Si no se encontró el proceso específico, intentar por puerto
netstat -ano | find "48732" >nul 2>&1
if errorlevel 1 (
    echo ℹ️  No se encontró ningún servidor ejecutándose en el puerto 48732
    goto :end
)

REM Si hay algo en el puerto, intentar terminar procesos Python
echo 🔍 Intentando detener procesos Python...
taskkill /IM python.exe /F >nul 2>&1
if errorlevel 0 (
    echo ✅ Procesos Python detenidos
) else (
    echo ❌ No se pudieron detener procesos Python
)

:end
echo.
echo ✅ Operación completada
timeout /t 2 >nul