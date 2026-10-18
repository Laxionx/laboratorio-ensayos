"""Geometría del crisol de ensayo: un tronco de cono (ancho arriba, angosto al fondo) y el nivel
que alcanza cada capa (plomo líquido al fondo, escoria encima).

Dimensiones ILUSTRATIVAS de un crisol de arcilla de mufla de «20 g»: radio interior de 1,8 cm
al fondo y de 3,45 cm arriba, 8,5 cm de alto. De Bugbee (1922, Tabla IV y texto) salen dos cosas:
la capacidad del crisol de 20 g (190 cm³, Denver y Battersea; con él se trata 1 assay-ton) y que
los crisoles de mufla «no pasan de 4 pulgadas de alto» (10,2 cm). El radio y la altura son una
elección nuestra que da esa capacidad; no son de un fabricante.

Regla de llenado (Bugbee 1922, notas del ensayo de crisol): «el crisol nunca debe estar a más de
dos tercios cuando la carga está toda dentro». Aquí se aplica al VOLUMEN, no a la altura.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .fusion_avisos import Warning

FILL_LIMIT = 2.0 / 3.0  # Bugbee 1922: nunca más de dos tercios llenos con la carga toda dentro
DRY_BULK_DENSITY = 1.5  # g/cm³ de la carga en polvo; SUPUESTO ilustrativo (Bugbee no lo da)


@dataclass(frozen=True)
class Crucible:
    """Tronco de cono de revolución: radios interiores `r_bottom` y `r_top` y alto `height` (cm)."""

    r_bottom: float
    r_top: float
    height: float

    @property
    def slope(self) -> float:
        """Cuánto crece el radio por cm de altura."""
        return (self.r_top - self.r_bottom) / self.height

    def radius_at(self, z: float) -> float:
        """Radio interior (cm) a la altura `z` (cm) sobre el fondo."""
        return self.r_bottom + self.slope * z

    def volume_below(self, z: float) -> float:
        """Volumen (cm³) entre el fondo y la altura `z`: ∫ π r(z)² dz, en forma cerrada."""
        z = min(max(z, 0.0), self.height)
        k = self.slope
        return math.pi * (self.r_bottom**2 * z + self.r_bottom * k * z**2 + k**2 * z**3 / 3.0)

    @property
    def capacity_cm3(self) -> float:
        return self.volume_below(self.height)

    @property
    def fill_limit_cm3(self) -> float:
        return FILL_LIMIT * self.capacity_cm3

    def level_for(self, volume: float) -> float:
        """Altura (cm) a la que el volumen acumulado desde el fondo vale `volume`; se corta en el
        borde. Inversa de `volume_below`: V = π/(3k)·((r0 + k z)³ − r0³)."""
        if volume <= 0:
            return 0.0
        if volume >= self.capacity_cm3:
            return self.height
        k = self.slope
        if abs(k) < 1e-12:
            return volume / (math.pi * self.r_bottom**2)
        cubed = 3.0 * k * volume / math.pi + self.r_bottom**3
        return (cubed ** (1.0 / 3.0) - self.r_bottom) / k


CRUCIBLE = Crucible(r_bottom=1.8, r_top=3.45, height=8.5)  # ilustrativo, capacidad ≈ 190 cm³


@dataclass(frozen=True)
class Layers:
    """Niveles (cm sobre el fondo): el plomo líquido llega a `lead_top`, la escoria a `slag_top`."""

    lead_top: float
    slag_top: float
    overflows: bool  # lo fundido pasa del borde del crisol


def layers(lead_cm3: float, slag_cm3: float, crucible: Crucible = CRUCIBLE) -> Layers:
    """Plomo líquido en un charco al fondo del cono y la escoria encima, llenando el cono."""
    lead_top = crucible.level_for(lead_cm3)
    slag_top = crucible.level_for(lead_cm3 + slag_cm3)
    return Layers(lead_top, slag_top, lead_cm3 + slag_cm3 > crucible.capacity_cm3)


def crucible_warnings(
    dry_charge_g: float, lead_cm3: float, slag_cm3: float, crucible: Crucible = CRUCIBLE
) -> list[Warning]:
    """Avisos si la carga en polvo o lo fundido pasan de la capacidad o de los 2/3 de Bugbee."""
    out: list[Warning] = []
    cap, limit = crucible.capacity_cm3, crucible.fill_limit_cm3
    dry_cm3 = dry_charge_g / DRY_BULK_DENSITY
    for kind, what, vol, extra in (
        ("dry", "La carga en polvo", dry_cm3, f"{dry_charge_g:.0f} g a {DRY_BULK_DENSITY:g} g/cm³"),
        ("melt", "Lo fundido (plomo y escoria)", lead_cm3 + slag_cm3, "plomo líquido más escoria"),
    ):
        args = (("vol", vol), ("grams", dry_charge_g), ("density", DRY_BULK_DENSITY),
                ("cap", cap), ("two_thirds", limit))  # fmt: skip
        if vol > cap:
            out.append(Warning(
                "riesgo",
                f"{what} ocupa {vol:.0f} cm³ ({extra}): pasa de la capacidad del crisol "
                f"({cap:.0f} cm³); se derrama. Usa un crisol mayor o una carga menor.",
                "capacidad: Bugbee 1922, Tabla IV (20 g = 190 cm³); densidad en polvo: supuesto",
                f"{kind}_over_capacity", args,
            ))  # fmt: skip
        elif vol > limit:
            out.append(Warning(
                "aviso",
                f"{what} ocupa {vol:.0f} cm³ ({extra}): pasa de los 2/3 del crisol "
                f"({limit:.0f} de {cap:.0f} cm³).",
                "Bugbee 1922: «nunca más de dos tercios llenos» (el 2/3 es del volumen)",
                f"{kind}_over_two_thirds", args,
            ))  # fmt: skip
    return out
