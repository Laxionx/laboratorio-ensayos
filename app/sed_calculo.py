"""Cálculo de la pestaña «Ensayo de sedimentación», sin Streamlit: valida la tabla del visitante,
llama a `muestreo.sedimentacion` y arma las vistas que dibujan los gráficos y la animación. Todo
lo que se ve sale de estos números."""

from __future__ import annotations

import math
from dataclasses import dataclass

from i18n import opt

from muestreo import sedimentacion as sd

MAX_FILAS, MIN_FILAS = 60, sd.MIN_FILAS
T_MAX_S, H_MAX_M = 172_800.0, 5.0  # límites razonables de la tabla (48 h y 5 m)
LUZ_T_MAX_S = 86_400.0  # la curva de Luz llega hasta las 24 h (la cota z∞ es la de esa hora)
LUZ_PUNTOS = 300
FRAMES = 97  # fotogramas de la animación (96 intervalos)
ANIM_FACTOR = 3.0  # la animación muestra de 0 a 3·tc
RHO_AGUA = sd.RHO_AGUA_T_M3

# Los valores de las listas de la barra lateral son rótulos en español (`opt` los traduce).
FUENTES = ("Modelo de Luz (ec. 1)", "Tabla editable")
COMPRESIONES = ("Punto dado (tc)", "Método de Roberts")
MODOS = ("Clásico (Hu del underflow)", "Vale modificado (cota a 24 h)")
FACTORES = ("Sin factor (1)", "Lamas de hierro de Vale (0,64)")
FACTOR_VALOR = {FACTORES[0]: 1.0, FACTORES[1]: sd.FACTOR_VALE_LAMAS}
TABLA_T_S = (0, 60, 120, 180, 240, 300, 360, 420, 540, 660, 780, 900, 1200, 1500, 3600, 86400)
LUZ_DEFECTO = (0.4, 0.035, 1.591, 203.0)  # z0 y z∞ (m): leídos de la Fig. 1; a y b: del artículo


@dataclass(frozen=True)
class SedParams:
    fuente: str = FUENTES[0]
    z0: float = LUZ_DEFECTO[0]
    z_inf: float = LUZ_DEFECTO[1]
    a: float = LUZ_DEFECTO[2]
    b: float = LUZ_DEFECTO[3]
    cma: float = 4.9  # % de sólidos en la alimentación (Fig. 1)
    cmu: float = 30.0  # % de sólidos en el underflow (Fig. 1)
    rho_s: float = 4.0  # t/m³: SUPUESTO declarado (el artículo no lo da)
    tc: float = 420.0  # s: inicio de compresión de la Fig. 1
    compresion: str = COMPRESIONES[0]
    modo: str = MODOS[0]
    tph: float = 157.0  # t/h de la Tabla 3
    factor: str = FACTORES[0]


def _numero(x: object) -> bool:
    return isinstance(x, int | float) and not isinstance(x, bool) and math.isfinite(x)


def tabla_de_luz() -> list[tuple[float, float]]:
    """La tabla precargada: la curva de Luz con sus parámetros por defecto, redondeada al 0,1 mm."""
    z0, zi, a, b = LUZ_DEFECTO
    return [(float(t), round(sd.luz_altura(t, z0, zi, a, b), 4)) for t in TABLA_T_S]


def leer_tabla(rows: list[list]) -> sd.CurvaSed:
    """La curva h(t) de la tabla editable, validada en el servidor: entre 4 y `MAX_FILAS` filas,
    números finitos, t ≥ 0 en orden creciente desde 0, alturas positivas que no suben."""
    if not MIN_FILAS <= len(rows) <= MAX_FILAS:
        raise sd.SedimentacionError("filas", lo=MIN_FILAS, hi=MAX_FILAS)
    cols = [[r[i] for r in rows] for i in range(2)]
    if not all(_numero(x) for col in cols for x in col):
        raise sd.SedimentacionError("numero")
    t, h = ([float(x) for x in col] for col in cols)
    if min(t) < 0 or min(h) <= 0 or max(t) > T_MAX_S or max(h) > H_MAX_M:
        raise sd.SedimentacionError("rango", t_max=T_MAX_S, h_max=H_MAX_M)
    return sd.CurvaSed(tuple(t), tuple(h))


@dataclass(frozen=True)
class SedView:
    params: SedParams
    curva: sd.CurvaSed
    c0: float
    cu: float
    h_inf: float
    tc_s: float
    tf: sd.TalmageFitch
    factor: float
    area_m2: float
    diametro_m: float
    kynch: sd.KynchPuntos | None
    g_limite: tuple[float, float] | None  # (G_L, C crítica)

    @property
    def area_unitaria_corregida(self) -> float:
        return self.tf.area_unitaria_m2_t_dia * self.factor

    @property
    def t_animacion_s(self) -> float:
        return min(self.curva.t_max, ANIM_FACTOR * self.tc_s)

    def alturas_animadas(self, k: int = FRAMES - 1) -> list[float]:
        """La cota de la interfase en k + 1 instantes parejos de 0 a `t_animacion_s`."""
        t_max = self.t_animacion_s
        return [self.curva.altura(t_max * i / k) for i in range(k + 1)]

    @property
    def y_area_flujo_limite(self) -> float | None:
        return None if self.g_limite is None else sd.area_flujo_limite_m2_t_dia(self.g_limite[0])


def curva_de_params(p: SedParams, rows: list[list] | None) -> tuple[sd.CurvaSed, float]:
    """(curva, h∞): la de Luz (z∞ es la cota a 24 h) o la tabla (h∞ es su última cota)."""
    if p.fuente == FUENTES[0]:
        curva = sd.curva_luz(p.z0, p.z_inf, p.a, p.b, LUZ_T_MAX_S, LUZ_PUNTOS)
        return curva, p.z_inf
    if rows is None:
        raise sd.SedimentacionError("filas", lo=MIN_FILAS, hi=MAX_FILAS)
    curva = leer_tabla(rows)
    return curva, curva.h_m[-1]


def run_sed(p: SedParams, rows: list[list] | None = None) -> SedView:
    """Lanza `SedimentacionError` si los datos no sirven."""
    curva, h_inf = curva_de_params(p, rows)
    if not p.cma < p.cmu:
        raise sd.SedimentacionError("conc")
    c0 = sd.concentracion_t_m3(p.cma / 100.0, p.rho_s)
    cu = sd.concentracion_t_m3(p.cmu / 100.0, p.rho_s)
    modo = "clasico" if p.modo == MODOS[0] else "vale"
    tc = p.tc if p.compresion == COMPRESIONES[0] else sd.roberts_punto_compresion(curva, h_inf)
    tf = sd.talmage_fitch(curva, c0, cu, tc, modo, h_inf)
    factor = FACTOR_VALOR[p.factor]
    area, diam = sd.dimensionar(tf.area_unitaria_m2_t_dia, p.tph, factor)
    k = sd.kynch(curva, c0)
    try:
        g_limite = sd.flujo_limite(k.c_t_m3, k.g_t_m2_h, cu) if k.c_t_m3 else None
    except sd.SedimentacionError:
        g_limite = None
    return SedView(p, curva, c0, cu, h_inf, tc, tf, factor, area, diam, k, g_limite)


def nombre(valor: str) -> str:
    """El rótulo de una opción de lista en el idioma de la app."""
    return opt(valor)
