"""Módulo para el icono de bandeja del sistema usando PyQt5.
Permite cambiar color según estado y mostrar menú contextual.
"""

import os
import sys

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

# Añadir path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backendbot.core.di.container import container


class TrayIcon(QtWidgets.QSystemTrayIcon):
    """Icono de bandeja del sistema con integración de dependencias."""

    # Señales esperadas por la app
    show_chat_signal = pyqtSignal()
    hide_chat_signal = pyqtSignal()

    def __init__(self, icon_active=None, icon_inactive=None, parent=None) -> None:
        # Inicializar dependencias
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()

        # Proveer iconos por defecto si no se pasan
        if icon_active is None:
            # Crear ícono rojo usando Qt
            pixmap = QtGui.QPixmap(32, 32)
            pixmap.fill(QtGui.QColor(255, 0, 0))  # Rojo
            icon_active = QtGui.QIcon(pixmap)
        if icon_inactive is None:
            # Crear ícono gris usando Qt
            pixmap = QtGui.QPixmap(32, 32)
            pixmap.fill(QtGui.QColor(128, 128, 128))  # Gris
            icon_inactive = QtGui.QIcon(pixmap)

        super().__init__(icon_active, parent)
        self.icon_active = icon_active
        self.icon_inactive = icon_inactive

        # Configurar menú contextual
        self._setup_menu()

        # Conectar señales
        self.activated.connect(self.on_click)
        self._panel_visible = False

        # Log de inicialización
        self.logger.info("TrayIcon inicializado correctamente", "TrayIcon")

    def _setup_menu(self):
        """Configurar menú contextual del icono de bandeja."""
        try:
            self.menu = QtWidgets.QMenu()

            # Acción para abrir/cerrar panel
            self.open_action = self.menu.addAction("Abrir panel", self.open_panel)
            self.menu.addSeparator()

            # Acción para mostrar estado
            self.status_action = self.menu.addAction(
                "Estado del sistema", self.show_status
            )
            self.menu.addSeparator()

            # Acción para salir
            self.quit_action = self.menu.addAction("Salir", QtWidgets.qApp.quit)

            self.setContextMenu(self.menu)

            self.logger.debug("Menú contextual configurado", "TrayIcon")

        except Exception as e:
            self.logger.error(f"Error configurando menú: {str(e)}", "TrayIcon")

    def set_active(self, active: bool):
        """Cambiar estado del icono."""
        try:
            self.setIcon(self.icon_active if active else self.icon_inactive)

            # Log del cambio de estado
            status = "activo" if active else "inactivo"
            self.logger.debug(f"Icono cambiado a estado: {status}", "TrayIcon")

        except Exception as e:
            self.logger.error(f"Error cambiando estado del icono: {str(e)}", "TrayIcon")

    def open_panel(self):
        """Alternar visibilidad del panel de chat."""
        try:
            if not self._panel_visible:
                # Mostrar panel
                self.show_chat_signal.emit()
                self._panel_visible = True
                self.open_action.setText("Cerrar panel")

                # Log
                self.logger.info("Panel de chat mostrado desde bandeja", "TrayIcon")

                # Guardar evento
                self.data_repo.save_system_event(
                    level="INFO",
                    source="TrayIcon",
                    message="Panel de chat abierto desde bandeja",
                    details="Usuario activó panel desde icono de bandeja",
                )

            else:
                # Ocultar panel
                self.hide_chat_signal.emit()
                self._panel_visible = False
                self.open_action.setText("Abrir panel")

                # Log
                self.logger.info("Panel de chat ocultado desde bandeja", "TrayIcon")

        except Exception as e:
            error_msg = f"Error alternando panel: {str(e)}"
            self.logger.error(error_msg, "TrayIcon")

            # Guardar error
            self.data_repo.save_system_event(
                level="ERROR", source="TrayIcon", message=error_msg, details=str(e)
            )

    def show_status(self):
        """Mostrar estado del sistema en un mensaje."""
        try:
            # Obtener estado básico del sistema
            import psutil

            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()

            status_msg = f"BackendBot Activo\nCPU: {cpu}%\nMemoria: {memory.percent}%"

            # Mostrar mensaje en bandeja
            self.showMessage(
                "Estado de BackendBot",
                status_msg,
                QtWidgets.QSystemTrayIcon.Information,
                3000,  # 3 segundos
            )

            # Log
            self.logger.info("Estado del sistema mostrado en bandeja", "TrayIcon")

        except Exception as e:
            error_msg = f"Error mostrando estado: {str(e)}"
            self.logger.error(error_msg, "TrayIcon")

    def on_click(self, reason):
        """Manejar clic en el icono de bandeja."""
        try:
            if reason == QtWidgets.QSystemTrayIcon.Trigger:
                self.open_panel()

                # Log del clic
                self.logger.debug("Clic en icono de bandeja procesado", "TrayIcon")

        except Exception as e:
            self.logger.error(f"Error procesando clic: {str(e)}", "TrayIcon")


if __name__ == "__main__":
    """Para testing independiente"""
    app = QtWidgets.QApplication(sys.argv)
    icon_active = QtGui.QIcon("icono_rojo.png")
    icon_inactive = QtGui.QIcon("icono_gris.png")
    tray = TrayIcon(icon_active, icon_inactive)
    tray.show()
    sys.exit(app.exec_())
