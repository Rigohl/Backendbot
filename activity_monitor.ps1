# BackendBot Activity Monitor - Enhanced Version
# Detects user activity and controls backend startup/shutdown with advanced features

param(
    [int]$InactivityThresholdMinutes = 5,  # Time before showing inactivity warning
    [int]$ResponseTimeoutMinutes = 3,      # Time to wait for user response
    [string]$BackendPath = "src\backendbot\main.py",
    [string]$PythonPath = "python",
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Monitor,
    [switch]$InstallService,
    [switch]$UninstallService,
    [string]$LogFile = "logs\activity_monitor.log"
)

# Configuration
$ScriptName = "BackendBot Activity Monitor"
$ServiceName = "BackendBotActivityMonitor"
$ServiceDisplayName = "BackendBot Activity Monitor Service"

# Add Windows API types for activity detection
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class UserActivity {
    [DllImport("user32.dll")]
    public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);

    [StructLayout(LayoutKind.Sequential)]
    public struct LASTINPUTINFO {
        public uint cbSize;
        public uint dwTime;
    }

    public static TimeSpan GetIdleTime() {
        LASTINPUTINFO lastInput = new LASTINPUTINFO();
        lastInput.cbSize = (uint)Marshal.SizeOf(lastInput);
        GetLastInputInfo(ref lastInput);

        uint tickCount = (uint)Environment.TickCount;
        uint idleTime = tickCount - lastInput.dwTime;

        return TimeSpan.FromMilliseconds(idleTime);
    }
}
"@

# Function to write to log
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "$Timestamp [$Level] - $Message"

    # Write to console with color
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor Red }
        "WARN" { Write-Host $LogMessage -ForegroundColor Yellow }
        "INFO" { Write-Host $LogMessage -ForegroundColor Green }
        "DEBUG" { Write-Host $LogMessage -ForegroundColor Gray }
        default { Write-Host $LogMessage }
    }

    # Write to file
    try {
        Add-Content -Path $LogFile -Value $LogMessage -ErrorAction SilentlyContinue
    }
    catch {
        Write-Host "Error writing to log file: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to get idle time in minutes with multiple detection methods
function Get-IdleTimeMinutes {
    try {
        # Method 1: Windows API (most accurate)
        $idleTime = [UserActivity]::GetIdleTime()
        return $idleTime.TotalMinutes
    }
    catch {
        Write-Log "Windows API method failed, trying alternative methods" "WARN"

        try {
            # Method 2: Check for active processes
            $activeProcesses = Get-Process | Where-Object {
                $_.CPU -gt 0 -and $_.ProcessName -notmatch "(idle|system|svchost)"
            } | Measure-Object

            if ($activeProcesses.Count -gt 0) {
                return 0  # Assume activity if processes are using CPU
            }
        }
        catch {
            Write-Log "Alternative method failed: $($_.Exception.Message)" "ERROR"
        }

        return 0  # Default to active if detection fails
    }
}

# Function to check if backend is running
function Test-BackendRunning {
    try {
        $backendProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like "*main.py*"
        }
        return $backendProcesses.Count -gt 0
    }
    catch {
        Write-Log "Error checking backend status: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Function to start backend process
function Start-BackendProcess {
    if (Test-BackendRunning) {
        Write-Log "Backend is already running"
        return $null
    }

    Write-Log "Starting BackendBot..."
    try {
        $backendJob = Start-Job -ScriptBlock {
            param($pythonPath, $backendPath, $workingDir)
            Set-Location $workingDir
            & $pythonPath $backendPath
        } -ArgumentList $PythonPath, $BackendPath, $PWD

        # Wait a moment and verify
        Start-Sleep -Seconds 3

        if (Test-BackendRunning) {
            Write-Log "BackendBot started successfully"
            return $backendJob
        }
        else {
            Write-Log "Failed to start BackendBot" "ERROR"
            return $null
        }
    }
    catch {
        Write-Log "Error starting BackendBot: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

# Function to stop backend process
function Stop-BackendProcess {
    Write-Log "Stopping BackendBot..."
    try {
        $backendProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like "*main.py*"
        }

        $stopped = $false
        foreach ($process in $backendProcesses) {
            Stop-Process -Id $process.Id -Force
            Write-Log "Stopped BackendBot process (PID: $($process.Id))"
            $stopped = $true
        }

        if (-not $stopped) {
            Write-Log "No BackendBot processes found to stop"
        }

        return $stopped
    }
    catch {
        Write-Log "Error stopping BackendBot: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Function to show inactivity notification with better UX
function Show-InactivityNotification {
    param([int]$TimeoutMinutes)

    Write-Log "Showing inactivity notification (timeout: $TimeoutMinutes minutes)"

    try {
        # Try Windows notification first
        Add-Type -AssemblyName System.Windows.Forms
        $notification = New-Object System.Windows.Forms.NotifyIcon
        $notification.Icon = [System.Drawing.SystemIcons]::Warning
        $notification.BalloonTipTitle = "BackendBot - Inactividad Detectada"
        $notification.BalloonTipText = "¿Sigues ahí? El sistema se apagará en $TimeoutMinutes minutos si no hay respuesta."
        $notification.Visible = $true
        $notification.ShowBalloonTip(10000)

        # Wait for user response or timeout
        $startTime = Get-Date
        while ((Get-Date) - $startTime).TotalSeconds -lt 60) {
        # Check for user activity
        if (Get-IdleTimeMinutes -lt 1) {
            $notification.Dispose()
            Write-Log "User responded via activity"
            return $true
        }
        Start-Sleep -Seconds 1
    }

    $notification.Dispose()
    return $false
}
catch {
    Write-Log "Windows notification failed, using popup: $($_.Exception.Message)" "WARN"

    # Fallback to popup
    try {
        $wshell = New-Object -ComObject Wscript.Shell
        $result = $wshell.Popup(
            "El backend se detendrá en $TimeoutMinutes minutos debido a inactividad.`n`n¿Desea mantenerlo activo?",
            60,
            "BackendBot - Inactividad Detectada",
            4 + 32
        )
        return $result -eq 6
    }
    catch {
        Write-Log "Popup notification failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}
}

# Function to start backend (legacy - replaced by Start-BackendProcess)
function Start-BackendProcess {
    if (-not (Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" })) {
        Write-Host "Starting backend..." -ForegroundColor Green
        $backendJob = Start-Job -ScriptBlock {
            param($pythonPath, $backendPath)
            Set-Location $using:PWD
            & $pythonPath $backendPath
        } -ArgumentList $PythonPath, $BackendPath

        return $backendJob
    }
    return $null
}

# Function to stop backend
function Stop-BackendProcess {
    $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    if ($pythonProcesses) {
        Write-Host "Stopping backend..." -ForegroundColor Yellow
        $pythonProcesses | Stop-Process -Force
        return $true
    }
    return $false
}

# Main monitoring loop
function Start-ActivityMonitor {
    Write-Host "Starting BackendBot Activity Monitor..." -ForegroundColor Cyan
    Write-Host "Inactivity threshold: $InactivityThresholdMinutes minutes" -ForegroundColor Cyan
    Write-Host "Response timeout: $ResponseTimeoutMinutes minutes" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Cyan
    Write-Host ""

    $backendJob = $null
    $lastActivityCheck = $null  # Will be set when activity is detected
    $warningShown = $false

    while ($true) {
        $idleMinutes = Get-IdleTimeMinutes
        $currentTime = Get-Date

        # Check if user is active
        if ($idleMinutes -lt $InactivityThresholdMinutes) {
            # User is active
            if ($warningShown) {
                Write-Host "$(Get-Date -Format 'HH:mm:ss') - User activity detected, canceling shutdown" -ForegroundColor Green
                $warningShown = $false
            }

            # Start backend if not running
            if (-not $backendJob -or $backendJob.State -ne "Running") {
                $backendJob = Start-BackendProcess
            }

            $lastActivityCheck = $currentTime
        }
        else {
            # User is inactive
            if (-not $warningShown) {
                Write-Host "$(Get-Date -Format 'HH:mm:ss') - Inactivity detected ($([math]::Round($idleMinutes, 1)) minutes)" -ForegroundColor Yellow
                $warningShown = $true
                $warningTime = $currentTime
            }

            # Check if warning timeout has passed
            $timeSinceWarning = ($currentTime - $warningTime).TotalMinutes
            if ($timeSinceWarning -ge $ResponseTimeoutMinutes) {
                Write-Host "$(Get-Date -Format 'HH:mm:ss') - No response received, stopping backend" -ForegroundColor Red
                Stop-BackendProcess
                $warningShown = $false

                # Wait for activity before checking again
                Write-Host "$(Get-Date -Format 'HH:mm:ss') - Waiting for user activity..." -ForegroundColor Gray
                do {
                    Start-Sleep -Seconds 30
                    $idleMinutes = Get-IdleTimeMinutes
                } while ($idleMinutes -ge $InactivityThresholdMinutes)

                Write-Host "$(Get-Date -Format 'HH:mm:ss') - User activity detected, resuming monitoring" -ForegroundColor Green
            }
            elseif ($timeSinceWarning -ge 1) {
                # Show notification every minute during warning period
                $remainingMinutes = [math]::Ceiling($ResponseTimeoutMinutes - $timeSinceWarning)
                if (([math]::Floor($timeSinceWarning) % 1) -eq 0) {
                    $userResponse = Show-InactivityNotification -TimeoutMinutes $remainingMinutes
                    if ($userResponse) {
                        Write-Host "$(Get-Date -Format 'HH:mm:ss') - User responded: Keep backend active" -ForegroundColor Green
                        $warningShown = $false
                        $lastActivityCheck = $currentTime
                    }
                }
            }
        }

        # Check backend status
        if ($backendJob -and $backendJob.State -eq "Completed") {
            Write-Host "$(Get-Date -Format 'HH:mm:ss') - Backend job completed" -ForegroundColor Yellow
            $backendJob = $null
        }

        Start-Sleep -Seconds 30  # Check every 30 seconds
    }
}

# Handle Ctrl+C gracefully
try {
    Start-ActivityMonitor
}
catch {
    Write-Host "`nStopping activity monitor..." -ForegroundColor Yellow
    if ($backendJob) {
        Stop-BackendProcess
        $backendJob | Stop-Job -ErrorAction SilentlyContinue
        $backendJob | Remove-Job -ErrorAction SilentlyContinue
    }
}
finally {
    Write-Host "Activity monitor stopped." -ForegroundColor Cyan
}