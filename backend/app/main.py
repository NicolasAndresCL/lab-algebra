"""Punto de entrada de la API.

Monta los routers bajo `/api/v1`, registra los manejadores de error y, al
arrancar, crea el esquema y carga el contenido del temario.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import obtener_ajustes
from app.db import SesionLocal, crear_tablas
from app.manejadores import registrar_manejadores
from app.routers import auth, estudio, herramientas, mazos, salud
from app.seed.cargar import sembrar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
logger = logging.getLogger("app")

PREFIJO = "/api/v1"


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    """Prepara la base al arrancar y la deja lista con el temario cargado."""
    crear_tablas()
    with SesionLocal() as sesion:
        sembrar(sesion)
    logger.info("lab-algebra API %s lista.", __version__)
    yield


def crear_app() -> FastAPI:
    ajustes = obtener_ajustes()
    aplicacion = FastAPI(
        title="lab-algebra — API",
        version=__version__,
        summary=(
            "Tarjetas de memorización de Álgebra: lógica proposicional, conjuntos "
            "y sistemas de ecuaciones lineales."
        ),
        description=(
            "Backend del laboratorio de Álgebra ST 2026. Sirve los mazos de tarjetas, "
            "calcula tablas de verdad, resuelve operaciones de conjuntos, genera "
            "diagramas de Venn y resuelve sistemas de ecuaciones lineales con "
            "aritmética exacta."
        ),
        lifespan=ciclo_de_vida,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    aplicacion.add_middleware(
        CORSMiddleware,
        allow_origins=ajustes.origenes,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registrar_manejadores(aplicacion)

    aplicacion.include_router(salud.router)
    aplicacion.include_router(auth.router, prefix=PREFIJO)
    aplicacion.include_router(mazos.router, prefix=PREFIJO)
    aplicacion.include_router(mazos.router_tarjetas, prefix=PREFIJO)
    aplicacion.include_router(herramientas.router, prefix=PREFIJO)
    aplicacion.include_router(estudio.router, prefix=PREFIJO)
    return aplicacion


app = crear_app()
