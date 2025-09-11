# Sistema de Autenticación para Control de BackendBot
# Solo permite que usuarios autorizados controlen el backend

import hashlib
import json
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta

class BackendBotAuth:
    """Sistema de autenticación para control del backend."""

    def __init__(self):
        self.backend_dir = Path(__file__).parent.parent
        self.auth_file = self.backend_dir / "config" / "auth.json"
        self.auth_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Usuario administrador por defecto
        self.default_admin = {
            "username": "admin",
            "password_hash": self.hash_password("backendbot2025"),
            "role": "admin",
            "created": datetime.now().isoformat(),
            "last_login": None
        }

        self.load_auth_data()

    def hash_password(self, password):
        """Hashea la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()

    def load_auth_data(self):
        """Carga datos de autenticación."""
        if self.auth_file.exists():
            try:
                with open(self.auth_file, 'r') as f:
                    self.auth_data = json.load(f)
            except Exception as e:
                self.logger.error(f"Error cargando auth data: {e}")
                self.auth_data = {"users": [self.default_admin]}
        else:
            self.auth_data = {"users": [self.default_admin]}
            self.save_auth_data()

    def save_auth_data(self):
        """Guarda datos de autenticación."""
        try:
            with open(self.auth_file, 'w') as f:
                json.dump(self.auth_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando auth data: {e}")

    def authenticate(self, username, password):
        """Autentica un usuario."""
        for user in self.auth_data["users"]:
            if user["username"] == username and user["password_hash"] == self.hash_password(password):
                user["last_login"] = datetime.now().isoformat()
                self.save_auth_data()
                return user
        return None

    def is_admin(self, user):
        """Verifica si un usuario es administrador."""
        return user and user.get("role") == "admin"

    def change_password(self, username, old_password, new_password):
        """Cambia la contraseña de un usuario."""
        user = self.authenticate(username, old_password)
        if user:
            user["password_hash"] = self.hash_password(new_password)
            self.save_auth_data()
            return True
        return False

    def add_user(self, admin_user, new_username, new_password, role="user"):
        """Agrega un nuevo usuario (solo admin)."""
        if not self.is_admin(admin_user):
            return False

        # Verificar que no exista
        for user in self.auth_data["users"]:
            if user["username"] == new_username:
                return False

        new_user = {
            "username": new_username,
            "password_hash": self.hash_password(new_password),
            "role": role,
            "created": datetime.now().isoformat(),
            "last_login": None
        }

        self.auth_data["users"].append(new_user)
        self.save_auth_data()
        return True

class BackendBotControl:
    """Control del backend con autenticación."""

    def __init__(self):
        self.auth = BackendBotAuth()
        self.logger = logging.getLogger(__name__)

    def authenticate_command(self, username, password, command):
        """Autentica y ejecuta un comando."""
        user = self.auth.authenticate(username, password)

        if not user:
            self.logger.warning(f"Autenticación fallida para usuario: {username}")
            return {"success": False, "message": "Credenciales inválidas"}

        # Solo admin puede detener el backend
        if command in ["stop", "restart", "kill"] and not self.auth.is_admin(user):
            self.logger.warning(f"Usuario no autorizado intentó comando: {username} - {command}")
            return {"success": False, "message": "No autorizado para este comando"}

        # Ejecutar comando
        return self.execute_command(command, user)

    def execute_command(self, command, user):
        """Ejecuta un comando autorizado."""
        try:
            if command == "status":
                # Verificar estado del backend
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', 8000))
                sock.close()
                status = "running" if result == 0 else "stopped"
                return {"success": True, "status": status}

            elif command == "stop":
                # Detener backend
                import subprocess
                import os
                backend_dir = Path(__file__).parent.parent
                os.chdir(backend_dir)

                # Encontrar proceso de Python ejecutando main.py
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], capture_output=True, text=True)
                if "python.exe" in result.stdout:
                    # Matar procesos python (esto es simplificado, en producción usar PID específico)
                    subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
                    self.logger.info(f"Backend detenido por usuario: {user['username']}")
                    return {"success": True, "message": "Backend detenido"}

            elif command == "restart":
                # Reiniciar backend
                self.execute_command("stop", user)
                time.sleep(2)
                # El monitor debería reiniciarlo automáticamente
                return {"success": True, "message": "Backend reiniciado"}

            else:
                return {"success": False, "message": "Comando desconocido"}

        except Exception as e:
            self.logger.error(f"Error ejecutando comando {command}: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

# Instancia global
backend_control = BackendBotControl()