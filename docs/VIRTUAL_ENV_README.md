# Entorno Virtual de BackendBot

## Descripción
BackendBot utiliza un entorno virtual Python para aislar sus dependencias y asegurar un despliegue limpio y reproducible.

## ⚠️ Nota Importante: Compatibilidad con Python 3.12

Si usas **Python 3.12**, puede haber problemas con GPUtil (monitoreo de GPU). Esto es normal y no afecta la funcionalidad principal:

- ✅ **Funcionalidad principal**: CPU, RAM, Disco - funcionan perfectamente
- ⚠️ **GPU**: Funcionalidad limitada, pero el sistema sigue funcionando
- 🔧 **Solución**: Usa `instalar_dependencias.bat` para instalación automática con manejo de errores

## Scripts Disponibles

### `activar_venv.bat`
Activa el entorno virtual y abre una terminal de comandos lista para usar.
```cmd
activar_venv.bat
```

### `desactivar_venv.bat`
Desactiva el entorno virtual.
```cmd
desactivar_venv.bat
```

### `iniciar_backendbot.bat`
Inicia BackendBot usando el entorno virtual (recomendado).
```cmd
iniciar_backendbot.bat
```

### `instalar_dependencias.bat` ⭐ **Nuevo**
Instala todas las dependencias con manejo especial para Python 3.12.
```cmd
instalar_dependencias.bat
```

### `verificar_instalacion.bat` ⭐ **Nuevo**
Verifica que todas las dependencias estén instaladas correctamente.
```cmd
verificar_instalacion.bat
```

## Instalación del Entorno Virtual

### Opción 1: Instalación Automática (Recomendado)
```cmd
instalar_dependencias.bat
```

### Opción 2: Instalación Manual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias principales
pip install -r requirements.txt

# Instalar dependencias adicionales (con manejo de errores)
pip install PyQt5
pip install GPUtil || echo "GPUtil no compatible - usando monitoreo básico"
```

## Verificación de Instalación

Después de la instalación, verifica que todo funcione:

```bash
# Activar entorno
venv\Scripts\activate

# Verificar dependencias críticas
python -c "import PyQt5, psutil, fastapi; print('✅ Dependencias principales OK')"

# Verificar GPUtil (opcional)
python -c "try: import GPUtil; print('✅ GPUtil OK') except: print('⚠️ GPUtil no disponible - funcionalidad limitada')"
```

**O usa el script automático:**
```cmd
verificar_instalacion.bat
```

## Beneficios del Entorno Virtual

- ✅ **Aislamiento**: Las dependencias no interfieren con otras instalaciones de Python
- ✅ **Reproducibilidad**: Entorno consistente en diferentes máquinas
- ✅ **Limpieza**: Fácil de eliminar y recrear
- ✅ **Versionado**: Control preciso de versiones de dependencias
- ✅ **Seguridad**: Reduce riesgos de conflictos de dependencias
- ✅ **Compatibilidad**: Manejo automático de problemas de versiones

## Estructura del Proyecto con Entorno Virtual

```
BackendBot/
├── venv/                       # Entorno virtual
│   ├── Scripts/               # Scripts de activación (Windows)
│   ├── Lib/                   # Librerías instaladas
│   └── ...
├── src/                       # Código fuente
├── tests/                     # Tests
├── docs/                      # Documentación
├── activar_venv.bat          # Script de activación
├── desactivar_venv.bat       # Script de desactivación
├── instalar_dependencias.bat # Instalación automática ⭐
├── iniciar_backendbot.bat    # Inicio con venv
└── requirements.txt          # Dependencias
```

## Solución de Problemas

### GPUtil no funciona en Python 3.12
**Estado**: ✅ **SOLUCIONADO** - Monitoreo de GPU completamente funcional
**Solución implementada**: 
1. Módulo alternativo `gpu_monitor.py` compatible con Python 3.12
2. Soporte para múltiples métodos de detección de GPU (pynvml, comandos del sistema)
3. Funcionalidad completa de monitoreo de GPU restaurada
4. BackendBot detecta automáticamente GPUs NVIDIA y AMD

### Entorno virtual no se activa
**Solución**: Asegúrate de usar `venv\Scripts\activate` en Windows

### Dependencias faltantes
**Solución**: Ejecuta `instalar_dependencias.bat` o `pip install -r requirements.txt`

### PyQt5 no funciona
**Solución**: 
1. Asegúrate de tener Visual C++ Build Tools instalados
2. Ejecuta `instalar_dependencias.bat` 
3. Si falla, intenta: `pip install PyQt5 --only-binary=all`