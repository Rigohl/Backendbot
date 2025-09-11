import os
import json
from typing import Dict, List

from pydantic_settings import BaseSettings, SettingsConfigDict


def load_processes_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config", "processes.json")
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)

processes_config = load_processes_config()

class Settings(BaseSettings):
    CPU_THRESHOLD: int = 80
    RAM_THRESHOLD: int = 4000  # en MB
    CHECK_TIME: int = 60  # en segundos
    HIBERNABLES: List[str] = processes_config.get("hibernables", [])
    MODO: str = "diario"
    PROCESOS_A_CERRAR: Dict[str, List[str]] = processes_config.get("procesos_a_cerrar", {})
    PROCESOS_IMPORTANTES: List[str] = processes_config.get("procesos_importantes", [])
    API_KEY: str = "your-super-secret-api-key"

    # Neon/SQLite DB config
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///"
        + os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "data",
            "backend_data.db",
        ),
    )

    # File paths
    LOG_FILE: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "backend.log"
    )
    MEMORY_FILE: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "memory.json"
    )
    DB_FILE: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "data",
        "backend_data.db",
    )

    # Watchdog thresholds
    SUSPENSION_THRESHOLD: int = 3  # Número de suspensiones antes de ignorar
    REJECTION_THRESHOLD: int = 3  # Número de rechazos antes de ignorar

    model_config = SettingsConfigDict(env_file="config/.env", env_file_encoding="utf-8")


settings = Settings()
