"""Esquema animado del ensayo de sedimentación: una probeta en corte cuya interfase baja según la
curva h(t) en un tiempo COMPRIMIDO (de 0 a `t_animacion_s` en `RUN_S` s), y el espesador visto
desde arriba con el diámetro que sale del cálculo, a una escala declarada.

Lo que sale del cálculo: la cota de la interfase en cada cuadro (la curva), el reloj del ensayo y
el diámetro del espesador (dibujado = calculado × escala). Lo ilustrativo, y así se rotula: el
ancho de la probeta, el giro de los rastrillos y la compresión del tiempo.
"""

from __future__ import annotations

import math
import textwrap

from cian_svg import HOLD_S, ROW_PX, RUN_S, _clock, _keyframes
from dibujo import INK, STEEL, es, svg, text
from i18n import t
from sed_calculo import FRAMES, SedView

W, H = 940, 520
CYL_X, CYL_W, CYL_BASE, CYL_PX = 70.0, 80.0, 410.0, 280.0  # probeta: H0 = CYL_PX px
TH_CX, TH_CY = 730.0, 250.0  # centro del espesador
MAX_SCALE_PX_M, MAX_DIAMETER_PX = 5.0, 340.0  # escala del espesador (px por m) y su tope
RAKE_PERIOD_S = 9.0  # ilustrativo
SLURRY, WATER, TANK, FEED = "#B7791F", "#CFE3EC", "#E4DED2", "#1F7A6F"
TEXT_X = 200.0


def thickener_scale_px_per_m(diametro_m: float) -> float:
    """Píxeles por metro: 5 px/m, o menos si el diámetro no cabe (tope de `MAX_DIAMETER_PX`)."""
    return min(MAX_SCALE_PX_M, MAX_DIAMETER_PX / diametro_m)


def drawn_diameter_px(view: SedView) -> float:
    return view.diametro_m * thickener_scale_px_per_m(view.diametro_m)


def interface_y(h: float, h0: float) -> float:
    """Coordenada y (px) de la interfase para la cota h (m)."""
    return CYL_BASE - CYL_PX * h / h0


def motion_css(view: SedView) -> str:
    heights = view.alturas_animadas(FRAMES - 1)
    h0 = view.curva.h0
    slurry = [f"transform:scaleY({h / h0:.5f})" for h in heights]
    count = [f"transform:translateY({-i * ROW_PX}px)" for i in range(len(heights))]
    total = RUN_S + HOLD_S
    return (
        "@keyframes lb-rake{to{transform:rotate(360deg)}}"
        + _keyframes("lb-slurry", slurry)
        + _keyframes("lb-count", count)
        + ".lb-rake{transform-box:view-box;animation:lb-rake linear infinite}"
        + f".lb-slurry{{transform-box:fill-box;transform-origin:50% 100%;"
        f"animation:lb-slurry {total:g}s linear infinite}}"
        + f".lb-count{{animation:lb-count {total:g}s steps(1,end) infinite}}"
    )


def _cylinder(view: SedView, paused: bool) -> str:
    final = view.alturas_animadas(FRAMES - 1)[-1] / view.curva.h0
    style = (
        f' style="transform:scaleY({final:.5f});transform-box:fill-box;transform-origin:50% 100%"'
    )
    ticks = "".join(
        f'<line x1="{CYL_X + CYL_W}" y1="{CYL_BASE - CYL_PX * k / 4:.1f}" '
        f'x2="{CYL_X + CYL_W + 10}" y2="{CYL_BASE - CYL_PX * k / 4:.1f}" stroke="{STEEL}" '
        f'stroke-width="2"/>'
        for k in range(5)
    )
    return (
        f'<rect x="{CYL_X}" y="{CYL_BASE - CYL_PX}" width="{CYL_W}" height="{CYL_PX}" '
        f'fill="{WATER}"/>'
        f'<rect class="lb-slurry" x="{CYL_X}" y="{CYL_BASE - CYL_PX}" width="{CYL_W}" '
        f'height="{CYL_PX}" fill="{SLURRY}"{"" if not paused else style}/>'
        f'<path d="M {CYL_X} {CYL_BASE - CYL_PX - 20} L {CYL_X} {CYL_BASE} L {CYL_X + CYL_W} '
        f'{CYL_BASE} L {CYL_X + CYL_W} {CYL_BASE - CYL_PX - 20}" fill="none" stroke="{STEEL}" '
        f'stroke-width="6" stroke-linejoin="round"/>{ticks}'
        + text(
            CYL_X + CYL_W / 2,
            CYL_BASE + 22,
            t("svg.s.cyl", h=es(view.curva.h0, 2)),
            12,
            anchor="middle",
            color=STEEL,
        )
    )


def _thickener(view: SedView, paused: bool) -> str:
    scale = thickener_scale_px_per_m(view.diametro_m)
    r = view.diametro_m * scale / 2.0

    def arm(a: float) -> str:
        return (
            f'<line x1="{TH_CX}" y1="{TH_CY}" x2="{TH_CX + r * 0.92 * math.cos(a):.1f}" '
            f'y2="{TH_CY + r * 0.92 * math.sin(a):.1f}" stroke="{STEEL}" stroke-width="5"/>'
        )

    spin = (
        ""
        if paused
        else f' style="transform-origin:{TH_CX}px {TH_CY}px;animation-duration:{RAKE_PERIOD_S}s"'
    )
    bar_m = 10 if view.diametro_m < 100 else 50
    bx = TH_CX - r
    by = TH_CY + r + 34
    return (
        f'<circle class="lb-tank" cx="{TH_CX}" cy="{TH_CY}" r="{r:.2f}" fill="{TANK}" '
        f'stroke="{STEEL}" stroke-width="6"/>'
        f'<circle cx="{TH_CX}" cy="{TH_CY}" r="{max(r * 0.12, 6):.1f}" fill="{FEED}"/>'
        f'<g class="lb-rake"{spin}>{arm(0.4)}{arm(0.4 + math.pi)}</g>'
        f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx + bar_m * scale:.1f}" y2="{by:.1f}" '
        f'stroke="{INK}" stroke-width="3"/>'
        + text(bx, by + 18, t("svg.s.bar", m=es(bar_m, 0)), 12, color=INK)
    )


def _legend(view: SedView) -> str:
    scale = thickener_scale_px_per_m(view.diametro_m)
    paragraph = t(
        "svg.s.legend",
        run=es(RUN_S, 0),
        tmax=es(view.t_animacion_s, 0),
        n=len(view.curva.t_s),
        s=es(scale, 2),
    )
    lines = textwrap.wrap(paragraph, 84)
    return "".join(
        text(24, H - 17 * (len(lines) - n) - 8, ln, 12, color=INK if n == 0 else STEEL)
        for n, ln in enumerate(lines)
    )


def settling_svg(view: SedView, paused: bool = False) -> str:
    heights = view.alturas_animadas(FRAMES - 1)
    t_max = view.t_animacion_s
    times = [es(t_max * i / (FRAMES - 1), 0) for i in range(FRAMES)]
    body = (
        _cylinder(view, paused)
        + text(TEXT_X, 40, t("svg.s.title"), 24, cls="t", color=INK)
        + text(TEXT_X, 70, t("svg.s.time", tmax=es(t_max, 0), run=es(RUN_S, 0)), 14, color=STEEL)
        + text(TEXT_X, 130, t("svg.s.clock"), 17)
        + _clock(times, TEXT_X + 180, 130, 90, paused, INK)
        + text(TEXT_X + 275, 130, "s", 17)
        + text(TEXT_X, 175, t("svg.s.height"), 17)
        + _clock([es(h, 3) for h in heights], TEXT_X + 180, 175, 90, paused, FEED)
        + text(TEXT_X + 275, 175, "m", 17)
        + text(TEXT_X, 230, t("svg.s.diam", d=es(view.diametro_m, 1)), 17, cls="t")
        + text(
            TEXT_X,
            255,
            t("svg.s.tu", tc=es(view.tf.tc_s, 0), tu=es(view.tf.tu_s, 0)),
            14,
            color=STEEL,
        )
        + _thickener(view, paused)
        + text(TH_CX, 38, t("svg.s.rake"), 12, anchor="middle", color=STEEL)
        + _legend(view)
    )
    return svg(W, H, body, paused, t("svg.s.label"), motion_css(view))
