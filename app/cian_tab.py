"""Pestaña «Ensayo de cianuración»: la calculadora de recuperación y ley de cabeza, los modelos
cinéticos con sus rectas y el vaso animado; y su sección de validación (pestaña Validación).
Nada que escriba el visitante entra al SVG ni al HTML: la tabla solo alimenta números."""

from __future__ import annotations

import carga
import pandas as pd
import streamlit as st
from cian_calculo import (
    PPB_MAX,
    T_MAX_H,
    CianParams,
    CianView,
    leer_tabla,
    model_name,
    run_cian,
)
from cian_estado import estado_cian, horas, prueba_cian
from cian_graficos import recovery_figure, terms_figure
from cian_svg import beaker_svg
from dibujo import as_images, es
from guia import ficha, markdown_table
from i18n import decimal, t

from muestreo import cianuracion as c
from muestreo import cianuracion_datos as cd

TABLE_KEY = "cian_tabla"
ROW_PX = 35  # alto de una fila de st.dataframe, para que la tabla se vea entera
COLUMNAS = (
    carga.Columna("t", "cn.col.t"),
    carga.Columna("sol", "cn.col.sol"),
    carga.Columna("res", "cn.col.res"),
)


def example_table() -> pd.DataFrame:
    return pd.DataFrame(
        {"t": list(cd.T_H), "sol": list(cd.SOLUCION_PPB), "res": list(cd.RESIDUO_PPB)}
    )


def _error_text(exc: c.SerieInvalida) -> str:
    args = {k: es(v, 0) for k, v in exc.args_.items()}
    return t(f"cn.err.{exc.code}", **args)


_h = horas


def balance_frame(view: CianView) -> pd.DataFrame:
    b = view.balance
    head = view.params.head
    return pd.DataFrame(
        {
            t("cn.col.t"): list(b.t_h),
            t("cn.col.sol"): list(b.solucion_ppb),
            t("cn.col.res"): list(b.residuo_ppb),
            t("cn.col.rec"): [round(x, 2) for x in b.recuperacion_pct],
            t("cn.col.sold"): [round(x, 1) for x in b.au_solucion_ppb],
            t("cn.col.head"): [round(x, 1) for x in b.cabeza_ppb],
            t("cn.col.dev"): [round(100.0 * (x / head - 1.0), 1) for x in b.cabeza_ppb],
        }
    )


def calculator(p: CianParams) -> CianView | None:
    st.markdown(t("cn.cal.h"))
    st.markdown(t("cn.cal.intro", head=es(p.head, 0), factor=es(p.factor, 3)))
    number = st.column_config.NumberColumn
    config = {
        "t": number(t("cn.col.t"), min_value=0.0, max_value=T_MAX_H, step=0.5, required=True),
        "sol": number(t("cn.col.sol"), min_value=0.0, max_value=PPB_MAX, step=1.0, required=True),
        "res": number(t("cn.col.res"), min_value=0.0, max_value=PPB_MAX, step=1.0, required=True),
    }
    edited = st.data_editor(
        carga.panel(TABLE_KEY, COLUMNAS, example_table(), "plantilla_cianuracion.csv"),
        key=TABLE_KEY,
        num_rows="dynamic",
        hide_index=True,
        column_config=config,
        width="stretch",
    )
    st.button(t("cn.reset"), on_click=carga.reiniciar, args=(TABLE_KEY,))
    rows = [
        [None if pd.isna(x) else x for x in r] for r in edited[["t", "sol", "res"]].values.tolist()
    ]
    try:
        times, sol, res = leer_tabla(rows)
        view = run_cian(p, times, sol, res)
    except c.SerieInvalida as exc:
        st.warning(_error_text(exc))
        return None
    st.dataframe(
        balance_frame(view), hide_index=True, width="stretch", height=ROW_PX * (len(rows) + 1) + 3
    )
    last = len(view.balance.t_h) - 1
    st.markdown(
        t(
            "cn.cal.res",
            r=es(view.balance.recuperacion_pct[last], 2),
            t=_h(view.balance.t_h[last]),
            head=es(p.head, 0),
        )
    )
    return view


def models_frame(view: CianView) -> pd.DataFrame:
    """La tabla de modelos, con los números en el formato del idioma y «–» donde no hay dato."""

    def num(x: float | None, d: int) -> str:
        return "–" if x is None else es(x, d)

    rows = []
    for f in view.filas:
        stretch = t(f"cn.stretch.{f.tramo}", cut=_h(view.params.split))
        rows.append({
            t("cn.m.model"): model_name(f.model), t("cn.m.stretch"): stretch, t("cn.m.n"): f.n,
            t("cn.m.r2"): num(f.r2, 4), t("cn.m.a"): num(f.intercepto, 4),
            t("cn.m.b"): num(f.pendiente, 5), t("cn.m.r0"): num(f.r_cero, 1),
            t("cn.m.rmse"): num(f.rmse, 2),
        })  # fmt: skip
    return pd.DataFrame(rows)


def _message(view: CianView) -> None:
    """El mensaje de la pestaña, con las cifras de estos datos."""
    first = {f.model: f for f in view.filas if f.tramo == 1}
    lin = [first[m] for m in c.MODELOS_LINEALES]
    if all(f.intercepto is not None and f.r_cero is not None for f in lin):
        st.markdown(
            t(
                "cn.msg.origin",
                i1=es(lin[0].intercepto, 3),
                i2=es(lin[1].intercepto, 3),
                i3=es(lin[2].intercepto, 3),
                z1=es(lin[0].r_cero, 0),
                z2=es(lin[1].r_cero, 0),
                z3=es(lin[2].r_cero, 0),
                r1=es(view.balance.recuperacion_pct[0], 0),
                t1=_h(view.balance.t_h[0]),
                n=lin[0].n,
                r2=es(max(f.r2 for f in lin), 3),
            )
        )
    else:
        st.info(t("cn.msg.fewpoints", n=c.MIN_PUNTOS_TRAMO))
    pot = next(f for f in view.filas if f.model == "potencial")
    one = view.modelos.primer_orden
    st.markdown(
        t(
            "cn.msg.models",
            b=es(view.modelos.potencial.b, 3),
            r2p=es(pot.r2, 3),
            rmse=es(pot.rmse, 1),
            r2o=es(one.r2, 2),
            rinf=es(one.r_inf, 1),
            k=es(one.k_por_h, 2),
        )
    )


def models_section(view: CianView) -> None:
    st.markdown(t("cn.mod.h"))
    if view.modelos is None:
        st.info(t("cn.msg.fewpoints", n=c.MIN_PUNTOS_TRAMO))
        return
    st.markdown(t("cn.mod.intro", cut=_h(view.params.split)))
    st.plotly_chart(recovery_figure(view), width="stretch")
    st.plotly_chart(terms_figure(view), width="stretch")
    _message(view)
    st.dataframe(models_frame(view), hide_index=True, width="stretch")
    st.caption(t("cn.mod.caption", b1=es(c.B_N1, 4), b2=es(c.B_N2, 2)))


def animation_section(view: CianView, animate: bool) -> None:
    st.markdown(t("cn.ani.h"))
    st.html(
        as_images(
            beaker_svg(view, paused=not animate), beaker_svg(view, paused=True), t("cn.ani.alt")
        )
    )
    st.caption(t("cn.ani.caption", model=model_name(view.params.model)))


def cian_tab(p: CianParams, animate: bool) -> None:
    ficha("cianuracion")
    estado = st.container()  # va arriba, pero se llena cuando la tabla ya dio su resultado
    view = calculator(p)
    if view is None:
        return
    with estado:
        estado_cian(view)
    models_section(view)
    animation_section(view, animate)
    prueba_cian()


# ------------------------------------------------------------------ validación
def _check_table(checks: list[cd.CianCheck]) -> str:
    df = pd.DataFrame(
        {
            t("cv.col.concept"): [f"{t('cv.kind.' + x.kind)} {x.label}" for x in checks],
            t("cv.col.published"): [decimal(x.published) for x in checks],
            t("cv.col.calculated"): [decimal(round(x.calculated, x.decimals + 1)) for x in checks],
            t("cv.col.fits"): [t("v.yes") if x.ok else t("v.no") for x in checks],
            t("cv.col.note"): [t("cv.note." + x.note) if x.note else "" for x in checks],
        }
    )
    return markdown_table(df)


def cian_validation_section() -> None:
    """Sección «Ensayo de cianuración» de la pestaña Validación."""
    st.markdown(t("cv.h"))
    checks = cd.all_checks()
    s = cd.summary(checks)
    st.markdown(t("cv.intro"))
    st.markdown(
        t(
            "cv.summary",
            t4=s["t4"][0],
            n4=s["t4"][1],
            t6=s["t6"][0],
            n6=s["t6"][1],
            t7=s["t7"][0],
            n7=s["t7"][1],
            e3=s["e3"][0],
            n3=s["e3"][1],
        )
    )
    for src in ("t4", "t6", "t7", "e3"):
        st.markdown(t("cv.h." + src))
        st.markdown(_check_table([x for x in checks if x.source == src]))
    iv, (h0, h1) = cd.b_intervals(), cd.head_range()
    st.markdown(
        t(
            "cv.b",
            b1=es(c.B_N1, 4),
            b2=es(c.B_N2, 2),
            s0=es(c.S0_PPB, 0),
            f=es(c.F_SOLUCION, 3),
            lo1=es(iv["N1"][0], 4),
            hi1=es(iv["N1"][1], 4),
            lo2=es(iv["N2"][0], 4),
            hi2=es(iv["N2"][1], 4),
            h0=es(h0, 1),
            h1=es(h1, 1),
        )
    )
    m1 = cd.regressions()["M1"]
    p2, pi, ps = cd.T7_PUB["M1"]
    st.markdown(
        t(
            "cv.m1",
            m1=es(cd.M_PUB[1.0], 3),
            m3=es(cd.M_PUB[3.0], 3),
            m7=es(cd.M_PUB[7.0], 3),
            c2=es(m1.r2, 4),
            ci=es(m1.intercepto, 3),
            cs=es(m1.pendiente, 3),
            p2=es(float(p2), 3),
            pi=es(float(pi), 3),
            ps=es(float(ps), 3),
            f=es(cd.T7_F_PUB["M1"], 2),
            r2=es(cd.m1_implied_r2(), 4),
        )
    )
    st.markdown(t("cv.rows"))
