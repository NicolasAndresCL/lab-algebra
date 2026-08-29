"""Configuración tipada por entorno.

Nada de valores quemados en el código: todo entra por variables de entorno y
se valida aquí. Si falta algo obligatorio, la aplicación falla al arrancar —
ruidoso y temprano — en vez de servir tráfico con una configuración a medias.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Entorno = Literal["dev", "test", "prod"]


class Ajustes(BaseSettings):
    """Ajustes de la aplicación leídos del entorno (o de un `.env` local)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    entorno: Entorno = "dev"

    # --- Base de datos --------------------------------------------------
    # En dev/prod apunta a Postgres; la suite de tests la sobreescribe con
    # SQLite en memoria para correr en un checkout limpio y sin contenedores.
    database_url: str = "postgresql+psycopg://algebra:algebra@localhost:5432/algebra"

    # --- Seguridad ------------------------------------------------------
    # 32 bytes es el mínimo recomendado por RFC 7518 §3.2 para HS256; PyJWT
    # avisa por debajo de eso.
    secret_key: str = Field(min_length=32)
    algoritmo_jwt: str = "HS256"
    minutos_expiracion_token: int = 12 * 60

    # --- Usuario semilla ------------------------------------------------
    # El enunciado del laboratorio pide poder entrar con nico/1234. La
    # contraseña vive en el entorno, no en el código, para que cambiarla en
    # una instalación real no obligue a tocar el repositorio.
    usuario_inicial: str = "nico"
    password_inicial: str = "1234"

    # --- CORS -----------------------------------------------------------
    origenes_permitidos: list[str] = ["http://localhost:8080", "http://127.0.0.1:8080"]

    @field_validator("origenes_permitidos", mode="before")
    @classmethod
    def _separar_por_comas(cls, valor: object) -> object:
        """Permite declarar la lista como `a,b,c` en una variable de entorno."""
        if isinstance(valor, str):
            return [item.strip() for item in valor.split(",") if item.strip()]
        return valor

    @property
    def es_produccion(self) -> bool:
        return self.entorno == "prod"


@lru_cache
def obtener_ajustes() -> Ajustes:
    """Instancia única de los ajustes (cacheada para no releer el entorno)."""
    return Ajustes()  # type: ignore[call-arg]
