"""BackendBot - Aplicación de escritorio simple y eficiente
Punto de entrada único para la aplicación desktop pura.
"""

import os
import sys

from PyQt5.QtWidgets import QApplication

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backendbot.bots.manager import BotManager
from backendbot.core.di.container import container
from backendbot.ui.chat_panel import ChatPanel
from backendbot.ui.tray_icon import TrayIcon

# Exponer una app mínima de FastAPI para compatibilidad con tests y orquestación ligera
try:
    # Prefer re-exporting the API app from core to ensure routers are included
    from backendbot.core.main import app as app
except Exception:
    app = None


class BackendBot:
    """Aplicación principal de BackendBot - 100% desktop."""

    def __init__(self) -> None:
        # Inicializar contenedor de dependencias
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()

        self.logger.info("Inicializando BackendBot", "Main")

        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # No cerrar al cerrar ventanas

        # Componentes principales
        self.tray = TrayIcon()
        self.chat = ChatPanel()
        self.bots = BotManager()

        # Conectar señales
        self._connect_signals()

        self.logger.info("BackendBot inicializado correctamente", "Main")

    def _connect_signals(self):
        """Conectar señales entre componentes."""
        # El tray icon controla mostrar/ocultar el chat
        self.tray.show_chat_signal.connect(self.chat.show)
        self.tray.hide_chat_signal.connect(self.chat.hide)

        # El chat procesa comandos a través de los bots
        self.chat.command_signal.connect(self._process_command)

    def _process_command(self, command):
        """Procesar comando del usuario."""
        try:
            self.logger.info(f"Procesando comando: {command}", "Main")
            response = self.bots.process_command(command)
            self.chat.add_message("BackendBot", response)

            # Guardar en el repositorio de datos
            self.data_repo.save_bot_action(
                bot_name="System",
                action_type="command",
                status="completed",
                target=command,
                result=response,
            )

        except Exception as e:
            error_msg = f"Error procesando comando: {str(e)}"
            self.logger.error(error_msg, "Main")
            self.chat.add_message("Error", error_msg)

            # Guardar error en el repositorio
            self.data_repo.save_system_event(
                level="ERROR", source="Main", message=error_msg, details=str(e)
            )

    def run(self):
        """Ejecutar la aplicación."""
        # Mostrar tray icon
        self.tray.show()

        # Iniciar aplicación Qt
        return self.app.exec_()


def main():
    """Función principal."""
    try:
        bot = BackendBot()
        sys.exit(bot.run())
    except Exception as e:
        print(f"Error iniciando BackendBot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
