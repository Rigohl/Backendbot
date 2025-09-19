"""Repositorio de datos para BackendBot - Principio de Responsabilidad Única."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from backendbot.core.database import get_db
from backendbot.core.models import BotAction, SystemEvent, BotStats
from backendbot.core.config import Settings

logger = logging.getLogger(__name__)


class IDataRepository(ABC):
    """Interfaz para repositorio de datos - Principio de Inversión de Dependencias"""

    @abstractmethod
    def save_bot_action(self, bot_name: str, action_type: str, status: str,
                       target: str, result: str) -> None:
        """Guardar acción de bot"""
        pass

    @abstractmethod
    def get_bot_actions(self, bot_name: Optional[str] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener acciones de bot"""
        pass

    @abstractmethod
    def save_system_event(self, level: str, source: str, message: str,
                         details: str = "") -> None:
        """Guardar evento del sistema"""
        pass

    @abstractmethod
    def get_system_events(self, level: Optional[str] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener eventos del sistema"""
        pass

    @abstractmethod
    def save_bot_stats(self, bot_name: str, stats: Dict[str, Any]) -> None:
        """Guardar estadísticas de bot"""
        pass

    @abstractmethod
    def get_bot_stats(self, bot_name: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estadísticas de bot"""
        pass


class DatabaseDataRepository(IDataRepository):
    """Implementación del repositorio usando base de datos SQL"""

    def __init__(self, db_manager: Any):
        """Inicializar repositorio con gestor de BD"""
        self.db_manager = db_manager
        self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Asegurar que las tablas existan"""
        try:
            from backendbot.core.database import sync_engine
            from backendbot.core.models import create_tables
            create_tables(sync_engine)
        except Exception as e:
            logger.warning(f"Could not create tables: {e}")

    def save_bot_action(self, bot_name: str, action_type: str, status: str,
                       target: str, result: str) -> None:
        """Guardar acción de bot en base de datos"""
        try:
            with get_db() as db:
                action = BotAction(
                    bot_name=bot_name,
                    action_type=action_type,
                    status=status,
                    target=target,
                    result=result,
                    timestamp=datetime.utcnow()
                )
                db.add(action)
                db.commit()
                logger.debug(f"Saved bot action: {bot_name} - {action_type}")
        except Exception as e:
            logger.error(f"Error saving bot action: {e}")
            raise

    def get_bot_actions(self, bot_name: Optional[str] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener acciones de bot desde base de datos"""
        try:
            with get_db() as db:
                query = db.query(BotAction)
                if bot_name:
                    query = query.filter(BotAction.bot_name == bot_name)
                actions = query.order_by(BotAction.timestamp.desc()).limit(limit).all()

                return [{
                    'id': action.id,
                    'bot_name': action.bot_name,
                    'action_type': action.action_type,
                    'status': action.status,
                    'target': action.target,
                    'result': action.result,
                    'timestamp': action.timestamp.isoformat()
                } for action in actions]
        except Exception as e:
            logger.error(f"Error getting bot actions: {e}")
            return []

    def save_system_event(self, level: str, source: str, message: str,
                         details: str = "") -> None:
        """Guardar evento del sistema en base de datos"""
        try:
            with get_db() as db:
                event = SystemEvent(
                    level=level,
                    source=source,
                    message=message,
                    details=details,
                    timestamp=datetime.utcnow()
                )
                db.add(event)
                db.commit()
                logger.debug(f"Saved system event: {level} - {source}")
        except Exception as e:
            logger.error(f"Error saving system event: {e}")
            raise

    def get_system_events(self, level: Optional[str] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener eventos del sistema desde base de datos"""
        try:
            with get_db() as db:
                query = db.query(SystemEvent)
                if level:
                    query = query.filter(SystemEvent.level == level)
                events = query.order_by(SystemEvent.timestamp.desc()).limit(limit).all()

                return [{
                    'id': event.id,
                    'level': event.level,
                    'source': event.source,
                    'message': event.message,
                    'details': event.details,
                    'timestamp': event.timestamp.isoformat()
                } for event in events]
        except Exception as e:
            logger.error(f"Error getting system events: {e}")
            return []

    def save_bot_stats(self, bot_name: str, stats: Dict[str, Any]) -> None:
        """Guardar estadísticas de bot en base de datos"""
        try:
            with get_db() as db:
                # Convertir dict a JSON string para almacenamiento
                import json
                stats_json = json.dumps(stats)

                bot_stat = BotStats(
                    bot_name=bot_name,
                    stats=stats_json,
                    timestamp=datetime.utcnow()
                )
                db.add(bot_stat)
                db.commit()
                logger.debug(f"Saved bot stats: {bot_name}")
        except Exception as e:
            logger.error(f"Error saving bot stats: {e}")
            raise

    def get_bot_stats(self, bot_name: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estadísticas de bot desde base de datos"""
        try:
            with get_db() as db:
                query = db.query(BotStats)
                if bot_name:
                    query = query.filter(BotStats.bot_name == bot_name)
                stats = query.order_by(BotStats.timestamp.desc()).first()

                if stats:
                    import json
                    return json.loads(stats.stats)
                return {}
        except Exception as e:
            logger.error(f"Error getting bot stats: {e}")
            return {}


class InMemoryDataRepository(IDataRepository):
    """Implementación en memoria para testing y desarrollo"""

    def __init__(self, db_manager: Any = None):
        """Inicializar repositorio en memoria"""
        self.bot_actions: List[Dict[str, Any]] = []
        self.system_events: List[Dict[str, Any]] = []
        self.bot_stats: Dict[str, Dict[str, Any]] = {}

    def save_bot_action(self, bot_name: str, action_type: str, status: str,
                       target: str, result: str) -> None:
        """Guardar acción de bot en memoria"""
        action = {
            'id': len(self.bot_actions) + 1,
            'bot_name': bot_name,
            'action_type': action_type,
            'status': status,
            'target': target,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.bot_actions.append(action)
        logger.debug(f"Saved bot action: {bot_name} - {action_type}")

    def get_bot_actions(self, bot_name: Optional[str] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener acciones de bot desde memoria"""
        actions = self.bot_actions
        if bot_name:
            actions = [a for a in actions if a['bot_name'] == bot_name]
        return actions[-limit:]

    def save_system_event(self, level: str, source: str, message: str,
                         details: str = "") -> None:
        """Guardar evento del sistema en memoria"""
        event = {
            'id': len(self.system_events) + 1,
            'level': level,
            'source': source,
            'message': message,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.system_events.append(event)
        logger.debug(f"Saved system event: {level} - {source}")

    def get_system_events(self, level: Optional[str] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener eventos del sistema desde memoria"""
        events = self.system_events
        if level:
            events = [e for e in events if e['level'] == level]
        return events[-limit:]

    def save_bot_stats(self, bot_name: str, stats: Dict[str, Any]) -> None:
        """Guardar estadísticas de bot en memoria"""
        self.bot_stats[bot_name] = stats
        logger.debug(f"Saved bot stats: {bot_name}")

    def get_bot_stats(self, bot_name: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estadísticas de bot desde memoria"""
        if bot_name and bot_name in self.bot_stats:
            return self.bot_stats[bot_name]
        return {}


# Factory para crear repositorios
class DataRepositoryFactory:
    """Factory para crear instancias de repositorio"""

    @staticmethod
    def create_repository(settings: Settings, db_manager: Any) -> IDataRepository:
        """Crear repositorio basado en configuración"""
        if settings.database.url.startswith("sqlite:///"):
            # Para desarrollo/testing usar memoria
            return InMemoryDataRepository(db_manager)
        else:
            # Para producción usar base de datos
            return DatabaseDataRepository(db_manager)