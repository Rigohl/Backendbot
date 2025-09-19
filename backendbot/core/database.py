"""
BackendBot - Configuración de Base de Datos
Configuración y utilidades para SQLAlchemy 2.0 con PostgreSQL
"""

import logging
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from .logging_config import logger

# Engine síncrono para operaciones simples
sync_engine = create_engine(
    settings.database.url,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    echo=settings.debug,
    future=True,  # SQLAlchemy 2.0
)

# Engine asíncrono para operaciones de alto rendimiento
async_engine = create_async_engine(
    settings.database.url.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    echo=settings.debug,
    future=True,
)

# Session makers
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    class_=Session,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    future=True,
)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Obtener sesión de base de datos síncrona"""
    db = SyncSessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database error", extra={"error": str(e)})
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Obtener sesión de base de datos asíncrona"""
    db = AsyncSessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database error", extra={"error": str(e)})
        await db.rollback()
        raise
    finally:
        await db.close()


async def init_database():
    """Inicializar la base de datos y crear tablas"""
    try:
        # Crear tablas
        from .models import create_indexes, create_tables

        create_tables(sync_engine)
        create_indexes(sync_engine)

        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", extra={"error": str(e)})
        raise


async def close_database():
    """Cerrar conexiones de base de datos"""
    try:
        await async_engine.dispose()
        sync_engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Error closing database connections", extra={"error": str(e)})


# Funciones de utilidad para operaciones comunes
def execute_query(query: str, params: dict = None) -> list:
    """Ejecutar consulta SQL directa (usar con precaución)"""
    with get_db() as db:
        result = db.execute(query, params or {})
        return result.fetchall()


async def execute_async_query(query: str, params: dict = None) -> list:
    """Ejecutar consulta SQL asíncrona directa (usar con precaución)"""
    async with get_async_db() as db:
        result = await db.execute(query, params or {})
        return result.fetchall()


# Health check de base de datos
def check_database_health() -> dict:
    """Verificar el estado de la conexión a la base de datos"""
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        logger.error("Database health check failed", extra={"error": str(e)})
        return {"status": "unhealthy", "message": str(e)}


# Configuración de logging para SQLAlchemy
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
