"""Pruebas de hash de contraseñas y tokens."""

from __future__ import annotations

import pytest

from app.excepciones import NoAutenticadoError
from app.seguridad import crear_token, hashear_password, leer_token, verificar_password


class TestPasswords:
    def test_el_hash_no_contiene_la_password(self) -> None:
        assert "1234" not in hashear_password("1234")

    def test_verifica_la_password_correcta(self) -> None:
        assert verificar_password("1234", hashear_password("1234"))

    def test_rechaza_la_password_incorrecta(self) -> None:
        assert not verificar_password("4321", hashear_password("1234"))

    def test_dos_hashes_de_la_misma_password_difieren(self) -> None:
        """La sal aleatoria evita que dos usuarios con la misma clave se delaten."""
        assert hashear_password("1234") != hashear_password("1234")

    def test_un_hash_corrupto_no_revienta(self) -> None:
        assert not verificar_password("1234", "esto-no-es-un-hash")

    def test_una_password_larguisima_no_revienta(self) -> None:
        """bcrypt trunca a 72 bytes; el recorte es explícito, no un fallo opaco."""
        larga = "á" * 200
        assert verificar_password(larga, hashear_password(larga))


class TestTokens:
    def test_el_token_devuelve_el_usuario(self) -> None:
        assert leer_token(crear_token("nico")) == "nico"

    def test_un_token_manipulado_se_rechaza(self) -> None:
        token = crear_token("nico")
        with pytest.raises(NoAutenticadoError):
            leer_token(token[:-3] + "aaa")

    def test_un_token_expirado_se_rechaza(self) -> None:
        with pytest.raises(NoAutenticadoError, match="expiró"):
            leer_token(crear_token("nico", minutos=-1))

    def test_una_cadena_cualquiera_no_es_un_token(self) -> None:
        with pytest.raises(NoAutenticadoError):
            leer_token("no-es-un-token")
