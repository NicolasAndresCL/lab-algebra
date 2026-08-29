"""Repetición espaciada (variante de SM-2).

Cada repaso se califica de 0 a 5. A partir de la calificación se recalculan el
factor de facilidad, el intervalo y la fecha de la próxima revisión.

La regla que importa: **una calificación menor que 3 reinicia la serie**. Si no
se reiniciara, una tarjeta fallada volvería a aparecer dentro de semanas, que es
exactamente cuando ya no sirve de nada repasarla.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

CALIDAD_MINIMA = 0
CALIDAD_MAXIMA = 5
UMBRAL_ACIERTO = 3
FACTOR_MINIMO = 1.3
FACTOR_INICIAL = 2.5


@dataclass(frozen=True)
class EstadoRepaso:
    repeticiones: int
    factor_facilidad: float
    intervalo_dias: int
    proxima_revision: date

    @property
    def acertada(self) -> bool:
        return self.repeticiones > 0


def calcular(
    calidad: int,
    repeticiones: int,
    factor_facilidad: float,
    intervalo_dias: int,
    hoy: date | None = None,
) -> EstadoRepaso:
    """Devuelve el nuevo estado de repaso tras calificar una tarjeta."""
    if not CALIDAD_MINIMA <= calidad <= CALIDAD_MAXIMA:
        raise ValueError(
            f"La calidad debe estar entre {CALIDAD_MINIMA} y {CALIDAD_MAXIMA}; llegó {calidad}."
        )
    hoy = hoy or date.today()

    if calidad < UMBRAL_ACIERTO:
        # Fallo: vuelve al principio y se repasa hoy mismo.
        nuevas_repeticiones = 0
        nuevo_intervalo = 0
    else:
        nuevas_repeticiones = repeticiones + 1
        if nuevas_repeticiones == 1:
            nuevo_intervalo = 1
        elif nuevas_repeticiones == 2:
            nuevo_intervalo = 3
        else:
            nuevo_intervalo = max(1, round(intervalo_dias * factor_facilidad))

    # Ajuste del factor de facilidad (fórmula de SM-2), con suelo en 1.3 para
    # que una tarjeta difícil no acabe repitiéndose cada pocos minutos.
    ajuste = 0.1 - (5 - calidad) * (0.08 + (5 - calidad) * 0.02)
    nuevo_factor = max(FACTOR_MINIMO, factor_facilidad + ajuste)

    return EstadoRepaso(
        repeticiones=nuevas_repeticiones,
        factor_facilidad=round(nuevo_factor, 3),
        intervalo_dias=nuevo_intervalo,
        proxima_revision=hoy + timedelta(days=nuevo_intervalo),
    )


def estado_inicial(hoy: date | None = None) -> EstadoRepaso:
    """Estado de una tarjeta nunca repasada: toca hoy."""
    hoy = hoy or date.today()
    return EstadoRepaso(
        repeticiones=0,
        factor_facilidad=FACTOR_INICIAL,
        intervalo_dias=0,
        proxima_revision=hoy,
    )
