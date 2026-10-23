import os
from PySide2.QtWidgets import (
	QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextBrowser,
	QTabWidget, QHBoxLayout, QTextEdit, QLabel, QScrollArea
)
from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QPixmap
from config import OPENAI_API_KEY, OPENAI_BASE_URL, LOGO_PATH, LOGO_PATH_EDIT, LOGO_PATH_SAVE, LOGO_PATH_SUGE
import openai
from admin_actions import AdminActionsMixin
from chat_actions import ChatActionsMixin



class ChatbotGUI(ChatActionsMixin, AdminActionsMixin, QWidget):
	def __init__(self, usuario):
		super().__init__()
		self.setWindowTitle("Sistema Administrativo")
		self.setGeometry(40, 40, 800, 480)
		self.pregunta_actual_editable = None
		self.respuesta_actual_editable = None
		self.usuario = usuario
		self.openai_client = openai.OpenAI(
			api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL,
			timeout=30.0,
		)
		self.init_ui()
		self.timer = QTimer()
		self.timer.timeout.connect(self.update_advertencia_btn)
		self.timer.start(2000)


	def fuente(self, var, font_size=10):
		var.setStyleSheet(f"font-size: {font_size}px; font-family: 'Times New Roman';")


	def init_ui(self):
		self.tabWidget = QTabWidget(self)

		self.tabWidget.setStyleSheet("""
			QTabBar::tab {
				font-size: 12px;
				font-family: 'Times New Roman';
				padding: 6px 12px;
			}
			QTabBar::tab:selected {
				font-weight: bold;
			}
		""")
		
		if self.usuario['rol'] != 'admin':
			self.init_chat_tab()
			self.init_sugerir_tab()
			
		else:
			self.init_chat_tab()
			self.init_edit_tab()
			self.init_admin_tab()
			self.init_sugerir_tab()


		main_layout = QVBoxLayout(self)
		main_layout.addWidget(self.tabWidget)
		self.setLayout(main_layout)
		self.tabWidget.setCurrentWidget(self.chat_tab)


	def init_chat_tab(self):
		self.chat_tab = QWidget()
		self.chat_layout_principal = QHBoxLayout(self.chat_tab)

		# Panel de sugerencias (izquierda)
		self.sugerencias_layout = QVBoxLayout()
		self.sugerencias_label = QLabel("🤖 Sugerencias:")
		self.fuente(self.sugerencias_label, 13)
		self.sugerencias_layout.addWidget(self.sugerencias_label)

		self.sugerencias_panel = QWidget()
		self.sugerencias_panel_layout = QVBoxLayout()
		self.sugerencias_panel.setLayout(self.sugerencias_panel_layout)

		self.sugerencias_scroll = QScrollArea()
		self.sugerencias_scroll.setWidgetResizable(True)
		self.sugerencias_scroll.setWidget(self.sugerencias_panel)
		self.sugerencias_layout.addWidget(self.sugerencias_scroll)

		self.chat_layout_principal.addLayout(self.sugerencias_layout, 1)

		# Panel central (chat)
		self.chat_layout = QVBoxLayout()

		self.boton_advertencia = QPushButton("⚠ Ver preguntas no resueltas")
		self.boton_advertencia.setStyleSheet("color: red; font-weight: bold; font-family: 'Times New Roman'; font-size: 11px;")
		self.boton_advertencia.setFixedSize(220, 32)
		self.boton_advertencia.clicked.connect(self.mostrar_no_resueltas)
		self.boton_advertencia.setVisible(False)
		self.chat_layout.addWidget(self.boton_advertencia, alignment=Qt.AlignRight)

		self.area_chat = QTextBrowser()
		self.area_chat.setFixedHeight(240)
		self.area_chat.setStyleSheet("font-size: 13px; font-family: 'Times New Roman';")
		self.chat_layout.addWidget(self.area_chat)
		
		self.boton_editar_respuesta = QPushButton("✏️ Editar esta respuesta")
		self.fuente(self.boton_editar_respuesta, 11)
		self.boton_editar_respuesta.clicked.connect(self.abrir_pestana_editar)
		self.boton_editar_respuesta.setVisible(False)
		self.chat_layout.addWidget(self.boton_editar_respuesta, alignment=Qt.AlignRight)

		# ---- Botones en una fila, campo de texto de sugerencias debajo ----
		self.entrada_layout = QHBoxLayout()
		self.boton_buscar = QPushButton("Buscar")
		self.boton_buscar.setFixedWidth(80)
		self.fuente(self.boton_buscar, 11)
		self.boton_buscar.clicked.connect(self.buscar_sugerencias)
		self.entrada_layout.addWidget(self.boton_buscar)

		self.boton_aleatorias = QPushButton("Dame sugerencias")
		self.boton_aleatorias.setFixedWidth(170)
		self.fuente(self.boton_aleatorias, 11)
		self.boton_aleatorias.clicked.connect(self.mostrar_sugerencias_aleatorias)
		self.entrada_layout.addWidget(self.boton_aleatorias)

		self.boton_limpiar = QPushButton("Limpiar chat")
		self.boton_limpiar.setFixedWidth(110)
		self.fuente(self.boton_limpiar, 11)
		self.boton_limpiar.clicked.connect(self.limpiar_pantalla)
		self.entrada_layout.addWidget(self.boton_limpiar)

		# Campo de texto debajo de los botones (para sugerencias)
		self.entrada_usuario = QLineEdit()
		self.entrada_usuario.setPlaceholderText("Escribe una palabra clave para buscar preguntas…")
		self.entrada_usuario.setFixedHeight(32)
		self.entrada_usuario.setStyleSheet("font-size: 12px; font-family: 'Times New Roman';")

		# Layout horizontal para el campo de la IA y su botón
		self.ia_layout = QHBoxLayout()
		self.ia_input = QLineEdit()
		self.ia_input.setPlaceholderText("Pregúntale algo a la IA...")
		self.ia_input.setFixedHeight(32)
		self.ia_input.setStyleSheet("font-size: 12px; font-family: 'Times New Roman';")
		self.ia_layout.addWidget(self.ia_input)

		self.boton_enviar_ia = QPushButton("Enviar a IA")
		self.boton_enviar_ia.setFixedWidth(100)
		self.fuente(self.boton_enviar_ia, 11)
		self.boton_enviar_ia.clicked.connect(self.enviar_a_ia)
		self.ia_layout.addWidget(self.boton_enviar_ia)

		# Layout vertical: botones, campo de sugerencias y luego campo de la IA
		self.entrada_vertical_layout = QVBoxLayout()
		self.entrada_vertical_layout.addLayout(self.entrada_layout)
		self.entrada_vertical_layout.addWidget(self.entrada_usuario)
		self.entrada_vertical_layout.addLayout(self.ia_layout)

		self.chat_layout.addLayout(self.entrada_vertical_layout)

		self.chat_layout_principal.addLayout(self.chat_layout, 3)

		# Logo (derecha) + botón de sugerir preguntas
		self.logo_layout = QVBoxLayout()
		self.label_imagen = QLabel()
		
		if os.path.exists(LOGO_PATH):
			self.label_imagen.setPixmap(QPixmap(LOGO_PATH))


		self.label_imagen.setScaledContents(True)
		self.label_imagen.setFixedSize(150, 150)
		self.logo_layout.addWidget(self.label_imagen, alignment=Qt.AlignCenter)

		self.boton_sugerir = QPushButton("Sugerir pregunta/respuesta")
		self.fuente(self.boton_sugerir, 11)
		self.boton_sugerir.clicked.connect(self.abrir_tab_sugerir)
		self.logo_layout.addWidget(self.boton_sugerir, alignment=Qt.AlignCenter)

		self.logo_layout.addStretch()
		self.chat_layout_principal.addLayout(self.logo_layout, 1)
		self.tabWidget.insertTab(0, self.chat_tab, "Chat")


	def init_sugerir_tab(self):
		self.sugerir_tab = QWidget()
		main_layout = QHBoxLayout()
		form_layout = QVBoxLayout()

		label = QLabel("Sugiere una nueva pregunta y respuesta que creas que falta")
		self.fuente(label, 12)
		form_layout.addWidget(label)

		self.sugerir_pregunta = QLineEdit()
		self.sugerir_pregunta.setPlaceholderText("Pregunta sugerida")
		self.fuente(self.sugerir_pregunta, 11)
		form_layout.addWidget(self.sugerir_pregunta)

		self.sugerir_respuesta = QTextEdit()
		self.sugerir_respuesta.setPlaceholderText("Respuesta sugerida")
		self.sugerir_respuesta.setFixedHeight(80)
		self.sugerir_respuesta.setStyleSheet("font-size: 12px; font-family: 'Times New Roman';")
		form_layout.addWidget(self.sugerir_respuesta)

		self.boton_guardar_sugerencia = QPushButton("Guardar sugerencia")
		self.fuente(self.boton_guardar_sugerencia, 11)
		self.boton_guardar_sugerencia.clicked.connect(self.guardar_sugerencia_usuario)
		form_layout.addWidget(self.boton_guardar_sugerencia)

		self.boton_volver_chat = QPushButton("Volver al Chat")
		self.fuente(self.boton_volver_chat, 11)
		self.boton_volver_chat.clicked.connect(lambda: self.tabWidget.setCurrentWidget(self.chat_tab))
		form_layout.addWidget(self.boton_volver_chat)

		main_layout.addLayout(form_layout)

		# Logo a la derecha (igual que Editar y Agregar)
		logo_layout = QVBoxLayout()
		self.sugerir_logo = QLabel()
		
		if os.path.exists(LOGO_PATH_SUGE):
			self.sugerir_logo.setPixmap(QPixmap(LOGO_PATH_SUGE))
			
			
		self.sugerir_logo.setScaledContents(True)
		self.sugerir_logo.setFixedSize(200, 200)
		logo_layout.addStretch()
		logo_layout.addWidget(self.sugerir_logo)
		logo_layout.addStretch()
		main_layout.addLayout(logo_layout)

		self.sugerir_tab.setLayout(main_layout)
		self.tabWidget.insertTab(1, self.sugerir_tab, "Sugerir Pregunta/Respuesta")


	def abrir_tab_sugerir(self):
		self.tabWidget.setCurrentWidget(self.sugerir_tab)
		#self.ver_mas_btn.setVisible(fin < len(sugerencias))


	def init_edit_tab(self):
		self.editar_tab = QWidget()
		self.editar_layout_principal = QHBoxLayout()
		self.editar_layout = QVBoxLayout()
		self.editar_logo_layout = QVBoxLayout()
		self.edit_pregunta = QLineEdit(self)
		self.edit_pregunta.setPlaceholderText("Editar pregunta")
		self.edit_pregunta.setFixedWidth(350)
		self.edit_pregunta.setAlignment(Qt.AlignCenter)
		self.fuente(self.edit_pregunta, 12)
		self.editar_layout.addWidget(self.edit_pregunta)
		self.edit_respuesta = QTextEdit(self)
		self.edit_respuesta.setPlaceholderText("Editar respuesta")
		self.edit_respuesta.setFixedWidth(350)
		self.edit_respuesta.setFixedHeight(80)
		self.edit_respuesta.setAlignment(Qt.AlignLeft)
		self.edit_respuesta.setContentsMargins(10, 0, 0, 0)
		self.edit_respuesta.setStyleSheet("font-size: 12px; font-family: 'Times New Roman';")
		self.editar_layout.addWidget(self.edit_respuesta)
		self.boton_guardar_edicion = QPushButton("Guardar cambios", self)
		self.boton_guardar_edicion.setFixedSize(170, 32)
		self.fuente(self.boton_guardar_edicion, 11)
		self.boton_guardar_edicion.clicked.connect(self.guardar_cambios_edicion)
		self.editar_layout.addWidget(self.boton_guardar_edicion)
		self.boton_volver_editar = QPushButton("Volver al Chat", self)
		self.boton_volver_editar.setFixedSize(170, 32)
		self.fuente(self.boton_volver_editar, 11)
		self.boton_volver_editar.clicked.connect(lambda: self.tabWidget.setCurrentWidget(self.chat_tab))
		self.editar_layout.addWidget(self.boton_volver_editar)
		self.editar_layout_principal.addLayout(self.editar_layout)
		self.editar_logo = QLabel()
		
		if os.path.exists(LOGO_PATH_EDIT):
			self.editar_logo.setPixmap(QPixmap(LOGO_PATH_EDIT))
			
			
		self.editar_logo.setScaledContents(True)
		self.editar_logo.setFixedSize(200, 200)
		self.editar_logo_layout.addStretch()
		self.editar_logo_layout.addWidget(self.editar_logo)
		self.editar_logo_layout.addStretch()
		self.editar_layout_principal.addLayout(self.editar_logo_layout)
		self.editar_tab.setLayout(self.editar_layout_principal)
		self.tabWidget.insertTab(2, self.editar_tab, "Editar Pregunta/Respuesta")


	def init_admin_tab(self):
		self.admin_tab = QWidget()
		self.admin_layout_principal = QHBoxLayout()
		self.admin_layout = QVBoxLayout()
		self.admin_logo_layout = QVBoxLayout()
		self.agregar_pregunta = QLineEdit(self)
		self.agregar_pregunta.setPlaceholderText("Nueva pregunta")
		self.agregar_pregunta.setFixedWidth(350)
		self.agregar_pregunta.setAlignment(Qt.AlignCenter)
		self.fuente(self.agregar_pregunta, 12)
		self.admin_layout.addWidget(self.agregar_pregunta)
		self.agregar_respuesta = QTextEdit(self)
		self.agregar_respuesta.setPlaceholderText("Respuesta")
		self.agregar_respuesta.setFixedWidth(350)
		self.agregar_respuesta.setFixedHeight(80)
		self.agregar_respuesta.setAlignment(Qt.AlignLeft)
		self.agregar_respuesta.setContentsMargins(10, 0, 0, 0)
		self.agregar_respuesta.setStyleSheet("font-size: 12px; font-family: 'Times New Roman';")
		self.admin_layout.addWidget(self.agregar_respuesta)
		self.boton_agregar = QPushButton("Agregar")
		self.boton_agregar.setFixedSize(110, 32)
		self.fuente(self.boton_agregar, 11)
		self.boton_agregar.clicked.connect(self.agregar_pregunta_respuesta)
		self.admin_layout.addWidget(self.boton_agregar)
		self.boton_volver = QPushButton("Volver al Chat")
		self.boton_volver.setFixedSize(110, 32)
		self.fuente(self.boton_volver, 11)
		self.boton_volver.clicked.connect(lambda: self.tabWidget.setCurrentWidget(self.chat_tab))
		self.admin_layout.addWidget(self.boton_volver)
		self.admin_layout_principal.addLayout(self.admin_layout)
		self.admin_logo = QLabel()
		
		if os.path.exists(LOGO_PATH_SAVE):
			self.admin_logo.setPixmap(QPixmap(LOGO_PATH_SAVE))


		self.admin_logo.setScaledContents(True)
		self.admin_logo.setFixedSize(200, 200)
		self.admin_logo_layout.addStretch()
		self.admin_logo_layout.addWidget(self.admin_logo)
		self.admin_logo_layout.addStretch()
		self.admin_layout_principal.addLayout(self.admin_logo_layout)
		self.admin_tab.setLayout(self.admin_layout_principal)
		self.tabWidget.insertTab(4, self.admin_tab, "Agregar Preguntas/Respuestas")
		

	def abrir_pestana_editar(self):
		self.edit_pregunta.setText(self.pregunta_actual_editable)
		self.edit_respuesta.setPlainText(self.respuesta_actual_editable)
		self.tabWidget.setCurrentWidget(self.editar_tab)



