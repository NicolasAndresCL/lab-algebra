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
from sympy import And, Equivalent, Implies, Not, Or, Symbol, Xor

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
