"""Auxiliares del esquema animado: paleta «cuaderno de planta», marco SVG, CSS de movimiento y
entrega como imagen (mismos patrones que las otras apps del mismo autor).

El esquema se arma solo con números del cálculo y textos fijos: nada que escriba el visitante
entra al dibujo. Se muestra como imagen (<img>, data URL), así que el navegador no ejecuta nada
de él. Con «reducir movimiento» en el sistema se ve la versión quieta.
"""

from __future__ import annotations

import base64
from html import escape

INK, PAPER, STEEL, STEEL_LIGHT = "#1F2A30", "#F5F1E8", "#4F5F69", "#A7B3BA"
BRONZE_SVG = "#B7791F"
SANS = "Segoe UI, Helvetica, Arial, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"
R = ".lb-svg "  # todo el CSS del esquema queda dentro de su raíz
SCHEME_NOTE = "esquema ilustrativo: las cantidades de granos sí son del cálculo"


def es(x: float, decimals: int = 1) -> str:
    """Número con coma decimal y espacio de miles."""
    return f"{x:,.{decimals}f}".replace(",", " ").replace(".", ",")


def svg(width: int, height: int, body: str, paused: bool, label: str, motion_css: str = "") -> str:
    """Marco SVG. `motion_css` (keyframes y reglas) solo se incluye si se mueve."""
    base = (
        f"{R}text{{font-family:{SANS};fill:{INK}}} {R}.lb-t{{font-family:{SERIF};font-weight:700}}"
    )
    reduce = f"@media (prefers-reduced-motion: reduce){{{R}*{{animation:none!important}}}}"
    css = base if paused else base + motion_css + reduce
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="lb-svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{escape(label)}">'
        f"<style>{css}</style>"
        f'<rect width="{width}" height="{height}" fill="{PAPER}"/>{body}</svg>'
    )


# Una regla de la página elige qué versión se ve: la quieta si el sistema pide reducir movimiento.
MOTION_CSS = (
    "<style>.lb-still{display:none}"
    "@media (prefers-reduced-motion: reduce){.lb-anim{display:none}.lb-still{display:block}}"
    "</style>"
)


def as_images(animated: str, still: str, alt: str) -> str:
    """Las dos versiones del esquema como <img> (data URL). Si la animación está apagada,
    `animated` ya es la versión quieta."""

    def tag(source: str, cls: str) -> str:
        data = base64.b64encode(source.encode("utf-8")).decode("ascii")
        return (
            f'<img class="{cls}" alt="{escape(alt)}" style="width:100%;height:auto" '
            f'src="data:image/svg+xml;base64,{data}">'
        )

    if animated == still:
        return tag(still, "lb-plain")
    return tag(animated, "lb-anim") + tag(still, "lb-still")


def text(x: float, y: float, s: str, size: int = 13, anchor: str = "start", cls: str = "",
         color: str = INK, extra: str = "", style: str = "") -> str:  # fmt: skip
    c = ' class="' + " ".join(f"lb-{x}" for x in cls.split()) + '"' if cls else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
        f'style="fill:{color};{style}"{c}{extra}>{escape(s)}</text>'
    )


RISE_CSS = (
    "@keyframes lb-rise{from{transform:translateY(0)}to{transform:translateY(calc(-1*var(--d)))}}"
    f"{R}.lb-rise{{animation:lb-rise linear infinite}}"
)


def rise(x: float, y: float, dist: float, duration: float, phase: float, inner: str,
         paused: bool) -> str:  # fmt: skip
    """Grupo que sube `dist` px desde (x, y) (baja si `dist` es negativo) y se repite cada
    `duration` s; `phase` (0 a 1) es en qué punto del ciclo va. Quieto, queda congelado ahí."""
    if paused:
        return f'<g transform="translate({x:.1f} {y - phase * dist:.1f})">{inner}</g>'
    style = (
        f"--d:{dist:.1f}px;animation-duration:{duration:.4f}s;"
        f"animation-delay:-{phase * duration:.4f}s"
    )
    return (
        f'<g transform="translate({x:.1f} {y:.1f})">'
        f'<g class="lb-rise" style="{style}">{inner}</g></g>'
    )
