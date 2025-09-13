import psutil
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from .cache import cache

logger = logging.getLogger(__name__)

class RailwayMonitor:
    """Monitoreo avanzado integrado con Railway"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.metrics_history = []
        self.alerts = []
        self.monitoring_active = True

    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Recopilar métricas del sistema usando Railway's monitoring"""
        loop = asyncio.get_event_loop()

        try:
            # Ejecutar métricas de sistema en thread pool
            cpu_percent = await loop.run_in_executor(self.executor, psutil.cpu_percent, 1)
            memory = await loop.run_in_executor(self.executor, psutil.virtual_memory)
            disk = await loop.run_in_executor(self.executor, psutil.disk_usage, '/')

            # Métricas de red
            network = await loop.run_in_executor(self.executor, psutil.net_io_counters)

            # Métricas de procesos
            process_count = len(await loop.run_in_executor(self.executor, psutil.pids))

            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'used': disk.used,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': process_count,
                'railway_env': {
                    'project_id': os.getenv('RAILWAY_PROJECT_ID'),
                    'environment_id': os.getenv('RAILWAY_ENVIRONMENT_ID'),
                    'service_id': os.getenv('RAILWAY_SERVICE_ID'),
                    'replica_id': os.getenv('RAILWAY_REPLICA_ID')
                }
            }

            # Cache las métricas por 5 minutos
            cache.set_metric('system_metrics', metrics, ttl=300)

            # Mantener historial limitado
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 100:  # Mantener últimas 100 métricas
                self.metrics_history.pop(0)

            return metrics

        except Exception as e:
            logger.error(f"Error recopilando métricas del sistema: {e}")
            return {}

    async def monitor_performance_trends(self) -> Dict[str, Any]:
        """Analizar tendencias de rendimiento"""
        if len(self.metrics_history) < 10:
            return {"status": "insufficient_data"}

        try:
            recent_metrics = self.metrics_history[-10:]

            # Calcular tendencias
            cpu_trend = self._calculate_trend([m['cpu_percent'] for m in recent_metrics])
            memory_trend = self._calculate_trend([m['memory']['percent'] for m in recent_metrics])

            # Detectar anomalías
            anomalies = self._detect_anomalies(recent_metrics)

            trends = {
                'cpu_trend': cpu_trend,
                'memory_trend': memory_trend,
                'anomalies': anomalies,
                'recommendations': self._generate_recommendations(cpu_trend, memory_trend, anomalies)
            }

            # Cache tendencias
            cache.set_metric('performance_trends', trends, ttl=600)  # 10 minutos

            return trends

        except Exception as e:
            logger.error(f"Error analizando tendencias: {e}")
            return {"status": "error", "error": str(e)}

    def _calculate_trend(self, values: List[float]) -> str:
        """Calcular tendencia de una serie de valores"""
        if len(values) < 2:
            return "stable"

        # Calcular pendiente usando regresión lineal simple
        n = len(values)
        x = list(range(n))
        y = values

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_xx = sum(xi * xi for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)

        if slope > 0.5:
            return "increasing"
        elif slope < -0.5:
            return "decreasing"
        else:
            return "stable"

    def _detect_anomalies(self, metrics: List[Dict[str, Any]]) -> List[str]:
        """Detectar anomalías en las métricas"""
        anomalies = []

        if not metrics:
            return anomalies

        # Calcular promedios
        avg_cpu = sum(m['cpu_percent'] for m in metrics) / len(metrics)
        avg_memory = sum(m['memory']['percent'] for m in metrics) / len(metrics)

        # Última métrica
        latest = metrics[-1]

        # Detectar anomalías
        if latest['cpu_percent'] > avg_cpu * 1.5:
            anomalies.append("high_cpu_usage")

        if latest['memory']['percent'] > avg_memory * 1.5:
            anomalies.append("high_memory_usage")

        if latest['disk']['percent'] > 90:
            anomalies.append("low_disk_space")

        return anomalies

    def _generate_recommendations(self, cpu_trend: str, memory_trend: str, anomalies: List[str]) -> List[str]:
        """Generar recomendaciones basadas en tendencias y anomalías"""
        recommendations = []

        if "high_cpu_usage" in anomalies:
            recommendations.append("Considerar optimizar procesos de CPU intensivos")
            recommendations.append("Evaluar posibilidad de escalar verticalmente")

        if "high_memory_usage" in anomalies:
            recommendations.append("Revisar gestión de memoria en la aplicación")
            recommendations.append("Considerar implementar garbage collection más agresivo")

        if "low_disk_space" in anomalies:
            recommendations.append("Limpiar archivos temporales y logs antiguos")
            recommendations.append("Evaluar necesidad de aumentar espacio en disco")

        if cpu_trend == "increasing":
            recommendations.append("Monitorear crecimiento de uso de CPU")

        if memory_trend == "increasing":
            recommendations.append("Monitorear crecimiento de uso de memoria")

        return recommendations

    async def create_health_check_endpoint(self) -> Dict[str, Any]:
        """Crear endpoint de health check para Railway"""
        try:
            metrics = await self.collect_system_metrics()
            trends = await self.monitor_performance_trends()

            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': os.getenv('RAILWAY_GIT_COMMIT_SHA', 'unknown'),
                'uptime': time.time(),  # Podríamos trackear uptime real
                'metrics': metrics,
                'trends': trends,
                'alerts': self.alerts[-5:] if self.alerts else []  # Últimas 5 alertas
            }

            # Verificar condiciones críticas
            if metrics.get('cpu_percent', 0) > 95:
                health_status['status'] = 'critical'
                health_status['message'] = 'CPU usage critically high'

            elif metrics.get('memory', {}).get('percent', 0) > 95:
                health_status['status'] = 'critical'
                health_status['message'] = 'Memory usage critically high'

            elif metrics.get('disk', {}).get('percent', 0) > 98:
                health_status['status'] = 'critical'
                health_status['message'] = 'Disk space critically low'

            # Cache health status
            cache.set_metric('health_check', health_status, ttl=60)  # 1 minuto

            return health_status

        except Exception as e:
            logger.error(f"Error creando health check: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def log_performance_metrics(self):
        """Log periódico de métricas de rendimiento"""
        while self.monitoring_active:
            try:
                metrics = await self.collect_system_metrics()

                # Log structured
                logger.info("Performance Metrics", extra={
                    'cpu_percent': metrics.get('cpu_percent'),
                    'memory_percent': metrics.get('memory', {}).get('percent'),
                    'disk_percent': metrics.get('disk', {}).get('percent'),
                    'railway_project': os.getenv('RAILWAY_PROJECT_ID'),
                    'railway_environment': os.getenv('RAILWAY_ENVIRONMENT_ID')
                })

                # Esperar 5 minutos
                await asyncio.sleep(300)

            except Exception as e:
                logger.error(f"Error en logging de métricas: {e}")
                await asyncio.sleep(60)  # Esperar 1 minuto en caso de error

    def start_monitoring(self):
        """Iniciar monitoreo en background"""
        asyncio.create_task(self.log_performance_metrics())

    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring_active = False

# Instancia global
monitor = RailwayMonitor()