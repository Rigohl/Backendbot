import os
import subprocess
import webbrowser
import requests
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

# Correct import for log_event and notify
from src.backendbot.utils import log_event, notify

FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# BACKEND = os.path.join(FOLDER, "src", "backendbot", "backend.py") # Not directly used here

# --- Icon Creation ---
def create_icon_image(color):
    """Creates a 64x64 icon with a circle of the specified color."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0)) # Transparent background
    draw = ImageDraw.Draw(img)
    draw.ellipse((12, 12, 52, 52), fill=color) # Draw a circle
    return img

# --- State ---
is_monitoring_active = False # Renamed for clarity
ICON_BLUE = create_icon_image((59, 130, 246)) # #3B82F6
ICON_RED = create_icon_image((239, 68, 68))   # #EF4444

# --- Menu Actions ---
def open_dashboard(icon, item):
    webbrowser.open("http://127.0.0.1:8000")
    log_event("🖥️ Dashboard abierto desde bandeja", notify_user=True)

def restart_backend(icon, item):
    log_event("♻️ Reiniciando backend por acción de usuario", notify_user=True)
    # Assuming restart_backend.bat is in the root FOLDER
    subprocess.Popen([os.path.join(FOLDER, "restart_backend.bat")], shell=True)
    # Give some time for backend to restart before trying to update menu
    # time.sleep(5) # This would block the tray icon, better to update asynchronously or on next check
    # update_menu(icon) # Will be updated on next cycle or manual refresh

def quit_tray(icon, item):
    log_event("⛔ Tray cerrado manualmente por usuario", notify_user=True)
    icon.stop()

def get_current_mode():
    try:
        response = requests.get("http://127.0.0.1:8000/get-modo")
        if response.status_code == 200:
            return response.json().get("modo", "diario")
    except requests.exceptions.ConnectionError as e:
        log_event(f"❌ Error de conexión al obtener modo actual: {e}", level="error")
    except Exception as e:
        log_event(f"❌ Error inesperado al obtener modo actual: {e}", level="error")
    return "diario" # Default mode if backend is not available or error occurs

def set_modo(icon, item, modo):
    try:
        response = requests.post(f"http://127.0.0.1:8000/set-modo/{modo}")
        if response.status_code == 200:
            log_event(f"🔄 Modo cambiado a {modo}", notify_user=True)
            # This call might also fail if backend is down, handle it
            try:
                requests.post("http://127.0.0.1:8000/restore-important")
            except requests.exceptions.ConnectionError:
                log_event("❌ No se pudo restaurar procesos importantes: Backend no disponible.", level="warning")
            update_menu(icon) # Update the menu to reflect the new mode
        else:
            log_event(f"❌ Error al cambiar modo: {response.text}", level="error", notify_user=True)
    except requests.exceptions.ConnectionError as e:
        log_event(f"❌ Error de conexión al cambiar modo: Backend no disponible. {e}", level="error", notify_user=True)
    except Exception as e:
        log_event(f"❌ Error inesperado al cambiar modo: {e}", level="error", notify_user=True)

# --- New Test/Toggle Functions ---
def send_test_notification(icon, item):
    log_event("Esta es una notificación de prueba enviada desde el ícono de la bandeja.", notify_user=True)

def toggle_monitoring_state(icon, item):
    global is_monitoring_active
    is_monitoring_active = not is_monitoring_active
    icon.icon = ICON_RED if is_monitoring_active else ICON_BLUE
    status_message = f"Monitoreo {'ACTIVADO' if is_monitoring_active else 'DESACTIVADO'}"
    log_event(status_message, notify_user=True)
    update_menu(icon) # Update menu to reflect checked state

# --- Menu Definition ---
def update_menu(icon):
    current_mode = get_current_mode()
    icon.menu = Menu(
        MenuItem("Abrir Dashboard", open_dashboard),
        MenuItem("Modos", Menu(
            MenuItem("Diario" + (" ✅" if current_mode == "diario" else ""), lambda i, s: set_modo(icon, i, "diario")),
            MenuItem("Editor" + (" ✅" if current_mode == "editor" else ""), lambda i, s: set_modo(icon, i, "editor")),
            MenuItem("Videojuego" + (" ✅" if current_mode == "videojuego" else ""), lambda i, s: set_modo(icon, i, "videojuego")),
            MenuItem("Streaming" + (" ✅" if current_mode == "streaming" else ""), lambda i, s: set_modo(icon, i, "streaming")),
            MenuItem("Multimedia" + (" ✅" if current_mode == "multimedia" else ""), lambda i, s: set_modo(icon, i, "multimedia")),
        )),
        Menu.SEPARATOR,
        MenuItem("Monitoreo Activo", toggle_monitoring_state, checked=lambda item: is_monitoring_active),
        MenuItem("Enviar Notificación de Prueba", send_test_notification),
        Menu.SEPARATOR,
        MenuItem("Reiniciar Backend", restart_backend),
        MenuItem("Salir", quit_tray),
    )

# --- Icon Setup ---
# This function will be called by icon.run_detached(setup=...)
def setup_icon(icon):
    icon.icon = ICON_BLUE # Initial icon state
    update_menu(icon)
    log_event("✅ Tray iniciado y menú actualizado.")

# --- Click handling for the icon itself (left-click) ---
def on_icon_click(icon, item):
    # pystray's click handler for the icon itself receives icon and item (which is None for left-click on icon)
    # We want left-click on the icon to open the dashboard
    open_dashboard(icon, item) # Pass icon and item as expected by open_dashboard

# --- Main execution ---
icon = Icon("BackendBot", ICON_BLUE, "BackendBot") # Global icon instance

def run_tray_icon():
    # The Icon object is created globally, so we just need to run it.
    # pystray's run_detached takes a setup function and a click handler for the icon itself.
    icon.run_detached(setup=setup_icon, click=on_icon_click)

if __name__ == "__main__":
    run_tray_icon()