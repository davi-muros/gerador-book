import os

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QMessageBox
from qfluentwidgets import FluentWindow, NavigationItemPosition, setTheme, Theme

from config import resource_path
from ui.dashboard import DashboardWidget
from ui.montagem import MontagemBookWidget

class DataBookApp(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataBook - Gerador Dinâmico v1.0")
        self.resize(1200, 800)
        setTheme(Theme.LIGHT)

        icon_path = resource_path("favicon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.dashboard = DashboardWidget(self)
        self.montagem = MontagemBookWidget(dashboard_ref=self.dashboard, parent=self)

        self.addSubInterface(self.dashboard, QIcon(), 'Dashboard', NavigationItemPosition.TOP)
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.montagem, QIcon(), 'Montagem do Book', NavigationItemPosition.TOP)
        
        tela_sair = QWidget(self)
        tela_sair.setObjectName("TelaSair")
        self.addSubInterface(tela_sair, QIcon(), 'Sair', NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        resposta = QMessageBox.question(
            self,
            "Sair do DataBook",
            "Deseja salvar o rascunho da montagem atual antes de fechar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )

        if resposta == QMessageBox.StandardButton.Yes:
            self.montagem.salvar_rascunho(notificar=False)
            event.accept()
        elif resposta == QMessageBox.StandardButton.No:
            event.accept()
        else:
            event.ignore()