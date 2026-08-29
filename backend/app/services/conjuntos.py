"""Motor de teoría de conjuntos: operaciones, conjunto potencia y cardinalidades.

Cubre las dos mitades de la unidad:

* **Operaciones sobre conjuntos concretos** (∪, ∩, −, complemento, Δ, potencia).
* **Conteo por cardinalidades** (principio de inclusión-exclusión para dos y
  tres conjuntos), que es lo que piden los problemas de encuesta con diagrama
  de Venn.

Las funciones de conteo **validan que las regiones no queden negativas**. Un
enunciado mal copiado produce, si no, un diagrama con `-5` personas en una
región y una respuesta que parece correcta.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import chain, combinations

from app.excepciones import DatosVennInvalidosError

Elemento = str | int


# --------------------------------------------------------------------------
# Operaciones sobre conjuntos concretos
# --------------------------------------------------------------------------
def union(a: set[Elemento], b: set[Elemento]) -> set[Elemento]:
    """A ∪ B: lo que está en A, en B, o en ambos."""
    return a | b


def interseccion(a: set[Elemento], b: set[Elemento]) -> set[Elemento]:
    """A ∩ B: solo lo que está en ambos."""
    return a & b


def diferencia(a: set[Elemento], b: set[Elemento]) -> set[Elemento]:
    """A − B: lo que está en A pero no en B."""
    return a - b


def diferencia_simetrica(a: set[Elemento], b: set[Elemento]) -> set[Elemento]:
    """A Δ B: lo que está en exactamente uno de los dos."""
    return a ^ b


def complemento(universo: set[Elemento], a: set[Elemento]) -> set[Elemento]:
    """Aᶜ: lo que está en el universo pero no en A."""
    if not a <= universo:
        sobran = sorted(str(x) for x in a - universo)
        raise DatosVennInvalidosError(
            f"El conjunto no está contenido en el universo; sobran: {', '.join(sobran)}."
        )
    return universo - a


def es_subconjunto(a: set[Elemento], b: set[Elemento]) -> bool:
    """A ⊂ B: todo elemento de A pertenece también a B."""
    return a <= b


def conjunto_potencia(a: set[Elemento]) -> list[tuple[Elemento, ...]]:
    """℘(A): todos los subconjuntos de A. Su cardinalidad es 2ⁿ.

    Se devuelven ordenados por tamaño (∅ primero) para que la lista se lea
    igual que en los apuntes.
    """
    elementos = sorted(a, key=str)
    return list(
        chain.from_iterable(combinations(elementos, k) for k in range(len(elementos) + 1))
    )


# --------------------------------------------------------------------------
# Conteo: principio de inclusión-exclusión
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class RegionesDos:
    """Reparto de un universo entre dos conjuntos."""

    solo_a: int
    solo_b: int
    ambos: int
    ninguno: int
    union: int
    etiquetas: tuple[str, str] = ("A", "B")

    @property
    def exactamente_uno(self) -> int:
        """|A Δ B| = |A| + |B| − 2·|A ∩ B|."""
        return self.solo_a + self.solo_b

    def como_dict(self) -> dict[str, int]:
        return {
            "solo_a": self.solo_a,
            "solo_b": self.solo_b,
            "ambos": self.ambos,
            "ninguno": self.ninguno,
            "union": self.union,
            "exactamente_uno": self.exactamente_uno,
        }


@dataclass(frozen=True)
class RegionesTres:
    """Reparto de un universo entre tres conjuntos (las siete regiones)."""

    solo_a: int
    solo_b: int
    solo_c: int
    ab: int  # A y B, pero no C
    ac: int  # A y C, pero no B
    bc: int  # B y C, pero no A
    abc: int
    ninguno: int
    union: int
    etiquetas: tuple[str, str, str] = ("A", "B", "C")

    @property
    def exactamente_uno(self) -> int:
        return self.solo_a + self.solo_b + self.solo_c

    @property
    def exactamente_dos(self) -> int:
        return self.ab + self.ac + self.bc

    @property
    def al_menos_dos(self) -> int:
        return self.exactamente_dos + self.abc

    def como_dict(self) -> dict[str, int]:
        return {
            "solo_a": self.solo_a,
            "solo_b": self.solo_b,
            "solo_c": self.solo_c,
            "ab": self.ab,
            "ac": self.ac,
            "bc": self.bc,
            "abc": self.abc,
            "ninguno": self.ninguno,
            "union": self.union,
            "exactamente_uno": self.exactamente_uno,
            "exactamente_dos": self.exactamente_dos,
            "al_menos_dos": self.al_menos_dos,
        }


def _exigir_no_negativo(nombre: str, valor: int) -> int:
    if valor < 0:
        raise DatosVennInvalidosError(
            f"La región «{nombre}» daría {valor}, que es imposible. "
            f"Revisa los datos del enunciado: alguna intersección es mayor que su conjunto."
        )
    return valor


def regiones_dos(
    n_a: int,
    n_b: int,
    n_ab: int,
    universo: int | None = None,
    etiquetas: tuple[str, str] = ("A", "B"),
) -> RegionesDos:
    """Reparte un universo entre dos conjuntos a partir de sus cardinalidades.

    `n(A ∪ B) = n(A) + n(B) − n(A ∩ B)` — se resta la intersección porque al
    sumar los totales se contó dos veces.
    """
    solo_a = _exigir_no_negativo(f"solo {etiquetas[0]}", n_a - n_ab)
    solo_b = _exigir_no_negativo(f"solo {etiquetas[1]}", n_b - n_ab)
    total_union = n_a + n_b - n_ab
    ninguno = 0
    if universo is not None:
        ninguno = _exigir_no_negativo("ninguno de los dos", universo - total_union)
    return RegionesDos(
        solo_a=solo_a,
        solo_b=solo_b,
        ambos=n_ab,
        ninguno=ninguno,
        union=total_union,
        etiquetas=etiquetas,
    )


def regiones_tres(
    n_a: int,
    n_b: int,
    n_c: int,
    n_ab: int,
    n_ac: int,
    n_bc: int,
    n_abc: int,
    universo: int | None = None,
    etiquetas: tuple[str, str, str] = ("A", "B", "C"),
) -> RegionesTres:
    """Reparte un universo entre tres conjuntos (inclusión-exclusión completa).

    `n(A∪B∪C) = n(A)+n(B)+n(C) − n(A∩B) − n(A∩C) − n(B∩C) + n(A∩B∩C)`.

    Los pares que se reciben son las intersecciones **totales** (incluyen a
    quienes están en los tres), tal como vienen en los enunciados.
    """
    a, b, c = etiquetas
    ab = _exigir_no_negativo(f"{a} y {b} sin {c}", n_ab - n_abc)
    ac = _exigir_no_negativo(f"{a} y {c} sin {b}", n_ac - n_abc)
    bc = _exigir_no_negativo(f"{b} y {c} sin {a}", n_bc - n_abc)
    solo_a = _exigir_no_negativo(f"solo {a}", n_a - ab - ac - n_abc)
    solo_b = _exigir_no_negativo(f"solo {b}", n_b - ab - bc - n_abc)
    solo_c = _exigir_no_negativo(f"solo {c}", n_c - ac - bc - n_abc)

    total_union = n_a + n_b + n_c - n_ab - n_ac - n_bc + n_abc
    ninguno = 0
    if universo is not None:
        ninguno = _exigir_no_negativo("ninguno de los tres", universo - total_union)

    return RegionesTres(
        solo_a=solo_a,
        solo_b=solo_b,
        solo_c=solo_c,
        ab=ab,
        ac=ac,
        bc=bc,
        abc=n_abc,
        ninguno=ninguno,
        union=total_union,
        etiquetas=etiquetas,
    )


# --------------------------------------------------------------------------
# Especificación declarativa de un diagrama (la que guardan las tarjetas)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class EspecificacionVenn:
    """Descripción de un diagrama tal como se guarda en el campo `venn`.

    Dos formas de describirlo:

    * `conjuntos`: los elementos literales (`{"A": [1,2,3], "B": [3,4]}`).
    * `cardinalidades`: los totales del enunciado (`{"a": 70, "b": 50, "ab": 30}`).
    """

    etiquetas: list[str]
    conjuntos: dict[str, list[Elemento]] | None = None
    cardinalidades: dict[str, int] | None = None
    universo: int | None = None
    titulo: str = ""
    elementos_universo: list[Elemento] = field(default_factory=list)

    @classmethod
    def desde_dict(cls, datos: dict) -> EspecificacionVenn:
        etiquetas = list(datos.get("etiquetas") or [])
        if len(etiquetas) not in (2, 3):
            raise DatosVennInvalidosError(
                "Un diagrama de Venn necesita exactamente 2 o 3 etiquetas."
            )
        conjuntos = datos.get("conjuntos")
        cardinalidades = datos.get("cardinalidades")
        if not conjuntos and not cardinalidades:
            raise DatosVennInvalidosError(
                "Falta describir el diagrama: hacen falta «conjuntos» o «cardinalidades»."
            )
        return cls(
            etiquetas=etiquetas,
            conjuntos={k: list(v) for k, v in conjuntos.items()} if conjuntos else None,
            cardinalidades=dict(cardinalidades) if cardinalidades else None,
            universo=datos.get("universo"),
            titulo=datos.get("titulo", ""),
            elementos_universo=list(datos.get("elementos_universo") or []),
        )

    def resolver_regiones(self) -> RegionesDos | RegionesTres:
        """Calcula las regiones, vengan de elementos o de cardinalidades."""
        if self.conjuntos:
            valores = [set(self.conjuntos.get(etiqueta, [])) for etiqueta in self.etiquetas]
            universo = len(set(self.elementos_universo)) or None
            if len(valores) == 2:
                a, b = valores
                return regiones_dos(
                    len(a), len(b), len(a & b), universo,
                    (self.etiquetas[0], self.etiquetas[1]),
                )
            a, b, c = valores
            return regiones_tres(
                len(a), len(b), len(c),
                len(a & b), len(a & c), len(b & c), len(a & b & c),
                universo,
                (self.etiquetas[0], self.etiquetas[1], self.etiquetas[2]),
            )

        card = self.cardinalidades or {}
        if len(self.etiquetas) == 2:
            return regiones_dos(
                int(card.get("a", 0)), int(card.get("b", 0)), int(card.get("ab", 0)),
                self.universo, (self.etiquetas[0], self.etiquetas[1]),
            )
        return regiones_tres(
            int(card.get("a", 0)), int(card.get("b", 0)), int(card.get("c", 0)),
            int(card.get("ab", 0)), int(card.get("ac", 0)), int(card.get("bc", 0)),
            int(card.get("abc", 0)),
            self.universo,
            (self.etiquetas[0], self.etiquetas[1], self.etiquetas[2]),
        )
