"""
Bot Optimizador de Procesos: lista y gestiona procesos, reporta a la UI.
Utiliza configuraciones dinámicas según el modo de operación.
"""
import threading
import time
import psutil
from src.backendbot.modes import mode_manager
from src.backendbot.modes.adaptive_learning import adaptive_learning

class BotOptimizerUI:
    def __init__(self, ui_connector):
        self.ui_connector = ui_connector
        self.running = True
        self.thread = threading.Thread(target=self.optimizer_loop, daemon=True)
        self.thread.start()
        self.last_optimization = 0
        self.optimization_interval = 300  # 5 minutos por defecto

    def optimizer_loop(self):
        while self.running:
            try:
                current_time = time.time()

                # Verificar si la optimización está habilitada para el modo actual
                if mode_manager.should_optimize():
                    # Realizar optimización periódica
                    if current_time - self.last_optimization > self.optimization_interval:
                        self.perform_optimization()
                        self.last_optimization = current_time

                    # Monitoreo continuo de procesos
                    self.monitor_processes()
                else:
                    # Modo que no requiere optimización agresiva
                    mode_info = mode_manager.get_mode_info()
                    msg = f"Optimización desactivada en modo {mode_info['mode'].capitalize()}"
                    self.ui_connector.send_message(msg)

                # Intervalo dinámico según el modo
                sleep_time = mode_manager.get_monitoring_interval() * 2  # Menos frecuente que el monitoreo
                time.sleep(sleep_time)

            except Exception as e:
                self.ui_connector.send_message(f"Error en optimización: {str(e)}")
                time.sleep(30)

    def monitor_processes(self):
        """Monitorear procesos y reportar información"""
        try:
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    cpu_percent = p.cpu_percent(interval=0.1)
                    memory_percent = p.memory_percent()
                    if cpu_percent > 0 or memory_percent > 0:  # Solo procesos activos
                        procs.append((p.pid, p.name(), cpu_percent, memory_percent))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Ordenar por uso de recursos
            top_procs = sorted(procs, key=lambda x: x[2] + x[3], reverse=True)[:5]

            if top_procs:
                proc_list = []
                for pid, name, cpu, mem in top_procs:
                    # Verificar si es un proceso foco del modo actual
                    is_focus = mode_manager.is_focus_process(name)
                    focus_indicator = "⭐" if is_focus else ""
                    proc_list.append(f"{name[:15]}{focus_indicator} (CPU:{cpu:.1f}%, RAM:{mem:.1f}%)")

                msg = "Top procesos: " + " | ".join(proc_list)
                self.ui_connector.send_message(msg)

        except Exception as e:
            self.ui_connector.send_message(f"Error monitoreando procesos: {str(e)}")

    def perform_optimization(self):
        """Realizar optimización del sistema según el modo y aprendizaje"""
        try:
            mode_info = mode_manager.get_mode_info()
            mode_name = mode_info['mode']

            # Obtener recomendaciones del sistema de aprendizaje
            recommendations = adaptive_learning.get_recommendations()

            # Registrar acción de optimización
            adaptive_learning.record_user_action('system_optimization', {
                'mode': mode_name,
                'recommendations_count': len(recommendations),
                'aggressive_mode': mode_name in ["desarrollo", "editor"]
            })

            if mode_name == "gaming":
                self.optimize_for_gaming()
            elif mode_name == "streaming":
                self.optimize_for_streaming()
            elif mode_name == "editor":
                self.optimize_for_editing()
            elif mode_name == "desarrollo":
                self.optimize_for_development()
            else:  # relax
                self.optimize_for_relax()

            # Mostrar recomendaciones si las hay
            if recommendations:
                for rec in recommendations[:2]:  # Mostrar máximo 2 recomendaciones
                    self.ui_connector.send_message(f"💡 {rec}")

            self.ui_connector.send_message(f"✅ Optimización completada para modo {mode_name.capitalize()}")

        except Exception as e:
            self.ui_connector.send_message(f"Error en optimización: {str(e)}")

    def optimize_for_gaming(self):
        """Optimizaciones específicas para gaming"""
        # Cerrar procesos no esenciales
        non_essential = ['chrome.exe', 'firefox.exe', 'spotify.exe', 'discord.exe']
        closed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.name().lower() in non_essential:
                    proc.terminate()
                    closed_count += 1
            except:
                pass
        if closed_count > 0:
            self.ui_connector.send_message(f"🎮 Cerrados {closed_count} procesos no esenciales para gaming")

    def optimize_for_streaming(self):
        """Optimizaciones específicas para streaming"""
        # Minimizar procesos que puedan interferir con la transmisión
        self.ui_connector.send_message("🎥 Modo streaming: Optimizando para transmisión estable")

    def optimize_for_editing(self):
        """Optimizaciones específicas para edición de código"""
        # Asegurar que los procesos de desarrollo tengan prioridad
        focus_procs = mode_manager.focus_processes
        prioritized = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if any(focus.lower() in proc.name().lower() for focus in focus_procs):
                    proc.nice(-10)  # Alta prioridad
                    prioritized += 1
            except:
                pass
        if prioritized > 0:
            self.ui_connector.send_message(f"💻 Priorizados {prioritized} procesos de desarrollo")

    def optimize_for_development(self):
        """Optimizaciones específicas para desarrollo intensivo"""
        # Similar a edición pero más agresivo
        self.optimize_for_editing()
        self.ui_connector.send_message("🔧 Modo desarrollo: Optimización intensiva activada")

    def optimize_for_relax(self):
        """Optimizaciones mínimas para modo relax"""
        self.ui_connector.send_message("😌 Modo relax: Optimización mínima para navegación")

    def stop(self):
        self.running = False
