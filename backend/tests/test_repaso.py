"""Pruebas de la repetición espaciada y del flujo de estudio."""

from __future__ import annotations

import pathlib
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.services import repaso


class TestAlgoritmo:
    def test_el_primer_acierto_programa_para_manana(self) -> None:
        hoy = date(2026, 3, 1)
        estado = repaso.calcular(5, repeticiones=0, factor_facilidad=2.5, intervalo_dias=0, hoy=hoy)
        assert estado.repeticiones == 1
        assert estado.intervalo_dias == 1
        assert estado.proxima_revision == hoy + timedelta(days=1)

    def test_el_segundo_acierto_programa_a_tres_dias(self) -> None:
        hoy = date(2026, 3, 1)
        estado = repaso.calcular(4, repeticiones=1, factor_facilidad=2.5, intervalo_dias=1, hoy=hoy)
        assert estado.repeticiones == 2
        assert estado.intervalo_dias == 3

    def test_a_partir_del_tercero_el_intervalo_se_multiplica(self) -> None:
        estado = repaso.calcular(5, repeticiones=2, factor_facilidad=2.5, intervalo_dias=3)
        assert estado.intervalo_dias == round(3 * 2.5)

    @pytest.mark.parametrize("calidad", [0, 1, 2])
    def test_un_fallo_reinicia_la_serie_y_la_deja_para_hoy(self, calidad: int) -> None:
        """Si no reiniciara, una tarjeta fallada volvería semanas después."""
        hoy = date(2026, 3, 1)
        estado = repaso.calcular(
            calidad, repeticiones=6, factor_facilidad=2.6, intervalo_dias=40, hoy=hoy
        )
        assert estado.repeticiones == 0
        assert estado.intervalo_dias == 0
        assert estado.proxima_revision == hoy

    def test_el_factor_de_facilidad_nunca_baja_de_1_3(self) -> None:
        factor = 2.5
        for _ in range(20):
            factor = repaso.calcular(0, 0, factor, 0).factor_facilidad
        assert factor == pytest.approx(repaso.FACTOR_MINIMO)

    def test_una_calidad_fuera_de_rango_es_un_error(self) -> None:
        with pytest.raises(ValueError, match="entre 0 y 5"):
            repaso.calcular(9, 0, 2.5, 0)

    def test_el_estado_inicial_toca_hoy(self) -> None:
        hoy = date(2026, 3, 1)
        assert repaso.estado_inicial(hoy).proxima_revision == hoy


class TestFuenteDeFecha:
    """Regresión de un bug que solo aparecía a ciertas horas del día.

    `calcular` programaba con `date.today()` (fecha LOCAL del servidor) y la
    consulta de la cola filtraba con `datetime.now(UTC).date()`. En cualquier
    huso al oeste de Greenwich las dos difieren durante las últimas horas del
    día, así que una tarjeta acertada volvía a la cola en el acto — justo por
    la noche, que es cuando se estudia.
    """

    def test_un_acierto_se_programa_estrictamente_despues_de_hoy(self) -> None:
        estado = repaso.calcular(5, repeticiones=0, factor_facilidad=2.5, intervalo_dias=0)
        assert estado.proxima_revision > repaso.hoy_utc()

    def test_el_estado_inicial_toca_exactamente_hoy(self) -> None:
        assert repaso.estado_inicial().proxima_revision == repaso.hoy_utc()

    def test_ningun_modulo_usa_la_fecha_local(self) -> None:
        """`date.today()` depende del huso del servidor; aquí no se usa.

        Es el test que impide que alguien vuelva a mezclar las dos fuentes: el
        fallo original no lo delataba ninguna prueba salvo por la hora a la que
        se ejecutara la suite.
        """
        raiz = pathlib.Path(__file__).resolve().parent.parent / "app"
        culpables = [
            f"{ruta.relative_to(raiz)}:{numero}"
            for ruta in raiz.rglob("*.py")
            for numero, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1)
            if "date.today()" in linea and not linea.lstrip().startswith(("#", "*"))
            and "`date.today()`" not in linea
        ]
        assert not culpables, f"usan la fecha local en vez de repaso.hoy_utc(): {culpables}"


class TestFlujoDeEstudio:
    def test_la_cola_incluye_tarjetas_nunca_vistas(self, autenticado: TestClient) -> None:
        """Un usuario nuevo no tiene filas en `repasos`: el LEFT JOIN es clave."""
        cola = autenticado.get("/api/v1/estudio/cola", params={"limite": 5}).json()
        assert len(cola) == 5

    def test_calificar_crea_el_registro_y_lo_programa(self, autenticado: TestClient) -> None:
        tarjeta = autenticado.get("/api/v1/estudio/cola", params={"limite": 1}).json()[0]
        respuesta = autenticado.post(
            f"/api/v1/estudio/tarjetas/{tarjeta['id']}/calificar", json={"calidad": 5}
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["repeticiones"] == 1
        assert cuerpo["aciertos"] == 1
        assert cuerpo["proxima_revision"] > str(date.today())

    def test_una_tarjeta_acertada_sale_de_la_cola_de_hoy(
        self, autenticado: TestClient
    ) -> None:
        tarjeta = autenticado.get(
            "/api/v1/estudio/cola", params={"limite": 1}
        ).json()[0]
        autenticado.post(
            f"/api/v1/estudio/tarjetas/{tarjeta['id']}/calificar", json={"calidad": 5}
        )
        cola = autenticado.get("/api/v1/estudio/cola", params={"limite": 100}).json()
        assert tarjeta["id"] not in [t["id"] for t in cola]

    def test_una_tarjeta_fallada_sigue_en_la_cola(self, autenticado: TestClient) -> None:
        tarjeta = autenticado.get("/api/v1/estudio/cola", params={"limite": 1}).json()[0]
        autenticado.post(
            f"/api/v1/estudio/tarjetas/{tarjeta['id']}/calificar", json={"calidad": 1}
        )
        cola = autenticado.get("/api/v1/estudio/cola", params={"limite": 100}).json()
        assert tarjeta["id"] in [t["id"] for t in cola]

    def test_calificar_una_tarjeta_inexistente_da_404(self, autenticado: TestClient) -> None:
        respuesta = autenticado.post(
            "/api/v1/estudio/tarjetas/99999/calificar", json={"calidad": 3}
        )
        assert respuesta.status_code == 404

    def test_una_calidad_fuera_de_rango_da_422(self, autenticado: TestClient) -> None:
        tarjeta = autenticado.get("/api/v1/estudio/cola", params={"limite": 1}).json()[0]
        respuesta = autenticado.post(
            f"/api/v1/estudio/tarjetas/{tarjeta['id']}/calificar", json={"calidad": 42}
        )
        assert respuesta.status_code == 422

    def test_el_progreso_cuadra_con_lo_calificado(self, autenticado: TestClient) -> None:
        tarjeta = autenticado.get("/api/v1/estudio/cola", params={"limite": 1}).json()[0]
        autenticado.post(
            f"/api/v1/estudio/tarjetas/{tarjeta['id']}/calificar", json={"calidad": 4}
        )
        progreso = autenticado.get("/api/v1/estudio/progreso").json()
        assert progreso["total_tarjetas"] > 0
        assert progreso["estudiadas"] >= 1
        assert 0 <= progreso["porcentaje_acierto"] <= 100
