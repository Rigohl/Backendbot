# BackendBot Initialization Script
# Configura el entorno completo automáticamente

param(
    [switch]$Force,
    [switch]$SkipTests,
    [switch]$SkipDeps
)

Write-Host "=== BackendBot Environment Setup ===" -ForegroundColor Green

$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$modulePath = Join-Path $projectPath "BackendAutomation.psm1"

# Verificar PowerShell versión
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Warning "PowerShell 5.0+ requerido. Versión actual: $($PSVersionTable.PSVersion)"
    exit 1
}

# Configurar política de ejecución si es necesario
$currentPolicy = Get-ExecutionPolicy
if ($currentPolicy -ne "RemoteSigned" -and $currentPolicy -ne "Bypass") {
    Write-Host "Configurando política de ejecución..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "Política de ejecución configurada" -ForegroundColor Green
    } catch {
        Write-Warning "No se pudo configurar política de ejecución automáticamente"
    }
}

# Instalar dependencias de Python si no se salta
if (!$SkipDeps) {
    Write-Host "Verificando dependencias de Python..." -ForegroundColor Yellow

    # Verificar pip
    try {
        $pipVersion = python -m pip --version 2>$null
        Write-Host "Pip encontrado: $pipVersion" -ForegroundColor Green
    } catch {
        Write-Warning "Pip no encontrado. Instalando..."
        # Instalar pip si no está disponible
        try {
            python -m ensurepip --upgrade
        } catch {
            Write-Error "No se pudo instalar pip automáticamente"
            exit 1
        }
    }

    # Instalar dependencias
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    try {
        python -m pip install -r (Join-Path $projectPath "requirements.txt")
        Write-Host "Dependencias instaladas" -ForegroundColor Green
    } catch {
        Write-Error "Error instalando dependencias: $_"
        exit 1
    }
}

# Verificar Node.js para Railway CLI
if (!$SkipDeps) {
    Write-Host "Verificando Node.js..." -ForegroundColor Yellow
    try {
        $nodeVersion = node --version 2>$null
        Write-Host "Node.js encontrado: $nodeVersion" -ForegroundColor Green

        # Instalar Railway CLI si no está
        if (!(Get-Command railway -ErrorAction SilentlyContinue)) {
            Write-Host "Instalando Railway CLI..." -ForegroundColor Yellow
            npm install -g @railway/cli
            Write-Host "Railway CLI instalado" -ForegroundColor Green
        }
    } catch {
        Write-Warning "Node.js no encontrado. Railway CLI no se instalará automáticamente."
    }
}

# Ejecutar tests si no se salta
if (!$SkipTests) {
    Write-Host "Ejecutando tests iniciales..." -ForegroundColor Yellow
    try {
        Push-Location $projectPath
        python -m pytest tests/ -v --tb=short
        Write-Host "Tests ejecutados exitosamente" -ForegroundColor Green
    } catch {
        Write-Warning "Algunos tests fallaron. Revisa la configuración."
    } finally {
        Pop-Location
    }
}

# Importar módulo de automatización
Write-Host "Importando módulo de automatización..." -ForegroundColor Yellow
try {
    Import-Module $modulePath -Force:$Force
    Write-Host "Módulo importado exitosamente" -ForegroundColor Green
} catch {
    Write-Error "Error importando módulo: $_"
    exit 1
}

# Configurar alias globales
Write-Host "Configurando alias..." -ForegroundColor Yellow
Set-Alias -Name backend -Value { Set-Location $projectPath }.GetNewClosure() -Scope Global
Set-Alias -Name test-backend -Value { Start-BackendAutomation -Test }.GetNewClosure() -Scope Global
Set-Alias -Name deploy-backend -Value { Start-BackendAutomation -Deploy }.GetNewClosure() -Scope Global

# Crear función de ayuda global
function global:Get-BackendHelp {
    Write-Host "=== BackendBot Help ===" -ForegroundColor Green
    Write-Host "Comandos disponibles:" -ForegroundColor Cyan
    Write-Host "  backend              - Ir al directorio del proyecto" -ForegroundColor White
    Write-Host "  test-backend         - Ejecutar tests" -ForegroundColor White
    Write-Host "  deploy-backend       - Desplegar aplicación" -ForegroundColor White
    Write-Host "  backend-auto         - Automatización completa" -ForegroundColor White
    Write-Host "  backend-auto -Test   - Solo tests" -ForegroundColor White
    Write-Host "  backend-auto -Deploy - Solo despliegue" -ForegroundColor White
    Write-Host "  backend-auto -Full   - Tests + Despliegue + Monitoreo" -ForegroundColor White
    Write-Host "  Get-BackendStatus    - Ver estado del proyecto" -ForegroundColor White
    Write-Host "`nEjemplos:" -ForegroundColor Yellow
    Write-Host "  test-backend" -ForegroundColor White
    Write-Host "  backend-auto -Full" -ForegroundColor White
}

# Mostrar ayuda inicial
Get-BackendHelp

Write-Host "`n=== Configuración Completada ===" -ForegroundColor Green
Write-Host "Ejecuta 'Get-BackendStatus' para ver el estado del proyecto" -ForegroundColor Cyan
Write-Host "Ejecuta 'backend-auto' para ver opciones de automatización" -ForegroundColor Cyan
