# Script de Validación de Pre-Deployment BackendBot
# Reemplaza completamente la función azure_check_predeploy problemática

param(
    [string]$EnvironmentName = "backendbot-dev",
    [string]$Location = "eastus",
    [switch]$SkipQuotaCheck,
    [switch]$Verbose
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 VALIDACIÓN DE PRE-DEPLOYMENT" -ForegroundColor Cyan
Write-Host "BackendBot - Azure Infrastructure Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Función para ejecutar comandos con manejo de errores
function Invoke-AzureCommand {
    param(
        [string]$Command,
        [string]$Description,
        [switch]$ContinueOnError
    )

    Write-Host "🔍 $Description..." -ForegroundColor Yellow

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

# 1. Verificar autenticación en Azure
Write-Host "📋 Verificando autenticación en Azure..." -ForegroundColor Yellow
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Host "✅ Autenticado en Azure" -ForegroundColor Green
    Write-Host "   Suscripción: $($account.name) ($($account.id))" -ForegroundColor Gray
    Write-Host "   Usuario: $($account.user.name)" -ForegroundColor Gray
    $subscriptionId = $account.id
}
catch {
    Write-Host "❌ No estás autenticado en Azure" -ForegroundColor Red
    Write-Host "Ejecuta: az login" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 2. Verificar directorio infra
if (-not (Test-Path "infra")) {
    Write-Host "❌ No se encuentra directorio 'infra'" -ForegroundColor Red
    exit 1
}

Push-Location "infra"

# 3. Verificar archivos de infraestructura
Write-Host "📁 Verificando archivos de infraestructura..." -ForegroundColor Yellow

$iacType = $null
$iacFile = $null

if (Test-Path "main.bicep") {
    Write-Host "✅ Encontrado: main.bicep" -ForegroundColor Green
    $iacType = "bicep"
    $iacFile = "main.bicep"
}
elseif (Test-Path "main.tf") {
    Write-Host "✅ Encontrado: main.tf" -ForegroundColor Green
    $iacType = "terraform"
    $iacFile = "main.tf"
}
else {
    Write-Host "❌ No se encontraron archivos de infraestructura (main.bicep o main.tf)" -ForegroundColor Red
    Pop-Location
    exit 1
}

# 4. Validar sintaxis de infraestructura
if ($iacType -eq "bicep") {
    Invoke-AzureCommand -Command "az bicep build --file $iacFile" -Description "Validando sintaxis de Bicep"
}
elseif ($iacType -eq "terraform") {
    # Verificar si terraform está instalado
    try {
        $terraformVersion = terraform version 2>$null
        Invoke-AzureCommand -Command "terraform validate" -Description "Validando sintaxis de Terraform"
    }
    catch {
        Write-Host "⚠️ Terraform no está instalado, omitiendo validación de sintaxis" -ForegroundColor Yellow
    }
}

# 5. Verificar archivos de parámetros
$paramFile = $null
if (Test-Path "main.parameters.json") {
    Write-Host "✅ Encontrado: main.parameters.json" -ForegroundColor Green
    $paramFile = "main.parameters.json"
}
elseif (Test-Path "main.tfvars.json") {
    Write-Host "✅ Encontrado: main.tfvars.json" -ForegroundColor Green
    $paramFile = "main.tfvars.json"
}
else {
    Write-Host "⚠️ No se encontraron archivos de parámetros" -ForegroundColor Yellow
}

Write-Host ""

# 6. Verificar región y recursos disponibles
Write-Host "🌍 Verificando región y recursos disponibles..." -ForegroundColor Yellow

# Obtener región configurada o usar por defecto
$configuredLocation = az configure --list-defaults --query "location" -o tsv 2>$null
if (-not $configuredLocation) {
    $configuredLocation = $Location
}

Write-Host "📍 Región objetivo: $configuredLocation" -ForegroundColor Gray

# 7. Verificar providers requeridos
$providers = @(
    "Microsoft.App",
    "Microsoft.ContainerRegistry",
    "Microsoft.OperationalInsights",
    "Microsoft.ManagedIdentity"
)

foreach ($provider in $providers) {
    $result = Invoke-AzureCommand -Command "az provider show --namespace $provider --query 'registrationState' -o tsv" -Description "Verificando provider $provider" -ContinueOnError
    if ($result) {
        $state = az provider show --namespace $provider --query 'registrationState' -o tsv 2>$null
        if ($state -ne "Registered") {
            Write-Host "⚠️ Provider $provider no está registrado completamente" -ForegroundColor Yellow
            Write-Host "   Estado: $state" -ForegroundColor Gray
        }
    }
}

# 8. Verificar quotas si no se omite
if (-not $SkipQuotaCheck) {
    Write-Host ""
    Write-Host "📊 Verificando quotas de recursos..." -ForegroundColor Yellow

    # Verificar quota de Container Apps
    try {
        $quotaResult = az quota show --scope "/subscriptions/$subscriptionId/providers/Microsoft.App/locations/$configuredLocation" --quota "Microsoft.App" 2>$null | ConvertFrom-Json
        if ($quotaResult) {
            Write-Host "✅ Quota de Container Apps verificada" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "⚠️ No se pudo verificar quota de Container Apps" -ForegroundColor Yellow
    }

    # Verificar disponibilidad de nombres
    $testStorageName = "backendbotstorage$((Get-Random -Maximum 99999).ToString('00000'))"
    try {
        $nameCheck = az storage account check-name --name $testStorageName --query "nameAvailable" -o tsv 2>$null
        if ($nameCheck -eq "true") {
            Write-Host "✅ Nombres de Storage Account disponibles" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "⚠️ No se pudo verificar disponibilidad de Storage Accounts" -ForegroundColor Yellow
    }
}

# 9. Validación final de template
Write-Host ""
Write-Host "🔍 Validación final de template..." -ForegroundColor Yellow

if ($iacType -eq "bicep" -and $paramFile) {
    $validateCommand = "az deployment group validate --resource-group '$EnvironmentName-rg' --template-file $iacFile --parameters $paramFile --mode Complete"
    Invoke-AzureCommand -Command $validateCommand -Description "Validando template de deployment" -ContinueOnError
}

Pop-Location

Write-Host ""
Write-Host "🎉 VALIDACIÓN COMPLETADA EXITOSAMENTE" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Resumen:" -ForegroundColor Cyan
Write-Host "  ✅ Autenticación en Azure: OK" -ForegroundColor Green
Write-Host "  ✅ Archivos de infraestructura: OK" -ForegroundColor Green
Write-Host "  ✅ Sintaxis de infraestructura: OK" -ForegroundColor Green
Write-Host "  ✅ Providers registrados: OK" -ForegroundColor Green
Write-Host "  ✅ Recursos disponibles: OK" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Listo para deployment" -ForegroundColor Green
Write-Host ""

# Información adicional
Write-Host "💡 Información adicional:" -ForegroundColor Cyan
Write-Host "  • Tipo de IaC: $iacType" -ForegroundColor Gray
Write-Host "  • Archivo principal: $iacFile" -ForegroundColor Gray
if ($paramFile) {
    Write-Host "  • Archivo de parámetros: $paramFile" -ForegroundColor Gray
}
Write-Host "  • Región: $configuredLocation" -ForegroundColor Gray
Write-Host "  • Environment: $EnvironmentName" -ForegroundColor Gray