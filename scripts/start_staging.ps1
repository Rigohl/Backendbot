# PowerShell starter script for BackendBot staging automation (safe by default)
param(
    [switch]$RunNow,
    [switch]$Background,
    [string]$Action = "preview",
    [switch]$Force
)

$scriptPath = Join-Path $PSScriptRoot "..\src\backendbot\staging_automation.py"
$python = "python"

# Safety check
if ($Force -and $Action -ne "preview") {
    Write-Warning "Force flag used with action '$Action'. This may perform real system changes."
    $confirmation = Read-Host "Are you sure you want to continue? (yes/no)"
    if ($confirmation -ne "yes") {
        Write-Host "Operation cancelled."
        exit
    }
}

if ($RunNow) {
    Write-Host "Running BackendBot staging automation ($Action mode)..."
    
    switch ($Action) {
        "preview" {
            Write-Host "Executing preview workflow (dry-run)"
            & $python -c "from src.backendbot.staging_automation import run_preview_workflow; import json; result = run_preview_workflow(); print(json.dumps(result, indent=2))"
        }
        "ram-optimize" {
            $dryRun = if ($Force) { "False" } else { "True" }
            Write-Host "RAM optimization (dry_run=$dryRun)"
            & $python -c "from src.backendbot.staging_automation import optimize_ram; import json; result = optimize_ram(dry_run=$dryRun); print(json.dumps(result, indent=2))"
        }
        "disk-cleanup" {
            $dryRun = if ($Force) { "False" } else { "True" }
            Write-Host "Disk cleanup preview (dry_run=$dryRun)"
            & $python -c "from src.backendbot.staging_automation import perform_disk_cleanup_preview; import json; result = perform_disk_cleanup_preview(dry_run=$dryRun); print(json.dumps(result, indent=2))"
        }
        default {
            Write-Host "Unknown action. Available: preview, ram-optimize, disk-cleanup"
        }
    }
} elseif ($Background) {
    Write-Host "Starting staging automation in background..."
    
    # Use Start-Job for background execution
    $job = Start-Job -ScriptBlock {
        param($python, $scriptPath, $action, $force)
        
        switch ($action) {
            "preview" {
                & $python -c "from src.backendbot.staging_automation import run_preview_workflow; result = run_preview_workflow(); print('Preview completed')"
            }
            "ram-optimize" {
                $dryRun = if ($force) { "False" } else { "True" }
                & $python -c "from src.backendbot.staging_automation import optimize_ram; result = optimize_ram(dry_run=$dryRun); print('RAM optimization completed')"
            }
            "disk-cleanup" {
                $dryRun = if ($force) { "False" } else { "True" }
                & $python -c "from src.backendbot.staging_automation import perform_disk_cleanup_preview; result = perform_disk_cleanup_preview(dry_run=$dryRun); print('Disk cleanup preview completed')"
            }
        }
    } -ArgumentList $python, $scriptPath, $Action, $Force
    
    Write-Host "Job started with ID: $($job.Id)"
    Write-Host "Use 'Get-Job -Id $($job.Id)' to check status"
    Write-Host "Use 'Receive-Job -Id $($job.Id)' to get results"
} else {
    Write-Host "BackendBot Staging Automation Script"
    Write-Host "Usage:"
    Write-Host "  .\start_staging.ps1 -RunNow -Action preview                    # Run preview (safe)"
    Write-Host "  .\start_staging.ps1 -RunNow -Action ram-optimize              # RAM optimization preview"
    Write-Host "  .\start_staging.ps1 -RunNow -Action disk-cleanup              # Disk cleanup preview"
    Write-Host "  .\start_staging.ps1 -RunNow -Action ram-optimize -Force      # REAL RAM optimization (dangerous!)"
    Write-Host "  .\start_staging.ps1 -Background -Action preview               # Run in background"
    Write-Host ""
    Write-Host "Available actions: preview, ram-optimize, disk-cleanup"
    Write-Host "Add -Force to perform real actions (use with caution!)"
}