import os
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt

try:
    from .config import settings
    from .process_routes import process_router  # New import
    from .services.ai_service import ai_service  # AI Service import
    from .utils import (
        load_memory,
        log_event,
        save_memory,
    )  # Removed store_process_data, store_optimization_event, restore_closed_processes
except ImportError:
    # Fallback for when running from tests
    from config import settings
    from process_routes import process_router
    from services.ai_service import ai_service
    from utils import (
        load_memory,
        log_event,
        save_memory,
    )

# Import staging automation functions
try:
    from .staging_automation import (
        schedule_optimizations,
        list_recommended_powershell_commands,
        prepare_background_command,
        optimize_ram,
        perform_disk_cleanup_preview,
        write_plan_to_file,
        run_preview_workflow,
    )
except ImportError:
    # Fallback for when running from tests
    from staging_automation import (
        schedule_optimizations,
        list_recommended_powershell_commands,
        prepare_background_command,
        optimize_ram,
        perform_disk_cleanup_preview,
        write_plan_to_file,
        run_preview_workflow,
    )

router = APIRouter()

try:
    from .dependencies import get_api_key, get_current_active_user
    from .routers import history_routes
except ImportError:
    # Fallback for when running from tests
    from dependencies import get_api_key, get_current_active_user
    from routers import history_routes

router.include_router(process_router)  # Include the new router
router.include_router(history_routes.router) # Include the history router


@router.post("/decision/{programa}/{accion}", dependencies=[Depends(get_current_active_user)])
async def guardar_decision(programa: str, accion: str) -> Dict[str, Any]:
    """Guarda la decisión de suspender o rechazar un programa en la memoria.

    Args:
        programa (str): El nombre del programa.
        accion (str): La acción realizada ('suspender' o 'rechazar').

    Returns:
        Dict[str, Any]: La información actualizada de las decisiones para el programa.

    """
    memory = await load_memory()
    memory.setdefault(programa, {"suspensiones": 0, "rechazos": 0})
    if accion == "suspender":
        memory[programa]["suspensiones"] += 1
    elif accion == "rechazar":
        memory[programa]["rechazos"] += 1
    await save_memory(memory)
    return memory.get(programa)


@router.get("/memoria", dependencies=[Depends(get_current_active_user)])
async def ver_memoria() -> dict[str, Any]:
    """Retorna el contenido actual de la memoria de decisiones.

    Returns:
        Dict[str, Any]: El diccionario que contiene la memoria de decisiones.

    """
    return await load_memory()


@router.post("/reset-memoria", dependencies=[Depends(get_api_key)])
async def reset_memoria() -> Dict[str, str]:
    """Resetea la memoria de decisiones a un estado vacío.

    Returns:
        Dict[str, str]: Un diccionario con el estado de la operación.

    """
    await save_memory({})
    log_event("🧹 Memoria de decisiones reseteada", notify_user=True)
    return {"status": "ok", "msg": "Memoria reiniciada"}


# === Autodiagnóstico (/self) ===
_app_start = time.time()


@router.get("/self", dependencies=[Depends(get_current_active_user)])
def self_metrics() -> dict[str, Any]:
    """Retorna métricas de autodiagnóstico del proceso del backend.

    Returns:
        Dict[str, Any]: Un diccionario con métricas como PID, uso de RAM, hilos, CPU, etc.

    Raises:
        HTTPException: Si ocurre un error al obtener las métricas.

    """
    try:
        p = psutil.Process(os.getpid())
        mem = p.memory_info()
        privados = getattr(mem, "private", None)
        privados_mb = None
        if privados is not None:
            privados_mb = round(privados / 1024 / 1024, 2)
        return {
            "pid": p.pid,
            "ram_mb": round(mem.rss / 1024 / 1024, 2),
            "privados_mb": privados_mb,
            "num_threads": p.num_threads(),
            "cpu_percent": p.cpu_percent(interval=0.1),
            "uptime_sec": round(time.time() - _app_start, 1),
            "started_at": datetime.fromtimestamp(
                _app_start, tz=timezone.utc
            ).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas de autodiagnóstico: {e}",
        ) from e





@router.get("/get-modo", dependencies=[Depends(get_api_key)])
def get_modo() -> dict[str, str]:
    """Retorna el modo de operación actual del BackendBot.

    Returns:
        Dict[str, str]: Un diccionario con la clave "modo" y el modo actual como valor.

    """
    return {"modo": settings.MODO}





@router.post("/auth/login")
async def login(credentials: dict[str, str]) -> dict[str, str]:
    """Autentica usuario y contraseña y retorna un token JWT si es válido.

    Args:
        credentials: Diccionario con username y password

    Returns:
        Dict[str, str]: Un token JWT si las credenciales son válidas

    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    username = credentials.get("username")
    password = credentials.get("password")

    if (hasattr(settings, 'ADMIN_USERNAME') and
        hasattr(settings, 'ADMIN_PASSWORD') and
        username == settings.ADMIN_USERNAME and
        password == settings.ADMIN_PASSWORD):

        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(timezone.utc) + access_token_expires
        to_encode = {"sub": username, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        return {"access_token": encoded_jwt, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas"
    )


@router.get("/logs", dependencies=[Depends(get_current_active_user)])
def get_logs(limit: int = 100) -> list[dict[str, Any]]:
    """Retorna los logs más recientes del backend.

    Args:
        limit (int): El número máximo de líneas de log a retornar.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de los logs.

    """
    def read_last_n_lines(file_path, n):
        """Reads the last n lines of a file efficiently."""
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'rb') as f: # Open in binary mode for seeking
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            
            block_size = 4096 # Read in 4KB blocks
            lines = []
            total_lines_read = 0
            
            # Start reading from the end of the file
            for i in range(1, int(file_size / block_size) + 2):
                offset = max(0, file_size - i * block_size)
                f.seek(offset)
                chunk = f.read(min(block_size, file_size - offset)).decode('utf-8', errors='ignore')
                
                # Split into lines and add to the beginning of the list
                new_lines = chunk.splitlines()
                for line in reversed(new_lines):
                    if line: # Avoid empty lines
                        lines.insert(0, line)
                        total_lines_read += 1
                        if total_lines_read >= n:
                            return lines[-n:] # Return the last n lines
                
                if offset == 0: # Reached beginning of file
                    break
            return lines[-n:]

    try:
        lines = read_last_n_lines(settings.LOG_FILE, limit)
        
        logs = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parsear el formato: [YYYY-MM-DD HH:MM:SS] mensaje
            if line.startswith("[") and "]" in line:
                timestamp_str, message = line.split("]", 1)
                timestamp_str = timestamp_str[1:]  # Remover el '[' inicial
                try:
                    # Intentar parsear la fecha
                    from datetime import datetime

                    timestamp = datetime.strptime(
                        timestamp_str, "%Y-%m-%d %H:%M:%S"
                    ).isoformat()
                except ValueError:
                    timestamp = timestamp_str

                # Determinar el nivel del log basado en el contenido del mensaje
                level = "info"
                if "❌" in message or "Error" in message.lower():
                    level = "error"
                elif "⚠️" in message or "Warning" in message.lower():
                    level = "warning"
                elif "✅" in message or "Success" in message.lower():
                    level = "info"
                elif "🔄" in message or "Debug" in message.lower():
                    level = "debug"

                logs.append(
                    {
                        "timestamp": timestamp,
                        "level": level,
                        "message": message.strip(),
                    }
                )
            else:
                # Si no tiene el formato esperado, agregarlo como info
                logs.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "level": "info",
                        "message": line,
                    }
                )

        return logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener logs: {e}",
        ) from e


# Integrated staging automation endpoints
@router.post("/schedule-optimizations", dependencies=[Depends(get_api_key)])
def api_schedule_optimizations(name: str = "backendbot_opt", command: str = "python main.py", schedule: str = "daily", dry_run: bool = True):
    """Schedule optimization tasks. Defaults to dry-run mode for safety."""
    try:
        plan = schedule_optimizations(name=name, command=command, schedule=schedule, dry_run=dry_run)
        log_event(f"Optimization scheduling plan created: {name}", notify_user=True)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling optimizations: {e}")


@router.get("/powershell-commands", dependencies=[Depends(get_api_key)])
def api_get_powershell_commands():
    """Get recommended PowerShell commands for automation."""
    try:
        cmds = list_recommended_powershell_commands()
        return {"commands": cmds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting PowerShell commands: {e}")


@router.post("/background-command", dependencies=[Depends(get_api_key)])
def api_prepare_background_command(script_path: str = "scripts/start_staging.ps1"):
    """Prepare a PowerShell command to run scripts in background."""
    try:
        cmd = prepare_background_command(script_path=script_path)
        return {"command": cmd, "note": "Execute this command in PowerShell to run in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preparing background command: {e}")


@router.post("/optimize-ram", dependencies=[Depends(get_api_key)])
def api_optimize_ram(dry_run: bool = True, max_processes: int = 10):
    """Optimize RAM usage by identifying and optionally terminating processes."""
    try:
        plan = optimize_ram(dry_run=dry_run, max_processes=max_processes)
        if not dry_run:
            log_event(f"RAM optimization executed: {plan.get('estimated_freed_mb', 0)} MB estimated", notify_user=True)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing RAM: {e}")


@router.post("/disk-cleanup-preview", dependencies=[Depends(get_api_key)])
def api_disk_cleanup_preview(directories: list = None, dry_run: bool = True):
    """Preview disk cleanup operations."""
    try:
        if directories is None:
            directories = [os.environ.get("TEMP", r"C:\\Windows\\Temp")]
        plan = perform_disk_cleanup_preview(directories=directories, dry_run=dry_run)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing disk cleanup: {e}")


@router.post("/run-preview-workflow", dependencies=[Depends(get_api_key)])
def api_run_preview_workflow(out_path: str = "data/optimization_plan.json"):
    """Run complete preview workflow and save plan to file."""
    try:
        plan = run_preview_workflow(out_path=out_path)
        log_event("Preview workflow completed and saved", notify_user=True)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running preview workflow: {e}")


@router.get("/automation-status", dependencies=[Depends(get_api_key)])
def get_automation_status():
    """Get current automation status and available features."""
    try:
        return {
            "staging_automation_available": True,
            "features": [
                "schedule_optimizations",
                "powershell_commands",
                "background_execution",
                "ram_optimization",
                "disk_cleanup",
                "preview_workflow"
            ],
            "safety_mode": "dry_run_default",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting automation status: {e}")

@router.post("/staging-preview", dependencies=[Depends(get_api_key)])
def run_staging_preview():
    """Ejecuta el workflow de preview de staging (dry-run)."""
    try:
        plan = run_preview_workflow()
        log_event("Staging preview ejecutado via API", notify_user=True)
        return {"status": "ok", "plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en staging preview: {e}")

@router.get("/metrics/ultra", dependencies=[Depends(get_api_key)])
def get_ultra_metrics():
    """Devuelve métricas avanzadas para el dashboard ultra."""
    import psutil
    import time
    try:
        ram = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.5)
        cores = psutil.cpu_count()
        uptime = time.time() - psutil.boot_time()
        processes = [
            {"pid": p.pid, "name": p.name(), "memory": p.memory_info().rss // 1024 // 1024}
            for p in psutil.process_iter(['pid', 'name', 'memory_info'])
        ][:10]
        # GPU (si disponible)
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            gpu_usage = gpus[0].load * 100 if gpus else 0
        except Exception:
            gpu_usage = 0
        return {
            "ram": {"used": ram.used // 1024 // 1024, "total": ram.total // 1024 // 1024},
            "cpu": {"usage": cpu, "cores": cores},
            "gpu": {"usage": gpu_usage},
            "uptime": int(uptime),
            "processes": processes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas ultra: {e}")


# ===== AI ROUTES =====

@router.get("/ai/status")
async def get_ai_status():
    """Obtiene el estado del servicio de IA y Ollama"""
    try:
        status = await ai_service.check_ollama_status()
        return {
            "ai_enabled": settings.AI_ENABLED,
            "ollama_status": status,
            "default_model": settings.DEFAULT_AI_MODEL,
            "conversations_count": len(ai_service.conversations),
            "agents_count": len(ai_service.agents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado de IA: {e}")


@router.post("/ai/conversation")
async def create_ai_conversation(model: str = None, system_prompt: str = None):
    """Crea una nueva conversación de IA"""
    try:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=400, detail="Servicio de IA deshabilitado")

        model = model or settings.DEFAULT_AI_MODEL
        conversation_id = await ai_service.create_conversation(model, system_prompt)

        return {
            "conversation_id": conversation_id,
            "model": model,
            "created": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando conversación: {e}")


@router.post("/ai/conversation/{conversation_id}/message")
async def send_ai_message(conversation_id: str, message: str, temperature: float = 0.7, max_tokens: int = 2048):
    """Envía un mensaje en una conversación de IA"""
    try:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=400, detail="Servicio de IA deshabilitado")

        response = await ai_service.send_message(
            conversation_id,
            message,
            temperature=temperature,
            max_tokens=max_tokens
        )

        if response is None:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        return {
            "response": response,
            "conversation_id": conversation_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje de IA: {e}")


@router.get("/ai/conversations")
async def list_ai_conversations():
    """Lista todas las conversaciones de IA"""
    try:
        conversations = []
        for conv in ai_service.conversations.values():
            conversations.append({
                "id": conv.id,
                "model": conv.model,
                "message_count": len(conv.messages),
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "last_message": conv.messages[-1].content[:100] + "..." if conv.messages else None
            })

        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando conversaciones: {e}")


@router.get("/ai/conversation/{conversation_id}")
async def get_ai_conversation(conversation_id: str):
    """Obtiene los detalles de una conversación específica"""
    try:
        if conversation_id not in ai_service.conversations:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        conv = ai_service.conversations[conversation_id]
        messages = []
        for msg in conv.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            })

        return {
            "id": conv.id,
            "model": conv.model,
            "messages": messages,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "context": conv.context
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo conversación: {e}")


@router.post("/ai/analyze-system")
async def analyze_system_with_ai():
    """Análisis inteligente del sistema usando IA"""
    try:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=400, detail="Servicio de IA deshabilitado")

        analysis = await ai_service.analyze_system_status()

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis de IA: {e}")


@router.post("/ai/agent")
async def create_ai_agent(name: str, description: str, capabilities: list[str], model: str = None):
    """Crea un nuevo agente de IA"""
    try:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=400, detail="Servicio de IA deshabilitado")

        model = model or settings.DEFAULT_AI_MODEL
        success = await ai_service.create_agent(name, description, capabilities, model)

        if not success:
            raise HTTPException(status_code=400, detail="Agente ya existe")

        return {
            "name": name,
            "created": True,
            "model": model
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando agente: {e}")


@router.get("/ai/agents")
async def list_ai_agents():
    """Lista todos los agentes de IA disponibles"""
    try:
        agents = []
        for name, agent in ai_service.agents.items():
            agents.append({
                "name": name,
                "description": agent["description"],
                "capabilities": agent["capabilities"],
                "model": agent["model"],
                "conversations_count": len(agent["conversations"]),
                "created_at": agent["created_at"]
            })

        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando agentes: {e}")


@router.post("/ai/agent/{agent_name}/task")
async def execute_agent_task(agent_name: str, task: str):
    """Ejecuta una tarea usando un agente específico"""
    try:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=400, detail="Servicio de IA deshabilitado")

        result = await ai_service.execute_agent_task(agent_name, task)

        if result is None:
            raise HTTPException(status_code=404, detail="Agente no encontrado")

        return {
            "agent": agent_name,
            "task": task,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando tarea del agente: {e}")


@router.delete("/ai/conversation/{conversation_id}")
async def delete_ai_conversation(conversation_id: str):
    """Elimina una conversación de IA"""
    try:
        if conversation_id not in ai_service.conversations:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        del ai_service.conversations[conversation_id]
        ai_service._save_conversations()

        return {"deleted": True, "conversation_id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando conversación: {e}")


@router.delete("/ai/agent/{agent_name}")
async def delete_ai_agent(agent_name: str):
    """Elimina un agente de IA"""
    try:
        if agent_name not in ai_service.agents:
            raise HTTPException(status_code=404, detail="Agente no encontrado")

        del ai_service.agents[agent_name]
        ai_service._save_agents()

        return {"deleted": True, "agent_name": agent_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando agente: {e}")
