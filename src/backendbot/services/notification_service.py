import os
import subprocess

def notify(title: str, message: str, duration: int = 5) -> None:
    """Muestra una notificación al usuario.
    Compatible con Windows, Linux y macOS.
    """
    try:
        if os.name == "nt":  # Windows
            from win10toast import ToastNotifier

            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=duration)
        elif os.name == "posix":  # Linux/macOS
            # Usar notify-send en Linux
            subprocess.run(["notify-send", title, message], check=False)
        else:
            # Fallback: imprimir en consola
            print(f"NOTIFICATION: {title} - {message}")
    except ImportError:
        # Fallback si no hay librerías disponibles
        print(f"NOTIFICATION: {title} - {message}")
    except Exception as e:
        print(f"Error mostrando notificación: {e}")
        print(f"NOTIFICATION: {title} - {message}")
