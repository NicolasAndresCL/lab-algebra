"""Pruebas de la generación de diagramas.

El contenido matemático del diagrama ya se comprueba en `test_contenido.py`;
aquí se verifica lo que depende del **tema de quien lo mira**, que es la parte
que se añadió al soportar cuatro paletas.
"""

from __future__ import annotations

import struct
import zlib

import pytest
from fastapi.testclient import TestClient

from app.services import venn

ESPECIFICACION = {
    "etiquetas": ["A", "B"],
    "cardinalidades": {"a": 10, "b": 8, "ab": 4},
    "universo": 20,
}


def color_de_fondo(png: bytes) -> tuple[int, int, int]:
    """Color del píxel de la esquina superior izquierda del PNG.

    Se decodifica a mano en vez de instalar Pillow solo para esto: el formato
    de un PNG sin entrelazar es lo bastante simple y evita una dependencia más
    en la imagen de producción.
    """
    assert png.startswith(b"\x89PNG\r\n\x1a\n"), "no es un PNG"
    posicion = 8
    ancho = alto = 0
    datos = b""
    while posicion < len(png):
        (longitud,) = struct.unpack(">I", png[posicion : posicion + 4])
        tipo = png[posicion + 4 : posicion + 8]
        cuerpo = png[posicion + 8 : posicion + 8 + longitud]
        if tipo == b"IHDR":
            ancho, alto, profundidad, color, *_ = struct.unpack(">IIBBBBB", cuerpo)
            assert profundidad == 8 and color in (2, 6), "se esperaba RGB(A) de 8 bits"
            canales = 3 if color == 2 else 4  # RGB o RGBA
        elif tipo == b"IDAT":
            datos += cuerpo
        elif tipo == b"IEND":
            break
        posicion += 12 + longitud

    crudo = zlib.decompress(datos)
    # Cada fila empieza con un byte de filtro; la primera sale sin filtrar, así
    # que basta con saltarlo. Los tres primeros canales son RGB tanto si la
    # imagen lleva alfa como si no.
    assert len(crudo) >= 1 + canales * ancho * alto
    return tuple(crudo[1:4])


def a_rgb(hexadecimal: str) -> tuple[int, int, int]:
    return tuple(int(hexadecimal[i : i + 2], 16) for i in (1, 3, 5))


class TestPaleta:
    def test_sin_colores_el_fondo_es_blanco(self) -> None:
        """El valor por defecto sirve a un cliente que no tenga temas."""
        png = venn.generar_png(ESPECIFICACION)
        assert color_de_fondo(png) == a_rgb(venn.FONDO_POR_DEFECTO)

    @pytest.mark.parametrize(
        "fondo", ["#000000", "#0a1120", "#14120f"], ids=["onix", "medianoche", "carbon"]
    )
    def test_el_fondo_del_tema_llega_a_la_imagen(self, fondo: str) -> None:
        png = venn.generar_png({**ESPECIFICACION, "fondo": fondo, "tinta": "#f4f4f5"})
        assert color_de_fondo(png) == a_rgb(fondo)

    def test_dos_temas_producen_imagenes_distintas(self) -> None:
        claro = venn.generar_png({**ESPECIFICACION, "fondo": "#ffffff", "tinta": "#111827"})
        oscuro = venn.generar_png({**ESPECIFICACION, "fondo": "#000000", "tinta": "#f4f4f5"})
        assert claro != oscuro

    def test_tambien_se_aplica_con_tres_conjuntos(self) -> None:
        png = venn.generar_png(
            {
                "etiquetas": ["A", "B", "C"],
                "cardinalidades": {"a": 9, "b": 8, "c": 7, "ab": 4, "ac": 3, "bc": 2, "abc": 1},
                "universo": 30,
                "fondo": "#14120f",
                "tinta": "#f5f0e8",
            }
        )
        assert color_de_fondo(png) == a_rgb("#14120f")

    def test_una_paleta_incompleta_cae_en_los_valores_por_defecto(self) -> None:
        paleta = venn.Paleta.desde_dict({"fondo": None, "tinta": ""})
        assert paleta.fondo == venn.FONDO_POR_DEFECTO
        assert paleta.tinta == venn.TINTA_POR_DEFECTO


class TestCache:
    def test_el_tema_forma_parte_de_la_clave(self) -> None:
        """Sin esto, el segundo tema recibiría la imagen cacheada del primero."""
        claro = venn.generar_png_cacheado(
            {**ESPECIFICACION, "fondo": "#ffffff", "tinta": "#111827"}
        )
        oscuro = venn.generar_png_cacheado(
            {**ESPECIFICACION, "fondo": "#000000", "tinta": "#f4f4f5"}
        )
        assert color_de_fondo(claro) != color_de_fondo(oscuro)

    def test_la_misma_peticion_devuelve_los_mismos_bytes(self) -> None:
        peticion = {**ESPECIFICACION, "fondo": "#0a1120", "tinta": "#e6edf8"}
        assert venn.generar_png_cacheado(peticion) is venn.generar_png_cacheado(peticion)


class TestEndpoint:
    def test_la_api_acepta_los_colores_del_tema(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/venn/imagen",
            json={**ESPECIFICACION, "fondo": "#000000", "tinta": "#f4f4f5"},
        )
        assert respuesta.status_code == 200
        assert color_de_fondo(respuesta.content) == (0, 0, 0)

    @pytest.mark.parametrize("valor", ["negro", "#fff", "rgb(0,0,0)", "#12345g"])
    def test_un_color_mal_formado_se_rechaza(
        self, autenticado: TestClient, valor: str
    ) -> None:
        """El color entra en una imagen: se valida el formato, no se confía."""
        respuesta = autenticado.post(
            "/api/v1/herramientas/venn/imagen", json={**ESPECIFICACION, "fondo": valor}
        )
        assert respuesta.status_code == 422
        assert respuesta.json()["error"]["codigo"] == "datos_invalidos"

    def test_sin_colores_sigue_funcionando(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/herramientas/venn/imagen", json=ESPECIFICACION
        )
        assert respuesta.status_code == 200
        assert color_de_fondo(respuesta.content) == (255, 255, 255)
