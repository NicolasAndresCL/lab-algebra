"""Endpoint de salud.

«Sano» aquí significa **que la API responde y la base de datos contesta**. Un
200 que no toca la base no prueba nada: el contenedor seguiría marcándose sano
con Postgres caído, y el healthcheck de Docker no serviría para nada.
"""

from __future__ import annotations

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app import __version__
from app.dependencias import SesionDep

router = APIRouter(tags=["salud"])


@router.get("/healthz", summary="Estado del servicio")
def healthz(sesion: SesionDep, respuesta: Response) -> dict:
    try:
        sesion.execute(text("SELECT 1"))
        base_de_datos = "ok"
    except Exception as error:
        base_de_datos = f"error: {type(error).__name__}"
        respuesta.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "estado": "ok" if base_de_datos == "ok" else "degradado",
        "version": __version__,
        "base_de_datos": base_de_datos,
    }
