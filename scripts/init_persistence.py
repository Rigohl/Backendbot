#!/usr/bin/env python3
"""
Script de Inicialización del Sistema de Persistencia
BackendBot v2.0.0
"""

import sys
import os
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_paths():
    """Configura las rutas del proyecto"""
    # Obtener el directorio del script
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Añadir src al path
    src_path = project_root / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    return project_root

def init_persistence_system():
    """Inicializa el sistema completo de persistencia"""
    try:
        logger.info("🚀 Iniciando sistema de persistencia BackendBot...")

        # Importar módulos del sistema de persistencia
        from backendbot.utils.database_manager import (
            db_manager,
            config_manager,
            migration_manager,
            init_database
        )

        # Inicializar base de datos
        logger.info("📊 Inicializando base de datos...")
        init_database()

        # Verificar configuración
        logger.info("⚙️ Verificando configuración...")
        app_name = config_manager.get('app.name', 'BackendBot')
        version = config_manager.get('app.version', '2.0.0')
        logger.info(f"✅ Configuración cargada: {app_name} v{version}")

        # Ejecutar migraciones
        logger.info("🔄 Ejecutando migraciones...")
        migration_manager.run_migrations()

        # Verificar conexión
        logger.info("🔗 Verificando conexión a base de datos...")
        db_manager.connect()
        logger.info("✅ Conexión a base de datos exitosa")

        # Crear usuario por defecto si no existe
        logger.info("👤 Verificando usuario por defecto...")
        users = db_manager.execute_query("SELECT COUNT(*) as count FROM users")
        if users[0]['count'] == 0:
            db_manager.execute_update(
                "INSERT INTO users (username, preferences) VALUES (?, ?)",
                ('default', '{"theme": "system", "language": "es"}')
            )
            logger.info("✅ Usuario por defecto creado")

        # Cerrar conexiones
        db_manager.disconnect()

        logger.info("🎉 Sistema de persistencia inicializado correctamente!")
        return True

    except Exception as e:
        logger.error(f"❌ Error inicializando sistema de persistencia: {e}")
        return False

def create_env_file():
    """Crea archivo .env si no existe"""
    project_root = setup_paths()
    env_path = project_root / '.env'

    if not env_path.exists():
        logger.info("📝 Creando archivo .env...")

        env_content = """# Configuración de Entorno - BackendBot
# Variables de entorno sensibles

# Base de datos
DATABASE_URL=sqlite:///data/backendbot.db

# Aplicación
APP_ENV=development
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/backendbot.log

# Opcional: Configuración de email para notificaciones
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password

# Opcional: Configuración de webhook
# WEBHOOK_URL=https://your-webhook-url.com
# WEBHOOK_SECRET=your-webhook-secret
"""

        env_path.write_text(env_content, encoding='utf-8')
        logger.info("✅ Archivo .env creado")

def main():
    """Función principal"""
    print("🔧 BackendBot - Inicialización del Sistema de Persistencia")
    print("=" * 60)

    # Configurar rutas
    project_root = setup_paths()
    logger.info(f"📁 Directorio del proyecto: {project_root}")

    # Crear archivo .env
    create_env_file()

    # Inicializar sistema de persistencia
    success = init_persistence_system()

    if success:
        print("\n✅ Inicialización completada exitosamente!")
        print("\n📋 Resumen:")
        print("  • Base de datos SQLite creada")
        print("  • Tablas principales inicializadas")
        print("  • Migraciones ejecutadas")
        print("  • Configuración por defecto cargada")
        print("  • Usuario por defecto creado")
        print("\n🚀 BackendBot está listo para usar!")
    else:
        print("\n❌ Error en la inicialización")
        print("Revisa los logs para más detalles")
        sys.exit(1)

if __name__ == "__main__":
    main()