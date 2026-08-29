"""Sesión del usuario en el navegador.

El token vive en `app.storage.user`, que NiceGUI respalda con una cookie
firmada: sobrevive a recargas y a navegar entre páginas, y es **por usuario**,
no compartido. Guardarlo en una variable de módulo haría que dos personas con
el navegador abierto compartieran sesión, que es el error clásico.
"""

from __future__ import annotations

from nicegui import app, ui

from app.api import ErrorApi, Sesion, verificar_sesion

CLAVE_TOKEN = "token"
CLAVE_USUARIO = "username"
CLAVE_NOMBRE = "nombre"
CLAVE_DESTINO = "destino"


def guardar_sesion(sesion: Sesion) -> None:
    app.storage.user[CLAVE_TOKEN] = sesion.token
    app.storage.user[CLAVE_USUARIO] = sesion.username
    app.storage.user[CLAVE_NOMBRE] = sesion.nombre


def cerrar_sesion() -> None:
    for clave in (CLAVE_TOKEN, CLAVE_USUARIO, CLAVE_NOMBRE):
        app.storage.user.pop(clave, None)


def sesion_actual() -> Sesion | None:
    token = app.storage.user.get(CLAVE_TOKEN)
    if not token:
        return None
    return Sesion(
        token=token,
        username=app.storage.user.get(CLAVE_USUARIO, ""),
        nombre=app.storage.user.get(CLAVE_NOMBRE, ""),
    )


def exigir_sesion(destino: str = "/") -> Sesion | None:
    """Devuelve la sesión o redirige al login.

    Se valida el token contra la API, no solo su presencia: un token expirado
    sigue guardado en la cookie y dejaría entrar a una pantalla que después
    fallaría en cada llamada.
    """
    sesion = sesion_actual()
    if sesion is None or not verificar_sesion(sesion):
        cerrar_sesion()
        app.storage.user[CLAVE_DESTINO] = destino
        ui.navigate.to("/login")
        return None
    return sesion


def destino_pendiente() -> str:
    """A dónde volver tras iniciar sesión."""
    return app.storage.user.pop(CLAVE_DESTINO, None) or "/"


def avisar(error: ErrorApi) -> None:
    """Muestra un error de la API como notificación."""
    ui.notify(str(error), type="negative", position="top", timeout=6000)
