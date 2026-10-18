"""Tamaño máximo nominal dN (el d95 de Gy) desde la especificación de un protocolo.

Un laboratorio especifica «70 % bajo 2 mm» o «85 % bajo 75 µm»: un punto de la curva. Se completa
con una forma Rosin-Rammler, P(x) = 1 − exp(−(x/x63)^m), cuya pendiente m es un SUPUESTO declarado
(no sale de ningún dato del protocolo). Como dN entra al cubo en la varianza, el error depende de m:
`muestreo.protocolo.sensibilidad_a_m` lo muestra. La curva se arma con `conminucion.sizes`
(simulador-conminucion, fijado a un commit).
"""

from __future__ import annotations

import math

import numpy as np
from conminucion.sizes import SizeGrid, cumulative_passing, rosin_rammler, size_at_passing

from .gy import GyError

MM_TO_CM = 0.1
UM_TO_CM = 1e-4
NOMINAL_PASSING = 0.95  # dN = d95
SLOPE_RANGE = (0.3, 4.0)  # m razonable para productos de chancado y pulverizado


def _check(pct: float, size: float, m: float) -> None:
    if not 0 < pct < 100:
        raise GyError(f"el porcentaje pasante debe estar entre 0 y 100: {pct}")
    if not (math.isfinite(size) and size > 0):
        raise GyError(f"el tamaño debe ser positivo y finito: {size}")
    if not SLOPE_RANGE[0] <= m <= SLOPE_RANGE[1]:
        raise GyError(f"la pendiente m debe estar entre {SLOPE_RANGE[0]} y {SLOPE_RANGE[1]}: {m}")


def x63_from_spec(pct: float, size: float, m: float) -> float:
    """Tamaño al que pasa el 63,2 %, dado que el `pct` % pasa `size` (mismas unidades)."""
    _check(pct, size, m)
    return size / (-math.log(1.0 - pct / 100.0)) ** (1.0 / m)


def size_at(x63: float, m: float, passing: float) -> float:
    """Tamaño al que pasa la fracción `passing` de una curva Rosin-Rammler."""
    return x63 * (-math.log(1.0 - passing)) ** (1.0 / m)


def d95_cm(pct: float, size_cm: float, m: float) -> float:
    """dN (cm): tamaño al que pasa el 95 %, con la especificación `pct` % bajo `size_cm`."""
    return size_at(x63_from_spec(pct, size_cm, m), m, NOMINAL_PASSING)


def d95_from_mm(pct: float, size_mm: float, m: float) -> float:
    return d95_cm(pct, size_mm * MM_TO_CM, m)


def d95_from_um(pct: float, size_um: float, m: float) -> float:
    return d95_cm(pct, size_um * UM_TO_CM, m)


def curve(pct: float, size_um: float, m: float, points: int = 60) -> tuple[np.ndarray, np.ndarray]:
    """(tamices en µm, % pasante) de la curva de la especificación, armada con la rejilla y
    `rosin_rammler` de conminucion. La rejilla llega a 20 veces el d95."""
    x63 = x63_from_spec(pct, size_um, m)
    top = 20.0 * size_at(x63, m, NOMINAL_PASSING)
    ratio = (top / (x63 * 1e-3)) ** (1.0 / (points - 1))
    grid = SizeGrid.geometric(top, points, ratio)
    fractions = rosin_rammler(grid, x63, m)
    return grid.sieves, 100.0 * cumulative_passing(fractions)


def d95_from_curve(pct: float, size_um: float, m: float, points: int = 400) -> float:
    """El d95 (µm) leído en la curva de conminucion: control independiente de `d95_cm`."""
    x63 = x63_from_spec(pct, size_um, m)
    top = 20.0 * size_at(x63, m, NOMINAL_PASSING)
    ratio = (top / (x63 * 1e-3)) ** (1.0 / (points - 1))
    grid = SizeGrid.geometric(top, points, ratio)
    fractions = rosin_rammler(grid, x63, m)
    return size_at_passing(grid, fractions, NOMINAL_PASSING)
