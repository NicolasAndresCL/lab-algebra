"""Alta de tarjetas y de mazos propios.

El laboratorio nace con el temario de la asignatura, pero el material crece:
esta pantalla permite añadir tarjetas para las unidades que vengan después sin
tocar una línea de código ni volver a construir la imagen.
"""

from __future__ import annotations

from nicegui import ui

from app.api import ErrorApi, Sesion, crear_mazo, crear_tarjeta, listar_mazos
from app.componentes import cabecera, campo_formula, titulo_pagina
from app.estado import avisar, exigir_sesion


@ui.page("/nueva")
def pagina_nueva() -> None:
    sesion = exigir_sesion("/nueva")
    if sesion is None:
        return

    cabecera("Nueva tarjeta", activo="/nueva")
    with ui.column().classes("w-full max-w-3xl mx-auto p-4 gap-4"):
        titulo_pagina(
            "Añadir material",
            "Las tarjetas nuevas entran en la misma cola de repaso que las del temario.",
        )
        with ui.tabs().classes("w-full") as pestanas:
            ui.tab("tarjeta", label="Nueva tarjeta", icon="add_card")
            ui.tab("mazo", label="Nuevo mazo", icon="create_new_folder")
        with ui.tab_panels(pestanas, value="tarjeta").classes("w-full"):
            with ui.tab_panel("tarjeta"):
                _formulario_tarjeta(sesion)
            with ui.tab_panel("mazo"):
                _formulario_mazo(sesion)


def _formulario_tarjeta(sesion: Sesion) -> None:
    try:
        mazos = listar_mazos(sesion)
    except ErrorApi as error:
        avisar(error)
        return
    if not mazos:
        ui.label("Todavía no hay mazos. Crea uno en la otra pestaña.").classes(
            "lab-tenue"
        )
        return

    opciones = {m["id"]: f"{m['nombre']} ({m['total_tarjetas']})" for m in mazos}
    mazo = ui.select(opciones, label="Mazo", value=mazos[0]["id"]).classes("w-full").props(
        "outlined dense"
    )
    concepto = ui.input("Concepto").classes("w-full").props("outlined dense")
    pregunta = ui.input("Pregunta del anverso").classes("w-full").props("outlined dense")
    definicion = ui.textarea("Definición").classes("w-full").props("outlined dense autogrow")
    notacion = ui.input("Notación (opcional)").classes("w-full").props("outlined dense")
    clave = ui.textarea("Clave de memoria (opcional)").classes("w-full").props(
        "outlined dense autogrow"
    )

    ui.separator()
    ui.label("Ejercicio resuelto").classes("font-semibold text-primary")
    ui.label(
        "Los tres campos son obligatorios: una tarjeta sin ejercicio resuelto no "
        "enseña a aplicar el concepto."
    ).classes("text-sm lab-tenue")
    enunciado = ui.textarea("Enunciado").classes("w-full").props("outlined dense autogrow")
    desarrollo = ui.textarea("Desarrollo paso a paso").classes("w-full").props(
        "outlined dense autogrow"
    )
    respuesta = ui.textarea("Respuesta").classes("w-full").props("outlined dense autogrow")

    ui.separator()
    ui.label("Extras opcionales").classes("font-semibold")
    ui.label(
        "Si indicas una fórmula, la tarjeta mostrará su tabla de verdad calculada."
    ).classes("text-sm lab-tenue")
    formula = campo_formula("Fórmula (opcional)")
    fuente = ui.input("Fuente (clase, lámina, PDF…)").classes("w-full").props("outlined dense")

    def guardar() -> None:
        faltan = [
            etiqueta
            for etiqueta, campo in (
                ("concepto", concepto),
                ("pregunta", pregunta),
                ("definición", definicion),
                ("enunciado", enunciado),
                ("desarrollo", desarrollo),
                ("respuesta", respuesta),
            )
            if not (campo.value or "").strip()
        ]
        if faltan:
            ui.notify(
                f"Faltan campos obligatorios: {', '.join(faltan)}.",
                type="warning",
                position="top",
            )
            return

        datos = {
            "mazo_id": mazo.value,
            "concepto": concepto.value.strip(),
            "pregunta": pregunta.value.strip(),
            "definicion": definicion.value.strip(),
            "notacion": (notacion.value or "").strip(),
            "clave_memoria": (clave.value or "").strip(),
            "ejercicio_enunciado": enunciado.value.strip(),
            "ejercicio_desarrollo": desarrollo.value.strip(),
            "ejercicio_respuesta": respuesta.value.strip(),
            "formula": (formula.value or "").strip() or None,
            "fuente": (fuente.value or "").strip(),
        }
        try:
            creada = crear_tarjeta(sesion, datos)
        except ErrorApi as error:
            avisar(error)
            return

        ui.notify(
            f"Tarjeta «{creada['concepto']}» creada.", type="positive", position="top"
        )
        for campo in (concepto, pregunta, definicion, notacion, clave, enunciado,
                      desarrollo, respuesta, formula, fuente):
            campo.value = ""

    ui.button("Guardar tarjeta", icon="save", on_click=guardar).props("no-caps").classes(
        "w-full"
    )


def _formulario_mazo(sesion: Sesion) -> None:
    slug = ui.input(
        "Identificador", placeholder="solo minúsculas, números y guiones"
    ).classes("w-full").props("outlined dense")
    nombre = ui.input("Nombre").classes("w-full").props("outlined dense")
    unidad = ui.input("Unidad", placeholder="Lógica, Conjuntos, Relaciones…").classes(
        "w-full"
    ).props("outlined dense")
    descripcion = ui.textarea("Descripción").classes("w-full").props("outlined dense autogrow")
    orden = ui.number("Orden en el listado", value=70).classes("w-full").props("outlined dense")

    def guardar() -> None:
        if not (slug.value or "").strip() or not (nombre.value or "").strip():
            ui.notify(
                "El identificador y el nombre son obligatorios.",
                type="warning",
                position="top",
            )
            return
        try:
            creado = crear_mazo(
                sesion,
                {
                    "slug": slug.value.strip().lower(),
                    "nombre": nombre.value.strip(),
                    "descripcion": (descripcion.value or "").strip(),
                    "unidad": (unidad.value or "").strip(),
                    "orden": int(orden.value or 0),
                },
            )
        except ErrorApi as error:
            avisar(error)
            return
        ui.notify(f"Mazo «{creado['nombre']}» creado.", type="positive", position="top")
        ui.navigate.to("/")

    ui.button("Crear mazo", icon="save", on_click=guardar).props("no-caps").classes("w-full")
