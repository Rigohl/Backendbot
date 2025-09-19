# UI de BackendBot

## Componentes
- `tray_icon.py`: Icono de bandeja del sistema (PyQt5)
- `floating_panel.py`: Panel flotante tipo chat (PyQt5)
- `bot_bridge.py`: Comunicación entre UI y bots
- `main_ui.py`: Lanzador principal de la UI

## Ejecución
1. Instala dependencias: `pip install PyQt5`
2. Ejecuta: `python -m src.backendbot.ui.main_ui`

## Integración
- Los comandos enviados desde el panel flotante se transmiten a los bots vía `BotBridge`.
- Los mensajes/notificaciones de los bots se muestran en tiempo real en el panel.

## Buenas prácticas
- Mantener la lógica de UI desacoplada de la lógica de bots.
- Documentar cada componente y flujo de usuario.
- Actualizar dependencias regularmente.
