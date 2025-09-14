#!/usr/bin/env python3
"""
Script de verificación completo para BackendBot en Railway
Uso: python verificar_railway.py <URL_DE_RAILWAY>
Ejemplo: python verificar_railway.py https://abc123.up.railway.app
"""

import requests
import json
import sys
from datetime import datetime

def test_endpoint(base_url, endpoint, description):
    """Prueba un endpoint específico"""
    try:
        url = f"{base_url.rstrip('/')}{endpoint}"
        print(f"\n📍 Probando: {description}")
        print(f"   URL: {url}")

        response = requests.get(url, timeout=15)
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   📊 Respuesta JSON:")
                print(f"   {json.dumps(data, indent=4)}")
                return True, data
            except json.JSONDecodeError:
                print(f"   📄 Respuesta HTML/Texto: {len(response.text)} caracteres")
                return True, response.text[:200]
        elif response.status_code == 404:
            print(f"   ⚠️  Endpoint no encontrado")
            return False, None
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   📝 Respuesta: {response.text[:100]}...")
            return False, None

    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout: El servidor no responde")
        return False, None
    except requests.exceptions.ConnectionError:
        print(f"   🔌 Error de conexión: No se puede conectar al servidor")
        return False, None
    except Exception as e:
        print(f"   💥 Error inesperado: {str(e)}")
        return False, None

def main():
    if len(sys.argv) != 2:
        print("❌ Uso incorrecto")
        print("Uso: python verificar_railway.py <URL_DE_RAILWAY>")
        print("Ejemplo: python verificar_railway.py https://abc123.up.railway.app")
        sys.exit(1)

    base_url = sys.argv[1]

    print("🔍 VERIFICACIÓN COMPLETA DEL BACKENDBOT EN RAILWAY")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL base: {base_url}")
    print("=" * 60)

    # Lista de endpoints a probar
    endpoints = [
        ("/health", "Health Check"),
        ("/", "API Root"),
        ("/docs", "Documentación API"),
        ("/redoc", "Documentación ReDoc"),
    ]

    results = []
    all_passed = True

    for endpoint, description in endpoints:
        success, data = test_endpoint(base_url, endpoint, description)
        results.append((endpoint, success, data))
        if not success:
            all_passed = False

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    print("=" * 60)

    for endpoint, success, data in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {endpoint}")

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ El BackendBot está funcionando correctamente en Railway")
    else:
        print("⚠️  Algunos tests fallaron")
        print("🔧 Revisa la configuración de Railway y los logs")

    print("\n💡 Próximos pasos:")
    print("   1. Verifica los logs en Railway dashboard")
    print("   2. Confirma que la base de datos esté conectada")
    print("   3. Revisa las variables de entorno")
    print("   4. Si hay errores, fuerza un redeploy")

if __name__ == "__main__":
    main()