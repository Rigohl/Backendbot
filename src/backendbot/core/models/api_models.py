"""
Modelos de API - Single Responsibility: Solo modelos de respuesta API
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SystemEventResponse(BaseModel):
    """Modelo de respuesta para eventos del sistema"""
    id: int
    timestamp: datetime
    level: str
    source: str
    message: str
    details: Optional[str] = None

    class Config:
        from_attributes = True


class BotActionResponse(BaseModel):
    """Modelo de respuesta para acciones de bots"""
    id: int
    timestamp: datetime
    bot_name: str
    action_type: str
    status: str
    target: Optional[str] = None
    result: Optional[str] = None

    class Config:
        from_attributes = True


class UserPreferenceResponse(BaseModel):
    """Modelo de respuesta para preferencias de usuario"""
    id: int
    user_id: str
    preference_key: str
    preference_value: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommandRequest(BaseModel):
    """Modelo de solicitud para comandos"""
    command: str
    parameters: Optional[dict] = None


class CommandResponse(BaseModel):
    """Modelo de respuesta para comandos"""
    success: bool
    message: str
    data: Optional[dict] = None