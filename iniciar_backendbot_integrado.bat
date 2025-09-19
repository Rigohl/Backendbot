@echo off
REM BackendBot - Inicio Rápido Integrado
REM Versión completa con todos los sistemas integrados

echo 🐝 BackendBot - Sistema Integrado Completo
echo ===========================================
echo.

REM Verificar si existe entorno virtual
if exist venv\Scripts\activate.bat (
    echo ✅ Entorno virtual encontrado
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Entorno virtual no encontrado, ejecutando sin activar...
)

REM Configurar PYTHONPATH
set PYTHONPATH=%~dp0src;%PYTHONPATH%

echo 🚀 Iniciando BackendBot Integrado...
echo.
echo Características incluidas:
echo • Dashboard en tiempo real con métricas del sistema
echo • 6 Bots especializados completamente funcionales
echo • Sistema de notificaciones inteligente
echo • Gestión de energía con perfiles adaptativos
echo • Sistema de backup robusto
echo • API REST completa (accesible en http://localhost:8000/docs)
echo • Chat interactivo integrado
echo • Ícono en bandeja del sistema
echo • Menú completo con todas las opciones
echo.

REM Ejecutar la aplicación integrada
python src\backendbot\main_integrated.py

pause