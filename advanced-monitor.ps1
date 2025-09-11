# Script Avanzado de Monitoreo BackendBot con PowerShell
param(
    [int]$IntervalSeconds = 15,
    [string]$BaseUrl = 'http://localhost:8000',
    [switch]$EnableNotifications,
    [switch]$AutoOptimize
)

Write-Host '=== BackendBot Advanced Monitor ===' -ForegroundColor Cyan
Write-Host "Intervalo: $IntervalSeconds segundos | URL: $BaseUrl" -ForegroundColor Yellow
Write-Host "Notificaciones: $($EnableNotifications ? 'Habilitadas' : 'Deshabilitadas')" -ForegroundColor Yellow
Write-Host "Auto-optimización: $($AutoOptimize ? 'Habilitada' : 'Deshabilitada')" -ForegroundColor Yellow
Write-Host ''

$headers = @{
    'Authorization' = 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('admin:password'))
}

$lastNotification = @{
    cpu = (Get-Date).AddMinutes(-10)
    memory = (Get-Date).AddMinutes(-10)
    disk = (Get-Date).AddMinutes(-10)
}

function Send-Notification {
    param([string]$Title, [string]$Message, [string]$Type = 'Info')
    
    if ($EnableNotifications) {
        $color = switch ($Type) {
            'Warning' { 'Yellow' }
            'Error' { 'Red' }
            default { 'Green' }
        }
        Write-Host "[] $Title" -ForegroundColor $color
        Write-Host "$Message" -ForegroundColor $color
        
        # Aquí se podría integrar con Windows Toast Notifications
        # New-BurntToastNotification -Text $Title, $Message -AppLogo 'C:\path\to\icon.png'
    }
}

function Test-BackendConnection {
    try {
        $response = Invoke-WebRequest -Uri "$BaseUrl/" -Headers $headers -Method Get -TimeoutSec 5
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

while ($true) {
    try {
        # Verificar conexión al backend
        if (-not (Test-BackendConnection)) {
            Write-Host "ERROR: No se puede conectar al backend en $BaseUrl" -ForegroundColor Red
            Start-Sleep -Seconds $IntervalSeconds
            continue
        }
        
        # Health check
        $health = Invoke-RestMethod -Uri "$BaseUrl/health" -Headers $headers -Method Get -TimeoutSec 5
        $uptime = [math]::Round($health.uptime_seconds / 60, 1)
        
        Write-Host "Health: $(.status.ToUpper()) | Uptime: ${uptime}min | CPU: $(.cpu_percent)% | Mem: $(.memory_percent)% | Disk: $(.disk_percent)%" -ForegroundColor Green
        
        # Alertas
        $alerts = Invoke-RestMethod -Uri "$BaseUrl/alerts" -Headers $headers -Method Get -TimeoutSec 5
        if ($alerts.Count -gt 0) {
            Write-Host "ALERTAS ACTIVAS: $(.Count)" -ForegroundColor Red
            $alerts | ForEach-Object {
                Write-Host "  $(.type.ToUpper()): $(.message)" -ForegroundColor Yellow
            }
        }
        
        # Información extendida del sistema
        $extended = Invoke-RestMethod -Uri "$BaseUrl/system/extended" -Headers $headers -Method Get -TimeoutSec 5
        if ($extended.gpu_info -and $extended.gpu_info.Count -gt 0) {
            Write-Host "GPU Info:" -ForegroundColor Magenta
            $extended.gpu_info | ForEach-Object {
                Write-Host "  $(.name): $(.gpu_util_percent)% uso | $([math]::Round($_.memory_used/$_.memory_total*100,1))% memoria" -ForegroundColor Magenta
            }
        }
        
        # Análisis de rendimiento
        $performance = Invoke-RestMethod -Uri "$BaseUrl/system/performance" -Headers $headers -Method Get -TimeoutSec 5
        Write-Host "Rendimiento General: $(.overall_status.ToUpper())" -ForegroundColor Cyan
        
        # Auto-optimización si está habilitada
        if ($AutoOptimize -and $performance.overall_status -eq 'critical') {
            Write-Host "AUTO-OPTIMIZACIÓN: Ejecutando optimización automática..." -ForegroundColor Yellow
            try {
                $optimize = Invoke-RestMethod -Uri "$BaseUrl/optimize" -Headers $headers -Method Post -TimeoutSec 10
                Write-Host "Optimización completada: $(.ram_liberada_mb) MB liberados" -ForegroundColor Green
            } catch {
                Write-Host "Error en auto-optimización: $(.Exception.Message)" -ForegroundColor Red
            }
        }
        
        # Procesos top
        $top = Invoke-RestMethod -Uri "$BaseUrl/processes/top?limit=3" -Headers $headers -Method Get -TimeoutSec 5
        if ($top.Count -gt 0) {
            Write-Host "Top Procesos (CPU):" -ForegroundColor Blue
            $top | ForEach-Object { 
                Write-Host "  $(.name) (PID:$(.pid)) - CPU:$(.cpu_percent)% Mem:$(.memory_mb)MB" -ForegroundColor Blue
            }
        }
        
        Write-Host "---" -ForegroundColor DarkGray
        
    } catch {
        Write-Host "Error en monitoreo: $(.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds $IntervalSeconds
}
