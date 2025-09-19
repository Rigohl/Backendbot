"""Sistema de Persistencia - BackendBot
Base de datos SQLite con migraciones y configuración unificada.
"""

import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import Any

import yaml


class DatabaseManager:
    """Gestor principal de base de datos SQLite."""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "data", "backend_data.db"
        )
        self.connection = None
        self.logger = logging.getLogger(__name__)
        self._ensure_db_directory()

    def _ensure_db_directory(self):
        """Asegura que el directorio de la base de datos existe."""
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)

    def connect(self):
        """Establece conexión con la base de datos."""
        try:
            # Enable parsing of declared types and allow cross-thread usage
            self.connection = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES,
                check_same_thread=False,
            )
            self.connection.row_factory = sqlite3.Row
            self.logger.info(f"Conectado a base de datos: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            self.logger.error(f"Error conectando a BD: {e}")
            raise

    def disconnect(self):
        """Cierra la conexión con la base de datos."""
        if self.connection:
            self.connection.close()
            self.logger.info("Conexión a BD cerrada")

    def execute_query(self, query: str, params: tuple = None) -> list[dict]:
        """Ejecuta una consulta SELECT y retorna resultados."""
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error ejecutando consulta: {e}")
            raise

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Ejecuta una consulta INSERT/UPDATE/DELETE y retorna filas afectadas."""
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            self.logger.error(f"Error ejecutando actualización: {e}")
            self.connection.rollback()
            raise

    def create_tables(self):
        """Crea todas las tablas necesarias."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                preferences TEXT,  -- JSON con preferencias de usuario
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                schedule TEXT,  -- Cron expression
                enabled INTEGER DEFAULT 1,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,  -- cpu, memory, disk, network
                value REAL NOT NULL,
                unit TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT  -- JSON con metadatos adicionales
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,  -- JSON con datos del patrón
                confidence REAL,
                occurrences INTEGER DEFAULT 1,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,  -- DEBUG, INFO, WARNING, ERROR
                message TEXT NOT NULL,
                module TEXT,
                function TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT  -- JSON con datos adicionales
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                value_type TEXT,  -- string, int, float, bool, json
                category TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
        ]

        for table_sql in tables:
            self.execute_update(table_sql)

        self.logger.info("Tablas de base de datos creadas exitosamente")


class ConfigManager:
    """Gestor de configuración unificado."""

    def __init__(self, config_path: str = None) -> None:
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "config", "backendbot.yaml"
        )
        self.db_manager = DatabaseManager()
        self._ensure_config_directory()
        self._load_config()

    def _ensure_config_directory(self):
        """Asegura que el directorio de configuración existe."""
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)

    def _load_config(self):
        """Carga configuración desde archivo YAML."""
        if os.path.exists(self.config_path):
            with open(self.config_path, encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = self._get_default_config()
            self._save_config()

    def _save_config(self):
        """Guarda configuración en archivo YAML."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

    def _get_default_config(self) -> dict:
        """Retorna configuración por defecto."""
        return {
            "app": {
                "name": "BackendBot",
                "version": "2.0.0",
                "debug": False,
                "log_level": "INFO",
            },
            "modes": {
                "default_mode": "balanced",
                "auto_switch": True,
                "switch_thresholds": {
                    "cpu_high": 80,
                    "memory_high": 85,
                    "disk_high": 90,
                },
            },
            "monitoring": {
                "enabled": True,
                "interval_seconds": 30,
                "metrics_retention_days": 30,
            },
            "learning": {
                "enabled": True,
                "confidence_threshold": 0.7,
                "max_patterns": 1000,
            },
            "ui": {
                "theme": "system",
                "language": "es",
                "tray_icon": True,
                "notifications": True,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Establece un valor de configuración."""
        keys = key.split(".")
        config = self.config

        # Navegar hasta el penúltimo nivel
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Establecer el valor
        config[keys[-1]] = value
        self._save_config()

        # También guardar en BD para persistencia
        self._save_to_db(key, value)

    def _save_to_db(self, key: str, value: Any):
        """Guarda configuración en base de datos."""
        try:
            self.db_manager.connect()

            # Determinar el tipo de valor
            if isinstance(value, bool):
                value_type = "bool"
            elif isinstance(value, int):
                value_type = "int"
            elif isinstance(value, float):
                value_type = "float"
            elif isinstance(value, dict | list):
                value_type = "json"
                value = json.dumps(value)
            else:
                value_type = "string"
                value = str(value)

            # Insertar o actualizar
            query = """
            INSERT OR REPLACE INTO configurations (key, value, value_type, updated_at)
            VALUES (?, ?, ?, ?)
            """
            # Convertir datetime a string ISO para compatibilidad con sqlite3
            updated_at = datetime.now().isoformat()
            self.db_manager.execute_update(query, (key, value, value_type, updated_at))

        except Exception as e:
            self.logger.error(f"Error guardando configuración en BD: {e}")
        finally:
            self.db_manager.disconnect()


class MigrationManager:
    """Gestor de migraciones de base de datos."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager
        self.migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
        os.makedirs(self.migrations_dir, exist_ok=True)

    def run_migrations(self):
        """Ejecuta todas las migraciones pendientes."""
        # Crear tabla de migraciones si no existe
        self.db_manager.execute_update(
            """
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # Obtener migraciones ejecutadas
        executed = self.db_manager.execute_query("SELECT name FROM migrations")
        executed_names = {row["name"] for row in executed}

        # Ejecutar migraciones pendientes
        migration_files = sorted(
            [
                f
                for f in os.listdir(self.migrations_dir)
                if f.endswith(".sql") and f not in executed_names
            ]
        )

        for migration_file in migration_files:
            self._run_migration(migration_file)

    def _run_migration(self, migration_file: str):
        """Ejecuta una migración específica."""
        migration_path = os.path.join(self.migrations_dir, migration_file)

        with open(migration_path, encoding="utf-8") as f:
            sql_content = f.read()

        # Dividir el contenido en statements individuales
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

        # Ejecutar cada statement por separado
        for statement in statements:
            if statement:  # Solo ejecutar si no está vacío
                self.db_manager.execute_update(statement)

        # Registrar como ejecutada
        self.db_manager.execute_update(
            "INSERT INTO migrations (name) VALUES (?)", (migration_file,)
        )

        print(f"Migración ejecutada: {migration_file}")


# Instancias globales
db_manager = DatabaseManager()
config_manager = ConfigManager()
migration_manager = MigrationManager(db_manager)


def init_database():
    """Inicializa la base de datos y ejecuta migraciones."""
    db_manager.connect()
    db_manager.create_tables()
    migration_manager.run_migrations()
    print("Base de datos inicializada correctamente")


if __name__ == "__main__":
    init_database()
