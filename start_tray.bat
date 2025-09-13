@echo off
echo Iniciando BackendBot Tray Icon...
cd /d "%~dp0"

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

REM Verificar si las dependencias están instaladas
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias si requirements.txt existe
if exist "requirements.txt" (
    echo Instalando dependencias...
    pip install -r requirements.txt
)

REM Verificar que el archivo tray_icon.py existe
if not exist "src\backendbot\tray_icon.py" (
    echo ERROR: No se encuentra src\backendbot\tray_icon.py
    pause
    exit /b 1
)

REM Iniciar el tray icon
echo Iniciando tray icon...
python -m src.backendbot.tray_icon

pause