from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from qfluentwidgets import LineEdit, PasswordLineEdit, PrimaryPushButton, PushButton, TitleLabel, SubtitleLabel
from config import SESSAO
import re

class LoginWindow(QWidget):
    login_sucesso = pyqtSignal()

    def __init__(self, callback_antigo=None, parent=None):
        if isinstance(callback_antigo, QWidget):
            parent = callback_antigo
            callback_antigo = None
            
        super().__init__(parent=parent)
        self.callback_antigo = callback_antigo
        
        self.setObjectName("LoginWindow")
        self.setStyleSheet("QWidget#LoginWindow { background-color: #ffffff; border-radius: 8px; }")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(15)

        lbl_titulo = TitleLabel("DataBook", self)
        lbl_titulo.setStyleSheet("color: #005bb5; font-weight: bold; font-size: 32px;")
        
        lbl_sub = SubtitleLabel("Acesso Restrito", self)
        lbl_sub.setStyleSheet("color: #7a7a7a; font-size: 16px;")

        self.input_login = LineEdit(self)
        self.input_login.setPlaceholderText("Usuário (ex: operador.nivel1)")
        
        self.input_senha = PasswordLineEdit(self)
        self.input_senha.setPlaceholderText("Senha")
        self.input_senha.returnPressed.connect(self.validar_login)

        self.btn_entrar = PrimaryPushButton("Entrar", self)
        self.btn_entrar.setStyleSheet("background-color: #005bb5; color: white; border-radius: 5px; padding: 8px;")
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.clicked.connect(self.validar_login)

        self.btn_cadastrar = PushButton("Solicitar Acesso", self)
        self.btn_cadastrar.setStyleSheet("background-color: #f0f0f0; color: #333333; border-radius: 5px; padding: 8px;")
        self.btn_cadastrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cadastrar.clicked.connect(self.solicitar_cadastro)

        self.layout.addWidget(lbl_titulo)
        self.layout.addWidget(lbl_sub)
        self.layout.addSpacing(20)
        
        self.layout.addWidget(SubtitleLabel("Login", self))
        self.layout.addWidget(self.input_login)
        
        self.layout.addWidget(SubtitleLabel("Senha", self))
        self.layout.addWidget(self.input_senha)
        self.layout.addSpacing(15)
        
        self.layout.addWidget(self.btn_entrar)
        self.layout.addWidget(self.btn_cadastrar)
        self.layout.addStretch(1)

    def validar_login(self):
        raw_user = self.input_login.text().strip().lower()
        usuario = re.sub(r'[^a-z0-9.]', '', raw_user)
        senha = self.input_senha.text().strip()

        if not usuario or not senha:
            QMessageBox.warning(self, "Aviso", "Preencha o login e a senha.")
            return

        if senha == "ADMIN123":
            SESSAO["usuario"] = usuario
            self.login_sucesso.emit()
            if callable(self.callback_antigo):
                self.callback_antigo()
        else:
            QMessageBox.warning(self, "Erro", "Senha incorreta. Acesso negado.")
            
    def solicitar_cadastro(self):
        QMessageBox.information(self, "Cadastro", "Para novos perfis e acessos, entre em contato com o administrador do sistema.")