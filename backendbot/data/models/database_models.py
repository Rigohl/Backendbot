"""Modelos de base de datos - Single Responsibility: Solo modelos de BD."""

from sqlalchemy import Column, DateTime, Integer, String, Text, func

from src.backendbot.data.models.base import Base


class SystemEvent(Base):
    """Modelo de base de datos para eventos del sistema."""

    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    level = Column(String, index=True)  # INFO, WARNING, ERROR
    source = Column(
        String, index=True
    )  # e.g., "Orquestador", "Bot Monitor", "Bot Organizer"
    message = Column(Text)
    details = Column(Text, nullable=True)  # JSON string for additional details


class BotAction(Base):
    """Modelo de base de datos para acciones de bots."""

    __tablename__ = "bot_actions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    bot_name = Column(String, index=True)
    action_type = Column(
        String, index=True
    )  # e.g., "scan_duplicates", "delete_files", "start_indexing"
    status = Column(String)  # e.g., "started", "completed", "failed"
    target = Column(Text, nullable=True)  # e.g., path scanned, files deleted
    result = Column(Text, nullable=True)  # JSON string for action results


class UserPreference(Base):
    """Modelo de base de datos para preferencias de usuario."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    preference_key = Column(String, index=True)
    preference_value = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
