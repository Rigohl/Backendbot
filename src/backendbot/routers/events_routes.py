from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.backendbot.utils.db_logger import get_db
from src.backendbot.models import SystemEvent, BotAction, SystemEventResponse, BotActionResponse
from src.backendbot.utils.logging_config import logger

router = APIRouter(
    prefix="/api/v1/events",
    tags=["Events"],
)

@router.get("/system", response_model=List[SystemEventResponse])
def get_system_events(
    db: Session = Depends(get_db),
    level: Optional[str] = Query(None, description="Filter by log level (INFO, WARNING, ERROR)"),
    source: Optional[str] = Query(None, description="Filter by event source (Orquestador, Bot Monitor, etc.)"),
    skip: int = 0,
    limit: int = 100
):
    logger.info(f"Acceso al endpoint de eventos del sistema. Level: {level}, Source: {source}")
    query = db.query(SystemEvent)
    if level:
        query = query.filter(SystemEvent.level == level)
    if source:
        query = query.filter(SystemEvent.source == source)
    return query.offset(skip).limit(limit).all()

@router.get("/bot_actions", response_model=List[BotActionResponse])
def get_bot_actions(
    db: Session = Depends(get_db),
    bot_name: Optional[str] = Query(None, description="Filter by bot name"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    status: Optional[str] = Query(None, description="Filter by action status (started, completed, failed)"),
    skip: int = 0,
    limit: int = 100
):
    logger.info(f"Acceso al endpoint de acciones de bots. Bot: {bot_name}, Action: {action_type}, Status: {status}")
    query = db.query(BotAction)
    if bot_name:
        query = query.filter(BotAction.bot_name == bot_name)
    if action_type:
        query = query.filter(BotAction.action_type == action_type)
    if status:
        query = query.filter(BotAction.status == status)
    return query.offset(skip).limit(limit).all()
