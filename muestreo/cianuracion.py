"""Ensayo de cianuración (botella): recuperación y ley de cabeza por balance, los términos del
modelo del núcleo sin reaccionar (L difusión, M reacción, N mixto), regresiones lineales por tramo,
el modelo potencial de los autores y un primer orden con meseta (modelo NUESTRO).

Fuente de los datos y de las ecuaciones de los autores: Roostaei, Kordparijaei y Mesroghli (2026),
«Cyanide dissolution of gold-bearing iron oxide minerals: kinetic studies and optimization using
response surface methodology», Discover Applied Sciences, doi 10.1007/s42452-026-08420-8
(acceso abierto, CC BY-NC-ND). Aquí solo se usan sus cifras citadas y las ecuaciones.

Lo INFERIDO (el artículo no lo publica) y se declara:
- `B_N1` y `B_N2`, la constante del término mixto N = (1 − 2X/3) − (1 − X)^(2/3) + B·M. Con
  N − L/3 = B·M, las celdas publicadas de N dan B = 0,7033 (rango compatible con su redondeo,
  0,7028 a 0,7039) para el tramo hasta 7 h y B = 0,75 (0,7500 a 0,7505) para el de 7 a 48 h.
- `S0_PPB` = 1 070 ppb, la ley de cabeza que sale de cada fila (residuo / (1 − R)).
- `F_SOLUCION` = 1,935: cuántos ppb del sólido hay por cada ppb de la solución en la Tabla 4
  ((S0 − residuo) / solución en las filas de 2 a 48 h). El artículo no publica el volumen.
Lo NUESTRO: la regla de exclusión de puntos, el primer orden con meseta y la tolerancia de
coherencia de la cabeza (5 %).
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy import stats
from scipy.optimize import brentq, least_squares

S0_PPB = 1070.0
F_SOLUCION = 1.935
B_N1, B_N2 = 0.7033, 0.75
T_CORTE_H = 7.0  # corte entre los dos tramos de los autores
MIN_PUNTOS_TRAMO = 3
DECIMALES_TABLA = 3  # los autores regresan sobre los términos redondeados a 3 decimales
COHERENCIA_PCT = 5.0  # una fila con cabeza a más de 5 % de la cabeza declarada se avisa
MODELOS_LINEALES = ("difusion", "reaccion", "mixto")
MODELOS = (*MODELOS_LINEALES, "potencial", "primer_orden")
CURVA_T_MIN_H = 0.5


class SerieInvalida(ValueError):
    """Los datos de la serie no sirven. `code` es una clave de texto de la app; `args` rellena
    sus {campos}."""

    def __init__(self, code: str, **args: float) -> None:
        super().__init__(code)
        self.code, self.args_ = code, args


@dataclass(frozen=True)
class Aviso:
    code: str
    t_h: float
    value: float = 0.0


@dataclass(frozen=True)
class Balance:
    t_h: tuple[float, ...]
    solucion_ppb: tuple[float, ...]
    residuo_ppb: tuple[float, ...]
    recuperacion_pct: tuple[float, ...]
    au_solucion_ppb: tuple[float, ...]  # F · solución: oro disuelto, en ppb del sólido
    cabeza_ppb: tuple[float, ...]  # residuo + F · solución, fila por fila
    avisos: tuple[Aviso, ...]


def _finito_positivo(x: float) -> bool:
    return isinstance(x, int | float) and not isinstance(x, bool) and math.isfinite(x) and x > 0


def validar_serie(
    t_h: Sequence[float], solucion: Sequence[float], residuo: Sequence[float]
) -> None:
    """Números finitos y positivos, tiempos estrictamente crecientes, al menos una fila."""
    if not t_h or not (len(t_h) == len(solucion) == len(residuo)):
        raise SerieInvalida("filas")
    for col in (t_h, solucion, residuo):
        if not all(_finito_positivo(x) for x in col):
            raise SerieInvalida("numero")
    if any(b <= a for a, b in itertools.pairwise(t_h)):
        raise SerieInvalida("orden")


def recuperacion_pct(residuo_ppb: float, cabeza_ppb: float) -> float:
    """R = (1 − St/S0) · 100 (Ec. 4 de los autores)."""
    if not (_finito_positivo(residuo_ppb) and _finito_positivo(cabeza_ppb)):
        raise SerieInvalida("numero")
    return (1.0 - residuo_ppb / cabeza_ppb) * 100.0


def cabeza_desde_recuperacion(residuo_ppb: float, rec_pct: float) -> float:
    """La ley de cabeza S0 que implica una fila: St / (1 − R/100)."""
    if rec_pct >= 100.0:
        raise SerieInvalida("recuperacion")
    return residuo_ppb / (1.0 - rec_pct / 100.0)


def balance(
    t_h: Sequence[float],
    solucion: Sequence[float],
    residuo: Sequence[float],
    cabeza: float = S0_PPB,
    factor: float = F_SOLUCION,
) -> Balance:
    """Recuperación de cada fila (con la cabeza dada) y cabeza por balance (residuo + F·solución).
    Avisos: `no_monotona` (la recuperación de una fila supera la de una posterior: el oro no se
    vuelve a depositar en un ensayo normal) y `cabeza` (la cabeza de la fila se aparta más de
    `COHERENCIA_PCT` de la declarada)."""
    validar_serie(t_h, solucion, residuo)
    if not (_finito_positivo(cabeza) and _finito_positivo(factor)):
        raise SerieInvalida("numero")
    if max(residuo) >= cabeza:
        raise SerieInvalida("residuo_mayor", cabeza=cabeza)
    rec = [recuperacion_pct(r, cabeza) for r in residuo]
    heads = [r + factor * s for r, s in zip(residuo, solucion, strict=True)]
    avisos = [Aviso("no_monotona", t_h[i], rec[i]) for i in np.flatnonzero(~_monotona(rec))]
    for t, h in zip(t_h, heads, strict=True):
        dev = 100.0 * (h / cabeza - 1.0)
        if abs(dev) > COHERENCIA_PCT:
            avisos.append(Aviso("cabeza", t, dev))
    return Balance(
        tuple(float(x) for x in t_h),
        tuple(float(x) for x in solucion),
        tuple(float(x) for x in residuo),
        tuple(rec),
        tuple(factor * s for s in solucion),
        tuple(heads),
        tuple(avisos),
    )


def _monotona(rec: Sequence[float]) -> np.ndarray:
    """True en los puntos cuya recuperación NO supera la de ninguna fila posterior."""
    r = np.asarray(rec, dtype=float)
    return np.array([bool(np.all(r[i] <= r[i + 1 :])) for i in range(len(r))], dtype=bool)


def puntos_usados(rec_pct: Sequence[float]) -> list[bool]:
    """Regla de selección (NUESTRA, reproduce la de los autores): se excluye el punto cuya
    recuperación es mayor que la de uno posterior. En la Tabla 4 solo queda fuera el de 2 h."""
    return [bool(x) for x in _monotona(rec_pct)]


# ------------------------------------------------------------------ términos del núcleo
def terminos(
    rec_pct: Sequence[float] | np.ndarray, b: float = B_N1, decimales: int | None = None
) -> dict[str, np.ndarray]:
    """L = 1 − 3(1−X)^(2/3) + 2(1−X) (difusión), M = 1 − (1−X)^(1/3) (reacción) y
    N = (1 − 2X/3) − (1−X)^(2/3) + B·M (mixto), con X = R/100 en (0, 1)."""
    x = np.asarray(rec_pct, dtype=float) / 100.0
    if np.any(x <= 0) or np.any(x >= 1) or not np.all(np.isfinite(x)):
        raise SerieInvalida("rango")
    u = 1.0 - x
    m = 1.0 - u ** (1 / 3)
    out = {
        "difusion": 1.0 - 3.0 * u ** (2 / 3) + 2.0 * u,
        "reaccion": m,
        "mixto": (1.0 - 2.0 * x / 3.0) - u ** (2 / 3) + b * m,
    }
    return out if decimales is None else {k: np.round(v, decimales) for k, v in out.items()}


def termino_de_x(modelo: str, x: float, b: float) -> float:
    """El término de `modelo` en la fracción disuelta x (0 a 1)."""
    u = 1.0 - x
    if modelo == "difusion":
        return 1.0 - 3.0 * u ** (2 / 3) + 2.0 * u
    if modelo == "reaccion":
        return 1.0 - u ** (1 / 3)
    return (1.0 - 2.0 * x / 3.0) - u ** (2 / 3) + b * (1.0 - u ** (1 / 3))


def x_de_termino(modelo: str, y: float, b: float) -> float:
    """Inversa de `termino_de_x` (los tres términos crecen con x): la fracción disuelta que da el
    término `y`, acotada a [0, 1]."""
    if y <= 0.0:
        return 0.0
    if y >= termino_de_x(modelo, 1.0, b):
        return 1.0
    return float(brentq(lambda x: termino_de_x(modelo, x, b) - y, 0.0, 1.0, xtol=1e-14))


# ------------------------------------------------------------------ regresiones
@dataclass(frozen=True)
class Regresion:
    n: int
    r2: float
    intercepto: float
    pendiente: float
    f: float  # F del modelo (gl 1 y n − 2)
    p: float

    def en(self, t: float) -> float:
        return self.intercepto + self.pendiente * t


def regresion(x: Sequence[float], y: Sequence[float]) -> Regresion:
    """Mínimos cuadrados de y contra x con R², F y su significancia (como SPSS: gl 1 y n − 2)."""
    xs, ys = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(xs) < MIN_PUNTOS_TRAMO or len(xs) != len(ys):
        raise SerieInvalida("pocos_puntos")
    if np.ptp(xs) == 0:
        raise SerieInvalida("orden")
    r = stats.linregress(xs, ys)
    r2 = float(r.rvalue**2)
    df2 = len(xs) - 2
    f = r2 / (1.0 - r2) * df2 if r2 < 1.0 else math.inf
    return Regresion(len(xs), r2, float(r.intercept), float(r.slope), f, float(r.pvalue))


@dataclass(frozen=True)
class AjusteLineal:
    """Las dos rectas de un término (hasta el corte y después de él) y los puntos que usaron."""

    modelo: str
    corte_h: float
    tramo1: Regresion | None
    tramo2: Regresion | None
    indices1: tuple[int, ...]
    indices2: tuple[int, ...]

    def recta(self, t: float) -> float | None:
        reg = self.tramo1 if t <= self.corte_h else self.tramo2
        return None if reg is None else reg.en(t)


def ajustar_lineal(
    modelo: str,
    t_h: Sequence[float],
    rec_pct: Sequence[float],
    corte_h: float = T_CORTE_H,
    decimales: int | None = DECIMALES_TABLA,
) -> AjusteLineal:
    """Regresiones lineales del término `modelo` contra t por tramo: t ≤ corte y t ≥ corte (el
    punto del corte entra en las dos, como en el artículo). Sin los puntos que excluye
    `puntos_usados`; un tramo con menos de `MIN_PUNTOS_TRAMO` puntos queda sin ajustar."""
    if modelo not in MODELOS_LINEALES:
        raise ValueError(f"modelo desconocido: {modelo}")
    t = np.asarray(t_h, dtype=float)
    usados = np.array(puntos_usados(rec_pct))
    regs, idxs = [], []
    for b, dentro in ((B_N1, t <= corte_h), (B_N2, t >= corte_h)):
        y = terminos(rec_pct, b, decimales)[modelo]
        idx = tuple(int(i) for i in np.flatnonzero(dentro & usados))
        ok = len(idx) >= MIN_PUNTOS_TRAMO and np.ptp(t[list(idx)]) > 0
        regs.append(regresion(t[list(idx)], y[list(idx)]) if ok else None)
        idxs.append(idx)
    return AjusteLineal(modelo, corte_h, regs[0], regs[1], idxs[0], idxs[1])


# ------------------------------------------------------------------ potencial y primer orden
@dataclass(frozen=True)
class Potencial:
    """ln St = ln a − b ln t (Ec. 3 de los autores): St en ppb y t en h."""

    a_ppb: float
    b: float
    r2: float

    def residuo(self, t: float) -> float:
        return self.a_ppb * t ** (-self.b)


def ajustar_potencial(t_h: Sequence[float], residuo: Sequence[float]) -> Potencial:
    """Regresión log-log del residuo contra el tiempo, con todos los puntos."""
    if len(t_h) < MIN_PUNTOS_TRAMO:
        raise SerieInvalida("pocos_puntos")
    r = stats.linregress(np.log(np.asarray(t_h, float)), np.log(np.asarray(residuo, float)))
    return Potencial(float(math.exp(r.intercept)), float(-r.slope), float(r.rvalue**2))


@dataclass(frozen=True)
class PrimerOrden:
    """R(t) = R∞ (1 − e^(−k t)): modelo NUESTRO, con meseta. `r2` es sobre la recuperación."""

    r_inf: float
    k_por_h: float
    r2: float

    def recuperacion(self, t: float) -> float:
        return self.r_inf * (1.0 - math.exp(-self.k_por_h * t))


def ajustar_primer_orden(t_h: Sequence[float], rec_pct: Sequence[float]) -> PrimerOrden:
    """Mínimos cuadrados de R∞ y k sobre todos los puntos."""
    t, r = np.asarray(t_h, dtype=float), np.asarray(rec_pct, dtype=float)
    if len(t) < MIN_PUNTOS_TRAMO:
        raise SerieInvalida("pocos_puntos")
    fit = least_squares(
        lambda p: p[0] * (1.0 - np.exp(-p[1] * t)) - r,
        [float(r.max()), 1.0 / float(np.median(t))],
        bounds=([0.0, 1e-6], [200.0, 1e3]),
        xtol=1e-14,
        ftol=1e-14,
        gtol=1e-14,
    )
    sse, sst = float(np.sum(fit.fun**2)), float(np.sum((r - r.mean()) ** 2))
    return PrimerOrden(float(fit.x[0]), float(fit.x[1]), 1.0 - sse / sst if sst > 0 else 0.0)


# ------------------------------------------------------------------ todos los modelos
@dataclass(frozen=True)
class Modelos:
    lineales: dict[str, AjusteLineal]
    potencial: Potencial | None
    primer_orden: PrimerOrden | None
    cabeza_ppb: float


def ajustar_modelos(
    t_h: Sequence[float], residuo: Sequence[float], cabeza: float, corte_h: float = T_CORTE_H
) -> Modelos:
    """Ajusta todos los modelos a una serie ya validada (con `balance`)."""
    rec = [recuperacion_pct(r, cabeza) for r in residuo]
    lin = {m: ajustar_lineal(m, t_h, rec, corte_h) for m in MODELOS_LINEALES}
    ok = len(t_h) >= MIN_PUNTOS_TRAMO
    return Modelos(
        lin,
        ajustar_potencial(t_h, residuo) if ok else None,
        ajustar_primer_orden(t_h, rec) if ok else None,
        cabeza,
    )


def recuperacion_modelo(modelos: Modelos, modelo: str, t: float) -> float | None:
    """Recuperación (%) que da `modelo` en t horas; None si ese modelo no se pudo ajustar ahí."""
    if modelo == "potencial":
        p = modelos.potencial
        return None if p is None else 100.0 * (1.0 - p.residuo(t) / modelos.cabeza_ppb)
    if modelo == "primer_orden":
        p1 = modelos.primer_orden
        return None if p1 is None else p1.recuperacion(t)
    aj = modelos.lineales[modelo]
    y = aj.recta(t)
    if y is None:
        return None
    return 100.0 * x_de_termino(modelo, y, B_N1 if t <= aj.corte_h else B_N2)


def curva(modelos: Modelos, modelo: str, ts: Sequence[float]) -> list[float | None]:
    return [recuperacion_modelo(modelos, modelo, float(t)) for t in ts]


def rmse_recuperacion(
    modelos: Modelos, modelo: str, t_h: Sequence[float], rec_pct: Sequence[float]
) -> float | None:
    """Error cuadrático medio (puntos de recuperación) del modelo sobre todos los puntos medidos."""
    pred = curva(modelos, modelo, t_h)
    if any(p is None for p in pred):
        return None
    return float(np.sqrt(np.mean((np.asarray(pred, float) - np.asarray(rec_pct, float)) ** 2)))


def recuperacion_en_cero(aj: AjusteLineal) -> float | None:
    """Recuperación (%) que da la recta del primer tramo en t = 0: con intercepto positivo, el
    modelo ya tiene disuelto ese oro antes de empezar."""
    if aj.tramo1 is None:
        return None
    return 100.0 * x_de_termino(aj.modelo, aj.tramo1.intercepto, B_N1)
