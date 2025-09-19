"""OptimizerBot - Bot para optimización de recursos del sistema, desacoplado de la UI.
Sigue el patrón de bots escalables y testables.
"""

import psutil

from backendbot.core.di.container import container


class OptimizerBot:
    """Bot Optimizer - Optimiza recursos del sistema."""

    def __init__(self) -> None:
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()

    def execute(self, action: str) -> str:
        """Ejecutar acción de optimización."""
        action = action.strip().lower()
        if action == "status":
            return self.get_status()
        elif action == "optimize":
            return self._perform_optimization()
        elif action == "scan":
            return self._scan_processes()
        else:
            return f"Acción '{action}' no reconocida para OptimizerBot"

    def get_status(self) -> str:
        """Obtener estado del bot."""
        return "OptimizerBot operativo y listo para optimizar recursos."

    def is_available(self) -> bool:
        """Verificar si el bot está disponible."""
        return True

    def _perform_optimization(self) -> str:
        """Realizar optimización básica de recursos."""
        try:
            # Ejemplo: cerrar procesos no esenciales (simulado)
            non_essential = ["chrome.exe", "firefox.exe", "spotify.exe", "discord.exe"]
            closed_count = 0
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if proc.name().lower() in non_essential:
                        proc.terminate()
                        closed_count += 1
                except Exception:
                    continue
            msg = f"🔧 Optimización completada. Procesos cerrados: {closed_count}"
            self.logger.info(msg, "OptimizerBot")
            return msg
        except Exception as e:
            error_msg = f"Error en optimización: {str(e)}"
            self.logger.error(error_msg, "OptimizerBot")
            return error_msg

    def _scan_processes(self) -> str:
        """Escanear procesos activos y reportar los más intensivos."""
        try:
            procs = []
            for p in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent"]
            ):
                try:
                    cpu_percent = p.cpu_percent(interval=0.1)
                    memory_percent = p.memory_percent()
                    if cpu_percent > 0 or memory_percent > 0:
                        procs.append((p.pid, p.name(), cpu_percent, memory_percent))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            top_procs = sorted(procs, key=lambda x: x[2] + x[3], reverse=True)[:5]
            if not top_procs:
                return "No hay procesos activos relevantes."
            proc_list = [
                f"{name[:15]} (CPU:{cpu:.1f}%, RAM:{mem:.1f}%)"
                for pid, name, cpu, mem in top_procs
            ]
            msg = "Top procesos: " + " | ".join(proc_list)
            self.logger.info(msg, "OptimizerBot")
            return msg
        except Exception as e:
            error_msg = f"Error escaneando procesos: {str(e)}"
            self.logger.error(error_msg, "OptimizerBot")
            return error_msg
