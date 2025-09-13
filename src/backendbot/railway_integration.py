"""
Integración completa de características avanzadas de Railway para BackendBot

Este módulo integra:
- Redis Cache avanzado
- Monitoreo de sistema con Railway
- Webhooks para automatización
- Cron jobs para tareas programadas
- PostgreSQL integrado de Railway
"""

import asyncio
import os
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from .cache import cache
from .monitor import monitor
from .webhooks import webhooks
from .cron_jobs import cron_jobs
from .railway_db import railway_db

logger = logging.getLogger(__name__)

class RailwayIntegration:
    """Integración completa de Railway para BackendBot"""

    def __init__(self):
        self.initialized = False
        self.components = {
            'cache': cache,
            'monitor': monitor,
            'webhooks': webhooks,
            'cron_jobs': cron_jobs,
            'database': railway_db
        }

    async def initialize(self):
        """Inicializar todos los componentes de Railway"""
        if self.initialized:
            logger.info("Railway integration ya inicializada")
            return True

        try:
            logger.info("🚀 Inicializando integración de Railway...")

            # 1. Conectar a Railway PostgreSQL
            if await railway_db.connect():
                await railway_db.create_tables_if_not_exist()
                logger.info("✅ Railway PostgreSQL inicializado")
            else:
                logger.warning("⚠️  Railway PostgreSQL no disponible")

            # 2. Configurar webhooks
            webhooks.setup_default_handlers()
            logger.info("✅ Webhooks configurados")

            # 3. Configurar cron jobs
            cron_jobs.setup_default_jobs()
            cron_jobs.start_scheduler()
            logger.info("✅ Cron jobs configurados e iniciados")

            # 4. Iniciar monitoreo
            monitor.start_monitoring()
            logger.info("✅ Monitoreo de sistema iniciado")

            # 5. Verificar cache Redis
            if cache.is_available():
                logger.info("✅ Redis cache disponible")
            else:
                logger.warning("⚠️  Redis cache no disponible")

            self.initialized = True
            logger.info("🎉 Integración de Railway completada exitosamente")

            return True

        except Exception as e:
            logger.error(f"❌ Error inicializando Railway integration: {e}")
            return False

    async def shutdown(self):
        """Apagar todos los componentes de Railway"""
        try:
            logger.info("🛑 Apagando integración de Railway...")

            # Detener cron jobs
            cron_jobs.stop_scheduler()

            # Detener monitoreo
            monitor.stop_monitoring()

            # Desconectar base de datos
            await railway_db.disconnect()

            self.initialized = False
            logger.info("✅ Integración de Railway apagada")

        except Exception as e:
            logger.error(f"Error apagando Railway integration: {e}")

    def is_railway_environment(self) -> bool:
        """Verificar si estamos ejecutando en Railway"""
        return bool(os.getenv('RAILWAY_PROJECT_ID'))

    def get_railway_info(self) -> Dict[str, Any]:
        """Obtener información del entorno de Railway"""
        return {
            'project_id': os.getenv('RAILWAY_PROJECT_ID'),
            'environment_id': os.getenv('RAILWAY_ENVIRONMENT_ID'),
            'service_id': os.getenv('RAILWAY_SERVICE_ID'),
            'replica_id': os.getenv('RAILWAY_REPLICA_ID'),
            'git_commit_sha': os.getenv('RAILWAY_GIT_COMMIT_SHA'),
            'git_branch': os.getenv('RAILWAY_GIT_BRANCH'),
            'public_domain': os.getenv('RAILWAY_PUBLIC_DOMAIN'),
            'private_domain': os.getenv('RAILWAY_PRIVATE_DOMAIN')
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        try:
            # Métricas del sistema
            system_metrics = await monitor.collect_system_metrics()

            # Estado del cache
            cache_stats = cache.get_cache_stats()

            # Estado de la base de datos
            db_stats = await railway_db.get_database_stats()

            # Estado de cron jobs
            job_status = cron_jobs.get_job_status()
            job_stats = cron_jobs.get_job_stats()

            # Estado de webhooks
            webhook_stats = webhooks.get_webhook_stats()

            return {
                'timestamp': system_metrics.get('timestamp'),
                'railway_info': self.get_railway_info(),
                'system_metrics': system_metrics,
                'cache_stats': cache_stats,
                'database_stats': db_stats,
                'cron_jobs': {
                    'status': job_status,
                    'stats': job_stats
                },
                'webhooks': webhook_stats,
                'overall_status': 'healthy' if self.initialized else 'initializing'
            }

        except Exception as e:
            logger.error(f"Error obteniendo estado del sistema: {e}")
            return {
                'timestamp': str(asyncio.get_event_loop().time()),
                'error': str(e),
                'overall_status': 'error'
            }

    async def optimize_system(self) -> Dict[str, Any]:
        """Ejecutar optimización completa del sistema"""
        try:
            logger.info("🔧 Iniciando optimización completa del sistema")

            # Recopilar métricas actuales
            before_metrics = await monitor.collect_system_metrics()

            # Limpiar cache antiguo
            cache.clear_cache_pattern("temp:*")
            cache.clear_cache_pattern("old:*")

            # Limpiar datos antiguos de la base de datos
            await railway_db.cleanup_old_data(days=7)  # Última semana

            # Recopilar métricas después
            after_metrics = await monitor.collect_system_metrics()

            # Calcular mejoras
            improvements = {
                'memory_freed_mb': before_metrics.get('memory', {}).get('used', 0) -
                                 after_metrics.get('memory', {}).get('used', 0),
                'cache_cleared': True,
                'old_data_cleaned': True
            }

            # Cache los resultados de optimización
            cache.set_metric('system_optimization', {
                'timestamp': after_metrics.get('timestamp'),
                'before': before_metrics,
                'after': after_metrics,
                'improvements': improvements
            }, ttl=3600)  # 1 hora

            logger.info("✅ Optimización completa del sistema finalizada")
            return {
                'status': 'completed',
                'before_metrics': before_metrics,
                'after_metrics': after_metrics,
                'improvements': improvements
            }

        except Exception as e:
            logger.error(f"Error en optimización del sistema: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def get_component(self, name: str):
        """Obtener componente específico por nombre"""
        return self.components.get(name)

    @asynccontextmanager
    async def database_connection(self):
        """Context manager para conexiones de base de datos"""
        async with railway_db.get_connection() as conn:
            yield conn

# Instancia global
railway = RailwayIntegration()

# Funciones de conveniencia para acceso rápido
async def init_railway():
    """Inicializar Railway (función de conveniencia)"""
    return await railway.initialize()

async def get_status():
    """Obtener estado del sistema (función de conveniencia)"""
    return await railway.get_system_status()

async def optimize():
    """Optimizar sistema (función de conveniencia)"""
    return await railway.optimize_system()

# Exportar componentes individuales para uso directo
__all__ = [
    'railway',
    'cache',
    'monitor',
    'webhooks',
    'cron_jobs',
    'railway_db',
    'init_railway',
    'get_status',
    'optimize'
]