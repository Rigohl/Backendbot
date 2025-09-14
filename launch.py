import subprocess
import sys
import os
import signal
import time

processes = []

def start_process(name, cmd):
    print(f"Iniciando {name}...")
    # For Windows, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP is used
    # For Unix-like, preexec_fn=os.setsid is used
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
    
    process = subprocess.Popen(cmd, creationflags=creationflags)
    processes.append(process)
    return process

def shutdown_processes():
    print("Deteniendo todos los procesos...")
    for p in processes:
        if p.poll() is None: # If process is still running
            try:
                if sys.platform == "win32":
                    # Terminate process group on Windows
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], check=True, capture_output=True)
                else:
                    # Send SIGTERM to the process group on Unix-like
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                p.wait(timeout=5) # Wait for process to terminate
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print(f"Proceso {p.pid} no respondió a SIGTERM, enviando SIGKILL...")
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/PID", str(p.pid)], check=True, capture_output=True)
                else:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                p.wait(timeout=5)
            except Exception as e:
                print(f"Error al detener proceso {p.pid}: {e}")
    print("Todos los procesos detenidos.")

if __name__ == "__main__":
    # Ensure current directory is in PYTHONPATH for module imports
    project_root = os.path.abspath(os.path.dirname(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        # Start the Guardian Bot first, as it will manage other bots
        guardian_cmd = [sys.executable, "src/backendbot/bots/bot_guardian.py"]
        start_process("Bot Guardián", guardian_cmd)
        time.sleep(2) # Give guardian a moment to start its bots

        # Start the FastAPI Orchestrator
        orchestrator_cmd = [sys.executable, "-m", "uvicorn", "src.backendbot.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        start_process("Orquestador FastAPI", orchestrator_cmd)

        print("BackendBot Hive iniciado. Presiona Ctrl+C para detener.")
        
        # Keep the main script alive until Ctrl+C
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Ctrl+C detectado.")
    finally:
        shutdown_processes()
