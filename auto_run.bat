@echo off
REM BackendBot Auto-Setup y Verificación Completa
REM Ejecuta todo automáticamente en múltiples terminales

echo [BOT] BackendBot Auto-Setup Completo
echo =====================================

REM Verificar Python
echo [OK] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instala Python 3.12+
    pause
    exit /b 1
)

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt --quiet

REM Configurar base de datos
echo [DB] Configurando base de datos...
python setup_postgres.py >nul 2>&1
if errorlevel 1 (
    echo [WARN] PostgreSQL no disponible, usando SQLite...
)

REM Verificar configuración
echo [CONFIG] Verificando configuración...
if not exist .env (
    echo DATABASE_URL="sqlite:///data/backend_data.db" > .env
)

REM Crear directorios necesarios
if not exist data mkdir data
if not exist logs mkdir logs

REM Iniciar launcher automático
echo [START] Iniciando sistema automático...
start "BackendBot-Server" cmd /c "python auto_launcher.py"

echo [OK] Sistema iniciado automáticamente!
echo [WEB] Servidor: http://localhost:8000
echo [STATS] Dashboard: http://localhost:8000/dashboard
echo [DOCS] API Docs: http://localhost:8000/docs
echo.
echo [STOP] Presiona cualquier tecla para detener...
pause >nul

REM Detener procesos
echo [HALT] Deteniendo procesos...
taskkill /f /im python.exe /fi "WINDOWTITLE eq BackendBot-Server" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq BackendBot-Verifier" >nul 2>&1

echo [OK] Sistema detenido
pause