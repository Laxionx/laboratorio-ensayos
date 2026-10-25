"""Copelación y partición: pérdida de plata y de oro en la copela, corrección de la ley y encuarte.

MODELO (simple y declarado; todo sale de las tablas de Bugbee 1922, ver `copelacion_datos`):

    pérdida de plata = IX(T) · [X(Pb) / X(10 g)] · [XI(Ag) / XI(200 mg)]

- IX(T): interpolación lineal de ln(pérdida) contra la temperatura (Tabla IX, Lodge: 200 mg de
  plata, 10 g de plomo, 700 a 1 000 °C). Fuera de ese rango NO se extrapola: se usa el valor del
  extremo y se avisa.
- X(Pb) / X(10): interpolación lineal de la pérdida contra el plomo (Tabla X, Lodge, 685 °C, 10 a
  25 g), relativa a la de 10 g. Fuera de 10 a 25 g, se queda en el extremo (aviso).
- XI(Ag) / XI(200): interpolación lineal de ln(pérdida) contra ln(plata) (Tabla XI, Godshall, 2 a
  200 mg), relativa a la de 200 mg. Fuera de 2 a 200 mg, se queda en el extremo (aviso).
SUPUESTO declarado: los tres efectos se MULTIPLICAN (separables). Las tablas no lo prueban: cada
una varía una sola cosa y las tres vienen de dos laboratorios distintos.

    pérdida de oro = XII(T)   (Tabla XII, Lodge: 200 mg de oro, 10 g de plomo, 775 a 1 075 °C)

El oro NO depende en el modelo del plomo ni de la plata: Bugbee dice que la pérdida de oro crece
al bajar su cantidad (p. 103) y que la plata la reduce (Smith, p. 103; la Fig. 41 es solo figura)
pero no da cifras. La pérdida de oro del modelo es, por eso, la de 200 mg de oro SIN plata: una
cota que subestima en cantidades chicas y sobrestima con plata presente.

INCERTIDUMBRE: reproducibilidad, no sesgo. Es la dispersión (sd de ln) de las tres series de
Godshall con ½ A.T. de plomo, que repitieron la misma medición con las mismas condiciones; la
pérdida se da con una banda multiplicativa ×/÷ exp(sd). Para el oro no hay dispersión publicada y
se usa la misma (SUPUESTO). La comparación con Godshall (`copelacion_validacion`) muestra que el
sesgo del modelo respecto de otro laboratorio es mayor que esta banda.

LEY CORREGIDA: ley corregida = ley medida / (1 − pérdida).

PARTICIÓN Y ENCUARTE (Bugbee p. 118, 121, 122; Rose): partir exige al menos 3 de plata por 1 de
oro; en perlas de mena conviene 8 a 10; Rose da la razón según el oro (de 20-30 a 1 con menos de
0,1 mg, a 2,5 a 1 con más de 50 mg). La plata que se agrega entra al botón ANTES de copelar, así
que también pierde plata: la que se agrega sale de resolver Ag_final = razón · Au_final.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Sequence
from dataclasses import dataclass

from scipy.optimize import brentq

from . import copelacion_datos as cd

# densidades de manual (g/cm³; NO son de Bugbee), solo para el volumen del dibujo
RHO_ORO, RHO_PLATA = 19.32, 10.49
MODOS_RAZON = ("rose", "minimo", "propia")
NUM_FRAMES_MIN = 2


class CopelacionError(ValueError):
    """Los datos no sirven. `code` es una clave de texto de la app; `args_` rellena sus campos."""

    def __init__(self, code: str, **args: float) -> None:
        super().__init__(code)
        self.code, self.args_ = code, args


def _finito(x: object) -> bool:
    return isinstance(x, int | float) and not isinstance(x, bool) and math.isfinite(x)


def _exigir(x: object, code: str, *, minimo: float = 0.0, estricto: bool = True) -> float:
    ok = _finito(x) and (x > minimo if estricto else x >= minimo)  # type: ignore[operator]
    if not ok:
        raise CopelacionError(code)
    return float(x)  # type: ignore[arg-type]


def _interpola(
    x: float, xs: Sequence[float], ys: Sequence[float], *, log_x: bool = False, log_y: bool = False
) -> tuple[float, bool]:
    """Interpolación lineal por tramos de ys sobre xs (crecientes); en los extremos NO extrapola
    (devuelve el valor del extremo) y avisa con el segundo valor (`True` = quedó en el extremo)."""
    fx = math.log if log_x else float
    fy = math.log if log_y else float
    if x <= xs[0] or x >= xs[-1]:
        edge = ys[0] if x <= xs[0] else ys[-1]
        return float(edge), x < xs[0] or x > xs[-1]
    for (x0, y0), (x1, y1) in itertools.pairwise(zip(xs, ys, strict=True)):
        if x0 <= x <= x1:
            f = (fx(x) - fx(x0)) / (fx(x1) - fx(x0))
            v = fy(y0) + f * (fy(y1) - fy(y0))
            return (math.exp(v) if log_y else v), False
    raise AssertionError("inalcanzable")  # pragma: no cover


# ------------------------------------------------------------------ las curvas del modelo
_T_IX = [r[2] for r in cd.TABLA_IX]
_L_IX = [r[3] for r in cd.TABLA_IX]
_PB_X = [r[1] for r in cd.TABLA_X]
_L_X = [r[3] for r in cd.TABLA_X]
_AG_XI = [a for a, _ in reversed(cd.TABLA_XI)]  # creciente
_L_XI = [p for _, p in reversed(cd.TABLA_XI)]
_T_XII = [r[2] for r in cd.TABLA_XII if r[3] is not None]
_L_XII = [r[3] for r in cd.TABLA_XII if r[3] is not None]
T_AG_RANGO = (_T_IX[0], _T_IX[-1])
T_AU_RANGO = (_T_XII[0], _T_XII[-1])
PB_RANGO = (_PB_X[0], _PB_X[-1])
AG_RANGO = (_AG_XI[0], _AG_XI[-1])


def _sd_ln_replicas() -> float:
    """sd de ln(pérdida) entre las tres series de Godshall con ½ A.T. de plomo, agrupada en las
    siete cantidades de plata (cada serie repite la medición)."""
    columnas = [
        [cd.GODSHALL_PRIMERA[i][1], cd.GODSHALL_SEGUNDA[i][1], cd.GODSHALL_TERCERA[i][1]]
        for i in range(len(cd.GODSHALL_PLATA_MG))
    ]
    var = []
    for col in columnas:
        logs = [math.log(v) for v in col]
        m = sum(logs) / len(logs)
        var.append(sum((v - m) ** 2 for v in logs) / (len(logs) - 1))
    return math.sqrt(sum(var) / len(var))


SD_LN = _sd_ln_replicas()
FACTOR_BANDA = math.exp(SD_LN)


@dataclass(frozen=True)
class Perdida:
    """Pérdida (fracción de 0 a 1) con su banda de reproducibilidad y los avisos de rango."""

    frac: float
    bajo: float
    alto: float
    avisos: tuple[str, ...] = ()

    @property
    def pct(self) -> float:
        return 100.0 * self.frac


def _perdida(frac: float, avisos: tuple[str, ...]) -> Perdida:
    return Perdida(frac, frac / FACTOR_BANDA, min(frac * FACTOR_BANDA, 1.0), avisos)


def factor_temperatura_plata(temp_c: float) -> tuple[float, bool]:
    """IX(T) en % (200 mg de plata, 10 g de plomo)."""
    return _interpola(temp_c, _T_IX, _L_IX, log_y=True)


def factor_plomo(plomo_g: float) -> tuple[float, bool]:
    """X(Pb) / X(10 g): cuánto cambia la pérdida con el plomo respecto de 10 g."""
    v, fuera = _interpola(plomo_g, _PB_X, _L_X)
    return v / _L_X[0], fuera


def factor_plata(plata_mg: float) -> tuple[float, bool]:
    """XI(Ag) / XI(200 mg): cuánto sube la pérdida al bajar la plata, respecto de 200 mg."""
    v, fuera = _interpola(plata_mg, _AG_XI, _L_XI, log_x=True, log_y=True)
    return v / _L_XI[-1], fuera


def perdida_plata(temp_c: float, plomo_g: float, plata_mg: float) -> Perdida:
    """Pérdida de plata en la copela. Con 0 mg de plata no hay nada que perder."""
    _exigir(temp_c, "temp", minimo=0.0)
    _exigir(plomo_g, "plomo")
    plata = _exigir(plata_mg, "plata", estricto=False)
    if plata == 0.0:
        return _perdida(0.0, ())
    base, f_t = factor_temperatura_plata(temp_c)
    k_pb, f_pb = factor_plomo(plomo_g)
    k_ag, f_ag = factor_plata(plata)
    avisos = tuple(n for n, f in (("temp", f_t), ("plomo", f_pb), ("plata", f_ag)) if f)
    return _perdida(min(base * k_pb * k_ag / 100.0, 0.99), avisos)


def perdida_oro(temp_c: float) -> Perdida:
    """Pérdida de oro en la copela (Tabla XII, 200 mg de oro sin plata). A 700 °C o menos el
    botón se congela (Bugbee): se avisa y se usa el valor de 775 °C."""
    _exigir(temp_c, "temp", minimo=0.0)
    v, fuera = _interpola(temp_c, _T_XII, _L_XII, log_y=True)
    avisos = ("congelado",) if temp_c <= cd.CONGELADO_C else (("temp",) if fuera else ())
    return _perdida(v / 100.0, avisos)


def ley_corregida(ley_medida: float, perdida: float) -> float:
    """ley corregida = ley medida / (1 − pérdida)."""
    _exigir(ley_medida, "ley", estricto=False)
    if not (_finito(perdida) and 0.0 <= perdida < 1.0):
        raise CopelacionError("perdida")
    return ley_medida / (1.0 - perdida)


# ------------------------------------------------------------------ encuarte
def razon_rose(oro_mg: float) -> float:
    """Razón plata:oro de Rose según el oro. Entre sus filas, interpolación lineal en ln-ln; con
    menos de 0,1 mg, la fila «20 o 30» (25) y con más de 50 mg, 2,5."""
    _exigir(oro_mg, "oro")
    xs, ys = [p[0] for p in cd.ROSE], [p[1] for p in cd.ROSE]
    return _interpola(oro_mg, xs, ys, log_x=True, log_y=True)[0]


def razon_objetivo(modo: str, oro_mg: float, razon_propia: float = 8.0) -> float:
    if modo == "rose":
        return razon_rose(oro_mg)
    if modo == "minimo":
        return cd.MINIMO_PARTIR
    if modo == "propia":
        return _exigir(razon_propia, "razon")
    raise CopelacionError("modo")


def estado_particion(razon: float) -> str:
    """«insuficiente» (menos de 2:1), «lamina» (de 2 a 3:1: solo parte si la aleación se lamina
    fina, como en lingote, y queda plata sin disolver), «lenta» (de 3 a 8:1: parte, con más ácido y
    tiempo) o «buena» (8:1 o más). Los umbrales llevan una tolerancia de 1e-9 por el redondeo del
    solucionador del encuarte."""
    margen = 1.0 + 1e-9
    if razon * margen < cd.LINGOTE_RAZON[0]:
        return "insuficiente"
    if razon * margen < cd.MINIMO_PARTIR:
        return "lamina"
    return "lenta" if razon * margen < cd.RECOMENDADO_MIN else "buena"


@dataclass(frozen=True)
class Copelacion:
    temp_c: float
    plomo_g: float
    oro_mg: float
    plata_presente_mg: float
    plata_agregada_mg: float
    razon_objetivo: float
    perdida_ag: Perdida
    perdida_au: Perdida

    @property
    def plata_total_mg(self) -> float:
        return self.plata_presente_mg + self.plata_agregada_mg

    @property
    def oro_final_mg(self) -> float:
        return self.oro_mg * (1.0 - self.perdida_au.frac)

    @property
    def plata_final_mg(self) -> float:
        return self.plata_total_mg * (1.0 - self.perdida_ag.frac)

    @property
    def perla_mg(self) -> float:
        return self.oro_final_mg + self.plata_final_mg

    @property
    def razon_final(self) -> float:
        return math.inf if self.oro_final_mg == 0 else self.plata_final_mg / self.oro_final_mg

    @property
    def estado(self) -> str:
        return estado_particion(self.razon_final)

    @property
    def oro_en_perla(self) -> float:
        return self.oro_final_mg / self.perla_mg

    @property
    def avisos(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(self.perdida_ag.avisos + self.perdida_au.avisos))


def _plata_a_agregar(temp_c: float, plomo_g: float, oro_final: float, presente: float,
                     razon: float) -> float:  # fmt: skip
    """Plata (mg) que hay que agregar para que, TRAS la copelación, quede `razon` · oro_final."""
    meta = razon * oro_final

    def exceso(total: float) -> float:
        return total * (1.0 - perdida_plata(temp_c, plomo_g, total).frac) - meta

    if exceso(presente) >= 0.0:
        return 0.0
    hi = max(2.0 * meta, 1.0)
    while exceso(hi) < 0.0:
        hi *= 2.0
    return brentq(exceso, presente, hi, xtol=1e-12, rtol=1e-12) - presente


def copelar(temp_c: float, plomo_g: float, oro_mg: float, plata_mg: float,
            modo: str = "rose", razon_propia: float = 8.0) -> Copelacion:  # fmt: skip
    """Copelación con encuarte: la plata que se agrega sale de la razón elegida."""
    _exigir(temp_c, "temp", minimo=0.0)
    _exigir(plomo_g, "plomo")
    oro = _exigir(oro_mg, "oro")
    presente = _exigir(plata_mg, "plata", estricto=False)
    razon = razon_objetivo(modo, oro, razon_propia)
    p_au = perdida_oro(temp_c)
    agregada = _plata_a_agregar(temp_c, plomo_g, oro * (1.0 - p_au.frac), presente, razon)
    total = presente + agregada
    return Copelacion(temp_c, plomo_g, oro, presente, agregada, razon,
                      perdida_plata(temp_c, plomo_g, total), p_au)  # fmt: skip


# ------------------------------------------------------------------ la animación sale de aquí
def volumen_cm3(plomo_mg: float, oro_mg: float, plata_mg: float, rho_plomo: float) -> float:
    """Volumen del botón (cm³) con las densidades dadas (las de oro y plata, de manual)."""
    return plomo_mg / 1000.0 / rho_plomo + oro_mg / 1000.0 / RHO_ORO + plata_mg / 1000.0 / RHO_PLATA


@dataclass(frozen=True)
class Cuadro:
    avance: float  # 0 a 1: ILUSTRATIVO (Bugbee solo da la curva minuto a minuto en la Fig. 40)
    plomo_mg: float
    oro_mg: float
    plata_mg: float
    perdida_acum: float  # fracción de la pérdida total ya ocurrida (forma de Rose, ver abajo)

    @property
    def masa_mg(self) -> float:
        return self.plomo_mg + self.oro_mg + self.plata_mg

    @property
    def ley_oro(self) -> float:
        """Fracción de oro en los metales preciosos del botón."""
        return self.oro_mg / (self.oro_mg + self.plata_mg) if self.oro_mg + self.plata_mg else 0.0


def perdida_acumulada(s: float, plomo_g: float, preciosos_mg: float) -> float:
    """Fracción de la pérdida total ocurrida cuando se ha oxidado la fracción `s` del plomo.

    FORMA cualitativa de Rose (Bugbee p. 101: «las pérdidas al principio son pequeñas mientras
    abundan los metales base que protegen la plata… la oxidación es máxima cuando la plata está
    casi pura»): la pérdida por plomo oxidado es proporcional a la fracción de preciosos del botón,
    m / (m + Pb_restante). Se integra y se normaliza para que en s = 1 valga 1: el TOTAL es el del
    cálculo; la curva entre 0 y 1 es ilustrativa."""
    m, pb = preciosos_mg, plomo_g * 1000.0
    if pb <= 0 or m <= 0:
        return s
    return math.log((m + pb) / (m + pb * (1.0 - s))) / math.log((m + pb) / m)


def trayectoria(c: Copelacion, n: int = 49) -> list[Cuadro]:
    """`n` cuadros del botón, del plomo entero a la perla. El plomo se oxida a ritmo constante
    (ilustrativo); la pérdida acumulada sigue `perdida_acumulada`; las masas de oro y de plata en
    cada cuadro, y la de la perla, son del cálculo."""
    if n < NUM_FRAMES_MIN:
        raise CopelacionError("cuadros")
    pb0 = c.plomo_g * 1000.0
    out = []
    for i in range(n):
        s = i / (n - 1)
        acum = perdida_acumulada(s, c.plomo_g, c.oro_mg + c.plata_total_mg)
        out.append(Cuadro(
            s, pb0 * (1.0 - s),
            c.oro_mg * (1.0 - c.perdida_au.frac * acum),
            c.plata_total_mg * (1.0 - c.perdida_ag.frac * acum), acum,
        ))  # fmt: skip
    return out
