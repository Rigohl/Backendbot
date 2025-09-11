# Script de instalación rápida para BackendBot Auto-Start
# Configura el backend para que se ejecute automáticamente al inicio del sistema

Write-Host "=== BackendBot Auto-Start Setup ===" -ForegroundColor Cyan
Write-Host "Configurando el backend para ejecucion automatica..." -ForegroundColor Yellow

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "main.py")) {
    Write-Host "Error: No se encuentra main.py. Ejecuta este script desde el directorio raiz de BackendBot." -ForegroundColor Red
    exit 1
}

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python no esta instalado o no esta en el PATH." -ForegroundColor Red
    exit 1
}

# Crear directorio de logs si no existe
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    Write-Host "Directorio de logs creado." -ForegroundColor Green
}

# Instalar el servicio usando el script de servicio
Write-Host "Instalando servicio automatico..." -ForegroundColor Yellow
& ".\backend_service.ps1" -Install

# Crear tarea adicional para el monitor
Write-Host "Configurando monitor automatico..." -ForegroundColor Yellow
$monitorAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File .\backend_monitor.ps1 -Start" -WorkingDirectory $PSScriptRoot
$monitorTrigger = New-ScheduledTaskTrigger -AtStartup -Delay "00:00:30"  # 30 segundos despues del inicio
$monitorSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$monitorPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType InteractiveToken

Register-ScheduledTask -TaskName "BackendBotMonitor" -Action $monitorAction -Trigger $monitorTrigger -Settings $monitorSettings -Principal $monitorPrincipal -Force | Out-Null

# Crear script de inicio rapido
$quickStartScript = @"
# Script de inicio rapido para BackendBot
Write-Host "Iniciando BackendBot..." -ForegroundColor Green

# Iniciar servicio
Start-ScheduledTask -TaskName "BackendBotService" -ErrorAction SilentlyContinue

# Iniciar monitor
Start-ScheduledTask -TaskName "BackendBotMonitor" -ErrorAction SilentlyContinue

# Verificar estado
Start-Sleep -Seconds 5
& ".\backend_service.ps1" -Status

Write-Host "BackendBot iniciado correctamente!" -ForegroundColor Green
"@

$quickStartScript | Out-File -FilePath "start_backend_quick.ps1" -Encoding UTF8

# Crear script de parada rapida
$quickStopScript = @"
# Script de parada rapida para BackendBot
Write-Host "Deteniendo BackendBot..." -ForegroundColor Yellow

# Detener monitor
Stop-ScheduledTask -TaskName "BackendBotMonitor" -ErrorAction SilentlyContinue

# Detener servicio
Stop-ScheduledTask -TaskName "BackendBotService" -ErrorAction SilentlyContinue

# Verificar que se detuvo
Start-Sleep -Seconds 3
& ".\backend_service.ps1" -Status

Write-Host "BackendBot detenido." -ForegroundColor Green
"@

$quickStopScript | Out-File -FilePath "stop_backend_quick.ps1" -Encoding UTF8

# Actualizar README con instrucciones
$readmeContent = @"

## Inicio Automatico

BackendBot puede ejecutarse automaticamente al inicio del sistema:

### Instalacion Rapida
```powershell
.\install_autostart.ps1
```

### Inicio/Parada Rapida
```powershell
# Iniciar
.\start_backend_quick.ps1

# Detener
.\stop_backend_quick.ps1
```

### Gestion del Servicio
```powershell
# Ver estado
.\backend_service.ps1 -Status

# Iniciar manualmente
.\backend_service.ps1 -Start

# Detener manualmente
.\backend_service.ps1 -Stop

# Desinstalar
.\backend_service.ps1 -Uninstall
```

### Monitor de Salud
El sistema incluye un monitor automatico que:
- Verifica la salud del backend cada 30 segundos
- Reinicia automaticamente si detecta fallos
- Registra toda la actividad en `logs/monitor.log`

```powershell
# Ver logs del monitor
Get-Content logs/monitor.log -Tail 20
```

### Logs
- `logs/service.log`: Actividad del servicio principal
- `logs/monitor.log`: Actividad del monitor de salud
"@

if (Test-Path "README.md") {
    $existingContent = Get-Content "README.md" -Raw
    if ($existingContent -notlike "*Inicio Automatico*") {
        $existingContent + $readmeContent | Out-File -FilePath "README.md" -Encoding UTF8
        Write-Host "README.md actualizado con instrucciones de auto-inicio." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=== Instalacion Completada ===" -ForegroundColor Green
Write-Host "BackendBot ahora se ejecutara automaticamente al inicio del sistema." -ForegroundColor Green
Write-Host ""
Write-Host "Comandos disponibles:" -ForegroundColor Cyan
Write-Host "  .\start_backend_quick.ps1    - Iniciar rapidamente" -ForegroundColor White
Write-Host "  .\stop_backend_quick.ps1     - Detener rapidamente" -ForegroundColor White
Write-Host "  .\backend_service.ps1 -Status - Ver estado del servicio" -ForegroundColor White
Write-Host ""
Write-Host "El sistema se reiniciara automaticamente si falla." -ForegroundColor Yellow
Write-Host "Revisa los logs en la carpeta 'logs' para monitorear la actividad." -ForegroundColor Yellow