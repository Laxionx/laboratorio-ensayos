"""Pestaña «Fusión»: la carga fundente de un ensayo al fuego y la validación de la fase 2."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from calculo import FusionUIParams, run_fusion
from dibujo import as_images, es
from fusion_estado import estado_fusion, prueba_fusion
from fusion_graficos import balance_figure
from fusion_svg import crucible_svg
from guia import ficha, markdown_table
from i18n import decimal, t, tm, tr_error

from muestreo import fusion_datos as fd
from muestreo.fusion import FUSION_TEMP_C, SLAG_DENSITY, FusionError, pb_liquid_density


def _pct_sum(f: FusionUIParams) -> float:
    return sum(v for _, v in f.minerals)


def fusion_tab(f: FusionUIParams, animate: bool) -> None:
    ficha("fusion")
    total = _pct_sum(f)
    if total > 100.0 + 1e-9:
        st.error(t("f.err.sum", total=es(total, 0)))
        return
    try:
        view = run_fusion(f)
    except FusionError as exc:
        st.error(t("f.err.calc", exc=tr_error(str(exc))))
        return
    r = view.result
    st.caption(t("f.minerals", total=es(total, 0), rest=es(100 - total, 0)) + t("f.codes"))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("f.m.button"), f"{es(r.button_g, 1)} g", t("f.m.button.delta", x=es(f.button_g, 1)),
              delta_color="off")  # fmt: skip
    c2.metric(t("f.m.slag"), f"{es(r.slag.mass_g, 1)} g")
    c3.metric(t("f.m.degree"), f"{tm(r.slag.label)} ({es(r.slag.degree, 2)})")
    uses_flour = view.designed.niter_g <= 0
    grams = view.used.flour_g if uses_flour else view.used.niter_g
    c4.metric(t("f.m.flour" if uses_flour else "f.m.niter"), f"{es(grams, 2)} g")
    if view.changed:
        st.info(t("f.info.changed"))
    estado_fusion(view, f)
    st.html(as_images(crucible_svg(view, paused=not animate), crucible_svg(view, paused=True),
                      t("f.alt")))  # fmt: skip
    st.caption(
        t("f.caption", lead=es(r.lead_hot_cm3, 2), rho=es(pb_liquid_density(FUSION_TEMP_C), 2),
          slag=es(r.slag_cm3, 1), slag_rho=es(SLAG_DENSITY, 1), cold=es(r.button_cm3, 2))
    )  # fmt: skip
    table = pd.DataFrame({
        t("f.col.reagent"): [t("r.soda"), t("r.litharge"), t("r.borax.formula"), t("r.silica"),
                             t("r.flour"), t("r.niter")],
        t("f.col.calc"): [round(x, 2) for x in (
            view.designed.soda_g, view.designed.litharge_g, view.designed.borax_g,
            view.designed.silica_g, view.designed.flour_g, view.designed.niter_g)],
        t("f.col.used"): [round(x, 2) for x in (
            view.used.soda_g, view.used.litharge_g, view.used.borax_g, view.used.silica_g,
            view.used.flour_g, view.used.niter_g)],
    })  # fmt: skip
    st.dataframe(table, hide_index=True)
    left, right = st.columns(2)
    left.plotly_chart(balance_figure(view), width="stretch")
    minerals = pd.DataFrame(
        [{t("f.min.mineral"): tm(n), "%": p, "g": round(g, 2), t("f.min.rp"): round(rp, 2),
          t("f.min.pb"): round(pb, 2)} for n, p, g, rp, pb in view.rows]
    )  # fmt: skip
    right.markdown(t("f.rp.head"))
    right.dataframe(minerals, hide_index=True)
    right.caption(t("f.rp.caption", sulfur=f.sulfur))
    slag = pd.DataFrame({t("f.slag.component"): list(r.slag.components_g),
                         "g": [round(v, 2) for v in r.slag.components_g.values()]})  # fmt: skip
    st.markdown(t("f.slag.head"))
    st.dataframe(slag, hide_index=True)
    prueba_fusion()


def _check_table(checks: list[fd.FusionCheck]) -> str:
    def number(x: float | None) -> str:
        return "-" if x is None else decimal(x)

    df = pd.DataFrame({
        t("fv.col.concept"): [tm(c.item) for c in checks],
        t("fv.col.published"): [number(c.published) for c in checks],
        t("fv.col.current"): [number(c.calculated) for c in checks],
        t("fv.col.bugbee"): [number(c.bugbee) for c in checks],
        t("fv.col.verdict"): [t("verdict." + c.fit) for c in checks],
        t("fv.col.diff"): [number(c.difference_bugbee) for c in checks],
        t("fv.col.unit"): [tm(c.unit) for c in checks],
        t("fv.col.note"): [tm(c.note) for c in checks],
    })  # fmt: skip
    return markdown_table(df)


def fusion_validation_section() -> None:
    """Sección «Fase 2: carga fundente» de la pestaña Validación."""
    st.markdown(t("fv.h"))
    checks = fd.all_checks()
    s = fd.summary(checks)
    st.markdown(
        t("fv.summary", total=s["total"], ok=s["cuadra"], trunc=s["truncamiento de Bugbee"],
          weights=s["cuadra con los pesos de Bugbee"], no=s["no cuadra"])
    )  # fmt: skip
    st.markdown(t("fv.h1"))
    st.markdown(_check_table(fd.theoretical_checks()))
    st.markdown(t("fv.h2"))
    st.markdown(_check_table(fd.neutralization_checks()))
    st.markdown(t("fv.h3"))
    st.markdown(_check_table(fd.example_checks()))
    st.markdown(_check_table(fd.mixture_checks()))
    st.markdown(t("fv.h4"))
    measured = pd.DataFrame([
        {t("fv.m.mineral"): tm(n), t("fv.m.so2"): round(a, 2), t("fv.m.so3"): round(b, 2),
         t("fv.m.measured"): "-" if m is None else m,
         t("fv.m.diff"): "-" if d is None else round(d, 2)}
        for n, a, b, m, d in fd.measured_rows()
    ])  # fmt: skip
    st.markdown(markdown_table(measured))
    st.caption(t("fv.m.caption"))
    st.markdown(t("fv.h5"))
    usgs = pd.DataFrame([
        {t("fv.u.load"): tm(r["carga"]), t("fv.u.button"): round(r["botón (g)"], 1),
         t("fv.u.degree"): round(r["grado"], 2), t("fv.u.slag"): tm(r["escoria"]),
         t("fv.u.slag_g"): round(r["escoria (g)"], 1)}
        for r in fd.usgs_load_rows()
    ])  # fmt: skip
    st.markdown(markdown_table(usgs))
    st.caption(t("fv.u.caption"))
    st.markdown(t("fv.h6"))
    st.markdown(_check_table([fd.usgs_niter_example()]))
