"""
Módulo de comunicación entre la UI y los bots de BackendBot.
Permite enviar comandos y recibir mensajes/notificaciones.
"""
import threading
import queue

class BotBridge:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.message_queue = queue.Queue()
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_messages, daemon=True)
        self.listener_thread.start()

    def send_command(self, cmd: str):
        self.command_queue.put(cmd)

    def get_next_message(self):
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None

    def listen_messages(self):
        while self.running:
            # Aquí se integrará la lógica real de escucha de mensajes de los bots
            pass

    def stop(self):
        self.running = False
