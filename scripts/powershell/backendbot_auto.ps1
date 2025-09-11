# PowerShell: Automatización avanzada para BackendBot
# Ejecuta tests, lint, monitorización y configuración de auto-inicio en paralelo

param(
    [switch]$SkipLint,
    [switch]$SkipTests,
    [switch]$SkipMonitor,
    [switch]$InstallAutoStart,
    [switch]$UninstallAutoStart,
    [switch]$StatusAutoStart,
    [switch]$StartAutoStart,
    [switch]$StopAutoStart
)

Write-Host "=== BackendBot: Automatización en paralelo ===" -ForegroundColor Cyan
Write-Host "Fecha: $(Get-Date)" -ForegroundColor Yellow

# Función para gestión de auto-inicio
function Invoke-AutoStartManagement {
    param([string]$Action)

    switch ($Action) {
        "install" {
            Write-Host "Instalando auto-inicio..." -ForegroundColor Yellow
            & ".\install_autostart.ps1"
        }
        "uninstall" {
            Write-Host "Desinstalando auto-inicio..." -ForegroundColor Yellow
            & ".\backend_service.ps1" -Uninstall
            Unregister-ScheduledTask -TaskName "BackendBotMonitor" -Confirm:$false -ErrorAction SilentlyContinue
        }
        "status" {
            Write-Host "Estado del auto-inicio:" -ForegroundColor Cyan
            & ".\backend_service.ps1" -Status
        }
        "start" {
            Write-Host "Iniciando servicios..." -ForegroundColor Green
            & ".\start_backend_quick.ps1"
        }
        "stop" {
            Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
            & ".\stop_backend_quick.ps1"
        }
    }
}

# Gestionar auto-inicio si se solicita
if ($InstallAutoStart) {
    Invoke-AutoStartManagement "install"
    exit 0
}
if ($UninstallAutoStart) {
    Invoke-AutoStartManagement "uninstall"
    exit 0
}
if ($StatusAutoStart) {
    Invoke-AutoStartManagement "status"
    exit 0
}
if ($StartAutoStart) {
    Invoke-AutoStartManagement "start"
    exit 0
}
if ($StopAutoStart) {
    Invoke-AutoStartManagement "stop"
    exit 0
}

function Start-BackgroundJob {
    param(
        [string]$Name,
        [scriptblock]$ScriptBlock
    )
    $job = Start-Job -Name $Name -ScriptBlock $ScriptBlock
    Write-Host "Iniciado job: $Name (ID: $($job.Id))" -ForegroundColor Green
    return $job
}

$jobs = @()

if (-not $SkipTests) {
    $jobs += Start-BackgroundJob -Name "Tests" -ScriptBlock {
        $env:API_KEY = "tu_clave_aqui"
        python -m pytest tests/ --disable-warnings -v
    }
}

if (-not $SkipLint) {
    $jobs += Start-BackgroundJob -Name "Lint" -ScriptBlock {
        python -m ruff check src/ --output-format=full
    }
}

if (-not $SkipMonitor) {
    $jobs += Start-BackgroundJob -Name "Monitor" -ScriptBlock {
        # Iniciar monitor de salud
        & ".\backend_monitor.ps1" -Start -CheckInterval 30
    }
}

Write-Host "Esperando que terminen los jobs..." -ForegroundColor Yellow
Wait-Job -Job $jobs

Write-Host "Resultados de los jobs:" -ForegroundColor Cyan
foreach ($job in $jobs) {
    Write-Host "--- $($job.Name) ---" -ForegroundColor Magenta
    Receive-Job -Job $job
    Remove-Job -Job $job
}

Write-Host "Automatización completada." -ForegroundColor Green
Write-Host ""
Write-Host "Comandos adicionales disponibles:" -ForegroundColor Cyan
Write-Host "  .\backendbot_auto.ps1 -InstallAutoStart    # Instalar auto-inicio" -ForegroundColor White
Write-Host "  .\backendbot_auto.ps1 -StatusAutoStart     # Ver estado" -ForegroundColor White
Write-Host "  .\backendbot_auto.ps1 -StartAutoStart      # Iniciar servicios" -ForegroundColor White
Write-Host "  .\backendbot_auto.ps1 -StopAutoStart       # Detener servicios" -ForegroundColor White
Write-Host "  .\backendbot_auto.ps1 -UninstallAutoStart  # Desinstalar auto-inicio" -ForegroundColor White
