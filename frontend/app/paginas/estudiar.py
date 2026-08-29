"""Sesión de estudio: la tarjeta se muestra, se gira y se califica."""

from __future__ import annotations

from nicegui import ui

from app.api import ErrorApi, Sesion, calificar, cola_de_estudio
from app.componentes import cabecera, titulo_pagina
from app.estado import avisar, exigir_sesion
from app.paginas.tarjeta import anverso, reverso
from app.temas import GestorTema

# Escala de SM-2 reducida a cuatro botones. Menos opciones que la escala
# completa 0-5 porque a la hora de repasar nadie distingue de verdad seis
# grados de recuerdo; sí distingue estos cuatro.
CALIFICACIONES = [
    (0, "No la sabía", "sentiment_very_dissatisfied", "negative"),
    (3, "Con esfuerzo", "sentiment_neutral", "warning"),
    (4, "Bien", "sentiment_satisfied", "primary"),
    (5, "Perfecta", "sentiment_very_satisfied", "positive"),
]


@ui.page("/estudiar")
def pagina_estudiar(mazo: int | None = None) -> None:
    sesion = exigir_sesion("/estudiar")
    if sesion is None:
        return

    gestor = cabecera("Sesión de estudio", activo="/estudiar")
    with ui.column().classes("w-full max-w-3xl mx-auto p-4 gap-4"):
        titulo_pagina(
            "Sesión de estudio",
            "Lee el concepto, intenta responder de memoria y recién entonces gira "
            "la tarjeta.",
        )
        _Sesion(sesion, mazo, gestor).montar()


class _Sesion:
    """Estado de una tanda de repaso.

    El estado vive en la instancia y no en variables de módulo: con variables
    de módulo, dos personas estudiando a la vez compartirían la misma cola.
    """

    def __init__(
        self, sesion: Sesion, mazo_id: int | None, gestor: GestorTema
    ) -> None:
        self.sesion = sesion
        self.mazo_id = mazo_id
        self.gestor = gestor
        self.cola: list[dict] = []
        self.indice = 0
        self.girada = False
        self.calificadas = 0
        self.contenedor: ui.column | None = None

    def montar(self) -> None:
        self.contenedor = ui.column().classes("w-full gap-4")
        self._cargar_cola()
        self._pintar()

    def _cargar_cola(self) -> None:
        try:
            self.cola = cola_de_estudio(self.sesion, self.mazo_id, limite=20)
        except ErrorApi as error:
            avisar(error)
            self.cola = []
        self.indice = 0
        self.girada = False

    @property
    def actual(self) -> dict | None:
        if self.indice < len(self.cola):
            return self.cola[self.indice]
        return None

    def _girar(self) -> None:
        self.girada = True
        self._pintar()

    def _calificar(self, calidad: int) -> None:
        tarjeta = self.actual
        if tarjeta is None:
            return
        try:
            calificar(self.sesion, tarjeta["id"], calidad)
        except ErrorApi as error:
            avisar(error)
            return
        self.calificadas += 1
        self.indice += 1
        self.girada = False
        self._pintar()

    def _reiniciar(self) -> None:
        self.calificadas = 0
        self._cargar_cola()
        self._pintar()

    def _pintar(self) -> None:
        assert self.contenedor is not None
        self.contenedor.clear()
        with self.contenedor:
            tarjeta = self.actual
            if tarjeta is None:
                self._pintar_final()
                return

            with ui.row().classes("w-full items-center justify-between"):
                ui.label(
                    f"Tarjeta {self.indice + 1} de {len(self.cola)}"
                ).classes("text-sm lab-tenue")
                ui.linear_progress(
                    self.indice / len(self.cola), show_value=False
                ).classes("w-40")

            with ui.card().classes("w-full p-6 gap-4 min-h-[18rem] lab-superficie"):
                anverso(tarjeta)
                if self.girada:
                    ui.separator()
                    reverso(self.sesion, tarjeta, self.gestor.tema)

            if not self.girada:
                ui.button(
                    "Girar tarjeta", icon="flip", on_click=self._girar
                ).props("no-caps size=lg").classes("w-full")
            else:
                ui.label("¿Qué tal la recordaste?").classes("text-sm lab-tenue")
                with ui.row().classes("w-full gap-2 flex-wrap justify-center"):
                    for calidad, etiqueta, icono, color in CALIFICACIONES:
                        ui.button(
                            etiqueta,
                            icon=icono,
                            on_click=lambda c=calidad: self._calificar(c),
                        ).props(f"no-caps color={color}").classes("flex-1 min-w-[9rem]")

    def _pintar_final(self) -> None:
        with ui.card().classes("w-full p-8 items-center gap-3 lab-superficie"):
            ui.icon("celebration", size="48px").classes("text-positive")
            if self.calificadas:
                ui.label(
                    f"Repasaste {self.calificadas} "
                    f"tarjeta{'s' if self.calificadas != 1 else ''}."
                ).classes("text-xl font-semibold")
                ui.label(
                    "Las que fallaste vuelven hoy mismo; las acertadas, más adelante."
                ).classes("text-sm lab-tenue text-center")
            else:
                ui.label("No hay tarjetas pendientes por ahora.").classes(
                    "text-xl font-semibold"
                )
                ui.label(
                    "Vuelve cuando toque el próximo repaso, o revisa los mazos "
                    "para consultarlas."
                ).classes("text-sm lab-tenue text-center")
            with ui.row().classes("gap-2 mt-2"):
                ui.button("Buscar más", icon="refresh", on_click=self._reiniciar).props(
                    "no-caps"
                )
                ui.button(
                    "Ver mazos", icon="style", on_click=lambda: ui.navigate.to("/")
                ).props("flat no-caps")
