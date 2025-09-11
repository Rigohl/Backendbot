# Script de Control de BackendBot
# Interfaz para controlar el backend con autenticación

import os
import sys
import getpass
from pathlib import Path

# Agregar directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from services.backendbot_auth import backend_control

def print_menu():
    """Imprime el menú principal."""
    print("\n" + "="*50)
    print("🎯 BackendBot Control Panel")
    print("="*50)
    print("1. Ver estado del backend")
    print("2. Detener backend (Solo Admin)")
    print("3. Reiniciar backend (Solo Admin)")
    print("4. Cambiar contraseña")
    print("5. Agregar usuario (Solo Admin)")
    print("6. Salir")
    print("="*50)

def get_credentials():
    """Obtiene credenciales del usuario."""
    username = input("Usuario: ").strip()
    password = getpass.getpass("Contraseña: ")
    return username, password

def main():
    """Función principal."""
    print("🔐 BackendBot Control System")
    print("Solo usuarios autorizados pueden controlar el backend.")

    while True:
        print_menu()
        try:
            choice = input("Selecciona una opción (1-6): ").strip()

            if choice == "1":
                # Ver estado
                username, password = get_credentials()
                result = backend_control.authenticate_command(username, password, "status")
                if result["success"]:
                    print(f"✅ Estado: {result['status']}")
                else:
                    print(f"❌ Error: {result['message']}")

            elif choice == "2":
                # Detener backend
                print("⚠️  ATENCIÓN: Esto detendrá el backend permanentemente.")
                confirm = input("¿Estás seguro? (escribe 'CONFIRMAR'): ").strip()
                if confirm == "CONFIRMAR":
                    username, password = get_credentials()
                    result = backend_control.authenticate_command(username, password, "stop")
                    if result["success"]:
                        print("✅ Backend detenido correctamente.")
                    else:
                        print(f"❌ Error: {result['message']}")
                else:
                    print("Operación cancelada.")

            elif choice == "3":
                # Reiniciar backend
                username, password = get_credentials()
                result = backend_control.authenticate_command(username, password, "restart")
                if result["success"]:
                    print("✅ Backend reiniciado correctamente.")
                else:
                    print(f"❌ Error: {result['message']}")

            elif choice == "4":
                # Cambiar contraseña
                username, password = get_credentials()
                new_password = getpass.getpass("Nueva contraseña: ")
                confirm_password = getpass.getpass("Confirmar nueva contraseña: ")

                if new_password != confirm_password:
                    print("❌ Las contraseñas no coinciden.")
                    continue

                from services.backendbot_auth import BackendBotAuth
                auth = BackendBotAuth()
                if auth.change_password(username, password, new_password):
                    print("✅ Contraseña cambiada correctamente.")
                else:
                    print("❌ Error cambiando contraseña.")

            elif choice == "5":
                # Agregar usuario
                admin_username, admin_password = get_credentials()

                from services.backendbot_auth import BackendBotAuth
                auth = BackendBotAuth()
                admin_user = auth.authenticate(admin_username, admin_password)

                if not auth.is_admin(admin_user):
                    print("❌ Solo administradores pueden agregar usuarios.")
                    continue

                new_username = input("Nuevo usuario: ").strip()
                new_password = getpass.getpass("Contraseña para nuevo usuario: ")
                role = input("Rol (admin/user) [user]: ").strip().lower() or "user"

                if auth.add_user(admin_user, new_username, new_password, role):
                    print(f"✅ Usuario '{new_username}' agregado correctamente.")
                else:
                    print("❌ Error agregando usuario.")

            elif choice == "6":
                print("👋 Hasta luego!")
                break

            else:
                print("❌ Opción inválida.")

        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()