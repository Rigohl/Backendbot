"""
Ejemplo de uso del sistema moderno de DI
Demuestra las mejores prácticas implementadas en BackendBot
"""

import sys
import os
from pathlib import Path
from typing import Any, Dict, List

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent))

from backendbot.core.di.enhanced_container import (
    ModernDependencyInjectionContainer,
    container,
    setup_wiring
)
from backendbot.core.services.logger_service import LoggerService
from backendbot.core.services.config_service import ConfigService
from backendbot.core.di.enhanced_container import ServiceDescriptor, ModernDependencyInjectionContainer
from typing import Dict, Any


class DIContainerWrapper:
    """Wrapper para el contenedor DI con métodos adicionales"""

    def __init__(self, container):
        self.container = container
        self._resources_initialized = False

    def register_service(self, service_type: type, implementation: type = None, lifetime: str = "transient"):
        return self.container.register_service(service_type, implementation, lifetime)

    def register_singleton(self, service_type: type, implementation: type = None):
        return self.container.register_service(service_type, implementation, "singleton")

    def register_transient(self, service_type: type, implementation: type = None):
        return self.container.register_service(service_type, implementation, "transient")

    def register_scoped(self, service_type: type, implementation: type = None):
        return self.container.register_service(service_type, implementation, "scoped")

    def resolve(self, service_type: type, scope_id: str = None):
        return self.container.resolve(service_type, scope_id)

    def get_service_descriptors(self):
        return self.container.get_service_descriptors()

    def has_service(self, service_type: type) -> bool:
        return self.container.has_service(service_type)

    def clear_services(self):
        return self.container.clear_services()

    def check_dependencies(self):
        return self.container.check_dependencies()

    def detect_circular_dependencies(self):
        return self.container.detect_circular_dependencies()

    def validate_all_services(self):
        return self.container.validate_all_services()

    def get_dependency_graph(self):
        return self.container.get_dependency_graph()

    def init_resources(self):
        if not self._resources_initialized:
            self._resources_initialized = True
            return self.container.init_resources()

    def shutdown_resources(self):
        if self._resources_initialized:
            self._resources_initialized = False
            return self.container.shutdown_resources()

    def __getattr__(self, name):
        # Delegar al container real para providers declarativos
        if hasattr(self.container, name):
            attr = getattr(self.container, name)
            # Si es un provider, llamarlo
            if hasattr(attr, '__call__') and hasattr(attr, 'provider_type'):
                return attr()
            return attr
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


def demonstrate_modern_di():
    """Demostrar el uso del sistema moderno de DI"""

    print("🚀 Demonstrating Modern Dependency Injection in BackendBot")
    print("=" * 60)

    # Crear instancia del contenedor moderno
    di_container = DIContainerWrapper(ModernDependencyInjectionContainer())
    # Acceder a la instancia real del container
    container_instance = di_container.container

    # Configurar el contenedor con valores de configuración
    container_instance.config.from_dict({
        'log_level': 'INFO',
        'log_file': 'demo_backendbot.log',
        'config_file': 'backendbot.yaml',
        'config_dir': 'config',
        'database': {
            'url': 'sqlite:///demo.db',
            'pool_size': 5
        },
        'ui': {
            'theme': 'dark'
        },
        'api_port': 8000
    })

    print("\n📋 1. Resolviendo servicios con inyección automática:")

    # Resolver servicios usando el contenedor
    logger = di_container.logger_service()
    config = di_container.config_service()

    print(f"✅ Logger service resolved: {type(logger).__name__}")
    print(f"✅ Config service resolved: {type(config).__name__}")

    print("\n📋 2. Registrando servicios personalizados:")

    # Registrar servicios personalizados
    class DatabaseService:
        def __init__(self, connection_string: str = "sqlite:///demo.db"):
            self.connection_string = connection_string

        def connect(self):
            print(f"📊 Conectando a base de datos: {self.connection_string}")
            return f"Connected to {self.connection_string}"

    class CacheService:
        def __init__(self, max_size: int = 100):
            self.max_size = max_size
            self.cache = {}

        def set(self, key: str, value: Any):
            if len(self.cache) >= self.max_size:
                # LRU eviction (simplified)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[key] = value
            print(f"💾 Cache set: {key} = {value}")

        def get(self, key: str) -> Any:
            return self.cache.get(key, None)

    # Registrar servicios con diferentes lifetimes
    di_container.register_singleton(DatabaseService)
    di_container.register_transient(CacheService)

    print("✅ DatabaseService registrado como Singleton")
    print("✅ CacheService registrado como Transient")

    print("\n📋 3. Demostrando diferentes lifetimes:")

    # Probar singleton
    db1 = di_container.resolve(DatabaseService)
    db2 = di_container.resolve(DatabaseService)
    print(f"🔄 Singleton test - Same instance: {db1 is db2}")

    # Probar transient
    cache1 = di_container.resolve(CacheService)
    cache2 = di_container.resolve(CacheService)
    print(f"🔄 Transient test - Different instances: {cache1 is not cache2}")

    print("\n📋 4. Usando servicios resueltos:")

    # Usar logger
    logger.info("Demo", "Modern DI System")
    logger.log_performance("demo_operation", 0.123)

    # Usar configuración
    db_url = config.get('database.url', 'default.db')
    print(f"⚙️ Database URL from config: {db_url}")

    # Usar servicios personalizados
    connection = db1.connect()
    cache1.set("demo_key", "demo_value")
    cached_value = cache1.get("demo_key")

    print(f"📊 Database connection: {connection}")
    print(f"💾 Cached value: {cached_value}")

    print("\n📋 5. Información del contenedor:")

    descriptors = di_container.get_service_descriptors()
    print(f"📊 Servicios registrados: {len(descriptors)}")

    for service_type, descriptor in descriptors.items():
        print(f"  - {service_type.__name__}: {descriptor.lifetime} lifetime")

    print("\n📋 6. Configuración avanzada:")

    # Demostrar configuración estructurada
    db_config = config.get_database_config()
    ui_config = config.get_ui_config()

    print(f"🗄️ Database pool size: {db_config.pool_size}")
    print(f"🎨 UI theme: {ui_config.theme}")
    print(f"🌐 API port: {config.get_api_config()['port']}")

    print("\n📋 7. Validación avanzada del contenedor:")

    try:
        di_container.check_dependencies()
        print("✅ Todas las dependencias están correctamente definidas")
    except ValueError as e:
        print(f"❌ Error en dependencias: {e}")

    try:
        di_container.detect_circular_dependencies()
        print("✅ No se detectaron dependencias circulares")
    except ValueError as e:
        print(f"❌ Dependencia circular encontrada: {e}")

    try:
        di_container.validate_all_services()
        print("✅ Todos los servicios son válidos")
    except ValueError as e:
        print(f"❌ Error de validación: {e}")

    print("\n📋 8. Grafo de dependencias:")
    graph = di_container.get_dependency_graph()
    print(graph)

    print("\n📋 9. Manejo de errores:")

    try:
        # Intentar resolver un servicio no registrado
        di_container.resolve(str)  # Esto debería fallar
    except ValueError as e:
        print(f"❌ Error esperado: {e}")

    print("\n📋 10. Limpieza de recursos:")

    # Limpiar servicios
    di_container.clear_services()
    print("🧹 Servicios limpiados")

    # Liberar recursos
    di_container.shutdown_resources()
    print("🔌 Recursos liberados")

    print("\n🎉 Demo completada exitosamente!")
    print("El sistema moderno de DI está funcionando correctamente.")


if __name__ == "__main__":
    demonstrate_modern_di()