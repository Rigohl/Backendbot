from typing import List, Dict, Any, Optional

from ..repositories.ram_repository import RamRepository
from ..config import settings
from ..utils import log_event, store_optimization_event # Will move _optimize_processes here later
from ..exceptions import ResourceNotFoundException, BadRequestException, InternalServerErrorException

class RamService:
    """
    Service layer for RAM management and control.
    Provides business logic for optimizing RAM, getting process info, and controlling processes.
    """
    def __init__(self, repository: RamRepository):
        self.repository = repository

    def get_system_ram_info(self) -> Dict[str, Any]:
        """Retrieves overall system RAM usage from the repository."""
        return self.repository.get_system_ram_info()

    def get_detailed_ram_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves detailed RAM metrics using the PowerShell script from the repository.
        """
        return self.repository.get_detailed_ram_metrics_powershell()

    def check_ram_thresholds(self) -> None:
        """
        Checks current RAM usage against defined thresholds and logs alerts.
        """
        detailed_metrics = self.get_detailed_ram_metrics()
        if detailed_metrics:
            used_memory_gb = detailed_metrics.get("UsedMemoryGB", 0)
            total_memory_gb = detailed_metrics.get("TotalMemoryGB", 1) # Avoid division by zero
            
            if total_memory_gb > 0:
                percent_used = (used_memory_gb / total_memory_gb) * 100
                log_event(f"Uso de RAM actual: {percent_used:.2f}% ({used_memory_gb:.2f} GB / {total_memory_gb:.2f} GB)")

                if percent_used >= settings.RAM_CRITICAL_THRESHOLD_PERCENT:
                    log_event(f"ALERTA CRÍTICA DE RAM: Uso de RAM ({percent_used:.2f}%) ha superado el umbral crítico ({settings.RAM_CRITICAL_THRESHOLD_PERCENT}%).", level="CRITICAL")
                    # TODO: Add more advanced notification mechanisms here (e.g., email, push notification)
                elif percent_used >= settings.RAM_WARNING_THRESHOLD_PERCENT:
                    log_event(f"ADVERTENCIA DE RAM: Uso de RAM ({percent_used:.2f}%) ha superado el umbral de advertencia ({settings.RAM_WARNING_THRESHOLD_PERCENT}%).", level="WARNING")
                    # TODO: Consider triggering a soft optimization or detailed logging here

    def get_all_processes_ram_info(self) -> List[Dict[str, Any]]:
        """Retrieves RAM usage for all running processes from the repository."""
        return self.repository.get_all_processes_ram_info()

    def get_process_ram_info(self, pid: int) -> Dict[str, Any]:
        """Retrieves RAM usage for a specific process by PID."""
        info = self.repository.get_process_ram_info(pid)
        if not info:
            raise ResourceNotFoundException(detail=f"Process with PID {pid} not found.")
        return info

    async def optimize_ram_now(self) -> Dict[str, Any]:
        """
        Optimizes RAM by suspending hibernatable processes.
        Returns the amount of RAM freed.
        """
        freed = 0
        for p_info in self.repository.get_all_processes_ram_info():
            if p_info['name'] in settings.HIBERNABLES:
                try:
                    if self.repository.suspend_process(p_info['pid']):
                        freed += p_info['ram_mb'] # Approximate freed RAM
                        log_event(f"Proceso suspendido: {p_info['name']} (PID {p_info['pid']})")
                except Exception as e:
                    log_event(f"Error al suspender {p_info['name']} (PID {p_info['pid']}): {e}")
        
        if freed > 0:
            await store_optimization_event(freed) # Store event in DB
            log_event(f"RAM optimizada. Se liberaron aproximadamente {freed:.2f} MB.")
        
        return {"status": "success", "freed_ram_mb": freed}

    def suspend_process(self, pid: int) -> Dict[str, Any]:
        """Suspends a process by PID."""
        if self.repository.suspend_process(pid):
            log_event(f"Proceso suspendido: PID {pid}")
            return {"status": "success", "message": f"Process {pid} suspended."}
        raise BadRequestException(detail=f"Could not suspend process {pid}. It might not exist or access denied.")

    def resume_process(self, pid: int) -> Dict[str, Any]:
        """Resumes a suspended process by PID."""
        if self.repository.resume_process(pid):
            log_event(f"Proceso reanudado: PID {pid}")
            return {"status": "success", "message": f"Process {pid} resumed."}
        raise BadRequestException(detail=f"Could not resume process {pid}. It might not exist or access denied.")

    def kill_process(self, pid: int) -> Dict[str, Any]:
        """Terminates a process by PID."""
        if self.repository.kill_process(pid):
            log_event(f"Proceso terminado: PID {pid}")
            return {"status": "success", "message": f"Process {pid} terminated."}
        raise BadRequestException(detail=f"Could not terminate process {pid}. It might not exist or access denied.")
