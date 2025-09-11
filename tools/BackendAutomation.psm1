# BackendBot Advanced PowerShell Automation
# Funciones avanzadas para desarrollo (sin workflows para compatibilidad PS6+)

function Test-BackendWorkflow {
    param([string]$ProjectPath = $PWD)

    Write-Output "=== Iniciando Tests Paralelos ==="

    # Crear jobs para paralelización
    $jobs = @()

    # Job 1: Tests de API
    $jobs += Start-Job -ScriptBlock {
        param($path)
        Set-Location $path
        Write-Output "Ejecutando tests de API..."
        try {
            $result = python -m pytest tests/test_api_routes.py -v --tb=short 2>&1
            return "API Tests: $($result | Out-String)"
        } catch {
            return "API Tests Error: $($_.Exception.Message)"
        }
    } -ArgumentList $ProjectPath

    # Job 2: Verificación de dependencias
    $jobs += Start-Job -ScriptBlock {
        param($path)
        Set-Location $path
        Write-Output "Verificando dependencias..."
        try {
            python -c "import fastapi, uvicorn, psutil, pydantic; print('Dependencias OK')" 2>&1
            return "Dependencies: OK"
        } catch {
            return "Dependencies Error: $($_.Exception.Message)"
        }
    } -ArgumentList $ProjectPath

    # Job 3: Linting
    $jobs += Start-Job -ScriptBlock {
        param($path)
        Set-Location $path
        Write-Output "Verificando linting..."
        try {
            if (Get-Command ruff -ErrorAction SilentlyContinue) {
                $result = ruff check . --quiet 2>&1
                return "Linting: $($result | Out-String)"
            } else {
                return "Linting: Ruff no disponible"
            }
        } catch {
            return "Linting Error: $($_.Exception.Message)"
        }
    } -ArgumentList $ProjectPath

    # Esperar y mostrar resultados
    $jobs | Wait-Job | Receive-Job

    # Limpiar jobs
    $jobs | Remove-Job

    Write-Output "=== Tests Paralelos Completados ==="
}

function Deploy-BackendWorkflow {
    param([string]$ProjectPath = $PWD)

    Write-Output "=== Iniciando Despliegue ==="

    # Verificar Railway CLI
    $railwayAvailable = Get-Command railway -ErrorAction SilentlyContinue

    if ($railwayAvailable) {
        Write-Output "Desplegando con Railway..."
        try {
            Set-Location $ProjectPath
            $deployResult = railway deploy 2>&1
            Write-Output "Deploy Result: $($deployResult | Out-String)"
        } catch {
            Write-Output "Deploy Error: $($_.Exception.Message)"
        }
    } else {
        Write-Output "Railway CLI no encontrado. Instalando..."
        try {
            npm install -g @railway/cli 2>&1
            Write-Output "Railway instalado. Ejecuta el comando nuevamente."
        } catch {
            Write-Output "Error instalando Railway: $($_.Exception.Message)"
        }
    }

    Write-Output "=== Despliegue Completado ==="
}

function Start-BackendAutomation {
    param(
        [switch]$Test,
        [switch]$Deploy,
        [switch]$Monitor,
        [switch]$Full
    )

    $projectPath = "C:\Users\DELL\Desktop\BackendBot"

    Write-Host "=== BackendBot Advanced Automation ===" -ForegroundColor Green
    Write-Host "Proyecto: $projectPath" -ForegroundColor Cyan
    Write-Host "PowerShell Version: $($PSVersionTable.PSVersion)" -ForegroundColor Cyan

    # Ejecutar tests con workflow
    if ($Test -or $Full) {
        Write-Host "Ejecutando tests con workflow..." -ForegroundColor Yellow
        Test-BackendWorkflow -ProjectPath $projectPath
    }

    # Desplegar con workflow
    if ($Deploy -or $Full) {
        Write-Host "Desplegando con workflow..." -ForegroundColor Yellow
        Deploy-BackendWorkflow -ProjectPath $projectPath
    }

    # Monitoreo en background
    if ($Monitor -or $Full) {
        Write-Host "Iniciando monitoreo en background..." -ForegroundColor Yellow

        $monitorScript = {
            param($path)
            while ($true) {
                $pythonProcs = Get-Process python -ErrorAction SilentlyContinue
                if ($pythonProcs) {
                    Write-Host "$(Get-Date -Format 'HH:mm:ss') - Procesos Python: $($pythonProcs.Count)" -ForegroundColor Green
                }

                # Verificar archivos recientes
                $recentFiles = Get-ChildItem $path -Recurse -File | Where-Object {
                    $_.LastWriteTime -gt (Get-Date).AddMinutes(-5)
                }
                if ($recentFiles) {
                    Write-Host "Archivos modificados:" -ForegroundColor Yellow
                    $recentFiles | ForEach-Object {
                        Write-Host "  $($_.FullName)" -ForegroundColor Gray
                    }
                }

                Start-Sleep -Seconds 30
            }
        }

        Start-Job -ScriptBlock $monitorScript -ArgumentList $projectPath -Name "BackendMonitor"
        Write-Host "Monitoreo iniciado (Job ID: $(Get-Job -Name BackendMonitor).Id)" -ForegroundColor Green
    }

    # Mostrar jobs activos
    $activeJobs = Get-Job | Where-Object { $_.State -eq "Running" }
    if ($activeJobs) {
        Write-Host "`nJobs activos:" -ForegroundColor Cyan
        $activeJobs | Format-Table -Property Id, Name, State, Command -AutoSize
    }

    Write-Host "`n=== Automatización Completada ===" -ForegroundColor Green
}

# Alias para facilitar uso
Set-Alias -Name backend-auto -Value Start-BackendAutomation
Set-Alias -Name backend-test -Value { Start-BackendAutomation -Test }
Set-Alias -Name backend-deploy -Value { Start-BackendAutomation -Deploy }
Set-Alias -Name backend-full -Value { Start-BackendAutomation -Full }

# Función de ayuda
function Get-BackendHelp {
    Write-Host "BackendBot Automation Commands:" -ForegroundColor Green
    Write-Host "  backend-test     - Ejecutar tests con workflow" -ForegroundColor White
    Write-Host "  backend-deploy   - Desplegar con workflow" -ForegroundColor White
    Write-Host "  backend-full     - Tests + Deploy + Monitor" -ForegroundColor White
    Write-Host "  backend-auto     - Menú interactivo" -ForegroundColor White
    Write-Host "  Get-Job          - Ver jobs activos" -ForegroundColor White
    Write-Host "  Receive-Job -Id <ID> - Ver resultado de job" -ForegroundColor White
}

# Exportar funciones
Export-ModuleMember -Function Start-BackendAutomation, Get-BackendHelp
Export-ModuleMember -Alias backend-auto, backend-test, backend-deploy, backend-full
