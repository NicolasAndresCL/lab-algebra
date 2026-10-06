"""Motor de sistemas de ecuaciones lineales: resolución exacta y clasificación.

Cubre la tercera unidad de la asignatura: sistemas de 2 × 2 y de 3 × 3, los
tres métodos que enseña el docente (**sustitución, igualación y reducción**),
la clasificación en *compatible determinado · compatible indeterminado ·
incompatible* y su interpretación geométrica (rectas que se cortan, paralelas
o coincidentes; tres planos en el espacio).

Dos decisiones que no se pueden relajar:

* **Aritmética exacta con `fractions.Fraction`, nunca coma flotante.** En este
  dominio la respuesta de un ejercicio es «x = 1/3», no «x = 0.3333»: con
  flotantes, un sistema compatible indeterminado se detecta como determinado
  —o al revés— porque un pivote que vale exactamente 0 sale como 1e−17. La
  clasificación es *la* pregunta de la unidad, así que el redondeo no es un
  detalle de presentación sino un error de resultado.
* **El desarrollo paso a paso forma parte de la salida.** Esto es material de
  estudio, no una calculadora: una respuesta sin el camino no sirve para
  aprender a resolver el siguiente.

Desde la unidad de matrices hay un cuarto método, la **regla de Cramer**:
de 2 × 2 desde la v1.2.0 (láminas 44 a 47 de «Matrices y determinantes») y de
3 × 3 desde la v1.3.0 (láminas 12 a 16 de «Matrices y determinantes II»).
Igual que los otros tres, Cramer **narra**; la clasificación sigue saliendo de
Gauss-Jordan. Los determinantes de 3 × 3 de Cramer se narran con
`matrices.desarrollo_por_cofactores`, el mismo método que enseña el curso.

Qué métodos admite cada orden está en `METODOS_POR_ORDEN`: sustitución e
igualación se enseñaron solo en 2 × 2. Lo que este módulo **no** hace, a
propósito: rangos, ni la resolución por matriz inversa. No se enseñaron como
método de resolver sistemas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Literal

import numpy as np

from app.excepciones import SistemaInvalidoError
from app.services import matrices, numeros
from app.services.numeros import MENOS, Coeficiente, formatear

Clasificacion = Literal[
    "compatible determinado",
    "compatible indeterminado",
    "incompatible",
]

METODOS: tuple[str, ...] = ("reducción", "sustitución", "igualación", "Cramer")
METODO_POR_DEFECTO = "reducción"

# Qué métodos se enseñaron para cada orden. La API lo publica tal cual
# (`GET /herramientas/ecuaciones/metodos`) y la interfaz arma su selector desde
# ahí: añadir un método a un orden es una línea aquí.
METODOS_POR_ORDEN: dict[int, tuple[str, ...]] = {
    2: METODOS,
    3: ("reducción", "Cramer"),
}
NOMBRES_POR_DEFECTO = ("x", "y", "z")
ORDENES_ADMITIDOS = (2, 3)

# --------------------------------------------------------------------------
# Números exactos (la implementación vive en `numeros.py`)
# --------------------------------------------------------------------------
def a_fraccion(valor: Coeficiente) -> Fraction:
    """`numeros.a_fraccion` con la excepción de esta unidad: `SistemaInvalidoError`."""
    return numeros.a_fraccion(valor, SistemaInvalidoError)


def _coeficiente_escrito(valor: Fraction, nombre: str) -> str:
    """«x», «2x», «(1/2)x» — el 1 no se escribe y las fracciones van entre paréntesis."""
    if valor == 1:
        return nombre
    if valor.denominator != 1:
        return f"({formatear(valor)}){nombre}"
    return f"{formatear(valor)}{nombre}"


# --------------------------------------------------------------------------
# El sistema
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Sistema:
    """Un sistema lineal cuadrado, guardado como matriz aumentada exacta.

    `matriz` es `[[a11, a12, …, b1], …]`: una fila por ecuación, con el término
    independiente en la última posición.
    """

    matriz: tuple[tuple[Fraction, ...], ...]
    incognitas: tuple[str, ...]

    @property
    def orden(self) -> int:
        return len(self.incognitas)

    @classmethod
    def desde_datos(
        cls, matriz: list[list[Coeficiente]], incognitas: list[str] | None = None
    ) -> Sistema:
        """Valida y normaliza lo que llega del formulario o de una tarjeta."""
        if not isinstance(matriz, list) or not matriz:
            raise SistemaInvalidoError("Hace falta la matriz de coeficientes del sistema.")
        orden = len(matriz)
        if orden not in ORDENES_ADMITIDOS:
            raise SistemaInvalidoError(
                f"El laboratorio resuelve sistemas de 2 × 2 y de 3 × 3; "
                f"este trae {orden} ecuaciones."
            )
        filas: list[tuple[Fraction, ...]] = []
        for numero, fila in enumerate(matriz, start=1):
            if not isinstance(fila, list) or len(fila) != orden + 1:
                raise SistemaInvalidoError(
                    f"La ecuación ({numero}) necesita {orden} coeficientes y su "
                    f"término independiente ({orden + 1} valores)."
                )
            filas.append(tuple(a_fraccion(valor) for valor in fila))

        nombres = tuple(incognitas) if incognitas else NOMBRES_POR_DEFECTO[:orden]
        if len(nombres) != orden:
            raise SistemaInvalidoError(
                f"Hacen falta {orden} nombres de incógnita; llegaron {len(nombres)}."
            )
        if len(set(nombres)) != orden:
            raise SistemaInvalidoError("Las incógnitas no pueden repetir nombre.")
        if all(coef == 0 for fila in filas for coef in fila[:orden]):
            raise SistemaInvalidoError(
                "Todos los coeficientes son cero: no hay ningún sistema que resolver."
            )
        return cls(matriz=tuple(filas), incognitas=nombres)

    def ecuacion_texto(self, fila: tuple[Fraction, ...]) -> str:
        """«2x − 3y = −8», saltando los coeficientes nulos."""
        partes: list[str] = []
        for coeficiente, nombre in zip(fila[:-1], self.incognitas, strict=True):
            if coeficiente == 0:
                continue
            cuerpo = _coeficiente_escrito(abs(coeficiente), nombre)
            if not partes:
                partes.append(f"{MENOS}{cuerpo}" if coeficiente < 0 else cuerpo)
            else:
                partes.append(f"{MENOS} {cuerpo}" if coeficiente < 0 else f"+ {cuerpo}")
        izquierda = " ".join(partes) if partes else "0"
        return f"{izquierda} = {formatear(fila[-1])}"

    def como_texto(self) -> list[str]:
        """Las ecuaciones reconstruidas, para que se vea qué se tecleó."""
        return [self.ecuacion_texto(fila) for fila in self.matriz]

    def sustituir(self, valores: dict[str, Fraction]) -> list[Fraction]:
        """Residuo de cada ecuación al reemplazar la solución: debe dar todo 0.

        Es la comprobación que no depende de nadie: una respuesta que no
        satisface su propio sistema está mal, la imprima quien la imprima.
        """
        residuos = []
        for fila in self.matriz:
            total = sum(
                (coef * valores[nombre] for coef, nombre in
                 zip(fila[:-1], self.incognitas, strict=True)),
                Fraction(0),
            )
            residuos.append(total - fila[-1])
        return residuos


# --------------------------------------------------------------------------
# El resultado
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Solucion:
    """Lo que el laboratorio devuelve de un sistema: resultado **y** camino."""

    sistema: Sistema
    clasificacion: Clasificacion
    metodo: str
    valores: dict[str, Fraction] = field(default_factory=dict)
    parametros: tuple[str, ...] = ()
    formulas: dict[str, str] = field(default_factory=dict)
    delta: Fraction | None = None
    pasos: tuple[str, ...] = ()
    interpretacion: str = ""

    @property
    def hay_solucion_unica(self) -> bool:
        return self.clasificacion == "compatible determinado"

    def respuesta(self) -> str:
        """La respuesta en una línea, como se escribe al final del ejercicio."""
        if self.clasificacion == "incompatible":
            return "El sistema no tiene solución."
        if self.clasificacion == "compatible indeterminado":
            libres = ", ".join(self.parametros)
            familia = "; ".join(
                f"{nombre} = {expresion}" for nombre, expresion in self.formulas.items()
            )
            cola = f" con {libres} cualquier número real."
            return (f"Infinitas soluciones: {familia}{cola}" if familia
                    else f"Infinitas soluciones, con {libres} libre.")
        terna = ", ".join(
            f"{nombre} = {formatear(self.valores[nombre])}"
            for nombre in self.sistema.incognitas
        )
        return f"{terna}."

    def como_dict(self) -> dict:
        """Forma serializable: los números ya escritos como fracción exacta."""
        return {
            "ecuaciones": self.sistema.como_texto(),
            "incognitas": list(self.sistema.incognitas),
            "clasificacion": self.clasificacion,
            "metodo": self.metodo,
            "valores": {
                nombre: formatear(valor) for nombre, valor in self.valores.items()
            },
            "parametros": list(self.parametros),
            "formulas": dict(self.formulas),
            "delta": formatear(self.delta) if self.delta is not None else None,
            "pasos": list(self.pasos),
            "interpretacion": self.interpretacion,
            "respuesta": self.respuesta(),
        }


# --------------------------------------------------------------------------
# Determinante de 2 × 2 (el único que pide la asignatura)
# --------------------------------------------------------------------------
def determinante_2x2(sistema: Sistema) -> Fraction:
    """Δ = a₁₁·a₂₂ − a₁₂·a₂₁, tal como lo escribe el libro del curso."""
    if sistema.orden != 2:
        raise SistemaInvalidoError(
            "El determinante Δ = a₁₁a₂₂ − a₁₂a₂₁ es el de un sistema de 2 × 2."
        )
    (a11, a12, _), (a21, a22, _) = sistema.matriz
    return a11 * a22 - a12 * a21


def _texto_delta(sistema: Sistema, delta: Fraction) -> str:
    (a11, a12, _), (a21, a22, _) = sistema.matriz
    producto_1 = f"({formatear(a11)})({formatear(a22)})"
    producto_2 = f"({formatear(a12)})({formatear(a21)})"
    conclusion = (
        "≠ 0 → hay solución única (compatible determinado)."
        if delta != 0
        else "→ no hay solución única: o no hay ninguna o hay infinitas."
    )
    return (
        f"Δ = a₁₁a₂₂ − a₁₂a₂₁ = {producto_1} − {producto_2} = "
        f"{formatear(delta)} {conclusion}"
    )


def _division(dividendo: Fraction, divisor: Fraction) -> str:
    """«(−7/6) / (−7/3)»: los paréntesis evitan leer dos signos seguidos."""
    return f"({formatear(dividendo)}) / ({formatear(divisor)})"


def _por(factor: Fraction, ecuacion: int) -> str:
    """«la (1)» o «la (1) por 3»: multiplicar por 1 no se dice."""
    return f"la ({ecuacion})" if factor == 1 else f"la ({ecuacion}) por {formatear(factor)}"


# --------------------------------------------------------------------------
# Eliminación de Gauss-Jordan con aritmética exacta
# --------------------------------------------------------------------------
@dataclass
class _Escalonada:
    filas: list[list[Fraction]]
    pivotes: list[int]
    pasos: list[str]


def _escalonar(sistema: Sistema, narrar: bool) -> _Escalonada:
    """Reduce la matriz aumentada a su forma escalonada reducida.

    Sin pivoteo numérico: con `Fraction` un coeficiente vale cero o no vale
    cero, y no hay error de redondeo que mitigar. Se elige el primer pivote no
    nulo, que además es el que usaría alguien a mano.
    """
    filas = [list(fila) for fila in sistema.matriz]
    orden = sistema.orden
    pasos: list[str] = []
    pivotes: list[int] = []
    fila_pivote = 0

    for columna in range(orden):
        nombre = sistema.incognitas[columna]
        candidata = next(
            (r for r in range(fila_pivote, len(filas)) if filas[r][columna] != 0), None
        )
        if candidata is None:
            continue
        if candidata != fila_pivote:
            filas[fila_pivote], filas[candidata] = filas[candidata], filas[fila_pivote]
            if narrar:
                pasos.append(
                    f"Intercambio las ecuaciones ({fila_pivote + 1}) y ({candidata + 1}): "
                    f"la primera no tiene {nombre} y hace falta un pivote."
                )
        pivote = filas[fila_pivote][columna]
        if pivote != 1:
            filas[fila_pivote] = [valor / pivote for valor in filas[fila_pivote]]
            if narrar:
                pasos.append(
                    f"Divido la ecuación ({fila_pivote + 1}) entre {formatear(pivote)} "
                    f"para dejar {nombre} con coeficiente 1: "
                    f"{sistema.ecuacion_texto(tuple(filas[fila_pivote]))}"
                )
        for otra in range(len(filas)):
            factor = filas[otra][columna]
            if otra == fila_pivote or factor == 0:
                continue
            filas[otra] = [
                valor - factor * referencia
                for valor, referencia in zip(filas[otra], filas[fila_pivote], strict=True)
            ]
            if narrar:
                verbo = "le sumo" if factor < 0 else "le resto"
                magnitud = abs(factor)
                cuantas = (
                    f"la ({fila_pivote + 1})"
                    if magnitud == 1
                    else f"{formatear(magnitud)} veces la ({fila_pivote + 1})"
                )
                pasos.append(
                    f"A la ecuación ({otra + 1}) {verbo} {cuantas} "
                    f"para eliminar {nombre}: "
                    f"{sistema.ecuacion_texto(tuple(filas[otra]))}"
                )
        pivotes.append(columna)
        fila_pivote += 1

    return _Escalonada(filas=filas, pivotes=pivotes, pasos=pasos)


def _fila_contradictoria(fila: list[Fraction], orden: int) -> bool:
    """`0x + 0y + 0z = k` con k ≠ 0: la igualdad falsa que delata un incompatible."""
    return all(coef == 0 for coef in fila[:orden]) and fila[orden] != 0


def _expresion_lineal(
    constante: Fraction, terminos: list[tuple[Fraction, str]]
) -> str:
    """«5z − 2», «−7x/4», «3» — la forma en que se escribe una solución paramétrica."""
    partes: list[str] = []
    for coeficiente, nombre in terminos:
        if coeficiente == 0:
            continue
        cuerpo = _coeficiente_escrito(abs(coeficiente), nombre)
        if not partes:
            partes.append(f"{MENOS}{cuerpo}" if coeficiente < 0 else cuerpo)
        else:
            partes.append(f"{MENOS} {cuerpo}" if coeficiente < 0 else f"+ {cuerpo}")
    if constante != 0 or not partes:
        texto = formatear(abs(constante))
        if not partes:
            partes.append(f"{MENOS}{texto}" if constante < 0 else texto)
        else:
            partes.append(f"{MENOS} {texto}" if constante < 0 else f"+ {texto}")
    return " ".join(partes)


def _interpretacion(orden: int, clasificacion: str, libres: int) -> str:
    """La lectura geométrica que pide la asignatura."""
    if orden == 2:
        if clasificacion == "compatible determinado":
            return "Las dos rectas se cortan en un único punto: la solución del sistema."
        if clasificacion == "incompatible":
            return (
                "Las dos rectas tienen la misma pendiente y distinta ordenada: son "
                "paralelas y no se cortan nunca."
            )
        if libres >= 2:
            return "Ninguna ecuación restringe el plano: sirve cualquier punto."
        return (
            "Las dos ecuaciones describen la misma recta: son rectas coincidentes y "
            "cualquier punto de ella es solución."
        )
    if clasificacion == "compatible determinado":
        return "Los tres planos se cortan en un único punto del espacio."
    if clasificacion == "incompatible":
        return (
            "No hay ningún punto común a los tres planos: al menos dos son paralelos "
            "o se cortan dos a dos sin una recta común."
        )
    if libres >= 2:
        return "Los tres planos coinciden: todo el plano común es solución."
    return "Los tres planos se cortan en una recta común, no en un punto."


# --------------------------------------------------------------------------
# Desarrollos de 2 × 2 por los tres métodos del curso
# --------------------------------------------------------------------------
def _pasos_reduccion(sistema: Sistema, clasificacion: str, delta: Fraction) -> list[str]:
    """Se suman o restan las ecuaciones hasta que una incógnita desaparece."""
    (a11, a12, b1), (a21, a22, b2) = sistema.matriz
    x, y = sistema.incognitas
    delta_x = b1 * a22 - a12 * b2
    delta_y = a11 * b2 - b1 * a21
    pasos = [
        f"(1)  {sistema.ecuacion_texto(sistema.matriz[0])}",
        f"(2)  {sistema.ecuacion_texto(sistema.matriz[1])}",
        _texto_delta(sistema, delta),
    ]
    if clasificacion == "compatible determinado":
        pasos += [
            f"Multiplico {_por(a22, 1)} y {_por(a12, 2)} y resto, con lo que se va "
            f"{y}: ({formatear(delta)}){x} = {formatear(delta_x)}.",
            f"{x} = {_division(delta_x, delta)} = {formatear(delta_x / delta)}.",
            f"Multiplico {_por(a21, 1)} y {_por(a11, 2)} y resto, con lo que se va "
            f"{x}: ({formatear(delta)}){y} = {formatear(delta_y)}.",
            f"{y} = {_division(delta_y, delta)} = {formatear(delta_y / delta)}.",
        ]
    elif clasificacion == "incompatible":
        pasos += [
            f"Con Δ = 0 el mismo par de multiplicaciones deja 0·{x} = "
            f"{formatear(delta_x)} y 0·{y} = {formatear(delta_y)}.",
            "Al menos una de esas igualdades es falsa: no existe ningún par que "
            "cumpla las dos ecuaciones.",
        ]
    else:
        pasos += [
            "Con Δ = 0 las dos combinaciones dejan 0 = 0, que es cierto siempre: "
            "las ecuaciones son dependientes.",
            "Una de las dos no aporta información nueva, así que basta despejar en "
            "la otra.",
        ]
    return pasos


def _indice_despejable(fila: tuple[Fraction, ...], orden: int) -> int | None:
    return next((j for j in range(orden) if fila[j] != 0), None)


def _pasos_sustitucion(sistema: Sistema, clasificacion: str) -> list[str]:
    """Se despeja una incógnita en una ecuación y se reemplaza en la otra."""
    matriz = sistema.matriz
    indice = _indice_despejable(matriz[0], 2)
    origen, destino = 0, 1
    if indice is None:
        indice = _indice_despejable(matriz[1], 2)
        origen, destino = 1, 0
    if indice is None:  # pragma: no cover - lo impide la validación del sistema
        raise SistemaInvalidoError("No hay ninguna incógnita que despejar.")

    otro = 1 - indice
    despejada = sistema.incognitas[indice]
    libre = sistema.incognitas[otro]
    a = matriz[origen][indice]
    b = matriz[origen][otro]
    c = matriz[origen][2]
    expresion = _expresion_lineal(c / a, [(-b / a, libre)])

    d = matriz[destino][indice]
    e = matriz[destino][otro]
    f = matriz[destino][2]
    coeficiente = e - d * b / a
    termino = f - d * c / a

    pasos = [
        f"(1)  {sistema.ecuacion_texto(matriz[0])}",
        f"(2)  {sistema.ecuacion_texto(matriz[1])}",
        f"Despejo {despejada} en la ({origen + 1}): {despejada} = {expresion}.",
        f"Reemplazo ese valor de {despejada} en la ({destino + 1}) y agrupo los "
        f"términos en {libre}: "
        f"{_coeficiente_escrito(coeficiente, libre) if coeficiente != 0 else '0'} = "
        f"{formatear(termino)}.",
    ]
    if clasificacion == "compatible determinado":
        valor_libre = termino / coeficiente
        valor_despejada = c / a - (b / a) * valor_libre
        pasos += [
            f"{libre} = {_division(termino, coeficiente)} = {formatear(valor_libre)}.",
            f"Vuelvo a la expresión despejada: {despejada} = {expresion} = "
            f"{formatear(valor_despejada)}.",
        ]
    elif clasificacion == "incompatible":
        pasos.append(
            f"Queda 0 = {formatear(termino)}, que es falso: el sistema no tiene solución."
        )
    else:
        pasos.append(
            f"Queda 0 = 0, cierto para cualquier valor de {libre}: hay infinitas "
            f"soluciones."
        )
    return pasos


def _pasos_igualacion(sistema: Sistema, clasificacion: str) -> list[str]:
    """Se despeja la misma incógnita en las dos ecuaciones y se igualan."""
    matriz = sistema.matriz
    indice = next((j for j in range(2) if matriz[0][j] != 0 and matriz[1][j] != 0), None)
    if indice is None:
        raise SistemaInvalidoError(
            "Para igualar hace falta una incógnita que aparezca en las dos "
            "ecuaciones; aquí no la hay. Prueba con sustitución o reducción."
        )
    otro = 1 - indice
    despejada = sistema.incognitas[indice]
    libre = sistema.incognitas[otro]

    a, b, c = matriz[0][indice], matriz[0][otro], matriz[0][2]
    d, e, f = matriz[1][indice], matriz[1][otro], matriz[1][2]
    primera = _expresion_lineal(c / a, [(-b / a, libre)])
    segunda = _expresion_lineal(f / d, [(-e / d, libre)])
    coeficiente = (-b / a) - (-e / d)
    termino = (f / d) - (c / a)

    pasos = [
        f"(1)  {sistema.ecuacion_texto(matriz[0])}",
        f"(2)  {sistema.ecuacion_texto(matriz[1])}",
        f"Despejo {despejada} en la (1): {despejada} = {primera}.",
        f"Despejo {despejada} en la (2): {despejada} = {segunda}.",
        f"Igualo las dos expresiones: {primera} = {segunda}.",
        f"Reordenando: {_coeficiente_escrito(coeficiente, libre) if coeficiente != 0 else '0'}"
        f" = {formatear(termino)}.",
    ]
    if clasificacion == "compatible determinado":
        valor_libre = termino / coeficiente
        valor_despejada = c / a - (b / a) * valor_libre
        pasos += [
            f"{libre} = {_division(termino, coeficiente)} = {formatear(valor_libre)}.",
            f"En la primera expresión despejada: {despejada} = "
            f"{formatear(valor_despejada)}.",
        ]
    elif clasificacion == "incompatible":
        pasos.append(
            f"Queda 0 = {formatear(termino)}, que es falso: las dos rectas no "
            f"se cortan."
        )
    else:
        pasos.append(
            "Queda 0 = 0: las dos expresiones despejadas son la misma, así que "
            "hay infinitas soluciones."
        )
    return pasos


def _determinante_escrito(nombre: str, a: Fraction, b: Fraction,
                          c: Fraction, d: Fraction) -> str:
    """«Dₓ = |4 −2; 13 1| = (4)(1) − (−2)(13) = 30», como en la lámina 45."""
    valor = a * d - b * c
    return (
        f"{nombre} = |{formatear(a)} {formatear(b)}; {formatear(c)} {formatear(d)}| = "
        f"({formatear(a)})({formatear(d)}) − ({formatear(b)})({formatear(c)}) = "
        f"{formatear(valor)}"
    )


def _pasos_cramer(sistema: Sistema, clasificacion: str, delta: Fraction) -> list[str]:
    """Regla de Cramer de 2 × 2: x = Dₓ / D, y = D_y / D, siempre que D ≠ 0.

    Dₓ se forma cambiando la columna de x por la de los términos
    independientes, y D_y cambiando la de y. Con D = 0 la regla **no es
    aplicable** —dividiría entre cero— y así se dice; el resultado lo da
    entonces la clasificación por eliminación, que es la que manda siempre.
    """
    (a, b, s), (c, d, t) = sistema.matriz
    x, y = sistema.incognitas
    delta_x = s * d - b * t
    delta_y = a * t - s * c
    pasos = [
        f"(1)  {sistema.ecuacion_texto(sistema.matriz[0])}",
        f"(2)  {sistema.ecuacion_texto(sistema.matriz[1])}",
        _determinante_escrito("D", a, b, c, d),
        f"Para D{_sub(x)} cambio la columna de {x} por los términos independientes; "
        f"para D{_sub(y)}, la de {y}.",
        _determinante_escrito(f"D{_sub(x)}", s, b, t, d),
        _determinante_escrito(f"D{_sub(y)}", a, s, c, t),
    ]
    if clasificacion == "compatible determinado":
        return [
            *pasos,
            f"{x} = D{_sub(x)} / D = {_division(delta_x, delta)} = "
            f"{formatear(delta_x / delta)}.",
            f"{y} = D{_sub(y)} / D = {_division(delta_y, delta)} = "
            f"{formatear(delta_y / delta)}.",
        ]
    lectura = (
        "D = 0 y algún numerador no es 0: las ecuaciones se contradicen."
        if clasificacion == "incompatible"
        else "D = 0 y los dos numeradores también: las ecuaciones son dependientes."
    )
    return [
        *pasos,
        "D = 0: la regla de Cramer no es aplicable, porque habría que dividir entre "
        "cero. No hay solución única.",
        lectura,
    ]


def _pasos_cramer_3x3(sistema: Sistema, clasificacion: str) -> list[str]:
    """Regla de Cramer de 3 × 3 (láminas 12 a 16 de la segunda parte).

    Cada determinante se narra desarrollando por la primera fila, como en la
    lámina 14. Con D = 0 **no** se calculan Dₓ, D_y y D_z: a diferencia del
    2 × 2, en 3 × 3 que los tres valgan 0 no garantiza infinitas soluciones
    (hay sistemas incompatibles con D = Dₓ = D_y = D_z = 0), así que decirlo
    sería enseñar una regla falsa. Decide la eliminación, como siempre.
    """
    coeficientes = np.array([fila[:3] for fila in sistema.matriz], dtype=object)
    terminos = np.array([fila[3] for fila in sistema.matriz], dtype=object)
    cabecera = [f"({i + 1})  {texto}" for i, texto in enumerate(sistema.como_texto())]
    delta, pasos_d = matrices.desarrollo_por_cofactores(coeficientes, "fila 1", "D")
    pasos = [*cabecera, "D es el determinante de los coeficientes.", *pasos_d]
    if delta == 0:
        return [
            *pasos,
            "D = 0: la regla de Cramer no es aplicable. El sistema es incompatible o "
            "tiene infinitas soluciones (lámina 16), y lo decide la eliminación: en "
            "3 × 3, que Dₓ, D_y y D_z valgan 0 no basta para asegurar infinitas "
            "soluciones.",
        ]
    soluciones = []
    for k, nombre in enumerate(sistema.incognitas):
        reemplazada = coeficientes.copy()
        reemplazada[:, k] = terminos
        etiqueta = f"D{_sub(nombre)}"
        valor, pasos_k = matrices.desarrollo_por_cofactores(reemplazada, "fila 1", etiqueta)
        pasos += [
            f"{etiqueta}: la columna de {nombre} se cambia por los términos independientes.",
            *pasos_k,
        ]
        soluciones.append(
            f"{nombre} = {etiqueta} / D = {_division(valor, delta)} = "
            f"{formatear(valor / delta)}."
        )
    return [*pasos, *soluciones]


# Subíndices para nombrar Dₓ, D_y. Unicode no tiene subíndice para todas las
# letras (no hay «y» ni «z» subíndice), así que las que faltan van con guion bajo.
_SUBINDICES = {"x": "ₓ", "a": "ₐ", "e": "ₑ", "o": "ₒ"}


def _sub(nombre: str) -> str:
    return _SUBINDICES.get(nombre, f"_{nombre}")


# --------------------------------------------------------------------------
# Punto de entrada
# --------------------------------------------------------------------------
def resolver(sistema: Sistema, metodo: str | None = None) -> Solucion:
    """Resuelve y clasifica el sistema, con el desarrollo paso a paso.

    La **clasificación siempre sale de la eliminación de Gauss-Jordan**, aunque
    el desarrollo que se muestre sea el de otro método: así el resultado no
    puede depender de por dónde se decidió atacar el ejercicio. El método solo
    elige cómo se cuenta el camino.
    """
    if metodo is not None and metodo not in METODOS:
        raise SistemaInvalidoError(
            f"«{metodo}» no es un método de los que enseña la asignatura. "
            f"Elige entre: {', '.join(METODOS)}."
        )
    elegido = metodo or METODO_POR_DEFECTO
    orden = sistema.orden
    if elegido not in METODOS_POR_ORDEN[orden]:
        raise SistemaInvalidoError(
            f"En {orden} × {orden} el curso enseña {' y '.join(METODOS_POR_ORDEN[orden])}. "
            f"Sustitución e igualación quedan para los sistemas de 2 × 2."
        )

    narrar_gauss = metodo is None or (orden == 3 and elegido == "reducción")
    escalonada = _escalonar(sistema, narrar=narrar_gauss)

    if any(_fila_contradictoria(fila, orden) for fila in escalonada.filas):
        clasificacion: Clasificacion = "incompatible"
    elif len(escalonada.pivotes) == orden:
        clasificacion = "compatible determinado"
    else:
        clasificacion = "compatible indeterminado"

    valores: dict[str, Fraction] = {}
    parametros: tuple[str, ...] = ()
    formulas: dict[str, str] = {}
    libres: list[int] = []

    if clasificacion == "compatible determinado":
        for numero, columna in enumerate(escalonada.pivotes):
            valores[sistema.incognitas[columna]] = escalonada.filas[numero][orden]
    elif clasificacion == "compatible indeterminado":
        libres = [c for c in range(orden) if c not in escalonada.pivotes]
        parametros = tuple(sistema.incognitas[c] for c in libres)
        for numero, columna in enumerate(escalonada.pivotes):
            fila = escalonada.filas[numero]
            terminos = [(-fila[c], sistema.incognitas[c]) for c in libres]
            formulas[sistema.incognitas[columna]] = _expresion_lineal(
                fila[orden], terminos
            )

    delta = determinante_2x2(sistema) if orden == 2 else None

    if metodo is not None and (orden == 2 or elegido == "Cramer"):
        generador = {
            "reducción": lambda: _pasos_reduccion(sistema, clasificacion, delta),
            "sustitución": lambda: _pasos_sustitucion(sistema, clasificacion),
            "igualación": lambda: _pasos_igualacion(sistema, clasificacion),
            "Cramer": lambda: (
                _pasos_cramer(sistema, clasificacion, delta) if orden == 2
                else _pasos_cramer_3x3(sistema, clasificacion)
            ),
        }[elegido]
        pasos = generador()
    else:
        cabecera = [f"({i + 1})  {texto}" for i, texto in enumerate(sistema.como_texto())]
        if delta is not None:
            cabecera.append(_texto_delta(sistema, delta))
        pasos = [*cabecera, *escalonada.pasos]

    pasos.append(f"Clasificación: {clasificacion}.")
    if clasificacion == "compatible determinado":
        residuos = sistema.sustituir(valores)
        comprobadas = ", ".join(
            f"({i + 1}) ✓" for i, residuo in enumerate(residuos) if residuo == 0
        )
        pasos.append(f"Comprobación: la solución satisface {comprobadas}")

    return Solucion(
        sistema=sistema,
        clasificacion=clasificacion,
        metodo=elegido,
        valores=valores,
        parametros=parametros,
        formulas=formulas,
        delta=delta,
        pasos=tuple(pasos),
        interpretacion=_interpretacion(orden, clasificacion, len(libres)),
    )


def resolver_datos(
    matriz: list[list[Coeficiente]],
    incognitas: list[str] | None = None,
    metodo: str | None = None,
) -> Solucion:
    """Atajo para quien llega con datos crudos (la API, una tarjeta, un test)."""
    return resolver(Sistema.desde_datos(matriz, incognitas), metodo)
