import os
import subprocess
import webbrowser

import requests
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

# I need to import the log_event function correctly
from src.backendbot.utils import log_event 

FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BACKEND = os.path.join(FOLDER, "src", "backendbot", "backend.py")

# --- Icon Creation --- 
def create_icon(color):
    """Creates a 64x64 icon with a circle of the specified color."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((12, 12, 52, 52), fill=color)
    return img

# --- State --- 
is_active = False
ICON_BLUE = create_icon((59, 130, 246)) # #3B82F6
ICON_RED = create_icon((239, 68, 68))   # #EF4444

# --- Menu Actions --- 
def open_dashboard(icon, item):
    webbrowser.open("http://127.0.0.1:8000")
    log_event("🖥️ Dashboard abierto desde bandeja")

def restart_backend(icon, item):
    log_event("♻️ Reiniciando backend por acción de usuario", notify_user=True)
    subprocess.run([os.path.join(FOLDER, "restart_backend.bat")], check=False)

def quit_tray(icon, item):
    log_event("⛔ Tray cerrado manualmente por usuario")
    icon.stop()

def get_current_mode():
    try:
        response = requests.get("http://127.0.0.1:8000/get-modo")
        if response.status_code == 200:
            return response.json().get("modo", "diario")
    except Exception as e:
        log_event(f"❌ Error al obtener modo actual: {e}")
    return "diario"

def set_modo(icon, item, modo):
    try:
        response = requests.post(f"http://127.0.0.1:8000/set-modo/{modo}")
        if response.status_code == 200:
            log_event(f"🔄 Modo cambiado a {modo}", notify_user=True)
            requests.post("http://127.0.0.1:8000/restore-important")
            update_menu(icon)
        else:
            log_event(f"❌ Error al cambiar modo: {response.text}", level="error", notify_user=True)
    except Exception as e:
        log_event(f"❌ Error al conectar al backend: {e}", level="error", notify_user=True)

# --- New Test/Toggle Functions --- 
def send_test_notification(icon, item):
    log_event("Esta es una notificación de prueba.", notify_user=True)

def toggle_active_state(icon, item):
    global is_active
    is_active = not is_active
    icon.icon = ICON_RED if is_active else ICON_BLUE
    status_message = f"Modo de monitoreo activo: {'ON' if is_active else 'OFF'}"
    log_event(status_message, notify_user=True)

# --- Menu Definition --- 
def update_menu(icon):
    current_mode = get_current_mode()
    icon.menu = Menu(
        MenuItem("Abrir Dashboard", open_dashboard),
        MenuItem("Modos", Menu(
            MenuItem("Diario" + (" ✅" if current_mode == "diario" else ""), lambda: set_modo(icon, None, "diario")),
            MenuItem("Editor" + (" ✅" if current_mode == "editor" else ""), lambda: set_modo(icon, None, "editor")),
            MenuItem("Videojuego" + (" ✅" if current_mode == "videojuego" else ""), lambda: set_modo(icon, None, "videojuego")),
            MenuItem("Streaming" + (" ✅" if current_mode == "streaming" else ""), lambda: set_modo(icon, None, "streaming")),
            MenuItem("Multimedia" + (" ✅" if current_mode == "multimedia" else ""), lambda: set_modo(icon, None, "multimedia")),
        )),
        Menu.SEPARATOR,
        MenuItem("Activar/Desactivar Monitoreo", toggle_active_state, checked=lambda item: is_active),
        MenuItem("Enviar Notificación de Prueba", send_test_notification),
        Menu.SEPARATOR,
        MenuItem("Reiniciar Backend", restart_backend),
        MenuItem("Salir", quit_tray),
    )

# --- Icon Setup --- 
icon = Icon("BackendBot", ICON_BLUE, "BackendBot")

# Click izquierdo -> abrir dashboard
def on_click(icon, item):
    if isinstance(item, str) and item == 'left_click':
        open_dashboard(icon, item)

def run_tray_icon():
    update_menu(icon)
    log_event("✅ Tray iniciado")
    # This is a workaround for left-click handling in pystray
    icon.run_detached(on_click=on_click)

if __name__ == "__main__":
    run_tray_icon()
