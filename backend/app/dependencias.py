"""Dependencias compartidas por los routers."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import obtener_sesion
from app.excepciones import NoAutenticadoError
from app.modelos import Usuario
from app.seguridad import leer_token

# `auto_error=False`: si falta la cabecera queremos lanzar NUESTRO error de
# dominio (con su código estable), no el 403 genérico de Starlette.
esquema_bearer = HTTPBearer(auto_error=False)

SesionDep = Annotated[Session, Depends(obtener_sesion)]


def usuario_actual(
    sesion: SesionDep,
    credenciales: Annotated[
        HTTPAuthorizationCredentials | None, Depends(esquema_bearer)
    ] = None,
) -> Usuario:
    """Resuelve el usuario autenticado a partir del token `Bearer`."""
    if credenciales is None or not credenciales.credentials:
        raise NoAutenticadoError("Falta la cabecera Authorization.")

    username = leer_token(credenciales.credentials)
    usuario = sesion.scalar(select(Usuario).where(Usuario.username == username))
    if usuario is None or not usuario.activo:
        raise NoAutenticadoError("El usuario del token ya no existe o está inactivo.")
    return usuario


UsuarioDep = Annotated[Usuario, Depends(usuario_actual)]
