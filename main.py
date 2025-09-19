"""
BackendBot - Punto de entrada único con mejores prácticas modernas de DI
Aplicación de escritorio simple y eficiente con arquitectura SOLID avanzada
"""

import sys
import os
from typing import Optional

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication

# Ensure .env is loaded early
try:
    from backendbot.core.env import ensure_loaded
    ensure_loaded()
except Exception:
    # Keep startup tolerant if env helper is missing or fails
    pass

# Importar contenedor moderno con wiring
from backendbot.core.di.enhanced_container import ModernDependencyInjectionContainer
from backendbot.core.di.container import container as legacy_container, ServiceFactory

# Importar configuración avanzada
from backendbot.core.config.advanced_config import AdvancedConfiguration

# Importar servicios con wiring
from backendbot.ui.tray_icon import TrayIcon
from backendbot.ui.chat_panel import ChatPanel
from backendbot.bots.manager import BotManager
from backendbot.core.services.logger_service import LoggerService
from backendbot.core.services.config_service import ConfigService

# Wiring imports para inyección automática
from dependency_injector.wiring import inject, Provide


class BackendBot:
    """Aplicación principal BackendBot con DI moderna"""

    @inject
    def __init__(
        self,
        logger: LoggerService = Provide['logger_service'],
        config: ConfigService = Provide['config_service'],
        tray_icon: Optional[TrayIcon] = None,
        chat_panel: Optional[ChatPanel] = None,
        bot_manager: Optional[BotManager] = None
    ):
        """
        Inicializar BackendBot con inyección de dependencias moderna

        Args:
            logger: Servicio de logging inyectado
            config: Servicio de configuración inyectado
            tray_icon: Icono de bandeja (opcional para compatibilidad)
            chat_panel: Panel de chat (opcional para compatibilidad)
            bot_manager: Gestor de bots (opcional para compatibilidad)
        """
        self.logger = logger
        self.config = config

        # Mantener compatibilidad con factories legacy si no se inyectan
        if tray_icon is None:
            factory = ServiceFactory(legacy_container)
            self.tray = factory.create_tray_icon()
            self.chat = factory.create_chat_panel()
            self.bots = factory.create_bot_manager()
        else:
            self.tray = tray_icon
            self.chat = chat_panel
            self.bots = bot_manager

        try:
            self.logger.info("BackendBot inicializado con arquitectura SOLID moderna")
        except Exception:
            # Logging should never break startup
            pass

    def run(self):
        """Ejecutar la aplicación"""
        try:
            # Mostrar componentes
            self.tray.show()
            self.chat.show()

            self.logger.info("BackendBot ejecutándose con DI moderna", "Main")

            # Mantener la aplicación corriendo
            # En una implementación completa, aquí iría el event loop

        except Exception as e:
            self.logger.error(f"Error ejecutando BackendBot: {e}", "Main")
            raise


@inject
def main(
    container: ModernDependencyInjectionContainer = Provide['container']
):
    """
    Función principal con inyección de contenedor moderno

    Args:
        container: Contenedor de DI moderno inyectado
    """
    try:
        # Inicializar contenedor moderno
        container.init_resources()

        # Crear aplicación Qt
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # Mantener en bandeja

        # Crear e iniciar BackendBot con DI moderna
        bot = BackendBot()
        bot.run()

        # Ejecutar event loop de Qt
        sys.exit(app.exec_())

    except KeyboardInterrupt:
        print("BackendBot detenido por usuario")
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)
    finally:
        # Limpiar recursos del contenedor
        if 'container' in locals():
            container.shutdown_resources()


    if __name__ == "__main__":
    # Configurar wiring para inyección automática
    # from dependency_injector.wiring import register
    # register(...)  # Comentado por compatibilidad

    main()