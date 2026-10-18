"""App «Laboratorio de ensayos al fuego, fase 1: preparación de muestras»: cuánto error de muestreo
mete cada etapa de un protocolo y cuánto se acumula, el oro grueso en la alícuota y la validación
de la ecuación de Gy contra números publicados. Pestañas: Guía, Protocolo, Oro grueso y
Validación."""

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
from controles import sidebar_config  # noqa: E402
from dibujo import MOTION_CSS, as_images, es  # noqa: E402
from guia import MINNITT_2007_NOTE, ficha, guide_tab, markdown_table  # noqa: E402
from nomograma import (  # noqa: E402
    granulometry_figure,
    nomogram_figure,
    sensitivity_figure,
    stage_figure,
)
from oro_graficos import aliquot_svg, histogram_figure  # noqa: E402
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

st.set_page_config(page_title="Laboratorio de ensayos al fuego: muestreo", layout="wide")


def _pct(x: float, decimals: int = 1) -> str:
    return f"{es(100 * x, decimals)} %"


def protocol_tab(p: ProtocolParams, mp: MineralParams) -> None:
    ficha("protocolo")
    try:
        view = run_protocol(p, mp)
    except (gy.GyError, ValueError) as exc:
        st.error(f"No se pudo calcular el protocolo con estos datos: {exc}")
        return
    result = view.result
    worst_index = max(range(len(result.stages)), key=lambda i: result.stages[i].variance)
    worst = result.stages[worst_index]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Error total del protocolo", _pct(result.rsd))
    share = f"{_pct(worst.share, 0)} de la varianza"
    c2.metric("Etapa que más aporta", f"Etapa {worst_index + 1}", share, delta_color="off")
    c3.metric("Error de la última división", _pct(result.stages[-1].rsd))
    c4.metric("Cada división bajo la seguridad", "sí" if view.meets_safety else "no",
              f"seguridad {es(p.safety_pct, 0)} %", delta_color="off")  # fmt: skip
    if p.preset == PRESETS[2]:
        st.info("Este protocolo usa sus propias masas y tamaños (Minnitt 2017, Tabla VIII); la "
                "masa recibida, la alícuota y la pendiente m no cambian nada.")  # fmt: skip
    st.caption(f"Mineral: {view.mineral.name}. " + (
        "K y α son los que Minnitt (2017) calibró para una mena de oro de Witwatersrand: no valen "
        "para otro mineral." if view.mineral.name.startswith("Calibrado") else ""
    ))  # fmt: skip
    st.plotly_chart(nomogram_figure(view), width="stretch")
    st.caption(
        "Cada tramo horizontal reduce el tamaño (masa constante); cada tramo vertical divide "
        "(tamaño constante). Las rectas son de error constante: la ruta debe quedar por encima "
        "de la línea de seguridad. «Reproducir» recorre las etapas. El tamaño inicial solo "
        "dibuja el primer tramo."
    )
    table = pd.DataFrame({
        "Etapa": [s.name for s in result.stages],
        "dN (cm)": [round(s.d_n_cm, 5) for s in result.stages],
        "Masa de entrada → salida (g)": [f"{es(s.mass_in_g, 0)} → {es(s.mass_out_g, 1)}"
                                         for s in result.stages],
        "Varianza relativa": [round(s.variance, 5) for s in result.stages],
        "Error de la etapa (%)": [round(100 * s.rsd, 2) for s in result.stages],
        "Error acumulado (%)": [round(100 * s.cum_rsd, 2) for s in result.stages],
        "Parte de la varianza (%)": [round(100 * s.share, 1) for s in result.stages],
    })  # fmt: skip
    st.dataframe(table, hide_index=True)
    st.caption(
        "El error acumulado es la raíz de la suma de las varianzas relativas. Corrección por masa "
        f"del lote: {'sí' if result.lot_correction else 'no (como en la Tabla VIII de Minnitt)'}."
    )
    left, right = st.columns(2)
    left.plotly_chart(stage_figure(view), width="stretch")
    right.plotly_chart(sensitivity_figure(view), width="stretch")
    st.caption(
        "Pendiente m de Rosin-Rammler: es un supuesto. Entre m = 0,5 y 3 el error total cambia "
        "mucho porque el d95 entra al cubo."
    )
    fig = granulometry_figure(view)
    if fig is not None:
        st.plotly_chart(fig, width="stretch")


def gold_tab(gp: GoldParams, grade: float, aliquot: float) -> None:
    ficha("oro")
    try:
        view = run_gold(gp, grade, aliquot)
    except (gy.GyError, ValueError) as exc:
        st.error(f"No se pudo calcular el oro con estos datos: {exc}")
        return
    sim = view.simulation
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Granos esperados en la alícuota", es(view.lam, 2))
    c2.metric("Probabilidad de ningún grano", _pct(poisson_p0(view.lam)))
    c3.metric("Mediana de los 1 000 ensayos", f"{es(sim.median_gpt, 2)} g/t",
              f"ley real {es(grade, 2)} g/t", delta_color="off")  # fmt: skip
    c4.metric("Ensayos con más de 2× la ley real", _pct(sim.share_above(2.0)))
    if recommend_screen_fire_assay(view.lam):
        st.warning(
            f"Se esperan {es(view.lam, 1)} granos por alícuota, menos de {PARTICLES_CRITERION} "
            f"(criterio de Clifton): conviene el **screen fire assay** (unos {es(SFA_MASS_G, 0)} g "
            f"tamizados a {es(SFA_SCREEN_UM, 0)} µm, el fino en duplicado y el grueso entero)."
        )
    else:
        st.success(f"Se esperan {es(view.lam, 0)} granos por alícuota: cumple el criterio de "
                   f"{PARTICLES_CRITERION} partículas de Clifton.")  # fmt: skip
    mass20 = mass_for_particles(grade, view.grain_g)
    lo, hi = clifton_limits(view.lam)
    exact = poisson_exact_limits(max(view.lam, 0.5))
    st.caption(
        f"Para {PARTICLES_CRITERION} granos harían falta {es(mass20, 0)} g de muestra. Con "
        f"{es(view.lam, 1)} granos, los límites al 95 % de Clifton son {es(100 * lo, 0)} % y "
        f"+{es(100 * hi, 0)} % (Poisson exacto: {es(100 * exact[0], 0)} % y "
        f"+{es(100 * exact[1], 0)} %; con pocos granos las ecuaciones de Clifton no valen del "
        "todo)."
    )
    st.plotly_chart(histogram_figure(view), width="stretch")
    st.caption(
        "La ley real (verde) y la mediana de lo simulado (rojo) no coinciden: con pocos granos, "
        "la mayoría de los ensayos da menos que la ley y unos pocos dan mucho más. «Reproducir» "
        "acumula de 10 a 1 000 ensayos."
    )
    st.html(as_images(aliquot_svg(view), aliquot_svg(view), "Tres alícuotas con granos de oro"))
    st.caption(f"Grano de {es(gp.grain_um, 0)} µm ({gp.shape}): {es(view.grain_g * 1e6, 2)} µg.")


def _check_table(checks: list[val.Check]) -> str:
    def number(x: float) -> str:
        return f"{x:.6g}".replace(".", ",")

    df = pd.DataFrame({
        "Fuente": [c.source for c in checks],
        "Concepto": [c.item for c in checks],
        "Publicado": [number(c.published) for c in checks],
        "Calculado": [number(c.calculated) for c in checks],
        "Unidad": [c.unit for c in checks],
        "¿Cuadra?": ["sí" if c.ok else "no" for c in checks],
        "Nota": [c.note for c in checks],
    })  # fmt: skip
    return markdown_table(df)


def validation_tab() -> None:
    m17, chi = val.minnitt_2017_checks(), val.chieregati_checks()
    cli, findings = val.clifton_checks(), val.minnitt_2007_findings()
    implied, lib = val.minnitt_2007_implied(), val.minnitt_2007_liberation()
    st.markdown(
        "Cada fuente se calcula con la ecuación de Gy y se compara con lo que publica. Lo que no "
        "cuadra se muestra tal cual."
    )
    summary = pd.DataFrame({
        "Fuente": ["Minnitt 2017, Tabla VIII", "Chieregati 2017, Tabla 2",
                   "Clifton 1969, Fig. 4", "Minnitt 2007, problemas 1 a 3 y apéndice",
                   "Minnitt 2007 con c·f·g·ℓ = 448", "Minnitt 2007, apéndice (dℓ)"],
        "Publicado": ["19 varianzas por etapa (DSA y SFA)", "varianza y error de 4 etapas",
                      "límites al 95 % de 7, 20, 75 y 400 partículas", "29,58 %, ≈16 kg y 0,9 cm",
                      "los mismos", "dℓ = 0,001337 cm y 0,0011977 cm"],
        "¿Cuadra?": [f"{sum(c.ok for c in m17)} de {len(m17)} filas",
                     f"{sum(c.ok for c in chi)} de {len(chi)}",
                     f"{sum(c.ok for c in cli)} de {len(cli)} límites (±2 puntos)",
                     f"{sum(c.ok for c in findings)} de 4 con los datos impresos "
                     "(errata del artículo)",
                     f"{sum(c.ok for c in implied)} de {len(implied)}",
                     f"{sum(c.ok for c in lib)} de {len(lib)}"],
    })  # fmt: skip
    st.markdown(markdown_table(summary))
    st.plotly_chart(variance_figure(m17 + chi), width="stretch")
    st.markdown("#### Minnitt (2017), Tabla VIII: varianza por etapa")
    st.markdown(_check_table(m17))
    st.markdown("#### Chieregati (2017), Tabla 2: protocolo de cobre")
    st.markdown(_check_table(chi))
    st.markdown("#### Clifton y colaboradores (1969), Fig. 4: límites al 95 %")
    st.plotly_chart(clifton_figure(), width="stretch")
    st.markdown(_check_table(cli))
    st.markdown("#### Minnitt, Rice y Spangenberg (2007): un hallazgo, no una validación")
    st.warning(MINNITT_2007_NOTE)
    printed = next(c for c in findings if c.item == "error relativo").calculated
    implied_pct = next(c for c in implied if c.item == "error relativo").calculated
    st.plotly_chart(minnitt_2007_figure(printed, implied_pct), width="stretch")
    st.markdown("**Con los datos impresos** (c = 16 000 000, f = 0,5, g = 0,25, ℓ = 0,000035):")
    st.markdown(_check_table(findings))
    st.markdown("**Con c·f·g·ℓ = 448**, el valor que implican los resultados publicados "
                "(documenta la errata; no valida la fórmula):")  # fmt: skip
    st.markdown(_check_table(implied))
    st.markdown("**La parte del apéndice que sí cuadra:**")
    st.markdown(_check_table(lib))


def main() -> None:
    st.title("Laboratorio de ensayos al fuego: preparación de muestras")
    st.caption(
        "Cuánto error de muestreo mete cada etapa de la preparación y cuántos granos de oro caen "
        "en la alícuota, con la ecuación de Gy validada contra números publicados. Fase 1: sin "
        "fusión ni química del ensayo. Empieza por la **Guía**; los datos se cambian en la "
        "barra lateral. Códigos de preparación públicos de ALS; sin afiliación."
    )
    st.html(MOTION_CSS)
    protocol, mineral, gold, aliquot = sidebar_config()
    tab_guide, tab_protocol, tab_gold, tab_validation = st.tabs(
        ["Guía", "Protocolo", "Oro grueso", "Validación"]
    )
    with tab_guide:
        guide_tab()
    with tab_protocol:
        protocol_tab(protocol, mineral)
    with tab_gold:
        gold_tab(gold, mineral.grade_gpt, aliquot)
    with tab_validation:
        validation_tab()


main()
