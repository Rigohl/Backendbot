#!/usr/bin/env python3
"""
Dashboard Interactivo - BackendBot
Panel de control con gráficos en tiempo real y widgets configurables
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
                             QPushButton, QComboBox, QCheckBox)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backendbot.core.di.container import container

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
                memory_percent = memory.percent

                # Disco
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent

                # Red
                network = psutil.net_io_counters()
                network_sent = network.bytes_sent
                network_recv = network.bytes_recv

                # Batería
                battery = psutil.sensors_battery()
                battery_percent = battery.percent if battery else None

                # Temperatura (si disponible)
                temperature = None
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Tomar la primera temperatura disponible
                        for sensor_name, sensor_data in temps.items():
                            if sensor_data:
                                temperature = sensor_data[0].current
                                break
                except:
                    pass

                metrics = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    disk_percent=disk_percent,
                    network_sent=network_sent,
                    network_recv=network_recv,
                    battery_percent=battery_percent,
                    temperature=temperature
                )

                self.metrics_updated.emit(metrics)

            except Exception as e:
                print(f"Error recolectando métricas: {e}")

            self.sleep(2)  # Actualizar cada 2 segundos

    def stop(self):
        self.running = False

class DashboardWidget(QGroupBox):
    """Widget base para el dashboard"""

    def __init__(self, title: str):
        super().__init__(title)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)

class SystemMonitorWidget(DashboardWidget):
    """Widget de monitoreo del sistema"""

    def __init__(self):
        super().__init__("📊 Monitoreo del Sistema")

        layout = QVBoxLayout()

        # CPU
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)

        # Memoria
        self.memory_label = QLabel("Memoria: 0%")
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        layout.addWidget(self.memory_label)
        layout.addWidget(self.memory_bar)

        # Disco
        self.disk_label = QLabel("Disco: 0%")
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.disk_bar)

        # Batería
        self.battery_label = QLabel("Batería: N/A")
        layout.addWidget(self.battery_label)

        # Temperatura
        self.temp_label = QLabel("Temperatura: N/A")
        layout.addWidget(self.temp_label)

        self.setLayout(layout)

    def update_metrics(self, metrics: SystemMetrics):
        """Actualiza las métricas mostradas"""
        self.cpu_label.setText(f"CPU: {metrics.cpu_percent:.1f}%")
        self.cpu_bar.setValue(int(metrics.cpu_percent))

        self.memory_label.setText(f"Memoria: {metrics.memory_percent:.1f}%")
        self.memory_bar.setValue(int(metrics.memory_percent))

        self.disk_label.setText(f"Disco: {metrics.disk_percent:.1f}%")
        self.disk_bar.setValue(int(metrics.disk_percent))

        if metrics.battery_percent is not None:
            self.battery_label.setText(f"Batería: {metrics.battery_percent:.1f}%")
        else:
            self.battery_label.setText("Batería: N/A")

        if metrics.temperature is not None:
            self.temp_label.setText(f"Temperatura: {metrics.temperature:.1f}°C")
        else:
            self.temp_label.setText("Temperatura: N/A")

class BotStatusWidget(DashboardWidget):
    """Widget de estado de los bots"""

    def __init__(self):
        super().__init__("🤖 Estado de Bots")

        layout = QVBoxLayout()

        self.bot_list = QListWidget()
        self.bot_list.addItem("🔴 Monitor Bot - Inactivo")
        self.bot_list.addItem("🔴 Organizer Bot - Inactivo")
        self.bot_list.addItem("🔴 Indexer Bot - Inactivo")
        self.bot_list.addItem("🔴 Guardian Bot - Inactivo")
        self.bot_list.addItem("🔴 Optimizer Bot - Inactivo")

        layout.addWidget(self.bot_list)

        # Botones de control
        controls_layout = QHBoxLayout()

        self.start_all_btn = QPushButton("▶️ Iniciar Todos")
        self.stop_all_btn = QPushButton("⏹️ Detener Todos")
        self.restart_all_btn = QPushButton("🔄 Reiniciar Todos")

        controls_layout.addWidget(self.start_all_btn)
        controls_layout.addWidget(self.stop_all_btn)
        controls_layout.addWidget(self.restart_all_btn)

        layout.addLayout(controls_layout)
        self.setLayout(layout)

    def update_bot_status(self, bot_name: str, status: str):
        """Actualiza el estado de un bot"""
        for i in range(self.bot_list.count()):
            item = self.bot_list.item(i)
            if bot_name.lower() in item.text().lower():
                if status == "running":
                    item.setText(f"🟢 {bot_name} - Activo")
                elif status == "stopped":
                    item.setText(f"🔴 {bot_name} - Inactivo")
                elif status == "error":
                    item.setText(f"🟡 {bot_name} - Error")
                break

class NotificationWidget(DashboardWidget):
    """Widget de notificaciones recientes"""

    def __init__(self):
        super().__init__("🔔 Notificaciones Recientes")

        layout = QVBoxLayout()

        self.notification_list = QListWidget()
        self.notification_list.addItem("Sistema inicializado correctamente")
        self.notification_list.addItem("Monitoreo activado")

        layout.addWidget(self.notification_list)

        # Controles
        controls_layout = QHBoxLayout()
        self.clear_btn = QPushButton("🗑️ Limpiar")
        self.settings_btn = QPushButton("⚙️ Configurar")

        controls_layout.addWidget(self.clear_btn)
        controls_layout.addWidget(self.settings_btn)

        layout.addLayout(controls_layout)
        self.setLayout(layout)

    def add_notification(self, message: str, priority: str = "info"):
        """Agrega una nueva notificación"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "success": "✅"}.get(priority, "ℹ️")
        self.notification_list.insertItem(0, f"{icon} [{timestamp}] {message}")

        # Mantener solo las últimas 20 notificaciones
        while self.notification_list.count() > 20:
            self.notification_list.takeItem(self.notification_list.count() - 1)

class PowerManagementWidget(DashboardWidget):
    """Widget de gestión de energía"""

    def __init__(self):
        super().__init__("⚡ Gestión de Energía")

        layout = QVBoxLayout()

        # Perfil actual
        self.profile_label = QLabel("Perfil actual: Equilibrado")
        layout.addWidget(self.profile_label)

        # Selector de perfil
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Cambiar perfil:"))

        self.profile_combo = QComboBox()
        self.profile_combo.addItems([
            "Alto Rendimiento",
            "Equilibrado",
            "Ahorro de Energía",
            "Ultra Bajo Consumo"
        ])
        profile_layout.addWidget(self.profile_combo)

        self.apply_profile_btn = QPushButton("Aplicar")
        profile_layout.addWidget(self.apply_profile_btn)

        layout.addLayout(profile_layout)

        # Estado de batería
        self.battery_label = QLabel("Batería: N/A")
        layout.addWidget(self.battery_label)

        # Auto-switch
        self.auto_switch_check = QCheckBox("Cambio automático de perfil")
        self.auto_switch_check.setChecked(True)
        layout.addWidget(self.auto_switch_check)

        self.setLayout(layout)

class BackupWidget(DashboardWidget):
    """Widget de gestión de backups"""

    def __init__(self):
        super().__init__("💾 Gestión de Backups")

        layout = QVBoxLayout()

        # Estado del último backup
        self.last_backup_label = QLabel("Último backup: Nunca")
        layout.addWidget(self.last_backup_label)

        # Botones de backup
        backup_layout = QHBoxLayout()

        self.config_backup_btn = QPushButton("📁 Backup Config")
        self.documents_backup_btn = QPushButton("📄 Backup Documentos")
        self.full_backup_btn = QPushButton("💽 Backup Completo")

        backup_layout.addWidget(self.config_backup_btn)
        backup_layout.addWidget(self.documents_backup_btn)
        backup_layout.addWidget(self.full_backup_btn)

        layout.addLayout(backup_layout)

        # Progreso
        self.backup_progress = QProgressBar()
        self.backup_progress.setRange(0, 100)
        self.backup_progress.setValue(0)
        layout.addWidget(self.backup_progress)

        # Historial
        self.backup_history = QListWidget()
        layout.addWidget(self.backup_history)

        self.setLayout(layout)

class BackendBotDashboard(QMainWindow):
    """Dashboard principal de BackendBot"""

    def __init__(self):
        super().__init__()
        self.logger = container.get_logger()
        self.config = container.get_config_manager()

        self.setWindowTitle("BackendBot Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        # Configurar ícono
        icon_path = os.path.join(os.path.dirname(__file__), 'ui', 'icons', 'backendbot.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Configurar tema
        self.setup_theme()

        # Inicializar componentes
        self.metrics_collector = MetricsCollector()
        self.metrics_collector.metrics_updated.connect(self.update_metrics)

        # Crear interfaz
        self.setup_ui()

        # Iniciar recolección de métricas
        self.metrics_collector.start()

        # Timer para actualizaciones periódicas
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.periodic_update)
        self.update_timer.start(5000)  # Actualizar cada 5 segundos

        self.logger.info("Dashboard inicializado")

    def setup_theme(self):
        """Configura el tema de la aplicación"""
        theme = self.config.get('ui.theme', 'system')

        if theme == 'dark':
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            self.setPalette(palette)

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Crear tabs
        self.tab_widget = QTabWidget()

        # Tab principal
        main_tab = QWidget()
        main_layout_tab = QGridLayout(main_tab)

        # Widgets del dashboard
        self.system_monitor = SystemMonitorWidget()
        self.bot_status = BotStatusWidget()
        self.notifications = NotificationWidget()

        main_layout_tab.addWidget(self.system_monitor, 0, 0)
        main_layout_tab.addWidget(self.bot_status, 0, 1)
        main_layout_tab.addWidget(self.notifications, 1, 0, 1, 2)

        self.tab_widget.addTab(main_tab, "📊 Dashboard")

        # Tab de energía
        power_tab = QWidget()
        power_layout = QVBoxLayout(power_tab)
        self.power_widget = PowerManagementWidget()
        power_layout.addWidget(self.power_widget)
        self.tab_widget.addTab(power_tab, "⚡ Energía")

        # Tab de backups
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        self.backup_widget = BackupWidget()
        backup_layout.addWidget(self.backup_widget)
        self.tab_widget.addTab(backup_tab, "💾 Backups")

        # Tab de configuración
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)

        self.config_text = QTextEdit()
        self.config_text.setPlainText("Configuración del sistema...")
        config_layout.addWidget(self.config_text)

        save_config_btn = QPushButton("💾 Guardar Configuración")
        config_layout.addWidget(save_config_btn)

        self.tab_widget.addTab(config_tab, "⚙️ Configuración")

        main_layout.addWidget(self.tab_widget)

        # Barra de estado
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("BackendBot Dashboard - Sistema operativo")

    def update_metrics(self, metrics: SystemMetrics):
        """Actualiza las métricas en todos los widgets"""
        self.system_monitor.update_metrics(metrics)

    def periodic_update(self):
        """Actualizaciones periódicas"""
        # Actualizar estado de bots (simulado)
        self.bot_status.update_bot_status("Monitor Bot", "running")
        self.bot_status.update_bot_status("Guardian Bot", "running")

        # Agregar notificación de ejemplo
        if hasattr(self, 'notification_count'):
            self.notification_count += 1
        else:
            self.notification_count = 1

        if self.notification_count % 10 == 0:  # Cada 50 segundos
            self.notifications.add_notification(
                f"Actualización del sistema #{self.notification_count}",
                "info"
            )

    def closeEvent(self, event):
        """Evento de cierre de la aplicación"""
        self.metrics_collector.stop()
        self.metrics_collector.wait()
        self.logger.info("Dashboard cerrado")
        event.accept()

def main():
    """Función principal del dashboard"""
    app = QApplication(sys.argv)
    app.setApplicationName("BackendBot Dashboard")
    app.setApplicationVersion("2.0.0")

    # Configurar fuente
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    # Crear y mostrar dashboard
    dashboard = BackendBotDashboard()
    dashboard.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()