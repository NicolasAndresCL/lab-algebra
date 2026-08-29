"""Generación de diagramas de Venn como PNG.

Se usa matplotlib con el backend **Agg**, elegido antes de importar `pyplot`:
dentro de un contenedor no hay servidor gráfico, y el backend interactivo por
defecto revienta al crear la figura.

Cada figura se cierra explícitamente (`plt.close`). Sin eso, un servidor que
atiende miles de peticiones acumula figuras en memoria hasta caerse — matplotlib
mantiene una referencia global a cada figura abierta.
"""

from __future__ import annotations

import io
import json
from functools import lru_cache

import matplotlib

matplotlib.use("Agg")  # antes de importar pyplot: sin display en el contenedor

import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3

from app.services.conjuntos import EspecificacionVenn, RegionesDos, RegionesTres

_COLORES = ("#1f6feb", "#d97706", "#15803d")
_FONDO = "#ffffff"


def _dibujar_dos(regiones: RegionesDos, titulo: str) -> bytes:
    figura, ejes = plt.subplots(figsize=(6.0, 4.2), dpi=140)
    try:
        diagrama = venn2(
            subsets=(regiones.solo_a, regiones.solo_b, regiones.ambos),
            set_labels=regiones.etiquetas,
            set_colors=_COLORES[:2],
            alpha=0.45,
            ax=ejes,
        )
        for etiqueta in diagrama.set_labels or []:
            if etiqueta is not None:
                etiqueta.set_fontsize(13)
                etiqueta.set_fontweight("bold")
        for etiqueta in diagrama.subset_labels or []:
            if etiqueta is not None:
                etiqueta.set_fontsize(12)

        if regiones.ninguno:
            # Los que no están en ningún conjunto viven fuera de los círculos,
            # dentro del rectángulo del universo: hay que dibujarlos aparte.
            ejes.text(
                0.97, 0.03, f"Fuera: {regiones.ninguno}",
                transform=ejes.transAxes, ha="right", va="bottom", fontsize=11,
            )
        if titulo:
            ejes.set_title(titulo, fontsize=12, pad=12)
        _marco_universo(ejes)
        return _a_png(figura)
    finally:
        plt.close(figura)


def _dibujar_tres(regiones: RegionesTres, titulo: str) -> bytes:
    figura, ejes = plt.subplots(figsize=(6.4, 5.0), dpi=140)
    try:
        # El orden que espera venn3 es (Abc, aBc, ABc, abC, AbC, aBC, ABC).
        diagrama = venn3(
            subsets=(
                regiones.solo_a, regiones.solo_b, regiones.ab,
                regiones.solo_c, regiones.ac, regiones.bc, regiones.abc,
            ),
            set_labels=regiones.etiquetas,
            set_colors=_COLORES,
            alpha=0.42,
            ax=ejes,
        )
        for etiqueta in diagrama.set_labels or []:
            if etiqueta is not None:
                etiqueta.set_fontsize(13)
                etiqueta.set_fontweight("bold")
        for etiqueta in diagrama.subset_labels or []:
            if etiqueta is not None:
                etiqueta.set_fontsize(11)

        if regiones.ninguno:
            ejes.text(
                0.97, 0.03, f"Fuera: {regiones.ninguno}",
                transform=ejes.transAxes, ha="right", va="bottom", fontsize=11,
            )
        if titulo:
            ejes.set_title(titulo, fontsize=12, pad=12)
        _marco_universo(ejes)
        return _a_png(figura)
    finally:
        plt.close(figura)


def _marco_universo(ejes) -> None:
    """Dibuja el rectángulo del conjunto universal alrededor de los círculos."""
    for lado in ejes.spines.values():
        lado.set_visible(True)
        lado.set_color("#334155")
        lado.set_linewidth(1.2)
    ejes.set_xticks([])
    ejes.set_yticks([])


def _a_png(figura) -> bytes:
    buffer = io.BytesIO()
    figura.savefig(buffer, format="png", bbox_inches="tight", facecolor=_FONDO)
    return buffer.getvalue()


def generar_png(especificacion: dict) -> bytes:
    """Genera el PNG de un diagrama a partir de su especificación."""
    spec = EspecificacionVenn.desde_dict(especificacion)
    regiones = spec.resolver_regiones()
    if isinstance(regiones, RegionesDos):
        return _dibujar_dos(regiones, spec.titulo)
    return _dibujar_tres(regiones, spec.titulo)


@lru_cache(maxsize=128)
def _generar_cacheado(especificacion_json: str) -> bytes:
    return generar_png(json.loads(especificacion_json))


def generar_png_cacheado(especificacion: dict) -> bytes:
    """Igual que `generar_png`, memorizando por especificación.

    Las tarjetas semilla piden siempre el mismo diagrama; dibujarlo una vez y
    servir los bytes evita ~150 ms de matplotlib en cada repaso.
    """
    return _generar_cacheado(json.dumps(especificacion, sort_keys=True, ensure_ascii=False))
