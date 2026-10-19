from rapidfuzz import process, fuzz

def normalizar_pregunta(pregunta, sinonimos):
	palabras = pregunta.lower().split()
	resultado = []
	for palabra in palabras:
		for clave, sin_list in sinonimos.items():
			if palabra in sin_list:
				resultado.append(clave)
				break
		else:
			resultado.append(palabra)
	return " ".join(resultado)

def buscar_coincidencia(pregunta_norm, preguntas_norm_db, threshold=60):
	mejor = process.extractOne(pregunta_norm, preguntas_norm_db, scorer=fuzz.token_set_ratio)
	if mejor and mejor[1] > threshold:
		return preguntas_norm_db.index(mejor[0])
	return None

def sugerencias(pregunta_norm, preguntas_norm_db, preguntas_originales, limit=5, threshold=60):
	sugerencias_idx = process.extract(pregunta_norm, preguntas_norm_db, scorer=fuzz.token_set_ratio, limit=limit)
	return [preguntas_originales[idx] for _, score, idx in sugerencias_idx if score > threshold]