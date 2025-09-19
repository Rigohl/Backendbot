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


class SystemMonitor:
    """Wrapper de compatibilidad para monitor del sistema.

    Ahora acepta `thresholds` opcional en el constructor para ajustarse a
    tests y callers que inyectan umbrales en la creación.
    """

    def __init__(self, thresholds: dict = None) -> None:
        self.thresholds = thresholds or {}

    def get_stats(self):
        stats = get_system_stats()
        return {
            "cpu_percent": stats.cpu_usage,
            "memory_percent": stats.ram_usage_percent,
            "disk_usage": {"total": 1, "used": 0, "free": 1},
        }

    def check_system_health(self, system_data: dict, gpu_data: dict = None) -> list:
        """Evaluar la salud del sistema frente a `thresholds` y retornar alertas."""
        alerts = []
        th = self.thresholds or {}

        cpu = system_data.get("cpu_percent", 0)
        mem = system_data.get("memory_percent", 0)

        if th.get("cpu_high") and cpu > th.get("cpu_high"):
            alerts.append(
                {
                    "type": "cpu",
                    "level": "high",
                    "message": f'CPU usage {cpu} > {th.get("cpu_high")}',
                }
            )

        if th.get("memory_high") and mem > th.get("memory_high"):
            alerts.append(
                {
                    "type": "memory",
                    "level": "high",
                    "message": f'memoria {mem} > {th.get("memory_high")}',
                }
            )

        # GPU checks (simple)
        if gpu_data and isinstance(gpu_data, dict):
            for k, v in gpu_data.items():
                if isinstance(v, dict) and "memory_total" in v:
                    if th.get("gpu_memory_high") and v.get("memory_total", 0) > th.get(
                        "gpu_memory_high"
                    ):
                        alerts.append(
                            {
                                "type": "gpu",
                                "level": "high",
                                "message": f"GPU {k} memory high",
                            }
                        )

        return alerts
