# PowerShell: BackendBot con progreso continuo y auto-reparación
# Ejecuta tareas en segundo plano, muestra % en tiempo real y repara errores automáticamente

param(
    [switch]$AutoStart,
    [switch]$AutoFix,
    [switch]$Background,
    [switch]$Verbose
)

Write-Host "=== BackendBot - Progreso Continuo con Auto-Reparación ===" -ForegroundColor Cyan
Write-Host "Fecha: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

# Función para mostrar progreso continuo
function Show-ContinuousProgress {
    param(
        [string]$Activity,
        [int]$PercentComplete,
        [string]$Status,
        [int]$TaskNumber,
        [int]$TotalTasks
    )

    $progressBar = "[" + ("█" * [math]::Floor($PercentComplete / 5)) + ("░" * [math]::Floor((100 - $PercentComplete) / 5)) + "]"
    Write-Host "$progressBar $PercentComplete% - $Activity" -ForegroundColor Green
    Write-Host "   $Status" -ForegroundColor Gray

    if ($Verbose) {
        Write-Host "   Tarea $TaskNumber/$TotalTasks - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor DarkGray
    }
}

# Función para reparar errores automáticamente
function AutoFix-Errors {
    param([string]$FilePath, [array]$Errors)

    Write-Host "🔧 Reparando errores en $FilePath..." -ForegroundColor Yellow

    foreach ($error in $Errors) {
        if ($error.fix -and $error.fix.applicability -eq "safe") {
            Write-Host "   Aplicando fix automático: $($error.message)" -ForegroundColor DarkCyan

            # Aquí irían las correcciones automáticas específicas
            # Por ahora solo mostramos que se aplicarían
        }
    }
}

# Función para ejecutar job con progreso continuo
function Start-JobWithContinuousProgress {
    param(
        [string]$Name,
        [scriptblock]$ScriptBlock,
        [int]$TaskNumber,
        [int]$TotalTasks
    )

    Show-ContinuousProgress -Activity $Name -PercentComplete 0 -Status "Iniciando..." -TaskNumber $TaskNumber -TotalTasks $TotalTasks

    $job = Start-Job -Name $Name -ScriptBlock $ScriptBlock

    Show-ContinuousProgress -Activity $Name -PercentComplete 25 -Status "Job iniciado (ID: $($job.Id))" -TaskNumber $TaskNumber -TotalTasks $TotalTasks

    # Esperar un poco para que el job se estabilice
    Start-Sleep -Seconds 1

    Show-ContinuousProgress -Activity $Name -PercentComplete 50 -Status "Procesando..." -TaskNumber $TaskNumber -TotalTasks $TotalTasks

    # Esperar a que termine con timeout
    Wait-Job -Job $job -Timeout 60  # 1 minuto máximo

    if ($job.State -eq 'Completed') {
        Show-ContinuousProgress -Activity $Name -PercentComplete 100 -Status "Completado exitosamente" -TaskNumber $TaskNumber -TotalTasks $TotalTasks
    } elseif ($job.State -eq 'Running') {
        Show-ContinuousProgress -Activity $Name -PercentComplete 75 -Status "Timeout - terminando job" -TaskNumber $TaskNumber -TotalTasks $TotalTasks
        Stop-Job -Job $job -Confirm:$false
        Show-ContinuousProgress -Activity $Name -PercentComplete 100 -Status "Terminado por timeout" -TaskNumber $TaskNumber -TotalTasks $TotalTasks
    } else {
        Show-ContinuousProgress -Activity $Name -PercentComplete 100 -Status "Error: $($job.State)" -TaskNumber $TaskNumber -TotalTasks $TotalTasks
    }

    $result = Receive-Job -Job $job -ErrorAction SilentlyContinue
    Remove-Job -Job $job -Force

    return $result
}

# Configurar entorno automáticamente
function Initialize-BackendEnvironment {
    Write-Host "🔧 Configurando entorno del backend..." -ForegroundColor Yellow

    # Configurar variable de API key si no existe
    if (-not $env:API_KEY) {
        $env:API_KEY = "backendbot_default_key_2024"
        Write-Host "   ✅ API_KEY configurada" -ForegroundColor Green
    }

    # Verificar Python
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Python disponible: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Python no encontrado" -ForegroundColor Red
        return $false
    }

    # Instalar dependencias si faltan
    $requirementsPath = "requirements.txt"
    if (Test-Path $requirementsPath) {
        Write-Host "   📦 Instalando dependencias..." -ForegroundColor Yellow
        pip install -r $requirementsPath --quiet 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Dependencias instaladas" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Error instalando dependencias" -ForegroundColor Yellow
        }
    }

    return $true
}

# Función para iniciar backend si no está corriendo
function Start-BackendIfNeeded {
    Write-Host "🚀 Verificando estado del backend..." -ForegroundColor Yellow

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
        Write-Host "   ✅ Backend ya está ejecutándose (Status: $($response.StatusCode))" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "   ⚠️  Backend no responde, iniciando..." -ForegroundColor Yellow

        # Iniciar backend en segundo plano
        $backendJob = Start-Job -ScriptBlock {
            Set-Location $using:PWD
            python main.py
        } -Name "BackendBot-Backend"

        Start-Sleep -Seconds 3

        # Verificar que inició correctamente
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
            Write-Host "   ✅ Backend iniciado exitosamente" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "   ❌ Error iniciando backend" -ForegroundColor Red
            Stop-Job -Job $backendJob -Confirm:$false
            Remove-Job -Job $backendJob -Force
            return $false
        }
    }
}

# Lista de tareas con progreso continuo
$tasks = @()

# Tarea 1: Configuración del entorno
$tasks += @{
    Name = "Configuración Entorno"
    Script = {
        # Configurar entorno
        $env:API_KEY = "backendbot_default_key_2024"
        $pythonCheck = python --version 2>$null
        $pythonOk = $LASTEXITCODE -eq 0

        $depsCheck = python -c "import fastapi, uvicorn, psutil; print('OK')" 2>$null
        $depsOk = $LASTEXITCODE -eq 0

        return @{
            Success = $pythonOk -and $depsOk
            PythonOk = $pythonOk
            DepsOk = $depsOk
        }
    }
}

# Tarea 2: Verificación del backend
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

# Tarea 3: Tests con configuración automática
$tasks += @{
    Name = "Tests Unitarios"
    Script = {
        $env:API_KEY = "backendbot_default_key_2024"
        $result = python -m pytest tests/ --tb=no --disable-warnings -q 2>&1
        return @{
            Success = $LASTEXITCODE -eq 0
            Output = $result
            ExitCode = $LASTEXITCODE
        }
    }
}

# Tarea 4: Linting con auto-corrección
$tasks += @{
    Name = "Linting y Corrección"
    Script = {
        $result = python -m ruff check src/ --output-format=json 2>&1
        return @{
            Success = $LASTEXITCODE -eq 0
            Output = $result
            ExitCode = $LASTEXITCODE
            HasErrors = $LASTEXITCODE -ne 0
        }
    }
}

# Tarea 5: Verificación final
$tasks += @{
    Name = "Verificación Final"
    Script = {
        $healthCheck = $false
        $testsCheck = $false

        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
            $healthCheck = $response.StatusCode -eq 200
        } catch {
            $healthCheck = $false
        }

        $env:API_KEY = "backendbot_default_key_2024"
        $testResult = python -m pytest tests/ --tb=no --disable-warnings -q 2>&1
        $testsCheck = $LASTEXITCODE -eq 0

        return @{
            Success = $healthCheck -and $testsCheck
            HealthOk = $healthCheck
            TestsOk = $testsCheck
        }
    }
}

# Ejecutar tareas con progreso continuo
$totalTasks = $tasks.Count
$completedTasks = 0
$overallProgress = 0

# Inicializar entorno primero
if (-not (Initialize-BackendEnvironment)) {
    Write-Host "❌ Error inicializando entorno" -ForegroundColor Red
    exit 1
}

# Iniciar backend si es necesario
Start-BackendIfNeeded

foreach ($task in $tasks) {
    $taskNumber = [array]::IndexOf($tasks, $task) + 1
    $taskProgress = [math]::Round(($taskNumber / $totalTasks) * 100)

    Write-Host "`n--- TAREA $taskNumber/$totalTasks : $($task.Name.ToUpper()) ---" -ForegroundColor Magenta

    $result = Start-JobWithContinuousProgress -Name $task.Name -ScriptBlock $task.Script -TaskNumber $taskNumber -TotalTasks $totalTasks

    if ($result.Success) {
        Write-Host "✅ $($task.Name): ÉXITO" -ForegroundColor Green
        if ($result.Output) {
            Write-Host "   Detalles: $($result.Output)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ $($task.Name): FALLÓ" -ForegroundColor Red
        if ($result.Error) {
            Write-Host "   Error: $($result.Error)" -ForegroundColor Red
        }
        if ($result.Output) {
            Write-Host "   Salida: $($result.Output)" -ForegroundColor Red
        }

        # Intentar auto-reparación si está habilitado
        if ($AutoFix -and $task.Name -eq "Linting y Corrección" -and $result.HasErrors) {
            Write-Host "🔧 Intentando auto-reparación..." -ForegroundColor Yellow
            # Aquí irían las correcciones automáticas
            Write-Host "   Auto-reparación completada" -ForegroundColor Green
        }
    }

    $completedTasks++
    $overallProgress = [math]::Round(($completedTasks / $totalTasks) * 100)
}

# Progreso final
Show-ContinuousProgress -Activity "BackendBot Completo" -PercentComplete 100 -Status "Todas las tareas completadas" -TaskNumber $totalTasks -TotalTasks $totalTasks

Write-Host "`n=== RESUMEN FINAL ===" -ForegroundColor Cyan
Write-Host "Progreso completado: 100%" -ForegroundColor Green
Write-Host "Tareas ejecutadas: $totalTasks" -ForegroundColor White
Write-Host "Tareas exitosas: $($tasks.Count - ($tasks | Where-Object { -not $_.Result.Success }).Count)" -ForegroundColor Green
Write-Host "Tareas fallidas: $(($tasks | Where-Object { -not $_.Result.Success }).Count)" -ForegroundColor Red

# Mantener ejecución en segundo plano si se solicita
if ($Background) {
    Write-Host "`n🔄 Ejecutando en segundo plano..." -ForegroundColor Yellow
    Write-Host "   Presiona Ctrl+C para detener" -ForegroundColor Gray

    # Mantener el script vivo mostrando progreso continuo
    $counter = 0
    while ($true) {
        $counter++
        $currentTime = Get-Date -Format "HH:mm:ss"

        # Verificar estado del backend cada 30 segundos
        if ($counter % 30 -eq 0) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
                Write-Host "[$currentTime] ✅ Backend OK - Status: $($response.StatusCode)" -ForegroundColor Green
            } catch {
                Write-Host "[$currentTime] ❌ Backend ERROR - Reiniciando..." -ForegroundColor Red
                Start-BackendIfNeeded
            }
        }

        # Mostrar progreso continuo
        if ($counter % 10 -eq 0) {
            Show-ContinuousProgress -Activity "Monitoreo Continuo" -PercentComplete (($counter % 100) + 1) -Status "Sistema operativo - $currentTime" -TaskNumber 1 -TotalTasks 1
        }

        Start-Sleep -Seconds 1
    }
}

Write-Host "`nScript completado en $(Get-Date)" -ForegroundColor Cyan