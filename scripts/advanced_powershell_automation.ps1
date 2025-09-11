# PowerShell Advanced Automation Script for BackendBot
# Supports background jobs, parallel execution, and monitoring

param(
    [switch]$RunFullAutomation,
    [switch]$MonitorOnly,
    [switch]$Cleanup,
    [int]$MaxJobs = 3,
    [string]$LogFile = "C:\Users\DELL\Desktop\BackendBot\logs\powershell_automation.log"
)

# Function to log messages
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - $Message"
    Write-Host $logEntry
    Add-Content -Path $LogFile -Value $logEntry
}

# Function to start background job for Python script
function Start-BackgroundJob {
    param([string]$ScriptPath, [string]$JobName)
    $job = Start-Job -ScriptBlock {
        param($path)
        & python $path
    } -ArgumentList $ScriptPath -Name $JobName
    Write-Log "Started background job: $JobName"
    return $job
}

# Function to monitor running jobs
function Get-RunningJobs {
    $runningJobs = Get-Job | Where-Object { $_.State -eq "Running" }
    Write-Log "Monitoring $($runningJobs.Count) running jobs"
    foreach ($job in $runningJobs) {
        Write-Log "Job $($job.Name): $($job.State)"
    }
    return $runningJobs
}

# Function to cleanup completed jobs
function Remove-CompletedJobs {
    $completedJobs = Get-Job | Where-Object { $_.State -eq "Completed" }
    foreach ($job in $completedJobs) {
        Write-Log "Cleaning up job: $($job.Name)"
        Remove-Job $job
    }
}

# Main execution
Write-Log "Starting BackendBot PowerShell Automation"

if ($RunFullAutomation) {
    Write-Log "Running full automation workflow"

    # Start multiple background jobs in parallel
    $jobs = @()

    # Job 1: Run staging preview
    $stagingPath = "C:\Users\DELL\Desktop\BackendBot\src\backendbot\staging_automation.py"
    $jobs += Start-BackgroundJob -ScriptPath $stagingPath -JobName "StagingPreview"

    # Job 2: Run main backend
    $mainPath = "C:\Users\DELL\Desktop\BackendBot\src\backendbot\main.py"
    $jobs += Start-BackgroundJob -ScriptPath $mainPath -JobName "MainBackend"

    # Job 3: Run tests
    $testCommand = "pytest tests/test_staging_automation.py"
    $jobs += Start-Job -ScriptBlock { param($cmd) Invoke-Expression $cmd } -ArgumentList $testCommand -Name "RunTests"

    # Wait for jobs to complete or timeout
    $timeout = 300  # 5 minutes
    $startTime = Get-Date
    while ((Get-Job | Where-Object { $_.State -eq "Running" }).Count -gt 0 -and (Get-Date) - $startTime -lt [TimeSpan]::FromSeconds($timeout)) {
        Start-Sleep -Seconds 10
        Get-RunningJobs
    }

    # Get results
    foreach ($job in $jobs) {
        $result = Receive-Job $job
        Write-Log "Job $($job.Name) result: $result"
    }

    Remove-CompletedJobs
    Write-Log "Full automation completed"
}

if ($MonitorOnly) {
    Write-Log "Monitoring mode activated"
    while ($true) {
        Get-RunningJobs
        Start-Sleep -Seconds 30
    }
}

if ($Cleanup) {
    Write-Log "Cleaning up all jobs"
    Get-Job | Remove-Job -Force
    Write-Log "Cleanup completed"
}

Write-Log "PowerShell automation script finished"