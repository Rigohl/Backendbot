# BackendBot - La Colmena (The Hive)

## 🚀 NUEVO: Sistema Automático Completo

**¡La forma más fácil de ejecutar BackendBot!** El sistema ahora incluye automatización completa que hace todo por ti.

### Inicio Automático (Recomendado)
```bash
# Windows - Sistema completo automático
python complete_auto_system.py

# O usando el batch file
auto_run.bat
```

**Este comando automáticamente:**
- ✅ Instala todas las dependencias
- 🗄️ Configura la base de datos (PostgreSQL o SQLite)
- 🚀 Inicia el servidor
- 🔍 Ejecuta verificaciones completas en paralelo
- 📊 Monitorea el sistema continuamente

### Verificación Independiente
```bash
# Solo ejecutar verificaciones
python auto_verify.py
```

---

Este repositorio contiene BackendBot, un sistema de monitoreo y gestión de recursos locales reconstruido con una **arquitectura de micro-servicios (bots)**. Diseñado para ser modular, resiliente y extensible, BackendBot opera como una "colmena" de bots especializados, orquestados por una API central.

## 🏛️ Arquitectura del Proyecto: La Colmena

BackendBot se compone de un **Orquestador central (FastAPI)** y múltiples **Bots Trabajadores** independientes que se comunican a través de una **base de datos PostgreSQL**.

- **El Orquestador (`src/backendbot/main.py`)**:
  - Es el punto de entrada principal y la API web.
  - Gestiona la comunicación con los bots a través de tablas en la base de datos.
  - Expone los endpoints para el Dashboard y otras aplicaciones.
  - Registra eventos importantes en la base de datos.

- **Los Bots Trabajadores (`src/backendbot/bots/`)**:
  - Son procesos Python independientes, cada uno con una tarea específica.
  - Se comunican con el Orquestador y entre sí a través de tablas en la base de datos.
  - Son supervisados por el **Bot Guardián** para asegurar su resiliencia.

- **Comunicación (`PostgreSQL`)**:
  - Utilizado como un bus de mensajes (tablas de comandos y resultados) y una base de datos para datos en tiempo real y estados de tareas.

- **Base de Datos (`SQLite/PostgreSQL`)**:
  - Almacena eventos históricos y acciones de los bots para auditoría y consulta.

## ✨ Características Clave

- **Arquitectura de Micro-servicios (Bots)**: Cada funcionalidad principal es un bot independiente, mejorando la modularidad y resiliencia.
- **Resiliencia Automática**: El **Bot Guardián** monitorea y reinicia automáticamente cualquier bot trabajador que se caiga.
- **Monitoreo de Sistema en Tiempo Real**: El **Bot Monitor** recopila y publica continuamente el uso de CPU y RAM.
- **Gestión Inteligente de Archivos**: El **Bot Organizador** puede escanear y reportar archivos duplicados, con un mecanismo de **borrado seguro (a la papelera)** que requiere tu confirmación.
- **Indexación y Búsqueda de Archivos**: El **Bot Indexador** crea un índice de tus archivos para búsquedas rápidas y eficientes.
- **Logging Detallado y Persistente**: Todos los eventos del sistema y acciones de los bots se registran en archivos de log y en una base de datos para un historial completo.
- **Configuración Flexible**: Carga la configuración desde un archivo `.env`.
- **Dashboard Web (Placeholder)**: Una interfaz de usuario básica lista para ser expandida, que consume las APIs de los bots.

## Endpoints de la API

La API principal se encuentra en `http://127.0.0.1:8000`.

| Método | Endpoint                      | Descripción                                                                        |
| :----- | :---------------------------- | :--------------------------------------------------------------------------------- |
| `GET`  | `/`                           | Endpoint raíz que devuelve un mensaje de bienvenida.                               |
| `GET`  | `/health`                     | Devuelve el estado de salud del servicio (útil para monitoreo en Railway).         |
| `GET`  | `/dashboard`                  | Muestra un dashboard web (actualmente un placeholder).                             |
| `GET`  | `/api/v1/monitor/stats`       | Devuelve un JSON con las últimas estadísticas de uso de CPU y RAM.                 |
| `GET`  | `/api/v1/history/`            | **(Placeholder)** Devuelve una lista de ejemplo de eventos del sistema.            |
| `POST` | `/api/v1/organizer/scan`      | Inicia un escaneo de duplicados en una ruta especificada.                          |
| `GET`  | `/api/v1/organizer/duplicates`| Obtiene la lista de duplicados encontrados (requiere confirmación para borrar).    |
| `POST` | `/api/v1/organizer/delete_duplicates`| Envía una orden para eliminar (a papelera) duplicados aprobados.                  |
| `POST` | `/api/v1/indexer/start_indexing`| Inicia la indexación de archivos en una ruta especificada.                         |
| `GET`  | `/api/v1/indexer/search?query=`| Busca archivos en el índice por palabra clave.                                     |
| `GET`  | `/api/v1/events/system`       | Consulta eventos del sistema registrados en la base de datos.                      |
| `GET`  | `/api/v1/events/bot_actions`  | Consulta acciones específicas de los bots registradas en la base de datos.         |

## 🚀 Instalación y Ejecución

Para poner en marcha BackendBot, sigue estos pasos:

### 1. Instalar Dependencias

Asegúrate de tener Python instalado (versión 3.9+ recomendada). Luego, instala las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

### 2. Configurar el Entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto para definir la URL de tu base de datos.

*   **Para empezar rápidamente con SQLite (recomendado para desarrollo local):**
    ```
    DATABASE_URL="sqlite:///./data/backend_data.db"
    ```
*   **Para usar PostgreSQL localmente:**
    ```
    DATABASE_URL="postgresql://user:password@host:port/dbname"
    ```
    (Reemplaza `user`, `password`, `host`, `port` y `dbname` con tus credenciales de PostgreSQL).

### 3. Configurar Base de Datos PostgreSQL (Opcional, solo si usas PostgreSQL localmente)

Si estás usando PostgreSQL y necesitas configurar la base de datos y el usuario, puedes ejecutar el script `setup_postgres.py` **una sola vez**:

```bash
python setup_postgres.py
```
**⚠️ Advertencia de Seguridad:** El script `setup_postgres.py` (y `grant_permissions.py`) contiene credenciales de base de datos hardcodeadas. Para entornos de producción o si compartes el código, es **crucial** externalizar estas credenciales a variables de entorno o un sistema de gestión de secretos.

### 4. Ejecutar los Tests (Opcional)

Para verificar que toda la configuración es correcta y la aplicación funciona:

```bash
pytest
```

### 5. Iniciar el Sistema (Orquestador + Bots)

Este es el paso principal para lanzar toda la "Colmena":

```bash
python launch.py
```

Este script iniciará el Orquestador FastAPI y el Bot Guardián, que a su vez gestionará los demás bots trabajadores. Presiona `Ctrl+C` en la terminal para detener todos los procesos de forma segura.

### 6. Acceder a la API y Dashboard

Una vez iniciado, puedes acceder a:

-   **API:** `http://127.0.0.1:8000`
-   **Dashboard:** `http://127.0.0.1:8000/dashboard`

## 🧪 Verificación de Despliegue en Railway

Para verificar que tu despliegue en Railway funciona correctamente, puedes usar el script `verificar_railway.py`.

```bash
python verificar_railway.py <URL_DE_TU_SERVICIO_WEB_EN_RAILWAY>
```

Ejemplo:

```bash
python verificar_railway.py https://backendbot-xyz.up.railway.app
```

Este script probará los endpoints principales de tu API y te dará un resumen del estado de tu despliegue.

## ☁️ Despliegue en Railway

Para desplegar BackendBot en Railway, seguirás estos pasos para configurar dos servicios principales: uno para el Orquestador (Web Service) y otro para los Bots (Worker Service).

### Paso 1: Crear un Nuevo Proyecto en Railway

1.  Ve a tu dashboard de Railway y haz clic en "New Project".
2.  Selecciona "Deploy from Git Repo" o "Empty Project" si prefieres configurar manualmente.

### Paso 2: Añadir el Servicio de Base de Datos PostgreSQL

1.  En tu nuevo proyecto de Railway, haz clic en "New" -> "Database" -> "PostgreSQL".
2.  Railway provisionará una base de datos PostgreSQL gestionada. Las credenciales de conexión estarán disponibles como variables de entorno.

### Paso 3: Configurar el Servicio Web (Orquestador FastAPI)

1.  En tu proyecto de Railway, haz clic en "New" -> "Deploy from Git Repo".
2.  Conecta tu repositorio de GitHub/GitLab donde tienes el código de `BackendBot`.
3.  **Configuración del Servicio:**
    *   **Environment:** `Python`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn src.backendbot.main:app --host 0.0.0.0 --port $PORT`
    *   **Variables de Entorno:** Asegúrate de que la variable `DATABASE_URL` esté vinculada a tu servicio de PostgreSQL. Railway lo hace automáticamente si lo creaste en el mismo proyecto.

### Paso 4: Configurar el Servicio Worker (Bots)

1.  En tu proyecto de Railway, haz clic en "New" -> "Deploy from Git Repo" (usa el mismo repositorio).
2.  **Configuración del Servicio:**
    *   **Environment:** `Python`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `python src/backendbot/bots/bot_guardian.py`
        *   *Explicación:* El Bot Guardián es un script de Python de larga ejecución que, una vez iniciado, se encarga de lanzar y supervisar a los demás bots (Monitor, Organizador, Indexador) como subprocesos dentro de este mismo worker de Railway.
    *   **Variables de Entorno:** Asegúrate de que la variable `DATABASE_URL` esté vinculada a tu servicio de PostgreSQL.

### Paso 5: Desplegar y Monitorear

1.  Una vez configurados ambos servicios, Railway intentará construir y desplegar tus aplicaciones.
2.  Monitorea los logs de ambos servicios para asegurarte de que se inicien sin errores y se conecten correctamente a la base de datos.

## 🤖 Flujo de Trabajo de Desarrollo (IA)

Este proyecto fue reconstruido por un equipo de IAs (Gemini y Copilot) coordinadas a través de un plan de tareas en `data/staging_plan.json`, demostrando un flujo de trabajo de desarrollo de software autónomo y asíncrono.

## 💡 Cómo Usar BackendBot

Una vez que el sistema BackendBot esté en ejecución (después de `python launch.py`), puedes interactuar con él de las siguientes maneras:

### 🌐 Dashboard Web

Accede al dashboard en tu navegador: `http://127.0.0.1:8000/dashboard`

Desde aquí podrás:
*   Ver métricas de CPU, RAM y Disco en tiempo real.
*   Activar la optimización del sistema.
*   Refrescar los datos.

### 🚀 API REST

Puedes interactuar con la API utilizando herramientas como `curl`, Postman, Insomnia o directamente desde tu código. Aquí algunos ejemplos de endpoints clave:

*   **Ver estado del sistema:**
    ```bash
    curl http://127.0.0.1:8000/health
    ```
*   **Obtener métricas detalladas:**
    ```bash
    curl http://127.0.0.1:8000/metrics
    ```
*   **Obtener lista de procesos:**
    ```bash
    curl http://127.0.0.1:8000/processes
    ```
*   **Iniciar un escaneo de duplicados (Bot Organizador):**
    ```bash
    curl -X POST http://127.0.0.1:8000/api/v1/organizer/scan -H "Content-Type: application/json" -d '{"path": "/ruta/a/escanear"}'
    ```
    (Reemplaza `"/ruta/a/escanear"` con la ruta real en tu sistema).

*   **Buscar archivos (Bot Indexador):**
    ```bash
    curl http://127.0.0.1:8000/api/v1/indexer/search?query=mi_archivo
    ```
    (Reemplaza `mi_archivo` con tu término de búsqueda).

Para una lista completa de endpoints, consulta la sección "Endpoints de la API" más arriba.

### 🛑 Detener el Sistema

Para detener todos los componentes de BackendBot, simplemente presiona `Ctrl+C` en la terminal donde ejecutaste `python launch.py`.
