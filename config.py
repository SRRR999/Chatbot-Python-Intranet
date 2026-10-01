import os
from dotenv import load_dotenv

# Cargar variables de archivo .env
load_dotenv()

# Obtenemos las variables de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("¡Falta la variable OPENAI_API_KEY en el archivo .env!")

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek/deepseek-r1:free")

# Rutas locales
DB_PATH = "chatbot.db"
LOGO_PATH = "icon/EcoSalud.png"
LOGO_PATH_SAVE = "icon/burbuja-de-chat.png"
LOGO_PATH_EDIT = "icon/document-editor.png"
LOGO_PATH_SUGE = "idea (1).png"
PREGUNTAS_NO_RESUELTAS = "preguntas_no_resueltas.txt"