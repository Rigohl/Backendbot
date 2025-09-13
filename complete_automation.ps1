# BackendBot Complete Automation with Activity Monitoring
# Integrates all automation features including activity monitoring

param(
    [switch]$Start,
    [switch]$Stop,
    [switch]$Monitor,
    [switch]$Test,
    [switch]$Deploy,
    [switch]$Optimize,
    [int]$InactivityThresholdMinutes = 5,
    [int]$ResponseTimeoutMinutes = 3,
    [switch]$Background
)

# Configuration
$ScriptName = "BackendBot Complete Automation"
$ProjectRoot = $PSScriptRoot
$LogFile = Join-Path $ProjectRoot "logs\complete_automation.log"

# Import required modules
$activityMonitorPath = Join-Path $ProjectRoot "activity_monitor.ps1"
$backendAutomationPath = Join-Path $ProjectRoot "backendbot_auto.ps1"

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

# Function to check system requirements
function Test-SystemRequirements {
    Write-Log "Checking system requirements..."

    $requirements = @(
        @{ Name = "Python"; Command = "python --version"; Required = $true },
        @{ Name = "PowerShell Version"; Command = "$PSVersionTable.PSVersion"; Required = $true },
        @{ Name = "Backend Files"; Command = "Test-Path 'src\backendbot\main.py'"; Required = $true },
        @{ Name = "Activity Monitor"; Command = "Test-Path 'activity_monitor.ps1'"; Required = $true }
    )

    $allMet = $true
    foreach ($req in $requirements) {
        try {
            $result = Invoke-Expression $req.Command
            if ($result) {
                Write-Log "✓ $($req.Name): OK" "INFO"
            }
            else {
                Write-Log "✗ $($req.Name): Failed" "ERROR"
                if ($req.Required) { $allMet = $false }
            }
        }
        catch {
            Write-Log "✗ $($req.Name): Error - $($_.Exception.Message)" "ERROR"
            if ($req.Required) { $allMet = $false }
        }
    }

    return $allMet
}

# Function to start complete system
function Start-CompleteSystem {
    Write-Log "Starting BackendBot Complete System..."

    # 1. Check requirements
    if (-not (Test-SystemRequirements)) {
        Write-Log "System requirements not met. Aborting startup." "ERROR"
        return $false
    }

    # 2. Start backend
    Write-Log "Starting backend..."
    & $activityMonitorPath -Start

    # 3. Start activity monitoring
    Write-Log "Starting activity monitoring..."
    if ($Background) {
        $monitorJob = Start-Job -ScriptBlock {
            param($monitorPath, $threshold, $timeout)
            & $monitorPath -Monitor -InactivityThresholdMinutes $threshold -ResponseTimeoutMinutes $timeout
        } -ArgumentList $activityMonitorPath, $InactivityThresholdMinutes, $ResponseTimeoutMinutes -Name "ActivityMonitor"

        Write-Log "Activity monitor started in background (Job ID: $($monitorJob.Id))"
        return $monitorJob
    }
    else {
        Write-Log "Starting activity monitor in foreground..."
        & $activityMonitorPath -Monitor -InactivityThresholdMinutes $InactivityThresholdMinutes -ResponseTimeoutMinutes $ResponseTimeoutMinutes
    }

    return $true
}

# Function to stop complete system
function Stop-CompleteSystem {
    Write-Log "Stopping BackendBot Complete System..."

    # Stop activity monitor job if running
    $monitorJob = Get-Job -Name "ActivityMonitor" -ErrorAction SilentlyContinue
    if ($monitorJob) {
        Write-Log "Stopping activity monitor job..."
        Stop-Job -Id $monitorJob.Id
        Remove-Job -Id $monitorJob.Id
    }

    # Stop backend
    Write-Log "Stopping backend..."
    & $activityMonitorPath -Stop

    Write-Log "Complete system stopped"
    return $true
}

# Function to run tests
function Invoke-SystemTests {
    Write-Log "Running BackendBot system tests..."

    # Run activity monitor tests
    Write-Log "Testing activity monitor..."
    & ".\test_activity_monitor.ps1" -QuickTest

    # Run backend automation tests
    if (Test-Path $backendAutomationPath) {
        Write-Log "Testing backend automation..."
        & $backendAutomationPath -Test
    }

    Write-Log "System tests completed"
}

# Function to optimize system
function Optimize-System {
    Write-Log "Optimizing BackendBot system..."

    # Run PowerShell optimization
    Write-Log "Optimizing PowerShell configuration..."
    & $backendAutomationPath -Optimize

    # Clean logs
    Write-Log "Cleaning old log files..."
    $oldLogs = Get-ChildItem "logs\*.log" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
    foreach ($log in $oldLogs) {
        Remove-Item $log.FullName
        Write-Log "Removed old log: $($log.Name)"
    }

    Write-Log "System optimization completed"
}

# Function to show system status
function Show-SystemStatus {
    Write-Log "=== BackendBot System Status ==="

    # Backend status
    $backendRunning = & $activityMonitorPath -Status
    Write-Log "Backend Status: $(if ($backendRunning) { 'Running' } else { 'Stopped' })"

    # Activity monitor status
    $monitorJob = Get-Job -Name "ActivityMonitor" -ErrorAction SilentlyContinue
    if ($monitorJob) {
        Write-Log "Activity Monitor: Running (Job ID: $($monitorJob.Id), State: $($monitorJob.State))"
    }
    else {
        Write-Log "Activity Monitor: Not running"
    }

    # System resources
    $cpu = Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average
    $memory = Get-WmiObject Win32_OperatingSystem
    $freeMemoryGB = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
    $totalMemoryGB = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)

    Write-Log "CPU Usage: $($cpu.Average)%"
    Write-Log "Memory: ${freeMemoryGB}GB free of ${totalMemoryGB}GB"

    # Recent logs
    Write-Log "Recent Log Entries:"
    try {
        $recentLogs = Get-Content $LogFile -Tail 5 -ErrorAction SilentlyContinue
        foreach ($log in $recentLogs) {
            Write-Log "  $log"
        }
    }
    catch {
        Write-Log "  No recent logs available"
    }

    Write-Log "============================"
}

# Main execution logic
Write-Log "=== $ScriptName ==="

try {
    if ($Start) {
        Write-Log "Command: Start Complete System"
        $result = Start-CompleteSystem
        if ($result) {
            Write-Log "Complete system started successfully"
        }
        else {
            Write-Log "Failed to start complete system" "ERROR"
            exit 1
        }
    }
    elseif ($Stop) {
        Write-Log "Command: Stop Complete System"
        if (Stop-CompleteSystem) {
            Write-Log "Complete system stopped successfully"
        }
        else {
            Write-Log "Failed to stop complete system" "ERROR"
            exit 1
        }
    }
    elseif ($Monitor) {
        Write-Log "Command: Start Monitoring Only"
        & $activityMonitorPath -Monitor -InactivityThresholdMinutes $InactivityThresholdMinutes -ResponseTimeoutMinutes $ResponseTimeoutMinutes
    }
    elseif ($Test) {
        Write-Log "Command: Run System Tests"
        Invoke-SystemTests
    }
    elseif ($Deploy) {
        Write-Log "Command: Deploy System"
        Write-Log "Deployment functionality not yet implemented" "WARN"
    }
    elseif ($Optimize) {
        Write-Log "Command: Optimize System"
        Optimize-System
    }
    else {
        Write-Log "Command: Show Status"
        Show-SystemStatus
    }

}
catch {
    Write-Log "Error executing command: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "DEBUG"
    exit 1
}
finally {
    Write-Log "Command execution completed"
}

# Usage information
if (-not ($Start -or $Stop -or $Monitor -or $Test -or $Deploy -or $Optimize)) {
    Write-Host ""
    Write-Host "Usage: $PSCommandPath [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "  -Start                Start complete system (backend + monitoring)" -ForegroundColor Gray
    Write-Host "  -Stop                 Stop complete system" -ForegroundColor Gray
    Write-Host "  -Monitor              Start activity monitoring only" -ForegroundColor Gray
    Write-Host "  -Test                 Run system tests" -ForegroundColor Gray
    Write-Host "  -Deploy               Deploy system (not implemented)" -ForegroundColor Gray
    Write-Host "  -Optimize             Optimize system performance" -ForegroundColor Gray
    Write-Host "  -Background           Run monitoring in background job" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor White
    Write-Host "  -InactivityThresholdMinutes  Minutes before warning (default: 5)" -ForegroundColor Gray
    Write-Host "  -ResponseTimeoutMinutes      Minutes to wait for response (default: 3)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  $PSCommandPath -Start -Background" -ForegroundColor Gray
    Write-Host "  $PSCommandPath -Monitor -InactivityThresholdMinutes 10" -ForegroundColor Gray
    Write-Host "  $PSCommandPath -Test" -ForegroundColor Gray
}