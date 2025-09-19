# Script para Reactivar Extensiones
# Ejecuta esto después de verificar que Gemini funciona
# NOTA: Excluye la extensión problemática azure-github-copilot por defecto

Write-Host "🔄 Reactivando extensiones de IA..." -ForegroundColor Green
Write-Host "⚠️  EXCLUYENDO: ms-azuretools.vscode-azure-github-copilot (problemática)" -ForegroundColor Yellow
Write-Host ""

$extensions = @(
    "google.gemini-cli-vscode-ide-companion",
    "google.geminicodeassist",
    "github.copilot",
    "github.copilot-chat"
    # EXCLUYENDO: "ms-azuretools.vscode-azure-github-copilot" - Causa nesting depth error
)

foreach ($ext in $extensions) {
    Write-Host "📳 Reactivando: $ext" -ForegroundColor Yellow
    & code --enable-extension $ext 2>$null

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Reactivada correctamente" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Error al reactivar" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "💡 Reinicia VS Code para completar la reactivación" -ForegroundColor Cyan
