"""Gráficos de la pestaña Validación: publicado frente a calculado."""

from __future__ import annotations

import plotly.graph_objects as go
from dibujo import INK, es
from nomograma import _layout

from muestreo import oro
from muestreo.validacion import (
    CLIFTON_PUBLISHED,
    MINNITT_2007_PRINTED,
    Check,
)

OK, BAD, LINE = "#1F7A6F", "#C0462B", "#8E979C"


def variance_figure(checks: list[Check]) -> go.Figure:
    """Varianza publicada (horizontal) contra calculada (vertical), en escala log; la diagonal es
    la coincidencia exacta. En rojo, lo que no cuadra al redondeo publicado."""
    rows = [c for c in checks if c.unit == "varianza relativa" and c.published > 0]
    fig = go.Figure()
    lo, hi = min(c.published for c in rows) / 3, max(c.published for c in rows) * 3
    fig.add_trace(
        go.Scatter(
            x=[lo, hi],
            y=[lo, hi],
            mode="lines",
            name="coincidencia exacta",
            line=dict(color=LINE, dash="dash"),
        )
    )
    for ok, name, color in ((True, "cuadra al redondeo publicado", OK), (False, "no cuadra", BAD)):
        part = [c for c in rows if c.ok is ok]
        if part:
            fig.add_trace(
                go.Scatter(
                    x=[c.published for c in part],
                    y=[c.calculated for c in part],
                    mode="markers",
                    name=name,
                    marker=dict(size=10, color=color),
                    text=[f"{c.source}: {c.item}" for c in part],
                    hovertemplate="%{text}<br>publicado %{x}<br>calculado %{y:.5f}<extra></extra>",
                )
            )
    return _layout(
        fig,
        "Varianza publicada frente a calculada (Minnitt 2017 y Chieregati 2017)",
        440,
        x=dict(title="Publicada", type="log"),
        y=dict(title="Calculada", type="log"),
    )


def clifton_figure() -> go.Figure:
    """Límites al 95 % de Clifton (Fig. 4) frente a sus ecuaciones y al Poisson exacto."""
    ns = list(CLIFTON_PUBLISHED)
    fig = go.Figure()
    series = (
        ("publicado (Fig. 4)", [CLIFTON_PUBLISHED[n] for n in ns], "diamond", INK, None),
        (
            "ecuaciones (11) y (12)",
            [tuple(100 * v for v in oro.clifton_limits(n)) for n in ns],
            "circle",
            OK,
            None,
        ),
        (
            "Poisson exacto (Garwood)",
            [tuple(100 * v for v in oro.poisson_exact_limits(n)) for n in ns],
            "x",
            BAD,
            None,
        ),
    )
    for name, values, symbol, color, _ in series:
        for side, label in ((0, "inferior"), (1, "superior")):
            fig.add_trace(
                go.Scatter(
                    x=ns,
                    y=[v[side] for v in values],
                    mode="markers",
                    name=f"{name}, {label}",
                    marker=dict(size=10, symbol=symbol, color=color, opacity=0.9 if side else 0.55),
                    legendgroup=name,
                    showlegend=side == 0,
                )
            )
    return _layout(
        fig,
        "Límites al 95 % según las partículas por muestra (Clifton 1969)",
        420,
        x=dict(title="Partículas por muestra", type="log"),
        y=dict(title="Error relativo (%)"),
    )


def minnitt_2007_figure(printed_calc_pct: float, implied_pct: float) -> go.Figure:
    """El problema 1 de Minnitt 2007: publicado, con los datos impresos y con c·f·g·ℓ = 448."""
    published = MINNITT_2007_PRINTED["sigma_pct"]
    fig = go.Figure(
        go.Bar(
            x=["publicado", "datos impresos (c·f·g·ℓ = 70)", "implícito (c·f·g·ℓ = 448)"],
            y=[published, printed_calc_pct, implied_pct],
            marker=dict(color=[INK, BAD, OK]),
            text=[es(v, 2) for v in (published, printed_calc_pct, implied_pct)],
            textposition="outside",
        )
    )
    return _layout(
        fig,
        "Minnitt 2007, problema 1: error relativo (%)",
        360,
        x=dict(title=""),
        y=dict(title="%"),
    )
