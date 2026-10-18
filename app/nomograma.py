"""Gráficos del protocolo con Plotly: nomograma de muestreo animado etapa por etapa, error por
etapa y acumulado, sensibilidad a la pendiente m y curvas granulométricas de las etapas.

Nada arranca solo: «Reproducir» recorre la ruta en el navegador. Cada cuadro lleva todos los
trazos (Plotly solo anima los que existen en la figura inicial)."""

from __future__ import annotations

import math

import numpy as np
import plotly.graph_objects as go
from calculo import ProtocolView
from dibujo import INK, PAPER, STEEL, es
from i18n import t, tm

from muestreo.granulometria import curve

FONT = dict(family="Segoe UI, Helvetica, Arial, sans-serif", color=INK, size=13)
ERROR_LEVELS = (1.0, 3.0, 10.0, 30.0, 100.0)  # % de error relativo de las rectas de Gy
COLORS = {"split": "#C0462B", "crush": "#3B82A6", "line": "#B7B0A0", "safety": "#1F7A6F"}
GRID_POINTS = 60


def _layout(
    fig: go.Figure, title: str, height: int, x: dict, y: dict, bottom: int = 50
) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(family="Georgia, serif", size=17)),
        paper_bgcolor=PAPER,
        plot_bgcolor="#FBF9F4",
        font=FONT,
        height=height,
        margin=dict(l=70, r=20, t=60, b=bottom),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="#E4DED2", linecolor=STEEL, **x)
    fig.update_yaxes(gridcolor="#E4DED2", linecolor=STEEL, **y)
    return fig


def _player(fig: go.Figure, names: list[str], ms: int) -> go.Figure:
    """Botones y deslizador, en el idioma de la app. Arranca mostrando el estado final;
    «Reproducir» lo recorre desde el principio. Nada arranca solo."""
    play = dict(
        frame=dict(duration=ms, redraw=True),
        fromcurrent=False,
        mode="immediate",
        transition=dict(duration=0),
    )
    pause = dict(frame=dict(duration=0, redraw=False), mode="immediate")
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.0,
                y=-0.2,
                xanchor="left",
                yanchor="top",
                buttons=[
                    dict(label=t("plot.play"), method="animate", args=[None, play]),
                    dict(label=t("plot.pause"), method="animate", args=[[None], pause]),
                ],
            )
        ],
        sliders=[
            dict(
                x=0.22,
                y=-0.17,
                len=0.78,
                active=len(names) - 1,
                currentvalue=dict(visible=False),
                steps=[
                    dict(
                        label=n,
                        method="animate",
                        args=[[n], dict(mode="immediate", frame=dict(duration=0, redraw=True))],
                    )
                    for n in names
                ],
            )
        ],
    )
    return fig


def size_grid(view: ProtocolView) -> np.ndarray:
    """dN (cm) del eje horizontal: del décimo del menor de la ruta a diez veces el mayor."""
    sizes = [d for _, d, _ in view.path]
    return np.geomspace(min(sizes) / 10.0, max(sizes) * 10.0, GRID_POINTS)


def gy_line(view: ProtocolView, error_pct: float) -> tuple[list[float], list[float]]:
    """Masa (g) contra dN (cm) a error constante: M = IHL(dN)/σ²; recta de Gy de ese error."""
    grid = size_grid(view)
    variance = (error_pct / 100.0) ** 2
    return grid.tolist(), [view.mineral.ih_l(float(d)) / variance for d in grid]


def path_prefix(view: ProtocolView, k: int) -> tuple[list[float], list[float]]:
    """Los primeros k+1 puntos de la ruta: (dN, masa)."""
    points = view.path[: k + 1]
    return [d for _, d, _ in points], [m for _, _, m in points]


def _note(text: str) -> dict:
    return dict(
        annotations=[
            dict(
                text=text,
                x=0.99,
                y=0.97,
                xref="paper",
                yref="paper",
                showarrow=False,
                xanchor="right",
                yanchor="top",
                font=dict(family="Georgia, serif", size=14, color=INK),
                bgcolor="rgba(251,249,244,.9)",
            )
        ]
    )


def nomogram_figure(view: ProtocolView) -> go.Figure:
    """Nomograma de Gy (log masa contra log dN) con la ruta del protocolo animada: reducir el
    tamaño es un tramo horizontal y dividir es un tramo vertical."""
    points = view.path
    names = [str(i) for i in range(len(points))]
    levels = sorted({*ERROR_LEVELS, view.params.safety_pct})

    def traces(k: int) -> list[go.Scatter]:
        out = []
        for level in levels:
            xs, ys = gy_line(view, level)
            safe = level == view.params.safety_pct
            out.append(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    name=t("plot.nomo.error", level=es(level, 0))
                    + (t("plot.nomo.safety") if safe else ""),
                    line=dict(
                        color=COLORS["safety"] if safe else COLORS["line"],
                        width=3.5 if safe else 1.2,
                        dash="solid" if safe else "dot",
                    ),
                    hovertemplate=t("plot.nomo.hover"),
                )
            )
        xs, ys = path_prefix(view, k)
        out.append(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines+markers",
                name=t("plot.nomo.route"),
                line=dict(color=INK, width=3),
                marker=dict(size=8, color=INK),
            )
        )
        last = (xs[-1:], ys[-1:])
        is_split = k > 0 and k % 2 == 0
        out.append(
            go.Scatter(
                x=last[0],
                y=last[1],
                mode="markers",
                name=t("plot.nomo.current"),
                showlegend=False,
                marker=dict(
                    size=15,
                    symbol="diamond",
                    color=COLORS["split"] if is_split else COLORS["crush"],
                    line=dict(color=PAPER, width=2),
                ),
            )
        )
        return out

    def note(k: int) -> dict:
        label, d, m = points[k]
        return _note(
            t(
                "plot.nomo.note",
                k=k + 1,
                n=len(points),
                label=tm(label),
                d=es(d, 4 if d < 0.1 else 2),
                m=es(m, 0),
            )
        )

    frames = [go.Frame(data=traces(k), name=names[k], layout=note(k)) for k in range(len(points))]
    fig = go.Figure(data=traces(len(points) - 1), frames=frames, layout=note(len(points) - 1))
    grid = size_grid(view)
    masses = [m for _, _, m in points]
    _layout(
        fig,
        t("plot.nomo.title"),
        520,
        x=dict(
            title=t("plot.nomo.x"),
            type="log",
            range=[math.log10(grid[0]), math.log10(grid[-1])],
        ),
        y=dict(
            title=t("plot.nomo.y"),
            type="log",
            range=[math.log10(min(masses) / 5.0), math.log10(max(masses) * 5.0)],
        ),
        bottom=130,
    )
    return _player(fig, names, ms=900)


def stage_figure(view: ProtocolView) -> go.Figure:
    """Error relativo de cada división (barras) y el acumulado (línea), en %."""
    stages = view.result.stages
    names = [tm(s.name) for s in stages]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=names,
            y=[100 * s.rsd for s in stages],
            name=t("plot.stage.err"),
            marker=dict(color=COLORS["split"]),
            text=[es(100 * s.rsd, 1) for s in stages],
            textposition="outside",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=names,
            y=[100 * s.cum_rsd for s in stages],
            mode="lines+markers",
            name=t("plot.stage.cum"),
            line=dict(color=INK, width=3),
        )
    )
    fig.add_hline(
        y=view.params.safety_pct,
        line=dict(color=COLORS["safety"], dash="dash"),
        annotation_text=t("plot.stage.safety", pct=es(view.params.safety_pct, 0)),
    )
    return _layout(
        fig,
        t("plot.stage.title"),
        380,
        x=dict(title=""),
        y=dict(title=t("plot.stage.y")),
    )


def sensitivity_figure(view: ProtocolView) -> go.Figure:
    """Error total del protocolo contra la pendiente m (dN pesa al cubo)."""
    ms = [m for m, _, _ in view.sensitivity]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ms,
            y=[100 * e for _, e, _ in view.sensitivity],
            mode="lines+markers",
            name=t("plot.sens.total"),
            line=dict(color=COLORS["split"], width=3),
        )
    )
    current = view.result.rsd * 100
    fig.add_trace(
        go.Scatter(
            x=[view.params.m],
            y=[current],
            mode="markers",
            name=t("plot.sens.chosen"),
            marker=dict(size=14, symbol="diamond", color=INK),
        )
    )
    return _layout(
        fig,
        t("plot.sens.title"),
        380,
        x=dict(title=t("plot.sens.x")),
        y=dict(title=t("plot.sens.y"), type="log"),
    )


def granulometry_figure(view: ProtocolView) -> go.Figure | None:
    """Curvas Rosin-Rammler de las etapas definidas por especificación, con su d95."""
    protocol = view.result.protocol
    fig = go.Figure()
    for stage, result in zip(protocol.stages, view.result.stages, strict=True):
        if stage.spec is None:
            continue
        sieves, passing = curve(stage.spec.pct, stage.spec.size_um, view.params.m)
        fig.add_trace(go.Scatter(x=sieves, y=passing, mode="lines", name=tm(stage.name)))
        fig.add_trace(
            go.Scatter(
                x=[result.d_n_cm * 1e4],
                y=[95.0],
                mode="markers",
                name=t("plot.gran.d95", mm=es(result.d_n_cm * 10, 3)),
                marker=dict(size=11, symbol="diamond"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[stage.spec.size_um],
                y=[stage.spec.pct],
                mode="markers",
                name=t("plot.gran.spec"),
                marker=dict(size=9, color=INK),
                showlegend=False,
            )
        )
    if not fig.data:
        return None
    return _layout(
        fig,
        t("plot.gran.title"),
        380,
        x=dict(title=t("plot.gran.x"), type="log"),
        y=dict(title=t("plot.gran.y"), range=[0, 102]),
    )
