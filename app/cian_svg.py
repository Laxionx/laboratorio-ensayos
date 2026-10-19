"""Esquema animado de la botella de cianuración en corte: la botella gira a las rpm del
procedimiento (una vuelta cada 60/rpm s), con la pulpa dentro, y un indicador de recuperación que
avanza siguiendo el modelo elegido en un tiempo COMPRIMIDO (todo el ensayo en `RUN_S` s), junto con
los puntos medidos.

Lo que sale del cálculo: las rpm (y el período de giro), la recuperación del modelo en cada
instante (la curva del modelo, muestreada en `FRAMES` instantes parejos), el reloj del ensayo y los
puntos medidos. Lo ilustrativo, y así se rotula: la botella, su tamaño y su nivel de pulpa (el
artículo no publica la botella), y la compresión del tiempo.
"""

from __future__ import annotations

import math
import textwrap

from cian_calculo import CURVA_PUNTOS, CianView, model_name
from dibujo import INK, STEEL, es, svg, text
from i18n import t

W, H = 940, 440
CX, CY, R_OUT = 200.0, 215.0, 130.0  # la botella, vista desde su extremo
GX, GY, GW, GH = 400.0, 262.0, 480.0, 26.0  # el indicador (barra de recuperación)
RUN_S, HOLD_S = 12.0, 2.0  # el ensayo completo en 12 s y 2 s de pausa antes de repetir
FRAMES = CURVA_PUNTOS  # instantes del indicador (96 intervalos)
ROW_PX = 22  # alto de cada número de los relojes
PULP, GAUGE, MEASURED = "#B7791F", "#1F7A6F", "#C0462B"
PULP_MIN, PULP_SPAN = 0.25, 0.60  # opacidad de la pulpa: 0,25 + 0,60·R/100 (ilustrativo)
TILT_DEG, FILL_FRACTION = 30.0, 0.35  # inclinación y nivel de la pulpa (ilustrativos)


def rotation_period_s(rpm: float) -> float:
    """Segundos por vuelta de la botella a `rpm` rpm."""
    return 60.0 / rpm


def _keyframes(name: str, values: list[str], easing: str = "") -> str:
    """Un @keyframes con un valor por instante, comprimido en la parte del ciclo que dura RUN_S;
    el resto (HOLD_S) se queda en el último valor."""
    run = 100.0 * RUN_S / (RUN_S + HOLD_S)
    k = len(values) - 1
    steps = "".join(f"{run * i / k:.4f}%{{{v}}}" for i, v in enumerate(values))
    return f"@keyframes {name}{{{steps}100%{{{values[-1]}}}}}"


def motion_css(view: CianView) -> str:
    rec = view.animada(view.params.model, FRAMES - 1)
    bar = [f"transform:scaleX({r / 100.0:.5f})" for r in rec]
    pulp = [f"fill-opacity:{PULP_MIN + PULP_SPAN * r / 100.0:.4f}" for r in rec]
    steps = len(rec) - 1
    count = [f"transform:translateY({-i * ROW_PX}px)" for i in range(len(rec))]
    total = RUN_S + HOLD_S
    return (
        "@keyframes lb-spin{to{transform:rotate(360deg)}}"
        + _keyframes("lb-bar", bar)
        + _keyframes("lb-pulp", pulp)
        + _keyframes("lb-count", count)
        + ".lb-spin{transform-box:view-box;animation:lb-spin linear infinite}"
        + f".lb-bar{{transform-box:fill-box;transform-origin:0 50%;"
        f"animation:lb-bar {total:g}s linear infinite}}"
        + f".lb-pulp{{animation:lb-pulp {total:g}s linear infinite}}"
        + f".lb-count{{animation:lb-count {total:g}s steps({steps},end) infinite}}"
    )


def _pulp_path() -> str:
    """El segmento circular de pulpa: ocupa `FILL_FRACTION` del diámetro, inclinado."""
    r = R_OUT - 14.0
    y = r * (1.0 - 2.0 * FILL_FRACTION)  # la cuerda, bajo el centro si FILL_FRACTION < 0,5
    half = math.sqrt(r * r - y * y)
    return f"M {-half:.2f} {y:.2f} A {r:.2f} {r:.2f} 0 0 0 {half:.2f} {y:.2f} Z"


def _bottle(view: CianView, paused: bool) -> str:
    period = rotation_period_s(view.params.rpm)
    final = view.animada(view.params.model, FRAMES - 1)[-1]
    ribs = "".join(
        f'<rect x="{CX - 4:.1f}" y="{CY - R_OUT - 7:.1f}" width="8" height="18" fill="{STEEL}" '
        f'transform="rotate({k * 45} {CX} {CY})"/>'
        for k in range(8)
    )
    spin = (
        ""
        if paused
        else f' style="transform-origin:{CX}px {CY}px;animation-duration:{period:.3f}s"'
    )
    pulp_style = (
        f' style="fill-opacity:{PULP_MIN + PULP_SPAN * final / 100.0:.4f}"' if paused else ""
    )
    return (
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUT + 10}" fill="{STEEL}"/>'
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUT}" fill="#E4DED2"/>'
        f'<g transform="translate({CX} {CY}) rotate({TILT_DEG})">'
        f'<path class="lb-pulp" d="{_pulp_path()}" fill="{PULP}"{pulp_style}/></g>'
        f'<g class="lb-spin"{spin}>{ribs}'
        f'<circle cx="{CX}" cy="{CY - R_OUT - 14}" r="4" fill="#F5F1E8"/></g>'
    )


def _clock(values: list[str], x: float, y: float, width: float, paused: bool, color: str) -> str:
    """Un reloj de números: una columna de textos tras una ventana que muestra uno solo."""
    final = -(len(values) - 1) * ROW_PX
    style = f' style="transform:translateY({final}px)"' if paused else ""
    cells = "".join(
        text(0, ROW_PX * (i + 1) - 5, v, 17, color=color, style="font-weight:700")
        for i, v in enumerate(values)
    )
    cid = f"lb-clip-{int(x)}-{int(y)}"
    return (
        f'<defs><clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" '
        f'height="{ROW_PX}"/></clipPath></defs>'
        f'<g clip-path="url(#{cid})"><g transform="translate({x:.1f} {y:.1f})">'
        f'<g class="lb-count"{style}>{cells}</g></g></g>'
    )


def _gauge(view: CianView, paused: bool) -> str:
    model = view.params.model
    rec = view.animada(model, FRAMES - 1)
    final = rec[-1]
    bar_style = (
        f' style="transform:scaleX({final / 100.0:.5f});transform-box:fill-box;'
        f'transform-origin:0 50%"'
        if paused
        else ""
    )
    out = [
        f'<rect x="{GX}" y="{GY}" width="{GW}" height="{GH}" fill="#E4DED2"/>',
        f'<rect class="lb-bar" x="{GX}" y="{GY}" width="{GW}" height="{GH}" fill="{GAUGE}"'
        f"{bar_style}/>",
        f'<rect x="{GX}" y="{GY}" width="{GW}" height="{GH}" fill="none" stroke="{STEEL}"/>',
    ]
    for v in (0, 25, 50, 75, 100):
        x = GX + GW * v / 100.0
        out.append(text(x, GY + GH + 18, f"{v}", 12, anchor="middle", color=STEEL))
    for i, (tt, r) in enumerate(zip(view.balance.t_h, view.balance.recuperacion_pct, strict=True)):
        x = GX + GW * min(max(r, 0.0), 100.0) / 100.0
        top = GY - 8 - 13 * (i % 4)
        out.append(
            f'<line x1="{x:.1f}" y1="{top:.1f}" x2="{x:.1f}" y2="{GY}" stroke="{MEASURED}" '
            f'stroke-width="2"/>'
            + text(
                x,
                top - 3,
                f"{es(tt, 0 if float(tt).is_integer() else 1)} h",
                11,
                anchor="middle",
                color=MEASURED,
            )
        )
    return "".join(out)


def _hours(view: CianView) -> list[str]:
    tmax = view.tmax
    d = 0 if tmax >= 48 else 1
    return [es(tmax * i / (FRAMES - 1), d) for i in range(FRAMES)]


def _legend(view: CianView) -> str:
    paragraph = t("svg.c.legend", run=es(RUN_S, 0), tmax=es(view.tmax, 0), n=len(view.balance.t_h))
    lines = textwrap.wrap(paragraph, 130)
    top = H - 17 * len(lines) - 8
    return "".join(
        text(24, top + 17 * n, ln, 12, color=INK if n == 0 else STEEL) for n, ln in enumerate(lines)
    )


def bottle_svg(view: CianView, paused: bool = False) -> str:
    rpm, model = view.params.rpm, view.params.model
    rec = view.animada(model, FRAMES - 1)
    rows = [
        (t("svg.c.title"), 24, "t", INK),
        (t("svg.c.rpm", rpm=es(rpm, 1), period=es(rotation_period_s(rpm), 2)), 17, "", INK),
        (t("svg.c.model", model=model_name(model)), 17, "", INK),
        (t("svg.c.time", run=es(RUN_S, 0), tmax=es(view.tmax, 0)), 14, "", STEEL),
    ]
    y, head = 40.0, []
    for line, size, cls, color in rows:
        head.append(text(GX, y, line, size, cls=cls, color=color))
        y += size * 1.5
    body = (
        _bottle(view, paused)
        + "".join(head)
        + text(GX, 180, t("svg.c.clock"), 17)
        + _clock(_hours(view), GX + 175, 162, 50, paused, INK)
        + text(GX + 230, 180, "h", 17)
        + text(GX, 220, t("svg.c.recovery", model=model_name(model)), 17)
        + _clock([es(r, 1) for r in rec], GX + 235, 202, 70, paused, GAUGE)
        + text(GX + 305, 220, "%", 17)
        + _gauge(view, paused)
        + text(GX, GY + GH + 48, t("svg.c.measured"), 12, color=MEASURED)
        + _legend(view)
    )
    return svg(W, H, body, paused, t("svg.c.label"), motion_css(view))
