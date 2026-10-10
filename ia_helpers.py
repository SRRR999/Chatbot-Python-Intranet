from PySide2.QtCore import QThread, Signal
from config import OPENAI_MODEL

def generar_prompt(pregunta, sugerencias):
    sugerencias_str = "\n- ".join(sugerencias)
    return (
        f"El usuario ha preguntado: \"{pregunta}\". "
        f"No tengo una respuesta directa en mi base de conocimientos. "
        f"Aquí hay algunas preguntas frecuentes de mi base de datos que podrían ser relevantes:\n- {sugerencias_str}\n"
        "Basado en la pregunta y las sugerencias, por favor, genera una respuesta útil, clara y bien formateada sin incluir letras y palabras en negritas. "
        "Si la pregunta del usuario es demasiado vaga o no se relaciona con farmacia/administración, pídele que la reformule o que elija una de las sugerencias."
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
            respuesta = "Lo siento, hubo un problema al buscar en la web. Por favor, inténtalo de nuevo más tarde."
        self.resultado.emit(respuesta)