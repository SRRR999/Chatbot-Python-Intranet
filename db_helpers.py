import sqlite3
from password import hash_password, verify_password
from rapidfuzz import fuzz, process

DB_PATH = "chatbot.db"


def init_db():
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS preguntas_respuestas (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		pregunta TEXT UNIQUE,
		respuesta TEXT
	)''')
	c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		nombre_usuario TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL,
		rol TEXT NOT NULL -- 'admin' o 'empleado'
	)''')
	conn.commit()
	conn.close()


def registrar_usuario(nombre_usuario, password, rol="empleado"):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	
	try:
		password_hash = hash_password(password)
		c.execute("INSERT INTO usuarios (nombre_usuario, password, rol) VALUES (?, ?, ?)",
				  (nombre_usuario, password_hash, rol))
		conn.commit()
		return True
		
	except sqlite3.IntegrityError:
		return False
		
	finally:
		conn.close()


def autenticar_usuario(nombre_usuario, password):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute("SELECT nombre_usuario, password, rol FROM usuarios WHERE nombre_usuario=?",
			  (nombre_usuario,))
	row = c.fetchone()
	conn.close()

	if not row:
		return None

	nombre, hash_guardado, rol = row
	if verify_password(password, hash_guardado):
		return {"nombre_usuario": nombre, "rol": rol}
	return None


def existe_admin():
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute("SELECT COUNT(*) FROM usuarios WHERE rol='admin'")
	count = c.fetchone()[0]
	conn.close()
	return count > 0


def get_preguntas_respuestas():
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute("SELECT pregunta, respuesta FROM preguntas_respuestas")
	resultados = c.fetchall()
	conn.close()
	return resultados


def insertar_pregunta_respuesta(pregunta, respuesta):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	
	try:
		c.execute("INSERT INTO preguntas_respuestas (pregunta, respuesta) VALUES (?, ?)", (pregunta, respuesta))
		conn.commit()
		
	except sqlite3.IntegrityError:
		pass
		
	finally:
		conn.close()


def update_pregunta_respuesta(pregunta_ant, respuesta_ant, pregunta_nueva, respuesta_nueva):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute("UPDATE preguntas_respuestas SET pregunta=?, respuesta=? WHERE pregunta=? AND respuesta=?",
			  (pregunta_nueva, respuesta_nueva, pregunta_ant, respuesta_ant))
	conn.commit()
	conn.close()


def buscar_pregunta_similar(pregunta_usuario, umbral=70):
	"""Busca la pregunta más parecida en la DB.

	Devuelve (pregunta, respuesta) si encuentra un match con
	similitud >= umbral. Si no, devuelve None.
	"""
	todas = get_preguntas_respuestas()
	if not todas:
		return None

	preguntas = [p for p, _ in todas]
	resultado = process.extractOne(
		pregunta_usuario,
		preguntas,
		scorer=fuzz.token_set_ratio,
	)

	if resultado is None:
		return None

	match_pregunta, score, _ = resultado
	if score < umbral:
		return None

	for p, r in todas:
		if p == match_pregunta:
			return (p, r, score)
	return None


def buscar_sugerencias_similares(pregunta_usuario, limit=20, umbral=60):
	todas = get_preguntas_respuestas()
	if not todas:
		return []

	preguntas = [p for p, _ in todas]
	resultados = process.extract(
		pregunta_usuario,
		preguntas,
		scorer=fuzz.token_set_ratio,
		limit=limit,
	)

	sugerencias = []
	for _, score, idx in resultados:
		if score >= umbral:
			sugerencias.append(todas[idx])
	return sugerencias