# Script de PowerShell para ejecutar tareas del backend en paralelo
# Usando jobs para aprovechar ejecución en segundo plano

param(
    [switch]$Verbose,
    [switch]$SkipTests,
    [switch]$SkipLint,
    [switch]$SkipBuild
)

Write-Host "=== BackendBot - Ejecución Paralela de Tareas ===" -ForegroundColor Cyan
Write-Host "Fecha: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

# Función para ejecutar comando en job
function Start-BackgroundJob {
    param(
        [string]$Name,
        [scriptblock]$ScriptBlock,
        [string]$WorkingDirectory = $PWD
    )

    $job = Start-Job -Name $Name -ScriptBlock $ScriptBlock -ArgumentList $WorkingDirectory
    Write-Host "Iniciado job: $Name (ID: $($job.Id))" -ForegroundColor Green
    return $job
}

# Función para esperar y mostrar resultados
function Wait-AndShowResults {
    param([array]$Jobs)

    Write-Host "`nEsperando que terminen $($Jobs.Count) jobs..." -ForegroundColor Yellow

    $completed = 0
    $total = $Jobs.Count

    while ($completed -lt $total) {
        $running = Get-Job | Where-Object { $_.State -eq 'Running' }
        $completed = $total - $running.Count

        Write-Progress -Activity "Ejecutando tareas en paralelo" -Status "$completed/$total completadas" -PercentComplete (($completed / $total) * 100)

        Start-Sleep -Seconds 2
    }

    Write-Progress -Activity "Ejecutando tareas en paralelo" -Completed

    Write-Host "`n=== RESULTADOS DE JOBS ===" -ForegroundColor Cyan

    foreach ($job in $Jobs) {
        $result = Receive-Job -Job $job -Wait
        Write-Host "`n--- Job: $($job.Name) ---" -ForegroundColor Magenta

        if ($job.State -eq 'Completed') {
            Write-Host "Estado: Completado" -ForegroundColor Green
            if ($result) {
                Write-Host "Salida:" -ForegroundColor White
                $result | ForEach-Object { Write-Host "  $_" }
            }
        } else {
            Write-Host "Estado: $($job.State)" -ForegroundColor Red
            if ($job.ChildJobs[0].JobStateInfo.Reason) {
                Write-Host "Error: $($job.ChildJobs[0].JobStateInfo.Reason.Message)" -ForegroundColor Red
            }
        }

        Remove-Job -Job $job -Force
    }
}

# Lista de jobs a ejecutar
$jobs = @()

# Job 1: Ejecutar tests
if (-not $SkipTests) {
    $testScript = {
        param($workDir)
        Set-Location $workDir
        Write-Host "Ejecutando tests..."
        try {
            $output = & python -m pytest tests/ -v --tb=short 2>&1
            return $output
        } catch {
            return "Error ejecutando tests: $($_.Exception.Message)"
        }
    }
    $jobs += Start-BackgroundJob -Name "Tests" -ScriptBlock $testScript
}

# Job 2: Linting del código
if (-not $SkipLint) {
    $lintScript = {
        param($workDir)
        Set-Location $workDir
        Write-Host "Ejecutando linting..."
        try {
            $output = & python -m ruff check src/ --output-format=full 2>&1
            return $output
        } catch {
            return "Error en linting: $($_.Exception.Message)"
        }
    }
    $jobs += Start-BackgroundJob -Name "Linting" -ScriptBlock $lintScript
}

# Job 3: Verificar dependencias
$depsScript = {
    param($workDir)
    Set-Location $workDir
    Write-Host "Verificando dependencias..."
    try {
        $output = & python -c "import sys; print('Python version:', sys.version); import fastapi, uvicorn, psutil, sqlalchemy; print('Dependencias OK')" 2>&1
        return $output
    } catch {
        return "Error verificando dependencias: $($_.Exception.Message)"
    }
}
$jobs += Start-BackgroundJob -Name "Dependencies" -ScriptBlock $depsScript

# Job 4: Verificar configuración
$configScript = {
    param($workDir)
    Set-Location $workDir
    Write-Host "Verificando configuración..."
    try {
        $output = & python -c "from src.backendbot.config import settings; print('Configuración cargada correctamente'); print(f'CPU Threshold: {settings.CPU_THRESHOLD}'); print(f'RAM Threshold: {settings.RAM_THRESHOLD}MB')" 2>&1
        return $output
    } catch {
        return "Error en configuración: $($_.Exception.Message)"
    }
}
$jobs += Start-BackgroundJob -Name "ConfigCheck" -ScriptBlock $configScript

# Job 5: Verificar archivos del proyecto
$filesScript = {
    param($workDir)
    Set-Location $workDir
    Write-Host "Verificando archivos del proyecto..."
    $files = @(
        "src/backendbot/backend.py",
        "src/backendbot/config.py",
        "src/backendbot/utils.py",
        "requirements.txt",
        "README.md"
    )
    $missing = @()
    foreach ($file in $files) {
        if (-not (Test-Path $file)) {
            $missing += $file
        }
    }
    if ($missing.Count -eq 0) {
        return "Todos los archivos principales están presentes"
    } else {
        return "Archivos faltantes: $($missing -join ', ')"
    }
}
$jobs += Start-BackgroundJob -Name "FileCheck" -ScriptBlock $filesScript

# Job 6: Generar documentación (si hay sphinx o similar)
$docsScript = {
    param($workDir)
    Set-Location $workDir
    Write-Host "Generando documentación..."
    try {
        if (Test-Path "docs/") {
            $output = & python -c "print('Directorio docs encontrado, pero no hay generador configurado')" 2>&1
        } else {
            $output = "No hay directorio docs/"
        }
        return $output
    } catch {
        return "Error generando docs: $($_.Exception.Message)"
    }
}
$jobs += Start-BackgroundJob -Name "Documentation" -ScriptBlock $docsScript

# Job 7: Verificar base de datos (opcional)
$dbScript = {
    param($workDir)
    Set-Location $workDir
    Write-Host "Verificando base de datos..."
    try {
        $output = & python -c "from src.backendbot.utils import async_engine; print('DB Engine:', 'Configurado' if async_engine else 'No configurado')" 2>&1
        return $output
    } catch {
        return "Error verificando DB: $($_.Exception.Message)"
    }
}
$jobs += Start-BackgroundJob -Name "DatabaseCheck" -ScriptBlock $dbScript

# Job 8: Verificar logs
$logsScript = {
    param($workDir)
    Set-Location $workDir
    Write-Host "Verificando logs..."
    $logFile = "logs/backend.log"
    if (Test-Path $logFile) {
        $size = (Get-Item $logFile).Length
        $lastWrite = (Get-Item $logFile).LastWriteTime
        return "Log file existe - Tamaño: $([math]::Round($size/1KB, 2)) KB - Última modificación: $lastWrite"
    } else {
        return "Archivo de log no encontrado: $logFile"
    }
}
$jobs += Start-BackgroundJob -Name "LogCheck" -ScriptBlock $logsScript

# Esperar y mostrar resultados
Wait-AndShowResults -Jobs $jobs

Write-Host "`n=== RESUMEN FINAL ===" -ForegroundColor Cyan
Write-Host "Todas las tareas paralelas han sido completadas." -ForegroundColor Green
Write-Host "Revisa los resultados arriba para cualquier error o problema." -ForegroundColor Yellow

# Limpiar jobs restantes
Get-Job | Remove-Job -Force

Write-Host "`nScript completado en $(Get-Date)" -ForegroundColor Cyan
