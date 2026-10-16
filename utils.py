import socket
import os
from config import PREGUNTAS_NO_RESUELTAS

def verificar_conexion_internet():
    try:
        socket.create_connection(("www.google.com", 80), timeout=2)
        return True
    except Exception:
        return False

def guardar_pregunta_no_resuelta(pregunta):
    with open(PREGUNTAS_NO_RESUELTAS, "a") as archivo:
        archivo.write(f"{pregunta}\n")

def eliminar_pregunta_del_txt(pregunta):
    if os.path.exists(PREGUNTAS_NO_RESUELTAS):
        with open(PREGUNTAS_NO_RESUELTAS, "r") as archivo:
            lineas = archivo.readlines()
        pregunta_normalizada = pregunta.strip().lower()
        lineas_filtradas = []
        for l in lineas:
            l_normalizada = l.strip().lower().removeprefix("pregunta sugerida: ")
            if l_normalizada != pregunta_normalizada:
                lineas_filtradas.append(l)
        with open(PREGUNTAS_NO_RESUELTAS, "w") as archivo:
            archivo.writelines(lineas_filtradas)

def cargar_preguntas_no_resueltas():
    if os.path.exists(PREGUNTAS_NO_RESUELTAS):
        with open(PREGUNTAS_NO_RESUELTAS, "r") as archivo:
            return [p.strip() for p in archivo if p.strip()]
    return []