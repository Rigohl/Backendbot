# Script de Testing Paralelo para BackendBot
# Ejecuta múltiples tests simultáneamente en segundo plano

Write-Host "🚀 Iniciando Testing Paralelo de BackendBot..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Yellow

# Función para ejecutar un test en background
function Start-TestJob {
    param(
        [string]$TestName,
        [string]$Command,
        [string]$LogFile
    )

    Write-Host "📋 Iniciando test: $TestName" -ForegroundColor Cyan

    # Crear job en background
    $job = Start-Job -ScriptBlock {
        param($cmd, $log)
        try {
            $startTime = Get-Date
            Write-Host "[$startTime] Iniciando $using:TestName..." | Out-File $log -Append

            # Ejecutar comando
            $result = Invoke-Expression $cmd 2>&1
            $exitCode = $LASTEXITCODE

            $endTime = Get-Date
            $duration = $endTime - $startTime

            # Loggear resultado
            Write-Host "[$endTime] $using:TestName completado (Exit: $exitCode, Duración: $($duration.TotalSeconds)s)" | Out-File $log -Append
            $result | Out-File $log -Append

            return @{
                Name = $using:TestName
                ExitCode = $exitCode
                Duration = $duration.TotalSeconds
                Success = ($exitCode -eq 0)
            }
        }
        catch {
            Write-Host "[$endTime] ERROR en $using:TestName : $($_.Exception.Message)" | Out-File $log -Append
            return @{
                Name = $using:TestName
                ExitCode = -1
                Duration = 0
                Success = $false
                Error = $_.Exception.Message
            }
        }
    } -ArgumentList $Command, $LogFile

    return $job
}

# Crear directorio de logs si no existe
$logDir = "test_logs"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# Timestamp para logs
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$baseLogFile = "$logDir\test_run_$timestamp.log"

Write-Host "📝 Logs disponibles en: $baseLogFile" -ForegroundColor Gray

# Lista de tests a ejecutar
$tests = @(
    @{
        Name = "Importaciones Basicas"
        Command = "python -c `"import sys; sys.path.insert(0, '.'); from src.backendbot.cron_jobs.task_scheduler import task_scheduler; from src.backendbot.modes.adaptive_learning import adaptive_learning; print('✅ Importaciones OK')`""
    },
    @{
        Name = "Sistema de Tareas"
        Command = "python -c `"import sys; sys.path.insert(0, '.'); from src.backendbot.cron_jobs.task_scheduler import task_scheduler; print(f'✅ Tasks: {len(task_scheduler.tasks)}'); print(f'✅ Scheduler: {task_scheduler.running}')`""
    },
    @{
        Name = "Sistema de Aprendizaje"
        Command = "python -c `"import sys; sys.path.insert(0, '.'); from src.backendbot.modes.adaptive_learning import adaptive_learning; stats = adaptive_learning.get_learning_stats(); print(f'✅ Learning: {stats}')`""
    },
    @{
        Name = "Procesador de Comandos"
        Command = "python -c `"import sys; sys.path.insert(0, '.'); from src.backendbot.utils.advanced_command_processor import advanced_command_processor; response, cmd = advanced_command_processor.process_command('hola'); print(f'✅ NLP: {response}')`""
    },
    @{
        Name = "UI Components"
        Command = "python -c `"import sys; sys.path.insert(0, '.'); from src.backendbot.ui.main_ui import BackendBotUI; print('✅ UI Components OK')`""
    },
    @{
        Name = "Bot Monitor"
        Command = "python -c `"import sys; sys.path.insert(0, '.'); from src.backendbot.bots.bot_monitor_ui import BotMonitorUI; print('✅ Bot Monitor OK')`""
    },
    @{
        Name = "Bot Organizer"
        Command = "python -c `"import sys; sys.path.insert(0, '.'); from src.backendbot.bots.bot_organizer_ui import BotOrganizerUI; print('✅ Bot Organizer OK')`""
    },
    @{
        Name = "Bot Indexer"
        Command = "python -c `"import sys; sys.path.insert(0, '.'); from src.backendbot.bots.bot_indexer_ui import BotIndexerUI; print('✅ Bot Indexer OK')`""
    },
    @{
        Name = "Bot Auditor"
        Command = "python -c `"import sys; sys.path.insert(0, '.'); from src.backendbot.bots.bot_auditor_files_ui import BotAuditorFilesUI; print('✅ Bot Auditor OK')`""
    },
    @{
        Name = "Bot Optimizer"
        Command = "python -c `"import sys; sys.path.insert(0, '.'); from src.backendbot.bots.bot_optimizer_ui import BotOptimizerUI; print('✅ Bot Optimizer OK')`""
    }
)

# Iniciar todos los tests en paralelo
$jobs = @()
foreach ($test in $tests) {
    $logFile = "$logDir\$($test.Name -replace '[^a-zA-Z0-9]', '_')_$timestamp.log"
    $job = Start-TestJob -TestName $test.Name -Command $test.Command -LogFile $logFile
    $jobs += $job
}

Write-Host "`n⏳ Tests ejecutándose en paralelo..." -ForegroundColor Yellow
Write-Host "Jobs activos: $($jobs.Count)" -ForegroundColor Cyan

# Función para mostrar progreso
function Show-Progress {
    $completed = ($jobs | Where-Object { $_.State -eq 'Completed' }).Count
    $running = ($jobs | Where-Object { $_.State -eq 'Running' }).Count
    $failed = ($jobs | Where-Object { $_.State -eq 'Failed' }).Count

    Write-Host "📊 Progreso: $completed completados, $running ejecutándose, $failed fallidos" -ForegroundColor Magenta
}

# Monitorear progreso cada 2 segundos
$startTime = Get-Date
while (($jobs | Where-Object { $_.State -eq 'Running' }).Count -gt 0) {
    Start-Sleep -Seconds 2
    Show-Progress

    # Timeout de 5 minutos
    if (((Get-Date) - $startTime).TotalMinutes -gt 5) {
        Write-Host "⏰ Timeout alcanzado (5 minutos)" -ForegroundColor Red
        break
    }
}

Write-Host "`n📋 Recopilando resultados..." -ForegroundColor Yellow

# Recopilar resultados
$results = @()
$totalDuration = 0
$successCount = 0

foreach ($job in $jobs) {
    $result = Receive-Job -Job $job
    if ($result) {
        $results += $result
        $totalDuration += $result.Duration
        if ($result.Success) { $successCount++ }
    }
    Remove-Job -Job $job
}

# Mostrar resumen final
Write-Host "`n🎯 RESULTADOS FINALES" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

$results | ForEach-Object {
    $status = if ($_.Success) { "✅" } else { "❌" }
    $color = if ($_.Success) { "Green" } else { "Red" }
    Write-Host "$status $($_.Name): $([math]::Round($_.Duration, 2))s" -ForegroundColor $color
}

Write-Host "`n📊 ESTADÍSTICAS GENERALES" -ForegroundColor Cyan
Write-Host "• Tests totales: $($results.Count)" -ForegroundColor White
Write-Host "• Tests exitosos: $successCount" -ForegroundColor Green
Write-Host "• Tests fallidos: $($results.Count - $successCount)" -ForegroundColor Red
Write-Host "• Tiempo total: $([math]::Round($totalDuration, 2))s" -ForegroundColor Yellow
Write-Host "• Tasa de éxito: $([math]::Round((($successCount / $results.Count) * 100), 1))%" -ForegroundColor Magenta

# Guardar resumen en archivo principal
$summary = @"
RESUMEN DE TESTING - $(Get-Date)
=====================================
Tests Totales: $($results.Count)
Tests Exitosos: $successCount
Tests Fallidos: $($results.Count - $successCount)
Tiempo Total: $([math]::Round($totalDuration, 2))s
Tasa de Éxito: $([math]::Round((($successCount / $results.Count) * 100), 1))%

DETALLE POR TEST:
"@

$results | ForEach-Object {
    $status = if ($_.Success) { "EXITO" } else { "FALLO" }
    $summary += "`n$($_.Name): $status ($([math]::Round($_.Duration, 2))s)"
    if ($_.Error) {
        $summary += "`n  Error: $($_.Error)"
    }
}

$summary | Out-File $baseLogFile -Encoding UTF8

Write-Host "`n💾 Resumen guardado en: $baseLogFile" -ForegroundColor Gray
Write-Host "`n🎉 Testing completado! Continúa trabajando mientras los resultados se procesan..." -ForegroundColor Green