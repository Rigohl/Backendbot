# Script de PowerShell para configurar BackendBot como servicio automático
# Se ejecuta al inicio del sistema y se mantiene corriendo

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status,
    [switch]$Start,
    [switch]$Stop
)

$serviceName = "BackendBotService"
$backendPath = Join-Path $PSScriptRoot "main.py"
$pythonPath = (Get-Command python).Source
$logPath = Join-Path $PSScriptRoot "logs\service.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $logPath -Append
}

function Install-BackendService {
    Write-Host "Instalando BackendBot como servicio automático..." -ForegroundColor Cyan

    # Crear directorio de logs si no existe
    $logDir = Split-Path $logPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    # Crear script de wrapper para el servicio
    $wrapperScript = @"
# Wrapper script para BackendBot Service
import sys
import os
import time
import subprocess
from datetime import datetime

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(r'$logPath', 'a') as f:
        f.write(f'{timestamp} - {message}\n')

def main():
    log_message('BackendBot Service starting...')
    os.environ['API_KEY'] = 'tu_clave_aqui'

    while True:
        try:
            log_message('Starting backend process...')
            process = subprocess.Popen([
                r'$pythonPath',
                r'$backendPath'
            ], cwd=r'$PSScriptRoot')

            process.wait()
            log_message(f'Backend process exited with code: {process.returncode}')

            if process.returncode != 0:
                log_message('Backend crashed, restarting in 5 seconds...')
                time.sleep(5)
            else:
                log_message('Backend stopped normally')
                break

        except Exception as e:
            log_message(f'Error in service wrapper: {e}')
            time.sleep(5)

if __name__ == '__main__':
    main()
"@

    $wrapperPath = Join-Path $PSScriptRoot "backend_service_wrapper.py"
    $wrapperScript | Out-File -FilePath $wrapperPath -Encoding UTF8

    # Crear tarea programada para inicio automático
    $action = New-ScheduledTaskAction -Execute $pythonPath -Argument $wrapperPath -WorkingDirectory $PSScriptRoot
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType InteractiveToken

    Register-ScheduledTask -TaskName $serviceName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

    Write-Host "Servicio instalado correctamente. Se iniciará automáticamente al arranque del sistema." -ForegroundColor Green
    Write-Log "Service installed successfully"
}

function Uninstall-BackendService {
    Write-Host "Desinstalando BackendBot service..." -ForegroundColor Yellow

    # Detener tarea si está corriendo
    Stop-ScheduledTask -TaskName $serviceName -ErrorAction SilentlyContinue

    # Eliminar tarea programada
    Unregister-ScheduledTask -TaskName $serviceName -Confirm:$false -ErrorAction SilentlyContinue

    # Eliminar archivos temporales
    $wrapperPath = Join-Path $PSScriptRoot "backend_service_wrapper.py"
    if (Test-Path $wrapperPath) {
        Remove-Item $wrapperPath -Force
    }

    Write-Host "Servicio desinstalado correctamente." -ForegroundColor Green
    Write-Log "Service uninstalled successfully"
}

function Get-ServiceStatus {
    $task = Get-ScheduledTask -TaskName $serviceName -ErrorAction SilentlyContinue
    if ($task) {
        $lastRun = $task.LastRunTime
        $nextRun = $task.NextRunTime
        $state = $task.State

        Write-Host "=== Estado del Servicio BackendBot ===" -ForegroundColor Cyan
        Write-Host "Estado: $state" -ForegroundColor $(if ($state -eq 'Ready') { 'Green' } else { 'Yellow' })
        Write-Host "Última ejecución: $lastRun" -ForegroundColor White
        Write-Host "Próxima ejecución: $nextRun" -ForegroundColor White

        # Verificar si el proceso está corriendo
        $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
        $backendRunning = $false
        foreach ($proc in $pythonProcesses) {
            try {
                $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
                if ($cmdLine -and $cmdLine.Contains("main.py")) {
                    $backendRunning = $true
                    break
                }
            } catch {
                continue
            }
        }

        Write-Host "Backend corriendo: $(if ($backendRunning) { 'Sí' } else { 'No' })" -ForegroundColor $(if ($backendRunning) { 'Green' } else { 'Red' })

        # Mostrar últimas líneas del log
        if (Test-Path $logPath) {
            Write-Host "`n=== Últimas líneas del log ===" -ForegroundColor Cyan
            Get-Content $logPath -Tail 5
        }
    } else {
        Write-Host "Servicio no instalado." -ForegroundColor Red
    }
}

function Start-BackendService {
    Write-Host "Iniciando BackendBot service..." -ForegroundColor Green
    Start-ScheduledTask -TaskName $serviceName
    Write-Log "Service started manually"
}

function Stop-BackendService {
    Write-Host "Deteniendo BackendBot service..." -ForegroundColor Yellow
    Stop-ScheduledTask -TaskName $serviceName
    Write-Log "Service stopped manually"
}

# Main logic
if ($Install) {
    Install-BackendService
} elseif ($Uninstall) {
    Uninstall-BackendService
} elseif ($Status) {
    Get-ServiceStatus
} elseif ($Start) {
    Start-BackendService
} elseif ($Stop) {
    Stop-BackendService
} else {
    Write-Host "Uso: .\backend_service.ps1 [-Install|-Uninstall|-Status|-Start|-Stop]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor White
    Write-Host "  .\backend_service.ps1 -Install    # Instalar como servicio automático"
    Write-Host "  .\backend_service.ps1 -Status     # Ver estado del servicio"
    Write-Host "  .\backend_service.ps1 -Start      # Iniciar manualmente"
    Write-Host "  .\backend_service.ps1 -Stop       # Detener manualmente"
    Write-Host "  .\backend_service.ps1 -Uninstall  # Desinstalar servicio"
}