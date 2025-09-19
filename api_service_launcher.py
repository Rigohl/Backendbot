#!/usr/bin/env python3
"""
BackendBot API Service Launcher - Ejecución Invisible
=====================================================

Script para ejecutar la API de BackendBot como un servicio invisible
en segundo plano, completamente oculto del usuario.

Características:
- Sin ventana de consola visible
- Sin icono en la barra de tareas
- Sin output visible
- Solo accesible desde localhost
- Puerto no estándar para mayor seguridad

Uso:
    python api_service_launcher.py start    # Iniciar servicio
    python api_service_launcher.py stop     # Detener servicio
    python api_service_launcher.py status   # Ver estado

Autor: BackendBot Team
Versión: 0.1.0
"""

import argparse
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Archivo PID para controlar el proceso
PID_FILE = root_dir / "backendbot_api.pid"


def is_process_running(pid):
    """Verifica si un proceso está ejecutándose."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_running_pid():
    """Obtiene el PID del proceso en ejecución desde el archivo PID."""
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
                if is_process_running(pid):
                    return pid
                else:
                    # Proceso ya no existe, limpiar archivo
                    PID_FILE.unlink()
        except (ValueError, OSError):
            pass
    return None


def start_service():
    """Inicia el servicio API de manera invisible."""
    # Verificar si ya está ejecutándose
    running_pid = get_running_pid()
    if running_pid:
        print(f"⚠️  El servicio ya está ejecutándose (PID: {running_pid})")
        return False

    try:
        # Comando para ejecutar el servidor API
        python_exe = sys.executable
        api_server_script = root_dir / "api_server.py"

        # En Windows, usar CREATE_NO_WINDOW para ocultar completamente
        if os.name == 'nt':
            # Usar subprocess con flags para ventana oculta
            creationflags = subprocess.CREATE_NO_WINDOW
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                [python_exe, str(api_server_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=creationflags,
                startupinfo=startupinfo,
                cwd=str(root_dir)
            )
        else:
            # Para Unix/Linux, usar nohup y redirección
            process = subprocess.Popen(
                [python_exe, str(api_server_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                preexec_fn=os.setsid,  # Crear nuevo grupo de procesos
                cwd=str(root_dir)
            )

        # Guardar el PID
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))

        # Verificar que el proceso se inició correctamente
        time.sleep(2)  # Esperar un poco para que se inicie
        if is_process_running(process.pid):
            print("✅ Servicio BackendBot API iniciado correctamente")
            print("🌐 Solo accesible desde localhost (127.0.0.1:48732)")
            print("� Modo invisible: Sin ventana visible")
            print("📖 Documentación: http://127.0.0.1:48732/docs")
            print("� Health Check: http://127.0.0.1:48732/api/v1/health")
            return True
        else:
            print("❌ Error: El proceso se detuvo inmediatamente")
            if PID_FILE.exists():
                PID_FILE.unlink()
            return False

    except Exception as e:
        print(f"❌ Error al iniciar el servicio: {e}")
        if PID_FILE.exists():
            PID_FILE.unlink()
        return False


def stop_service():
    """Detiene el servicio API."""
    running_pid = get_running_pid()
    if not running_pid:
        print("ℹ️  El servicio no está ejecutándose")
        return False

    try:
        if os.name == 'nt':
            # En Windows, terminar el proceso
            os.kill(running_pid, signal.SIGTERM)
        else:
            # En Unix/Linux, terminar el grupo de procesos
            os.killpg(os.getpgid(running_pid), signal.SIGTERM)

        # Esperar a que termine
        time.sleep(2)

        # Verificar si realmente terminó
        if not is_process_running(running_pid):
            PID_FILE.unlink()
            print("✅ Servicio BackendBot API detenido correctamente")
            return True
        else:
            print("⚠️  El servicio no respondió a la señal de terminación")
            print("Intentando forzar terminación...")
            try:
                if os.name == 'nt':
                    os.kill(running_pid, signal.SIGKILL)
                else:
                    os.killpg(os.getpgid(running_pid), signal.SIGKILL)
                time.sleep(1)
                if not is_process_running(running_pid):
                    PID_FILE.unlink()
                    print("✅ Servicio forzado a detener")
                    return True
            except:
                pass
            print("❌ No se pudo detener el servicio")
            return False

    except Exception as e:
        print(f"❌ Error al detener el servicio: {e}")
        return False


def status_service():
    """Muestra el estado del servicio."""
    running_pid = get_running_pid()
    if running_pid:
        print(f"✅ Servicio BackendBot API ejecutándose (PID: {running_pid})")
        print("🌐 Accesible en: http://127.0.0.1:48732")
        print("📖 Documentación: http://127.0.0.1:48732/docs")
        return True
    else:
        print("❌ Servicio BackendBot API no está ejecutándose")
        return False


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="BackendBot API Service Launcher")
    parser.add_argument(
        "action",
        choices=["start", "stop", "status"],
        help="Acción a realizar"
    )

    args = parser.parse_args()

    if args.action == "start":
        success = start_service()
        sys.exit(0 if success else 1)
    elif args.action == "stop":
        success = stop_service()
        sys.exit(0 if success else 1)
    elif args.action == "status":
        success = status_service()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()