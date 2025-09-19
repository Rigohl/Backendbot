"""Bot Monitor - Monitorea recursos del sistema."""

import psutil

from backendbot.core.di.container import container
from backendbot.core.bot_base import BaseBot


class MonitorBot(BaseBot):
    """Bot Monitor - Monitorea recursos del sistema."""

    def __init__(self) -> None:
        super().__init__(name="monitor")
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()

    def execute(self, action: str) -> str:
        """Ejecutar acción del monitor."""
        if action == "status":
            # Obtener stats básicos del sistema
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            result = f"📊 Estado del Sistema:\nCPU: {cpu}%\nRAM: {ram.percent}%\nDisco: {disk.percent}%"
            try:
                self.record_result("status", {"cpu": cpu, "ram": ram.percent, "disk": disk.percent})
            except Exception:
                pass
            return result

        elif action == "monitor":
            return self._monitor_system()

        elif action == "processes":
            return self._get_processes()

        elif action == "network":
            return self._get_network_info()

        elif action == "alerts":
            return self._check_alerts()

        elif action == "start":
            return "Monitor iniciado"

        else:
            return f"Acción '{action}' no reconocida. Usa: status, monitor, processes, network, alerts"

    def get_status(self) -> str:
        """Obtener estado del bot."""
        return "Monitor operativo"

    def is_available(self) -> bool:
        """Verificar si el bot está disponible."""
        return True

    def _monitor_system(self) -> str:
        """Monitorear sistema completo."""
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        network = psutil.net_io_counters()

        return f"""📊 Monitoreo del Sistema:

CPU: {cpu:.1f}%
RAM: {ram.percent:.1f}% ({ram.used/1024/1024/1024:.1f}GB usado)
Disco: {disk.percent:.1f}% ({disk.used/1024/1024/1024:.1f}GB usado)
Red: ↑{network.bytes_sent/1024/1024:.1f}MB ↓{network.bytes_recv/1024/1024:.1f}MB
"""

    def _get_processes(self) -> str:
        """Obtener procesos principales."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['cpu_percent'] > 1 or proc.info['memory_percent'] > 1:
                    processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        top_processes = processes[:10]

        result = "🔥 Procesos principales:\n"
        for proc in top_processes:
            result += f"• {proc['name']}: CPU {proc['cpu_percent']:.1f}%, RAM {proc['memory_percent']:.1f}%\n"

        return result

    def _get_network_info(self) -> str:
        """Obtener información de red."""
        network = psutil.net_io_counters()
        return f"""🌐 Información de Red:
Enviado: {network.bytes_sent/1024/1024:.1f} MB
Recibido: {network.bytes_recv/1024/1024:.1f} MB
Paquetes enviados: {network.packets_sent}
Paquetes recibidos: {network.packets_recv}
"""

    def _check_alerts(self) -> str:
        """Verificar alertas del sistema."""
        alerts = []

        # Verificar RAM alta
        ram = psutil.virtual_memory()
        if ram.percent > 80:
            alerts.append(f"⚠️ RAM alta: {ram.percent}%")

        # Verificar CPU alta
        cpu = psutil.cpu_percent()
        if cpu > 80:
            alerts.append(f"⚠️ CPU alta: {cpu}%")

        # Verificar disco lleno
        disk = psutil.disk_usage("/")
        if disk.percent > 90:
            alerts.append(f"⚠️ Disco lleno: {disk.percent}%")

        if alerts:
            try:
                self.record_result("alerts", alerts)
            except Exception:
                pass
            return "🚨 Alertas del sistema:\n" + "\n".join(alerts)
        else:
            return "✅ Sistema funcionando correctamente"

    def learn(self) -> dict:
        """Ejemplo simple de aprendizaje: contar eventos de alertas recientes."""
        stats = self.get_stats()
        alerts = stats.get("alerts", [])
        high_cpu_events = 0
        for e in alerts:
            if isinstance(e.get("value") if isinstance(e, dict) else e, list):
                high_cpu_events += 1
        insight = {"alert_events": len(alerts), "high_cpu_events": high_cpu_events}
        return insight
