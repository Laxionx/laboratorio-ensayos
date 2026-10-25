"""Pestaña «Control de calidad»: la carta de control de un CRM con ±2 SD y ±3 SD, los duplicados
(Thompson-Howarth y diferencia relativa), los blancos y cómo se certifica un estándar; y su
sección de validación (pestaña Validación). Los números salen de `muestreo.qaqc`; lo que escribe
el visitante en una tabla solo alimenta números y nunca entra al HTML ni a un gráfico como texto."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from dibujo import es
from guia import ficha, markdown_table
from i18n import decimal, int_num, opt, t
from qaqc_calculo import (
    DUP_FUENTES,
    FUENTES,
    BlkView,
    CertView,
    CrmView,
    DupView,
    QaqcParams,
    run_blk,
    run_cert,
    run_crm,
    run_dup,
    tabla_blancos,
    tabla_crm,
    tabla_duplicados,
)
from qaqc_graficos import blk_figure, cert_figure, crm_figure, rpd_figure, th_figure

from muestreo import qaqc as qc
from muestreo import qaqc_validacion as qv

KEY_CRM, KEY_DUP, KEY_BLK = "qaqc_tabla_crm", "qaqc_tabla_dup", "qaqc_tabla_blk"
VALOR_MAX = 1_000_000.0  # tope de una celda de la tabla editable
VERDICT_CALL = {
    qc.PASA: st.success,
    qc.AVISO: st.info,
    qc.REENSAYAR: st.warning,
    qc.RECHAZAR: st.error,
}
BLANK_CALL = {qc.BLANCO_OK: st.success, qc.BLANCO_ALERTA: st.warning, qc.BLANCO_FALLA: st.error}


def _error_text(exc: qc.QaqcError) -> str:
    return t(f"qc.err.{exc.code}", **{k: es(v, 0) for k, v in exc.args_.items()})


def _reset(*keys: str) -> None:
    for key in keys:
        st.session_state.pop(key, None)


def _cell(x: object) -> object:
    return None if pd.isna(x) else x


def _column(df: pd.DataFrame, name: str) -> list:
    return [_cell(x) for x in df[name].tolist()]


def _number_column(label_key: str) -> object:
    return st.column_config.NumberColumn(
        t(label_key), min_value=0.0, max_value=VALOR_MAX, step=0.001, format="%.4f"
    )


def _editor(key: str, frame: pd.DataFrame, columns: dict) -> pd.DataFrame:
    edited = st.data_editor(
        frame, key=key, num_rows="dynamic", hide_index=True, column_config=columns, width="stretch"
    )
    st.button(t("qc.reset"), key=key + "_reset", on_click=_reset, args=(key,))
    return edited


def _table_or_hint(
    use_table: bool, key: str, frame: pd.DataFrame, columns: dict
) -> pd.DataFrame | None:
    if use_table:
        return _editor(key, frame, columns)
    st.caption(t("qc.table.hint", max=int_num(qc.MAX_FILAS)))
    return None


# ------------------------------------------------------------------ CRM
def _crm_intro(v: CrmView) -> None:
    if v.sd_publicada is None:
        note = t("qc.crm.sdnote.own")
    else:
        rsd = 100.0 * v.sd / v.certificado
        note = t("qc.crm.sdnote.pub", sdpub=es(v.sd_publicada, 3), rsd=es(rsd, 2))
    (lo2, hi2), (lo3, hi3) = v.lim2, v.lim3
    st.markdown(
        t(
            "qc.crm.intro",
            name=opt(v.nombre),
            v=es(v.certificado, 3),
            sd=es(v.sd, 5),
            sdnote=note,
            lo2=es(lo2, 3),
            hi2=es(hi2, 3),
            lo3=es(lo3, 3),
            hi3=es(hi3, 3),
        )
    )


def _crm_metrics(v: CrmView) -> None:
    r = v.veredicto
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("qc.crm.m.n"), int_num(r.n))
    c2.metric(
        t("qc.crm.m.f2"),
        int_num(r.n_fuera_2sd),
        t("qc.crm.m.f2.delta", pct=es(100 * r.frac_fuera_2sd, 1)),
        delta_color="off",
    )
    c3.metric(
        t("qc.crm.m.f3"),
        int_num(r.n_fuera_3sd),
        t("qc.crm.m.f3.delta", pct=es(100 * r.tasa_3sd, 1)),
        delta_color="off",
    )
    c4.metric(
        t("qc.crm.m.bias"),
        f"{es(r.sesgo_pct, 2)} %",
        t("qc.crm.m.bias.delta", mean=es(r.media, 4)),
        delta_color="off",
    )


def _crm_verdict(v: CrmView) -> None:
    r = v.veredicto
    text = t(
        f"qc.crm.v.{r.veredicto}",
        n=int_num(r.n),
        f2=int_num(r.n_fuera_2sd),
        f3=int_num(r.n_fuera_3sd),
        pares=int_num(r.n_pares),
        pct=es(100 * (r.tasa_3sd if r.veredicto == qc.RECHAZAR else r.frac_fuera_2sd), 1),
    )
    VERDICT_CALL[r.veredicto](text)


def crm_section(p: QaqcParams) -> CrmView | None:
    st.markdown(t("qc.crm.h"))
    own = p.crm_fuente != FUENTES[0]
    frame = pd.DataFrame({"res": tabla_crm(p)})
    edited = _table_or_hint(own, KEY_CRM, frame, {"res": _number_column("qc.col.res")})
    try:
        view = run_crm(p, None if edited is None else _column(edited, "res"))
    except qc.QaqcError as exc:
        st.warning(_error_text(exc))
        return None
    _crm_intro(view)
    _crm_metrics(view)
    _crm_verdict(view)
    st.plotly_chart(crm_figure(view), width="stretch")
    st.caption(t("qc.crm.caption"))
    st.caption(t("qc.crm.rules"))
    return view


# ------------------------------------------------------------------ duplicados
def _dup_intro(p: QaqcParams, v: DupView) -> None:
    if v.es_gemas:
        st.markdown(t("qc.dup.intro.gemas", el=t("qc.dup.el." + str(v.elemento))))
    else:
        st.markdown(
            t("qc.dup.intro.table", n=int_num(len(v.pares)), tipo=opt(p.dup_tipo), p=es(v.p_pct, 0))
        )


def _dup_metrics(v: DupView) -> None:
    th, d = v.th, v.dup
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("qc.dup.m.pairs"), int_num(th.n))
    c2.metric(
        t("qc.dup.m.in90"),
        int_num(th.dentro90),
        t("qc.dup.m.cnt.delta", pct=es(th.pct90, 1), n=int_num(th.n)),
        delta_color="off",
    )
    c3.metric(
        t("qc.dup.m.in99"),
        int_num(th.dentro99),
        t("qc.dup.m.cnt.delta", pct=es(th.pct99, 1), n=int_num(th.n)),
        delta_color="off",
    )
    rule = t("qc.dup.rule.lt" if d.umbral.estricto else "qc.dup.rule.le")
    c4.metric(
        t("qc.dup.m.pct"),
        f"{es(d.pct_bajo, 1)} %",
        t("qc.dup.m.pct.delta", rule=rule, u=es(d.umbral.rpd_max, 0)),
        delta_color="off",
    )


def _dup_verdicts(p: QaqcParams, v: DupView) -> None:
    th, d = v.th, v.dup
    key = "pasa" if th.pasa else "falla"
    (st.success if th.pasa else st.warning)(
        t(f"qc.dup.v.th.{key}", p=es(v.p_pct, 0), pct90=es(th.pct90, 1), pct99=es(th.pct99, 1))
    )
    if th.sin_media:
        st.caption(t("qc.dup.th.sin", n=int_num(th.sin_media)))
    u = d.umbral
    key = "pasa" if d.pasa else "falla"
    (st.success if d.pasa else st.warning)(
        t(
            f"qc.dup.v.dup.{key}",
            tipo=opt(p.dup_tipo).lower(),
            pct=es(d.pct_bajo, 1),
            n=int_num(d.n_evaluables),
            u=es(u.rpd_max, 0),
            min=es(u.minimo_pct, 0),
            rule=t("qc.dup.rule.lt" if u.estricto else "qc.dup.rule.le"),
            hard=es(d.hard_medio, 1),
        )
    )


def dup_section(p: QaqcParams) -> DupView | None:
    st.markdown(t("qc.dup.h"))
    own = p.dup_fuente == DUP_FUENTES[-1]
    frame = pd.DataFrame(tabla_duplicados(), columns=["a", "b"])
    cols = {"a": _number_column("qc.col.a"), "b": _number_column("qc.col.b")}
    edited = _table_or_hint(own, KEY_DUP, frame, cols)
    rows = (
        None
        if edited is None
        else [[_cell(a), _cell(b)] for a, b in edited[["a", "b"]].values.tolist()]
    )
    try:
        view = run_dup(p, rows)
    except qc.QaqcError as exc:
        st.warning(_error_text(exc))
        return None
    _dup_intro(p, view)
    _dup_metrics(view)
    _dup_verdicts(p, view)
    st.plotly_chart(th_figure(view), width="stretch")
    st.plotly_chart(rpd_figure(view), width="stretch")
    st.caption(t("qc.dup.caption"))
    st.caption(t("qc.dup.rules"))
    return view


# ------------------------------------------------------------------ blancos
def blk_section(p: QaqcParams) -> BlkView | None:
    st.markdown(t("qc.blk.h"))
    own = p.blk_fuente != FUENTES[0]
    frame = pd.DataFrame({"res": tabla_blancos(p)})
    edited = _table_or_hint(own, KEY_BLK, frame, {"res": _number_column("qc.col.res")})
    try:
        view = run_blk(p, None if edited is None else _column(edited, "res"))
    except qc.QaqcError as exc:
        st.warning(_error_text(exc))
        return None
    r = view.res
    src = t("qc.src.synth" if view.sintetica else "qc.src.table")
    st.markdown(
        t(
            "qc.blk.intro",
            n=int_num(r.n),
            src=src,
            ld=es(r.ld, 4),
            l3=es(qc.K_ALERTA * r.ld, 4),
            l10=es(qc.K_FALLA * r.ld, 4),
        )
    )
    c1, c2, c3 = st.columns(3)
    c1.metric(t("qc.blk.m.n"), int_num(r.n))
    c2.metric(
        t("qc.blk.m.s3"),
        int_num(r.n_sobre_3),
        t("qc.blk.m.delta", pct=es(r.pct_sobre_3, 1)),
        delta_color="off",
    )
    c3.metric(
        t("qc.blk.m.s10"),
        int_num(r.n_sobre_10),
        t("qc.blk.m.delta", pct=es(r.pct_sobre_10, 1)),
        delta_color="off",
    )
    BLANK_CALL[r.veredicto](
        t(
            f"qc.blk.v.{_BLK_KEY[r.veredicto]}",
            s3=int_num(r.n_sobre_3),
            s10=int_num(r.n_sobre_10),
            pct3=es(r.pct_sobre_3, 1),
            pct10=es(r.pct_sobre_10, 1),
        )
    )
    st.plotly_chart(blk_figure(view), width="stretch")
    st.caption(t("qc.blk.rules"))
    return view


_BLK_KEY = {qc.BLANCO_OK: "pasa", qc.BLANCO_ALERTA: "alerta", qc.BLANCO_FALLA: "falla"}


# ------------------------------------------------------------------ certificar un estándar
def cert_section() -> CertView:
    v = run_cert()
    c, (pub_m, pub_2sd) = v.cert, v.publicado
    st.markdown(t("qc.cert.h"))
    st.markdown(t("qc.cert.intro", n=int_num(c.n_total)))
    c1, c2, c3 = st.columns(3)
    c1.metric(
        t("qc.cert.m.keep"),
        int_num(c.n),
        t("qc.cert.m.keep.delta", n=int_num(c.n_total)),
        delta_color="off",
    )
    c2.metric(
        t("qc.cert.m.mean"),
        f"{es(c.media, 3)} g/t",
        t("qc.cert.m.mean.delta", pub=es(pub_m, 3)),
        delta_color="off",
    )
    c3.metric(
        t("qc.cert.m.band"),
        f"{es(c.dos_sd, 3)} g/t",
        t("qc.cert.m.band.delta", pub=es(pub_2sd, 3)),
        delta_color="off",
    )
    fits = round(c.media, 3) == pub_m and round(c.dos_sd, 3) == pub_2sd
    st.markdown(
        t(
            "qc.cert.res",
            n=int_num(c.n_total),
            m0=es(c.media_total, 4),
            s0=es(c.sd_total, 4),
            lo=es(c.bajo, 3),
            hi=es(c.alto, 3),
            drop=int_num(c.n_total - c.n),
            keep=int_num(c.n),
            m=es(c.media, 3),
            band=es(c.dos_sd, 3),
            pub=es(pub_m, 3),
            pubband=es(pub_2sd, 3),
            fit=t("qc.cert.fit.yes" if fits else "qc.cert.fit.no"),
        )
    )
    st.plotly_chart(cert_figure(v), width="stretch")
    st.caption(t("qc.cert.note"))
    return v


def qaqc_tab(p: QaqcParams) -> None:
    ficha("qaqc")
    st.markdown(t("qc.intro"))
    crm_section(p)
    dup_section(p)
    blk_section(p)
    cert_section()


# ------------------------------------------------------------------ validación
def _check_table(checks: list[qv.QaqcCheck]) -> str:
    df = pd.DataFrame(
        {
            t("qv.col.concept"): [f"{t('qv.kind.' + x.kind)} {x.label}" for x in checks],
            t("qv.col.published"): [decimal(x.published) for x in checks],
            t("qv.col.calculated"): [decimal(round(x.calculated, x.decimals)) for x in checks],
            t("qv.col.tol"): [decimal(x.tol) for x in checks],
            t("qv.col.fits"): [t("v.yes") if x.ok else t("v.no") for x in checks],
        }
    )
    return markdown_table(df)


def qaqc_validation_section() -> None:
    """Sección «Control de calidad» de la pestaña Validación."""
    checks = qv.all_checks()
    s = qv.summary(checks)
    st.markdown(t("qv.h"))
    st.markdown(t("qv.intro"))
    st.markdown(
        t(
            "qv.summary",
            cdn=s["cdn"][0],
            ncdn=s["cdn"][1],
            oreas=s["oreas"][0],
            noreas=s["oreas"][1],
            gemas=s["gemas"][0],
            ngemas=s["gemas"][1],
            th=s["th"][0],
            nth=s["th"][1],
            rr=s["rr"][0],
            nrr=s["rr"][1],
            ll=s["ll"][0],
            nll=s["ll"][1],
        )
    )
    for src in qv.FUENTES:
        st.markdown(t("qv.h." + src))
        st.markdown(_check_table([x for x in checks if x.source == src]))
        if src == "oreas":
            rounded = qv.oreas_checks(redondeada=True)
            st.markdown(t("qv.oreas.round", ok=sum(x.ok for x in rounded), n=len(rounded)))
        if src == "rr":
            diff = max(abs(x.calculated - x.published) for x in qv.rr_checks())
            st.markdown(t("qv.rr.found", diff=es(diff, 2)))
    st.markdown(t("qv.not.h"))
    for n in range(1, 5):
        st.markdown(f"- {t(f'qv.not.{n}')}")
