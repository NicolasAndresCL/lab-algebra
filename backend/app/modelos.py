"""Modelos de datos del laboratorio.

Cuatro entidades: quién estudia (`Usuario`), qué se estudia (`Mazo`,
`Tarjeta`) y cómo va (`Repaso`).
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import JSON as SAJson
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _ahora() -> datetime:
    return datetime.now(UTC)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hash_password: Mapped[str] = mapped_column(String(255))
    nombre: Mapped[str] = mapped_column(String(120), default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_ahora)

    repasos: Mapped[list[Repaso]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )


class Mazo(Base):
    """Agrupación temática de tarjetas (una unidad de la asignatura)."""

    __tablename__ = "mazos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(140))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    unidad: Mapped[str] = mapped_column(String(60), default="")
    orden: Mapped[int] = mapped_column(Integer, default=0)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_ahora)

    tarjetas: Mapped[list[Tarjeta]] = relationship(
        back_populates="mazo",
        cascade="all, delete-orphan",
        order_by="Tarjeta.orden",
    )


class Tarjeta(Base):
    """Una tarjeta de memorización.

    Anverso = el concepto que hay que recordar. Reverso = la definición, más un
    ejercicio **resuelto**: enunciado, desarrollo paso a paso y respuesta. Esa
    terna es el requisito central del laboratorio: memorizar una definición sin
    verla aplicada no sirve para rendir una prueba.
    """

    __tablename__ = "tarjetas"
    __table_args__ = (UniqueConstraint("mazo_id", "concepto", name="uq_tarjeta_concepto"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mazo_id: Mapped[int] = mapped_column(ForeignKey("mazos.id", ondelete="CASCADE"), index=True)
    orden: Mapped[int] = mapped_column(Integer, default=0)

    concepto: Mapped[str] = mapped_column(String(180))
    pregunta: Mapped[str] = mapped_column(Text)
    definicion: Mapped[str] = mapped_column(Text)
    notacion: Mapped[str] = mapped_column(String(255), default="")
    clave_memoria: Mapped[str] = mapped_column(Text, default="")

    ejercicio_enunciado: Mapped[str] = mapped_column(Text)
    ejercicio_desarrollo: Mapped[str] = mapped_column(Text)
    ejercicio_respuesta: Mapped[str] = mapped_column(Text)

    # Fórmula proposicional opcional: si está, la tarjeta muestra su tabla de
    # verdad calculada en vivo por el backend.
    formula: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Especificación opcional de un diagrama de Venn (ver services/venn.py).
    venn: Mapped[dict | None] = mapped_column(SAJson, nullable=True)
    # Sistema lineal opcional: `{"matriz": [[…]], "incognitas": […], "metodo": …}`.
    # Si está, la tarjeta muestra el sistema resuelto paso a paso por el motor
    # de `services/ecuaciones.py`, con aritmética exacta.
    sistema: Mapped[dict | None] = mapped_column(SAJson, nullable=True)

    fuente: Mapped[str] = mapped_column(String(180), default="")
    es_semilla: Mapped[bool] = mapped_column(Boolean, default=False)
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_ahora)

    mazo: Mapped[Mazo] = relationship(back_populates="tarjetas")
    repasos: Mapped[list[Repaso]] = relationship(
        back_populates="tarjeta", cascade="all, delete-orphan"
    )


class Repaso(Base):
    """Estado de repetición espaciada de una tarjeta para un usuario."""

    __tablename__ = "repasos"
    __table_args__ = (
        UniqueConstraint("usuario_id", "tarjeta_id", name="uq_repaso_usuario_tarjeta"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    tarjeta_id: Mapped[int] = mapped_column(
        ForeignKey("tarjetas.id", ondelete="CASCADE"), index=True
    )

    repeticiones: Mapped[int] = mapped_column(Integer, default=0)
    factor_facilidad: Mapped[float] = mapped_column(Float, default=2.5)
    intervalo_dias: Mapped[int] = mapped_column(Integer, default=0)
    # Misma fuente que el resto del sistema de repaso; ver repaso.hoy_utc().
    proxima_revision: Mapped[date] = mapped_column(
        Date, default=lambda: datetime.now(UTC).date()
    )
    ultima_calidad: Mapped[int | None] = mapped_column(Integer, nullable=True)
    aciertos: Mapped[int] = mapped_column(Integer, default=0)
    fallos: Mapped[int] = mapped_column(Integer, default=0)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_ahora)

    usuario: Mapped[Usuario] = relationship(back_populates="repasos")
    tarjeta: Mapped[Tarjeta] = relationship(back_populates="repasos")
