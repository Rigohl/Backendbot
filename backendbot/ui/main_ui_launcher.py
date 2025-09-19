"""Lanzador principal de BackendBot: inicia la UI y el Bot Monitor conectado a la UI."""

import logging
import traceback

from src.backendbot.bots.bot_auditor_files_ui import BotAuditorFilesUI
from src.backendbot.bots.bot_auditor_programs_ui import BotAuditorProgramsUI
from src.backendbot.bots.bot_guardian_ui import BotGuardianUI
from src.backendbot.bots.bot_indexer_ui import BotIndexerUI
from src.backendbot.bots.bot_monitor_ui import BotMonitorUI
from src.backendbot.bots.bot_optimizer_ui import BotOptimizerUI
from src.backendbot.bots.bot_organizer_ui import BotOrganizerUI
from src.backendbot.bots.bot_ui_connector import BotUIConnector
from src.backendbot.cron_jobs.task_scheduler import task_scheduler
from src.backendbot.modes import mode_manager
from src.backendbot.ui.bot_bridge import BotBridge
from src.backendbot.ui.main_ui import BackendBotUI


def main():
    logging.basicConfig(
        filename="backendbot_error.log",
        level=logging.ERROR,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    try:
        bridge = BotBridge()
        connector = BotUIConnector(bridge)

        # Inicializar bots con configuración de modo
        bots = [
            BotMonitorUI(connector),
            BotOrganizerUI(connector),
            BotIndexerUI(connector),
            BotAuditorFilesUI(connector),
            BotAuditorProgramsUI(connector),
            BotOptimizerUI(connector),
        ]

        # Configurar guardian con referencia al mode_manager
        guardian = BotGuardianUI(connector, bots)

        # Inicializar UI con integración de modos
        ui = BackendBotUI()

        # Inicializar sistema de tareas programadas
        task_scheduler.start_scheduler()

        # Mostrar información inicial del modo
        mode_info = mode_manager.get_mode_info()
        ui.panel.show_message(
            f"Modo inicial: {mode_info['mode'].capitalize()} - {mode_info['description']}"
        )
        ui.panel.show_message("Sistema de tareas programadas iniciado")

        ui.run()

    except Exception as e:
        logging.error("Excepción no controlada:\n%s", traceback.format_exc())
        from PyQt5.QtWidgets import QApplication, QMessageBox

        app = QApplication([])
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error en BackendBot")
        msg.setText(
            "Ocurrió un error crítico. Revisa backendbot_error.log para más detalles."
        )
        msg.setDetailedText(str(e))
        msg.exec_()
    finally:
        # Detener sistema de tareas programadas
        task_scheduler.stop_scheduler()

        for bot in locals().get("bots", []):
            bot.stop()
        if "guardian" in locals():
            guardian.stop()
        if "connector" in locals():
            connector.stop()
        if "bridge" in locals():
            bridge.stop()


if __name__ == "__main__":
    main()
