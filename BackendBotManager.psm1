# BackendBotManager.psm1
# Centralized PowerShell Module for BackendBot Management

function Write-BackendBotLog {
    param(
        [string]$Message,
        [string]$LogFile = "C:\Users\DELL\Desktop\BackendBot\logs\backendbot_manager.log"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - $Message"
    Write-Host $logEntry
    Add-Content -Path $LogFile -Value $logEntry -ErrorAction SilentlyContinue
}

function Get-BackendBotProcess {
    Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*BackendBot\main.py*" -or $_.CommandLine -like "*BackendBot\backend.py*"
    }
}

function Start-BackendBot {
    param(
        [switch]$Background = $true
    )
    if ((Get-BackendBotProcess).Count -gt 0) {
        Write-BackendBotLog "BackendBot is already running."
        return
    }

    Write-BackendBotLog "Starting BackendBot..."
    $backendPath = "C:\Users\DELL\Desktop\BackendBot\src\backendbot\main.py"
    if ($Background) {
        Start-Process -FilePath "python" -ArgumentList $backendPath -WindowStyle Hidden -PassThru | Out-Null
        Start-Sleep -Seconds 2
        if ((Get-BackendBotProcess).Count -gt 0) {
            Write-BackendBotLog "BackendBot started successfully in background."
        } else {
            Write-BackendBotLog "Failed to start BackendBot." -LogFile "C:\Users\DELL\Desktop\BackendBot\logs\backendbot_manager_errors.log"
        }
    } else {
        & python $backendPath
    }
}

function Stop-BackendBot {
    $processes = Get-BackendBotProcess
    if ($processes.Count -eq 0) {
        Write-BackendBotLog "No BackendBot processes found."
        return
    }

    Write-BackendBotLog "Stopping BackendBot processes..."
    $processes | ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-BackendBotLog "Stopped process ID: $($_.Id)"
    }
}

function Get-BackendBotStatus {
    $processes = Get-BackendBotProcess
    if ($processes.Count -gt 0) {
        Write-BackendBotLog "BackendBot Status: RUNNING"
        $processes | ForEach-Object {
            Write-BackendBotLog "  Process ID: $($_.Id)"
            Write-BackendBotLog "  CPU Usage: $($_.CPU.ToString("F2"))%"
            Write-BackendBotLog "  Memory Usage: $([math]::Round($_.WorkingSet / 1MB, 2)) MB"
            Write-BackendBotLog "  Start Time: $($_.StartTime)"
        }
    } else {
        Write-BackendBotLog "BackendBot Status: STOPPED"
    }

    # Check API health
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-BackendBotLog "API Status: RESPONDING (http://localhost:8000/health)"
        } else {
            Write-BackendBotLog "API Status: NOT RESPONDING (http://localhost:8000/health) - Status Code: $($response.StatusCode)" -LogFile "C:\Users\DELL\Desktop\BackendBot\logs\backendbot_manager_errors.log"
        }
    } catch {
        Write-BackendBotLog "API Status: NOT RESPONDING (http://localhost:8000/health) - Error: $($_.Exception.Message)" -LogFile "C:\Users\DELL\Desktop\BackendBot\logs\backendbot_manager_errors.log"
    }
}

function Invoke-BackendBotTask {
    param(
        [string]$TaskName,
        [string]$ScriptPath,
        [string[]]$Arguments = @(),
        [switch]$Wait = $false
    )
    Write-BackendBotLog "Invoking task: $TaskName"
    $jobName = "BackendBotTask-$TaskName-$(Get-Random)"
    $scriptBlock = {
        param($path, $args)
        & python $path @args
    }

    $job = Start-Job -ScriptBlock $scriptBlock -ArgumentList $ScriptPath, $Arguments -Name $jobName

    if ($Wait) {
        Wait-Job $job | Out-Null
        $result = Receive-Job $job
        Write-BackendBotLog "Task '$TaskName' completed. Result: $($result | Out-String)"
        Remove-Job $job
    } else {
        Write-BackendBotLog "Task '$TaskName' started in background (Job ID: $($job.Id))."
    }
    return $job
}

function Invoke-BackendBotRamOptimization {
    param(
        [switch]$DryRun = $true
    )
    Write-BackendBotLog "Initiating RAM optimization (DryRun=$DryRun)..."
    $scriptPath = "C:\Users\DELL\Desktop\BackendBot\src\backendbot\ram_optimizer.py"
    $arguments = @("--dry-run", "$DryRun")
    Invoke-BackendBotTask -TaskName "RAM_Optimization" -ScriptPath $scriptPath -Arguments $arguments -Wait $true
}

Export-ModuleMember -Function *
