"""
Pruebas básicas para la UI de BackendBot (tray icon y panel flotante).
"""
def test_import_tray_icon():
    try:
        from src.backendbot.ui import tray_icon
    except ImportError:
        assert False, "No se pudo importar tray_icon"

def test_import_floating_panel():
    try:
        from src.backendbot.ui import floating_panel
    except ImportError:
        assert False, "No se pudo importar floating_panel"
