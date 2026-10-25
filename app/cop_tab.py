"""Pestaña «Copelación»: cuánto oro y plata se pierde en la copela según la temperatura, el plomo y
la plata presente, la ley corregida, la plata que hay que agregar (encuarte) para partir en ácido,
los gráficos de las tablas de Bugbee con el modelo encima y la animación; y su sección de
validación (pestaña Validación). Nada que escriba el visitante entra al SVG ni al HTML."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from calculo import FusionUIParams
from cop_calculo import FUENTES_PLOMO, CopParams, CopView, boton_de_fusion, run_cop
from cop_graficos import lead_figure, silver_figure, temperature_figure
from cop_svg import copelacion_svg
from dibujo import as_images, es
from guia import ficha, markdown_table
from i18n import decimal, opt, t

from muestreo import copelacion as cp
from muestreo import copelacion_datos as cd
from muestreo import copelacion_validacion as cv

STATE_CALL = {"buena": st.success, "lenta": st.info, "lamina": st.warning, "insuficiente": st.error}


def _error_text(exc: cp.CopelacionError) -> str:
    return t(f"cp.err.{exc.code}", **{k: es(v, 0) for k, v in exc.args_.items()})


def _range_text(code: str) -> str:
    """El texto del aviso de rango, con el rango de la tabla que se salió."""
    rango = {"temp": cp.T_AG_RANGO, "plomo": cp.PB_RANGO, "plata": cp.AG_RANGO}.get(code)
    if rango is None:
        return t(f"cp.warn.{code}", t0=es(cd.CONGELADO_C, 0), t1=es(cp.T_AU_RANGO[0], 0))
    return t(f"cp.warn.{code}", lo=es(rango[0], 0), hi=es(rango[1], 0))


def _metrics(v: CopView) -> None:
    r = v.res
    c1, c2, c3, c4 = st.columns(4)
    band = t("cp.m.band", lo=es(100 * r.perdida_ag.bajo, 2), hi=es(100 * r.perdida_ag.alto, 2))
    c1.metric(t("cp.m.ag"), f"{es(r.perdida_ag.pct, 2)} %", band, delta_color="off")
    c2.metric(t("cp.m.au"), f"{es(r.perdida_au.pct, 2)} %", t("cp.m.au.delta"), delta_color="off")
    c3.metric(t("cp.m.add"), f"{es(r.plata_agregada_mg, 2)} mg",
              t("cp.m.add.delta", ratio=es(r.razon_objetivo, 1)), delta_color="off")  # fmt: skip
    c4.metric(t("cp.m.pearl"), f"{es(r.perla_mg, 2)} mg",
              t("cp.m.pearl.delta", au=es(100 * r.oro_en_perla, 1)), delta_color="off")  # fmt: skip


def _warnings(v: CopView) -> None:
    if v.fusion_no_sirve:
        st.warning(t("cp.warn.fusion", pb=es(v.plomo_g, 1)))
    for code in v.res.avisos:
        st.warning(_range_text(code))


def calculator_section(v: CopView) -> None:
    r, p = v.res, v.params
    st.markdown(t("cp.cal.h"))
    source = t("cp.cal.pb.fusion") if v.plomo_de_fusion else t("cp.cal.pb.own")
    st.markdown(
        t("cp.cal.res", temp=es(r.temp_c, 0), pb=es(v.plomo_g, 1), source=source,
          au=es(r.oro_mg, 2), ag=es(r.plata_total_mg, 2),
          lag=es(r.perdida_ag.pct, 2), lau=es(r.perdida_au.pct, 2), rho=es(v.rho_plomo, 2))
    )  # fmt: skip
    st.markdown(
        t(
            "cp.cal.ley",
            med=es(p.ley_gpt, 2),
            cor=es(v.ley_au_corregida, 2),
            lau=es(r.perdida_au.pct, 2),
        )
    )
    st.caption(t("cp.cal.caption", sd=es(100 * cp.SD_LN, 0), f=es(cp.FACTOR_BANDA, 2)))


def rose_frame() -> pd.DataFrame:
    rows = [(t("cp.rose.lt"), f"{es(cd.ROSE_BAJO[0], 0)} {t('cp.or')} {es(cd.ROSE_BAJO[1], 0)}")]
    rows += [(es(mg, 1), es(r, 1)) for mg, r in cd.ROSE[1:-1]]
    rows.append((t("cp.rose.gt", mg=es(cd.ROSE[-1][0], 0)), es(cd.ROSE[-1][1], 1)))
    return pd.DataFrame(rows, columns=[t("cp.rose.au"), t("cp.rose.ratio")])


def inquartation_section(v: CopView) -> None:
    r = v.res
    st.markdown(t("cp.enc.h"))
    st.markdown(t("cp.enc.intro", mode=opt(v.params.modo), ratio=es(r.razon_objetivo, 2)))
    table = pd.DataFrame({
        t("cp.enc.col.what"): [t("cp.enc.au"), t("cp.enc.ag0"), t("cp.enc.add"),
                               t("cp.enc.ag1"), t("cp.enc.ag2"), t("cp.enc.au2"),
                               t("cp.enc.pearl")],
        "mg": [round(x, 3) for x in (r.oro_mg, r.plata_presente_mg, r.plata_agregada_mg,
                                     r.plata_total_mg, r.plata_final_mg, r.oro_final_mg,
                                     r.perla_mg)],
    })  # fmt: skip
    st.dataframe(table, hide_index=True)
    STATE_CALL[r.estado](t(f"cp.enc.state.{r.estado}", ratio=es(r.razon_final, 1),
                           min=es(cd.MINIMO_PARTIR, 0), rec=es(cd.RECOMENDADO_MIN, 0),
                           low=es(cd.LINGOTE_RAZON[0], 0)))  # fmt: skip
    st.caption(
        t(
            "cp.enc.caption",
            rec=es(cd.RECOMENDADO_MIN, 0),
            hi=es(cd.RECOMENDADO_MAX, 0),
            bullion=es(cd.LINGOTE_RAZON[0], 0),
            bullion2=es(cd.LINGOTE_RAZON[1], 1),
            gold=es(100 * cd.MAX_ORO_FRACCION, 0),
        )
    )
    with st.expander(t("cp.rose.h")):
        st.dataframe(rose_frame(), hide_index=True)
        st.caption(t("cp.rose.caption", mid=es(cd.ROSE[0][1], 0)))


def charts_section(v: CopView) -> None:
    st.markdown(t("cp.plot.h"))
    st.caption(t("cp.plot.intro"))
    a, b, c = st.columns(3)
    a.plotly_chart(temperature_figure(v), width="stretch")
    b.plotly_chart(lead_figure(v), width="stretch")
    c.plotly_chart(silver_figure(v), width="stretch")
    st.caption(t("cp.plot.caption"))


def animation_section(v: CopView, animate: bool) -> None:
    st.markdown(t("cp.ani.h"))
    st.html(as_images(copelacion_svg(v, paused=not animate), copelacion_svg(v, paused=True),
                      t("cp.ani.alt")))  # fmt: skip
    st.caption(t("cp.ani.caption"))


def cop_tab(p: CopParams, fusion_ui: FusionUIParams, animate: bool) -> None:
    ficha("copelacion")
    boton = boton_de_fusion(fusion_ui) if p.plomo_fuente == FUENTES_PLOMO[0] else None
    try:
        view = run_cop(p, boton)
    except cp.CopelacionError as exc:
        st.error(_error_text(exc))
        return
    _metrics(view)
    _warnings(view)
    calculator_section(view)
    inquartation_section(view)
    charts_section(view)
    animation_section(view, animate)


# ------------------------------------------------------------------ validación
def _tables_frame() -> pd.DataFrame:
    rows = [
        ("IX", len(cd.TABLA_IX), "Lodge", "cp.v.t.ix"), ("X", len(cd.TABLA_X), "Lodge", "cp.v.t.x"),
        ("XI", len(cd.TABLA_XI), "Godshall", "cp.v.t.xi"),
        ("XII", len(cd.TABLA_XII), "Lodge", "cp.v.t.xii"),
    ]  # fmt: skip
    return pd.DataFrame({
        t("cp.v.col.table"): [x[0] for x in rows],
        t("cp.v.col.page"): [cd.PAGINA_IMPRESA[x[0]] for x in rows],
        t("cp.v.col.scan"): [cd.PAGINA_ESCANEO[x[0]] for x in rows],
        t("cp.v.col.rows"): [x[1] for x in rows],
        t("cp.v.col.author"): [x[2] for x in rows],
        t("cp.v.col.what"): [t(x[3]) for x in rows],
    })  # fmt: skip


def _quantitative_frame() -> pd.DataFrame:
    cells = cv.celdas_cuantitativas()
    return pd.DataFrame({
        t("cp.v.col.ag"): [decimal(c.plata_mg) for c in cells],
        t("cp.v.col.pb"): [decimal(round(c.plomo_g, 2)) for c in cells],
        t("cp.v.col.pub"): [decimal(c.publicada) for c in cells],
        t("cp.v.col.pred"): [decimal(round(c.predicha, 3)) for c in cells],
        t("cp.v.col.err"): [decimal(round(100 * c.error_relativo, 1)) for c in cells],
        t("cp.v.col.fits"): [t("v.yes") if c.cuadra else t("v.no") for c in cells],
        t("cp.v.col.timp"): [decimal(round(c.temp_implicita_c)) for c in cells],
    })  # fmt: skip


def cop_validation_section() -> None:
    """Sección «Copelación» de la pestaña Validación."""
    cells = cv.celdas_cuantitativas()
    trend, rep = cv.tendencias(), cv.razones_de_plata()
    st.markdown(t("cp.v.h"))
    st.markdown(t("cp.v.intro", a=es(cd.A_T_G, 2), t0=es(cv.T_VALIDACION_C, 0)))
    st.markdown(t("cp.v.h.tables"))
    st.markdown(markdown_table(_tables_frame()))
    diff = [x for x in cv.cita_tabla_xi() if x[1] != x[2]]
    ag, bugbee, godshall = diff[0]
    st.markdown(t("cp.v.xi.note", ag=es(ag, 0), b=es(bugbee, 2), g=es(godshall, 2)))
    st.markdown(t("cp.v.h.overlap"))
    plomos = [cv.plomo_g(a) for a in cd.GODSHALL_PLOMO_AT]
    st.markdown(t("cp.v.overlap", n=len(cells), total=len(cv.celdas_finales()),
                  cut=es(100 * cv.CORTE_RELATIVO, 0), pbmin=es(min(plomos), 1),
                  pbmax=es(max(plomos), 1)))  # fmt: skip
    st.markdown(markdown_table(_quantitative_frame()))
    timp = [c.temp_implicita_c for c in cells if c.temp_implicita_c is not None]
    st.markdown(t("cp.v.verdict", ok=sum(c.cuadra for c in cells), n=len(cells),
                  tlo=es(round(min(timp), -1), 0), thi=es(round(max(timp), -1), 0)))  # fmt: skip
    st.markdown(t("cp.v.h.trend"))
    st.markdown(t("cp.v.trend", a=trend.plata_mas_pierde[0], na=trend.plata_mas_pierde[1],
                  b=trend.plomo_mas_pierde[0], nb=trend.plomo_mas_pierde[1],
                  c=trend.orden_de_magnitud[0], nc=trend.orden_de_magnitud[1],
                  f=es(cv.FACTOR_ORDEN, 0)))  # fmt: skip
    fails = sorted({x.plata_mg for x in rep if not x.cuadra})
    st.markdown(t("cp.v.rep", n=sum(x.cuadra for x in rep), total=len(rep),
                  cut=es(100 * cv.CORTE_RELATIVO, 0),
                  fails=", ".join(es(x, 0) for x in fails)))  # fmt: skip
    st.markdown(t("cp.v.not"))
