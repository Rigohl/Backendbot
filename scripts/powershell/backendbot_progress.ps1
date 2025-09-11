# PowerShell: BackendBot con progreso en tiempo real
# Ejecuta tareas en segundo plano y muestra % de progreso

param(
    [switch]$AutoStart,
    [switch]$SkipTests,
    [switch]$Verbose
)

Write-Host "=== BackendBot - Progreso en Tiempo Real ===" -ForegroundColor Cyan
Write-Host "Fecha: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

# Función para mostrar progreso
function Show-Progress {
    param(
        [string]$Activity,
        [int]$PercentComplete,
        [string]$Status
    )
    Write-Progress -Activity $Activity -Status $Status -PercentComplete $PercentComplete
    if ($Verbose) {
        Write-Host "[$PercentComplete%] $Status" -ForegroundColor Green
    }
}

# Función para ejecutar job con progreso
function Start-JobWithProgress {
    param(
        [string]$Name,
        [scriptblock]$ScriptBlock,
        [int]$ProgressId
    )

    Show-Progress -Activity "Ejecutando $Name" -PercentComplete 0 -Status "Iniciando..."

    $job = Start-Job -Name $Name -ScriptBlock $ScriptBlock

    Show-Progress -Activity "Ejecutando $Name" -PercentComplete 25 -Status "Job iniciado (ID: $($job.Id))"

    # Esperar un poco para que el job se estabilice
    Start-Sleep -Seconds 2

    Show-Progress -Activity "Ejecutando $Name" -PercentComplete 50 -Status "Procesando..."

    # Esperar a que termine
    Wait-Job -Job $job -Timeout 300  # 5 minutos máximo

    if ($job.State -eq 'Completed') {
        Show-Progress -Activity "Ejecutando $Name" -PercentComplete 100 -Status "Completado exitosamente"
    } elseif ($job.State -eq 'Running') {
        Show-Progress -Activity "Ejecutando $Name" -PercentComplete 75 -Status "Aún ejecutándose..."
        Stop-Job -Job $job -Confirm:$false
        Show-Progress -Activity "Ejecutando $Name" -PercentComplete 100 -Status "Terminado por timeout"
    } else {
        Show-Progress -Activity "Ejecutando $Name" -PercentComplete 100 -Status "Error: $($job.State)"
    }

    $result = Receive-Job -Job $job -ErrorAction SilentlyContinue
    Remove-Job -Job $job -Force

    return $result
}

# Lista de tareas con progreso
$tasks = @()

if (-not $SkipTests) {
    $tasks += @{
        Name = "Tests Unitarios"
        Script = {
            $env:API_KEY = "tu_clave_aqui"
            $result = python -m pytest tests/ --tb=no --disable-warnings -q 2>&1
            return @{
                Success = $LASTEXITCODE -eq 0
                Output = $result
                ExitCode = $LASTEXITCODE
            }
        }
    }
}

$tasks += @{
    Name = "Verificación Backend"
    Script = {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
            return @{
                Success = $true
                StatusCode = $response.StatusCode
                Content = $response.Content
            }
        } catch {
            return @{
                Success = $false
                Error = $_.Exception.Message
            }
        }
    }
}

$tasks += @{
    Name = "Linting Código"
    Script = {
        $result = python -m ruff check src/ --output-format=json 2>&1
        return @{
            Success = $LASTEXITCODE -eq 0
            Output = $result
            ExitCode = $LASTEXITCODE
        }
    }
}

$tasks += @{
    Name = "Verificación Dependencias"
    Script = {
        $result = python -c "import fastapi, uvicorn, psutil, sqlalchemy; print('OK')" 2>&1
        return @{
            Success = $LASTEXITCODE -eq 0
            Output = $result
        }
    }
}

# Ejecutar tareas con progreso
$totalTasks = $tasks.Count
$completedTasks = 0

foreach ($task in $tasks) {
    $taskNumber = [array]::IndexOf($tasks, $task) + 1
    $overallProgress = [math]::Round(($completedTasks / $totalTasks) * 100)

    Write-Host "`n--- Tarea $taskNumber/$totalTasks : $($task.Name) ---" -ForegroundColor Magenta
    Write-Host "Progreso general: $overallProgress%" -ForegroundColor Yellow

    $result = Start-JobWithProgress -Name $task.Name -ScriptBlock $task.Script -ProgressId $taskNumber

    if ($result.Success) {
        Write-Host "✅ $($task.Name): Éxito" -ForegroundColor Green
        if ($result.Output) {
            Write-Host "   Detalles: $($result.Output)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ $($task.Name): Falló" -ForegroundColor Red
        if ($result.Error) {
            Write-Host "   Error: $($result.Error)" -ForegroundColor Red
        }
        if ($result.Output) {
            Write-Host "   Salida: $($result.Output)" -ForegroundColor Red
        }
    }

    $completedTasks++
}

# Progreso final
$finalProgress = 100
Show-Progress -Activity "BackendBot" -PercentComplete $finalProgress -Status "Todas las tareas completadas"
Write-Progress -Activity "BackendBot" -Completed

Write-Host "`n=== RESUMEN FINAL ===" -ForegroundColor Cyan
Write-Host "Progreso completado: $finalProgress%" -ForegroundColor Green
Write-Host "Tareas ejecutadas: $totalTasks" -ForegroundColor White
Write-Host "Tareas exitosas: $($tasks.Count - ($tasks | Where-Object { -not $_.Result.Success }).Count)" -ForegroundColor Green
Write-Host "Tareas fallidas: $(($tasks | Where-Object { -not $_.Result.Success }).Count)" -ForegroundColor Red

# Iniciar backend si se solicita
if ($AutoStart) {
    Write-Host "`nIniciando backend automáticamente..." -ForegroundColor Yellow
    Start-Process -FilePath python -ArgumentList 'main.py' -WindowStyle Hidden
    Write-Host "Backend iniciado en segundo plano" -ForegroundColor Green
}

Write-Host "`nScript completado en $(Get-Date)" -ForegroundColor Cyan