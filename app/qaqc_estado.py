"""Indicadores, «Estado de la operación» y «Prueba esto» de la pestaña Control de calidad. El panel
reúne los veredictos que cada sección ya calculaba (CRM, duplicados, blancos y la certificación del
estándar CDN-GS-2X) con las reglas y fuentes que `muestreo.qaqc` cita una por una (Rainy River
2025, OREAS, Abzalov 2011, Thompson y Howarth 1973, Demetriades y Argyraki 2025, Stoker 2006, Loma
Larga, CDN). No hay caso publicado que se mapee exacto a los controles: la serie del CRM y los pares
de duplicados son sintéticos o de GEMAS, y la certificación del estándar ya muestra lo publicado
junto a lo calculado en su propia sección. Los experimentos parten del ejemplo de la barra lateral
(los valores por defecto de `controles.DATOS`) y llevan números calculados en vivo."""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache

import streamlit as st
from controles import reset_to_example
from dibujo import es
from estado import Experimento, Fila, Prueba, controles_de, indicadores, panel, peor, pruebas
from i18n import int_num, opt, t, use
from qaqc_calculo import (
    BlkView,
    CertView,
    CrmView,
    DupView,
    QaqcParams,
    coincide,
    run_blk,
    run_cert,
    run_crm,
    run_dup,
)

from muestreo import qaqc as qc

NIVEL_CRM = {qc.PASA: "ok", qc.AVISO: "aviso", qc.REENSAYAR: "aviso", qc.RECHAZAR: "mal"}
NIVEL_BLK = {qc.BLANCO_OK: "ok", qc.BLANCO_ALERTA: "aviso", qc.BLANCO_FALLA: "mal"}
CLAVE_BLK = {qc.BLANCO_OK: "pasa", qc.BLANCO_ALERTA: "alerta", qc.BLANCO_FALLA: "falla"}


def texto_crm(v: CrmView) -> str:
    r = v.veredicto
    pct = 100 * (r.tasa_3sd if r.veredicto == qc.RECHAZAR else r.frac_fuera_2sd)
    return t(
        f"qc.crm.v.{r.veredicto}",
        n=int_num(r.n),
        f2=int_num(r.n_fuera_2sd),
        f3=int_num(r.n_fuera_3sd),
        pares=int_num(r.n_pares),
        pct=es(pct, 1),
    )


def texto_th(p: QaqcParams, v: DupView) -> str:
    th = v.th
    clave = "pasa" if th.pasa else "falla"
    return t(f"qc.dup.v.th.{clave}", p=es(v.p_pct, 0), pct90=es(th.pct90, 1), pct99=es(th.pct99, 1))


def texto_dup(p: QaqcParams, v: DupView) -> str:
    d, u = v.dup, v.dup.umbral
    clave = "pasa" if d.pasa else "falla"
    return t(
        f"qc.dup.v.dup.{clave}",
        tipo=opt(p.dup_tipo).lower(),
        pct=es(d.pct_bajo, 1),
        n=int_num(d.n_evaluables),
        u=es(u.rpd_max, 0),
        min=es(u.minimo_pct, 0),
        rule=t("qc.dup.rule.lt" if u.estricto else "qc.dup.rule.le"),
        hard=es(d.hard_medio, 1),
    )


def texto_blk(v: BlkView) -> str:
    r = v.res
    return t(
        f"qc.blk.v.{CLAVE_BLK[r.veredicto]}",
        s3=int_num(r.n_sobre_3),
        s10=int_num(r.n_sobre_10),
        pct3=es(r.pct_sobre_3, 1),
        pct10=es(r.pct_sobre_10, 1),
    )


def filas_qaqc(
    p: QaqcParams,
    crm: CrmView | None,
    dup: DupView | None,
    blk: BlkView | None,
    cert: CertView | None,
) -> list[Fila]:
    """Los chequeos del panel; una sección cuya tabla no sirve no aporta fila (ya avisó arriba)."""
    filas: list[Fila] = []
    if crm is not None:
        filas.append(Fila(NIVEL_CRM[crm.veredicto.veredicto], texto_crm(crm), t("qc.src.crm")))
    if dup is not None:
        filas.append(Fila("ok" if dup.th.pasa else "aviso", texto_th(p, dup), t("qc.src.th")))
        filas.append(Fila("ok" if dup.dup.pasa else "aviso", texto_dup(p, dup), t("qc.src.dup")))
    if blk is not None:
        filas.append(Fila(NIVEL_BLK[blk.res.veredicto], texto_blk(blk), t("qc.src.blk")))
    if cert is not None:
        ok = coincide(cert.cert, cert.publicado)
        filas.append(
            Fila(
                "ok" if ok else "aviso",
                t(
                    "qc.chk.cert.ok" if ok else "qc.chk.cert.mal",
                    m=es(cert.cert.media, 3),
                    band=es(cert.cert.dos_sd, 3),
                ),
                t("qc.src.cert"),
            )
        )
    return filas


def indicadores_qaqc(
    crm: CrmView | None, dup: DupView | None, blk: BlkView | None
) -> list[tuple[str, str, str]]:
    nada = "–"
    crm_v = nada if crm is None else t("qc.verd." + crm.veredicto.veredicto)
    dup_v = nada if dup is None else f"{es(dup.dup.pct_bajo, 1)} %"
    blk_v = nada if blk is None else f"{int_num(blk.res.n_sobre_3)} / {int_num(blk.res.n)}"
    return [
        (t("qc.i.crm"), crm_v, t("qc.i.crm.help")),
        (t("qc.i.dup"), dup_v, t("qc.i.dup.help")),
        (t("qc.i.blk"), blk_v, t("qc.i.blk.help")),
    ]


# ------------------------------------------------------------------ prueba esto
@dataclass(frozen=True)
class ResQc:
    n_fuera_3sd: int
    n_fuera_2sd: int
    sesgo: float  # %
    pct90: float
    pct99: float
    n_sobre_10: int
    veredicto: str  # del CRM
    veredicto_blk: str
    nivel: str


def evaluar_qaqc(**mod: object) -> ResQc:
    p = replace(QaqcParams(), **mod)  # type: ignore[arg-type]
    crm, dup, blk, cert = run_crm(p), run_dup(p), run_blk(p), run_cert()
    r = crm.veredicto
    with use("es"):
        nivel = peor(filas_qaqc(p, crm, dup, blk, cert))
    return ResQc(
        r.n_fuera_3sd,
        r.n_fuera_2sd,
        r.sesgo_pct,
        dup.th.pct90,
        dup.th.pct99,
        blk.res.n_sobre_10,
        r.veredicto,
        blk.res.veredicto,
        nivel,
    )


EXPERIMENTOS_QC: tuple[Experimento, ...] = (
    Experimento("sesgo", {"q_sesgo": 4.0}, {"sesgo": 4.0}, {"n_fuera_3sd": +1, "sesgo": +1}, "mal"),
    Experimento(
        "precision", {"q_dup_p": "20"}, {"dup_p": "20"}, {"pct90": +1, "pct99": +1}, "aviso"
    ),
    Experimento("pico", {"q_pico": 12.0}, {"pico": 12.0}, {"n_sobre_10": +1}, "mal"),
)


@lru_cache(maxsize=1)
def pares_qaqc() -> tuple[tuple[Experimento, ResQc, ResQc], ...]:
    base = evaluar_qaqc()
    return tuple((e, base, evaluar_qaqc(**e.mod)) for e in EXPERIMENTOS_QC)


def numeros_qaqc(a: ResQc, b: ResQc) -> dict[str, str]:
    p = QaqcParams()
    return {
        "s0": es(a.sesgo, 2),
        "s1": es(b.sesgo, 2),
        "f30": str(a.n_fuera_3sd),
        "f31": str(b.n_fuera_3sd),
        "sesgo": es(4, 0),
        "p0": es(float(p.dup_p), 0),
        "p1": es(20, 0),
        "a90": es(a.pct90, 1),
        "b90": es(b.pct90, 1),
        "a99": es(a.pct99, 1),
        "b99": es(b.pct99, 1),
        "pico0": es(p.pico, 0),
        "pico1": es(12, 0),
        "k": es(qc.K_FALLA, 0),
        "ld": es(p.ld, 3),
        "x0": str(a.n_sobre_10),
        "x1": str(b.n_sobre_10),
    }


def pruebas_qaqc() -> list[Prueba]:
    return [
        Prueba(
            e.clave,
            t(f"qc.exp.{e.clave}.titulo"),
            t(f"qc.exp.{e.clave}.texto", **numeros_qaqc(a, b)),
            controles_de(e.ctl),
        )
        for e, a, b in pares_qaqc()
    ]


def prueba_qaqc() -> None:
    pruebas(pruebas_qaqc(), "qc_", reset_to_example)


def estado_qaqc(
    p: QaqcParams,
    crm: CrmView | None,
    dup: DupView | None,
    blk: BlkView | None,
    cert: CertView | None,
) -> None:
    indicadores(indicadores_qaqc(crm, dup, blk))
    st.markdown(t("estado.h"))
    panel(filas_qaqc(p, crm, dup, blk, cert))
