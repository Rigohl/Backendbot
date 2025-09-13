# local_agent.py
# Este script se ejecuta en tu PC para monitorear la actividad y comunicarse con el backend en Railway.

import time
import threading
import httpx
import os
from pynput import mouse, keyboard

# --- Configuración --- #
# URL de tu backend en Railway (cámbiala cuando tengas la URL pública)
BACKEND_URL = "http://localhost:8000"  # Placeholder: Reemplazar con tu URL de Railway
API_KEY = "your-super-secret-api-key-goes-here"  # La misma API Key que en tu .env

# Tiempo en segundos para considerar que el usuario está inactivo
INACTIVITY_TIMEOUT_SECONDS = 300  # 5 minutos

# Intervalo en segundos para que el agente revise el estado
AGENT_SLEEP_INTERVAL_SECONDS = 10


class ActivityMonitor:
    """Monitorea la actividad del mouse y teclado y se comunica con el backend."""

    def __init__(self):
        self.last_activity_time = time.time()
        self.is_inactive_state = False
        self.http_client = httpx.Client(headers={"X-API-Key": API_KEY})

    def _update_last_activity(self, *args):
        """Actualiza el timestamp de la última actividad detectada."""
        # Si estábamos en estado inactivo, informamos al backend que volvimos.
        if self.is_inactive_state:
            print("[INFO] Actividad detectada. Volviendo a estado activo.")
            try:
                # Futuro endpoint para notificar al backend que el usuario ha vuelto.
                # self.http_client.post(f"{BACKEND_URL}/api/agent/active")
                pass
            except httpx.RequestError as e:
                print(f"[ERROR] No se pudo comunicar con el backend: {e}")

        self.last_activity_time = time.time()
        self.is_inactive_state = False

    def _start_listeners(self):
        """Inicia los listeners de mouse y teclado en un hilo separado."""
        # Usamos un hilo "daemon" para que no bloquee la salida del programa principal.
        mouse_listener = mouse.Listener(
            on_move=self._update_last_activity,
            on_click=self._update_last_activity,
            on_scroll=self._update_last_activity
        )
        keyboard_listener = keyboard.Listener(on_press=self._update_last_activity)

        listener_thread = threading.Thread(
            target=lambda: (mouse_listener.start(), keyboard_listener.start()),
            daemon=True
        )
        listener_thread.start()
        print("[INFO] Monitores de actividad iniciados.")

    def run(self):
        """Inicia el ciclo principal del agente."""
        self._start_listeners()

        while True:
            time_since_last_activity = time.time() - self.last_activity_time

            if not self.is_inactive_state and time_since_last_activity > INACTIVITY_TIMEOUT_SECONDS:
                print(f"[INFO] Inactividad detectada por más de {INACTIVITY_TIMEOUT_SECONDS} segundos.")
                self.is_inactive_state = True
                try:
                    # 1. Notificar al backend que el usuario está inactivo.
                    #    El backend podría entonces enviar una notificación (Discord, etc.)
                    print("[ACTION] Notificando al backend sobre inactividad (simulado).")
                    # response = self.http_client.post(f"{BACKEND_URL}/api/agent/inactive")
                    # response.raise_for_status()

                except httpx.RequestError as e:
                    print(f"[ERROR] No se pudo notificar inactividad al backend: {e}")

            if self.is_inactive_state:
                # 2. Si estamos inactivos, empezamos a preguntar al backend si debemos apagar.
                try:
                    print("[ACTION] Preguntando al backend si se debe apagar (simulado).")
                    # response = self.http_client.get(f"{BACKEND_URL}/api/agent/should_shutdown")
                    # response.raise_for_status()
                    # data = response.json()

                    # if data.get("shutdown"):
                    #     print("[CRITICAL] Orden de apagado recibida. Apagando el PC en 30 segundos.")
                    #     # ¡¡CUIDADO!! Esta línea apagará tu PC.
                    #     # En Windows: os.system("shutdown /s /t 30")
                    #     # En Linux/macOS: os.system("shutdown -h +1")
                    #     break # Terminar el script

                except httpx.RequestError as e:
                    print(f"[ERROR] No se pudo consultar el estado de apagado: {e}")

            # Esperar antes de la siguiente verificación.
            time.sleep(AGENT_SLEEP_INTERVAL_SECONDS)

if __name__ == "__main__":
    print("Iniciando agente local de BackendBot...")
    monitor = ActivityMonitor()
    monitor.run()