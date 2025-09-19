from fastapi import APIRouter, Query
from typing import List, Optional, Dict
from datetime import datetime

from src.backendbot.utils.logging_config import logger

router = APIRouter(
    prefix="/api/v1/events",
    tags=["Events"],
)

# Almacenamiento local simple para eventos
system_events = []
bot_actions = []

class SystemEventResponse:
    def __init__(self, id: int, timestamp: str, level: str, source: str, message: str, details: Optional[str] = None):
        self.id = id
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message
        self.details = details

class BotActionResponse:
    def __init__(self, id: int, timestamp: str, bot_name: str, action_type: str, status: str, details: Optional[str] = None):
        self.id = id
        self.timestamp = timestamp
        self.bot_name = bot_name
        self.action_type = action_type
        self.status = status
        self.details = details

@router.get("/system")
def get_system_events(
    level: Optional[str] = Query(None, description="Filter by log level (INFO, WARNING, ERROR)"),
    source: Optional[str] = Query(None, description="Filter by event source (Orquestador, Bot Monitor, etc.)"),
    skip: int = 0,
    limit: int = 100
):
    logger.info(f"Acceso al endpoint de eventos del sistema. Level: {level}, Source: {source}")
    
    filtered_events = system_events
    if level:
        filtered_events = [e for e in filtered_events if e.level == level]
    if source:
        filtered_events = [e for e in filtered_events if e.source == source]
    
    return filtered_events[skip:skip + limit]

@router.get("/bot_actions")
def get_bot_actions(
    bot_name: Optional[str] = Query(None, description="Filter by bot name"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    status: Optional[str] = Query(None, description="Filter by action status (started, completed, failed)"),
    skip: int = 0,
    limit: int = 100
):
    logger.info(f"Acceso al endpoint de acciones de bots. Bot: {bot_name}, Action: {action_type}, Status: {status}")
    
    filtered_actions = bot_actions
    if bot_name:
        filtered_actions = [a for a in filtered_actions if a.bot_name == bot_name]
    if action_type:
        filtered_actions = [a for a in filtered_actions if a.action_type == action_type]
    if status:
        filtered_actions = [a for a in filtered_actions if a.status == status]
    
    return filtered_actions[skip:skip + limit]
