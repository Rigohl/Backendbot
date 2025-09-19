"""
Bot Monitor - Monitorea recursos del sistema
"""

import psutil
from backendbot.core.di.container import container


class MonitorBot:
    """Bot Monitor - Monitorea recursos del sistema"""

    def __init__(self):
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()

    def execute(self, action: str) -> str:
        """Ejecutar acción del monitor"""
        if action == "status":
            # Obtener stats básicos del sistema
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            return f"📊 CPU: {cpu}%, RAM: {ram.percent}%"
        elif action == "start":
            return "Monitor iniciado"
        else:
            return f"Acción '{action}' no reconocida para Monitor"

    def get_status(self) -> str:
        """Obtener estado del bot"""
        return "Monitor operativo"

    def is_available(self) -> bool:
        """Verificar si el bot está disponible"""
        return True