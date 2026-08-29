"""Laboratorio de cálculo: tablas de verdad, conjuntos y diagramas de Venn."""

from __future__ import annotations

from nicegui import ui

from app.api import (
    ErrorApi,
    Sesion,
    equivalencia,
    imagen_venn,
    operar_conjuntos,
    regiones_venn,
    tabla_de_verdad,
)
from app.componentes import cabecera, campo_formula, titulo_pagina
from app.componentes import tabla_de_verdad as pintar_tabla
from app.estado import exigir_sesion
from app.temas import Tema


@ui.page("/herramientas")
def pagina_herramientas() -> None:
    sesion = exigir_sesion("/herramientas")
    if sesion is None:
        return

    gestor = cabecera("Herramientas", activo="/herramientas")
    with ui.column().classes("w-full max-w-4xl mx-auto p-4 gap-4"):
        titulo_pagina(
            "Herramientas de cálculo",
            "Escribe tus propios ejercicios y contrástalos con el resultado del motor.",
        )
        with ui.tabs().classes("w-full") as pestanas:
            ui.tab("tabla", label="Tabla de verdad", icon="table_chart")
            ui.tab("equivalencia", label="Equivalencia", icon="compare_arrows")
            ui.tab("conjuntos", label="Conjuntos", icon="join_inner")
            ui.tab("venn", label="Diagrama de Venn", icon="pie_chart")
        with ui.tab_panels(pestanas, value="tabla").classes("w-full"):
            with ui.tab_panel("tabla"):
                _panel_tabla(sesion)
            with ui.tab_panel("equivalencia"):
                _panel_equivalencia(sesion)
            with ui.tab_panel("conjuntos"):
                _panel_conjuntos(sesion)
            with ui.tab_panel("venn"):
                _panel_venn(sesion, gestor.tema)


# --------------------------------------------------------------------------
def _panel_tabla(sesion: Sesion) -> None:
    # `resultado` se declara aquí y se crea al final: el contenedor tiene que
    # quedar DEBAJO del formulario, pero `calcular` necesita cerrarse sobre él.
    resultado: ui.column

    def calcular() -> None:
        resultado.clear()
        try:
            datos = tabla_de_verdad(sesion, entrada.value or "")
        except ErrorApi as error:
            with resultado:
                _mostrar_error(error, entrada.value or "")
            return
        with resultado:
            pintar_tabla(datos)

    ui.label(
        "Acepta los símbolos de la asignatura y también los atajos de teclado: "
        "~ o !, & o ^, | , -> , <->."
    ).classes("text-sm lab-tenue")
    entrada = campo_formula("Fórmula proposicional", "(p ∨ r) → (p ∧ ¬s)", calcular)
    ui.button("Calcular tabla", icon="play_arrow", on_click=calcular).props("no-caps")
    resultado = ui.column().classes("w-full gap-2")
    calcular()


def _panel_equivalencia(sesion: Sesion) -> None:
    resultado: ui.column

    def comprobar() -> None:
        resultado.clear()
        try:
            datos = equivalencia(sesion, a.value or "", b.value or "")
        except ErrorApi as error:
            with resultado:
                _mostrar_error(error, f"{a.value} / {b.value}")
            return
        with resultado:
            if datos["equivalentes"]:
                ui.label("Son lógicamente equivalentes.").classes(
                    "text-positive font-semibold"
                )
                ui.label(
                    "Su bicondicional es una tautología, así que se pueden sustituir "
                    "la una por la otra."
                ).classes("text-sm lab-tenue")
            else:
                ui.label("No son equivalentes.").classes("text-negative font-semibold")
                ui.label(
                    "Busca en la tabla la fila con F en la última columna: ahí es donde "
                    "difieren."
                ).classes("text-sm lab-tenue")
            pintar_tabla(datos["tabla"])

    ui.label(
        "Dos fórmulas son equivalentes si su bicondicional es una tautología."
    ).classes("text-sm lab-tenue")
    a = campo_formula("Primera fórmula", "¬(p ∧ q)", comprobar)
    b = campo_formula("Segunda fórmula", "¬p ∨ ¬q", comprobar)
    ui.button("Comprobar", icon="play_arrow", on_click=comprobar).props("no-caps")
    resultado = ui.column().classes("w-full gap-2")
    comprobar()


def _panel_conjuntos(sesion: Sesion) -> None:
    resultado: ui.column

    def separar(texto: str) -> list[str]:
        """Admite «1, 2, 3», «1 2 3» y «{1,2,3}» — lo que se copia del enunciado."""
        limpio = (texto or "").replace("{", " ").replace("}", " ").replace(",", " ")
        return [t for t in limpio.split() if t]

    def calcular() -> None:
        resultado.clear()
        try:
            datos = operar_conjuntos(
                sesion, separar(a.value), separar(b.value), separar(u.value)
            )
        except ErrorApi as error:
            with resultado:
                _mostrar_error(error, "")
            return
        with resultado:
            filas = [
                ("A ∪ B", datos["union"]),
                ("A ∩ B", datos["interseccion"]),
                ("A − B", datos["diferencia_ab"]),
                ("B − A", datos["diferencia_ba"]),
                ("A Δ B", datos["diferencia_simetrica"]),
                ("Aᶜ", datos["complemento_a"]),
                ("Bᶜ", datos["complemento_b"]),
            ]
            for etiqueta, valores in filas:
                with ui.row().classes("items-baseline gap-2"):
                    ui.label(etiqueta).classes("font-mono font-semibold w-20")
                    ui.label("{" + ", ".join(valores) + "}").classes("font-mono")
            card = datos["cardinalidades"]
            ui.separator()
            ui.label(
                f"|A| = {card['a']} · |B| = {card['b']} · |A ∪ B| = {card['union']} · "
                f"|A ∩ B| = {card['interseccion']} · |℘(A)| = {card['partes_de_a']}"
            ).classes("text-sm lab-tenue")

    ui.label(
        "Si no declaras universo, se toma A ∪ B como universo para los complementos."
    ).classes("text-sm lab-tenue")
    a = ui.input("Conjunto A", value="1, 2, 3, 4").classes("w-full").props("outlined dense")
    b = ui.input("Conjunto B", value="3, 4, 5, 6").classes("w-full").props("outlined dense")
    u = ui.input("Universo (opcional)", value="").classes("w-full").props("outlined dense")
    for campo in (a, b, u):
        campo.on("keydown.enter", calcular)
    ui.button("Calcular", icon="play_arrow", on_click=calcular).props("no-caps")
    resultado = ui.column().classes("w-full gap-2")
    calcular()


def _panel_venn(sesion: Sesion, tema: Tema) -> None:
    resultado: ui.column

    def numero(campo: ui.input) -> int:
        try:
            return int(float(campo.value or 0))
        except ValueError:
            return 0

    def calcular() -> None:
        resultado.clear()
        tres = usar_c.value
        especificacion: dict = {
            "etiquetas": [e_a.value or "A", e_b.value or "B"],
            "cardinalidades": {"a": numero(n_a), "b": numero(n_b), "ab": numero(n_ab)},
            "universo": numero(n_u) or None,
            "titulo": titulo.value or "",
        }
        if tres:
            especificacion["etiquetas"].append(e_c.value or "C")
            especificacion["cardinalidades"].update(
                {
                    "c": numero(n_c),
                    "ac": numero(n_ac),
                    "bc": numero(n_bc),
                    "abc": numero(n_abc),
                }
            )
        try:
            regiones = regiones_venn(sesion, especificacion)["regiones"]
            fuente = imagen_venn(
                sesion,
                {**especificacion, "fondo": tema.lab_venn_fondo,
                 "tinta": tema.lab_venn_texto},
            )
        except ErrorApi as error:
            with resultado:
                _mostrar_error(error, "")
            return
        with resultado:
            ui.image(fuente).classes("w-full max-w-2xl rounded lab-superficie")
            with ui.row().classes("flex-wrap gap-3 justify-center"):
                for clave, valor in regiones.items():
                    with ui.column().classes("items-center gap-0"):
                        ui.label(str(valor)).classes("font-bold")
                        ui.label(clave.replace("_", " ")).classes("text-xs lab-tenue")

    # `ui.markdown`, no `ui.label`: label no interpreta el formato y los
    # asteriscos salían literales en pantalla.
    ui.markdown(
        "Introduce las cardinalidades **totales** del enunciado; el reparto por "
        "regiones lo calcula el motor con inclusión-exclusión."
    ).classes("text-sm lab-tenue")

    usar_c = ui.switch("Tres conjuntos", value=False, on_change=lambda: _alternar())
    with ui.row().classes("w-full gap-2 flex-wrap"):
        e_a = ui.input("Nombre A", value="Java").props("outlined dense").classes("flex-1")
        e_b = ui.input("Nombre B", value="Python").props("outlined dense").classes("flex-1")
        e_c = ui.input("Nombre C", value="C++").props("outlined dense").classes("flex-1")
    with ui.row().classes("w-full gap-2 flex-wrap"):
        n_a = ui.number("n(A)", value=70).props("outlined dense").classes("flex-1")
        n_b = ui.number("n(B)", value=50).props("outlined dense").classes("flex-1")
        n_c = ui.number("n(C)", value=45).props("outlined dense").classes("flex-1")
    with ui.row().classes("w-full gap-2 flex-wrap"):
        n_ab = ui.number("n(A∩B)", value=30).props("outlined dense").classes("flex-1")
        n_ac = ui.number("n(A∩C)", value=25).props("outlined dense").classes("flex-1")
        n_bc = ui.number("n(B∩C)", value=20).props("outlined dense").classes("flex-1")
    with ui.row().classes("w-full gap-2 flex-wrap"):
        n_abc = ui.number("n(A∩B∩C)", value=15).props("outlined dense").classes("flex-1")
        n_u = ui.number("Universo", value=120).props("outlined dense").classes("flex-1")
    titulo = ui.input("Título del diagrama", value="").props("outlined dense").classes("w-full")

    solo_tres = [e_c, n_c, n_ac, n_bc, n_abc]

    def _alternar() -> None:
        for campo in solo_tres:
            campo.set_visibility(bool(usar_c.value))
        calcular()

    ui.button("Dibujar", icon="play_arrow", on_click=calcular).props("no-caps")
    resultado = ui.column().classes("w-full gap-2 items-center")
    _alternar()


def _mostrar_error(error: ErrorApi, contexto: str) -> None:
    """Muestra el error con la pista de posición cuando la API la devuelve."""
    ui.label(str(error)).classes("text-negative font-medium")
    posicion = error.detalle.get("posicion")
    if posicion is not None and contexto:
        ui.label(contexto).classes("font-mono text-sm")
        ui.label(" " * int(posicion) + "▲").classes("font-mono text-sm text-negative")
