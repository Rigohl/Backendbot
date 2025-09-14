from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
# Asegurarse de que se carga desde la raíz del proyecto
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

class Settings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

# Mensaje de depuración para verificar la carga
print(f"DEBUG: DATABASE_URL cargada: {settings.database_url}")
print(f"DEBUG: Directorio de trabajo actual: {os.getcwd()}")