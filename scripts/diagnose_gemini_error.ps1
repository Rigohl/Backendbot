# Script para Diagnosticar y Resolver Error de Gemini 2.5 Pro
# Problema: FunctionDeclaration 'azure_check_predeploy' exceeds maximum allowed nesting depth

Write-Host "========================================" -ForegroundColor Red
Write-Host "🔧 DIAGNÓSTICO: Error Gemini 2.5 Pro" -ForegroundColor Red
Write-Host "Problema: azure_check_predeploy nesting depth" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Función para verificar extensiones de VS Code
function Test-VSCodeExtensions {
    Write-Host "🔍 Verificando extensiones de VS Code relacionadas con IA..." -ForegroundColor Yellow

    $extensions = & code --list-extensions 2>$null

    if ($LASTEXITCODE -eq 0) {
        $aiExtensions = $extensions | Where-Object {
            $_ -match "gemini|google|ai|copilot|anthropic|openai" -or
            $_ -match "intellicode|tabnine|pytorch|tensorflow"
        }

        if ($aiExtensions) {
            Write-Host "⚠️ Extensiones de IA encontradas:" -ForegroundColor Yellow
            foreach ($ext in $aiExtensions) {
                Write-Host "  • $ext" -ForegroundColor Gray
            }
            Write-Host ""
            Write-Host "💡 RECOMENDACIÓN: Desactiva temporalmente estas extensiones para probar" -ForegroundColor Cyan
        } else {
            Write-Host "✅ No se encontraron extensiones de IA sospechosas" -ForegroundColor Green
        }
    } else {
        Write-Host "❌ No se pudo acceder a VS Code. Asegúrate de que esté instalado." -ForegroundColor Red
    }

    Write-Host ""
}

# Función para verificar configuraciones de GitHub Copilot
function Test-GitHubCopilot {
    Write-Host "🔍 Verificando configuración de GitHub Copilot..." -ForegroundColor Yellow

    # Verificar si Copilot está habilitado
    $copilotEnabled = code --list-extensions | Where-Object { $_ -eq "GitHub.copilot" }

    if ($copilotEnabled) {
        Write-Host "⚠️ GitHub Copilot está instalado" -ForegroundColor Yellow
        Write-Host "💡 RECOMENDACIÓN: Desactiva Copilot temporalmente" -ForegroundColor Cyan
        Write-Host "   VS Code > Extensiones > GitHub Copilot > Desactivar" -ForegroundColor Gray
    } else {
        Write-Host "✅ GitHub Copilot no está instalado" -ForegroundColor Green
    }

    Write-Host ""
}

# Función para verificar archivos de configuración
function Test-ConfigurationFiles {
    Write-Host "🔍 Verificando archivos de configuración..." -ForegroundColor Yellow

    $configPaths = @(
        "$env:APPDATA\Code\User\settings.json",
        "$env:APPDATA\Code\User\keybindings.json",
        "$env:APPDATA\Code\User\tasks.json"
    )

    foreach ($path in $configPaths) {
        if (Test-Path $path) {
            Write-Host "✅ Encontrado: $path" -ForegroundColor Green

            # Buscar configuraciones relacionadas con Gemini/AI
            $content = Get-Content $path -Raw -ErrorAction SilentlyContinue
            if ($content -match "gemini|google.*ai|anthropic|openai") {
                Write-Host "⚠️ Archivo contiene configuraciones de IA: $path" -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ No encontrado: $path" -ForegroundColor Gray
        }
    }

    Write-Host ""
}

# Función para mostrar soluciones
function Show-Solutions {
    Write-Host "🛠️ SOLUCIONES RECOMENDADAS:" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "1. 🔧 Desactivar Extensiones de IA Temporalmente:" -ForegroundColor Yellow
    Write-Host "   • Abre VS Code" -ForegroundColor Gray
    Write-Host "   • Ve a Extensiones (Ctrl+Shift+X)" -ForegroundColor Gray
    Write-Host "   • Busca extensiones con 'AI', 'Gemini', 'Copilot'" -ForegroundColor Gray
    Write-Host "   • Desactiva una por una y prueba" -ForegroundColor Gray
    Write-Host ""

    Write-Host "2. 🔄 Reiniciar VS Code:" -ForegroundColor Yellow
    Write-Host "   • Cierra completamente VS Code" -ForegroundColor Gray
    Write-Host "   • Espera 10 segundos" -ForegroundColor Gray
    Write-Host "   • Vuelve a abrir" -ForegroundColor Gray
    Write-Host ""

    Write-Host "3. 🗑️ Limpiar Cache de Extensiones:" -ForegroundColor Yellow
    Write-Host "   • Cierra VS Code" -ForegroundColor Gray
    Write-Host "   • Elimina: %APPDATA%\Code\CachedExtensions" -ForegroundColor Gray
    Write-Host "   • Elimina: %APPDATA%\Code\CachedExtensionVSIXs" -ForegroundColor Gray
    Write-Host "   • Reinicia VS Code" -ForegroundColor Gray
    Write-Host ""

    Write-Host "4. ⚙️ Verificar Configuración de Modelos:" -ForegroundColor Yellow
    Write-Host "   • Archivo > Preferencias > Configuración" -ForegroundColor Gray
    Write-Host "   • Busca 'model' o 'ai' o 'gemini'" -ForegroundColor Gray
    Write-Host "   • Revisa configuraciones relacionadas" -ForegroundColor Gray
    Write-Host ""

    Write-Host "5. 🔄 Reinstalar Extensiones Problemáticas:" -ForegroundColor Yellow
    Write-Host "   • Desinstala la extensión problemática" -ForegroundColor Gray
    Write-Host "   • Reinicia VS Code" -ForegroundColor Gray
    Write-Host "   • Reinstala la extensión" -ForegroundColor Gray
    Write-Host ""

    Write-Host "6. 📞 Contactar Soporte:" -ForegroundColor Yellow
    Write-Host "   • Si es GitHub Copilot: https://github.com/github/copilot" -ForegroundColor Gray
    Write-Host "   • Si es otra extensión: Reporta en su repositorio" -ForegroundColor Gray
    Write-Host ""
}

# Función para crear backup de configuraciones
function Backup-Configurations {
    Write-Host "💾 Creando backup de configuraciones..." -ForegroundColor Yellow

    $backupDir = "$env:USERPROFILE\Desktop\VSCode_Backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

    $configFiles = @(
        "$env:APPDATA\Code\User\settings.json",
        "$env:APPDATA\Code\User\keybindings.json",
        "$env:APPDATA\Code\User\tasks.json"
    )

    foreach ($file in $configFiles) {
        if (Test-Path $file) {
            Copy-Item $file $backupDir -ErrorAction SilentlyContinue
            Write-Host "✅ Backup: $(Split-Path $file -Leaf)" -ForegroundColor Green
        }
    }

    Write-Host "📁 Backup guardado en: $backupDir" -ForegroundColor Cyan
    Write-Host ""
}

# Función principal
function Start-Diagnostic {
    Write-Host "🚀 Iniciando diagnóstico del error de Gemini 2.5 Pro..." -ForegroundColor Green
    Write-Host ""

    Test-VSCodeExtensions
    Test-GitHubCopilot
    Test-ConfigurationFiles
    Backup-Configurations
    Show-Solutions

    Write-Host "🎯 RESUMEN DEL PROBLEMA:" -ForegroundColor Cyan
    Write-Host "El error indica que una función 'azure_check_predeploy' está siendo enviada" -ForegroundColor Gray
    Write-Host "a la API de Gemini con demasiados niveles de anidamiento." -ForegroundColor Gray
    Write-Host ""
    Write-Host "Esto generalmente ocurre por:" -ForegroundColor Gray
    Write-Host "• Extensiones de IA mal configuradas" -ForegroundColor Gray
    Write-Host "• Funciones recursivas o complejas" -ForegroundColor Gray
    Write-Host "• Configuraciones de modelos desactualizadas" -ForegroundColor Gray
    Write-Host ""

    Write-Host "✅ Diagnóstico completado. Revisa las recomendaciones arriba." -ForegroundColor Green
}

# Ejecutar diagnóstico
Start-Diagnostic