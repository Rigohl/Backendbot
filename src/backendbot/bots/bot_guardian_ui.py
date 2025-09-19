"""
Bot Guardián: supervisa bots activos y reporta a la UI.
"""
import threading
import time

class BotGuardianUI:
    def __init__(self, ui_connector, bots=None):
        self.ui_connector = ui_connector
        self.bots = bots if bots is not None else []
        self.running = True
        self.thread = threading.Thread(target=self.guardian_loop, daemon=True)
        self.thread.start()

    def guardian_loop(self):
        while self.running:
            for bot in self.bots:
                if hasattr(bot, 'running') and not bot.running:
                    self.ui_connector.send_message(f"Bot detenido: {bot.__class__.__name__}")
                    # Aquí podría reiniciarse el bot si se desea
            time.sleep(10)

    def stop(self):
        self.running = False
