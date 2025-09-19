"""
ChatPanel - Panel flotante de chat para BackendBot
Interfaz simple para comandos y respuestas.
"""

import os
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

# Añadir path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.backendbot.core.di.container import container
from src.backendbot.bots.manager import BotManager


class ChatPanel(QtWidgets.QWidget):
    """Panel flotante tipo chat para interactuar con BackendBot"""

    # Señales para comunicar con otros componentes
    command_signal = pyqtSignal(str)  # Señal cuando se envía un comando

    def __init__(self):
        super().__init__()

        # Inicializar dependencias
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.data_repo = container.get_data_repository()
        self.bot_manager = BotManager()

        # Configuración de ventana
        self.setWindowTitle("🤖 BackendBot - Chat")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.resize(500, 400)
        self.setMinimumSize(400, 300)

        # Layout principal
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Área de mensajes (solo lectura)
        self.message_area = QtWidgets.QTextEdit(self)
        self.message_area.setReadOnly(True)
        self.message_area.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.message_area)

        # Layout para input y botón
        input_layout = QtWidgets.QHBoxLayout()

        # Campo de entrada de comandos
        self.input_field = QtWidgets.QLineEdit(self)
        self.input_field.setPlaceholderText("Escribe un comando... (help para ayuda)")
        self.input_field.returnPressed.connect(self._send_command)
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        input_layout.addWidget(self.input_field)

        # Botón enviar
        self.send_button = QtWidgets.QPushButton("Enviar", self)
        self.send_button.clicked.connect(self._send_command)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Mensaje de bienvenida
        self.add_message("BackendBot", "¡Hola! Soy BackendBot, tu asistente de escritorio. Escribe 'help' para ver comandos disponibles.")

        # Log de inicialización
        self.logger.info("ChatPanel inicializado correctamente", "ChatPanel")

    def add_message(self, sender: str, message: str):
        """
        Agregar mensaje al área de chat

        Args:
            sender: Nombre del remitente
            message: Contenido del mensaje
        """
        try:
            # Formatear mensaje con timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Colores por remitente
            if sender == "BackendBot":
                color = "#007bff"  # Azul
            elif sender == "Error":
                color = "#dc3545"  # Rojo
            else:
                color = "#28a745"  # Verde

            # HTML para el mensaje
            html_message = f"""
            <div style="margin: 5px 0;">
                <span style="color: {color}; font-weight: bold;">[{timestamp}] {sender}:</span>
                <span style="color: #333;">{message}</span>
            </div>
            """

            # Agregar al área de texto
            self.message_area.append(html_message)

            # Auto-scroll al final
            scrollbar = self.message_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

            # Log del mensaje
            self.logger.debug(f"Mensaje agregado: {sender}: {message[:50]}...", "ChatPanel")

        except Exception as e:
            self.logger.error(f"Error agregando mensaje: {str(e)}", "ChatPanel")

    def _send_command(self):
        """Enviar comando cuando se presiona Enter o el botón"""
        try:
            command = self.input_field.text().strip()

            if not command:
                return

            # Mostrar comando del usuario
            self.add_message("Tú", command)

            # Limpiar campo de entrada
            self.input_field.clear()

            # Procesar comando con el BotManager
            response = self._process_command(command)

            # Mostrar respuesta
            self.add_message("BackendBot", response)

            # Emitir señal con el comando
            self.command_signal.emit(command)

            # Log del comando procesado
            self.logger.info(f"Comando procesado: {command}", "ChatPanel")

        except Exception as e:
            error_msg = f"Error procesando comando: {str(e)}"
            self.add_message("Error", error_msg)
            self.logger.error(error_msg, "ChatPanel")

    def _process_command(self, command: str) -> str:
        """
        Procesar comando usando el BotManager

        Args:
            command: Comando del usuario

        Returns:
            Respuesta del sistema
        """
        try:
            # Delegar al BotManager
            response = self.bot_manager.process_command(command)

            # Guardar comando en el repositorio
            self.data_repo.save_system_event(
                level="INFO",
                source="ChatPanel",
                message=f"Comando procesado: {command}",
                details=f"Respuesta: {response[:100]}..."
            )

            return response

        except Exception as e:
            error_msg = f"Error interno: {str(e)}"
            self.logger.error(error_msg, "ChatPanel")

            # Guardar error en el repositorio
            self.data_repo.save_system_event(
                level="ERROR",
                source="ChatPanel",
                message=error_msg,
                details=str(e)
            )

            return error_msg

    def show(self):
        """Mostrar el panel"""
        try:
            super().show()
            self.raise_()  # Traer al frente
            self.activateWindow()  # Activar ventana

            self.logger.debug("ChatPanel mostrado", "ChatPanel")

        except Exception as e:
            self.logger.error(f"Error mostrando ChatPanel: {str(e)}", "ChatPanel")

    def closeEvent(self, event):
        """Evento al cerrar la ventana - solo ocultar, no cerrar"""
        try:
            event.ignore()
            self.hide()

            self.logger.debug("ChatPanel ocultado", "ChatPanel")

        except Exception as e:
            self.logger.error(f"Error en closeEvent: {str(e)}", "ChatPanel")


if __name__ == "__main__":
    """Para testing independiente"""
    import sys
    app = QtWidgets.QApplication(sys.argv)

    panel = ChatPanel()
    panel.show()

    sys.exit(app.exec_())