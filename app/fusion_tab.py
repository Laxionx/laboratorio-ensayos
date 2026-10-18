"""Pestaña «Fusión»: la carga fundente de un ensayo al fuego y la validación de la fase 2."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from calculo import FusionUIParams, run_fusion
from dibujo import as_images, es
from fusion_graficos import balance_figure
from fusion_svg import crucible_svg
from guia import ficha, markdown_table

from muestreo import fusion_datos as fd
from muestreo.fusion import SLAG_DENSITY, FusionError
from muestreo.fusion_avisos import BUTTON_RANGE

CODES_NOTE = (
    "La carga es un cálculo de reactivos a partir de la mineralogía y de los textos de Bugbee "
    "(1922) y del USGS (1977): no es la receta de ningún laboratorio."
)


def _pct_sum(f: FusionUIParams) -> float:
    return sum(v for _, v in f.minerals)


def fusion_tab(f: FusionUIParams, animate: bool) -> None:
    ficha("fusion")
    total = _pct_sum(f)
    if total > 100.0 + 1e-9:
        st.error(f"Los minerales suman {es(total, 0)} %: no pueden pasar de 100 %. Baja alguno.")
        return
    try:
        view = run_fusion(f)
    except FusionError as exc:
        st.error(f"No se pudo calcular la carga con estos datos: {exc}")
        return
    r = view.result
    st.caption(f"Minerales: {es(total, 0)} % (el {es(100 - total, 0)} % restante es inerte). "
               + CODES_NOTE)  # fmt: skip
    lo, hi = BUTTON_RANGE
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Botón de plomo", f"{es(r.button_g, 1)} g", f"pedido {es(f.button_g, 1)} g",
              delta_color="off")  # fmt: skip
    c2.metric("Escoria", f"{es(r.slag.mass_g, 1)} g")
    c3.metric("Grado de silicato", f"{r.slag.label} ({es(r.slag.degree, 2)})")
    reductant = "harina" if view.designed.niter_g <= 0 else "nitro"
    grams = view.used.flour_g if reductant == "harina" else view.used.niter_g
    c4.metric(f"{reductant.capitalize()} de la carga", f"{es(grams, 2)} g")
    if view.changed:
        st.info("Estás probando una carga cambiada: el botón y la escoria son los de la carga "
                "cambiada, no los de la calculada.")  # fmt: skip
    if not lo <= r.button_g <= hi:
        st.warning(f"El botón de {es(r.button_g, 1)} g queda fuera de {es(lo, 0)} a {es(hi, 0)} g.")
    for w in r.warnings:
        if "Botón de" in w.text:
            continue  # ya está arriba
        st.warning(f"**{w.level.capitalize()}:** {w.text} _(Fuente: {w.source})_")
    st.html(as_images(crucible_svg(view, paused=not animate), crucible_svg(view, paused=True),
                      "Crisol en corte con escoria, gotas de plomo y botón"))  # fmt: skip
    st.caption(
        f"La escoria llega a {es(r.slag_cm3, 1)} cm³ con una densidad supuesta de "
        f"{es(SLAG_DENSITY, 1)} g/cm³ (Bugbee no la da); el botón mide {es(r.button_cm3, 2)} cm³ "
        "(plomo sólido, 11,34 g/cm³). Las gotas, las burbujas y el tamaño del crisol son "
        "ilustrativos."
    )
    table = pd.DataFrame({
        "Reactivo": ["Soda (Na₂CO₃)", "Litargirio (PbO)", "Bórax vidrio (Na₂B₄O₇)",
                     "Sílice (SiO₂)", "Harina", "Nitro (KNO₃)"],
        "Calculada (g)": [round(x, 2) for x in (
            view.designed.soda_g, view.designed.litharge_g, view.designed.borax_g,
            view.designed.silica_g, view.designed.flour_g, view.designed.niter_g)],
        "Usada (g)": [round(x, 2) for x in (
            view.used.soda_g, view.used.litharge_g, view.used.borax_g, view.used.silica_g,
            view.used.flour_g, view.used.niter_g)],
    })  # fmt: skip
    st.dataframe(table, hide_index=True)
    left, right = st.columns(2)
    left.plotly_chart(balance_figure(view), width="stretch")
    minerals = pd.DataFrame(
        [{"Mineral": n, "%": p, "g": round(g, 2), "R.P. (g Pb/g)": round(rp, 2),
          "Pb (g)": round(pb, 2)} for n, p, g, rp, pb in view.rows]
    )  # fmt: skip
    right.markdown("**Poder reductor de la muestra**")
    right.dataframe(minerals, hide_index=True)
    right.caption(f"Azufre oxidado a {f.sulfur}. Negativo: oxida (resta plomo).")
    slag = pd.DataFrame({"Componente": list(r.slag.components_g),
                         "g": [round(v, 2) for v in r.slag.components_g.values()]})  # fmt: skip
    st.markdown("**Composición de la escoria**")
    st.dataframe(slag, hide_index=True)


def _check_table(checks: list[fd.FusionCheck]) -> str:
    def number(x: float | None) -> str:
        return "-" if x is None else f"{x:.6g}".replace(".", ",")

    df = pd.DataFrame({
        "Concepto": [c.item for c in checks],
        "Publicado": [number(c.published) for c in checks],
        "Pesos actuales": [number(c.calculated) for c in checks],
        "Pesos de Bugbee": [number(c.bugbee) for c in checks],
        "Veredicto": [c.fit for c in checks],
        "Dif. (Bugbee)": [number(c.difference_bugbee) for c in checks],
        "Unidad": [c.unit for c in checks],
        "Nota": [c.note for c in checks],
    })  # fmt: skip
    return markdown_table(df)


def fusion_validation_section() -> None:
    """Sección «Fase 2: carga fundente» de la pestaña Validación."""
    st.markdown("### Fase 2: carga fundente (Bugbee 1922 y USGS Bulletin 1445)")
    checks = fd.all_checks()
    s = fd.summary(checks)
    st.markdown(
        f"{s['total']} cifras publicadas: **{s['cuadra']}** cuadran con pesos atómicos actuales, "
        f"**{s['cuadra con los pesos de Bugbee']}** cuadran con los pesos de Bugbee, "
        f"**{s['truncamiento de Bugbee']}** son truncamientos suyos y **{s['no cuadra']}** no "
        "cuadran. Difieren porque Bugbee calculó a mano con pesos atómicos redondeados (207 para "
        "el Pb, 56 para el Fe) y a veces truncó en vez de redondear; los pesos de Bugbee de esta "
        "tabla se infieren de sus propias cifras (el juego que mejor las reproduce, declarado en "
        "`fusion_pesos.py`) y la app calcula siempre con pesos actuales. Las cifras de la Tabla XX "
        "y de la Tabla XXI se leyeron también en la imagen del escaneo."
    )
    st.markdown("#### Poderes reductores y oxidantes teóricos")
    st.markdown(_check_table(fd.theoretical_checks()))
    st.markdown("#### Neutralización de bases y tablas de fundentes")
    st.markdown(_check_table(fd.neutralization_checks()))
    st.markdown("#### Ejemplos resueltos de Bugbee")
    st.markdown(_check_table(fd.example_checks()))
    st.markdown(_check_table(fd.mixture_checks()))
    st.markdown("#### Poderes reductores medidos por Bugbee (no son corte)")
    measured = pd.DataFrame([
        {"Mineral": n, "Teórico, S a SO₂": round(a, 2), "Teórico, S a SO₃": round(b, 2),
         "Medido": "-" if m is None else m, "Medido − SO₃": "-" if d is None else round(d, 2)}
        for n, a, b, m, d in fd.measured_rows()
    ])  # fmt: skip
    st.markdown(markdown_table(measured))
    st.caption("Carga de prueba de Bugbee: 5 g de Na₂CO₃, 80 g de PbO, 2 g de SiO₂ y mineral para "
               "un botón de unos 25 g. Argoles: 11,04 (sub-silicato), 10,93 (mono), 10,62 (bi) y "
               "9,26 (tri).")  # fmt: skip
    st.markdown("#### Cargas del USGS 1445 evaluadas con la calculadora (informativo)")
    usgs = pd.DataFrame([
        {"Carga": r["carga"], "Botón (g)": round(r["botón (g)"], 1), "Grado": round(r["grado"], 2),
         "Escoria": r["escoria"], "Escoria (g)": round(r["escoria (g)"], 1)}
        for r in fd.usgs_load_rows()
    ])  # fmt: skip
    st.markdown(markdown_table(usgs))
    st.caption(
        "Harina de R.P. 10,5 (medio del USGS) y azufre ausente. Son cargas del manual del "
        "USGS (1977), no recetas; el USGS agrega 0 a 12 g de CaF₂ que aquí no se modela."
    )
    st.markdown("#### Nitro del USGS")
    st.markdown(_check_table([fd.usgs_niter_example()]))
