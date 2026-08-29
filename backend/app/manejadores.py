"""Traducción de excepciones a respuestas HTTP.

Un único punto de traducción. Todo error — de dominio, de validación de FastAPI
o inesperado — sale con la misma forma:

    {"error": {"codigo": "...", "mensaje": "...", "detalle": {...}}}

El `codigo` es el identificador estable que consume el frontend; el `mensaje`
es texto en español que puede cambiar sin romper a nadie.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.excepciones import ErrorLabAlgebra

logger = logging.getLogger("app")


def _cuerpo(codigo: str, mensaje: str, detalle: dict | None = None) -> dict:
    return {"error": {"codigo": codigo, "mensaje": mensaje, "detalle": detalle or {}}}


def registrar_manejadores(aplicacion: FastAPI) -> None:
    """Engancha los manejadores de error en la aplicación."""

    @aplicacion.exception_handler(ErrorLabAlgebra)
    async def _dominio(_: Request, error: ErrorLabAlgebra) -> JSONResponse:
        # Errores de negocio: esperables. Se registran como warning, no como
        # excepción — no son bugs y no deben ensuciar el log con trazas.
        logger.warning("Error de dominio %s: %s", error.codigo, error.mensaje)
        return JSONResponse(
            status_code=error.http_status,
            content=_cuerpo(error.codigo, error.mensaje, error.detalle()),
        )

    @aplicacion.exception_handler(RequestValidationError)
    async def _validacion(_: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_cuerpo(
                "datos_invalidos",
                "Los datos enviados no son válidos.",
                {"campos": error.errors()},
            ),
        )

    @aplicacion.exception_handler(StarletteHTTPException)
    async def _http(_: Request, error: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content=_cuerpo("error_http", str(error.detail)),
        )

    @aplicacion.exception_handler(Exception)
    async def _inesperado(_: Request, error: Exception) -> JSONResponse:
        # Un error no previsto ES un bug: traza completa, siempre visible.
        logger.exception("Error inesperado: %s", error)
        return JSONResponse(
            status_code=500,
            content=_cuerpo("error_interno", "Ocurrió un error inesperado en el servidor."),
        )
