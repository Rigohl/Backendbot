"""Staging automation helpers for BackendBot.

This module contains safe, non-invasive automation helpers that default to dry-run mode.
Do NOT import or execute these functions from production code until tests pass and you
explicitly integrate them.

Functions are designed to return plans/results without performing destructive actions when
`dry_run=True`.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import json
import psutil # Moved import to top

try:
    from .config import settings # Moved import to top
except ImportError:
    # Fallback for when running from tests
    from config import settings

# Small contract for functions in this module:
# - Inputs: dry_run: bool, minimal params.
# - Outputs: dict describing actions that WOULD be taken and simple metadata.


@dataclass
class ScheduledTask:
    name: str
    command: str
    schedule: str
    next_run: Optional[datetime] = None


def schedule_optimizations(name: str = "staging_opt", command: str = "python staging_runner.py", schedule: str = "daily", dry_run: bool = True) -> Dict[str, Any]:
    """Prepare a scheduled task plan. Returns the schedule plan. Does not create the task unless dry_run is False.

    This function intentionally does not call schtasks. Use the returned plan to create the task manually
    or via a controlled deployment step.
    """
    next_run = datetime.now() + timedelta(days=1)
    task = ScheduledTask(name=name, command=command, schedule=schedule, next_run=next_run)
    plan = {
        "task": task.__dict__,
        "dry_run": dry_run,
        "message": "Task prepared. Set dry_run=False to actually create it using a controlled mechanism."
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
    cmd = f"Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoProfile -WindowStyle Hidden -File \"{abs_path}\" ' -WindowStyle Hidden"
    return cmd


def optimize_ram(dry_run: bool = True, max_processes: int = 10) -> Dict[str, Any]:
    """Return a plan for RAM optimization. When dry_run=True this function only simulates what it would do.

    The returned dict contains 'to_terminate' list and estimated freed memory MB.
    """
    try:
        # Get real process data when not in dry-run
        if not dry_run:
            processes = []
            important_processes = [p.lower() for p in settings.PROCESOS_IMPORTANTES]
            total_ram_mb = psutil.virtual_memory().total / (1024 * 1024) # Total RAM in MB

            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']): # Changed memory_percent to memory_info for accurate RSS
                try:
                    # Get RSS (Resident Set Size) which is a better indicator of actual RAM usage
                    memory_mb = proc.memory_info().rss / (1024 * 1024) 
                    
                    # Filter based on RAM_THRESHOLD from settings and exclude important processes
                    if memory_mb > settings.RAM_THRESHOLD and proc.info['name'].lower() not in important_processes:
                        processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "memory_mb": round(memory_mb, 2),
                            "memory_percent": round((memory_mb / total_ram_mb) * 100, 2), # Calculate percentage based on RSS
                            "cpu_percent": round(proc.info['cpu_percent'], 2)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage descending
            processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            candidates = processes[:max_processes]
        else:
            # Simulated data for dry-run
            candidates = [
                {"pid": 1234, "name": "notepad.exe", "memory_mb": 50, "memory_percent": 2.1, "cpu_percent": 1.2},
                {"pid": 2345, "name": "some_background_worker.exe", "memory_mb": 150, "memory_percent": 6.3, "cpu_percent": 5.8},
            ]

        plan = {
            "dry_run": dry_run,
            "candidates": candidates,
            "estimated_freed_mb": sum(p["memory_mb"] for p in candidates),
            "total_candidates": len(candidates),
            "timestamp": datetime.now().isoformat(),
        }

        if not dry_run:
            plan["executed"] = False
            plan["note"] = "dry_run was False; caller must implement actual termination with careful checks."

        return plan
    except Exception as e:
        return {
            "error": str(e),
            "dry_run": dry_run,
            "candidates": [],
            "estimated_freed_mb": 0,
            "timestamp": datetime.now().isoformat()
        }


def perform_disk_cleanup_preview(directories: Optional[List[str]] = None, dry_run: bool = True) -> Dict[str, Any]:
    """Return a preview of files/directories that would be cleaned.

    This function lists candidates and sizes without deleting when dry_run=True.
    """
    try:
        if directories is None:
            # Default directories to clean
            directories = [
                os.environ.get("TEMP", r"C:\\Windows\\Temp"),
                os.path.expanduser("~\\AppData\\Local\\Temp"),
                "C:\\Windows\\Prefetch" if os.path.exists("C:\\Windows\\Prefetch") else None
            ]
            directories = [d for d in directories if d and os.path.exists(d)]

        preview = []
        total_files = 0
        total_bytes = 0
        
        for d in directories:
            if not os.path.exists(d):
                preview.append({"path": d, "exists": False, "files_count": 0, "total_bytes": 0, "error": "Directory not found"})
                continue
            
            dir_files = 0
            dir_bytes = 0
            old_files = []
            
            try:
                for root, _, files in os.walk(d):
                    for f in files:
                        try:
                            p = os.path.join(root, f)
                            stat = os.stat(p)
                            file_age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                            
                            # Only consider files older than 7 days and not system critical
                            if file_age_days > 7 and not any(critical in p.lower() for critical in ['system', 'windows', 'program files']):
                                dir_bytes += stat.st_size
                                dir_files += 1
                                if len(old_files) < 20:  # Limit to prevent huge responses
                                    old_files.append({
                                        "path": p,
                                        "size": stat.st_size,
                                        "age_days": file_age_days,
                                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                                    })
                        except Exception:
                            continue
            except Exception as e:
                preview.append({"path": d, "exists": True, "files_count": 0, "total_bytes": 0, "error": str(e)})
                continue
                
            preview.append({
                "path": d, 
                "exists": True, 
                "files_count": dir_files, 
                "total_bytes": dir_bytes,
                "sample_files": old_files
            })
            total_files += dir_files
            total_bytes += dir_bytes

        return {
            "dry_run": dry_run, 
            "preview": preview, 
            "summary": {
                "total_directories": len(preview),
                "total_files": total_files,
                "total_bytes": total_bytes,
                "total_mb": round(total_bytes / (1024 * 1024), 2)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "dry_run": dry_run,
            "preview": [],
            "summary": {"total_directories": 0, "total_files": 0, "total_bytes": 0, "total_mb": 0},
            "timestamp": datetime.now().isoformat()
        }


def write_plan_to_file(plan: Dict[str, Any], out_path: str = "data/staging_plan.json") -> str:
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
