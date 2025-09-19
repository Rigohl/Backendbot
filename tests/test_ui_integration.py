"""
Prueba de integración básica entre la UI y los bots usando BotBridge y BotUIConnector.
"""
from backendbot.ui.bot_bridge import BotBridge
from backendbot.bots.bot_ui_connector import BotUIConnector
import time

def test_ui_bot_communication():
    bridge = BotBridge()
    connector = BotUIConnector(bridge)
    bridge.send_command("prueba_comando")
    time.sleep(1)
    msg = bridge.get_next_message()
    assert msg is not None and "Comando recibido" in msg
    connector.stop()
    bridge.stop()
