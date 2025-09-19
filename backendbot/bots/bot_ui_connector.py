"""Conector entre los bots y la UI (BotBridge).
Permite a los bots enviar mensajes y recibir comandos de la UI.
"""

import queue
import threading


class BotUIConnector:
    def __init__(self, bridge) -> None:
        self.bridge = bridge
        self.running = True
        self.worker = threading.Thread(target=self.process_commands, daemon=True)
        self.worker.start()

    def send_message(self, msg: str):
        self.bridge.message_queue.put(msg)

    def process_commands(self):
        while self.running:
            try:
                cmd = self.bridge.command_queue.get(timeout=1)
                # Aquí se integraría el procesamiento real del comando por los bots
                self.send_message(f"Comando recibido por bots: {cmd}")
            except queue.Empty:
                continue

    def stop(self):
        self.running = False
