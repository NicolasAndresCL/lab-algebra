"""Componentes de interfaz reutilizados por varias páginas."""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from app.api import ErrorApi, Sesion, imagen_venn
from app.estado import cerrar_sesion, sesion_actual

# Símbolos que el teclado no trae. Se ofrecen como botones para que escribir
# una fórmula no obligue a buscar caracteres en el mapa de caracteres.
SIMBOLOS = ["¬", "∧", "∨", "⊻", "→", "↔", "(", ")"]

COLOR_CLASIFICACION = {
    "tautología": "positive",
    "contradicción": "negative",
    "contingencia": "warning",
}


def cabecera(titulo: str, activo: str = "") -> None:
    """Barra superior con la navegación principal."""
    sesion = sesion_actual()
    with ui.header().classes("items-center justify-between px-4 py-2 bg-primary"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("school", size="28px").classes("text-white")
            ui.label("lab-algebra").classes("text-white text-lg font-bold")
            ui.label(titulo).classes("text-white/80 text-sm hidden sm:block")
        with ui.row().classes("items-center gap-1"):
            for etiqueta, ruta, icono in (
                ("Mazos", "/", "style"),
                ("Estudiar", "/estudiar", "psychology"),
                ("Herramientas", "/herramientas", "calculate"),
                ("Nueva tarjeta", "/nueva", "add_card"),
            ):
                boton = ui.button(
                    etiqueta, icon=icono, on_click=lambda r=ruta: ui.navigate.to(r)
                ).props("flat color=white no-caps")
                if ruta == activo:
                    boton.props("outline")
            if sesion is not None:
                ui.label(sesion.nombre).classes("text-white/80 text-sm ml-2 hidden md:block")
                ui.button(icon="logout", on_click=_salir).props("flat color=white").tooltip(
                    "Cerrar sesión"
                )


def _salir() -> None:
    cerrar_sesion()
    ui.navigate.to("/login")


def titulo_pagina(texto: str, subtitulo: str = "") -> None:
    with ui.column().classes("w-full gap-0 mb-3"):
        ui.label(texto).classes("text-2xl font-bold")
        if subtitulo:
            ui.label(subtitulo).classes("text-sm text-gray-500 dark:text-gray-400")


def tabla_de_verdad(datos: dict) -> None:
    """Dibuja una tabla de verdad ya calculada por el backend."""
    columnas = [
        {"name": f"c{i}", "label": nombre, "field": f"c{i}", "align": "center"}
        for i, nombre in enumerate(datos["columnas"])
    ]
    filas = [
        {f"c{i}": valor for i, valor in enumerate(fila)} for fila in datos["filas"]
    ]
    with ui.column().classes("w-full gap-2"):
        with ui.row().classes("items-center gap-2"):
            ui.badge(datos["clasificacion"].upper()).props(
                f"color={COLOR_CLASIFICACION.get(datos['clasificacion'], 'primary')}"
            )
            ui.label(
                f"{datos['numero_filas']} filas "
                f"({len(datos['variables'])} variables: {', '.join(datos['variables'])})"
            ).classes("text-sm text-gray-500")
        ui.table(columns=columnas, rows=filas, row_key="c0").props(
            "dense flat bordered"
        ).classes("w-full text-center")


def diagrama_venn(sesion: Sesion, especificacion: dict) -> None:
    """Descarga y muestra el diagrama; si falla, lo dice en vez de dejar un hueco."""
    try:
        fuente = imagen_venn(sesion, especificacion)
    except ErrorApi as error:
        ui.label(f"No se pudo generar el diagrama: {error}").classes("text-negative text-sm")
        return
    ui.image(fuente).classes("w-full max-w-xl rounded border border-gray-300")


def parrafo_multilinea(texto: str, clases: str = "") -> None:
    """Muestra un texto con saltos de línea reales.

    `ui.label` colapsa los `\\n`; el desarrollo de los ejercicios está escrito
    paso por paso y perdería toda su estructura.
    """
    for linea in texto.split("\n"):
        if linea.strip():
            ui.label(linea).classes(f"leading-relaxed {clases}")
        else:
            ui.space()


def campo_formula(
    etiqueta: str, valor_inicial: str = "", al_cambiar: Callable | None = None
) -> ui.input:
    """Campo de texto para fórmulas, con botonera de símbolos lógicos."""
    entrada = ui.input(etiqueta, value=valor_inicial).classes("w-full").props("outlined dense")
    if al_cambiar is not None:
        entrada.on("keydown.enter", al_cambiar)

    def insertar(simbolo: str) -> None:
        entrada.value = (entrada.value or "") + simbolo

    with ui.row().classes("gap-1 flex-wrap"):
        for simbolo in SIMBOLOS:
            ui.button(simbolo, on_click=lambda s=simbolo: insertar(s)).props(
                "flat dense no-caps"
            ).classes("min-w-[2.2rem] text-lg")
        ui.button(
            "Borrar", icon="backspace", on_click=lambda: setattr(entrada, "value", "")
        ).props("flat dense no-caps")
    return entrada
