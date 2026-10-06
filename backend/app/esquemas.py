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
    sistema: dict | None = None
    matriz: dict | None = None
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
    sistema: dict | None = None
    matriz: dict | None = None
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
    # Colores del tema de quien mira el diagrama. Son opcionales: sin ellos se
    # dibuja sobre blanco, que es lo correcto para un cliente que no tenga
    # temas (un script, la documentación de /docs).
    fondo: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    tinta: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")


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
# Sistemas de ecuaciones lineales
# --------------------------------------------------------------------------
class SistemaEntrada(BaseModel):
    """Matriz aumentada de un sistema de 2 × 2 o 3 × 3.

    Los coeficientes viajan como **entero o texto**, nunca como `float`: el
    motor trabaja con fracciones exactas y aceptar un flotante invitaría a
    escribir `0.333` donde el enunciado dice `1/3`. Se admite «1/2», «−3» y
    «0.5» en forma de texto, que `Fraction` convierte sin perder nada.
    """

    matriz: list[list[int | str]] = Field(min_length=2, max_length=3)
    incognitas: list[str] | None = Field(default=None, min_length=2, max_length=3)
    metodo: str | None = None


class SistemaSalida(BaseModel):
    ecuaciones: list[str]
    incognitas: list[str]
    clasificacion: str
    metodo: str
    valores: dict[str, str]
    parametros: list[str]
    formulas: dict[str, str]
    delta: str | None
    pasos: list[str]
    interpretacion: str
    respuesta: str


# --------------------------------------------------------------------------
# Matrices y determinantes
# --------------------------------------------------------------------------
Numero = int | str
"""Entero o texto, nunca `float`: la misma regla que en los sistemas."""


class MatrizEntrada(BaseModel):
    """Una operación de la unidad de matrices: `operacion`, A y lo que pida.

    Todo lo demás es opcional porque depende de la operación: la traza solo
    usa A; la combinación lineal, A, B, k y m; el menor, A, i y j; el
    determinante admite la línea de `desarrollo`. El catálogo de
    `GET /herramientas/matrices/operaciones` dice qué pide cada una.
    """

    operacion: str = Field(min_length=1, max_length=40)
    a: list[list[Numero]] = Field(min_length=1, max_length=4)
    b: list[list[Numero]] | None = Field(default=None, min_length=1, max_length=4)
    k: Numero | None = None
    m: Numero | None = None
    i: Numero | None = None
    j: Numero | None = None
    desarrollo: str | None = Field(default=None, max_length=20)


class MatrizSalida(BaseModel):
    operacion: str
    nombre: str
    notacion: str
    definida: bool
    operandos: dict[str, list[list[str]]]
    ordenes: dict[str, str]
    parametros: dict[str, str]
    resultado: list[list[str]] | None
    valor: str | None
    pasos: list[str]
    tipos: dict[str, list[str]]
    invertible: bool | None
    respuesta: str


class ParametroSalida(BaseModel):
    nombre: str
    etiqueta: str
    tipo: str
    opciones: list[str]
    defecto: str | None


class OperacionMatricesSalida(BaseModel):
    clave: str
    nombre: str
    notacion: str
    usa_b: bool
    parametros: list[ParametroSalida]
    ejemplo: dict
    fuente: str


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
