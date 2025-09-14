import psutil
from pydantic import BaseModel

class SystemStats(BaseModel):
    cpu_usage: float
    ram_usage_percent: float
    ram_used_gb: float
    ram_total_gb: float

def get_system_stats() -> SystemStats:
    """Obtiene las estadísticas actuales del sistema."""
    cpu_usage = psutil.cpu_percent(interval=0.1)
    
    ram = psutil.virtual_memory()
    ram_usage_percent = ram.percent
    ram_used_gb = round(ram.used / (1024**3), 2)
    ram_total_gb = round(ram.total / (1024**3), 2)
    
    return SystemStats(
        cpu_usage=cpu_usage,
        ram_usage_percent=ram_usage_percent,
        ram_used_gb=ram_used_gb,
        ram_total_gb=ram_total_gb,
    )
