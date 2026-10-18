"""Esquema animado del crisol en corte durante la fusión: gotas de plomo que bajan por la escoria,
el botón al fondo, la capa de escoria y burbujas de gas.

Lo que sale del cálculo: la altura de la escoria (volumen = masa ÷ densidad supuesta, sobre la
sección del crisol), el volumen del botón (masa ÷ 11,34 g/cm³, plomo sólido, dibujado como esfera),
la cantidad de gotas (DROPS_PER_G por cada g de Pb) y el color (1 050 °C, USGS 1445). Lo
ilustrativo, y así se rotula: el radio y la altura del crisol, la densidad de la escoria (Bugbee no
la da), la posición de gotas y burbujas, y su rapidez.
"""

from __future__ import annotations

import math
import textwrap

import numpy as np
from calculo import FusionView
from colores import NOTE, temperature_color
from dibujo import INK, RISE_CSS, STEEL, es, rise, svg, text

from muestreo.fusion import FUSION_TEMP_C, PB_DENSITY, SLAG_DENSITY

W, H = 940, 620
PX_PER_CM = 50.0  # escala del dibujo
CRUCIBLE_R_CM = 3.0  # radio interior, ILUSTRATIVO
CRUCIBLE_H_CM = 5.0  # altura interior, ILUSTRATIVA
X0, BOTTOM = 70.0, 470.0
DROPS_PER_G = 0.5  # gotas de plomo por cada g de Pb reducido
BUBBLES_PER_MOL = 60.0  # burbujas por mol de gas (CO2 y SO2); ilustrativo
MAX_BUBBLES = 30
FALL_S, BUBBLE_S = 2.6, 1.8  # ilustrativas
LEAD_COLOR, BUBBLE_COLOR = "#7A8389", "#F5F1E8"
SEED = 2017


def interior_px() -> tuple[float, float]:
    """(ancho, alto) interior del crisol en px."""
    return 2 * CRUCIBLE_R_CM * PX_PER_CM, CRUCIBLE_H_CM * PX_PER_CM


def slag_height_cm(slag_g: float) -> float:
    """Altura (cm) de la escoria en el crisol cilíndrico: volumen ÷ sección."""
    return slag_g / SLAG_DENSITY / (math.pi * CRUCIBLE_R_CM**2)


def slag_height_px(slag_g: float) -> float:
    return min(slag_height_cm(slag_g) * PX_PER_CM, interior_px()[1])


def button_radius_cm(button_g: float) -> float:
    """Radio (cm) del botón como esfera de plomo sólido: V = m/ρ = 4/3 π r³."""
    return (3.0 * (button_g / PB_DENSITY) / (4.0 * math.pi)) ** (1.0 / 3.0)


def drop_count(button_g: float) -> int:
    return round(button_g * DROPS_PER_G)


def bubble_count(gas_mol: dict[str, float]) -> int:
    return min(MAX_BUBBLES, round(sum(gas_mol.values()) * BUBBLES_PER_MOL))


def _crucible() -> str:
    width, height = interior_px()
    wall = f'fill="none" stroke="{STEEL}" stroke-width="10" stroke-linejoin="round"'
    two_thirds = BOTTOM - height * 2.0 / 3.0
    return (
        f'<path d="M {X0 - 5} {BOTTOM - height - 10} L {X0 - 5} {BOTTOM + 5} L {X0 + width + 5} '
        f'{BOTTOM + 5} L {X0 + width + 5} {BOTTOM - height - 10}" {wall}/>'
        f'<line x1="{X0}" y1="{two_thirds:.1f}" x2="{X0 + width}" y2="{two_thirds:.1f}" '
        f'stroke="{STEEL}" stroke-width="1.5" stroke-dasharray="6 5"/>'
        + text(X0 + width + 12, two_thirds + 4, "2/3 del crisol", 11, color=STEEL)
    )


def _slag(view: FusionView) -> str:
    width, _ = interior_px()
    h = slag_height_px(view.result.slag.mass_g)
    color = temperature_color(FUSION_TEMP_C)
    return (
        f'<rect class="lb-slag" x="{X0}" y="{BOTTOM - h:.2f}" width="{width}" height="{h:.2f}" '
        f'fill="{color}"/>'
    )


def _button(view: FusionView) -> str:
    r = button_radius_cm(view.result.button_g) * PX_PER_CM
    if r <= 0:
        return ""
    cx = X0 + interior_px()[0] / 2
    return (
        f'<circle class="lb-button" cx="{cx:.1f}" cy="{BOTTOM - r:.2f}" r="{r:.2f}" '
        f'fill="{LEAD_COLOR}" stroke="#4A5359" stroke-width="2"/>'
        f'<circle cx="{cx - r * 0.3:.1f}" cy="{BOTTOM - r * 1.3:.2f}" r="{r * 0.22:.2f}" '
        f'fill="#FFFFFF" fill-opacity=".35"/>'
    )


def _particles(view: FusionView, paused: bool) -> str:
    width, _ = interior_px()
    rng = np.random.default_rng(SEED)
    slag_h = slag_height_px(view.result.slag.mass_g)
    drops, out = drop_count(view.result.button_g), []
    fall = max(slag_h - 8.0, 0.0)
    for n in range(drops):
        x = X0 + 12 + rng.random() * (width - 24)
        out.append(
            rise(
                x,
                BOTTOM - slag_h + 4,
                -fall,
                FALL_S,
                (n / max(drops, 1)) % 1.0,
                f'<circle class="lb-drop" r="3.4" fill="{LEAD_COLOR}"/>',
                paused,
            )
        )
    bubbles = bubble_count(view.result.gas_mol)
    for n in range(bubbles):
        x = X0 + 12 + rng.random() * (width - 24)
        out.append(
            rise(
                x,
                BOTTOM - 6,
                slag_h - 8,
                BUBBLE_S,
                (n * 0.37) % 1.0,
                f'<circle class="lb-bubble" r="3" fill="{BUBBLE_COLOR}" fill-opacity=".8" '
                f'stroke="#FFFFFF"/>',
                paused,
            )
        )
    return "".join(out)


def _panel(view: FusionView) -> str:
    r, used, designed = view.result, view.used, view.designed
    x, rows = (
        470.0,
        [
            ("Soda (Na₂CO₃)", used.soda_g, designed.soda_g),
            ("Litargirio (PbO)", used.litharge_g, designed.litharge_g),
            ("Bórax vidrio", used.borax_g, designed.borax_g),
            ("Sílice (SiO₂)", used.silica_g, designed.silica_g),
            ("Harina", used.flour_g, designed.flour_g),
            ("Nitro (KNO₃)", used.niter_g, designed.niter_g),
        ],
    )
    out = [text(x, 70, "Carga (g)", 15, cls="t")]
    for i, (name, usedg, designedg) in enumerate(rows):
        y = 98 + 22 * i
        mark = "" if abs(usedg - designedg) < 1e-9 else f"  (calculada {es(designedg, 1)})"
        out.append(text(x, y, name, 13))
        out.append(text(x + 160, y, f"{es(usedg, 1)}{mark}", 13, color=STEEL))
    y = 98 + 22 * len(rows) + 22
    out.append(
        text(
            x, y, f"Botón de plomo: {es(r.button_g, 1)} g · {es(r.button_cm3, 2)} cm³", 15, cls="t"
        )
    )
    out.append(
        text(
            x,
            y + 24,
            f"Escoria: {es(r.slag.mass_g, 1)} g · grado {r.slag.label} ({es(r.slag.degree, 2)})",
            15,
            cls="t",
        )
    )
    out.append(
        text(
            x,
            y + 48,
            f"Volumen de la escoria: {es(r.slag_cm3, 1)} cm³ (densidad "
            f"supuesta {es(SLAG_DENSITY, 1)} g/cm³)",
            12,
            color=STEEL,
        )
    )
    out.append(
        text(
            x,
            y + 68,
            f"Gotas dibujadas: {drop_count(r.button_g)} · burbujas: {bubble_count(r.gas_mol)}",
            12,
            color=STEEL,
        )
    )
    return "".join(out)


def _legend(view: FusionView) -> str:
    paragraphs = [
        f"Alto de la escoria ∝ su masa: volumen = masa ÷ {es(SLAG_DENSITY, 1)} g/cm³ (densidad "
        f"supuesta ilustrativa) sobre un crisol de {es(CRUCIBLE_R_CM, 0)} cm de radio "
        "(ilustrativo). Botón = masa ÷ 11,34 g/cm³ (plomo sólido), dibujado como esfera. "
        f"Gotas de plomo: {DROPS_PER_G:g} por g reducido. Burbujas de CO₂ y SO₂ y la posición de "
        f"gotas y burbujas: ilustrativas. Color: {NOTE} a {es(FUSION_TEMP_C, 0)} °C.",
    ]
    lines = [ln for para in paragraphs for ln in textwrap.wrap(para, 140)]
    lines.append("esquema, no a escala: las cantidades sí son del cálculo")
    top = H - 17 * len(lines) - 6
    return "".join(
        text(24, top + 17 * n, ln, 12, color=INK if n == len(lines) - 1 else STEEL)
        for n, ln in enumerate(lines)
    )


def crucible_svg(view: FusionView, paused: bool = False) -> str:
    title = text(24, 30, "Crisol en corte durante la fusión", 18, cls="t")
    body = (
        title
        + _crucible()
        + _slag(view)
        + _particles(view, paused)
        + _button(view)
        + _panel(view)
        + _legend(view)
    )
    return svg(W, H, body, paused, "Crisol con escoria, gotas de plomo y botón al fondo", RISE_CSS)
