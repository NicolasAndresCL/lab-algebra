"""Configuración tipada por entorno.

Nada de valores quemados en el código: todo entra por variables de entorno y
se valida aquí. Si falta algo obligatorio, la aplicación falla al arrancar —
ruidoso y temprano — en vez de servir tráfico con una configuración a medias.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
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
    # Se declara como cadena separada por comas, NO como `list[str]`: para un
    # campo de tipo complejo, pydantic-settings intenta interpretar la variable
    # de entorno como JSON *antes* de llamar a ningún validador, y
    # `ORIGENES_PERMITIDOS=http://a,http://b` revienta al arrancar con un
    # SettingsError. Es un fallo que los tests no ven, porque usan el valor por
    # defecto y nunca pasan por el entorno.
    origenes_permitidos: str = "http://localhost:8080,http://127.0.0.1:8080"

    @property
    def origenes(self) -> list[str]:
        """Los orígenes permitidos, ya separados y sin espacios sobrantes."""
        return [item.strip() for item in self.origenes_permitidos.split(",") if item.strip()]

    @property
    def es_produccion(self) -> bool:
        return self.entorno == "prod"


@lru_cache
def obtener_ajustes() -> Ajustes:
    """Instancia única de los ajustes (cacheada para no releer el entorno)."""
    return Ajustes()  # type: ignore[call-arg]
