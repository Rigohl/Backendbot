"""Servidor API para BackendBot - Principio de Responsabilidad Única."""

from __future__ import annotations
from typing import Optional
import logging
from fastapi import FastAPI
from uvicorn import Server, Config

from backendbot.core.config import Settings

logger = logging.getLogger(__name__)


class APIServer:
    """Servidor API FastAPI - Principio de Responsabilidad Única"""

    def __init__(self, settings: Settings):
        """Inicializar servidor API"""
        self.settings = settings
        self.app: Optional[FastAPI] = None
        self.server: Optional[Server] = None
        self._is_running = False

    def create_app(self) -> FastAPI:
        """Crear aplicación FastAPI"""
        app = FastAPI(
            title="BackendBot API",
            description="API para BackendBot - Sistema de Automatización",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )

        # Health check endpoint
        @app.get("/api/v1/health")
        async def health_check():
            return {"status": "healthy", "service": "BackendBot API"}

        # API v1 routes
        @app.get("/api/v1/status")
        async def get_status():
            return {"status": "running", "version": "1.0.0"}

        self.app = app
        return app

    def configure_server(self) -> None:
        """Configurar servidor uvicorn"""
        if not self.app:
            self.app = self.create_app()

        config = Config(
            app=self.app,
            host=self.settings.api.host,
            port=self.settings.api.port,
            log_level="info",
            access_log=False  # Desactivar logs de acceso por seguridad
        )

        self.server = Server(config)

    def start(self) -> None:
        """Iniciar servidor"""
        if not self.server:
            self.configure_server()

        logger.info(f"Starting API server on {self.settings.api.host}:{self.settings.api.port}")
        self._is_running = True

        try:
            self.server.run()
        except KeyboardInterrupt:
            logger.info("API server stopped by user")
        except Exception as e:
            logger.error(f"Error running API server: {e}")
        finally:
            self._is_running = False

    def stop(self) -> None:
        """Detener servidor"""
        if self.server and self._is_running:
            logger.info("Stopping API server...")
            self.server.should_exit = True
            self._is_running = False

    @property
    def is_running(self) -> bool:
        """Verificar si el servidor está ejecutándose"""
        return self._is_running

    def get_app(self) -> Optional[FastAPI]:
        """Obtener instancia de FastAPI"""
        return self.app