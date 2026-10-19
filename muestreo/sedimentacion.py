"""Ensayo de sedimentación en probeta y dimensionamiento de un espesador convencional.

Métodos (todos de dominio público o abiertos; aquí solo sus ecuaciones):
- Coe y Clevenger (1916), «Methods for Determining the Capacities of Slime-Settling Tanks»,
  Trans. AIME 55:356-385: A = 2000 (F − D) / (24 · 62,35 · R) pies² por tonelada corta por día,
  con F y D las diluciones (partes de fluido por parte de sólido) de la alimentación y de la
  descarga y R la velocidad de sedimentación en pies/h (forma verificada en la página impresa 372).
- Kynch (1952): de UNA curva de sedimentación h(t), la tangente en cada punto da la concentración
  C = C0 H0 / H (H = ordenada de la tangente en t = 0) y la velocidad v = −dh/dt; el flujo de
  sólidos es G = v C.
- Talmage y Fitch (1955): la tangente en el punto de compresión corta la cota del underflow
  Hu = C0 H0 / Cu en el tiempo tu, y el área unitaria es tu / (C0 H0).
- Yoshioka y otros (1957) / Hassett: el flujo límite G_L = min G(C) / (1 − C/Cu), con C entre la
  concentración inicial y la del underflow; área unitaria = 1 / G_L.
- Luz (en Torquato et al., 2011, REM 64(1):91-96), ec. 1:
  z(t) = (z0 − z∞)(1 − t^a/(t^a + b^a)) + z∞.
- Roberts: el punto de compresión se busca donde ln(h − h∞) contra t cambia de pendiente (aquí, el
  quiebre que minimiza el error de dos rectas: criterio NUESTRO, declarado).

Unidades: tiempos en s, alturas en m, concentraciones en t/m³, velocidades en m/h y áreas
unitarias en m² por (t/d).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

RHO_AGUA_T_M3 = 1.0  # supuesto declarado
LB_POR_PIE3_AGUA = 62.35  # Coe y Clevenger (1916)
LB_POR_TON_CORTA = 2000.0
HORAS_DIA = 24.0
MIN_FILAS = 4
FACTOR_VALE_LAMAS = 0.64  # Torquato et al. (2011): SOLO lamas de hierro de Vale, no es universal
FACTOR_VALE_PELLET = 1.3


class SedimentacionError(ValueError):
    """Los datos no sirven. `code` es una clave de texto de la app; `args_` rellena sus campos."""

    def __init__(self, code: str, **args: float) -> None:
        super().__init__(code)
        self.code, self.args_ = code, args


def _positivo(x: object) -> bool:
    return isinstance(x, int | float) and not isinstance(x, bool) and math.isfinite(x) and x > 0


# ------------------------------------------------------------------ Coe y Clevenger (1916)
def coe_clevenger_pies2_ton_dia(f: float, d: float, r_pies_h: float) -> float:
    """Área (pies² por tonelada corta por día): 2000 (F − D) / (24 · 62,35 · R)."""
    if not (_positivo(f) and _positivo(d) and _positivo(r_pies_h)) or f <= d:
        raise SedimentacionError("coe")
    return LB_POR_TON_CORTA * (f - d) / (HORAS_DIA * LB_POR_PIE3_AGUA * r_pies_h)


def coe_clevenger_m2_t_dia(
    f: float, d: float, r_m_h: float, rho_agua: float = RHO_AGUA_T_M3
) -> float:
    """Área (m² por t/d): el agua que sube, (F − D) t por t de sólido, por la velocidad R."""
    if not (_positivo(f) and _positivo(d) and _positivo(r_m_h) and _positivo(rho_agua)) or f <= d:
        raise SedimentacionError("coe")
    return (f - d) * (1000.0 / HORAS_DIA) / (rho_agua * 1000.0 * r_m_h)


def diametro_m(area_m2: float) -> float:
    if not _positivo(area_m2):
        raise SedimentacionError("numero")
    return math.sqrt(4.0 * area_m2 / math.pi)


def diametro_pies(area_pies2: float) -> float:
    return diametro_m(area_pies2)


def area_circulo_m2(diametro: float) -> float:
    return math.pi * diametro**2 / 4.0


# ------------------------------------------------------------------ espesadores en general
def area_unitaria_m2_t_dia(diametro: float, t_h: float) -> float:
    """Área unitaria de un espesador: (π D² / 4) / (t/h · 24). `t_h` es por espesador."""
    if not (_positivo(diametro) and _positivo(t_h)):
        raise SedimentacionError("numero")
    return area_circulo_m2(diametro) / (t_h * HORAS_DIA)


def diametro_desde_area_unitaria(area_unitaria: float, t_h: float) -> float:
    if not (_positivo(area_unitaria) and _positivo(t_h)):
        raise SedimentacionError("numero")
    return diametro_m(area_unitaria * t_h * HORAS_DIA)


def dimensionar(area_unitaria: float, t_h: float, factor: float = 1.0) -> tuple[float, float]:
    """(área m², diámetro m) para `t_h` t/h, con el factor de corrección multiplicativo."""
    if not (_positivo(area_unitaria) and _positivo(t_h) and _positivo(factor)):
        raise SedimentacionError("numero")
    area = area_unitaria * t_h * HORAS_DIA * factor
    return area, diametro_m(area)


def concentracion_t_m3(fraccion_masica: float, rho_s: float, rho_w: float = RHO_AGUA_T_M3) -> float:
    """Sólidos por m³ de pulpa: C = cm · ρ_pulpa, con ρ_pulpa = 1 / (cm/ρs + (1 − cm)/ρw)."""
    if not (0.0 < fraccion_masica < 1.0 and _positivo(rho_s) and _positivo(rho_w)):
        raise SedimentacionError("numero")
    rho_pulpa = 1.0 / (fraccion_masica / rho_s + (1.0 - fraccion_masica) / rho_w)
    return fraccion_masica * rho_pulpa


# ------------------------------------------------------------------ la curva h(t)
@dataclass(frozen=True)
class CurvaSed:
    """Cota de la interfase (m) contra el tiempo (s) de una probeta; empieza en t = 0."""

    t_s: tuple[float, ...]
    h_m: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.t_s) < MIN_FILAS or len(self.t_s) != len(self.h_m):
            raise SedimentacionError("filas", lo=MIN_FILAS, hi=0)
        if not all(_positivo(x) for x in self.h_m) or not all(
            isinstance(x, int | float) and math.isfinite(x) and x >= 0 for x in self.t_s
        ):
            raise SedimentacionError("numero")
        if self.t_s[0] != 0.0:
            raise SedimentacionError("origen")
        if any(b <= a for a, b in zip(self.t_s, self.t_s[1:], strict=False)):
            raise SedimentacionError("orden")
        if any(b > a for a, b in zip(self.h_m, self.h_m[1:], strict=False)):
            raise SedimentacionError("sube")

    @property
    def h0(self) -> float:
        return self.h_m[0]

    @property
    def t_max(self) -> float:
        return self.t_s[-1]

    def interpolante(self) -> PchipInterpolator:
        return PchipInterpolator(np.asarray(self.t_s, float), np.asarray(self.h_m, float))

    def altura(self, t: float) -> float:
        return float(self.interpolante()(min(max(t, 0.0), self.t_max)))

    def velocidad_m_h(self, t: float) -> float:
        """Velocidad de descenso de la interfase (m/h), positiva."""
        d = self.interpolante().derivative()
        return float(-d(min(max(t, 0.0), self.t_max)) * 3600.0)


def luz_altura(t: float, z0: float, z_inf: float, a: float, b: float) -> float:
    """Ec. 1 de Luz: z(t) = (z0 − z∞)(1 − t^a / (t^a + b^a)) + z∞."""
    if t <= 0:
        return z0
    ta, ba = t**a, b**a
    return (z0 - z_inf) * (1.0 - ta / (ta + ba)) + z_inf


def luz_velocidad_m_s(t: float, z0: float, z_inf: float, a: float, b: float) -> float:
    """Ec. 2: v = −(z0 − z∞) a b^a t^(a−1) / (t^a + b^a)², en m/s con signo negativo (desciende)."""
    if t <= 0:
        return 0.0 if a > 1 else -(z0 - z_inf) * a / b
    return -(z0 - z_inf) * a * b**a * t ** (a - 1) / (t**a + b**a) ** 2


def curva_luz(z0: float, z_inf: float, a: float, b: float, t_max: float, n: int = 120) -> CurvaSed:
    """La curva de Luz muestreada en `n` instantes de 0 a `t_max` (más densos al principio)."""
    if not all(_positivo(x) for x in (z0, z_inf, a, b, t_max)) or z_inf >= z0:
        raise SedimentacionError("luz")
    ts = [0.0, *(t_max * (i / (n - 1)) ** 1.6 for i in range(1, n))]
    return CurvaSed(tuple(ts), tuple(luz_altura(t, z0, z_inf, a, b) for t in ts))


# ------------------------------------------------------------------ Kynch
@dataclass(frozen=True)
class KynchPuntos:
    t_s: tuple[float, ...]
    h_m: tuple[float, ...]
    v_m_h: tuple[float, ...]
    h_tangente_m: tuple[float, ...]  # ordenada de la tangente en t = 0
    c_t_m3: tuple[float, ...]
    g_t_m2_h: tuple[float, ...]  # flujo de sólidos G = v C


def kynch(curva: CurvaSed, c0: float, v_min_m_h: float = 1e-9) -> KynchPuntos:
    """Los pares (C, v) y el flujo G = v·C de la curva, por tangentes, desde la velocidad máxima
    (después del arranque lento) y con la tangente bajo H0."""
    if not _positivo(c0):
        raise SedimentacionError("numero")
    t, h = np.asarray(curva.t_s, float), np.asarray(curva.h_m, float)
    v_s = -curva.interpolante().derivative()(t)
    h_tan = h + v_s * t
    # sin el arranque lento: antes de la velocidad máxima la interfase aún acelera (la tangente
    # cortaría sobre H0, concentración < C0) y no hay zona de concentración uniforme que medir
    arranque = int(np.argmax(v_s >= 0.999 * np.max(v_s)))
    keep = (v_s * 3600.0 > v_min_m_h) & (h_tan <= curva.h0 * (1.0 + 1e-6))
    keep[:arranque] = False
    t, h, v_s, h_tan = t[keep], h[keep], v_s[keep], h_tan[keep]
    c = c0 * curva.h0 / h_tan
    v_h = v_s * 3600.0
    return KynchPuntos(*(tuple(map(float, x)) for x in (t, h, v_h, h_tan, c, v_h * c)))


def flujo_limite(c: Sequence[float], g: Sequence[float], cu: float) -> tuple[float, float]:
    """(G_L, C en el mínimo): G_L = min G(C) / (1 − C/Cu) sobre los C < Cu (Yoshioka/Hassett)."""
    pairs = [(ci, gi) for ci, gi in zip(c, g, strict=True) if 0 < ci < cu and gi > 0]
    if not pairs:
        raise SedimentacionError("flujo")
    ci, gi = min(pairs, key=lambda p: p[1] / (1.0 - p[0] / cu))
    return gi / (1.0 - ci / cu), ci


def area_flujo_limite_m2_t_dia(g_limite_t_m2_h: float) -> float:
    return 1.0 / (HORAS_DIA * g_limite_t_m2_h)


# ------------------------------------------------------------------ Talmage y Fitch
@dataclass(frozen=True)
class TalmageFitch:
    modo: str  # «clasico» (Hu del underflow) o «vale» (Hu = cota a 24 h)
    hu_m: float
    tc_s: float
    hc_m: float
    v_c_m_h: float
    tu_s: float
    area_unitaria_m2_t_dia: float

    def tangente(self, t: float) -> float:
        return self.hc_m - self.v_c_m_h / 3600.0 * (t - self.tc_s)


def talmage_fitch(
    curva: CurvaSed, c0: float, cu: float, tc_s: float, modo: str = "clasico",
    h_inf: float | None = None,
) -> TalmageFitch:  # fmt: skip
    """Talmage-Fitch: tu es donde la tangente en el punto de compresión (tc, hc) corta Hu; el
    área unitaria es tu / (C0 H0) (en m² por t/h; dividida por 24 queda por t/d)."""
    if modo not in ("clasico", "vale") or not (_positivo(c0) and _positivo(cu)) or cu <= c0:
        raise SedimentacionError("numero")
    if not 0.0 < tc_s < curva.t_max:
        raise SedimentacionError("compresion", t_max=curva.t_max)
    hu = curva.h0 * c0 / cu if modo == "clasico" else (curva.h_m[-1] if h_inf is None else h_inf)
    hc, v = curva.altura(tc_s), curva.velocidad_m_h(tc_s)
    if v <= 0 or hc <= hu:
        raise SedimentacionError("tangente")
    tu = tc_s + (hc - hu) / (v / 3600.0)
    area = (tu / 3600.0) / (c0 * curva.h0) / HORAS_DIA
    return TalmageFitch(modo, hu, tc_s, hc, v, tu, area)


def roberts_punto_compresion(curva: CurvaSed, h_inf: float | None = None) -> float:
    """Tiempo (s) del quiebre de ln(h − h∞) contra t, con dos rectas de error total mínimo (cada
    una con al menos 3 puntos). h∞ por defecto es la última cota."""
    hi = curva.h_m[-1] if h_inf is None else h_inf
    pts = [
        (t, math.log(h - hi))
        for t, h in zip(curva.t_s, curva.h_m, strict=True)
        if h > hi * (1 + 1e-9)
    ]
    if len(pts) < 7:
        raise SedimentacionError("roberts")
    t, y = (np.array(c, float) for c in zip(*pts, strict=True))

    def sse(i: int, j: int) -> float:
        coef = np.polyfit(t[i:j], y[i:j], 1)
        return float(np.sum((np.polyval(coef, t[i:j]) - y[i:j]) ** 2))

    best = min(range(3, len(t) - 3), key=lambda k: sse(0, k + 1) + sse(k, len(t)))
    return float(t[best])


# ------------------------------------------------------------------ curva sintética de Kynch
def v_richardson_zaki(c: float, v0: float, c_max: float, n: float) -> float:
    """v(C) = v0 (1 − C/Cmax)^n: velocidad de sedimentación en zona, m/h (función DECLARADA)."""
    return v0 * max(1.0 - c / c_max, 0.0) ** n


def sintetica_kynch(
    v0: float, c_max: float, n: float, c0: float, h0: float, t_max_s: float, puntos: int = 2000,
) -> CurvaSed:  # fmt: skip
    """h(t) EXACTA de una probeta sin compresión con v(C) = v0 (1 − C/Cmax)^n, por el método de las
    características: velocidad v0 hasta t_c y después, con C entre C0 y Cmax,
    t(C) = C0 H0 / (C² · (−v'(C))) y h(C) = C0 H0 / C − v(C) t(C). Requiere C0 > 2 Cmax / (n + 1)
    para que t(C) crezca con C (flujo convexo en el tramo de interés)."""
    if not (n > 1 and 0 < c0 < c_max and c0 > 2.0 * c_max / (n + 1.0)):
        raise SedimentacionError("sintetica")
    k = c0 * h0

    def t_h(c: float) -> float:  # horas
        return k / (c * c * (v0 * n / c_max) * (1.0 - c / c_max) ** (n - 1.0))

    def h_de_c(c: float) -> float:
        return k / c - v_richardson_zaki(c, v0, c_max, n) * t_h(c)

    v_c0 = v_richardson_zaki(c0, v0, c_max, n)
    t_c = t_h(c0) * 3600.0
    ts = [0.0, *np.linspace(t_max_s / puntos, t_max_s, puntos)]
    hs = []
    for t in ts:
        if t <= t_c:
            hs.append(h0 - v_c0 * t / 3600.0)
            continue
        th = t / 3600.0
        c = brentq(lambda x, th=th: t_h(x) - th, c0, c_max * (1.0 - 1e-12), xtol=1e-15, rtol=1e-14)
        hs.append(h_de_c(c))
    hs = np.minimum.accumulate(np.asarray(hs))  # el redondeo no puede subir la interfase
    return CurvaSed(tuple(float(x) for x in ts), tuple(float(x) for x in hs))
