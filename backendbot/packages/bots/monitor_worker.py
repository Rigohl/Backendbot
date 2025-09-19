"""
BackendBot Monitor Worker
=========================

Worker especializado en monitoreo del sistema.
Implementa el patrón Observer para detectar cambios en el sistema.

Autor: BackendBot Team
Versión: 0.1.0
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil

from backendbot.packages.bots.base_bot import BaseBot, BotState
from backendbot.packages.models.models import SystemMetrics
from backendbot.packages.core.database import DatabaseManager


class MonitorWorker(BaseBot):
    """
    Worker especializado en monitoreo del sistema.

    Monitorea recursos del sistema, procesos y detecta anomalías.
    Implementa patrón Observer para notificaciones de cambios.
    """

    def __init__(self, bot_id: str = "monitor-001", name: str = "Monitor Worker", db_manager: DatabaseManager = None):
        """
        Inicializar Monitor Worker.

        Args:
            bot_id: ID único del bot
            name: Nombre del bot
            db_manager: Administrador de la base de datos
        """
        super().__init__(
            bot_id=bot_id,
            name=name,
            description="Worker especializado en monitoreo del sistema",
        )

        # Configuración específica del monitor
        self.monitoring_interval = self.config.get(
            "monitoring_interval", 30
        )  # segundos
        self.alert_thresholds = self.config.get(
            "alert_thresholds",
            {"cpu_percent": 80.0, "memory_percent": 85.0, "disk_percent": 90.0},
        )

        # Estado del monitoreo
        self.last_metrics: Optional[SystemMetrics] = None
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = self.config.get("max_history_size", 100)

        # Sistema de alertas
        self.alerts: List[Dict[str, Any]] = []
        self.alert_callbacks: List[callable] = []

        # Locks para thread safety
        self._metrics_lock = threading.Lock()
        self._alerts_lock = threading.Lock()
        self.db_manager = db_manager

    def _load_default_config(self) -> Dict[str, Any]:
        """
        Cargar configuración por defecto del Monitor Worker.

        Returns:
            Configuración por defecto
        """
        return {
            "monitoring_interval": 30,  # segundos
            "max_history_size": 100,
            "alert_thresholds": {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "disk_percent": 90.0,
                "network_errors": 10,
            },
            "enable_process_monitoring": True,
            "enable_disk_monitoring": True,
            "enable_network_monitoring": False,
            "alert_cooldown_minutes": 5,
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validar configuración del Monitor Worker.

        Args:
            config: Configuración a validar

        Returns:
            True si la configuración es válida
        """
        required_keys = ["monitoring_interval", "alert_thresholds"]
        for key in required_keys:
            if key not in config:
                self.logger.error(f"Configuración faltante: {key}")
                return False

        if not isinstance(config["monitoring_interval"], (int, float)):
            self.logger.error("monitoring_interval debe ser numérico")
            return False

        if config["monitoring_interval"] < 1:
            self.logger.error("monitoring_interval debe ser >= 1 segundo")
            return False

        return True

    def should_run_in_background(self) -> bool:
        """
        El Monitor Worker debe ejecutarse en background.

        Returns:
            True
        """
        return True

    def get_execution_interval(self) -> int:
        """
        Obtener intervalo de ejecución.

        Returns:
            Intervalo en segundos
        """
        return self.monitoring_interval

    def execute_task(self, **kwargs) -> Dict[str, Any]:
        """
        Ejecutar tarea de monitoreo.

        Returns:
            Resultado del monitoreo
        """
        try:
            metrics = self._collect_system_metrics()

            with self._metrics_lock:
                self.last_metrics = metrics
                self.metrics_history.append(metrics)

                # Mantener tamaño máximo del historial
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)

            # Guardar métricas en la base de datos
            if self.db_manager:
                metric_data = Metric(
                    cpu_usage=metrics.cpu_usage,
                    ram_usage=metrics.memory_usage,
                    disk_usage=metrics.disk_usage,
                    network_usage=metrics.network_io['bytes_sent'] + metrics.network_io['bytes_recv'] if metrics.network_io else 0.0
                )
                self.db_manager.log_metric(metric_data)

            # Verificar alertas
            self._check_alerts(metrics)

            self.success_count += 1
            self.last_activity = datetime.now()

            return {
                "success": True,
                "metrics": metrics.model_dump(),
                "alerts_count": len(self.alerts),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error en monitoreo: {e}")
            self.error_count += 1
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def execute_periodic_task(self):
        """Ejecutar tarea periódica de monitoreo."""
        result = self.execute_task()

        if result["success"]:
            self.logger.debug(
                f"Monitoreo completado: CPU={result['metrics']['cpu_usage']:.1f}%, "
                f"Mem={result['metrics']['memory_usage']:.1f}%"
            )
        else:
            self.logger.warning(f"Error en monitoreo: {result['error']}")

    def _collect_system_metrics(self) -> SystemMetrics:
        """
        Recopilar métricas del sistema.

        Returns:
            Métricas del sistema
        """
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memoria
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Disco
        disk = psutil.disk_usage("/")
        disk_percent = disk.percent

        # Red (opcional)
        network_io = None
        if self.config.get("enable_network_monitoring", False):
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            }

        return SystemMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory_percent,
            disk_usage=disk_percent,
            network_io=network_io,
            timestamp=datetime.now(),
        )

    def _check_alerts(self, metrics: SystemMetrics):
        """
        Verificar si se deben generar alertas.

        Args:
            metrics: Métricas actuales
        """
        alerts_to_add = []

        # Verificar CPU
        if metrics.cpu_usage > self.alert_thresholds["cpu_percent"]:
            alerts_to_add.append(
                {
                    "type": "cpu_high",
                    "message": f"Uso de CPU alto: {metrics.cpu_usage:.1f}%",
                    "value": metrics.cpu_usage,
                    "threshold": self.alert_thresholds["cpu_percent"],
                    "timestamp": datetime.now(),
                }
            )

        # Verificar memoria
        if metrics.memory_usage > self.alert_thresholds["memory_percent"]:
            alerts_to_add.append(
                {
                    "type": "memory_high",
                    "message": f"Uso de memoria alto: {metrics.memory_usage:.1f}%",
                    "value": metrics.memory_usage,
                    "threshold": self.alert_thresholds["memory_percent"],
                    "timestamp": datetime.now(),
                }
            )

        # Verificar disco
        if metrics.disk_usage > self.alert_thresholds["disk_percent"]:
            alerts_to_add.append(
                {
                    "type": "disk_high",
                    "message": f"Uso de disco alto: {metrics.disk_usage:.1f}%",
                    "value": metrics.disk_usage,
                    "threshold": self.alert_thresholds["disk_percent"],
                    "timestamp": datetime.now(),
                }
            )

        # Agregar alertas con cooldown
        with self._alerts_lock:
            for alert in alerts_to_add:
                if self._should_add_alert(alert):
                    self.alerts.append(alert)
                    self.logger.warning(f"ALERTA: {alert['message']}")

                    # Notificar callbacks
                    self._notify_alert_callbacks(alert)

            # Mantener máximo de alertas
            max_alerts = self.config.get("max_alerts", 100)
            if len(self.alerts) > max_alerts:
                self.alerts = self.alerts[-max_alerts:]

    def _should_add_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Verificar si se debe agregar una alerta considerando cooldown.

        Args:
            alert: Alerta a verificar

        Returns:
            True si se debe agregar
        """
        cooldown_minutes = self.config.get("alert_cooldown_minutes", 5)
        cooldown_time = timedelta(minutes=cooldown_minutes)

        # Buscar alertas similares recientes
        for existing_alert in reversed(self.alerts):
            if (
                existing_alert["type"] == alert["type"]
                and alert["timestamp"] - existing_alert["timestamp"] < cooldown_time
            ):
                return False

        return True

    def add_alert_callback(self, callback: callable):
        """
        Agregar callback para alertas.

        Args:
            callback: Función a llamar cuando hay alerta
        """
        with self._alerts_lock:
            if callback not in self.alert_callbacks:
                self.alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: callable):
        """
        Remover callback de alertas.

        Args:
            callback: Función a remover
        """
        with self._alerts_lock:
            if callback in self.alert_callbacks:
                self.alert_callbacks.remove(callback)

    def _notify_alert_callbacks(self, alert: Dict[str, Any]):
        """
        Notificar callbacks de alertas.

        Args:
            alert: Alerta a notificar
        """
        for callback in self.alert_callbacks.copy():
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error en callback de alerta: {e}")

    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Obtener métricas actuales.

        Returns:
            Métricas actuales o None
        """
        with self._metrics_lock:
            if self.last_metrics:
                return self.last_metrics.model_dump()
            return None

    def get_metrics_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener historial de métricas.

        Args:
            limit: Número máximo de métricas a retornar

        Returns:
            Lista de métricas históricas
        """
        with self._metrics_lock:
            return [m.model_dump() for m in self.metrics_history[-limit:]]

    def get_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener alertas recientes.

        Args:
            limit: Número máximo de alertas a retornar

        Returns:
            Lista de alertas recientes
        """
        with self._alerts_lock:
            return self.alerts[-limit:]

    def clear_alerts(self):
        """Limpiar todas las alertas."""
        with self._alerts_lock:
            self.alerts.clear()
            self.logger.info("Alertas limpiadas")

    def get_system_info(self) -> Dict[str, Any]:
        """
        Obtener información completa del sistema.

        Returns:
            Información del sistema
        """
        try:
            system_info = {
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_total": psutil.disk_usage("/").total,
                "disk_free": psutil.disk_usage("/").free,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "platform": "Unknown",  # Simplificado para evitar problemas con psutil
                "python_version": "3.12.0",  # Simplificado para evitar problemas con psutil
            }

            # Información de procesos (opcional)
            if self.config.get("enable_process_monitoring", True):
                system_info["process_count"] = len(psutil.pids())

            return system_info

        except Exception as e:
            self.logger.error(f"Error obteniendo información del sistema: {e}")
            return {"error": str(e)}

    def on_starting(self):
        """Hook llamado antes de iniciar."""
        self.logger.info("Inicializando Monitor Worker...")
        self.logger.info(f"Intervalo de monitoreo: {self.monitoring_interval}s")
        self.logger.info(f"Umbrales de alerta: {self.alert_thresholds}")

    def on_started(self):
        """Hook llamado después de iniciar."""
        self.logger.info("Monitor Worker iniciado correctamente")
        self.logger.info(
            f"Monitoreando sistema cada {self.monitoring_interval} segundos"
        )

    def on_stopping(self):
        """Hook llamado antes de detener."""
        self.logger.info("Deteniendo Monitor Worker...")

    def on_stopped(self):
        """Hook llamado después de detener."""
        self.logger.info("Monitor Worker detenido correctamente")

    def __repr__(self) -> str:
        return f"MonitorWorker(id='{self.bot_id}', interval={self.monitoring_interval}s, alerts={len(self.alerts)})"
