# PowerShell starter script for staging automation (non-destructive by default)
param(
    [switch]$RunNow
)

$scriptPath = Join-Path $PSScriptRoot "..\src\backendbot\staging_automation.py"
$python = "python"

if ($RunNow) {
    Write-Output "Running staging preview workflow (dry-run)"
    & $python -c "from src.backendbot.staging_automation import run_preview_workflow; print(run_preview_workflow())"
} else {
    Write-Output "Staging script prepared. Use -RunNow to execute preview workflow."
}

# Example background execution using Start-Job (commented to keep safe)
# Start-Job -ScriptBlock { & python -c "from src.backendbot.staging_automation import run_preview_workflow; print(run_preview_workflow())" } -Name BackendBot_Staging
