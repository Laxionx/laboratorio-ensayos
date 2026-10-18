"""Esquema animado del crisol en corte durante la fusión: un crisol cónico (ancho arriba, angosto
al fondo) con el plomo LÍQUIDO en un charco al fondo, la escoria encima, gotas de plomo que bajan
por la escoria y burbujas de gas.

Lo que sale del cálculo: el volumen del plomo líquido (masa ÷ densidad del plomo líquido a
1 050 °C, 9,79 g/cm³) y el de la escoria (masa ÷ densidad supuesta); el nivel de cada capa es el que
tiene ese volumen dentro del cono (`muestreo.crisol`, integrando el cono), de modo que el plomo
queda SIEMPRE debajo de la escoria. Cada capa se dibuja como el trozo del cono entre sus dos
niveles. Lo ilustrativo, y así se rotula: las medidas del crisol (su capacidad, 190 cm³, sí es de
Bugbee), la densidad de la escoria (Bugbee no la da), la cantidad de gotas, la posición de gotas
y burbujas y su rapidez. El botón ya frío (g y cm³, plomo sólido) va aparte en el panel.
"""

from __future__ import annotations

import textwrap

import numpy as np
from calculo import FusionView
from colores import NOTE, temperature_color
from dibujo import INK, RISE_CSS, STEEL, es, rise, svg, text

from muestreo.crisol import CRUCIBLE, DRY_BULK_DENSITY, Layers, layers
from muestreo.fusion import FUSION_TEMP_C, SLAG_DENSITY, pb_liquid_density

W, H = 940, 620
PX_PER_CM = 46.0  # escala del dibujo
CX, BOTTOM = 240.0, 490.0  # eje del crisol y fondo interior, en px
DROPS_PER_G = 0.5  # gotas de plomo por cada g de Pb reducido
BUBBLES_PER_MOL = 60.0  # burbujas por mol de gas (CO2 y SO2); ilustrativo
MAX_BUBBLES = 30
FALL_S, BUBBLE_S = 2.6, 1.8  # ilustrativas
LEAD_COLOR, BUBBLE_COLOR = "#7A8389", "#F5F1E8"
SEED = 2017


def y_of(z_cm: float) -> float:
    """Coordenada y (px) de la altura `z_cm` sobre el fondo del crisol."""
    return BOTTOM - z_cm * PX_PER_CM


def half_width_px(z_cm: float) -> float:
    """Semiancho (px) del interior del cono a la altura `z_cm`."""
    return CRUCIBLE.radius_at(z_cm) * PX_PER_CM


def view_layers(view: FusionView) -> Layers:
    """Niveles del plomo líquido y de la escoria de esta carga, dentro del cono."""
    return layers(view.result.lead_hot_cm3, view.result.slag_cm3)


def drop_count(button_g: float) -> int:
    return round(button_g * DROPS_PER_G)


def bubble_count(gas_mol: dict[str, float]) -> int:
    return min(MAX_BUBBLES, round(sum(gas_mol.values()) * BUBBLES_PER_MOL))


def _band(cls: str, z0: float, z1: float, fill: str, stroke: str = "none") -> str:
    """Trozo del cono entre las alturas z0 y z1 (cm): un trapecio con los lados sobre la pared."""
    pts = (
        (CX - half_width_px(z0), y_of(z0)),
        (CX + half_width_px(z0), y_of(z0)),
        (CX + half_width_px(z1), y_of(z1)),
        (CX - half_width_px(z1), y_of(z1)),
    )
    points = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
    return f'<polygon class="{cls}" points="{points}" fill="{fill}" stroke="{stroke}"/>'


def _crucible() -> str:
    """Pared del crisol (cono) y la línea de los 2/3 de la capacidad (por volumen)."""
    top = CRUCIBLE.height
    wall = f'fill="none" stroke="{STEEL}" stroke-width="10" stroke-linejoin="round"'
    pts = (
        f"M {CX - half_width_px(top) - 5:.2f} {y_of(top) - 10:.2f} "
        f"L {CX - half_width_px(0) - 5:.2f} {BOTTOM + 5:.2f} "
        f"L {CX + half_width_px(0) + 5:.2f} {BOTTOM + 5:.2f} "
        f"L {CX + half_width_px(top) + 5:.2f} {y_of(top) - 10:.2f}"
    )
    z23 = CRUCIBLE.level_for(CRUCIBLE.fill_limit_cm3)
    xr = CX + half_width_px(z23)
    return (
        f'<path class="lb-wall" d="{pts}" {wall}/>'
        f'<line class="lb-limit" x1="{CX - half_width_px(z23):.2f}" y1="{y_of(z23):.2f}" '
        f'x2="{xr:.2f}" y2="{y_of(z23):.2f}" stroke="{STEEL}" stroke-width="1.5" '
        f'stroke-dasharray="6 5"/>'
        + text(CX - half_width_px(z23) + 10, y_of(z23) - 6,
               f"2/3 de la capacidad ({es(CRUCIBLE.fill_limit_cm3, 0)} cm³)", 11, color=STEEL)
    )  # fmt: skip


def _melt(view: FusionView) -> str:
    """Plomo líquido (charco al fondo del cono) y escoria encima."""
    lay = view_layers(view)
    return _band("lb-slag", lay.lead_top, lay.slag_top, temperature_color(FUSION_TEMP_C)) + _band(
        "lb-button", 0.0, lay.lead_top, LEAD_COLOR, "#4A5359"
    )


def _particles(view: FusionView, paused: bool) -> str:
    lay = view_layers(view)
    rng = np.random.default_rng(SEED)
    # la caída y las burbujas van verticales dentro del ancho del charco: no tocan la pared
    span = max(half_width_px(lay.lead_top) - 8.0, 1.0)
    drops, out = drop_count(view.result.button_g), []
    fall = max(y_of(lay.lead_top) - y_of(lay.slag_top) - 4.0, 0.0)
    for n in range(drops):
        x = CX + (rng.random() * 2 - 1) * span
        out.append(
            rise(
                x,
                y_of(lay.slag_top) + 2,
                -fall,
                FALL_S,
                (n / max(drops, 1)) % 1.0,
                f'<circle class="lb-drop" r="3.4" fill="{LEAD_COLOR}"/>',
                paused,
            )
        )
    for n in range(bubble_count(view.result.gas_mol)):
        x = CX + (rng.random() * 2 - 1) * span
        out.append(
            rise(
                x,
                y_of(lay.lead_top) - 4,
                max(fall - 4.0, 0.0),
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
    rho = pb_liquid_density(FUSION_TEMP_C)
    lines = (
        (f"Plomo líquido: {es(r.button_g, 1)} g · {es(r.lead_hot_cm3, 2)} cm³ a {es(rho, 2)} g/cm³",
         15, INK),
        (f"Botón ya frío: {es(r.button_g, 1)} g · {es(r.button_cm3, 2)} cm³ (sólido, 11,34 g/cm³)",
         12, STEEL),
        (f"Escoria: {es(r.slag.mass_g, 1)} g · grado {r.slag.label} ({es(r.slag.degree, 2)})",
         15, INK),
        (f"Volumen de la escoria: {es(r.slag_cm3, 1)} cm³ (densidad supuesta "
         f"{es(SLAG_DENSITY, 1)} g/cm³)", 12, STEEL),
        (f"Carga en polvo: {es(r.dry_charge_g, 0)} g ≈ {es(r.dry_charge_g / DRY_BULK_DENSITY, 0)} "
         f"cm³ (supuesto {es(DRY_BULK_DENSITY, 1)} g/cm³); capacidad "
         f"{es(CRUCIBLE.capacity_cm3, 0)} "
         f"cm³", 12, STEEL),
        (f"Gotas dibujadas: {drop_count(r.button_g)} · burbujas: {bubble_count(r.gas_mol)}",
         12, STEEL),
    )  # fmt: skip
    for n, (line, size, color) in enumerate(lines):
        out.append(text(x, y + 22 * n, line, size, color=color, cls="t" if color == INK else ""))
    return "".join(out)


def _legend(view: FusionView) -> str:
    paragraphs = [
        f"Crisol cónico ilustrativo: radio de {es(CRUCIBLE.r_bottom, 2)} cm al fondo y "
        f"{es(CRUCIBLE.r_top, 2)} cm arriba, {es(CRUCIBLE.height, 1)} cm de alto; su capacidad, "
        f"{es(CRUCIBLE.capacity_cm3, 0)} cm³, es la del crisol de 20 g de Bugbee (Tabla IV). "
        "El plomo está LÍQUIDO y forma un charco al fondo: volumen = masa ÷ densidad del plomo "
        f"líquido a {es(FUSION_TEMP_C, 0)} °C (OECD/NEA 2007). La escoria llena el cono encima: "
        f"volumen = masa ÷ {es(SLAG_DENSITY, 1)} g/cm³ (supuesto). Gotas de plomo: "
        f"{DROPS_PER_G:g} por g reducido; burbujas de CO₂ y SO₂ y su posición: ilustrativas. "
        f"Escoria con el {NOTE} a {es(FUSION_TEMP_C, 0)} °C.",
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
        title + _melt(view) + _crucible() + _particles(view, paused) + _panel(view) + _legend(view)
    )
    return svg(
        W, H, body, paused, "Crisol cónico con el plomo líquido al fondo y la escoria encima",
        RISE_CSS,
    )  # fmt: skip
