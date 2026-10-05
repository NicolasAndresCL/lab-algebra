"""Laboratorio de cálculo: lógica, conjuntos, Venn, ecuaciones y matrices."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from itertools import product

from nicegui import ui

from app.api import (
    ErrorApi,
    Sesion,
    equivalencia,
    imagen_venn,
    operaciones_matrices,
    operar_conjuntos,
    operar_matrices,
    regiones_venn,
    resolver_sistema,
    tabla_de_verdad,
)
from app.componentes import (
    cabecera,
    campo_formula,
    matriz_resuelta,
    sistema_resuelto,
    titulo_pagina,
)
from app.componentes import tabla_de_verdad as pintar_tabla
from app.estado import exigir_sesion
from app.temas import Tema


@dataclass(frozen=True)
class Pestana:
    """Una herramienta: su clave, cómo se rotula y quién pinta su panel."""

    clave: str
    etiqueta: str
    icono: str
    pintar: Callable[[Sesion, Tema], None]


# Las herramientas, en el orden de las unidades. Una herramienta nueva es una
# entrada más aquí; la página no tiene que saber cuántas hay. Las funciones de
# panel se definen más abajo: las lambdas las resuelven al pintar, no al cargar.
PESTANAS: tuple[Pestana, ...] = (
    Pestana("tabla", "Tabla de verdad", "table_chart", lambda s, _: _panel_tabla(s)),
    Pestana("equivalencia", "Equivalencia", "compare_arrows",
            lambda s, _: _panel_equivalencia(s)),
    Pestana("conjuntos", "Conjuntos", "join_inner", lambda s, _: _panel_conjuntos(s)),
    Pestana("venn", "Diagrama de Venn", "pie_chart", lambda s, tema: _panel_venn(s, tema)),
    Pestana("ecuaciones", "Sistemas de ecuaciones", "grid_on",
            lambda s, _: _panel_ecuaciones(s)),
    Pestana("matrices", "Matrices", "apps", lambda s, _: _panel_matrices(s)),
)


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
            for pestana in PESTANAS:
                ui.tab(pestana.clave, label=pestana.etiqueta, icon=pestana.icono)
        with ui.tab_panels(pestanas, value=PESTANAS[0].clave).classes("w-full"):
            for pestana in PESTANAS:
                with ui.tab_panel(pestana.clave):
                    pestana.pintar(sesion, gestor.tema)


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


# Los métodos que enseña la asignatura: los tres de la unidad de ecuaciones y
# la regla de Cramer de la de matrices, que solo se enseñó para 2 × 2. No hay
# Cramer de orden 3, ni matriz inversa, ni rangos: no se vieron en clase.
METODOS = ["reducción", "sustitución", "igualación", "Cramer"]

# La rejilla tiene siempre cuatro columnas —a, b, c y término— y en 2 × 2 se
# oculta la de c. El término independiente va por tanto en el índice 3, no en
# el 2: armar la matriz leyendo «las primeras n+1 columnas» mandaría el
# coeficiente de z como término independiente.
COLUMNA_TERMINO = 3

# Ejemplos de arranque, para que la pestaña se abra mostrando algo correcto en
# vez de un formulario vacío: el problema 1 de la lámina 14 (x + y = 3 ;
# x + 2y = −8) y el sistema 1 de la lámina 4 del PDF de 3 × 3. Cada uno ocupa
# la rejilla completa, así que al cambiar de orden se carga el que toca — y se
# pierde lo que hubiera escrito: son dos ejercicios distintos, no el mismo con
# una fila más.
EJEMPLOS: dict[int, list[list[str]]] = {
    2: [
        ["1", "1", "0", "3"],
        ["1", "2", "0", "-8"],
        ["", "", "", ""],
    ],
    3: [
        ["1", "1", "-1", "-1"],
        ["4", "-3", "2", "16"],
        ["2", "-2", "-3", "5"],
    ],
}


def _panel_ecuaciones(sesion: Sesion) -> None:
    resultado: ui.column

    def leer(campo: ui.input) -> str:
        """Un hueco vacío es un coeficiente 0, no un error de escritura."""
        return (campo.value or "").strip() or "0"

    def calcular() -> None:
        resultado.clear()
        orden = 3 if tres.value else 2
        columnas = [*range(orden), COLUMNA_TERMINO]
        matriz = [[leer(campos[f][c]) for c in columnas] for f in range(orden)]
        nombres = [
            (campo.value or "").strip() or defecto
            for campo, defecto in zip(
                nombres_campos[:orden], ("x", "y", "z")[:orden], strict=True
            )
        ]
        try:
            datos = resolver_sistema(sesion, matriz, nombres, metodo.value)
        except ErrorApi as error:
            with resultado:
                _mostrar_error(error, "")
            return
        with resultado:
            sistema_resuelto(datos)

    ui.markdown(
        "Escribe los **coeficientes**, no las ecuaciones. Se admiten fracciones "
        "(`1/2`, `-19/2`): el motor trabaja con aritmética exacta, así que 1/3 sale "
        "como 1/3 y nunca como 0,333. Un hueco vacío cuenta como coeficiente 0. "
        "Cambiar entre 2 × 2 y 3 × 3 **carga el ejemplo de la lámina** correspondiente."
    ).classes("text-sm lab-tenue")

    tres = ui.switch("Tres ecuaciones (3 × 3)", value=False, on_change=lambda: alternar())

    nombres_campos: list[ui.input] = []
    with ui.row().classes("w-full gap-2 flex-wrap items-end"):
        for defecto in ("x", "y", "z"):
            nombres_campos.append(
                ui.input(f"Nombre de «{defecto}»", value=defecto)
                .props("outlined dense")
                .classes("flex-1 min-w-[6rem]")
            )

    campos: list[list[ui.input]] = []
    filas_ui: list[ui.row] = []
    for numero in range(3):
        with ui.row().classes("w-full gap-2 flex-wrap items-center") as fila_ui:
            ui.label(f"({numero + 1})").classes("font-mono w-8 lab-tenue")
            fila = [
                ui.input(etiqueta, value=EJEMPLOS[2][numero][columna])
                .props("outlined dense")
                .classes("flex-1 min-w-[4.5rem]")
                for columna, etiqueta in enumerate(("a", "b", "c", "término"))
            ]
            for campo in fila:
                campo.on("keydown.enter", calcular)
            campos.append(fila)
        filas_ui.append(fila_ui)

    metodo = (
        ui.select(METODOS, value="reducción", label="Método del desarrollo")
        .props("outlined dense")
        .classes("w-full sm:w-72")
    )
    aviso_metodo = ui.label(
        "En 3 × 3 el desarrollo va por reducción (eliminación de Gauss-Jordan), "
        "que es el método sistemático."
    ).classes("text-xs lab-tenue")

    def alternar() -> None:
        """Muestra u oculta la tercera incógnita y la tercera ecuación."""
        hay_tres = bool(tres.value)
        nombres_campos[2].set_visibility(hay_tres)
        filas_ui[2].set_visibility(hay_tres)
        for fila in campos:
            fila[2].set_visibility(hay_tres)
        ejemplo = EJEMPLOS[3 if hay_tres else 2]
        for numero, fila in enumerate(campos):
            for columna, campo in enumerate(fila):
                campo.set_value(ejemplo[numero][columna])
        if hay_tres:
            metodo.set_value("reducción")
        metodo.set_enabled(not hay_tres)
        aviso_metodo.set_visibility(hay_tres)
        calcular()

    ui.button("Resolver", icon="play_arrow", on_click=calcular).props("no-caps")
    resultado = ui.column().classes("w-full gap-2")
    alternar()


# --------------------------------------------------------------------------
# Matrices y determinantes
# --------------------------------------------------------------------------
DIMENSIONES = [1, 2, 3, 4]
"""Hasta 4 × 4, el mismo tope que `DIMENSION_MAXIMA` del backend."""


class EditorMatriz:
    """Rejilla de 4 × 4 campos de la que solo se muestran filas × columnas.

    Los dieciséis campos se crean una vez y se ocultan o muestran al cambiar
    el orden: recrearlos en cada cambio perdería lo que ya estaba escrito en
    las casillas que siguen visibles. Es una instancia por página, no estado
    de módulo: dos personas con la pestaña abierta no comparten matrices.
    """

    def __init__(self, nombre: str, al_confirmar: Callable[[], None]) -> None:
        with ui.column().classes("gap-1") as self.contenedor:
            with ui.row().classes("items-center gap-2 no-wrap"):
                ui.label(nombre).classes("font-mono font-semibold w-5")
                self.filas = (
                    ui.select(DIMENSIONES, value=2, label="filas",
                              on_change=self._mostrar_orden)
                    .props("outlined dense").classes("w-20")
                )
                ui.label("×").classes("lab-tenue")
                self.columnas = (
                    ui.select(DIMENSIONES, value=2, label="columnas",
                              on_change=self._mostrar_orden)
                    .props("outlined dense").classes("w-28")
                )
            self.renglones: list[ui.row] = []
            self.campos: list[list[ui.input]] = []
            for _ in DIMENSIONES:
                with ui.row().classes("gap-1 no-wrap") as renglon:
                    celdas = [
                        ui.input(value="0").props("outlined dense input-class=text-right")
                        .classes("w-16")
                        for _ in DIMENSIONES
                    ]
                for celda in celdas:
                    celda.on("keydown.enter", al_confirmar)
                self.renglones.append(renglon)
                self.campos.append(celdas)
        self._mostrar_orden()

    def _mostrar_orden(self) -> None:
        m, n = self.filas.value, self.columnas.value
        for i, renglon in enumerate(self.renglones):
            renglon.set_visibility(i < m)
            for j, celda in enumerate(self.campos[i]):
                celda.set_visibility(j < n)

    def cargar(self, valores: list[list]) -> None:
        """Pone una matriz del catálogo: ajusta el orden y rellena con ceros el resto."""
        m, n = len(valores), len(valores[0])
        self.filas.set_value(m)
        self.columnas.set_value(n)
        for i, j in product(range(len(DIMENSIONES)), repeat=2):
            self.campos[i][j].set_value(str(valores[i][j]) if i < m and j < n else "0")
        self._mostrar_orden()

    def leer(self) -> list[list[str]]:
        """Las entradas visibles como texto; un hueco vacío cuenta como 0."""
        m, n = self.filas.value, self.columnas.value
        return [[(self.campos[i][j].value or "").strip() or "0" for j in range(n)]
                for i in range(m)]


def _panel_matrices(sesion: Sesion) -> None:
    resultado: ui.column
    try:
        catalogo = {op["clave"]: op for op in operaciones_matrices(sesion)}
    except ErrorApi as error:
        _mostrar_error(error, "")
        return

    def calcular() -> None:
        resultado.clear()
        elegida = catalogo[operacion.value]
        datos: dict = {"operacion": elegida["clave"], "a": editor_a.leer()}
        if elegida["usa_b"]:
            datos["b"] = editor_b.leer()
        for nombre in elegida["escalares"]:
            datos[nombre] = (escalares[nombre].value or "").strip() or "0"
        try:
            respuesta = operar_matrices(sesion, datos)
        except ErrorApi as error:
            with resultado:
                _mostrar_error(error, "")
            return
        with resultado:
            matriz_resuelta(respuesta)

    def cargar_ejemplo() -> None:
        """Cada operación abre con su ejercicio de la lámina, como la de ecuaciones."""
        elegida = catalogo[operacion.value]
        ejemplo = elegida["ejemplo"]
        editor_a.cargar(ejemplo["a"])
        if "b" in ejemplo:
            editor_b.cargar(ejemplo["b"])
        editor_b.contenedor.set_visibility(elegida["usa_b"])
        for nombre, campo in escalares.items():
            campo.set_visibility(nombre in elegida["escalares"])
            if nombre in ejemplo:
                campo.set_value(str(ejemplo[nombre]))
        fuente.set_text(f"Ejemplo: {elegida['fuente']}.")
        calcular()

    ui.markdown(
        "Elige la operación y escribe las matrices. Se admiten fracciones (`1/2`, "
        "`-3/4`): el motor trabaja con aritmética exacta. Si la operación **no está "
        "definida** para esos órdenes, la respuesta lo dice y explica por qué. "
        "Cambiar de operación **carga el ejemplo de la lámina**."
    ).classes("text-sm lab-tenue")
    operacion = (
        ui.select(
            {clave: f"{op['nombre']}  ·  {op['notacion']}" for clave, op in catalogo.items()},
            value="producto" if "producto" in catalogo else next(iter(catalogo)),
            label="Operación",
            on_change=lambda: cargar_ejemplo(),
        )
        .props("outlined dense")
        .classes("w-full sm:w-96")
    )
    fuente = ui.label("").classes("text-xs lab-tenue")
    with ui.row().classes("w-full gap-8 flex-wrap items-start"):
        editor_a = EditorMatriz("A", calcular)
        editor_b = EditorMatriz("B", calcular)
    with ui.row().classes("gap-2"):
        escalares = {
            nombre: ui.input(nombre, value="1").props("outlined dense").classes("w-24")
            for nombre in ("k", "m")
        }
    for campo in escalares.values():
        campo.on("keydown.enter", calcular)
    ui.button("Calcular", icon="play_arrow", on_click=calcular).props("no-caps")
    resultado = ui.column().classes("w-full gap-2")
    cargar_ejemplo()


def _mostrar_error(error: ErrorApi, contexto: str) -> None:
    """Muestra el error con la pista de posición cuando la API la devuelve."""
    ui.label(str(error)).classes("text-negative font-medium")
    posicion = error.detalle.get("posicion")
    if posicion is not None and contexto:
        ui.label(contexto).classes("font-mono text-sm")
        ui.label(" " * int(posicion) + "▲").classes("font-mono text-sm text-negative")
