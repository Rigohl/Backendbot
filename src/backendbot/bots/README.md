# Bots de BackendBot

- `bot_monitor_ui.py`: Monitorea recursos y reporta a la UI.
- `bot_ui_connector.py`: Conector genérico para comunicación UI <-> bots.

## Plantillas para otros bots
- Crea nuevos bots siguiendo el patrón de `BotMonitorUI`, usando el conector para enviar mensajes y recibir comandos.
- Ejemplo de inicialización:

```python
from src.backendbot.ui.bot_bridge import BotBridge
from src.backendbot.bots.bot_ui_connector import BotUIConnector
from src.backendbot.bots.bot_guardian import BotGuardianUI

bridge = BotBridge()
connector = BotUIConnector(bridge)
guardian = BotGuardianUI(connector)
```
