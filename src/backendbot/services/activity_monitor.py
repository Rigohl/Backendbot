"""
Servicio de monitoreo de actividad del usuario para BackendBot.
Detecta inactividad y controla el estado del backend automáticamente.
"""

import asyncio
import time
import threading
from typing import Optional, Callable
import psutil
import win32api
import win32con
import win32gui
from pynput import mouse, keyboard
from plyer import notification

from backendbot.config import settings
from backendbot.utils import log_event, notify


class ActivityMonitor:
    """Monitorea la actividad del usuario y controla el backend."""

    def __init__(self):
        self.last_activity = time.time()
        self.is_active = True
        self.backend_process: Optional[psutil.Process] = None
        self.monitoring = False
        self.inactivity_timer: Optional[threading.Timer] = None
        self.warning_shown = False

        # Callbacks
        self.on_inactivity_detected: Optional[Callable] = None
        self.on_activity_resumed: Optional[Callable] = None
        self.on_backend_start: Optional[Callable] = None
        self.on_backend_stop: Optional[Callable] = None

        # Listeners
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None

    def start_monitoring(self):
        """Inicia el monitoreo de actividad."""
        if self.monitoring:
            return

        log_event("Iniciando monitoreo de actividad del usuario")
        self.monitoring = True
        self.last_activity = time.time()

        # Iniciar listeners
        self._start_listeners()

        # Iniciar tarea de monitoreo
        asyncio.create_task(self._monitor_loop())

    def stop_monitoring(self):
        """Detiene el monitoreo de actividad."""
        if not self.monitoring:
            return

        log_event("Deteniendo monitoreo de actividad")
        self.monitoring = False

        # Detener listeners
        self._stop_listeners()

        # Cancelar timer si existe
        if self.inactivity_timer:
            self.inactivity_timer.cancel()
            self.inactivity_timer = None

    def _start_listeners(self):
        """Inicia los listeners de mouse y teclado."""
        try:
            self.mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            self.mouse_listener.start()

            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()

        except Exception as e:
            log_event(f"Error iniciando listeners: {e}")

    def _stop_listeners(self):
        """Detiene los listeners."""
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def _on_mouse_move(self, x, y):
        """Callback para movimiento del mouse."""
        self._update_activity()

    def _on_mouse_click(self, x, y, button, pressed):
        """Callback para clicks del mouse."""
        if pressed:
            self._update_activity()

    def _on_mouse_scroll(self, x, y, dx, dy):
        """Callback para scroll del mouse."""
        self._update_activity()

    def _on_key_press(self, key):
        """Callback para teclas presionadas."""
        self._update_activity()

    def _on_key_release(self, key):
        """Callback para teclas liberadas."""
        self._update_activity()

    def _update_activity(self):
        """Actualiza el timestamp de última actividad."""
        self.last_activity = time.time()

        if not self.is_active:
            self._resume_activity()

    def _resume_activity(self):
        """Reanuda la actividad después de inactividad."""
        log_event("Actividad del usuario detectada - reanudando")
        self.is_active = True
        self.warning_shown = False

        # Cancelar timer de apagado
        if self.inactivity_timer:
            self.inactivity_timer.cancel()
            self.inactivity_timer = None

        # Callback
        if self.on_activity_resumed:
            self.on_activity_resumed()

        # Iniciar backend si no está corriendo
        if not self._is_backend_running():
            self._start_backend()

    async def _monitor_loop(self):
        """Loop principal de monitoreo."""
        while self.monitoring:
            current_time = time.time()
            inactive_time = current_time - self.last_activity

            if self.is_active and inactive_time > settings.INACTIVITY_WARNING_TIME:
                self._handle_inactivity_warning()
            elif not self.is_active and inactive_time > settings.INACTIVITY_SHUTDOWN_TIME:
                self._handle_shutdown()

            await asyncio.sleep(1)

    def _handle_inactivity_warning(self):
        """Maneja la detección de inactividad."""
        if self.warning_shown:
            return

        log_event("Inactividad detectada - mostrando advertencia")
        self.is_active = False
        self.warning_shown = True

        # Mostrar notificación
        try:
            notification.notify(
                title="BackendBot - Inactividad Detectada",
                message="¿Sigues ahí? El sistema se apagará en 3 minutos si no hay respuesta.",
                timeout=10
            )
        except Exception as e:
            log_event(f"Error mostrando notificación: {e}")

        # Callback
        if self.on_inactivity_detected:
            self.on_inactivity_detected()

        # Programar apagado automático
        self.inactivity_timer = threading.Timer(
            settings.INACTIVITY_SHUTDOWN_TIME - settings.INACTIVITY_WARNING_TIME,
            self._shutdown_backend
        )
        self.inactivity_timer.start()

    def _handle_shutdown(self):
        """Maneja el apagado por inactividad prolongada."""
        log_event("Tiempo de inactividad agotado - apagando backend")
        self._shutdown_backend()

    def _start_backend(self):
        """Inicia el backend."""
        if self._is_backend_running():
            return

        try:
            log_event("Iniciando backend por actividad detectada")
            import subprocess
            import sys
            import os

            # Ejecutar en segundo plano
            backend_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "main.py"
            )

            process = subprocess.Popen(
                [sys.executable, backend_path],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.backend_process = psutil.Process(process.pid)

            # Callback
            if self.on_backend_start:
                self.on_backend_start()

        except Exception as e:
            log_event(f"Error iniciando backend: {e}")

    def _shutdown_backend(self):
        """Apaga el backend."""
        if not self._is_backend_running():
            return

        try:
            log_event("Apagando backend por inactividad")
            if self.backend_process:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                self.backend_process = None

            # Callback
            if self.on_backend_stop:
                self.on_backend_stop()

        except Exception as e:
            log_event(f"Error apagando backend: {e}")

    def _is_backend_running(self) -> bool:
        """Verifica si el backend está ejecutándose."""
        if not self.backend_process:
            return False

        try:
            return self.backend_process.is_running()
        except:
            return False

    def get_status(self) -> dict:
        """Obtiene el estado actual del monitor."""
        return {
            "monitoring": self.monitoring,
            "is_active": self.is_active,
            "last_activity": self.last_activity,
            "backend_running": self._is_backend_running(),
            "warning_shown": self.warning_shown,
            "inactive_seconds": time.time() - self.last_activity
        }


# Instancia global
activity_monitor = ActivityMonitor()