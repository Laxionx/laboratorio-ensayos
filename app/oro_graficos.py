"""Oro grueso: histograma animado de los 1 000 ensayos simulados (Plotly) y esquema SVG de la
alícuota con sus granos de oro. Los números de granos son los de la simulación; sus posiciones
dentro de la alícuota son ilustrativas y así se rotulan."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from calculo import GoldView
from dibujo import BRONZE_SVG, INK, SCHEME_NOTE, STEEL, es, svg, text
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
                name="ensayos simulados",
                marker=dict(color=BAR_COLOR),
                hovertemplate="%{x:.3g} g/t: %{y} ensayos<extra></extra>",
            )
        ]
        out.append(
            go.Scatter(
                x=[view.grade_gpt] * 2,
                y=[0, top],
                mode="lines",
                name=f"ley real {es(view.grade_gpt, 2)} g/t",
                line=dict(color=TRUE_COLOR, width=3),
            )
        )
        median = float(np.median(grades))
        out.append(
            go.Scatter(
                x=[median] * 2,
                y=[0, top],
                mode="lines",
                name=f"mediana de lo simulado {es(median, 2)} g/t",
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
                    name="Poisson analítico",
                    marker=dict(size=7, color=INK),
                )
            )
        return out

    def note(n: int) -> dict:
        grades = sim.grades_gpt[:n]
        return _note(
            f"{n} ensayos: mediana {es(float(np.median(grades)), 2)} g/t, "
            f"máximo {es(float(grades.max()), 1)} g/t"
        )

    frames = [go.Frame(data=traces(n), name=str(n), layout=note(n)) for n in sizes]
    fig = go.Figure(data=traces(sizes[-1]), frames=frames, layout=note(sizes[-1]))
    _layout(
        fig,
        "Ensayos repetidos de la misma alícuota (Poisson, semilla fija)",
        460,
        x=dict(title="Ley que daría el ensayo (g/t)"),
        y=dict(title="Número de ensayos"),
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
        ("ensayo bajo (percentil 10)", int(np.percentile(counts, 10, method="lower"))),
        ("ensayo mediano", int(np.median(counts))),
        ("ensayo alto (percentil 99)", int(np.percentile(counts, 99, method="higher"))),
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
        f"La misma alícuota de {es(view.aliquot_g, 0)} g, tres ensayos de la simulación",
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
                f"{count} {'grano' if count == 1 else 'granos'} de oro",
                15,
                cls="t",
            )
            + text(
                x0,
                y0 + CRUCIBLE[1] + 46,
                f"ley que daría: {es(count * per_grain, 2)} g/t (real {es(view.grade_gpt, 2)} g/t)",
                13,
            )
        )
        if count > MAX_DOTS:
            body += text(
                x0 + CRUCIBLE[0],
                y0 + CRUCIBLE[1] + 26,
                f"(se dibujan {MAX_DOTS})",
                11,
                "end",
                color=STEEL,
            )
    body += text(
        24, H - 14, f"{SCHEME_NOTE}; la posición de cada grano es ilustrativa.", 12, color=STEEL
    )
    return svg(W, H, body, True, "Tres alícuotas con distinto número de granos de oro")


def poisson_summary(view: GoldView) -> dict[str, float]:
    """Resumen analítico de Poisson, para comparar con la simulación."""
    return {"p0": poisson_p0(view.lam), "median_particles": poisson_median_particles(view.lam)}
