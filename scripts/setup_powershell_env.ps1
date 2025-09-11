# Setup script para PowerShell: instala posh-git y oh-my-posh, configura perfil de usuario
# Ejecutar en PowerShell (pwsh) como usuario normal. Este script intenta ejecutar sin elevación.

$ErrorActionPreference = 'Stop'

Write-Host "Iniciando configuración PowerShell para desarrollo..." -ForegroundColor Cyan

# Comprueba versión de PowerShell
$psv = $PSVersionTable.PSVersion
Write-Host "PowerShell version: $psv"

# Instalar posh-git y oh-my-posh desde PowerShell Gallery si no están instalados
function Install-ModuleIfMissing {
    param(
        [string]$Name
    )
    if (-not (Get-Module -ListAvailable -Name $Name)) {
        Write-Host "Instalando $Name..." -ForegroundColor Yellow
        Install-Module $Name -Scope CurrentUser -Force -AllowClobber
    } else {
        Write-Host "$Name ya instalado." -ForegroundColor Green
    }
}

Install-ModuleIfMissing -Name 'posh-git'
Install-ModuleIfMissing -Name 'oh-my-posh'

# Añadir imports al perfil del usuario si no existen
$profilePath = $PROFILE.CurrentUserAllHosts
if (-not (Test-Path -Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force | Out-Null
}
$profileText = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
$needUpdate = $false
if ($profileText -notmatch "Import-Module posh-git") { $profileText += "`nImport-Module posh-git"; $needUpdate = $true }
if ($profileText -notmatch "Import-Module oh-my-posh") { $profileText += "`nImport-Module oh-my-posh"; $needUpdate = $true }
if ($profileText -notmatch "Set-Theme") {
    # Añadir tema por defecto si oh-my-posh está instalado
    $profileText += "`n# Tema recomendado: Paradox (puedes cambiarlo)
Set-Theme -Name paradox"; $needUpdate = $true
}
if ($needUpdate) { $profileText | Out-File -FilePath $profilePath -Encoding utf8 -Force; Write-Host "Perfil actualizado: $profilePath" -ForegroundColor Green } else { Write-Host "Perfil ya contiene configuraciones." -ForegroundColor Green }

Write-Host "Instalación completada. Recomiendo reiniciar PowerShell para aplicar cambios." -ForegroundColor Cyan
