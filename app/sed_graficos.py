"""Gráficos de la pestaña «Ensayo de sedimentación»: la curva h(t) con la construcción de
Talmage-Fitch dibujada (línea del underflow, tangente en el punto de compresión, tu) y la curva de
flujo de Kynch con la construcción del flujo límite."""

from __future__ import annotations

import plotly.graph_objects as go
from dibujo import INK, es
from i18n import t
from nomograma import _layout
from sed_calculo import FUENTES, SedView

CURVE, TANGENT, UNDER, ASYMP, KYN = "#3B82A6", "#C0462B", "#6B5B8C", "#8E979C", "#B7791F"
X_SPAN = 2.5  # el eje horizontal llega a 2,5·tu


def x_max(view: SedView) -> float:
    return min(view.curva.t_max, max(X_SPAN * view.tf.tu_s, 3.0 * view.tf.tc_s))


def curve_figure(view: SedView) -> go.Figure:
    """h(t) y su construcción: la línea de Hu, la tangente en C, tc y tu."""
    c, tf = view.curva, view.tf
    xm = x_max(view)
    pts = [(a, b) for a, b in zip(c.t_s, c.h_m, strict=True) if a <= xm * 1.02]
    fig = go.Figure()
    from_table = view.params.fuente != FUENTES[0]
    fig.add_trace(
        go.Scatter(
            x=[a for a, _ in pts],
            y=[b for _, b in pts],
            mode="lines+markers" if from_table else "lines",
            name=t("sd.plot.curve"),
            line=dict(color=CURVE, width=3),
            marker=dict(size=8, color=CURVE),
        )
    )
    for y, name, color, dash in (
        (tf.hu_m, t("sd.plot.hu" if tf.modo == "clasico" else "sd.plot.hu24"), UNDER, "solid"),
        (view.h_inf, t("sd.plot.hinf"), ASYMP, "dash"),
    ):
        fig.add_trace(
            go.Scatter(
                x=[0, xm],
                y=[y, y],
                mode="lines",
                name=name,
                line=dict(color=color, width=2, dash=dash),
            )
        )
    t_a = max(0.0, tf.tc_s - 0.6 * (tf.tu_s - tf.tc_s))
    t_b = tf.tu_s + 0.25 * (tf.tu_s - tf.tc_s)
    fig.add_trace(
        go.Scatter(
            x=[t_a, t_b],
            y=[tf.tangente(t_a), tf.tangente(t_b)],
            mode="lines",
            name=t("sd.plot.tangent"),
            line=dict(color=TANGENT, width=2.5, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[tf.tc_s, tf.tu_s],
            y=[tf.hc_m, tf.hu_m],
            mode="markers+text",
            text=[t("sd.plot.c"), t("sd.plot.u")],
            textposition="top right",
            name=t("sd.plot.points"),
            marker=dict(size=12, color=TANGENT, line=dict(width=2, color=INK)),
        )
    )
    for x, lab in ((tf.tc_s, "tc"), (tf.tu_s, "tu")):
        fig.add_trace(
            go.Scatter(
                x=[x, x],
                y=[0, tf.tangente(x)],
                mode="lines+text",
                text=["", f"{lab} = {es(x, 0)} s"],
                textposition="bottom right",
                showlegend=False,
                line=dict(color=TANGENT, width=1, dash="dot"),
            )
        )
    return _layout(
        fig,
        t("sd.plot.title"),
        430,
        x=dict(title=t("sd.plot.t"), range=[0, xm]),
        y=dict(title=t("sd.plot.h"), range=[0, view.curva.h0 * 1.05]),
    )


def kynch_figure(view: SedView) -> go.Figure | None:
    """El flujo de sólidos G = v·C contra C (Kynch) y, si hay, la tangente desde (Cu, 0): su
    ordenada al origen es el flujo límite."""
    k = view.kynch
    if k is None or not k.c_t_m3:
        return None
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(k.c_t_m3),
            y=list(k.g_t_m2_h),
            mode="markers",
            name=t("sd.plot.flux"),
            marker=dict(size=6, color=KYN),
        )
    )
    if view.g_limite is not None:
        gl, cc = view.g_limite
        gc = gl * (1.0 - cc / view.cu)  # G en el punto crítico
        fig.add_trace(
            go.Scatter(
                x=[0.0, view.cu],
                y=[gl, 0.0],
                mode="lines",
                name=t("sd.plot.limit"),
                line=dict(color=TANGENT, width=2.5, dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[cc],
                y=[gc],
                mode="markers",
                name=t("sd.plot.crit"),
                marker=dict(size=12, color=TANGENT, line=dict(width=2, color=INK)),
            )
        )
    return _layout(
        fig,
        t("sd.plot.kynch.title"),
        400,
        x=dict(title=t("sd.plot.c.axis"), range=[0, view.cu * 1.05]),
        y=dict(title=t("sd.plot.g.axis"), rangemode="tozero"),
    )
