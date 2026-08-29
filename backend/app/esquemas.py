"""Esquemas Pydantic: el contrato público de la API.

Se separan los esquemas de entrada (`...Crear`) de los de salida (`...Salida`)
a propósito: si el frontend pudiera mandar `id`, `es_semilla` o `creada_en`,
podría pisar campos que solo el servidor debe fijar.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# --------------------------------------------------------------------------
# Errores
# --------------------------------------------------------------------------
class DetalleError(BaseModel):
    codigo: str
    mensaje: str
    detalle: dict = Field(default_factory=dict)


class RespuestaError(BaseModel):
    error: DetalleError


# --------------------------------------------------------------------------
# Autenticación
# --------------------------------------------------------------------------
class CredencialesEntrada(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class TokenSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_en_minutos: int
    usuario: UsuarioSalida


class UsuarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nombre: str


# --------------------------------------------------------------------------
# Mazos y tarjetas
# --------------------------------------------------------------------------
class MazoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    nombre: str
    descripcion: str
    unidad: str
    orden: int
    total_tarjetas: int = 0


class MazoCrear(BaseModel):
    slug: str = Field(min_length=2, max_length=60, pattern=r"^[a-z0-9-]+$")
    nombre: str = Field(min_length=2, max_length=140)
    descripcion: str = ""
    unidad: str = ""
    orden: int = 0


class TarjetaBase(BaseModel):
    concepto: str = Field(min_length=2, max_length=180)
    pregunta: str = Field(min_length=2)
    definicion: str = Field(min_length=2)
    notacion: str = ""
    clave_memoria: str = ""
    ejercicio_enunciado: str = Field(min_length=2)
    ejercicio_desarrollo: str = Field(min_length=2)
    ejercicio_respuesta: str = Field(min_length=1)
    formula: str | None = None
    venn: dict | None = None
    fuente: str = ""
    orden: int = 0

    @field_validator("formula")
    @classmethod
    def _formula_vacia_es_nula(cls, valor: str | None) -> str | None:
        """Un campo de texto vacío desde un formulario es «sin fórmula»."""
        if valor is not None and not valor.strip():
            return None
        return valor


class TarjetaCrear(TarjetaBase):
    mazo_id: int


class TarjetaActualizar(BaseModel):
    concepto: str | None = None
    pregunta: str | None = None
    definicion: str | None = None
    notacion: str | None = None
    clave_memoria: str | None = None
    ejercicio_enunciado: str | None = None
    ejercicio_desarrollo: str | None = None
    ejercicio_respuesta: str | None = None
    formula: str | None = None
    venn: dict | None = None
    fuente: str | None = None
    orden: int | None = None


class TarjetaSalida(TarjetaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mazo_id: int
    es_semilla: bool
    creada_en: datetime


# --------------------------------------------------------------------------
# Tablas de verdad
# --------------------------------------------------------------------------
class FormulaEntrada(BaseModel):
    formula: str = Field(min_length=1, max_length=255)


class TablaVerdadSalida(BaseModel):
    formula: str
    formula_normalizada: str
    variables: list[str]
    columnas: list[str]
    filas: list[list[str]]
    clasificacion: str
    numero_filas: int


class EquivalenciaEntrada(BaseModel):
    formula_a: str = Field(min_length=1, max_length=255)
    formula_b: str = Field(min_length=1, max_length=255)


class EquivalenciaSalida(BaseModel):
    formula_a: str
    formula_b: str
    equivalentes: bool
    tabla: TablaVerdadSalida


# --------------------------------------------------------------------------
# Conjuntos
# --------------------------------------------------------------------------
class VennEntrada(BaseModel):
    etiquetas: list[str] = Field(min_length=2, max_length=3)
    conjuntos: dict[str, list[str | int]] | None = None
    cardinalidades: dict[str, int] | None = None
    universo: int | None = None
    titulo: str = ""
    elementos_universo: list[str | int] = Field(default_factory=list)


class RegionesSalida(BaseModel):
    etiquetas: list[str]
    regiones: dict[str, int]


class OperacionConjuntosEntrada(BaseModel):
    a: list[str | int]
    b: list[str | int] = Field(default_factory=list)
    universo: list[str | int] = Field(default_factory=list)


class OperacionConjuntosSalida(BaseModel):
    union: list[str]
    interseccion: list[str]
    diferencia_ab: list[str]
    diferencia_ba: list[str]
    diferencia_simetrica: list[str]
    complemento_a: list[str]
    complemento_b: list[str]
    cardinalidades: dict[str, int]


# --------------------------------------------------------------------------
# Repaso
# --------------------------------------------------------------------------
class CalificacionEntrada(BaseModel):
    calidad: int = Field(ge=0, le=5)


class RepasoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tarjeta_id: int
    repeticiones: int
    factor_facilidad: float
    intervalo_dias: int
    proxima_revision: date
    aciertos: int
    fallos: int


class ProgresoSalida(BaseModel):
    total_tarjetas: int
    estudiadas: int
    pendientes_hoy: int
    aciertos: int
    fallos: int
    porcentaje_acierto: float


TokenSalida.model_rebuild()
