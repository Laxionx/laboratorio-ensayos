"""Cifras publicadas del control de calidad (solo cifras y reglas, nunca el texto ni los PDF de
las fuentes) y los ejemplos sintéticos de la pestaña.

- **CDN-GS-2X** (CDN Resource Laboratories, certificado del 20-ago-2021): los 150 resultados
  crudos de Au del round robin (15 laboratorios × 10 réplicas, g/t, 30 g de ensayo al fuego) y el
  valor publicado 2,388 ± 0,232 g/t.
- **OREAS 501b, 501c, 503c y 200** (certificados de análisis, Au por ensayo al fuego, ppm = g/t):
  valor certificado, SD y 1RSD de la tabla de «performance gates», con sus intervalos de 2 SD y
  3 SD. Los certificados redondean la SD: los intervalos se calculan con SD = valor × 1RSD.
- **Rainy River** (NI 43-101, 10-feb-2025, Tabla 11-12, p. 107 del informe) y **Loma Larga**
  (estudio de factibilidad de Dundee Precious Metals, 29-nov-2021, Tabla 11-3, p. 87): sesgos de
  CRM de Au, leídos de la IMAGEN de cada tabla (la extracción de texto sale desordenada).
- **GEMAS** (`qaqc_gemas.py`): conteos de pares dentro de las líneas, publicados en el tutorial de
  Demetriades y Argyraki (2025).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# ------------------------------------------------------------------ CDN-GS-2X
# filas = réplicas GS-2X-1 … GS-2X-10; columnas = laboratorios 1 … 15
CDN_GS2X: tuple[tuple[float, ...], ...] = (
    (2.39, 2.65, 2.49, 2.4, 2.42, 2.31, 2.29, 2.39, 2.35, 2.314, 2.263, 2.44, 2.54, 2.5, 2.326),
    (2.34, 2.41, 2.45, 2.56, 2.49, 2.43, 2.25, 2.32, 2.44, 2.287, 2.106, 2.28, 2.51, 2.41, 2.236),
    (2.49, 2.37, 2.57, 2.38, 2.49, 2.64, 2.28, 2.32, 2.2, 2.257, 2.338, 2.15, 2.49, 2.41, 2.328),
    (2.51, 2.47, 2.6, 2.35, 2.57, 2.39, 2.39, 2.41, 2.36, 2.272, 2.32, 2.12, 2.53, 2.33, 2.287),
    (2.35, 2.43, 2.62, 2.46, 2.76, 2.19, 2.43, 2.25, 2.32, 2.247, 2.346, 2.21, 2.51, 2.4, 2.191),
    (2.37, 2.64, 2.53, 2.43, 2.36, 2.57, 2.2, 2.47, 2.37, 2.301, 2.353, 2.12, 2.51, 2.5, 2.207),
    (2.31, 2.48, 2.42, 2.6, 2.43, 2.4, 2.43, 2.38, 2.4, 2.264, 2.279, 2.2, 2.55, 2.38, 2.242),
    (2.43, 2.29, 2.51, 2.47, 2.37, 2.34, 2.24, 2.54, 2.52, 2.294, 2.223, 2.12, 2.53, 2.56, 2.287),
    (2.32, 2.4, 2.43, 2.3, 2.68, 2.37, 2.29, 2.33, 2.6, 2.237, 2.3, 2.34, 2.54, 2.62, 2.32),
    (2.14, 2.25, 2.4, 2.55, 2.4, 2.33, 2.34, 2.49, 2.37, 2.282, 2.28, 2.48, 2.54, 2.55, 2.193),
)  # fmt: skip
CDN_RESULTADOS: tuple[float, ...] = tuple(x for fila in CDN_GS2X for x in fila)
CDN_PUBLICADO = (2.388, 0.232)  # valor recomendado y «dos desviaciones estándar entre laboratorios»


# ------------------------------------------------------------------ OREAS
@dataclass(frozen=True)
class Oreas:
    nombre: str
    valor: float  # ppm = g/t
    sd: float  # SD publicada (redondeada)
    rsd1_pct: float  # 1RSD publicada
    puertas: tuple[float, float, float, float]  # 2SD bajo, 2SD alto, 3SD bajo, 3SD alto

    @property
    def sd_sin_redondear(self) -> float:
        """SD con la que OREAS calcula sus intervalos: valor × 1RSD."""
        return self.valor * self.rsd1_pct / 100.0


OREAS: tuple[Oreas, ...] = (
    Oreas("OREAS 501b", 0.248, 0.010, 3.84, (0.229, 0.267, 0.219, 0.276)),
    Oreas("OREAS 501c", 0.221, 0.007, 2.95, (0.208, 0.234, 0.202, 0.241)),
    Oreas("OREAS 503c", 0.698, 0.015, 2.22, (0.667, 0.729, 0.651, 0.744)),
    Oreas("OREAS 200", 0.340, 0.012, 3.64, (0.316, 0.365, 0.303, 0.378)),
)
OREAS_BY_NAME = {o.nombre: o for o in OREAS}

# ------------------------------------------------------------------ sesgos de CRM de Au
# Rainy River, Tabla 11-12 (2024, Actlabs): CRM, n, esperado, media, sesgo publicado %, RSD %,
# fallas > 3 SD %. Orden de la tabla.
RAINY_RIVER: tuple[tuple[str, int, float, float, float, float, float], ...] = (
    ("OREAS 294", 78, 0.207, 0.205, -1.0, 6.5, 3),
    ("OREAS 230", 127, 0.337, 0.331, -1.8, 3.2, 0),
    ("OREAS 231", 128, 0.542, 0.533, -1.7, 3.4, 2),
    ("OREAS 233", 124, 1.050, 1.042, -0.8, 4.6, 5),
    ("OREAS 236", 23, 1.850, 1.827, -1.3, 2.7, 0),
    ("OREAS 238", 100, 3.080, 3.059, -0.7, 3.3, 1),
    ("OREAS 240", 14, 5.510, 5.377, -2.5, 3.6, 14),
    ("OREAS 242", 46, 8.670, 8.629, -0.5, 4.1, 4),
)
# Loma Larga, Tabla 11-3: CRM, n, media observada, SD observada, media esperada, SD esperada,
# diferencia publicada %.
LOMA_LARGA: tuple[tuple[str, int, float, float, float, float, float], ...] = (
    ("SG14", 25, 0.978, 0.036, 0.989, 0.044, -1.11),
    ("SI15", 21, 1.748, 0.063, 1.805, 0.067, -3.17),
    ("SN16", 28, 8.631, 0.199, 8.367, 0.217, 3.15),
)

# ------------------------------------------------------------------ GEMAS (Thompson-Howarth)
# (elemento, P %) -> (publicado bajo p99, publicado bajo p90) de 104 pares; Ge solo bajo p90.
GEMAS_PUBLICADO: dict[tuple[str, int], tuple[int | None, int]] = {
    ("Ag", 20): (99, 95),
    ("Ag", 10): (88, 68),
    ("Ge", 10): (None, 15),
}
# la hoja de Excel del tutorial: d90 y d99 (× C) para P = 10 % y 20 %
TH_HOJA = {10: (0.11631, 0.182135), 20: (0.23262, 0.36427)}

# ------------------------------------------------------------------ ejemplos sintéticos
SEMILLA_CRM = 19  # fija: con n = 30 un resultado cae fuera de ±2 SD y ninguna regla de serie
SEMILLA_BLANCOS = 11
SEMILLA_DUPLICADOS = 5
PUESTO_PICO = 0.7  # el pico del ejemplo de blancos va al 70 % de la serie


def serie_crm_sintetica(valor: float, sd: float, n: int, sesgo_pct: float = 0.0) -> list[float]:
    """n resultados normales con media valor × (1 + sesgo/100) y SD `sd`, de semilla fija. Es una
    serie SINTÉTICA de ejemplo: no son resultados de ningún laboratorio."""
    z = np.random.default_rng(SEMILLA_CRM).normal(size=n)
    return [float(round(valor * (1.0 + sesgo_pct / 100.0) + s * sd, 4)) for s in z]


def serie_blancos_sintetica(ld: float, n: int, pico_x_ld: float) -> list[float]:
    """n blancos entre 0,2 y 1,5 × LD, de semilla fija, y un pico de `pico_x_ld` × LD al 70 % de
    la serie (0 = sin pico). SINTÉTICA."""
    u = np.random.default_rng(SEMILLA_BLANCOS).uniform(0.2, 1.5, size=n)
    out = [float(round(ld * x, 6)) for x in u]
    if pico_x_ld > 0 and n:
        out[int(PUESTO_PICO * n)] = float(round(ld * pico_x_ld, 6))
    return out


def duplicados_sinteticos(n: int = 20) -> list[tuple[float, float]]:
    """n pares de un material de unos g/t, con 6 % de error relativo en cada medición, de
    semilla fija. SINTÉTICOS: punto de partida de la tabla editable."""
    rng = np.random.default_rng(SEMILLA_DUPLICADOS)
    c = np.exp(rng.normal(0.0, 0.8, size=n))
    a = c * (1.0 + 0.06 * rng.normal(size=n))
    b = c * (1.0 + 0.06 * rng.normal(size=n))
    return [(float(round(x, 3)), float(round(y, 3))) for x, y in zip(a, b, strict=True)]
