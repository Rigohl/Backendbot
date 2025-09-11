# BackendBot PowerShell Automation Script
# Optimización máxima para desarrollo y despliegue

param(
    [switch]$Parallel,
    [switch]$Background,
    [switch]$Optimize,
    [switch]$Deploy,
    [switch]$Test,
    [switch]$Monitor
)

# Configuración de PowerShell para máximo rendimiento
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$VerbosePreference = "Continue"

# Función para logging optimizado
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# Configuración de entorno optimizada
function Optimize-PowerShell {
    Write-Log "Optimizando configuración de PowerShell..." "INFO"

    # Configurar PSReadLine para mejor experiencia
    if (Get-Module -Name PSReadLine -ErrorAction SilentlyContinue) {
        Set-PSReadLineOption -EditMode Windows
        Set-PSReadLineOption -HistorySearchCursorMovesToEnd
        Set-PSReadLineKeyHandler -Key Tab -Function Complete
    }

    # Configurar alias útiles
    Set-Alias -Name ll -Value Get-ChildItem
    Set-Alias -Name grep -Value Select-String
    Set-Alias -Name touch -Value New-Item

    Write-Log "PowerShell optimizado exitosamente" "SUCCESS"
}

# Función para ejecutar tareas en paralelo
function Start-ParallelTasks {
    Write-Log "Iniciando tareas en paralelo..." "INFO"

    $jobs = @()

    # Job 1: Verificar dependencias
    $jobs += Start-Job -ScriptBlock {
        Set-Location "C:\Users\DELL\Desktop\BackendBot"
        python -c "import fastapi, uvicorn, psutil; print('Dependencias OK')"
    } -Name "CheckDeps"

    # Job 2: Ejecutar tests
    $jobs += Start-Job -ScriptBlock {
        Set-Location "C:\Users\DELL\Desktop\BackendBot"
        python -m pytest tests/ -v --tb=short
    } -Name "RunTests"

    # Job 3: Verificar linting
    $jobs += Start-Job -ScriptBlock {
        Set-Location "C:\Users\DELL\Desktop\BackendBot"
        if (Get-Command ruff -ErrorAction SilentlyContinue) {
            ruff check .
        } else {
            Write-Host "Ruff no instalado"
        }
    } -Name "LintCode"

    # Job 4: Verificar formato
    $jobs += Start-Job -ScriptBlock {
        Set-Location "C:\Users\DELL\Desktop\BackendBot"
        if (Get-Command black -ErrorAction SilentlyContinue) {
            black --check --diff .
        } else {
            Write-Host "Black no instalado"
        }
    } -Name "FormatCode"

    # Esperar y mostrar resultados
    foreach ($job in $jobs) {
        $result = Receive-Job -Job $job -Wait
        Write-Log "Resultado de $($job.Name):" "INFO"
        $result | ForEach-Object { Write-Host "  $_" }
        Remove-Job -Job $job
    }

    Write-Log "Tareas paralelas completadas" "SUCCESS"
}

# Función para despliegue optimizado
function Start-OptimizedDeployment {
    Write-Log "Iniciando despliegue optimizado..." "INFO"

    $deployScript = {
        param($projectPath)

        Set-Location $projectPath

        # Verificar Railway CLI
        if (!(Get-Command railway -ErrorAction SilentlyContinue)) {
            Write-Host "Instalando Railway CLI..."
            npm install -g @railway/cli
        }

        # Login si es necesario
        if (!(Test-Path "$env:USERPROFILE\.railway\config.json")) {
            Write-Host "Railway login requerido"
            return "LOGIN_REQUIRED"
        }

        # Desplegar
        Write-Host "Desplegando a Railway..."
        $deployResult = railway deploy 2>&1
        return $deployResult
    }

    $job = Start-Job -ScriptBlock $deployScript -ArgumentList "C:\Users\DELL\Desktop\BackendBot" -Name "RailwayDeploy"

    # Mostrar progreso
    while ($job.State -eq "Running") {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }

    $result = Receive-Job -Job $job
    Remove-Job -Job $job

    if ($result -eq "LOGIN_REQUIRED") {
        Write-Log "Railway login requerido. Ejecuta: railway login" "WARN"
    } else {
        Write-Log "Despliegue completado" "SUCCESS"
        $result | ForEach-Object { Write-Host $_ }
    }
}

# Función para monitoreo en tiempo real
function Start-RealTimeMonitor {
    Write-Log "Iniciando monitoreo en tiempo real..." "INFO"

    $monitorScript = {
        param($projectPath)

        Set-Location $projectPath

        while ($true) {
            # Verificar procesos Python
            $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
            if ($pythonProcesses) {
                Write-Host "$(Get-Date -Format 'HH:mm:ss') - Procesos Python activos: $($pythonProcesses.Count)"
            }

            # Verificar archivos modificados recientemente
            $recentFiles = Get-ChildItem -Recurse -File | Where-Object {
                $_.LastWriteTime -gt (Get-Date).AddMinutes(-5)
            }
            if ($recentFiles) {
                Write-Host "Archivos modificados recientemente:"
                $recentFiles | ForEach-Object {
                    Write-Host "  $($_.FullName) - $($_.LastWriteTime)"
                }
            }

            Start-Sleep -Seconds 30
        }
    }

    Start-Job -ScriptBlock $monitorScript -ArgumentList "C:\Users\DELL\Desktop\BackendBot" -Name "RealTimeMonitor"
    Write-Log "Monitoreo iniciado en segundo plano (Job ID: $(Get-Job -Name RealTimeMonitor).Id)" "SUCCESS"
}

# Función principal
function Main {
    Write-Log "=== BackendBot PowerShell Automation ===" "INFO"
    Write-Log "PowerShell Version: $($PSVersionTable.PSVersion)" "INFO"
    Write-Log "Working Directory: $(Get-Location)" "INFO"

    # Optimizar PowerShell
    if ($Optimize) {
        Optimize-PowerShell
    }

    # Ejecutar tareas en paralelo
    if ($Parallel) {
        Start-ParallelTasks
    }

    # Despliegue
    if ($Deploy) {
        Start-OptimizedDeployment
    }

    # Tests
    if ($Test) {
        Write-Log "Ejecutando tests..." "INFO"
        Set-Location "C:\Users\DELL\Desktop\BackendBot"
        python -m pytest tests/ -v --tb=short
    }

    # Monitoreo
    if ($Monitor) {
        Start-RealTimeMonitor
    }

    # Si no se especifica nada, mostrar ayuda
    if (!$Parallel -and !$Optimize -and !$Deploy -and !$Test -and !$Monitor) {
        Write-Log "Uso: .\automation.ps1 [-Parallel] [-Optimize] [-Deploy] [-Test] [-Monitor]" "INFO"
        Write-Log "Ejemplos:" "INFO"
        Write-Log "  .\automation.ps1 -Parallel -Optimize    # Optimización completa" "INFO"
        Write-Log "  .\automation.ps1 -Deploy               # Despliegue optimizado" "INFO"
        Write-Log "  .\automation.ps1 -Test -Monitor        # Tests + monitoreo" "INFO"
    }

    # Mostrar jobs activos
    $activeJobs = Get-Job | Where-Object { $_.State -eq "Running" }
    if ($activeJobs) {
        Write-Log "Jobs activos:" "INFO"
        $activeJobs | ForEach-Object {
            Write-Log "  $($_.Name) (ID: $($_.Id)) - $($_.State)" "INFO"
        }
    }

    Write-Log "=== Automatización completada ===" "SUCCESS"
}

# Ejecutar función principal
Main
