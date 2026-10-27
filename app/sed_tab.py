"""Pestaña «Ensayo de sedimentación»: de la curva h(t) de una probeta al diámetro de un espesador.
Ficha, curva (modelo de Luz o tabla editable), construcción de Talmage-Fitch, curva de flujo de
Kynch, dimensionamiento con el factor de corrección, tabla de Vale, Coe y Clevenger (1916) y la
animación; y su sección de validación (pestaña Validación). Nada que escriba el visitante entra al
SVG ni al HTML: la tabla solo alimenta números."""

from __future__ import annotations

import carga
import pandas as pd
import streamlit as st
from dibujo import as_images, es
from guia import ficha, markdown_table
from i18n import decimal, t
from sed_calculo import (
    FUENTES,
    H_MAX_M,
    T_MAX_S,
    SedParams,
    SedView,
    run_sed,
    tabla_de_luz,
)
from sed_estado import estado_sed, prueba_sed
from sed_graficos import curve_figure, kynch_figure
from sed_svg import settling_svg

from muestreo import sedimentacion as sd
from muestreo import sedimentacion_datos as dd

TABLE_KEY = "sed_tabla"
ROW_PX = 35  # alto de una fila de st.dataframe
COLUMNAS = (carga.Columna("t", "sd.col.t"), carga.Columna("h", "sd.col.h"))
FT = 0.3048  # m por pie
SHORT_TON = 0.90718474  # t por tonelada corta
APPS = {"lama": "sd.app.lama", "pellet feed": "sd.app.pellet", "alim. flotación": "sd.app.flot"}


def example_table() -> pd.DataFrame:
    rows = tabla_de_luz()
    return pd.DataFrame({"t": [a for a, _ in rows], "h": [b for _, b in rows]})


def _error_text(exc: sd.SedimentacionError) -> str:
    return t(f"sd.err.{exc.code}", **{k: es(v, 0) for k, v in exc.args_.items()})


def _rows(edited: pd.DataFrame) -> list[list]:
    return [[None if pd.isna(x) else x for x in r] for r in edited[["t", "h"]].values.tolist()]


def curve_section(p: SedParams) -> SedView | None:
    st.markdown(t("sd.cur.h"))
    st.markdown(t("sd.cur.intro", z0=es(p.z0, 3), zinf=es(p.z_inf, 3), a=es(p.a, 3), b=es(p.b, 0)))
    number = st.column_config.NumberColumn
    config = {
        "t": number(t("sd.col.t"), min_value=0.0, max_value=T_MAX_S, step=10.0, required=True),
        "h": number(
            t("sd.col.h"),
            min_value=0.0,
            max_value=H_MAX_M,
            step=0.001,
            format="%.4f",
            required=True,
        ),
    }
    edited = st.data_editor(
        carga.panel(TABLE_KEY, COLUMNAS, example_table(), "plantilla_sedimentacion.csv"),
        key=TABLE_KEY,
        num_rows="dynamic",
        hide_index=True,
        column_config=config,
        width="stretch",
    )
    st.button(t("sd.reset"), on_click=carga.reiniciar, args=(TABLE_KEY,))
    rows = _rows(edited) if p.fuente != FUENTES[0] else None
    st.caption(t("sd.cur.source", fuente=t("opt." + p.fuente)))
    try:
        return run_sed(p, rows)
    except sd.SedimentacionError as exc:
        st.warning(_error_text(exc))
        return None


def construction_section(v: SedView) -> None:
    tf = v.tf
    st.markdown(t("sd.tf.h"))
    st.markdown(
        t(
            "sd.tf.res",
            modo=t("sd.tf.modo." + tf.modo),
            c0=es(v.c0, 4),
            cu=es(v.cu, 4),
            hu=es(tf.hu_m, 4),
            tc=es(tf.tc_s, 0),
            hc=es(tf.hc_m, 4),
            v=es(tf.v_c_m_h, 3),
            tu=es(tf.tu_s, 0),
            au=es(tf.area_unitaria_m2_t_dia, 3),
        )
    )
    st.plotly_chart(curve_figure(v), width="stretch")
    fig = kynch_figure(v)
    st.markdown(t("sd.ky.h"))
    if fig is None:
        st.info(t("sd.ky.none"))
        return
    st.plotly_chart(fig, width="stretch")
    gl = v.g_limite
    if gl is not None:
        st.caption(
            t(
                "sd.ky.cap",
                gl=es(gl[0], 3),
                cc=es(gl[1], 4),
                area=es(v.y_area_flujo_limite, 3),
                tf=es(tf.area_unitaria_m2_t_dia, 3),
            )
        )


def sizing_section(v: SedView) -> None:
    p = v.params
    st.markdown(t("sd.dim.h"))
    st.markdown(
        t(
            "sd.dim.res",
            au=es(v.tf.area_unitaria_m2_t_dia, 3),
            factor=es(v.factor, 2),
            auc=es(v.area_unitaria_corregida, 3),
            tph=es(p.tph, 0),
            area=es(v.area_m2, 0),
            d=es(v.diametro_m, 1),
        )
    )
    if v.factor == 1.0:
        st.caption(t("sd.dim.nofactor"))


def scale_section() -> None:
    st.markdown(t("sd.sc.h"))
    au3 = next(r[5] for r in dd.VALE_T3 if r[0] == dd.VALE_T3_ENSAYO)
    au_ind = sd.area_unitaria_m2_t_dia(dd.VALE_T2_D, dd.VALE_T2_TPH)
    st.markdown(
        t(
            "sd.sc.res",
            au3=es(au3, 3),
            area=es(dd.VALE_T2_AREA, 2),
            d=es(dd.VALE_T2_D, 0),
            tph=es(dd.VALE_T2_TPH, 1),
            au=es(au_ind, 3),
            f=es(dd.factor_vale(), 2),
            inv=es(dd.factor_inverso(), 2),
            pellet=es(sd.FACTOR_VALE_PELLET, 1),
        )
    )


def vale_frame() -> pd.DataFrame:
    rows = []
    for mina, qtd, app, tph, _d50, cma, cmu, au, diam in dd.VALE_T1:
        calc_au = sd.area_unitaria_m2_t_dia(diam, tph)
        calc_d = sd.diametro_desde_area_unitaria(au, tph)
        ok = round(calc_au, 3) == au and round(calc_d) == diam
        rows.append(
            {
                t("sd.v.mina"): mina,
                t("sd.v.qtd"): qtd,
                t("sd.v.app"): t(APPS[app]),
                t("sd.v.tph"): tph,
                t("sd.v.cma"): "–" if cma is None else es(cma, 1),
                t("sd.v.cmu"): cmu,
                t("sd.v.au"): au,
                t("sd.v.auc"): round(calc_au, 3),
                t("sd.v.d"): diam,
                t("sd.v.dc"): round(calc_d, 1),
                t("sd.v.ok"): t("sd.yes") if ok else t("sd.no"),
            }
        )
    return pd.DataFrame(rows)


def vale_section() -> None:
    st.markdown(t("sd.v.h"))
    st.markdown(t("sd.v.intro"))
    frame = vale_frame()
    st.dataframe(frame, hide_index=True, width="stretch", height=ROW_PX * (len(frame) + 1) + 3)


def coe_frame() -> pd.DataFrame:
    rows = []
    for i, (f, r, pub) in enumerate(dd.CC_ENSAYOS, start=1):
        calc = sd.coe_clevenger_pies2_ton_dia(f, dd.CC_D, r)
        rows.append(
            {
                t("sd.cc.n"): i,
                t("sd.cc.f"): f,
                t("sd.cc.r"): r,
                t("sd.cc.pub"): pub,
                t("sd.cc.calc"): round(calc, 2),
                t("sd.cc.ok"): t("sd.yes") if round(calc, 2) == pub else t("sd.no"),
            }
        )
    return pd.DataFrame(rows)


def coe_section() -> None:
    st.markdown(t("sd.cc.h"))
    a = dd.cc_area()
    pies2 = a * dd.CC_TON_DIA
    d_ft = sd.diametro_pies(pies2)
    r_m = dd.CC_R * FT
    a_si = sd.coe_clevenger_m2_t_dia(dd.CC_F, dd.CC_D, r_m)
    st.markdown(
        t(
            "sd.cc.res",
            f=es(dd.CC_F, 2),
            d=es(dd.CC_D, 2),
            r=es(dd.CC_R, 3),
            a=es(a, 2),
            pies2=es(pies2, 0),
            dft=es(d_ft, 1),
            dm=es(d_ft * FT, 1),
            asi=es(a_si, 3),
            ton=es(dd.CC_TON_DIA, 0),
        )
    )
    st.dataframe(coe_frame(), hide_index=True, width="stretch")
    st.caption(t("sd.cc.note", d=es(dd.CC_D, 2)))


def animation_section(v: SedView, animate: bool) -> None:
    st.markdown(t("sd.ani.h"))
    st.html(
        as_images(
            settling_svg(v, paused=not animate), settling_svg(v, paused=True), t("sd.ani.alt")
        )
    )
    st.caption(t("sd.ani.caption"))


def sed_tab(p: SedParams, animate: bool) -> None:
    ficha("sedimentacion")
    estado = st.container()  # va arriba, pero se llena cuando la curva ya dio su resultado
    view = curve_section(p)
    if view is not None:
        with estado:
            estado_sed(view)
        construction_section(view)
        sizing_section(view)
    scale_section()
    vale_section()
    coe_section()
    if view is not None:
        animation_section(view, animate)
    prueba_sed()


# ------------------------------------------------------------------ validación
def _check_table(checks: list[dd.SedCheck]) -> str:
    df = pd.DataFrame(
        {
            t("sv.col.concept"): [f"{t('sv.kind.' + x.kind)} {x.label}".strip() for x in checks],
            t("sv.col.published"): [decimal(x.published) for x in checks],
            t("sv.col.calculated"): [decimal(round(x.calculated, x.decimals)) for x in checks],
            t("sv.col.fits"): [t("v.yes") if x.ok else t("v.no") for x in checks],
            t("sv.col.note"): [t("sv.note." + x.note) if x.note else "" for x in checks],
        }
    )
    return markdown_table(df)


def sed_validation_section() -> None:
    """Sección «Ensayo de sedimentación» de la pestaña Validación."""
    st.markdown(t("sv.h"))
    checks = dd.all_checks()
    s = dd.summary(checks)
    st.markdown(t("sv.intro"))
    st.markdown(
        t(
            "sv.summary",
            cc=s["cc"][0],
            ncc=s["cc"][1],
            v1=s["v1"][0],
            nv1=s["v1"][1],
            v2=s["v2"][0],
            nv2=s["v2"][1],
            v3=s["v3"][0],
            nv3=s["v3"][1],
            kn=s["kn"][0],
            nkn=s["kn"][1],
        )
    )
    for src in ("cc", "v2", "v3", "kn"):
        st.markdown(t("sv.h." + src))
        st.markdown(_check_table([x for x in checks if x.source == src]))
    st.markdown(t("sv.h.v1"))
    bad = [x for x in checks if x.source == "v1" and not x.ok]
    st.markdown(t("sv.v1.res", ok=s["v1"][0], n=s["v1"][1]))
    st.markdown(_check_table(bad))
    err, npts, c_lo, c_hi = dd.kynch_error()
    st.markdown(
        t(
            "sv.kn.res",
            err=es(100 * err, 5),
            n=npts,
            lo=es(c_lo, 3),
            hi=es(c_hi, 3),
            v0=es(dd.SINT_V0, 0),
            cmax=es(dd.SINT_CMAX, 2),
            n_exp=es(dd.SINT_N, 0),
        )
    )
    ty = dd.talmage_vs_yoshioka()
    st.markdown(
        t(
            "sv.ty.res",
            y=es(ty["yoshioka"], 4),
            a5=es(ty["tf_0.5"], 4),
            d5=es(ty["dif_0.5"], 1),
            a9=es(ty["tf_0.9"], 4),
            d9=es(ty["dif_0.9"], 1),
            a99=es(ty["tf_0.999"], 4),
            d99=es(ty["dif_0.999"], 4),
        )
    )
    st.markdown(t("sv.notes"))
