"""Cianuración en botella: las cifras publicadas por Roostaei, Kordparijaei y Mesroghli (2026)
(Tablas 4, 6 y 7 y Ec. 3) y los cortes de validación, fijados ANTES de correr:

- Tabla 4: la ley de cabeza de cada fila (S0 = residuo / (1 − R)) debe caer en el intervalo que
  deja el redondeo de esa fila, con S0 = 1 070 ppb; y R = (1 − residuo/S0)·100 al redondeo.
- Tabla 6: L y M a 3 decimales; N con la B inferida, a 3 decimales.
- Tabla 7: R², intercepto y pendiente de las 6 regresiones al redondeo publicado, con los mismos
  puntos (sin el de 2 h) y sobre los términos redondeados a 3 decimales, como los tabuló el
  artículo.
- Ec. 3: 228,046, 0,332 y R² 0,937 al redondeo publicado.

Los rótulos son CÓDIGOS de idioma neutro (la app los vuelve texto); aquí no hay frases.
Hallazgo (se informa tal cual, sin ajustar nada): la fila M1 de la Tabla 7 no sale de los datos;
sus propios R² y F (0,994 y 171,04) cuadran entre sí, pero no con los términos M de la Tabla 6.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import cianuracion as c

T_H = (1.0, 2.0, 3.0, 7.0, 11.0, 24.0, 48.0)
SOLUCION_PPB = (446.0, 473.0, 455.0, 490.0, 495.0, 510.0, 524.0)
RESIDUO_PPB = (220.0, 153.0, 189.0, 121.0, 112.0, 83.0, 56.0)
RECUPERACION_PUB = (79.44, 85.70, 82.34, 88.69, 89.53, 92.24, 94.77)
# Tabla 6, por columna y tiempo (h)
L_PUB = dict(zip(T_H, (0.366, 0.466, 0.409, 0.525, 0.543, 0.609, 0.685), strict=True))
M_PUB = dict(zip(T_H, (0.410, 0.477, 0.439, 0.516, 0.529, 0.573, 0.626), strict=True))
N1_PUB = {1.0: 0.410, 2.0: 0.491, 3.0: 0.445, 7.0: 0.538}
N2_PUB = {7.0: 0.562, 11.0: 0.578, 24.0: 0.633, 48.0: 0.698}
# Tabla 7: (R², intercepto, pendiente) impresos
T7_PUB = {
    "L1": ("0.995", "0.335", "0.027"),
    "L2": ("0.986", "0.503", "0.004"),
    "M1": ("0.994", "0.388", "0.019"),
    "M2": ("0.988", "0.501", "0.003"),
    "N1": ("0.996", "0.385", "0.022"),
    "N2": ("0.987", "0.543", "0.003"),
}
T7_F_PUB = {"M1": 171.040}  # el F impreso de M1, que implica R² = 0,99419
E3_PUB = {"a": ("228.046", 228.046), "b": ("0.332", 0.332), "r2": ("0.937", 0.937)}


@dataclass(frozen=True)
class CianCheck:
    source: str  # t4, t6, t7, e3
    kind: str  # clave del concepto
    label: str  # detalle neutro: «1 h», «L1», «a»
    published: float
    calculated: float
    ok: bool
    note: str = ""  # clave de nota o vacío
    decimals: int = 3


def _decimals(printed: str) -> int:
    return len(printed.split(".")[1]) if "." in printed else 0


def _matches(printed: str, value: float) -> bool:
    """El valor calculado, redondeado a los decimales con que se imprimió, es lo publicado."""
    d = _decimals(printed)
    return round(value, d) == round(float(printed), d)


def _label_h(t: float) -> str:
    return f"{t:g} h"


def table4_checks() -> list[CianCheck]:
    out = []
    for t, res, rec in zip(T_H, RESIDUO_PPB, RECUPERACION_PUB, strict=True):
        head = c.cabeza_desde_recuperacion(res, rec)
        # intervalo de S0 que deja el redondeo de la fila (residuo ±0,5 ppb, R ±0,005 puntos)
        lo = (res - 0.5) / (1 - (rec - 0.005) / 100)
        hi = (res + 0.5) / (1 - (rec + 0.005) / 100)
        lo, hi = min(lo, hi), max(lo, hi)
        out.append(
            CianCheck("t4", "cabeza", _label_h(t), c.S0_PPB, head, lo <= c.S0_PPB <= hi, "", 1)
        )
    for t, res, rec in zip(T_H, RESIDUO_PPB, RECUPERACION_PUB, strict=True):
        calc = c.recuperacion_pct(res, c.S0_PPB)
        out.append(
            CianCheck("t4", "recuperacion", _label_h(t), rec, calc, round(calc, 2) == rec, "", 2)
        )
    return out


def table6_checks() -> list[CianCheck]:
    rec = np.array(RECUPERACION_PUB)
    out = []
    rows = (
        ("L", L_PUB, c.terminos(rec, c.B_N1)["difusion"], T_H),
        ("M", M_PUB, c.terminos(rec, c.B_N1)["reaccion"], T_H),
        ("N1", N1_PUB, c.terminos(rec, c.B_N1)["mixto"], T_H),
        ("N2", N2_PUB, c.terminos(rec, c.B_N2)["mixto"], T_H),
    )
    for name, pub, calc, times in rows:
        for t, value in zip(times, calc, strict=True):
            if t in pub:
                ok = round(float(value), 3) == pub[t]
                out.append(CianCheck("t6", name, _label_h(t), pub[t], float(value), ok))
    return out


def regressions() -> dict[str, c.Regresion]:
    """Las 6 regresiones de la Tabla 7: puntos de 1, 3 y 7 h y de 7, 11, 24 y 48 h, sobre los
    términos de la Tabla 6 con las recuperaciones impresas y redondeados a 3 decimales."""
    t = np.array(T_H)
    out = {}
    for name, model, b, picks in (
        ("L1", "difusion", c.B_N1, (0, 2, 3)),
        ("L2", "difusion", c.B_N2, (3, 4, 5, 6)),
        ("M1", "reaccion", c.B_N1, (0, 2, 3)),
        ("M2", "reaccion", c.B_N2, (3, 4, 5, 6)),
        ("N1", "mixto", c.B_N1, (0, 2, 3)),
        ("N2", "mixto", c.B_N2, (3, 4, 5, 6)),
    ):
        y = c.terminos(RECUPERACION_PUB, b, c.DECIMALES_TABLA)[model]
        out[name] = c.regresion(t[list(picks)], y[list(picks)])
    return out


def table7_checks() -> list[CianCheck]:
    out = []
    for name, reg in regressions().items():
        for kind, printed, value in zip(
            ("r2", "intercepto", "pendiente"),
            T7_PUB[name],
            (reg.r2, reg.intercepto, reg.pendiente),
            strict=True,
        ):
            ok = _matches(printed, value)
            note = "m1" if name == "M1" and not ok else ""
            out.append(
                CianCheck("t7", kind, name, float(printed), value, ok, note, _decimals(printed))
            )
    return out


def equation3_checks() -> list[CianCheck]:
    fit = c.ajustar_potencial(T_H, RESIDUO_PPB)
    calc = {"a": fit.a_ppb, "b": fit.b, "r2": fit.r2}
    return [
        CianCheck(
            "e3",
            key,
            key,
            E3_PUB[key][1],
            calc[key],
            _matches(E3_PUB[key][0], calc[key]),
            "",
            _decimals(E3_PUB[key][0]),
        )
        for key in ("a", "b", "r2")
    ]


def all_checks() -> list[CianCheck]:
    return [*table4_checks(), *table6_checks(), *table7_checks(), *equation3_checks()]


def summary(checks: list[CianCheck] | None = None) -> dict[str, tuple[int, int]]:
    """(cuadran, total) por fuente."""
    checks = checks or all_checks()
    out: dict[str, tuple[int, int]] = {}
    for src in ("t4", "t6", "t7", "e3"):
        rows = [x for x in checks if x.source == src]
        out[src] = (sum(x.ok for x in rows), len(rows))
    return out


def m1_implied_r2() -> float:
    """R² que implica el F impreso de M1 (F = R²/(1 − R²)·gl2, con gl2 = 1)."""
    f = T7_F_PUB["M1"]
    return f / (f + 1.0)


def b_intervals() -> dict[str, tuple[float, float]]:
    """Para cada columna N, el rango de B que reproduce todas sus celdas publicadas (3 decimales):
    de N − L/3 = B·M, B está entre (N ± 0,0005 − L/3)/M en cada celda."""
    rec = np.array(RECUPERACION_PUB)
    m = c.terminos(rec)["reaccion"]
    base = c.terminos(rec)["difusion"] / 3.0
    out = {}
    for name, pub in (("N1", N1_PUB), ("N2", N2_PUB)):
        lo, hi = -np.inf, np.inf
        for t, v in pub.items():
            i = T_H.index(t)
            lo = max(lo, (v - 0.0005 - base[i]) / m[i])
            hi = min(hi, (v + 0.0005 - base[i]) / m[i])
        out[name] = (float(lo), float(hi))
    return out


def head_range() -> tuple[float, float]:
    """Mínimo y máximo de la ley de cabeza que implica cada fila de la Tabla 4."""
    heads = [
        c.cabeza_desde_recuperacion(r, p)
        for r, p in zip(RESIDUO_PPB, RECUPERACION_PUB, strict=True)
    ]
    return min(heads), max(heads)
