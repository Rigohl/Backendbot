"""
Tests para Monitor Worker
=========================

Tests unitarios siguiendo metodología TDD para MonitorWorker.
Pruebas de funcionalidad de monitoreo, alertas y threading.

Autor: BackendBot Team
Versión: 0.1.0
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from backendbot.packages.bots.base_bot import BotState
from backendbot.packages.bots.monitor_worker import MonitorWorker
from backendbot.packages.models.models import SystemMetrics


class TestMonitorWorker:
    """Tests para MonitorWorker."""

    @pytest.fixture
    def monitor_worker(self):
        """Fixture para crear instancia de MonitorWorker."""
        worker = MonitorWorker(bot_id="test-monitor", name="Test Monitor")
        yield worker
        # Cleanup
        if worker.state == BotState.RUNNING:
            worker.stop()

    def test_initialization(self, monitor_worker):
        """Test inicialización correcta del MonitorWorker."""
        assert monitor_worker.bot_id == "test-monitor"
        assert monitor_worker.name == "Test Monitor"
        assert monitor_worker.monitoring_interval == 30
        assert monitor_worker.alert_thresholds["cpu_percent"] == 80.0
        assert monitor_worker.alert_thresholds["memory_percent"] == 85.0
        assert monitor_worker.alert_thresholds["disk_percent"] == 90.0
        assert monitor_worker.last_metrics is None
        assert len(monitor_worker.metrics_history) == 0
        assert len(monitor_worker.alerts) == 0

    def test_config_validation_valid(self, monitor_worker):
        """Test validación de configuración válida."""
        valid_config = {
            "monitoring_interval": 60,
            "alert_thresholds": {
                "cpu_percent": 90.0,
                "memory_percent": 80.0,
                "disk_percent": 85.0,
            },
        }
        assert monitor_worker.validate_config(valid_config)

    def test_config_validation_invalid_missing_keys(self, monitor_worker):
        """Test validación de configuración con claves faltantes."""
        invalid_config = {"monitoring_interval": 30}  # Falta alert_thresholds
        assert not monitor_worker.validate_config(invalid_config)

    def test_config_validation_invalid_interval(self, monitor_worker):
        """Test validación de configuración con intervalo inválido."""
        invalid_config = {
            "monitoring_interval": 0,  # Debe ser >= 1
            "alert_thresholds": {"cpu_percent": 80.0},
        }
        assert not monitor_worker.validate_config(invalid_config)

    def test_should_run_in_background(self, monitor_worker):
        """Test que el worker debe ejecutarse en background."""
        assert monitor_worker.should_run_in_background() is True

    def test_get_execution_interval(self, monitor_worker):
        """Test obtener intervalo de ejecución."""
        assert monitor_worker.get_execution_interval() == 30

    @patch("backendbot.packages.bots.monitor_worker.psutil.cpu_percent")
    @patch("backendbot.packages.bots.monitor_worker.psutil.virtual_memory")
    @patch("backendbot.packages.bots.monitor_worker.psutil.disk_usage")
    def test_collect_system_metrics(
        self, mock_disk, mock_memory, mock_cpu, monitor_worker
    ):
        """Test recopilación de métricas del sistema."""
        # Configurar mocks
        mock_cpu.return_value = 45.5
        mock_memory.return_value = Mock(percent=67.8)
        mock_disk.return_value = Mock(percent=72.3)

        metrics = monitor_worker._collect_system_metrics()

        assert isinstance(metrics, SystemMetrics)
        assert metrics.cpu_usage == 45.5
        assert metrics.memory_usage == 67.8
        assert metrics.disk_usage == 72.3
        assert metrics.network_io is None  # No habilitado por defecto

    @patch("backendbot.packages.bots.monitor_worker.psutil.cpu_percent")
    @patch("backendbot.packages.bots.monitor_worker.psutil.virtual_memory")
    @patch("backendbot.packages.bots.monitor_worker.psutil.disk_usage")
    def test_execute_task_success(
        self, mock_disk, mock_memory, mock_cpu, monitor_worker
    ):
        """Test ejecución exitosa de tarea."""
        # Configurar mocks
        mock_cpu.return_value = 45.5
        mock_memory.return_value = Mock(percent=67.8)
        mock_disk.return_value = Mock(percent=72.3)

        result = monitor_worker.execute_task()

        assert result["success"] is True
        assert "metrics" in result
        assert "alerts_count" in result
        assert "timestamp" in result
        assert result["metrics"]["cpu_usage"] == 45.5
        assert result["metrics"]["memory_usage"] == 67.8
        assert result["metrics"]["disk_usage"] == 72.3

    def test_execute_task_error_handling(self, monitor_worker):
        """Test manejo de errores en ejecución de tarea."""
        with patch.object(
            monitor_worker,
            "_collect_system_metrics",
            side_effect=Exception("Test error"),
        ):
            result = monitor_worker.execute_task()

            assert result["success"] is False
            assert "error" in result
            assert result["error"] == "Test error"

    @patch("backendbot.packages.bots.monitor_worker.psutil.cpu_percent")
    @patch("backendbot.packages.bots.monitor_worker.psutil.virtual_memory")
    @patch("backendbot.packages.bots.monitor_worker.psutil.disk_usage")
    def test_check_alerts_cpu_high(
        self, mock_disk, mock_memory, mock_cpu, monitor_worker
    ):
        """Test verificación de alertas para CPU alta."""
        # Configurar mocks para CPU alta
        mock_cpu.return_value = 85.0  # Por encima del umbral 80.0
        mock_memory.return_value = Mock(percent=50.0)
        mock_disk.return_value = Mock(percent=50.0)

        metrics = monitor_worker._collect_system_metrics()
        monitor_worker._check_alerts(metrics)

        assert len(monitor_worker.alerts) == 1
        assert monitor_worker.alerts[0]["type"] == "cpu_high"
        assert "CPU alto" in monitor_worker.alerts[0]["message"]

    @patch("backendbot.packages.bots.monitor_worker.psutil.cpu_percent")
    @patch("backendbot.packages.bots.monitor_worker.psutil.virtual_memory")
    @patch("backendbot.packages.bots.monitor_worker.psutil.disk_usage")
    def test_check_alerts_memory_high(
        self, mock_disk, mock_memory, mock_cpu, monitor_worker
    ):
        """Test verificación de alertas para memoria alta."""
        # Configurar mocks para memoria alta
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=90.0)  # Por encima del umbral 85.0
        mock_disk.return_value = Mock(percent=50.0)

        metrics = monitor_worker._collect_system_metrics()
        monitor_worker._check_alerts(metrics)

        assert len(monitor_worker.alerts) == 1
        assert monitor_worker.alerts[0]["type"] == "memory_high"
        assert "memoria alto" in monitor_worker.alerts[0]["message"]

    @patch("backendbot.packages.bots.monitor_worker.psutil.cpu_percent")
    @patch("backendbot.packages.bots.monitor_worker.psutil.virtual_memory")
    @patch("backendbot.packages.bots.monitor_worker.psutil.disk_usage")
    def test_check_alerts_disk_high(
        self, mock_disk, mock_memory, mock_cpu, monitor_worker
    ):
        """Test verificación de alertas para disco alto."""
        # Configurar mocks para disco alto
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=50.0)
        mock_disk.return_value = Mock(percent=95.0)  # Por encima del umbral 90.0

        metrics = monitor_worker._collect_system_metrics()
        monitor_worker._check_alerts(metrics)

        assert len(monitor_worker.alerts) == 1
        assert monitor_worker.alerts[0]["type"] == "disk_high"
        assert "disco alto" in monitor_worker.alerts[0]["message"]

    def test_alert_cooldown(self, monitor_worker):
        """Test cooldown de alertas para evitar spam."""
        # Configurar umbrales bajos para forzar alerta
        monitor_worker.alert_thresholds["cpu_percent"] = 10.0

        # Crear métricas con CPU alta
        metrics = SystemMetrics(
            cpu_usage=50.0, memory_usage=50.0, disk_usage=50.0, timestamp=datetime.now()
        )

        # Primera alerta
        monitor_worker._check_alerts(metrics)
        assert len(monitor_worker.alerts) == 1

        # Segunda alerta inmediata (debe ser bloqueada por cooldown)
        monitor_worker._check_alerts(metrics)
        assert len(monitor_worker.alerts) == 1  # No debe aumentar

    def test_alert_callbacks(self, monitor_worker):
        """Test sistema de callbacks para alertas."""
        callback_mock = Mock()
        monitor_worker.add_alert_callback(callback_mock)

        # Crear alerta
        metrics = SystemMetrics(
            cpu_usage=90.0, memory_usage=50.0, disk_usage=50.0, timestamp=datetime.now()
        )

        monitor_worker._check_alerts(metrics)

        # Verificar que el callback fue llamado
        callback_mock.assert_called_once()
        call_args = callback_mock.call_args[0][0]
        assert call_args["type"] == "cpu_high"

    def test_remove_alert_callback(self, monitor_worker):
        """Test remover callback de alertas."""
        callback_mock = Mock()
        monitor_worker.add_alert_callback(callback_mock)
        monitor_worker.remove_alert_callback(callback_mock)

        # Crear alerta
        metrics = SystemMetrics(
            cpu_usage=90.0, memory_usage=50.0, disk_usage=50.0, timestamp=datetime.now()
        )

        monitor_worker._check_alerts(metrics)

        # Verificar que el callback NO fue llamado
        callback_mock.assert_not_called()

    def test_get_current_metrics_none(self, monitor_worker):
        """Test obtener métricas actuales cuando no hay."""
        assert monitor_worker.get_current_metrics() is None

    @patch("backendbot.packages.bots.monitor_worker.psutil.cpu_percent")
    @patch("backendbot.packages.bots.monitor_worker.psutil.virtual_memory")
    @patch("backendbot.packages.bots.monitor_worker.psutil.disk_usage")
    def test_get_current_metrics(
        self, mock_disk, mock_memory, mock_cpu, monitor_worker
    ):
        """Test obtener métricas actuales."""
        # Configurar mocks
        mock_cpu.return_value = 45.5
        mock_memory.return_value = Mock(percent=67.8)
        mock_disk.return_value = Mock(percent=72.3)

        # Ejecutar tarea para generar métricas
        monitor_worker.execute_task()
        metrics = monitor_worker.get_current_metrics()

        assert metrics is not None
        assert metrics["cpu_usage"] == 45.5
        assert metrics["memory_usage"] == 67.8
        assert metrics["disk_usage"] == 72.3

    def test_get_metrics_history_empty(self, monitor_worker):
        """Test obtener historial vacío."""
        history = monitor_worker.get_metrics_history()
        assert len(history) == 0

    @patch("backendbot.packages.bots.monitor_worker.psutil.cpu_percent")
    @patch("backendbot.packages.bots.monitor_worker.psutil.virtual_memory")
    @patch("backendbot.packages.bots.monitor_worker.psutil.disk_usage")
    def test_get_metrics_history(
        self, mock_disk, mock_memory, mock_cpu, monitor_worker
    ):
        """Test obtener historial de métricas."""
        # Configurar mocks
        mock_cpu.return_value = 45.5
        mock_memory.return_value = Mock(percent=67.8)
        mock_disk.return_value = Mock(percent=72.3)

        # Ejecutar múltiples tareas
        for i in range(5):
            monitor_worker.execute_task()

        history = monitor_worker.get_metrics_history(limit=3)
        assert len(history) == 3

        # Verificar orden (más reciente al final)
        assert history[-1]["cpu_usage"] == 45.5

    def test_get_alerts_empty(self, monitor_worker):
        """Test obtener alertas cuando no hay."""
        alerts = monitor_worker.get_alerts()
        assert len(alerts) == 0

    @patch("backendbot.packages.bots.monitor_worker.psutil.cpu_percent")
    @patch("backendbot.packages.bots.monitor_worker.psutil.virtual_memory")
    @patch("backendbot.packages.bots.monitor_worker.psutil.disk_usage")
    def test_get_alerts(self, mock_disk, mock_memory, mock_cpu, monitor_worker):
        """Test obtener alertas."""
        # Configurar mocks para generar alerta
        mock_cpu.return_value = 85.0
        mock_memory.return_value = Mock(percent=50.0)
        mock_disk.return_value = Mock(percent=50.0)

        monitor_worker.execute_task()
        alerts = monitor_worker.get_alerts(limit=5)

        assert len(alerts) == 1
        assert alerts[0]["type"] == "cpu_high"

    def test_clear_alerts(self, monitor_worker):
        """Test limpiar alertas."""
        # Agregar alerta manualmente
        monitor_worker.alerts.append(
            {"type": "test", "message": "Test alert", "timestamp": datetime.now()}
        )

        assert len(monitor_worker.alerts) == 1
        monitor_worker.clear_alerts()
        assert len(monitor_worker.alerts) == 0

    @patch("backendbot.packages.bots.monitor_worker.psutil.cpu_count")
    @patch("backendbot.packages.bots.monitor_worker.psutil.virtual_memory")
    @patch("backendbot.packages.bots.monitor_worker.psutil.disk_usage")
    @patch("backendbot.packages.bots.monitor_worker.psutil.boot_time")
    @patch("backendbot.packages.bots.monitor_worker.psutil.pids")
    def test_get_system_info(
        self,
        mock_pids,
        mock_boot_time,
        mock_disk,
        mock_memory,
        mock_cpu_count,
        monitor_worker,
    ):
        """Test obtener información del sistema."""
        # Configurar mocks
        mock_cpu_count.side_effect = [
            4,
            8,
        ]  # Primera llamada sin logical, segunda con logical=True
        mock_memory.return_value = Mock(
            total=16 * 1024**3, available=8 * 1024**3
        )  # 16GB total, 8GB available
        mock_disk.return_value = Mock(
            total=500 * 1024**3, free=200 * 1024**3
        )  # 500GB total, 200GB free
        mock_boot_time.return_value = time.time() - 3600  # 1 hora atrás
        mock_pids.return_value = [1, 2, 3, 4, 5]  # 5 procesos

        info = monitor_worker.get_system_info()

        assert info["cpu_count"] == 4
        assert info["cpu_count_logical"] == 8
        assert info["memory_total"] == 16 * 1024**3
        assert info["memory_available"] == 8 * 1024**3
        assert info["disk_total"] == 500 * 1024**3
        assert info["disk_free"] == 200 * 1024**3
        assert "boot_time" in info
        assert info["platform"] == "Unknown"  # Simplificado
        assert info["python_version"] == "3.12.0"  # Simplificado
        assert info["process_count"] == 5

    def test_threading_execution(self, monitor_worker):
        """Test ejecución con threading."""
        # Iniciar worker
        monitor_worker.start()

        # Esperar un poco para que ejecute
        time.sleep(2)

        # Verificar que está ejecutando
        assert monitor_worker.state == BotState.RUNNING
        assert monitor_worker.get_current_metrics() is not None

        # Detener worker
        monitor_worker.stop()

        # Esperar a que termine
        time.sleep(1)
        assert monitor_worker.state == BotState.STOPPED

    def test_repr(self, monitor_worker):
        """Test representación string del worker."""
        repr_str = repr(monitor_worker)
        assert "MonitorWorker" in repr_str
        assert "test-monitor" in repr_str
        assert "30" in repr_str  # intervalo
        assert "0" in repr_str  # alertas iniciales
