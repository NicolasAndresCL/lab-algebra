"""Pruebas de las paletas.

Un tema mal definido no rompe nada: la página carga igual y el fallo es que un
texto queda ilegible sobre su fondo. Eso no lo caza un linter y cuesta verlo a
ojo si solo se revisa la pantalla en la que uno estaba trabajando, así que se
comprueba aquí: **contraste real, tema por tema**.
"""

from __future__ import annotations

import re

import pytest

from app.temas import CSS_BASE, TEMA_POR_DEFECTO, TEMAS, Tema

COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")

CAMPOS_DE_COLOR = [
    campo
    for campo in Tema.__dataclass_fields__
    if campo.startswith(("q_", "lab_"))
]


def _canal(valor: float) -> float:
    """Linealiza un canal sRGB (fórmula de la WCAG 2.1)."""
    return valor / 12.92 if valor <= 0.03928 else ((valor + 0.055) / 1.055) ** 2.4


def luminancia(color: str) -> float:
    r, g, b = (int(color[i : i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * _canal(r) + 0.7152 * _canal(g) + 0.0722 * _canal(b)


def contraste(uno: str, otro: str) -> float:
    """Razón de contraste WCAG entre dos colores (de 1 a 21)."""
    a, b = sorted((luminancia(uno), luminancia(otro)), reverse=True)
    return (a + 0.05) / (b + 0.05)


class TestCatalogo:
    def test_hay_al_menos_tres_paletas_oscuras(self) -> None:
        oscuras = [t for t in TEMAS.values() if t.oscuro]
        assert len(oscuras) >= 3, "el laboratorio se pidió con tres variantes oscuras"

    def test_hay_una_alternativa_clara(self) -> None:
        assert any(not t.oscuro for t in TEMAS.values())

    def test_el_tema_por_defecto_esta_en_el_catalogo(self) -> None:
        assert TEMAS[TEMA_POR_DEFECTO.clave] is TEMA_POR_DEFECTO

    def test_las_claves_y_los_nombres_no_se_repiten(self) -> None:
        assert len({t.clave for t in TEMAS.values()}) == len(TEMAS)
        assert len({t.nombre for t in TEMAS.values()}) == len(TEMAS)

    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_todos_los_colores_son_hex_de_seis_digitos(self, tema: Tema) -> None:
        """El backend valida los colores del Venn con este mismo patrón."""
        for campo in CAMPOS_DE_COLOR:
            valor = getattr(tema, campo)
            assert COLOR.match(valor), f"{tema.clave}.{campo} = {valor!r}"

    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_cada_tema_tiene_descripcion_util(self, tema: Tema) -> None:
        """La descripción es lo que distingue «Ónix» de «Carbón» en el menú."""
        assert len(tema.descripcion) > 20


class TestContraste:
    """Umbrales de la WCAG 2.1: 4.5 para texto normal, 3.0 para texto grande."""

    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_el_texto_principal_se_lee_sobre_el_fondo(self, tema: Tema) -> None:
        assert contraste(tema.lab_texto, tema.lab_fondo) >= 4.5

    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_el_texto_principal_se_lee_sobre_las_superficies(self, tema: Tema) -> None:
        for superficie in (tema.lab_superficie, tema.lab_superficie_alta):
            assert contraste(tema.lab_texto, superficie) >= 4.5

    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_el_texto_tenue_sigue_siendo_legible(self, tema: Tema) -> None:
        """Tenue no es lo mismo que invisible: es texto secundario, no adorno."""
        assert contraste(tema.lab_texto_tenue, tema.lab_superficie) >= 4.5

    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_el_color_primario_destaca_sobre_la_superficie(self, tema: Tema) -> None:
        """El primario rotula botones y enlaces; 3.0 es el mínimo para texto grande.

        Este es el test que habría cazado de inmediato la cabecera azul del tema
        claro, donde los botones quedaban del mismo color que su fondo.
        """
        assert contraste(tema.q_primary, tema.lab_superficie) >= 3.0

    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_los_botones_de_la_cabecera_no_desaparecen(self, tema: Tema) -> None:
        assert contraste(tema.q_primary, tema.lab_cabecera) >= 3.0

    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_los_colores_de_estado_se_distinguen(self, tema: Tema) -> None:
        """Positivo, negativo y aviso rotulan la clasificación de una fórmula."""
        for estado in (tema.q_positive, tema.q_negative, tema.q_warning):
            assert contraste(estado, tema.lab_superficie) >= 3.0

    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_el_diagrama_de_venn_se_lee(self, tema: Tema) -> None:
        """Los rótulos del PNG los dibuja el backend con estos dos colores."""
        assert contraste(tema.lab_venn_texto, tema.lab_venn_fondo) >= 4.5

    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_el_borde_se_distingue_de_la_superficie(self, tema: Tema) -> None:
        """Un borde invisible convierte las tarjetas en un bloque continuo."""
        assert contraste(tema.lab_borde, tema.lab_superficie) >= 1.15


class TestVariablesCss:
    @pytest.mark.parametrize("tema", TEMAS.values(), ids=[t.clave for t in TEMAS.values()])
    def test_declara_una_variable_por_cada_campo_de_color(self, tema: Tema) -> None:
        declaradas = {
            par.split(":")[0].strip() for par in tema.variables_css().split(";")
        }
        # `lab_venn_*` no viaja como variable CSS: lo consume el backend.
        esperadas = {
            "--" + campo.replace("_", "-", 1).replace("_", "-")
            for campo in CAMPOS_DE_COLOR
            if not campo.startswith("lab_venn")
        }
        assert esperadas <= declaradas

    def test_el_css_base_no_usa_ninguna_variable_sin_declarar(self) -> None:
        """Si se añade una variable a la hoja y se olvida en el tema, falla aquí.

        Sin este test, la propiedad simplemente no resuelve y el elemento se
        queda transparente o negro, sin ningún aviso.
        """
        usadas = set(re.findall(r"var\((--lab-[a-z-]+)\)", CSS_BASE))
        declaradas = {
            par.split(":")[0].strip()
            for par in TEMA_POR_DEFECTO.variables_css().split(";")
        }
        assert usadas <= declaradas, f"sin declarar: {sorted(usadas - declaradas)}"

    def test_el_css_base_no_lleva_colores_literales(self) -> None:
        """Todo el color vive en los temas; la hoja solo los consume.

        Se admite el gris del borde de la muestra, que es neutro a propósito
        para verse en las cuatro paletas.
        """
        literales = re.findall(r"#[0-9a-fA-F]{3,8}\b", CSS_BASE)
        assert not literales, f"colores literales en CSS_BASE: {literales}"

    def test_la_muestra_del_selector_usa_tres_colores_distintos(self) -> None:
        for tema in TEMAS.values():
            assert len(set(tema.muestra)) == 3, tema.clave
