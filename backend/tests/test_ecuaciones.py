"""Pruebas del motor de sistemas de ecuaciones lineales.

Los valores esperados están **escritos a mano resolviendo cada sistema**, no
copiados de lo que devuelve el programa: copiarlos anularía el sentido de la
comprobación. Los sistemas provienen de las láminas de la asignatura y del
documento de ejercicios resueltos de la carpeta de apuntes.

Se cubren en particular los casos límite, que son donde un motor de sistemas
se rompe en silencio: incompatible, compatible indeterminado, coeficiente cero
y solución fraccionaria.
"""

from __future__ import annotations

from fractions import Fraction as F

import pytest

from app.excepciones import SistemaInvalidoError
from app.services import ecuaciones
from app.services.ecuaciones import Sistema, resolver_datos


# --------------------------------------------------------------------------
# Lectura de coeficientes
# --------------------------------------------------------------------------
class TestCoeficientes:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            (3, F(3)),
            (-2, F(-2)),
            ("3", F(3)),
            ("1/2", F(1, 2)),
            ("-1/2", F(-1, 2)),
            ("−1/2", F(-1, 2)),  # menos tipográfico, el que se copia del PDF
            ("0.5", F(1, 2)),
            ("", F(0)),
            (" 7 / 2 ", F(7, 2)),
            (F(5, 3), F(5, 3)),
        ],
    )
    def test_se_leen_exactos(self, entrada, esperado) -> None:
        assert ecuaciones.a_fraccion(entrada) == esperado

    def test_un_flotante_se_rechaza(self) -> None:
        """0.333 no es 1/3, y la unidad entera se apoya en esa diferencia."""
        with pytest.raises(SistemaInvalidoError) as error:
            ecuaciones.a_fraccion(0.333)
        assert "1/3" in str(error.value)

    def test_un_texto_que_no_es_numero_se_rechaza(self) -> None:
        with pytest.raises(SistemaInvalidoError):
            ecuaciones.a_fraccion("dos tercios")

    def test_un_denominador_cero_se_rechaza(self) -> None:
        with pytest.raises(SistemaInvalidoError):
            ecuaciones.a_fraccion("1/0")

    def test_un_booleano_no_es_un_coeficiente(self) -> None:
        with pytest.raises(SistemaInvalidoError):
            ecuaciones.a_fraccion(True)

    @pytest.mark.parametrize(
        ("valor", "texto"),
        [(F(3), "3"), (F(-3), "−3"), (F(1, 2), "1/2"), (F(-7, 4), "−7/4")],
    )
    def test_los_numeros_salen_con_el_menos_tipografico(self, valor, texto) -> None:
        """`str(Fraction(-3))` trae el guion ASCII y desentona con el resto del texto."""
        assert ecuaciones.formatear(valor) == texto


# --------------------------------------------------------------------------
# Validación del sistema
# --------------------------------------------------------------------------
class TestValidacion:
    def test_un_sistema_de_cuatro_ecuaciones_se_rechaza(self) -> None:
        with pytest.raises(SistemaInvalidoError):
            Sistema.desde_datos([[1, 0, 0, 0, 1]] * 4)

    def test_una_fila_con_el_largo_equivocado_se_rechaza(self) -> None:
        with pytest.raises(SistemaInvalidoError) as error:
            Sistema.desde_datos([[1, 1, 3], [1, 2]])
        assert "(2)" in str(error.value)

    def test_una_matriz_vacia_se_rechaza(self) -> None:
        with pytest.raises(SistemaInvalidoError):
            Sistema.desde_datos([])

    def test_las_incognitas_no_pueden_repetirse(self) -> None:
        with pytest.raises(SistemaInvalidoError):
            Sistema.desde_datos([[1, 1, 3], [1, 2, -8]], ["x", "x"])

    def test_hacen_falta_tantos_nombres_como_incognitas(self) -> None:
        with pytest.raises(SistemaInvalidoError):
            Sistema.desde_datos([[1, 1, 3], [1, 2, -8]], ["x", "y", "z"])

    def test_un_sistema_sin_ningun_coeficiente_se_rechaza(self) -> None:
        """El formulario vacío no es un sistema con infinitas soluciones."""
        with pytest.raises(SistemaInvalidoError):
            Sistema.desde_datos([[0, 0, 0], [0, 0, 0]])

    def test_un_metodo_inventado_se_rechaza(self) -> None:
        with pytest.raises(SistemaInvalidoError) as error:
            resolver_datos([[1, 1, 3], [1, 2, -8]], metodo="cramer")
        assert "sustitución" in str(error.value)

    def test_en_3x3_solo_se_desarrolla_por_reduccion(self) -> None:
        with pytest.raises(SistemaInvalidoError):
            resolver_datos([[1, 1, 1, 3], [1, 2, 1, 4], [1, 1, 2, 5]], metodo="igualación")

    def test_el_determinante_es_cosa_de_los_2x2(self) -> None:
        sistema = Sistema.desde_datos([[1, 1, 1, 3], [1, 2, 1, 4], [1, 1, 2, 5]])
        with pytest.raises(SistemaInvalidoError):
            ecuaciones.determinante_2x2(sistema)


# --------------------------------------------------------------------------
# Sistemas de 2 × 2 — resultados leídos del material de clase
# --------------------------------------------------------------------------
# (matriz, Δ, solución escrita a mano desde el enunciado)
DETERMINADOS_2X2 = [
    ([[1, 1, 3], [1, 2, -8]], F(1), {"x": F(14), "y": F(-11)}),
    ([[4, 5, 0], [-2, -1, 3]], F(6), {"x": F(-5, 2), "y": F(2)}),
    ([[-2, 0, 1], [4, -3, 0]], F(6), {"x": F(-1, 2), "y": F(-2, 3)}),
    ([[7, 3, 0], [-5, 10, 0]], F(85), {"x": F(0), "y": F(0)}),
    ([[3, -7, -5], [4, -3, -2]], F(19), {"x": F(1, 19), "y": F(14, 19)}),
    ([[-13, 3, 7], [5, 22, 9]], F(-301), {"x": F(-127, 301), "y": F(152, 301)}),
    ([[9, -3, -3], [-2, 4, 1]], F(30), {"x": F(-3, 10), "y": F(1, 10)}),
    ([[1, 2, 5], [3, 4, 6]], F(-2), {"x": F(-4), "y": F(9, 2)}),
    ([[2, -1, 5], [5, 2, 8]], F(9), {"x": F(2), "y": F(-1)}),
    ([[3, 2, 2], [1, -7, -30]], F(-23), {"x": F(-2), "y": F(4)}),
    ([[3, -4, 4], ["1/2", -3, "-1/2"]], F(-7), {"x": F(2), "y": F(1, 2)}),
    ([[1, -1, 3], ["1/2", 1, 3]], F(3, 2), {"x": F(4), "y": F(1)}),
    ([[1, -1, 3], [-3, 1, 1]], F(-2), {"x": F(-2), "y": F(-5)}),
    ([[2, "1/2", 0], [3, -4, "-19/2"]], F(-19, 2), {"x": F(-1, 2), "y": F(2)}),
]


@pytest.mark.parametrize(("matriz", "delta", "esperada"), DETERMINADOS_2X2)
def test_sistemas_2x2_compatibles_determinados(matriz, delta, esperada) -> None:
    solucion = resolver_datos(matriz)
    assert solucion.clasificacion == "compatible determinado"
    assert solucion.delta == delta
    assert solucion.valores == esperada
    # La comprobación que no depende de nadie: sustituir en el sistema original.
    assert all(residuo == 0 for residuo in solucion.sistema.sustituir(solucion.valores))


def test_una_solucion_fraccionaria_no_se_redondea() -> None:
    """1/3 tiene que salir como 1/3; con flotantes saldría 0.3333333333333333."""
    solucion = resolver_datos([[3, 0, 1], [0, 7, 1]])
    assert solucion.valores == {"x": F(1, 3), "y": F(1, 7)}
    assert solucion.respuesta() == "x = 1/3, y = 1/7."


def test_un_coeficiente_cero_no_rompe_la_eliminacion() -> None:
    """−2x = 1 tiene a₁₂ = 0: el pivote de y hay que buscarlo en la otra fila."""
    solucion = resolver_datos([[-2, 0, 1], [4, -3, 0]])
    assert solucion.valores == {"x": F(-1, 2), "y": F(-2, 3)}


def test_un_cero_en_el_primer_pivote_obliga_a_intercambiar() -> None:
    """La primera ecuación no tiene x, así que hay que cambiar el orden."""
    solucion = resolver_datos([[0, 2, 4], [3, 1, 5]])
    assert solucion.valores == {"x": F(1), "y": F(2)}
    assert any("Intercambio" in paso for paso in solucion.pasos)


class TestIncompatibles:
    def test_2x2_rectas_paralelas(self) -> None:
        """7x + 4y = 1 y −7x − 4y = −3: coeficientes proporcionales, términos no."""
        solucion = resolver_datos([[7, 4, 1], [-7, -4, -3]])
        assert solucion.clasificacion == "incompatible"
        assert solucion.delta == 0
        assert solucion.valores == {}
        assert "paralelas" in solucion.interpretacion
        assert solucion.respuesta() == "El sistema no tiene solución."

    def test_3x3_con_contradiccion(self) -> None:
        """4x − y no puede valer −7 y 12 a la vez."""
        solucion = resolver_datos([[3, -2, 2, 6], [7, -3, 2, -1], [2, -3, 4, 0]])
        assert solucion.clasificacion == "incompatible"
        assert "planos" in solucion.interpretacion

    def test_una_fila_de_ceros_con_termino_no_nulo(self) -> None:
        """0x + 0y = 5 es falso aunque Δ valga 0 y el resto cuadre."""
        solucion = resolver_datos([[0, 0, 5], [1, 1, 2]])
        assert solucion.clasificacion == "incompatible"


class TestIndeterminados:
    def test_2x2_rectas_coincidentes(self) -> None:
        """La segunda ecuación es la primera por −1: es la misma recta."""
        solucion = resolver_datos([[7, 4, 0], [-7, -4, 0]])
        assert solucion.clasificacion == "compatible indeterminado"
        assert solucion.delta == 0
        assert solucion.parametros == ("y",)
        assert "coincidentes" in solucion.interpretacion

    def test_la_familia_de_soluciones_cumple_el_sistema(self) -> None:
        """Dos puntos concretos de la recta, escritos a mano: (0,0) y (4,−7)."""
        solucion = resolver_datos([[7, 4, 0], [-7, -4, 0]])
        for punto in ({"x": F(0), "y": F(0)}, {"x": F(4), "y": F(-7)}):
            assert all(residuo == 0 for residuo in solucion.sistema.sustituir(punto))

    def test_3x3_los_planos_se_cortan_en_una_recta(self) -> None:
        """(x, y, z) = (5t − 2, 4t − 3, t): una recta, no un punto."""
        solucion = resolver_datos([[1, -1, -1, 1], [-1, 2, -3, -4], [3, -2, -7, 0]])
        assert solucion.clasificacion == "compatible indeterminado"
        assert solucion.parametros == ("z",)
        assert solucion.formulas == {"x": "5z − 2", "y": "4z − 3"}
        assert "recta" in solucion.interpretacion

    @pytest.mark.parametrize("t", [F(0), F(1), F(-2), F(1, 2)])
    def test_cada_punto_de_la_familia_3x3_cumple_las_tres_ecuaciones(self, t) -> None:
        """La parametrización se valida con muestras, no comparándola con otra."""
        solucion = resolver_datos([[1, -1, -1, 1], [-1, 2, -3, -4], [3, -2, -7, 0]])
        punto = {"x": 5 * t - 2, "y": 4 * t - 3, "z": t}
        assert all(residuo == 0 for residuo in solucion.sistema.sustituir(punto))

    def test_dos_incognitas_libres(self) -> None:
        """Una sola ecuación repetida tres veces no restringe nada más que un plano."""
        solucion = resolver_datos([[1, 1, 1, 6], [2, 2, 2, 12], [3, 3, 3, 18]])
        assert solucion.clasificacion == "compatible indeterminado"
        assert solucion.parametros == ("y", "z")
        assert "coinciden" in solucion.interpretacion

    def test_dos_rectas_coincidentes_degeneradas(self) -> None:
        """Con 0 = 0 en una fila queda un solo grado de libertad en el plano."""
        solucion = resolver_datos([[0, 0, 0], [1, 1, 2]])
        assert solucion.clasificacion == "compatible indeterminado"
        assert solucion.formulas == {"x": "−y + 2"}


# --------------------------------------------------------------------------
# Sistemas de 3 × 3 — resultados leídos del material de clase
# --------------------------------------------------------------------------
DETERMINADOS_3X3 = [
    ([[1, 1, -1, -1], [4, -3, 2, 16], [2, -2, -3, 5]], {"x": 2, "y": -2, "z": 1}),
    ([[3, 3, 2, 4], [1, -3, 1, 10], [5, -2, -3, 8]], {"x": 2, "y": -2, "z": 2}),
    ([[3, 3, 2, 4], [1, -1, -1, 0], [0, 2, -3, -8]], {"x": 1, "y": -1, "z": 2}),
    ([[4, 0, -1, 7], [8, 5, -1, 0], [-1, -1, 5, 6]], {"x": 2, "y": -3, "z": 1}),
    ([[4, 0, -5, 6], [0, 5, -1, -17], [-1, -6, 5, 24]], {"x": 4, "y": -3, "z": 2}),
    ([[1, 1, -1, 6], [3, -2, 1, -5], [1, 3, -2, 14]], {"x": 1, "y": 3, "z": -2}),
]


@pytest.mark.parametrize(("matriz", "esperada"), DETERMINADOS_3X3)
def test_sistemas_3x3_compatibles_determinados(matriz, esperada) -> None:
    solucion = resolver_datos(matriz)
    assert solucion.clasificacion == "compatible determinado"
    assert solucion.valores == {nombre: F(v) for nombre, v in esperada.items()}
    assert solucion.delta is None, "el Δ del libro es solo el de 2 × 2"
    assert all(residuo == 0 for residuo in solucion.sistema.sustituir(solucion.valores))


def test_una_solucion_3x3_fraccionaria() -> None:
    solucion = resolver_datos([[1, 2, -1, -3], [2, -4, 1, -7], [-2, 2, -3, 4]])
    assert solucion.valores == {"x": F(-3), "y": F(1, 2), "z": F(1)}


# --------------------------------------------------------------------------
# Los tres métodos del curso
# --------------------------------------------------------------------------
@pytest.mark.parametrize("metodo", ecuaciones.METODOS)
def test_los_tres_metodos_llegan_a_la_misma_solucion(metodo: str) -> None:
    """El método elige cómo se cuenta el camino, nunca cuál es el resultado."""
    solucion = resolver_datos([[2, -1, 5], [5, 2, 8]], metodo=metodo)
    assert solucion.metodo == metodo
    assert solucion.valores == {"x": F(2), "y": F(-1)}
    assert len(solucion.pasos) >= 4


@pytest.mark.parametrize("metodo", ecuaciones.METODOS)
def test_los_tres_metodos_clasifican_igual_un_incompatible(metodo: str) -> None:
    solucion = resolver_datos([[7, 4, 1], [-7, -4, -3]], metodo=metodo)
    assert solucion.clasificacion == "incompatible"


@pytest.mark.parametrize("metodo", ecuaciones.METODOS)
def test_los_tres_metodos_clasifican_igual_un_indeterminado(metodo: str) -> None:
    solucion = resolver_datos([[7, 4, 0], [-7, -4, 0]], metodo=metodo)
    assert solucion.clasificacion == "compatible indeterminado"


def test_la_igualacion_avisa_cuando_no_se_puede_aplicar() -> None:
    """Si la incógnita no está en las dos ecuaciones, no hay nada que igualar."""
    with pytest.raises(SistemaInvalidoError) as error:
        resolver_datos([[2, 0, 4], [0, 3, 9]], metodo="igualación")
    assert "sustitución" in str(error.value)


def test_la_sustitucion_funciona_aunque_la_primera_no_sirva() -> None:
    """Con 0x + 0y… en la primera fila hay que despejar desde la segunda."""
    solucion = resolver_datos([[0, 0, 0], [1, 1, 2]], metodo="sustitución")
    assert solucion.clasificacion == "compatible indeterminado"


# --------------------------------------------------------------------------
# El desarrollo paso a paso: es material de estudio, no una calculadora
# --------------------------------------------------------------------------
class TestDesarrollo:
    def test_el_desarrollo_menciona_delta_en_los_2x2(self) -> None:
        solucion = resolver_datos([[1, 1, 3], [1, 2, -8]])
        assert any("Δ" in paso for paso in solucion.pasos)

    def test_el_desarrollo_termina_clasificando(self) -> None:
        solucion = resolver_datos([[1, 1, 3], [1, 2, -8]])
        assert any(paso.startswith("Clasificación:") for paso in solucion.pasos)

    def test_el_desarrollo_de_un_3x3_narra_cada_eliminacion(self) -> None:
        solucion = resolver_datos([[1, 1, -1, -1], [4, -3, 2, 16], [2, -2, -3, 5]])
        eliminaciones = [p for p in solucion.pasos if "para eliminar" in p]
        assert len(eliminaciones) >= 3

    def test_las_ecuaciones_se_reescriben_tal_como_se_leen(self) -> None:
        sistema = Sistema.desde_datos([[1, 1, 3], [-2, 0, 1], ["1/2", -3, "-1/2"]][:2])
        assert sistema.como_texto() == ["x + y = 3", "−2x = 1"]

    def test_una_ecuacion_sin_incognitas_se_escribe_como_cero(self) -> None:
        sistema = Sistema.desde_datos([[0, 0, 5], [1, 1, 2]])
        assert sistema.como_texto()[0] == "0 = 5"

    def test_los_coeficientes_fraccionarios_van_entre_parentesis(self) -> None:
        """«(1/2)x», no «1/2x», que se lee como 1/(2x)."""
        sistema = Sistema.desde_datos([["1/2", 1, 3], [1, 1, 2]])
        assert sistema.como_texto()[0] == "(1/2)x + y = 3"


# --------------------------------------------------------------------------
# Forma serializable
# --------------------------------------------------------------------------
def test_el_diccionario_de_salida_lleva_los_numeros_ya_escritos() -> None:
    datos = resolver_datos([[3, -4, 4], ["1/2", -3, "-1/2"]], metodo="reducción").como_dict()
    assert datos["valores"] == {"x": "2", "y": "1/2"}
    assert datos["delta"] == "−7"
    assert datos["clasificacion"] == "compatible determinado"
    assert datos["metodo"] == "reducción"
    assert datos["ecuaciones"][0] == "3x − 4y = 4"
    assert datos["pasos"] and datos["interpretacion"] and datos["respuesta"]


def test_el_diccionario_de_un_indeterminado_lleva_la_familia() -> None:
    datos = resolver_datos([[7, 4, 0], [-7, -4, 0]]).como_dict()
    assert datos["parametros"] == ["y"]
    assert datos["formulas"] == {"x": "−(4/7)y"}
    assert datos["valores"] == {}
