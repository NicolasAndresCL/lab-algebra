"""Números exactos compartidos por los motores de ecuaciones y de matrices.

Las dos unidades numéricas del laboratorio —sistemas de ecuaciones y
matrices— trabajan con `fractions.Fraction`, nunca con coma flotante: un
pivote o un determinante que vale exactamente 0 sale como 1e−17 con
flotantes, y en estas unidades «¿vale cero?» **es** la pregunta del ejercicio
(¿compatible determinado?, ¿admite inversa?).

Este módulo vivía dentro de `ecuaciones.py`. Se separó al llegar la unidad de
matrices porque las dos necesitan leer y escribir los números de la misma
manera; duplicarlo habría acabado con «−1/2» en una pestaña y «-1/2» en otra.
Cada motor lanza **su** excepción de dominio, por eso `a_fraccion` la recibe
como parámetro en vez de fijar una.
"""

from __future__ import annotations

from fractions import Fraction

from app.excepciones import ErrorLabAlgebra

# Menos tipográfico U+2212. `str(Fraction(-3))` devuelve el guion ASCII, que
# junto al resto del texto mezcla dos rayas de distinta longitud y se nota a
# simple vista. Todo número que salga de los motores pasa por `formatear`.
MENOS = "−"

Coeficiente = int | str | Fraction


def a_fraccion(valor: Coeficiente, error: type[ErrorLabAlgebra] = ErrorLabAlgebra) -> Fraction:
    """Convierte un número del enunciado en una fracción exacta.

    Admite enteros, fracciones y texto («3», «−1/2», «0.5»). **Rechaza los
    flotantes** a propósito: aceptarlos invitaría a escribir 0.333 donde el
    enunciado dice 1/3. `error` es la excepción de dominio que se lanza si el
    valor no se puede leer; cada motor pasa la suya.
    """
    if isinstance(valor, Fraction):
        return valor
    if isinstance(valor, bool):  # bool es subclase de int; no es un número del enunciado
        raise error(f"«{valor}» no es un coeficiente válido.")
    if isinstance(valor, int):
        return Fraction(valor)
    if isinstance(valor, float):
        raise error(
            f"«{valor}» es un número con coma. Escribe la fracción exacta "
            f"(1/3, no 0.333): el laboratorio trabaja sin redondeos."
        )
    texto = str(valor).strip().replace(MENOS, "-").replace(" ", "")
    if not texto:
        return Fraction(0)
    try:
        return Fraction(texto)
    except (ValueError, ZeroDivisionError):
        raise error(
            f"«{valor}» no es un número que se pueda leer. Usa enteros o "
            f"fracciones como 3, −2 o 1/2."
        )


def formatear(valor: Fraction | int) -> str:
    """El número tal como se escribe en el cuaderno: «3», «−1/2», «9/2»."""
    return str(valor).replace("-", MENOS)


def entre_parentesis(valor: Fraction | int) -> str:
    """«(−3)» si es negativo o fraccionario, «3» si no: así se escribe un factor.

    `6 · (−2)` se lee; `6 · −2` obliga a pararse. Las fracciones van también
    entre paréntesis para que `3 · 1/2` no parezca `(3 · 1)/2`.
    """
    texto = formatear(valor)
    es_simple = valor >= 0 and Fraction(valor).denominator == 1
    return texto if es_simple else f"({texto})"
