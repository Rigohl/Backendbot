# BackendBot - La Colmena (The Hive)

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

### 0. Prerrequisitos

- **Base de Datos PostgreSQL:** Asegúrate de tener una base de datos PostgreSQL accesible. Para desarrollo local, puedes usar Docker o una instalación directa. Railway proveerá esto en producción.

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar el Entorno

Crea un archivo `.env` en la raíz del proyecto con la URL de tu base de datos. Ejemplo para PostgreSQL local o Railway:

```
DATABASE_URL="postgresql://user:password@host:port/dbname"
```

Para una base de datos SQLite local (recomendado para empezar a probar):

```
DATABASE_URL="sqlite:///./data/backend_data.db"
```

### 3. Ejecutar los Tests

Para verificar que toda la configuración es correcta y la aplicación funciona:

```bash
pytest
```

### 4. Iniciar el Sistema (Orquestador + Bots)

```bash
python launch.py
```

Este script iniciará el Orquestador FastAPI y el Bot Guardián, que a su vez gestionará los demás bots trabajadores. Presiona `Ctrl+C` en la terminal para detener todos los procesos de forma segura.

### 5. Acceder a la API y Dashboard

Una vez iniciado, puedes acceder a:

- **API:** `http://127.0.0.1:8000`
- **Dashboard:** `http://127.0.0.1:8000/dashboard`

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
