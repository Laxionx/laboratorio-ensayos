"""Cálculo de lo que muestra la app, sin Streamlit: llama a `muestreo` y arma las vistas que
dibujan los gráficos. Todo lo que se ve sale de estos números."""

from __future__ import annotations

from dataclasses import dataclass

from muestreo import Mineral, evaluate
from muestreo.gy import GyError
from muestreo.oro import GoldSimulation, expected_particles, grain_mass_g, simulate
from muestreo.protocolo import (
    PRESETS,
    ProtocolResult,
    path_points,
    preset,
    safety_mass,
    sensibilidad_a_m,
)

# Mineral por defecto: el calibrado de Minnitt (2017), J. SAIMM 117(2), con su fuente.
MINERALS = (
    "Calibrado DSA (Minnitt 2017)",
    "Calibrado SFA (Minnitt 2017)",
    "Calibrado propio (K y α)",
    "Clásico (c·f·g·ℓ)",
)
DSA_K, DSA_ALPHA = 167.4, 1.123
SFA_K, SFA_ALPHA = 2539.0, 1.03
SOURCE_NOTE = (
    "K y α son los que Minnitt (2017) calibró para una mena de oro de Witwatersrand; no valen para "
    "otro mineral. Cada laboratorio debe calibrar los suyos (ensayo de heterogeneidad o árbol de "
    "muestreo)."
)
SLOPES = (0.5, 0.7, 1.0, 1.3, 1.6, 2.0, 2.5, 3.0)


@dataclass(frozen=True)
class MineralParams:
    form: str = MINERALS[0]
    k: float = DSA_K  # solo con «propio»
    alpha: float = DSA_ALPHA
    grade_gpt: float = 3.84  # ley de oro (Minnitt 2017, promedio de 32 ensayos)
    rho_m: float = 16.0  # amalgama oro-plata (Minnitt 2017)
    rho_g: float = 2.75
    d_lib_um: float = 82.0  # tamaño de liberación del oro, DSA (Minnitt 2017)
    f: float = 0.5
    g: float = 0.25
    b: float = 1.5

    def to_mineral(self) -> Mineral:
        if self.form == MINERALS[0]:
            return Mineral(MINERALS[0], k=DSA_K, alpha=DSA_ALPHA)
        if self.form == MINERALS[1]:
            return Mineral(MINERALS[1], k=SFA_K, alpha=SFA_ALPHA)
        if self.form == MINERALS[2]:
            return Mineral(MINERALS[2], k=self.k, alpha=self.alpha)
        if self.form == MINERALS[3]:
            return Mineral(MINERALS[3], a=self.grade_gpt * 1e-6, rho_m=self.rho_m,
                           rho_g=self.rho_g, f=self.f, g=self.g, d_lib=self.d_lib_um * 1e-4,
                           b=self.b)  # fmt: skip
        raise GyError(f"mineral desconocido: {self.form!r}")


@dataclass(frozen=True)
class ProtocolParams:
    preset: str = PRESETS[0]
    aliquot_g: float = 30.0
    lot_g: float = 3000.0  # supuesto: masa de la muestra recibida
    d_n0_cm: float = 5.0  # supuesto: solo dibuja el primer tramo horizontal
    m: float = 1.0  # supuesto: pendiente Rosin-Rammler
    safety_pct: float = 10.0
    lot_correction: bool = True


@dataclass(frozen=True)
class ProtocolView:
    params: ProtocolParams
    mineral: Mineral
    result: ProtocolResult
    path: tuple[tuple[str, float, float], ...]  # (rótulo, dN cm, masa g)
    sensitivity: tuple[tuple[float, float, tuple[float, ...]], ...]

    @property
    def safety_variance(self) -> float:
        return (self.params.safety_pct / 100.0) ** 2

    def safety_mass(self, d_n_cm: float) -> float:
        return safety_mass(self.mineral, d_n_cm, self.safety_variance)

    @property
    def meets_safety(self) -> bool:
        """¿Cada división queda sobre la línea de seguridad (error ≤ el elegido)?"""
        return all(s.variance <= self.safety_variance for s in self.result.stages)


def run_protocol(p: ProtocolParams, mp: MineralParams) -> ProtocolView:
    """Lanza GyError (ValueError) si los datos no sirven (masa, tamaño, pendiente...)."""
    mineral = mp.to_mineral()
    protocol = preset(p.preset, p.lot_g, p.aliquot_g, p.d_n0_cm)
    result = evaluate(protocol, mineral, p.m, p.lot_correction)
    sensitivity = tuple(sensibilidad_a_m(protocol, mineral, SLOPES, p.lot_correction))
    return ProtocolView(p, mineral, result, tuple(path_points(result)), sensitivity)


# ------------------------------------------------------------------ oro grueso
@dataclass(frozen=True)
class GoldParams:
    grain_um: float = 150.0
    shape: str = "esfera"


@dataclass(frozen=True)
class GoldView:
    params: GoldParams
    grade_gpt: float
    aliquot_g: float
    grain_g: float
    lam: float
    simulation: GoldSimulation


def run_gold(p: GoldParams, grade_gpt: float, aliquot_g: float) -> GoldView:
    grain = grain_mass_g(p.grain_um, p.shape)
    return GoldView(p, grade_gpt, aliquot_g, grain,
                    expected_particles(grade_gpt, aliquot_g, grain),
                    simulate(grade_gpt, aliquot_g, grain))  # fmt: skip
