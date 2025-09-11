try {
    \ = Invoke-RestMethod -Uri "http://127.0.0.1:8000/optimize" -Method POST
    Write-Host "✅ RAM liberada:  MB" -ForegroundColor Green
} catch { Write-Host "❌ No se pudo conectar al backend." -ForegroundColor Red }
