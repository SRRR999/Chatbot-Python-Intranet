import random

from PySide2.QtWidgets import QMessageBox, QPushButton

from db_helpers import get_preguntas_respuestas, buscar_pregunta_similar, buscar_sugerencias_similares
from ia_helpers import generar_prompt, IAWorker
from utils import cargar_preguntas_no_resueltas

SUGERENCIAS_POR_PAGINA = 5


class ChatActionsMixin:
	def enviar_a_ia(self):
		pregunta = self.ia_input.text().strip()
		if not pregunta:
			QMessageBox.warning(self, "Campo vacío", "Por favor escribe algo.")
			return

		# 1. Buscar primero en la DB
		match = buscar_pregunta_similar(pregunta)

		if match:
			db_pregunta, db_respuesta, score = match
			self.area_chat.append(
				f"<span style='color:#0074D9;'><b>Tú:</b> {pregunta}</span>"
			)
			self.area_chat.append(
				f"<span style='color:#219150;'><b>--------- 📚 Respuesta ---------------------"
				f"<br/>{db_respuesta}</span><br>"
			)
			# Setear variables y mostrar botón (lo que hace mostrar_respuesta, sin los appends)
			self.pregunta_actual_editable = db_pregunta
			self.respuesta_actual_editable = db_respuesta
			if self.usuario['rol'] == 'admin':
				self.boton_editar_respuesta.setVisible(True)
			self.ia_input.clear()
			return

		# 2. Si no hay match, ir a la IA con contexto
		todas = get_preguntas_respuestas()
		sugerencias = [p for p, _ in todas[:5]]   # top 5 como contexto
		prompt = generar_prompt(pregunta, sugerencias)

		self.worker = IAWorker(prompt, self.openai_client)
		self.worker.resultado.connect(self.mostrar_respuesta_ia)
		self.worker.start()


	def mostrar_respuesta_ia(self, respuesta):
		pregunta = self.ia_input.text().strip()
		self.area_chat.append(f"<span style='color:#0074D9;'><b>Tú (IA):</b> {pregunta}</span>")
		self.area_chat.append(f"<span style='color:#85144b;'><b>IA:</b> {respuesta}</span><br>")
		self.ia_input.clear()


	def buscar_sugerencias(self):
		palabra = self.entrada_usuario.text().strip()
		
		if not palabra:
			QMessageBox.warning(self, "Campo vacío",
								"Escribe una palabra clave para buscar.")
			return
			

		self.sugerencias = buscar_sugerencias_similares(palabra, limit=5, umbral=60)
		self.sugerencias_pagina = 0
		
		if not self.sugerencias:
			self.mostrar_sugerencias([])
			QMessageBox.information(self, "Sin resultados",
									"No se encontraron preguntas relacionadas. Intenta con otra palabra clave.")
									
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


	def mostrar_respuesta(self, pregunta, respuesta):
		self.area_chat.append(f"<span style='color:#219150; font-family: Times New Roman; font-size: 13px;'><b>{pregunta}</b></span>")
		self.area_chat.append(f"<span style='color:#222; font-family: Times New Roman; font-size: 13px;'>{respuesta}</span><br>")
		self.pregunta_actual_editable = pregunta
		self.respuesta_actual_editable = respuesta
		
		if self.usuario['rol'] == 'admin':
			self.boton_editar_respuesta.setVisible(True)


	def limpiar_pantalla(self):
		self.area_chat.clear()
		self.boton_editar_respuesta.setVisible(False)


	def update_advertencia_btn(self):
		self.boton_advertencia.setVisible(bool(cargar_preguntas_no_resueltas()))


	def mostrar_no_resueltas(self):
		preguntas = cargar_preguntas_no_resueltas()
		contenido = "\n".join(preguntas) if preguntas else "No hay preguntas pendientes por resolver."
		QMessageBox.information(self, "Preguntas no resueltas", contenido)