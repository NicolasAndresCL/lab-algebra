"""Configuración de la suite.

Los defaults se inyectan en `os.environ` **antes** de importar cualquier módulo
de la aplicación: así la suite corre en un checkout limpio, sin `.env` y sin
contenedores, exactamente como corre en CI.
"""

from __future__ import annotations

import os

os.environ.setdefault("ENTORNO", "test")
os.environ.setdefault("SECRET_KEY", "clave-de-pruebas-suficientemente-larga-0123456789")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("USUARIO_INICIAL", "nico")
os.environ.setdefault("PASSWORD_INICIAL", "1234")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import SesionLocal, crear_tablas, engine
from app.main import app
from app.seed.cargar import sembrar


@pytest.fixture(scope="session", autouse=True)
def _base_de_datos():
    """Crea el esquema y el contenido una sola vez para toda la suite."""
    crear_tablas()
    with SesionLocal() as sesion:
        sembrar(sesion)
    yield
    engine.dispose()


@pytest.fixture
def sesion() -> Session:
    with SesionLocal() as s:
        yield s


@pytest.fixture
def cliente() -> TestClient:
    """Cliente HTTP sin autenticar."""
    # `raise_server_exceptions=False` para poder comprobar el 500 del manejador
    # de errores inesperados en vez de que la excepción escape al test.
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def token(cliente: TestClient) -> str:
    respuesta = cliente.post(
        "/api/v1/auth/login", json={"username": "nico", "password": "1234"}
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["access_token"]


@pytest.fixture
def autenticado(cliente: TestClient, token: str) -> TestClient:
    """Cliente con la cabecera Authorization ya puesta."""
    cliente.headers.update({"Authorization": f"Bearer {token}"})
    return cliente
