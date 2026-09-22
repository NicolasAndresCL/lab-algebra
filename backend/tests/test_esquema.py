"""Actualización del esquema sobre una base que ya existía.

`Base.metadata.create_all` crea las tablas que faltan pero **nunca añade una
columna a una tabla que ya existe**. Como el laboratorio guarda el progreso de
estudio en un volumen que sobrevive a `docker compose down`, actualizar la
aplicación significa arrancar contra una base creada por la versión anterior:
sin `asegurar_columnas`, la primera consulta moriría con «columna inexistente»
y el contenedor entraría en bucle de reinicio.

La comprobación se hace en los dos sentidos —esquema viejo y esquema al día—
porque una verificación probada solo en el caso bueno no está probada.
"""

from __future__ import annotations

from sqlalchemy import create_engine, inspect, text

from app.db import COLUMNAS_ANADIDAS, Base, asegurar_columnas


def _columnas(motor, tabla: str) -> set[str]:
    return {c["name"] for c in inspect(motor).get_columns(tabla)}


def _motor_con_esquema_viejo(ruta):
    """Crea el esquema actual y le quita las columnas nuevas: la base de la v1.0."""
    motor = create_engine(f"sqlite+pysqlite:///{ruta}")
    from app import modelos  # noqa: F401  (registra los modelos en la metadata)

    Base.metadata.create_all(bind=motor)
    with motor.begin() as conexion:
        for tabla, columna, _ in COLUMNAS_ANADIDAS:
            conexion.execute(text(f"ALTER TABLE {tabla} DROP COLUMN {columna}"))
    return motor


def test_la_lista_de_columnas_nuevas_no_esta_vacia() -> None:
    """Si alguien la vacía, los dos tests de abajo pasarían sin comprobar nada."""
    assert COLUMNAS_ANADIDAS


def test_una_base_vieja_recibe_las_columnas_que_le_faltan(tmp_path) -> None:
    motor = _motor_con_esquema_viejo(tmp_path / "vieja.sqlite3")
    try:
        assert "sistema" not in _columnas(motor, "tarjetas")
        anadidas = asegurar_columnas(motor)
        assert anadidas == [f"{t}.{c}" for t, c, _ in COLUMNAS_ANADIDAS]
        assert "sistema" in _columnas(motor, "tarjetas")
    finally:
        motor.dispose()


def test_repetirlo_sobre_una_base_al_dia_no_hace_nada(tmp_path) -> None:
    """Se ejecuta en cada arranque: tiene que ser idempotente."""
    motor = _motor_con_esquema_viejo(tmp_path / "idempotente.sqlite3")
    try:
        asegurar_columnas(motor)
        assert asegurar_columnas(motor) == []
        assert asegurar_columnas(motor) == []
    finally:
        motor.dispose()


def test_los_datos_existentes_sobreviven_a_la_actualizacion(tmp_path) -> None:
    """El progreso de estudio no se pierde al añadir una columna."""
    motor = _motor_con_esquema_viejo(tmp_path / "con-datos.sqlite3")
    try:
        with motor.begin() as conexion:
            conexion.execute(
                text(
                    "INSERT INTO mazos "
                    "(id, slug, nombre, descripcion, unidad, orden, creado_en) "
                    "VALUES (1, 'previo', 'Mazo previo', '', 'Lógica', 1, "
                    "'2026-01-01 00:00:00')"
                )
            )
        asegurar_columnas(motor)
        with motor.begin() as conexion:
            fila = conexion.execute(text("SELECT slug FROM mazos WHERE id = 1")).one()
        assert fila.slug == "previo"
    finally:
        motor.dispose()
