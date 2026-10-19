import sys
from PySide2.QtWidgets import QApplication, QDialog
from dialogs import LoginDialog
from chatbot_gui import ChatbotGUI
from db_helpers import init_db


if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    login = LoginDialog()
    
    if login.exec_() == QDialog.Accepted:
        gui = ChatbotGUI(usuario=login.usuario)
        gui.show()
        sys.exit(app.exec_())
        
    else:
        sys.exit()