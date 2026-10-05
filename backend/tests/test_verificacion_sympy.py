"""Segunda verificación, por un camino independiente: sympy.

El motor propio (`app.services.logica`) y este módulo no comparten una sola
línea: aquí las fórmulas se traducen a expresiones de sympy y se evalúan con
`Implies`, `Equivalent`, `And`, `Or`, `Not` y `Xor`. Una respuesta solo se da
por buena si ambos caminos coinciden **columna a columna**.

Es la misma disciplina que se aplicó a los talleres entregados de la
asignatura: nunca una sola fuente de verdad para un resultado.
"""

from __future__ import annotations

import itertools

import pytest
from sympy import And, Eq, Equivalent, Implies, Not, Or, Rational, Symbol, Xor, solve

from app.seed.cargar import MAZOS
from app.services import logica

# --------------------------------------------------------------------------
# Traducción independiente: texto -> expresión de sympy
# --------------------------------------------------------------------------
_PRECEDENCIA = {"↔": 1, "→": 2, "∨": 3, "⊻": 3, "∧": 4}


def _a_sympy(formula: str):
    """Analiza la fórmula con un algoritmo distinto (shunting-yard) y la evalúa.

    Usar otro algoritmo de análisis, y no solo otra librería de evaluación, es
    deliberado: si ambos caminos compartieran el analizador, un error de
    precedencia pasaría inadvertido en los dos.
    """
    salida: list = []
    operadores: list[str] = []

    def aplicar(operador: str) -> None:
        if operador == "¬":
            salida.append(Not(salida.pop()))
            return
        derecha = salida.pop()
        izquierda = salida.pop()
        salida.append(
            {
                "∧": lambda a, b: And(a, b),
                "∨": lambda a, b: Or(a, b),
                "⊻": lambda a, b: Xor(a, b),
                "→": lambda a, b: Implies(a, b),
                "↔": lambda a, b: Equivalent(a, b),
            }[operador](izquierda, derecha)
        )

    for token in logica.tokenizar(formula):
        if token.tipo == "var":
            salida.append(Symbol(token.valor))
        elif token.tipo == "abre":
            operadores.append("(")
        elif token.tipo == "cierra":
            while operadores and operadores[-1] != "(":
                aplicar(operadores.pop())
            operadores.pop()
        elif token.valor == "¬":
            operadores.append("¬")
        else:
            while (
                operadores
                and operadores[-1] != "("
                and (
                    operadores[-1] == "¬"
                    or _PRECEDENCIA[operadores[-1]] > _PRECEDENCIA[token.valor]
                    # → asocia por la derecha: con igual precedencia NO se
                    # desapila, al contrario que ∧, ∨ y ↔.
                    or (
                        _PRECEDENCIA[operadores[-1]] == _PRECEDENCIA[token.valor]
                        and token.valor != "→"
                    )
                )
            ):
                aplicar(operadores.pop())
            operadores.append(token.valor)

    while operadores:
        aplicar(operadores.pop())
    return salida[0]


def _tabla_sympy(formula: str) -> list[bool]:
    expresion = _a_sympy(formula)
    variables = sorted({str(s) for s in expresion.free_symbols})
    resultado = []
    for combinacion in itertools.product([True, False], repeat=len(variables)):
        sustitucion = {Symbol(v): valor for v, valor in zip(variables, combinacion, strict=True)}
        resultado.append(bool(expresion.subs(sustitucion)))
    return resultado


FORMULAS_DE_CONTRASTE = [
    "¬p",
    "p ∧ q",
    "p ∨ q",
    "p ⊻ q",
    "p → q",
    "p ↔ q",
    "¬(p ∨ q)",
    "(p ∧ q) → p",
    "p ↔ ¬p",
    "(p ∨ q) ∧ ¬p",
    "¬(p ∧ q) ↔ (¬p ∨ ¬q)",
    "(p ∧ ¬p) ∨ q",
    "(p ∨ q) → (p ∧ q)",
    "((p ∨ q) ∧ ¬p) → q",
    "(p ∧ (p → q)) → q",
    "¬(p → q) ↔ (p ∧ ¬q)",
    "(p ∨ ¬q) ∧ (¬p ∨ q)",
    "((p → q) ∧ p) → q",
    "(p ∧ q) ∧ (¬p ∨ ¬q)",
    "(p ∨ r) → (p ∧ ¬s)",
    "(p ∧ q) → (r ∨ ¬s)",
    "(q ∨ r) → (¬p ∧ s)",
    "(¬p ∨ q) ↔ (r ∧ ¬s)",
    "p → q → r",
    "p ∨ q ∧ r",
    "¬p ∧ q ∨ r",
]


@pytest.mark.parametrize("formula", FORMULAS_DE_CONTRASTE)
def test_el_motor_propio_coincide_con_sympy(formula: str) -> None:
    """Los dos caminos deben dar la misma columna final, valor a valor."""
    assert logica.construir_tabla(formula).resultado == _tabla_sympy(formula)


def test_todas_las_formulas_del_temario_coinciden_con_sympy() -> None:
    """Ninguna fórmula de las tarjetas puede discrepar entre ambos caminos."""
    discrepancias = []
    for mazo in MAZOS:
        for tarjeta in mazo["tarjetas"]:
            formula = tarjeta.get("formula")
            if not formula:
                continue
            propio = logica.construir_tabla(formula).resultado
            referencia = _tabla_sympy(formula)
            if propio != referencia:
                discrepancias.append((tarjeta["concepto"], formula, propio, referencia))
    assert not discrepancias, f"Discrepancias motor/sympy: {discrepancias}"



# --------------------------------------------------------------------------
# Igualdad de matrices (unidad de matrices, láminas 7 y 8)
# --------------------------------------------------------------------------
# Estas tarjetas no declaran `matriz`: su respuesta son los valores de unas
# incógnitas, no el resultado de una operación. Se verifican aquí: sympy
# resuelve, posición por posición, las ecuaciones transcritas de la lámina, y
# el conjunto de soluciones tiene que ser exactamente el que dice la tarjeta.
_w, _x, _y, _z = (Symbol(nombre, real=True) for nombre in "wxyz")

IGUALDADES_DE_MATRICES = {
    # [−1 2; x³ 0] = [2y + 1 2; 8 0]
    "Igualdad de matrices": (
        [Eq(-1, 2 * _y + 1), Eq(_x**3, 8)],
        (_x, _y),
        {(2, -1)},
    ),
    # [w + 1  10 + x; 3y − 2  x − 4] = [2  2x + 1; y − 5  4z]
    "Igualdad con varias incógnitas": (
        [Eq(_w + 1, 2), Eq(10 + _x, 2 * _x + 1), Eq(3 * _y - 2, _y - 5), Eq(_x - 4, 4 * _z)],
        (_w, _x, _y, _z),
        {(1, 9, Rational(-3, 2), Rational(5, 4))},
    ),
    # [x² − 9x  x; 1  0] = [10  x; 1  y² − 1]
    "Igualdad con más de una solución": (
        [Eq(_x**2 - 9 * _x, 10), Eq(0, _y**2 - 1)],
        (_x, _y),
        {(10, 1), (10, -1), (-1, 1), (-1, -1)},
    ),
}

_CONCEPTOS = {t["concepto"] for mazo in MAZOS for t in mazo["tarjetas"]}


@pytest.mark.parametrize("concepto", list(IGUALDADES_DE_MATRICES))
def test_las_igualdades_de_matrices_coinciden_con_sympy(concepto: str) -> None:
    assert concepto in _CONCEPTOS, f"no hay ninguna tarjeta «{concepto}»"
    ecuaciones, incognitas, esperadas = IGUALDADES_DE_MATRICES[concepto]
    soluciones = {
        tuple(solucion[v] for v in incognitas)
        for solucion in solve(ecuaciones, incognitas, dict=True)
    }
    assert soluciones == esperadas
