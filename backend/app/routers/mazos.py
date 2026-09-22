"""Mazos y tarjetas: consulta y alta de material nuevo."""

from __future__ import annotations

from fastapi import APIRouter, Query, Response, status
from sqlalchemy import func, select

from app.dependencias import SesionDep, UsuarioDep
from app.esquemas import (
    MazoCrear,
    MazoSalida,
    TarjetaActualizar,
    TarjetaCrear,
    TarjetaSalida,
)
from app.excepciones import RecursoDuplicadoError, RecursoNoEncontradoError
from app.modelos import Mazo, Tarjeta
from app.services import ecuaciones, logica, venn

router = APIRouter(prefix="/mazos", tags=["mazos"])
router_tarjetas = APIRouter(prefix="/tarjetas", tags=["tarjetas"])


def _obtener_mazo(sesion: SesionDep, mazo_id: int) -> Mazo:
    mazo = sesion.get(Mazo, mazo_id)
    if mazo is None:
        raise RecursoNoEncontradoError("mazo", mazo_id)
    return mazo


def _obtener_tarjeta(sesion: SesionDep, tarjeta_id: int) -> Tarjeta:
    tarjeta = sesion.get(Tarjeta, tarjeta_id)
    if tarjeta is None:
        raise RecursoNoEncontradoError("tarjeta", tarjeta_id)
    return tarjeta


def _validar_contenido_calculado(
    formula: str | None,
    especificacion: dict | None,
    sistema: dict | None = None,
) -> None:
    """Rechaza una fórmula, un diagrama o un sistema que no se pueden calcular.

    Se comprueba **al guardar**, no al mostrar: si no, la tarjeta se crea sin
    problema y revienta después, en mitad de un repaso.
    """
    if formula:
        logica.construir_tabla(formula)
    if especificacion:
        venn.generar_png(especificacion)
    if sistema:
        ecuaciones.resolver_datos(
            sistema.get("matriz"),
            sistema.get("incognitas"),
            sistema.get("metodo"),
        )


# --------------------------------------------------------------------------
# Mazos
# --------------------------------------------------------------------------
@router.get("", response_model=list[MazoSalida], summary="Listar mazos")
def listar_mazos(sesion: SesionDep, _: UsuarioDep) -> list[MazoSalida]:
    conteos = dict(
        sesion.execute(
            select(Tarjeta.mazo_id, func.count(Tarjeta.id)).group_by(Tarjeta.mazo_id)
        ).all()
    )
    mazos = sesion.scalars(select(Mazo).order_by(Mazo.orden, Mazo.id)).all()
    return [
        MazoSalida(
            id=m.id,
            slug=m.slug,
            nombre=m.nombre,
            descripcion=m.descripcion,
            unidad=m.unidad,
            orden=m.orden,
            total_tarjetas=conteos.get(m.id, 0),
        )
        for m in mazos
    ]


@router.post(
    "",
    response_model=MazoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un mazo",
)
def crear_mazo(datos: MazoCrear, sesion: SesionDep, _: UsuarioDep) -> MazoSalida:
    existente = sesion.scalar(select(Mazo).where(Mazo.slug == datos.slug))
    if existente is not None:
        raise RecursoDuplicadoError(f"Ya existe un mazo con el identificador «{datos.slug}».")

    mazo = Mazo(**datos.model_dump())
    sesion.add(mazo)
    sesion.commit()
    sesion.refresh(mazo)
    return MazoSalida(**datos.model_dump(), id=mazo.id, total_tarjetas=0)


@router.get(
    "/{mazo_id}/tarjetas",
    response_model=list[TarjetaSalida],
    summary="Tarjetas de un mazo",
)
def listar_tarjetas(
    mazo_id: int,
    sesion: SesionDep,
    _: UsuarioDep,
    buscar: str | None = Query(default=None, max_length=120),
) -> list[Tarjeta]:
    _obtener_mazo(sesion, mazo_id)
    consulta = select(Tarjeta).where(Tarjeta.mazo_id == mazo_id)
    if buscar:
        patron = f"%{buscar.strip()}%"
        consulta = consulta.where(
            Tarjeta.concepto.ilike(patron) | Tarjeta.definicion.ilike(patron)
        )
    return list(sesion.scalars(consulta.order_by(Tarjeta.orden, Tarjeta.id)).all())


# --------------------------------------------------------------------------
# Tarjetas
# --------------------------------------------------------------------------
@router_tarjetas.get("/{tarjeta_id}", response_model=TarjetaSalida, summary="Ver una tarjeta")
def ver_tarjeta(tarjeta_id: int, sesion: SesionDep, _: UsuarioDep) -> Tarjeta:
    return _obtener_tarjeta(sesion, tarjeta_id)


@router_tarjetas.post(
    "",
    response_model=TarjetaSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una tarjeta",
)
def crear_tarjeta(datos: TarjetaCrear, sesion: SesionDep, _: UsuarioDep) -> Tarjeta:
    _obtener_mazo(sesion, datos.mazo_id)
    duplicada = sesion.scalar(
        select(Tarjeta).where(
            Tarjeta.mazo_id == datos.mazo_id, Tarjeta.concepto == datos.concepto
        )
    )
    if duplicada is not None:
        raise RecursoDuplicadoError(
            f"El mazo ya tiene una tarjeta para el concepto «{datos.concepto}»."
        )
    _validar_contenido_calculado(datos.formula, datos.venn, datos.sistema)

    tarjeta = Tarjeta(**datos.model_dump(), es_semilla=False)
    sesion.add(tarjeta)
    sesion.commit()
    sesion.refresh(tarjeta)
    return tarjeta


@router_tarjetas.patch(
    "/{tarjeta_id}", response_model=TarjetaSalida, summary="Editar una tarjeta"
)
def editar_tarjeta(
    tarjeta_id: int, datos: TarjetaActualizar, sesion: SesionDep, _: UsuarioDep
) -> Tarjeta:
    tarjeta = _obtener_tarjeta(sesion, tarjeta_id)
    cambios = datos.model_dump(exclude_unset=True)
    _validar_contenido_calculado(
        cambios.get("formula", tarjeta.formula),
        cambios.get("venn", tarjeta.venn),
        cambios.get("sistema", tarjeta.sistema),
    )
    for campo, valor in cambios.items():
        setattr(tarjeta, campo, valor)
    sesion.commit()
    sesion.refresh(tarjeta)
    return tarjeta


@router_tarjetas.delete(
    "/{tarjeta_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Borrar una tarjeta propia",
)
def borrar_tarjeta(tarjeta_id: int, sesion: SesionDep, _: UsuarioDep) -> Response:
    """Borra una tarjeta creada por el usuario.

    Las tarjetas semilla (el temario extraído de los PDF) no se borran: son el
    material de la asignatura, y recuperarlas exigiría recrear la base.
    """
    tarjeta = _obtener_tarjeta(sesion, tarjeta_id)
    if tarjeta.es_semilla:
        raise RecursoDuplicadoError(
            "Las tarjetas del temario no se pueden borrar; sí puedes editarlas."
        )
    sesion.delete(tarjeta)
    sesion.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
