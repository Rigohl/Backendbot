from sqlalchemy import Column, Integer, String, DateTime, Text, func
from src.backendbot.utils.db import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    level = Column(String, index=True) # INFO, WARNING, ERROR
    source = Column(String, index=True) # e.g., "Orquestador", "Bot Monitor", "Bot Organizer"
    message = Column(Text)
    details = Column(Text, nullable=True) # JSON string for additional details

class BotAction(Base):
    __tablename__ = "bot_actions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    bot_name = Column(String, index=True)
    action_type = Column(String, index=True) # e.g., "scan_duplicates", "delete_files", "start_indexing"
    status = Column(String) # e.g., "started", "completed", "failed"
    target = Column(Text, nullable=True) # e.g., path scanned, files deleted
    result = Column(Text, nullable=True) # JSON string for action results

# Pydantic models for API responses
class SystemEventResponse(BaseModel):
    id: int
    timestamp: datetime
    level: str
    source: str
    message: str
    details: Optional[str] = None

    class Config:
        from_attributes = True

class BotActionResponse(BaseModel):
    id: int
    timestamp: datetime
    bot_name: str
    action_type: str
    status: str
    target: Optional[str] = None
    result: Optional[str] = None

    class Config:
        from_attributes = True
