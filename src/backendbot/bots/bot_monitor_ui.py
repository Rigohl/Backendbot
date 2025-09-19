"""
Bot Monitor integrado con la UI de BackendBot.
Monitorea CPU, RAM, VRAM y disco, y reporta a la UI.
Utiliza configuraciones dinámicas según el modo de operación.
"""
import threading
import time
import psutil
try:
    from src.backendbot.utils.gpu_monitor import getGPUs
    gpu_available = True
    print("✅ Monitoreo de GPU disponible")
except (ImportError, ModuleNotFoundError) as e:
    gpu_available = False
    print(f"⚠️ Monitoreo de GPU no disponible: {e}")

from src.backendbot.modes import mode_manager
from src.backendbot.modes.adaptive_learning import adaptive_learning

class BotMonitorUI:
    def __init__(self, ui_connector):
        self.ui_connector = ui_connector
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()
        self.last_alert_time = 0
        self.alert_cooldown = 30  # segundos entre alertas

    def get_thresholds(self):
        """Obtener umbrales dinámicos según el modo actual"""
        return mode_manager._configure_monitoring_thresholds()

    def monitor_loop(self):
        while self.running:
            try:
                # Obtener métricas del sistema
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent

                # Construir mensaje base
                msg = f"CPU: {cpu:.1f}% | RAM: {ram:.1f}% | Disco: {disk:.1f}%"

                # Agregar información de GPU si está disponible
                if gpu_available:
                    try:
                        gpus = getGPUs()
                        if gpus:
                            gpu = gpus[0]
                            if gpu.memoryTotal > 0:
                                vram_percent = (gpu.memoryUsed / gpu.memoryTotal) * 100
                                msg += f" | VRAM: {vram_percent:.1f}%"
                            else:
                                msg += f" | GPU: {gpu.name[:15]}..."
                    except Exception as e:
                        msg += f" | GPU: Error ({str(e)[:20]}...)"

                # Obtener umbrales del modo actual
                thresholds = self.get_thresholds()

                # Verificar alertas según umbrales del modo
                current_time = time.time()
                alerts = []

                if cpu > thresholds['cpu']:
                    alerts.append(f"CPU alta ({cpu:.1f}% > {thresholds['cpu']}%)")

                if ram > thresholds['memory']:
                    alerts.append(f"RAM alta ({ram:.1f}% > {thresholds['memory']}%)")

                if disk > thresholds['disk']:
                    alerts.append(f"Disco lleno ({disk:.1f}% > {thresholds['disk']}%)")

                # Agregar información del modo actual
                mode_info = mode_manager.get_mode_info()
                msg += f" | Modo: {mode_info['mode'].capitalize()}"

                # Enviar mensaje de estado
                self.ui_connector.send_message(msg)

                # Registrar métricas para aprendizaje adaptativo
                adaptive_learning.record_performance_metric('cpu_usage', cpu)
                adaptive_learning.record_performance_metric('memory_usage', ram)
                adaptive_learning.record_performance_metric('disk_usage', disk)

                if gpu_available and gpus:
                    gpu = gpus[0]
                    if gpu.memoryTotal > 0:
                        vram_percent = (gpu.memoryUsed / gpu.memoryTotal) * 100
                        adaptive_learning.record_performance_metric('gpu_memory_usage', vram_percent)

                # Registrar acción de monitoreo para patrones de uso
                adaptive_learning.record_user_action('system_monitoring', {
                    'cpu_level': 'high' if cpu > 80 else 'normal',
                    'memory_level': 'high' if ram > 85 else 'normal',
                    'disk_level': 'high' if disk > 90 else 'normal',
                    'mode': mode_manager.get_mode_info()['mode']
                })

                # Enviar alertas si hay y ha pasado el cooldown
                if alerts and (current_time - self.last_alert_time) > self.alert_cooldown:
                    alert_msg = "⚠️ ALERTA: " + ", ".join(alerts)
                    self.ui_connector.send_message(alert_msg)
                    self.last_alert_time = current_time

                # Usar intervalo dinámico según el modo
                sleep_time = mode_manager.get_monitoring_interval()
                time.sleep(sleep_time)

            except Exception as e:
                self.ui_connector.send_message(f"Error en monitoreo: {str(e)}")
                time.sleep(5)  # Esperar antes de reintentar

    def stop(self):
        self.running = False
