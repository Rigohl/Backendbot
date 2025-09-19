"""
Ejemplo de detección de dependencias circulares
Demuestra cómo el sistema DI moderno detecta y previene dependencias circulares
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent))

from demo_modern_di import DIContainerWrapper
from backendbot.core.di.enhanced_container import ModernDependencyInjectionContainer


def demonstrate_circular_dependency_detection():
    """Demostrar detección de dependencias circulares"""

    print("🔄 Demonstrating Circular Dependency Detection")
    print("=" * 50)

    # Crear contenedor
    di_container = DIContainerWrapper(ModernDependencyInjectionContainer())

    print("\n📋 Creando servicios con dependencia circular:")

    # Definir servicios que tienen dependencia circular
    class ServiceA:
        def __init__(self, service_b):
            self.service_b = service_b
            print("🔗 ServiceA inicializado con ServiceB")

    class ServiceB:
        def __init__(self, service_a):
            self.service_a = service_a
            print("🔗 ServiceB inicializado con ServiceA")

    # Registrar servicios con dependencia circular usando factories
    print("⚠️  Registrando ServiceA (depende de ServiceB)...")
    di_container.register_transient(ServiceA, lambda: ServiceA(di_container.resolve(ServiceB)))

    print("⚠️  Registrando ServiceB (depende de ServiceA)...")
    di_container.register_transient(ServiceB, lambda: ServiceB(di_container.resolve(ServiceA)))

    print("\n🔍 Intentando detectar dependencias circulares...")

    try:
        di_container.detect_circular_dependencies()
        print("✅ No se detectaron dependencias circulares (inesperado)")
    except ValueError as e:
        print(f"❌ Dependencia circular detectada correctamente: {e}")

    print("\n📋 Grafo de dependencias actual:")
    graph = di_container.get_dependency_graph()
    print(graph)

    print("\n📋 Intentando resolver ServiceA (esto fallará)...")

    try:
        service_a = di_container.resolve(ServiceA)
        print("✅ ServiceA resuelto (inesperado)")
    except RecursionError as e:
        print(f"❌ RecursionError esperado: {str(e)[:100]}...")
    except ValueError as e:
        print(f"❌ ValueError: {e}")

    print("\n🧹 Limpiando servicios...")
    di_container.clear_services()

    print("\n📋 Creando servicios sin dependencia circular:")

    # Ahora crear servicios sin dependencia circular
    class IndependentServiceA:
        def __init__(self):
            self.name = "ServiceA"
            print("🔗 IndependentServiceA inicializado")

    class IndependentServiceB:
        def __init__(self, service_a: IndependentServiceA):
            self.service_a = service_a
            self.name = "ServiceB"
            print("🔗 IndependentServiceB inicializado con ServiceA")

    # Registrar correctamente
    di_container.register_transient(IndependentServiceA)
    di_container.register_transient(IndependentServiceB)

    print("\n🔍 Verificando dependencias sin circularidad...")

    try:
        di_container.detect_circular_dependencies()
        print("✅ No se detectaron dependencias circulares")
    except ValueError as e:
        print(f"❌ Error inesperado: {e}")

    print("\n📋 Resolviendo servicios correctamente...")

    try:
        service_a = di_container.resolve(IndependentServiceA)
        service_b = di_container.resolve(IndependentServiceB)
        print("✅ Servicios resueltos correctamente")
        print(f"🔗 ServiceA: {service_a.name}")
        print(f"🔗 ServiceB: {service_b.name}, depende de: {service_b.service_a.name}")
    except Exception as e:
        print(f"❌ Error al resolver: {e}")

    print("\n📋 Grafo de dependencias final:")
    graph = di_container.get_dependency_graph()
    print(graph)

    print("\n🎉 Demo de detección de dependencias circulares completada!")


if __name__ == "__main__":
    demonstrate_circular_dependency_detection()