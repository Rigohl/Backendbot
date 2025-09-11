# Script de Instalación del Servicio BackendBot
# Instala el servicio de Windows para auto-inicio

import os
import sys
import subprocess
import win32serviceutil
import win32service
from pathlib import Path

def install_service():
    """Instala el servicio de BackendBot."""
    print("Instalando servicio BackendBot...")

    try:
        # Ruta del script del servicio
        service_script = Path(__file__).parent / "backendbot_service.py"

        # Instalar servicio
        subprocess.run([
            sys.executable, service_script,
            "--startup", "auto",
            "install"
        ], check=True)

        print("✅ Servicio instalado correctamente")

        # Iniciar servicio
        subprocess.run([
            sys.executable, service_script,
            "start"
        ], check=True)

        print("✅ Servicio iniciado correctamente")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando servicio: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

    return True

def uninstall_service():
    """Desinstala el servicio de BackendBot."""
    print("Desinstalando servicio BackendBot...")

    try:
        # Ruta del script del servicio
        service_script = Path(__file__).parent / "backendbot_service.py"

        # Detener y desinstalar servicio
        subprocess.run([
            sys.executable, service_script,
            "stop"
        ], check=True)

        subprocess.run([
            sys.executable, service_script,
            "remove"
        ], check=True)

        print("✅ Servicio desinstalado correctamente")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error desinstalando servicio: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

    return True

def create_startup_script():
    """Crea script de inicio automático."""
    startup_dir = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup_dir.mkdir(parents=True, exist_ok=True)

    monitor_script = Path(__file__).parent / "backendbot_monitor.py"
    startup_script = startup_dir / "BackendBotMonitor.bat"

    with open(startup_script, 'w') as f:
        f.write(f'@echo off\n')
        f.write(f'python "{monitor_script}"\n')

    print(f"✅ Script de inicio creado: {startup_script}")

def create_desktop_shortcuts():
    """Crea accesos directos en el escritorio."""
    desktop_dir = Path(os.environ.get('USERPROFILE', '')) / "Desktop"

    # Script de control
    control_script = Path(__file__).parent / "backendbot_control.py"
    control_shortcut = desktop_dir / "BackendBot Control.lnk"

    # Crear acceso directo usando PowerShell
    ps_script = f'''
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{control_shortcut}")
    $Shortcut.TargetPath = "python.exe"
    $Shortcut.Arguments = '"{control_script}"'
    $Shortcut.WorkingDirectory = "{Path(__file__).parent}"
    $Shortcut.IconLocation = "python.exe,0"
    $Shortcut.Description = "Control de BackendBot"
    $Shortcut.Save()
    '''

    subprocess.run(["powershell", "-Command", ps_script], check=True)
    print(f"✅ Acceso directo creado: {control_shortcut}")

def main():
    """Función principal."""
    if len(sys.argv) < 2:
        print("Uso: python install_service.py [install|uninstall|startup]")
        return

    command = sys.argv[1].lower()

    if command == "install":
        if install_service():
            create_startup_script()
            create_desktop_shortcuts()
            print("\n🎉 BackendBot instalado correctamente!")
            print("El backend ahora se mantendrá siempre activo.")
            print("Solo tú puedes detenerlo usando las credenciales de administrador.")

    elif command == "uninstall":
        if uninstall_service():
            print("\n✅ BackendBot desinstalado correctamente.")

    elif command == "startup":
        create_startup_script()
        print("✅ Script de inicio creado.")

    else:
        print("Comando desconocido. Use: install, uninstall, o startup")

if __name__ == "__main__":
    main()