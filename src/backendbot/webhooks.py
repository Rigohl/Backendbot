import hmac
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import logging
import asyncio
from aiohttp import web
import aiohttp

logger = logging.getLogger(__name__)

class RailwayWebhooks:
    """Gestión de webhooks para Railway"""

    def __init__(self):
        self.webhook_secret = os.getenv("RAILWAY_WEBHOOK_SECRET")
        self.handlers: Dict[str, Callable] = {}
        self.received_webhooks = []

    def register_handler(self, event_type: str, handler: Callable):
        """Registrar handler para un tipo de evento"""
        self.handlers[event_type] = handler
        logger.info(f"✅ Handler registrado para evento: {event_type}")

    def unregister_handler(self, event_type: str):
        """Desregistrar handler"""
        if event_type in self.handlers:
            del self.handlers[event_type]
            logger.info(f"❌ Handler desregistrado para evento: {event_type}")

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verificar firma del webhook usando Railway's webhook secret"""
        if not self.webhook_secret:
            logger.warning("⚠️  RAILWAY_WEBHOOK_SECRET no configurado")
            return False

        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()

            # Railway usa formato "sha256=..."
            if signature.startswith("sha256="):
                signature = signature[7:]

            return hmac.compare_digest(expected_signature, signature)

        except Exception as e:
            logger.error(f"Error verificando firma: {e}")
            return False

    async def handle_webhook(self, request: web.Request) -> web.Response:
        """Manejar webhook entrante de Railway"""
        try:
            # Obtener payload
            payload = await request.text()

            # Verificar firma
            signature = request.headers.get('X-Railway-Signature')
            if not self.verify_signature(payload, signature):
                logger.warning("⚠️  Firma de webhook inválida")
                return web.Response(status=401, text="Invalid signature")

            # Parsear payload
            data = json.loads(payload)

            # Log del webhook
            webhook_log = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': data.get('type'),
                'project_id': data.get('project', {}).get('id'),
                'environment_id': data.get('environment', {}).get('id'),
                'service_id': data.get('service', {}).get('id'),
                'payload': data
            }

            self.received_webhooks.append(webhook_log)
            if len(self.received_webhooks) > 100:  # Mantener últimos 100
                self.received_webhooks.pop(0)

            logger.info(f"📨 Webhook recibido: {data.get('type')}")

            # Procesar evento
            event_type = data.get('type')
            if event_type in self.handlers:
                try:
                    await self.handlers[event_type](data)
                except Exception as e:
                    logger.error(f"Error procesando webhook {event_type}: {e}")
                    return web.Response(status=500, text="Internal error")
            else:
                logger.warning(f"⚠️  No hay handler para evento: {event_type}")

            return web.Response(status=200, text="OK")

        except json.JSONDecodeError:
            logger.error("Error parseando payload JSON")
            return web.Response(status=400, text="Invalid JSON")
        except Exception as e:
            logger.error(f"Error procesando webhook: {e}")
            return web.Response(status=500, text="Internal error")

    # Handlers específicos para eventos de Railway
    async def handle_deployment_success(self, data: Dict[str, Any]):
        """Manejar evento de deployment exitoso"""
        logger.info("🚀 Deployment exitoso detectado")
        logger.info(f"Proyecto: {data.get('project', {}).get('name')}")
        logger.info(f"Environment: {data.get('environment', {}).get('name')}")

        # Aquí podríamos:
        # - Notificar a usuarios
        # - Actualizar métricas
        # - Ejecutar tareas post-deployment
        # - Limpiar cache si es necesario

    async def handle_deployment_failed(self, data: Dict[str, Any]):
        """Manejar evento de deployment fallido"""
        logger.error("❌ Deployment fallido detectado")
        logger.error(f"Proyecto: {data.get('project', {}).get('name')}")
        logger.error(f"Environment: {data.get('environment', {}).get('name')}")

        # Obtener detalles del error
        deployment = data.get('deployment', {})
        logger.error(f"Error: {deployment.get('message', 'Unknown error')}")

        # Aquí podríamos:
        # - Enviar alertas
        # - Rollback automático
        # - Notificar al equipo de desarrollo

    async def handle_service_crashed(self, data: Dict[str, Any]):
        """Manejar evento de servicio caído"""
        logger.critical("💥 Servicio caído detectado")
        logger.critical(f"Servicio: {data.get('service', {}).get('name')}")

        # Aquí podríamos:
        # - Intentar reinicio automático
        # - Escalar recursos
        # - Notificar inmediatamente

    async def handle_database_backup_completed(self, data: Dict[str, Any]):
        """Manejar evento de backup de base de datos completado"""
        logger.info("💾 Backup de base de datos completado")
        logger.info(f"Base de datos: {data.get('database', {}).get('name')}")

        # Aquí podríamos:
        # - Verificar integridad del backup
        # - Actualizar métricas de backup
        # - Limpiar backups antiguos

    async def handle_usage_alert(self, data: Dict[str, Any]):
        """Manejar evento de alerta de uso"""
        alert = data.get('alert', {})
        logger.warning("⚠️  Alerta de uso detectada")
        logger.warning(f"Tipo: {alert.get('type')}")
        logger.warning(f"Mensaje: {alert.get('message')}")

        # Aquí podríamos:
        # - Escalar recursos automáticamente
        # - Notificar al equipo
        # - Implementar throttling

    def setup_default_handlers(self):
        """Configurar handlers por defecto para eventos comunes"""
        self.register_handler('DEPLOYMENT_SUCCESS', self.handle_deployment_success)
        self.register_handler('DEPLOYMENT_FAILED', self.handle_deployment_failed)
        self.register_handler('SERVICE_CRASHED', self.handle_service_crashed)
        self.register_handler('DATABASE_BACKUP_COMPLETED', self.handle_database_backup_completed)
        self.register_handler('USAGE_ALERT', self.handle_usage_alert)

        logger.info("✅ Handlers por defecto configurados")

    def get_webhook_history(self, limit: int = 50) -> list:
        """Obtener historial de webhooks recibidos"""
        return self.received_webhooks[-limit:]

    def get_webhook_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de webhooks"""
        if not self.received_webhooks:
            return {"total_webhooks": 0}

        event_types = {}
        for webhook in self.received_webhooks:
            event_type = webhook.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return {
            "total_webhooks": len(self.received_webhooks),
            "event_types": event_types,
            "last_webhook": self.received_webhooks[-1] if self.received_webhooks else None
        }

# Instancia global
webhooks = RailwayWebhooks()