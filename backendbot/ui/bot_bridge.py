"""Bot Bridge - Puente de comunicación entre la UI y los bots."""

import queue
import threading


class BotBridge:
    """Puente de comunicación entre la interfaz de usuario y los bots especializados.
    Maneja mensajes, comandos y coordinación entre componentes.
    """

    def __init__(self) -> None:
        self.message_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.bots = {}
        self._running = False

    def register_bot(self, bot_name: str, bot_instance):
        """Registrar un bot en el puente."""
        self.bots[bot_name] = bot_instance

    def send_message(self, message: str, bot_name: str | None = None):
        """Enviar mensaje a la cola para que lo procese la UI."""
        self.message_queue.put(
            {
                "message": message,
                "bot": bot_name,
                "timestamp": threading.current_thread().name,
            }
        )

    def get_next_message(self) -> dict | None:
        """Obtener el siguiente mensaje de la cola (no bloqueante)."""
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None

    def send_command(self, command: str, target_bot: str | None = None):
        """Enviar comando a un bot específico o broadcast."""
        self.command_queue.put(
            {
                "command": command,
                "target": target_bot,
                "timestamp": threading.current_thread().name,
            }
        )

    def get_next_command(self) -> dict | None:
        """Obtener el siguiente comando de la cola."""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None

    def start(self):
        """Iniciar el puente de comunicación."""
        self._running = True
        # Aquí se podrían iniciar hilos para manejar comunicación entre bots

    def stop(self):
        """Detener el puente de comunicación."""
        self._running = False

    def is_running(self) -> bool:
        """Verificar si el puente está activo."""
        return self._running


# Instancia global del puente
bot_bridge = BotBridge()
