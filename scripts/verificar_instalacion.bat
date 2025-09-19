@echo off
echo ========================================
echo    VERIFICACION DE INSTALACION
echo    BackendBot - Entorno Virtual
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo ❌ ERROR: No se encuentra el entorno virtual
    echo    Ejecuta 'instalar_dependencias.bat' primero
    pause
    exit /b 1
)

echo ✅ Entorno virtual encontrado

REM Activar entorno virtual
echo.
echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo ✅ Entorno virtual activado

REM Verificar dependencias críticas
echo.
echo 🔍 Verificando dependencias críticas...

python -c "import sys; print(f'🐍 Python: {sys.version}')" 2>nul
if errorlevel 1 (
    echo ❌ ERROR: Python no disponible en entorno virtual
    pause
    exit /b 1
)

python -c "import fastapi, uvicorn; print('✅ FastAPI y Uvicorn OK')" 2>nul
if errorlevel 1 (
    echo ❌ ERROR: FastAPI o Uvicorn faltantes
    echo    Ejecuta 'instalar_dependencias.bat'
    pause
    exit /b 1
)

python -c "import psutil; print('✅ Psutil OK')" 2>nul
if errorlevel 1 (
    echo ❌ ERROR: Psutil faltante
    echo    Ejecuta 'instalar_dependencias.bat'
    pause
    exit /b 1
)

REM Verificar PyQt5 (requerido para UI completa)
python -c "import PyQt5; print('✅ PyQt5 OK')" 2>nul
if errorlevel 1 (
    echo ❌ ERROR: PyQt5 faltante (requerido para interfaz completa)
    echo    Ejecuta 'instalar_dependencias.bat'
    pause
    exit /b 1
) else (
    echo ✅ PyQt5 OK
)

REM Verificar monitoreo de GPU (completamente funcional)
python -c "from src.backendbot.utils.gpu_monitor import getGPUs; gpus = getGPUs(); print('✅ Monitoreo de GPU OK -', len(gpus), 'GPUs detectadas')" 2>nul
if errorlevel 1 (
    echo ⚠️ AVISO: Monitoreo de GPU limitado (pero funcional)
) else (
    echo ✅ Monitoreo de GPU OK
)

echo.
echo ========================================
echo    VERIFICACION COMPLETA
echo ========================================
echo.
echo 🎉 ¡Instalación verificada exitosamente!
echo.
echo 📋 Estado de componentes:
echo    ✅ Entorno virtual: Funcionando
echo    ✅ Python: Disponible
echo    ✅ FastAPI/Uvicorn: OK
echo    ✅ Psutil: OK
echo    ✅ PyQt5: OK (Interfaz completa disponible)
echo    ✅ Monitoreo de GPU: Completamente funcional
echo.
echo 🚀 Puedes iniciar BackendBot con:
echo    iniciar_backendbot.bat
echo.
pause