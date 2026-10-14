import os
import random
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextBrowser,
    QTabWidget, QHBoxLayout, QTextEdit, QLabel, QMessageBox, QScrollArea, QApplication, QDialog
)
from PySide2.QtCore import QTimer, QCoreApplication, Qt
from PySide2.QtGui import QPixmap

from ia_helpers import generar_prompt, IAWorker
from dialogs import LoginDialog
from config import OPENAI_API_KEY, OPENAI_BASE_URL, LOGO_PATH, LOGO_PATH_EDIT, LOGO_PATH_SAVE, LOGO_PATH_SUGE

import openai

from db_helpers import (
    init_db, get_preguntas_respuestas, insertar_pregunta_respuesta,
    update_pregunta_respuesta
)

from utils import (
    guardar_pregunta_no_resuelta, eliminar_pregunta_del_txt, cargar_preguntas_no_resueltas
)

SUGERENCIAS_POR_PAGINA = 5

class ChatbotGUI(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.setWindowTitle("Sistema Administrativo")
        self.setGeometry(40, 40, 800, 480)
        self.pregunta_actual_editable = None
        self.respuesta_actual_editable = None
        self.usuario = usuario
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        # Control de permisos:
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_advertencia_btn)
        self.timer.start(2000)
        

    def enviar_a_ia(self):
        pregunta = self.ia_input.text().strip()
        if not pregunta:
            QMessageBox.warning(self, "Campo vacío", "Por favor escribe algo para enviar a la IA.")
            return

        # Colocar sugerencias reales aquí (opcional)
        sugerencias = []
        prompt = generar_prompt(pregunta, sugerencias)

        #self.dialogo_carga = CargandoDialog(self)
        #self.dialogo_carga.show()

        self.worker = IAWorker(prompt, self.openai_client)
        self.worker.resultado.connect(self.mostrar_respuesta_ia)
        self.worker.start()

    def mostrar_respuesta_ia(self, respuesta):
        #self.dialogo_carga.close()
        pregunta = self.ia_input.text().strip()
        self.area_chat.append(f"<span style='color:#0074D9;'><b>Tú (IA):</b> {pregunta}</span>")
        self.area_chat.append(f"<span style='color:#85144b;'><b>IA:</b> {respuesta}</span><br>")
        self.ia_input.clear()

    def fuente(self, var, font_size=10):
        var.setStyleSheet(f"font-size: {font_size}px; font-family: 'Times New Roman';")

    def init_ui(self):
        self.tabWidget = QTabWidget(self)
        
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


    def guardar_sugerencia_usuario(self):
        pregunta = self.sugerir_pregunta.text().strip()
        respuesta = self.sugerir_respuesta.toPlainText().strip()
        if not pregunta or not respuesta:
            QMessageBox.warning(self, "Campos vacíos", "Por favor, completa la pregunta y la respuesta.")
            return

        # Formato: pregunta y respuesta juntas
        guardar_pregunta_no_resuelta(f"Pregunta sugerida: {pregunta}\nRespuesta sugerida: {respuesta}\n---")
        QMessageBox.information(self, "¡Gracias!", "Tu sugerencia ha sido guardada para revisión.")
        self.sugerir_pregunta.clear()
        self.sugerir_respuesta.clear()
        self.tabWidget.setCurrentWidget(self.chat_tab)
        self.boton_volver_chat.clicked.connect(lambda: self.tabWidget.setCurrentWidget(self.chat_tab))

    def init_sugerir_tab(self):
        self.sugerir_tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Sugiere una nueva pregunta y respuesta que creas que falta")
        self.fuente(label, 12)
        layout.addWidget(label)

        self.sugerir_pregunta = QLineEdit()
        self.sugerir_pregunta.setPlaceholderText("Pregunta sugerida")
        self.fuente(self.sugerir_pregunta, 11)
        layout.addWidget(self.sugerir_pregunta)

        self.sugerir_respuesta = QTextEdit()
        self.sugerir_respuesta.setPlaceholderText("Respuesta sugerida")
        self.sugerir_respuesta.setFixedHeight(80)
        self.sugerir_respuesta.setStyleSheet("font-size: 12px; font-family: 'Times New Roman';")
        layout.addWidget(self.sugerir_respuesta)

        self.boton_guardar_sugerencia = QPushButton("Guardar sugerencia")
        self.fuente(self.boton_guardar_sugerencia, 11)
        self.boton_guardar_sugerencia.clicked.connect(self.guardar_sugerencia_usuario)
        layout.addWidget(self.boton_guardar_sugerencia)

        self.boton_volver_chat = QPushButton("Volver al Chat")
        self.fuente(self.boton_volver_chat, 11)
        self.boton_volver_chat.clicked.connect(lambda: self.tabWidget.setCurrentWidget(self.chat_tab))
        layout.addWidget(self.boton_volver_chat)

        self.sugerir_tab.setLayout(layout)
        self.tabWidget.insertTab(1, self.sugerir_tab, "Sugerir Pregunta/Respuesta")

    def abrir_tab_sugerir(self):
        self.tabWidget.setCurrentWidget(self.sugerir_tab)

    def buscar_sugerencias(self):
        palabra = self.entrada_usuario.text().strip()
        todas_preguntas = get_preguntas_respuestas()
        if not palabra:
            self.mostrar_sugerencias_aleatorias()
            return
        self.sugerencias = [(p, r) for (p, r) in todas_preguntas if palabra.lower() in p.lower()]
        self.sugerencias_pagina = 0
        if not self.sugerencias:
            self.mostrar_sugerencias([])
            QMessageBox.information(self, "Sin resultados", "No se encontraron preguntas relacionadas. Intenta con otra palabra clave.")
        else:
            self.mostrar_sugerencias(self.sugerencias)

    def mostrar_sugerencias_aleatorias(self):
        todas_preguntas = get_preguntas_respuestas()
        if not todas_preguntas:
            self.mostrar_sugerencias([])
            QMessageBox.information(self, "Sin datos", "La base de datos no tiene preguntas registradas.")
            return
        sugerencias_random = random.sample(todas_preguntas, min(SUGERENCIAS_POR_PAGINA, len(todas_preguntas)))
        self.sugerencias = sugerencias_random
        self.sugerencias_pagina = 0
        self.mostrar_sugerencias(self.sugerencias)

    def mostrar_sugerencias(self, sugerencias):
        for i in reversed(range(self.sugerencias_panel_layout.count())):
            widget = self.sugerencias_panel_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not sugerencias:
            return

        inicio = self.sugerencias_pagina * SUGERENCIAS_POR_PAGINA
        fin = inicio + SUGERENCIAS_POR_PAGINA
        sugerencias_pag = sugerencias[inicio:fin]

        for idx, (pregunta, respuesta) in enumerate(sugerencias_pag, start=1):
            btn = QPushButton(f"📗 Pregunta {idx + inicio}")
            btn.setStyleSheet("""
                text-align: left;
                padding: 8px 12px;
                background-color: #e6faea;
                border: 1px solid #8fd19e;
                border-radius: 10px;
                font-size: 13px;
                font-family: 'Times New Roman';
            """)
            btn.setToolTip(pregunta)
            btn.clicked.connect(lambda _=None, p=pregunta, r=respuesta: self.mostrar_respuesta(p, r))
            self.sugerencias_panel_layout.addWidget(btn)

        #self.ver_mas_btn.setVisible(fin < len(sugerencias))

    def ver_mas_sugerencias(self):
        self.sugerencias_pagina += 1
        self.mostrar_sugerencias(self.sugerencias)

    def mostrar_respuesta(self, pregunta, respuesta):
        self.area_chat.append(f"<span style='color:#219150; font-family: Times New Roman; font-size: 13px;'><b>{pregunta}</b></span>")
        self.area_chat.append(f"<span style='color:#222; font-family: Times New Roman; font-size: 13px;'>{respuesta}</span><br>")
        self.mostrar_boton_editar(pregunta, respuesta)

    def limpiar_pantalla(self):
        self.area_chat.clear()

    def update_advertencia_btn(self):
        self.boton_advertencia.setVisible(bool(cargar_preguntas_no_resueltas()))

    def mostrar_no_resueltas(self):
        preguntas = cargar_preguntas_no_resueltas()
        contenido = "\n".join(preguntas) if preguntas else "No hay preguntas pendientes por resolver."
        QMessageBox.information(self, "Preguntas no resueltas", contenido)

    # ------------ ADMINISTRACIÓN Y EDICIÓN ------------

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

    def guardar_cambios_edicion(self):
        pregunta_nueva = self.edit_pregunta.text().strip()
        respuesta_nueva = self.edit_respuesta.toPlainText().strip()
        if pregunta_nueva and respuesta_nueva:
            update_pregunta_respuesta(
                self.pregunta_actual_editable, self.respuesta_actual_editable,
                pregunta_nueva, respuesta_nueva
            )
            QMessageBox.information(self, "Éxito", "Pregunta y respuesta actualizadas correctamente.")
            self.tabWidget.setCurrentWidget(self.chat_tab)
            self.pregunta_actual_editable = None
            self.respuesta_actual_editable = None
            self.buscar_sugerencias()
        else:
            QMessageBox.warning(self, "Error", "No puedes dejar campos vacíos.")

    def mostrar_boton_editar(self, pregunta, respuesta):
        self.pregunta_actual_editable = pregunta
        self.respuesta_actual_editable = respuesta
        

    def abrir_pestana_editar(self):
        self.edit_pregunta.setText(self.pregunta_actual_editable)
        self.edit_respuesta.setPlainText(self.respuesta_actual_editable)
        self.tabWidget.setCurrentWidget(self.editar_tab)

    def agregar_pregunta_respuesta(self):
        pregunta = self.agregar_pregunta.text().strip()
        respuesta = self.agregar_respuesta.toPlainText().strip()
        if pregunta and respuesta:
            datos = get_preguntas_respuestas()
            if any(pregunta.lower() == p.lower() for p, _ in datos):
                QMessageBox.warning(self, "Duplicado", "Esa pregunta ya existe.")
                return
            insertar_pregunta_respuesta(pregunta, respuesta)
            self.area_chat.append("Chatbot: Se ha actualizado la base de datos.\n")
            self.agregar_pregunta.clear()
            self.agregar_respuesta.clear()
            eliminar_pregunta_del_txt(pregunta)
            self.buscar_sugerencias()
        else:
            QMessageBox.warning(self, "Campos vacíos", "No puedes dejar campos vacíos.")
