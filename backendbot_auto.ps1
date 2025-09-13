# PowerShell: Automatización completa de BackendBot
# Ejecuta tests, lint, monitorización y servicios en paralelo
# Muestra progreso en tiempo real

param(
    [switch]$SkipTests,
    [switch]$SkipLint,
    [switch]$SkipMonitor,
    [switch]$Verbose,
    [int]$MaxJobs = 4
)

Write-Host "=== BackendBot: Automatización Completa ===" -ForegroundColor Cyan
Write-Host "Fecha: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Modo: Paralelo con progreso" -ForegroundColor Green
Write-Host ""

# Función para mostrar progreso
function Show-Progress {
    param([int]$Completed, [int]$Total, [string]$Activity)
    $percent = [math]::Round(($Completed / $Total) * 100, 1)
    Write-Progress -Activity $Activity -Status "$Completed/$Total completado ($percent%)" -PercentComplete $percent
}

# Función para iniciar job con progreso
function Start-ProgressJob {
    param(
        [string]$Name,
        [scriptblock]$ScriptBlock,
        [ref]$JobCount
    )
    $job = Start-Job -Name $Name -ScriptBlock $ScriptBlock
    Write-Host "Iniciado job: $Name (ID: $($job.Id))" -ForegroundColor Green
    $JobCount.Value++
    return $job
}

# Función para esperar jobs con progreso
function Wait-ProgressJobs {
    param([array]$Jobs, [string]$Activity)
    $completed = 0
    $total = $Jobs.Count

    while ($completed -lt $total) {
        $running = Get-Job | Where-Object { $_.State -eq 'Running' }
        $completed = $total - $running.Count
        Show-Progress -Completed $completed -Total $total -Activity $Activity
        Start-Sleep -Seconds 1
    }

    Write-Progress -Activity $Activity -Completed
}

# Lista de jobs
$jobs = @()
$jobCount = 0

# Job 1: Tests
if (-not $SkipTests) {
    $testScript = {
        Write-Host "Ejecutando tests..."
        $env:API_KEY = "tu_clave_aqui"
        $result = python -m pytest tests/ --disable-warnings --tb=short -q 2>&1
        return @{
            Name = "Tests"
            Output = $result
            ExitCode = $LASTEXITCODE
        }
    }
    $jobs += Start-ProgressJob -Name "Tests" -ScriptBlock $testScript -JobCount ([ref]$jobCount)
}

# Job 2: Linting
if (-not $SkipLint) {
    $lintScript = {
        Write-Host "Ejecutando linting..."
        $result = python -m ruff check src/ --output-format=concise 2>&1
        return @{
            Name = "Lint"
            Output = $result
            ExitCode = $LASTEXITCODE
        }
    }
    $jobs += Start-ProgressJob -Name "Lint" -ScriptBlock $lintScript -JobCount ([ref]$jobCount)
}

# Job 3: Verificar configuración
$configScript = {
    Write-Host "Verificando configuración..."
    $env:API_KEY = "tu_clave_aqui"
    $result = python -c "from src.backendbot.config import settings; print('Configuración OK:', settings.API_KEY[:10] + '...')" 2>&1
    return @{
        Name = "Config"
        Output = $result
        ExitCode = $LASTEXITCODE
    }
}
$jobs += Start-ProgressJob -Name "Config" -ScriptBlock $configScript -JobCount ([ref]$jobCount)

# Job 4: Verificar servicios
$servicesScript = {
    Write-Host "Verificando servicios..."
    $result = python -c "import os; print('Servicios disponibles:', len([f for f in os.listdir('src/backendbot/services') if f.endswith('.py')]))" 2>&1
    return @{
        Name = "Services"
        Output = $result
        ExitCode = $LASTEXITCODE
    }
}
$jobs += Start-ProgressJob -Name "Services" -ScriptBlock $servicesScript -JobCount ([ref]$jobCount)

# Esperar todos los jobs
Wait-ProgressJobs -Jobs $jobs -Activity "Ejecutando tareas del backend"

# Mostrar resultados
Write-Host "`n=== RESULTADOS FINALES ===" -ForegroundColor Cyan

$passed = 0
$failed = 0

foreach ($job in $jobs) {
    $result = Receive-Job -Job $job -Wait
    Write-Host "`n--- $($result.Name) ---" -ForegroundColor Magenta

    if ($result.ExitCode -eq 0) {
        Write-Host "Estado: PASADO ✅" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "Estado: FALLADO ❌" -ForegroundColor Red
        $failed++
    }

    if ($Verbose -or $result.ExitCode -ne 0) {
        Write-Host "Salida:" -ForegroundColor White
        $result.Output | ForEach-Object { Write-Host "  $_" }
    }

    Remove-Job -Job $job -Force
}

# Resumen final
$total = $jobs.Count
$successRate = [math]::Round(($passed / $total) * 100, 1)

Write-Host "`n=== RESUMEN ===" -ForegroundColor Cyan
Write-Host "Total de tareas: $total" -ForegroundColor White
Write-Host "Pasadas: $passed ✅" -ForegroundColor Green
Write-Host "Falladas: $failed ❌" -ForegroundColor Red
Write-Host "Tasa de éxito: $successRate%" -ForegroundColor Yellow

if ($successRate -ge 80) {
    Write-Host "`n🎉 ¡Excelente progreso! Backend listo para producción." -ForegroundColor Green
} elseif ($successRate -ge 60) {
    Write-Host "`n⚠️  Buen progreso, pero hay que arreglar algunos fallos." -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Necesitas arreglar varios problemas antes de continuar." -ForegroundColor Red
}

Write-Host "`nScript completado: $(Get-Date)" -ForegroundColor Cyan