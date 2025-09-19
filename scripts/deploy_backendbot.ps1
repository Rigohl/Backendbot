# Script de Deployment Completo BackendBot
# Incluye validación y deployment usando Azure CLI

param(
    [string]$EnvironmentName = "backendbot-dev",
    [string]$Location = "eastus",
    [switch]$SkipValidation,
    [switch]$SkipQuotaCheck,
    [switch]$Verbose
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOYMENT BACKENDBOT" -ForegroundColor Cyan
Write-Host "Azure Container Apps + Infrastructure" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Función para ejecutar comandos con manejo de errores
function Invoke-AzureCommand {
    param(
        [string]$Command,
        [string]$Description,
        [switch]$ContinueOnError
    )

    Write-Host "🔧 $Description..." -ForegroundColor Yellow

    try {
        $result = Invoke-Expression $Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description completada" -ForegroundColor Green
            if ($Verbose) {
                Write-Host "   Resultado: $result" -ForegroundColor Gray
            }
            return $true
        } else {
            Write-Host "❌ Error en $Description" -ForegroundColor Red
            Write-Host "   Error: $result" -ForegroundColor Red
            if (-not $ContinueOnError) {
                exit 1
            }
            return $false
        }
    }
    catch {
        Write-Host "❌ Excepción en $Description" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        if (-not $ContinueOnError) {
            exit 1
        }
        return $false
    }
}

# 1. Ejecutar validación si no se omite
if (-not $SkipValidation) {
    Write-Host "🔍 Ejecutando validación de pre-deployment..." -ForegroundColor Yellow
    $validationScript = Join-Path $PSScriptRoot "validate_predeploy.ps1"

    if (Test-Path $validationScript) {
        $validationArgs = @("-EnvironmentName", $EnvironmentName, "-Location", $Location)
        if ($SkipQuotaCheck) { $validationArgs += "-SkipQuotaCheck" }
        if ($Verbose) { $validationArgs += "-Verbose" }

        & $validationScript @validationArgs

        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Validación fallida. Abortando deployment." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "⚠️ Script de validación no encontrado. Continuando..." -ForegroundColor Yellow
    }
}

Write-Host ""

# 2. Crear grupo de recursos si no existe
$resourceGroupName = "$EnvironmentName-rg"
Write-Host "📁 Verificando grupo de recursos: $resourceGroupName" -ForegroundColor Yellow

$rgExists = az group exists --name $resourceGroupName 2>$null
if ($rgExists -eq "false") {
    Write-Host "🔧 Creando grupo de recursos..." -ForegroundColor Yellow
    Invoke-AzureCommand -Command "az group create --name $resourceGroupName --location $Location --tags Project=BackendBot Environment=Development" -Description "Creando grupo de recursos"
} else {
    Write-Host "✅ Grupo de recursos ya existe" -ForegroundColor Green
}

# 3. Navegar al directorio infra
if (-not (Test-Path "infra")) {
    Write-Host "❌ No se encuentra directorio 'infra'" -ForegroundColor Red
    exit 1
}

Push-Location "infra"

# 4. Ejecutar deployment
Write-Host ""
Write-Host "🚀 Iniciando deployment de infraestructura..." -ForegroundColor Yellow

$deploymentCommand = "az deployment group create --resource-group $resourceGroupName --template-file main.bicep --parameters main.parameters.json --mode Incremental"

if ($Verbose) {
    $deploymentCommand += " --verbose"
}

Invoke-AzureCommand -Command $deploymentCommand -Description "Deploying infraestructura BackendBot"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 DEPLOYMENT COMPLETADO EXITOSAMENTE" -ForegroundColor Green
    Write-Host ""

    # 5. Mostrar outputs del deployment
    Write-Host "📋 Outputs del deployment:" -ForegroundColor Cyan
    try {
        $outputs = az deployment group show --resource-group $resourceGroupName --name main --query "properties.outputs" -o json 2>$null | ConvertFrom-Json

        if ($outputs) {
            $outputs.PSObject.Properties | ForEach-Object {
                Write-Host "  • $($_.Name): $($_.Value.value)" -ForegroundColor Gray
            }
        }
    }
    catch {
        Write-Host "  ⚠️ No se pudieron obtener los outputs" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "🌐 URLs de acceso:" -ForegroundColor Cyan

    # Obtener URL de Container App
    try {
        $appUrl = az containerapp show --name "$EnvironmentName-app" --resource-group $resourceGroupName --query "properties.configuration.ingress.fqdn" -o tsv 2>$null
        if ($appUrl) {
            Write-Host "  • BackendBot App: https://$appUrl" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "  ⚠️ No se pudo obtener URL de Container App" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "  1. Verifica que la aplicación esté funcionando" -ForegroundColor Gray
    Write-Host "  2. Configura variables de entorno si es necesario" -ForegroundColor Gray
    Write-Host "  3. Revisa logs en Azure Portal si hay problemas" -ForegroundColor Gray
    Write-Host "  4. Considera configurar CI/CD para deployments automáticos" -ForegroundColor Gray

} else {
    Write-Host ""
    Write-Host "❌ DEPLOYMENT FALLIDO" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔍 Revisando logs de deployment..." -ForegroundColor Yellow

    try {
        az deployment group show --resource-group $resourceGroupName --name main --query "properties.error" -o json 2>$null | ConvertFrom-Json
    }
    catch {
        Write-Host "  ⚠️ No se pudieron obtener detalles del error" -ForegroundColor Yellow
    }

    exit 1
}

Pop-Location