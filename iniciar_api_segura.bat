@echo off
REM BackendBot API Server - Inicio Seguro e Invisible
REM ==================================================
REM Inicia el servidor API en modo seguro local
REM - Solo localhost (127.0.0.1)
REM - Puerto no estándar (48732)
REM - Modo invisible (sin output)
REM - Segundo plano

echo.
echo 🔒 Iniciando BackendBot API Server - Modo Seguro...
echo.

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Ejecutar el servidor en segundo plano de forma invisible
start /B python api_server.py >nul 2>&1

REM Esperar un momento para que inicie
timeout /t 2 /nobreak >nul

REM Verificar que el servidor esté funcionando
curl -s http://127.0.0.1:48732/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: No se pudo verificar que el servidor esté funcionando
    echo    Verifica que no haya otro proceso usando el puerto 48732
    pause
    exit /b 1
)

echo ✅ BackendBot API Server ejecutándose correctamente
echo 🌐 Accesible solo en: http://127.0.0.1:48732
echo 👻 Modo invisible activado
echo 📖 Documentación: http://127.0.0.1:48732/docs
echo 💚 Health Check: http://127.0.0.1:48732/api/v1/health
echo.
echo 🔒 El servidor está protegido y solo accesible desde esta máquina
echo.

REM Mantener la ventana abierta por un momento
timeout /t 3 >nul