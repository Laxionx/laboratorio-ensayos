"""Esquema animado del ensayo de cianuración: un vaso de precipitados en corte con un agitador
(eje y paletas) y un indicador de recuperación que avanza siguiendo el modelo elegido en un tiempo
COMPRIMIDO (todo el ensayo en `RUN_S` s), junto con los puntos medidos.

Lo que sale del cálculo: la recuperación del modelo en cada instante (la curva del modelo,
muestreada en `FRAMES` instantes parejos), el reloj del ensayo y los 7 puntos medidos. Lo
ilustrativo, y así se rotula: el vaso en pantalla, su nivel de pulpa y el giro del agitador (el
artículo no informa la velocidad de agitación), y la compresión del tiempo.
"""

from __future__ import annotations

import textwrap

from cian_calculo import CURVA_PUNTOS, CianView, model_name
from dibujo import INK, STEEL, es, svg, text
from i18n import t

W, H = 940, 440
CX = 200.0  # eje del agitador
GX, GY, GW, GH = 400.0, 262.0, 480.0, 26.0  # el indicador (barra de recuperación)
RUN_S, HOLD_S = 12.0, 2.0  # el ensayo completo en 12 s y 2 s de pausa antes de repetir
FRAMES = CURVA_PUNTOS  # instantes del indicador (96 intervalos)
ROW_PX, WINDOW_PX, BASE_PX = 40, 28, 22  # paso, alto de la ventana y línea base de cada dígito
PULP, GAUGE, MEASURED = "#B7791F", "#1F7A6F", "#C0462B"
PULP_MIN, PULP_SPAN = 0.25, 0.60  # opacidad de la pulpa: 0,25 + 0,60·R/100 (ilustrativo)
STIR_PERIOD_S = 1.6  # ilustrativo: el artículo no informa la velocidad de agitación
LEVEL_Y, BOTTOM_Y = 200.0, 346.0  # nivel de pulpa (ilustrativo) y fondo del vaso
MARK_GAP = 36.0  # separación mínima (px) entre los rótulos de las marcas medidas


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
    count = [f"transform:translateY({-i * ROW_PX}px)" for i in range(len(rec))]
    total = RUN_S + HOLD_S
    return (
        "@keyframes lb-stir{0%,100%{transform:scaleX(1)}50%{transform:scaleX(-1)}}"
        + _keyframes("lb-bar", bar)
        + _keyframes("lb-pulp", pulp)
        + _keyframes("lb-count", count)
        + ".lb-stir{transform-box:view-box;animation:lb-stir linear infinite}"
        + f".lb-bar{{transform-box:fill-box;transform-origin:0 50%;"
        f"animation:lb-bar {total:g}s linear infinite}}"
        + f".lb-pulp{{animation:lb-pulp {total:g}s linear infinite}}"
        + f".lb-count{{animation:lb-count {total:g}s steps(1,end) infinite}}"
    )


def _beaker(view: CianView, paused: bool) -> str:
    """El vaso de precipitados en corte (ilustrativo), su pulpa (opacidad según la recuperación)
    y el agitador: un eje y dos paletas que giran vistas de canto (escala horizontal que pasa por
    cero y se invierte)."""
    final = view.animada(view.params.model, FRAMES - 1)[-1]
    left, right, top = CX - 110.0, CX + 110.0, 96.0
    stir = (
        "" if paused else f' style="transform-origin:{CX}px 0;animation-duration:{STIR_PERIOD_S}s"'
    )
    pulp_style = (
        f' style="fill-opacity:{PULP_MIN + PULP_SPAN * final / 100.0:.4f}"' if paused else ""
    )
    wall = f'fill="none" stroke="{STEEL}" stroke-width="8" stroke-linejoin="round"'
    return (
        f'<rect class="lb-pulp" x="{left + 4}" y="{LEVEL_Y}" width="{right - left - 8}" '
        f'height="{BOTTOM_Y - LEVEL_Y - 2}" fill="{PULP}"{pulp_style}/>'
        f'<line x1="{left + 4}" y1="{LEVEL_Y}" x2="{right - 4}" y2="{LEVEL_Y}" stroke="{PULP}" '
        f'stroke-width="2"/>'
        f'<path d="M {left - 8} {top - 8} L {left} {top} L {left} {BOTTOM_Y - 10} '
        f"Q {left} {BOTTOM_Y} {left + 10} {BOTTOM_Y} L {right - 10} {BOTTOM_Y} "
        f'Q {right} {BOTTOM_Y} {right} {BOTTOM_Y - 10} L {right} {top} L {right + 8} {top - 8}" '
        f"{wall}/>"
        f'<rect x="{CX - 4}" y="62" width="8" height="{BOTTOM_Y - 24 - 62}" fill="{STEEL}"/>'
        f'<rect x="{CX - 26}" y="46" width="52" height="18" rx="4" fill="{STEEL}"/>'
        f'<g class="lb-stir"{stir}>'
        f'<rect x="{CX - 52}" y="{BOTTOM_Y - 40}" width="104" height="12" rx="3" fill="{STEEL}"/>'
        f'<rect x="{CX - 52}" y="{BOTTOM_Y - 62}" width="12" height="34" rx="3" fill="{STEEL}"/>'
        f'<rect x="{CX + 40}" y="{BOTTOM_Y - 62}" width="12" height="34" rx="3" fill="{STEEL}"/>'
        f"</g>"
    )


def _clock(values: list[str], x: float, y: float, width: float, paused: bool, color: str) -> str:
    """Un reloj de números: una columna de textos (uno cada `ROW_PX`) tras una ventana de
    `WINDOW_PX` que muestra uno solo; `y` es la línea base del dígito visible. El paso es mucho
    mayor que el alto del texto, así que no asoma nada de los vecinos."""
    top = y - BASE_PX
    final = -(len(values) - 1) * ROW_PX
    style = f' style="transform:translateY({final}px)"' if paused else ""
    cells = "".join(
        text(0, ROW_PX * i + BASE_PX, v, 17, color=color, style="font-weight:700")
        for i, v in enumerate(values)
    )
    cid = f"lb-clip-{int(x)}-{int(y)}"
    return (
        f'<defs><clipPath id="{cid}"><rect x="{x:.1f}" y="{top:.1f}" width="{width:.1f}" '
        f'height="{WINDOW_PX}"/></clipPath></defs>'
        f'<g clip-path="url(#{cid})"><g transform="translate({x:.1f} {top:.1f})">'
        f'<g class="lb-count"{style}>{cells}</g></g></g>'
    )


def mark_layout(view: CianView) -> list[tuple[float, float, float]]:
    """(tiempo, x de la marca, x de su rótulo) de cada punto medido. Los rótulos se reparten a
    al menos `MARK_GAP` px entre sí (se enlazan con su marca con una línea) para no encimarse."""
    pts = sorted(
        (GX + GW * min(max(r, 0.0), 100.0) / 100.0, tt)
        for tt, r in zip(view.balance.t_h, view.balance.recuperacion_pct, strict=True)
    )
    xs = [x for x, _ in pts]
    lab = list(xs)
    for i in range(1, len(lab)):
        lab[i] = max(lab[i], lab[i - 1] + MARK_GAP)
    limit = GX + GW + 40.0
    lab[-1] = min(lab[-1], limit)
    for i in range(len(lab) - 2, -1, -1):
        lab[i] = min(lab[i], lab[i + 1] - MARK_GAP)
    return [(tt, x, lx) for (x, tt), lx in zip(pts, lab, strict=True)]


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
    for tt, x, lx in mark_layout(view):
        label = f"{es(tt, 0 if float(tt).is_integer() else 1)} h"
        out.append(
            f'<polyline points="{x:.1f},{GY} {x:.1f},{GY - 8} {lx:.1f},{GY - 24}" fill="none" '
            f'stroke="{MEASURED}" stroke-width="2"/>'
            + text(lx, GY - 28, label, 11, anchor="middle", color=MEASURED)
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


def beaker_svg(view: CianView, paused: bool = False) -> str:
    model = view.params.model
    rec = view.animada(model, FRAMES - 1)
    rows = [
        (t("svg.c.title"), 24, "t", INK),
        (t("svg.c.stir"), 14, "", STEEL),
        (t("svg.c.model", model=model_name(model)), 17, "", INK),
        (t("svg.c.time", run=es(RUN_S, 0), tmax=es(view.tmax, 0)), 14, "", STEEL),
    ]
    y, head = 40.0, []
    for line, size, cls, color in rows:
        head.append(text(GX, y, line, size, cls=cls, color=color))
        y += size * 1.5
    body = (
        _beaker(view, paused)
        + "".join(head)
        + text(GX, 180, t("svg.c.clock"), 17)
        + _clock(_hours(view), GX + 175, 180, 50, paused, INK)
        + text(GX + 230, 180, "h", 17)
        + text(GX, 220, t("svg.c.recovery", model=model_name(model)), 17)
        + _clock([es(r, 1) for r in rec], GX + 235, 220, 70, paused, GAUGE)
        + text(GX + 305, 220, "%", 17)
        + _gauge(view, paused)
        + text(GX, GY + GH + 48, t("svg.c.measured"), 12, color=MEASURED)
        + _legend(view)
    )
    return svg(W, H, body, paused, t("svg.c.label"), motion_css(view))
