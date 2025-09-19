#!/usr/bin/env python3
"""Módulo de monitoreo de GPU compatible con Python 3.12
Solución alternativa a GPUtil que maneja el error de distutils.
"""

import logging
import platform
import re
import subprocess

logger = logging.getLogger(__name__)


class GPUInfo:
    """Clase que representa información de una GPU."""

    def __init__(
        self,
        id,
        name="Unknown GPU",
        memory_total=0,
        memory_used=0,
        memory_free=0,
        temperature=0,
    ) -> None:
        self.id = id
        self.name = name
        self.memoryTotal = memory_total
        self.memoryUsed = memory_used
        self.memoryFree = memory_free
        self.temperature = temperature


def getGPUs():
    """Función compatible con GPUtil.getGPUs()
    Retorna una lista de objetos GPUInfo.
    """
    gpus = []

    try:
        # Intentar usar GPUtil primero
        import GPUtil

        gpus_gputil = GPUtil.getGPUs()
        for gpu in gpus_gputil:
            gpu_info = GPUInfo(
                id=gpu.id,
                name=gpu.name,
                memory_total=gpu.memoryTotal,
                memory_used=gpu.memoryUsed,
                memory_free=gpu.memoryFree,
                temperature=getattr(gpu, "temperature", 0),
            )
            gpus.append(gpu_info)
        logger.info(f"GPUtil funcionó correctamente - {len(gpus)} GPUs encontradas")
        return gpus

    except ImportError as e:
        logger.warning(f"GPUtil no disponible: {e}")
    except Exception as e:
        logger.error(f"Error con GPUtil: {e}")

    # Si GPUtil falla, intentar métodos alternativos
    try:
        # Método 1: Usar nvidia-ml-py si está disponible (mejor que pynvml)
        try:
            import pynvml

            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()

            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                # Convertir bytes a string si es necesario
                if isinstance(name, bytes):
                    name = name.decode("utf-8")
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                temperature = 0
                try:
                    temp_info = pynvml.nvmlDeviceGetTemperature(
                        handle, pynvml.NVML_TEMPERATURE_GPU
                    )
                    temperature = temp_info
                except:
                    pass

                gpu_info = GPUInfo(
                    id=i,
                    name=name,
                    memory_total=memory_info.total // (1024 * 1024),  # Convertir a MB
                    memory_used=memory_info.used // (1024 * 1024),
                    memory_free=memory_info.free // (1024 * 1024),
                    temperature=temperature,
                )
                gpus.append(gpu_info)

            pynvml.nvmlShutdown()
            logger.info(
                f"nvidia-ml-py funcionó correctamente - {len(gpus)} GPUs encontradas"
            )
            return gpus

        except ImportError:
            logger.warning("pynvml no disponible")
        except Exception as e:
            logger.error(f"Error con pynvml: {e}")

    except Exception as e:
        logger.error(f"Error en métodos alternativos: {e}")

    # Método 2: Detectar GPUs usando comandos del sistema
    try:
        if platform.system() == "Windows":
            # En Windows, intentar usar wmic
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Saltar header
                for i, line in enumerate(lines):
                    if line.strip():
                        gpu_info = GPUInfo(
                            id=i,
                            name=line.strip(),
                            memory_total=0,  # No disponible
                            memory_used=0,
                            memory_free=0,
                            temperature=0,
                        )
                        gpus.append(gpu_info)

        elif platform.system() == "Linux":
            # En Linux, intentar usar lspci
            result = subprocess.run(
                ["lspci", "-v"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                gpu_lines = [
                    line
                    for line in result.stdout.split("\n")
                    if "VGA" in line or "3D" in line
                ]
                for i, line in enumerate(gpu_lines):
                    # Extraer nombre de GPU de la línea
                    match = re.search(r"\[([^\]]+)\]", line)
                    name = match.group(1) if match else line.split(":")[-1].strip()

                    gpu_info = GPUInfo(
                        id=i,
                        name=name,
                        memory_total=0,
                        memory_used=0,
                        memory_free=0,
                        temperature=0,
                    )
                    gpus.append(gpu_info)

    except Exception as e:
        logger.error(f"Error detectando GPUs con comandos del sistema: {e}")

    # Si no se encontraron GPUs, retornar una lista vacía
    if not gpus:
        logger.info("No se encontraron GPUs en el sistema")
        # Retornar al menos una GPU genérica para compatibilidad
        gpus.append(
            GPUInfo(
                id=0,
                name="GPU No Detectada",
                memory_total=0,
                memory_used=0,
                memory_free=0,
                temperature=0,
            )
        )

    return gpus


def getAvailable(limit=1, maxLoad=0.5, maxMemory=0.5):
    """Función compatible con GPUtil.getAvailable()."""
    try:
        import GPUtil

        return GPUtil.getAvailable(limit=limit, maxLoad=maxLoad, maxMemory=maxMemory)
    except:
        # Si GPUtil falla, retornar lista vacía
        return []


def getFirstAvailable():
    """Función compatible con GPUtil.getFirstAvailable()."""
    try:
        import GPUtil

        return GPUtil.getFirstAvailable()
    except:
        # Si GPUtil falla, retornar 0 (primera GPU)
        return 0


# Para compatibilidad con código existente
__version__ = "1.4.0 (BackendBot Compatible)"
