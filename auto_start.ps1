# Auto-start script for BackendBot Activity Monitor
# This script should be added to Windows startup

param(
    [switch]$Install,    # Install as startup task
    [switch]$Uninstall,  # Remove from startup
    [switch]$Test        # Test the monitor without installing
)

$ScriptPath = $PSScriptRoot
$MonitorScript = Join-Path $ScriptPath "activity_monitor.ps1"
$TaskName = "BackendBotActivityMonitor"

function Install-StartupTask {
    Write-Host "Installing BackendBot Activity Monitor..." -ForegroundColor Green

    # Create startup folder entry
    $startupFolder = [Environment]::GetFolderPath("Startup")
    $shortcutPath = Join-Path $startupFolder "BackendBot Monitor.lnk"

    # Remove existing shortcut
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
    }

    # Create WScript Shell object to create shortcut
    $wshell = New-Object -ComObject WScript.Shell
    $shortcut = $wshell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$MonitorScript`""
    $shortcut.WorkingDirectory = $ScriptPath
    $shortcut.Description = "BackendBot Activity Monitor"
    $shortcut.Save()

    Write-Host "Shortcut created in startup folder: $shortcutPath" -ForegroundColor Green
    Write-Host "The monitor will start automatically when you log in." -ForegroundColor Cyan
}

function Uninstall-StartupTask {
    Write-Host "Removing BackendBot Activity Monitor from startup..." -ForegroundColor Yellow

    $startupFolder = [Environment]::GetFolderPath("Startup")
    $shortcutPath = Join-Path $startupFolder "BackendBot Monitor.lnk"

    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Write-Host "Startup shortcut removed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Startup shortcut not found." -ForegroundColor Yellow
    }
}

function Test-Monitor {
    Write-Host "Testing BackendBot Activity Monitor..." -ForegroundColor Cyan
    Write-Host "This will run the monitor for 2 minutes for testing purposes." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop the test." -ForegroundColor Yellow
    Write-Host ""

    # Run monitor with shorter timeouts for testing
    & $MonitorScript -InactivityThresholdMinutes 1 -ResponseTimeoutMinutes 1
}

# Main logic
if ($Install) {
    Install-StartupTask
}
elseif ($Uninstall) {
    Uninstall-StartupTask
}
elseif ($Test) {
    Test-Monitor
}
else {
    Write-Host "BackendBot Auto-Start Manager" -ForegroundColor Cyan
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  .\auto_start.ps1 -Install     # Install as startup task" -ForegroundColor White
    Write-Host "  .\auto_start.ps1 -Uninstall   # Remove from startup" -ForegroundColor White
    Write-Host "  .\auto_start.ps1 -Test        # Test the monitor" -ForegroundColor White
    Write-Host ""
    Write-Host "Current status:" -ForegroundColor Yellow
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "  ✓ Installed as startup task" -ForegroundColor Green
        Write-Host "  State: $($task.State)" -ForegroundColor White
    } else {
        Write-Host "  ✗ Not installed" -ForegroundColor Red
    }
}