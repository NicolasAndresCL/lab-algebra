"""Sesión y metadatos de SQLAlchemy.

Se usa el estilo síncrono a propósito: FastAPI ejecuta los endpoints `def` en
un threadpool, y el coste de este laboratorio está en generar imágenes y tablas
de verdad, no en esperar a la base de datos. Un stack síncrono es mucho menos
propenso a errores de sesión compartida entre corrutinas.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import obtener_ajustes

logger = logging.getLogger("app.db")


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


# Columnas nuevas que se añadieron DESPUÉS de que el esquema ya estuviera
# creado en alguna base real. `create_all` crea las tablas que faltan pero
# **nunca añade una columna a una tabla que ya existe**: sin esta lista, quien
# actualice el laboratorio conservando su volumen de datos —que es lo normal,
# porque ahí vive su progreso de estudio— arrancaría con un error de columna
# inexistente en la primera consulta.
#
# Los nombres son constantes de este módulo, no entradas del usuario: el SQL
# se construye por interpolación porque `ALTER TABLE` no admite parámetros.
COLUMNAS_ANADIDAS: tuple[tuple[str, str, str], ...] = (
    # Unidad de sistemas de ecuaciones (v1.1.0).
    ("tarjetas", "sistema", "JSON"),
    # Unidad de matrices y determinantes (v1.2.0).
    ("tarjetas", "matriz", "JSON"),
)


def asegurar_columnas(destino=None) -> list[str]:
    """Añade las columnas nuevas a una base que ya venía creada. Idempotente.

    Devuelve las columnas que tuvo que añadir, para poder comprobar en un test
    que la actualización **hace algo** sobre un esquema viejo y **nada** sobre
    uno al día. Una comprobación que solo se prueba en el caso bueno no está
    probada.
    """
    motor = destino if destino is not None else engine
    inspector = inspect(motor)
    tablas = set(inspector.get_table_names())
    anadidas: list[str] = []
    for tabla, columna, tipo in COLUMNAS_ANADIDAS:
        if tabla not in tablas:
            continue  # la acaba de crear create_all, ya viene completa
        if columna in {c["name"] for c in inspector.get_columns(tabla)}:
            continue
        with motor.begin() as conexion:
            conexion.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}"))
        logger.info("Columna «%s.%s» añadida al esquema existente.", tabla, columna)
        anadidas.append(f"{tabla}.{columna}")
    return anadidas


def crear_tablas() -> None:
    """Crea el esquema si no existe y lo pone al día si venía de una versión previa.

    Basta para un laboratorio de una asignatura. Un sistema con más cambios de
    modelo que estos necesitaría migraciones de verdad (Alembic).
    """
    from app import modelos  # noqa: F401  (registra los modelos en la metadata)

    Base.metadata.create_all(bind=engine)
    asegurar_columnas()
