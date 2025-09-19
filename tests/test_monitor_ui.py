"""
Prueba de integración del Bot Monitor con la UI.
"""
from backendbot.ui.bot_bridge import BotBridge
from backendbot.bots.bot_ui_connector import BotUIConnector
from backendbot.bots.bot_monitor_ui import BotMonitorUI
import time

def test_monitor_ui_message():
    bridge = BotBridge()
    connector = BotUIConnector(bridge)
    monitor = BotMonitorUI(connector)
    time.sleep(6)
    msg = bridge.get_next_message()
    assert msg is not None and "CPU" in msg
    monitor.stop()
    connector.stop()
    bridge.stop()
