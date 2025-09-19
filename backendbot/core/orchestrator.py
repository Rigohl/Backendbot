"""
System Orchestrator for BackendBot.
"""
from backendbot.bots.manager import BotManager
from backendbot.core.di.container import container

class Orchestrator:
    def __init__(self):
        self.logger = container.get_logger()
        config_manager = container.get_config_manager()
        if hasattr(config_manager, 'get_settings'):
            self.config = config_manager.get_settings()
        else:
            self.config = config_manager  # Asumir que ya es el objeto de configuración
        self.bot_manager = BotManager()
        # Initialize other components like Dashboard and API connections here

    def start(self):
        self.logger.info("Starting System Orchestrator...")
        # Start bot workers
        self.bot_manager.start_all_bots()
        self.logger.info("All bots started.")
        # Start other components

    def stop(self):
        self.logger.info("Stopping System Orchestrator...")
        # Stop bot workers
        self.bot_manager.stop_all_bots()
        self.logger.info("All bots stopped.")
        # Stop other components

    def get_system_status(self):
        # Aggregate status from all components
        status = {
            "bots": self.bot_manager.get_all_bot_status(),
            # "dashboard": self.dashboard.get_status(),
            # "api": self.api.get_status(),
        }
        return status
