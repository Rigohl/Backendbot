try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/reset-memoria" -Method POST
    Write-Host "✅ Memoria de decisiones reseteada." -ForegroundColor Yellow
} catch { Write-Host "❌ No se pudo conectar al backend." -ForegroundColor Red }
