#!/usr/bin/env python3
"""
BackendBot - Integración con Sistemas Externos
===============================================

Ejemplos de integración de BackendBot con otros sistemas
usando el acceso directo con API key.

Estos ejemplos muestran cómo:
- Integrar con sistemas de monitoreo
- Automatizar tareas programadas
- Conectar con dashboards externos
- Crear webhooks para notificaciones
- Integrar con sistemas de logging
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent
import sys
sys.path.insert(0, str(root_dir))

from api_client import BackendBotAPIClient, load_api_key_from_env


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackendBotIntegrator:
    """Clase para integrar BackendBot con sistemas externos"""

    def __init__(self, api_key=None):
        self.client = BackendBotAPIClient(api_key=api_key)
        self.logger = logging.getLogger(self.__class__.__name__)

    def health_monitor(self):
        """Monitor de salud para sistemas externos"""
        try:
            result = self.client.health_check()
            status = "OK" if result.get("status") == "healthy" else "ERROR"
            return {
                "service": "BackendBot",
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "details": result
            }
        except Exception as e:
            self.logger.error(f"Error en health monitor: {e}")
            return {
                "service": "BackendBot",
                "status": "ERROR",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def system_metrics_collector(self):
        """Colector de métricas del sistema"""
        try:
            status = self.client.get_system_status()
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": status.get("cpu_percent", 0),
                "memory_percent": status.get("memory_percent", 0),
                "disk_usage": status.get("disk_usage", {}),
                "network_io": status.get("network_io", {}),
                "battery": status.get("battery", {})
            }
        except Exception as e:
            self.logger.error(f"Error recolectando métricas: {e}")
            return None

    def automated_backup_scheduler(self, schedule_config):
        """Programador automático de backups"""
        try:
            backup_name = f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result = self.client.create_backup(
                backup_name,
                schedule_config.get("strategy", "incremental")
            )

            self.logger.info(f"Backup automático creado: {backup_name}")
            return result
        except Exception as e:
            self.logger.error(f"Error en backup automático: {e}")
            return None

    def notification_webhook_handler(self, webhook_data):
        """Manejador de webhooks para notificaciones"""
        try:
            # Procesar datos del webhook
            message = webhook_data.get("message", "Notificación desde webhook")
            priority = webhook_data.get("priority", "info")
            channels = webhook_data.get("channels", ["desktop"])

            result = self.client.send_notification(message, priority, channels)
            self.logger.info(f"Webhook procesado: {message}")
            return result
        except Exception as e:
            self.logger.error(f"Error procesando webhook: {e}")
            return None

    def bot_execution_scheduler(self, bot_config):
        """Programador de ejecución de bots"""
        try:
            bot_name = bot_config.get("bot_name")
            action = bot_config.get("action")
            params = bot_config.get("params", {})

            result = self.client.execute_bot(bot_name, action, **params)
            self.logger.info(f"Bot ejecutado: {bot_name}.{action}")
            return result
        except Exception as e:
            self.logger.error(f"Error ejecutando bot: {e}")
            return None


def ejemplo_integracion_monitor_sistema():
    """Ejemplo: Integración con sistema de monitoreo"""
    print("🔍 Integración con Sistema de Monitoreo")
    print("=" * 50)

    integrator = BackendBotIntegrator()

    # Simular colección continua de métricas
    for i in range(3):
        metrics = integrator.system_metrics_collector()
        if metrics:
            print(f"📊 Métricas recolectadas {i+1}:")
            print(json.dumps(metrics, indent=2, ensure_ascii=False))
        time.sleep(2)

    # Health check
    health = integrator.health_monitor()
    print("
❤️  Estado de salud:"    print(json.dumps(health, indent=2, ensure_ascii=False))


def ejemplo_automatizacion_backups():
    """Ejemplo: Automatización de backups"""
    print("\n💾 Automatización de Backups")
    print("=" * 50)

    integrator = BackendBotIntegrator()

    # Configuración de backup automático
    backup_config = {
        "strategy": "incremental",
        "schedule": "daily",
        "retention_days": 30
    }

    result = integrator.automated_backup_scheduler(backup_config)
    if result:
        print("✅ Backup automático creado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ Error creando backup automático")


def ejemplo_webhook_notificaciones():
    """Ejemplo: Webhook para notificaciones"""
    print("\n🔔 Webhook de Notificaciones")
    print("=" * 50)

    integrator = BackendBotIntegrator()

    # Simular datos de webhook
    webhook_data = {
        "message": "🚨 Alerta: CPU por encima del 80%",
        "priority": "high",
        "channels": ["desktop", "email"],
        "source": "monitoring_system"
    }

    result = integrator.notification_webhook_handler(webhook_data)
    if result:
        print("✅ Notificación enviada vía webhook:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ Error enviando notificación vía webhook")


def ejemplo_programacion_bots():
    """Ejemplo: Programación automática de bots"""
    print("\n🤖 Programación de Bots")
    print("=" * 50)

    integrator = BackendBotIntegrator()

    # Configuraciones de bots para ejecutar
    bot_configs = [
        {
            "bot_name": "monitor",
            "action": "status",
            "params": {}
        },
        {
            "bot_name": "organizer",
            "action": "scan",
            "params": {"path": str(Path.home() / "Downloads")}
        },
        {
            "bot_name": "auditor_files",
            "action": "scan",
            "params": {}
        }
    ]

    for config in bot_configs:
        print(f"\n🔄 Ejecutando {config['bot_name']}...")
        result = integrator.bot_execution_scheduler(config)
        if result:
            print(f"✅ Resultado de {config['bot_name']}:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:200] + "...")
        else:
            print(f"❌ Error ejecutando {config['bot_name']}")

        time.sleep(1)


def ejemplo_dashboard_externo():
    """Ejemplo: Integración con dashboard externo"""
    print("\n📊 Dashboard Externo")
    print("=" * 50)

    integrator = BackendBotIntegrator()

    # Recopilar datos para dashboard
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "health": integrator.health_monitor(),
        "metrics": integrator.system_metrics_collector(),
        "bots_status": None
    }

    # Obtener estado de bots
    try:
        dashboard_data["bots_status"] = integrator.client.get_bots_status()
    except Exception as e:
        logger.error(f"Error obteniendo estado de bots: {e}")

    print("📈 Datos recopilados para dashboard:")
    print(json.dumps(dashboard_data, indent=2, ensure_ascii=False, default=str))


def ejemplo_logging_centralizado():
    """Ejemplo: Integración con sistema de logging centralizado"""
    print("\n📝 Logging Centralizado")
    print("=" * 50)

    # Configurar logging para enviar a BackendBot
    class BackendBotLogHandler(logging.Handler):
        def __init__(self, integrator):
            super().__init__()
            self.integrator = integrator

        def emit(self, record):
            try:
                message = self.format(record)
                priority = "error" if record.levelno >= logging.ERROR else "warning" if record.levelno >= logging.WARNING else "info"

                self.integrator.client.send_notification(
                    message=f"Log: {message}",
                    priority=priority,
                    channels=["file"]  # Solo a archivo, no popup
                )
            except Exception:
                pass  # No fallar si BackendBot no está disponible

    # Configurar handler
    integrator = BackendBotIntegrator()
    backend_handler = BackendBotLogHandler(integrator)
    backend_handler.setLevel(logging.WARNING)  # Solo warnings y errores

    # Añadir a logger principal
    logger.addHandler(backend_handler)

    # Generar algunos logs de ejemplo
    logger.info("Esta es una info normal (no se envía)")
    logger.warning("Esta es una advertencia (se envía a BackendBot)")
    logger.error("Este es un error (se envía a BackendBot)")

    print("✅ Sistema de logging centralizado configurado")
    print("Los mensajes de warning y error se enviarán automáticamente a BackendBot")


def main():
    """Función principal con todos los ejemplos de integración"""
    print("🔗 BackendBot - Ejemplos de Integración con Sistemas Externos")
    print("=" * 70)

    # Verificar API key
    api_key = load_api_key_from_env()
    if not api_key:
        print("❌ Error: No se encontró API key en .env")
        print("   Configura BACKENDBOT_MASTER_API_KEY en tu archivo .env")
        sys.exit(1)

    print(f"✅ API Key encontrada: {api_key[:10]}...")
    print("🌐 Conectando a BackendBot API...")

    try:
        # Ejecutar ejemplos de integración
        ejemplo_integracion_monitor_sistema()
        ejemplo_automatizacion_backups()
        ejemplo_webhook_notificaciones()
        ejemplo_programacion_bots()
        ejemplo_dashboard_externo()
        ejemplo_logging_centralizado()

        print("\n" + "=" * 70)
        print("✅ TODOS LOS EJEMPLOS DE INTEGRACIÓN COMPLETADOS")
        print("🔗 BackendBot está listo para integrarse con tus sistemas!")
        print("\n💡 Casos de uso:")
        print("   - Monitoreo continuo del sistema")
        print("   - Backups automáticos programados")
        print("   - Notificaciones vía webhooks")
        print("   - Ejecución automática de bots")
        print("   - Dashboards externos")
        print("   - Logging centralizado")

    except KeyboardInterrupt:
        print("\n⚠️  Ejemplos interrumpidos por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        print("💡 Asegúrate de que BackendBot esté ejecutándose")


if __name__ == "__main__":
    main()