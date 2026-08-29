"""Configuración del frontend, leída del entorno."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Ajustes(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Dentro de la red de Compose el backend se resuelve por su nombre de
    # servicio; en local, por localhost.
    api_url: str = "http://localhost:8000"
    puerto: int = 8080
    # Firma las cookies de `app.storage.user`. Sin ella NiceGUI no puede
    # mantener la sesión entre recargas.
    storage_secret: str = Field(min_length=16)
    titulo: str = "lab-algebra — Tarjetas de Álgebra"
    timeout_segundos: float = 20.0

    @property
    def base_api(self) -> str:
        return f"{self.api_url.rstrip('/')}/api/v1"


@lru_cache
def obtener_ajustes() -> Ajustes:
    return Ajustes()  # type: ignore[call-arg]
