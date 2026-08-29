"""Motor de lógica proposicional: análisis, evaluación y tabla de verdad.

Analizador descendente recursivo sobre la gramática de la asignatura. Las
precedencias son las habituales, de mayor a menor:

    ¬   >   ∧   >   ∨ , ⊻   >   →   >   ↔

`→` asocia por la derecha (`p→q→r` ≡ `p→(q→r)`) y `↔` por la izquierda, que es
la convención de los apuntes. Cualquier ambigüedad real se resuelve con
paréntesis en el enunciado, nunca en silencio dentro del motor.

Las filas se generan con `itertools.product([True, False], repeat=n)`, que ya
entrega el orden de la asignatura (**V primero**). Nunca se escriben a mano.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Literal

from app.excepciones import FormulaInvalidaError

# --------------------------------------------------------------------------
# Símbolos aceptados. Se admiten alias ASCII para poder escribir fórmulas desde
# un teclado normal; todo se normaliza al símbolo canónico de la asignatura.
# --------------------------------------------------------------------------
NEGACION = "¬"
CONJUNCION = "∧"
DISYUNCION = "∨"
DISYUNCION_EXCLUSIVA = "⊻"
CONDICIONAL = "→"
BICONDICIONAL = "↔"

ALIAS: dict[str, str] = {
    "~": NEGACION, "!": NEGACION, "¬": NEGACION,
    "^": CONJUNCION, "&": CONJUNCION, "∧": CONJUNCION, "˄": CONJUNCION,
    "|": DISYUNCION, "+": DISYUNCION, "∨": DISYUNCION, "˅": DISYUNCION,
    "⊻": DISYUNCION_EXCLUSIVA, "⊕": DISYUNCION_EXCLUSIVA,
    "→": CONDICIONAL, "⇒": CONDICIONAL,
    "↔": BICONDICIONAL, "⇔": BICONDICIONAL, "≡": BICONDICIONAL,
}
ALIAS_LARGOS: list[tuple[str, str]] = [
    ("<->", BICONDICIONAL), ("<=>", BICONDICIONAL),
    ("->", CONDICIONAL), ("=>", CONDICIONAL),
]

_ABRE = "(["
_CIERRA = ")]"

Clasificacion = Literal["tautología", "contradicción", "contingencia"]


# --------------------------------------------------------------------------
# Árbol sintáctico
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Variable:
    nombre: str

    def evaluar(self, valores: dict[str, bool]) -> bool:
        return valores[self.nombre]

    def texto(self) -> str:
        return self.nombre


@dataclass(frozen=True)
class Negacion:
    hijo: Nodo

    def evaluar(self, valores: dict[str, bool]) -> bool:
        return not self.hijo.evaluar(valores)

    def texto(self) -> str:
        interno = self.hijo.texto()
        if isinstance(self.hijo, (Variable, Negacion)):
            return f"{NEGACION}{interno}"
        return f"{NEGACION}({interno})"


@dataclass(frozen=True)
class Binaria:
    operador: str
    izquierda: Nodo
    derecha: Nodo

    def evaluar(self, valores: dict[str, bool]) -> bool:
        a = self.izquierda.evaluar(valores)
        b = self.derecha.evaluar(valores)
        if self.operador == CONJUNCION:
            return a and b
        if self.operador == DISYUNCION:
            return a or b
        if self.operador == DISYUNCION_EXCLUSIVA:
            return a != b
        if self.operador == CONDICIONAL:
            return (not a) or b
        if self.operador == BICONDICIONAL:
            return a == b
        raise FormulaInvalidaError(f"Operador desconocido: {self.operador!r}")

    def texto(self) -> str:
        izq = self.izquierda.texto()
        der = self.derecha.texto()
        if not isinstance(self.izquierda, (Variable, Negacion)):
            izq = f"({izq})"
        if not isinstance(self.derecha, (Variable, Negacion)):
            der = f"({der})"
        return f"{izq}{self.operador}{der}"


Nodo = Variable | Negacion | Binaria


# --------------------------------------------------------------------------
# Análisis léxico
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Token:
    tipo: str  # "var" | "op" | "abre" | "cierra"
    valor: str
    posicion: int


def tokenizar(formula: str) -> list[Token]:
    """Convierte el texto en tokens, normalizando los alias a símbolos canónicos."""
    if not formula or not formula.strip():
        raise FormulaInvalidaError("La fórmula está vacía.", posicion=0)

    tokens: list[Token] = []
    i = 0
    n = len(formula)
    while i < n:
        caracter = formula[i]
        if caracter.isspace():
            i += 1
            continue

        # Los alias de varios caracteres van primero: "->" debe ganar a "-".
        alias_largo = next(
            (
                (texto, simbolo)
                for texto, simbolo in ALIAS_LARGOS
                if formula[i : i + len(texto)] == texto
            ),
            None,
        )
        if alias_largo is not None:
            texto, simbolo = alias_largo
            tokens.append(Token("op", simbolo, i))
            i += len(texto)
            continue

        if caracter in _ABRE:
            tokens.append(Token("abre", "(", i))
        elif caracter in _CIERRA:
            tokens.append(Token("cierra", ")", i))
        elif caracter in ALIAS:
            tokens.append(Token("op", ALIAS[caracter], i))
        elif caracter.isalpha():
            tokens.append(Token("var", caracter.lower(), i))
        else:
            raise FormulaInvalidaError(
                f"Carácter no reconocido {caracter!r} en la posición {i}.", posicion=i
            )
        i += 1

    return tokens


# --------------------------------------------------------------------------
# Análisis sintáctico (descendente recursivo)
# --------------------------------------------------------------------------
class _Analizador:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._i = 0

    def _actual(self) -> Token | None:
        return self._tokens[self._i] if self._i < len(self._tokens) else None

    def _consumir(self) -> Token:
        token = self._tokens[self._i]
        self._i += 1
        return token

    def analizar(self) -> Nodo:
        nodo = self._bicondicional()
        sobrante = self._actual()
        if sobrante is not None:
            raise FormulaInvalidaError(
                f"Sobra {sobrante.valor!r} en la posición {sobrante.posicion}.",
                posicion=sobrante.posicion,
            )
        return nodo

    def _bicondicional(self) -> Nodo:
        nodo = self._condicional()
        while (t := self._actual()) and t.tipo == "op" and t.valor == BICONDICIONAL:
            self._consumir()
            nodo = Binaria(BICONDICIONAL, nodo, self._condicional())
        return nodo

    def _condicional(self) -> Nodo:
        nodo = self._disyuncion()
        t = self._actual()
        if t and t.tipo == "op" and t.valor == CONDICIONAL:
            self._consumir()
            # Asociatividad por la derecha: p→q→r ≡ p→(q→r).
            return Binaria(CONDICIONAL, nodo, self._condicional())
        return nodo

    def _disyuncion(self) -> Nodo:
        nodo = self._conjuncion()
        while (
            (t := self._actual())
            and t.tipo == "op"
            and t.valor in (DISYUNCION, DISYUNCION_EXCLUSIVA)
        ):
            operador = self._consumir().valor
            nodo = Binaria(operador, nodo, self._conjuncion())
        return nodo

    def _conjuncion(self) -> Nodo:
        nodo = self._unaria()
        while (t := self._actual()) and t.tipo == "op" and t.valor == CONJUNCION:
            self._consumir()
            nodo = Binaria(CONJUNCION, nodo, self._unaria())
        return nodo

    def _unaria(self) -> Nodo:
        t = self._actual()
        if t is None:
            raise FormulaInvalidaError("La fórmula termina antes de tiempo.")
        if t.tipo == "op" and t.valor == NEGACION:
            self._consumir()
            return Negacion(self._unaria())
        return self._atomo()

    def _atomo(self) -> Nodo:
        t = self._actual()
        if t is None:
            raise FormulaInvalidaError("Falta un operando al final de la fórmula.")
        if t.tipo == "var":
            self._consumir()
            return Variable(t.valor)
        if t.tipo == "abre":
            self._consumir()
            nodo = self._bicondicional()
            cierre = self._actual()
            if cierre is None or cierre.tipo != "cierra":
                raise FormulaInvalidaError(
                    f"Falta cerrar el paréntesis abierto en la posición {t.posicion}.",
                    posicion=t.posicion,
                )
            self._consumir()
            return nodo
        raise FormulaInvalidaError(
            f"Se esperaba una variable o un paréntesis en la posición {t.posicion}, "
            f"y se encontró {t.valor!r}.",
            posicion=t.posicion,
        )


def analizar(formula: str) -> Nodo:
    """Analiza una fórmula y devuelve su árbol sintáctico."""
    tokens = tokenizar(formula)
    if not tokens:
        raise FormulaInvalidaError("La fórmula no contiene ningún símbolo.", posicion=0)
    return _Analizador(tokens).analizar()


# --------------------------------------------------------------------------
# Tabla de verdad
# --------------------------------------------------------------------------
def variables_de(nodo: Nodo) -> list[str]:
    """Variables que aparecen en la fórmula, en orden alfabético."""
    encontradas: set[str] = set()

    def recorrer(actual: Nodo) -> None:
        if isinstance(actual, Variable):
            encontradas.add(actual.nombre)
        elif isinstance(actual, Negacion):
            recorrer(actual.hijo)
        else:
            recorrer(actual.izquierda)
            recorrer(actual.derecha)

    recorrer(nodo)
    return sorted(encontradas)


def subformulas(nodo: Nodo) -> list[Nodo]:
    """Subfórmulas compuestas en orden de evaluación (internas antes que externas).

    Cada una merece su propia columna: son los resultados intermedios que la
    asignatura exige mostrar para no equivocarse al construir la tabla.
    """
    resultado: list[Nodo] = []

    def recorrer(actual: Nodo) -> None:
        if isinstance(actual, Variable):
            return
        if isinstance(actual, Negacion):
            recorrer(actual.hijo)
        else:
            recorrer(actual.izquierda)
            recorrer(actual.derecha)
        if actual not in resultado:
            resultado.append(actual)

    recorrer(nodo)
    return resultado


@dataclass(frozen=True)
class TablaVerdad:
    formula: str
    formula_normalizada: str
    variables: list[str]
    columnas: list[str]
    filas: list[list[bool]]
    resultado: list[bool]
    clasificacion: Clasificacion

    @property
    def numero_filas(self) -> int:
        return len(self.filas)

    def como_texto(self) -> list[list[str]]:
        """La tabla con `V`/`F`, tal como se escribe en el cuaderno."""
        return [["V" if celda else "F" for celda in fila] for fila in self.filas]


def clasificar(resultado: list[bool]) -> Clasificacion:
    """Tautología si todo V; contradicción si todo F; contingencia si hay mezcla."""
    if not resultado:
        raise FormulaInvalidaError("No hay valores que clasificar.")
    if all(resultado):
        return "tautología"
    if not any(resultado):
        return "contradicción"
    return "contingencia"


# Máximo de variables admitido. 2^7 = 128 filas ya no se leen en pantalla; el
# límite es didáctico, no técnico.
MAX_VARIABLES = 6


def construir_tabla(formula: str) -> TablaVerdad:
    """Construye la tabla de verdad completa de una fórmula proposicional."""
    arbol = analizar(formula)
    variables = variables_de(arbol)
    if not variables:
        raise FormulaInvalidaError("La fórmula no contiene ninguna variable proposicional.")
    if len(variables) > MAX_VARIABLES:
        raise FormulaInvalidaError(
            f"La fórmula usa {len(variables)} variables; el máximo admitido es "
            f"{MAX_VARIABLES} ({2 ** len(variables)} filas serían ilegibles)."
        )

    intermedias = [sub for sub in subformulas(arbol) if sub != arbol]
    columnas = [*variables, *(sub.texto() for sub in intermedias), arbol.texto()]

    filas: list[list[bool]] = []
    resultado: list[bool] = []
    # V primero: itertools.product([True, False], ...) ya entrega ese orden.
    for combinacion in itertools.product([True, False], repeat=len(variables)):
        valores = dict(zip(variables, combinacion, strict=True))
        fila = [*combinacion]
        fila += [sub.evaluar(valores) for sub in intermedias]
        final = arbol.evaluar(valores)
        fila.append(final)
        filas.append(fila)
        resultado.append(final)

    return TablaVerdad(
        formula=formula,
        formula_normalizada=arbol.texto(),
        variables=variables,
        columnas=columnas,
        filas=filas,
        resultado=resultado,
        clasificacion=clasificar(resultado),
    )


def son_equivalentes(formula_a: str, formula_b: str) -> bool:
    """Dos fórmulas son equivalentes si su bicondicional es una tautología."""
    tabla = construir_tabla(f"({formula_a}) {BICONDICIONAL} ({formula_b})")
    return tabla.clasificacion == "tautología"
