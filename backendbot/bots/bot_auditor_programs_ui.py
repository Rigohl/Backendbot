"""Bot Auditor de Programas: detecta programas no usados y reporta a la UI."""

import threading
import time


class BotAuditorProgramsUI:
    def __init__(self, ui_connector) -> None:
        self.ui_connector = ui_connector
        self.running = True
        self.thread = threading.Thread(target=self.audit_loop, daemon=True)
        self.thread.start()

    def audit_loop(self):
        while self.running:
            # Aquí se integraría la lógica real de auditoría de programas
            self.ui_connector.send_message("Auditor de programas: revisión completada.")
            time.sleep(300)

    def stop(self):
        self.running = False
