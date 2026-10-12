import hashlib
import bcrypt


_ROUNDS = 12


def _preparar(password: str) -> bytes:
    """Convierte el password a 32 bytes fijos con SHA-256.

    Así bcrypt nunca trunca, sin importar si el usuario escribe
    5 o 500 caracteres.
    """
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    """Convierte 'MiClave123!' en un hash tipo '$2b$12$...'.

    El hash incluye un salt aleatorio, así que la misma contraseña
    produce hashes distintos cada vez.
    """
    if not password:
        raise ValueError("La contraseña no puede estar vacía.")
    salt = bcrypt.gensalt(rounds=_ROUNDS)
    return bcrypt.hashpw(_preparar(password), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Devuelve True si 'password' coincide con el hash guardado.

    No lanza excepciones: si el hash está corrupto, devuelve False.
    """
    if not password or not hashed:
        return False
    try:
        return bcrypt.checkpw(_preparar(password), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def is_hashed(value: str) -> bool:
    """True si el string ya parece un hash bcrypt.

    Útil para no hashear dos veces lo que ya está hasheado
    (por ejemplo, durante la migración de datos viejos).
    """
    return isinstance(value, str) and value.startswith(("$2a$", "$2b$", "$2y$"))