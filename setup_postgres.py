#!/usr/bin/env python3
"""
Script para configurar PostgreSQL para BackendBot
"""
import psycopg2
import sys

def main():
    print("🚀 Configurando PostgreSQL para BackendBot...")
    print(f"Host: localhost")
    print(f"Puerto: 5432")
    print(f"Usuario: postgres")
    print(f"Contraseña: rigo007x10")
    print()

    try:
        # Conectar como postgres
        print("🔍 Conectando a PostgreSQL...")
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='rigo007x10',
            host='localhost',
            port='5432'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Conexión exitosa")

        # Crear base de datos
        print("🗄️ Creando base de datos backendbot_db...")
        cursor.execute("DROP DATABASE IF EXISTS backendbot_db")
        cursor.execute("CREATE DATABASE backendbot_db")
        print("✅ Base de datos creada")

        # Crear usuario
        print("👤 Creando usuario 'user'...")
        cursor.execute("DROP USER IF EXISTS \"user\"")
        cursor.execute("CREATE USER \"user\" WITH PASSWORD 'rigo007x10'")
        print("✅ Usuario creado")

        # Otorgar permisos
        print("🔑 Otorgando permisos...")
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE backendbot_db TO \"user\"")
        print("✅ Permisos otorgados")

        cursor.close()
        conn.close()

        # Probar conexión con nuevo usuario
        print("🧪 Probando conexión con usuario 'user'...")
        conn2 = psycopg2.connect(
            dbname='backendbot_db',
            user='user',
            password='rigo007x10',
            host='localhost',
            port='5432'
        )
        conn2.close()
        print("✅ Conexión de usuario exitosa")

        print()
        print("🎉 ¡Configuración completada exitosamente!")
        print("✅ BackendBot puede ahora conectarse a PostgreSQL local")
        print()
        print("📋 Configuración:")
        print("   Base de datos: backendbot_db")
        print("   Usuario: user")
        print("   Contraseña: rigo007x10")
        print("   Puerto: 5432")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()