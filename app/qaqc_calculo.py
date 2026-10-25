"""Cálculo de la pestaña «Control de calidad», sin Streamlit: elige la serie (de ejemplo sintética
o la tabla del visitante), la valida en el servidor, llama a `muestreo.qaqc` y arma las vistas que
dibujan los gráficos. Todo lo que se ve sale de estos números."""

from __future__ import annotations

from dataclasses import dataclass

from muestreo import qaqc as qc
from muestreo import qaqc_datos as dd
from muestreo import qaqc_gemas as gemas

# Los valores de las listas de la barra lateral son rótulos en español (`opt` los traduce).
CRMS = (*(o.nombre for o in dd.OREAS), "CRM propio")
FUENTES = ("Serie sintética de ejemplo", "Tabla editable")
DUP_FUENTES = ("GEMAS: plata (Ag), no es oro", "GEMAS: germanio (Ge), no es oro", "Tabla editable")
DUP_TIPOS = ("Duplicado de campo", "Rechazo grueso", "Pulpa")
TIPO_CLAVE = dict(zip(DUP_TIPOS, ("campo", "rechazo", "pulpa"), strict=True))
PRECISIONES = ("10", "20")  # P de Thompson-Howarth, en %
GEMAS_PARES = {DUP_FUENTES[0]: ("Ag", gemas.AG_PARES), DUP_FUENTES[1]: ("Ge", gemas.GE_PARES)}
N_RANGO = (10, 200)  # largo de la serie sintética
MAX_CUADROS = 100  # cuadros del reproductor de la carta de control


@dataclass(frozen=True)
class QaqcParams:
    crm: str = CRMS[0]
    valor_propio: float = 1.0  # g/t, solo con «CRM propio»
    sd_propia: float = 0.04  # g/t, solo con «CRM propio»
    crm_fuente: str = FUENTES[0]
    n: int = 30
    sesgo: float = 0.0  # % de sesgo del ejemplo sintético
    dup_fuente: str = DUP_FUENTES[0]
    dup_tipo: str = DUP_TIPOS[0]
    dup_p: str = PRECISIONES[0]
    blk_fuente: str = FUENTES[0]
    ld: float = 0.005  # g/t
    pico: float = 4.0  # × LD del pico del ejemplo de blancos


def crm_de_params(p: QaqcParams) -> tuple[str, float, float, float | None]:
    """(nombre, certificado, SD con la que se calculan los límites, SD publicada o None). Los
    límites de OREAS se calculan con valor × 1RSD, como en su certificado."""
    if p.crm == CRMS[-1]:
        return p.crm, p.valor_propio, p.sd_propia, None
    o = dd.OREAS_BY_NAME[p.crm]
    return o.nombre, o.valor, o.sd_sin_redondear, o.sd


# ------------------------------------------------------------------ CRM
@dataclass(frozen=True)
class CrmView:
    nombre: str
    certificado: float
    sd: float
    sd_publicada: float | None
    sintetica: bool
    puntos: tuple[qc.PuntoCRM, ...]
    veredicto: qc.VeredictoCRM

    @property
    def lim2(self) -> tuple[float, float]:
        return qc.limites(self.certificado, self.sd, 2)

    @property
    def lim3(self) -> tuple[float, float]:
        return qc.limites(self.certificado, self.sd, 3)


def run_crm(p: QaqcParams, filas: list | None = None) -> CrmView:
    """Lanza `QaqcError` si la serie o el CRM no sirven."""
    nombre, valor, sd, sd_pub = crm_de_params(p)
    sintetica = p.crm_fuente == FUENTES[0]
    if sintetica:
        valores = dd.serie_crm_sintetica(valor, sd, p.n, p.sesgo)
    else:
        valores = qc.leer_serie(filas if filas is not None else [])
    puntos = qc.clasificar_crm(valores, valor, sd)
    return CrmView(nombre, valor, sd, sd_pub, sintetica, tuple(puntos),
                   qc.veredicto_crm(puntos, valor))  # fmt: skip


def cuadros(n: int) -> list[int]:
    """Los puntos hasta los que llega cada cuadro del reproductor: todos si son pocos, y como
    mucho `MAX_CUADROS` repartidos parejo, terminando siempre en el último."""
    if n <= MAX_CUADROS:
        return list(range(1, n + 1))
    return sorted({max(1, round(i * n / MAX_CUADROS)) for i in range(1, MAX_CUADROS + 1)} | {n})


# ------------------------------------------------------------------ duplicados
@dataclass(frozen=True)
class DupView:
    fuente: str
    elemento: str | None  # «Ag» o «Ge» con los datos de GEMAS; None con la tabla del visitante
    pares: tuple[tuple[float, float], ...]
    p_pct: float
    th: qc.ResultadoTH
    dup: qc.ResultadoDuplicados
    rpd: tuple[float | None, ...]  # por par; None si a + b = 0

    @property
    def es_gemas(self) -> bool:
        return self.elemento is not None


def run_dup(p: QaqcParams, filas: list | None = None) -> DupView:
    """Lanza `QaqcError` si los pares no sirven."""
    if p.dup_fuente in GEMAS_PARES:
        elemento, pares = GEMAS_PARES[p.dup_fuente]
    else:
        elemento, pares = None, qc.leer_pares(filas if filas is not None else [])
    p_pct = float(p.dup_p)
    th = qc.evaluar_th(pares, p_pct)
    dup = qc.evaluar_duplicados(pares, TIPO_CLAVE[p.dup_tipo])
    rpd = tuple(qc.rpd_pct(a, b) for a, b in pares)
    return DupView(p.dup_fuente, elemento, tuple(pares), p_pct, th, dup, rpd)


# ------------------------------------------------------------------ blancos
@dataclass(frozen=True)
class BlkView:
    sintetica: bool
    valores: tuple[float, ...]
    res: qc.ResultadoBlancos


def run_blk(p: QaqcParams, filas: list | None = None) -> BlkView:
    """Lanza `QaqcError` si los blancos o el límite de detección no sirven."""
    sintetica = p.blk_fuente == FUENTES[0]
    if sintetica:
        valores = dd.serie_blancos_sintetica(p.ld, p.n, p.pico)
    else:
        valores = qc.leer_serie(filas if filas is not None else [])
    return BlkView(sintetica, tuple(valores), qc.evaluar_blancos(valores, p.ld))


# ------------------------------------------------------------------ certificar un estándar
@dataclass(frozen=True)
class CertView:
    resultados: tuple[float, ...]
    cert: qc.Certificacion
    publicado: tuple[float, float]


def run_cert() -> CertView:
    return CertView(dd.CDN_RESULTADOS, qc.certificar_recorte(dd.CDN_RESULTADOS), dd.CDN_PUBLICADO)


# ------------------------------------------------------------------ tablas de partida
def tabla_crm(p: QaqcParams) -> list[float]:
    """La serie con la que arranca la tabla editable del CRM: la de ejemplo."""
    _, valor, sd, _ = crm_de_params(p)
    return dd.serie_crm_sintetica(valor, sd, p.n, p.sesgo)


def tabla_blancos(p: QaqcParams) -> list[float]:
    return dd.serie_blancos_sintetica(p.ld, p.n, p.pico)


def tabla_duplicados() -> list[tuple[float, float]]:
    return dd.duplicados_sinteticos()
