"""Container de dependencias avanzado para BackendBot - Arquitectura SOLID completa."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar, Generic, Optional, Callable
import logging
import inspect
from contextlib import contextmanager

from backendbot.core.data_repository import IDataRepository
from backendbot.core.config import get_settings, Settings
from backendbot.core.config_manager import DatabaseConfigManager
from backendbot.core.database.manager import DatabaseManager
from backendbot.core.logging_config import setup_logging

# Type variables para genéricos
T = TypeVar('T')
ServiceType = TypeVar('ServiceType')

# Configurar logging
logger = logging.getLogger(__name__)

# Importar framework moderno de DI (opcional)
try:
    from dependency_injector import containers, providers
    from dependency_injector.wiring import Provide, inject
    DEPENDENCY_INJECTOR_AVAILABLE = True
except ImportError:
    DEPENDENCY_INJECTOR_AVAILABLE = False
    logger.warning("dependency-injector not available, using fallback implementation")


class IServiceProvider(ABC):
    """Interfaz para proveedores de servicios - Principio de Inversión de Dependencias"""

    @abstractmethod
    def get_service(self, service_type: Type[T]) -> T:
        """Obtener una instancia del servicio solicitado"""
        pass

    @abstractmethod
    def register_service(self, service_type: Type[T], factory: Callable[[], T],
                        lifetime: str = "transient") -> None:
        """Registrar un servicio con su factory"""
        pass


class IServiceScope(ABC):
    """Interfaz para scopes de servicios"""

    @abstractmethod
    def get_service(self, service_type: Type[T]) -> T:
        """Obtener servicio dentro del scope"""
        pass

    @abstractmethod
    def dispose(self) -> None:
        """Liberar recursos del scope"""
        pass


class ServiceLifetime:
    """Enumeración de lifetimes de servicios"""
    TRANSIENT = "transient"  # Nueva instancia cada vez
    SCOPED = "scoped"       # Una instancia por scope
    SINGLETON = "singleton" # Una instancia para toda la aplicación


class ServiceDescriptor(Generic[T]):
    """Descriptor de servicio con metadata"""

    def __init__(self, service_type: Type[T], factory: Callable[[], T],
                 lifetime: str = ServiceLifetime.TRANSIENT):
        self.service_type = service_type
        self.factory = factory
        self.lifetime = lifetime
        self.instance: Optional[T] = None
        self.is_disposed = False

    def create_instance(self) -> T:
        """Crear nueva instancia usando la factory"""
        if self.is_disposed:
            raise RuntimeError(f"Service {self.service_type} has been disposed")

        try:
            instance = self.factory()
            if self.lifetime == ServiceLifetime.SINGLETON:
                self.instance = instance
            return instance
        except Exception as e:
            logger.error(f"Error creating service {self.service_type}: {e}")
            raise


# Container moderno usando dependency-injector si está disponible
if DEPENDENCY_INJECTOR_AVAILABLE:

    class ModernDependencyInjectionContainer(containers.DeclarativeContainer):
        """
        Container moderno usando python-dependency-injector
        Implementa mejores prácticas modernas de DI
        """

        # Configuration provider - supports YAML, JSON, env vars
        config = providers.Configuration()

        # Database provider with resource management
        database_manager = providers.Resource(
            DatabaseManager,
            connection_string=config.database.connection_string.optional(default="sqlite:///backendbot.db"),
            pool_size=config.database.pool_size.optional(default=5)
        )

        # Repository providers with interface segregation
        # Placeholder factory: real wiring happens via register_service()/legacy fallback
        data_repository = providers.Factory(lambda: None)

        # Settings service as singleton
        settings_service = providers.Singleton(
            Settings
        )

        # Logger provider (setup_logging expected no args)
        logger_service = providers.Singleton(lambda: setup_logging())

        # Async service provider example
        async def _noop_async_init():
            """No-op async initializer used as placeholder for async providers."""
            return None

        async_service = providers.Coroutine(
            _noop_async_init
        )

    # Instancia global del container moderno
    _modern_container: Optional[ModernDependencyInjectionContainer] = None

    def get_modern_container() -> ModernDependencyInjectionContainer:
        """Obtener instancia del container moderno"""
        global _modern_container
        if _modern_container is None:
            _modern_container = ModernDependencyInjectionContainer()
        return _modern_container

else:
    # Fallback si no está disponible dependency-injector
    ModernDependencyInjectionContainer = None
    get_modern_container = lambda: None


class DependencyInjectionContainer(IServiceProvider):
    """Container IoC avanzado que cumple con principios SOLID"""

    def __init__(self, use_modern_framework: bool = DEPENDENCY_INJECTOR_AVAILABLE):
        self._use_modern = use_modern_framework and DEPENDENCY_INJECTOR_AVAILABLE
        self._modern_container = None

        # Initialize legacy structures always so fallback works reliably
        self._services: Dict[Type[Any], ServiceDescriptor[Any]] = {}
        self._scoped_services: Dict[str, Dict[Type[Any], Any]] = {}
        self._current_scope_id: Optional[str] = None
        self._is_disposed = False

        if self._use_modern:
            # Setup modern container, but keep legacy structures for safe fallback
            self._modern_container = get_modern_container()
            self._configure_modern_container()

        # Register default services into legacy descriptors so get_service can fallback
        self._register_default_services()

    def _configure_modern_container(self):
        """Configurar el container moderno"""
        if not self._modern_container:
            return

        # Configurar desde variables de entorno
        # BACKENDBOT_API_KEY no es obligatorio en entornos locales; usar valor por defecto vacío
        try:
            self._modern_container.config.api_key.from_env("BACKENDBOT_API_KEY", required=False, default="")
        except Exception:
            # Algunos backends de providers pueden no aceptar 'default' param; fallback a required=False
            try:
                self._modern_container.config.api_key.from_env("BACKENDBOT_API_KEY", required=False)
            except Exception:
                pass
        self._modern_container.config.database.connection_string.from_env(
            "DATABASE_URL", default="sqlite:///backendbot.db"
        )
        self._modern_container.config.database.pool_size.from_env(
            "DB_POOL_SIZE", as_=int, default=5
        )

        # Wire the container
        if DEPENDENCY_INJECTOR_AVAILABLE:
            self._modern_container.wire(modules=[__name__])

    def _register_default_services(self):
        """Registrar servicios core por defecto.

        Registramos también en la estructura legacy para garantizar un
        fallback fiable cuando se use el container moderno.
        """
        # Settings como singleton
        self.register_service(Settings, lambda: get_settings(), ServiceLifetime.SINGLETON)

        # Config Manager como singleton
        self.register_service(
            DatabaseConfigManager,
            lambda: DatabaseConfigManager(self.get_service(Settings)),
            ServiceLifetime.SINGLETON,
        )

        # Logger como singleton - setup_logging no espera argumentos
        self.register_service(
            logging.Logger,
            lambda: setup_logging(),
            ServiceLifetime.SINGLETON,
        )

        # Registrar adapter LoggerService como implementación de ILogger (lazy import para evitar circular)
        try:
            def _logger_factory():
                from backendbot.services.logger_service import LoggerService
                return LoggerService()

            from backendbot.core.interfaces import ILogger
            self.register_service(ILogger, _logger_factory, ServiceLifetime.SINGLETON)
        except Exception:
            pass

        # Registrar ConfigService como implementación de IConfigManager (lazy import)
        try:
            def _config_factory():
                from backendbot.services.config_service import ConfigService
                return ConfigService()

            from backendbot.core.interfaces import IConfigManager
            self.register_service(IConfigManager, _config_factory, ServiceLifetime.SINGLETON)
        except Exception:
            pass

        # Database Manager como singleton
        self.register_service(DatabaseManager, lambda: DatabaseManager(), ServiceLifetime.SINGLETON)

        # Repositorios como scoped (uno por contexto de uso)
        from backendbot.core.data_repository import DataRepositoryFactory

        self.register_service(
            IDataRepository,
            lambda: DataRepositoryFactory.create_repository(
                self.get_service(Settings), self.get_service(DatabaseManager)
            ),
            ServiceLifetime.SCOPED,
        )

    def register_service(self, service_type: Type[T], factory: Callable[[], T],
                        lifetime: str = ServiceLifetime.TRANSIENT) -> None:
        """Registrar un servicio con su factory - Principio Abierto/Cerrado"""
        if self._use_modern and self._modern_container:
            # Usar providers del framework moderno
            if lifetime == ServiceLifetime.SINGLETON:
                provider = providers.Singleton(factory)
            elif lifetime == ServiceLifetime.SCOPED:
                provider = providers.ThreadLocalSingleton(factory)  # Approximation of scoped
            else:  # TRANSIENT
                provider = providers.Factory(factory)

            # Add to container dynamically
            setattr(self._modern_container, f"{service_type.__name__.lower()}_provider", provider)
            logger.debug(f"Registered modern service {service_type} with lifetime {lifetime}")
            # Also register into legacy descriptors to ensure fallback availability
            try:
                self._services[service_type] = ServiceDescriptor(service_type, factory, lifetime)
            except Exception:
                # If legacy structures are not initialized yet, ignore
                pass
        else:
            # Legacy implementation
            if self._is_disposed:
                raise RuntimeError("Container has been disposed")

            if service_type in self._services:
                logger.warning(f"Service {service_type} is being overwritten")

            self._services[service_type] = ServiceDescriptor(service_type, factory, lifetime)
            logger.debug(f"Registered legacy service {service_type} with lifetime {lifetime}")

    def get_service(self, service_type: Type[T]) -> T:
        """Obtener servicio - Principio de Responsabilidad Única"""
        if self._use_modern and self._modern_container:
            # Try to get from modern container
            try:
                provider_name = f"{service_type.__name__.lower()}_provider"
                if hasattr(self._modern_container, provider_name):
                    provider = getattr(self._modern_container, provider_name)
                    return provider()
                else:
                    # Try direct service resolution
                    return self._modern_container.get(service_type)
            except Exception as e:
                logger.warning(f"Modern container failed for {service_type}: {e}, falling back to legacy")
                return self._get_legacy_service(service_type)
        else:
            return self._get_legacy_service(service_type)

    def _get_legacy_service(self, service_type: Type[T]) -> T:
        """Legacy service resolution"""
        if self._is_disposed:
            raise RuntimeError("Container has been disposed")

        if service_type not in self._services:
            raise ValueError(f"Service {service_type} not registered")

        descriptor = self._services[service_type]

        # Manejar diferentes lifetimes
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if descriptor.instance is None:
                descriptor.instance = descriptor.create_instance()
            return descriptor.instance

        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if self._current_scope_id is None:
                raise RuntimeError("No active scope for scoped service")

            scope_services = self._scoped_services[self._current_scope_id]
            if service_type not in scope_services:
                scope_services[service_type] = descriptor.create_instance()
            return scope_services[service_type]

        else:  # TRANSIENT
            return descriptor.create_instance()

    @contextmanager
    def create_scope(self, scope_id: str):
        """Crear un scope para servicios scoped"""
        if self._use_modern:
            # Modern framework handles scoping differently
            yield self
        else:
            # Legacy scoping
            if self._is_disposed:
                raise RuntimeError("Container has been disposed")

            previous_scope = self._current_scope_id
            self._current_scope_id = scope_id
            self._scoped_services[scope_id] = {}

            try:
                yield self
            finally:
                # Limpiar servicios scoped
                if scope_id in self._scoped_services:
                    del self._scoped_services[scope_id]
                self._current_scope_id = previous_scope

    def resolve_dependencies(self, target_type: Type[T]) -> T:
        """Resolver dependencias automáticamente usando introspección"""
        if self._use_modern and DEPENDENCY_INJECTOR_AVAILABLE:
            # Usar el framework moderno para resolución automática
            try:
                return self._modern_container.resolve_dependencies(target_type)
            except:
                # Fallback to legacy
                return self._resolve_legacy_dependencies(target_type)
        else:
            return self._resolve_legacy_dependencies(target_type)

    def _resolve_legacy_dependencies(self, target_type: Type[T]) -> T:
        """Legacy dependency resolution"""
        if self._is_disposed:
            raise RuntimeError("Container has been disposed")

        # Obtener la signatura del constructor
        init_signature = inspect.signature(target_type.__init__)
        parameters = init_signature.parameters

        # Resolver dependencias
        kwargs = {}
        for param_name, param in parameters.items():
            if param_name == 'self':
                continue

            if param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = self.get_service(param.annotation)
                except ValueError:
                    # Si no está registrado, intentar con valor por defecto
                    if param.default != inspect.Parameter.empty:
                        kwargs[param_name] = param.default
                    else:
                        raise ValueError(f"Cannot resolve dependency {param_name} of type {param.annotation}")

        return target_type(**kwargs)

    def wire_module(self, module):
        """Wire a module for automatic injection (modern framework feature)"""
        if self._use_modern and DEPENDENCY_INJECTOR_AVAILABLE:
            self._modern_container.wire(modules=[module])
        else:
            logger.info("Wiring not available in legacy mode")

    def override_service(self, service_type: Type[T], factory: Callable[[], T]):
        """Override a service for testing (modern framework feature)"""
        if self._use_modern and self._modern_container:
            provider_name = f"{service_type.__name__.lower()}_provider"
            if hasattr(self._modern_container, provider_name):
                provider = getattr(self._modern_container, provider_name)
                provider.override(factory)
        else:
            logger.info("Service override not available in legacy mode")

    def reset_overrides(self):
        """Reset all service overrides"""
        if self._use_modern and self._modern_container:
            self._modern_container.reset_override()
        else:
            logger.info("Reset overrides not available in legacy mode")

    def dispose(self) -> None:
        """Liberar recursos - Principio de Responsabilidad Única"""
        if self._use_modern:
            # Modern framework handles disposal automatically
            if self._modern_container:
                self._modern_container.unwire()
        else:
            # Legacy disposal
            if self._is_disposed:
                return

            self._is_disposed = True

            # Dispose de servicios singleton que implementen IDisposable
            for descriptor in self._services.values():
                if descriptor.instance and hasattr(descriptor.instance, 'dispose'):
                    try:
                        descriptor.instance.dispose()
                    except Exception as e:
                        logger.error(f"Error disposing service {descriptor.service_type}: {e}")

            # Limpiar referencias
            self._services.clear()
            self._scoped_services.clear()

        logger.info("DependencyInjectionContainer disposed")


class ServiceFactory:
    """Factory para crear servicios - Principio de Responsabilidad Única"""

    def __init__(self, container: DependencyInjectionContainer):
        self.container = container

    def create_bot_manager(self):
        """Factory para BotManager"""
        from backendbot.bots.manager import BotManager
        return self.container.resolve_dependencies(BotManager)

    def create_tray_icon(self):
        """Factory para TrayIcon"""
        from backendbot.ui.tray_icon import TrayIcon
        return self.container.resolve_dependencies(TrayIcon)

    def create_chat_panel(self):
        """Factory para ChatPanel"""
        from backendbot.ui.chat_panel import ChatPanel
        return self.container.resolve_dependencies(ChatPanel)

    def create_api_server(self):
        """Factory para APIServer"""
        from backendbot.api.server import APIServer
        return self.container.resolve_dependencies(APIServer)

    def create_dashboard(self):
        """Factory para Dashboard"""
        from backendbot.ui.dashboard import Dashboard
        return self.container.resolve_dependencies(Dashboard)


# Singleton global del container
_container_instance: Optional[DependencyInjectionContainer] = None

def get_container(use_modern: bool = DEPENDENCY_INJECTOR_AVAILABLE) -> DependencyInjectionContainer:
    """Obtener instancia global del container"""
    global _container_instance
    if _container_instance is None or (hasattr(_container_instance, '_is_disposed') and _container_instance._is_disposed):
        _container_instance = DependencyInjectionContainer(use_modern_framework=use_modern)
    return _container_instance

def reset_container() -> None:
    """Reset del container para testing"""
    global _container_instance
    if _container_instance:
        _container_instance.dispose()
    _container_instance = None

def configure_container_from_env():
    """Configurar container desde variables de entorno"""
    container = get_container()
    if DEPENDENCY_INJECTOR_AVAILABLE and container._use_modern:
        # Modern configuration
        modern_container = container._modern_container
        if modern_container:
            # BACKENDBOT_API_KEY no es obligatorio en entornos locales; usar valor por defecto vacío
            try:
                modern_container.config.api_key.from_env("BACKENDBOT_API_KEY", required=False, default="")
            except Exception:
                try:
                    modern_container.config.api_key.from_env("BACKENDBOT_API_KEY", required=False)
                except Exception:
                    pass

            modern_container.config.database.connection_string.from_env(
                "DATABASE_URL", default="sqlite:///backendbot.db"
            )
            modern_container.config.database.pool_size.from_env(
                "DB_POOL_SIZE", as_=int, default=5
            )
    else:
        # Legacy configuration via settings
        logger.info("Using legacy configuration")

def validate_container_setup():
    """Validar que el container esté correctamente configurado"""
    container = get_container()

    try:
        # Test basic services
        settings = container.get_service(Settings)
        logger.info("✅ Container validation passed")
        return True
    except Exception as e:
        logger.error(f"❌ Container validation failed: {e}")
        return False

# Funciones de utilidad para mejores prácticas modernas
def inject_dependencies(func):
    """Decorator para inyección automática de dependencias (modern framework)"""
    if DEPENDENCY_INJECTOR_AVAILABLE:
        return inject(func)
    else:
        # Fallback: no injection
        return func

def provide_service(service_type: Type[T]):
    """Provider function for modern framework"""
    if DEPENDENCY_INJECTOR_AVAILABLE:
        container = get_container()
        if container._use_modern:
            return Provide(container._modern_container, service_type)
    return None

# Proxy lazy para compatibilidad con código existente
class _LazyContainerProxy:
    """Proxy lazy que mantiene compatibilidad con código existente"""

    def __init__(self):
        self._container = None

    @property
    def _ensure_container(self):
        if self._container is None:
            self._container = get_container()
        return self._container

    def get_settings(self):
        return self._ensure_container.get_service(Settings)

    def get_config_manager(self):
        return self._ensure_container.get_service(DatabaseConfigManager)

    def get_logger(self):
        return self._ensure_container.get_service(logging.Logger)

    def get_data_repository(self):
        from backendbot.core.data_repository import IDataRepository
        return self._ensure_container.get_service(IDataRepository)

    def get_db_manager(self):
        return self._ensure_container.get_service(DatabaseManager)

    def create_scope(self, scope_id: str):
        return self._ensure_container.create_scope(scope_id)

    def register_service(self, service_type: Type[T], factory: Callable[[], T],
                        lifetime: str = ServiceLifetime.TRANSIENT):
        return self._ensure_container.register_service(service_type, factory, lifetime)

    def get_service(self, service_type: Type[T]) -> T:
        return self._ensure_container.get_service(service_type)

    def resolve_dependencies(self, target_type: Type[T]) -> T:
        return self._ensure_container.resolve_dependencies(target_type)

    def wire_module(self, module):
        return self._ensure_container.wire_module(module)

    def override_service(self, service_type: Type[T], factory: Callable[[], T]):
        return self._ensure_container.override_service(service_type, factory)

    def reset_overrides(self):
        return self._ensure_container.reset_overrides()

    def dispose(self):
        if self._container:
            self._container.dispose()
            self._container = None

# Instancia global para compatibilidad
container = _LazyContainerProxy()


# Ejemplos de uso de mejores prácticas modernas
"""
Ejemplos de uso del sistema de DI mejorado:

1. Configuración moderna:
```python
from backendbot.core.di.container import get_container, configure_container_from_env

# Configurar desde variables de entorno
configure_container_from_env()

# Obtener container
container = get_container()

# Usar servicios
settings = container.get_service(Settings)
repo = container.get_service(IDataRepository)
```

2. Inyección automática con decoradores:
```python
from backendbot.core.di.container import inject_dependencies, provide_service

@inject_dependencies
def process_data(
    repository: IDataRepository = provide_service(IDataRepository),
    settings: Settings = provide_service(Settings)
):
    # Dependencias inyectadas automáticamente
    pass
```

3. Override para testing:
```python
# En tests
container.override_service(IDataRepository, lambda: MockRepository())
# ... ejecutar tests ...
container.reset_overrides()
```

4. Wiring de módulos:
```python
# En el punto de entrada de la aplicación
container.wire_module(my_module)
```

5. Scopes para manejo de recursos:
```python
with container.create_scope("request_scope") as scope:
    repo = scope.get_service(IDataRepository)
    # repo se limpia automáticamente al salir del scope
```
"""
