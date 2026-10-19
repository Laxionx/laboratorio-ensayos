"""Gráficos de la pestaña «Ensayo de cianuración»: recuperación contra tiempo con la curva de cada
modelo, y los términos linealizados del núcleo sin reaccionar con las rectas por tramo (y su
extensión hasta t = 0, donde se ve que no pasan por el origen)."""

from __future__ import annotations

import math

import plotly.graph_objects as go
from cian_calculo import CianView, model_name
from dibujo import INK, es
from i18n import t
from nomograma import _layout
from plotly.subplots import make_subplots

from muestreo import cianuracion as c

COLORS = {
    "potencial": "#B7791F",
    "primer_orden": "#8E979C",
    "difusion": "#3B82A6",
    "reaccion": "#1F7A6F",
    "mixto": "#6B5B8C",
}
MEASURED, T1, T2 = "#C0462B", "#3B82A6", "#1F7A6F"
LINEAR_TITLES = {"difusion": "L", "reaccion": "M", "mixto": "N"}


def recovery_figure(view: CianView) -> go.Figure:
    """Puntos medidos (con X los que las rectas dejan fuera) y la curva de cada modelo. El del
    indicador del vaso va más grueso."""
    bal, grid = view.balance, view.grid()
    fig = go.Figure()
    for model in c.MODELOS:
        ys = view.curva(model)
        if not ys:
            continue
        chosen = model == view.params.model
        fig.add_trace(
            go.Scatter(
                x=grid.tolist(),
                y=ys,
                mode="lines",
                name=model_name(model),
                connectgaps=False,
                line=dict(color=COLORS[model], width=4.5 if chosen else 2, dash="solid"),
            )
        )
    for used, name, symbol in (
        (True, t("cn.plot.used"), "circle"),
        (False, t("cn.plot.excluded"), "x"),
    ):
        idx = [i for i, u in enumerate(view.usados) if u is used]
        if idx:
            fig.add_trace(
                go.Scatter(
                    x=[bal.t_h[i] for i in idx],
                    y=[bal.recuperacion_pct[i] for i in idx],
                    mode="markers",
                    name=name,
                    marker=dict(
                        color=MEASURED, size=11, symbol=symbol, line=dict(width=2, color=INK)
                    ),
                )
            )
    lo, hi = min(c.CURVA_T_MIN_H, bal.t_h[0]), view.tmax
    ymin = max(0.0, 10.0 * math.floor((min(bal.recuperacion_pct) - 10.0) / 10.0))
    return _layout(
        fig,
        t("cn.plot.rec.title"),
        430,
        x=dict(
            title=t("cn.plot.t"),
            type="log",
            range=[math.log10(lo * 0.8), math.log10(hi * 1.15)],
            tickvals=list(bal.t_h),
            ticktext=[es(x, 0 if float(x).is_integer() else 1) for x in bal.t_h],
        ),
        y=dict(title=t("cn.plot.rec.y"), range=[ymin, 100]),
    )


def _model_points(
    view: CianView, model: str, tramo: int
) -> tuple[list[float], list[float], list[bool]]:
    """(t, término, ¿usado?) de los puntos del tramo, con la B de ese tramo."""
    bal = view.balance
    b = c.B_N1 if tramo == 1 else c.B_N2
    y = c.terminos(bal.recuperacion_pct, b)[model]
    cut = view.params.split
    keep = [i for i, tt in enumerate(bal.t_h) if (tt <= cut if tramo == 1 else tt >= cut)]
    return [bal.t_h[i] for i in keep], [float(y[i]) for i in keep], [view.usados[i] for i in keep]


def terms_figure(view: CianView) -> go.Figure:
    """Un panel por término (L, M, N): puntos de cada tramo, su recta (sólida donde hay puntos,
    punteada hasta t = 0) y el origen. Una recta que explicara el mecanismo pasaría por él."""
    fig = make_subplots(
        rows=1,
        cols=3,
        shared_yaxes=True,
        horizontal_spacing=0.04,
        subplot_titles=[f"{LINEAR_TITLES[m]}: {model_name(m)}" for m in c.MODELOS_LINEALES],
    )
    top = 0.0
    for col, model in enumerate(c.MODELOS_LINEALES, start=1):
        aj = view.modelos.lineales[model] if view.modelos else None
        fig.add_trace(
            go.Scatter(
                x=[0.0],
                y=[0.0],
                mode="markers",
                name=t("cn.plot.origin"),
                legendgroup="origin",
                showlegend=col == 1,
                marker=dict(symbol="star", size=13, color=INK),
            ),
            row=1,
            col=col,
        )
        for tramo, color in ((1, T1), (2, T2)):
            ts, ys, used = _model_points(view, model, tramo)
            top = max([top, *ys])
            for flag, name, symbol in (
                (True, t("cn.plot.used"), "circle"),
                (False, t("cn.plot.excluded"), "x"),
            ):
                sel = [i for i, u in enumerate(used) if u is flag]
                if sel:
                    fig.add_trace(
                        go.Scatter(
                            x=[ts[i] for i in sel],
                            y=[ys[i] for i in sel],
                            mode="markers",
                            name=f"{name} ({t(f'cn.plot.tramo{tramo}')})",
                            showlegend=col == 1,
                            legendgroup=f"{flag}{tramo}",
                            marker=dict(
                                color=color, size=10, symbol=symbol, line=dict(width=1, color=INK)
                            ),
                        ),
                        row=1,
                        col=col,
                    )
            reg = None if aj is None else (aj.tramo1 if tramo == 1 else aj.tramo2)
            idx = () if aj is None else (aj.indices1 if tramo == 1 else aj.indices2)
            if reg is None or not idx:
                continue
            t0, t1 = view.balance.t_h[idx[0]], view.balance.t_h[idx[-1]]
            top = max(top, reg.en(t1))
            for xs, dash, show in (([0.0, t0], "dot", False), ([t0, t1], "solid", True)):
                fig.add_trace(
                    go.Scatter(
                        x=xs,
                        y=[reg.en(x) for x in xs],
                        mode="lines",
                        showlegend=show and col == 1,
                        name=f"{t('cn.plot.line')} ({t(f'cn.plot.tramo{tramo}')})",
                        legendgroup=f"line{tramo}",
                        line=dict(color=color, width=2.5, dash=dash),
                    ),
                    row=1,
                    col=col,
                )
            fig.add_annotation(
                xref="x domain",
                yref="y domain",
                x=0.97,
                y=0.30 - 0.08 * (tramo - 1),
                text=t("cn.plot.intercept", a=es(reg.intercepto, 3)),
                showarrow=False,
                xanchor="right",
                font=dict(color=color, size=12),
                row=1,
                col=col,
            )
    for ann in fig.layout.annotations[:3]:  # los títulos de los paneles
        ann.update(font=dict(size=13, color=INK))
    _layout(
        fig,
        t("cn.plot.terms.title"),
        460,
        x=dict(title=t("cn.plot.t"), range=[-1, view.tmax * 1.03]),
        y=dict(range=[-0.03, top * 1.12]),
        bottom=110,
    )
    fig.update_yaxes(title=t("cn.plot.terms.y"), row=1, col=1)
    fig.update_layout(legend=dict(orientation="h", y=-0.3, x=0.0, bgcolor="rgba(0,0,0,0)"))
    return fig
