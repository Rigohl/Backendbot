"""
Panel flotante tipo chat para BackendBot usando PyQt5.
Permite mostrar mensajes, notificaciones y recibir comandos.
"""
from PyQt5 import QtWidgets, QtCore

class FloatingPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BackendBot - Panel de Reportes")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.resize(400, 300)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.text_area = QtWidgets.QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.input_line = QtWidgets.QLineEdit(self)
        self.input_line.returnPressed.connect(self.send_command)
        self.layout.addWidget(self.text_area)
        self.layout.addWidget(self.input_line)

    def show_message(self, msg: str):
        self.text_area.append(msg)

    def send_command(self):
        cmd = self.input_line.text()
        self.text_area.append(f"<b>&gt; {cmd}</b>")
        self.input_line.clear()
        # Aquí se integrará el procesamiento real del comando

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    panel = FloatingPanel()
    panel.show()
    app.exec_()
