"""Control de calidad de un lote de ensayos: materiales de referencia certificados (CRM),
duplicados, blancos y cómo se certifica un estándar. Cada regla lleva su cita; ninguna es mía.

Reglas y fuentes (las cifras publicadas que las comprueban están en `qaqc_validacion.py`):

- **CRM, un resultado fuera de ±3 SD = rechazo del lote; dos seguidos fuera de ±2 SD =
  re-ensayo.** Rainy River Mine, NI 43-101 (New Gold, firmado el 10-feb-2025), sec. 11, p. 97:
  «re-assaying assay batches where two consecutive CRMs occur outside two standard deviations, or
  one CRM occurred outside three standard deviations»; y p. 108: fuera de ±3 SD = falla que pide
  re-análisis. OREAS (certificados 501b, 501c, 503c y 200): los intervalos de 2 SD y 3 SD son
  «advertencia o rechazo para múltiples valores fuera de 2 SD, o rechazo para valores individuales
  fuera de 3 SD».
- **Tasa de fallas < 5 % por CRM** (fallas = fuera de ±3 SD, como en la Tabla 11-12 del informe):
  Rainy River, p. 97.
- **Un solo CRM: |X − μ| ≤ 2 σ** y, con buena calidad, 95 % de los puntos dentro de ±2 SD:
  Abzalov (2011), Applications and Experiences of Quality Control, InTech, cap. 29, Eq. 21
  (CC BY-SA 3.0).
- **Sesgo** = (media medida / valor certificado − 1) × 100 (Rainy River, Tabla 11-12; Loma Larga,
  Tabla 11-3).
- **HARD** = |a − b| / (a + b) en % (Abzalov 2011, Tabla 3; Shaw 1997); la diferencia relativa
  porcentual (RPD = AMPD) es el doble: |a − b| / ((a + b) / 2).
- **Duplicados**: campo y rechazo grueso, 80-85 % de los pares con RPD < 20 %; pulpa, 80 % de los
  pares dentro de 10 % (Stoker 2006, citado por Rainy River 2025, p. 103). El informe no da la
  fórmula del RPD: se toma la diferencia absoluta relativa a la media del par.
- **Thompson-Howarth**: líneas de percentil 90 y 99 de la diferencia absoluta de dos mediciones
  con precisión P a 95 % de confianza: |d| = z · √2 · (P / 2) · C, con z = 1,6449 y 2,5758 y C la
  media del par. El 90 % de los pares debe quedar bajo la primera y el 99 % bajo la segunda
  (Thompson y Howarth 1973; Demetriades y Argyraki 2025, DOI 10.5281/zenodo.15557648, CC BY 4.0,
  que da d90 = 0,11631 C y d99 = 0,182135 C para P = 10 %).
- **Blancos**: falla con más de 10 veces el límite de detección (Rainy River, p. 101; Loma Larga,
  sec. 11.3.2.2); más de 3 veces el límite es el indicador que el mismo informe cuenta aparte.
- **Certificar un estándar** (CDN Resource Laboratories, certificado CDN-GS-2X, 2021): media y SD
  de los resultados del round robin, se descarta lo que cae fuera de media ± 2 SD y se recalcula;
  el valor certificado es esa media y el intervalo, 2 SD de la media recalculada.

El módulo califica un lote contra esas reglas; no dice que el lote «cumple la norma».
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

MAX_FILAS = 2000  # tope declarado de filas de una tabla pegada
MIN_CERTIFICACION = 5  # un recorte a ±2 SD con menos resultados no dice nada

Z_P90, Z_P99 = 1.6449, 2.5758  # z de la hoja de Demetriades y Argyraki (2025)
PCT_P90, PCT_P99 = 90.0, 99.0  # % de pares que deben quedar bajo cada línea
FALLA_3SD_MAX = 0.05  # tasa de fallas aceptable: < 5 % por CRM (Rainy River)
FUERA_2SD_MAX = 0.05  # con buena calidad, 95 % dentro de ±2 SD (Abzalov, Eq. 21)
K_ALERTA, K_FALLA = 3.0, 10.0  # múltiplos del límite de detección de los blancos

# estado de cada punto de un CRM
OK, FUERA_2SD, DOS_SEGUIDOS, FUERA_3SD = "ok", "fuera_2sd", "dos_seguidos", "fuera_3sd"
ESTADOS = (OK, FUERA_2SD, DOS_SEGUIDOS, FUERA_3SD)


class QaqcError(ValueError):
    """Los datos no sirven. `code` es una clave de texto de la app; `args_` rellena sus campos."""

    def __init__(self, code: str, **args: float) -> None:
        super().__init__(code)
        self.code, self.args_ = code, args


def _numero(x: object) -> bool:
    return isinstance(x, int | float) and not isinstance(x, bool) and math.isfinite(x)


def _vacio(x: object) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))


def leer_serie(filas: Sequence[object], minimo: int = 1) -> list[float]:
    """Una columna pegada, validada en el servidor. Las celdas vacías (y NaN) se descartan; hay
    que quedar con entre `minimo` y `MAX_FILAS` resultados, todos números finitos y no negativos
    (un ensayo no es negativo). Ningún texto del visitante vuelve en el error."""
    if len(filas) > MAX_FILAS * 2:  # no se recorre una tabla absurda
        raise QaqcError("filas", lo=minimo, hi=MAX_FILAS)
    datos = [x for x in filas if not _vacio(x)]
    if not minimo <= len(datos) <= MAX_FILAS:
        raise QaqcError("filas", lo=minimo, hi=MAX_FILAS)
    if not all(_numero(x) for x in datos):
        raise QaqcError("numero")
    if any(x < 0 for x in datos):
        raise QaqcError("negativo")
    return [float(x) for x in datos]


def leer_pares(filas: Sequence[Sequence[object]], minimo: int = 1) -> list[tuple[float, float]]:
    """Dos columnas pegadas (original y duplicado). Se descartan las filas del todo vacías; una
    fila con una sola celda llena es un error. Mismas reglas que `leer_serie`."""
    if len(filas) > MAX_FILAS * 2:
        raise QaqcError("filas", lo=minimo, hi=MAX_FILAS)
    llenas = [f for f in filas if not all(_vacio(x) for x in f)]
    if not minimo <= len(llenas) <= MAX_FILAS:
        raise QaqcError("filas", lo=minimo, hi=MAX_FILAS)
    if any(_vacio(x) for f in llenas for x in f):
        raise QaqcError("incompleta")
    if not all(_numero(x) for f in llenas for x in f):
        raise QaqcError("numero")
    if any(x < 0 for f in llenas for x in f):
        raise QaqcError("negativo")
    return [(float(f[0]), float(f[1])) for f in llenas]


# ------------------------------------------------------------------ CRM
def limites(valor: float, sd: float, k: float) -> tuple[float, float]:
    """El intervalo valor ± k SD (k = 2: advertencia; k = 3: rechazo)."""
    return valor - k * sd, valor + k * sd


def sesgo_pct(media: float, esperado: float) -> float:
    """(media medida / valor certificado − 1) × 100 (Rainy River, Tabla 11-12)."""
    return (media / esperado - 1.0) * 100.0


@dataclass(frozen=True)
class PuntoCRM:
    n: int  # posición en la serie (desde 1)
    valor: float
    z: float  # (valor − certificado) / SD
    estado: str  # uno de ESTADOS


def clasificar_crm(valores: Sequence[float], certificado: float, sd: float) -> list[PuntoCRM]:
    """El estado de cada resultado cuando llega: fuera de ±3 SD (rechazo del lote); fuera de ±2
    SD con el anterior también fuera de ±2 SD (re-ensayo, regla de Rainy River); fuera de ±2 SD
    solo (advertencia). «Fuera» es estrictamente más allá: |X − μ| ≤ 2 σ es aceptable."""
    if not (_numero(certificado) and _numero(sd) and sd > 0):
        raise QaqcError("crm")
    puntos: list[PuntoCRM] = []
    anterior_fuera = False
    for i, x in enumerate(valores, start=1):
        z = (x - certificado) / sd
        if abs(z) > 3.0:
            estado = FUERA_3SD
        elif abs(z) > 2.0:
            estado = DOS_SEGUIDOS if anterior_fuera else FUERA_2SD
        else:
            estado = OK
        anterior_fuera = abs(z) > 2.0
        puntos.append(PuntoCRM(i, float(x), z, estado))
    return puntos


# veredictos del lote
PASA, AVISO, REENSAYAR, RECHAZAR = "pasa", "aviso", "reensayar", "rechazar"


@dataclass(frozen=True)
class VeredictoCRM:
    n: int
    n_fuera_2sd: int  # fuera de ±2 SD, sean advertencia o parte de un par
    n_fuera_3sd: int
    n_pares: int  # resultados que cierran un par seguido fuera de ±2 SD
    tasa_3sd: float
    frac_fuera_2sd: float
    media: float
    sesgo_pct: float
    veredicto: str


def veredicto_crm(puntos: Sequence[PuntoCRM], certificado: float) -> VeredictoCRM:
    """Rechazo si algún resultado cae fuera de ±3 SD; re-ensayo si dos seguidos caen fuera de ±2
    SD; aviso si más del 5 % de los resultados cae fuera de ±2 SD (se espera ≤ 5 %); si no, pasa."""
    if not puntos:
        raise QaqcError("filas", lo=1, hi=MAX_FILAS)
    n = len(puntos)
    f3 = sum(p.estado == FUERA_3SD for p in puntos)
    pares = sum(p.estado == DOS_SEGUIDOS for p in puntos)
    f2 = sum(abs(p.z) > 2.0 for p in puntos)
    media = sum(p.valor for p in puntos) / n
    if f3:
        v = RECHAZAR
    elif pares:
        v = REENSAYAR
    elif f2 / n > FUERA_2SD_MAX:
        v = AVISO
    else:
        v = PASA
    return VeredictoCRM(n, f2, f3, pares, f3 / n, f2 / n, media, sesgo_pct(media, certificado), v)


# ------------------------------------------------------------------ certificar un estándar
@dataclass(frozen=True)
class Certificacion:
    n_total: int
    media_total: float
    sd_total: float
    k: float
    bajo: float
    alto: float
    retenidos: tuple[bool, ...]
    n: int
    media: float
    sd: float

    @property
    def dos_sd(self) -> float:
        """El intervalo publicado: 2 SD de los resultados que quedan."""
        return 2.0 * self.sd


def certificar_recorte(valores: Sequence[float], k: float = 2.0) -> Certificacion:
    """Valor certificado por recorte a ±k SD en UNA pasada (CDN-GS-2X): media y SD de todos los
    resultados; se descarta lo que cae fuera de media ± k SD; se recalculan media y SD."""
    if not MIN_CERTIFICACION <= len(valores) <= MAX_FILAS:
        raise QaqcError("filas", lo=MIN_CERTIFICACION, hi=MAX_FILAS)
    x = np.asarray(valores, dtype=float)
    if not np.all(np.isfinite(x)):
        raise QaqcError("numero")
    m0, s0 = float(x.mean()), float(x.std(ddof=1))
    bajo, alto = m0 - k * s0, m0 + k * s0
    keep = (x >= bajo) & (x <= alto)
    if keep.sum() < 2:
        raise QaqcError("recorte")
    y = x[keep]
    return Certificacion(
        len(x), m0, s0, k, bajo, alto, tuple(bool(b) for b in keep), int(keep.sum()),
        float(y.mean()), float(y.std(ddof=1)),
    )  # fmt: skip


# ------------------------------------------------------------------ duplicados
def hard_pct(a: float, b: float) -> float | None:
    """HARD = |a − b| / (a + b) en % (Abzalov 2011). None si a + b = 0 (no se puede evaluar)."""
    s = a + b
    return None if s <= 0 else 100.0 * abs(a - b) / s


def rpd_pct(a: float, b: float) -> float | None:
    """Diferencia relativa porcentual |a − b| / ((a + b)/2): el doble del HARD."""
    h = hard_pct(a, b)
    return None if h is None else 2.0 * h


def coeficiente_th(z: float, p_pct: float) -> float:
    """z · √2 · (P / 2), con P en %: la línea es coeficiente × C (P = 10 %, z = 1,6449: 0,11631)."""
    return z * math.sqrt(2.0) * (p_pct / 100.0 / 2.0)


def linea_th(media: float, p_pct: float, z: float) -> float:
    return coeficiente_th(z, p_pct) * media


@dataclass(frozen=True)
class ResultadoTH:
    n: int
    p_pct: float
    dentro90: int
    dentro99: int
    sin_media: int  # pares con media ≤ 0: no tienen línea y cuentan como fuera

    @property
    def pct90(self) -> float:
        return 100.0 * self.dentro90 / self.n

    @property
    def pct99(self) -> float:
        return 100.0 * self.dentro99 / self.n

    @property
    def pasa(self) -> bool:
        return self.pct90 >= PCT_P90 and self.pct99 >= PCT_P99


def evaluar_th(pares: Sequence[tuple[float, float]], p_pct: float) -> ResultadoTH:
    """Cuántos pares quedan dentro de cada línea (|d| ≤ línea). Un par con media ≤ 0 no tiene
    línea: cuenta como fuera, igual que el recuento publicado del tutorial."""
    if not pares:
        raise QaqcError("filas", lo=1, hi=MAX_FILAS)
    if not _numero(p_pct) or p_pct <= 0:
        raise QaqcError("precision")
    d90 = d99 = sin = 0
    for a, b in pares:
        c = (a + b) / 2.0
        if c <= 0:
            sin += 1
            continue
        d = abs(a - b)
        d90 += d <= linea_th(c, p_pct, Z_P90)
        d99 += d <= linea_th(c, p_pct, Z_P99)
    return ResultadoTH(len(pares), p_pct, d90, d99, sin)


@dataclass(frozen=True)
class UmbralDuplicado:
    rpd_max: float  # % de diferencia relativa
    estricto: bool  # «menos de» (True) o «dentro de» (False)
    minimo_pct: float  # % de pares que deben quedar bajo el umbral


# Stoker (2006) vía Rainy River 2025, p. 103: se toma el extremo bajo del rango 80-85 %
UMBRALES: dict[str, UmbralDuplicado] = {
    "campo": UmbralDuplicado(20.0, True, 80.0),
    "rechazo": UmbralDuplicado(20.0, True, 80.0),
    "pulpa": UmbralDuplicado(10.0, False, 80.0),
}


@dataclass(frozen=True)
class ResultadoDuplicados:
    tipo: str
    n: int  # pares
    n_evaluables: int  # pares con a + b > 0
    n_bajo: int
    hard_medio: float  # HARD medio de los pares evaluables (%)
    umbral: UmbralDuplicado

    @property
    def pct_bajo(self) -> float:
        return 100.0 * self.n_bajo / self.n_evaluables

    @property
    def pasa(self) -> bool:
        return self.pct_bajo >= self.umbral.minimo_pct


def evaluar_duplicados(pares: Sequence[tuple[float, float]], tipo: str) -> ResultadoDuplicados:
    """El % de pares con RPD bajo el umbral de su tipo (campo, rechazo grueso o pulpa)."""
    if tipo not in UMBRALES:
        raise QaqcError("tipo")
    u = UMBRALES[tipo]
    rpd = [r for a, b in pares if (r := rpd_pct(a, b)) is not None]
    if not rpd:
        raise QaqcError("sin_pares")
    bajo = sum(r < u.rpd_max if u.estricto else r <= u.rpd_max for r in rpd)
    return ResultadoDuplicados(tipo, len(pares), len(rpd), bajo, sum(rpd) / len(rpd) / 2.0, u)


# ------------------------------------------------------------------ blancos
BLANCO_OK, BLANCO_ALERTA, BLANCO_FALLA = "pasa", "alerta", "falla"


@dataclass(frozen=True)
class ResultadoBlancos:
    n: int
    ld: float
    n_sobre_3: int
    n_sobre_10: int
    veredicto: str

    @property
    def pct_sobre_3(self) -> float:
        return 100.0 * self.n_sobre_3 / self.n

    @property
    def pct_sobre_10(self) -> float:
        return 100.0 * self.n_sobre_10 / self.n


def evaluar_blancos(valores: Sequence[float], ld: float) -> ResultadoBlancos:
    """Falla si algún blanco supera 10 × LD (Rainy River, Loma Larga); alerta si supera 3 × LD
    (el indicador que Rainy River cuenta aparte); si no, pasa. «Supera» es estrictamente más."""
    if not valores:
        raise QaqcError("filas", lo=1, hi=MAX_FILAS)
    if not (_numero(ld) and ld > 0):
        raise QaqcError("ld")
    s3 = sum(x > K_ALERTA * ld for x in valores)
    s10 = sum(x > K_FALLA * ld for x in valores)
    v = BLANCO_FALLA if s10 else BLANCO_ALERTA if s3 else BLANCO_OK
    return ResultadoBlancos(len(valores), ld, s3, s10, v)
