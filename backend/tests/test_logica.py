"""Pruebas del motor de lógica proposicional."""

from __future__ import annotations

import pytest

from app.excepciones import FormulaInvalidaError
from app.services import logica


class TestTokenizacion:
    def test_acepta_los_alias_ascii(self) -> None:
        """`p -> q` y `p → q` deben producir el mismo árbol."""
        assert logica.analizar("p -> q") == logica.analizar("p → q")
        assert logica.analizar("~p & q") == logica.analizar("¬p ∧ q")
        assert logica.analizar("p <-> q") == logica.analizar("p ↔ q")

    def test_la_flecha_larga_gana_a_la_corta(self) -> None:
        """`<->` no debe leerse como `<` seguido de `->`."""
        arbol = logica.analizar("p <-> q")
        assert isinstance(arbol, logica.Binaria)
        assert arbol.operador == logica.BICONDICIONAL

    @pytest.mark.parametrize("formula", ["", "   ", "p $ q", "p ∧", "(p ∨ q", "p q)"])
    def test_rechaza_formulas_malformadas(self, formula: str) -> None:
        with pytest.raises(FormulaInvalidaError):
            logica.construir_tabla(formula)

    def test_el_error_indica_donde_esta_el_problema(self) -> None:
        with pytest.raises(FormulaInvalidaError) as excepcion:
            logica.construir_tabla("p ∧ $")
        assert excepcion.value.detalle()["posicion"] == 4


class TestPrecedencia:
    def test_la_negacion_liga_mas_fuerte_que_la_conjuncion(self) -> None:
        assert logica.analizar("¬p ∧ q") == logica.analizar("(¬p) ∧ q")

    def test_la_conjuncion_liga_mas_que_la_disyuncion(self) -> None:
        assert logica.analizar("p ∨ q ∧ r") == logica.analizar("p ∨ (q ∧ r)")

    def test_el_condicional_asocia_por_la_derecha(self) -> None:
        assert logica.analizar("p → q → r") == logica.analizar("p → (q → r)")

    def test_el_condicional_liga_menos_que_la_disyuncion(self) -> None:
        assert logica.analizar("p ∨ r → t") == logica.analizar("(p ∨ r) → t")


class TestTablaDeVerdad:
    def test_el_numero_de_filas_es_dos_elevado_a_n(self) -> None:
        assert logica.construir_tabla("¬p").numero_filas == 2
        assert logica.construir_tabla("p ∧ q").numero_filas == 4
        assert logica.construir_tabla("(p ∨ r) → (p ∧ ¬s)").numero_filas == 8
        assert logica.construir_tabla("(p ∧ q) → (r ∨ ¬s)").numero_filas == 16

    def test_una_sola_variable_da_dos_filas_no_cuatro(self) -> None:
        """Uniformar todas las tablas a 4 filas repetiría casos inexistentes."""
        tabla = logica.construir_tabla("p ↔ ¬p")
        assert tabla.numero_filas == 2
        assert tabla.variables == ["p"]

    def test_la_primera_fila_es_todo_verdadero(self) -> None:
        """El orden de la asignatura empieza por V, no por F."""
        tabla = logica.construir_tabla("p ∧ q")
        assert tabla.filas[0][:2] == [True, True]
        assert tabla.filas[-1][:2] == [False, False]

    def test_hay_una_columna_por_cada_subformula(self) -> None:
        tabla = logica.construir_tabla("¬(p ∨ q)")
        assert tabla.columnas == ["p", "q", "p∨q", "¬(p∨q)"]

    def test_condicional_solo_falla_con_v_f(self) -> None:
        tabla = logica.construir_tabla("p → q")
        assert tabla.resultado == [True, False, True, True]

    def test_la_disyuncion_solo_falla_con_f_f(self) -> None:
        tabla = logica.construir_tabla("r ∨ s")
        assert tabla.resultado == [True, True, True, False]


class TestClasificacion:
    @pytest.mark.parametrize(
        ("formula", "esperada"),
        [
            ("(p ∧ q) → p", "tautología"),
            ("p ↔ ¬p", "contradicción"),
            ("(p ∨ q) ∧ ¬p", "contingencia"),
            ("¬(p ∧ q) ↔ (¬p ∨ ¬q)", "tautología"),
            ("(p ∧ ¬p) ∨ q", "contingencia"),
            ("(p ∨ q) → (p ∧ q)", "contingencia"),
            ("((p ∨ q) ∧ ¬p) → q", "tautología"),
            ("(p ∧ (p → q)) → q", "tautología"),
            ("¬(p → q) ↔ (p ∧ ¬q)", "tautología"),
            ("(p ∨ ¬q) ∧ (¬p ∨ q)", "contingencia"),
            ("p ∨ ¬p", "tautología"),
            ("p ∧ ¬p", "contradicción"),
        ],
    )
    def test_las_diez_proposiciones_del_taller(self, formula: str, esperada: str) -> None:
        """Las diez del taller de clase, más los dos principios básicos."""
        assert logica.construir_tabla(formula).clasificacion == esperada


class TestEquivalencias:
    @pytest.mark.parametrize(
        ("a", "b"),
        [
            ("¬(p ∧ q)", "¬p ∨ ¬q"),
            ("¬(p ∨ q)", "¬p ∧ ¬q"),
            ("p → q", "¬p ∨ q"),
            ("p → q", "¬q → ¬p"),
            ("p ↔ q", "(p → q) ∧ (q → p)"),
            ("p ⊻ q", "¬(p ↔ q)"),
        ],
    )
    def test_equivalencias_conocidas(self, a: str, b: str) -> None:
        assert logica.son_equivalentes(a, b)

    def test_el_condicional_no_equivale_a_su_reciproca(self) -> None:
        assert not logica.son_equivalentes("p → q", "q → p")


class TestLimites:
    def test_rechaza_demasiadas_variables(self) -> None:
        with pytest.raises(FormulaInvalidaError, match="máximo admitido"):
            logica.construir_tabla("a ∧ b ∧ c ∧ d ∧ e ∧ f ∧ g")

    def test_rechaza_una_formula_sin_variables(self) -> None:
        with pytest.raises(FormulaInvalidaError):
            logica.construir_tabla("()")
