from fastapi.templating import Jinja2Templates

# Instancia global de templates para evitar importaciones circulares
templates = Jinja2Templates(directory="src/backendbot/templates")