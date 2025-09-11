Staging automation for BackendBot

This folder contains non-destructive staging helpers and a PowerShell starter for safely testing automation flows.

Files added:
- `src/backendbot/staging_automation.py` - safe helpers, dry-run by default
- `scripts/start_staging.ps1` - PowerShell starter script to preview the workflow
- `tests/test_staging_automation.py` - pytest tests validating behavior

How to run the preview workflow (in PowerShell):

```powershell
# Run the preview (dry-run, will not modify system)
python -c "from src.backendbot.staging_automation import run_preview_workflow; print(run_preview_workflow())"

# Or use the provided script (prints guidance). To actually run the preview:
.
\scripts\start_staging.ps1 -RunNow
```

Notes:
- Everything defaults to dry-run. To make any change you must set dry_run=False and implement the actual destructive steps in a reviewed, tested location.
- PowerShell examples use Start-Process and Start-Job for background execution.
- Tests were added to `tests/test_staging_automation.py` and should pass with pytest.
