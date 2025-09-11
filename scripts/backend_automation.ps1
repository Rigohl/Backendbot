# Advanced PowerShell automation script for BackendBot
param(
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Optimize,
    [switch]$Monitor,
    [int]$Interval = 300,  # 5 minutes default
    [switch]$Background,
    [switch]$Force
)

$backendPath = Join-Path $PSScriptRoot "..\src\backendbot"
$python = "python"
$mainScript = Join-Path $backendPath "main.py"

# Function to check if backend is running
function Test-BackendRunning {
    $processes = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*main.py*"
    }
    return $processes.Count -gt 0
}

# Function to start backend
function Start-BackendBot {
    if (Test-BackendRunning) {
        Write-Host "BackendBot is already running."
        return
    }

    Write-Host "Starting BackendBot..."
    if ($Background) {
        Start-Process -FilePath $python -ArgumentList $mainScript -WindowStyle Hidden
        Start-Sleep -Seconds 2
        if (Test-BackendRunning) {
            Write-Host "BackendBot started successfully in background."
        } else {
            Write-Host "Failed to start BackendBot."
        }
    } else {
        & $python $mainScript
    }
}

# Function to stop backend
function Stop-BackendBot {
    $processes = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*main.py*"
    }

    if ($processes.Count -eq 0) {
        Write-Host "No BackendBot processes found."
        return
    }

    Write-Host "Stopping BackendBot processes..."
    $processes | ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-Host "Stopped process ID: $($_.Id)"
    }
}

# Function to get status
function Get-BackendStatus {
    $running = Test-BackendRunning

    if ($running) {
        Write-Host "BackendBot Status: RUNNING"

        # Get additional info
        $processes = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like "*main.py*"
        }

        $processes | ForEach-Object {
            Write-Host "  Process ID: $($_.Id)"
            Write-Host "  CPU Usage: $($_.CPU.ToString("F2"))%"
            Write-Host "  Memory Usage: $([math]::Round($_.WorkingSet / 1MB, 2)) MB"
            Write-Host "  Start Time: $($_.StartTime)"
        }
    } else {
        Write-Host "BackendBot Status: STOPPED"
    }

    # Check if API is responding
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "API Status: RESPONDING"
        }
    } catch {
        Write-Host "API Status: NOT RESPONDING"
    }
}

# Function to run optimization
function Invoke-Optimization {
    Write-Host "Running system optimization..."

    if ($Force) {
        Write-Warning "Force mode enabled - this will perform real optimizations!"
        $confirmation = Read-Host "Continue? (yes/no)"
        if ($confirmation -ne "yes") {
            Write-Host "Optimization cancelled."
            return
        }
    }

    # Run RAM optimization
    Write-Host "Optimizing RAM usage..."
    & $python -c "from src.backendbot.staging_automation import optimize_ram; import json; result = optimize_ram(dry_run=$($Force ? 'False' : 'True')); print(json.dumps(result, indent=2))"

    # Run disk cleanup
    Write-Host "Running disk cleanup..."
    & $python -c "from src.backendbot.staging_automation import perform_disk_cleanup_preview; import json; result = perform_disk_cleanup_preview(dry_run=$($Force ? 'False' : 'True')); print(json.dumps(result, indent=2))"

    Write-Host "Optimization completed."
}

# Function for continuous monitoring
function Start-Monitoring {
    Write-Host "Starting continuous monitoring (interval: $Interval seconds)..."
    Write-Host "Press Ctrl+C to stop."

    try {
        while ($true) {
            Clear-Host
            Write-Host "=== BackendBot Monitor $(Get-Date) ==="
            Get-BackendStatus

            # Additional system info
            $cpu = Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average
            $memory = Get-WmiObject Win32_OperatingSystem
            $freeMemory = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
            $totalMemory = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)

            Write-Host "System CPU: $($cpu.Average)%"
            Write-Host "System Memory: $freeMemory / $totalMemory MB free"

            Start-Sleep -Seconds $Interval
        }
    } catch {
        Write-Host "Monitoring stopped."
    }
}

# Main execution logic
if ($Start) {
    Start-BackendBot
} elseif ($Stop) {
    Stop-BackendBot
} elseif ($Status) {
    Get-BackendStatus
} elseif ($Optimize) {
    Invoke-Optimization
} elseif ($Monitor) {
    Start-Monitoring
} else {
    Write-Host "BackendBot Advanced Automation Script"
    Write-Host "Usage:"
    Write-Host "  .\backend_automation.ps1 -Start [-Background]           # Start BackendBot"
    Write-Host "  .\backend_automation.ps1 -Stop                          # Stop BackendBot"
    Write-Host "  .\backend_automation.ps1 -Status                        # Check status"
    Write-Host "  .\backend_automation.ps1 -Optimize [-Force]             # Run optimizations"
    Write-Host "  .\backend_automation.ps1 -Monitor [-Interval seconds]   # Continuous monitoring"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\backend_automation.ps1 -Start -Background             # Start in background"
    Write-Host "  .\backend_automation.ps1 -Optimize -Force               # Real optimization (dangerous!)"
    Write-Host "  .\backend_automation.ps1 -Monitor -Interval 60          # Monitor every minute"
}