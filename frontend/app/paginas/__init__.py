"""Páginas de la aplicación.

Importar este paquete registra todas las rutas con `@ui.page`; por eso los
imports parecen sin usar (`F401`) y por eso no se pueden borrar.
"""

from app.paginas import estudiar, herramientas, inicio, login, nueva

__all__ = ["estudiar", "herramientas", "inicio", "login", "nueva"]
