import hashlib
import bcrypt

_ROUNDS = 12



def _preparar(password: str) -> bytes:
	return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
	if not password:
		raise ValueError("La contraseña no puede estar vacía.")
	salt = bcrypt.gensalt(rounds=_ROUNDS)
	return bcrypt.hashpw(_preparar(password), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
	if not password or not hashed:
		return False
	try:
		return bcrypt.checkpw(_preparar(password), hashed.encode("utf-8"))
	except (ValueError, TypeError):
		return False