"""Componentes de interfaz reutilizados por varias páginas."""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from app.api import ErrorApi, Sesion, imagen_venn
from app.estado import cerrar_sesion, sesion_actual
from app.temas import TEMAS, GestorTema, Tema

# Símbolos que el teclado no trae. Se ofrecen como botones para que escribir
# una fórmula no obligue a buscar caracteres en el mapa de caracteres.
SIMBOLOS = ["¬", "∧", "∨", "⊻", "→", "↔", "(", ")"]

COLOR_CLASIFICACION = {
    "tautología": "positive",
    "contradicción": "negative",
    "contingencia": "warning",
}

# Los tres tipos de sistema de la tercera unidad. El indeterminado va en
# «warning» y no en «positive» aunque sí tenga solución: lo que avisa el color
# es que la respuesta no es un punto y hay que entregar la familia entera.
COLOR_SISTEMA = {
    "compatible determinado": "positive",
    "compatible indeterminado": "warning",
    "incompatible": "negative",
}


# --------------------------------------------------------------------------
# Tema
# --------------------------------------------------------------------------
def selector_de_tema(gestor: GestorTema) -> None:
    """Botón de paleta con el menú de temas.

    Va **a la izquierda del botón de cerrar sesión**: es una preferencia que se
    toca a menudo, y pegarla al botón de salir sin separarla invitaría a
    pulsarlo por error.
    """
    with (
        ui.button(icon="palette").props("flat round").tooltip("Cambiar de tema"),
        ui.menu().props("auto-close").classes("lab-superficie"),
    ):
        ui.label("Tema de la interfaz").classes("px-3 pt-2 pb-1 text-xs lab-tenue")
        for tema in TEMAS.values():
            _fila_de_tema(gestor, tema)


def _fila_de_tema(gestor: GestorTema, tema: Tema) -> None:
    def elegir() -> None:
        gestor.cambiar(tema)
        ui.notify(f"Tema «{tema.nombre}»", type="positive", position="bottom-right")

    with ui.item(on_click=elegir).classes("min-w-[17rem]"):
        with ui.item_section().props("avatar"):
            # Una muestra con los tres colores reales del tema dice más que el
            # nombre: «Ónix» y «Carbón» no se distinguen por el texto.
            fondo, superficie, marca = tema.muestra
            ui.html(
                f'<span class="lab-muestra" style="background: linear-gradient('
                f"90deg, {fondo} 0 40%, {superficie} 40% 70%, {marca} 70% 100%)\"></span>"
            )
        with ui.item_section():
            with ui.row().classes("items-center gap-2 no-wrap"):
                ui.label(tema.nombre).classes("font-medium")
                if tema.clave == gestor.tema.clave:
                    ui.icon("check", size="18px").classes("text-positive")
            ui.label(tema.descripcion).classes("text-xs lab-tenue")


# --------------------------------------------------------------------------
# Estructura de página
# --------------------------------------------------------------------------
def cabecera(titulo: str, activo: str = "") -> GestorTema:
    """Barra superior con la navegación, el selector de tema y la salida.

    Devuelve el gestor de tema porque lo crea ella: el tema tiene que aplicarse
    **antes** de que se pinte el contenido, y la cabecera es lo primero que
    construye toda página.
    """
    gestor = GestorTema()
    sesion = sesion_actual()

    with ui.header().classes("items-center justify-between px-4 py-2 lab-cabecera"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("school", size="28px").classes("text-primary")
            ui.label("lab-algebra").classes("text-lg font-bold lab-rotulo")
            ui.label(titulo).classes("text-sm opacity-70 hidden sm:block lab-rotulo")

        with ui.row().classes("items-center gap-1"):
            for etiqueta, ruta, icono in (
                ("Mazos", "/", "style"),
                ("Estudiar", "/estudiar", "psychology"),
                ("Herramientas", "/herramientas", "calculate"),
                ("Nueva tarjeta", "/nueva", "add_card"),
            ):
                boton = ui.button(
                    etiqueta, icon=icono, on_click=lambda r=ruta: ui.navigate.to(r)
                ).props("flat no-caps")
                if ruta == activo:
                    boton.props("outline")

            if sesion is not None:
                ui.label(sesion.nombre).classes(
                    "text-sm opacity-70 ml-2 hidden md:block lab-rotulo"
                )
            ui.separator().props("vertical inset").classes("mx-1 opacity-30")
            selector_de_tema(gestor)
            if sesion is not None:
                ui.button(icon="logout", on_click=_salir).props("flat round").tooltip(
                    "Cerrar sesión"
                )
    return gestor


def _salir() -> None:
    cerrar_sesion()
    ui.navigate.to("/login")


def titulo_pagina(texto: str, subtitulo: str = "") -> None:
    with ui.column().classes("w-full gap-0 mb-3"):
        ui.label(texto).classes("text-2xl font-bold lab-texto")
        if subtitulo:
            ui.label(subtitulo).classes("text-sm lab-tenue")


# --------------------------------------------------------------------------
# Contenido
# --------------------------------------------------------------------------
def tabla_de_verdad(datos: dict) -> None:
    """Dibuja una tabla de verdad ya calculada por el backend."""
    columnas = [
        {"name": f"c{i}", "label": nombre, "field": f"c{i}", "align": "center"}
        for i, nombre in enumerate(datos["columnas"])
    ]
    filas = [{f"c{i}": valor for i, valor in enumerate(fila)} for fila in datos["filas"]]
    with ui.column().classes("w-full gap-2"):
        with ui.row().classes("items-center gap-2"):
            ui.badge(datos["clasificacion"].upper()).props(
                f"color={COLOR_CLASIFICACION.get(datos['clasificacion'], 'primary')}"
            )
            ui.label(
                f"{datos['numero_filas']} filas "
                f"({len(datos['variables'])} variables: {', '.join(datos['variables'])})"
            ).classes("text-sm lab-tenue")
        ui.table(columns=columnas, rows=filas, row_key="c0").props(
            "dense flat bordered"
        ).classes("w-full text-center lab-tabla")


def sistema_resuelto(datos: dict) -> None:
    """Dibuja un sistema ya resuelto por el backend: camino y respuesta.

    El desarrollo va **antes** que la respuesta a propósito: esto es material
    de estudio, y una tarjeta que enseña primero el resultado invita a saltarse
    justo lo que hay que aprender.
    """
    with ui.column().classes("w-full gap-2"):
        with ui.row().classes("items-center gap-2 flex-wrap"):
            ui.badge(datos["clasificacion"].upper()).props(
                f"color={COLOR_SISTEMA.get(datos['clasificacion'], 'primary')}"
            )
            if datos.get("delta") is not None:
                ui.label(f"Δ = {datos['delta']}").classes("font-mono text-sm")
            ui.label(f"por {datos['metodo']}").classes("text-sm lab-tenue")

        with ui.card().classes("w-full lab-superficie lab-superficie-alta p-3 gap-1"):
            ui.label("Sistema").classes("text-xs uppercase lab-tenue")
            for numero, ecuacion in enumerate(datos["ecuaciones"], start=1):
                ui.label(f"({numero})  {ecuacion}").classes("font-mono text-sm")

        with (
            ui.expansion("Desarrollo paso a paso", icon="functions").classes(
                "w-full lab-superficie"
            ),
            ui.column().classes("w-full gap-1 p-2"),
        ):
            for paso in datos["pasos"]:
                ui.label(paso).classes("font-mono text-sm leading-relaxed")

        with ui.row().classes("items-start gap-2 w-full"):
            ui.icon("check_circle", size="20px").classes("text-positive mt-1")
            ui.label(datos["respuesta"]).classes("font-medium flex-1")
        if datos.get("interpretacion"):
            with ui.row().classes("items-start gap-2 w-full"):
                ui.icon("landscape", size="18px").classes("text-primary mt-1")
                ui.label(datos["interpretacion"]).classes("text-sm flex-1 lab-tenue")


def matriz_visual(filas: list[list[str]], nombre: str = "") -> None:
    """Una matriz entre paréntesis, con las columnas alineadas a la derecha.

    Una tabla de Quasar no sirve aquí: trae cabeceras, bordes de celda y
    paginación, y lo que se quiere es la matriz tal como se escribe a mano.
    """
    with ui.row().classes("items-center gap-2 no-wrap"):
        if nombre:
            ui.label(f"{nombre} =").classes("font-mono text-sm")
        columnas = len(filas[0]) if filas else 1
        with (
            ui.element("div")
            .classes("lab-matriz font-mono text-sm")
            .style(f"grid-template-columns: repeat({columnas}, auto)")
        ):
            for fila in filas:
                for valor in fila:
                    ui.label(valor)


def matriz_resuelta(datos: dict) -> None:
    """Dibuja una operación con matrices ya calculada por el backend.

    Mismo orden que `sistema_resuelto`: operandos, desarrollo y, al final, la
    respuesta. Una operación **no definida** se pinta como respuesta, no como
    error: saber cuándo no se puede operar es parte del temario.
    """
    with ui.column().classes("w-full gap-2"):
        with ui.row().classes("items-center gap-2 flex-wrap"):
            ui.badge(datos["nombre"].upper()).props(
                f"color={'primary' if datos['definida'] else 'negative'}"
            )
            ui.label(datos["notacion"]).classes("font-mono text-sm")
            if datos.get("invertible") is not None:
                ui.badge(
                    "ADMITE INVERSA" if datos["invertible"] else "SINGULAR"
                ).props(f"color={'positive' if datos['invertible'] else 'warning'}")

        with ui.row().classes("w-full gap-6 flex-wrap items-center"):
            for nombre, filas in datos["operandos"].items():
                with ui.column().classes("gap-1"):
                    matriz_visual(filas, nombre)
                    ui.label(_tipos_en_texto(datos, nombre)).classes("text-xs lab-tenue")
            for nombre, valor in datos.get("escalares", {}).items():
                ui.label(f"{nombre} = {valor}").classes("font-mono text-sm")

        with (
            ui.expansion("Desarrollo paso a paso", icon="functions", value=True).classes(
                "w-full lab-superficie"
            ),
            ui.column().classes("w-full gap-1 p-2"),
        ):
            for paso in datos["pasos"]:
                ui.label(paso).classes("font-mono text-sm leading-relaxed")

        with ui.row().classes("items-center gap-3 w-full flex-wrap"):
            icono, color = (
                ("check_circle", "text-positive") if datos["definida"]
                else ("block", "text-negative")
            )
            ui.icon(icono, size="20px").classes(f"{color}")
            if datos.get("resultado") is not None:
                matriz_visual(datos["resultado"], datos["notacion"])
            else:
                ui.label(datos["respuesta"]).classes("font-medium flex-1")


def _tipos_en_texto(datos: dict, nombre: str) -> str:
    """«2 × 3 · simétrica, cuadrada», o solo el orden si no es de ningún tipo."""
    tipos = datos.get("tipos", {}).get(nombre) or []
    orden = datos.get("ordenes", {}).get(nombre, "")
    return " · ".join(filter(None, [orden, ", ".join(tipos)]))


def diagrama_venn(sesion: Sesion, especificacion: dict, tema: Tema) -> None:
    """Descarga y muestra el diagrama; si falla, lo dice en vez de dejar un hueco.

    El tema viaja al backend para que la imagen se genere con el fondo de la
    paleta activa: un PNG blanco en mitad de una pantalla negra se ve como un
    foco encendido.
    """
    peticion = {**especificacion, "fondo": tema.lab_venn_fondo, "tinta": tema.lab_venn_texto}
    try:
        fuente = imagen_venn(sesion, peticion)
    except ErrorApi as error:
        ui.label(f"No se pudo generar el diagrama: {error}").classes("text-negative text-sm")
        return
    ui.image(fuente).classes("w-full max-w-xl rounded lab-superficie")


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
