"""Cálculo de la pestaña «Cianuración en botella», sin Streamlit: valida la tabla del visitante,
llama a `muestreo.cianuracion` y arma las vistas que dibujan los gráficos y la botella. Todo lo que
se ve sale de estos números."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from i18n import opt

from muestreo import cianuracion as c

MAX_FILAS, MIN_FILAS = 30, 1
T_MAX_H, PPB_MAX = 1000.0, 100_000.0  # límites razonables de la tabla
CURVA_PUNTOS = 97  # puntos por curva y fotogramas del indicador de la botella
TABLE_COLS = ("t", "sol", "res")
# El valor de la lista de la barra lateral es el rótulo en español (como en el resto de la app);
# `opt` lo traduce. El modelo que mueve el indicador es el de `muestreo.cianuracion`.
MODEL_LABELS = {
    "Potencial (Ec. 3 de los autores)": "potencial",
    "Primer orden con meseta (nuestro)": "primer_orden",
    "Difusión (L)": "difusion",
    "Reacción (M)": "reaccion",
    "Mixto (N)": "mixto",
}
LABEL_OF = {code: label for label, code in MODEL_LABELS.items()}


def model_name(code: str) -> str:
    """El nombre del modelo en el idioma de la app."""
    return opt(LABEL_OF[code])


@dataclass(frozen=True)
class CianParams:
    model: str = "potencial"
    rpm: float = 31.0  # procedimiento estándar: 30 a 32 rpm (Cetin et al., 2017)
    head: float = c.S0_PPB
    factor: float = c.F_SOLUCION
    split: float = c.T_CORTE_H


def leer_tabla(rows: list[list]) -> tuple[list[float], list[float], list[float]]:
    """Las filas (t, solución, residuo) de la tabla editable, validadas en el servidor: entre 1 y
    `MAX_FILAS` filas, números finitos y positivos, tiempos estrictamente crecientes y dentro de
    límites razonables. Lanza `SerieInvalida` con la clave del texto del problema."""
    if not MIN_FILAS <= len(rows) <= MAX_FILAS:
        raise c.SerieInvalida("filas", lo=MIN_FILAS, hi=MAX_FILAS)
    cols = [[r[i] for r in rows] for i in range(3)]
    for col in cols:
        if not all(_numero(x) for x in col):
            raise c.SerieInvalida("numero")
    t, sol, res = ([float(x) for x in col] for col in cols)
    if max(t) > T_MAX_H or max(sol) > PPB_MAX or max(res) > PPB_MAX:
        raise c.SerieInvalida("rango", t_max=T_MAX_H, ppb_max=PPB_MAX)
    c.validar_serie(t, sol, res)
    return t, sol, res


def _numero(x: object) -> bool:
    return isinstance(x, int | float) and not isinstance(x, bool) and math.isfinite(x) and x > 0


@dataclass(frozen=True)
class FilaModelo:
    """Una fila de la tabla de modelos: una recta de un tramo, o un modelo de todo el ensayo."""

    model: str
    tramo: int  # 1 o 2 en los lineales; 0 en el potencial y el primer orden
    n: int
    r2: float | None
    intercepto: float | None
    pendiente: float | None
    r_cero: float | None  # recuperación (%) que da la recta en t = 0
    rmse: float | None  # puntos de recuperación, sobre todos los puntos medidos


@dataclass(frozen=True)
class CianView:
    params: CianParams
    balance: c.Balance
    modelos: c.Modelos | None
    filas: tuple[FilaModelo, ...]
    usados: tuple[bool, ...]

    @property
    def tmax(self) -> float:
        return self.balance.t_h[-1]

    def grid(self) -> np.ndarray:
        """Tiempos de las curvas: de `CURVA_T_MIN_H` al último punto medido."""
        return np.linspace(min(c.CURVA_T_MIN_H, self.tmax), self.tmax, CURVA_PUNTOS)

    def curva(self, modelo: str) -> list[float | None]:
        return [] if self.modelos is None else c.curva(self.modelos, modelo, self.grid())

    def animada(self, modelo: str, k: int = CURVA_PUNTOS - 1) -> list[float]:
        """La recuperación (%, de 0 a 100) del modelo en k + 1 instantes parejos de 0 a tmax: lo
        que mueve el indicador de la botella. En t = 0 el potencial no existe y se dibuja en 0;
        donde el modelo no se pudo ajustar, el indicador conserva el valor anterior."""
        out: list[float] = []
        for i in range(k + 1):
            t = self.tmax * i / k
            r = None
            if self.modelos is not None and not (modelo == "potencial" and t == 0.0):
                r = c.recuperacion_modelo(self.modelos, modelo, t)
            if r is None:
                r = out[-1] if out else 0.0
            out.append(min(max(r, 0.0), 100.0))
        return out


def run_cian(p: CianParams, t: list[float], sol: list[float], res: list[float]) -> CianView:
    """Lanza `SerieInvalida` si los datos no sirven."""
    bal = c.balance(t, sol, res, p.head, p.factor)
    usados = tuple(c.puntos_usados(bal.recuperacion_pct))
    if len(t) < c.MIN_PUNTOS_TRAMO:
        return CianView(p, bal, None, (), usados)
    modelos = c.ajustar_modelos(t, res, p.head, p.split)
    return CianView(p, bal, modelos, _filas(modelos, bal), usados)


def _filas(modelos: c.Modelos, bal: c.Balance) -> tuple[FilaModelo, ...]:
    out: list[FilaModelo] = []
    for m in c.MODELOS_LINEALES:
        aj = modelos.lineales[m]
        rmse = c.rmse_recuperacion(modelos, m, bal.t_h, bal.recuperacion_pct)
        for tramo, reg in ((1, aj.tramo1), (2, aj.tramo2)):
            if reg is None:
                out.append(FilaModelo(m, tramo, 0, None, None, None, None, None))
                continue
            r0 = c.recuperacion_en_cero(aj) if tramo == 1 else None
            out.append(FilaModelo(m, tramo, reg.n, reg.r2, reg.intercepto, reg.pendiente, r0, rmse))
    p, po = modelos.potencial, modelos.primer_orden
    n = len(bal.t_h)
    out.append(
        FilaModelo(
            "potencial",
            0,
            n,
            p.r2,
            None,
            None,
            None,
            c.rmse_recuperacion(modelos, "potencial", bal.t_h, bal.recuperacion_pct),
        )
    )
    out.append(
        FilaModelo(
            "primer_orden",
            0,
            n,
            po.r2,
            None,
            None,
            None,
            c.rmse_recuperacion(modelos, "primer_orden", bal.t_h, bal.recuperacion_pct),
        )
    )
    return tuple(out)
