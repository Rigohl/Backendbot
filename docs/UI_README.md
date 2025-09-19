# UI de BackendBot

## Estructura
- `tray_icon.py`: Icono de bandeja del sistema (PyQt5).
- `floating_panel.py`: Panel flotante tipo chat (PyQt5).

## Requisitos
- PyQt5: `pip install PyQt5`

## Pruebas
- Ejecutar `pytest tests/test_ui.py` para validar importaciones básicas.

## Buenas prácticas
- Mantener la lógica de UI desacoplada de la lógica de bots.
- Documentar cada componente y flujo de usuario.
- Actualizar dependencias regularmente (ver `.github/dependabot.yml`).
