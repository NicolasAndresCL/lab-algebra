"""Temas de la interfaz.

Tres paletas oscuras y una clara. El cambio de tema es **instantáneo y sin
recargar**: todo el color vive en variables CSS que se escriben sobre `body`,
así que cambiar de paleta es reescribir un puñado de propiedades, no reconstruir
la página.

Por qué variables CSS y no clases de Tailwind
---------------------------------------------
La versión anterior usaba clases fijas (`text-gray-500`, `bg-gray-50`,
`dark:bg-gray-800`). Eso tiene dos problemas:

1. Con tres paletas oscuras distintas, un `bg-gray-800` fijo pertenece a una y
   desentona en las otras dos.
2. Las variantes `dark:` de Tailwind responden a `prefers-color-scheme`, es
   decir, al tema del **sistema operativo** — no al que el usuario elija aquí.
   Con el sistema en claro no se aplicaban nunca.

Se sobreescriben también las variables de marca de Quasar (`--q-primary`,
`--q-dark`, …), que es lo que usan por dentro los botones, los campos y las
tablas. Así el tema alcanza a los componentes que no se estilan a mano.
"""

from __future__ import annotations

from dataclasses import dataclass

from nicegui import app, ui

CLAVE_TEMA = "tema"


@dataclass(frozen=True)
class Tema:
    """Una paleta completa.

    Los campos `q_*` son los colores de marca de Quasar; los `lab_*`, las
    superficies y los textos propios de esta aplicación.
    """

    clave: str
    nombre: str
    descripcion: str
    icono: str
    oscuro: bool

    # --- marca (Quasar) -------------------------------------------------
    q_primary: str
    q_secondary: str
    q_accent: str
    q_positive: str
    q_negative: str
    q_warning: str
    q_info: str
    q_dark: str
    q_dark_page: str

    # --- superficies y texto (propios) ----------------------------------
    lab_fondo: str
    lab_superficie: str
    lab_superficie_alta: str
    lab_borde: str
    lab_texto: str
    lab_texto_tenue: str
    lab_cabecera: str
    lab_cabecera_texto: str
    # Fondo de los diagramas de Venn que genera el backend, para que la imagen
    # no aparezca como un recuadro luminoso en mitad de una pantalla negra.
    lab_venn_fondo: str
    lab_venn_texto: str

    def variables_css(self) -> str:
        """Las variables de este tema, listas para escribir en `body`."""
        pares = {
            "--q-primary": self.q_primary,
            "--q-secondary": self.q_secondary,
            "--q-accent": self.q_accent,
            "--q-positive": self.q_positive,
            "--q-negative": self.q_negative,
            "--q-warning": self.q_warning,
            "--q-info": self.q_info,
            "--q-dark": self.q_dark,
            "--q-dark-page": self.q_dark_page,
            "--lab-fondo": self.lab_fondo,
            "--lab-superficie": self.lab_superficie,
            "--lab-superficie-alta": self.lab_superficie_alta,
            "--lab-borde": self.lab_borde,
            "--lab-texto": self.lab_texto,
            "--lab-texto-tenue": self.lab_texto_tenue,
            "--lab-cabecera": self.lab_cabecera,
            "--lab-cabecera-texto": self.lab_cabecera_texto,
        }
        return "; ".join(f"{nombre}: {valor}" for nombre, valor in pares.items())

    @property
    def muestra(self) -> tuple[str, str, str]:
        """Tres colores representativos, para la miniatura del selector."""
        return (self.lab_fondo, self.lab_superficie_alta, self.q_primary)


# --------------------------------------------------------------------------
# Las paletas
# --------------------------------------------------------------------------
ONIX = Tema(
    clave="onix",
    nombre="Ónix",
    descripcion="Negro puro, para pantallas OLED y para estudiar de noche",
    icono="dark_mode",
    oscuro=True,
    # Negro absoluto en el fondo y azul eléctrico como único acento fuerte:
    # con el fondo a #000 cualquier color saturado destaca solo, así que la
    # paleta se mantiene deliberadamente corta.
    q_primary="#4c8dff",
    q_secondary="#22d3ee",
    q_accent="#a855f7",
    q_positive="#22c55e",
    q_negative="#f43f5e",
    q_warning="#eab308",
    q_info="#38bdf8",
    q_dark="#0b0b0d",
    q_dark_page="#000000",
    lab_fondo="#000000",
    lab_superficie="#0b0b0d",
    lab_superficie_alta="#141418",
    lab_borde="#26262d",
    lab_texto="#f4f4f5",
    lab_texto_tenue="#9b9ba5",
    lab_cabecera="#0b0b0d",
    lab_cabecera_texto="#f4f4f5",
    lab_venn_fondo="#0b0b0d",
    lab_venn_texto="#f4f4f5",
)

MEDIANOCHE = Tema(
    clave="medianoche",
    nombre="Medianoche",
    descripcion="Azul profundo, menos contraste y más descansado en sesiones largas",
    icono="bedtime",
    oscuro=True,
    # El azul del fondo baja el contraste respecto al negro puro: cansa menos
    # cuando la sesión de repaso dura media hora.
    q_primary="#38bdf8",
    q_secondary="#2dd4bf",
    q_accent="#c084fc",
    q_positive="#34d399",
    q_negative="#fb7185",
    q_warning="#fbbf24",
    q_info="#60a5fa",
    q_dark="#111c31",
    q_dark_page="#0a1120",
    lab_fondo="#0a1120",
    lab_superficie="#111c31",
    lab_superficie_alta="#18243d",
    lab_borde="#26375a",
    lab_texto="#e6edf8",
    lab_texto_tenue="#93a4c3",
    lab_cabecera="#111c31",
    lab_cabecera_texto="#e6edf8",
    lab_venn_fondo="#111c31",
    lab_venn_texto="#e6edf8",
)

CARBON = Tema(
    clave="carbon",
    nombre="Carbón",
    descripcion="Gris cálido y ámbar, el más suave con la vista bajo luz artificial",
    icono="local_fire_department",
    oscuro=True,
    # Grises cálidos en vez de neutros: bajo una bombilla, un gris azulado se
    # ve «sucio» y este no.
    q_primary="#e3a13c",
    q_secondary="#a3a380",
    q_accent="#f472b6",
    q_positive="#84cc16",
    q_negative="#ef4444",
    q_warning="#f59e0b",
    q_info="#38bdf8",
    q_dark="#1d1a16",
    q_dark_page="#14120f",
    lab_fondo="#14120f",
    lab_superficie="#1d1a16",
    lab_superficie_alta="#26221c",
    lab_borde="#3a352c",
    lab_texto="#f5f0e8",
    lab_texto_tenue="#a8a094",
    lab_cabecera="#1d1a16",
    lab_cabecera_texto="#f5f0e8",
    lab_venn_fondo="#1d1a16",
    lab_venn_texto="#f5f0e8",
)

PAPEL = Tema(
    clave="papel",
    nombre="Papel",
    descripcion="Claro, para repasar con luz de día o proyectar en clase",
    icono="light_mode",
    oscuro=False,
    q_primary="#2563eb",
    q_secondary="#0d9488",
    q_accent="#7c3aed",
    q_positive="#16a34a",
    q_negative="#dc2626",
    q_warning="#d97706",
    q_info="#0284c7",
    q_dark="#1d1d1d",
    q_dark_page="#121212",
    lab_fondo="#f4f5f7",
    lab_superficie="#ffffff",
    lab_superficie_alta="#eef0f4",
    lab_borde="#d4d8e0",
    lab_texto="#111827",
    lab_texto_tenue="#5b6472",
    # La cabecera es una superficie más, no una banda de color: los botones de
    # navegación son `flat` y Quasar los pinta con el color primario, así que
    # una cabecera azul los volvía azul sobre azul — invisibles.
    lab_cabecera="#ffffff",
    lab_cabecera_texto="#111827",
    lab_venn_fondo="#ffffff",
    lab_venn_texto="#111827",
)

TEMAS: dict[str, Tema] = {t.clave: t for t in (ONIX, MEDIANOCHE, CARBON, PAPEL)}
TEMA_POR_DEFECTO = ONIX


# --------------------------------------------------------------------------
# Hoja de estilo base
# --------------------------------------------------------------------------
# Consume las variables; nunca declara un color literal. Cambiar de tema es
# reescribir las variables, no esta hoja.
CSS_BASE = """
body {
    background: var(--lab-fondo);
    color: var(--lab-texto);
    transition: background-color .25s ease, color .25s ease;
}
.q-page, .nicegui-content, .q-page-container { background: transparent; }

.lab-superficie {
    background: var(--lab-superficie);
    border: 1px solid var(--lab-borde);
}
.lab-superficie-alta { background: var(--lab-superficie-alta); }
.lab-borde { border-color: var(--lab-borde) !important; }
.lab-texto { color: var(--lab-texto); }
.lab-tenue { color: var(--lab-texto-tenue); }

.lab-cabecera {
    background: var(--lab-cabecera) !important;
    color: var(--lab-cabecera-texto);
    border-bottom: 1px solid var(--lab-borde);
    box-shadow: none;
}
/* Solo el rótulo y el nombre del usuario toman el color de la cabecera; los
   botones se quedan con el primario, que es lo que los hace localizables. */
.lab-cabecera > div > .q-label,
.lab-cabecera .lab-rotulo { color: var(--lab-cabecera-texto); }

/* Las tarjetas de Quasar traen su propio fondo; se neutraliza para que sigan
   la superficie del tema en vez de imponer el gris del modo oscuro. */
.q-card.lab-superficie { box-shadow: none; }

.lab-codigo {
    background: var(--lab-superficie-alta);
    border: 1px solid var(--lab-borde);
    border-radius: .375rem;
}

/* La tabla de verdad hereda del tema: sin esto, en modo oscuro Quasar la
   pinta con su propio gris y queda como un parche. */
.lab-tabla .q-table__container,
.lab-tabla .q-table thead th,
.lab-tabla .q-table tbody td { background: transparent; color: var(--lab-texto); }
.lab-tabla .q-table thead th { color: var(--lab-texto-tenue); font-weight: 600; }
.lab-tabla .q-table tbody tr:nth-child(even) { background: var(--lab-superficie-alta); }
.lab-tabla .q-table--bordered { border-color: var(--lab-borde); }

/* Una matriz como se escribe en el cuaderno: rejilla de números alineados a
   la derecha entre dos bordes laterales redondeados, que hacen de paréntesis.
   El número de columnas lo fija `grid-template-columns` en línea, porque
   depende de cada matriz. */
.lab-matriz {
    display: inline-grid;
    gap: .15rem 1rem;
    padding: .2rem .6rem;
    border-left: 2px solid var(--lab-texto-tenue);
    border-right: 2px solid var(--lab-texto-tenue);
    border-radius: .5rem;
}
.lab-matriz > * { text-align: right; }

/* La muestra de color del selector de tema. `display: block` no es opcional:
   un <span> es inline y descarta width y height, así que la muestra salía
   como una rayita de un píxel. */
.lab-muestra {
    display: block;
    width: 2.8rem; height: 1.4rem; border-radius: .3rem;
    border: 1px solid rgba(128, 128, 128, .5);
}
"""


# --------------------------------------------------------------------------
# Aplicación y persistencia
# --------------------------------------------------------------------------
def tema_guardado() -> Tema:
    """El tema elegido por este usuario, o el de por defecto."""
    return TEMAS.get(app.storage.user.get(CLAVE_TEMA, ""), TEMA_POR_DEFECTO)


def guardar_tema(tema: Tema) -> None:
    app.storage.user[CLAVE_TEMA] = tema.clave


class GestorTema:
    """Aplica un tema a la página actual y permite cambiarlo en caliente.

    Se instancia **una vez por página**. El elemento `ui.dark_mode` se conserva
    para poder mover su `value`: recrearlo en cada cambio dejaría elementos
    huérfanos acumulándose en el DOM.
    """

    def __init__(self) -> None:
        ui.add_css(CSS_BASE)
        self._tema = tema_guardado()
        self._modo_oscuro = ui.dark_mode(self._tema.oscuro)
        # `ui.colors` se llama una sola vez, para que Quasar genere sus clases
        # de utilidad (.text-primary, .bg-positive…). A partir de ahí el color
        # vivo lo llevan las variables CSS.
        ui.colors(
            primary=self._tema.q_primary,
            secondary=self._tema.q_secondary,
            accent=self._tema.q_accent,
            positive=self._tema.q_positive,
            negative=self._tema.q_negative,
            warning=self._tema.q_warning,
            info=self._tema.q_info,
            dark=self._tema.q_dark,
            dark_page=self._tema.q_dark_page,
        )
        self._aplicar_variables()

    @property
    def tema(self) -> Tema:
        return self._tema

    def _aplicar_variables(self) -> None:
        ui.query("body").style(self._tema.variables_css())

    def cambiar(self, tema: Tema) -> None:
        """Cambia el tema, lo persiste y lo aplica sin recargar la página."""
        self._tema = tema
        guardar_tema(tema)
        self._modo_oscuro.value = tema.oscuro
        self._aplicar_variables()
