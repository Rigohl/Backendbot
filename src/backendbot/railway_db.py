import os
import asyncpg
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

class RailwayPostgreSQL:
    """Integración con Railway PostgreSQL"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool = None
        self.is_connected = False

    async def connect(self):
        """Conectar a Railway PostgreSQL"""
        if not self.database_url:
            logger.error("❌ DATABASE_URL no configurada")
            return False

        try:
            # Crear pool de conexiones
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )

            # Verificar conexión
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT version()")
                logger.info(f"✅ Conectado a PostgreSQL: {result[:50]}...")

            self.is_connected = True
            return True

        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            return False

    async def disconnect(self):
        """Desconectar del pool"""
        if self.pool:
            await self.pool.close()
            self.is_connected = False
            logger.info("❌ Desconectado de PostgreSQL")

    @asynccontextmanager
    async def get_connection(self):
        """Context manager para obtener conexión del pool"""
        if not self.is_connected or not self.pool:
            raise Exception("No hay conexión activa a PostgreSQL")

        async with self.pool.acquire() as conn:
            yield conn

    async def execute_query(self, query: str, *args) -> List[asyncpg.Record]:
        """Ejecutar query SELECT"""
        async with self.get_connection() as conn:
            try:
                result = await conn.fetch(query, *args)
                return result
            except Exception as e:
                logger.error(f"Error ejecutando query: {e}")
                raise

    async def execute_command(self, command: str, *args) -> str:
        """Ejecutar comando INSERT/UPDATE/DELETE"""
        async with self.get_connection() as conn:
            try:
                result = await conn.execute(command, *args)
                return result
            except Exception as e:
                logger.error(f"Error ejecutando comando: {e}")
                raise

    async def create_tables_if_not_exist(self):
        """Crear tablas necesarias si no existen"""
        try:
            # Tabla para historial de procesos (extensión del sistema existente)
            await self.execute_command("""
                CREATE TABLE IF NOT EXISTS railway_process_history (
                    id SERIAL PRIMARY KEY,
                    process_name VARCHAR(255) NOT NULL,
                    pid INTEGER,
                    cpu_percent DECIMAL(5,2),
                    memory_mb DECIMAL(10,2),
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    railway_metadata JSONB
                )
            """)

            # Tabla para métricas de Railway
            await self.execute_command("""
                CREATE TABLE IF NOT EXISTS railway_metrics (
                    id SERIAL PRIMARY KEY,
                    metric_type VARCHAR(100) NOT NULL,
                    value JSONB NOT NULL,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    project_id VARCHAR(255),
                    environment_id VARCHAR(255)
                )
            """)

            # Tabla para logs de Railway
            await self.execute_command("""
                CREATE TABLE IF NOT EXISTS railway_logs (
                    id SERIAL PRIMARY KEY,
                    level VARCHAR(20) NOT NULL,
                    message TEXT NOT NULL,
                    source VARCHAR(100),
                    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                )
            """)

            # Tabla para backups
            await self.execute_command("""
                CREATE TABLE IF NOT EXISTS railway_backups (
                    id SERIAL PRIMARY KEY,
                    backup_type VARCHAR(50) NOT NULL,
                    file_path VARCHAR(500),
                    size_bytes BIGINT,
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            # Índices para optimización
            await self.execute_command("""
                CREATE INDEX IF NOT EXISTS idx_process_history_created_at
                ON railway_process_history(created_at)
            """)

            await self.execute_command("""
                CREATE INDEX IF NOT EXISTS idx_metrics_collected_at
                ON railway_metrics(collected_at)
            """)

            await self.execute_command("""
                CREATE INDEX IF NOT EXISTS idx_logs_logged_at
                ON railway_logs(logged_at)
            """)

            logger.info("✅ Tablas de Railway creadas/verficadas")

        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
            raise

    async def save_process_history(self, process_data: Dict[str, Any]):
        """Guardar historial de procesos en Railway PostgreSQL"""
        try:
            railway_metadata = {
                'project_id': os.getenv('RAILWAY_PROJECT_ID'),
                'environment_id': os.getenv('RAILWAY_ENVIRONMENT_ID'),
                'service_id': os.getenv('RAILWAY_SERVICE_ID'),
                'replica_id': os.getenv('RAILWAY_REPLICA_ID')
            }

            await self.execute_command("""
                INSERT INTO railway_process_history
                (process_name, pid, cpu_percent, memory_mb, status, railway_metadata)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
            process_data.get('name'),
            process_data.get('pid'),
            process_data.get('cpu_percent'),
            process_data.get('memory_mb'),
            process_data.get('status'),
            json.dumps(railway_metadata)
            )

        except Exception as e:
            logger.error(f"Error guardando historial de proceso: {e}")

    async def save_metrics(self, metric_type: str, value: Dict[str, Any]):
        """Guardar métricas en Railway PostgreSQL"""
        try:
            await self.execute_command("""
                INSERT INTO railway_metrics
                (metric_type, value, project_id, environment_id)
                VALUES ($1, $2, $3, $4)
            """,
            metric_type,
            json.dumps(value),
            os.getenv('RAILWAY_PROJECT_ID'),
            os.getenv('RAILWAY_ENVIRONMENT_ID')
            )

        except Exception as e:
            logger.error(f"Error guardando métricas: {e}")

    async def save_log(self, level: str, message: str, source: str = None, metadata: Dict = None):
        """Guardar log en Railway PostgreSQL"""
        try:
            await self.execute_command("""
                INSERT INTO railway_logs
                (level, message, source, metadata)
                VALUES ($1, $2, $3, $4)
            """,
            level,
            message,
            source,
            json.dumps(metadata) if metadata else None
            )

        except Exception as e:
            logger.error(f"Error guardando log: {e}")

    async def get_recent_metrics(self, metric_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener métricas recientes"""
        try:
            result = await self.execute_query("""
                SELECT * FROM railway_metrics
                WHERE metric_type = $1
                ORDER BY collected_at DESC
                LIMIT $2
            """, metric_type, limit)

            return [dict(row) for row in result]

        except Exception as e:
            logger.error(f"Error obteniendo métricas recientes: {e}")
            return []

    async def get_process_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtener historial de procesos de las últimas N horas"""
        try:
            result = await self.execute_query("""
                SELECT * FROM railway_process_history
                WHERE created_at >= NOW() - INTERVAL '%s hours'
                ORDER BY created_at DESC
            """ % hours)

            return [dict(row) for row in result]

        except Exception as e:
            logger.error(f"Error obteniendo historial de procesos: {e}")
            return []

    async def get_logs(self, level: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener logs filtrados por nivel"""
        try:
            if level:
                result = await self.execute_query("""
                    SELECT * FROM railway_logs
                    WHERE level = $1
                    ORDER BY logged_at DESC
                    LIMIT $2
                """, level, limit)
            else:
                result = await self.execute_query("""
                    SELECT * FROM railway_logs
                    ORDER BY logged_at DESC
                    LIMIT $1
                """, limit)

            return [dict(row) for row in result]

        except Exception as e:
            logger.error(f"Error obteniendo logs: {e}")
            return []

    async def cleanup_old_data(self, days: int = 30):
        """Limpiar datos antiguos"""
        try:
            # Limpiar métricas antiguas
            await self.execute_command("""
                DELETE FROM railway_metrics
                WHERE collected_at < NOW() - INTERVAL '%s days'
            """ % days)

            # Limpiar logs antiguos
            await self.execute_command("""
                DELETE FROM railway_logs
                WHERE logged_at < NOW() - INTERVAL '%s days'
            """ % days)

            # Limpiar historial de procesos antiguo
            await self.execute_command("""
                DELETE FROM railway_process_history
                WHERE created_at < NOW() - INTERVAL '%s days'
            """ % days)

            logger.info(f"✅ Datos antiguos limpiados (más de {days} días)")

        except Exception as e:
            logger.error(f"Error limpiando datos antiguos: {e}")

    async def get_database_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos"""
        try:
            # Tamaño de la base de datos
            db_size = await self.execute_query("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """)

            # Conteo de registros por tabla
            table_counts = await self.execute_query("""
                SELECT
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
            """)

            # Conexiones activas
            active_connections = await self.execute_query("""
                SELECT count(*) as active_connections
                FROM pg_stat_activity
                WHERE state = 'active'
            """)

            return {
                'database_size': db_size[0]['size'] if db_size else 'Unknown',
                'table_stats': [dict(row) for row in table_counts],
                'active_connections': active_connections[0]['active_connections'] if active_connections else 0,
                'collected_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de BD: {e}")
            return {}

# Instancia global
railway_db = RailwayPostgreSQL()