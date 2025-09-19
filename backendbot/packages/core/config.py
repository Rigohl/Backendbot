class Config:
    def get_settings(self):
        return self
"""
BackendBot Configuration
========================

Configuración centralizada usando Pydantic Settings.
Maneja variables de entorno y configuración por defecto.

Autor: BackendBot Team
Versión: 0.1.0
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Configuración de base de datos."""

    url: str = Field(
        default="sqlite:///./backendbot.db",
        description="URL de conexión a la base de datos",
    )
    pool_size: int = Field(
        default=5, ge=1, le=20, description="Tamaño del pool de conexiones"
    )
    max_overflow: int = Field(
        default=10, ge=0, le=50, description="Máximo overflow de conexiones"
    )
    echo: bool = Field(default=False, description="Echo SQL para debugging")


class APISettings(BaseSettings):
    """Configuración de la API."""

    host: str = Field(default="0.0.0.0", description="Host del servidor API")
    port: int = Field(
        default=8000, ge=1, le=65535, description="Puerto del servidor API"
    )
    reload: bool = Field(default=True, description="Recarga automática en desarrollo")
    workers: int = Field(default=1, ge=1, le=8, description="Número de workers")


class LoggingSettings(BaseSettings):
    """Configuración de logging."""

    level: str = Field(default="INFO", description="Nivel de logging")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato de log",
    )
    file_path: Optional[str] = Field(
        default="logs/backendbot.log", description="Ruta del archivo de log"
    )


class SecuritySettings(BaseSettings):
    """Configuración de seguridad."""

    secret_key: str = Field(
        default="your-secret-key-here", description="Clave secreta para JWT"
    )
    algorithm: str = Field(default="HS256", description="Algoritmo de encriptación")
    access_token_expire_minutes: int = Field(
        default=30, ge=1, description="Expiración del token en minutos"
    )


class Settings(BaseSettings):
    """Configuración principal de BackendBot."""

    app_name: str = Field(default="BackendBot", description="Nombre de la aplicación")
    version: str = Field(default="0.1.0", description="Versión de la aplicación")
    environment: str = Field(default="development", description="Entorno de ejecución")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: APISettings = Field(default_factory=APISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "BACKENDBOT_"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """Obtener la configuración actual."""
    return settings


def reload_settings() -> Settings:
    """Recargar configuración desde variables de entorno."""
    global settings
    settings = Settings()
    return settings
