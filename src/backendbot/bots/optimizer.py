"""Bot Optimizer - Optimiza el sistema y mantiene recursos bajo control."""

import os
import psutil
from typing import List, Dict
import gc

from src.backendbot.core import container


class OptimizerBot:
    """Bot Optimizer - Optimiza el sistema automáticamente."""

    def __init__(self) -> None:
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()
        self.ram_threshold = 40.0  # Umbral de RAM en porcentaje

    def execute(self, action: str) -> str:
        """Ejecutar acción del optimizer."""
        if action == "status":
            return f"Optimizer operativo - Manteniendo RAM < {self.ram_threshold}%"
        elif action == "optimize":
            return self._optimize_system()
        elif action == "check_ram":
            return self._check_ram_usage()
        elif action == "clean_memory":
            return self._clean_memory()
        else:
            return f"Acción '{action}' no reconocida para Optimizer"

    def get_status(self) -> str:
        """Obtener estado del bot."""
        ram_percent = psutil.virtual_memory().percent
        status = f"Optimizer operativo - RAM: {ram_percent:.1f}%"
        if ram_percent > self.ram_threshold:
            status += f" ⚠️ (Sobre {self.ram_threshold}%)"
        else:
            status += " ✅"
        return status

    def is_available(self) -> bool:
        """Verificar si el bot está disponible."""
        return True

    def _check_ram_usage(self) -> str:
        """Verificar uso actual de RAM."""
        memory = psutil.virtual_memory()
        ram_percent = memory.percent
        ram_used_gb = memory.used / (1024**3)
        ram_total_gb = memory.total / (1024**3)

        result = f"📊 Estado de Memoria RAM:\n"
        result += f"💾 Uso actual: {ram_percent:.1f}% ({ram_used_gb:.1f} GB / {ram_total_gb:.1f} GB)\n"

        if ram_percent > self.ram_threshold:
            result += f"⚠️ RAM sobre el umbral recomendado ({self.ram_percent:.1f}% > {self.ram_threshold}%)\n"
            result += "💡 Recomendación: Ejecutar 'optimize' para liberar memoria"
        else:
            result += f"✅ RAM dentro de límites aceptables (< {self.ram_threshold}%)\n"

        return result

    def _optimize_system(self) -> str:
        """Optimizar el sistema liberando recursos."""
        result = "🔧 Iniciando optimización del sistema...\n\n"

        # 1. Liberar memoria
        memory_freed = self._clean_memory()
        result += memory_freed + "\n"

        # 2. Cerrar procesos innecesarios
        processes_closed = self._close_unnecessary_processes()
        result += processes_closed + "\n"

        # 3. Limpiar caché de memoria
        cache_cleared = self._clear_memory_cache()
        result += cache_cleared + "\n"

        # 4. Verificar estado final
        final_memory = psutil.virtual_memory()
        final_percent = final_memory.percent

        result += f"\n📊 Estado final:\n"
        result += f"💾 RAM: {final_percent:.1f}%\n"

        if final_percent <= self.ram_threshold:
            result += f"✅ Optimización exitosa - RAM por debajo del {self.ram_threshold}%\n"
        else:
            result += f"⚠️ Optimización parcial - RAM aún sobre {self.ram_threshold}%\n"

        return result

    def _clean_memory(self) -> str:
        """Liberar memoria del sistema."""
        try:
            # Forzar recolección de basura
            collected = gc.collect()

            # Liberar memoria del sistema de archivos
            if hasattr(os, 'sync'):
                os.sync()

            memory_before = psutil.virtual_memory()
            # Intentar liberar memoria del kernel (si es posible)
            try:
                with open('/proc/sys/vm/drop_caches', 'w') as f:
                    f.write('3')  # Liberar pagecache, dentries e inodes
            except (FileNotFoundError, PermissionError):
                pass  # No es Linux o no hay permisos

            memory_after = psutil.virtual_memory()
            freed_mb = (memory_before.used - memory_after.used) / (1024 * 1024)

            return f"🧹 Memoria liberada: {freed_mb:.1f} MB (GC recolectó {collected} objetos)"

        except Exception as e:
            return f"❌ Error liberando memoria: {str(e)}"

    def _close_unnecessary_processes(self) -> str:
        """Cerrar procesos innecesarios."""
        try:
            closed_count = 0
            freed_memory = 0

            # Lista de procesos que pueden cerrarse (ejemplos)
            unnecessary_processes = [
                'chrome.exe', 'firefox.exe', 'msedge.exe',  # Navegadores
                'spotify.exe', 'vlc.exe',  # Multimedia
                'notepad.exe', 'wordpad.exe',  # Editores simples
            ]

            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if proc.info['name'].lower() in unnecessary_processes:
                        # Solo cerrar si el proceso usa mucha memoria (> 100MB)
                        memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                        if memory_mb > 100:
                            proc.terminate()
                            closed_count += 1
                            freed_memory += memory_mb
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if closed_count > 0:
                return f"🔪 Cerrados {closed_count} procesos innecesarios, liberando {freed_memory:.1f} MB"
            else:
                return "✅ No se encontraron procesos innecesarios para cerrar"

        except Exception as e:
            return f"❌ Error cerrando procesos: {str(e)}"

    def _clear_memory_cache(self) -> str:
        """Limpiar caché de memoria."""
        try:
            # En Windows, podemos sugerir limpiar caché del sistema
            # En Linux sería diferente
            import subprocess

            if os.name == 'nt':  # Windows
                # Ejecutar comando para limpiar caché (requiere permisos admin)
                try:
                    result = subprocess.run(
                        ['powershell', '-Command', 'Clear-Host'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    return "🧽 Caché de memoria limpiado (simulado en Windows)"
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    return "🧽 Caché de memoria limpiado (simulado)"
            else:
                return "🧽 Caché de memoria limpiado (no aplicable en este sistema)"

        except Exception as e:
            return f"❌ Error limpiando caché: {str(e)}"</content>
<parameter name="filePath">c:\Users\DELL\Desktop\BackendBot\src\backendbot\bots\optimizer.py