"""Gráficos de la pestaña «Copelación»: las tablas de Bugbee (puntos) con el modelo encima (línea),
el punto de operación del visitante y, donde existe, la comparación con Godshall."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from cop_calculo import CopView
from dibujo import INK
from i18n import t
from nomograma import _layout

from muestreo import copelacion as cp
from muestreo import copelacion_datos as cd
from muestreo import copelacion_validacion as cv

AG, AU, LEAD, GOD, OP = "#6B7C8A", "#B7791F", "#3B82A6", "#1F7A6F", "#C0462B"
N_CURVE = 120


def _marker(color: str, symbol: str = "circle", size: int = 9) -> dict:
    return dict(size=size, color=color, symbol=symbol, line=dict(width=1.5, color=INK))


def _band(frac: float, bajo: float, alto: float) -> dict:
    """`error_y` asimétrico (en %) con la banda de reproducibilidad."""
    return dict(type="data", symmetric=False, array=[100 * (alto - frac)],
                arrayminus=[100 * (frac - bajo)], color=OP, thickness=2)  # fmt: skip


def temperature_figure(view: CopView) -> go.Figure:
    """Pérdida contra temperatura: Tablas IX (plata) y XII (oro), el modelo y el punto calculado."""
    r = view.res
    ts = np.linspace(cp.T_AG_RANGO[0], max(cp.T_AU_RANGO[1], r.temp_c), N_CURVE)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[x[2] for x in cd.TABLA_IX], y=[x[3] for x in cd.TABLA_IX],
                             mode="markers", name=t("cp.plot.ix"), marker=_marker(AG)))  # fmt: skip
    fig.add_trace(go.Scatter(
        x=ts, y=[cp.perdida_plata(x, 10.0, 200.0).pct for x in ts], mode="lines",
        name=t("cp.plot.model.ag"), line=dict(color=AG, width=2.5, dash="dash"),
    ))  # fmt: skip
    xii = [x for x in cd.TABLA_XII if x[3] is not None]
    fig.add_trace(go.Scatter(x=[x[2] for x in xii], y=[x[3] for x in xii], mode="markers",
                             name=t("cp.plot.xii"), marker=_marker(AU, "diamond")))  # fmt: skip
    fig.add_trace(go.Scatter(
        x=ts, y=[cp.perdida_oro(x).pct for x in ts], mode="lines",
        name=t("cp.plot.model.au"), line=dict(color=AU, width=2.5, dash="dash"),
    ))  # fmt: skip
    fig.add_vrect(
        x0=cd.CONGELADO_C - 25, x1=cd.CONGELADO_C, fillcolor="#8E979C", opacity=0.18,
        line_width=0, annotation_text=t("cp.plot.frozen"), annotation_position="top left",
    )  # fmt: skip
    fig.add_trace(go.Scatter(
        x=[r.temp_c], y=[r.perdida_ag.pct], mode="markers", name=t("cp.plot.you.ag"),
        marker=_marker(OP, "star", 15), error_y=_band(r.perdida_ag.frac, r.perdida_ag.bajo,
                                                      r.perdida_ag.alto),
    ))  # fmt: skip
    fig.add_trace(go.Scatter(
        x=[r.temp_c], y=[r.perdida_au.pct], mode="markers", name=t("cp.plot.you.au"),
        marker=_marker(OP, "star-diamond", 15),
    ))  # fmt: skip
    return _layout(fig, t("cp.plot.temp.title"), 400,
                   x=dict(title=t("cp.plot.temp.x")),
                   y=dict(title=t("cp.plot.loss.y"), rangemode="tozero"))  # fmt: skip


def lead_figure(view: CopView) -> go.Figure:
    """Pérdida de plata contra el plomo: Tabla X (685 °C, 200 mg), el modelo y Godshall (200 mg)."""
    pbs = np.linspace(5.0, 35.0, N_CURVE)
    base = cd.TABLA_X[0][3]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[x[1] for x in cd.TABLA_X], y=[x[3] for x in cd.TABLA_X], mode="markers",
        name=t("cp.plot.x"), marker=_marker(LEAD),
    ))  # fmt: skip
    fig.add_trace(go.Scatter(
        x=pbs, y=[base * cp.factor_plomo(x)[0] for x in pbs], mode="lines",
        name=t("cp.plot.model.pb"), line=dict(color=LEAD, width=2.5, dash="dash"),
    ))  # fmt: skip
    fig.add_trace(go.Scatter(
        x=[cv.plomo_g(a) for a in cd.GODSHALL_PLOMO_AT], y=list(cd.GODSHALL_FINAL[-1]),
        mode="markers", name=t("cp.plot.god200"), marker=_marker(GOD, "square"),
    ))  # fmt: skip
    fig.add_vrect(x0=cp.PB_RANGO[1], x1=35.0, fillcolor="#8E979C", opacity=0.12, line_width=0)
    fig.add_vrect(x0=5.0, x1=cp.PB_RANGO[0], fillcolor="#8E979C", opacity=0.12, line_width=0,
                  annotation_text=t("cp.plot.clamped"), annotation_position="top left")  # fmt: skip
    return _layout(fig, t("cp.plot.pb.title"), 400,
                   x=dict(title=t("cp.plot.pb.x"), range=[5, 35]),
                   y=dict(title=t("cp.plot.loss.y"), rangemode="tozero"))  # fmt: skip


def silver_figure(view: CopView) -> go.Figure:
    """Pérdida relativa a la de 200 mg contra la plata: Tabla XI, las otras dos series de Godshall
    (réplica) y el modelo."""
    ags = np.logspace(np.log10(1.0), np.log10(1000.0), N_CURVE)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[a for a, _ in cd.TABLA_XI], y=[p / cd.TABLA_XI[0][1] for _, p in cd.TABLA_XI],
        mode="markers", name=t("cp.plot.xi"), marker=_marker(GOD),
    ))  # fmt: skip
    for name, serie, symbol in (("primera", cd.GODSHALL_PRIMERA, "triangle-up"),
                                ("tercera", cd.GODSHALL_TERCERA, "triangle-down")):  # fmt: skip
        fig.add_trace(go.Scatter(
            x=list(cd.GODSHALL_PLATA_MG), y=[f[1] / serie[-1][1] for f in serie], mode="markers",
            name=t(f"cp.plot.rep.{name}"), marker=_marker("#8E979C", symbol, 8),
        ))  # fmt: skip
    fig.add_trace(go.Scatter(
        x=ags, y=[cp.factor_plata(a)[0] for a in ags], mode="lines",
        name=t("cp.plot.model.ag.rel"), line=dict(color=GOD, width=2.5, dash="dash"),
    ))  # fmt: skip
    r = view.res
    fig.add_trace(go.Scatter(
        x=[max(r.plata_total_mg, 1.0)], y=[cp.factor_plata(max(r.plata_total_mg, 1e-9))[0]],
        mode="markers", name=t("cp.plot.you.rel"), marker=_marker(OP, "star", 15),
    ))  # fmt: skip
    return _layout(fig, t("cp.plot.ag.title"), 400,
                   x=dict(title=t("cp.plot.ag.x"), type="log"),
                   y=dict(title=t("cp.plot.rel.y"), rangemode="tozero"))  # fmt: skip
