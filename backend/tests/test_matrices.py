"""Motor de matrices y determinantes (`app.services.matrices`).

Tres capas:

1. **Contrato**: validación de la entrada, operaciones no definidas que salen
   como respuesta y no como error, forma del resultado.
2. **Propiedades del PDF**: cada una de las diez propiedades del determinante,
   la no conmutatividad del producto y las de la traspuesta y la traza, puestas
   a prueba sobre muchas matrices, no solo sobre el ejemplo de la lámina.
3. **Segundo camino, sympy**: las mismas operaciones calculadas con
   `sympy.Matrix`, que no comparte una línea con el motor (numpy + Sarrus).
   Una respuesta solo se da por buena si los dos caminos coinciden.

Las matrices aleatorias salen de un generador con semilla fija: si un caso
falla, falla siempre igual y se puede reproducir.
"""

from __future__ import annotations

import random
from fractions import Fraction as F

import numpy as np
import pytest
import sympy

from app.excepciones import MatrizInvalidaError
from app.services import matrices
from app.services.ecuaciones import resolver_datos
from app.services.matrices import ATAJOS, OPERACIONES, TIPOS, operar

SEMILLA = 20261005


def _aleatoria(rng: random.Random, filas: int, columnas: int) -> list[list[F]]:
    """Enteros pequeños y alguna fracción: lo que trae un ejercicio de clase."""
    def numero() -> F:
        return F(rng.randint(-9, 9), rng.choice((1, 1, 1, 2, 3)))

    return [[numero() for _ in range(columnas)] for _ in range(filas)]


def _sympy(filas: list[list[F]]) -> sympy.Matrix:
    return sympy.Matrix([[sympy.Rational(v.numerator, v.denominator) for v in f] for f in filas])


def _a_fracciones(matriz: sympy.Matrix) -> list[list[F]]:
    return [[F(int(v.p), int(v.q)) for v in matriz.row(i)] for i in range(matriz.rows)]


# --------------------------------------------------------------------------
# Contrato
# --------------------------------------------------------------------------
class TestEntrada:
    def test_lee_enteros_fracciones_y_texto(self) -> None:
        matriz = matrices.Matriz.desde_datos([[1, "−1/2"], ["3", F(2, 3)]])
        assert matriz.valores.tolist() == [[F(1), F(-1, 2)], [F(3), F(2, 3)]]
        assert matriz.orden == "2 × 2"

    @pytest.mark.parametrize(
        "filas",
        [[], [[1, 2], [3]], [[1] * 5], [[1]] * 5, "no es una lista", [[1, 2], "fila"]],
        ids=["vacía", "filas desiguales", "5 columnas", "5 filas", "texto", "fila texto"],
    )
    def test_rechaza_lo_que_no_es_una_matriz(self, filas) -> None:
        with pytest.raises(MatrizInvalidaError):
            matrices.Matriz.desde_datos(filas)

    def test_rechaza_flotantes_con_el_mismo_criterio_que_ecuaciones(self) -> None:
        with pytest.raises(MatrizInvalidaError, match="fracción exacta"):
            operar("traspuesta", [[0.5, 1]])

    def test_operacion_desconocida(self) -> None:
        with pytest.raises(MatrizInvalidaError, match="Elige entre"):
            operar("rango", [[1, 2], [3, 4]])

    def test_falta_b(self) -> None:
        with pytest.raises(MatrizInvalidaError, match="segunda matriz"):
            operar("suma", [[1]])

    def test_falta_el_escalar(self) -> None:
        with pytest.raises(MatrizInvalidaError, match="escalar k"):
            operar("escalar", [[1]])

    @pytest.mark.parametrize("datos", [None, {"a": [[1]]}, {"operacion": "traza"}])
    def test_operar_datos_exige_operacion_y_a(self, datos) -> None:
        with pytest.raises(MatrizInvalidaError):
            matrices.operar_datos(datos)

    def test_b_se_ignora_si_la_operacion_no_la_usa(self) -> None:
        resultado = operar("traza", [[1, 2], [3, 4]], b=[[9]])
        assert set(resultado.entrada.matrices) == {"A"}


class TestNoDefinida:
    """Una operación no definida es una respuesta de la unidad, no un error."""

    @pytest.mark.parametrize(
        ("clave", "a", "b", "motivo"),
        [
            ("suma", [[1, 2, 3]], [[1], [2], [3]], "mismo orden"),
            ("resta", [[1, 2]], [[1, 2], [3, 4]], "mismo orden"),
            ("producto", [[1, 2, 3]], [[1, 2, 3]], "columnas de A (3)"),
            ("producto_ba", [[1, 2], [3, 4]], [[1, 2, 3]], "columnas de B (3)"),
            ("traza", [[1, 2, 3]], None, "cuadradas"),
            ("determinante", [[1, 2]], None, "cuadradas"),
            ("determinante", [[1, 2, 3, 4]] * 4, None, "2 × 2 y de 3 × 3"),
            ("determinante", [[7]], None, "2 × 2 y de 3 × 3"),
        ],
    )
    def test_dice_por_que(self, clave, a, b, motivo) -> None:
        resultado = operar(clave, a, b)
        assert resultado.definida is False
        assert resultado.matriz is None and resultado.valor is None
        assert motivo in resultado.pasos[0]
        assert "no está definida" in resultado.respuesta()

    def test_la_formula_vale_para_cualquier_orden_aunque_el_temario_no(self) -> None:
        """Laplace es general; lo que limita a 2 × 2 y 3 × 3 son los `Requisito`."""
        rng = random.Random(SEMILLA)
        filas = _aleatoria(rng, 4, 4)
        det = _sympy(filas).det()
        assert matrices.determinante(np.array(filas, dtype=object)) == F(int(det.p), int(det.q))
        assert operar("determinante", filas).definida is False


class TestSalida:
    def test_como_dict_escribe_fracciones_con_el_menos_tipografico(self) -> None:
        datos = operar("escalar", [[1, -2]], k="1/2").como_dict()
        assert datos["resultado"] == [["1/2", "−1"]]
        assert datos["parametros"] == {"k": "1/2"}
        assert datos["invertible"] is None
        assert datos["respuesta"] == "k·A = [1/2 −1]."

    def test_los_tipos_incluyen_los_del_resultado(self) -> None:
        tipos = operar("resta", [[1, 2], [3, 4]], [[1, 2], [3, 4]]).tipos
        assert "nula" in tipos["A − B"]

    def test_la_traspuesta_es_una_copia(self) -> None:
        """Una vista de numpy compartiría memoria con A: cambiar una tocaría la otra."""
        resultado = operar("traspuesta", [[1, 2], [3, 4]])
        resultado.matriz[0, 0] = F(99)
        assert resultado.entrada.a.valores[0, 0] == 1

    def test_el_catalogo_trae_el_ejemplo_de_cada_operacion_y_funciona(self) -> None:
        for operacion in OPERACIONES.values():
            resultado = matrices.operar_datos({"operacion": operacion.clave, **operacion.ejemplo})
            assert resultado.definida, operacion.clave
            assert operacion.como_dict()["ejemplo"] == operacion.ejemplo

    def test_la_suma_escribe_el_negativo_entre_parentesis(self) -> None:
        """Lámina 23: «7 + (−5)», no «7 + −5»."""
        pasos = operar("suma", [[7]], [[-5]]).pasos
        assert "7 + (−5) = 2" in pasos[-1]

    def test_el_producto_avisa_de_que_no_conmuta(self) -> None:
        pasos = operar("producto", [[1, 2], [3, 4]], [[-2, 0], [-1, 3]]).pasos
        assert "no es conmutativo" in pasos[-1]

    def test_el_producto_no_avisa_cuando_si_conmutan(self) -> None:
        pasos = operar("producto", [[1, 2], [3, 4]], [[1, 0], [0, 1]]).pasos
        assert not any("conmutativo" in paso for paso in pasos)


# --------------------------------------------------------------------------
# Tipos de matrices
# --------------------------------------------------------------------------
class TestTipos:
    @pytest.mark.parametrize(
        ("filas", "esperados"),
        [
            # Láminas 10, 11, 12, 15, 19 y 20.
            ([[1, 0], [0, 1]], {"identidad", "escalar", "diagonal", "simétrica"}),
            ([[-1, 0], [0, 5]], {"diagonal", "simétrica"}),
            ([[5, 0, 0], [0, 5, 0], [0, 0, 5]], {"escalar", "diagonal"}),
            ([[1, 2, 7], [0, -3, -9], [0, 0, 5]], {"triangular superior"}),
            ([[8, 0, 0], [1, -3, 0], [-2, 5, 4]], {"triangular inferior"}),
            ([[1, 0, 3], [0, 2, -1], [3, -1, 0]], {"simétrica"}),
            ([[0, 3, -1], [-3, 0, 2], [1, -2, 0]], {"antisimétrica"}),
        ],
    )
    def test_ejemplos_de_las_laminas(self, filas, esperados) -> None:
        tipos = set(matrices.clasificar(matrices.Matriz.desde_datos(filas).valores))
        assert esperados <= tipos

    def test_una_no_cuadrada_solo_admite_los_tipos_que_no_lo_exigen(self) -> None:
        tipos = matrices.clasificar(matrices.Matriz.desde_datos([[0, 0, 0]]).valores)
        assert tipos == ["fila", "nula"]

    def test_la_jerarquia_identidad_escalar_diagonal(self) -> None:
        """Lámina 12: toda identidad es escalar, y toda escalar es diagonal."""
        rng = random.Random(SEMILLA)
        for _ in range(200):
            n = rng.randint(1, 4)
            valores = np.diag([F(rng.choice((1, 1, 2))) for _ in range(n)]).astype(object)
            tipos = set(matrices.clasificar(valores))
            if "identidad" in tipos:
                assert "escalar" in tipos
            if "escalar" in tipos:
                assert "diagonal" in tipos

    def test_coinciden_con_los_predicados_de_sympy(self) -> None:
        """Segundo camino: sympy decide simetría, diagonal y triangular por su cuenta."""
        rng = random.Random(SEMILLA)
        for _ in range(300):
            n = rng.randint(1, 4)
            filas = _aleatoria(rng, n, n)
            # Se fuerza la estructura en un tercio de los casos: con entradas al
            # azar casi nunca saldría una simétrica o una triangular.
            forma = rng.choice(("libre", "simetrica", "antisimetrica", "superior", "inferior"))
            for i in range(n):
                for j in range(n):
                    if forma == "simetrica" and j < i:
                        filas[i][j] = filas[j][i]
                    elif forma == "antisimetrica":
                        filas[i][j] = F(0) if i == j else (-filas[j][i] if j < i else filas[i][j])
                    elif (forma == "superior" and i > j) or (forma == "inferior" and i < j):
                        filas[i][j] = F(0)
            tipos = set(matrices.clasificar(np.array(filas, dtype=object)))
            s = _sympy(filas)
            assert ("simétrica" in tipos) == s.is_symmetric()
            assert ("antisimétrica" in tipos) == s.is_anti_symmetric()
            assert ("diagonal" in tipos) == s.is_diagonal()
            assert ("triangular superior" in tipos) == s.is_upper
            assert ("triangular inferior" in tipos) == s.is_lower
            assert ("identidad" in tipos) == (s == sympy.eye(n))

    def test_cada_tipo_tiene_definicion(self) -> None:
        assert all(tipo.definicion for tipo in TIPOS)

    def test_clasificar_narra_cada_definicion(self) -> None:
        resultado = operar("clasificar", [[1, 0, 3], [0, 2, -1], [3, -1, 0]])
        assert "✓ simétrica: Aᵀ = A." in resultado.pasos
        assert "✗ antisimétrica: Aᵀ = −A." in resultado.pasos
        assert resultado.respuesta() == "A es cuadrada, simétrica."

    def test_clasificar_una_matriz_sin_tipo_especial(self) -> None:
        resultado = operar("clasificar", [[2, 5, -1], [0, 3, 4]])
        assert "no es de ninguno" in resultado.respuesta()
        assert "No es cuadrada" in resultado.pasos[0]


# --------------------------------------------------------------------------
# Segundo camino: sympy
# --------------------------------------------------------------------------
class TestContraSympy:
    """El motor y sympy no comparten código; tienen que coincidir siempre."""

    @pytest.fixture
    def rng(self) -> random.Random:
        return random.Random(SEMILLA)

    def test_suma_resta_escalar_y_combinacion(self, rng: random.Random) -> None:
        for _ in range(150):
            m, n = rng.randint(1, 4), rng.randint(1, 4)
            a, b = _aleatoria(rng, m, n), _aleatoria(rng, m, n)
            k, c = F(rng.randint(-5, 5), rng.randint(1, 3)), F(rng.randint(-5, 5))
            sa, sb = _sympy(a), _sympy(b)
            sk, sc = sympy.Rational(k.numerator, k.denominator), sympy.Integer(int(c))
            assert operar("suma", a, b).matriz.tolist() == _a_fracciones(sa + sb)
            assert operar("resta", a, b).matriz.tolist() == _a_fracciones(sa - sb)
            assert operar("escalar", a, k=k).matriz.tolist() == _a_fracciones(sk * sa)
            assert operar("combinacion", a, b, k=k, m=c).matriz.tolist() == _a_fracciones(
                sk * sa + sc * sb
            )

    def test_producto_en_los_dos_ordenes(self, rng: random.Random) -> None:
        for _ in range(150):
            m, n, p = (rng.randint(1, 4) for _ in range(3))
            a, b = _aleatoria(rng, m, n), _aleatoria(rng, n, p)
            assert operar("producto", a, b).matriz.tolist() == _a_fracciones(
                _sympy(a) * _sympy(b)
            )
            ba = operar("producto_ba", a, b)
            assert ba.definida == (p == m)
            if ba.definida:
                assert ba.matriz.tolist() == _a_fracciones(_sympy(b) * _sympy(a))

    def test_traspuesta_y_traza(self, rng: random.Random) -> None:
        for _ in range(150):
            m, n = rng.randint(1, 4), rng.randint(1, 4)
            a = _aleatoria(rng, m, n)
            assert operar("traspuesta", a).matriz.tolist() == _a_fracciones(_sympy(a).T)
            if m == n:
                traza = _sympy(a).trace()
                assert operar("traza", a).valor == F(int(traza.p), int(traza.q))

    def test_determinante(self, rng: random.Random) -> None:
        for _ in range(300):
            n = rng.choice((2, 3))
            a = _aleatoria(rng, n, n)
            det = _sympy(a).det()
            assert operar("determinante", a).valor == F(int(det.p), int(det.q))


# --------------------------------------------------------------------------
# Las diez propiedades del determinante (láminas 39 a 43)
# --------------------------------------------------------------------------
class TestPropiedadesDelDeterminante:
    @pytest.fixture
    def casos(self) -> list[np.ndarray]:
        rng = random.Random(SEMILLA)
        return [
            np.array(_aleatoria(rng, n, n), dtype=object)
            for n in (2, 3) for _ in range(150)
        ]

    def test_1_coincide_con_el_de_la_traspuesta(self, casos) -> None:
        assert all(matrices.determinante(a) == matrices.determinante(a.T) for a in casos)

    def test_2_permutar_dos_filas_cambia_el_signo(self, casos) -> None:
        for a in casos:
            permutada = a[[1, 0, *range(2, a.shape[0])], :]
            assert matrices.determinante(permutada) == -matrices.determinante(a)

    def test_6_el_del_producto_es_el_producto(self, casos) -> None:
        for a, b in zip(casos[::2], casos[1::2], strict=True):
            if a.shape == b.shape:
                assert matrices.determinante(a @ b) == (
                    matrices.determinante(a) * matrices.determinante(b)
                )

    def test_7_una_linea_por_k_multiplica_por_k(self, casos) -> None:
        for a in casos:
            b = a.copy()
            b[0, :] = F(3) * b[0, :]
            assert matrices.determinante(b) == 3 * matrices.determinante(a)

    @pytest.mark.parametrize("n", [2, 3])
    def test_8_el_de_la_identidad_vale_1(self, n: int) -> None:
        assert matrices.determinante(np.eye(n, dtype=int).astype(object)) == 1

    def test_10_admite_inversa_si_y_solo_si_det_no_es_cero(self, casos) -> None:
        for a in casos:
            resultado = operar("determinante", a.tolist())
            assert resultado.invertible == (_sympy(a.tolist()).rank() == a.shape[0])

    @pytest.mark.parametrize(
        ("filas", "propiedad", "valor"),
        [
            ([[1, 0, -2], [3, 1, 1], [1, 0, -2]], 3, 0),   # lámina 40
            ([[1, 0, -2], [3, 1, 1], [0, 0, 0]], 4, 0),    # lámina 40
            ([[1, 0, -2], [3, 1, 1], [2, 0, -4]], 5, 0),   # lámina 41
            ([[-2, 4, -5], [0, 1, 3], [0, 0, 6]], 9, -12),  # lámina 43
            ([[2, 0], [0, 0]], 4, 0),
            ([[1, 2], [2, 4]], 5, 0),
        ],
    )
    def test_cada_atajo_se_reconoce_en_su_lamina(self, filas, propiedad, valor) -> None:
        a = matrices.Matriz.desde_datos(filas).valores
        atajo, _ = matrices.atajo_aplicable(a)
        assert atajo.propiedad == propiedad
        assert atajo.predice(a) == valor == matrices.determinante(a)

    def test_lo_que_predice_un_atajo_coincide_siempre_con_la_formula(self) -> None:
        """Es justo lo que afirma cada propiedad: se comprueba en miles de casos."""
        rng = random.Random(SEMILLA)
        vistos: set[int] = set()
        for _ in range(3000):
            n = rng.choice((2, 3))
            # Entradas en {−1, 0, 1, 2}: con tan pocos valores salen a menudo
            # filas nulas, iguales, proporcionales y matrices triangulares.
            a = np.array(
                [[F(rng.choice((-1, 0, 0, 1, 2))) for _ in range(n)] for _ in range(n)],
                dtype=object,
            )
            aplicable = matrices.atajo_aplicable(a)
            if aplicable is not None:
                atajo, _ = aplicable
                vistos.add(atajo.propiedad)
                assert atajo.predice(a) == matrices.determinante(a), a.tolist()
        assert vistos == {atajo.propiedad for atajo in ATAJOS}

    def test_el_desarrollo_narra_el_atajo_y_la_inversa(self) -> None:
        pasos = operar("determinante", [[2, 1, 1], [2, 1, 1], [0, -3, 1]]).pasos
        assert any("propiedad 3" in paso for paso in pasos)
        assert pasos[-1] == "det A = 0 → A es singular: no admite inversa (propiedad 10)."

    def test_sarrus_narra_las_seis_diagonales(self) -> None:
        """Lámina 39: |1 0 −2; 3 1 1; 3 2 0| = −8."""
        pasos = operar(
            "determinante", [[1, 0, -2], [3, 1, 1], [3, 2, 0]], desarrollo="Sarrus"
        ).pasos
        assert pasos[1] == "Bajan: (1)(1)(0) + (0)(1)(3) + (−2)(3)(2) = −12."
        assert pasos[3] == "det A = −12 − (−4) = −8."


# --------------------------------------------------------------------------
# Propiedades de la traspuesta, la traza y el producto (láminas 13, 18, 32)
# --------------------------------------------------------------------------
def test_propiedades_de_la_traspuesta_y_la_traza() -> None:
    rng = random.Random(SEMILLA)
    for _ in range(200):
        n = rng.randint(1, 4)
        a = np.array(_aleatoria(rng, n, n), dtype=object)
        b = np.array(_aleatoria(rng, n, n), dtype=object)
        assert np.array_equal((a @ b).T, b.T @ a.T)        # (AB)ᵀ = BᵀAᵀ
        assert np.array_equal((a + b).T, a.T + b.T)        # (A + B)ᵀ = Aᵀ + Bᵀ
        assert np.trace(a @ b) == np.trace(b @ a)          # tr(AB) = tr(BA)
        assert np.trace(a + b) == np.trace(a) + np.trace(b)


def test_por_que_no_se_usa_np_linalg_det() -> None:
    """La razón de trabajar con `Fraction` en vez de float64, en un caso.

    La matriz 1..9 es singular: su determinante exacto es 0, y el motor lo dice.
    `np.linalg.det` trabaja en coma flotante y devuelve un número que, según la
    plataforma, puede no ser exactamente 0: preguntar «¿admite inversa?» con
    `!= 0` sobre ese valor daría una respuesta equivocada.
    """
    filas = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert operar("determinante", filas).invertible is False
    assert abs(np.linalg.det(np.array(filas, dtype=float))) < 1e-9


# --------------------------------------------------------------------------
# Cramer (en el motor de ecuaciones)
# --------------------------------------------------------------------------
def test_cramer_con_d_cero_distingue_bien_los_dos_casos() -> None:
    """Con D = 0, «algún numerador ≠ 0» ⟺ incompatible (en 2 × 2 no nulos).

    La tarjeta «Cramer cuando D = 0» lo afirma, y el desarrollo de Cramer lo
    narra a partir de la clasificación de Gauss-Jordan. Aquí se comprueba que
    las dos cosas dicen lo mismo en todos los sistemas singulares de entradas
    pequeñas.
    """
    rng = random.Random(SEMILLA)
    singulares = 0
    for _ in range(4000):
        a, b, s, t = (rng.randint(-3, 3) for _ in range(4))
        factor = rng.choice((0, 1, -1, 2))
        c, d = factor * a, factor * b  # fuerza D = 0 casi siempre
        if (a, b, c, d) == (0, 0, 0, 0):
            continue
        if a * d - b * c != 0:
            continue
        singulares += 1
        delta_x, delta_y = s * d - b * t, a * t - s * c
        solucion = resolver_datos([[a, b, s], [c, d, t]], metodo="Cramer")
        esperada = "incompatible" if (delta_x, delta_y) != (0, 0) else "compatible indeterminado"
        assert solucion.clasificacion == esperada, (a, b, s, c, d, t)
    assert singulares > 500



# --------------------------------------------------------------------------
# «Matrices y determinantes II»: menores, cofactores, adjunta, inversa
# --------------------------------------------------------------------------
LAMINA_3 = [[2, -1, 3], [-2, 5, 1], [0, 6, -9]]
LAMINA_10 = [[3, 4, -1], [4, 6, 2], [8, -2, 3]]


class TestParametros:
    def test_el_catalogo_publica_los_parametros_de_cada_operacion(self) -> None:
        catalogo = {op.clave: op.como_dict() for op in OPERACIONES.values()}
        assert [p["nombre"] for p in catalogo["menor"]["parametros"]] == ["i", "j"]
        desarrollo = catalogo["determinante"]["parametros"][0]
        assert desarrollo["tipo"] == "opcion" and desarrollo["defecto"] == "fila 1"
        assert "Sarrus" in desarrollo["opciones"]

    @pytest.mark.parametrize(
        ("parametros", "mensaje"),
        [
            ({"i": 4, "j": 1}, "entre 1 y 3"),
            ({"i": "dos", "j": 1}, "no es un número"),
            ({"j": 1}, "Falta la fila i"),
        ],
    )
    def test_los_indices_se_validan_contra_el_orden_de_a(self, parametros, mensaje) -> None:
        with pytest.raises(MatrizInvalidaError, match=mensaje):
            operar("menor", LAMINA_3, **parametros)

    def test_una_linea_de_desarrollo_inventada_se_rechaza(self) -> None:
        with pytest.raises(MatrizInvalidaError, match="Elige entre"):
            operar("determinante", LAMINA_10, desarrollo="diagonal")

    def test_los_indices_llegan_tambien_como_texto(self) -> None:
        """Desde un formulario todo es texto: «1» vale lo mismo que 1."""
        assert operar("menor", LAMINA_3, i="1", j="2").valor == 18


class TestMenoresYCofactores:
    def test_laminas_3_y_4(self) -> None:
        assert operar("menor", LAMINA_3, i=1, j=2).valor == 18
        assert operar("menor", LAMINA_3, i=2, j=3).valor == 12
        assert operar("cofactor", LAMINA_3, i=1, j=2).valor == -18
        assert operar("cofactor", LAMINA_3, i=2, j=3).respuesta() == "A₂₃ = −12."

    def test_en_2x2_el_menor_es_el_numero_que_queda(self) -> None:
        resultado = operar("menor", [[2, -4], [1, 3]], i=1, j=1)
        assert resultado.valor == 3
        assert "M₁₁ = 3." in resultado.pasos

    def test_coinciden_con_sympy(self) -> None:
        rng = random.Random(SEMILLA)
        for _ in range(100):
            n = rng.choice((2, 3))
            filas = _aleatoria(rng, n, n)
            s = _sympy(filas)
            for i in range(n):
                for j in range(n):
                    assert operar("menor", filas, i=i + 1, j=j + 1).valor == F(
                        str(s.minor(i, j))
                    )
            assert operar("cofactores", filas).matriz.tolist() == _a_fracciones(
                s.cofactor_matrix()
            )
            assert operar("adjunta", filas).matriz.tolist() == _a_fracciones(s.adjugate())


class TestDesarrolloPorCofactores:
    @pytest.mark.parametrize("linea", matrices.LINEAS)
    def test_cualquier_linea_da_el_mismo_determinante(self, linea: str) -> None:
        """Láminas 10 y 11: 138 por la fila 1 y 138 por la columna 3."""
        resultado = operar("determinante", LAMINA_10, desarrollo=linea)
        assert resultado.valor == 138
        assert resultado.pasos[-2].endswith("= 138.")

    def test_la_narracion_suma_lo_mismo_que_la_formula_en_matrices_al_azar(self) -> None:
        """La última línea de la narración es una suma escrita: se reevalúa y se compara."""
        rng = random.Random(SEMILLA)
        for _ in range(200):
            a = np.array(_aleatoria(rng, 3, 3), dtype=object)
            linea = rng.choice(matrices.LINEAS)
            valor, pasos = matrices.desarrollo_por_cofactores(a, linea)
            assert valor == matrices.determinante(a)
            terminos = [
                [F(f.strip("()").replace("−", "-")) for f in termino.split("·")]
                for termino in pasos[-1].split(" = ")[1].split(" + ") if termino != "0"
            ]
            assert sum((x * y for x, y in terminos), F(0)) == valor

    def test_un_cero_en_la_linea_se_salta(self) -> None:
        """Lámina 6: desarrollando por la fila 2, el 0 de a₂₂ ahorra un menor."""
        resultado = operar("determinante", [[2, -3, 5], [1, 0, 4], [3, -3, 9]],
                           desarrollo="fila 2")
        assert resultado.valor == 0
        assert any(paso.startswith("a₂₂ = 0") for paso in resultado.pasos)


class TestInversa:
    def test_lamina_25(self) -> None:
        resultado = operar("inversa", [[1, 2, 0], [0, 1, 1], [1, 0, 3]])
        quinto = F(1, 5)
        assert resultado.matriz.tolist() == [
            [3 * quinto, -6 * quinto, 2 * quinto],
            [quinto, 3 * quinto, -quinto],
            [-quinto, 2 * quinto, quinto],
        ]
        assert resultado.pasos[-1] == "Comprobación: A·A⁻¹ = I ✓"
        assert resultado.invertible is True

    def test_lamina_27_con_determinante_1(self) -> None:
        resultado = operar("inversa", [[1, 2, 3], [0, 1, 4], [5, 6, 0]])
        assert resultado.matriz.tolist() == _a_fracciones(
            sympy.Matrix([[-24, 18, 5], [20, -15, -4], [-5, 4, 1]])
        )

    def test_lamina_20_en_2x2(self) -> None:
        """La lámina 20 no imprime la respuesta: (1/10)·[3 4; −1 2]."""
        resultado = operar("inversa", [[2, -4], [1, 3]])
        assert resultado.respuesta() == "A⁻¹ = [3/10 2/5; −1/10 1/5]."
        assert "A⁻¹ = (1/10)·[3 4; −1 2]." in resultado.pasos

    def test_una_singular_no_tiene_inversa_y_no_es_un_error(self) -> None:
        resultado = operar("inversa", [[2, 1, 1], [2, 1, 1], [0, -3, 1]])
        assert resultado.definida is False
        assert resultado.respuesta() == "A⁻¹ no existe para esta matriz."
        assert resultado.invertible is False
        assert "singular" in resultado.pasos[0]

    def test_coincide_con_sympy_y_da_la_identidad(self) -> None:
        rng = random.Random(SEMILLA)
        invertibles = 0
        for _ in range(200):
            n = rng.choice((2, 3))
            filas = _aleatoria(rng, n, n)
            resultado = operar("inversa", filas)
            s = _sympy(filas)
            assert resultado.definida == (s.det() != 0)
            if resultado.definida:
                invertibles += 1
                assert resultado.matriz.tolist() == _a_fracciones(s.inv())
                assert np.array_equal(
                    np.array(filas, dtype=object) @ resultado.matriz, np.eye(n, dtype=int)
                )
        assert invertibles > 150
