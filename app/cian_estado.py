"""Indicadores, «Estado de la operación», caso publicado y «Prueba esto» de la pestaña Ensayo de
cianuración. Los chequeos son los avisos que el cálculo ya emite (`cianuracion.balance`: la
recuperación que no sube y la cabeza que no cuadra, con la tolerancia de coherencia de 5 % que el
módulo declara como NUESTRA) y la regla de al menos 3 puntos por tramo (`MIN_PUNTOS_TRAMO`). El
caso publicado es la Tabla 4 de Roostaei, Kordparijaei y Mesroghli (2026), que es la tabla con que
abre la pestaña. Los experimentos parten del ejemplo de la barra lateral y llevan números
calculados en vivo."""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache

import pandas as pd
import streamlit as st
from cian_calculo import CianParams, CianView, run_cian
from controles import reset_to_example
from dibujo import es
from estado import Experimento, Fila, Prueba, controles_de, indicadores, panel, peor, pruebas
from i18n import decimal, t, use

from muestreo import cianuracion as c
from muestreo import cianuracion_datos as cd


def horas(x: float) -> str:
    return es(x, 0 if float(x).is_integer() else 1)


def _tabla4() -> tuple[list[float], list[float], list[float]]:
    return list(cd.T_H), list(cd.SOLUCION_PPB), list(cd.RESIDUO_PPB)


def aviso_texto(a: c.Aviso) -> str:
    return t(f"cn.warn.{a.code}", t=horas(a.t_h), v=es(a.value, 1))


def filas_cian(view: CianView) -> list[Fila]:
    """Los chequeos del panel de la pestaña Ensayo de cianuración."""
    bal, p = view.balance, view.params
    filas: list[Fila] = []
    no_sube = [a for a in bal.avisos if a.code == "no_monotona"]
    if no_sube:
        filas += [Fila("aviso", aviso_texto(a), t("cn.src.monotona")) for a in no_sube]
    else:
        filas.append(Fila("ok", t("cn.chk.monotona.ok", n=len(bal.t_h)), t("cn.src.monotona")))
    lejos = [a for a in bal.avisos if a.code == "cabeza"]
    if lejos:
        peor_a = max(lejos, key=lambda a: abs(a.value))
        filas.append(
            Fila(
                "aviso",
                t(
                    "cn.chk.cabeza.mal",
                    tol=es(c.COHERENCIA_PCT, 0),
                    head=es(p.head, 0),
                    n=len(lejos),
                    total=len(bal.t_h),
                    v=es(abs(peor_a.value), 1),
                    t=horas(peor_a.t_h),
                ),
                t("cn.src.cabeza", tol=es(c.COHERENCIA_PCT, 0)),
            )
        )
    else:
        filas.append(
            Fila(
                "ok",
                t("cn.chk.cabeza.ok", head=es(p.head, 0), tol=es(c.COHERENCIA_PCT, 0)),
                t("cn.src.cabeza", tol=es(c.COHERENCIA_PCT, 0)),
            )
        )
    if view.modelos is not None:
        primero = {f.tramo: f for f in view.filas if f.model == "difusion" and f.tramo}
        sin = [k for k, f in primero.items() if f.n < c.MIN_PUNTOS_TRAMO]
        if sin:
            filas.append(
                Fila(
                    "aviso",
                    t(
                        "cn.chk.tramos.mal",
                        cut=horas(p.split),
                        n=c.MIN_PUNTOS_TRAMO,
                        tramos=", ".join(str(k) for k in sin),
                    ),
                    t("cn.src.tramos"),
                )
            )
        else:
            filas.append(
                Fila(
                    "ok",
                    t("cn.chk.tramos.ok", n1=primero[1].n, n2=primero[2].n, min=c.MIN_PUNTOS_TRAMO),
                    t("cn.src.tramos"),
                )
            )
    return filas


def indicadores_cian(view: CianView) -> list[tuple[str, str, str]]:
    bal = view.balance
    pot = None if view.modelos is None else view.modelos.potencial
    r2 = "–" if pot is None else es(pot.r2, 3)
    return [
        (
            t("cn.i.rec"),
            f"{es(bal.recuperacion_pct[-1], 2)} %",
            t("cn.i.rec.help", t=horas(bal.t_h[-1])),
        ),
        (
            t("cn.i.head"),
            es(bal.cabeza_ppb[-1], 0),
            t("cn.i.head.help", f=es(view.params.factor, 3)),
        ),
        (t("cn.i.r2"), r2, t("cn.i.r2.help")),
    ]


# ------------------------------------------------------------------ el caso publicado
def es_tabla4(view: CianView) -> bool:
    """La tabla y la cabeza declarada son las de la Tabla 4 (el ejemplo con que abre la pestaña)."""
    b = view.balance
    return (
        list(b.t_h) == list(cd.T_H)
        and list(b.solucion_ppb) == list(cd.SOLUCION_PPB)
        and list(b.residuo_ppb) == list(cd.RESIDUO_PPB)
        and view.params.head == c.S0_PPB
    )


def comparar_publicado(view: CianView) -> None:
    b = view.balance
    pub = cd.RECUPERACION_PUB
    table = pd.DataFrame(
        {
            t("cn.col.t"): [horas(x) for x in b.t_h],
            t("caso.col.pub"): [decimal(x) for x in pub],
            t("caso.col.calc"): [decimal(round(x, 2)) for x in b.recuperacion_pct],
            t("caso.col.delta"): [
                decimal(round(x - p, 2) + 0.0) for x, p in zip(b.recuperacion_pct, pub, strict=True)
            ],
        }
    )
    peor_d = max(abs(x - p) for x, p in zip(b.recuperacion_pct, pub, strict=True))
    with st.expander(t("cn.caso.h"), expanded=True):
        st.markdown(t("cn.caso.res", head=es(c.S0_PPB, 0), delta=es(peor_d, 2)))
        st.dataframe(table, hide_index=True)


# ------------------------------------------------------------------ prueba esto
@dataclass(frozen=True)
class ResCian:
    rec: float  # recuperación de la última fila, %
    cabeza: float  # cabeza por balance de la última fila, ppb
    lejos: int  # filas con la cabeza a más de la tolerancia
    r2_reaccion1: float  # R² del primer tramo del término de reacción (M)
    nivel: str


def evaluar_cian(**mod: object) -> ResCian:
    p = replace(CianParams(), **mod)  # type: ignore[arg-type]
    view = run_cian(p, *_tabla4())
    bal = view.balance
    reac = next(f for f in view.filas if f.model == "reaccion" and f.tramo == 1)
    with use("es"):
        nivel = peor(filas_cian(view))
    return ResCian(
        bal.recuperacion_pct[-1],
        bal.cabeza_ppb[-1],
        sum(a.code == "cabeza" for a in bal.avisos),
        reac.r2 or 0.0,
        nivel,
    )


EXPERIMENTOS_CIAN: tuple[Experimento, ...] = (
    Experimento("cabeza", {"c_head": 900.0}, {"head": 900.0}, {"rec": -1, "lejos": +1}, "aviso"),
    Experimento("factor", {"c_factor": 2.5}, {"factor": 2.5}, {"cabeza": +1, "lejos": +1}, "aviso"),
    Experimento("corte", {"c_split": 11.0}, {"split": 11.0}, {"r2_reaccion1": -1}, "aviso"),
)


@lru_cache(maxsize=1)
def pares_cian() -> tuple[tuple[Experimento, ResCian, ResCian], ...]:
    base = evaluar_cian()
    return tuple((e, base, evaluar_cian(**e.mod)) for e in EXPERIMENTOS_CIAN)


def numeros_cian(a: ResCian, b: ResCian) -> dict[str, str]:
    p = CianParams()
    return {
        "rec0": es(a.rec, 2),
        "rec1": es(b.rec, 2),
        "cab0": es(a.cabeza, 0),
        "cab1": es(b.cabeza, 0),
        "n1": str(b.lejos),
        "r0": es(a.r2_reaccion1, 3),
        "r1": es(b.r2_reaccion1, 3),
        "head0": es(p.head, 0),
        "head1": es(900, 0),
        "f0": es(p.factor, 3),
        "f1": es(2.5, 1),
        "cut0": horas(p.split),
        "cut1": horas(11),
        "tol": es(c.COHERENCIA_PCT, 0),
    }


def pruebas_cian() -> list[Prueba]:
    return [
        Prueba(
            e.clave,
            t(f"cn.exp.{e.clave}.titulo"),
            t(f"cn.exp.{e.clave}.texto", **numeros_cian(a, b)),
            controles_de(e.ctl),
        )
        for e, a, b in pares_cian()
    ]


def prueba_cian() -> None:
    pruebas(pruebas_cian(), "cian_", reset_to_example)


def estado_cian(view: CianView) -> None:
    indicadores(indicadores_cian(view))
    st.markdown(t("estado.h"))
    panel(filas_cian(view))
    if es_tabla4(view):
        comparar_publicado(view)
