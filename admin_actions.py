from PySide2.QtWidgets import QMessageBox
import sqlite3

from db_helpers import (
	get_preguntas_respuestas,
	insertar_pregunta_respuesta,
	update_pregunta_respuesta,
)
from utils import eliminar_pregunta_del_txt, guardar_pregunta_no_resuelta


class AdminActionsMixin:
	def guardar_sugerencia_usuario(self):
		pregunta = self.sugerir_pregunta.text().strip()
		respuesta = self.sugerir_respuesta.toPlainText().strip()
		
		if not pregunta or not respuesta:
			QMessageBox.warning(self, "Campos vacíos", "Por favor, completa la pregunta y la respuesta.")
			return

		guardar_pregunta_no_resuelta(f"Pregunta sugerida: {pregunta}\nRespuesta sugerida: {respuesta}\n---")
		QMessageBox.information(self, "¡Gracias!", "Tu sugerencia ha sido guardada para revisión.")
		self.sugerir_pregunta.clear()
		self.sugerir_respuesta.clear()
		self.tabWidget.setCurrentWidget(self.chat_tab)


	def guardar_cambios_edicion(self):
		pregunta_nueva = self.edit_pregunta.text().strip()
		respuesta_nueva = self.edit_respuesta.toPlainText().strip()
		
		if pregunta_nueva and respuesta_nueva:
			try:
				update_pregunta_respuesta(
					self.pregunta_actual_editable, self.respuesta_actual_editable,
					pregunta_nueva, respuesta_nueva
				)
				QMessageBox.information(self, "Éxito", "Pregunta y respuesta actualizadas correctamente.")
				self.tabWidget.setCurrentWidget(self.chat_tab)
				self.pregunta_actual_editable = None
				self.respuesta_actual_editable = None
			except sqlite3.IntegrityError:
				QMessageBox.warning(self, "Duplicado",
									"Ya existe una pregunta con ese texto. Elegí otro.")
		else:
			QMessageBox.warning(self, "Error", "No puedes dejar campos vacíos.")

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
			
		else:
			QMessageBox.warning(self, "Campos vacíos", "No puedes dejar campos vacíos.")