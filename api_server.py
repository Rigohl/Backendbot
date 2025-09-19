#!/usr/bin/env python3
"""
API REST Local - BackendBot
Proporciona endpoints para integraciones externas y automatización
"""
import os
import sys
import json
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import threading

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backendbot.core.di.container import container

# Modelos de datos para la API
class SystemStatus(BaseModel):
    """Estado del sistema"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    battery_percent: Optional[float]
    temperature: Optional[float]
    active_bots: List[str]
    uptime: str

class BotCommand(BaseModel):
    """Comando para un bot"""
    bot_name: str
    action: str
    parameters: Optional[Dict[str, Any]] = {}

class BackupRequest(BaseModel):
    """Solicitud de backup"""
    job_name: str
    async_execution: bool = True

class NotificationRequest(BaseModel):
    """Solicitud de notificación"""
    message: str
    priority: str = "info"
    channels: List[str] = ["desktop"]

class PowerProfileRequest(BaseModel):
    """Cambio de perfil de energía"""
    profile: str

class WebhookConfig(BaseModel):
    """Configuración de webhook"""
    url: str
    events: List[str]
    enabled: bool = True

class BackendBotAPI:
    """API REST principal de BackendBot"""

    def __init__(self):
        self.app = FastAPI(
            title="BackendBot API",
            description="API REST local para BackendBot",
            version="2.0.0"
        )

        self.logger = container.get_logger()
        self.config = container.get_config_manager()

        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # En producción, especificar orígenes permitidos
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Webhooks registrados
        self.webhooks: Dict[str, WebhookConfig] = {}

        # Configurar rutas
        self.setup_routes()

        # Servidor en hilo separado
        self.server_thread = None
        self.running = False

    def setup_routes(self):
        """Configura todas las rutas de la API"""

        @self.app.get("/")
        async def root():
            """Endpoint raíz"""
            return {
                "message": "BackendBot API",
                "version": "2.0.0",
                "status": "running",
                "endpoints": [
                    "/status",
                    "/bots",
                    "/backup",
                    "/power",
                    "/notifications",
                    "/webhooks"
                ]
            }

        @self.app.get("/status", response_model=SystemStatus)
        async def get_system_status():
            """Obtiene el estado actual del sistema"""
            try:
                # Obtener métricas del sistema
                import psutil

                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                battery = psutil.sensors_battery()

                # Obtener bots activos (simulado)
                active_bots = ["monitor", "guardian"]  # En producción, obtener de BotManager

                # Calcular uptime
                uptime = str(timedelta(seconds=int(psutil.boot_time() - datetime.now().timestamp())))

                return SystemStatus(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_percent=disk.percent,
                    battery_percent=battery.percent if battery else None,
                    temperature=None,  # Implementar si hay sensores
                    active_bots=active_bots,
                    uptime=uptime
                )
            except Exception as e:
                self.logger.error(f"Error obteniendo estado del sistema: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/bots")
        async def get_bots_status():
            """Obtiene el estado de todos los bots"""
            # En producción, obtener del BotManager real
            return {
                "bots": [
                    {"name": "monitor", "status": "running", "last_activity": datetime.now().isoformat()},
                    {"name": "organizer", "status": "idle", "last_activity": datetime.now().isoformat()},
                    {"name": "indexer", "status": "running", "last_activity": datetime.now().isoformat()},
                    {"name": "guardian", "status": "running", "last_activity": datetime.now().isoformat()},
                    {"name": "optimizer", "status": "idle", "last_activity": datetime.now().isoformat()}
                ]
            }

        @self.app.post("/bots/command")
        async def execute_bot_command(command: BotCommand, background_tasks: BackgroundTasks):
            """Ejecuta un comando en un bot"""
            try:
                self.logger.info(f"Ejecutando comando en bot {command.bot_name}: {command.action}")

                # En producción, enrutar al bot correspondiente
                if command.bot_name == "monitor":
                    # Simular acción
                    result = {"status": "executed", "action": command.action, "result": "success"}
                elif command.bot_name == "organizer":
                    result = {"status": "executed", "action": command.action, "files_processed": 10}
                else:
                    result = {"status": "unknown_bot", "bot": command.bot_name}

                # Notificar webhooks
                background_tasks.add_task(self.notify_webhooks, "bot_command", {
                    "bot": command.bot_name,
                    "action": command.action,
                    "timestamp": datetime.now().isoformat()
                })

                return result

            except Exception as e:
                self.logger.error(f"Error ejecutando comando de bot: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/backup")
        async def create_backup(request: BackupRequest, background_tasks: BackgroundTasks):
            """Crea un backup"""
            try:
                self.logger.info(f"Iniciando backup: {request.job_name}")

                if request.async_execution:
                    # Ejecutar en background
                    background_tasks.add_task(self.execute_backup_async, request.job_name)
                    return {"status": "accepted", "message": "Backup iniciado en segundo plano"}
                else:
                    # Ejecutar inmediatamente
                    result = await self.execute_backup_sync(request.job_name)
                    return result

            except Exception as e:
                self.logger.error(f"Error creando backup: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/power/profile")
        async def change_power_profile(request: PowerProfileRequest):
            """Cambia el perfil de energía"""
            try:
                valid_profiles = ["high_performance", "balanced", "power_saver", "ultra_low"]

                if request.profile not in valid_profiles:
                    raise HTTPException(status_code=400, detail=f"Perfil inválido. Opciones: {valid_profiles}")

                self.logger.info(f"Cambiando perfil de energía a: {request.profile}")

                # En producción, aplicar el perfil usando PowerManager
                return {"status": "applied", "profile": request.profile}

            except Exception as e:
                self.logger.error(f"Error cambiando perfil de energía: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/notifications")
        async def send_notification(request: NotificationRequest):
            """Envía una notificación"""
            try:
                self.logger.info(f"Enviando notificación: {request.message}")

                # En producción, usar NotificationManager
                return {
                    "status": "sent",
                    "message": request.message,
                    "priority": request.priority,
                    "channels": request.channels
                }

            except Exception as e:
                self.logger.error(f"Error enviando notificación: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/webhooks")
        async def get_webhooks():
            """Obtiene todos los webhooks configurados"""
            return {"webhooks": list(self.webhooks.values())}

        @self.app.post("/webhooks")
        async def register_webhook(webhook: WebhookConfig):
            """Registra un nuevo webhook"""
            try:
                webhook_id = f"webhook_{len(self.webhooks)}"
                self.webhooks[webhook_id] = webhook
                self.logger.info(f"Webhook registrado: {webhook.url}")
                return {"status": "registered", "id": webhook_id}

            except Exception as e:
                self.logger.error(f"Error registrando webhook: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/webhooks/{webhook_id}")
        async def remove_webhook(webhook_id: str):
            """Elimina un webhook"""
            if webhook_id in self.webhooks:
                del self.webhooks[webhook_id]
                return {"status": "removed"}
            else:
                raise HTTPException(status_code=404, detail="Webhook no encontrado")

    async def execute_backup_sync(self, job_name: str) -> Dict:
        """Ejecuta un backup de forma síncrona"""
        # Simular backup
        await asyncio.sleep(2)  # Simular tiempo de backup
        return {
            "status": "completed",
            "job_name": job_name,
            "files_processed": 150,
            "size_mb": 45.2,
            "duration_seconds": 2
        }

    async def execute_backup_async(self, job_name: str):
        """Ejecuta un backup de forma asíncrona"""
        try:
            # Simular backup en background
            await asyncio.sleep(5)
            self.logger.info(f"Backup asíncrono completado: {job_name}")

            # Notificar webhooks
            await self.notify_webhooks("backup_completed", {
                "job_name": job_name,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            self.logger.error(f"Error en backup asíncrono: {e}")

    async def notify_webhooks(self, event: str, data: Dict):
        """Notifica a todos los webhooks registrados para un evento"""
        import aiohttp

        for webhook_id, webhook in self.webhooks.items():
            if webhook.enabled and event in webhook.events:
                try:
                    async with aiohttp.ClientSession() as session:
                        payload = {
                            "event": event,
                            "timestamp": datetime.now().isoformat(),
                            "data": data
                        }

                        async with session.post(webhook.url, json=payload) as response:
                            if response.status == 200:
                                self.logger.info(f"Webhook notificado: {webhook.url}")
                            else:
                                self.logger.warning(f"Error en webhook {webhook.url}: {response.status}")

                except Exception as e:
                    self.logger.error(f"Error notificando webhook {webhook.url}: {e}")

    def start_server(self, host: str = "127.0.0.1", port: int = 8000):
        """Inicia el servidor API en un hilo separado"""
        def run_server():
            try:
                self.logger.info(f"Iniciando API server en {host}:{port}")
                uvicorn.run(
                    self.app,
                    host=host,
                    port=port,
                    log_level="info"
                )
            except Exception as e:
                self.logger.error(f"Error iniciando servidor API: {e}")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True
        self.logger.info("Servidor API iniciado en segundo plano")

    def stop_server(self):
        """Detiene el servidor API"""
        self.running = False
        self.logger.info("Servidor API detenido")

# Instancia global de la API
api_instance = BackendBotAPI()

def main():
    """Función principal para ejecutar la API"""
    import argparse

    parser = argparse.ArgumentParser(description="BackendBot API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host para el servidor")
    parser.add_argument("--port", type=int, default=8000, help="Puerto para el servidor")
    parser.add_argument("--reload", action="store_true", help="Recargar en cambios (desarrollo)")

    args = parser.parse_args()

    print("🚀 Iniciando BackendBot API Server")
    print(f"📍 URL: http://{args.host}:{args.port}")
    print(f"📚 Docs: http://{args.host}:{args.port}/docs")
    print("=" * 50)

    try:
        uvicorn.run(
            api_instance.app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

if __name__ == "__main__":
    main()