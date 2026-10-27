"""Indicadores, «Estado de la operación» y «Prueba esto» de la pestaña Ensayo de sedimentación. Los
chequeos son de definición del cálculo (concentraciones de la alimentación y del underflow, punto
de compresión y tangente de Talmage-Fitch, puntos de Kynch) y el aviso del factor de corrección
de Vale, que `sedimentacion.py` declara válido SOLO para las lamas de hierro de Vale (Torquato et
al. 2011). No hay caso publicado que se mapee exacto a los controles: las tablas de Vale y de Coe y
Clevenger se validan con sus propios datos (secciones fijas de la pestaña), no con la curva de Luz
de la barra lateral. Los experimentos parten del ejemplo de la barra lateral (los valores por
defecto de `controles.DATOS`) y llevan números calculados en vivo."""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache

import streamlit as st
from controles import reset_to_example
from dibujo import es
from estado import Experimento, Fila, Prueba, controles_de, indicadores, panel, peor, pruebas
from i18n import t, use
from sed_calculo import FACTORES, SedParams, SedView, run_sed

from muestreo import sedimentacion as sd


def filas_sed(v: SedView) -> list[Fila]:
    """Los chequeos del panel de la pestaña Ensayo de sedimentación."""
    p, tf = v.params, v.tf
    filas = [
        Fila(
            "ok",
            t(
                "se.chk.conc",
                cma=es(p.cma, 1),
                cmu=es(p.cmu, 1),
                c0=es(v.c0, 3),
                cu=es(v.cu, 3),
                rho=es(p.rho_s, 1),
            ),
            t("se.src.conc"),
        ),
        Fila(
            "ok",
            t(
                "se.chk.compresion",
                tc=es(v.tc_s, 0),
                hc=es(tf.hc_m, 3),
                hu=es(tf.hu_m, 3),
                tu=es(tf.tu_s, 0),
                tmax=es(v.curva.t_max, 0),
            ),
            t("se.src.compresion"),
        ),
    ]
    k = v.kynch
    if k is not None and k.c_t_m3:
        filas.append(
            Fila(
                "ok",
                t(
                    "se.chk.kynch",
                    n=len(k.c_t_m3),
                    lo=es(min(k.c_t_m3), 3),
                    hi=es(max(k.c_t_m3), 3),
                ),
                t("se.src.kynch"),
            )
        )
    else:
        filas.append(Fila("aviso", t("sd.ky.none"), t("se.src.kynch")))
    if v.factor == 1.0:
        filas.append(Fila("ok", t("se.chk.factor.ok"), t("se.src.factor")))
    else:
        filas.append(Fila("aviso", t("sd.dim.vale"), t("se.src.factor")))
    return filas


def indicadores_sed(v: SedView) -> list[tuple[str, str, str]]:
    return [
        (t("se.i.au"), es(v.area_unitaria_corregida, 3), t("se.i.au.help")),
        (t("se.i.area"), es(v.area_m2, 0), t("se.i.area.help", tph=es(v.params.tph, 0))),
        (t("se.i.d"), es(v.diametro_m, 1), t("se.i.d.help")),
    ]


# ------------------------------------------------------------------ prueba esto
@dataclass(frozen=True)
class ResSed:
    au: float  # área unitaria corregida, m² por t/d
    area: float  # m²
    diametro: float  # m
    tu: float  # s
    nivel: str


def evaluar_sed(**mod: object) -> ResSed:
    v = run_sed(replace(SedParams(), **mod))  # type: ignore[arg-type]
    with use("es"):
        nivel = peor(filas_sed(v))
    return ResSed(v.area_unitaria_corregida, v.area_m2, v.diametro_m, v.tf.tu_s, nivel)


EXPERIMENTOS_SED: tuple[Experimento, ...] = (
    Experimento("caudal", {"s_tph": 314.0}, {"tph": 314.0}, {"area": +1, "diametro": +1}, "ok"),
    Experimento(
        "vale",
        {"s_factor": FACTORES[1]},
        {"factor": FACTORES[1]},
        {"au": -1, "area": -1, "diametro": -1},
        "aviso",
    ),
    Experimento(
        "compresion", {"s_tc": 900.0}, {"tc": 900.0}, {"tu": +1, "au": +1, "diametro": +1}, "ok"
    ),
)


@lru_cache(maxsize=1)
def pares_sed() -> tuple[tuple[Experimento, ResSed, ResSed], ...]:
    base = evaluar_sed()
    return tuple((e, base, evaluar_sed(**e.mod)) for e in EXPERIMENTOS_SED)


def numeros_sed(a: ResSed, b: ResSed) -> dict[str, str]:
    p = SedParams()
    return {
        "au0": es(a.au, 3),
        "au1": es(b.au, 3),
        "a0": es(a.area, 0),
        "a1": es(b.area, 0),
        "d0": es(a.diametro, 1),
        "d1": es(b.diametro, 1),
        "tu0": es(a.tu, 0),
        "tu1": es(b.tu, 0),
        "tph0": es(p.tph, 0),
        "tph1": es(314, 0),
        "tc0": es(p.tc, 0),
        "tc1": es(900, 0),
        "f": es(sd.FACTOR_VALE_LAMAS, 2),
        "ratio": es(b.area / a.area, 2),
        "rd": es(b.diametro / a.diametro, 2),
    }


def pruebas_sed() -> list[Prueba]:
    return [
        Prueba(
            e.clave,
            t(f"se.exp.{e.clave}.titulo"),
            t(f"se.exp.{e.clave}.texto", **numeros_sed(a, b)),
            controles_de(e.ctl),
        )
        for e, a, b in pares_sed()
    ]


def prueba_sed() -> None:
    pruebas(pruebas_sed(), "sed_", reset_to_example)


def estado_sed(v: SedView) -> None:
    indicadores(indicadores_sed(v))
    st.markdown(t("estado.h"))
    panel(filas_sed(v))
