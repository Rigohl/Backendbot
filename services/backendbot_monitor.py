# BackendBot Monitor - Monitoreo y reinicio automático
# Script que mantiene el backend siempre activo

import time
import subprocess
import logging
import os
import signal
import psutil
from pathlib import Path
import json

class BackendBotMonitor:
    """Monitor que mantiene BackendBot siempre activo."""

    def __init__(self):
        self.backend_dir = Path(__file__).parent.parent
        self.python_exe = self.find_python_exe()
        self.backend_script = self.backend_dir / "main.py"
        self.process = None
        self.restart_count = 0
        self.max_restarts = 10  # Máximo de reinicios por hora
        self.restart_window = 3600  # Ventana de 1 hora
        self.restart_times = []

        self.setup_logging()
        self.load_config()

    def setup_logging(self):
        """Configura el logging."""
        log_file = self.backend_dir / "logs" / "monitor.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """Carga configuración desde archivo."""
        config_file = self.backend_dir / "config" / "monitor_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.max_restarts = config.get('max_restarts', 10)
                    self.restart_window = config.get('restart_window', 3600)
            except Exception as e:
                self.logger.error(f"Error cargando configuración: {e}")

    def find_python_exe(self):
        """Encuentra el ejecutable de Python."""
        possible_paths = [
            r"C:\Python312\python.exe",
            r"C:\Python311\python.exe",
            r"C:\Python310\python.exe",
            r"C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe",
        ]

        for path in possible_paths:
            if Path(path).exists():
                return path

        return "python"

    def is_backend_running(self):
        """Verifica si el backend está ejecutándose."""
        try:
            # Verificar puerto 8000
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            return result == 0
        except:
            return False

    def start_backend(self):
        """Inicia el backend."""
        try:
            self.logger.info("Iniciando BackendBot...")

            # Cambiar al directorio del backend
            os.chdir(self.backend_dir)

            # Iniciar proceso
            self.process = subprocess.Popen(
                [self.python_exe, str(self.backend_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            self.logger.info(f"BackendBot iniciado con PID: {self.process.pid}")
            return True

        except Exception as e:
            self.logger.error(f"Error iniciando backend: {e}")
            return False

    def stop_backend(self, force=False):
        """Detiene el backend."""
        if self.process:
            try:
                if force:
                    self.process.kill()
                    self.logger.info("BackendBot detenido forzosamente")
                else:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=10)
                        self.logger.info("BackendBot detenido correctamente")
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.logger.warning("BackendBot forzado a detenerse")
            except Exception as e:
                self.logger.error(f"Error deteniendo backend: {e}")

    def can_restart(self):
        """Verifica si puede reiniciar basado en límites."""
        current_time = time.time()

        # Limpiar reinicios antiguos
        self.restart_times = [t for t in self.restart_times if current_time - t < self.restart_window]

        return len(self.restart_times) < self.max_restarts

    def record_restart(self):
        """Registra un reinicio."""
        self.restart_times.append(time.time())
        self.restart_count += 1

    def monitor_loop(self):
        """Bucle principal de monitoreo."""
        self.logger.info("Monitor de BackendBot iniciado")

        while True:
            try:
                if not self.is_backend_running():
                    if self.can_restart():
                        self.logger.warning("BackendBot no responde, reiniciando...")
                        self.record_restart()
                        self.start_backend()
                    else:
                        self.logger.error("Demasiados reinicios, esperando...")
                        time.sleep(300)  # Esperar 5 minutos
                        self.restart_times.clear()  # Resetear contador
                else:
                    self.logger.debug("BackendBot ejecutándose correctamente")

                time.sleep(30)  # Verificar cada 30 segundos

            except KeyboardInterrupt:
                self.logger.info("Monitor detenido por usuario")
                self.stop_backend()
                break
            except Exception as e:
                self.logger.error(f"Error en monitor: {e}")
                time.sleep(10)

    def shutdown_handler(self, signum, frame):
        """Manejador de señales para apagado graceful."""
        self.logger.info("Señal de apagado recibida")
        self.stop_backend()
        exit(0)

if __name__ == "__main__":
    monitor = BackendBotMonitor()

    # Configurar manejadores de señales
    if os.name != 'nt':  # Unix-like systems
        signal.signal(signal.SIGTERM, monitor.shutdown_handler)
        signal.signal(signal.SIGINT, monitor.shutdown_handler)

    monitor.monitor_loop()