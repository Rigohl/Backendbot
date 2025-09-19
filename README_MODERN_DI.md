# BackendBot - Arquitectura SOLID Moderna con DI Avanzada

## 🚀 Visión General

BackendBot implementa una arquitectura moderna basada en los principios SOLID con un sistema avanzado de inyección de dependencias (DI) que combina las mejores prácticas de frameworks como `dependency-injector` y patrones de Microsoft.Extensions.DependencyInjection.

## 🏗️ Arquitectura Implementada

### Principios SOLID Aplicados

1. **S - Single Responsibility**: Cada servicio tiene una responsabilidad única y bien definida
2. **O - Open/Closed**: Los servicios son extensibles sin modificar el código existente
3. **L - Liskov Substitution**: Las implementaciones pueden ser sustituidas por sus interfaces
4. **I - Interface Segregation**: Interfaces específicas en lugar de generales
5. **D - Dependency Inversion**: Dependencias de abstracciones, no de implementaciones concretas

### Sistema de Inyección de Dependencias

#### Lifetimes de Servicios
- **Transient**: Nueva instancia cada resolución
- **Scoped**: Instancia compartida en el mismo scope
- **Singleton**: Única instancia para toda la aplicación

#### Proveedores de Configuración
- **YAML**: Configuración estructurada en archivos YAML
- **JSON**: Configuración en formato JSON
- **Environment**: Variables de entorno con prefijo `BACKENDBOT_`
- **Default**: Valores por defecto integrados

## 📁 Estructura del Proyecto

```
backendbot/
├── core/
│   ├── di/
│   │   ├── container.py              # Contenedor legacy (compatible)
│   │   └── enhanced_container.py     # Contenedor moderno
│   ├── services/
│   │   ├── logger_service.py         # Servicio de logging moderno
│   │   └── config_service.py         # Servicio de configuración avanzado
│   └── config/
│       └── advanced_config.py        # Configuración avanzada
├── ui/                              # Componentes de interfaz
├── bots/                            # Gestión de bots
└── api/                             # API REST
```

## 🔧 Configuración

### Archivo de Configuración (config/backendbot.yaml)

```yaml
# Configuración de base de datos
database:
  url: "sqlite:///backendbot.db"
  pool_size: 5
  max_overflow: 10

# Configuración de logging
logging:
  level: "INFO"
  file: "backendbot.log"
  max_size: 10485760
  backup_count: 5

# Configuración de UI
ui:
  theme: "dark"
  language: "es"
  tray_icon: true

# Configuración de API
api_port: 8000
api_host: "localhost"
ssl_enabled: false
```

### Variables de Entorno

```bash
# Override configuración via environment
export BACKENDBOT_API_PORT=9000
export BACKENDBOT_LOGGING_LEVEL=DEBUG
export BACKENDBOT_DATABASE_URL="postgresql://user:pass@localhost/db"
```

## 💻 Uso del Sistema de DI

### Configuración Básica

```python
from backendbot.core.di.enhanced_container import container, setup_wiring

# Configurar wiring para inyección automática
setup_wiring()

# Inicializar contenedor
container.init_resources()

# Configurar servicios
container.config.from_dict({
    'logger': {'level': 'INFO', 'file': 'app.log'},
    'config_file': 'backendbot.yaml',
    'config_dir': 'config'
})
```

### Inyección Automática con Decorators

```python
from dependency_injector.wiring import inject, Provide

class MyService:
    @inject
    def __init__(
        self,
        logger: LoggerService = Provide['logger_service'],
        config: ConfigService = Provide['config_service']
    ):
        self.logger = logger
        self.config = config

    def do_work(self):
        self.logger.info("Trabajando...", "MyService")
        db_url = self.config.get('database.url')
        # ... lógica del servicio
```

### Registro Manual de Servicios

```python
# Registrar servicios con diferentes lifetimes
container.register_singleton(DatabaseService)
container.register_transient(CacheService)
container.register_scoped(RequestContextService)

# Resolver servicios
db = container.resolve(DatabaseService)
cache = container.resolve(CacheService)
```

### Uso de Funciones con Inyección

```python
@inject
def process_data(
    data: Dict,
    logger: LoggerService = Provide['logger_service'],
    cache: CacheService = Provide['cache_service']
):
    logger.info(f"Procesando {len(data)} items", "Processor")
    # ... procesamiento
```

## 🎯 Mejores Prácticas Implementadas

### 1. Inyección de Constructor
```python
class OrderService:
    def __init__(self, repository: IOrderRepository, logger: ILogger):
        self.repository = repository
        self.logger = logger
```

### 2. Manejo de Lifetimes
```python
# Singleton para servicios costosos
container.register_singleton(DatabaseConnection)

# Transient para servicios stateless
container.register_transient(ValidationService)

# Scoped para contexto de request
container.register_scoped(UserContext)
```

### 3. Configuración Multi-fuente
```python
# Prioridad: Environment > Archivo > Default
config_service = ConfigService()
api_port = config_service.get('api.port', 8000)
```

### 4. Logging Estructurado
```python
logger.info("Usuario creado", "UserService", {
    'user_id': user.id,
    'email': user.email
})
```

## 🚀 Ejecución

### Demo del Sistema Moderno
```bash
python demo_modern_di.py
```

### Aplicación Principal
```bash
python main.py
```

### Con Configuración Personalizada
```bash
BACKENDBOT_LOGGING_LEVEL=DEBUG python main.py
```

## 🔍 Monitoreo y Debugging

### Ver Servicios Registrados
```python
descriptors = container.get_service_descriptors()
for service_type, descriptor in descriptors.items():
    print(f"{service_type.__name__}: {descriptor.lifetime}")
```

### Verificar Configuración
```python
config = container.config_service()
print(config.get_all())
```

## 📊 Beneficios de la Arquitectura Moderna

1. **Mantenibilidad**: Código modular y fácil de mantener
2. **Testabilidad**: Inyección facilita los tests unitarios
3. **Flexibilidad**: Fácil cambio de implementaciones
4. **Escalabilidad**: Arquitectura preparada para crecimiento
5. **Configurabilidad**: Configuración externa y flexible
6. **Observabilidad**: Logging estructurado y monitoreo

## 🔄 Migración desde Sistema Legacy

El sistema mantiene compatibilidad con el contenedor legacy mientras introduce las nuevas capacidades:

```python
# Legacy (aún soportado)
from backendbot.core.di.container import container as legacy_container
factory = ServiceFactory(legacy_container)

# Moderno (recomendado)
from backendbot.core.di.enhanced_container import container
service = container.resolve(MyService)
```

## 📈 Próximos Pasos

1. **Implementar Providers Asíncronos**: Para servicios que requieren async/await
2. **Añadir Validación de Configuración**: Esquemas JSON Schema para configuración
3. **Implementar Health Checks**: Verificación automática de dependencias
4. **Añadir Métricas**: Monitoreo de rendimiento de servicios
5. **Documentar APIs**: Generación automática de documentación

---

## 🤝 Contribución

Para contribuir al desarrollo de BackendBot:

1. Seguir los principios SOLID en todo nuevo código
2. Usar el sistema de DI para nuevas dependencias
3. Añadir tests para nueva funcionalidad
4. Actualizar documentación según cambios
5. Mantener compatibilidad con versiones anteriores

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para más detalles.