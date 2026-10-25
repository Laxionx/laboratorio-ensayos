"""App «Laboratorio de ensayos al fuego» / "Fire-assay laboratory": cuánto error de muestreo
mete cada etapa de un protocolo y cuánto se acumula, el oro grueso en la alícuota y la validación
de la ecuación de Gy contra números publicados. Pestañas: Guía, Protocolo, Oro grueso, Fusión,
Copelación, Ensayo de cianuración, Ensayo de sedimentación y Validación."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Streamlit Community Cloud instala solo requirements.txt: el paquete se importa desde la raíz,
# y los módulos de la app, desde esta carpeta.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

import pandas as pd  # noqa: E402
from calculo import (  # noqa: E402
    GoldParams,
    MineralParams,
    ProtocolParams,
    run_gold,
    run_protocol,
)
from cian_tab import cian_tab, cian_validation_section  # noqa: E402
from controles import sidebar_config  # noqa: E402
from cop_tab import cop_tab, cop_validation_section  # noqa: E402
from dibujo import MOTION_CSS, as_images, es  # noqa: E402
from fusion_tab import fusion_tab, fusion_validation_section  # noqa: E402
from guia import ficha, guide_tab, markdown_table, minnitt_2007_note  # noqa: E402
from i18n import activate, decimal, opt, sidebar_selector, t, tm, tr_error  # noqa: E402
from nomograma import (  # noqa: E402
    granulometry_figure,
    nomogram_figure,
    sensitivity_figure,
    stage_figure,
)
from oro_graficos import aliquot_svg, histogram_figure  # noqa: E402
from sed_tab import sed_tab, sed_validation_section  # noqa: E402
from validacion_graficos import clifton_figure, minnitt_2007_figure, variance_figure  # noqa: E402

from muestreo import gy  # noqa: E402
from muestreo import validacion as val  # noqa: E402
from muestreo.oro import (  # noqa: E402
    PARTICLES_CRITERION,
    SFA_MASS_G,
    SFA_SCREEN_UM,
    clifton_limits,
    mass_for_particles,
    poisson_exact_limits,
    poisson_p0,
    recommend_screen_fire_assay,
)
from muestreo.protocolo import PRESETS  # noqa: E402

activate()  # idioma de esta corrida: la sesión o `?lang=` (solo es o en)
st.set_page_config(page_title=t("page.title"), layout="wide")


def _pct(x: float, decimals: int = 1) -> str:
    return f"{es(100 * x, decimals)} %"


def protocol_tab(p: ProtocolParams, mp: MineralParams) -> None:
    ficha("protocolo")
    try:
        view = run_protocol(p, mp)
    except (gy.GyError, ValueError) as exc:
        st.error(t("err.protocol", exc=tr_error(str(exc))))
        return
    result = view.result
    worst_index = max(range(len(result.stages)), key=lambda i: result.stages[i].variance)
    worst = result.stages[worst_index]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("p.total"), _pct(result.rsd))
    share = t("p.worst.delta", pct=_pct(worst.share, 0))
    c2.metric(t("p.worst"), t("p.worst.value", n=worst_index + 1), share, delta_color="off")
    c3.metric(t("p.last"), _pct(result.stages[-1].rsd))
    c4.metric(t("p.safe"), t("yes") if view.meets_safety else t("no"),
              t("p.safe.delta", pct=es(p.safety_pct, 0)), delta_color="off")  # fmt: skip
    if p.preset == PRESETS[2]:
        st.info(t("p.info"))
    st.caption(
        t("p.mineral", name=opt(view.mineral.name))
        + (t("p.mineral.note") if view.mineral.name.startswith("Calibrado") else "")
    )
    st.plotly_chart(nomogram_figure(view), width="stretch")
    st.caption(t("p.nomo.caption"))
    table = pd.DataFrame({
        t("p.col.stage"): [tm(s.name) for s in result.stages],
        t("p.col.dn"): [round(s.d_n_cm, 5) for s in result.stages],
        t("p.col.mass"): [f"{es(s.mass_in_g, 0)} → {es(s.mass_out_g, 1)}" for s in result.stages],
        t("p.col.var"): [round(s.variance, 5) for s in result.stages],
        t("p.col.err"): [round(100 * s.rsd, 2) for s in result.stages],
        t("p.col.cum"): [round(100 * s.cum_rsd, 2) for s in result.stages],
        t("p.col.share"): [round(100 * s.share, 1) for s in result.stages],
    })  # fmt: skip
    st.dataframe(table, hide_index=True)
    st.caption(t("p.cum.caption",
                 corr=t("p.corr.yes") if result.lot_correction else t("p.corr.no")))  # fmt: skip
    left, right = st.columns(2)
    left.plotly_chart(stage_figure(view), width="stretch")
    right.plotly_chart(sensitivity_figure(view), width="stretch")
    st.caption(t("p.slope.caption"))
    fig = granulometry_figure(view)
    if fig is not None:
        st.plotly_chart(fig, width="stretch")


def gold_tab(gp: GoldParams, grade: float, aliquot: float) -> None:
    ficha("oro")
    try:
        view = run_gold(gp, grade, aliquot)
    except (gy.GyError, ValueError) as exc:
        st.error(t("err.gold", exc=tr_error(str(exc))))
        return
    sim = view.simulation
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("g.grains"), es(view.lam, 2))
    c2.metric(t("g.p0"), _pct(poisson_p0(view.lam)))
    c3.metric(t("g.median"), f"{es(sim.median_gpt, 2)} g/t",
              t("g.median.delta", grade=es(grade, 2)), delta_color="off")  # fmt: skip
    c4.metric(t("g.above"), _pct(sim.share_above(2.0)))
    if recommend_screen_fire_assay(view.lam):
        st.warning(t("g.sfa", lam=es(view.lam, 1), n=PARTICLES_CRITERION,
                     mass=es(SFA_MASS_G, 0), screen=es(SFA_SCREEN_UM, 0)))  # fmt: skip
    else:
        st.success(t("g.ok", lam=es(view.lam, 0), n=PARTICLES_CRITERION))
    mass20 = mass_for_particles(grade, view.grain_g)
    lo, hi = clifton_limits(view.lam)
    exact = poisson_exact_limits(max(view.lam, 0.5))
    st.caption(
        t(
            "g.caption1",
            n=PARTICLES_CRITERION,
            mass=es(mass20, 0),
            lam=es(view.lam, 1),
            lo=es(100 * lo, 0),
            hi=es(100 * hi, 0),
            elo=es(100 * exact[0], 0),
            ehi=es(100 * exact[1], 0),
        )
    )
    st.plotly_chart(histogram_figure(view), width="stretch")
    st.caption(t("g.caption2"))
    st.html(as_images(aliquot_svg(view), aliquot_svg(view), t("g.alt")))
    st.caption(t("g.grain", size=es(gp.grain_um, 0), shape=opt(gp.shape),
                 mass=es(view.grain_g * 1e6, 2)))  # fmt: skip


def _check_table(checks: list[val.Check]) -> str:
    df = pd.DataFrame({
        t("v.col.source"): [tm(c.source) for c in checks],
        t("v.col.concept"): [tm(c.item) for c in checks],
        t("v.col.published"): [decimal(c.published) for c in checks],
        t("v.col.calculated"): [decimal(c.calculated) for c in checks],
        t("v.col.unit"): [tm(c.unit) for c in checks],
        t("v.col.fits"): [t("v.yes") if c.ok else t("v.no") for c in checks],
        t("v.col.note"): [tm(c.note) for c in checks],
    })  # fmt: skip
    return markdown_table(df)


def validation_tab() -> None:
    m17, chi = val.minnitt_2017_checks(), val.chieregati_checks()
    cli, findings = val.clifton_checks(), val.minnitt_2007_findings()
    implied, lib = val.minnitt_2007_implied(), val.minnitt_2007_liberation()
    st.markdown(t("v.intro"))
    summary = pd.DataFrame({
        t("v.col.source"): [t(f"v.s{i}") for i in range(1, 7)],
        t("v.col.published"): [t(f"v.p{i}") for i in range(1, 7)],
        t("v.col.fits"): [
            t("v.f1", n=sum(c.ok for c in m17), m=len(m17)),
            t("v.f2", n=sum(c.ok for c in chi), m=len(chi)),
            t("v.f3", n=sum(c.ok for c in cli), m=len(cli)),
            t("v.f4", n=sum(c.ok for c in findings)),
            t("v.f5", n=sum(c.ok for c in implied), m=len(implied)),
            t("v.f6", n=sum(c.ok for c in lib), m=len(lib)),
        ],
    })  # fmt: skip
    st.markdown(markdown_table(summary))
    st.plotly_chart(variance_figure(m17 + chi), width="stretch")
    st.markdown(t("v.h.m17"))
    st.markdown(_check_table(m17))
    st.markdown(t("v.h.chi"))
    st.markdown(_check_table(chi))
    st.markdown(t("v.h.cli"))
    st.plotly_chart(clifton_figure(), width="stretch")
    st.markdown(_check_table(cli))
    st.markdown(t("v.h.m07"))
    st.warning(minnitt_2007_note())
    printed = next(c for c in findings if c.item == "error relativo").calculated
    implied_pct = next(c for c in implied if c.item == "error relativo").calculated
    st.plotly_chart(minnitt_2007_figure(printed, implied_pct), width="stretch")
    st.markdown(t("v.m07.printed"))
    st.markdown(_check_table(findings))
    st.markdown(t("v.m07.implied"))
    st.markdown(_check_table(implied))
    st.markdown(t("v.m07.lib"))
    st.markdown(_check_table(lib))


def main() -> None:
    sidebar_selector()
    st.title(t("app.title"))
    st.caption(t("app.caption"))
    st.html(MOTION_CSS)
    protocol, mineral, gold, aliquot, fusion_ui, cian, sed, cop = sidebar_config()
    animate = st.toggle(t("toggle.label"), value=True, help=t("toggle.help"))
    tab_guide, tab_protocol, tab_gold, tab_fusion, tab_cop, tab_cian, tab_sed, tab_validation = (
        st.tabs(
            [
                t("tab.guide"),
                t("tab.protocol"),
                t("tab.gold"),
                t("tab.fusion"),
                t("tab.cop"),
                t("tab.cian"),
                t("tab.sed"),
                t("tab.validation"),
            ]
        )
    )
    with tab_guide:
        guide_tab()
    with tab_protocol:
        protocol_tab(protocol, mineral)
    with tab_gold:
        gold_tab(gold, mineral.grade_gpt, aliquot)
    with tab_fusion:
        fusion_tab(fusion_ui, animate)
    with tab_cop:
        cop_tab(cop, fusion_ui, animate)
    with tab_cian:
        cian_tab(cian, animate)
    with tab_sed:
        sed_tab(sed, animate)
    with tab_validation:
        validation_tab()
        fusion_validation_section()
        cian_validation_section()
        sed_validation_section()
        cop_validation_section()


main()
