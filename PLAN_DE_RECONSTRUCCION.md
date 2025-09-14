# Plan de Reconstrucción y Configuración Inicial de BackendBot

## 1. Introducción

Tras la eliminación accidental de archivos críticos, este plan detalla la estrategia para reconstruir y configurar el entorno de desarrollo local de `BackendBot`. El objetivo es restablecer la operatividad del backend, asegurar la correcta integración con los servicios de Railway (con un fuerte énfasis en la optimización de costos) y preparar la base para futuras expansiones.

## 2. Principios Rectores

Para garantizar un desarrollo robusto y eficiente, nos adheriremos a los siguientes principios:

*   **Modularidad:** Separación clara de responsabilidades para facilitar el desarrollo, las pruebas y el mantenimiento.
*   **Escalabilidad:** Diseño que permita el crecimiento y la adaptación a nuevas funcionalidades y cargas de trabajo.
*   **Mantenibilidad:** Código limpio, legible, bien estructurado y con comentarios cuando sea necesario para explicar el *porqué* de las decisiones.
*   **Seguridad:** Implementación de prácticas de seguridad básicas desde las primeras etapas.
*   **Optimización de Costos (Railway):** Priorización de soluciones y configuraciones que minimicen el consumo de recursos y créditos en la plataforma Railway.

## 3. Arquitectura Propuesta

### 3.1. Backend (Python con FastAPI)

El backend será el cerebro de la aplicación, gestionando toda la lógica de negocio y la interacción con los datos.

*   **Responsabilidades Clave:**
    *   **Lógica de Negocio:** Implementación de las reglas y procesos centrales de `BackendBot`.
    *   **API RESTful:** Exposición de endpoints para que el frontend (o cualquier cliente) interactúe con la aplicación.
    *   **Gestión de Datos:** Interacción con la base de datos (PostgreSQL) para almacenamiento y recuperación de información.
    *   **Tareas Programadas (Cron Jobs):** Ejecución de tareas automatizadas para mantenimiento, optimización y monitoreo.
    *   **Integración con Servicios Externos:** Conexión con la API de Railway para monitoreo y gestión de recursos, y uso de Redis para caché.
    *   **Monitoreo de Rendimiento:** Recopilación y análisis de métricas del sistema y la aplicación.
    *   **Autenticación y Autorización:** (Consideración futura) Gestión de acceso seguro a los recursos.
    *   **Análisis y Optimización de Recursos del Sistema:** Identificación de archivos no utilizados, programas inactivos y archivos antiguos para liberar espacio y optimizar el uso de RAM.

*   **Componentes Clave (Estructura de Directorios y Archivos):**
    *   `src/backendbot/`: Directorio principal del módulo Python.
        *   `main.py`: Punto de entrada de la aplicación FastAPI, inicialización de servicios.
        *   `api_routes.py`: Archivo que agrega todas las rutas de la API definidas en los módulos de `routers/`.
        *   `routers/`: Directorio para organizar las rutas de la API por funcionalidad (e.g., `history_routes.py`, `config_routes.py`, `monitor_routes.py`).
        *   `utils/`: Directorio para utilidades compartidas y módulos auxiliares.
            *   `db.py`: Módulo para la conexión y gestión de la base de datos.
            *   `cache.py`: Módulo para la interacción con Redis (caché).
            *   `logger.py`: Configuración centralizada del sistema de logging.
            *   `helpers.py`: Funciones de ayuda generales.
        *   `services/`: Directorio para la lógica de negocio más compleja y servicios específicos.
        *   `system_optimizer.py`: Módulo para la lógica de análisis y optimización de recursos del sistema.
        *   `models/`: Definiciones de modelos de datos (Pydantic para validación de API, SQLAlchemy/SQLModel para ORM de base de datos).
        *   `config.py`: Gestión de la configuración de la aplicación (variables de entorno, constantes).
        *   `railway_integration/`: Módulos específicos para interactuar con la API de Railway y sus servicios.
        *   `cron_jobs/`: Definición y gestión de las tareas programadas (APScheduler).
        *   `monitor/`: Módulos para la recolección y procesamiento de métricas del sistema (`psutil`, `GPUtil`, `WMI`).
    *   `requirements.txt`: Lista de dependencias de Python.
    *   `config.json`: Archivo de configuración general (si aplica, aunque se prefiere variables de entorno).

*   **Tecnologías Utilizadas:**
    *   **Framework Web:** FastAPI
    *   **Servidor ASGI:** Uvicorn
    *   **Base de Datos:** PostgreSQL (a través de Railway)
    *   **ORM:** SQLAlchemy / SQLModel
    *   **Caché:** Redis
    *   **Tareas Programadas:** APScheduler
    *   **Monitoreo del Sistema:** `psutil` (multiplataforma), `GPUtil` (GPU), `WMI` (Windows Management Instrumentation).

### 3.2. Frontend (Placeholder - No se implementará en esta fase)

El frontend es la capa de presentación que permite la interacción del usuario con el backend.

*   **Responsabilidades Clave:**
    *   **Interfaz de Usuario (UI):** Renderizado de componentes visuales y elementos interactivos.
    *   **Consumo de API:** Realización de solicitudes HTTP a los endpoints del backend.
    *   **Visualización de Datos:** Presentación de información y métricas de manera comprensible.
    *   **Experiencia de Usuario (UX):** Diseño intuitivo y responsivo.
    *   **Icono de Bandeja (Tray Icon):** Interfaz mínima para control rápido y notificaciones (parte de la interfaz de usuario que necesita ser restaurada).

*   **Tecnologías (Ejemplos - No se implementarán ahora):**
    *   **Frameworks:** React, Vue.js, Angular.
    *   **Lenguajes:** HTML, CSS, JavaScript/TypeScript.
    *   **Librerías UI:** Bootstrap, Material-UI, etc.

*   **Nota:** Por el momento, la interacción principal con el `BackendBot` se realizará a través de la línea de comandos (CLI) y pruebas directas a los endpoints de la API. La restauración del "Tray Icon" es una prioridad para la interacción local.

## 4. Plan de Reconstrucción Detallado (Fases)

### Fase 1: Restauración de la Estructura Básica y Corrección de Errores Críticos

1.  **Creación de Directorios Esenciales:**
    *   `mkdir -p src/backendbot/routers`
    *   `mkdir -p src/backendbot/utils`
    *   `mkdir -p src/backendbot/railway_integration`
    *   `mkdir -p src/backendbot/cron_jobs`
    *   `mkdir -p src/backendbot/monitor`
2.  **Creación de Archivos Mínimos para Evitar Errores de Importación:**
    *   `src/backendbot/main.py`: Punto de entrada con `import os` y `import platform`.
    *   `src/backendbot/api_routes.py`: Archivo vacío o con un `APIRouter` básico.
    *   `src/backendbot/routers/history_routes.py`: Archivo vacío o con un `APIRouter` básico.
    *   `src/backendbot/utils/db.py`: Archivo vacío o con una función `get_db_connection` placeholder.
    *   `src/backendbot/utils/cache.py`: Archivo vacío o con una función `get_redis_client` placeholder.
    *   `src/backendbot/config.py`: Archivo con configuración básica.
    *   `src/backendbot/__init__.py`: Archivos `__init__.py` en todos los directorios para que Python los reconozca como paquetes.
3.  **Verificación:** Intentar iniciar el servidor Uvicorn para asegurar que no haya errores de importación o `NameError`.

### Fase 2: Configuración de Base de Datos y Caché

1.  **Instrucciones `DATABASE_URL`:** Proporcionar al usuario las instrucciones para configurar la variable de entorno `DATABASE_URL` (esencial para PostgreSQL en Railway).
2.  **Instrucciones Redis:** Aconsejar sobre cómo iniciar un servidor Redis local o cómo configurar la aplicación para que no intente conectarse si no es necesario.
3.  **Implementación Básica de `db.py`:** Añadir la lógica para conectar a PostgreSQL usando `DATABASE_URL`.
4.  **Implementación Básica de `cache.py`:** Añadir la lógica para conectar a Redis.

### Fase 3: Restauración de la Funcionalidad del Tray Icon

1.  **Diagnóstico:** Investigar el error `Error iniciando tray icon: No module named 'backendbot'`. Esto a menudo indica un problema con la forma en que Python resuelve los módulos o con la configuración del entorno.
2.  **Corrección:** Ajustar la estructura de paquetes o el `PYTHONPATH` si es necesario para que el módulo `backendbot` sea reconocido correctamente.

### Fase 4: Integración con Railway y Cron Jobs

1.  **Revisión de `railway_integration/`:** Restaurar los módulos para interactuar con la API de Railway (webhooks, monitoreo de despliegues, etc.).
2.  **Revisión de `cron_jobs/`:** Restaurar la definición y programación de las tareas automatizadas (limpieza de logs, backups, optimización, etc.).

### Fase 5: Monitoreo y Optimización

1.  **Restauración de `monitor/`:** Implementar la recolección de métricas de rendimiento del sistema.
2.  **Estrategias de Optimización:** Verificar que las configuraciones y los cron jobs estén alineados con el objetivo de ahorro de costos en Railway.
3.  **Implementación de `system_optimizer.py`:** Desarrollar la lógica para escanear el sistema, identificar elementos no utilizados y generar reportes/recomendaciones.

## 5. Ejecución Local

Para iniciar el backend localmente una vez que las fases iniciales estén completas:

1.  **Instalar Dependencias:** Asegurarse de que todas las dependencias listadas en `requirements.txt` estén instaladas:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Iniciar el Servidor Uvicorn:**
    ```bash
    uvicorn src.backendbot.main:app --reload
    ```
    El flag `--reload` es útil para el desarrollo, ya que reinicia el servidor automáticamente al detectar cambios en el código.

Este plan nos guiará paso a paso para restaurar la funcionalidad completa de `BackendBot`.
