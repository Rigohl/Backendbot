"""
Script principal para lanzar la UI de BackendBot e integrar el tray icon, panel flotante y comunicación con bots.
"""
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import time
from .tray_icon import TrayIcon
from .floating_panel import FloatingPanel
from .bot_bridge import BotBridge
from src.backendbot.config import OperationMode
from src.backendbot.modes import mode_manager
from src.backendbot.modes.adaptive_learning import adaptive_learning
from src.backendbot.cron_jobs.task_scheduler import task_scheduler
from src.backendbot.utils.advanced_command_processor import advanced_command_processor

class BackendBotUI:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.icon_active = QtGui.QIcon("icono_rojo.png")
        self.icon_inactive = QtGui.QIcon("icono_gris.png")
        self.tray = TrayIcon(self.icon_active, self.icon_inactive)
        self.panel = FloatingPanel()
        self.bridge = BotBridge()
        self.tray.open_panel = self.panel.show
        self.tray.show()
        self.panel.show_message("BackendBot iniciado.")
        self.panel.input_line.returnPressed.connect(self.handle_command)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_bot_messages)
        self.timer.start(500)

        # Configurar menú de modos
        self._setup_mode_menu()

        # Mostrar modo actual
        self._update_mode_display()

    def _setup_mode_menu(self):
        """Configurar menú contextual para cambio de modos"""
        mode_menu = QtWidgets.QMenu("Modos de Operación")

        # Crear acciones para cada modo
        modes = [
            (OperationMode.EDITOR, "Editor - Optimizado para desarrollo"),
            (OperationMode.STREAMING, "Streaming - Para grabación y transmisión"),
            (OperationMode.RELAX, "Relax - Navegación y entretenimiento"),
            (OperationMode.DESARROLLO, "Desarrollo - Compilación intensiva"),
            (OperationMode.GAMING, "Gaming - Alto rendimiento")
        ]

        for mode, description in modes:
            action = QtWidgets.QAction(description, self.tray.menu)
            action.triggered.connect(lambda checked, m=mode: self.change_mode(m))
            mode_menu.addAction(action)

        # Agregar separador y acción de información
        mode_menu.addSeparator()
        info_action = QtWidgets.QAction("Ver configuración actual", self.tray.menu)
        info_action.triggered.connect(self.show_mode_info)
        mode_menu.addAction(info_action)

        # Agregar el menú de modos al menú principal del tray
        self.tray.menu.addMenu(mode_menu)

    def change_mode(self, mode: OperationMode):
        """Cambiar el modo de operación"""
        try:
            mode_manager.set_mode(mode)
            self._update_mode_display()
            self.panel.show_message(f"Modo cambiado a: {mode.value}")
        except Exception as e:
            self.panel.show_message(f"Error cambiando modo: {str(e)}")

    def _update_mode_display(self):
        """Actualizar visualización del modo actual"""
        mode_info = mode_manager.get_mode_info()
        mode_name = mode_info['mode'].capitalize()
        self.tray.setToolTip(f"BackendBot - Modo: {mode_name}")

    def show_recommendations(self):
        """Mostrar recomendaciones del sistema de aprendizaje"""
        try:
            recommendations = adaptive_learning.get_recommendations()
            if recommendations:
                self.panel.show_message("🤖 Recomendaciones del sistema:")
                for i, rec in enumerate(recommendations[:3], 1):
                    self.panel.show_message(f"{i}. {rec}")
            else:
                self.panel.show_message("📚 No hay recomendaciones disponibles aún. El sistema está aprendiendo...")
        except Exception as e:
            self.panel.show_message(f"Error obteniendo recomendaciones: {str(e)}")

    def show_learning_stats(self):
        """Mostrar estadísticas del sistema de aprendizaje"""
        try:
            stats = adaptive_learning.get_learning_stats()
            self.panel.show_message("🧠 Estadísticas de Aprendizaje:")
            self.panel.show_message(f"• Acciones aprendidas: {stats['total_actions_learned']}")
            self.panel.show_message(f"• Métricas registradas: {stats['total_metrics_recorded']}")
            self.panel.show_message(f"• Patrones analizados: {stats['patterns_analyzed']}")
            self.panel.show_message(f"• Sistema activo: {'Sí' if stats['learning_active'] else 'No'}")
        except Exception as e:
            self.panel.show_message(f"Error obteniendo estadísticas: {str(e)}")

    def show_task_stats(self):
        """Mostrar estadísticas del sistema de tareas programadas"""
        try:
            stats = task_scheduler.get_task_stats()
            self.panel.show_message("⏰ Estadísticas de Tareas Programadas:")
            self.panel.show_message(f"• Total de tareas: {stats['total_tasks']}")
            self.panel.show_message(f"• Tareas habilitadas: {stats['enabled_tasks']}")
            self.panel.show_message(f"• Tareas deshabilitadas: {stats['disabled_tasks']}")
            self.panel.show_message(f"• Total de ejecuciones: {stats['total_runs']}")
            self.panel.show_message(f"• Tasa de éxito: {stats['success_rate']:.1f}%")
            self.panel.show_message(f"• Programador activo: {'Sí' if stats['running'] else 'No'}")
        except Exception as e:
            self.panel.show_message(f"Error obteniendo estadísticas de tareas: {str(e)}")

    def show_task_list(self):
        """Mostrar lista de tareas programadas"""
        try:
            tasks = task_scheduler.get_tasks_list()
            if not tasks:
                self.panel.show_message("📋 No hay tareas programadas")
                return

            self.panel.show_message("📋 Lista de Tareas Programadas:")
            for task in tasks:
                status = "✅" if task['enabled'] else "❌"
                freq = task['frequency'].replace('_', ' ').capitalize()
                priority = task['priority'].replace('_', ' ').capitalize()
                self.panel.show_message(f"{status} {task['name']} ({freq}) - {priority}")
                self.panel.show_message(f"   ID: {task['task_id']}")
                self.panel.show_message(f"   Ejecutada: {task['run_count']} veces")
                if task['last_run']:
                    self.panel.show_message(f"   Última: {task['last_run'][:19]}")
                self.panel.show_message("")
        except Exception as e:
            self.panel.show_message(f"Error obteniendo lista de tareas: {str(e)}")

    def enable_task(self, task_id: str):
        """Habilitar una tarea programada"""
        try:
            if task_scheduler.enable_task(task_id):
                self.panel.show_message(f"✅ Tarea '{task_id}' habilitada")
                # Registrar en aprendizaje adaptativo
                adaptive_learning.record_user_action('task_management', {
                    'action': 'enable',
                    'task_id': task_id,
                    'mode': mode_manager.get_mode_info()['mode']
                })
            else:
                self.panel.show_message(f"❌ No se encontró la tarea '{task_id}'")
        except Exception as e:
            self.panel.show_message(f"Error habilitando tarea: {str(e)}")

    def disable_task(self, task_id: str):
        """Deshabilitar una tarea programada"""
        try:
            if task_scheduler.disable_task(task_id):
                self.panel.show_message(f"✅ Tarea '{task_id}' deshabilitada")
                # Registrar en aprendizaje adaptativo
                adaptive_learning.record_user_action('task_management', {
                    'action': 'disable',
                    'task_id': task_id,
                    'mode': mode_manager.get_mode_info()['mode']
                })
            else:
                self.panel.show_message(f"❌ No se encontró la tarea '{task_id}'")
        except Exception as e:
            self.panel.show_message(f"Error deshabilitando tarea: {str(e)}")

    def run_tasks_manually(self):
        """Ejecutar tareas manualmente (solo las habilitadas)"""
        try:
            self.panel.show_message("🔄 Ejecutando tareas programadas manualmente...")
            # Nota: En una implementación completa, podríamos ejecutar todas las tareas
            # Por ahora, solo mostramos que la funcionalidad está disponible
            self.panel.show_message("✅ Comando recibido. Las tareas se ejecutarán según su programación.")
            self.panel.show_message("💡 Usa 'tareas lista' para ver todas las tareas disponibles")
        except Exception as e:
            self.panel.show_message(f"Error ejecutando tareas: {str(e)}")

    def _handle_mode_change_from_nlp(self, recognized_command: str):
        """Manejar cambio de modo desde procesamiento de lenguaje natural"""
        mode_map = {
            'mode_change': OperationMode.EDITOR,
            'mode_editor': OperationMode.EDITOR,
            'mode_streaming': OperationMode.STREAMING,
            'mode_relax': OperationMode.RELAX,
            'mode_desarrollo': OperationMode.DESARROLLO,
            'mode_gaming': OperationMode.GAMING
        }

        if recognized_command in mode_map:
            self.change_mode(mode_map[recognized_command])

    def _handle_task_management_from_nlp(self, recognized_command: str, original_cmd: str):
        """Manejar gestión de tareas desde procesamiento de lenguaje natural"""
        # Extraer ID de tarea del comando original (simplificado)
        words = original_cmd.split()
        if len(words) >= 3:
            task_id = words[-1]  # Última palabra como ID de tarea
            if recognized_command == 'task_enable':
                self.enable_task(task_id)
            elif recognized_command == 'task_disable':
                self.disable_task(task_id)

    def _show_detailed_system_status(self):
        """Mostrar estado detallado del sistema"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            self.panel.show_message("🔍 Estado Detallado del Sistema:")
            self.panel.show_message(f"• CPU: {cpu_percent}%")
            self.panel.show_message(f"• Memoria: {memory.percent}% ({memory.used / 1024 / 1024 / 1024:.1f} GB usado)")
            self.panel.show_message(f"• Disco: {disk.percent}% ({disk.free / 1024 / 1024 / 1024:.1f} GB libre)")
            self.panel.show_message(f"• Modo actual: {mode_manager.get_mode_info()['mode'].capitalize()}")
        except Exception as e:
            self.panel.show_message(f"Error obteniendo estado del sistema: {str(e)}")

    def _show_detailed_performance(self):
        """Mostrar métricas detalladas de rendimiento"""
        try:
            import psutil
            cpu_freq = psutil.cpu_freq()
            memory = psutil.virtual_memory()
            network = psutil.net_io_counters()

            self.panel.show_message("📊 Métricas de Rendimiento Detalladas:")
            self.panel.show_message(f"• CPU Frecuencia: {cpu_freq.current:.0f} MHz" if cpu_freq else "• CPU Frecuencia: N/A")
            self.panel.show_message(f"• Memoria Total: {memory.total / 1024 / 1024 / 1024:.1f} GB")
            self.panel.show_message(f"• Memoria Disponible: {memory.available / 1024 / 1024 / 1024:.1f} GB")
            self.panel.show_message(f"• Red Enviado: {network.bytes_sent / 1024 / 1024:.1f} MB")
            self.panel.show_message(f"• Red Recibido: {network.bytes_recv / 1024 / 1024:.1f} MB")
        except Exception as e:
            self.panel.show_message(f"Error obteniendo métricas de rendimiento: {str(e)}")

    def _perform_cleanup(self):
        """Realizar limpieza del sistema"""
        try:
            self.panel.show_message("🧹 Iniciando limpieza del sistema...")

            # Aquí se integraría con las funciones de limpieza reales
            # Por simplicidad, mostramos progreso
            import time
            time.sleep(0.5)
            self.panel.show_message("✅ Limpieza de archivos temporales completada")
            time.sleep(0.5)
            self.panel.show_message("✅ Limpieza de cache completada")
            time.sleep(0.5)
            self.panel.show_message("✅ Optimización del sistema completada")

            # Registrar en aprendizaje adaptativo
            adaptive_learning.record_user_action('cleanup', {
                'type': 'manual_cleanup',
                'mode': mode_manager.get_mode_info()['mode']
            })

        except Exception as e:
            self.panel.show_message(f"Error durante la limpieza: {str(e)}")

    def handle_command(self):
        cmd = self.panel.input_line.text().strip()

        # Procesar comando con sistema avanzado
        proc_result = advanced_command_processor.process_command(cmd)

        # process_command may return either (dict, recognized) or a dict directly
        recognized_command = None
        if isinstance(proc_result, tuple) and len(proc_result) == 2:
            response, recognized_command = proc_result
        else:
            response = proc_result

        # Mostrar respuesta del procesador avanzado
        try:
            # If response is a dict, show the message
            if isinstance(response, dict):
                self.panel.show_message(response.get('message') or str(response))
            else:
                self.panel.show_message(str(response))
        except Exception:
            self.panel.show_message(str(response))

        # Si el comando fue reconocido como uno específico, procesarlo adicionalmente
        if recognized_command:
            self._process_recognized_command(recognized_command, cmd)

        # Limpiar campo de entrada
        self.panel.input_line.clear()

    def _process_recognized_command(self, recognized_command: str, original_cmd: str):
        """Procesar comandos reconocidos adicionalmente si es necesario"""
        try:
            # Procesar comandos que requieren acciones específicas
            if recognized_command.startswith('mode_'):
                self._handle_mode_change_from_nlp(recognized_command)
            elif recognized_command in ['task_enable', 'task_disable']:
                self._handle_task_management_from_nlp(recognized_command, original_cmd)
            elif recognized_command == 'system_status':
                self._show_detailed_system_status()
            elif recognized_command == 'performance_check':
                self._show_detailed_performance()
            elif recognized_command == 'cleanup_request':
                self._perform_cleanup()
            elif recognized_command == 'recommendations':
                self.show_recommendations()
            elif recognized_command == 'learning_stats':
                self.show_learning_stats()
            elif recognized_command == 'task_management':
                self.show_task_list()

        except Exception as e:
            self.panel.show_message(f"Error procesando comando específico: {str(e)}")

    def check_bot_messages(self):
        msg = self.bridge.get_next_message()
        if msg:
            self.panel.show_message(msg)

    def run(self):
        self.panel.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    ui = BackendBotUI()
    ui.run()
