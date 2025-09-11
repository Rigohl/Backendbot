import psutil
import sys
from typing import List, Dict, Any

from .staging_automation import optimize_ram
from .utils import log_event

def terminate_processes(process_list: List[Dict[str, Any]], dry_run: bool = True) -> Dict[str, Any]:
    """Terminates processes based on the provided list.

    Args:
        process_list: A list of dictionaries, each containing 'pid' and 'name' of the process.
        dry_run: If True, only simulates termination. If False, actually terminates processes.

    Returns:
        A dictionary with the results of the termination attempt.
    """
    terminated_count = 0
    failed_to_terminate = []
    results = []

    log_event(f"Attempting to {'simulate ' if dry_run else ''}terminate {len(process_list)} processes.")

    for p_info in process_list:
        pid = p_info.get("pid")
        name = p_info.get("name", "Unknown")

        if not pid:
            log_event(f"Skipping process with missing PID: {name}")
            continue

        try:
            process = psutil.Process(pid)
            if dry_run:
                log_event(f"[DRY-RUN] Would terminate process: PID={pid}, Name={name}")
                results.append({"pid": pid, "name": name, "status": "would_terminate"})
                terminated_count += 1
            else:
                log_event(f"Terminating process: PID={pid}, Name={name}")
                process.terminate()  # or process.kill() for a more forceful termination
                process.wait(timeout=3) # Wait for process to terminate
                log_event(f"Successfully terminated process: PID={pid}, Name={name}")
                results.append({"pid": pid, "name": name, "status": "terminated"})
                terminated_count += 1
        except psutil.NoSuchProcess:
            log_event(f"Process not found (already terminated or invalid PID): PID={pid}, Name={name}")
            results.append({"pid": pid, "name": name, "status": "not_found"})
        except psutil.AccessDenied:
            log_event(f"Access denied to terminate process: PID={pid}, Name={name}")
            results.append({"pid": pid, "name": name, "status": "access_denied"})
            failed_to_terminate.append({"pid": pid, "name": name, "reason": "access_denied"})
        except Exception as e:
            log_event(f"Error terminating process: PID={pid}, Name={name}, Error: {e}")
            results.append({"pid": pid, "name": name, "status": "error", "error_message": str(e)})
            failed_to_terminate.append({"pid": pid, "name": name, "reason": str(e)})

    return {
        "dry_run": dry_run,
        "terminated_count": terminated_count,
        "failed_to_terminate": failed_to_terminate,
        "total_attempted": len(process_list),
        "results": results
    }

def run_ram_optimization(dry_run: bool = True) -> Dict[str, Any]:
    """Runs the full RAM optimization workflow.

    Args:
        dry_run: If True, only simulates the optimization. If False, actually terminates processes.

    Returns:
        A dictionary with the optimization plan and termination results.
    """
    log_event(f"Starting RAM optimization workflow (dry_run={dry_run}).")
    
    initial_ram_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
    log_event(f"Initial RAM usage: {initial_ram_usage_mb:.2f} MB")

    # Get the optimization plan (candidates for termination)
    optimization_plan = optimize_ram(dry_run=dry_run) # Pass dry_run to optimize_ram

    if "error" in optimization_plan:
        log_event(f"Error getting RAM optimization plan: {optimization_plan['error']}")
        return {"status": "error", "message": "Failed to get optimization plan", "details": optimization_plan}

    candidates = optimization_plan.get("candidates", [])
    if not candidates:
        log_event("No processes identified for RAM optimization.")
        return {"status": "success", "message": "No processes to optimize", "plan": optimization_plan}

    # Terminate the identified processes
    termination_results = terminate_processes(candidates, dry_run=dry_run)

    final_ram_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
    ram_freed_mb = initial_ram_usage_mb - final_ram_usage_mb

    log_event(f"RAM optimization workflow {'completed' if not dry_run else 'simulated'}. Terminated: {termination_results['terminated_count']}/{termination_results['total_attempted']}")
    log_event(f"Final RAM usage: {final_ram_usage_mb:.2f} MB. RAM freed: {ram_freed_mb:.2f} MB.")

    if not dry_run:
        log_event(f"RAM Optimization Complete: Freed {ram_freed_mb:.2f} MB of RAM by terminating {termination_results['terminated_count']} processes.", notify_user=True)

    return {
        "status": "completed",
        "plan": optimization_plan,
        "termination_results": termination_results,
        "initial_ram_usage_mb": round(initial_ram_usage_mb, 2),
        "final_ram_usage_mb": round(final_ram_usage_mb, 2),
        "ram_freed_mb": round(ram_freed_mb, 2)
    }

if __name__ == "__main__":
    # Example usage from command line
    # python -m src.backendbot.ram_optimizer --dry-run False
    _dry_run = True
    if "--dry-run" in sys.argv:
        try:
            _dry_run = sys.argv[sys.argv.index("--dry-run") + 1].lower() == "false"
        except IndexError:
            print("Usage: python -m src.backendbot.ram_optimizer --dry-run [True|False]")
            sys.exit(1)

    results = run_ram_optimization(dry_run=_dry_run)
    print(results)
