"""Inicio de sesión y perfil del usuario autenticado."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.config import obtener_ajustes
from app.dependencias import SesionDep, UsuarioDep
from app.esquemas import CredencialesEntrada, TokenSalida, UsuarioSalida
from app.excepciones import CredencialesInvalidasError
from app.modelos import Usuario
from app.seguridad import crear_token, verificar_password

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/login", response_model=TokenSalida, summary="Iniciar sesión")
def login(datos: CredencialesEntrada, sesion: SesionDep) -> TokenSalida:
    """Valida las credenciales y devuelve un JWT.

    El mismo mensaje de error para «usuario inexistente» y «contraseña
    incorrecta»: distinguirlos permitiría enumerar qué usuarios existen.
    """
    usuario = sesion.scalar(select(Usuario).where(Usuario.username == datos.username.strip()))
    if usuario is None or not verificar_password(datos.password, usuario.hash_password):
        raise CredencialesInvalidasError
    if not usuario.activo:
        raise CredencialesInvalidasError("La cuenta está desactivada.")

    ajustes = obtener_ajustes()
    return TokenSalida(
        access_token=crear_token(usuario.username),
        expira_en_minutos=ajustes.minutos_expiracion_token,
        usuario=UsuarioSalida.model_validate(usuario),
    )


@router.get("/yo", response_model=UsuarioSalida, summary="Usuario de la sesión actual")
def yo(usuario: UsuarioDep) -> UsuarioSalida:
    return UsuarioSalida.model_validate(usuario)
