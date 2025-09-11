import os
import subprocess
import webbrowser

import requests
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem, SubMenu

from .utils import log_event  # Import log_event and notify from utils

FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BACKEND = os.path.join(FOLDER, "src", "backendbot", "backend.py")


def create_image():
    img = Image.new("RGBA", (64, 64), (255, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((16, 16, 48, 48), fill=(255, 0, 0))
    return img


def open_dashboard():
    webbrowser.open("http://127.0.0.1:8000")
    log_event("🖥 Dashboard abierto desde bandeja")


def restart_backend(icon, item):
    log_event("♻️ Reiniciando backend por acción de usuario")
    subprocess.run([os.path.join(FOLDER, "restart_backend.bat")], check=False)


def quit_tray(icon, item):
    log_event("⛔ Tray cerrado manualmente por usuario")
    icon.stop()


def get_current_mode():
    try:
        response = requests.get("http://127.0.0.1:8000/get-modo")
        if response.status_code == 200:
            return response.json().get("modo")
    except Exception as e:
        log_event(f"❌ Error al obtener modo actual del backend: {e}")
    return "diario"  # Default mode if backend is not available or error occurs


def set_modo(icon, item, modo):
    try:
        response = requests.post(f"http://127.0.0.1:8000/set-modo/{modo}")
        if response.status_code == 200:
            log_event(f"🔄 Modo cambiado a {modo}")
            # Restaurar procesos importantes si es necesario
            requests.post("http://127.0.0.1:8000/restore-important")
            update_menu(icon)  # Update the menu to reflect the new mode
        else:
            log_event(f"❌ Error al cambiar modo: {response.text}")
    except Exception as e:
        log_event(f"❌ Error al conectar al backend: {e}")


def update_menu(icon):
    current_mode = get_current_mode()
    icon.menu = Menu(
        SubMenu(
            "Modos",
            [
                MenuItem(
                    "Diario" + (" ✅" if current_mode == "diario" else ""),
                    lambda icon, item: set_modo(icon, item, "diario"),
                ),
                MenuItem(
                    "Editor" + (" ✅" if current_mode == "editor" else ""),
                    lambda icon, item: set_modo(icon, item, "editor"),
                ),
                MenuItem(
                    "Videojuego" + (" ✅" if current_mode == "videojuego" else ""),
                    lambda icon, item: set_modo(icon, item, "videojuego"),
                ),
            ],
        ),
        MenuItem("Abrir Dashboard", lambda icon, item: open_dashboard()),
        MenuItem("Reiniciar Backend", restart_backend),
        MenuItem("Salir", quit_tray),
    )


icon = Icon("BackendBot", create_image(), "BackendBot")
update_menu(icon)  # Initial menu creation


# Click izquierdo -> abrir dashboard
def on_click(icon, event, button, pressed):
    if pressed and button == 1:
        open_dashboard()


log_event("✅ Tray iniciado")
icon.run_detached()
icon._listener.click = on_click
