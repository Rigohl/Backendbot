# PowerShell: Automatización avanzada para BackendBot
# Ejecuta tests, lint y monitorización en paralelo y en segundo plano

param(
    [switch]$SkipLint,
    [switch]$SkipTests,
    [switch]$SkipMonitor
)

Write-Host "=== BackendBot: Automatización en paralelo ===" -ForegroundColor Cyan
Write-Host "Fecha: $(Get-Date)" -ForegroundColor Yellow

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
        python main.py
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
