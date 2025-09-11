# BackendBot

BackendBot es una API construida con FastAPI para monitoreo y control de procesos del sistema, con funcionalidades avanzadas de health checks, logs, métricas y optimización de memoria.

## Estructura del Proyecto

```
BackendBot/
├── config/                 # Archivos de configuración
│   ├── python/            # Configuración Python (requirements.txt, pyproject.toml)
│   └── powershell/        # Configuración PowerShell
├── dashboard/             # Archivos del frontend/dashboard
├── data/                  # Base de datos y archivos de datos
├── docs/                  # Documentación
├── logs/                  # Archivos de logs
├── scripts/               # Scripts de automatización
│   ├── batch/            # Scripts batch (.bat)
│   ├── powershell/       # Scripts PowerShell (.ps1)
│   └── vbs/              # Scripts VBScript (.vbs)
├── services/              # Servicios adicionales
├── src/backendbot/        # Código fuente principal
├── temp/                  # Archivos temporales
├── tests/                 # Tests unitarios
└── tools/                 # Herramientas y módulos PowerShell
```

## Inicio Rápido

1. Ejecuta `scripts/batch/start_backend.bat` para iniciar el backend completo.
2. Ejecuta `scripts/batch/open_dashboard.bat` para abrir el dashboard en el navegador.

## Dashboard Frontend

- **dashboard/index.html**: Dashboard simple con navegación a Pro y API Docs.
- **dashboard/pro_dashboard.html**: Dashboard avanzado con gráficos en tiempo real y métricas.

## Características

### Backend
- Monitoreo de procesos del sistema
- Health checks automáticos
- Gestión de logs y métricas
- Optimización de memoria RAM
- API RESTful con FastAPI
- Base de datos SQLite integrada

### Frontend
- Navegación intuitiva entre dashboards
- Gráficos interactivos con Chart.js
- Diseño responsivo con Tailwind CSS
- Enlaces directos a documentación API

### Automatización
- Scripts PowerShell para monitoreo continuo
- Scripts batch para inicio rápido
- Automatización de tareas con Celery
- Integración con watchdog para monitoreo de archivos

## Instalación

```bash
# Instalar dependencias Python
pip install -r config/python/requirements.txt

# Instalar dependencias del sistema (si es necesario)
# Para Windows con PowerShell
scripts/powershell/install_dependencies.ps1
```

## Ejecución

### Backend
```bash
# Desde la raíz del proyecto
python src/backendbot/main.py

# O usando el script batch
scripts/batch/start_backend.bat
```

### Dashboard
```bash
# Abrir en navegador
scripts/batch/open_dashboard.bat

# O manualmente abrir dashboard/index.html
```

### Automatización
```powershell
# Ejecutar scripts de monitoreo
scripts/powershell/monitor_live.ps1

# Ver logs en tiempo real
scripts/powershell/log_viewer.ps1
```

## Desarrollo

### Tests
```bash
# Ejecutar todos los tests
pytest tests/

# Con cobertura
pytest --cov=src/backendbot tests/
```

### Formateo y Linting
```bash
# Formatear código
black src/backendbot/

# Verificar estilo
ruff check src/backendbot/
```

## API Documentation

Una vez ejecutado el backend, accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Base**: http://localhost:8000/api/v1

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
