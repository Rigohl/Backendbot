"""Staging automation helpers for BackendBot.

This module contains safe, non-invasive automation helpers that default to dry-run mode.
Do NOT import or execute these functions from production code until tests pass and you
explicitly integrate them.

Functions are designed to return plans/results without performing destructive actions when
`dry_run=True`.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Small contract for functions in this module:
# - Inputs: dry_run: bool, minimal params.
# - Outputs: dict describing actions that WOULD be taken and simple metadata.


@dataclass
class ScheduledTask:
    name: str
    command: str
    schedule: str
    next_run: Optional[datetime] = None


def schedule_optimizations(
    name: str = "staging_opt",
    command: str = "python staging_runner.py",
    schedule: str = "daily",
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Prepare a scheduled task plan. Returns the schedule plan. Does not create the task unless dry_run is False.

    This function intentionally does not call schtasks. Use the returned plan to create the task manually
    or via a controlled deployment step.
    """
    next_run = datetime.now() + timedelta(days=1)
    task = ScheduledTask(
        name=name, command=command, schedule=schedule, next_run=next_run
    )
    plan = {
        "task": task.__dict__,
        "dry_run": dry_run,
        "message": "Task prepared. Set dry_run=False to actually create it using a controlled mechanism.",
    }
    return plan


def list_recommended_powershell_commands() -> List[str]:
    """Return a list of curated PowerShell commands recommended for staging automation.

    These are suggestions only; they are not executed here.
    """
    cmds = [
        # Use Start-Job for background tasks
        "Start-Job -ScriptBlock { <# your script here #> } -Name BackendBot_Staging",
        # Use Register-ScheduledTask for more control (requires full XML or Action/Trigger objects)
        "Register-ScheduledTask -Action (New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-File C:\\path\\to\\script.ps1') -Trigger (New-ScheduledTaskTrigger -Daily -At 3am) -TaskName 'BackendBot_Staging'",
        # Example to run a Python script in background
        "Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoProfile -WindowStyle Hidden -File C:\\path\\to\\start_staging.ps1' -WindowStyle Hidden",
    ]
    return cmds


def prepare_background_command(script_path: str = "scripts\\start_staging.ps1") -> str:
    """Return a PowerShell command string that will start the staging script in background using Start-Process.

    Caller should not execute it directly inside production without review.
    """
    abs_path = os.path.abspath(script_path)
    cmd = f"Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoProfile -WindowStyle Hidden -File \"{abs_path}\"' -WindowStyle Hidden"
    return cmd


def optimize_ram(dry_run: bool = True, max_processes: int = 10) -> Dict[str, Any]:
    """Return a plan for RAM optimization. When dry_run=True this function only simulates what it would do.

    The returned dict contains 'to_terminate' list and estimated freed memory MB.
    """
    # For staging we don't query the real system unless explicitly requested.
    simulated = [
        {"pid": 1234, "name": "notepad.exe", "memory_mb": 50},
        {"pid": 2345, "name": "some_background_worker.exe", "memory_mb": 150},
    ]

    plan = {
        "dry_run": dry_run,
        "candidates": simulated[:max_processes],
        "estimated_freed_mb": sum(p["memory_mb"] for p in simulated[:max_processes]),
        "timestamp": datetime.now().isoformat(),
    }

    if not dry_run:
        # If someone runs with dry_run=False they should be aware this will attempt to terminate processes.
        # We still keep the actual termination logic outside this function to make it easier to test and review.
        plan["executed"] = False
        plan[
            "note"
        ] = "dry_run was False; caller must implement actual termination with careful checks."

    return plan


def perform_disk_cleanup_preview(
    directories: Optional[List[str]] = None, dry_run: bool = True
) -> Dict[str, Any]:
    """Return a preview of files/directories that would be cleaned.

    This function lists candidates and sizes without deleting when dry_run=True.
    """
    if directories is None:
        directories = [os.environ.get("TEMP", r"C:\\Windows\\Temp")]

    preview = []
    for d in directories:
        if not os.path.exists(d):
            preview.append(
                {"path": d, "exists": False, "files_count": 0, "total_bytes": 0}
            )
            continue
        total = 0
        files_count = 0
        for root, _, files in os.walk(d):
            for f in files:
                try:
                    p = os.path.join(root, f)
                    total += os.path.getsize(p)
                    files_count += 1
                except Exception:
                    continue
        preview.append(
            {
                "path": d,
                "exists": True,
                "files_count": files_count,
                "total_bytes": total,
            }
        )

    return {
        "dry_run": dry_run,
        "preview": preview,
        "timestamp": datetime.now().isoformat(),
    }


def write_plan_to_file(
    plan: Dict[str, Any], out_path: str = "data/staging_plan.json"
) -> str:
    """Write a JSON plan to a file and return the absolute path."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, default=str)
    return os.path.abspath(out_path)


# Small CLI-ish helper for manual testing (kept safe)
def run_preview_workflow(out_path: str = "data/staging_plan.json") -> Dict[str, Any]:
    plan = {
        "scheduled": schedule_optimizations(),
        "powershell_cmds": list_recommended_powershell_commands(),
        "ram_preview": optimize_ram(),
        "disk_preview": perform_disk_cleanup_preview(),
    }
    write_plan_to_file(plan, out_path)
    return plan
