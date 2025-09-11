import sys
import threading
from PIL import Image, ImageDraw
from pystray import Icon

# Crear un icono circular rojo
ICON_SIZE = 64
image = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
draw.ellipse((8, 8, ICON_SIZE-8, ICON_SIZE-8), fill=(255, 0, 0, 255))

def on_quit(icon, item):
    icon.stop()

def run_tray_icon():
    icon = Icon('BackendBot', image, 'BackendBot activo', menu=None)
    icon.run()

if __name__ == '__main__':
    # Ejecutar el icono en un hilo para no bloquear
    t = threading.Thread(target=run_tray_icon, daemon=True)
    t.start()
    # Mantener el proceso vivo
    try:
        while t.is_alive():
            t.join(1)
    except KeyboardInterrupt:
        sys.exit(0)
