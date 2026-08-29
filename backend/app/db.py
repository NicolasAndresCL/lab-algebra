"""Sesión y metadatos de SQLAlchemy.

Se usa el estilo síncrono a propósito: FastAPI ejecuta los endpoints `def` en
un threadpool, y el coste de este laboratorio está en generar imágenes y tablas
de verdad, no en esperar a la base de datos. Un stack síncrono es mucho menos
propenso a errores de sesión compartida entre corrutinas.
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import obtener_ajustes


class Base(DeclarativeBase):
    """Base declarativa de todos los modelos."""


def _crear_engine():
    ajustes = obtener_ajustes()
    url = ajustes.database_url
    # SQLite (tests) necesita desactivar la comprobación de hilo, porque el
    # threadpool de FastAPI atiende cada petición desde un hilo distinto.
    kwargs: dict = {"pool_pre_ping": True, "future": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url:
            # Una única conexión compartida: con el pool por defecto cada
            # conexión nueva vería una base vacía.
            from sqlalchemy.pool import StaticPool

            kwargs["poolclass"] = StaticPool
    return create_engine(url, **kwargs)


engine = _crear_engine()
SesionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def obtener_sesion() -> Iterator[Session]:
    """Dependencia de FastAPI: una sesión por petición, siempre cerrada."""
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()


def crear_tablas() -> None:
    """Crea el esquema si no existe.

    Basta para un laboratorio de una asignatura. Un sistema con datos que
    sobreviven a un cambio de modelo necesitaría migraciones (Alembic).
    """
    from app import modelos  # noqa: F401  (registra los modelos en la metadata)

    Base.metadata.create_all(bind=engine)
