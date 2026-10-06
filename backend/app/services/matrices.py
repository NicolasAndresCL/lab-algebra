"""Motor de matrices y determinantes: la cuarta unidad de la asignatura.

Cubre lo que enseñan los dos PDF de la unidad. «Matrices y determinantes»:
orden y elementos, tipos de matrices, traspuesta, traza, suma, resta, producto
por un escalar, producto de matrices y determinante, con sus propiedades.
«Matrices y determinantes II» (el archivo `Matrices-determ.pdf`): menores,
cofactores, el determinante de 3 × 3 **desarrollado por cualquier fila o
columna**, la matriz adjunta y la **inversa** de 2 × 2 y 3 × 3. La regla de
Cramer, que está en los dos, vive en `ecuaciones.py` como un método más de
resolver un sistema, y usa de aquí `desarrollo_por_cofactores`.

Tres decisiones de diseño:

* **numpy para operar, `Fraction` para contar.** Las matrices son arrays de
  numpy con `dtype=object` cuyas entradas son fracciones exactas. Así se usa
  el álgebra vectorizada de numpy —`A + B`, `k * A`, `A @ B`, `A.T`,
  `np.trace`, `np.tril`— sin perder la exactitud: con `float64` un
  determinante que vale 0 sale como 1e−16 y la pregunta «¿admite inversa?»
  se responde mal. `np.linalg.det` queda fuera por esa razón: solo trabaja en
  coma flotante.
* **Declarativo.** Los tipos de matriz, los requisitos de cada operación, los
  parámetros que pide (escalares, índices, línea de desarrollo), las
  operaciones y los atajos del determinante son **registros de datos**
  (`TIPOS`, `PARAMETROS`, `OPERACIONES`, `ATAJOS`). Añadir un tipo o una
  operación es añadir una entrada; no hay una cadena de `if` que recorrer ni
  que olvidar.
* **Una operación no definida no es un error.** «A·B no está definida porque
  A tiene 3 columnas y B 2 filas» es una respuesta de la unidad —igual que
  «incompatible» lo es en la de ecuaciones— y sale con `definida = False`.
  `MatrizInvalidaError` queda para lo que de verdad está mal escrito.

El determinante se **narra** como lo enseña el curso —por cofactores, en la
fila o columna que se elija— y se **calcula** siempre por el mismo camino
(`determinante`, desarrollo de Laplace). Sarrus queda como opción de
narración: el curso no la enseñó, pero es una comprobación rápida y legítima
en 3 × 3.

Lo que **no** entra, a propósito: el rango, la inversa por Gauss-Jordan y los
determinantes de orden mayor que 3 como operación. El criterio de qué entra
es el temario.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations
from typing import Literal, NamedTuple

import numpy as np

from app.excepciones import MatrizInvalidaError
from app.services import numeros
from app.services.numeros import MENOS, Coeficiente, entre_parentesis, formatear

DIMENSION_MAXIMA = 4
"""Hasta 4 × 4: el ejercicio más grande del PDF (lámina 14) es un 3 × 4."""

ORDENES_DETERMINANTE = (2, 3)
"""El PDF define el determinante de 2 × 2 y da ejemplos de 3 × 3."""

_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _sub(i: int, j: int) -> str:
    """Índices de una entrada en base 1 y como subíndice: (0, 1) → «₁₂»."""
    return f"{i + 1}{j + 1}".translate(_SUBINDICES)


# --------------------------------------------------------------------------
# La matriz
# --------------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class Matriz:
    """Una matriz con nombre y entradas exactas.

    `eq=False` porque la igualdad de dos arrays de numpy es otro array, no un
    booleano: el `__eq__` que genera dataclass rompería con «truth value of an
    array is ambiguous». Para comparar matrices está `np.array_equal`.
    """

    nombre: str
    valores: np.ndarray

    @classmethod
    def desde_datos(cls, filas: list[list[Coeficiente]], nombre: str = "A") -> Matriz:
        """Valida y convierte lo que llega del formulario o de una tarjeta."""
        if not isinstance(filas, list) or not filas or not all(
            isinstance(fila, list) for fila in filas
        ):
            raise MatrizInvalidaError(f"Hacen falta las filas de la matriz {nombre}.")
        anchos = {len(fila) for fila in filas}
        if len(anchos) != 1:
            raise MatrizInvalidaError(
                f"Todas las filas de {nombre} tienen que tener el mismo número de "
                f"entradas; llegaron filas de {', '.join(map(str, sorted(anchos)))}."
            )
        (columnas,) = anchos
        if not 1 <= len(filas) <= DIMENSION_MAXIMA or not 1 <= columnas <= DIMENSION_MAXIMA:
            raise MatrizInvalidaError(
                f"El laboratorio trabaja con matrices de hasta {DIMENSION_MAXIMA} × "
                f"{DIMENSION_MAXIMA}; {nombre} es {len(filas)} × {columnas}."
            )
        valores = np.array(
            [[numeros.a_fraccion(v, MatrizInvalidaError) for v in fila] for fila in filas],
            dtype=object,
        )
        return cls(nombre=nombre, valores=valores)

    @property
    def filas(self) -> int:
        return self.valores.shape[0]

    @property
    def columnas(self) -> int:
        return self.valores.shape[1]

    @property
    def es_cuadrada(self) -> bool:
        return self.filas == self.columnas

    @property
    def orden(self) -> str:
        """«2 × 3»: filas por columnas, como se escribe en clase."""
        return f"{self.filas} × {self.columnas}"

    def como_texto(self) -> list[list[str]]:
        return como_texto(self.valores)


def como_texto(valores: np.ndarray) -> list[list[str]]:
    """Las entradas ya escritas como fracción, listas para viajar en JSON."""
    return [[formatear(v) for v in fila] for fila in valores]


def en_linea(valores: np.ndarray) -> str:
    """«[4 3 3; 2 3 2]»: una matriz dentro de una frase, fila por fila."""
    return "[" + "; ".join(" ".join(fila) for fila in como_texto(valores)) + "]"


# --------------------------------------------------------------------------
# Tipos de matrices (láminas 5 a 20)
# --------------------------------------------------------------------------
def _fuera_de_la_diagonal(a: np.ndarray) -> np.ndarray:
    return a[~np.eye(*a.shape, dtype=bool)]


def _es_diagonal(a: np.ndarray) -> bool:
    return bool(np.all(_fuera_de_la_diagonal(a) == 0))


@dataclass(frozen=True)
class Tipo:
    """Un tipo de matriz: su nombre, su definición y el predicado que la comprueba."""

    nombre: str
    definicion: str
    cumple: Callable[[np.ndarray], bool]
    solo_cuadradas: bool = True


# El orden es el de las láminas. Una misma matriz puede ser de varios tipos a
# la vez —la identidad es escalar, diagonal, triangular y simétrica—, y se
# listan todos: la lámina 12 insiste justo en esa relación.
TIPOS: tuple[Tipo, ...] = (
    Tipo("fila", "tiene una sola fila", lambda a: a.shape[0] == 1, solo_cuadradas=False),
    Tipo("columna", "tiene una sola columna", lambda a: a.shape[1] == 1, solo_cuadradas=False),
    Tipo("nula", "todas sus entradas son 0", lambda a: bool(np.all(a == 0)),
         solo_cuadradas=False),
    Tipo("cuadrada", "tiene tantas filas como columnas (m = n)", lambda a: True),
    Tipo("identidad", "1 en la diagonal principal y 0 en el resto",
         lambda a: np.array_equal(a, np.eye(a.shape[0], dtype=int))),
    Tipo("escalar", "diagonal con todos los elementos de la diagonal iguales (k·Iₙ)",
         lambda a: _es_diagonal(a) and len(set(np.diagonal(a))) == 1),
    Tipo("diagonal", "aᵢⱼ = 0 para todo i ≠ j", _es_diagonal),
    Tipo("triangular superior", "aᵢⱼ = 0 para i > j (ceros bajo la diagonal)",
         lambda a: bool(np.all(np.tril(a, -1) == 0))),
    Tipo("triangular inferior", "aᵢⱼ = 0 para i < j (ceros sobre la diagonal)",
         lambda a: bool(np.all(np.triu(a, 1) == 0))),
    Tipo("simétrica", "Aᵀ = A", lambda a: np.array_equal(a.T, a)),
    Tipo("antisimétrica", "Aᵀ = −A", lambda a: np.array_equal(a.T, -a)),
)


def clasificar(valores: np.ndarray) -> list[str]:
    """Todos los tipos de `TIPOS` que cumple la matriz, en el orden de las láminas."""
    cuadrada = valores.shape[0] == valores.shape[1]
    return [
        tipo.nombre
        for tipo in TIPOS
        if (cuadrada or not tipo.solo_cuadradas) and tipo.cumple(valores)
    ]


# --------------------------------------------------------------------------
# Determinante, menores y cofactores
# (I: láminas 35 a 43; II: láminas 1 a 11)
# --------------------------------------------------------------------------
def submatriz(a: np.ndarray, i: int, j: int) -> np.ndarray:
    """Lo que queda al eliminar la fila i y la columna j (en base 0)."""
    return np.delete(np.delete(a, i, axis=0), j, axis=1)


def determinante(a: np.ndarray) -> Fraction:
    """Determinante exacto por desarrollo de Laplace sobre la primera fila.

    Es la definición de la lámina 1 de la segunda parte, aplicada de forma
    recursiva: con `Fraction` no hay redondeo que justifique un método
    numérico, y para el tamaño de estas matrices el coste es irrelevante. Lo
    que el curso limita a 2 × 2 y 3 × 3 lo limitan los `Requisito` de cada
    operación, no esta función.
    """
    n = a.shape[0]
    if n == 1:
        return Fraction(a[0, 0])
    if n == 2:
        return a[0, 0] * a[1, 1] - a[0, 1] * a[1, 0]
    return sum(
        (cofactor(a, 0, j) * a[0, j] for j in range(n) if a[0, j] != 0), Fraction(0)
    )


def menor(a: np.ndarray, i: int, j: int) -> Fraction:
    """Mᵢⱼ: el determinante de lo que queda al eliminar la fila i y la columna j."""
    return determinante(submatriz(a, i, j))


def signo(i: int, j: int) -> int:
    """(−1)^(i+j) con índices en base 0, que tiene la misma paridad que en base 1."""
    return 1 if (i + j) % 2 == 0 else -1


def cofactor(a: np.ndarray, i: int, j: int) -> Fraction:
    """Aᵢⱼ = (−1)^(i+j) · Mᵢⱼ (lámina 7 de la segunda parte)."""
    return signo(i, j) * menor(a, i, j)


def matriz_de_cofactores(a: np.ndarray) -> np.ndarray:
    n = a.shape[0]
    return np.array([[cofactor(a, i, j) for j in range(n)] for i in range(n)], dtype=object)


def adjunta(a: np.ndarray) -> np.ndarray:
    """adj(A) = Cᵀ, la traspuesta de la matriz de cofactores (lámina 21)."""
    return matriz_de_cofactores(a).T.copy()


def inversa(a: np.ndarray) -> np.ndarray:
    """A⁻¹ = (1 / det A) · adj(A). Quien llama comprueba antes que det A ≠ 0."""
    return adjunta(a) * (Fraction(1) / determinante(a))


LINEAS: tuple[str, ...] = (
    "fila 1", "fila 2", "fila 3", "columna 1", "columna 2", "columna 3",
)
"""Por dónde se puede desarrollar un 3 × 3 (lámina 9 de la segunda parte)."""


def _posiciones(linea: str, n: int) -> list[tuple[int, int]]:
    """Las posiciones (i, j) de una línea: «fila 2» → (1, 0), (1, 1), (1, 2)."""
    eje, numero = linea.split()
    k = int(numero) - 1
    return [(k, t) if eje == "fila" else (t, k) for t in range(n)]


def _barras(a: np.ndarray) -> str:
    """«|2 4; −2 −3|»: un determinante dentro de una frase."""
    return "|" + "; ".join(" ".join(fila) for fila in como_texto(a)) + "|"


def _menor_2x2_escrito(nombre: str, m: np.ndarray) -> str:
    """«M₁₁ = |2 4; −2 −3| = (2)(−3) − (4)(−2) = 2»."""
    valor = determinante(m)
    return (
        f"{nombre} = {_barras(m)} = ({formatear(m[0, 0])})({formatear(m[1, 1])}) − "
        f"({formatear(m[0, 1])})({formatear(m[1, 0])}) = {formatear(valor)}"
    )


def desarrollo_por_cofactores(
    a: np.ndarray, linea: str = "fila 1", nombre: str = "det A"
) -> tuple[Fraction, list[str]]:
    """Narra el desarrollo de un 3 × 3 por una fila o columna, como en la lámina 10.

    Cada elemento de la línea se multiplica por su cofactor. Los elementos que
    valen 0 se dicen y se saltan: es justo por lo que conviene elegir la línea
    con más ceros (lámina 6). Devuelve el valor **calculado por `determinante`**
    —no por esta narración— y los pasos; un test exige que coincidan para las
    seis líneas.
    """
    posiciones = _posiciones(linea, 3)
    pasos = [
        f"Desarrollo por la {linea}: cada elemento por su cofactor, "
        f"Aᵢⱼ = (−1)^(i+j)·Mᵢⱼ.",
    ]
    terminos: list[str] = []
    for i, j in posiciones:
        elemento = a[i, j]
        par = "par" if (i + j) % 2 == 0 else "impar"
        if elemento == 0:
            pasos.append(f"a{_sub(i, j)} = 0: su término vale 0 y no hace falta su menor.")
            continue
        m = menor(a, i, j)
        pasos.append(
            f"{_menor_2x2_escrito(f'M{_sub(i, j)}', submatriz(a, i, j))}; "
            f"{i + 1} + {j + 1} es {par} → A{_sub(i, j)} = {formatear(signo(i, j) * m)}."
        )
        terminos.append(f"{entre_parentesis(elemento)}·{entre_parentesis(signo(i, j) * m)}")
    valor = determinante(a)
    pasos.append(f"{nombre} = {' + '.join(terminos) or '0'} = {formatear(valor)}.")
    return valor, pasos


def _producto(factores: tuple[Fraction, ...]) -> Fraction:
    return math.prod(factores, start=Fraction(1))


def _diagonales_de_sarrus(a: np.ndarray) -> tuple[list[tuple], list[tuple]]:
    """Las tres diagonales que «bajan» (suman) y las tres que «suben» (restan)."""
    bajan = [tuple(a[i, (i + k) % 3] for i in range(3)) for k in range(3)]
    suben = [tuple(a[i, (k - i) % 3] for i in range(3)) for k in range(3)]
    return bajan, suben


def _producto_escrito(factores: tuple[Fraction, ...]) -> str:
    return "".join(f"({formatear(f)})" for f in factores)


def _filas(a: np.ndarray) -> list[tuple[str, np.ndarray]]:
    return [(f"fila {i + 1}", a[i, :]) for i in range(a.shape[0])]


def _columnas(a: np.ndarray) -> list[tuple[str, np.ndarray]]:
    return [(f"columna {j + 1}", a[:, j]) for j in range(a.shape[1])]


def _proporcionales(u: np.ndarray, v: np.ndarray) -> bool:
    """Dos líneas son proporcionales si todos sus «productos cruzados» se anulan."""
    return all(u[i] * v[j] == u[j] * v[i] for i, j in combinations(range(len(u)), 2))


def _pares_paralelos(a: np.ndarray) -> list[tuple[tuple[str, np.ndarray], ...]]:
    """Fila con fila y columna con columna: las «líneas paralelas» del PDF."""
    return [*combinations(_filas(a), 2), *combinations(_columnas(a), 2)]


def _linea_nula(a: np.ndarray) -> str | None:
    return next(
        (nombre for nombre, linea in [*_filas(a), *_columnas(a)] if np.all(linea == 0)), None
    )


def _lineas_iguales(a: np.ndarray) -> str | None:
    return next(
        (f"la {p[0]} y la {q[0]}" for p, q in _pares_paralelos(a)
         if np.array_equal(p[1], q[1])),
        None,
    )


def _lineas_proporcionales(a: np.ndarray) -> str | None:
    return next(
        (f"la {p[0]} y la {q[0]}" for p, q in _pares_paralelos(a)
         if _proporcionales(p[1], q[1])),
        None,
    )


def _es_triangular(a: np.ndarray) -> str | None:
    tipos = clasificar(a)
    return next((t for t in ("triangular superior", "triangular inferior") if t in tipos), None)


@dataclass(frozen=True)
class Atajo:
    """Una propiedad del determinante que permite saber el valor sin la fórmula.

    `detecta` devuelve el detalle para la frase («la fila 3») o `None` si la
    propiedad no aplica. `predice` da el valor que la propiedad anuncia. El
    motor **calcula siempre por la fórmula** y usa el atajo solo para
    narrarlo; un test comprueba que lo predicho y lo calculado coinciden en
    todos los casos, que es justo lo que afirma la propiedad.
    """

    propiedad: int
    detecta: Callable[[np.ndarray], str | None]
    explica: Callable[[str], str]
    predice: Callable[[np.ndarray], Fraction]


# Del más específico al más general: una línea nula es también proporcional a
# cualquier otra, y unas líneas iguales son proporcionales con factor 1. Se
# narra solo el primero que aplica, que es el que miraría alguien a mano.
ATAJOS: tuple[Atajo, ...] = (
    Atajo(4, _linea_nula,
          lambda d: f"la {d} de A es toda de ceros, así que el determinante es nulo",
          lambda a: Fraction(0)),
    Atajo(3, _lineas_iguales,
          lambda d: f"en A, {d} son iguales, así que el determinante es nulo",
          lambda a: Fraction(0)),
    Atajo(5, _lineas_proporcionales,
          lambda d: f"en A, {d} son proporcionales, así que el determinante es nulo",
          lambda a: Fraction(0)),
    Atajo(9, _es_triangular,
          lambda d: f"A es {d}, así que el determinante es el producto de su diagonal",
          lambda a: _producto(tuple(np.diagonal(a)))),
)


def atajo_aplicable(a: np.ndarray) -> tuple[Atajo, str] | None:
    """El primer atajo de `ATAJOS` que aplica a la matriz, con su detalle."""
    return next(
        ((atajo, detalle) for atajo in ATAJOS if (detalle := atajo.detecta(a)) is not None),
        None,
    )


# --------------------------------------------------------------------------
# Operaciones: entrada, requisitos y cálculo
# --------------------------------------------------------------------------
TipoParametro = Literal["escalar", "indice", "opcion"]


@dataclass(frozen=True)
class Parametro:
    """Un dato que pide una operación además de las matrices.

    `tipo` decide cómo se lee: un `escalar` es una fracción exacta; un
    `indice` es una fila o columna en base 1, que tiene que existir en A; una
    `opcion` es uno de los textos de `opciones`. Sin `defecto`, es
    obligatorio. La interfaz construye el campo de cada parámetro a partir de
    `como_dict`, así que un parámetro nuevo tampoco toca el frontend.
    """

    nombre: str
    etiqueta: str
    tipo: TipoParametro
    opciones: tuple[str, ...] = ()
    defecto: str | None = None

    def leer(self, valor: object, a: Matriz) -> Fraction | int | str:
        if valor is None:
            if self.defecto is None:
                raise MatrizInvalidaError(f"Falta {self.etiqueta}.")
            valor = self.defecto
        if self.tipo == "escalar":
            return numeros.a_fraccion(valor, MatrizInvalidaError)
        if self.tipo == "opcion":
            if valor not in self.opciones:
                raise MatrizInvalidaError(
                    f"«{valor}» no es una opción de {self.etiqueta}. Elige entre: "
                    f"{', '.join(self.opciones)}."
                )
            return valor
        try:
            indice = int(str(valor).strip())
        except ValueError:
            raise MatrizInvalidaError(f"«{valor}» no es un número de {self.etiqueta}.")
        if not 1 <= indice <= a.filas:
            raise MatrizInvalidaError(
                f"A es {a.orden}: {self.etiqueta} tiene que estar entre 1 y {a.filas}."
            )
        return indice

    def como_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "etiqueta": self.etiqueta,
            "tipo": self.tipo,
            "opciones": list(self.opciones),
            "defecto": self.defecto,
        }


PARAMETROS: dict[str, Parametro] = {
    parametro.nombre: parametro
    for parametro in (
        Parametro("k", "el escalar k", "escalar"),
        Parametro("m", "el escalar m", "escalar"),
        Parametro("i", "la fila i", "indice"),
        Parametro("j", "la columna j", "indice"),
        Parametro("desarrollo", "la línea de desarrollo", "opcion",
                  opciones=(*LINEAS, "Sarrus"), defecto="fila 1"),
    )
}


@dataclass(frozen=True, eq=False)
class Entrada:
    """Los operandos ya validados: A, B si la operación la usa, y sus parámetros."""

    a: Matriz
    b: Matriz | None = None
    parametros: dict[str, Fraction | int | str] = field(default_factory=dict)

    @property
    def matrices(self) -> dict[str, Matriz]:
        return {mat.nombre: mat for mat in (self.a, self.b) if mat is not None}

    @property
    def k(self) -> Fraction | None:
        return self.parametros.get("k")

    @property
    def m(self) -> Fraction | None:
        return self.parametros.get("m")

    @property
    def posicion(self) -> tuple[int, int]:
        """(i, j) en base 0, para las operaciones que piden un elemento."""
        return self.parametros["i"] - 1, self.parametros["j"] - 1


class Calculo(NamedTuple):
    """Lo que devuelve cada operación: una matriz **o** un número, y el camino.

    `respuesta` solo la usan las operaciones cuyo resultado no es ni una
    matriz ni un número (clasificar); las demás la dejan en `None` y la frase
    final se arma sola a partir del resultado.
    """

    matriz: np.ndarray | None
    valor: Fraction | None
    pasos: list[str]
    respuesta: str | None = None


@dataclass(frozen=True)
class Requisito:
    """Una condición para que la operación esté definida, y cómo decir que falla."""

    cumple: Callable[[Entrada], bool]
    motivo: Callable[[Entrada], str]


MISMO_ORDEN = Requisito(
    lambda e: e.a.valores.shape == e.b.valores.shape,
    lambda e: f"Solo se suman o restan matrices del mismo orden, y A es {e.a.orden} "
              f"mientras que B es {e.b.orden}.",
)
A_CUADRADA = Requisito(
    lambda e: e.a.es_cuadrada,
    lambda e: f"Solo se define para matrices cuadradas, y A es {e.a.orden}.",
)
ENCADENAN_AB = Requisito(
    lambda e: e.a.columnas == e.b.filas,
    lambda e: f"Para multiplicar A·B el número de columnas de A ({e.a.columnas}) tiene "
              f"que ser igual al número de filas de B ({e.b.filas}).",
)
ENCADENAN_BA = Requisito(
    lambda e: e.b.columnas == e.a.filas,
    lambda e: f"Para multiplicar B·A el número de columnas de B ({e.b.columnas}) tiene "
              f"que ser igual al número de filas de A ({e.a.filas}).",
)
ORDEN_DE_DETERMINANTE = Requisito(
    lambda e: e.a.filas in ORDENES_DETERMINANTE,
    lambda e: f"El curso calcula determinantes de 2 × 2 y de 3 × 3, y A es {e.a.orden}.",
)
# Va siempre DESPUÉS de A_CUADRADA y ORDEN_DE_DETERMINANTE: los requisitos se
# comprueban en orden y este calcula el determinante, que necesita los otros dos.
A_INVERTIBLE = Requisito(
    lambda e: determinante(e.a.valores) != 0,
    lambda e: "det A = 0: A es singular y no tiene inversa (propiedad 10 y lámina 18 "
              "de la segunda parte).",
)


# --------------------------------------------------------------------------
# Cómo se narra cada operación
# --------------------------------------------------------------------------
def _por_filas(resultado: np.ndarray, expresion: Callable[[int, int], str]) -> list[str]:
    """«Fila 1: 1 + 3 = 4 · 2 + 1 = 3» — una línea por fila del resultado."""
    return [
        f"Fila {i + 1}: " + " · ".join(
            f"{expresion(i, j)} = {formatear(resultado[i, j])}"
            for j in range(resultado.shape[1])
        )
        for i in range(resultado.shape[0])
    ]


def _combinacion(e: Entrada, k: Fraction, m: Fraction, frase: str) -> Calculo:
    """kA + mB entrada a entrada. La suma (1, 1) y la resta (1, −1) son casos suyos."""
    a, b = e.a.valores, e.b.valores
    resultado = k * a + m * b

    def termino(factor: Fraction, valor: Fraction, primero: bool) -> str:
        """«7 + (−5)», como en la lámina 23: solo el primer sumando va sin paréntesis."""
        if factor != 1:
            return f"{entre_parentesis(factor)}·{entre_parentesis(valor)}"
        return formatear(valor) if primero else entre_parentesis(valor)

    def expresion(i: int, j: int) -> str:
        if m == -1 and k == 1:
            return f"{formatear(a[i, j])} {MENOS} {entre_parentesis(b[i, j])}"
        return f"{termino(k, a[i, j], primero=True)} + {termino(m, b[i, j], primero=False)}"

    pasos = [
        f"A y B son las dos {e.a.orden}: {frase}",
        *_por_filas(resultado, expresion),
    ]
    return Calculo(resultado, None, pasos)


def _suma(e: Entrada) -> Calculo:
    return _combinacion(e, Fraction(1), Fraction(1),
                        "se suman las entradas que ocupan la misma posición.")


def _resta(e: Entrada) -> Calculo:
    return _combinacion(e, Fraction(1), Fraction(-1),
                        "a cada entrada de A se le resta la de B en la misma posición.")


def _combinacion_lineal(e: Entrada) -> Calculo:
    return _combinacion(
        e, e.k, e.m,
        f"cada entrada es {formatear(e.k)} veces la de A más {formatear(e.m)} veces la de B.",
    )


def _escalar(e: Entrada) -> Calculo:
    a = e.a.valores
    resultado = e.k * a
    pasos = [
        f"Cada entrada de A se multiplica por k = {formatear(e.k)}; el orden no "
        f"cambia ({e.a.orden}).",
        *_por_filas(
            resultado, lambda i, j: f"{entre_parentesis(e.k)}·{entre_parentesis(a[i, j])}"
        ),
    ]
    return Calculo(resultado, None, pasos)


def _multiplicar(izquierda: Matriz, derecha: Matriz) -> Calculo:
    """Fila de la izquierda por columna de la derecha, como en la lámina 29."""
    p, q = izquierda.valores, derecha.valores
    resultado = p @ q
    nombre = f"{izquierda.nombre}{derecha.nombre}"
    pasos = [
        f"{izquierda.nombre} es {izquierda.orden} y {derecha.nombre} es {derecha.orden}: "
        f"columnas de {izquierda.nombre} = filas de {derecha.nombre} = {p.shape[1]}, así "
        f"que {nombre} está definida y es {resultado.shape[0]} × {resultado.shape[1]}.",
        f"Cada entrada cᵢⱼ es la fila i de {izquierda.nombre} por la columna j de "
        f"{derecha.nombre}, término a término, y sumando.",
        *(
            f"c{_sub(i, j)} = "
            + " + ".join(
                f"{entre_parentesis(x)}·{entre_parentesis(y)}"
                for x, y in zip(p[i, :], q[:, j], strict=True)
            )
            + f" = {formatear(resultado[i, j])}"
            for i in range(resultado.shape[0])
            for j in range(resultado.shape[1])
        ),
    ]
    return Calculo(resultado, None, pasos)


def _producto_ab(e: Entrada) -> Calculo:
    calculo = _multiplicar(e.a, e.b)
    if ENCADENAN_BA.cumple(e) and not np.array_equal(e.b.valores @ e.a.valores, calculo.matriz):
        calculo.pasos.append(
            f"Ojo: BA = {en_linea(e.b.valores @ e.a.valores)} no es igual a AB. El "
            f"producto de matrices no es conmutativo (lámina 31)."
        )
    return calculo


def _producto_ba(e: Entrada) -> Calculo:
    return _multiplicar(e.b, e.a)


def _traspuesta(e: Entrada) -> Calculo:
    a = e.a.valores
    pasos = [
        f"La fila i de A pasa a ser la columna i de Aᵀ, así que un {e.a.orden} se "
        f"convierte en un {e.a.columnas} × {e.a.filas}.",
        *(
            f"Fila {i + 1} de A ({', '.join(como_texto(a)[i])}) → columna {i + 1} de Aᵀ."
            for i in range(e.a.filas)
        ),
    ]
    return Calculo(a.T.copy(), None, pasos)


def _clasificar(e: Entrada) -> Calculo:
    """Recorre `TIPOS` y dice, definición por definición, cuáles cumple A."""
    a = e.a.valores
    aplicables = [t for t in TIPOS if e.a.es_cuadrada or not t.solo_cuadradas]
    tipos = clasificar(a)
    pasos = [
        f"A es {e.a.orden}."
        + ("" if e.a.es_cuadrada else " No es cuadrada: solo pueden aplicar los tipos "
           "que no lo exigen."),
        *(
            f"{'✓' if tipo.nombre in tipos else '✗'} {tipo.nombre}: {tipo.definicion}."
            for tipo in aplicables
        ),
    ]
    respuesta = (
        f"A es {', '.join(tipos)}." if tipos
        else f"A no es de ninguno de los tipos especiales: es una matriz {e.a.orden}."
    )
    return Calculo(None, None, pasos, respuesta)


def _suma_escrita(valores: list[Fraction]) -> str:
    """«2 + 3 + 6», «−1 + 5», «4 − 2»: como se escribe una suma a mano."""
    primero, *resto = valores
    return formatear(primero) + "".join(
        f" {MENOS} {formatear(-v)}" if v < 0 else f" + {formatear(v)}" for v in resto
    )


def _traza(e: Entrada) -> Calculo:
    diagonal = list(np.diagonal(e.a.valores))
    valor = sum(diagonal, Fraction(0))
    pasos = [
        f"La diagonal principal de A es {', '.join(map(formatear, diagonal))}.",
        f"tr(A) = {_suma_escrita(diagonal)} = {formatear(valor)}.",
    ]
    return Calculo(None, valor, pasos)


def _determinante(e: Entrada) -> Calculo:
    a = e.a.valores
    valor = determinante(a)
    if e.a.filas == 2:
        pasos = [
            "det A = a₁₁a₂₂ − a₁₂a₂₁ (el producto de la diagonal principal menos el "
            "de la secundaria).",
            f"det A = ({formatear(a[0, 0])})({formatear(a[1, 1])}) − "
            f"({formatear(a[0, 1])})({formatear(a[1, 0])}) = {formatear(valor)}.",
        ]
    elif e.parametros.get("desarrollo") == "Sarrus":
        bajan, suben = _diagonales_de_sarrus(a)
        suma_bajan = sum(map(_producto, bajan), Fraction(0))
        suma_suben = sum(map(_producto, suben), Fraction(0))
        pasos = [
            "Regla de Sarrus: se suman los productos de las tres diagonales que bajan "
            "y se restan los de las tres que suben. Ojo: el curso enseña el desarrollo "
            "por cofactores; Sarrus es un atajo que solo vale en 3 × 3.",
            f"Bajan: {' + '.join(map(_producto_escrito, bajan))} = {formatear(suma_bajan)}.",
            f"Suben: {' + '.join(map(_producto_escrito, suben))} = {formatear(suma_suben)}.",
            f"det A = {formatear(suma_bajan)} − {entre_parentesis(suma_suben)} = "
            f"{formatear(valor)}.",
        ]
    else:
        _, pasos = desarrollo_por_cofactores(a, e.parametros.get("desarrollo", "fila 1"))
    if (aplicable := atajo_aplicable(a)) is not None:
        atajo, detalle = aplicable
        pasos.append(
            f"Atajo (propiedad {atajo.propiedad}): {atajo.explica(detalle)} → "
            f"{formatear(atajo.predice(a))}, que coincide con la fórmula."
        )
    pasos.append(
        f"det A = {formatear(valor)} ≠ 0 → A admite inversa (propiedad 10)."
        if valor != 0
        else "det A = 0 → A es singular: no admite inversa (propiedad 10)."
    )
    return Calculo(None, valor, pasos)


def _quitar(e: Entrada) -> tuple[int, int, np.ndarray, str]:
    """Posición pedida, la submatriz que queda y la frase que cuenta qué se quitó."""
    i, j = e.posicion
    resto = submatriz(e.a.valores, i, j)
    return i, j, resto, f"Se eliminan la fila {i + 1} y la columna {j + 1} de A"


def _menor_escrito(i: int, j: int, resto: np.ndarray) -> str:
    """El menor narrado: un 2 × 2 con su fórmula, o el número que queda en un 2 × 2."""
    if resto.shape[0] == 1:
        return f"M{_sub(i, j)} = {formatear(resto[0, 0])}"
    return _menor_2x2_escrito(f"M{_sub(i, j)}", resto)


def _menor(e: Entrada) -> Calculo:
    """Láminas 3 y 4 de la segunda parte."""
    i, j, resto, frase = _quitar(e)
    valor = determinante(resto)
    pasos = [f"{frase}: queda {_barras(resto)}.", f"{_menor_escrito(i, j, resto)}."]
    return Calculo(None, valor, pasos, f"M{_sub(i, j)} = {formatear(valor)}.")


def _cofactor(e: Entrada) -> Calculo:
    """Lámina 7 de la segunda parte: el menor con el signo de su posición."""
    i, j, resto, frase = _quitar(e)
    m = determinante(resto)
    valor = signo(i, j) * m
    paridad = "par" if (i + j) % 2 == 0 else "impar"
    pasos = [
        f"{frase}: queda {_barras(resto)}.",
        f"{_menor_escrito(i, j, resto)}.",
        f"i + j = {i + 1} + {j + 1} = {i + j + 2} es {paridad} → "
        f"(−1)^{i + j + 2} = {formatear(signo(i, j))}.",
        f"A{_sub(i, j)} = ({formatear(signo(i, j))})·{entre_parentesis(m)} = "
        f"{formatear(valor)}.",
    ]
    return Calculo(None, valor, pasos, f"A{_sub(i, j)} = {formatear(valor)}.")


def _pasos_de_cofactores(a: np.ndarray) -> list[str]:
    """Una línea por cofactor, como la tabla de las láminas 23 y 24."""
    n = a.shape[0]
    return [
        f"C{_sub(i, j)} = {'+' if signo(i, j) > 0 else MENOS}"
        f"{_barras(submatriz(a, i, j))} = {formatear(cofactor(a, i, j))}"
        for i in range(n)
        for j in range(n)
    ]


def _cofactores(e: Entrada) -> Calculo:
    a = e.a.valores
    pasos = [
        "Cada entrada de C es el cofactor de la misma posición: "
        "Cᵢⱼ = (−1)^(i+j)·Mᵢⱼ, con el signo + en las posiciones de suma par.",
        *_pasos_de_cofactores(a),
    ]
    return Calculo(matriz_de_cofactores(a), None, pasos)


def _adjunta(e: Entrada) -> Calculo:
    a = e.a.valores
    if e.a.filas == 2:
        pasos = [
            "En 2 × 2 (lámina 17 de la segunda parte): se intercambian los elementos "
            "de la diagonal principal y se cambia el signo de los de la secundaria.",
            f"Diagonal principal: {formatear(a[0, 0])} y {formatear(a[1, 1])} se "
            f"intercambian. Secundaria: {formatear(a[0, 1])} → {formatear(-a[0, 1])} y "
            f"{formatear(a[1, 0])} → {formatear(-a[1, 0])}.",
        ]
    else:
        pasos = [
            "Paso 1: la matriz de cofactores C.",
            *_pasos_de_cofactores(a),
            f"C = {en_linea(matriz_de_cofactores(a))}.",
            "Paso 2: adj(A) = Cᵀ, la traspuesta de C: la fila i de C pasa a ser la "
            "columna i de adj(A).",
        ]
    return Calculo(adjunta(a), None, pasos)


def _inversa(e: Entrada) -> Calculo:
    """Láminas 19 (2 × 2) y 21 a 27 (3 × 3) de la segunda parte.

    Termina comprobando A·A⁻¹ = I con el producto de numpy: es la prueba que
    no depende de nadie, como sustituir la solución en un sistema.
    """
    a = e.a.valores
    det = determinante(a)
    adj = adjunta(a)
    resultado = inversa(a)
    if e.a.filas == 2:
        pasos = [
            f"det A = ({formatear(a[0, 0])})({formatear(a[1, 1])}) − "
            f"({formatear(a[0, 1])})({formatear(a[1, 0])}) = {formatear(det)} ≠ 0, así "
            f"que A es invertible.",
            "A⁻¹ = (1/det A)·[a₂₂ −a₁₂; −a₂₁ a₁₁]: se intercambia la diagonal "
            "principal y se cambia el signo de la secundaria.",
            f"A⁻¹ = (1/{formatear(det)})·{en_linea(adj)}.",
        ]
    else:
        _, pasos_det = desarrollo_por_cofactores(a, "fila 1")
        pasos = [
            "Paso 1: el determinante. Si fuera 0, se pararía aquí.",
            *pasos_det,
            "Paso 2: la matriz de cofactores C.",
            *_pasos_de_cofactores(a),
            f"Paso 3: adj(A) = Cᵀ = {en_linea(adj)}.",
            f"Paso 4: A⁻¹ = (1/{formatear(det)})·adj(A), entrada por entrada.",
        ]
    identidad = np.array_equal(a @ resultado, np.eye(e.a.filas, dtype=int))
    pasos.append(
        "Comprobación: A·A⁻¹ = I ✓" if identidad
        else "Comprobación: A·A⁻¹ no da I — esto es un error del motor."
    )
    return Calculo(resultado, None, pasos)


# --------------------------------------------------------------------------
# El catálogo de operaciones
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Operacion:
    """Una operación del temario, descrita como datos.

    `ejemplo` es el ejercicio de la lámina con el que la herramienta abre la
    pestaña: la interfaz construye su selector **a partir de este catálogo**,
    así que una operación nueva aparece en pantalla sin tocar el frontend.
    """

    clave: str
    nombre: str
    notacion: str
    resolver: Callable[[Entrada], Calculo]
    usa_b: bool = False
    parametros: tuple[str, ...] = ()
    requisitos: tuple[Requisito, ...] = ()
    ejemplo: dict = field(default_factory=dict)
    fuente: str = ""
    sin_resultado: str = "no está definida para estas matrices"
    informa_inversa: bool = False

    def como_dict(self) -> dict:
        return {
            "clave": self.clave,
            "nombre": self.nombre,
            "notacion": self.notacion,
            "usa_b": self.usa_b,
            "parametros": [PARAMETROS[nombre].como_dict() for nombre in self.parametros],
            "ejemplo": self.ejemplo,
            "fuente": self.fuente,
        }


# Las operaciones que piden un elemento de una matriz de 2 × 2 o 3 × 3.
CUADRADA_DEL_TEMARIO = (A_CUADRADA, ORDEN_DE_DETERMINANTE)
SEGUNDA = "Matrices y determinantes II"


OPERACIONES: dict[str, Operacion] = {
    operacion.clave: operacion
    for operacion in (
        Operacion(
            "clasificar", "Tipo de matriz", "tipo de A", _clasificar,
            ejemplo={"a": [[1, 0, 3], [0, 2, -1], [3, -1, 0]]},
            fuente="Matrices y determinantes, lámina 15",
        ),
        Operacion(
            "suma", "Suma", "A + B", _suma, usa_b=True, requisitos=(MISMO_ORDEN,),
            ejemplo={"a": [[1, 2, 0], [7, 3, -4]], "b": [[3, 1, 3], [-5, 0, 6]]},
            fuente="Matrices y determinantes, lámina 23",
        ),
        Operacion(
            "resta", "Resta", "A − B", _resta, usa_b=True, requisitos=(MISMO_ORDEN,),
            ejemplo={"a": [[4, 5, -2], [10, 6, 8], [9, -7, -1]],
                     "b": [[5, 1, 3], [-1, 2, 6], [4, 9, -8]]},
            fuente="Matrices y determinantes, lámina 27",
        ),
        Operacion(
            "escalar", "Producto por un escalar", "k·A", _escalar, parametros=("k",),
            ejemplo={"a": [[1, 2], [3, 4]], "k": "3"},
            fuente="Matrices y determinantes, lámina 25",
        ),
        Operacion(
            "combinacion", "Combinación lineal", "k·A + m·B", _combinacion_lineal,
            usa_b=True, parametros=("k", "m"), requisitos=(MISMO_ORDEN,),
            ejemplo={"a": [[1, 0, 2], [-3, 4, 5]], "b": [[7, 2, -1], [4, 0, 3]],
                     "k": "-1", "m": "2"},
            fuente="Matrices y determinantes, lámina 25",
        ),
        Operacion(
            "producto", "Producto", "A·B", _producto_ab, usa_b=True,
            requisitos=(ENCADENAN_AB,),
            ejemplo={"a": [[2, 1, 5], [3, 0, 4]], "b": [[-1, 7, 8], [4, 6, 0], [5, 7, 3]]},
            fuente="Matrices y determinantes, lámina 30",
        ),
        Operacion(
            "producto_ba", "Producto en el otro orden", "B·A", _producto_ba, usa_b=True,
            requisitos=(ENCADENAN_BA,),
            ejemplo={"a": [[1, 2], [3, 4]], "b": [[-2, 0], [-1, 3]]},
            fuente="Matrices y determinantes, lámina 31",
        ),
        Operacion(
            "traspuesta", "Traspuesta", "Aᵀ", _traspuesta,
            ejemplo={"a": [[1, 4, 8, 2], [0, 7, 3, 6], [-2, -1, 2, 1]]},
            fuente="Matrices y determinantes, lámina 14",
        ),
        Operacion(
            "traza", "Traza", "tr(A)", _traza, requisitos=(A_CUADRADA,),
            ejemplo={"a": [[2, 5, 7], [1, 3, 4], [0, -2, 6]]},
            fuente="Matrices y determinantes, lámina 17",
        ),
        Operacion(
            "determinante", "Determinante", "det(A)", _determinante,
            parametros=("desarrollo",), requisitos=CUADRADA_DEL_TEMARIO,
            informa_inversa=True,
            ejemplo={"a": [[3, 4, -1], [4, 6, 2], [8, -2, 3]], "desarrollo": "fila 1"},
            fuente=f"{SEGUNDA}, lámina 10",
        ),
        Operacion(
            "menor", "Menor de un elemento", "Mᵢⱼ", _menor,
            parametros=("i", "j"), requisitos=CUADRADA_DEL_TEMARIO,
            ejemplo={"a": [[2, -1, 3], [-2, 5, 1], [0, 6, -9]], "i": 1, "j": 2},
            fuente=f"{SEGUNDA}, lámina 3",
        ),
        Operacion(
            "cofactor", "Cofactor de un elemento", "Aᵢⱼ", _cofactor,
            parametros=("i", "j"), requisitos=CUADRADA_DEL_TEMARIO,
            ejemplo={"a": [[2, -1, 3], [-2, 5, 1], [0, 6, -9]], "i": 2, "j": 3},
            fuente=f"{SEGUNDA}, láminas 4 y 7",
        ),
        Operacion(
            "cofactores", "Matriz de cofactores", "C", _cofactores,
            requisitos=CUADRADA_DEL_TEMARIO,
            ejemplo={"a": [[1, 2, 0], [0, 1, 1], [1, 0, 3]]},
            fuente=f"{SEGUNDA}, láminas 23 y 24",
        ),
        Operacion(
            "adjunta", "Matriz adjunta", "adj(A)", _adjunta,
            requisitos=CUADRADA_DEL_TEMARIO,
            ejemplo={"a": [[1, 2, 0], [0, 1, 1], [1, 0, 3]]},
            fuente=f"{SEGUNDA}, láminas 17 y 25",
        ),
        Operacion(
            "inversa", "Matriz inversa", "A⁻¹", _inversa,
            requisitos=(*CUADRADA_DEL_TEMARIO, A_INVERTIBLE), informa_inversa=True,
            sin_resultado="no existe para esta matriz",
            ejemplo={"a": [[1, 2, 3], [0, 1, 4], [5, 6, 0]]},
            fuente=f"{SEGUNDA}, láminas 26 y 27",
        ),
    )
}


# --------------------------------------------------------------------------
# El resultado
# --------------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class Resultado:
    """Lo que el laboratorio devuelve de una operación: resultado **y** camino."""

    operacion: Operacion
    entrada: Entrada
    definida: bool
    pasos: tuple[str, ...]
    matriz: np.ndarray | None = None
    valor: Fraction | None = None
    texto: str | None = None

    @property
    def invertible(self) -> bool | None:
        """Lo informan el determinante y la inversa (propiedad 10), si A es del temario."""
        a = self.entrada.a
        if not self.operacion.informa_inversa or not all(
            r.cumple(self.entrada) for r in CUADRADA_DEL_TEMARIO
        ):
            return None
        return determinante(a.valores) != 0

    @property
    def tipos(self) -> dict[str, list[str]]:
        """Los tipos de cada operando y del resultado, si es una matriz."""
        tipos = {nombre: clasificar(m.valores) for nombre, m in self.entrada.matrices.items()}
        if self.matriz is not None:
            tipos[self.operacion.notacion] = clasificar(self.matriz)
        return tipos

    def respuesta(self) -> str:
        notacion = self.operacion.notacion
        if not self.definida:
            return f"{notacion} {self.operacion.sin_resultado}."
        if self.texto is not None:
            return self.texto
        if self.matriz is not None:
            return f"{notacion} = {en_linea(self.matriz)}."
        return f"{notacion} = {formatear(self.valor)}."

    def como_dict(self) -> dict:
        """Forma serializable: las entradas ya escritas como fracción exacta."""
        e = self.entrada
        return {
            "operacion": self.operacion.clave,
            "nombre": self.operacion.nombre,
            "notacion": self.operacion.notacion,
            "definida": self.definida,
            "operandos": {nombre: m.como_texto() for nombre, m in e.matrices.items()},
            "ordenes": {nombre: m.orden for nombre, m in e.matrices.items()},
            "parametros": {
                nombre: formatear(valor) if isinstance(valor, Fraction) else str(valor)
                for nombre, valor in e.parametros.items()
            },
            "resultado": como_texto(self.matriz) if self.matriz is not None else None,
            "valor": formatear(self.valor) if self.valor is not None else None,
            "pasos": list(self.pasos),
            "tipos": self.tipos,
            "invertible": self.invertible,
            "respuesta": self.respuesta(),
        }


# --------------------------------------------------------------------------
# Punto de entrada
# --------------------------------------------------------------------------
def operar(
    clave: str,
    a: list[list[Coeficiente]],
    b: list[list[Coeficiente]] | None = None,
    **parametros: object,
) -> Resultado:
    """Valida los datos, comprueba los requisitos y calcula con el camino.

    `parametros` son los que declare la operación en el catálogo (`k`, `m`,
    `i`, `j`, `desarrollo`); los que no declare se ignoran, igual que B en una
    operación de una sola matriz. Si un requisito falla, la respuesta es «no
    está definida» con el motivo, no una excepción: saber **cuándo** se puede
    operar es parte del temario.
    """
    operacion = OPERACIONES.get(clave)
    if operacion is None:
        raise MatrizInvalidaError(
            f"«{clave}» no es una operación del laboratorio. Elige entre: "
            f"{', '.join(OPERACIONES)}."
        )
    if operacion.usa_b and b is None:
        raise MatrizInvalidaError(f"{operacion.nombre} necesita una segunda matriz, B.")
    matriz_a = Matriz.desde_datos(a, "A")
    entrada = Entrada(
        a=matriz_a,
        b=Matriz.desde_datos(b, "B") if operacion.usa_b else None,
        parametros={
            nombre: PARAMETROS[nombre].leer(parametros.get(nombre), matriz_a)
            for nombre in operacion.parametros
        },
    )
    fallo = next((r for r in operacion.requisitos if not r.cumple(entrada)), None)
    if fallo is not None:
        return Resultado(operacion, entrada, definida=False, pasos=(fallo.motivo(entrada),))

    calculo = operacion.resolver(entrada)
    return Resultado(
        operacion,
        entrada,
        definida=True,
        pasos=tuple(calculo.pasos),
        matriz=calculo.matriz,
        valor=calculo.valor,
        texto=calculo.respuesta,
    )


def operar_datos(datos: dict) -> Resultado:
    """Atajo para quien llega con un diccionario (una tarjeta, un test)."""
    if not isinstance(datos, dict) or not {"operacion", "a"} <= datos.keys():
        raise MatrizInvalidaError("La operación necesita al menos «operacion» y la matriz «a».")
    resto = {k: v for k, v in datos.items() if k not in {"operacion", "a", "b"}}
    return operar(datos["operacion"], datos["a"], datos.get("b"), **resto)
