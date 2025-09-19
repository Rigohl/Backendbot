"""
BackendBot - Configuración Centralizada
Configuración unificada para toda la aplicación escalable
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings
from pydantic import Field


class DatabaseSettings(BaseSettings):
    """Configuración de base de datos"""

    url: str = Field(
        default="postgresql://backendbot:password@localhost:5432/backendbot",
        env="DATABASE_URL",
    )
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")


class RedisSettings(BaseSettings):
    """Configuración de Redis"""

    url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    db: int = Field(default=0, env="REDIS_DB")


class APISettings(BaseSettings):
    """Configuración de la API"""

    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=4, env="API_WORKERS")
    reload: bool = Field(default=True, env="API_RELOAD")


class SecuritySettings(BaseSettings):
    """Configuración de seguridad"""

    secret_key: str = Field(
        default="your-secret-key-change-in-production", env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )


class MonitoringSettings(BaseSettings):
    """Configuración de monitoreo"""

    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")


class BotSettings(BaseSettings):
    """Configuración de bots"""

    enabled_bots: List[str] = Field(
        default=[
            "monitor",
            "organizer",
            "indexer",
            "guardian",
            "auditor_files",
            "auditor_programs",
        ],
        env="ENABLED_BOTS",
    )
    max_concurrent_bots: int = Field(default=3, env="MAX_CONCURRENT_BOTS")
    bot_timeout_seconds: int = Field(default=300, env="BOT_TIMEOUT_SECONDS")


class Settings(BaseSettings):
    """Configuración principal de BackendBot"""

    # Entorno
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")

    # Rutas
    base_dir: Path = Path(__file__).parent.parent.parent
    logs_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "logs"
    )
    data_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data"
    )

    # Sub-configuraciones
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    api: APISettings = APISettings()
    security: SecuritySettings = SecuritySettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    bots: BotSettings = BotSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow extra environment variables so importing Settings
        # during test collection doesn't fail when unrelated env vars
        # are present in the environment (common on developer machines).
        extra = "ignore"


# Instancia global de configuración
settings = Settings()


# Función para obtener configuración (útil para dependency injection)
def get_settings() -> Settings:
    return settings


# Validar configuración al importar
def validate_configuration():
    """Validar que la configuración sea correcta"""
    errors = []

    # Validar directorios
    if not settings.logs_dir.exists():
        settings.logs_dir.mkdir(parents=True, exist_ok=True)

    if not settings.data_dir.exists():
        settings.data_dir.mkdir(parents=True, exist_ok=True)

    # Validar configuración crítica
    if settings.environment not in ["development", "staging", "production"]:
        errors.append(f"Invalid environment: {settings.environment}")

    if settings.api.port < 1 or settings.api.port > 65535:
        errors.append(f"Invalid API port: {settings.api.port}")

    if settings.security.secret_key == "your-secret-key-change-in-production":
        if settings.environment == "production":
            errors.append("Secret key must be changed in production")

    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

    return True


# Validar configuración
validate_configuration()
