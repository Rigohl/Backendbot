# Script de monitoreo automático para BackendBot
# Se ejecuta en segundo plano y reinicia el backend si es necesario

param(
    [int]$CheckInterval = 30,  # Segundos entre verificaciones
    [switch]$Start,
    [switch]$Stop
)

$logPath = Join-Path $PSScriptRoot "logs\monitor.log"
$backendUrl = "http://127.0.0.1:8000"
$maxRetries = 3
$retryDelay = 5

function Write-MonitorLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] [$Level] $Message" | Out-File -FilePath $logPath -Append
}

function Test-BackendHealth {
    try {
        $response = Invoke-WebRequest -Uri "$backendUrl/health" -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            if ($data.status -eq "healthy") {
                return $true
            }
        }
    } catch {
        Write-MonitorLog "Health check failed: $($_.Exception.Message)" "ERROR"
    }
    return $false
}

function Start-BackendProcess {
    Write-MonitorLog "Starting backend process..."

    try {
        $pythonPath = (Get-Command python).Source
        $backendPath = Join-Path $PSScriptRoot "main.py"

        # Configurar variables de entorno
        $env:API_KEY = "tu_clave_aqui"

        $process = Start-Process -FilePath $pythonPath -ArgumentList $backendPath -WorkingDirectory $PSScriptRoot -PassThru -WindowStyle Hidden

        # Esperar un poco para que inicie
        Start-Sleep -Seconds 5

        # Verificar que el proceso esté corriendo
        if (-not $process.HasExited) {
            Write-MonitorLog "Backend process started successfully (PID: $($process.Id))"
            return $process
        } else {
            Write-MonitorLog "Backend process failed to start" "ERROR"
            return $null
        }
    } catch {
        Write-MonitorLog "Error starting backend: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Stop-BackendProcess {
    param([System.Diagnostics.Process]$Process)

    if ($Process -and -not $Process.HasExited) {
        Write-MonitorLog "Stopping backend process (PID: $($Process.Id))"
        $Process.Kill()
        $Process.WaitForExit(5000)
        Write-MonitorLog "Backend process stopped"
    }
}

function Start-MonitorLoop {
    Write-MonitorLog "Starting BackendBot monitor service"
    Write-MonitorLog "Check interval: $CheckInterval seconds"

    $backendProcess = $null
    $consecutiveFailures = 0

    while ($true) {
        try {
            # Verificar si el proceso está corriendo
            if ($backendProcess -and -not $backendProcess.HasExited) {
                # Proceso corriendo, verificar salud
                if (Test-BackendHealth) {
                    $consecutiveFailures = 0
                    Write-MonitorLog "Backend is healthy"
                } else {
                    $consecutiveFailures++
                    Write-MonitorLog "Backend health check failed ($consecutiveFailures/$maxRetries)" "WARNING"

                    if ($consecutiveFailures -ge $maxRetries) {
                        Write-MonitorLog "Maximum failures reached, restarting backend..." "ERROR"
                        Stop-BackendProcess $backendProcess
                        $backendProcess = Start-BackendProcess
                        $consecutiveFailures = 0
                    }
                }
            } else {
                # Proceso no está corriendo, intentar iniciar
                Write-MonitorLog "Backend process not running, starting..." "WARNING"
                $backendProcess = Start-BackendProcess
                $consecutiveFailures = 0
            }

        } catch {
            Write-MonitorLog "Error in monitor loop: $($_.Exception.Message)" "ERROR"
        }

        # Esperar hasta la siguiente verificación
        Start-Sleep -Seconds $CheckInterval
    }
}

function Stop-MonitorService {
    Write-MonitorLog "Stopping monitor service"

    # Detener todos los procesos de Python relacionados con BackendBot
    $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
    foreach ($proc in $pythonProcesses) {
        try {
            $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            if ($cmdLine -and ($cmdLine.Contains("main.py") -or $cmdLine.Contains("backend_monitor"))) {
                Write-MonitorLog "Stopping process PID: $($proc.Id)"
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
        } catch {
            continue
        }
    }

    Write-MonitorLog "Monitor service stopped"
}

# Crear directorio de logs si no existe
$logDir = Split-Path $logPath -Parent
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

if ($Start) {
    Write-MonitorLog "Monitor service started manually"
    Start-MonitorLoop
} elseif ($Stop) {
    Stop-MonitorService
} else {
    Write-Host "BackendBot Monitor Service" -ForegroundColor Cyan
    Write-Host "Uso: .\backend_monitor.ps1 [-Start|-Stop] [-CheckInterval <segundos>]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor White
    Write-Host "  .\backend_monitor.ps1 -Start                          # Iniciar monitoreo"
    Write-Host "  .\backend_monitor.ps1 -Start -CheckInterval 60       # Monitoreo cada 60 segundos"
    Write-Host "  .\backend_monitor.ps1 -Stop                           # Detener monitoreo"
    Write-Host ""
    Write-Host "El monitor verifica automáticamente la salud del backend" -ForegroundColor Green
    Write-Host "y lo reinicia si es necesario." -ForegroundColor Green
}