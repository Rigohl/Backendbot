import redis
import json
import os
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Cache avanzado usando Railway Redis"""

    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Error connecting to Redis: {e}")
            self.redis = None

    def is_available(self) -> bool:
        """Verificar si Redis está disponible"""
        return self.redis is not None

    def set_metric(self, key: str, value: Dict[str, Any], ttl: int = 300):
        """Cache métricas del sistema (5 minutos por defecto)"""
        if not self.is_available():
            return

        try:
            self.redis.setex(f"metric:{key}", ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Error guardando métrica en cache: {e}")

    def get_metric(self, key: str) -> Optional[Dict[str, Any]]:
        """Obtener métricas del cache"""
        if not self.is_available():
            return None

        try:
            data = self.redis.get(f"metric:{key}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error obteniendo métrica del cache: {e}")
            return None

    def cache_ai_response(self, query: str, response: str, ttl: int = 3600):
        """Cache respuestas de IA (1 hora por defecto)"""
        if not self.is_available():
            return

        try:
            # Usar hash de la query como key
            query_hash = str(hash(query))
            cache_key = f"ai_response:{query_hash}"

            cache_data = {
                'query': query,
                'response': response,
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }

            self.redis.setex(cache_key, ttl, json.dumps(cache_data))
        except Exception as e:
            logger.error(f"Error guardando respuesta de IA en cache: {e}")

    def get_ai_response(self, query: str) -> Optional[str]:
        """Obtener respuesta de IA del cache"""
        if not self.is_available():
            return None

        try:
            query_hash = str(hash(query))
            cache_key = f"ai_response:{query_hash}"

            data = self.redis.get(cache_key)
            if data:
                cache_data = json.loads(data)
                return cache_data['response']
            return None
        except Exception as e:
            logger.error(f"Error obteniendo respuesta de IA del cache: {e}")
            return None

    def cache_user_session(self, user_id: str, session_data: Dict[str, Any], ttl: int = 86400):
        """Cache datos de sesión de usuario (24 horas por defecto)"""
        if not self.is_available():
            return

        try:
            cache_key = f"user_session:{user_id}"
            self.redis.setex(cache_key, ttl, json.dumps(session_data))
        except Exception as e:
            logger.error(f"Error guardando sesión de usuario: {e}")

    def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener sesión de usuario del cache"""
        if not self.is_available():
            return None

        try:
            cache_key = f"user_session:{user_id}"
            data = self.redis.get(cache_key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error obteniendo sesión de usuario: {e}")
            return None

    def increment_counter(self, key: str, ttl: int = 3600) -> int:
        """Incrementar contador (útil para rate limiting)"""
        if not self.is_available():
            return 0

        try:
            counter_key = f"counter:{key}"
            count = self.redis.incr(counter_key)

            # Set TTL si es la primera vez
            if count == 1:
                self.redis.expire(counter_key, ttl)

            return count
        except Exception as e:
            logger.error(f"Error incrementando contador: {e}")
            return 0

    def get_counter(self, key: str) -> int:
        """Obtener valor de contador"""
        if not self.is_available():
            return 0

        try:
            counter_key = f"counter:{key}"
            count = self.redis.get(counter_key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Error obteniendo contador: {e}")
            return 0

    def set_rate_limit(self, identifier: str, window_seconds: int = 60, max_requests: int = 100) -> bool:
        """Implementar rate limiting"""
        if not self.is_available():
            return True  # Permitir si no hay Redis

        try:
            key = f"ratelimit:{identifier}"
            current = self.redis.incr(key)

            if current == 1:
                self.redis.expire(key, window_seconds)

            return current <= max_requests
        except Exception as e:
            logger.error(f"Error en rate limiting: {e}")
            return True  # Permitir en caso de error

    def publish_event(self, channel: str, message: Dict[str, Any]):
        """Publicar evento en canal de Redis (para WebSockets o notificaciones)"""
        if not self.is_available():
            return

        try:
            self.redis.publish(channel, json.dumps(message))
        except Exception as e:
            logger.error(f"Error publicando evento: {e}")

    def subscribe_to_events(self, channels: list, callback):
        """Suscribirse a eventos (útil para notificaciones en tiempo real)"""
        if not self.is_available():
            return

        try:
            pubsub = self.redis.pubsub()
            pubsub.subscribe(channels)

            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        callback(message['channel'], data)
                    except Exception as e:
                        logger.error(f"Error procesando mensaje: {e}")
        except Exception as e:
            logger.error(f"Error en suscripción: {e}")

    def clear_cache_pattern(self, pattern: str):
        """Limpiar cache por patrón (útil para invalidación)"""
        if not self.is_available():
            return

        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                logger.info(f"Limpiadas {len(keys)} keys con patrón {pattern}")
        except Exception as e:
            logger.error(f"Error limpiando cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        if not self.is_available():
            return {"status": "unavailable"}

        try:
            info = self.redis.info()
            return {
                "status": "available",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_keys": self.redis.dbsize(),
                "uptime_days": info.get("uptime_in_days", 0)
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"status": "error", "error": str(e)}

# Instancia global
cache = RedisCache()