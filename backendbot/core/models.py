"""
BackendBot - Modelos de Base de Datos
Modelos SQLAlchemy 2.0 para persistencia de datos escalable
"""

from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, Text, Index)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Bot(Base):
    """Modelo para representar un bot en el sistema"""

    __tablename__ = "bots"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # monitor, organizer, indexer, etc.
    status = Column(String(20), default="inactive")  # active, inactive, error
    config = Column(JSON, default=dict)  # Configuración específica del bot
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    executions = relationship(
        "BotExecution", back_populates="bot", cascade="all, delete-orphan"
    )
    metrics = relationship(
        "BotMetric", back_populates="bot", cascade="all, delete-orphan"
    )


class BotExecution(Base):
    """Modelo para registrar ejecuciones de bots"""

    __tablename__ = "bot_executions"

    id = Column(String(50), primary_key=True)
    bot_id = Column(String(50), ForeignKey("bots.id"), nullable=False)
    status = Column(String(20), nullable=False)  # running, completed, failed
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    result = Column(JSON, default=dict)  # Resultado de la ejecución
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    bot = relationship("Bot", back_populates="executions")


class BotMetric(Base):
    """Modelo para métricas de rendimiento de bots"""

    __tablename__ = "bot_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(String(50), ForeignKey("bots.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metric_metadata = Column(JSON, default=dict)

    # Relaciones
    bot = relationship("Bot", back_populates="metrics")


class SystemMetric(Base):
    """Modelo para métricas del sistema"""

    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)  # cpu_percent, memory_mb, etc.
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metric_metadata = Column(JSON, default=dict)


class User(Base):
    """Modelo para usuarios del sistema (futuro uso)"""

    __tablename__ = "users"

    id = Column(String(50), primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )


class UserSession(Base):
    """Modelo para sesiones de usuario"""

    __tablename__ = "user_sessions"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="sessions")


class AuditLog(Base):
    """Modelo para logs de auditoría"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    resource_id = Column(String(50), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    """Modelo para notificaciones del sistema"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)  # info, warning, error, success
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    recipient = Column(String(100), nullable=True)  # user_id o 'system'
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)


class BotAction(Base):
    """Modelo para acciones de bot"""

    __tablename__ = "bot_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_name = Column(String(100), nullable=False)
    action_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    target = Column(String(255), nullable=False)
    result = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class SystemEvent(Base):
    """Modelo para eventos del sistema"""

    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    source = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class BotStats(Base):
    """Modelo para estadísticas de bot"""

    __tablename__ = "bot_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_name = Column(String(100), nullable=False)
    stats = Column(JSON, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# Funciones de utilidad para el modelo
def create_tables(engine):
    """Crear todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)


def drop_tables(engine):
    """Eliminar todas las tablas de la base de datos"""
    Base.metadata.drop_all(bind=engine)


# Índices recomendados para optimización
def create_indexes(engine):
    """Crear índices adicionales para optimización de consultas"""
    # Índices para BotExecution
    Index(
        "idx_bot_executions_bot_id_status", BotExecution.bot_id, BotExecution.status
    ).create(bind=engine)
    Index("idx_bot_executions_start_time", BotExecution.start_time).create(bind=engine)

    # Índices para BotMetric
    Index(
        "idx_bot_metrics_bot_id_timestamp", BotMetric.bot_id, BotMetric.timestamp
    ).create(bind=engine)
    Index(
        "idx_bot_metrics_name_timestamp", BotMetric.metric_name, BotMetric.timestamp
    ).create(bind=engine)

    # Índices para SystemMetric
    Index(
        "idx_system_metrics_name_timestamp",
        SystemMetric.metric_name,
        SystemMetric.timestamp,
    ).create(bind=engine)

    # Índices para AuditLog
    Index("idx_audit_logs_timestamp", AuditLog.timestamp).create(bind=engine)
    Index("idx_audit_logs_user_action", AuditLog.user_id, AuditLog.action).create(
        bind=engine
    )

    # Índices para Notification
    Index(
        "idx_notifications_recipient_read", Notification.recipient, Notification.is_read
    ).create(bind=engine)
    Index("idx_notifications_created_at", Notification.created_at).create(bind=engine)

    # Índices para nuevos modelos
    Index("idx_bot_actions_bot_name_timestamp", BotAction.bot_name, BotAction.timestamp).create(bind=engine)
    Index("idx_system_events_level_timestamp", SystemEvent.level, SystemEvent.timestamp).create(bind=engine)
    Index("idx_bot_stats_bot_name_timestamp", BotStats.bot_name, BotStats.timestamp).create(bind=engine)
