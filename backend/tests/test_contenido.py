"""Verificación del contenido del temario.

Dos capas:

1. **Estructura**: ninguna tarjeta puede quedar sin ejercicio resuelto, sin
   fuente o con una fórmula/diagrama que no se pueda calcular.
2. **Resultados**: las clasificaciones y las regiones de Venn que afirman las
   tarjetas se contrastan con lo que calculan los motores. Los valores
   esperados de este archivo se leyeron de los PDF de clase, **no** se copiaron
   del código: si el motor cambiara de comportamiento, este test lo delata.
"""

from __future__ import annotations

import pytest

from app.seed.cargar import MAZOS
from app.services import conjuntos, logica, venn

TARJETAS = [(mazo["slug"], tarjeta) for mazo in MAZOS for tarjeta in mazo["tarjetas"]]
IDS = [f"{slug}::{t['concepto']}" for slug, t in TARJETAS]


class TestEstructura:
    def test_hay_contenido_de_las_dos_unidades(self) -> None:
        unidades = {mazo["unidad"] for mazo in MAZOS}
        assert unidades == {"Lógica", "Conjuntos"}

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
