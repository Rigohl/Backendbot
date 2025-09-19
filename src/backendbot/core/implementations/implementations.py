"""
Implementaciones concretas de las interfaces - Dependency Inversion Principle
"""
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# Añadir path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.backendbot.core.interfaces.interfaces import ILogger, IConfigManager, IDataRepository


class Logger(ILogger):
    """Implementación concreta del logger"""

    def __init__(self):
        self._logger = logging.getLogger('BackendBot')
        self._logger.setLevel(logging.INFO)

        # Crear handler si no existe
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def info(self, message: str, source: str = None):
        """Log de información"""
        if source:
            self._logger.info(f"[{source}] {message}")
        else:
            self._logger.info(message)

    def warning(self, message: str, source: str = None):
        """Log de advertencia"""
        if source:
            self._logger.warning(f"[{source}] {message}")
        else:
            self._logger.warning(message)

    def error(self, message: str, source: str = None):
        """Log de error"""
        if source:
            self._logger.error(f"[{source}] {message}")
        else:
            self._logger.error(message)


class ConfigManager(IConfigManager):
    """Implementación concreta del gestor de configuración"""

    def __init__(self, config_file: str = None):
        self._config_file = config_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config', 'backendbot.yaml'
        )
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Cargar configuración desde archivo"""
        try:
            import yaml
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                self._config = self._get_default_config()
        except ImportError:
            # Si no hay yaml, usar configuración por defecto
            self._config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Obtener configuración por defecto"""
        return {
            'app': {
                'debug': False,
                'log_level': 'INFO',
                'name': 'BackendBot',
                'version': '2.0.0'
            },
            'ui': {
                'language': 'es',
                'theme': 'system'
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Establecer valor de configuración"""
        keys = key.split('.')
        config = self._config

        # Navegar hasta el penúltimo nivel
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Establecer el valor
        config[keys[-1]] = value

    def save(self):
        """Guardar configuración"""
        try:
            import yaml
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
            with open(self._config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
        except ImportError:
            # Si no hay yaml, no guardar
            pass


class DataRepository(IDataRepository):
    """Implementación concreta del repositorio de datos"""

    def __init__(self, db_path: str = None):
        self._db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data', 'backendbot.db'
        )
        self._init_db()

    def _init_db(self):
        """Inicializar base de datos"""
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            # Crear directorio si no existe
            os.makedirs(os.path.dirname(self._db_path), exist_ok=True)

            # Crear engine
            self._engine = create_engine(f'sqlite:///{self._db_path}')
            self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

            # Crear tablas
            from src.backendbot.data.models.database_models import Base
            Base.metadata.create_all(bind=self._engine)

        except ImportError:
            # Si no hay SQLAlchemy, usar almacenamiento simple
            self._engine = None
            self._data = []

    def save_system_event(self, level: str, source: str, message: str, details: Optional[str] = None):
        """Guardar evento del sistema"""
        if self._engine:
            from src.backendbot.data.models.database_models import SystemEvent
            from sqlalchemy.orm import Session

            db: Session = self._SessionLocal()
            try:
                event = SystemEvent(
                    level=level,
                    source=source,
                    message=message,
                    details=details
                )
                db.add(event)
                db.commit()
            finally:
                db.close()
        else:
            # Almacenamiento simple
            event = {
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'source': source,
                'message': message,
                'details': details
            }
            self._data.append(event)

    def save_bot_action(self, bot_name: str, action_type: str, status: str,
                       target: Optional[str] = None, result: Optional[str] = None):
        """Guardar acción de bot"""
        if self._engine:
            from src.backendbot.data.models.database_models import BotAction
            from sqlalchemy.orm import Session

            db: Session = self._SessionLocal()
            try:
                action = BotAction(
                    bot_name=bot_name,
                    action_type=action_type,
                    status=status,
                    target=target,
                    result=result
                )
                db.add(action)
                db.commit()
            finally:
                db.close()
        else:
            # Almacenamiento simple
            action = {
                'timestamp': datetime.now().isoformat(),
                'bot_name': bot_name,
                'action_type': action_type,
                'status': status,
                'target': target,
                'result': result
            }
            self._data.append(action)

    def get_recent_events(self, limit: int = 100) -> list:
        """Obtener eventos recientes"""
        if self._engine:
            from src.backendbot.data.models.database_models import SystemEvent
            from sqlalchemy.orm import Session

            db: Session = self._SessionLocal()
            try:
                events = db.query(SystemEvent).order_by(
                    SystemEvent.timestamp.desc()
                ).limit(limit).all()
                return [event.__dict__ for event in events]
            finally:
                db.close()
        else:
            return self._data[-limit:] if self._data else []