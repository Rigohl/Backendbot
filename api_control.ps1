# BackendBot API Service Control Script
# ====================================
#
# Script para controlar el servicio API de BackendBot
# Ejecuta la API de manera invisible en segundo plano
#
# Uso:
#     .\api_control.ps1 start    - Iniciar servicio
#     .\api_control.ps1 stop     - Detener servicio
#     .\api_control.ps1 status   - Ver estado
#     .\api_control.ps1 restart  - Reiniciar servicio
#
# Autor: BackendBot Team
# Version: 0.1.0

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "status", "restart")]
    [string]$Action
)

# Configuración
$PythonExe = "python"
$ServiceScript = Join-Path $PSScriptRoot "api_service_launcher.py"
$ScriptDir = $PSScriptRoot

# Verificar que el script de servicio existe
if (-not (Test-Path $ServiceScript)) {
    Write-Host "❌ Error: No se encuentra api_service_launcher.py" -ForegroundColor Red
    Write-Host "Asegúrate de que el archivo esté en el mismo directorio" -ForegroundColor Yellow
    Read-Host "Presiona Enter para continuar"
    exit 1
}

# Función para mostrar ayuda
function Show-Help {
    Write-Host ""
    Write-Host "BackendBot API Service Control" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Uso: $($MyInvocation.MyCommand.Name) {start|stop|status|restart}"
    Write-Host ""
    Write-Host "  start   - Iniciar el servicio API de manera invisible"
    Write-Host "  stop    - Detener el servicio API"
    Write-Host "  status  - Mostrar estado del servicio"
    Write-Host "  restart - Reiniciar el servicio API"
    Write-Host ""
    Read-Host "Presiona Enter para continuar"
    exit 0
}

# Función para ejecutar comando Python
function Invoke-PythonCommand {
    param([string]$Command)

    try {
        $process = Start-Process -FilePath $PythonExe -ArgumentList "`"$ServiceScript`" $Command" -NoNewWindow -Wait -PassThru -WorkingDirectory $ScriptDir
        return $process.ExitCode
    }
    catch {
        Write-Host "❌ Error al ejecutar comando: $($_.Exception.Message)" -ForegroundColor Red
        return 1
    }
}

# Mostrar ayuda si no se especifica acción
if (-not $Action) {
    Show-Help
}

# Procesar acciones
switch ($Action) {
    "start" {
        Write-Host ""
        Write-Host "🚀 Iniciando BackendBot API Service..." -ForegroundColor Green
        Write-Host ""

        $exitCode = Invoke-PythonCommand "start"

        if ($exitCode -eq 0) {
            Write-Host ""
            Write-Host "✅ Servicio iniciado correctamente" -ForegroundColor Green
            Write-Host ""
        } else {
            Write-Host ""
            Write-Host "❌ Error al iniciar el servicio" -ForegroundColor Red
            Read-Host "Presiona Enter para continuar"
            exit 1
        }
    }

    "stop" {
        Write-Host ""
        Write-Host "🛑 Deteniendo BackendBot API Service..." -ForegroundColor Yellow
        Write-Host ""

        $exitCode = Invoke-PythonCommand "stop"

        if ($exitCode -eq 0) {
            Write-Host ""
            Write-Host "✅ Servicio detenido correctamente" -ForegroundColor Green
            Write-Host ""
        } else {
            Write-Host ""
            Write-Host "❌ Error al detener el servicio" -ForegroundColor Red
            Read-Host "Presiona Enter para continuar"
            exit 1
        }
    }

    "status" {
        Write-Host ""
        Write-Host "📊 Estado del BackendBot API Service:" -ForegroundColor Cyan
        Write-Host ""

        Invoke-PythonCommand "status"
        Write-Host ""
    }

    "restart" {
        Write-Host ""
        Write-Host "🔄 Reiniciando BackendBot API Service..." -ForegroundColor Magenta
        Write-Host ""

        # Detener servicio
        Write-Host "Deteniendo servicio actual..." -ForegroundColor Yellow
        Invoke-PythonCommand "stop"
        Start-Sleep -Seconds 2

        # Iniciar servicio
        Write-Host "Iniciando servicio..." -ForegroundColor Green
        $exitCode = Invoke-PythonCommand "start"

        if ($exitCode -eq 0) {
            Write-Host ""
            Write-Host "✅ Servicio reiniciado correctamente" -ForegroundColor Green
            Write-Host ""
        } else {
            Write-Host ""
            Write-Host "❌ Error al reiniciar el servicio" -ForegroundColor Red
            Read-Host "Presiona Enter para continuar"
            exit 1
        }
    }
}

# Pausa final
Read-Host "Presiona Enter para continuar"