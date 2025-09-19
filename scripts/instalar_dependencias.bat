@echo off
REM Script alternativo para instalar REM Intentar instalar GPUtil con compatibilidad (ya no es crítico)
echo.
echo 🔄 Intentando instalar GPUtil...
pip install GPUtil || echo "⚠️ GPUtil no compatible - usando monitoreo alternativo de GPU (funciona igual)"ndencias con compatibilidad Python 3.12
echo ========================================
echo    INSTALACION DE DEPENDENCIAS
echo    BackendBot - Python 3.12 Compatible
echo ========================================
echo.

cd /d "%~dp0"

REM Verificar si existe entorno virtual
if not exist "venv" (
    echo ❌ ERROR: No se encuentra el entorno virtual
    echo    Ejecuta primero: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate
if errorlevel 1 (
    echo ❌ ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo ✅ Entorno virtual activado

REM Instalar dependencias principales
echo.
echo 🔄 Instalando dependencias principales...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ ERROR: Falló la instalación de dependencias principales
    pause
    exit /b 1
)

REM Instalar PyQt5 específicamente (por si no está en requirements.txt)
echo.
echo 🔄 Instalando PyQt5...
pip install PyQt5
if errorlevel 1 (
    echo ❌ ERROR: Falló la instalación de PyQt5
    echo    Intenta: pip install PyQt5 --only-binary=all
    pause
    exit /b 1
)

REM Intentar instalar GPUtil con compatibilidad
echo.
echo 🔄 Intentando instalar GPUtil...
pip install GPUtil || echo "⚠️ GPUtil no compatible con Python 3.12 - se usará monitoreo básico de GPU"

REM Verificar instalación completa
echo.
echo 🔍 Verificando instalación...

python -c "import fastapi, uvicorn, psutil; print('✅ FastAPI, Uvicorn, Psutil OK')" 2>nul
if errorlevel 1 (
    echo ❌ ERROR: Dependencias principales faltantes
    pause
    exit /b 1
)

python -c "import PyQt5; print('✅ PyQt5 OK')" 2>nul
if errorlevel 1 (
    echo ❌ ERROR: PyQt5 no instalado correctamente
    pause
    exit /b 1
)

python -c "try: import GPUtil; print('✅ GPUtil OK') except: print('⚠️ GPUtil no disponible - funcionalidad limitada')" 2>nul

echo.
echo ========================================
echo    INSTALACION COMPLETADA EXITOSAMENTE
echo ========================================
echo.
echo 🎉 ¡Todas las dependencias instaladas correctamente!
echo.
echo 📋 Estado final:
echo    ✅ FastAPI/Uvicorn: OK
echo    ✅ Psutil: OK
echo    ✅ PyQt5: OK
echo    ⚠️  GPUtil: Limitado (normal en Python 3.12)
echo.
echo 🚀 Puedes iniciar BackendBot con:
echo    iniciar_backendbot.bat
echo.
pause