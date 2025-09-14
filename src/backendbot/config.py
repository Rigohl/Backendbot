from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

class Settings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

# Mensaje de depuración para verificar la carga
print(f"DEBUG: DATABASE_URL cargada: {settings.database_url}")
