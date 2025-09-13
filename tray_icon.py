import sys
import webbrowser
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

def create_image():
    # Icono simple azul
    image = Image.new('RGB', (64, 64), color=(59, 130, 246))
    draw = ImageDraw.Draw(image)
    draw.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
    draw.text((22, 22), "BB", fill=(59, 130, 246))
    return image

def open_dashboard():
    webbrowser.open('http://localhost:8000')

def quit_app(icon, item):
    icon.stop()
    sys.exit(0)

icon = Icon(
    "BackendBot",
    create_image(),
    "BackendBot",
    menu=Menu(
        MenuItem("Abrir Dashboard", lambda icon, item: open_dashboard()),
        MenuItem("Salir", quit_app)
    )
)

if __name__ == "__main__":
    icon.run()