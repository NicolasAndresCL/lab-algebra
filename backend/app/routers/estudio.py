"""Sesión de estudio: qué toca repasar hoy, calificación y progreso."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.dependencias import SesionDep, UsuarioDep
from app.esquemas import CalificacionEntrada, ProgresoSalida, RepasoSalida, TarjetaSalida
from app.excepciones import RecursoNoEncontradoError
from app.modelos import Repaso, Tarjeta
from app.services import repaso as svc_repaso

router = APIRouter(prefix="/estudio", tags=["estudio"])


def _obtener_o_crear_repaso(sesion: SesionDep, usuario_id: int, tarjeta_id: int) -> Repaso:
    registro = sesion.scalar(
        select(Repaso).where(Repaso.usuario_id == usuario_id, Repaso.tarjeta_id == tarjeta_id)
    )
    if registro is None:
        inicial = svc_repaso.estado_inicial()
        registro = Repaso(
            usuario_id=usuario_id,
            tarjeta_id=tarjeta_id,
            repeticiones=inicial.repeticiones,
            factor_facilidad=inicial.factor_facilidad,
            intervalo_dias=inicial.intervalo_dias,
            proxima_revision=inicial.proxima_revision,
        )
        sesion.add(registro)
        sesion.flush()
    return registro


@router.get(
    "/cola",
    response_model=list[TarjetaSalida],
    summary="Tarjetas que toca repasar hoy",
)
def cola_de_estudio(
    sesion: SesionDep,
    usuario: UsuarioDep,
    mazo_id: int | None = Query(default=None),
    limite: int = Query(default=20, ge=1, le=100),
) -> list[Tarjeta]:
    """Devuelve las tarjetas vencidas y las que aún no se han visto nunca.

    Las nunca vistas no tienen fila en `repasos`, así que hace falta un LEFT
    JOIN: con un INNER JOIN la cola de un usuario nuevo saldría vacía.
    """
    hoy = svc_repaso.hoy_utc()
    consulta = (
        select(Tarjeta)
        .outerjoin(
            Repaso,
            (Repaso.tarjeta_id == Tarjeta.id) & (Repaso.usuario_id == usuario.id),
        )
        .where((Repaso.id.is_(None)) | (Repaso.proxima_revision <= hoy))
        .order_by(Repaso.proxima_revision.nulls_first(), Tarjeta.mazo_id, Tarjeta.orden)
        .limit(limite)
    )
    if mazo_id is not None:
        consulta = consulta.where(Tarjeta.mazo_id == mazo_id)
    return list(sesion.scalars(consulta).all())


@router.post(
    "/tarjetas/{tarjeta_id}/calificar",
    response_model=RepasoSalida,
    summary="Calificar un repaso (0 a 5)",
)
def calificar(
    tarjeta_id: int,
    datos: CalificacionEntrada,
    sesion: SesionDep,
    usuario: UsuarioDep,
) -> RepasoSalida:
    tarjeta = sesion.get(Tarjeta, tarjeta_id)
    if tarjeta is None:
        raise RecursoNoEncontradoError("tarjeta", tarjeta_id)

    registro = _obtener_o_crear_repaso(sesion, usuario.id, tarjeta_id)
    nuevo = svc_repaso.calcular(
        calidad=datos.calidad,
        repeticiones=registro.repeticiones,
        factor_facilidad=registro.factor_facilidad,
        intervalo_dias=registro.intervalo_dias,
    )
    registro.repeticiones = nuevo.repeticiones
    registro.factor_facilidad = nuevo.factor_facilidad
    registro.intervalo_dias = nuevo.intervalo_dias
    registro.proxima_revision = nuevo.proxima_revision
    registro.ultima_calidad = datos.calidad
    if datos.calidad >= svc_repaso.UMBRAL_ACIERTO:
        registro.aciertos += 1
    else:
        registro.fallos += 1
    registro.actualizado_en = datetime.now(UTC)

    sesion.commit()
    sesion.refresh(registro)
    return RepasoSalida.model_validate(registro)


@router.get("/progreso", response_model=ProgresoSalida, summary="Progreso del usuario")
def progreso(sesion: SesionDep, usuario: UsuarioDep) -> ProgresoSalida:
    total = sesion.scalar(select(func.count(Tarjeta.id))) or 0
    estudiadas = (
        sesion.scalar(select(func.count(Repaso.id)).where(Repaso.usuario_id == usuario.id)) or 0
    )
    aciertos = (
        sesion.scalar(
            select(func.coalesce(func.sum(Repaso.aciertos), 0)).where(
                Repaso.usuario_id == usuario.id
            )
        )
        or 0
    )
    fallos = (
        sesion.scalar(
            select(func.coalesce(func.sum(Repaso.fallos), 0)).where(
                Repaso.usuario_id == usuario.id
            )
        )
        or 0
    )
    vencidas = (
        sesion.scalar(
            select(func.count(Repaso.id)).where(
                Repaso.usuario_id == usuario.id,
                Repaso.proxima_revision <= svc_repaso.hoy_utc(),
            )
        )
        or 0
    )
    nunca_vistas = total - estudiadas
    intentos = aciertos + fallos
    return ProgresoSalida(
        total_tarjetas=total,
        estudiadas=estudiadas,
        pendientes_hoy=vencidas + nunca_vistas,
        aciertos=aciertos,
        fallos=fallos,
        porcentaje_acierto=round(100 * aciertos / intentos, 1) if intentos else 0.0,
    )
