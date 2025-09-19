"""
BackendBot - Punto de entrada único
Aplicación de escritorio simple y eficiente
"""

import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from backendbot.ui.tray_icon import TrayIcon
from backendbot.ui.chat_panel import ChatPanel
from backendbot.bots.manager import BotManager
from backendbot.core.di.container import container


class BackendBot:
    """Aplicación principal BackendBot"""

    def __init__(self):
        self.logger = container.get_logger()
        self.config = container.get_config_manager()

        # Inicializar componentes
        self.tray = TrayIcon()
        self.chat = ChatPanel()
        self.bots = BotManager()

        self.logger.info("BackendBot inicializado", "Main")

    def run(self):
        """Ejecutar la aplicación"""
        try:
            # Mostrar componentes
            self.tray.show()
            self.chat.show()

            self.logger.info("BackendBot ejecutándose", "Main")

            # Mantener la aplicación corriendo
            # En una implementación completa, aquí iría el event loop

        except Exception as e:
            self.logger.error(f"Error ejecutando BackendBot: {e}", "Main")
            raise


def main():
    """Función principal"""
    try:
        # Crear aplicación Qt
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # Mantener en bandeja

        # Crear e iniciar BackendBot
        bot = BackendBot()
        bot.run()

        # Ejecutar event loop de Qt
        sys.exit(app.exec_())

    except KeyboardInterrupt:
        print("BackendBot detenido por usuario")
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()