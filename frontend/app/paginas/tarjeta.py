"""Render de una tarjeta.

Vive aparte porque lo usan dos pantallas con necesidades distintas: el listado
del mazo (todo desplegado, para consultar) y la sesión de estudio (anverso
primero, reverso solo al girarla). Duplicar este render en ambas garantizaría
que se desincronicen a la primera corrección.

El tema llega como parámetro y no se lee de un global: el diagrama de Venn se
genera en el backend con los colores de la paleta activa, así que quien pinta
la tarjeta tiene que saber cuál es.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from nicegui import ui

from app.api import ErrorApi, Sesion
from app.api import operar_matrices as pedir_matriz
from app.api import resolver_sistema as pedir_sistema
from app.api import tabla_de_verdad as pedir_tabla
from app.componentes import (
    diagrama_venn,
    matriz_resuelta,
    parrafo_multilinea,
    sistema_resuelto,
    tabla_de_verdad,
)
from app.temas import Tema


def anverso(tarjeta: dict) -> None:
    """Lo que se ve antes de girar la tarjeta: el concepto y la pregunta."""
    with ui.column().classes("w-full items-center gap-2 py-6"):
        ui.label(tarjeta["concepto"]).classes("text-2xl font-bold text-center lab-texto")
        ui.label(tarjeta["pregunta"]).classes("text-lg text-center lab-tenue")


def reverso(sesion: Sesion, tarjeta: dict, tema: Tema) -> None:
    """La definición, la clave de memoria y el ejercicio resuelto."""
    with ui.column().classes("w-full gap-3"):
        parrafo_multilinea(tarjeta["definicion"])

        if tarjeta.get("notacion"):
            ui.label(f"Notación: {tarjeta['notacion']}").classes(
                "font-mono text-sm lab-codigo p-2 w-full"
            )

        if tarjeta.get("clave_memoria"):
            with ui.row().classes("items-start gap-2 w-full"):
                ui.icon("lightbulb", size="18px").classes("text-warning mt-1")
                with ui.column().classes("gap-0 flex-1"):
                    parrafo_multilinea(tarjeta["clave_memoria"], "text-sm")

        ui.separator().classes("lab-borde")
        ui.label("Ejercicio resuelto").classes("font-semibold text-primary")
        parrafo_multilinea(tarjeta["ejercicio_enunciado"], "text-sm")

        with ui.card().classes("w-full lab-superficie lab-superficie-alta p-3 gap-0"):
            ui.label("Desarrollo").classes("text-xs uppercase lab-tenue mb-1")
            parrafo_multilinea(tarjeta["ejercicio_desarrollo"], "text-sm font-mono")

        with ui.row().classes("items-start gap-2 w-full"):
            ui.icon("check_circle", size="20px").classes("text-positive mt-1")
            with ui.column().classes("gap-0 flex-1"):
                parrafo_multilinea(tarjeta["ejercicio_respuesta"], "font-medium")

        for extra in EXTRAS:
            if tarjeta.get(extra.campo):
                ui.separator().classes("lab-borde")
                ui.label(extra.titulo(tarjeta)).classes("text-sm font-semibold")
                extra.pintar(sesion, tarjeta[extra.campo], tema)

        if tarjeta.get("fuente"):
            ui.label(f"Fuente: {tarjeta['fuente']}").classes("text-xs lab-tenue mt-2")


def _tabla(sesion: Sesion, formula: str) -> None:
    try:
        tabla_de_verdad(pedir_tabla(sesion, formula))
    except ErrorApi as error:
        ui.label(f"No se pudo calcular la tabla: {error}").classes("text-negative text-sm")


def _sistema(sesion: Sesion, declarado: dict) -> None:
    """El sistema de la tarjeta, recalculado en vivo con aritmética exacta.

    Es la segunda mitad de la doble verificación que se ve en pantalla: el
    desarrollo escrito a mano está arriba, y aquí debajo el que calcula el
    motor. Si alguna vez discreparan, se notaría al estudiar.
    """
    try:
        sistema_resuelto(
            pedir_sistema(
                sesion,
                declarado["matriz"],
                declarado.get("incognitas"),
                declarado.get("metodo"),
            )
        )
    except ErrorApi as error:
        ui.label(f"No se pudo resolver el sistema: {error}").classes(
            "text-negative text-sm"
        )


def _matriz(sesion: Sesion, declarada: dict) -> None:
    """La operación de la tarjeta, recalculada en vivo: misma idea que `_sistema`."""
    try:
        matriz_resuelta(pedir_matriz(sesion, declarada))
    except ErrorApi as error:
        ui.label(f"No se pudo calcular la operación: {error}").classes(
            "text-negative text-sm"
        )


@dataclass(frozen=True)
class Extra:
    """Un bloque calculado del reverso: qué campo lo activa, su título y quién lo pinta."""

    campo: str
    titulo: Callable[[dict], str]
    pintar: Callable[[Sesion, Any, Tema], None]


# Los bloques que el motor calcula en vivo, en el orden en que se muestran. Un
# campo calculado nuevo en las tarjetas es una entrada más aquí, no otro `if`
# en `reverso`. Cada uno es la segunda mitad de la doble verificación: el
# desarrollo escrito a mano está arriba, y el del motor debajo.
EXTRAS: tuple[Extra, ...] = (
    Extra("formula", lambda t: f"Tabla de verdad de {t['formula']}",
          lambda sesion, formula, _: _tabla(sesion, formula)),
    Extra("venn", lambda _: "Diagrama de Venn", diagrama_venn),
    Extra("sistema", lambda _: "El sistema, resuelto por el motor",
          lambda sesion, sistema, _: _sistema(sesion, sistema)),
    Extra("matriz", lambda _: "La operación, resuelta por el motor",
          lambda sesion, matriz, _: _matriz(sesion, matriz)),
)


def panel_tarjeta(sesion: Sesion, tarjeta: dict, tema: Tema) -> None:
    """Tarjeta completa (anverso + reverso), para consulta."""
    with ui.column().classes("w-full gap-2 p-2"):
        if not tarjeta.get("es_semilla", True):
            ui.badge("propia").props("color=accent")
        ui.label(tarjeta["pregunta"]).classes("italic lab-tenue")
        reverso(sesion, tarjeta, tema)
