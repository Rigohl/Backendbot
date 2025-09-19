# BackendBot - La Colmena (The Hive) — v2.0 (Documentación organizada)

Breve: BackendBot es un conjunto de bots locales que ayudan a optimizar, organizar y proteger tu equipo. Este README está reorganizado para facilitar instalación, ejecución local, pruebas y contribución; el README original se preserva íntegro al final del archivo.

**Resumen rápido**
 - Propósito: asistentes/bots locales para mantenimiento, organización, backups y automatización.
 - Modo: 100% local, sin servicios externos obligatorios.
 - Stack: Python 3.10+ (probado con 3.12), FastAPI para la API REST, PyQt5/GUI opcional.

**Contenido del README**
 - Instalación
 - Ejecución local
 - Pruebas
 - Configuración y variables de entorno
 - Estructura del proyecto
 - Desarrollo y contribución
 - Cambios recientes y notas de diseño
 - README ORIGINAL (preservado)

---

## Instalación

Recomendado: usar un entorno virtual y Python 3.10+ (3.12 funciona en la mayoría de las funciones).

Windows (PowerShell):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Notas:
 - Si usas GPU o librerías opcionales, revisa `requirements.txt` y la sección de compatibilidades.
 - Para desarrollo, recomendamos instalar `requirements-dev.txt`.

---

## Ejecución local

Opciones principales:

 - Versión integrada (recomendada, todo en una app):

```powershell
# Desde Windows Explorer: doble clic en `iniciar_backendbot_integrado.bat`
# O desde PowerShell con entorno activado:
python iniciar_backendbot_integrado.bat
```

 - Ejecutar componentes por separado:

```powershell
# API REST (FastAPI)
python api_server.py
# Dashboard (interfaz)
python dashboard.py
# Lanzador UI (antiguo)
python src\\backendbot\\main_ui_launcher.py
```

 - Ejecución rápida de comprobación (script corto):

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -c "import sys; sys.path.insert(0,'src'); from backendbot.bots.manager import BotManager; print(BotManager()._get_status())"
```

---

## Pruebas

 - Ejecutar tests unitarios locales:

```powershell
$env:PYTHONPATH = (Get-Location).Path
pytest -q
```

 - Nota: durante refactorizaciones la inicialización de `Settings` puede causar errores en la colección de tests si se instancia en import-time. Si ves `ValidationError` relacionados con `Settings`, asegúrate de tener un `.env` o de ejecutar en un entorno donde las variables necesarias estén definidas. El proyecto ahora expone `backendbot.core.config.get_settings()` para evitar validación en import-time.

---

## Configuración y variables de entorno

 - El proyecto usa Pydantic (v2) para `Settings` y carga variables con prefijo `BACKENDBOT_` (o `backendbot_` según la versión). Para ejecutar en un entorno de CI o local sin errores, crea un archivo `.env` en la raíz con las variables mínimas requeridas.

Ejemplo mínimo (`.env.example`):

```
BACKENDBOT_API_HOST=127.0.0.1
BACKENDBOT_API_PORT=8000
BACKENDBOT_DATABASE_URL=sqlite:///data/backendbot.db
BACKENDBOT_ENABLE_METRICS=false
# Claves opcionales
BACKENDBOT_MASTER_API_KEY=your_api_key_here
```

 - Recomendación: No instanciar `Settings` en import-time. Usa `from backendbot.core.config import get_settings; settings = get_settings()` en puntos de ejecución.

---

## Estructura del proyecto (resumen)

 - `src/` / `backendbot/` - paquete principal
 - `api_server.py`, `dashboard.py`, `main.py` - entrypoints
 - `backendbot/core/` - utilidades, config, logging, locks, audit
 - `backendbot/bots/` - implementación de bots y manager
 - `docs/` - documentación por subsistema
 - `tests/` - pruebas unitarias y de integración
 - `data/` - almacenamiento local, audit logs, persistencia ligera

---

## Desarrollo y Contribución

 - Estilo: sigue principios SOLID; código claro, modular y con tests.
 - Antes de crear PR:
   - Ejecuta `pytest -q` y corrige fallos.
   - Añade tests para nuevas funcionalidades.
   - Mantén el comportamiento local reproducible (no dependas de variables de entorno secretas en tests).
 - Para cambios grandes: abre un issue describiendo la propuesta y diseño. Se sugiere abrir PRs por feature/bug con una descripción clara y ejemplo de uso.

---

## Cambios recientes y notas de diseño

 - Añadido sistema local de `locks` y `audit` con append-only JSONL para auditoría local y `filelock` para la serialización de accesos. Ideal para prototipos locales; en producción recomendamos migrar a Redis/DB para locks y a un sistema centralizado de logs/auditoría.
 - `Settings` ahora debería instanciarse de forma perezosa con `get_settings()` para evitar ValidationsErrors en la colección de tests.
 - Se comenzó una refactorización para introducir un `BaseBot` canonical y migrar bots a heredar de él (trabajo en progreso en ramas feature).

---

## Próximos pasos sugeridos (para mantener el repo sano)

 - Añadir un `.env.example` (ya recomendado arriba). Yo puedo crearlo si quieres.
 - Ejecutar la suite completa de tests e iterar sobre fallos residuales.
 - Completar la unificación de bots bajo `BaseBot` y documentar la API interna para desarrolladores.
 - Revisar `.gitignore` para evitar commitear archivos de `venv/`, `logs/` o data sensibles.

---

## README ORIGINAL (preservado)

El contenido ORIGINAL del README se preserva a continuación exactamente como estaba al inicio de esta edición. No se ha eliminado información: el bloque a continuación es una copia fiel y puede servir de referencia o restauración.

````markdown

# 🐝 BackendBot - La Colmena (The Hive) **v2.0**

## 📌 Descripción General

BackendBot es un **asistente digital local avanzado** que funciona como una colmena de bots independientes, cada uno con una tarea específica, para optimizar tu PC, organizar tus archivos y gestionar recursos de forma eficiente, **sin depender de internet ni de servicios web**.  
**Versión 2.0** incluye arquitectura SOLID completa, sistemas avanzados de notificaciones, gestión inteligente de energía, backup robusto, dashboard interactivo y API REST para integraciones.

 - **100% local**: No requiere conexión a internet para funcionar.
 - **Ligero**: Optimizado para usar la menor cantidad posible de memoria RAM.
 - **Interfaz tipo aplicación**: No es una página web; es una app de escritorio con controles directos.
 - **Icono en la bandeja del sistema** (junto al reloj de Windows):
   - 🔴 **Rojo** = BackendBot encendido y trabajando.
   - ⚪ **Gris** = BackendBot apagado.
 - **Aprendizaje adaptativo**: Los bots aprenden de tus decisiones para mejorar con el tiempo.
 - **Control por chat**: Puedes darle órdenes en lenguaje natural y ejecutar comandos directamente.
 - **Panel flotante de reportes**: Ventanita tipo chat que muestra notificaciones y permite responder.
 - **🆕 Arquitectura SOLID**: Principios de diseño orientado a objetos completamente implementados.
 - **🆕 Sistemas avanzados**: Notificaciones, energía, backup, dashboard y API REST.
 - **🆕 Inyección de dependencias**: Container para gestión de servicios y configuración.

---

# 🐝 BackendBot - La Colmena (The Hive) **v2.0**

## 📌 Descripción General

BackendBot es un **asistente digital local avanzado** que funciona como una colmena de bots independientes, cada uno con una tarea específica, para optimizar tu PC, organizar tus archivos y gestionar recursos de forma eficiente, **sin depender de internet ni de servicios web**.  
**Versión 2.0** incluye arquitectura SOLID completa, sistemas avanzados de notificaciones, gestión inteligente de energía, backup robusto, dashboard interactivo y API REST para integraciones.

- **100% local**: No requiere conexión a internet para funcionar.
- **Ligero**: Optimizado para usar la menor cantidad posible de memoria RAM.
- **Interfaz tipo aplicación**: No es una página web; es una app de escritorio con controles directos.
- **Icono en la bandeja del sistema** (junto al reloj de Windows):
  - 🔴 **Rojo** = BackendBot encendido y trabajando.
  - ⚪ **Gris** = BackendBot apagado.
- **Aprendizaje adaptativo**: Los bots aprenden de tus decisiones para mejorar con el tiempo.
- **Control por chat**: Puedes darle órdenes en lenguaje natural y ejecutar comandos directamente.
- **Panel flotante de reportes**: Ventanita tipo chat que muestra notificaciones y permite responder.
- **🆕 Arquitectura SOLID**: Principios de diseño orientado a objetos completamente implementados.
- **🆕 Sistemas avanzados**: Notificaciones, energía, backup, dashboard y API REST.
- **🆕 Inyección de dependencias**: Container para gestión de servicios y configuración.

---

## 🚀 **Inicio Rápido - Versión Integrada Completa**

**¡NUEVO!** BackendBot ahora incluye una interfaz completamente integrada que combina todo en una sola aplicación.

### ⚡ **Inicio Súper Rápido (Recomendado)**
```cmd
# Doble clic en el archivo
iniciar_backendbot_integrado.bat
```

### 🔧 **Inicio Manual**
```cmd
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar versión integrada completa
python src\backendbot\main_integrated.py
```

### 📊 **¿Qué incluye la versión integrada?**

**🖥️ Interfaz Unificada Completa:**
- **Dashboard en tiempo real** con métricas de CPU, RAM, disco, red, batería y temperatura
- **Panel de Bots** con control completo de los 6 bots especializados
- **Sistemas Avanzados** integrados (notificaciones, energía, backup)
- **Chat Interactivo** integrado en la aplicación
- **Menú completo** con todas las opciones disponibles
- **Bandeja del sistema** con ícono rojo/verde según estado

**🤖 Bots Completamente Funcionales:**
1. **📊 Monitor** - Monitoreo en tiempo real del sistema
2. **📁 Organizer** - Organización automática de archivos
3. **🔍 Indexer** - Búsqueda instantánea de archivos
4. **🛡️ Guardian** - Supervisión y reinicio automático de bots
5. **📂 Auditor Archivos** - Detección de archivos antiguos
6. **💻 Auditor Programas** - Análisis de programas no usados

**⚙️ Sistemas Avanzados Integrados:**
- **🔔 Notificaciones** - Sistema inteligente con múltiples canales
- **⚡ Gestión de Energía** - Perfiles adaptativos (Alto Rendimiento, Equilibrado, Ahorro, Ultra Bajo)
- **💾 Backup** - Sistema robusto con estrategias múltiples
- **🌐 API REST** - Documentación completa en `/docs`
- **📊 Dashboard** - Métricas y gráficos en tiempo real

---

## 🎮 **Cómo Usar la Interfaz Integrada**

### **Panel Principal (Dashboard)**
- **Métricas en tiempo real** - CPU, RAM, disco, red, batería, temperatura
- **Estado de bots** - Lista completa con estado de cada bot
- **Gráficos históricos** - Tendencias de rendimiento (próximamente)

### **Panel de Bots**
- **Lista de bots disponibles** - Selecciona cualquier bot para ver detalles
- **Botón "Estado"** - Obtén información detallada del bot seleccionado
- **Botón "Ejecutar"** - Ejecuta acciones del bot (scan, status, etc.)
- **Área de resultados** - Ve los resultados de las operaciones

### **Sistemas Avanzados**
- **Notificaciones** - Envía notificaciones de prueba
- **Gestión de Energía** - Cambia perfiles de energía al instante
- **Backup** - Crea backups del sistema con un clic

### **Chat Interactivo**
- **Comandos en lenguaje natural** - Escribe "organiza mis descargas" o "muestra estado"
- **Respuestas inteligentes** - El sistema procesa y responde automáticamente
- **Historial completo** - Todas las conversaciones quedan guardadas

### **Bandeja del Sistema**
- **Ícono rojo** - BackendBot activo y funcionando
- **Doble clic** - Mostrar/ocultar la aplicación principal
- **Menú contextual** - Acceso rápido a funciones principales

---

## 🎯 **Comandos de Chat Disponibles**

```
help                    - Mostrar ayuda completa
status                  - Estado general del sistema
monitor status          - Estado del bot Monitor
organizer scan          - Escanear archivos para organizar
indexer search [término]- Buscar archivos
guardian backup         - Crear backup de seguridad
auditor_files scan      - Escanear archivos antiguos
auditor_programs scan   - Escanear programas no usados
```

---

## 🔗 **Acceso a Sistemas Individuales**

Si necesitas acceder a sistemas específicos individualmente:

```bash
# Solo Dashboard
python dashboard.py

# Solo API REST
python api_server.py
# Documentación: http://localhost:8000/docs

# Solo Chat (versión anterior)
python src\backendbot\main_ui_launcher.py
```

---

## ✅ **Verificación de Funcionamiento**

Para verificar que todo está funcionando correctamente:

```bash
python -c "
import sys
sys.path.insert(0, 'src')
from backendbot.bots.manager import BotManager
manager = BotManager()
print(manager._get_status())
"
```

**Deberías ver:**
```
📊 Estado de BackendBot:
🤖 Bots cargados: 6
  ✅ monitor: Monitor operativo
  ✅ organizer: Organizer operativo
  ✅ indexer: Indexer operativo
  ✅ guardian: Guardian operativo
  ✅ auditor_files: AuditorArchivos operativo
  ✅ auditor_programs: AuditorProgramas operativo
💾 Memoria: X% usada
```

---

## 🎉 **¡TODO INTEGRADO Y FUNCIONANDO!**

La nueva interfaz integrada combina **TODO** lo que BackendBot puede hacer en una sola aplicación:

- ✅ **Dashboard completo** con métricas en tiempo real
- ✅ **6 Bots especializados** completamente funcionales
- ✅ **Sistemas avanzados** integrados y accesibles
- ✅ **Chat interactivo** para control por voz
- ✅ **API REST** ejecutándose en segundo plano
- ✅ **Bandeja del sistema** con notificaciones
- ✅ **Menú completo** con todas las opciones
- ✅ **Interfaz moderna** y fácil de usar

**¡Ya no necesitas ejecutar múltiples aplicaciones! Todo está en un solo lugar.**

---

## 🆕 **Nuevos Sistemas Avanzados (v2.0)**

BackendBot ha evolucionado con sistemas avanzados que amplían sus capacidades de gestión y automatización:

### 🔔 **Sistema de Notificaciones Inteligente**
- **Múltiples canales**: Desktop, email, sonido y webhooks
- **Reglas inteligentes**: Notificaciones basadas en condiciones del sistema
- **Historial completo**: Seguimiento de todas las notificaciones enviadas
- **Cooldown system**: Evita spam de notificaciones repetidas

### ⚡ **Gestión Inteligente de Energía**
- **Perfiles adaptativos**: Automático cambio según carga del sistema
- **Monitoreo térmico**: Control de temperatura y ventiladores
- **Optimización automática**: Ajustes basados en batería vs. corriente
- **Perfiles personalizables**: High-performance, balanced, power-saver, ultra-low

### 💾 **Sistema de Backup Robusto**
- **Múltiples estrategias**: Incremental, diferencial y completo
- **Compresión inteligente**: Reducción de tamaño con algoritmos eficientes
- **Verificación de integridad**: Hashing para detectar corrupciones
- **Base de datos SQLite**: Seguimiento completo de archivos y versiones
- **Restauración selectiva**: Recuperar archivos específicos o versiones anteriores

### 📊 **Dashboard Interactivo**
- **Widgets en tiempo real**: CPU, RAM, disco, red y procesos
- **Controles directos**: Botones para acciones rápidas
- **Gráficos históricos**: Tendencias de rendimiento a lo largo del tiempo
- **Tema personalizable**: Interfaz adaptable a preferencias del usuario
- **Alertas visuales**: Indicadores de estado del sistema

### 🌐 **API REST Completa**
- **Endpoints completos**: Control total del sistema vía HTTP
- **Documentación automática**: Swagger UI y ReDoc integrados
- **Webhooks**: Notificaciones automáticas a sistemas externos
- **Automatización**: Integración con otros servicios y herramientas
- **FastAPI framework**: Alto rendimiento y validación automática

---

## 🚀 **Uso de los Nuevos Sistemas**

### Iniciar API REST
```bash
# Ejecutar servidor API
python api_server.py

# Acceder a documentación
# http://localhost:8000/docs
```

### Ejecutar Dashboard
```bash
# Desde el entorno virtual
python dashboard.py
```

### Configurar Notificaciones
```python
from notification_system import NotificationManager

manager = NotificationManager()
manager.send_notification(
    message="Sistema optimizado",
    priority="info",
    channels=["desktop", "email"]
)
```

### Gestionar Energía
```python
from power_management import PowerManager

manager = PowerManager()
manager.apply_profile("balanced")  # high_performance, balanced, power_saver, ultra_low
```

### Crear Backup
```python
from backup_system import BackupManager

manager = BackupManager()
manager.create_backup("daily_backup", strategy="incremental")
```

---

## 🤖 Bots Especializados

Cada bot es **totalmente independiente** y cumple una función específica para que solo se ejecute lo que necesitas:

- **Bot Monitor**  
  Vigila en tiempo real CPU, RAM, VRAM y uso de disco.  
  Genera alertas si detecta picos anormales y reporta al panel de chat.

- **Bot Organizador**  
  Escanea carpetas, clasifica archivos por tipo y fecha.  
  Detecta duplicados y solicita confirmación antes de borrarlos (a papelera).  
  Puede mover archivos a Google Drive según reglas.

- **Bot Indexador**  
  Crea un índice de todos los archivos para búsquedas instantáneas.  
  Permite buscar por nombre, extensión o fecha.  
  Actualiza el índice de forma incremental para ahorrar recursos.

- **Bot Guardián**  
  Supervisa que todos los bots activos estén funcionando.  
  Reinicia automáticamente cualquier bot que se detenga.  
  Puede pausar o apagar bots bajo demanda.

- **Bot Optimizador de Procesos**  
  Lista procesos activos y su consumo de recursos.  
  Puede **apagar procesos**, **congelarlos** (suspenderlos temporalmente) o **priorizarlos**.  
  Ajusta el uso de memoria virtual según el proceso.  
  Mantiene una lista blanca de procesos críticos que nunca se tocan.

- **Bot Auditor de Archivos Antiguos**  
  Escanea carpetas para detectar archivos que no se usan desde hace meses o años.  
  Genera reportes y sugiere archivarlos, moverlos o borrarlos.

- **Bot Auditor de Programas**  
  Detecta programas instalados que no se han usado en mucho tiempo.  
  Sugiere desinstalarlos o deshabilitarlos del inicio automático.  
  Puede generar un informe periódico de "software olvidado".

---

## 🖥️ Modos de Operación

BackendBot puede cambiar su comportamiento según lo que estés haciendo:

- **🎬 Modo Editor (Fotos/Vídeos/Música)**  
  Optimiza recursos para edición multimedia, priorizando programas como GIMP, DaVinci Resolve y otros relacionados.

- **📡 Modo Streaming**  
  Ajusta el sistema para transmisión en vivo, priorizando OBS y herramientas de chat, reduciendo procesos que puedan causar lag.

- **🎞️ Modo Relax**  
  Optimiza para ver películas o series, priorizando reproductores y navegadores, reduciendo procesos en segundo plano.

- **💻 Modo Desarrollo** *(opcional)*  
  Configura el entorno para programación, manteniendo activos editores y herramientas de depuración.

- **🎯 Modo Gaming** *(opcional)*  
  Libera recursos para juegos, cerrando procesos no esenciales y optimizando GPU/CPU.

---

## 💬 Control por Chat y Panel de Reportes

- **Chat interactivo**: Escribe órdenes como "organiza mi carpeta de descargas" o "libera memoria RAM" y BackendBot las ejecutará.
- **Panel flotante**: Muestra mensajes en tiempo real con el estado del sistema y acciones realizadas.
- **Respuestas inteligentes**: Te pedirá confirmación antes de acciones críticas.
- **Interacción directa**: No necesitas abrir consolas ni menús complejos.

---

## 🛠️ Funciones de Gestión de Recursos

- **Monitoreo en tiempo real** de CPU, RAM, VRAM y uso de disco.
- **Optimización de memoria** cerrando procesos no esenciales.
- **Análisis de disco** para detectar archivos grandes, antiguos o duplicados.
- **Limpieza de temporales y cachés** de forma segura.
- **Organización automática** de descargas por tipo y fecha.
- **Compresión y archivado** de carpetas poco usadas.
- **Protección de procesos críticos** para evitar cierres accidentales.
- **Monitoreo de red local** para detectar procesos con alto consumo de ancho de banda.
- **Tareas programadas** para limpiezas y optimizaciones en horarios de baja actividad.
- **🆕 Sistema de backup avanzado** con estrategias múltiples y compresión.
- **🆕 Gestión inteligente de energía** con perfiles adaptativos.
- **🆕 Notificaciones inteligentes** con múltiples canales y reglas.
- **🆕 Dashboard interactivo** con widgets en tiempo real.
- **🆕 API REST completa** para integraciones y automatización.

---

## 📂 Cómo Trabaja

1. **Se inicia** desde un script o acceso directo.
2. **Carga los bots** según el modo de operación seleccionado.
3. **Monitorea y organiza** en segundo plano, consumiendo pocos recursos.
4. **Reporta en tiempo real** a través del panel flotante.
5. **Aprende de tus decisiones** para automatizar tareas futuras.

---

## 📚 Documentación Completa

BackendBot v2.0 cuenta con documentación completa y actualizada para todos sus sistemas:

### 📖 **Documentos Disponibles**
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Documentación completa de la API REST con ejemplos
- **[Notification System](docs/NOTIFICATION_SYSTEM.md)** - Guía completa del sistema de notificaciones inteligentes
- **[Power Management](docs/POWER_MANAGEMENT.md)** - Documentación del sistema de gestión de energía
- **[Backup System](docs/BACKUP_SYSTEM.md)** - Guía completa del sistema de backup robusto
- **[Dashboard System](docs/DASHBOARD_SYSTEM.md)** - Documentación del dashboard interactivo
- **[System Integration](docs/SYSTEM_INTEGRATION.md)** - Guía de integración entre todos los sistemas

### 🔗 **Estado de la Documentación**
✅ **100% Completa** - Toda la documentación de BackendBot v2.0 está actualizada y disponible
- API REST completamente documentada con ejemplos prácticos
- Todos los sistemas avanzados tienen guías detalladas
- Ejemplos de código funcionales incluidos
- Guías de integración y configuración disponibles

### 📋 **Estructura de Documentación**
```
docs/
├── API_DOCUMENTATION.md      # API REST completa
├── NOTIFICATION_SYSTEM.md    # Sistema de notificaciones
├── POWER_MANAGEMENT.md       # Gestión de energía
├── BACKUP_SYSTEM.md          # Sistema de backup
├── DASHBOARD_SYSTEM.md       # Dashboard interactivo
├── SYSTEM_INTEGRATION.md     # Integración de sistemas
└── UI_README.md             # Interfaz de usuario
```

---

## 🎯 Objetivo

BackendBot está pensado para usuarios que quieren:
- Mantener su PC optimizada sin gastar recursos innecesarios.
- Organizar y limpiar archivos de forma automática.
- Tener control total desde una interfaz sencilla y un chat interactivo.
- Trabajar completamente **offline** y con **bajo consumo de RAM**.
- **🆕 Acceder a sistemas avanzados** de backup, notificaciones y gestión de energía.
- **🆕 Integrar con otros servicios** mediante API REST y webhooks.
- **🆕 Monitorear el sistema** con dashboard interactivo y métricas en tiempo real.
- **🆕 Contar con documentación completa** para todos los sistemas y funcionalidades.

---

## 📞 Soporte y Comunidad

- **Documentación**: Consulta la carpeta `docs/` para guías detalladas
- **Issues**: Reporta problemas en el repositorio
- **Contribuciones**: Las mejoras son bienvenidas siguiendo la arquitectura SOLID

---

**🐝 BackendBot v2.0 - La evolución de la gestión inteligente de sistemas**

---

## 🚀 Inicio Rápido con Entorno Virtual

BackendBot utiliza un **entorno virtual Python** para un despliegue limpio y seguro:

### ⚠️ Nota Importante: Compatibilidad con Python 3.12

Si usas **Python 3.12**, puede haber problemas con GPUtil (monitoreo de GPU). Esto es normal y no afecta la funcionalidad principal:

- ✅ **Funcionalidad principal**: CPU, RAM, Disco - funcionan perfectamente
- ✅ **Interfaz completa**: PyQt5 funcionando al 100%
- ✅ **Monitoreo de GPU**: Completamente funcional (compatible con Python 3.12)
- 🔧 **Solución**: Sistema alternativo inteligente que detecta GPUs automáticamente

### Opción 1: Inicio Automático (Recomendado)
```cmd
# Doble clic en el archivo
iniciar_backendbot.bat
```

### Opción 2: Inicio Manual
```cmd
# Activar entorno virtual
activar_venv.bat

# Ejecutar BackendBot
python src\backendbot\main_ui_launcher.py
```

### Opción 3: Recrear Entorno Virtual
```bash
# Crear nuevo entorno virtual
python -m venv venv

# Activar y instalar dependencias
venv\Scripts\activate
pip install -r requirements.txt
```

**Nota**: El entorno virtual asegura que las dependencias no interfieran con otras aplicaciones Python en tu sistema.

---

## 🆕 **Nuevos Sistemas Avanzados (v2.0)**

BackendBot ha evolucionado con sistemas avanzados que amplían sus capacidades de gestión y automatización:

### 🔔 **Sistema de Notificaciones Inteligente**
- **Múltiples canales**: Desktop, email, sonido y webhooks
- **Reglas inteligentes**: Notificaciones basadas en condiciones del sistema
- **Historial completo**: Seguimiento de todas las notificaciones enviadas
- **Cooldown system**: Evita spam de notificaciones repetidas

### ⚡ **Gestión Inteligente de Energía**
- **Perfiles adaptativos**: Automático cambio según carga del sistema
- **Monitoreo térmico**: Control de temperatura y ventiladores
- **Optimización automática**: Ajustes basados en batería vs. corriente
- **Perfiles personalizables**: High-performance, balanced, power-saver, ultra-low

### 💾 **Sistema de Backup Robusto**
- **Múltiples estrategias**: Incremental, diferencial y completo
- **Compresión inteligente**: Reducción de tamaño con algoritmos eficientes
- **Verificación de integridad**: Hashing para detectar corrupciones
- **Base de datos SQLite**: Seguimiento completo de archivos y versiones
- **Restauración selectiva**: Recuperar archivos específicos o versiones anteriores

### 📊 **Dashboard Interactivo**
- **Widgets en tiempo real**: CPU, RAM, disco, red y procesos
- **Controles directos**: Botones para acciones rápidas
- **Gráficos históricos**: Tendencias de rendimiento a lo largo del tiempo
- **Tema personalizable**: Interfaz adaptable a preferencias del usuario
- **Alertas visuales**: Indicadores de estado del sistema

### � **API REST Completa**
- **Endpoints completos**: Control total del sistema vía HTTP
- **Documentación automática**: Swagger UI y ReDoc integrados
- **Webhooks**: Notificaciones automáticas a sistemas externos
- **Automatización**: Integración con otros servicios y herramientas
- **FastAPI framework**: Alto rendimiento y validación automática

---

## 🚀 **Uso de los Nuevos Sistemas**

### Iniciar API REST
```bash
# Ejecutar servidor API
python api_server.py

# Acceder a documentación
# http://localhost:8000/docs
```

### Ejecutar Dashboard
```bash
# Desde el entorno virtual
python dashboard.py
```

### Configurar Notificaciones
```python
from notification_system import NotificationManager

manager = NotificationManager()
manager.send_notification(
    message="Sistema optimizado",
    priority="info",
    channels=["desktop", "email"]
)
```

### Gestionar Energía
```python
from power_management import PowerManager

manager = PowerManager()
manager.apply_profile("balanced")  # high_performance, balanced, power_saver, ultra_low
```

### Crear Backup
```python
from backup_system import BackupManager

manager = BackupManager()
manager.create_backup("daily_backup", strategy="incremental")
```

---

## 🤖 Bots Especializados

Cada bot es **totalmente independiente** y cumple una función específica para que solo se ejecute lo que necesitas:

- **Bot Monitor**  
  Vigila en tiempo real CPU, RAM, VRAM y uso de disco.  
  Genera alertas si detecta picos anormales y reporta al panel de chat.

- **Bot Organizador**  
  Escanea carpetas, clasifica archivos por tipo y fecha.  
  Detecta duplicados y solicita confirmación antes de borrarlos (a papelera).  
  Puede mover archivos a Google Drive según reglas.

- **Bot Indexador**  
  Crea un índice de todos los archivos para búsquedas instantáneas.  
  Permite buscar por nombre, extensión o fecha.  
  Actualiza el índice de forma incremental para ahorrar recursos.

- **Bot Guardián**  
  Supervisa que todos los bots activos estén funcionando.  
  Reinicia automáticamente cualquier bot que se detenga.  
  Puede pausar o apagar bots bajo demanda.

- **Bot Optimizador de Procesos**  
  Lista procesos activos y su consumo de recursos.  
  Puede **apagar procesos**, **congelarlos** (suspenderlos temporalmente) o **priorizarlos**.  
  Ajusta el uso de memoria virtual según el proceso.  
  Mantiene una lista blanca de procesos críticos que nunca se tocan.

- **Bot Auditor de Archivos Antiguos**  
  Escanea carpetas para detectar archivos que no se usan desde hace meses o años.  
  Genera reportes y sugiere archivarlos, moverlos o borrarlos.

- **Bot Auditor de Programas**  
  Detecta programas instalados que no se han usado en mucho tiempo.  
  Sugiere desinstalarlos o deshabilitarlos del inicio automático.  
  Puede generar un informe periódico de "software olvidado".

---

## 🖥️ Modos de Operación

BackendBot puede cambiar su comportamiento según lo que estés haciendo:

- **🎬 Modo Editor (Fotos/Vídeos/Música)**  
  Optimiza recursos para edición multimedia, priorizando programas como GIMP, DaVinci Resolve y otros relacionados.

- **📡 Modo Streaming**  
  Ajusta el sistema para transmisión en vivo, priorizando OBS y herramientas de chat, reduciendo procesos que puedan causar lag.

- **🎞️ Modo Relax**  
  Optimiza para ver películas o series, priorizando reproductores y navegadores, reduciendo procesos en segundo plano.

- **💻 Modo Desarrollo** *(opcional)*  
  Configura el entorno para programación, manteniendo activos editores y herramientas de depuración.

- **🎯 Modo Gaming** *(opcional)*  
  Libera recursos para juegos, cerrando procesos no esenciales y optimizando GPU/CPU.

---

## 💬 Control por Chat y Panel de Reportes

- **Chat interactivo**: Escribe órdenes como "organiza mi carpeta de descargas" o "libera memoria RAM" y BackendBot las ejecutará.
- **Panel flotante**: Muestra mensajes en tiempo real con el estado del sistema y acciones realizadas.
- **Respuestas inteligentes**: Te pedirá confirmación antes de acciones críticas.
- **Interacción directa**: No necesitas abrir consolas ni menús complejos.

---

## 🛠️ Funciones de Gestión de Recursos

- **Monitoreo en tiempo real** de CPU, RAM, VRAM y uso de disco.
- **Optimización de memoria** cerrando procesos no esenciales.
- **Análisis de disco** para detectar archivos grandes, antiguos o duplicados.
- **Limpieza de temporales y cachés** de forma segura.
- **Organización automática** de descargas por tipo y fecha.
- **Compresión y archivado** de carpetas poco usadas.
- **Protección de procesos críticos** para evitar cierres accidentales.
- **Monitoreo de red local** para detectar procesos con alto consumo de ancho de banda.
- **Tareas programadas** para limpiezas y optimizaciones en horarios de baja actividad.
- **🆕 Sistema de backup avanzado** con estrategias múltiples y compresión.
- **🆕 Gestión inteligente de energía** con perfiles adaptativos.
- **🆕 Notificaciones inteligentes** con múltiples canales y reglas.
- **🆕 Dashboard interactivo** con widgets en tiempo real.
- **🆕 API REST completa** para integraciones y automatización.

---

## 📂 Cómo Trabaja

1. **Se inicia** desde un script o acceso directo.
2. **Carga los bots** según el modo de operación seleccionado.
3. **Monitorea y organiza** en segundo plano, consumiendo pocos recursos.
4. **Reporta en tiempo real** a través del panel flotante.
5. **Aprende de tus decisiones** para automatizar tareas futuras.

---

## 📚 Documentación Completa

BackendBot v2.0 cuenta con documentación completa y actualizada para todos sus sistemas:

### 📖 **Documentos Disponibles**
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Documentación completa de la API REST con ejemplos
- **[Notification System](docs/NOTIFICATION_SYSTEM.md)** - Guía completa del sistema de notificaciones inteligentes
- **[Power Management](docs/POWER_MANAGEMENT.md)** - Documentación del sistema de gestión de energía
- **[Backup System](docs/BACKUP_SYSTEM.md)** - Guía completa del sistema de backup robusto
- **[Dashboard System](docs/DASHBOARD_SYSTEM.md)** - Documentación del dashboard interactivo
- **[System Integration](docs/SYSTEM_INTEGRATION.md)** - Guía de integración entre todos los sistemas

### 🔗 **Estado de la Documentación**
✅ **100% Completa** - Toda la documentación de BackendBot v2.0 está actualizada y disponible
- API REST completamente documentada con ejemplos prácticos
- Todos los sistemas avanzados tienen guías detalladas
- Ejemplos de código funcionales incluidos
- Guías de integración y configuración disponibles

### 📋 **Estructura de Documentación**
```
docs/
├── API_DOCUMENTATION.md      # API REST completa
├── NOTIFICATION_SYSTEM.md    # Sistema de notificaciones
├── POWER_MANAGEMENT.md       # Gestión de energía
├── BACKUP_SYSTEM.md          # Sistema de backup
├── DASHBOARD_SYSTEM.md       # Dashboard interactivo
├── SYSTEM_INTEGRATION.md     # Integración de sistemas
└── UI_README.md             # Interfaz de usuario
```

---

## 🎯 Objetivo

BackendBot está pensado para usuarios que quieren:
- Mantener su PC optimizada sin gastar recursos innecesarios.
- Organizar y limpiar archivos de forma automática.
- Tener control total desde una interfaz sencilla y un chat interactivo.
- Trabajar completamente **offline** y con **bajo consumo de RAM**.
- **🆕 Acceder a sistemas avanzados** de backup, notificaciones y gestión de energía.
- **🆕 Integrar con otros servicios** mediante API REST y webhooks.
- **🆕 Monitorear el sistema** con dashboard interactivo y métricas en tiempo real.
- **🆕 Contar con documentación completa** para todos los sistemas y funcionalidades.

---

## 📞 Soporte y Comunidad

- **Documentación**: Consulta la carpeta `docs/` para guías detalladas
- **Issues**: Reporta problemas en el repositorio
- **Contribuciones**: Las mejoras son bienvenidas siguiendo la arquitectura SOLID

---

**🐝 BackendBot v2.0 - La evolución de la gestión inteligente de sistemas**

## 🚀 Inicio Rápido con Entorno Virtual

BackendBot utiliza un **entorno virtual Python** para un despliegue limpio y seguro:

### ⚠️ Nota Importante: Compatibilidad con Python 3.12

Si usas **Python 3.12**, puede haber problemas con GPUtil (monitoreo de GPU). Esto es normal y no afecta la funcionalidad principal:

- ✅ **Funcionalidad principal**: CPU, RAM, Disco - funcionan perfectamente
- ✅ **Interfaz completa**: PyQt5 funcionando al 100%
- ✅ **Monitoreo de GPU**: Completamente funcional (compatible con Python 3.12)
- 🔧 **Solución**: Sistema alternativo inteligente que detecta GPUs automáticamente

### Opción 1: Inicio Automático (Recomendado)
```cmd
# Doble clic en el archivo
iniciar_backendbot.bat
```

### Opción 2: Inicio Manual
```cmd
# Activar entorno virtual
activar_venv.bat

# Ejecutar BackendBot
python src\backendbot\main_ui_launcher.py
```

### Opción 3: Recrear Entorno Virtual
```bash
# Crear nuevo entorno virtual
python -m venv venv

# Activar y instalar dependencias
venv\Scripts\activate
pip install -r requirements.txt
```

**Nota**: El entorno virtual asegura que las dependencias no interfieran con otras aplicaciones Python en tu sistema.

---

## 🆕 **Nuevos Sistemas Avanzados (v2.0)**

BackendBot ha evolucionado con sistemas avanzados que amplían sus capacidades de gestión y automatización:

### 🔔 **Sistema de Notificaciones Inteligente**
- **Múltiples canales**: Desktop, email, sonido y webhooks
- **Reglas inteligentes**: Notificaciones basadas en condiciones del sistema
- **Historial completo**: Seguimiento de todas las notificaciones enviadas
- **Cooldown system**: Evita spam de notificaciones repetidas

### ⚡ **Gestión Inteligente de Energía**
- **Perfiles adaptativos**: Automático cambio según carga del sistema
- **Monitoreo térmico**: Control de temperatura y ventiladores
- **Optimización automática**: Ajustes basados en batería vs. corriente
- **Perfiles personalizables**: High-performance, balanced, power-saver, ultra-low

### 💾 **Sistema de Backup Robusto**
- **Múltiples estrategias**: Incremental, diferencial y completo
- **Compresión inteligente**: Reducción de tamaño con algoritmos eficientes
- **Verificación de integridad**: Hashing para detectar corrupciones
- **Base de datos SQLite**: Seguimiento completo de archivos y versiones
- **Restauración selectiva**: Recuperar archivos específicos o versiones anteriores

### 📊 **Dashboard Interactivo**
- **Widgets en tiempo real**: CPU, RAM, disco, red y procesos
- **Controles directos**: Botones para acciones rápidas
- **Gráficos históricos**: Tendencias de rendimiento a lo largo del tiempo
- **Tema personalizable**: Interfaz adaptable a preferencias del usuario
- **Alertas visuales**: Indicadores de estado del sistema

### 🌐 **API REST Completa**
- **Endpoints completos**: Control total del sistema vía HTTP
- **Documentación automática**: Swagger UI y ReDoc integrados
- **Webhooks**: Notificaciones automáticas a sistemas externos
- **Automatización**: Integración con otros servicios y herramientas
- **FastAPI framework**: Alto rendimiento y validación automática

---

## 🤖 Bots Especializados

Cada bot es **totalmente independiente** y cumple una función específica para que solo se ejecute lo que necesitas:

- **Bot Monitor**  
  Vigila en tiempo real CPU, RAM, VRAM y uso de disco.  
  Genera alertas si detecta picos anormales y reporta al panel de chat.

- **Bot Organizador**  
  Escanea carpetas, clasifica archivos por tipo y fecha.  
  Detecta duplicados y solicita confirmación antes de borrarlos (a papelera).  
  Puede mover archivos a Google Drive según reglas.

- **Bot Indexador**  
  Crea un índice de todos los archivos para búsquedas instantáneas.  
  Permite buscar por nombre, extensión o fecha.  
  Actualiza el índice de forma incremental para ahorrar recursos.

- **Bot Guardián**  
  Supervisa que todos los bots activos estén funcionando.  
  Reinicia automáticamente cualquier bot que se detenga.  
  Puede pausar o apagar bots bajo demanda.

- **Bot Optimizador de Procesos**  
  Lista procesos activos y su consumo de recursos.  
  Puede **apagar procesos**, **congelarlos** (suspenderlos temporalmente) o **priorizarlos**.  
  Ajusta el uso de memoria virtual según el proceso.  
  Mantiene una lista blanca de procesos críticos que nunca se tocan.

- **Bot Auditor de Archivos Antiguos**  
  Escanea carpetas para detectar archivos que no se usan desde hace meses o años.  
  Genera reportes y sugiere archivarlos, moverlos o borrarlos.

- **Bot Auditor de Programas**  
  Detecta programas instalados que no se han usado en mucho tiempo.  
  Sugiere desinstalarlos o deshabilitarlos del inicio automático.  
  Puede generar un informe periódico de “software olvidado”.

---

## 🖥️ Modos de Operación

BackendBot puede cambiar su comportamiento según lo que estés haciendo:

- **🎬 Modo Editor (Fotos/Vídeos/Música)**  
  Optimiza recursos para edición multimedia, priorizando programas como GIMP, DaVinci Resolve y otros relacionados.

- **📡 Modo Streaming**  
  Ajusta el sistema para transmisión en vivo, priorizando OBS y herramientas de chat, reduciendo procesos que puedan causar lag.

- **🎞️ Modo Relax**  
  Optimiza para ver películas o series, priorizando reproductores y navegadores, reduciendo procesos en segundo plano.

- **💻 Modo Desarrollo** *(opcional)*  
  Configura el entorno para programación, manteniendo activos editores y herramientas de depuración.

- **🎯 Modo Gaming** *(opcional)*  
  Libera recursos para juegos, cerrando procesos no esenciales y optimizando GPU/CPU.

---

## � **Uso de los Nuevos Sistemas**

### Iniciar API REST
```bash
# Ejecutar servidor API
python api_server.py

# Acceder a documentación
# http://localhost:8000/docs
```

### Ejecutar Dashboard
```bash
# Desde el entorno virtual
python dashboard.py
```

### Configurar Notificaciones
```python
from notification_system import NotificationManager

manager = NotificationManager()
manager.send_notification(
    message="Sistema optimizado",
    priority="info",
    channels=["desktop", "email"]
)
```

### Gestionar Energía
```python
from power_management import PowerManager

manager = PowerManager()
manager.apply_profile("balanced")  # high_performance, balanced, power_saver, ultra_low
```

### Crear Backup
```python
from backup_system import BackupManager

manager = BackupManager()
manager.create_backup("daily_backup", strategy="incremental")
```

---

## �💬 Control por Chat y Panel de Reportes

- **Chat interactivo**: Escribe órdenes como “organiza mi carpeta de descargas” o “libera memoria RAM” y BackendBot las ejecutará.
- **Panel flotante**: Muestra mensajes en tiempo real con el estado del sistema y acciones realizadas.
- **Respuestas inteligentes**: Te pedirá confirmación antes de acciones críticas.
- **Interacción directa**: No necesitas abrir consolas ni menús complejos.

---

## 🛠️ Funciones de Gestión de Recursos

- **Monitoreo en tiempo real** de CPU, RAM y VRAM.
- **Optimización de memoria** cerrando procesos no esenciales.
- **Análisis de disco** para detectar archivos grandes, antiguos o duplicados.
- **Limpieza de temporales y cachés** de forma segura.
- **Organización automática** de descargas por tipo y fecha.
- **Compresión y archivado** de carpetas poco usadas.
- **Protección de procesos críticos** para evitar cierres accidentales.
- **Monitoreo de red local** para detectar procesos con alto consumo de ancho de banda.
- **Tareas programadas** para limpiezas y optimizaciones en horarios de baja actividad.

---

## 📂 Cómo Trabaja

1. **Se inicia** desde un script o acceso directo.
2. **Carga los bots** según el modo de operación seleccionado.
3. **Monitorea y organiza** en segundo plano, consumiendo pocos recursos.
4. **Reporta en tiempo real** a través del panel flotante.
5. **Aprende de tus decisiones** para automatizar tareas futuras.

---

## 🎯 Objetivo

BackendBot está pensado para usuarios que quieren:
- Mantener su PC optimizada sin gastar recursos innecesarios.
- Organizar y limpiar archivos de forma automática.
- Tener control total desde una interfaz sencilla y un chat interactivo.
- Trabajar completamente **offline** y con **bajo consumo de RAM**.