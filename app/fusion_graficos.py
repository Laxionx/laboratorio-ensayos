"""Gráfico de la pestaña Fusión: balance del plomo (qué reduce u oxida cada parte de la carga)."""

from __future__ import annotations

import plotly.graph_objects as go
from calculo import FusionView
from dibujo import es
from i18n import t
from nomograma import _layout

from muestreo.fusion_avisos import BUTTON_RANGE

COLORS = {"muestra": "#B7791F", "harina": "#1F7A6F", "nitro": "#C0462B", "botón": "#4F5F69"}


def balance_rows(view: FusionView) -> list[tuple[str, float]]:
    """(parte, g de Pb): lo que reduce (+) u oxida (−) la muestra, la harina y el nitro, y el
    botón que resulta."""
    r = view.result
    return [
        ("muestra", r.ore_pb_g),
        ("harina", r.flour_pb_g),
        ("nitro", r.niter_pb_g),
        ("botón", r.button_g),
    ]


def balance_figure(view: FusionView) -> go.Figure:
    rows = balance_rows(view)
    fig = go.Figure(
        go.Bar(
            x=[t("bal." + n) for n, _ in rows],
            y=[v for _, v in rows],
            marker=dict(color=[COLORS[n] for n, _ in rows]),
            text=[es(v, 1) for _, v in rows],
            textposition="outside",
        )
    )
    lo, hi = BUTTON_RANGE
    fig.add_hrect(
        y0=lo,
        y1=hi,
        fillcolor="#1F7A6F",
        opacity=0.12,
        line_width=0,
        annotation_text=t("bal.band"),
        annotation_position="top left",
    )
    return _layout(
        fig,
        t("bal.title"),
        380,
        x=dict(title=""),
        y=dict(title=t("bal.y")),
    )
