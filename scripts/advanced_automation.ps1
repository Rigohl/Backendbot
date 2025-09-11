# Script de automatización avanzada para BackendBot
# Ejecuta tests en paralelo, maneja Git y aplica cambios si pasan

# Script de automatización avanzada para BackendBot
# Ejecuta tests en paralelo, maneja Git y aplica cambios si pasan

param(
    [switch]$SkipTests,
    [switch]$ForceApply,
    [string]$BranchName,
    [switch]$StartBackend,
    [int]$RamThreshold,
    [switch]$RestartOnLimit
)

# --- CONFIGURACIÓN INICIAL ---
Write-Host "=== BackendBot Advanced Automation Script ===" -ForegroundColor Cyan

# Cargar configuración desde JSON
$configFile = "config/config.json"
if (!(Test-Path $configFile)) {
    throw "No se encuentra el archivo de configuración en '$configFile'"
}
$config = Get-Content $configFile | ConvertFrom-Json
$automationConfig = $config.automation

# Sobrescribir configuración con parámetros si se proveen
$BranchName = if ($PSBoundParameters.ContainsKey('BranchName')) { $BranchName } else { "$($automationConfig.branch_prefix)-$(Get-Date -Format 'yyyyMMdd-HHmmss')" }
$RamThreshold = if ($PSBoundParameters.ContainsKey('RamThreshold')) { $RamThreshold } else { $automationConfig.ram_threshold_mb }
$RestartOnLimit = if ($PSBoundParameters.ContainsKey('RestartOnLimit')) { $RestartOnLimit } else { $automationConfig.restart_on_ram_limit }

Write-Host "Fecha: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Rama objetivo: $BranchName" -ForegroundColor Yellow
Write-Host "Límite de RAM: ${RamThreshold}MB" -ForegroundColor Yellow
Write-Host "Reinicio por RAM: $RestartOnLimit" -ForegroundColor Yellow
Write-Host ""

# --- FUNCIONES ---

# Función para rotar logs
function Rotate-Logs {
    param(
        [string[]]$LogFiles,
        [int]$MaxSizeMB,
        [int]$KeepFiles
    )

    foreach ($logFile in $LogFiles) {
        if (Test-Path $logFile) {
            $file = Get-Item $logFile
            if ($file.Length -gt ($MaxSizeMB * 1MB)) {
                Write-Host "Rotando log '$logFile' (tamaño: $([math]::Round($file.Length / 1MB, 2))MB)" -ForegroundColor Gray
                
                # Eliminar el archivo de log más antiguo si se supera el límite
                $archiveFiles = Get-ChildItem -Path "$logFile.*" | Sort-Object -Property Name -Descending
                if ($archiveFiles.Count -ge $KeepFiles) {
                    $archiveFiles | Select-Object -Last ($archiveFiles.Count - $KeepFiles + 1) | ForEach-Object {
                        Write-Host "Eliminando log antiguo: $($_.Name)" -ForegroundColor Gray
                        Remove-Item $_.FullName
                    }
                }

                # Renombrar archivos existentes
                for ($i = $KeepFiles - 1; $i -ge 1; $i--) {
                    $oldPath = "$logFile.$i"
                    $newPath = "$logFile.($i+1)"
                    if (Test-Path $oldPath) {
                        Rename-Item -Path $oldPath -NewName $newPath
                    }
                }

                # Renombrar el log actual
                Rename-Item -Path $logFile -NewName "$logFile.1"
                Write-Host "Log rotado a '$logFile.1'" -ForegroundColor Gray
            }
        }
    }
}

# Llamar a la rotación de logs al inicio
Rotate-Logs -LogFiles "logs/ram_usage.log", "logs/ram_alerts.log" -MaxSizeMB $automationConfig.log_rotation_max_size_mb -KeepFiles $automationConfig.log_rotation_keep_files

# Función para ejecutar comando con timeout
function Invoke-WithTimeout {
    param(
        [ScriptBlock]$ScriptBlock,
        [int]$TimeoutSeconds = 300
    )

    $job = Start-Job -ScriptBlock $ScriptBlock
    $result = Wait-Job $job -Timeout $TimeoutSeconds

    if ($result) {
        $output = Receive-Job $job
        Remove-Job $job
        return $output
    } else {
        Stop-Job $job
        Remove-Job $job
        throw "Timeout después de $TimeoutSeconds segundos"
    }
}

# Función para ejecutar tests en paralelo
function Run-ParallelTests {
    Write-Host "Ejecutando tests en paralelo..." -ForegroundColor Green

    $testFiles = Get-ChildItem -Path "tests" -Filter "test_*.py" | Select-Object -ExpandProperty Name
    $jobs = @()
    $results = @{}

    foreach ($testFile in $testFiles) {
        $jobName = "Test-$testFile"
        Write-Host "Iniciando job: $jobName" -ForegroundColor Gray

        $job = Start-Job -Name $jobName -ScriptBlock {
            param($file)
            $startTime = Get-Date

            try {
                $output = & python -m pytest "tests/$file" -v --tb=short 2>&1
                $exitCode = $LASTEXITCODE

                $endTime = Get-Date
                $duration = $endTime - $startTime

                return @{
                    File = $file
                    Output = $output
                    ExitCode = $exitCode
                    Duration = $duration
                    Success = ($exitCode -eq 0)
                }
            }
            catch {
                $endTime = Get-Date
                $duration = $endTime - $startTime

                return @{
                    File = $file
                    Output = $_.Exception.Message
                    ExitCode = 1
                    Duration = $duration
                    Success = $false
                }
            }
        } -ArgumentList $testFile

        $jobs += $job
    }

    Write-Host "Esperando que terminen $($jobs.Count) jobs de tests..." -ForegroundColor Yellow

    # Esperar con progreso
    $completed = 0
    while ($jobs | Where-Object { $_.State -eq 'Running' }) {
        $running = $jobs | Where-Object { $_.State -eq 'Running' } | Measure-Object | Select-Object -ExpandProperty Count
        Write-Progress -Activity "Ejecutando tests en paralelo" -Status "$completed completados, $running ejecutándose" -PercentComplete (($completed / $jobs.Count) * 100)
        Start-Sleep -Seconds 2
    }

    Write-Progress -Activity "Ejecutando tests en paralelo" -Completed

    # Recopilar resultados
    foreach ($job in $jobs) {
        $result = Receive-Job $job
        $results[$result.File] = $result
        Remove-Job $job
    }

    # Mostrar resultados
    Write-Host "`n=== RESULTADOS DE TESTS ===" -ForegroundColor Cyan
    $totalPassed = 0
    $totalFailed = 0

    foreach ($file in $results.Keys) {
        $result = $results[$file]
        if ($result.Success) {
            Write-Host "✅ $file - PASÓ ($($result.Duration.TotalSeconds.ToString('F2'))s)" -ForegroundColor Green
            $totalPassed++
        } else {
            Write-Host "❌ $file - FALLÓ ($($result.Duration.TotalSeconds.ToString('F2'))s)" -ForegroundColor Red
            Write-Host "   Salida: $($result.Output)" -ForegroundColor Red
            $totalFailed++
        }
    }

    Write-Host "`nResumen: $totalPassed pasaron, $totalFailed fallaron" -ForegroundColor $(if ($totalFailed -eq 0) { 'Green' } else { 'Red' })

    return @{
        AllPassed = ($totalFailed -eq 0)
        Results = $results
        PassedCount = $totalPassed
        FailedCount = $totalFailed
    }
}

# Función para crear rama y aplicar cambios
function Apply-Changes {
    param([string]$BranchName)

    Write-Host "`n=== APLICANDO CAMBIOS ===" -ForegroundColor Cyan

    # Crear nueva rama
    Write-Host "Creando rama: $BranchName" -ForegroundColor Yellow
    git checkout -b $BranchName 2>&1

    # Agregar archivos modificados
    Write-Host "Agregando archivos modificados..." -ForegroundColor Yellow
    git add . 2>&1

    # Crear commit
    $commitMessage = "feat: Implementación automática - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host "Creando commit: $commitMessage" -ForegroundColor Yellow
    git commit -m $commitMessage 2>&1

    Write-Host "✅ Cambios aplicados exitosamente" -ForegroundColor Green
}

# Función para ejecutar linting en paralelo
function Run-ParallelLinting {
    Write-Host "`n=== EJECUTANDO LINTING EN PARALELO ===" -ForegroundColor Green

    $lintJobs = @()

    # Job para Python linting
    $pythonJob = Start-Job -Name "PythonLint" -ScriptBlock {
        try {
            $output = & python -m ruff check src/ tests/ --output-format=full 2>&1
            return @{
                Tool = "Ruff"
                Output = $output
                ExitCode = $LASTEXITCODE
                Success = ($LASTEXITCODE -eq 0)
            }
        }
        catch {
            return @{
                Tool = "Ruff"
                Output = $_.Exception.Message
                ExitCode = 1
                Success = $false
            }
        }
    }
    $lintJobs += $pythonJob

    # Job para Python formatting check
    $formatJob = Start-Job -Name "PythonFormat" -ScriptBlock {
        try {
            $output = & python -m black --check --diff src/ tests/ 2>&1
            return @{
                Tool = "Black"
                Output = $output
                ExitCode = $LASTEXITCODE
                Success = ($LASTEXITCODE -eq 0)
            }
        }
        catch {
            return @{
                Tool = "Black"
                Output = $_.Exception.Message
                ExitCode = 1
                Success = $false
            }
        }
    }
    $lintJobs += $formatJob

    # Esperar que terminen
    Write-Host "Esperando linting jobs..." -ForegroundColor Yellow
    $lintJobs | Wait-Job | Out-Null

    # Recopilar resultados
    $lintResults = @()
    foreach ($job in $lintJobs) {
        $result = Receive-Job $job
        $lintResults += $result
        Remove-Job $job
    }

    # Mostrar resultados
    Write-Host "`nResultados de linting:" -ForegroundColor Cyan
    $allLintPassed = $true
    foreach ($result in $lintResults) {
        if ($result.Success) {
            Write-Host "✅ $($result.Tool) - PASÓ" -ForegroundColor Green
        } else {
            Write-Host "❌ $($result.Tool) - FALLÓ" -ForegroundColor Red
            Write-Host "   Salida: $($result.Output)" -ForegroundColor Red
            $allLintPassed = $false
        }
    }

    return $allLintPassed
}

#region Funciones de Monitoreo y RAM

# Función para monitorear el uso de RAM de un proceso
function Monitor-RamUsage {
    param(
        [string]$ProcessName,
        [int]$ThresholdMB = 500, # Límite de RAM en MB
        [int]$IntervalSeconds = 10,
        [switch]$RestartOnLimit
    )

    Write-Host "Iniciando monitoreo de RAM para '$ProcessName' (límite: ${ThresholdMB}MB, intervalo: ${IntervalSeconds}s)" -ForegroundColor Magenta

    while ($true) {
        $process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
        if ($process) {
            $ramUsage = [math]::Round($process.WorkingSet64 / 1MB, 2)
            $cpuUsage = $process.CPU
            $logLine = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Proceso: $($process.Name) | RAM: ${ramUsage}MB | CPU: ${cpuUsage}"
            
            # Guardar en log
            $logLine | Out-File -FilePath "logs/ram_usage.log" -Append

            if ($ramUsage -gt $ThresholdMB) {
                $warning = "⚠️ ALERTA: Uso de RAM ($($ramUsage)MB) para '$($ProcessName)' ha superado el límite de $($ThresholdMB)MB"
                Write-Host $warning -ForegroundColor Yellow
                $warning | Out-File -FilePath "logs/ram_alerts.log" -Append

                if ($RestartOnLimit) {
                    Write-Host "Reiniciando proceso '$($ProcessName)' por exceso de RAM..." -ForegroundColor Red
                    Stop-Process -Name $ProcessName -Force
                    # Aquí podrías añadir un comando para reiniciar tu backend
                    # Ejemplo: Start-Process -FilePath "path/to/your/backend.exe"
                }
            }
        } else {
            Write-Host "Proceso '$($ProcessName)' no encontrado. El monitoreo se detendrá." -ForegroundColor Gray
            break
        }
        Start-Sleep -Seconds $IntervalSeconds
    }
}

# Función para iniciar el backend y el monitoreo en segundo plano
function Start-BackendAndMonitor {
    param(
        [int]$RamThreshold = 500,
        [switch]$RestartOnLimit
    )

    Write-Host "`n=== INICIANDO BACKEND Y MONITOREO DE RAM ===" -ForegroundColor Magenta

    # Iniciar el backend en un proceso separado
    Write-Host "Iniciando backend (python main.py)..." -ForegroundColor Yellow
    $backendProcess = Start-Process python -ArgumentList "main.py" -PassThru -NoNewWindow
    $processName = $backendProcess.Name
    Write-Host "Backend iniciado con el nombre de proceso: '$($processName)' (PID: $($backendProcess.Id))" -ForegroundColor Green

    # Iniciar el monitoreo en un job de PowerShell
    $monitorJob = Start-Job -Name "RamMonitor" -ScriptBlock {
        param(
            [string]$ProcessName,
            [int]$ThresholdMB,
            [switch]$RestartOnLimit
        )

        # Definición de la función de monitoreo dentro del job
        function Monitor-RamUsage {
            param(
                [string]$ProcessName,
                [int]$ThresholdMB = 500,
                [int]$IntervalSeconds = 10,
                [switch]$RestartOnLimit
            )

            Write-Host "Iniciando monitoreo de RAM para '$ProcessName' (límite: ${ThresholdMB}MB, intervalo: ${IntervalSeconds}s)" -ForegroundColor Magenta

            while ($true) {
                $process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
                if ($process) {
                    $ramUsage = [math]::Round($process.WorkingSet64 / 1MB, 2)
                    $cpuUsage = $process.CPU
                    $logLine = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Proceso: $($process.Name) | RAM: ${ramUsage}MB | CPU: ${cpuUsage}"
                    
                    $logLine | Out-File -FilePath "logs/ram_usage.log" -Append

                    if ($ramUsage -gt $ThresholdMB) {
                        $warning = "⚠️ ALERTA: Uso de RAM ($($ramUsage)MB) para '$($ProcessName)' ha superado el límite de $($ThresholdMB)MB"
                        Write-Host $warning -ForegroundColor Yellow
                        $warning | Out-File -FilePath "logs/ram_alerts.log" -Append

                        if ($RestartOnLimit) {
                            Write-Host "Reiniciando proceso '$($ProcessName)' por exceso de RAM..." -ForegroundColor Red
                            Stop-Process -Name $ProcessName -Force
                            # Reiniciar el backend
                            Start-Process python -ArgumentList "main.py" -NoNewWindow
                        }
                    }
                } else {
                    Write-Host "Proceso '$($ProcessName)' no encontrado. El monitoreo se detendrá." -ForegroundColor Gray
                    break
                }
                Start-Sleep -Seconds $IntervalSeconds
            }
        }

        # Llamar a la función de monitoreo
        Monitor-RamUsage -ProcessName $ProcessName -ThresholdMB $ThresholdMB -IntervalSeconds 10 -RestartOnLimit:$RestartOnLimit
    } -ArgumentList $processName, $RamThreshold, $RestartOnLimit

    Write-Host "Monitoreo de RAM iniciado en segundo plano. Logs en 'logs/ram_usage.log' y 'logs/ram_alerts.log'" -ForegroundColor Green
    return $monitorJob
}

#endregion

# Script principal
try {
    # Verificar que estamos en el directorio correcto
    if (!(Test-Path "main.py") -or !(Test-Path "src")) {
        throw "No se encuentra en el directorio raíz del proyecto BackendBot"
    }

    if ($StartBackend) {
        Start-BackendAndMonitor -RamThreshold $RamThreshold -RestartOnLimit:$RestartOnLimit
        Write-Host "`nEl backend y el monitoreo de RAM están corriendo en segundo plano." -ForegroundColor Green
        Write-Host "Puedes cerrar esta ventana, los procesos seguirán ejecutándose." -ForegroundColor Green
        exit 0
    }

    # Ejecutar linting si no se salta
    if (!$SkipTests) {
        $lintPassed = Run-ParallelLinting
        if (!$lintPassed) {
            Write-Host "`n❌ Linting falló. Corrigiendo automáticamente..." -ForegroundColor Red

            # Auto-fix con ruff
            Write-Host "Ejecutando auto-fix..." -ForegroundColor Yellow
            & python -m ruff check src/ tests/ --fix 2>&1

            # Auto-format con black
            Write-Host "Formateando código..." -ForegroundColor Yellow
            & python -m black src/ tests/ 2>&1

            # Re-ejecutar linting
            Write-Host "Re-ejecutando linting..." -ForegroundColor Yellow
            $lintPassed = Run-ParallelLinting
        }
    } else {
        $lintPassed = $true
    }

    # Ejecutar tests si no se salta
    if (!$SkipTests) {
        $testResults = Run-ParallelTests
        $testsPassed = $testResults.AllPassed
    } else {
        $testsPassed = $true
        Write-Host "`n⚠️  Tests saltados (-SkipTests)" -ForegroundColor Yellow
    }

    # Aplicar cambios si todo pasó o se fuerza
    if (($testsPassed -and $lintPassed) -or $ForceApply) {
        Apply-Changes -BranchName $BranchName

        Write-Host "`n🎉 ¡Implementación completada exitosamente!" -ForegroundColor Green
        Write-Host "Rama creada: $BranchName" -ForegroundColor Green
        Write-Host "Archivos modificados aplicados" -ForegroundColor Green

        # Mostrar resumen de cambios
        Write-Host "`n=== RESUMEN DE CAMBIOS ===" -ForegroundColor Cyan
        git show --stat HEAD 2>&1

    } else {
        Write-Host "`n❌ No se aplicaron cambios debido a fallos en tests o linting" -ForegroundColor Red
        Write-Host "Usa -ForceApply para forzar la aplicación" -ForegroundColor Yellow
        exit 1
    }

} catch {
    Write-Host "`n💥 Error durante la automatización: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== FIN DEL SCRIPT ===" -ForegroundColor Cyan
