"""Carga del contenido inicial en la base de datos.

Es **idempotente**: se ejecuta en cada arranque del contenedor y no duplica
nada. Si una tarjeta semilla ya existe, se actualiza su texto; así corregir una
errata en el temario solo exige reiniciar el servicio, sin borrar la base ni
perder el progreso de estudio.

Lo que nunca se toca es una tarjeta creada por el usuario (`es_semilla=False`):
el contenido propio es suyo.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import obtener_ajustes
from app.modelos import Mazo, Tarjeta, Usuario
from app.seed.contenido_conjuntos import MAZOS_CONJUNTOS
from app.seed.contenido_ecuaciones import MAZOS_ECUACIONES
from app.seed.contenido_logica import MAZOS_LOGICA
from app.seguridad import hashear_password

logger = logging.getLogger("app.seed")

MAZOS: list[dict] = [*MAZOS_LOGICA, *MAZOS_CONJUNTOS, *MAZOS_ECUACIONES]

CAMPOS_TARJETA = (
    "pregunta",
    "definicion",
    "notacion",
    "clave_memoria",
    "ejercicio_enunciado",
    "ejercicio_desarrollo",
    "ejercicio_respuesta",
    "formula",
    "venn",
    "sistema",
    "fuente",
    "orden",
)


def crear_usuario_inicial(sesion: Session) -> Usuario:
    """Crea el usuario del laboratorio si aún no existe."""
    ajustes = obtener_ajustes()
    usuario = sesion.scalar(
        select(Usuario).where(Usuario.username == ajustes.usuario_inicial)
    )
    if usuario is not None:
        return usuario

    usuario = Usuario(
        username=ajustes.usuario_inicial,
        hash_password=hashear_password(ajustes.password_inicial),
        nombre="Nicolás Cano",
    )
    sesion.add(usuario)
    sesion.commit()
    sesion.refresh(usuario)
    logger.info("Usuario inicial «%s» creado.", usuario.username)
    return usuario


def cargar_mazos(sesion: Session) -> tuple[int, int]:
    """Inserta o actualiza los mazos y sus tarjetas. Devuelve (mazos, tarjetas)."""
    total_mazos = 0
    total_tarjetas = 0

    for definicion_mazo in MAZOS:
        mazo = sesion.scalar(select(Mazo).where(Mazo.slug == definicion_mazo["slug"]))
        if mazo is None:
            mazo = Mazo(
                slug=definicion_mazo["slug"],
                nombre=definicion_mazo["nombre"],
                descripcion=definicion_mazo["descripcion"],
                unidad=definicion_mazo["unidad"],
                orden=definicion_mazo["orden"],
            )
            sesion.add(mazo)
            sesion.flush()
        else:
            mazo.nombre = definicion_mazo["nombre"]
            mazo.descripcion = definicion_mazo["descripcion"]
            mazo.unidad = definicion_mazo["unidad"]
            mazo.orden = definicion_mazo["orden"]
        total_mazos += 1

        for posicion, datos in enumerate(definicion_mazo["tarjetas"], start=1):
            tarjeta = sesion.scalar(
                select(Tarjeta).where(
                    Tarjeta.mazo_id == mazo.id, Tarjeta.concepto == datos["concepto"]
                )
            )
            valores = {campo: datos.get(campo) for campo in CAMPOS_TARJETA}
            valores["orden"] = datos.get("orden") or posicion
            # Los campos de texto opcionales van vacíos, no nulos: la columna
            # es NOT NULL y el frontend espera siempre una cadena.
            for campo in ("notacion", "clave_memoria", "fuente"):
                valores[campo] = valores[campo] or ""

            if tarjeta is None:
                tarjeta = Tarjeta(
                    mazo_id=mazo.id,
                    concepto=datos["concepto"],
                    es_semilla=True,
                    **valores,
                )
                sesion.add(tarjeta)
            elif tarjeta.es_semilla:
                for campo, valor in valores.items():
                    setattr(tarjeta, campo, valor)
            total_tarjetas += 1

    sesion.commit()
    logger.info("Contenido cargado: %s mazos, %s tarjetas.", total_mazos, total_tarjetas)
    return total_mazos, total_tarjetas


def sembrar(sesion: Session) -> None:
    """Punto de entrada: usuario inicial + contenido del temario."""
    crear_usuario_inicial(sesion)
    cargar_mazos(sesion)
