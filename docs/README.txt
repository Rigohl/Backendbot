# BackendBot

## Instalación
1. Abre PowerShell en esta carpeta y ejecuta:
   pip install -r requirements.txt

## Uso
- Doble clic en start_backend.bat
- Abre en navegador: http://127.0.0.1:8000/docs

## Funciones API
- GET /procesos → lista procesos
- POST /apagar/{pid} → mata proceso
- POST /abrir/{programa} → abre Chrome, VS Code, Steam, Riot, Discord

## Bot integrado
- CPU: alerta si >80% durante 1 min
- RAM: alerta si >4000 MB durante 1 min
- GPU: alerta si >90% uso o VRAM >90%
- Pregunta en ventana emergente antes de cerrar
