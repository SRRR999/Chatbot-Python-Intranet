# 🤖 Sistema Administrativo con Chatbot IA (PyQt5)

Un sistema de escritorio interactivo y modular desarrollado en Python utilizando PyQt5. Este proyecto integra un chatbot inteligente potenciado por modelos de lenguaje avanzados (vía OpenAI u OpenRouter), un sistema de gestión de base de datos local SQLite y un control riguroso de roles de usuario (Administrador y Empleado).

---

## ✨ Características Principales

* **Interfaz Gráfica Moderna (PyQt5):** Interfaz limpia estructurada en pestañas con diseño optimizado (fuentes personalizadas, logotipos y paneles interactivos).
* **Control de Acceso y Roles (Login):** Autenticación de usuarios con diferenciación de privilegios:
  * *Empleados:* Pueden chatear, consultar sugerencias frecuentes y proponer nuevas preguntas/respuestas.
  * *Administradores:* Tienen acceso total para agregar, editar y administrar la base de conocimientos oficial.
* **Base de Datos Local (SQLite):** Información rápida e interna mediante archivos locales.
* **Sugerencias Dinámicas y Búsqueda Inteligente:** Búsqueda en tiempo real por palabras clave o generación de sugerencias aleatorias basadas en el historial.
* **Procesamiento Asíncrono (`IAWorker`):** Consultas a la IA ejecutadas en hilos independientes (`QThread`) para evitar congelamientos en la interfaz gráfica.
* **Gestión de Preguntas No Resueltas:** Sistema de respaldo que registra automáticamente consultas que la IA no pudo responder de forma directa para su posterior revisión administrativa.

---

## 🛠️ Tecnologías y Librerías Utilizadas

* **Python** 3.10+
* **PyQt5** (Interfaz gráfica de escritorio)
* **OpenAI Python SDK** (Comunicación con modelos de lenguaje)
* **python-dotenv** (Gestión segura de variables de entorno)
* **rapidfuzz** (Coincidencia difusa de texto para sugerencias y NLP)
* **SQLite3** (Base de datos)

---

## 🔒 Consideraciones de Seguridad (Datos Sensibles)

Este proyecto maneja credenciales privadas (como tu llave de API de OpenAI u OpenRouter). Para evitar filtraciones accidentales en GitHub:
1. Nunca subas tus claves directamente en el código fuente.
2. Utiliza siempre un archivo `.env` local para tus credenciales.
3. El archivo `.env` está protegido por el archivo `.gitignore` preconfigurado en este repositorio.

---

## ⚙️ Requisitos e Instalación

Sigue estos pasos para clonar y poner en marcha el proyecto en tu máquina local:

### 1. Clona el repositorio
#### bash <br>
git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
cd tu-repositorio

### 2. Crea y activa un entorno virtual
#### bash <br>
python -m venv venv


#### En Windows:
venv\Scripts\activate

#### En macOS / Linux:
source venv/bin/activate

### 3. Instala las dependencias
Instala los paquetes necesarios ejecutando el siguiente comando:

#### bash <br>
pip install PyQt5 openai python-dotenv rapidfuzz
(Opcional: Si cuentas con un archivo de requerimientos, puedes usar pip install -r requirements.txt)

### 4. Configura tus variables de entorno
Crea un archivo llamado exactamente .env en la raíz del proyecto y añade tus credenciales basándote en la siguiente estructura:

* OPENAI_API_KEY=tu_clave_real_de_openrouter_o_openai
* OPENAI_BASE_URL=[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)
* OPENAI_MODEL=deepseek/deepseek-r1:free


## Personalización de Logos e Iconos 🎨

Puedes cambiar fácilmente la identidad visual de tu chatbot:
1. Reemplaza los archivos de imagen ubicados en `icon/` por tus propios logos.
2. Asegúrate de mantener los mismos nombres de archivo o actualiza las rutas en el archivo de configuración (config.py).

*(Nota: Los iconos por defecto utilizados en este proyecto provienen de [Flaticon](https://www.flaticon.com/) y se otorgan los créditos correspondientes a sus autores).*

### 🚀 Uso de la Aplicación

Una vez configurado el entorno y tus llaves de acceso, ejecuta el archivo principal de la interfaz gráfica:

#### bash <br>
python chatbot_gui.py<br>


### 📂 Estructura del Proyecto

📦 tu-repositorio/

├── 📁 icon/                 # Recursos gráficos (logotipos e iconos de pestañas)

├── 📄 .env                  # Variables de entorno y llaves privadas (Ignorado por Git)

├── 📄 .gitignore            # Archivos y carpetas ignorados por control de versiones

├── 📄 chatbot_gui.py        # Ventana principal y control de pestañas (PyQt5)

├── 📄 config.py             # Cargador de configuraciones y variables de entorno

├── 📄 db_helpers.py         # Conexión, esquemas y operaciones con SQLite

├── 📄 ia_helpers.py         # Construcción de prompts y gestión del hilo de IA (QThread)

├── 📄 nlp_helpers.py        # Funciones de procesamiento de texto y búsqueda difusa

├── 📄 utils.py              # Funciones auxiliares (conexión a internet y archivos de texto)

└── 📄 README.md             # Documentación oficial del proyecto

<br/>

## 🎨 Agradecimientos y Recursos

* Créditos a los autores de los iconos:
  * chatbot.png: Diseñado por [ppanggm](https://www.magnific.com/es/autor/ppanggm/iconos)
  * burbuja-de-chat.png --- edicion-chat.png --- sugerencia-chat.png: Diseñados por [Prabowo747](https://www.magnific.com/es/autor/prabowo747/iconos)

### 🤝 Contribuciones
¡Las contribuciones y sugerencias son completamente bienvenidas! Si deseas proponer mejoras, por favor abre un issue o envía un pull request con tus cambios propuestos.

### 📄 Licencia
Este proyecto se distribuye bajo los términos de la licencia MIT.
