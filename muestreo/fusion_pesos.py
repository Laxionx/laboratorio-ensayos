"""Las cifras de Bugbee (1922) con los pesos atómicos actuales y con los «de Bugbee».

Bugbee calculó a mano, con pesos atómicos redondeados que no declara (usa 207 para el Pb, 56 para
el Fe y 32 para el S en sus cuentas: 207/56 = 3,696 y él imprime 3,70; 7·207/120 = 12,075 y él
imprime 12,07, o sea que truncó). El juego `BUGBEE_WEIGHTS` se INFIERE de sus propias cifras: es
el que mejor reproduce las de sus tablas entre valores redondeados de uso común en 1922, buscado
con las cifras a la vista (así que su ajuste está a favor de Bugbee, y se declara). La app calcula
SIEMPRE con los pesos actuales (`quimica.ATOMIC_WEIGHTS`); este módulo solo explica la diferencia.

Veredicto por cifra:
- «cuadra»: con pesos actuales, al redondeo publicado (media unidad del último dígito);
- «cuadra con los pesos de Bugbee»: no con los actuales, pero sí con los de Bugbee;
- «truncamiento de Bugbee»: con sus pesos queda a menos de una unidad del último dígito y,
  truncando (no redondeando), sale su cifra;
- «no cuadra»: ninguna de las tres, con su diferencia.
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable
from dataclasses import dataclass

from . import fusion as fu
from .quimica import ATOMIC_WEIGHTS
from .validacion import Check, decimals_of, matches_rounding

BUGBEE_WEIGHTS = {
    "H": 1.0,
    "B": 11.0,
    "C": 12.0,
    "N": 14.0,
    "O": 16.0,
    "Na": 23.0,
    "Mg": 24.32,
    "Si": 28.3,
    "S": 32.06,
    "K": 39.1,
    "Ca": 40.1,
    "Mn": 55.0,
    "Fe": 56.0,
    "Cu": 64.0,
    "Zn": 65.4,
    "As": 75.0,
    "Sb": 120.2,
    "Pb": 207.1,
}

CUADRA = "cuadra"
CON_PESOS = "cuadra con los pesos de Bugbee"
TRUNCA = "truncamiento de Bugbee"
NO_CUADRA = "no cuadra"
VERDICTS = (CUADRA, CON_PESOS, TRUNCA, NO_CUADRA)


@dataclass(frozen=True)
class FusionCheck(Check):
    """Una comparación: `calculated` usa pesos actuales; `bugbee` usa los de Bugbee (None si la
    cifra no depende de pesos atómicos)."""

    close: bool = False  # con pesos actuales, a menos de una unidad del último dígito
    bugbee: float | None = None
    verdict: str = ""

    @property
    def fit(self) -> str:
        return self.verdict or (CUADRA if self.ok else NO_CUADRA)

    @property
    def difference_bugbee(self) -> float | None:
        return None if self.bugbee is None else self.bugbee - self.published


def truncated_equals(value: float, printed: str) -> bool:
    """¿Truncar `value` (no redondearlo) a los decimales impresos da la cifra publicada?"""
    d = decimals_of(printed)
    return abs(math.floor(value * 10**d + 1e-9) / 10**d - float(printed)) < 10.0 ** (-d) * 1e-6


def verdict(printed: str, current: float, bugbee: float | None) -> str:
    if matches_rounding(current, printed):
        return CUADRA
    if bugbee is None:
        return NO_CUADRA
    if matches_rounding(bugbee, printed):
        return CON_PESOS
    unit = 10.0 ** (-decimals_of(printed))
    if abs(bugbee - float(printed)) < unit and truncated_equals(bugbee, printed):
        return TRUNCA
    return NO_CUADRA


def make_check(
    source: str,
    item: str,
    printed: str,
    current: float,
    unit: str,
    note: str = "",
    bugbee: float | None = None,
) -> FusionCheck:
    published = float(printed)
    unit_size = 10.0 ** (-decimals_of(printed))
    return FusionCheck(
        source,
        item,
        published,
        current,
        unit,
        matches_rounding(current, printed),
        note,
        abs(current - published) <= unit_size * (1 + 1e-9),
        bugbee,
        verdict(printed, current, bugbee),
    )


class Stoich:
    """Estequiometría de las cifras de Bugbee con un juego de pesos atómicos dado."""

    def __init__(self, weights: dict[str, float]) -> None:
        self.w = weights
        self.pb = weights["Pb"]

    def mm(self, formula: str) -> float:
        return sum(
            self.w[e] * (int(n) if n else 1) for e, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula)
        )

    def rp(self, spec: fu.MineralSpec, sulfur: str) -> float:
        n = fu.pb_reduced_per_mol(spec.s_atoms, spec.s_state, spec.extra_e, sulfur)
        return n * self.pb / self.mm(spec.formula)

    def silica_per_base(self, base: str, degree: float = 2.0) -> float:
        moles_o = {"NaHCO3": 0.5}.get(base, 1.0)
        return moles_o * degree / 2.0 * self.mm("SiO2") / self.mm(base)

    def borax_per_base(self, base: str) -> float:
        return self.silica_per_base(base) / fu.BORAX_SILICA_EQUIVALENT

    def design(
        self,
        minerals: dict[str, float],
        soda_g: float,
        litharge_slag_g: float,
        pure_split: bool = False,
        flour_rp: float = 12.0,
    ) -> dict[str, float]:
        """Los ejemplos de Bugbee (botón de 28 g, bi-silicato, 1 assay-ton) con estos pesos."""
        at, pbo = fu.AT_G, self.mm("PbO")
        grams = {k: at * v / 100.0 for k, v in minerals.items()}
        quartz = grams.get("cuarzo", 0.0) / self.mm("SiO2")
        base_mol = grams.get("calcita", 0.0) / self.mm("CaCO3")
        litharge = 28.0 * pbo / self.pb
        flour = 28.0 / flour_rp
        if pure_split:  # sílice pura: toda la sílice se reparte 3/5 con soda y 2/5 con PbO
            total = quartz
            return {
                "soda": fu.SODA_SHARE * total * self.mm("Na2CO3"),
                "litharge slag": (1 - fu.SODA_SHARE) * total * pbo,
                "flour": flour,
            }
        slag_pbo = litharge_slag_g
        need = (
            base_mol * self.mm("SiO2")
            + soda_g / self.mm("Na2CO3") * self.mm("SiO2")
            + slag_pbo / pbo * self.mm("SiO2")
            - quartz * self.mm("SiO2")
        )
        borax = max(5.0, (need / 3.0) / fu.BORAX_SILICA_EQUIVALENT)
        return {
            "borax": borax,
            "silica": need - borax * fu.BORAX_SILICA_EQUIVALENT,
            "litharge": litharge + slag_pbo,
        }


CURRENT, BUGBEE = Stoich(ATOMIC_WEIGHTS), Stoich(BUGBEE_WEIGHTS)


def dual(
    source: str, item: str, printed: str, unit: str, fn: Callable[[Stoich], float], note: str = ""
) -> FusionCheck:
    """Una cifra que depende de los pesos atómicos: con los actuales y con los de Bugbee."""
    return make_check(source, item, printed, fn(CURRENT), unit, note, fn(BUGBEE))
