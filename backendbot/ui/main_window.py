"""
Main Window for BackendBot UI.
"""
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from .dashboard import BackendBotDashboard as Dashboard
from .chat_panel import ChatPanel
from .bots_panel import BotsPanel
from backendbot.core.orchestrator import Orchestrator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BackendBot Control Center")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Orchestrator
        self.orchestrator = Orchestrator()

        # Add tabs
        self.dashboard_tab = Dashboard()
        self.chat_tab = ChatPanel()
        self.bots_tab = BotsPanel(self.orchestrator)

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.chat_tab, "Chat")
        self.tabs.addTab(self.bots_tab, "Bots")

        # Connect to Orchestrator
        self.connect_to_orchestrator()

    def connect_to_orchestrator(self):
        # Logic to connect UI with the orchestrator
        # For example, update dashboard periodically
        from PyQt5.QtCore import QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(5000) # Update every 5 seconds

    def update_dashboard(self):
        status = self.orchestrator.get_system_status()
        # Update dashboard widgets with the new status
        # This is a placeholder for the actual implementation
        print(f"Updating dashboard with status: {status}")
