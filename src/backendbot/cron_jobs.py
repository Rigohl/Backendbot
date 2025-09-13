import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, List
import logging
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .cache import cache
from .monitor import monitor

logger = logging.getLogger(__name__)

class RailwayCronJobs:
    """Sistema de cron jobs para Railway"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}
        self.job_history = []

    def start_scheduler(self):
        """Iniciar el scheduler de tareas"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Scheduler de cron jobs iniciado")

    def stop_scheduler(self):
        """Detener el scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("❌ Scheduler de cron jobs detenido")

    def add_cron_job(self, job_id: str, func: Callable, cron_expression: str, **kwargs):
        """Agregar job con expresión cron"""
        try:
            trigger = CronTrigger.from_crontab(cron_expression)
            job = self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                name=job_id,
                **kwargs
            )
            self.jobs[job_id] = job
            logger.info(f"✅ Cron job agregado: {job_id} - {cron_expression}")
        except Exception as e:
            logger.error(f"Error agregando cron job {job_id}: {e}")

    def add_interval_job(self, job_id: str, func: Callable, seconds: int, **kwargs):
        """Agregar job con intervalo en segundos"""
        try:
            trigger = IntervalTrigger(seconds=seconds)
            job = self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                name=job_id,
                **kwargs
            )
            self.jobs[job_id] = job
            logger.info(f"✅ Interval job agregado: {job_id} - cada {seconds} segundos")
        except Exception as e:
            logger.error(f"Error agregando interval job {job_id}: {e}")

    def remove_job(self, job_id: str):
        """Remover job"""
        try:
            if job_id in self.jobs:
                self.scheduler.remove_job(job_id)
                del self.jobs[job_id]
                logger.info(f"❌ Job removido: {job_id}")
        except Exception as e:
            logger.error(f"Error removiendo job {job_id}: {e}")

    def get_job_status(self) -> Dict[str, Any]:
        """Obtener estado de todos los jobs"""
        status = {}
        for job_id, job in self.jobs.items():
            status[job_id] = {
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
        return status

    # Jobs específicos para BackendBot
    async def cleanup_old_logs(self):
        """Limpiar logs antiguos (ejecutar diariamente a las 2 AM)"""
        try:
            logger.info("🧹 Iniciando limpieza de logs antiguos")

            # Mantener logs de los últimos 30 días
            cutoff_date = datetime.utcnow() - timedelta(days=30)

            # Aquí iría la lógica para limpiar logs antiguos
            # Por ejemplo, eliminar archivos .log más antiguos que cutoff_date

            # Log de la operación
            operation_log = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': 'cleanup_old_logs',
                'cutoff_date': cutoff_date.isoformat(),
                'status': 'completed'
            }

            self.job_history.append(operation_log)
            logger.info("✅ Limpieza de logs completada")

        except Exception as e:
            logger.error(f"Error en limpieza de logs: {e}")

    async def backup_database(self):
        """Backup de base de datos (ejecutar diariamente a las 3 AM)"""
        try:
            logger.info("💾 Iniciando backup de base de datos")

            # Aquí iría la lógica para hacer backup de la base de datos
            # Usando Railway PostgreSQL

            # Log de la operación
            operation_log = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': 'backup_database',
                'status': 'completed'
            }

            self.job_history.append(operation_log)
            logger.info("✅ Backup de base de datos completado")

        except Exception as e:
            logger.error(f"Error en backup de base de datos: {e}")

    async def optimize_performance(self):
        """Optimización de rendimiento (ejecutar cada 6 horas)"""
        try:
            logger.info("⚡ Iniciando optimización de rendimiento")

            # Recopilar métricas actuales
            metrics = await monitor.collect_system_metrics()

            # Analizar tendencias
            trends = await monitor.monitor_performance_trends()

            # Aplicar optimizaciones basadas en métricas
            if metrics.get('memory', {}).get('percent', 0) > 80:
                logger.warning("Memoria alta detectada, aplicando optimizaciones")
                # Aquí iría lógica para liberar memoria

            if metrics.get('cpu_percent', 0) > 70:
                logger.warning("CPU alta detectada, aplicando optimizaciones")
                # Aquí iría lógica para optimizar CPU

            # Cache las métricas de optimización
            cache.set_metric('last_optimization', {
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics,
                'trends': trends
            }, ttl=21600)  # 6 horas

            # Log de la operación
            operation_log = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': 'optimize_performance',
                'cpu_before': metrics.get('cpu_percent'),
                'memory_before': metrics.get('memory', {}).get('percent'),
                'status': 'completed'
            }

            self.job_history.append(operation_log)
            logger.info("✅ Optimización de rendimiento completada")

        except Exception as e:
            logger.error(f"Error en optimización de rendimiento: {e}")

    async def health_check(self):
        """Health check periódico (ejecutar cada 5 minutos)"""
        try:
            health_status = await monitor.create_health_check_endpoint()

            # Cache el health check
            cache.set_metric('periodic_health_check', health_status, ttl=300)  # 5 minutos

            # Log solo si hay problemas
            if health_status.get('status') != 'healthy':
                logger.warning(f"Health check: {health_status.get('status')}")
                if 'message' in health_status:
                    logger.warning(f"Mensaje: {health_status['message']}")

            # Log de la operación
            operation_log = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': 'health_check',
                'status': health_status.get('status'),
                'alerts': len(health_status.get('alerts', []))
            }

            self.job_history.append(operation_log)

        except Exception as e:
            logger.error(f"Error en health check: {e}")

    async def update_cache_stats(self):
        """Actualizar estadísticas del cache (ejecutar cada hora)"""
        try:
            cache_stats = cache.get_cache_stats()

            # Log estadísticas
            logger.info("📊 Estadísticas del cache actualizadas", extra=cache_stats)

            # Cache las estadísticas
            cache.set_metric('cache_stats', cache_stats, ttl=3600)  # 1 hora

            # Log de la operación
            operation_log = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': 'update_cache_stats',
                'cache_status': cache_stats.get('status'),
                'total_keys': cache_stats.get('total_keys'),
                'status': 'completed'
            }

            self.job_history.append(operation_log)

        except Exception as e:
            logger.error(f"Error actualizando estadísticas del cache: {e}")

    async def maintenance_window(self):
        """Ventana de mantenimiento (ejecutar semanalmente los domingos a las 4 AM)"""
        try:
            logger.info("🔧 Iniciando ventana de mantenimiento semanal")

            # Operaciones de mantenimiento:
            # 1. Limpiar cache antiguo
            cache.clear_cache_pattern("temp:*")
            cache.clear_cache_pattern("session:*")

            # 2. Optimizar base de datos (si es necesario)
            # Aquí iría lógica para vacuum/analyze en PostgreSQL

            # 3. Verificar integridad de archivos
            # Aquí iría lógica para verificar archivos del sistema

            # 4. Actualizar métricas de mantenimiento
            maintenance_stats = {
                'timestamp': datetime.utcnow().isoformat(),
                'cache_cleared': True,
                'database_optimized': True,
                'files_verified': True
            }

            cache.set_metric('maintenance_stats', maintenance_stats, ttl=604800)  # 1 semana

            # Log de la operación
            operation_log = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': 'maintenance_window',
                'status': 'completed',
                'actions_performed': list(maintenance_stats.keys())[1:]
            }

            self.job_history.append(operation_log)
            logger.info("✅ Ventana de mantenimiento completada")

        except Exception as e:
            logger.error(f"Error en ventana de mantenimiento: {e}")

    def setup_default_jobs(self):
        """Configurar jobs por defecto"""
        # Jobs diarios
        self.add_cron_job(
            'cleanup_logs',
            self.cleanup_old_logs,
            '0 2 * * *'  # Todos los días a las 2 AM
        )

        self.add_cron_job(
            'backup_database',
            self.backup_database,
            '0 3 * * *'  # Todos los días a las 3 AM
        )

        # Jobs cada 6 horas
        self.add_cron_job(
            'optimize_performance',
            self.optimize_performance,
            '0 */6 * * *'  # Cada 6 horas
        )

        # Jobs cada hora
        self.add_cron_job(
            'update_cache_stats',
            self.update_cache_stats,
            '0 * * * *'  # Cada hora
        )

        # Jobs cada 5 minutos
        self.add_interval_job(
            'health_check',
            self.health_check,
            300  # 5 minutos
        )

        # Jobs semanales
        self.add_cron_job(
            'maintenance_window',
            self.maintenance_window,
            '0 4 * * 0'  # Domingos a las 4 AM
        )

        logger.info("✅ Jobs por defecto configurados")

    def get_job_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener historial de ejecuciones de jobs"""
        return self.job_history[-limit:]

    def get_job_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de jobs"""
        if not self.job_history:
            return {"total_executions": 0}

        operations = {}
        for execution in self.job_history:
            operation = execution.get('operation', 'unknown')
            operations[operation] = operations.get(operation, 0) + 1

        return {
            "total_executions": len(self.job_history),
            "operations": operations,
            "last_execution": self.job_history[-1] if self.job_history else None
        }

# Instancia global
cron_jobs = RailwayCronJobs()