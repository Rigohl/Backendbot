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