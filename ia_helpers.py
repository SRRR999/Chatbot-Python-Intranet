import logging
from PySide2.QtCore import QThread, Signal
from config import OPENAI_MODEL

logger = logging.getLogger(__name__)


def generar_prompt(pregunta, sugerencias):
	sugerencias_str = "\n- ".join(sugerencias) if sugerencias else "(ninguna)"
	return (
		f"El usuario ha preguntado: \"{pregunta}\". "
		f"No tengo una respuesta directa en mi base de conocimientos. "
		f"Aquí hay algunas preguntas frecuentes que podrían ser relevantes:\n- {sugerencias_str}\n"
		"Basado en la pregunta y las sugerencias, genera una respuesta útil, clara y bien formateada sin negritas. "
		"Si la pregunta es demasiado vaga o no se relaciona con el dominio de la empresa, "
		"pídele que la reformule o que elija una de las sugerencias."
	)


class IAWorker(QThread):
	resultado = Signal(str)


	def __init__(self, prompt, openai_client):
		super().__init__()
		self.prompt = prompt
		self.openai_client = openai_client


	def run(self):
		try:
			chat = self.openai_client.chat.completions.create(
				model=OPENAI_MODEL,
				messages=[{"role": "user", "content": self.prompt}]
			)
			respuesta = chat.choices[0].message.content
			
		except Exception:
			logger.exception("Error al llamar a la IA")
			respuesta = "Lo siento, hubo un problema al conectar con la IA. Por favor, inténtalo de nuevo más tarde."
			
			
		self.resultado.emit(respuesta)