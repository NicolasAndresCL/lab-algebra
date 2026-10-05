"""Portada (progreso y mazos) y listado de tarjetas de un mazo."""

from __future__ import annotations

from nicegui import ui

from app.api import ErrorApi, Sesion, listar_mazos, listar_tarjetas, progreso
from app.componentes import cabecera, titulo_pagina
from app.estado import avisar, exigir_sesion
from app.paginas.tarjeta import panel_tarjeta

# Ecuaciones comparte el primario con Lógica (es el color que ya mostraba por
# defecto); Matrices toma el acento para no confundirse con Ecuaciones, que es
# la unidad que tiene al lado en la rejilla.
COLOR_UNIDAD = {
    "Lógica": "primary",
    "Conjuntos": "secondary",
    "Ecuaciones": "primary",
    "Matrices": "accent",
}


@ui.page("/")
def pagina_inicio() -> None:
    sesion = exigir_sesion("/")
    if sesion is None:
        return

    cabecera("Mazos", activo="/")
    with ui.column().classes("w-full max-w-5xl mx-auto p-4 gap-4"):
        titulo_pagina(
            "Mazos de estudio",
            "Cada tarjeta trae la definición y un ejercicio resuelto paso a paso.",
        )
        _panel_progreso(sesion)
        _rejilla_de_mazos(sesion)


def _panel_progreso(sesion: Sesion) -> None:
    try:
        datos = progreso(sesion)
    except ErrorApi as error:
        avisar(error)
        return

    with ui.card().classes("w-full p-4 lab-superficie"):
        with ui.row().classes("w-full justify-around items-center flex-wrap gap-4"):
            for etiqueta, valor, icono in (
                ("Tarjetas", datos["total_tarjetas"], "style"),
                ("Estudiadas", datos["estudiadas"], "done_all"),
                ("Pendientes hoy", datos["pendientes_hoy"], "schedule"),
                ("Aciertos", datos["aciertos"], "check_circle"),
                ("Fallos", datos["fallos"], "cancel"),
                ("% acierto", f"{datos['porcentaje_acierto']}%", "insights"),
            ):
                with ui.column().classes("items-center gap-0"):
                    ui.icon(icono, size="22px").classes("text-primary")
                    ui.label(str(valor)).classes("text-xl font-bold")
                    ui.label(etiqueta).classes("text-xs lab-tenue")

        if datos["total_tarjetas"]:
            avance = datos["estudiadas"] / datos["total_tarjetas"]
            ui.linear_progress(avance, show_value=False).classes("w-full mt-2")


def _rejilla_de_mazos(sesion: Sesion) -> None:
    try:
        mazos = listar_mazos(sesion)
    except ErrorApi as error:
        avisar(error)
        return

    with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2"):
        for mazo in mazos:
            with ui.card().classes("p-4 gap-2 lab-superficie"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label(mazo["nombre"]).classes("text-lg font-semibold")
                    ui.badge(mazo["unidad"]).props(
                        f"color={COLOR_UNIDAD.get(mazo['unidad'], 'primary')}"
                    )
                ui.label(mazo["descripcion"]).classes("text-sm lab-tenue")
                with ui.row().classes("items-center justify-between w-full mt-2"):
                    ui.label(f"{mazo['total_tarjetas']} tarjetas").classes(
                        "text-sm lab-tenue"
                    )
                    with ui.row().classes("gap-2"):
                        ui.button(
                            "Ver",
                            icon="visibility",
                            on_click=lambda m=mazo: ui.navigate.to(f"/mazo/{m['id']}"),
                        ).props("flat no-caps")
                        ui.button(
                            "Estudiar",
                            icon="psychology",
                            on_click=lambda m=mazo: ui.navigate.to(
                                f"/estudiar?mazo={m['id']}"
                            ),
                        ).props("no-caps")


@ui.page("/mazo/{mazo_id}")
def pagina_mazo(mazo_id: int) -> None:
    sesion = exigir_sesion(f"/mazo/{mazo_id}")
    if sesion is None:
        return

    gestor = cabecera("Tarjetas del mazo", activo="/")
    with ui.column().classes("w-full max-w-4xl mx-auto p-4 gap-4"):
        try:
            mazos = {m["id"]: m for m in listar_mazos(sesion)}
        except ErrorApi as error:
            avisar(error)
            return

        mazo = mazos.get(mazo_id)
        if mazo is None:
            ui.label("Ese mazo no existe.").classes("text-negative")
            ui.button("Volver a los mazos", on_click=lambda: ui.navigate.to("/")).props(
                "flat no-caps"
            )
            return

        titulo_pagina(mazo["nombre"], mazo["descripcion"])

        buscador = (
            ui.input("Buscar concepto o definición")
            .classes("w-full")
            .props("outlined dense clearable")
        )
        contenedor = ui.column().classes("w-full gap-3")

        def recargar() -> None:
            contenedor.clear()
            try:
                tarjetas = listar_tarjetas(sesion, mazo_id, buscador.value or None)
            except ErrorApi as error:
                avisar(error)
                return
            with contenedor:
                if not tarjetas:
                    ui.label("Ninguna tarjeta coincide con la búsqueda.").classes(
                        "lab-tenue"
                    )
                for tarjeta in tarjetas:
                    with ui.expansion(tarjeta["concepto"]).classes(
                        "w-full rounded lab-superficie"
                    ).props("dense-toggle"):
                        panel_tarjeta(sesion, tarjeta, gestor.tema)

        buscador.on("keydown.enter", recargar)
        buscador.on("clear", recargar)
        recargar()
