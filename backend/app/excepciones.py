"""Excepciones de dominio.

Las reglas de negocio **lanzan**; no arman una respuesta HTTP a mano. Un único
manejador (`app.manejadores`) traduce estas excepciones al contrato de error de
la API. Así los servicios se prueban con `pytest.raises(...)` sin levantar HTTP,
y el frontend consume siempre la misma forma de error.
"""

from __future__ import annotations

from http import HTTPStatus


class ErrorLabAlgebra(Exception):
    """Raíz de los errores de negocio.

    Cualquier excepción que NO herede de esta clase es un bug: debe salir como
    500 y quedar registrada con traza completa, nunca tragarse en silencio.
    """

    codigo: str = "error_lab_algebra"
    http_status: int = HTTPStatus.BAD_REQUEST
    mensaje: str = "No se pudo completar la operación."

    def __init__(self, mensaje: str | None = None) -> None:
        self.mensaje = mensaje or self.mensaje
        super().__init__(self.mensaje)

    def detalle(self) -> dict:
        """Datos extra para el cliente. Las subclases lo enriquecen."""
        return {}


class CredencialesInvalidasError(ErrorLabAlgebra):
    codigo = "credenciales_invalidas"
    http_status = HTTPStatus.UNAUTHORIZED
    mensaje = "Usuario o contraseña incorrectos."


class NoAutenticadoError(ErrorLabAlgebra):
    codigo = "no_autenticado"
    http_status = HTTPStatus.UNAUTHORIZED
    mensaje = "Se requiere iniciar sesión."


class RecursoNoEncontradoError(ErrorLabAlgebra):
    codigo = "recurso_no_encontrado"
    http_status = HTTPStatus.NOT_FOUND
    mensaje = "El recurso solicitado no existe."

    def __init__(self, recurso: str = "recurso", identificador: object = None) -> None:
        self.recurso = recurso
        self.identificador = identificador
        super().__init__(f"No existe {recurso} con identificador {identificador!r}.")

    def detalle(self) -> dict:
        return {"recurso": self.recurso, "id": self.identificador}


class RecursoDuplicadoError(ErrorLabAlgebra):
    """409, no 400: la petición está bien formada; choca con el estado actual."""

    codigo = "recurso_duplicado"
    http_status = HTTPStatus.CONFLICT
    mensaje = "Ya existe un recurso con esos datos."


class FormulaInvalidaError(ErrorLabAlgebra):
    """La fórmula proposicional no se pudo analizar.

    Lleva la posición del carácter conflictivo: sin ella, el usuario recibe un
    "fórmula inválida" que no le dice dónde mirar.
    """

    codigo = "formula_invalida"
    http_status = HTTPStatus.UNPROCESSABLE_ENTITY
    mensaje = "La fórmula proposicional no es válida."

    def __init__(self, mensaje: str, posicion: int | None = None) -> None:
        self.posicion = posicion
        super().__init__(mensaje)

    def detalle(self) -> dict:
        return {"posicion": self.posicion}


class DatosVennInvalidosError(ErrorLabAlgebra):
    codigo = "datos_venn_invalidos"
    http_status = HTTPStatus.UNPROCESSABLE_ENTITY
    mensaje = "Los datos del diagrama de Venn no son consistentes."
