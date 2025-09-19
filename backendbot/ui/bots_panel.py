"""
Bots Panel for BackendBot UI.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QMessageBox

class BotsPanel(QWidget):
    def __init__(self, orchestrator):
        super().__init__()
        self.orchestrator = orchestrator
        self.layout = QVBoxLayout(self)

        self.bot_list = QListWidget()
        self.layout.addWidget(self.bot_list)

        self.start_button = QPushButton("Start Bot")
        self.start_button.clicked.connect(self.start_bot)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Bot")
        self.stop_button.clicked.connect(self.stop_bot)
        self.layout.addWidget(self.stop_button)

        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.refresh_bot_list)
        self.layout.addWidget(self.refresh_button)

        self.refresh_bot_list()

    def refresh_bot_list(self):
        self.bot_list.clear()
        bots = self.orchestrator.get_system_status()['bots']
        for bot_name, bot_status in bots.items():
            self.bot_list.addItem(f"{bot_name} - {bot_status}")

    def get_selected_bot(self):
        selected_items = self.bot_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Bot Selected", "Please select a bot from the list.")
            return None
        return selected_items[0].text().split(" - ")[0]

    def start_bot(self):
        bot_name = self.get_selected_bot()
        if bot_name:
            self.orchestrator.bot_manager.get_bot(bot_name).start()
            self.refresh_bot_list()

    def stop_bot(self):
        bot_name = self.get_selected_bot()
        if bot_name:
            self.orchestrator.bot_manager.get_bot(bot_name).stop()
            self.refresh_bot_list()
