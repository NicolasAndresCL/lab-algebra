"""Render de una tarjeta.

Vive aparte porque lo usan dos pantallas con necesidades distintas: el listado
del mazo (todo desplegado, para consultar) y la sesión de estudio (anverso
primero, reverso solo al girarla). Duplicar este render en ambas garantizaría
que se desincronicen a la primera corrección.
"""

from __future__ import annotations

from nicegui import ui

from app.api import ErrorApi, Sesion
from app.api import tabla_de_verdad as pedir_tabla
from app.componentes import diagrama_venn, parrafo_multilinea, tabla_de_verdad


def anverso(tarjeta: dict) -> None:
    """Lo que se ve antes de girar la tarjeta: el concepto y la pregunta."""
    with ui.column().classes("w-full items-center gap-2 py-6"):
        ui.label(tarjeta["concepto"]).classes("text-2xl font-bold text-center")
        ui.label(tarjeta["pregunta"]).classes(
            "text-lg text-center text-gray-600 dark:text-gray-300"
        )


def reverso(sesion: Sesion, tarjeta: dict) -> None:
    """La definición, la clave de memoria y el ejercicio resuelto."""
    with ui.column().classes("w-full gap-3"):
        parrafo_multilinea(tarjeta["definicion"])

        if tarjeta.get("notacion"):
            ui.label(f"Notación: {tarjeta['notacion']}").classes(
                "font-mono text-sm bg-gray-100 dark:bg-gray-800 p-2 rounded w-full"
            )

        if tarjeta.get("clave_memoria"):
            with ui.row().classes("items-start gap-2 w-full"):
                ui.icon("lightbulb", size="18px").classes("text-amber-500 mt-1")
                with ui.column().classes("gap-0 flex-1"):
                    parrafo_multilinea(tarjeta["clave_memoria"], "text-sm")

        ui.separator()
        ui.label("Ejercicio resuelto").classes("font-semibold text-primary")
        parrafo_multilinea(tarjeta["ejercicio_enunciado"], "text-sm")

        with ui.card().classes("w-full bg-gray-50 dark:bg-gray-800 p-3 gap-0"):
            ui.label("Desarrollo").classes("text-xs uppercase text-gray-500 mb-1")
            parrafo_multilinea(tarjeta["ejercicio_desarrollo"], "text-sm font-mono")

        with ui.row().classes("items-start gap-2 w-full"):
            ui.icon("check_circle", size="20px").classes("text-positive mt-1")
            with ui.column().classes("gap-0 flex-1"):
                parrafo_multilinea(tarjeta["ejercicio_respuesta"], "font-medium")

        if tarjeta.get("formula"):
            ui.separator()
            ui.label(f"Tabla de verdad de {tarjeta['formula']}").classes(
                "text-sm font-semibold"
            )
            _tabla(sesion, tarjeta["formula"])

        if tarjeta.get("venn"):
            ui.separator()
            ui.label("Diagrama de Venn").classes("text-sm font-semibold")
            diagrama_venn(sesion, tarjeta["venn"])

        if tarjeta.get("fuente"):
            ui.label(f"Fuente: {tarjeta['fuente']}").classes("text-xs text-gray-400 mt-2")


def _tabla(sesion: Sesion, formula: str) -> None:
    try:
        tabla_de_verdad(pedir_tabla(sesion, formula))
    except ErrorApi as error:
        ui.label(f"No se pudo calcular la tabla: {error}").classes("text-negative text-sm")


def panel_tarjeta(sesion: Sesion, tarjeta: dict) -> None:
    """Tarjeta completa (anverso + reverso), para consulta."""
    with ui.column().classes("w-full gap-2 p-2"):
        if not tarjeta.get("es_semilla", True):
            ui.badge("propia").props("color=accent")
        ui.label(tarjeta["pregunta"]).classes("italic text-gray-500")
        reverso(sesion, tarjeta)
