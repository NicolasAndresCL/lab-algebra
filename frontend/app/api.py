"""Cliente HTTP del backend.

Toda llamada pasa por `_peticion`, que traduce el contrato de error de la API
(`{"error": {"codigo", "mensaje", "detalle"}}`) a una excepción con el mensaje
ya en español, listo para mostrar en un `ui.notify`.

Un fallo de red **no** es lo mismo que un error de negocio: si el backend no
responde, el usuario tiene que enterarse de eso y no de un «no se pudo
completar la operación» genérico.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import obtener_ajustes


class ErrorApi(Exception):
    """Error devuelto por la API o fallo al hablar con ella."""

    def __init__(
        self, mensaje: str, codigo: str = "error", detalle: dict | None = None
    ) -> None:
        self.codigo = codigo
        self.detalle = detalle or {}
        super().__init__(mensaje)


@dataclass(frozen=True)
class Sesion:
    token: str
    username: str
    nombre: str

    @property
    def cabeceras(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}


def _extraer_error(respuesta: httpx.Response) -> ErrorApi:
    try:
        cuerpo = respuesta.json().get("error", {})
    except ValueError:
        cuerpo = {}
    return ErrorApi(
        cuerpo.get("mensaje") or f"El servidor respondió {respuesta.status_code}.",
        cuerpo.get("codigo", "error_http"),
        cuerpo.get("detalle", {}),
    )


def _peticion(
    metodo: str,
    ruta: str,
    *,
    sesion: Sesion | None = None,
    json: Any = None,
    params: dict | None = None,
    binario: bool = False,
) -> Any:
    ajustes = obtener_ajustes()
    url = f"{ajustes.base_api}{ruta}"
    cabeceras = sesion.cabeceras if sesion else {}
    try:
        with httpx.Client(timeout=ajustes.timeout_segundos) as cliente:
            respuesta = cliente.request(
                metodo, url, json=json, params=params, headers=cabeceras
            )
    except httpx.RequestError as error:
        raise ErrorApi(
            f"No se pudo contactar con la API en {ajustes.api_url}. "
            f"¿Está levantado el contenedor lab-algebra-api?",
            "sin_conexion",
        ) from error

    if respuesta.status_code >= 400:
        raise _extraer_error(respuesta)
    if binario:
        return respuesta.content
    if respuesta.status_code == 204 or not respuesta.content:
        return None
    return respuesta.json()


# --------------------------------------------------------------------------
# Autenticación
# --------------------------------------------------------------------------
def login(username: str, password: str) -> Sesion:
    datos = _peticion("POST", "/auth/login", json={"username": username, "password": password})
    return Sesion(
        token=datos["access_token"],
        username=datos["usuario"]["username"],
        nombre=datos["usuario"]["nombre"] or datos["usuario"]["username"],
    )


def verificar_sesion(sesion: Sesion) -> bool:
    """Comprueba que el token sigue siendo válido (puede haber expirado)."""
    try:
        _peticion("GET", "/auth/yo", sesion=sesion)
    except ErrorApi:
        return False
    return True


# --------------------------------------------------------------------------
# Mazos y tarjetas
# --------------------------------------------------------------------------
def listar_mazos(sesion: Sesion) -> list[dict]:
    return _peticion("GET", "/mazos", sesion=sesion)


def listar_tarjetas(sesion: Sesion, mazo_id: int, buscar: str | None = None) -> list[dict]:
    params = {"buscar": buscar} if buscar else None
    return _peticion("GET", f"/mazos/{mazo_id}/tarjetas", sesion=sesion, params=params)


def crear_tarjeta(sesion: Sesion, datos: dict) -> dict:
    return _peticion("POST", "/tarjetas", sesion=sesion, json=datos)


def borrar_tarjeta(sesion: Sesion, tarjeta_id: int) -> None:
    _peticion("DELETE", f"/tarjetas/{tarjeta_id}", sesion=sesion)


def crear_mazo(sesion: Sesion, datos: dict) -> dict:
    return _peticion("POST", "/mazos", sesion=sesion, json=datos)


# --------------------------------------------------------------------------
# Estudio
# --------------------------------------------------------------------------
def cola_de_estudio(sesion: Sesion, mazo_id: int | None = None, limite: int = 20) -> list[dict]:
    params: dict = {"limite": limite}
    if mazo_id:
        params["mazo_id"] = mazo_id
    return _peticion("GET", "/estudio/cola", sesion=sesion, params=params)


def calificar(sesion: Sesion, tarjeta_id: int, calidad: int) -> dict:
    return _peticion(
        "POST", f"/estudio/tarjetas/{tarjeta_id}/calificar", sesion=sesion,
        json={"calidad": calidad},
    )


def progreso(sesion: Sesion) -> dict:
    return _peticion("GET", "/estudio/progreso", sesion=sesion)


# --------------------------------------------------------------------------
# Herramientas
# --------------------------------------------------------------------------
def tabla_de_verdad(sesion: Sesion, formula: str) -> dict:
    return _peticion(
        "POST", "/herramientas/tabla-verdad", sesion=sesion, json={"formula": formula}
    )


def equivalencia(sesion: Sesion, formula_a: str, formula_b: str) -> dict:
    return _peticion(
        "POST", "/herramientas/equivalencia", sesion=sesion,
        json={"formula_a": formula_a, "formula_b": formula_b},
    )


def operar_conjuntos(sesion: Sesion, a: list, b: list, universo: list) -> dict:
    return _peticion(
        "POST", "/herramientas/conjuntos", sesion=sesion,
        json={"a": a, "b": b, "universo": universo},
    )


def resolver_sistema(
    sesion: Sesion,
    matriz: list[list],
    incognitas: list[str] | None = None,
    metodo: str | None = None,
) -> dict:
    """Resuelve un sistema lineal de 2×2 o 3×3 con aritmética exacta.

    Los coeficientes viajan como **texto**, no como número: el backend
    rechaza los flotantes a propósito para que «1/3» no se convierta en
    «0.333» por el camino.
    """
    cuerpo: dict = {"matriz": matriz}
    if incognitas:
        cuerpo["incognitas"] = incognitas
    if metodo:
        cuerpo["metodo"] = metodo
    return _peticion("POST", "/herramientas/ecuaciones", sesion=sesion, json=cuerpo)


def regiones_venn(sesion: Sesion, especificacion: dict) -> dict:
    return _peticion(
        "POST", "/herramientas/venn/regiones", sesion=sesion, json=especificacion
    )


def imagen_venn(sesion: Sesion, especificacion: dict) -> str:
    """Devuelve el diagrama como data URI, listo para `ui.image`.

    El endpoint es un POST que responde `image/png`, así que no se puede pasar
    su URL directamente a `ui.image`: se descarga y se incrusta en base64.
    """
    png = _peticion(
        "POST", "/herramientas/venn/imagen", sesion=sesion,
        json=especificacion, binario=True,
    )
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


def salud() -> dict:
    """Estado del backend. No requiere sesión: sirve para la pantalla de login."""
    ajustes = obtener_ajustes()
    try:
        with httpx.Client(timeout=5.0) as cliente:
            return cliente.get(f"{ajustes.api_url.rstrip('/')}/healthz").json()
    except (httpx.RequestError, ValueError):
        return {"estado": "sin conexión", "base_de_datos": "desconocida"}
