"""Color ilustrativo de la temperatura, de acero frío (20 °C) a naranja (1 000 °C).

Es la rampa de la app «Planta completa» (simulador-procesos), extendida por debajo de ~500 °C a
tonos de acero frío y reajustada para que la luminosidad crezca siempre con la temperatura. Fuera
del rango se satura. Es una rampa ILUSTRATIVA (no es la emisión real del cuerpo negro), y así se
rotula en el esquema.
"""

from __future__ import annotations

import itertools

NOTE = "color ilustrativo de la temperatura"
STOPS = (
    (20.0, (20, 30, 42)),  # acero frío
    (250.0, (30, 38, 50)),
    (450.0, (78, 40, 34)),  # empieza a verse rojo oscuro
    (600.0, (128, 38, 26)),
    (720.0, (172, 52, 24)),
    (800.0, (205, 66, 22)),
    (875.0, (232, 98, 30)),  # temperatura de austenización del ejemplo
    (1000.0, (245, 140, 40)),
)


def temperature_rgb_float(temp_c: float) -> tuple[float, float, float]:
    """Interpolación lineal entre las paradas, sin redondear."""
    t = min(max(temp_c, STOPS[0][0]), STOPS[-1][0])
    for (t0, c0), (t1, c1) in itertools.pairwise(STOPS):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            r, g, b = (a + (b_ - a) * f for a, b_ in zip(c0, c1, strict=True))
            return r, g, b
    r, g, b = STOPS[-1][1]
    return float(r), float(g), float(b)


def temperature_rgb(temp_c: float) -> tuple[int, int, int]:
    r, g, b = temperature_rgb_float(temp_c)
    return round(r), round(g), round(b)


def temperature_color(temp_c: float) -> str:
    return "#{:02X}{:02X}{:02X}".format(*temperature_rgb(temp_c))


def luminance(rgb: tuple[float, ...]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
