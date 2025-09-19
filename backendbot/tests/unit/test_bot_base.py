"""
Tests unitarios para la clase base abstracta de bots.

Este módulo contiene tests exhaustivos para validar la funcionalidad
de la clase BaseBot y sus interfaces.

Author: BackendBot Team
Version: 1.0.0
"""

import threading
import time
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

from backendbot.packages.core.bot_base import (BaseBot, BotConfig,
                                               BotInterface, BotPriority,
                                               BotType, TaskResult)


class TestBot(BaseBot):
    """Bot de prueba para testing."""

    def __init__(self, config: BotConfig):
        super().__init__(config)
        self.executed_tasks = []

    def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Implementación de prueba."""
        task_id = task_data.get("task_id", "test_task")
        self.executed_tasks.append(task_data)

        # Simular procesamiento
        time.sleep(0.1)

        return TaskResult(
            task_id=task_id,
            success=True,
            result={"processed": True, "data": task_data},
            metadata={"bot_type": "test"},
        )

    def validate_task(self, task_data: Dict[str, Any]) -> bool:
        """Implementación de prueba."""
        return isinstance(task_data, dict) and "task_id" in task_data

    def get_supported_tasks(self) -> List[str]:
        """Implementación de prueba."""
        return ["test_task", "mock_task"]


class TestBotConfig:
    """Tests para BotConfig."""

    def test_bot_config_creation(self):
        """Test creación básica de configuración."""
        config = BotConfig(
            name="TestBot", type=BotType.MONITOR, priority=BotPriority.HIGH
        )

        assert config.name == "TestBot"
        assert config.type == BotType.MONITOR
        assert config.priority == BotPriority.HIGH
        assert config.max_concurrent_tasks == 5
        assert config.enabled is True
        assert config.metadata == {}

    def test_bot_config_with_metadata(self):
        """Test configuración con metadata."""
        metadata = {"version": "1.0", "author": "test"}
        config = BotConfig(name="TestBot", type=BotType.MONITOR, metadata=metadata)

        assert config.metadata == metadata

    def test_bot_config_post_init(self):
        """Test post_init method."""
        config = BotConfig(name="TestBot", type=BotType.MONITOR)
        assert config.metadata == {}


class TestTaskResult:
    """Tests para TaskResult."""

    def test_task_result_creation(self):
        """Test creación básica de resultado de tarea."""
        result = TaskResult(task_id="test_123", success=True, result={"data": "test"})

        assert result.task_id == "test_123"
        assert result.success is True
        assert result.result == {"data": "test"}
        assert result.error is None
        assert isinstance(result.timestamp, datetime)
        assert result.metadata == {}

    def test_task_result_with_error(self):
        """Test resultado con error."""
        result = TaskResult(task_id="test_123", success=False, error="Test error")

        assert result.success is False
        assert result.error == "Test error"
        assert result.result is None

    def test_task_result_post_init(self):
        """Test post_init method."""
        result = TaskResult(task_id="test_123", success=True)
        assert isinstance(result.timestamp, datetime)
        assert result.metadata == {}


class TestBaseBot:
    """Tests para BaseBot."""

    @pytest.fixture
    def test_config(self):
        """Fixture para configuración de prueba."""
        return BotConfig(
            name="TestBot",
            type=BotType.MONITOR,
            priority=BotPriority.NORMAL,
            max_concurrent_tasks=2,
        )

    @pytest.fixture
    def test_bot(self, test_config):
        """Fixture para bot de prueba."""
        return TestBot(test_config)

    def test_bot_initialization(self, test_bot, test_config):
        """Test inicialización del bot."""
        assert test_bot.config == test_config
        assert test_bot.status.name == "STOPPED"
        assert test_bot.get_running_tasks_count() == 0

    def test_bot_initialize_success(self, test_bot):
        """Test inicialización exitosa."""
        result = test_bot.initialize()
        assert result is True
        assert test_bot.status.name == "RUNNING"
        assert test_bot._executor is not None

    def test_bot_initialize_failure(self, test_config):
        """Test inicialización fallida."""
        with patch(
            "concurrent.futures.ThreadPoolExecutor", side_effect=Exception("Test error")
        ):
            bot = TestBot(test_config)
            result = bot.initialize()
            assert result is False
            assert bot.status.name == "ERROR"

    def test_bot_shutdown_success(self, test_bot):
        """Test apagado exitoso."""
        test_bot.initialize()
        result = test_bot.shutdown()
        assert result is True
        assert test_bot.status.name == "STOPPED"
        assert test_bot._executor is None

    def test_bot_shutdown_failure(self, test_bot):
        """Test apagado fallido."""
        test_bot.initialize()
        with patch.object(
            test_bot._executor, "shutdown", side_effect=Exception("Test error")
        ):
            result = test_bot.shutdown()
            assert result is False
            assert test_bot.status.name == "ERROR"

    def test_execute_task_async_success(self, test_bot):
        """Test ejecución asíncrona exitosa."""
        test_bot.initialize()

        task_data = {"task_id": "test_123", "data": "test"}
        task_id = test_bot.execute_task_async(task_data)

        assert task_id.startswith("TestBot_")
        assert test_bot.is_task_running(task_id)

        # Esperar a que termine
        time.sleep(0.2)
        assert not test_bot.is_task_running(task_id)
        assert len(test_bot.executed_tasks) == 1

    def test_execute_task_async_invalid_task(self, test_bot):
        """Test ejecución con tarea inválida."""
        test_bot.initialize()

        invalid_task_data = {"invalid": "data"}

        with pytest.raises(ValueError, match="Tarea inválida"):
            test_bot.execute_task_async(invalid_task_data)

    def test_execute_task_async_not_initialized(self, test_bot):
        """Test ejecución sin inicializar."""
        task_data = {"task_id": "test_123"}

        with pytest.raises(RuntimeError, match="no está inicializado"):
            test_bot.execute_task_async(task_data)

    def test_execute_task_async_with_callback(self, test_bot):
        """Test ejecución con callback."""
        test_bot.initialize()

        callback_mock = Mock()
        task_data = {"task_id": "test_123", "data": "test"}

        test_bot.execute_task_async(task_data, callback_mock)

        # Esperar a que termine
        time.sleep(0.2)

        # Verificar que el callback fue llamado
        callback_mock.assert_called_once()
        result = callback_mock.call_args[0][0]
        assert isinstance(result, TaskResult)
        assert result.success is True

    def test_task_validation(self, test_bot):
        """Test validación de tareas."""
        valid_task = {"task_id": "test_123"}
        invalid_task = {"invalid": "data"}

        assert test_bot.validate_task(valid_task) is True
        assert test_bot.validate_task(invalid_task) is False

    def test_get_supported_tasks(self, test_bot):
        """Test obtener tareas soportadas."""
        tasks = test_bot.get_supported_tasks()
        assert "test_task" in tasks
        assert "mock_task" in tasks

    def test_metrics_update(self, test_bot):
        """Test actualización de métricas."""
        test_bot.initialize()

        # Ejecutar tarea
        task_data = {"task_id": "test_123"}
        test_bot.execute_task_async(task_data)

        time.sleep(0.2)

        metrics = test_bot.metrics
        assert metrics.tasks_completed == 1
        assert metrics.tasks_failed == 0
        assert metrics.average_execution_time > 0

    def test_concurrent_tasks_limit(self, test_bot):
        """Test límite de tareas concurrentes."""
        test_bot.initialize()

        # Ejecutar múltiples tareas
        tasks = []
        for i in range(5):
            task_data = {"task_id": f"test_{i}"}
            task_id = test_bot.execute_task_async(task_data)
            tasks.append(task_id)

        # Verificar que no exceda el límite configurado
        assert (
            test_bot.get_running_tasks_count() <= test_bot.config.max_concurrent_tasks
        )

        # Esperar a que terminen
        time.sleep(1)
        assert test_bot.get_running_tasks_count() == 0

    def test_task_callbacks(self, test_bot):
        """Test sistema de callbacks."""
        callback1 = Mock()
        callback2 = Mock()

        test_bot.add_task_callback(callback1)
        test_bot.add_task_callback(callback2)

        assert len(test_bot._task_callbacks) == 2

        test_bot.remove_task_callback(callback1)
        assert len(test_bot._task_callbacks) == 1

        test_bot.remove_task_callback(callback2)
        assert len(test_bot._task_callbacks) == 0

    def test_cleanup_completed_tasks(self, test_bot):
        """Test limpieza de tareas completadas."""
        test_bot.initialize()

        # Ejecutar tarea
        task_data = {"task_id": "test_123"}
        task_id = test_bot.execute_task_async(task_data)

        assert test_bot.is_task_running(task_id)

        # Esperar a que termine y limpiar
        time.sleep(0.2)
        test_bot._cleanup_completed_tasks()

        assert not test_bot.is_task_running(task_id)

    def test_shutdown_event_handling(self, test_bot):
        """Test manejo del evento de shutdown."""
        test_bot.initialize()
        assert not test_bot._shutdown_event.is_set()

        test_bot.shutdown()
        assert test_bot._shutdown_event.is_set()

    @pytest.mark.parametrize(
        "bot_type", [BotType.MONITOR, BotType.ORGANIZER, BotType.INDEXER]
    )
    def test_different_bot_types(self, bot_type):
        """Test diferentes tipos de bot."""
        config = BotConfig(name="TestBot", type=bot_type)
        bot = TestBot(config)

        assert bot.config.type == bot_type


class TestBotInterface:
    """Tests para verificar que BaseBot implementa BotInterface correctamente."""

    def test_implements_bot_interface(self):
        """Test que BaseBot implementa BotInterface."""
        config = BotConfig(name="TestBot", type=BotType.MONITOR)
        bot = TestBot(config)

        # Verificar que tiene todos los métodos requeridos
        assert hasattr(bot, "config")
        assert hasattr(bot, "status")
        assert hasattr(bot, "metrics")
        assert hasattr(bot, "initialize")
        assert hasattr(bot, "shutdown")
        assert hasattr(bot, "execute_task")
        assert hasattr(bot, "validate_task")
        assert hasattr(bot, "get_supported_tasks")

        # Verificar que son del tipo correcto
        assert isinstance(bot.config, BotConfig)
        assert isinstance(bot.status, type(bot.status))  # Enum
        assert isinstance(bot.metrics, type(bot.metrics))  # Dataclass

    def test_abstract_methods_not_implemented_in_base(self):
        """Test que los métodos abstractos no están implementados en la clase base."""
        # Esto debería fallar si intentamos instanciar BotInterface directamente
        with pytest.raises(TypeError):
            BotInterface()


if __name__ == "__main__":
    pytest.main([__file__])
