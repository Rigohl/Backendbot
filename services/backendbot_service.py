# BackendBot Auto-Start Service
# Servicio de Windows para mantener BackendBot siempre activo

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import os
import subprocess
import logging
from pathlib import Path

class BackendBotService(win32serviceutil.ServiceFramework):
    _svc_name_ = "BackendBotService"
    _svc_display_name_ = "BackendBot Auto-Start Service"
    _svc_description_ = "Mantiene BackendBot siempre activo y lo reinicia automáticamente"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True

        # Configurar logging
        self.setup_logging()

        # Configurar rutas
        self.backend_dir = Path(__file__).parent.parent
        self.python_exe = self.find_python_exe()
        self.backend_script = self.backend_dir / "main.py"

    def setup_logging(self):
        """Configura el sistema de logging para el servicio."""
        log_file = Path(os.environ.get('PROGRAMDATA', 'C:\\ProgramData')) / "BackendBot" / "service.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def find_python_exe(self):
        """Encuentra el ejecutable de Python."""
        # Buscar en rutas comunes
        possible_paths = [
            r"C:\Python312\python.exe",
            r"C:\Python311\python.exe",
            r"C:\Python310\python.exe",
            r"C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe",
            r"C:\Users\DELL\AppData\Local\Programs\Python\Python311\python.exe",
        ]

        for path in possible_paths:
            if Path(path).exists():
                return path

        # Buscar en PATH
        try:
            result = subprocess.run(['where', 'python'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass

        return "python"  # Usar python del PATH como fallback

    def SvcStop(self):
        """Detiene el servicio."""
        self.logger.info("Deteniendo servicio BackendBot...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    def SvcDoRun(self):
        """Ejecuta el servicio principal."""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            (self._svc_name_, " - Servicio iniciado")
        )

        self.logger.info("Servicio BackendBot iniciado")
        self.main()

    def main(self):
        """Bucle principal del servicio."""
        backend_process = None

        while self.is_alive:
            try:
                # Verificar si el backend está ejecutándose
                if not self.is_backend_running():
                    self.logger.info("Backend no está ejecutándose, iniciando...")
                    backend_process = self.start_backend()
                else:
                    self.logger.debug("Backend ejecutándose correctamente")

                # Verificar cada 30 segundos
                win32event.WaitForSingleObject(self.hWaitStop, 30000)

            except Exception as e:
                self.logger.error(f"Error en bucle principal: {e}")
                time.sleep(5)

        # Limpiar proceso al salir
        if backend_process:
            try:
                backend_process.terminate()
                backend_process.wait(timeout=10)
            except:
                backend_process.kill()

    def is_backend_running(self):
        """Verifica si el backend está ejecutándose."""
        try:
            # Verificar puerto 8000
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            return result == 0
        except:
            return False

    def start_backend(self):
        """Inicia el backend."""
        try:
            self.logger.info(f"Iniciando backend con: {self.python_exe} {self.backend_script}")

            # Cambiar al directorio del backend
            os.chdir(self.backend_dir)

            # Iniciar proceso
            process = subprocess.Popen(
                [self.python_exe, str(self.backend_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            self.logger.info(f"Backend iniciado con PID: {process.pid}")
            return process

        except Exception as e:
            self.logger.error(f"Error iniciando backend: {e}")
            return None

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BackendBotService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(BackendBotService)