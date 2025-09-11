# 🖥️ BackendBot – Supervisor Autónomo de Procesos

**BackendBot** es un sistema local que mantiene tu backend siempre en ejecución, optimiza recursos y te da control desde la bandeja del sistema. Está diseñado para controlar el uso de RAM suspendiendo procesos de alto consumo como Discord, Steam, etc., y proporciona un dashboard web para monitoreo en tiempo real.

## 📋 Características

- **Monitoreo en tiempo real** de procesos y recursos del sistema.
- **Optimización automática** de RAM suspendiendo procesos hibernables.
- **Watchdog inteligente** con aprendizaje basado en decisiones previas.
- **Dashboard web** simple para visualizar procesos y métricas.
- **Icono en bandeja del sistema** para control rápido.
- **Scripts de automatización** para logs, reinicio, etc.

## 🛠️ Instalación

1. Clona o descarga el repositorio.
2. Navega al directorio raíz del proyecto.
3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Ejecuta el backend:
   - Desde scripts: `.\scripts\start_backend.bat`
   - O manualmente: `python src\backendbot\backend.py`

## 🚀 Uso

- **Iniciar Backend:** Ejecuta `scripts\start_backend.bat`.
- **Iniciar Tray Icon:** Ejecuta `scripts\start_tray.bat`.
- **Abrir Dashboard:** Ejecuta `scripts\open_dashboard.bat` o visita `http://127.0.0.1:8000/docs` para la API docs.
- **Ver Logs:** Ejecuta `scripts\log_viewer.ps1`.
- **Optimizar RAM:** Ejecuta `scripts\optimize_now.ps1`.

## 📚 API Endpoints

- `GET /procesos` - Lista procesos con PID, nombre, RAM.
- `POST /apagar/{pid}` - Termina un proceso por PID.
- `POST /optimize` - Optimiza RAM suspendiendo procesos hibernables.
- `POST /decision/{programa}/{accion}` - Registra decisión (suspender/rechazar).
- `GET /memoria` - Ver memoria de decisiones.
- `POST /reset-memoria` - Resetea memoria de decisiones.
- `GET /self` - Métricas del backend.

## ⚙️ Configuración

- Umbrales: CPU >80%, RAM >4000 MB por 60s.
- Procesos hibernables: Discord.exe, Steam.exe, RiotClientServices.exe.
- Logs en `logs/backend.log`.
- Memoria en `memory.json`.

## ☁️ Opción Gratuita para Montarlo

Dado que es un backend local para Windows, la mejor opción gratuita es ejecutarlo localmente. Si deseas una versión remota (no recomendada por dependencias de Windows), considera:

- **Render.com**: Despliegue gratuito para apps web, pero requiere adaptar para Linux.
- **Railway**: PaaS gratuito con soporte para Python/FastAPI.
- **Heroku**: Free tier para apps pequeñas.

Para despliegue remoto, necesitarías contenerizar con Docker y adaptar dependencias.

[Ver instrucciones completas arriba 👆]

---

## 🚀 Próximas Mejoras y Hoja de Ruta

Estamos trabajando activamente en las siguientes mejoras para BackendBot, enfocándonos en robustez, flexibilidad y una mejor experiencia de usuario:

1.  **Gestión de Configuración Externa:**
    *   Externalización de umbrales (CPU, RAM) y listas de programas "hibernables" a un archivo de configuración (ej. `.env` o YAML) utilizando `pydantic-settings`. Esto permitirá una personalización sencilla sin modificar el código fuente.

2.  **Manejo de Errores Robusto:**
    *   Implementación de un manejo de excepciones más específico y granular en todo el código para mejorar la depuración y la estabilidad general de la aplicación.

3.  **Modularización del Código:**
    *   Refactorización de `backend.py` en módulos más pequeños y especializados (ej. `api_routes.py`, `utils.py`, `watchdog.py`, `config.py`) para mejorar la mantenibilidad y escalabilidad del proyecto.

4.  **Seguridad (para despliegues no locales):**
    *   Investigación e implementación de mecanismos de autenticación y autorización para la API, en caso de que se considere un despliegue en entornos no locales o públicos.

5.  **Gestión Avanzada de Procesos:**
    *   Desarrollo de funcionalidades para reanudar procesos suspendidos, ya sea de forma manual o automática.
    *   Exploración de acciones escalables para procesos con consumo persistente, incluyendo opciones de terminación forzada bajo criterios estrictos.

6.  **Interacción y Feedback al Usuario Mejorados:**
    *   Investigación de notificaciones de Windows más interactivas que permitan al usuario tomar decisiones directamente desde la notificación.
    *   Mejora del feedback visual en el dashboard para mostrar el estado de los procesos, el impacto de las optimizaciones y el historial de eventos.

7.  **Recopilación y Análisis de Datos Históricos:**
    *   Implementación de una base de datos ligera (ej. SQLite) para almacenar datos históricos de consumo de recursos, eventos de optimización y decisiones del watchdog. Esto permitirá generar informes y visualizar tendencias en el dashboard.

8.  **Documentación Interna del Código:**
    *   Adición de docstrings completos y claros a todas las funciones, clases y métodos para facilitar la comprensión y el mantenimiento del código por parte de los desarrolladores.

9.  **Apagado Grácil de la Aplicación:**
    *   Asegurar un proceso de apagado limpio para la aplicación FastAPI y el hilo del watchdog, garantizando que los recursos se liberen correctamente y se guarde cualquier estado pendiente.

---

## ☁️ Despliegue No Local (Opciones de Backend Remoto)

Aunque BackendBot está diseñado principalmente para operar localmente, si en el futuro se deseara ejecutar el backend en un servidor remoto (por ejemplo, para monitorear múltiples máquinas o para una gestión centralizada), aquí hay algunas opciones recomendadas para el despliegue de la API de FastAPI:

1.  **Plataformas como Servicio (PaaS):**
    *   **Render.com:** Una plataforma sencilla y potente para desplegar aplicaciones web y APIs. Ofrece despliegues continuos desde Git y es muy amigable para proyectos Python/FastAPI.
    *   **Google App Engine / AWS Elastic Beanstalk:** Soluciones PaaS robustas de los principales proveedores de la nube, que abstraen gran parte de la gestión de infraestructura.

2.  **Contenedores (Docker) y Servicios de Contenedores:**
    *   **Docker:** Contenerizar la aplicación FastAPI en una imagen Docker es una excelente práctica para asegurar la portabilidad y consistencia del entorno.
    *   **Google Cloud Run / AWS Fargate:** Servicios que permiten ejecutar contenedores sin preocuparse por la gestión de servidores. Son ideales para APIs y microservicios, escalando automáticamente según la demanda.

Estas opciones permitirían que el backend de BackendBot se ejecute en la nube, accesible desde cualquier lugar (con la debida configuración de seguridad), desacoplando su ejecución de la máquina local del usuario.