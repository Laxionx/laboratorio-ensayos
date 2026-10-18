"""Oro grueso: histograma animado de los 1 000 ensayos simulados (Plotly) y esquema SVG de la
alícuota con sus granos de oro. Los números de granos son los de la simulación; sus posiciones
dentro de la alícuota son ilustrativas y así se rotulan."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from calculo import GoldView
from dibujo import BRONZE_SVG, INK, STEEL, es, scheme_note, svg, text
from i18n import t
from nomograma import _layout, _note, _player
from scipy.stats import poisson

from muestreo.oro import SEED, poisson_median_particles, poisson_p0

MAX_UNIT_BINS = 60  # hasta esta cantidad de granos distintos, una barra por número de granos
BINS = 40
FRAME_SIZES = (10, 20, 30, 50, 75, 100, 150, 200, 300, 400, 550, 700, 850, 1000)
TRUE_COLOR, MEDIAN_COLOR, BAR_COLOR = "#1F7A6F", "#C0462B", "#B7791F"


def bin_edges(view: GoldView) -> tuple[np.ndarray, bool]:
    """Bordes de las barras en número de granos. Si hay pocos valores distintos, una barra por
    número entero de granos; si no, BINS barras iguales."""
    top = int(view.simulation.counts.max())
    if top < MAX_UNIT_BINS:
        return np.arange(-0.5, top + 1.5), True
    return np.linspace(-0.5, top + 0.5, BINS + 1), False


def histogram(view: GoldView, n: int) -> tuple[np.ndarray, np.ndarray]:
    """(ley al centro de cada barra en g/t, número de ensayos) con los primeros `n` ensayos."""
    edges, _ = bin_edges(view)
    heights, _ = np.histogram(view.simulation.counts[:n], bins=edges)
    centers = (edges[:-1] + edges[1:]) / 2.0
    per_grain = view.grain_g / view.aliquot_g * 1e6  # g/t que da un grano en la alícuota
    return centers * per_grain, heights


def frame_sizes(trials: int) -> list[int]:
    sizes = [n for n in FRAME_SIZES if n < trials]
    return [*sizes, trials]


def histogram_figure(view: GoldView) -> go.Figure:
    """Histograma de la ley que daría cada ensayo, acumulándose de 10 a 1 000 ensayos, con la ley
    real marcada y la mediana de lo simulado hasta ese cuadro."""
    sim, per_grain = view.simulation, view.grain_g / view.aliquot_g * 1e6
    sizes = frame_sizes(len(sim.counts))
    names = [str(n) for n in sizes]
    _, unit = bin_edges(view)
    top = float(max(np.histogram(sim.counts, bins=bin_edges(view)[0])[0])) * 1.12

    def traces(n: int) -> list[go.Scatter]:
        x, y = histogram(view, n)
        grades = sim.grades_gpt[:n]
        width = (x[1] - x[0]) * 0.9 if len(x) > 1 else per_grain * 0.9
        out = [
            go.Bar(
                x=x,
                y=y,
                width=width,
                name=t("plot.hist.sim"),
                marker=dict(color=BAR_COLOR),
                hovertemplate=t("plot.hist.hover"),
            )
        ]
        out.append(
            go.Scatter(
                x=[view.grade_gpt] * 2,
                y=[0, top],
                mode="lines",
                name=t("plot.hist.true", grade=es(view.grade_gpt, 2)),
                line=dict(color=TRUE_COLOR, width=3),
            )
        )
        median = float(np.median(grades))
        out.append(
            go.Scatter(
                x=[median] * 2,
                y=[0, top],
                mode="lines",
                name=t("plot.hist.median", median=es(median, 2)),
                line=dict(color=MEDIAN_COLOR, width=3, dash="dash"),
            )
        )
        if unit:  # Poisson analítico, solo con una barra por número de granos
            ks = np.arange(len(x))
            out.append(
                go.Scatter(
                    x=ks * per_grain,
                    y=n * poisson.pmf(ks, view.lam),
                    mode="markers",
                    name=t("plot.hist.poisson"),
                    marker=dict(size=7, color=INK),
                )
            )
        return out

    def note(n: int) -> dict:
        grades = sim.grades_gpt[:n]
        return _note(
            t(
                "plot.hist.note",
                n=n,
                median=es(float(np.median(grades)), 2),
                max=es(float(grades.max()), 1),
            )
        )

    frames = [go.Frame(data=traces(n), name=str(n), layout=note(n)) for n in sizes]
    fig = go.Figure(data=traces(sizes[-1]), frames=frames, layout=note(sizes[-1]))
    _layout(
        fig,
        t("plot.hist.title"),
        460,
        x=dict(title=t("plot.hist.x")),
        y=dict(title=t("plot.hist.y")),
        bottom=130,
    )
    return _player(fig, names, ms=500)


# ------------------------------------------------------------------ esquema de la alícuota
W, H = 940, 340
CRUCIBLE = (220.0, 150.0)  # ancho y alto de cada crisol dibujado
MAX_DOTS = 120  # granos que se dibujan como máximo por crisol


def representative_runs(view: GoldView) -> list[tuple[str, int]]:
    """(rótulo, granos) de tres ensayos de la simulación: percentil 10, mediana y percentil 99."""
    counts = view.simulation.counts
    return [
        (t("svg.gold.low"), int(np.percentile(counts, 10, method="lower"))),
        (t("svg.gold.median"), int(np.median(counts))),
        (t("svg.gold.high"), int(np.percentile(counts, 99, method="higher"))),
    ]


def _dots(count: int, x0: float, y0: float, seed: int) -> str:
    rng = np.random.default_rng(seed)
    shown = min(count, MAX_DOTS)
    out = []
    for _ in range(shown):
        x = x0 + 10 + rng.random() * (CRUCIBLE[0] - 20)
        y = y0 + 40 + rng.random() * (CRUCIBLE[1] - 55)
        out.append(f'<circle class="grain" cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{BRONZE_SVG}"/>')
    return "".join(out)


def aliquot_svg(view: GoldView) -> str:
    """Tres alícuotas con sus granos de oro: la cantidad es la de un ensayo simulado (percentil 10,
    mediana y percentil 99); las posiciones son ilustrativas."""
    per_grain = view.grain_g / view.aliquot_g * 1e6
    body = text(
        24,
        30,
        t("svg.gold.title", mass=es(view.aliquot_g, 0)),
        17,
        cls="t",
    )
    for i, (label, count) in enumerate(representative_runs(view)):
        x0, y0 = 40.0 + i * 300.0, 70.0
        body += (
            f'<rect x="{x0}" y="{y0}" width="{CRUCIBLE[0]}" height="{CRUCIBLE[1]}" rx="14" '
            f'fill="#EFE9DD" stroke="{STEEL}" stroke-width="3"/>'
            + _dots(count, x0, y0, SEED + i)
            + text(x0, y0 - 10, label, 13, color=STEEL)
            + text(
                x0,
                y0 + CRUCIBLE[1] + 26,
                t("svg.gold.grain1" if count == 1 else "svg.gold.grains", n=count),
                15,
                cls="t",
            )
            + text(
                x0,
                y0 + CRUCIBLE[1] + 46,
                t("svg.gold.grade", grade=es(count * per_grain, 2), real=es(view.grade_gpt, 2)),
                13,
            )
        )
        if count > MAX_DOTS:
            body += text(
                x0 + CRUCIBLE[0],
                y0 + CRUCIBLE[1] + 26,
                t("svg.gold.shown", n=MAX_DOTS),
                11,
                "end",
                color=STEEL,
            )
    body += text(24, H - 14, t("svg.gold.foot", note=scheme_note()), 12, color=STEEL)
    return svg(W, H, body, True, t("svg.gold.label"))


def poisson_summary(view: GoldView) -> dict[str, float]:
    """Resumen analítico de Poisson, para comparar con la simulación."""
    return {"p0": poisson_p0(view.lam), "median_particles": poisson_median_particles(view.lam)}
