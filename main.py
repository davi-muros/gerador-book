import sys
from PyQt6.QtWidgets import QApplication
from ui.login import LoginWindow
from ui.main_window import DataBookApp

def abrir_sistema_principal():
    global main_window
    main_window = DataBookApp()
    main_window.show()
    login_window.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    login_window = LoginWindow(callback_antigo=abrir_sistema_principal)
    login_window.show()
    
    sys.exit(app.exec())