# Ejecuta varias tareas de BackendBot en segundo plano usando PowerShell multitarea

# Tarea 1: Staging preview (dry-run)
Start-Job -Name StagingPreview -ScriptBlock {
    python -c "from backendbot.staging_automation import run_preview_workflow; print(run_preview_workflow())"
}

# Tarea 2: Limpieza de disco (simulada)
Start-Job -Name DiskCleanup -ScriptBlock {
    python -c "from backendbot.staging_automation import perform_disk_cleanup_preview; print(perform_disk_cleanup_preview())"
}

# Tarea 3: Optimización de RAM (simulada)
Start-Job -Name RamOptimize -ScriptBlock {
    python -c "from backendbot.staging_automation import optimize_ram; print(optimize_ram())"
}

# Tarea 4: Ejecutar API health check (si tienes endpoint)
Start-Job -Name HealthCheck -ScriptBlock {
    python -c "import requests; print(requests.get('http://localhost:8000/system-health').json())"
}

# Espera y muestra resultados
Start-Sleep -Seconds 5
Get-Job | Receive-Job
