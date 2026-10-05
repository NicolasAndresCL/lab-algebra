"""Verificación del contenido del temario.

Dos capas:

1. **Estructura**: ninguna tarjeta puede quedar sin ejercicio resuelto, sin
   fuente o con una fórmula, un diagrama o un sistema que no se pueda calcular.
2. **Resultados**: las clasificaciones lógicas, las regiones de Venn y las
   soluciones de los sistemas que afirman las tarjetas se contrastan con lo que
   calculan los motores. Los valores esperados de este archivo se leyeron de
   los PDF de clase —o se resolvieron a mano desde la lámina—, **no** se
   copiaron del código: si un motor cambiara de comportamiento, este test lo
   delata.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from app.seed.cargar import MAZOS
from app.services import conjuntos, ecuaciones, logica, matrices, venn

TARJETAS = [(mazo["slug"], tarjeta) for mazo in MAZOS for tarjeta in mazo["tarjetas"]]
IDS = [f"{slug}::{t['concepto']}" for slug, t in TARJETAS]


class TestEstructura:
    def test_hay_contenido_de_las_cuatro_unidades(self) -> None:
        unidades = {mazo["unidad"] for mazo in MAZOS}
        assert unidades == {"Lógica", "Conjuntos", "Ecuaciones", "Matrices"}

    def test_los_slugs_de_mazo_son_unicos(self) -> None:
        slugs = [mazo["slug"] for mazo in MAZOS]
        assert len(slugs) == len(set(slugs))

    def test_los_conceptos_no_se_repiten_dentro_de_un_mazo(self) -> None:
        for mazo in MAZOS:
            conceptos = [t["concepto"] for t in mazo["tarjetas"]]
            assert len(conceptos) == len(set(conceptos)), mazo["slug"]

    @pytest.mark.parametrize(("slug", "tarjeta"), TARJETAS, ids=IDS)
    def test_cada_tarjeta_lleva_ejercicio_resuelto(self, slug: str, tarjeta: dict) -> None:
        """El requisito central: definición + enunciado + desarrollo + respuesta."""
        for campo in (
            "pregunta",
            "definicion",
            "ejercicio_enunciado",
            "ejercicio_desarrollo",
            "ejercicio_respuesta",
            "fuente",
        ):
            valor = tarjeta.get(campo, "")
            assert valor and valor.strip(), f"{slug}::{tarjeta['concepto']} sin «{campo}»"

    @pytest.mark.parametrize(("slug", "tarjeta"), TARJETAS, ids=IDS)
    def test_el_desarrollo_explica_mas_que_la_respuesta(
        self, slug: str, tarjeta: dict
    ) -> None:
        """Un desarrollo que no desarrolla nada no enseña a resolver el ejercicio."""
        assert len(tarjeta["ejercicio_desarrollo"]) > len(tarjeta["ejercicio_respuesta"])

    @pytest.mark.parametrize(("slug", "tarjeta"), TARJETAS, ids=IDS)
    def test_las_formulas_se_pueden_calcular(self, slug: str, tarjeta: dict) -> None:
        formula = tarjeta.get("formula")
        if formula:
            logica.construir_tabla(formula)

    @pytest.mark.parametrize(("slug", "tarjeta"), TARJETAS, ids=IDS)
    def test_los_diagramas_se_pueden_generar(self, slug: str, tarjeta: dict) -> None:
        especificacion = tarjeta.get("venn")
        if especificacion:
            png = venn.generar_png(especificacion)
            assert png.startswith(b"\x89PNG"), "el resultado no es un PNG válido"

    @pytest.mark.parametrize(("slug", "tarjeta"), TARJETAS, ids=IDS)
    def test_los_sistemas_se_pueden_resolver(self, slug: str, tarjeta: dict) -> None:
        declarado = tarjeta.get("sistema")
        if declarado:
            ecuaciones.resolver_datos(
                declarado["matriz"],
                declarado.get("incognitas"),
                declarado.get("metodo"),
            )

    @pytest.mark.parametrize(("slug", "tarjeta"), TARJETAS, ids=IDS)
    def test_las_operaciones_con_matrices_se_pueden_calcular(
        self, slug: str, tarjeta: dict
    ) -> None:
        declarada = tarjeta.get("matriz")
        if declarada:
            matrices.operar_datos(declarada)

    @pytest.mark.parametrize(("slug", "tarjeta"), TARJETAS, ids=IDS)
    def test_ninguna_matriz_lleva_un_numero_con_coma(self, slug: str, tarjeta: dict) -> None:
        declarada = tarjeta.get("matriz")
        if declarada:
            planos = [
                v for clave in ("a", "b") for fila in declarada.get(clave) or [] for v in fila
            ] + [declarada.get("k"), declarada.get("m")]
            assert not any(isinstance(v, float) for v in planos), (
                f"{slug}::{tarjeta['concepto']} guarda un flotante; usa «1/2»"
            )

    @pytest.mark.parametrize(("slug", "tarjeta"), TARJETAS, ids=IDS)
    def test_ningun_sistema_lleva_un_coeficiente_con_coma(
        self, slug: str, tarjeta: dict
    ) -> None:
        """Un 0.333 guardado en la base ya no se puede volver a leer como 1/3."""
        declarado = tarjeta.get("sistema")
        if declarado:
            planos = [valor for fila in declarado["matriz"] for valor in fila]
            assert not any(isinstance(valor, float) for valor in planos), (
                f"{slug}::{tarjeta['concepto']} guarda un flotante; usa «1/2» o «39/5»"
            )


# --------------------------------------------------------------------------
# Resultados esperados, leídos de los PDF de clase
# --------------------------------------------------------------------------
CLASIFICACIONES_ESPERADAS = {
    "p ∨ ¬p": "tautología",
    "p ∧ ¬p": "contradicción",
    "(p ∧ q) → p": "tautología",
    "(p ∧ q) ∧ (¬p ∨ ¬q)": "contradicción",
    "(p ∨ q) ∧ ¬p": "contingencia",
    "¬(p ∧ q) ↔ (¬p ∨ ¬q)": "tautología",
    "((p → q) ∧ p) → q": "tautología",
    "¬(p → q) ↔ (p ∧ ¬q)": "tautología",
    "((p ∨ q) ∧ ¬p) → q": "tautología",
    "p ↔ ¬p": "contradicción",
    "(p ∨ r) → (p ∧ ¬s)": "contingencia",
    "(p ⊻ q) ↔ ¬(p ↔ q)": "tautología",
}


@pytest.mark.parametrize(
    ("formula", "esperada"), sorted(CLASIFICACIONES_ESPERADAS.items())
)
def test_clasificaciones_del_temario(formula: str, esperada: str) -> None:
    assert logica.construir_tabla(formula).clasificacion == esperada


def test_la_tabla_del_taller_coincide_con_la_del_pdf() -> None:
    """(p ∨ r) ⇒ (p ∧ ¬s) — ítem de desarrollo de la Tarea-Taller 1.

    Orden de filas VVV, VVF, VFV, VFF, FVV, FVF, FFV, FFF.
    """
    tabla = logica.construir_tabla("(p ∨ r) → (p ∧ ¬s)")
    assert tabla.variables == ["p", "r", "s"]
    assert "".join("V" if x else "F" for x in tabla.resultado) == "FVFVFFVV"


# Regiones esperadas de los problemas de encuesta (láminas de la Clase 2).
REGIONES_DOS_ESPERADAS = [
    # (etiquetas, n_a, n_b, n_ab, universo, solo_a, solo_b, union, ninguno)
    (("Java", "Python"), 70, 50, 30, 120, 40, 20, 90, 30),
    (("SQL", "MongoDB"), 40, 30, 20, 90, 20, 10, 50, 40),
    (("Antivirus", "Firewall"), 60, 45, 25, 100, 35, 20, 80, 20),
]


@pytest.mark.parametrize(
    ("etiquetas", "n_a", "n_b", "n_ab", "universo", "solo_a", "solo_b", "union", "ninguno"),
    REGIONES_DOS_ESPERADAS,
    ids=[e[0][0] for e in REGIONES_DOS_ESPERADAS],
)
def test_problemas_de_dos_conjuntos(
    etiquetas, n_a, n_b, n_ab, universo, solo_a, solo_b, union, ninguno
) -> None:
    regiones = conjuntos.regiones_dos(n_a, n_b, n_ab, universo, etiquetas)
    assert regiones.solo_a == solo_a
    assert regiones.solo_b == solo_b
    assert regiones.union == union
    assert regiones.ninguno == ninguno
    # El universo se reparte por completo: nada se pierde ni se cuenta dos veces.
    assert regiones.solo_a + regiones.solo_b + regiones.ambos + regiones.ninguno == universo


def test_problema_de_las_revistas() -> None:
    """Problema 8: 200 personas, tres revistas."""
    r = conjuntos.regiones_tres(120, 90, 70, 50, 40, 30, 20, 200, ("A", "B", "C"))
    assert r.union == 180
    assert r.ninguno == 20
    assert (r.solo_a, r.solo_b, r.solo_c) == (50, 30, 20)
    assert r.exactamente_uno == 100
    assert (r.ab, r.ac, r.bc, r.abc) == (30, 20, 10, 20)
    assert r.solo_a + r.solo_b + r.solo_c + r.ab + r.ac + r.bc + r.abc + r.ninguno == 200


def test_problema_de_las_herramientas() -> None:
    """Problema 11: 150 ingenieros, Git / Docker / Kubernetes."""
    r = conjuntos.regiones_tres(90, 80, 70, 50, 40, 30, 20, 150, ("Git", "Docker", "K8s"))
    assert r.union == 140
    assert r.ninguno == 10
    assert (r.solo_a, r.solo_b, r.solo_c) == (20, 20, 20)
    assert r.exactamente_uno == 60


def test_problema_de_la_panaderia() -> None:
    """Práctica 1: el total es un resultado, no un dato del enunciado."""
    r = conjuntos.regiones_tres(109, 203, 162, 25, 28, 41, 5, etiquetas=("M", "H", "D"))
    assert r.union == 385
    assert r.union + 115 == 500  # las 115 que no consumen ninguno
    assert r.solo_a == 61
    assert r.al_menos_dos == 84


def test_las_regiones_negativas_se_rechazan() -> None:
    """Un enunciado mal copiado no puede producir un diagrama imposible."""
    from app.excepciones import DatosVennInvalidosError

    with pytest.raises(DatosVennInvalidosError):
        conjuntos.regiones_dos(n_a=10, n_b=10, n_ab=15)


# --------------------------------------------------------------------------
# Sistemas de las tarjetas: clasificación y solución leídas del material
# --------------------------------------------------------------------------
# Misma disciplina que `CLASIFICACIONES_ESPERADAS`: cada valor está **resuelto
# a mano desde el enunciado de la lámina**, no copiado de lo que devuelve el
# motor. Copiarlo anularía el sentido de la comprobación — el test pasaría
# aunque el motor se equivocara, porque estaría comparándose consigo mismo.
#
# Clave: el concepto de la tarjeta. Valor: clasificación, solución exacta
# (vacía si no es determinado) y, en los 2 × 2, el Δ que pide el libro.
SISTEMAS_ESPERADOS: dict[str, dict] = {
    "Solución de un sistema": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(1),
        "valores": {"x": Fraction(14), "y": Fraction(-11)},
    },
    "Matriz aumentada": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(6),
        "valores": {"x": Fraction(-1, 2), "y": Fraction(-2, 3)},
    },
    "Interpretación geométrica en el plano": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(9),
        "valores": {"x": Fraction(2), "y": Fraction(-1)},
    },
    "Interpretación geométrica en el espacio": {
        "clasificacion": "compatible determinado",
        "delta": None,
        "valores": {"x": Fraction(2), "y": Fraction(-2), "z": Fraction(1)},
    },
    "Método de sustitución": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(-23),
        "valores": {"x": Fraction(-2), "y": Fraction(4)},
    },
    "Método de igualación": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(-2),
        "valores": {"x": Fraction(-2), "y": Fraction(-5)},
    },
    "Método de reducción": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(3, 2),
        "valores": {"x": Fraction(4), "y": Fraction(1)},
    },
    "Sistemas con coeficientes fraccionarios": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(-7),
        "valores": {"x": Fraction(2), "y": Fraction(1, 2)},
    },
    "Planteamiento de un problema": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(-2),
        "valores": {"x": Fraction(30), "y": Fraction(25)},
    },
    "Problema de precios": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(-7),
        # 1,20 € y 1,80 €, escritos como fracción exacta.
        "valores": {"x": Fraction(6, 5), "y": Fraction(9, 5)},
    },
    "Sistema homogéneo": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(85),
        "valores": {"x": Fraction(0), "y": Fraction(0)},
    },
    "Determinante Δ de un 2 × 2": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(6),
        "valores": {"x": Fraction(-5, 2), "y": Fraction(2)},
    },
    "Compatible determinado": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(-301),
        "valores": {"x": Fraction(-127, 301), "y": Fraction(152, 301)},
    },
    "Compatible indeterminado": {
        "clasificacion": "compatible indeterminado",
        "delta": Fraction(0),
        "valores": {},
    },
    "Incompatible": {
        "clasificacion": "incompatible",
        "delta": Fraction(0),
        "valores": {},
    },
    "Resolver un 3 × 3 por sustitución": {
        "clasificacion": "compatible determinado",
        "delta": None,
        "valores": {"x": Fraction(2), "y": Fraction(-2), "z": Fraction(2)},
    },
    "Un 3 × 3 sin solución": {
        "clasificacion": "incompatible",
        "delta": None,
        "valores": {},
    },
    "Un 3 × 3 con infinitas soluciones": {
        "clasificacion": "compatible indeterminado",
        "delta": None,
        "valores": {},
    },
    # Unidad de matrices: los cuatro sistemas que se resuelven por Cramer.
    # Láminas 46 y 47; D, Dₓ y D_y calculados a mano en cada caso.
    "Regla de Cramer": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(15),
        "valores": {"x": Fraction(2), "y": Fraction(1)},
    },
    "Cramer cuando D = 0": {
        "clasificacion": "incompatible",
        "delta": Fraction(0),
        "valores": {},
    },
    "Cramer con soluciones fraccionarias": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(19),
        "valores": {"x": Fraction(1, 19), "y": Fraction(14, 19)},
    },
    "Cramer con una incógnita ausente": {
        "clasificacion": "compatible determinado",
        "delta": Fraction(6),
        "valores": {"x": Fraction(-1, 2), "y": Fraction(-2, 3)},
    },
}

TARJETAS_CON_SISTEMA = [(slug, t) for slug, t in TARJETAS if t.get("sistema")]


@pytest.mark.parametrize(
    ("slug", "tarjeta"),
    TARJETAS_CON_SISTEMA,
    ids=[t["concepto"] for _, t in TARJETAS_CON_SISTEMA],
)
def test_los_sistemas_del_temario_dan_lo_que_dice_la_lamina(
    slug: str, tarjeta: dict
) -> None:
    esperado = SISTEMAS_ESPERADOS.get(tarjeta["concepto"])
    assert esperado is not None, (
        f"«{tarjeta['concepto']}» declara un sistema pero no tiene su resultado "
        f"esperado en SISTEMAS_ESPERADOS. Resuélvelo a mano desde la lámina."
    )
    declarado = tarjeta["sistema"]
    solucion = ecuaciones.resolver_datos(
        declarado["matriz"], declarado.get("incognitas"), declarado.get("metodo")
    )
    assert solucion.clasificacion == esperado["clasificacion"]
    assert solucion.delta == esperado["delta"]
    assert solucion.valores == esperado["valores"]


def test_toda_tarjeta_con_sistema_tiene_resultado_esperado() -> None:
    """La comprobación que obliga a mantener la disciplina al añadir tarjetas."""
    declarados = {t["concepto"] for _, t in TARJETAS_CON_SISTEMA}
    assert declarados <= set(SISTEMAS_ESPERADOS), (
        f"sin resultado esperado: {sorted(declarados - set(SISTEMAS_ESPERADOS))}"
    )
    assert set(SISTEMAS_ESPERADOS) <= declarados, (
        f"esperados que ya no corresponden a ninguna tarjeta: "
        f"{sorted(set(SISTEMAS_ESPERADOS) - declarados)}"
    )


# --------------------------------------------------------------------------
# Matrices y determinantes
# --------------------------------------------------------------------------
# Misma disciplina que en los sistemas: cada valor sale **de la lámina** —que
# en esta unidad casi siempre imprime la respuesta— o de resolverlo a mano. Las
# claves posibles son `resultado` (la matriz), `valor` (traza o determinante),
# `tipos` (los de A, al clasificar), `invertible` y `definida`.
def _m(*filas: list[int]) -> list[list[Fraction]]:
    return [[Fraction(v) for v in fila] for fila in filas]


MATRICES_ESPERADAS: dict[str, dict] = {
    # Fundamentos
    "Matriz": {"tipos": []},
    "Elemento aᵢⱼ": {"valor": Fraction(14)},
    "Matriz traspuesta": {"resultado": _m([1, 5], [2, 6], [10, 9])},
    "Propiedades de la traspuesta": {"resultado": _m([-4, -10], [6, 12])},
    "Traza de una matriz": {"valor": Fraction(11)},
    "Propiedades de la traza": {"valor": Fraction(8)},
    # Tipos
    "Matriz cuadrada": {"tipos": ["cuadrada"]},
    "Matriz identidad": {"resultado": _m([1, 2, 0], [7, 3, -4])},
    "Matriz diagonal": {
        "tipos": ["cuadrada", "diagonal", "triangular superior", "triangular inferior",
                  "simétrica"],
    },
    "Matriz escalar": {"resultado": _m([5, 0, 0], [0, 5, 0], [0, 0, 5])},
    "Matriz triangular": {"valor": Fraction(-15), "invertible": True},
    "Matriz simétrica": {"tipos": ["cuadrada", "simétrica"]},
    "Matriz antisimétrica": {"tipos": ["cuadrada", "antisimétrica"]},
    # Operaciones (las láminas 23 a 31 traen la respuesta impresa)
    "Suma de matrices": {"resultado": _m([4, 3, 3], [2, 3, 2])},
    "Propiedades de la suma": {"resultado": _m([4, 3, 3], [2, 3, 2])},
    "Resta de matrices": {"resultado": _m([-1, 4, -5], [11, 4, 2], [5, -16, 7])},
    "Producto por un escalar": {"resultado": _m([3, 6], [9, 12])},
    "Propiedades del producto por un escalar": {"resultado": _m([13, 4, -4], [11, -4, 1])},
    "Producto de matrices": {"resultado": _m([-9, -42])},
    "Producto fila por columna": {"resultado": _m([27, 55, 31], [17, 49, 36])},
    "El producto no es conmutativo": {"resultado": _m([-4, 6], [-10, 12])},
    "Cuándo no está definido el producto": {"definida": False},
    "Propiedades del producto de matrices": {"resultado": _m([-8, 12], [-20, 24])},
    # Determinantes
    "Determinante": {"valor": Fraction(-11), "invertible": True},
    "Determinante de 2 × 2": {"valor": Fraction(15)},
    "Determinante de 3 × 3 (regla de Sarrus)": {"valor": Fraction(-8)},
    "Traspuesta y permutación de líneas": {"valor": Fraction(8)},
    "Determinantes que se anulan": {"valor": Fraction(0), "invertible": False},
    "Determinante de un producto": {"valor": Fraction(12)},
    "Multiplicar una línea por un número": {"valor": Fraction(-22)},
    "Determinante de una matriz triangular": {"valor": Fraction(-12)},
    "Matriz inversa: cuándo existe": {"valor": Fraction(0), "invertible": False},
}

TARJETAS_CON_MATRIZ = [(slug, t) for slug, t in TARJETAS if t.get("matriz")]


@pytest.mark.parametrize(
    ("slug", "tarjeta"),
    TARJETAS_CON_MATRIZ,
    ids=[t["concepto"] for _, t in TARJETAS_CON_MATRIZ],
)
def test_las_matrices_del_temario_dan_lo_que_dice_la_lamina(slug: str, tarjeta: dict) -> None:
    esperado = MATRICES_ESPERADAS.get(tarjeta["concepto"])
    assert esperado is not None, (
        f"«{tarjeta['concepto']}» declara una operación con matrices pero no tiene su "
        f"resultado esperado en MATRICES_ESPERADAS. Resuélvela a mano desde la lámina."
    )
    resultado = matrices.operar_datos(tarjeta["matriz"])
    assert resultado.definida == esperado.get("definida", True)
    if "resultado" in esperado:
        assert resultado.matriz.tolist() == esperado["resultado"]
    if "valor" in esperado:
        assert resultado.valor == esperado["valor"]
    if "tipos" in esperado:
        assert resultado.tipos["A"] == esperado["tipos"]
    if "invertible" in esperado:
        assert resultado.invertible is esperado["invertible"]


def test_toda_tarjeta_con_matriz_tiene_resultado_esperado() -> None:
    """En los dos sentidos: ni tarjetas sin esperado ni esperados huérfanos."""
    declaradas = {t["concepto"] for _, t in TARJETAS_CON_MATRIZ}
    assert declaradas <= set(MATRICES_ESPERADAS), (
        f"sin resultado esperado: {sorted(declaradas - set(MATRICES_ESPERADAS))}"
    )
    assert set(MATRICES_ESPERADAS) <= declaradas, (
        f"esperados que ya no corresponden a ninguna tarjeta: "
        f"{sorted(set(MATRICES_ESPERADAS) - declaradas)}"
    )


def test_la_respuesta_escrita_cita_el_resultado_del_motor() -> None:
    """Tercera comprobación, barata: el texto de la tarjeta cita el número del motor.

    Cubre lo que los esperados no ven: que la respuesta escrita a mano diga lo
    mismo que el campo `matriz`. Si alguien corrige uno y olvida el otro, salta.
    """
    discrepancias = []
    for _, tarjeta in TARJETAS_CON_MATRIZ:
        resultado = matrices.operar_datos(tarjeta["matriz"])
        if resultado.valor is not None:
            citado = matrices.formatear(resultado.valor)
        elif resultado.matriz is not None:
            citado = matrices.en_linea(resultado.matriz)
        else:
            continue
        if citado not in tarjeta["ejercicio_respuesta"] + tarjeta["ejercicio_desarrollo"]:
            discrepancias.append(f"{tarjeta['concepto']}: el motor da {citado}")
    assert not discrepancias, "; ".join(discrepancias)
