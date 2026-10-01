import sqlite3

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
        c.execute("INSERT INTO usuarios (nombre_usuario, password, rol) VALUES (?, ?, ?)",
                  (nombre_usuario, password, rol))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def autenticar_usuario(nombre_usuario, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT nombre_usuario, rol FROM usuarios WHERE nombre_usuario=? AND password=?", (nombre_usuario, password))
    row = c.fetchone()
    conn.close()
    if row:
        return {"nombre_usuario": row[0], "rol": row[1]}
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