"""Pantalla de inicio de sesión."""

from __future__ import annotations

from nicegui import ui

from app.api import ErrorApi, login, salud
from app.estado import avisar, destino_pendiente, guardar_sesion, sesion_actual


@ui.page("/login")
def pagina_login() -> None:
    if sesion_actual() is not None:
        ui.navigate.to("/")
        return

    ui.query("body").classes("bg-gray-100 dark:bg-gray-900")

    with (
        ui.column().classes("w-full h-screen items-center justify-center gap-4"),
        ui.card().classes("w-full max-w-md p-6 gap-4"),
    ):
        with ui.row().classes("items-center gap-3"):
            ui.icon("school", size="34px").classes("text-primary")
            with ui.column().classes("gap-0"):
                ui.label("lab-algebra").classes("text-2xl font-bold")
                ui.label("Tarjetas de Álgebra — ST 2026").classes(
                    "text-sm text-gray-500"
                )

        ui.separator()

        usuario = ui.input("Usuario", value="").classes("w-full").props(
            "outlined dense autofocus"
        )
        clave = (
            ui.input("Contraseña", password=True, password_toggle_button=True)
            .classes("w-full")
            .props("outlined dense")
        )

        def entrar() -> None:
            try:
                sesion = login((usuario.value or "").strip(), clave.value or "")
            except ErrorApi as error:
                avisar(error)
                clave.value = ""
                return
            guardar_sesion(sesion)
            ui.navigate.to(destino_pendiente())

        clave.on("keydown.enter", entrar)
        usuario.on("keydown.enter", entrar)

        ui.button("Entrar", icon="login", on_click=entrar).props("no-caps").classes(
            "w-full"
        )

        estado = salud()
        color = "text-positive" if estado.get("estado") == "ok" else "text-negative"
        with ui.row().classes("items-center gap-2 justify-center w-full"):
            ui.icon("dns", size="16px").classes(color)
            ui.label(f"API: {estado.get('estado')} · base de datos: "
                     f"{estado.get('base_de_datos')}").classes(f"text-xs {color}")
