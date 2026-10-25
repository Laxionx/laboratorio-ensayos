"""Validación de la copelación contra Godshall (1896), un experimentador distinto de Lodge.

CORTES Y PROTOCOLO, FIJADOS ANTES DE CORRER (el modelo se ajusta con Lodge: Tablas IX, X y XII; la
plata presente sale de la Tabla XI, que es de Godshall, y por eso NO es independiente):

1. SOLAPAMIENTO. El modelo cubre T de 700 a 1 000 °C, plomo de 10 a 25 g, plata de 2 a 200 mg. Las
   condiciones de Godshall son: plata de 2 a 200 mg, plomo de ¼, ½, ¾ y 1 A.T. (7,29; 14,58; 21,88
   y 29,17 g) y temperatura NO medida. Solo se solapan, por lo tanto, las celdas con 200 mg de
   plata (la única cantidad de plata de las tablas de Lodge) y plomo de ½ y ¾ A.T. (dentro de
   10 a 25 g): 2 celdas del promedio final, y con la temperatura SUPUESTA (ver 2). Las demás celdas
   no son una validación cuantitativa: se informan solo como tendencia (3).
2. VALIDACIÓN CUANTITATIVA (n = 2). Pérdida de plata predicha por el modelo (Lodge) con T = 740 °C
   (centro de 700 a 775 °C, el intervalo de la Tabla IX con cristales de PbO, que es lo que
   Godshall describe con «calor bajo»; elegido ANTES de ver el resultado) contra el promedio final
   de Godshall. Corte: error relativo dentro de ±25 % en las 2 celdas. Si falla, falla (xfail
   estricto): no se ajusta nada para que pase. Se informa también, como diagnóstico y no como
   validación, la temperatura que haría coincidir al modelo con cada celda.
3. TENDENCIAS (las 28 celdas del promedio final). (a) la pérdida de plata es mayor con 2 mg que con
   200 mg en cada uno de los 4 plomos (4 de 4); (b) la pérdida con 1 A.T. supera a la de ¼ A.T. en
   cada cantidad de plata (7 de 7); (c) la predicha cae a menos de un factor 2 de la publicada
   (28 de 28), con la temperatura de (2). La tendencia (a) no es independiente (la plata sale de
   Godshall) y se rotula así.
4. RÉPLICA DE LA PLATA (informativa, sin corte previo de aprobación): la razón pérdida(Ag) /
   pérdida(200 mg) del modelo contra la de las series primera y tercera de Godshall con ½ A.T.
   (la segunda es la que ajustó el factor). Se cuenta cuántas de 12 razones caen a ±25 %.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

from . import copelacion as cp
from . import copelacion_datos as cd

T_VALIDACION_C = 740.0  # fijada antes de correr (ver 2)
CORTE_RELATIVO = 0.25
FACTOR_ORDEN = 2.0
PLOMO_RANGO_G = cp.PB_RANGO


def plomo_g(at: float) -> float:
    return at * cd.A_T_G


@dataclass(frozen=True)
class Celda:
    plata_mg: float
    plomo_at: float
    publicada: float  # %
    predicha: float  # % con T_VALIDACION_C

    @property
    def plomo_g(self) -> float:
        return plomo_g(self.plomo_at)

    @property
    def error_relativo(self) -> float:
        return self.predicha / self.publicada - 1.0

    @property
    def solapa(self) -> bool:
        """Solapan con las tablas de Lodge: 200 mg de plata y plomo dentro de 10 a 25 g."""
        return (
            self.plata_mg == cd.TABLA_IX[0][0]
            and PLOMO_RANGO_G[0] <= self.plomo_g <= PLOMO_RANGO_G[1]
        )

    @property
    def cuadra(self) -> bool:
        return abs(self.error_relativo) <= CORTE_RELATIVO

    @property
    def temp_implicita_c(self) -> float | None:
        """T (°C) con la que el modelo daría la cifra publicada, si cae en 700 a 1 000 °C."""
        k = cp.factor_plomo(self.plomo_g)[0] * cp.factor_plata(self.plata_mg)[0]
        objetivo = self.publicada / k  # % de la Tabla IX
        t, ls = cp.T_AG_RANGO, [r[3] for r in cd.TABLA_IX]
        if not ls[0] <= objetivo <= ls[-1]:
            return None
        ts = [r[2] for r in cd.TABLA_IX]
        for (t0, l0), (t1, l1) in itertools.pairwise(zip(ts, ls, strict=True)):
            if l0 <= objetivo <= l1:
                f = (math.log(objetivo) - math.log(l0)) / (math.log(l1) - math.log(l0))
                return t0 + f * (t1 - t0)
        return t[0]  # pragma: no cover


def celdas_finales() -> list[Celda]:
    out = []
    for i, ag in enumerate(cd.GODSHALL_PLATA_MG):
        for j, at in enumerate(cd.GODSHALL_PLOMO_AT):
            pred = 100.0 * cp.perdida_plata(T_VALIDACION_C, plomo_g(at), ag).frac
            out.append(Celda(ag, at, cd.GODSHALL_FINAL[i][j], pred))
    return out


def celdas_cuantitativas() -> list[Celda]:
    return [c for c in celdas_finales() if c.solapa]


@dataclass(frozen=True)
class Tendencias:
    plata_mas_pierde: tuple[int, int]  # (cuántas, de cuántas)
    plomo_mas_pierde: tuple[int, int]
    orden_de_magnitud: tuple[int, int]


def tendencias() -> Tendencias:
    cells = celdas_finales()
    pb_at = cd.GODSHALL_PLOMO_AT
    a = sum(
        cd.GODSHALL_FINAL[0][j] > cd.GODSHALL_FINAL[-1][j]
        and cp.perdida_plata(T_VALIDACION_C, plomo_g(at), 2.0).frac
        > cp.perdida_plata(T_VALIDACION_C, plomo_g(at), 200.0).frac
        for j, at in enumerate(pb_at)
    )
    b = sum(
        cd.GODSHALL_FINAL[i][-1] > cd.GODSHALL_FINAL[i][0]
        and cp.perdida_plata(T_VALIDACION_C, plomo_g(pb_at[-1]), ag).frac
        > cp.perdida_plata(T_VALIDACION_C, plomo_g(pb_at[0]), ag).frac
        for i, ag in enumerate(cd.GODSHALL_PLATA_MG)
    )
    c = sum(1.0 / FACTOR_ORDEN <= x.predicha / x.publicada <= FACTOR_ORDEN for x in cells)
    return Tendencias((a, len(pb_at)), (b, len(cd.GODSHALL_PLATA_MG)), (c, len(cells)))


@dataclass(frozen=True)
class RazonPlata:
    serie: str
    plata_mg: float
    publicada: float  # pérdida(Ag) / pérdida(200 mg), de la serie
    modelo: float

    @property
    def cuadra(self) -> bool:
        return abs(self.modelo / self.publicada - 1.0) <= CORTE_RELATIVO


def razones_de_plata() -> list[RazonPlata]:
    """Réplica de la plata con las series primera y tercera (½ A.T.): 6 razones cada una."""
    out = []
    for nombre, serie in (("primera", cd.GODSHALL_PRIMERA), ("tercera", cd.GODSHALL_TERCERA)):
        ref = serie[-1][1]
        for i, ag in enumerate(cd.GODSHALL_PLATA_MG[:-1]):
            out.append(RazonPlata(nombre, ag, serie[i][1] / ref, cp.factor_plata(ag)[0]))
    return out


def cita_tabla_xi() -> list[tuple[float, float, float]]:
    """(plata, Bugbee Tabla XI, Godshall segunda serie ½ A.T.): lo que imprime Bugbee contra el
    artículo original. Solo difiere la celda de 50 mg (2,65 contra 2,67)."""
    segunda = {ag: cd.GODSHALL_SEGUNDA[i][1] for i, ag in enumerate(cd.GODSHALL_PLATA_MG)}
    return [(ag, perd, segunda[ag]) for ag, perd in cd.TABLA_XI]
