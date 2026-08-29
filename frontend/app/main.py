"""Punto de entrada del frontend NiceGUI.

NiceGUI corre sobre su propio FastAPI; el backend de la aplicación es un
servicio aparte (`lab-algebra-api`) al que se llama por HTTP. Mantenerlos
separados es lo que permite levantar la API sola —para la documentación
interactiva de `/docs` o para un script— sin arrastrar la interfaz.
"""

from __future__ import annotations

import logging

from nicegui import app, ui

from app import __version__
from app.config import obtener_ajustes
from app.paginas import *  # registra las rutas @ui.page

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
logger = logging.getLogger("frontend")

ajustes = obtener_ajustes()


@app.get("/healthz")
def healthz() -> dict:
    """Salud del propio frontend.

    Deliberadamente **no** consulta al backend: si la API está caída, quien
    debe marcarse enfermo es su contenedor, no este. Un healthcheck que se
    contagia del vecino provoca reinicios en cascada.
    """
    return {"estado": "ok", "version": __version__, "api_url": ajustes.api_url}


ui.run(
    title=ajustes.titulo,
    port=ajustes.puerto,
    host="0.0.0.0",  # dentro del contenedor hay que escuchar en todas las interfaces
    storage_secret=ajustes.storage_secret,
    favicon="🧮",
    dark=None,  # sigue el tema del sistema operativo del usuario
    reload=False,
    show=False,  # en un contenedor no hay navegador que abrir
)
