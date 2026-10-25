"""Control de calidad: las cifras publicadas que el módulo debe reproducir y los cortes, fijados
ANTES de correr.

- CDN-GS-2X: media 2,388 y «± 0,232» (2 SD) g/t, al redondeo publicado (±0,0005).
- OREAS 501b, 501c, 503c y 200: los intervalos de 2 SD y 3 SD de sus tablas de «performance gates»,
  a ±0,001 ppm, con la SD sin redondear (valor × 1RSD, como los calcula OREAS). Con la SD
  redondeada del certificado se muestra aparte cuántos intervalos no salen.
- GEMAS (Thompson-Howarth, 104 pares): conteos de pares dentro de las líneas a ±2 pares (los autores
  cuentan sobre el gráfico); y los coeficientes de la hoja de Excel del tutorial a 1e-4 relativo.
- Sesgos de Rainy River (Tabla 11-12) y Loma Larga (Tabla 11-3): a 0,1 punto porcentual, leídos de
  la imagen de cada tabla.

Las reglas de serie, de duplicados y de blancos NO se validan aquí: no hay cifra publicada que
reproducir (son pruebas unitarias contra la regla citada, en `tests/test_qaqc.py`).
"""

from __future__ import annotations

from dataclasses import dataclass

from . import qaqc as q
from . import qaqc_datos as d
from . import qaqc_gemas as g

TOL_CDN = 0.0005
TOL_OREAS = 0.001
TOL_GEMAS = 2
TOL_SESGO = 0.1
TOL_TH = 1e-4  # relativo
EPS = 1e-9
FUENTES = ("cdn", "oreas", "gemas", "th", "rr", "ll")
PARES = {"Ag": g.AG_PARES, "Ge": g.GE_PARES}


@dataclass(frozen=True)
class QaqcCheck:
    source: str  # uno de FUENTES
    label: str  # rótulo que no se traduce (nombre del CRM, elemento, fila)
    kind: str  # clave del tipo de cifra (qv.kind.<kind>)
    published: float
    calculated: float
    tol: float
    decimals: int

    @property
    def ok(self) -> bool:
        return abs(self.calculated - self.published) <= self.tol + EPS


def cdn_checks() -> list[QaqcCheck]:
    c = q.certificar_recorte(d.CDN_RESULTADOS)
    pub_m, pub_2sd = d.CDN_PUBLICADO
    return [
        QaqcCheck("cdn", "CDN-GS-2X", "media", pub_m, c.media, TOL_CDN, 4),
        QaqcCheck("cdn", "CDN-GS-2X", "dos_sd", pub_2sd, c.dos_sd, TOL_CDN, 4),
    ]


def oreas_checks(redondeada: bool = False) -> list[QaqcCheck]:
    """Los 16 intervalos de las cuatro tablas. `redondeada`: con la SD del certificado."""
    out = []
    for o in d.OREAS:
        sd = o.sd if redondeada else o.sd_sin_redondear
        calc = (*q.limites(o.valor, sd, 2), *q.limites(o.valor, sd, 3))
        for kind, pub, val in zip(("l2", "h2", "l3", "h3"), o.puertas, calc, strict=True):
            out.append(QaqcCheck("oreas", o.nombre, kind, pub, val, TOL_OREAS, 4))
    return out


def gemas_checks() -> list[QaqcCheck]:
    out = []
    for (el, p), (pub99, pub90) in d.GEMAS_PUBLICADO.items():
        r = q.evaluar_th(PARES[el], p)
        label = f"{el} ±{p} %"
        if pub99 is not None:
            out.append(QaqcCheck("gemas", label, "p99", pub99, r.dentro99, TOL_GEMAS, 0))
        out.append(QaqcCheck("gemas", label, "p90", pub90, r.dentro90, TOL_GEMAS, 0))
    return out


def th_checks() -> list[QaqcCheck]:
    out = []
    for p, (pub90, pub99) in d.TH_HOJA.items():
        for kind, z, pub in (("c90", q.Z_P90, pub90), ("c99", q.Z_P99, pub99)):
            out.append(
                QaqcCheck("th", f"P = {p} %", kind, pub, q.coeficiente_th(z, p), TOL_TH * pub, 6)
            )
    return out


def rr_checks() -> list[QaqcCheck]:
    return [
        QaqcCheck("rr", crm, "sesgo", pub, q.sesgo_pct(media, esp), TOL_SESGO, 2)
        for crm, _n, esp, media, pub, _rsd, _f in d.RAINY_RIVER
    ]


def ll_checks() -> list[QaqcCheck]:
    return [
        QaqcCheck("ll", crm, "sesgo", pub, q.sesgo_pct(obs, esp), TOL_SESGO, 2)
        for crm, _n, obs, _so, esp, _se, pub in d.LOMA_LARGA
    ]


def all_checks() -> list[QaqcCheck]:
    return [
        *cdn_checks(), *oreas_checks(), *gemas_checks(), *th_checks(), *rr_checks(), *ll_checks()
    ]  # fmt: skip


def summary(checks: list[QaqcCheck] | None = None) -> dict[str, tuple[int, int]]:
    """Por fuente: (cuántas cuadran, cuántas son)."""
    checks = all_checks() if checks is None else checks
    return {
        s: (sum(c.ok for c in checks if c.source == s), sum(c.source == s for c in checks))
        for s in FUENTES
    }
