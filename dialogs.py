from PySide2.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox,
    QHBoxLayout
)
from db_helpers import registrar_usuario, autenticar_usuario, existe_admin

import bcrypt
import hashlib

def _preparar(password: str) -> bytes:
    """Convierte el password a 32 bytes fijos con SHA-256.
    Así bcrypt nunca trunca, sin importar el largo del password."""
    return hashlib.sha256(password.encode("utf-8")).digest()

class RegistroDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Registro de Usuario")
        self.resize(320, 150)

        layout = QVBoxLayout()

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Nombre de usuario")
        layout.addWidget(self.input_usuario)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contraseña")
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)

        self.btn_registrar = QPushButton("Registrar")
        self.btn_registrar.clicked.connect(self.registrar)
        layout.addWidget(self.btn_registrar)

        self.setLayout(layout)
        self.usuario = None


    def registrar(self):
        usuario = self.input_usuario.text().strip()
        password = self.input_password.text().strip()
        
        if not usuario or not password:
            QMessageBox.warning(self, "Campos vacíos", "Completa todos los campos.")
            return
            
            
        if not existe_admin():
            rol = "admin"
            info = "¡Este usuario será el administrador!"
            
        else:
            rol = "empleado"
            info = "Registrado como empleado."
        success = registrar_usuario(usuario, password, rol)
        
        
        if success:
            QMessageBox.information(self, "Éxito", f"Usuario registrado correctamente. {info}")
            self.accept()
            
        else:
            QMessageBox.warning(self, "Error", "Nombre de usuario ya existe.")
            


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Inicio de Sesión")
        self.resize(320, 140)

        layout = QVBoxLayout()

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Nombre de usuario")
        layout.addWidget(self.input_usuario)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contraseña")
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)

        btn_layout = QHBoxLayout()
        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.clicked.connect(self.login)
        btn_layout.addWidget(self.btn_login)

        self.btn_registro = QPushButton("Registrarse")
        self.btn_registro.clicked.connect(self.abrir_registro)
        btn_layout.addWidget(self.btn_registro)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.usuario = None


    def login(self):
        usuario = self.input_usuario.text().strip()
        password = self.input_password.text().strip()
        
        if not usuario or not password:
            QMessageBox.warning(self, "Campos vacíos", "Completa usuario y contraseña.")
            return
            
            
        user_data = autenticar_usuario(usuario, password)
        password_value = bcrypt.checkpw(_preparar(password), user_data['password_hash_bytes'])
        
        if user_data and password_value:
            self.usuario = user_data
            self.accept()
            
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")


    def abrir_registro(self):
        reg = RegistroDialog()
        
        if reg.exec_() == QDialog.Accepted:
            self.input_usuario.setText(reg.input_usuario.text())
            self.input_password.setText("")