import sys, os, time, threading, subprocess, psutil, webbrowser, json, datetime, requests
from pystray import Icon, MenuItem, Menu, SubMenu
from PIL import Image, ImageDraw

FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BACKEND = os.path.join(FOLDER, "src", "backendbot", "backend.py")
LOGFILE = os.path.join(FOLDER, "logs", "tray.log")
SETTINGS_FILE = os.path.join(FOLDER, "tray_settings.json")

def log(msg):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            log("⚠️ No pude leer settings.json, restaurando defaults")
    return {
        "modo": "diario",
        "procesos_a_cerrar": {
            "videojuego": ["Discord.exe", "Steam.exe", "RiotClientServices.exe", "chrome.exe", "firefox.exe", "msedge.exe", "spotify.exe", "vlc.exe"],
            "editor": ["chrome.exe", "firefox.exe", "msedge.exe", "discord.exe", "steam.exe"],
            "diario": ["Code.exe", "Code - Insiders.exe", "electron.exe", "github.exe", "copilot.exe", "cmd.exe", "powershell.exe"]
        }
    }

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f)

settings = load_settings()

def create_image():
    img = Image.new('RGBA', (64, 64), (255, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((16, 16, 48, 48), fill=(255, 0, 0))
    return img

def open_dashboard():
    webbrowser.open("file://" + os.path.join(FOLDER, "dashboard", "index.html"))
    log("🖥 Dashboard abierto desde bandeja")

def toggle_modo_juego(icon, item):
    settings["modo_juego"] = not settings["modo_juego"]
    save_settings(settings)
    state = "ON" if settings["modo_juego"] else "OFF"
    log(f"🎮 Modo Juego -> {state}")

def restart_backend(icon, item):
    log("♻️ Reiniciando backend por acción de usuario")
    subprocess.run([os.path.join(FOLDER, "restart_backend.bat")])

def quit_tray(icon, item):
    log("⛔ Tray cerrado manualmente por usuario")
    icon.stop()

def watchdog():
    while True:
        try:
            running = any("backend.py" in " ".join(p.cmdline()) for p in psutil.process_iter(['cmdline']))
            if not running:
                log("🚨 Backend no detectado → reiniciando")
                subprocess.Popen(["pythonw.exe", BACKEND], cwd=FOLDER)
        except Exception as e:
            log(f"❌ Error en watchdog: {e}")
        time.sleep(10)

def set_modo(icon, item, modo):
    try:
        response = requests.post(f"http://127.0.0.1:8000/set-modo/{modo}")
        if response.status_code == 200:
            settings["modo"] = modo
            save_settings(settings)
            log(f"🔄 Modo cambiado a {modo}")
            # Restaurar procesos importantes si es necesario
            requests.post("http://127.0.0.1:8000/restore-important")
        else:
            log(f"❌ Error al cambiar modo: {response.text}")
    except Exception as e:
        log(f"❌ Error al conectar al backend: {e}")

menu = Menu(
    SubMenu("Modos", [
        MenuItem("Diario" + (" ✅" if settings.get("modo") == "diario" else ""), lambda icon, item: set_modo(icon, item, "diario")),
        MenuItem("Editor" + (" ✅" if settings.get("modo") == "editor" else ""), lambda icon, item: set_modo(icon, item, "editor")),
        MenuItem("Videojuego" + (" ✅" if settings.get("modo") == "videojuego" else ""), lambda icon, item: set_modo(icon, item, "videojuego"))
    ]),
    MenuItem("Abrir Dashboard", lambda icon, item: open_dashboard()),
    MenuItem("Reiniciar Backend", restart_backend),
    MenuItem("Salir", quit_tray)
)

icon = Icon("BackendBot", create_image(), "BackendBot", menu)

# Click izquierdo -> abrir dashboard
def on_click(icon, event, button, pressed):
    if pressed and button == 1:
        open_dashboard()

log("✅ Tray iniciado")
threading.Thread(target=watchdog, daemon=True).start()
icon.run_detached()
icon._listener.click = on_click
