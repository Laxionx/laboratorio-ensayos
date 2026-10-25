"""Esquema animado de la copelación: una copela en corte, dentro de la mufla, con el botón de plomo
que se achica mientras el litargirio se absorbe en la copela, hasta que queda la perla de oro y
plata.

Lo que sale del cálculo (en cada cuadro): la masa del botón (plomo + oro + plata), su radio
((volumen / volumen inicial)^(1/3), con la densidad del plomo líquido a la temperatura de
copelación), su color (de gris plomo al color de la perla según la composición), la parte de plomo
oxidada (la copela absorbida) y la masa de la perla del último cuadro. Color de la mufla: la rampa
ILUSTRATIVA de temperatura de `colores.py`.

Lo ilustrativo, y así se rotula: el avance en el tiempo (Bugbee da la curva minuto a minuto solo
como figura, Fig. 40), la forma de la pérdida acumulada (Rose, cualitativa; el total sí es del
cálculo) y el tamaño del botón inicial, que no depende de los gramos de plomo.
"""

from __future__ import annotations

import textwrap

from cian_svg import HOLD_S, ROW_PX, RUN_S, _clock, _keyframes
from colores import temperature_color
from cop_calculo import FRAMES, CopView
from dibujo import INK, STEEL, es, svg, text
from i18n import t

W, H = 940, 540
CX, RIM_Y, POCKET_Y = 230.0, 222.0, 276.0  # eje de la copela, borde y fondo de su hueco
R0, RY0 = 62.0, 42.0  # semiancho y alto del botón entero (px): fijos, no dependen del plomo
TEXT_X = 470.0
LEAD, SILVER, GOLD, BONE, LITHARGE = "#7C8590", "#C9CED2", "#D6A21E", "#E6DCC3", "#B7791F"
SOAK_MAX = 0.85  # opacidad de la copela con todo el plomo absorbido


def hex_rgb(color: str) -> tuple[int, int, int]:
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


def mix(a: str, b: str, w: float) -> str:
    """Mezcla de dos colores `#RRGGBB`: a con peso `w` y b con `1 - w`."""
    w = min(max(w, 0.0), 1.0)
    return "#{:02X}{:02X}{:02X}".format(
        *(round(x * w + y * (1.0 - w)) for x, y in zip(hex_rgb(a), hex_rgb(b), strict=True))
    )


def frame_color(c) -> str:
    """Color del botón de un cuadro: gris plomo mezclado con el de los preciosos, según la masa."""
    pearl = mix(GOLD, SILVER, c.ley_oro)
    return mix(LEAD, pearl, c.plomo_mg / c.masa_mg)


def frame_soak(view: CopView, i: int) -> float:
    """Opacidad de la copela en el cuadro `i`: la parte del plomo que ya se oxidó y absorbió."""
    pb0 = view.cuadros[0].plomo_mg
    return SOAK_MAX * (1.0 - view.cuadros[i].plomo_mg / pb0)


def motion_css(view: CopView) -> str:
    scale = [f"transform:scale({s:.5f})" for s in view.escalas]
    color = [f"fill:{frame_color(c)}" for c in view.cuadros]
    soak = [f"opacity:{frame_soak(view, i):.4f}" for i in range(FRAMES)]
    count = [f"transform:translateY({-i * ROW_PX}px)" for i in range(FRAMES)]
    total = RUN_S + HOLD_S
    return (
        _keyframes("lb-btn", scale)
        + _keyframes("lb-btnc", color)
        + _keyframes("lb-soak", soak)
        + _keyframes("lb-count", count)
        + f".lb-btn{{transform-box:fill-box;transform-origin:50% 100%;"
        f"animation:lb-btn {total:g}s linear infinite}}"
        + f".lb-btnc{{animation:lb-btnc {total:g}s linear infinite}}"
        + f".lb-soak{{animation:lb-soak {total:g}s linear infinite}}"
        + f".lb-count{{animation:lb-count {total:g}s steps(1,end) infinite}}"
    )


def _pearl_marker(view: CopView) -> str:
    """Una cúpula a trazos del tamaño de la perla final (radio = el del cálculo) con su rótulo:
    queda tapada por el botón mientras es grande y aparece cuando se achica hasta ella."""
    r = R0 * view.escalas[-1] + 3.0
    ry = r * RY0 / R0
    return (
        f'<path d="M {CX - r:.1f} {POCKET_Y} A {r:.1f} {ry:.1f} 0 0 1 {CX + r:.1f} {POCKET_Y} Z" '
        f'fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="3 2"/>'
        f'<line x1="{CX}" y1="{RIM_Y + 22}" x2="{CX}" y2="{POCKET_Y - ry - 2:.1f}" '
        f'stroke="{INK}" stroke-width="1"/>'
        + text(CX, RIM_Y + 18, t("svg.k.bead"), 12, anchor="middle", color=INK)
    )


def _cupel(view: CopView, paused: bool) -> str:
    """La mufla (color de la temperatura), la copela con su hueco, la parte absorbida y el botón."""
    last = view.cuadros[-1]
    glow = temperature_color(view.params.temp_c)
    left, right = CX - 100.0, CX + 100.0
    pocket = (
        f"M {CX - 82} {RIM_Y} Q {CX - 82} {POCKET_Y} {CX} {POCKET_Y} "
        f"Q {CX + 82} {POCKET_Y} {CX + 82} {RIM_Y} Z"
    )
    soak = (
        f"M {CX - 82} {RIM_Y} Q {CX - 82} {POCKET_Y} {CX} {POCKET_Y} "
        f"Q {CX + 82} {POCKET_Y} {CX + 82} {RIM_Y} L {CX + 96} {RIM_Y} "
        f"Q {CX + 96} {POCKET_Y + 20} {CX} {POCKET_Y + 20} "
        f"Q {CX - 96} {POCKET_Y + 20} {CX - 96} {RIM_Y} Z"
    )
    soak_style = f' style="opacity:{frame_soak(view, FRAMES - 1):.4f}"' if paused else ""
    btn_style = (
        f' style="transform:scale({view.escalas[-1]:.5f});transform-box:fill-box;'
        f'transform-origin:50% 100%"'
        if paused
        else ""
    )
    fill_style = f' style="fill:{frame_color(last)}"' if paused else ""
    dome = f"M {-R0} 0 A {R0} {RY0} 0 0 1 {R0} 0 Z"
    return (
        f'<rect x="30" y="110" width="400" height="300" rx="16" fill="{glow}" fill-opacity="0.9" '
        f'stroke="{STEEL}" stroke-width="5"/>'
        + text(34, 100, t("svg.k.muffle"), 12, color=STEEL)
        + f'<path d="M {left} {RIM_Y} L {left + 14} 372 Q {left + 16} 388 {left + 34} 388 '
        f'L {right - 34} 388 Q {right - 16} 388 {right - 14} 372 L {right} {RIM_Y} Z" '
        f'fill="{BONE}" stroke="{INK}" stroke-width="2"/>'
        f'<path d="{soak}" fill="{LITHARGE}" class="lb-soak"{soak_style}/>'
        f'<path d="{pocket}" fill="#CDBF9C" fill-opacity="0.55" stroke="{INK}" stroke-width="1.5"/>'
        + _pearl_marker(view)
        + f'<g transform="translate({CX} {POCKET_Y})"><g class="lb-btn"{btn_style}>'
        f'<path d="{dome}" class="lb-btnc" fill="{LEAD}" stroke="{INK}" stroke-width="2"'
        f"{fill_style}/>"
        f"</g></g>" + text(CX, 432, t("svg.k.cupel"), 12, anchor="middle", color=STEEL)
    )


def _legend(view: CopView) -> str:
    paragraph = t("svg.k.legend", run=es(RUN_S, 0), pb=es(view.plomo_g, 1))
    lines = textwrap.wrap(paragraph, 128)
    top = H - 17 * len(lines) - 6
    return "".join(
        text(24, top + 17 * n, ln, 12, color=INK if n == 0 else STEEL) for n, ln in enumerate(lines)
    )


def clock_values(view: CopView) -> tuple[list[str], list[str], list[str]]:
    """Los textos de los tres relojes (avance %, masa del botón mg, plomo que queda g)."""
    cuadros = view.cuadros
    return (
        [es(100.0 * c.avance, 0) for c in cuadros],
        [es(c.masa_mg, 1) for c in cuadros],
        [es(c.plomo_mg / 1000.0, 2) for c in cuadros],
    )


def copelacion_svg(view: CopView, paused: bool = False) -> str:
    r, p = view.res, view.params
    progress, mass, lead = clock_values(view)
    body = (
        _cupel(view, paused)
        + text(TEXT_X, 40, t("svg.k.title"), 24, cls="t", color=INK)
        + text(
            TEXT_X,
            68,
            t("svg.k.cond", temp=es(p.temp_c, 0), pb=es(view.plomo_g, 1)),
            14,
            color=STEEL,
        )
        + text(TEXT_X, 130, t("svg.k.progress"), 17)
        + _clock(progress, TEXT_X + 250, 130, 90, paused, INK)
        + text(TEXT_X + 345, 130, "%", 17)
        + text(TEXT_X, 175, t("svg.k.mass"), 17)
        + _clock(mass, TEXT_X + 250, 175, 110, paused, "#1F7A6F")
        + text(TEXT_X + 365, 175, "mg", 17)
        + text(TEXT_X, 220, t("svg.k.lead"), 17)
        + _clock(lead, TEXT_X + 250, 220, 90, paused, STEEL)
        + text(TEXT_X + 345, 220, "g", 17)
        + text(
            TEXT_X,
            275,
            t("svg.k.pearl", mg=es(r.perla_mg, 2), au=es(100 * r.oro_en_perla, 1)),
            17,
            cls="t",
        )
        + text(
            TEXT_X,
            302,
            t("svg.k.au", mg=es(r.oro_final_mg, 3), loss=es(r.perdida_au.pct, 2)),
            14,
            color=STEEL,
        )
        + text(
            TEXT_X,
            324,
            t("svg.k.ag", mg=es(r.plata_final_mg, 2), loss=es(r.perdida_ag.pct, 2)),
            14,
            color=STEEL,
        )
        + text(TEXT_X, 346, t("svg.k.ratio", ratio=es(r.razon_final, 1)), 14, color=STEEL)
        + _legend(view)
    )
    return svg(W, H, body, paused, t("svg.k.label"), motion_css(view))
