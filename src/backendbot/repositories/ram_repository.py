import psutil
import subprocess
import json
from typing import List, Dict, Any, Optional

class RamRepository:
    """
    Repository layer for RAM management.
    Encapsulates direct interactions with psutil for RAM-related data and process control.
    """
    def get_system_ram_info(self) -> Dict[str, Any]:
        """Returns overall system RAM usage."""
        mem = psutil.virtual_memory()
        return {
            "total_mb": round(mem.total / (1024 * 1024), 2),
            "available_mb": round(mem.available / (1024 * 1024), 2),
            "percent_used": mem.percent,
            "used_mb": round(mem.used / (1024 * 1024), 2),
            "free_mb": round(mem.free / (1024 * 1024), 2),
        }

    def get_detailed_ram_metrics_powershell(self) -> Optional[Dict[str, Any]]:
        """
        Executes a PowerShell script to get detailed RAM metrics and returns the parsed JSON output.
        """
        script_path = "c:/Users/DELL/Desktop/BackendBot/scripts/get_detailed_ram_metrics.ps1"
        try:
            # Use powershell.exe for Windows compatibility
            command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing PowerShell script: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from PowerShell script output: {e}")
            print(f"Output: {result.stdout}")
            return None
        except FileNotFoundError:
            print(f"PowerShell script not found at: {script_path}")
            return None

    def get_all_processes_ram_info(self) -> List[Dict[str, Any]]:
        """Returns RAM usage for all running processes."""
        processes_info = []
        for p in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                mem_info = p.info['memory_info']
                processes_info.append({
                    "pid": p.info['pid'],
                    "name": p.info['name'],
                    "ram_mb": round(mem_info.rss / (1024 * 1024), 2),
                    "cpu_percent": p.info['cpu_percent'],
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return processes_info

    def get_process_ram_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Returns RAM usage for a specific process by PID."""
        try:
            p = psutil.Process(pid)
            mem_info = p.memory_info()
            return {
                "pid": p.pid,
                "name": p.name(),
                "ram_mb": round(mem_info.rss / (1024 * 1024), 2),
                "cpu_percent": p.cpu_percent(interval=0.1),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None

    def suspend_process(self, pid: int) -> bool:
        """Suspends a process by PID."""
        try:
            p = psutil.Process(pid)
            p.suspend()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

    def resume_process(self, pid: int) -> bool:
        """Resumes a suspended process by PID."""
        try:
            p = psutil.Process(pid)
            p.resume()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

    def kill_process(self, pid: int) -> bool:
        """Terminates a process by PID."""
        try:
            p = psutil.Process(pid)
            p.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

