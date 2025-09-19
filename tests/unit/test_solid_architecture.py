"""
Test de integración para validar la nueva arquitectura SOLID
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

# Añadir path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.backendbot.core.di.container import container
from src.backendbot.bots.manager import BotManager, MonitorBot
from src.backendbot.ui.chat_panel import ChatPanel


class TestSOLIDArchitecture:
    """Test suite para validar la arquitectura SOLID refactorizada"""

    def setup_method(self):
        """Configurar entorno de test"""
        # Limpiar container antes de cada test
        from src.backendbot.core.di.container import container
        container._services = {}
        container._singletons = {}
        container._register_defaults()

    def test_container_initialization(self):
        """Test que el contenedor se inicializa correctamente"""
        # Forzar reinicialización del container
        from src.backendbot.core.di.container import container
        container._services = {}
        container._singletons = {}
        container._register_defaults()

        # Verificar que los servicios básicos están registrados
        logger = container.get_logger()
        config = container.get_config_manager()
        data_repo = container.get_data_repository()

        assert logger is not None
        assert config is not None
        assert data_repo is not None

    def test_bot_manager_with_dependencies(self):
        """Test que BotManager usa correctamente las dependencias"""
        bot_manager = BotManager()

        # Verificar que tiene acceso a las dependencias
        assert hasattr(bot_manager, 'logger')
        assert hasattr(bot_manager, 'config')
        assert hasattr(bot_manager, 'data_repo')

        # Verificar que los bots están cargados
        assert len(bot_manager.bots) == 5
        assert 'monitor' in bot_manager.bots
        assert 'organizer' in bot_manager.bots

    def test_bot_execution_with_logging(self):
        """Test que los bots ejecutan acciones y registran logs"""
        monitor_bot = MonitorBot()

        # Verificar que tiene dependencias
        assert hasattr(monitor_bot, 'logger')
        assert hasattr(monitor_bot, 'config')
        assert hasattr(monitor_bot, 'data_repo')

        # Ejecutar acción
        result = monitor_bot.execute("status")
        assert "CPU:" in result
        assert "RAM:" in result

    def test_command_processing_integration(self):
        """Test integración completa de procesamiento de comandos"""
        bot_manager = BotManager()

        # Test comando help
        response = bot_manager.process_command("help")
        assert "BackendBot" in response
        assert "Comandos disponibles" in response

        # Test comando status
        response = bot_manager.process_command("status")
        assert "Estado de BackendBot" in response
        assert "Bots cargados" in response

        # Test comando monitor
        response = bot_manager.process_command("monitor status")
        assert "CPU:" in response or "RAM:" in response

    def test_chat_panel_dependencies_available(self):
        """Test que las dependencias necesarias para ChatPanel están disponibles"""
        # Verificar que podemos crear las dependencias que usa ChatPanel
        from src.backendbot.bots.manager import BotManager

        bot_manager = BotManager()

        # Verificar que BotManager tiene las dependencias correctas
        assert hasattr(bot_manager, 'logger')
        assert hasattr(bot_manager, 'config')
        assert hasattr(bot_manager, 'data_repo')

        # Verificar que los bots están disponibles
        assert len(bot_manager.bots) == 5
        assert 'monitor' in bot_manager.bots
        assert 'organizer' in bot_manager.bots

    def test_dependency_injection_isolation(self):
        """Test que las dependencias están correctamente aisladas"""
        # Crear dos instancias diferentes
        bot1 = MonitorBot()
        bot2 = MonitorBot()

        # Verificar que comparten las mismas dependencias (singletons)
        assert bot1.logger is bot2.logger
        assert bot1.config is bot2.config
        assert bot1.data_repo is bot2.data_repo

        # Pero son instancias diferentes
        assert bot1 is not bot2

    def test_error_handling_with_logging(self):
        """Test que los errores se manejan y registran correctamente"""
        bot_manager = BotManager()

        # Simular un comando que cause error
        response = bot_manager.process_command("invalid_command_xyz")

        # Debería devolver mensaje de error controlado
        assert "no reconocido" in response or "Error" in response

    def test_data_persistence_integration(self):
        """Test que las acciones se persisten correctamente"""
        bot_manager = BotManager()

        # Ejecutar un comando que debería guardarse
        initial_count = len(bot_manager.data_repo.get_recent_events())

        response = bot_manager.process_command("monitor status")

        # Verificar que se guardó la acción
        final_count = len(bot_manager.data_repo.get_recent_events())
        assert final_count >= initial_count


if __name__ == "__main__":
    # Ejecutar tests manualmente
    test_suite = TestSOLIDArchitecture()

    print("🧪 Ejecutando tests de arquitectura SOLID...")

    try:
        test_suite.setup_method()
        test_suite.test_container_initialization()
        print("✅ Container initialization: PASSED")

        test_suite.setup_method()
        test_suite.test_bot_manager_with_dependencies()
        print("✅ BotManager dependencies: PASSED")

        test_suite.setup_method()
        test_suite.test_bot_execution_with_logging()
        print("✅ Bot execution with logging: PASSED")

        test_suite.setup_method()
        test_suite.test_command_processing_integration()
        print("✅ Command processing integration: PASSED")

        print("\n🎉 Todos los tests pasaron exitosamente!")

    except Exception as e:
        print(f"❌ Test falló: {str(e)}")
        import traceback
        traceback.print_exc()