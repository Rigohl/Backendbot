"""ChatBot - Bot conversacional que entiende lenguaje natural."""

import re
from backendbot.core.di.container import container


class ChatBot:
    """Bot de chat que entiende lenguaje natural y coordina otros bots."""

    def __init__(self) -> None:
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()

        # Patrones de lenguaje natural
        self.patterns = {
            # Búsqueda de archivos
            r'busca(?:me)?\s+(?:archivos?\s+)?duplicados?': ('indexer', 'find_duplicates'),
            r'busca(?:me)?\s+(?:archivos?\s+)?(?:que\s+)?no\s+(?:he\s+)?utilizado': ('auditor_files', 'scan_old'),
            r'busca(?:me)?\s+(?:archivos?\s+)?antiguos?': ('auditor_files', 'scan_old'),
            r'busca(?:me)?\s+(?:archivos?\s+)?grandes?': ('auditor_files', 'scan_large'),

            # Búsqueda de programas
            r'busca(?:me)?\s+programas?\s+(?:que\s+)?no\s+(?:uso|use)': ('auditor_programs', 'scan_unused'),
            r'busca(?:me)?\s+programas?\s+antiguos?': ('auditor_programs', 'scan_unused'),
            r'analiza(?:r)?\s+programas?': ('auditor_programs', 'analyze'),

            # Organización
            r'organiza(?:r)?\s+(?:mis\s+)?archivos?': ('organizer', 'organize'),
            r'ordena(?:r)?\s+(?:mis\s+)?archivos?': ('organizer', 'organize'),
            r'organiza(?:r)?\s+por\s+tipo': ('organizer', 'organize_by_type'),

            # Monitoreo
            r'(?:como\s+)?esta\s+el\s+sistema': ('monitor', 'status'),
            r'estado\s+del\s+sistema': ('monitor', 'status'),
            r'monitorea(?:r)?\s+sistema': ('monitor', 'monitor'),
            r'ver\s+(?:el\s+)?estado': ('monitor', 'status'),

            # Optimización
            r'optimiza(?:r)?\s+(?:el\s+)?sistema': ('optimizer', 'optimize'),
            r'limpia(?:r)?\s+memoria': ('optimizer', 'clean_memory'),
            r'optimiza(?:r)?\s+ram': ('optimizer', 'optimize_ram'),

            # Guardian
            r'verifica(?:r)?\s+seguridad': ('guardian', 'check_security'),
            r'chequea(?:r)?\s+sistema': ('guardian', 'check_system'),
            r'guardian\s+status': ('guardian', 'status'),

            # Indexer
            r'indexa(?:r)?\s+archivos?': ('indexer', 'index'),
            r'busca(?:r)?\s+(.+)': ('indexer', 'search'),
        }

    def execute(self, action: str) -> str:
        """Ejecutar acción del chat."""
        if action == "status":
            return "🤖 ChatBot operativo - Entiendo lenguaje natural"
        elif action == "help":
            return self._get_help()
        else:
            # Intentar interpretar como lenguaje natural
            return self._interpret_natural_language(action)

    def _interpret_natural_language(self, message: str) -> str:
        """Interpretar mensaje en lenguaje natural."""
        message = message.lower().strip()

        # Buscar patrones
        for pattern, (bot_name, action) in self.patterns.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                # Si es búsqueda, extraer el término
                if bot_name == 'indexer' and action == 'search' and match.groups():
                    search_term = match.group(1).strip()
                    return f"indexer search {search_term}"

                return f"{bot_name} {action}"

        # Si no se reconoce, dar sugerencias
        return self._get_suggestions(message)

    def _get_suggestions(self, message: str) -> str:
        """Obtener sugerencias para mensaje no reconocido."""
        suggestions = [
            "🤔 No entendí tu mensaje. Aquí van algunas sugerencias:",
            "",
            "📁 Para archivos:",
            "  • 'buscame archivos duplicados'",
            "  • 'buscame archivos que no he utilizado'",
            "  • 'organiza mis archivos'",
            "",
            "💻 Para programas:",
            "  • 'busca programas que no uso'",
            "  • 'analiza programas'",
            "",
            "📊 Para sistema:",
            "  • 'como esta el sistema'",
            "  • 'optimiza el sistema'",
            "  • 'verifica seguridad'",
            "",
            "💡 También puedes usar comandos directos como:",
            "  • 'monitor status'",
            "  • 'organizer organize'",
            "  • 'help' para más ayuda"
        ]

        return "\n".join(suggestions)

    def _get_help(self) -> str:
        """Obtener ayuda del chat."""
        return """
🤖 ChatBot - Entiendo lenguaje natural

💬 Puedo interpretar frases como:
• "buscame archivos duplicados"
• "buscame archivos que no he utilizado"
• "organiza mis archivos"
• "busca programas que no uso"
• "como esta el sistema"
• "optimiza el sistema"
• "verifica seguridad"

📋 Comandos directos disponibles:
• help - Esta ayuda
• status - Estado del chat

También coordino con todos los bots especializados.
        """

    def get_status(self) -> str:
        """Obtener estado del bot."""
        return "ChatBot operativo - Lenguaje natural activado"

    def is_available(self) -> bool:
        """Verificar si el bot está disponible."""
        return True