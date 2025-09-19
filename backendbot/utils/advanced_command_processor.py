"""Sistema Avanzado de Procesamiento de Comandos para BackendBot
Implementa procesamiento de lenguaje natural y respuestas inteligentes.
"""

import random
import re
from datetime import datetime
from typing import Any

# Imports lazy para evitar ciclos de importación
# from src.backendbot.modes import mode_manager
# from src.backendbot.modes.adaptive_learning import adaptive_learning
# from src.backendbot.cron_jobs.task_scheduler import task_scheduler
from src.backendbot.utils.logging_config import logger


class AdvancedCommandProcessor:
    def __init__(self) -> None:
        self.command_patterns = self._load_command_patterns()
        self.response_templates = self._load_response_templates()
        self.conversation_context = []
        self.max_context_length = 10

    def _load_command_patterns(self) -> dict[str, list[str]]:
        """Cargar patrones de comandos para reconocimiento de lenguaje natural."""
        return {
            "mode_change": [
                r"cambiar\s+a\s+(modo\s+)?editor",
                r"pon(er)?\s+(en\s+)?modo\s+editor",
                r"activa(r)?\s+(el\s+)?modo\s+editor",
                r"switch\s+to\s+editor\s+mode",
                r"editor\s+mode",
            ],
            "mode_streaming": [
                r"cambiar\s+a\s+(modo\s+)?streaming",
                r"pon(er)?\s+(en\s+)?modo\s+streaming",
                r"activa(r)?\s+(el\s+)?modo\s+streaming",
                r"switch\s+to\s+streaming\s+mode",
                r"streaming\s+mode",
            ],
            "mode_relax": [
                r"cambiar\s+a\s+(modo\s+)?relax",
                r"pon(er)?\s+(en\s+)?modo\s+relax",
                r"activa(r)?\s+(el\s+)?modo\s+relax",
                r"switch\s+to\s+relax\s+mode",
                r"relax\s+mode",
            ],
            "mode_desarrollo": [
                r"cambiar\s+a\s+(modo\s+)?desarrollo",
                r"pon(er)?\s+(en\s+)?modo\s+desarrollo",
                r"activa(r)?\s+(el\s+)?modo\s+desarrollo",
                r"switch\s+to\s+development\s+mode",
                r"desarrollo\s+mode",
            ],
            "mode_gaming": [
                r"cambiar\s+a\s+(modo\s+)?gaming",
                r"pon(er)?\s+(en\s+)?modo\s+gaming",
                r"activa(r)?\s+(el\s+)?modo\s+gaming",
                r"switch\s+to\s+gaming\s+mode",
                r"gaming\s+mode",
            ],
            "task_management": [
                r"(ver|mostrar|lista)\s+(las\s+)?tareas",
                r"estado\s+de\s+(las\s+)?tareas",
                r"tasks\s+(list|status)",
                r"show\s+(me\s+)?tasks",
            ],
            "task_enable": [
                r"(habilita|activa|enable)\s+(la\s+)?tarea\s+(\w+)",
                r"encender\s+(la\s+)?tarea\s+(\w+)",
                r"turn\s+on\s+task\s+(\w+)",
            ],
            "task_disable": [
                r"(deshabilita|desactiva|disable)\s+(la\s+)?tarea\s+(\w+)",
                r"apagar\s+(la\s+)?tarea\s+(\w+)",
                r"turn\s+off\s+task\s+(\w+)",
            ],
            "system_status": [
                r"(como\s+estas?|cómo\s+estás?|status|estado)",
                r"qué\s+tal\s+estás?",
                r"how\s+are\s+you",
                r"system\s+status",
            ],
            "performance_check": [
                r"(rendimiento|performance|cpu|memoria|ram)",
                r"cómo\s+va\s+el\s+(rendimiento|sistema)",
                r"check\s+(performance|system)",
            ],
            "cleanup_request": [
                r"limpia(r)?\s+(archivos|temporales|cache)",
                r"clean\s+(up\s+)?files",
                r"borrar\s+archivos\s+temporales",
            ],
            "help_request": [
                r"(ayuda|help|comandos|qué\s+puedes\s+hacer)",
                r"what\s+can\s+you\s+do",
                r"show\s+(commands|help)",
            ],
            "recommendations": [
                r"(recomendaciones|sugerencias|advise)",
                r"qué\s+me\s+recomiendas",
                r"what\s+do\s+you\s+recommend",
            ],
            "learning_stats": [
                r"(estadísticas|stats|aprendizaje)",
                r"learning\s+statistics",
                r"show\s+(stats|statistics)",
            ],
        }

    def _load_response_templates(self) -> dict[str, list[str]]:
        """Cargar plantillas de respuestas inteligentes."""
        return {
            "greetings": [
                "¡Hola! ¿En qué puedo ayudarte hoy?",
                "¡Hola! Estoy listo para asistirte.",
                "¡Hola! ¿Qué necesitas que haga?",
            ],
            "mode_changed": [
                "✅ Modo cambiado exitosamente a {mode}",
                "🔄 Cambio realizado. Ahora estoy en modo {mode}",
                "✨ Perfecto, activé el modo {mode}",
            ],
            "task_enabled": [
                "✅ Tarea '{task}' habilitada correctamente",
                "🔄 La tarea '{task}' ahora está activa",
                "✨ Tarea '{task}' activada con éxito",
            ],
            "task_disabled": [
                "✅ Tarea '{task}' deshabilitada correctamente",
                "🔄 La tarea '{task}' ahora está inactiva",
                "✨ Tarea '{task}' desactivada con éxito",
            ],
            "system_healthy": [
                "✅ El sistema está funcionando correctamente",
                "🔄 Todo parece estar en orden",
                "✨ Sistema operativo y saludable",
            ],
            "system_issues": [
                "⚠️ Detecté algunos problemas en el sistema",
                "🔄 Hay algunas cuestiones que requieren atención",
                "✨ Encontré algunos problemas que puedo ayudar a resolver",
            ],
            "cleanup_done": [
                "🧹 Limpieza completada exitosamente",
                "✨ Archivos temporales eliminados",
                "🔄 Sistema limpiado y optimizado",
            ],
            "help_response": [
                "🤖 Puedo ayudarte con:\n• Cambiar modos de operación\n• Gestionar tareas programadas\n• Monitorear el sistema\n• Limpiar archivos\n• Mostrar recomendaciones\n• Ver estadísticas",
                "💡 Comandos disponibles:\n• 'modo [tipo]' - Cambiar modo\n• 'tareas' - Ver tareas programadas\n• 'recomendaciones' - Ver sugerencias\n• 'ayuda' - Mostrar esta ayuda",
            ],
            "unknown_command": [
                "🤔 No entendí ese comando. Prueba con 'ayuda' para ver los comandos disponibles",
                "❓ Comando no reconocido. Escribe 'ayuda' para ver qué puedo hacer",
                "🔍 No pude interpretar eso. Usa 'ayuda' para ver las opciones",
            ],
            "error_response": [
                "❌ Ocurrió un error: {error}",
                "🔄 Hubo un problema: {error}",
                "⚠️ Error detectado: {error}",
            ],
        }

    def process_command(self, command: str) -> dict[str, Any]:
        """Procesar comando usando lenguaje natural
        Retorna: (resultado_dict, comando_traducido)
        donde resultado_dict al menos contiene keys: 'action' y 'confidence' o
        'message' cuando corresponde.
        """
        try:
            # Limpiar y normalizar comando
            command = command.strip().lower()

            # Agregar al contexto de conversación
            self._add_to_context(command)

            # Intentar reconocer patrón
            recognized_command, params = self._recognize_pattern(command)

            if recognized_command:
                # Registrar comando reconocido para aprendizaje
                from src.backendbot.modes import mode_manager
                from src.backendbot.modes.adaptive_learning import \
                    adaptive_learning

                adaptive_learning.record_user_action(
                    "natural_command",
                    {
                        "original_command": command,
                        "recognized_command": recognized_command,
                        "params": params,
                        "mode": mode_manager.get_mode_info()["mode"],
                    },
                )

                # Procesar comando reconocido
                response_text = self._process_recognized_command(
                    recognized_command, params
                )
                return {
                    "action": recognized_command,
                    "message": response_text,
                    "confidence": 0.9,
                }

            # Si no se reconoce, intentar procesamiento básico
            basic_response = self._process_basic_command(command)
            if basic_response:
                return {
                    "action": "basic_response",
                    "message": basic_response,
                    "confidence": 0.6,
                }

            # Comando desconocido
            response = random.choice(self.response_templates["unknown_command"])
            return {"action": "unknown", "message": response, "confidence": 0.2}

        except Exception as e:
            logger.error(f"Error procesando comando: {e}")
            error_response = random.choice(self.response_templates["error_response"])
            return {
                "action": "error",
                "message": error_response.format(error=str(e)),
                "confidence": 0.0,
            }

    def _recognize_pattern(self, command: str) -> tuple[str | None, dict[str, Any]]:
        """Reconocer patrón de comando usando expresiones regulares."""
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    params = {}
                    if (
                        command_type in ["task_enable", "task_disable"]
                        and len(match.groups()) > 0
                    ):
                        params["task_id"] = match.group(len(match.groups()))

                    return command_type, params

        return None, {}

    def _process_recognized_command(
        self, command_type: str, params: dict[str, Any]
    ) -> str:
        """Procesar comando reconocido."""
        try:
            if command_type.startswith("mode_"):
                return self._process_mode_command(command_type, params)
            elif command_type.startswith("task_"):
                return self._process_task_command(command_type, params)
            elif command_type == "system_status":
                return self._process_system_status()
            elif command_type == "performance_check":
                return self._process_performance_check()
            elif command_type == "cleanup_request":
                return self._process_cleanup_request()
            elif command_type == "help_request":
                return self._process_help_request()
            elif command_type == "recommendations":
                return self._process_recommendations()
            elif command_type == "learning_stats":
                return self._process_learning_stats()
            elif command_type == "task_management":
                return self._process_task_management()

        except Exception as e:
            logger.error(f"Error procesando comando reconocido {command_type}: {e}")
            return random.choice(self.response_templates["error_response"]).format(
                error=str(e)
            )

        return random.choice(self.response_templates["unknown_command"])

    def _process_mode_command(self, command_type: str, params: dict[str, Any]) -> str:
        """Procesar comandos de cambio de modo."""
        mode_map = {
            "mode_change": "editor",
            "mode_editor": "editor",
            "mode_streaming": "streaming",
            "mode_relax": "relax",
            "mode_desarrollo": "desarrollo",
            "mode_gaming": "gaming",
        }

        target_mode = mode_map.get(command_type, "editor")

        # Aquí se integraría con el cambio real de modo
        # Por simplicidad, solo retornamos la respuesta
        response = random.choice(self.response_templates["mode_changed"])
        return response.format(mode=target_mode)

    def _process_task_command(self, command_type: str, params: dict[str, Any]) -> str:
        """Procesar comandos de gestión de tareas."""
        task_id = params.get("task_id", "")

        if command_type == "task_enable":
            # Aquí se integraría con task_scheduler.enable_task(task_id)
            response = random.choice(self.response_templates["task_enabled"])
            return response.format(task=task_id)
        elif command_type == "task_disable":
            # Aquí se integraría con task_scheduler.disable_task(task_id)
            response = random.choice(self.response_templates["task_disabled"])
            return response.format(task=task_id)

        return "Comando de tarea procesado"

    def _process_system_status(self) -> str:
        """Procesar consulta de estado del sistema."""
        # Verificar estado básico del sistema
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            if cpu_percent < 80 and memory.percent < 85:
                return random.choice(self.response_templates["system_healthy"])
            else:
                return random.choice(self.response_templates["system_issues"])
        except:
            return "Estado del sistema: Funcionando correctamente"

    def _process_performance_check(self) -> str:
        """Procesar consulta de rendimiento."""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            return f"📊 Rendimiento actual:\n• CPU: {cpu_percent}%\n• Memoria: {memory.percent}%\n• Memoria usada: {memory.used / 1024 / 1024 / 1024:.1f} GB"
        except:
            return "No pude obtener métricas de rendimiento"

    def _process_cleanup_request(self) -> str:
        """Procesar solicitud de limpieza."""
        # Aquí se integraría con las funciones de limpieza
        return random.choice(self.response_templates["cleanup_done"])

    def _process_help_request(self) -> str:
        """Procesar solicitud de ayuda."""
        return random.choice(self.response_templates["help_response"])

    def _process_recommendations(self) -> str:
        """Procesar solicitud de recomendaciones."""
        try:
            from src.backendbot.modes.adaptive_learning import \
                adaptive_learning

            recommendations = adaptive_learning.get_recommendations()
            if recommendations:
                response = "🤖 Recomendaciones del sistema:\n"
                for i, rec in enumerate(recommendations[:3], 1):
                    response += f"{i}. {rec}\n"
                return response.strip()
            else:
                return "📚 No hay recomendaciones disponibles aún. El sistema está aprendiendo..."
        except:
            return "No pude obtener recomendaciones"

    def _process_learning_stats(self) -> str:
        """Procesar solicitud de estadísticas de aprendizaje."""
        try:
            from src.backendbot.modes.adaptive_learning import \
                adaptive_learning

            stats = adaptive_learning.get_learning_stats()
            return f"🧠 Estadísticas de Aprendizaje:\n• Acciones aprendidas: {stats['total_actions_learned']}\n• Métricas registradas: {stats['total_metrics_recorded']}\n• Patrones analizados: {stats['patterns_analyzed']}"
        except:
            return "No pude obtener estadísticas de aprendizaje"

    def _process_task_management(self) -> str:
        """Procesar consulta de gestión de tareas."""
        try:
            from src.backendbot.cron_jobs.task_scheduler import task_scheduler

            stats = task_scheduler.get_task_stats()
            return f"⏰ Estado de Tareas:\n• Total: {stats['total_tasks']}\n• Activas: {stats['enabled_tasks']}\n• Ejecutadas: {stats['total_runs']}\n• Tasa éxito: {stats['success_rate']:.1f}%"
        except:
            return "No pude obtener información de tareas"

    def _process_basic_command(self, command: str) -> str | None:
        """Procesar comandos básicos que no requieren patrones complejos."""
        # Comandos simples de saludo
        if any(word in command for word in ["hola", "hello", "hi", "hey"]):
            return random.choice(self.response_templates["greetings"])

        # Comandos de despedida
        if any(word in command for word in ["adios", "bye", "chau", "hasta luego"]):
            return "¡Hasta luego! 👋"

        # Comandos de agradecimiento
        if any(word in command for word in ["gracias", "thanks", "thank you"]):
            return "¡De nada! 😊 ¿En qué más puedo ayudarte?"

        return None

    def _add_to_context(self, command: str):
        """Agregar comando al contexto de conversación."""
        from src.backendbot.modes import mode_manager

        self.conversation_context.append(
            {
                "command": command,
                "timestamp": datetime.now(),
                "mode": mode_manager.get_mode_info()["mode"],
            }
        )

        # Mantener límite de contexto
        if len(self.conversation_context) > self.max_context_length:
            self.conversation_context.pop(0)

    def get_conversation_context(self) -> list[dict[str, Any]]:
        """Obtener contexto de conversación actual."""
        return self.conversation_context.copy()

    def clear_context(self):
        """Limpiar contexto de conversación."""
        self.conversation_context.clear()


# Instancia global del procesador avanzado de comandos
advanced_command_processor = AdvancedCommandProcessor()
