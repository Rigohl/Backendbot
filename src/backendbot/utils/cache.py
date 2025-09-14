import redis
import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

_redis_client = None

def get_redis_client():
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(REDIS_URL)
            _redis_client.ping() # Probar la conexión
            print("Conectado a Redis exitosamente!")
        except redis.exceptions.ConnectionError as e:
            print(f"Error conectando a Redis: {e}")
            _redis_client = None # Asegurarse de que sea None si falla la conexión
    return _redis_client