"""Autenticación: hash de contraseñas y tokens JWT.

Se usa `bcrypt` directamente en vez de `passlib`: passlib 1.7 lee
`bcrypt.__about__.__version__`, atributo que bcrypt 4.x eliminó, y arranca
escupiendo un error de compatibilidad. Aquí no hay capa intermedia que se rompa.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import obtener_ajustes
from app.excepciones import NoAutenticadoError

# bcrypt trunca en 72 bytes; recortar aquí evita un fallo opaco en el hash.
LIMITE_BCRYPT = 72


def hashear_password(password: str) -> str:
    """Devuelve el hash bcrypt de una contraseña en claro."""
    bytes_password = password.encode("utf-8")[:LIMITE_BCRYPT]
    return bcrypt.hashpw(bytes_password, bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, hash_guardado: str) -> bool:
    """Comprueba una contraseña contra su hash. Nunca lanza por hash corrupto."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8")[:LIMITE_BCRYPT], hash_guardado.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def crear_token(username: str, minutos: int | None = None) -> str:
    """Emite un JWT firmado para el usuario indicado."""
    ajustes = obtener_ajustes()
    minutos = minutos if minutos is not None else ajustes.minutos_expiracion_token
    ahora = datetime.now(UTC)
    carga = {
        "sub": username,
        "iat": int(ahora.timestamp()),
        "exp": int((ahora + timedelta(minutes=minutos)).timestamp()),
    }
    return jwt.encode(carga, ajustes.secret_key, algorithm=ajustes.algoritmo_jwt)


def leer_token(token: str) -> str:
    """Valida el token y devuelve el `username`. Lanza si es inválido o expiró."""
    ajustes = obtener_ajustes()
    try:
        carga = jwt.decode(token, ajustes.secret_key, algorithms=[ajustes.algoritmo_jwt])
    except jwt.ExpiredSignatureError as error:
        raise NoAutenticadoError("La sesión expiró; vuelve a iniciar sesión.") from error
    except jwt.PyJWTError as error:
        raise NoAutenticadoError("El token de sesión no es válido.") from error

    username = carga.get("sub")
    if not username:
        raise NoAutenticadoError("El token no identifica a ningún usuario.")
    return str(username)
