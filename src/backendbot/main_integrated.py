#!/usr/bin/env python3
"""
BackendBot - Interfaz Integrada Completa
Combina dashboard, bots, sistemas avanzados y chat en una sola aplicación
"""
import os
import sys
import json
import psutil
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QProgressBar, QGroupBox,
                             QGridLayout, QTabWidget, QTextEdit, QListWidget,
                             QPushButton, QComboBox, QCheckBox, QSplitter,
                             QFrame, QScrollArea, QMenuBar, QMenu, QAction,
                             QSystemTrayIcon, QStatusBar, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backendbot.core.di.container import container
from backendbot.bots.manager import BotManager
from backendbot.ui.chat_panel import ChatPanel
from backendbot.ui.tray_icon import TrayIcon

# Importar sistemas avanzados
try:
    from notification_system import NotificationManager
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

try:
    from power_management import PowerManager
    POWER_AVAILABLE = True
except ImportError:
    POWER_AVAILABLE = False

try:
    from backup_system import BackupManager
    BACKUP_AVAILABLE = True
except ImportError:
    BACKUP_AVAILABLE = False

@dataclass
class SystemMetrics:
    """Métricas del sistema en tiempo real"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int
    network_recv: int
    battery_percent: Optional[float]
    temperature: Optional[float]

class MetricsCollector(QThread):
    """Hilo para recolectar métricas del sistema"""
    metrics_updated = pyqtSignal(SystemMetrics)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)

                # Memoria
                memory = psutil.virtual_memory()

                # Disco
                disk = psutil.disk_usage('/')

                # Red
                network = psutil.net_io_counters()

                # Batería
                battery = psutil.sensors_battery()
                battery_percent = battery.percent if battery else None

                # Temperatura (si está disponible)
                temperature = None
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Tomar la primera temperatura disponible
                        for sensor_name, sensor_readings in temps.items():
                            if sensor_readings:
                                temperature = sensor_readings[0].current
                                break
                except:
                    pass

                metrics = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_percent=disk.percent,
                    network_sent=network.bytes_sent,
                    network_recv=network.bytes_recv,
                    battery_percent=battery_percent,
                    temperature=temperature
                )

                self.metrics_updated.emit(metrics)

            except Exception as e:
                print(f"Error recolectando métricas: {e}")

            self.sleep(2)  # Actualizar cada 2 segundos

    def stop(self):
        self.running = False

class IntegratedDashboard(QMainWindow):
    """Dashboard integrado completo de BackendBot"""

    def __init__(self):
        super().__init__()

        # Inicializar dependencias
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()

        # Inicializar sistemas avanzados
        self.notifications = NotificationManager() if NOTIFICATIONS_AVAILABLE else None
        self.power_manager = PowerManager() if POWER_AVAILABLE else None
        self.backup_manager = BackupManager() if BACKUP_AVAILABLE else None

        # Inicializar bots
        self.bot_manager = BotManager()

        # Configurar ventana principal
        self.setWindowTitle("🐝 BackendBot - Sistema Integrado Completo")
        self.setGeometry(100, 100, 1400, 900)
        self.setWindowIcon(self._create_icon())

        # Crear interfaz
        self._setup_ui()

        # Configurar métricas
        self.metrics_collector = MetricsCollector()
        self.metrics_collector.metrics_updated.connect(self._update_metrics)
        self.metrics_collector.start()

        # Configurar timers
        self._setup_timers()

        # Configurar menú y barra de estado
        self._setup_menu()
        self._setup_status_bar()

        # Configurar bandeja del sistema
        self._setup_tray()

        # Log de inicialización
        self.logger.info("BackendBot integrado inicializado correctamente", "IntegratedDashboard")

    def _create_icon(self):
        """Crear ícono para la aplicación"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(255, 0, 0))  # Rojo
        return QIcon(pixmap)

    def _setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)

        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Panel izquierdo - Dashboard
        self._create_dashboard_panel(splitter)

        # Panel derecho - Bots y Sistemas
        self._create_bots_panel(splitter)

        # Configurar splitter
        splitter.setSizes([800, 600])

    def _create_dashboard_panel(self, parent):
        """Crear panel del dashboard"""
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)

        # Título
        title_label = QLabel("📊 Dashboard en Tiempo Real")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        dashboard_layout.addWidget(title_label)

        # Scroll area para el dashboard
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.dashboard_layout = QVBoxLayout(scroll_widget)

        # Métricas del sistema
        self._create_system_metrics_section()

        # Gráficos y widgets
        self._create_charts_section()

        # Estado de bots
        self._create_bots_status_section()

        scroll_widget.setLayout(self.dashboard_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        dashboard_layout.addWidget(scroll_area)

        parent.addWidget(dashboard_widget)

    def _create_system_metrics_section(self):
        """Crear sección de métricas del sistema"""
        metrics_group = QGroupBox("📈 Métricas del Sistema")
        metrics_layout = QGridLayout(metrics_group)

        # CPU
        metrics_layout.addWidget(QLabel("CPU:"), 0, 0)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        metrics_layout.addWidget(self.cpu_progress, 0, 1)
        self.cpu_label = QLabel("0%")
        metrics_layout.addWidget(self.cpu_label, 0, 2)

        # Memoria
        metrics_layout.addWidget(QLabel("Memoria:"), 1, 0)
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        metrics_layout.addWidget(self.memory_progress, 1, 1)
        self.memory_label = QLabel("0%")
        metrics_layout.addWidget(self.memory_label, 1, 2)

        # Disco
        metrics_layout.addWidget(QLabel("Disco:"), 2, 0)
        self.disk_progress = QProgressBar()
        self.disk_progress.setRange(0, 100)
        metrics_layout.addWidget(self.disk_progress, 2, 1)
        self.disk_label = QLabel("0%")
        metrics_layout.addWidget(self.disk_label, 2, 2)

        # Red
        metrics_layout.addWidget(QLabel("Red ↑:"), 3, 0)
        self.network_sent_label = QLabel("0 MB")
        metrics_layout.addWidget(self.network_sent_label, 3, 1)
        metrics_layout.addWidget(QLabel("Red ↓:"), 3, 2)
        self.network_recv_label = QLabel("0 MB")
        metrics_layout.addWidget(self.network_recv_label, 3, 3)

        # Batería
        metrics_layout.addWidget(QLabel("Batería:"), 4, 0)
        self.battery_progress = QProgressBar()
        self.battery_progress.setRange(0, 100)
        metrics_layout.addWidget(self.battery_progress, 4, 1)
        self.battery_label = QLabel("N/A")
        metrics_layout.addWidget(self.battery_label, 4, 2)

        # Temperatura
        metrics_layout.addWidget(QLabel("Temperatura:"), 5, 0)
        self.temperature_label = QLabel("N/A")
        metrics_layout.addWidget(self.temperature_label, 5, 1)

        self.dashboard_layout.addWidget(metrics_group)

    def _create_charts_section(self):
        """Crear sección de gráficos"""
        charts_group = QGroupBox("📊 Gráficos y Tendencias")
        charts_layout = QVBoxLayout(charts_group)

        # Área para gráficos (placeholder)
        charts_placeholder = QLabel("📈 Gráficos históricos próximamente")
        charts_placeholder.setAlignment(Qt.AlignCenter)
        charts_placeholder.setStyleSheet("border: 2px dashed #ccc; padding: 20px;")
        charts_layout.addWidget(charts_placeholder)

        self.dashboard_layout.addWidget(charts_group)

    def _create_bots_status_section(self):
        """Crear sección de estado de bots"""
        bots_group = QGroupBox("🤖 Estado de Bots")
        bots_layout = QVBoxLayout(bots_group)

        self.bots_status_list = QListWidget()
        self.bots_status_list.setMaximumHeight(200)
        bots_layout.addWidget(self.bots_status_list)

        # Botón para actualizar estado
        refresh_button = QPushButton("🔄 Actualizar Estado")
        refresh_button.clicked.connect(self._update_bots_status)
        bots_layout.addWidget(refresh_button)

        self.dashboard_layout.addWidget(bots_group)

    def _create_bots_panel(self, parent):
        """Crear panel de bots y sistemas"""
        bots_widget = QWidget()
        bots_layout = QVBoxLayout(bots_widget)

        # Tabs para diferentes secciones
        tabs = QTabWidget()

        # Tab de Bots
        self._create_bots_tab(tabs)

        # Tab de Sistemas Avanzados
        self._create_advanced_systems_tab(tabs)

        # Tab de Chat
        self._create_chat_tab(tabs)

        bots_layout.addWidget(tabs)
        parent.addWidget(bots_widget)

    def _create_bots_tab(self, tabs):
        """Crear tab de bots"""
        bots_tab = QWidget()
        bots_layout = QVBoxLayout(bots_tab)

        # Lista de bots disponibles
        bots_list_group = QGroupBox("🤖 Bots Disponibles")
        bots_list_layout = QVBoxLayout(bots_list_group)

        self.bots_list = QListWidget()
        self.bots_list.addItems([
            "📊 Monitor - Monitoreo del sistema",
            "📁 Organizer - Organización de archivos",
            "🔍 Indexer - Búsqueda de archivos",
            "🛡️ Guardian - Supervisión de bots",
            "📂 Auditor Archivos - Análisis de archivos antiguos",
            "💻 Auditor Programas - Análisis de programas"
        ])
        bots_list_layout.addWidget(self.bots_list)

        # Botones de acción
        buttons_layout = QHBoxLayout()

        status_button = QPushButton("📊 Estado")
        status_button.clicked.connect(self._show_bot_status)
        buttons_layout.addWidget(status_button)

        execute_button = QPushButton("▶️ Ejecutar")
        execute_button.clicked.connect(self._execute_bot_command)
        buttons_layout.addWidget(execute_button)

        bots_list_layout.addLayout(buttons_layout)
        bots_layout.addWidget(bots_list_group)

        # Área de resultados
        results_group = QGroupBox("📝 Resultados")
        results_layout = QVBoxLayout(results_group)

        self.bot_results = QTextEdit()
        self.bot_results.setReadOnly(True)
        self.bot_results.setMaximumHeight(300)
        results_layout.addWidget(self.bot_results)

        bots_layout.addWidget(results_group)

        tabs.addTab(bots_tab, "🤖 Bots")

    def _create_advanced_systems_tab(self, tabs):
        """Crear tab de sistemas avanzados"""
        systems_tab = QWidget()
        systems_layout = QVBoxLayout(systems_tab)

        # Notificaciones
        if NOTIFICATIONS_AVAILABLE:
            notifications_group = QGroupBox("🔔 Sistema de Notificaciones")
            notifications_layout = QVBoxLayout(notifications_group)

            test_notification_button = QPushButton("📢 Enviar Notificación de Prueba")
            test_notification_button.clicked.connect(self._send_test_notification)
            notifications_layout.addWidget(test_notification_button)

            systems_layout.addWidget(notifications_group)

        # Gestión de Energía
        if POWER_AVAILABLE:
            power_group = QGroupBox("⚡ Gestión de Energía")
            power_layout = QVBoxLayout(power_group)

            power_combo = QComboBox()
            power_combo.addItems(["Alto Rendimiento", "Equilibrado", "Ahorro de Energía", "Ultra Bajo"])
            power_combo.currentTextChanged.connect(self._change_power_profile)
            power_layout.addWidget(power_combo)

            systems_layout.addWidget(power_group)

        # Backup
        if BACKUP_AVAILABLE:
            backup_group = QGroupBox("💾 Sistema de Backup")
            backup_layout = QVBoxLayout(backup_group)

            create_backup_button = QPushButton("💾 Crear Backup")
            create_backup_button.clicked.connect(self._create_backup)
            backup_layout.addWidget(create_backup_button)

            systems_layout.addWidget(backup_group)

        # Si no hay sistemas avanzados
        if not (NOTIFICATIONS_AVAILABLE or POWER_AVAILABLE or BACKUP_AVAILABLE):
            no_systems_label = QLabel("⚠️ Sistemas avanzados no disponibles")
            no_systems_label.setAlignment(Qt.AlignCenter)
            systems_layout.addWidget(no_systems_label)

        tabs.addTab(systems_tab, "⚙️ Sistemas Avanzados")

    def _update_metrics(self, metrics: SystemMetrics):
        """Actualizar métricas en la UI"""
        self.cpu_progress.setValue(int(metrics.cpu_percent))
        self.cpu_label.setText(f"{metrics.cpu_percent:.1f}%")

        self.memory_progress.setValue(int(metrics.memory_percent))
        self.memory_label.setText(f"{metrics.memory_percent:.1f}%")

        self.disk_progress.setValue(int(metrics.disk_percent))
        self.disk_label.setText(f"{metrics.disk_percent:.1f}%")

        # Red en MB
        sent_mb = metrics.network_sent / (1024 * 1024)
        recv_mb = metrics.network_recv / (1024 * 1024)
        self.network_sent_label.setText(f"{sent_mb:.1f} MB")
        self.network_recv_label.setText(f"{recv_mb:.1f} MB")

        # Batería
        if metrics.battery_percent is not None:
            self.battery_progress.setValue(int(metrics.battery_percent))
            self.battery_label.setText(f"{metrics.battery_percent:.1f}%")
        else:
            self.battery_progress.setValue(0)
            self.battery_label.setText("N/A")

        # Temperatura
        if metrics.temperature is not None:
            self.temperature_label.setText(f"{metrics.temperature:.1f}°C")
        else:
            self.temperature_label.setText("N/A")

        # Actualizar barra de estado
        self.memory_status.setText(f"💾 RAM: {metrics.memory_percent:.1f}%")

    def _update_all_metrics(self):
        """Forzar actualización de métricas"""
        # Esto será llamado por el timer
        pass

    def _update_bots_status(self):
        """Actualizar estado de todos los bots"""
        self.bots_status_list.clear()

        for bot_name, bot in self.bot_manager.bots.items():
            try:
                status = bot.get_status()
                self.bots_status_list.addItem(f"✅ {bot_name}: {status}")
            except Exception as e:
                self.bots_status_list.addItem(f"❌ {bot_name}: Error - {str(e)}")

        # Actualizar barra de estado
        active_bots = len([b for b in self.bot_manager.bots.values() if b.is_available()])
        self.bots_status.setText(f"🤖 Bots: {active_bots}/{len(self.bot_manager.bots)}")

    def _show_bot_status(self):
        """Mostrar estado del bot seleccionado"""
        current_item = self.bots_list.currentItem()
        if not current_item:
            return

        bot_name = current_item.text().split(" - ")[0].replace("📊 ", "").replace("📁 ", "").replace("🔍 ", "").replace("🛡️ ", "").replace("📂 ", "").replace("💻 ", "").lower()

        # Mapear nombres de UI a nombres internos
        name_mapping = {
            "monitor": "monitor",
            "organizer": "organizer",
            "indexer": "indexer",
            "guardian": "guardian",
            "auditor archivos": "auditor_files",
            "auditor programas": "auditor_programs"
        }

        internal_name = name_mapping.get(bot_name, bot_name)

        try:
            result = self.bot_manager._process_bot_command(internal_name, f"{internal_name} status")
            self.bot_results.append(f"📊 Estado de {bot_name}:\n{result}\n")
        except Exception as e:
            self.bot_results.append(f"❌ Error obteniendo estado de {bot_name}: {str(e)}\n")

    def _execute_bot_command(self):
        """Ejecutar comando en el bot seleccionado"""
        current_item = self.bots_list.currentItem()
        if not current_item:
            return

        bot_name = current_item.text().split(" - ")[0].replace("📊 ", "").replace("📁 ", "").replace("🔍 ", "").replace("🛡️ ", "").replace("📂 ", "").replace("💻 ", "").lower()

        # Mapear nombres
        name_mapping = {
            "monitor": "monitor",
            "organizer": "organizer",
            "indexer": "indexer",
            "guardian": "guardian",
            "auditor archivos": "auditor_files",
            "auditor programas": "auditor_programs"
        }

        internal_name = name_mapping.get(bot_name, bot_name)

        try:
            result = self.bot_manager._process_bot_command(internal_name, f"{internal_name} scan")
            self.bot_results.append(f"▶️ Ejecutando {bot_name}:\n{result}\n")
        except Exception as e:
            self.bot_results.append(f"❌ Error ejecutando {bot_name}: {str(e)}\n")

    def _send_test_notification(self):
        """Enviar notificación de prueba"""
        if self.notifications:
            try:
                self.notifications.send_notification(
                    message="¡Notificación de prueba desde BackendBot!",
                    priority="info",
                    channels=["desktop"]
                )
                QMessageBox.information(self, "Éxito", "Notificación enviada correctamente")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error enviando notificación: {str(e)}")

    def _change_power_profile(self, profile):
        """Cambiar perfil de energía"""
        if self.power_manager:
            try:
                profile_mapping = {
                    "Alto Rendimiento": "high_performance",
                    "Equilibrado": "balanced",
                    "Ahorro de Energía": "power_saver",
                    "Ultra Bajo": "ultra_low"
                }
                internal_profile = profile_mapping.get(profile, "balanced")
                self.power_manager.apply_profile(internal_profile)
                QMessageBox.information(self, "Éxito", f"Perfil de energía cambiado a: {profile}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error cambiando perfil: {str(e)}")

    def _create_backup(self):
        """Crear backup del sistema"""
        if self.backup_manager:
            try:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.backup_manager.create_backup(backup_name, strategy="incremental")
                QMessageBox.information(self, "Éxito", f"Backup creado: {backup_name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error creando backup: {str(e)}")

    def _send_chat_message(self):
        """Enviar mensaje de chat"""
        message = self.chat_input.toPlainText().strip()
        if not message:
            return

        # Mostrar mensaje del usuario
        self.chat_area.append(f"👤 Tú: {message}")

        # Procesar con bot manager
        try:
            response = self.bot_manager.process_command(message)
            self.chat_area.append(f"🤖 BackendBot: {response}")
        except Exception as e:
            self.chat_area.append(f"❌ Error: {str(e)}")

        # Limpiar input
        self.chat_input.clear()

    def _toggle_tray(self):
        """Alternar visibilidad del ícono de bandeja"""
        if self.tray_icon.isVisible():
            self.tray_icon.hide()
        else:
            self.tray_icon.show()

    def _show_chat_panel(self):
        """Mostrar panel de chat flotante"""
        # Crear panel de chat si no existe
        if not hasattr(self, 'chat_panel'):
            self.chat_panel = ChatPanel()
            self.chat_panel.command_signal.connect(self._process_chat_command)

        self.chat_panel.show()

    def _process_chat_command(self, command):
        """Procesar comando desde el panel de chat"""
        try:
            response = self.bot_manager.process_command(command)
            self.chat_panel.add_message("BackendBot", response)
        except Exception as e:
            self.chat_panel.add_message("Error", str(e))

    def _tray_activated(self, reason):
        """Manejar activación del ícono de bandeja"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()

    def _show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """
        🐝 BackendBot - Sistema Integrado Completo

        Versión: 2.0
        Arquitectura: SOLID completa
        Interfaz: PyQt5

        Sistemas incluidos:
        • Dashboard en tiempo real
        • 6 Bots especializados
        • Sistema de notificaciones
        • Gestión de energía
        • Sistema de backup
        • API REST completa
        • Chat interactivo

        ¡Todo funcionando desde una sola aplicación!
        """

        QMessageBox.about(self, "Acerca de BackendBot", about_text)

    def closeEvent(self, event):
        """Evento al cerrar la aplicación"""
        # Ocultar en bandeja en lugar de cerrar
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "BackendBot",
                "La aplicación se minimizó a la bandeja del sistema. Haz doble clic en el ícono para restaurar.",
                QSystemTrayIcon.Information,
                3000
            )
        else:
            # Detener hilos
            if hasattr(self, 'metrics_collector'):
                self.metrics_collector.stop()
                self.metrics_collector.wait()

            event.accept()

def main():
    """Función principal"""
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # No cerrar al cerrar ventanas

        # Crear aplicación integrada
        window = IntegratedDashboard()
        window.show()

        # Ejecutar aplicación
        sys.exit(app.exec_())

    except Exception as e:
        print(f"Error iniciando BackendBot Integrado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()