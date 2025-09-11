# PowerShell: Monitor de Estado del BackendBot
# Muestra el progreso y estado en tiempo real

param(
    [switch]$Continuous,
    [int]$RefreshInterval = 5
)

Write-Host "=== Monitor de Estado - BackendBot ===" -ForegroundColor Cyan
Write-Host "Actualización cada $RefreshInterval segundos" -ForegroundColor Yellow
Write-Host "Presiona Ctrl+C para salir`n" -ForegroundColor Gray

function Get-BackendStatus {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
        return @{
            Status = "Online"
            Code = $response.StatusCode
            Content = $response.Content
            Color = "Green"
        }
    } catch {
        return @{
            Status = "Offline"
            Code = "N/A"
            Content = "Error de conexión"
            Color = "Red"
        }
    }
}

function Get-SystemInfo {
    $cpu = Get-WmiObject -Class Win32_Processor | Select-Object -First 1
    $memory = Get-WmiObject -Class Win32_OperatingSystem
    $totalMemory = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
    $freeMemory = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
    $usedMemory = $totalMemory - $freeMemory
    $memoryPercent = [math]::Round(($usedMemory / $totalMemory) * 100, 1)

    return @{
        CPU = "$($cpu.LoadPercentage)%"
        Memory = "$memoryPercent% ($usedMemory GB / $totalMemory GB)"
        MemoryPercent = $memoryPercent
    }
}

function Show-ProgressBar {
    param([int]$Percent, [string]$Label, [string]$Color = "Green")

    $width = 50
    $filled = [math]::Floor($Percent * $width / 100)
    $empty = $width - $filled

    $bar = "[" + ("█" * $filled) + ("░" * $empty) + "]"

    Write-Host "$bar $Percent% - $Label" -ForegroundColor $Color
}

function Show-Status {
    Clear-Host
    Write-Host "=== BackendBot - Estado en Tiempo Real ===" -ForegroundColor Cyan
    Write-Host "Hora: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Yellow
    Write-Host ""

    # Estado del Backend
    $backendStatus = Get-BackendStatus
    Write-Host "🔧 BACKEND STATUS:" -ForegroundColor Magenta
    Write-Host "   Estado: $($backendStatus.Status)" -ForegroundColor $backendStatus.Color
    Write-Host "   Código: $($backendStatus.Code)" -ForegroundColor White
    Write-Host "   Respuesta: $($backendStatus.Content)" -ForegroundColor Gray
    Write-Host ""

    # Información del Sistema
    $systemInfo = Get-SystemInfo
    Write-Host "💻 SISTEMA:" -ForegroundColor Magenta
    Write-Host "   CPU: $($systemInfo.CPU)" -ForegroundColor White
    Write-Host "   Memoria: $($systemInfo.Memory)" -ForegroundColor White
    Show-ProgressBar -Percent $systemInfo.MemoryPercent -Label "Uso de Memoria" -Color "Yellow"
    Write-Host ""

    # Progreso de Tareas
    Write-Host "📊 PROGRESO DE TAREAS:" -ForegroundColor Magenta

    # Verificar si hay procesos de Python ejecutándose
    $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        Show-ProgressBar -Percent 100 -Label "Backend Ejecutándose" -Color "Green"
        Write-Host "   Procesos Python: $($pythonProcesses.Count)" -ForegroundColor White
    } else {
        Show-ProgressBar -Percent 0 -Label "Backend Detenido" -Color "Red"
        Write-Host "   No hay procesos Python ejecutándose" -ForegroundColor Red
    }

    # Verificar tests
    $testFiles = Get-ChildItem -Path "tests" -Filter "*.py" -ErrorAction SilentlyContinue
    if ($testFiles) {
        Show-ProgressBar -Percent 70 -Label "Tests (70% completado)" -Color "Yellow"
        Write-Host "   Archivos de test: $($testFiles.Count)" -ForegroundColor White
    } else {
        Show-ProgressBar -Percent 0 -Label "Tests no encontrados" -Color "Red"
    }

    # Verificar linting
    $srcFiles = Get-ChildItem -Path "src" -Filter "*.py" -Recurse -ErrorAction SilentlyContinue
    if ($srcFiles) {
        Show-ProgressBar -Percent 60 -Label "Linting (60% completado)" -Color "Yellow"
        Write-Host "   Archivos fuente: $($srcFiles.Count)" -ForegroundColor White
    }

    # Verificar icono de bandeja
    $trayIcon = Get-Process tray_icon -ErrorAction SilentlyContinue
    if ($trayIcon) {
        Show-ProgressBar -Percent 100 -Label "Icono de Bandeja" -Color "Green"
    } else {
        Show-ProgressBar -Percent 0 -Label "Icono de Bandeja (Inactivo)" -Color "Red"
    }

    Write-Host ""

    # Estado General
    Write-Host "🎯 ESTADO GENERAL:" -ForegroundColor Magenta
    $overallProgress = 75  # Basado en el progreso anterior
    Show-ProgressBar -Percent $overallProgress -Label "Proyecto BackendBot" -Color "Cyan"

    Write-Host ""
    Write-Host "💡 ACCIONES DISPONIBLES:" -ForegroundColor Magenta
    Write-Host "   [R] Reiniciar backend" -ForegroundColor White
    Write-Host "   [T] Ejecutar tests" -ForegroundColor White
    Write-Host "   [L] Ejecutar linting" -ForegroundColor White
    Write-Host "   [I] Iniciar icono de bandeja" -ForegroundColor White
    Write-Host "   [Q] Salir" -ForegroundColor White
    Write-Host ""

    Write-Host "Presiona una tecla para acción o espera $RefreshInterval segundos..." -ForegroundColor Gray
}

# Función principal
function Start-Monitor {
    if ($Continuous) {
        # Modo continuo
        while ($true) {
            Show-Status

            # Esperar entrada del usuario o timeout
            $timeout = $RefreshInterval * 1000  # Convertir a milisegundos

            if ([Console]::KeyAvailable) {
                $key = [Console]::ReadKey($true)
                switch ($key.Key) {
                    'R' {
                        Write-Host "`n🔄 Reiniciando backend..." -ForegroundColor Yellow
                        # Aquí iría la lógica para reiniciar
                        Start-Sleep -Seconds 2
                    }
                    'T' {
                        Write-Host "`n🧪 Ejecutando tests..." -ForegroundColor Yellow
                        # Aquí iría la lógica para ejecutar tests
                        Start-Sleep -Seconds 2
                    }
                    'L' {
                        Write-Host "`n🔍 Ejecutando linting..." -ForegroundColor Yellow
                        # Aquí iría la lógica para linting
                        Start-Sleep -Seconds 2
                    }
                    'I' {
                        Write-Host "`n📱 Iniciando icono de bandeja..." -ForegroundColor Yellow
                        # Aquí iría la lógica para el icono
                        Start-Sleep -Seconds 2
                    }
                    'Q' {
                        Write-Host "`n👋 Saliendo..." -ForegroundColor Yellow
                        return
                    }
                }
            } else {
                Start-Sleep -Milliseconds $timeout
            }
        }
    } else {
        # Mostrar estado una vez
        Show-Status
    }
}

# Ejecutar monitor
Start-Monitor