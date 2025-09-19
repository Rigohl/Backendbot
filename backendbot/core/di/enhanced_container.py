"""
Contenedor de Inyección de Dependencias Moderno
Implementa mejores prácticas con dependency-injector framework
"""

import asyncio
from typing import Any, Dict, Optional, Callable, Awaitable
from abc import ABC, abstractmethod
import inspect

from dependency_injector import containers, providers
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Factory, Singleton, Configuration, Resource,
    Callable as CallableProvider, Coroutine
)

# Importar servicios que existen
from backendbot.core.services.logger_service import LoggerService
from backendbot.core.services.config_service import ConfigService


class IServiceLifetime(ABC):
    """Interfaz para lifetime de servicios"""

    @abstractmethod
    def get_instance(self) -> Any:
        """Obtener instancia del servicio"""
        pass


class TransientLifetime(IServiceLifetime):
    """Lifetime transient - nueva instancia cada vez"""

    def __init__(self, factory: Callable):
        self.factory = factory

    def get_instance(self, scope_id: str = None) -> Any:
        return self.factory()


class ScopedLifetime(IServiceLifetime):
    """Lifetime scoped - instancia compartida en el mismo scope"""

    def __init__(self, factory: Callable):
        self.factory = factory
        self._instance = None
        self._scope_id = None

    def get_instance(self, scope_id: str = None) -> Any:
        current_scope = scope_id or id(asyncio.current_task())
        if self._scope_id != current_scope:
            self._instance = self.factory()
            self._scope_id = current_scope
        return self._instance


class SingletonLifetime(IServiceLifetime):
    """Lifetime singleton - única instancia para toda la aplicación"""

    def __init__(self, factory: Callable):
        self.factory = factory
        self._instance = None

    def get_instance(self, scope_id: str = None) -> Any:
        if self._instance is None:
            self._instance = self.factory()
        return self._instance


class ServiceDescriptor:
    """Descriptor de servicio para registro"""

    def __init__(
        self,
        service_type: type,
        implementation: type = None,
        lifetime: str = "transient",
        factory: Callable = None
    ):
        self.service_type = service_type
        self.implementation = implementation or service_type
        self.lifetime = lifetime.lower()
        self.factory = factory

        # Crear lifetime manager
        if self.lifetime == "singleton":
            self.lifetime_manager = SingletonLifetime(self._create_factory())
        elif self.lifetime == "scoped":
            self.lifetime_manager = ScopedLifetime(self._create_factory())
        else:  # transient
            self.lifetime_manager = TransientLifetime(self._create_factory())

    def _create_factory(self) -> Callable:
        """Crear factory para el servicio"""
        if self.factory:
            return self.factory
        return lambda: self.implementation()

    def get_instance(self, scope_id: str = None) -> Any:
        """Obtener instancia del servicio"""
        return self.lifetime_manager.get_instance(scope_id)


class ModernDependencyInjectionContainer:
    """
    Contenedor moderno de DI con mejores prácticas
    Implementa patrones avanzados de inyección de dependencias
    """

    def __init__(self):
        # Crear el contenedor declarativo para providers estáticos
        self._declarative_container = containers.DeclarativeContainer()
        self._declarative_container.config = providers.Configuration()
        self._declarative_container.logger_service = providers.Singleton(
            lambda config: LoggerService(
                log_level=config.get('log_level', 'INFO'),
                log_file=config.get('log_file', 'backendbot.log'),
                config=config
            ),
            config=self._declarative_container.config
        )
        self._declarative_container.config_service = providers.Singleton(
            lambda config: ConfigService(
                config_file=config.get('config_file', 'backendbot.yaml'),
                config_dir=config.get('config_dir', 'config')
            ),
            config=self._declarative_container.config
        )

        # Contenedor dinámico para servicios registrados en runtime
        self.dynamic_services = containers.DynamicContainer()
        self._resources_initialized = False

    def register_service(
        self,
        service_type: type,
        implementation: type = None,
        lifetime: str = "transient",
        factory: Callable = None
    ):
        """
        Registrar un servicio en el contenedor

        Args:
            service_type: Tipo del servicio (interfaz)
            implementation: Implementación concreta
            lifetime: Lifetime del servicio (transient, scoped, singleton)
            factory: Factory opcional para crear instancias
        """
        impl = implementation or service_type

        if factory:
            provider = providers.Factory(factory)
        else:
            provider = providers.Factory(impl)

        # Aplicar lifetime
        if lifetime.lower() == "singleton":
            provider = providers.Singleton(impl)
        elif lifetime.lower() == "scoped":
            # Scoped no es directamente soportado, usar singleton por ahora
            provider = providers.Singleton(impl)
        # transient es el default (Factory)

        # Añadir al contenedor dinámico
        setattr(self.dynamic_services, service_type.__name__.lower(), provider)

    def resolve(self, service_type: type, scope_id: str = None) -> Any:
        """
        Resolver un servicio

        Args:
            service_type: Tipo del servicio a resolver
            scope_id: ID del scope (para servicios scoped)

        Returns:
            Instancia del servicio
        """
        service_name = service_type.__name__.lower()
        if hasattr(self.dynamic_services, service_name):
            provider = getattr(self.dynamic_services, service_name)
            return provider()
        else:
            raise ValueError(f"Service {service_type} not registered")

    def register_singleton(self, service_type: type, implementation: type = None):
        """Registrar servicio como singleton"""
        self.register_service(service_type, implementation, "singleton")

    def register_transient(self, service_type: type, implementation: type = None):
        """Registrar servicio como transient"""
        self.register_service(service_type, implementation, "transient")

    def register_scoped(self, service_type: type, implementation: type = None):
        """Registrar servicio como scoped"""
        self.register_service(service_type, implementation, "scoped")

    def init_resources(self):
        """Inicializar recursos del contenedor"""
        if not self._resources_initialized:
            # Aquí se pueden inicializar recursos como conexiones a BD, etc.
            self._resources_initialized = True
            print("Recursos del contenedor DI moderno inicializados")

    def shutdown_resources(self):
        """Liberar recursos del contenedor"""
        if self._resources_initialized:
            # Aquí se pueden liberar recursos
            self._resources_initialized = False
            print("Recursos del contenedor DI moderno liberados")

    def get_service_descriptors(self) -> Dict[str, Any]:
        """Obtener descriptores de servicios registrados"""
        return {name: getattr(self.dynamic_services, name) for name in dir(self.dynamic_services) if not name.startswith('_')}

    def has_service(self, service_type: type) -> bool:
        """Verificar si un servicio está registrado"""
        service_name = service_type.__name__.lower()
        return hasattr(self.dynamic_services, service_name)

    def clear_services(self):
        """Limpiar todos los servicios registrados"""
        # Crear un nuevo DynamicContainer vacío
        self.dynamic_services = containers.DynamicContainer()

    def check_dependencies(self):
        """Check if all dependencies are properly defined."""
        missing_deps = []
        for name in dir(self.dynamic_services):
            if not name.startswith('_'):
                provider = getattr(self.dynamic_services, name)
                try:
                    # Try to resolve the provider to check if dependencies are available
                    provider()
                except Exception as e:
                    missing_deps.append(f"{name}: {str(e)}")

        if missing_deps:
            raise ValueError(f"Missing dependencies: {', '.join(missing_deps)}")

    def detect_circular_dependencies(self):
        """Detect circular dependencies in the provider graph."""
        visited = set()
        rec_stack = set()
        path = []

        def dfs(provider_name, provider):
            visited.add(provider_name)
            rec_stack.add(provider_name)
            path.append(provider_name)

            # Get dependencies of this provider
            deps = self._get_provider_dependencies(provider)

            for dep_name in deps:
                if dep_name not in visited:
                    if hasattr(self.dynamic_services, dep_name):
                        dep_provider = getattr(self.dynamic_services, dep_name)
                        if dfs(dep_name, dep_provider):
                            return True
                    # Skip external dependencies
                elif dep_name in rec_stack:
                    # Found circular dependency
                    cycle_start = path.index(dep_name)
                    cycle = path[cycle_start:] + [dep_name]
                    raise ValueError(f"Circular dependency detected: {' -> '.join(cycle)}")

            path.pop()
            rec_stack.remove(provider_name)
            return False

        for name in dir(self.dynamic_services):
            if not name.startswith('_') and name not in visited:
                provider = getattr(self.dynamic_services, name)
                if dfs(name, provider):
                    return True
        return False

    def _get_provider_dependencies(self, provider):
        """Extract dependency names from a provider."""
        deps = []
        if hasattr(provider, '_args'):
            for arg in provider._args:
                if hasattr(arg, '__name__'):
                    deps.append(arg.__name__)
                elif isinstance(arg, str):
                    deps.append(arg)
        if hasattr(provider, '_kwargs'):
            for key, value in provider._kwargs.items():
                if hasattr(value, '__name__'):
                    deps.append(value.__name__)
                elif isinstance(value, str):
                    deps.append(value)
        return deps

    def validate_service_registration(self, service_name, service_class):
        """Validate that a service can be properly registered."""
        if not callable(service_class):
            raise ValueError(f"Service {service_name} must be callable (class or function)")

        # Check if service has proper constructor
        if hasattr(service_class, '__init__'):
            init_sig = inspect.signature(service_class.__init__)
            params = list(init_sig.parameters.values())[1:]  # Skip 'self'

            for param in params:
                if param.default == inspect.Parameter.empty and param.name not in dir(self.dynamic_services):
                    raise ValueError(f"Service {service_name} requires parameter '{param.name}' but no provider found")

    def validate_all_services(self):
        """Validate all registered services."""
        for name in dir(self.dynamic_services):
            if not name.startswith('_'):
                provider = getattr(self.dynamic_services, name)
                try:
                    # Try to get the service class from the provider
                    if hasattr(provider, '_cls'):
                        service_class = provider._cls
                    elif hasattr(provider, '_factory'):
                        service_class = provider._factory
                    else:
                        continue

                    self.validate_service_registration(name, service_class)
                except Exception as e:
                    raise ValueError(f"Validation failed for service {name}: {str(e)}")

    def get_dependency_graph(self):
        """Get a textual representation of the dependency graph."""
        graph_lines = ["Dependency Graph:"]
        for name in dir(self.dynamic_services):
            if not name.startswith('_'):
                provider = getattr(self.dynamic_services, name)
                deps = self._get_provider_dependencies(provider)
                if deps:
                    graph_lines.append(f"  {name} -> {', '.join(deps)}")
                else:
                    graph_lines.append(f"  {name} -> (no dependencies)")
        return "\n".join(graph_lines)
# Instancia global del contenedor moderno
container = ModernDependencyInjectionContainer()

# Configurar wiring para inyección automática
def setup_wiring():
    """Configurar wiring para inyección automática"""
    # En versiones modernas de dependency-injector, el wiring se configura automáticamente
    # No necesitamos register explícito
    pass


if __name__ == "__main__":
    # Demo del contenedor moderno
    print("🚀 Contenedor de DI Moderna - Demo")

    # Configurar wiring
    setup_wiring()

    # Inicializar contenedor
    container.init_resources()

    # Configurar el contenedor
    container.config.from_dict({
        'logger': {
            'level': 'INFO',
            'file': 'demo_backendbot.log'
        },
        'config_file': 'backendbot.yaml',
        'config_dir': 'config'
    })

    print("\n📋 Resolviendo servicios:")

    # Resolver servicios usando el contenedor
    logger = container.logger_service()
    config = container.config_service()

    print(f"✅ Logger service: {type(logger).__name__}")
    print(f"✅ Config service: {type(config).__name__}")

    print("\n📋 Registrando servicios personalizados:")

    # Servicio de ejemplo
    class DatabaseService:
        def __init__(self, connection_string: str = "sqlite:///demo.db"):
            self.connection_string = connection_string

        def connect(self):
            return f"Connected to {self.connection_string}"

    # Registrar servicio
    container.register_singleton(DatabaseService)

    # Resolver servicio personalizado
    db = container.resolve(DatabaseService)
    print(f"✅ Database service: {db.connect()}")

    print("\n📋 Información del contenedor:")

    descriptors = container.get_service_descriptors()
    print(f"📊 Servicios registrados: {len(descriptors)}")

    print("\n🔍 Validando dependencias...")

    try:
        container.check_dependencies()
        print("✅ Todas las dependencias están correctamente definidas")
    except ValueError as e:
        print(f"❌ Error en dependencias: {e}")

    try:
        container.detect_circular_dependencies()
        print("✅ No se detectaron dependencias circulares")
    except ValueError as e:
        print(f"❌ Dependencia circular encontrada: {e}")

    try:
        container.validate_all_services()
        print("✅ Todos los servicios son válidos")
    except ValueError as e:
        print(f"❌ Error de validación: {e}")

    print("\n📈 Grafo de dependencias:")
    print(container.get_dependency_graph())

    # Demo de dependencia circular (comentado para evitar error)
    print("\n⚠️  Demo de dependencia circular (comentado):")
    print("# class ServiceA:")
    print("#     def __init__(self, service_b): pass")
    print("# class ServiceB:")
    print("#     def __init__(self, service_a): pass")
    print("# container.register_transient(ServiceA, lambda: ServiceA(container.resolve(ServiceB)))")
    print("# container.register_transient(ServiceB, lambda: ServiceB(container.resolve(ServiceA)))")
    print("# container.detect_circular_dependencies()  # Esto lanzaría ValueError")

    # Limpiar recursos
    container.shutdown_resources()

    print("\n🎉 Demo completada exitosamente!")