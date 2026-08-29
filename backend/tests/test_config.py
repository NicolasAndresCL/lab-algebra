"""Pruebas de la configuración leída del entorno.

Este archivo existe por un fallo real: `ORIGENES_PERMITIDOS` estaba declarado
como `list[str]`, y pydantic-settings intenta interpretar como JSON el valor de
un campo de tipo complejo **antes** de llamar a ningún validador. La aplicación
arrancaba perfectamente en los tests —que usan el valor por defecto— y moría
con `SettingsError` en cuanto Compose le pasaba la variable de verdad.

La lección: los ajustes hay que probarlos **pasando por el entorno**, que es
como llegan en producción, no solo por sus defaults.
"""

from __future__ import annotations

import pytest

from app.config import Ajustes

BASE = {
    "SECRET_KEY": "clave-de-pruebas-suficientemente-larga-0123456789",
    "DATABASE_URL": "sqlite+pysqlite:///:memory:",
}


def _ajustes(monkeypatch: pytest.MonkeyPatch, **entorno: str) -> Ajustes:
    for clave, valor in {**BASE, **entorno}.items():
        monkeypatch.setenv(clave, valor)
    # `_env_file=None` evita que un `.env` presente en la máquina de quien
    # ejecuta la suite contamine el resultado.
    return Ajustes(_env_file=None)  # type: ignore[call-arg]


class TestOrigenesPermitidos:
    def test_una_lista_separada_por_comas_se_parsea(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        ajustes = _ajustes(
            monkeypatch,
            ORIGENES_PERMITIDOS="http://localhost:8080,http://127.0.0.1:8080",
        )
        assert ajustes.origenes == ["http://localhost:8080", "http://127.0.0.1:8080"]

    def test_se_ignoran_los_espacios_sobrantes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        ajustes = _ajustes(monkeypatch, ORIGENES_PERMITIDOS=" http://a , http://b ,, ")
        assert ajustes.origenes == ["http://a", "http://b"]

    def test_un_solo_origen_tambien_vale(self, monkeypatch: pytest.MonkeyPatch) -> None:
        ajustes = _ajustes(monkeypatch, ORIGENES_PERMITIDOS="http://solo-uno:8080")
        assert ajustes.origenes == ["http://solo-uno:8080"]

    def test_el_valor_por_defecto_apunta_al_frontend(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ORIGENES_PERMITIDOS", raising=False)
        assert "http://localhost:8080" in _ajustes(monkeypatch).origenes


class TestClaves:
    def test_una_secret_key_corta_se_rechaza(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """32 caracteres es el mínimo de la RFC 7518 §3.2 para HS256."""
        with pytest.raises(ValueError, match="secret_key"):
            _ajustes(monkeypatch, SECRET_KEY="corta")

    def test_la_url_de_la_base_se_toma_del_entorno(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        url = "postgresql+psycopg://u:p@lab-algebra-db:5432/algebra"
        assert _ajustes(monkeypatch, DATABASE_URL=url).database_url == url


class TestEntorno:
    def test_por_defecto_no_es_produccion(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ENTORNO", raising=False)
        assert _ajustes(monkeypatch).es_produccion is False

    def test_prod_se_reconoce(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert _ajustes(monkeypatch, ENTORNO="prod").es_produccion is True

    def test_un_entorno_desconocido_se_rechaza(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with pytest.raises(ValueError, match="entorno"):
            _ajustes(monkeypatch, ENTORNO="produccion-de-verdad")
