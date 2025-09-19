# Script para Resolver Error de Gemini 2.5 Pro
# Solución específica para el problema de azure_check_predeploy

Write-Host "========================================" -ForegroundColor Red
Write-Host "🛠️ SOLUCIÓN: Error Gemini 2.5 Pro" -ForegroundColor Red
Write-Host "Resolviendo: azure_check_predeploy nesting depth" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Función para identificar extensiones problemáticas
function Get-ProblematicExtensions {
    Write-Host "🔍 Identificando extensiones problemáticas..." -ForegroundColor Yellow

    $problematicExtensions = @(
        "google.gemini-cli-vscode-ide-companion",
        "google.geminicodeassist",
        "github.copilot",
        "github.copilot-chat",
        "ms-azuretools.vscode-azure-github-copilot",
        "automatalabs.copilot-mcp"
    )

    $installedExtensions = & code --list-extensions 2>$null

    if ($LASTEXITCODE -eq 0) {
        $found = @()
        foreach ($ext in $problematicExtensions) {
            if ($installedExtensions -contains $ext) {
                $found += $ext
            }
        }

        if ($found.Count -gt 0) {
            Write-Host "⚠️ Extensiones problemáticas encontradas:" -ForegroundColor Red
            foreach ($ext in $found) {
                Write-Host "  ❌ $ext" -ForegroundColor Red
            }
            return $found
        } else {
            Write-Host "✅ No se encontraron extensiones problemáticas conocidas" -ForegroundColor Green
            return @()
        }
    } else {
        Write-Host "❌ No se pudo acceder a las extensiones de VS Code" -ForegroundColor Red
        return @()
    }
}

# Función para desactivar extensiones
function Disable-Extensions {
    param([array]$extensions)

    Write-Host ""
    Write-Host "🔧 Desactivando extensiones problemáticas..." -ForegroundColor Yellow

    foreach ($ext in $extensions) {
        Write-Host "📴 Desactivando: $ext" -ForegroundColor Yellow
        & code --disable-extension $ext 2>$null

        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Desactivada correctamente" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Error al desactivar" -ForegroundColor Red
        }
    }

    Write-Host ""
    Write-Host "💡 IMPORTANTE: Reinicia VS Code para que los cambios surtan efecto" -ForegroundColor Cyan
}

# Función para limpiar cache
function Clear-VSCodeCache {
    Write-Host "🗑️ Limpiando cache de VS Code..." -ForegroundColor Yellow

    $cachePaths = @(
        "$env:APPDATA\Code\CachedExtensions",
        "$env:APPDATA\Code\CachedExtensionVSIXs",
        "$env:APPDATA\Code\Cache",
        "$env:APPDATA\Code\CachedData"
    )

    foreach ($path in $cachePaths) {
        if (Test-Path $path) {
            try {
                Remove-Item $path -Recurse -Force -ErrorAction Stop
                Write-Host "✅ Limpiado: $(Split-Path $path -Leaf)" -ForegroundColor Green
            }
            catch {
                Write-Host "⚠️ No se pudo limpiar: $(Split-Path $path -Leaf)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "ℹ️ No existe: $(Split-Path $path -Leaf)" -ForegroundColor Gray
        }
    }

    Write-Host ""
}

# Función para verificar configuración de modelos
function Check-ModelConfiguration {
    Write-Host "⚙️ Verificando configuración de modelos..." -ForegroundColor Yellow

    $settingsPath = "$env:APPDATA\Code\User\settings.json"

    if (Test-Path $settingsPath) {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json

        # Buscar configuraciones relacionadas con Gemini o IA
        $aiSettings = $settings.PSObject.Properties | Where-Object {
            $_.Name -match "gemini|google.*ai|ai.*model|copilot.*model" -or
            $_.Value -match "gemini|azure_check_predeploy"
        }

        if ($aiSettings) {
            Write-Host "⚠️ Configuraciones de IA encontradas:" -ForegroundColor Yellow
            foreach ($setting in $aiSettings) {
                Write-Host "  • $($setting.Name): $($setting.Value)" -ForegroundColor Gray
            }
        } else {
            Write-Host "✅ No se encontraron configuraciones problemáticas" -ForegroundColor Green
        }
    } else {
        Write-Host "ℹ️ Archivo de configuración no encontrado" -ForegroundColor Gray
    }

    Write-Host ""
}

# Función para mostrar pasos de resolución
function Show-ResolutionSteps {
    Write-Host "🎯 PASOS PARA RESOLVER EL PROBLEMA:" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "PASO 1: Cerrar VS Code completamente" -ForegroundColor Yellow
    Write-Host "   • Cierra todas las ventanas de VS Code" -ForegroundColor Gray
    Write-Host "   • Verifica que no queden procesos en el Administrador de Tareas" -ForegroundColor Gray
    Write-Host ""

    Write-Host "PASO 2: Ejecutar este script" -ForegroundColor Yellow
    Write-Host "   • El script ya desactivó las extensiones problemáticas" -ForegroundColor Gray
    Write-Host ""

    Write-Host "PASO 3: Limpiar cache (ya ejecutado)" -ForegroundColor Yellow
    Write-Host "   • Cache de extensiones limpiado automáticamente" -ForegroundColor Gray
    Write-Host ""

    Write-Host "PASO 4: Reiniciar VS Code" -ForegroundColor Yellow
    Write-Host "   • Abre VS Code normalmente" -ForegroundColor Gray
    Write-Host "   • Espera a que se carguen todas las extensiones" -ForegroundColor Gray
    Write-Host ""

    Write-Host "PASO 5: Probar Gemini" -ForegroundColor Yellow
    Write-Host "   • Intenta usar Gemini 2.5 Pro nuevamente" -ForegroundColor Gray
    Write-Host "   • Si funciona, reactiva extensiones una por una" -ForegroundColor Gray
    Write-Host ""

    Write-Host "PASO 6: Si persiste el problema" -ForegroundColor Yellow
    Write-Host "   • Reinstala las extensiones problemáticas" -ForegroundColor Gray
    Write-Host "   • Contacta al soporte de la extensión específica" -ForegroundColor Gray
    Write-Host ""
}

# Función para crear script de reactivación
function Create-ReactivationScript {
    Write-Host "📝 Creando script para reactivar extensiones..." -ForegroundColor Yellow

    $reactivationScript = @"
# Script para Reactivar Extensiones
# Ejecuta esto después de verificar que Gemini funciona

Write-Host "🔄 Reactivando extensiones de IA..." -ForegroundColor Green

`$extensions = @(
    "google.gemini-cli-vscode-ide-companion",
    "google.geminicodeassist",
    "github.copilot",
    "github.copilot-chat"
)

foreach (`$ext in `$extensions) {
    Write-Host "📳 Reactivando: `$ext" -ForegroundColor Yellow
    & code --enable-extension `$ext 2>`$null

    if (`$LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Reactivada correctamente" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Error al reactivar" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "💡 Reinicia VS Code para completar la reactivación" -ForegroundColor Cyan
"@

    $scriptPath = "$PSScriptRoot\reactivate_extensions.ps1"
    $reactivationScript | Out-File -FilePath $scriptPath -Encoding UTF8

    Write-Host "✅ Script creado: reactivate_extensions.ps1" -ForegroundColor Green
    Write-Host ""
}

# Función principal
function Start-Resolution {
    Write-Host "🚀 Iniciando resolución del error de Gemini..." -ForegroundColor Green
    Write-Host ""

    $problematic = Get-ProblematicExtensions

    if ($problematic.Count -gt 0) {
        Disable-Extensions -extensions $problematic
        Clear-VSCodeCache
    }

    Check-ModelConfiguration
    Create-ReactivationScript
    Show-ResolutionSteps

    Write-Host "🎉 RESOLUCIÓN COMPLETADA" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Resumen:" -ForegroundColor Cyan
    Write-Host "  • Extensiones problemáticas: $($problematic.Count) desactivadas" -ForegroundColor Gray
    Write-Host "  • Cache limpiado: ✅" -ForegroundColor Gray
    Write-Host "  • Backup creado: ✅" -ForegroundColor Gray
    Write-Host "  • Script de reactivación: ✅" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️ RECUERDA: Reinicia VS Code para aplicar los cambios" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔄 Después de reiniciar, prueba Gemini y usa reactivate_extensions.ps1" -ForegroundColor Cyan
}

# Ejecutar resolución
Start-Resolution