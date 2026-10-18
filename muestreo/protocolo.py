"""Protocolo de preparación de muestras: etapas de reducción de tamaño y división, con la varianza
de Gy de cada división y la acumulada.

Cada etapa es «reducir el tamaño y dividir hasta una masa»: la división toma MS de una masa de
entrada ML al tamaño dN de esa etapa y mete una varianza σ² = IHL(dN)·(1/MS − 1/ML). El error
total del protocolo es la suma de las varianzas relativas (errores independientes; Gy, Pitard).

El dN de cada etapa sale de la ESPECIFICACIÓN (p. ej. «70 % bajo 2 mm» + una forma Rosin-Rammler
con pendiente m supuesta) o se da directo (como en la Tabla VIII de Minnitt 2017).

Códigos de preparación públicos de ALS (alsglobal.com, sample-preparation/rock-preparation),
sin afiliación: PREP-31 = chancar al 70 % bajo 2 mm, dividir 250 g con riffle y pulverizar al 85 %
bajo 75 µm; PREP-31B = igual con 1 kg. La alícuota de fuego es de 30 g (Au-AA23) o 50 g (Au-AA24).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .granulometria import d95_from_um
from .gy import GyError, Mineral, sample_mass

ALIQUOTS = {"AA23": 30.0, "AA24": 50.0}  # g de la alícuota de fuego


@dataclass(frozen=True)
class SizeSpec:
    """«pct % bajo size_um µm»."""

    pct: float
    size_um: float


@dataclass(frozen=True)
class Stage:
    name: str
    mass_out_g: float
    spec: SizeSpec | None = None
    d_n_cm: float | None = None  # dN dado directo (si no hay especificación)

    def d_n(self, m: float) -> float:
        """dN (cm) de la etapa: el d95 de su especificación con pendiente `m`, o el dado."""
        if self.d_n_cm is not None:
            return self.d_n_cm
        if self.spec is None:
            raise GyError(f"la etapa «{self.name}» no tiene tamaño ni especificación")
        return d95_from_um(self.spec.pct, self.spec.size_um, m)


@dataclass(frozen=True)
class Protocol:
    name: str
    lot_g: float
    d_n0_cm: float  # tamaño del material recibido: solo para dibujar el primer tramo
    stages: tuple[Stage, ...]
    source: str = ""


@dataclass(frozen=True)
class StageResult:
    name: str
    d_n_cm: float
    mass_in_g: float
    mass_out_g: float
    variance: float
    cum_variance: float
    share: float  # parte de la varianza total

    @property
    def rsd(self) -> float:
        return math.sqrt(self.variance)

    @property
    def cum_rsd(self) -> float:
        return math.sqrt(self.cum_variance)


@dataclass(frozen=True)
class ProtocolResult:
    protocol: Protocol
    stages: tuple[StageResult, ...]
    lot_correction: bool

    @property
    def variance(self) -> float:
        return self.stages[-1].cum_variance

    @property
    def rsd(self) -> float:
        return math.sqrt(self.variance)


def evaluate(protocol: Protocol, mineral: Mineral, m: float = 1.0,
             lot_correction: bool = True) -> ProtocolResult:  # fmt: skip
    """Varianza de Gy de cada división y acumulada. Con `lot_correction` False se usa 1/MS
    (lote infinito), como en la Tabla VIII de Minnitt 2017."""
    if not protocol.stages:
        raise GyError("el protocolo necesita al menos una etapa")
    mass_in, cumulative, parts = protocol.lot_g, 0.0, []
    for stage in protocol.stages:
        if not 0 < stage.mass_out_g < mass_in:
            raise GyError(
                f"«{stage.name}»: la masa dividida ({stage.mass_out_g:g} g) debe ser menor que la "
                f"de entrada ({mass_in:g} g)"
            )
        d_n = stage.d_n(m)
        variance = mineral.variance(d_n, stage.mass_out_g, mass_in if lot_correction else None)
        cumulative += variance
        parts.append((stage, d_n, mass_in, variance, cumulative))
        mass_in = stage.mass_out_g
    results = tuple(
        StageResult(s.name, d, mi, s.mass_out_g, v, c, v / cumulative if cumulative else 0.0)
        for s, d, mi, v, c in parts
    )
    return ProtocolResult(protocol, results, lot_correction)


def sensibilidad_a_m(
    protocol: Protocol, mineral: Mineral, slopes: tuple[float, ...], lot_correction: bool = True
) -> list[tuple[float, float, tuple[float, ...]]]:
    """(m, error relativo total, dN de cada etapa) para varias pendientes Rosin-Rammler."""
    out = []
    for m in slopes:
        result = evaluate(protocol, mineral, m, lot_correction)
        out.append((m, result.rsd, tuple(s.d_n_cm for s in result.stages)))
    return out


# ------------------------------------------------------------------ rutas del nomograma
def path_points(result: ProtocolResult, d_n0_cm: float | None = None
                ) -> list[tuple[str, float, float]]:  # fmt: skip
    """(rótulo, dN en cm, masa en g) de la ruta: reducción de tamaño = tramo horizontal (masa
    constante) y división = tramo vertical (tamaño constante)."""
    protocol = result.protocol
    d_n = protocol.d_n0_cm if d_n0_cm is None else d_n0_cm
    points = [("Inicio", d_n, protocol.lot_g)]
    for stage in result.stages:
        points.append((f"{stage.name}: reducir a dN", stage.d_n_cm, stage.mass_in_g))
        points.append((f"{stage.name}: dividir", stage.d_n_cm, stage.mass_out_g))
    return points


def safety_mass(mineral: Mineral, d_n_cm: float, rel_variance: float) -> float:
    """Masa mínima (g) para no pasar de esa varianza a ese tamaño: la recta de seguridad del
    nomograma (lote infinito)."""
    return sample_mass(mineral.ih_l(d_n_cm), rel_variance)


# ------------------------------------------------------------------ protocolos precargados
def prep_31(lot_g: float, aliquot_g: float, d_n0_cm: float = 5.0) -> Protocol:
    """PREP-31 (ALS, público): 70 % bajo 2 mm, riffle 250 g, 85 % bajo 75 µm y alícuota."""
    return Protocol(
        "PREP-31", lot_g, d_n0_cm,
        (Stage("Chancado y riffle", 250.0, SizeSpec(70.0, 2000.0)),
         Stage("Pulverizado y alícuota de fuego", aliquot_g, SizeSpec(85.0, 75.0))),
        "códigos públicos de ALS (alsglobal.com); sin afiliación",
    )  # fmt: skip


def prep_31b(lot_g: float, aliquot_g: float, d_n0_cm: float = 5.0) -> Protocol:
    """PREP-31B (ALS, público): igual que PREP-31 pero con 1 kg de pulpa."""
    return Protocol(
        "PREP-31B", lot_g, d_n0_cm,
        (Stage("Chancado y riffle", 1000.0, SizeSpec(70.0, 2000.0)),
         Stage("Pulverizado y alícuota de fuego", aliquot_g, SizeSpec(85.0, 75.0))),
        "códigos públicos de ALS (alsglobal.com); sin afiliación",
    )  # fmt: skip


# Minnitt (2017), J. SAIMM 117(2), Tabla VII: 5 000 000 t/a, 4 629 629,6 g por turno de 8 h; Tabla
# VIII: cada división de masa (g) y tamaño dN (cm) que lleva ese turno a una alícuota de ~50 g.
MINNITT_LOT_G = 4_629_629.6
MINNITT_DN0_CM = 60.0
MINNITT_STAGES = (
    Stage("Chancado a 20 cm y división", 462_963.0, d_n_cm=20.0),
    Stage("Chancado a 1 cm y división", 23_148.1, d_n_cm=1.0),
    Stage("Pulverizado a 0,03 cm y división", 694.4, d_n_cm=0.03),
    Stage("Pulverizado a 0,003 cm y alícuota", 48.61, d_n_cm=0.003),
)


def minnitt_2017() -> Protocol:
    return Protocol("Minnitt 2017, Tabla VIII", MINNITT_LOT_G, MINNITT_DN0_CM, MINNITT_STAGES,
                    "Minnitt (2017), J. SAIMM 117(2), Tablas VII y VIII")  # fmt: skip


PRESETS = ("PREP-31", "PREP-31B", "Minnitt 2017, Tabla VIII")


def preset(name: str, lot_g: float, aliquot_g: float, d_n0_cm: float = 5.0) -> Protocol:
    if name == PRESETS[0]:
        return prep_31(lot_g, aliquot_g, d_n0_cm)
    if name == PRESETS[1]:
        return prep_31b(lot_g, aliquot_g, d_n0_cm)
    if name == PRESETS[2]:
        return minnitt_2017()
    raise GyError(f"protocolo desconocido: {name!r}; use uno de {PRESETS}")
