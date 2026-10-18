"""Oro grueso: cuántos granos de oro caen en la alícuota de ensayo al fuego y qué error eso mete.

Si el oro viene en granos de masa m_p, la alícuota de masa MS con ley a contiene en promedio
λ = a·MS/m_p granos. El número de granos que cae en cada alícuota es Poisson(λ): con λ chico casi
todos los ensayos dan menos que la ley real (o cero) y unos pocos dan muy alto, así que la
MEDIANA queda bajo la ley real. Criterio de Clifton, Hunter, Swanson y Phillips (1969, USGS
Professional Paper 625-C): para una precisión de unos ±50 % al 95 % se necesitan unas 20
partículas por muestra; con menos conviene el screen fire assay (pesar y ensayar entero el grueso
retenido en una malla fina y el fino por duplicado).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.stats import chi2, poisson

from .gy import AU_DENSITY, GyError

PARTICLES_CRITERION = 20  # Clifton et al. 1969
Z95 = 1.959964  # normal, 95 % a dos colas
SHAPES = {"esfera": math.pi / 6.0, "cubo": 1.0}  # volumen = factor·d³
SEED = 2017  # semilla fija de la simulación
TRIALS = 1000
SFA_SCREEN_UM = 100.0  # screen fire assay: se tamiza a 100 µm
SFA_MASS_G = 1000.0  # ~1 kg


def grain_mass_g(d_um: float, shape: str = "esfera", density: float = AU_DENSITY) -> float:
    """Masa (g) de un grano de oro de diámetro `d_um` µm: ρ·factor·d³ (esfera o cubo)."""
    if shape not in SHAPES:
        raise GyError(f"forma desconocida {shape!r}; use una de {tuple(SHAPES)}")
    if not (math.isfinite(d_um) and d_um > 0 and density > 0):
        raise GyError("el tamaño del grano y la densidad deben ser positivos")
    return density * SHAPES[shape] * (d_um * 1e-4) ** 3


def expected_particles(grade_gpt: float, aliquot_g: float, particle_g: float) -> float:
    """λ = ley (g/t) × 1e-6 × masa de la alícuota ÷ masa del grano."""
    if not (grade_gpt > 0 and aliquot_g > 0 and particle_g > 0):
        raise GyError("la ley, la alícuota y la masa del grano deben ser positivas")
    return grade_gpt * 1e-6 * aliquot_g / particle_g


def mass_for_particles(grade_gpt: float, particle_g: float,
                       particles: float = PARTICLES_CRITERION) -> float:  # fmt: skip
    """Masa de muestra (g) que contiene en promedio esa cantidad de granos."""
    if not (grade_gpt > 0 and particle_g > 0 and particles > 0):
        raise GyError("la ley, la masa del grano y las partículas deben ser positivas")
    return particles * particle_g / (grade_gpt * 1e-6)


@dataclass(frozen=True)
class GoldSimulation:
    """Ensayos repetidos de la misma alícuota: granos por ensayo y ley que daría cada uno."""

    lam: float
    true_grade_gpt: float
    counts: np.ndarray
    grades_gpt: np.ndarray

    @property
    def median_gpt(self) -> float:
        return float(np.median(self.grades_gpt))

    @property
    def mean_gpt(self) -> float:
        return float(self.grades_gpt.mean())

    @property
    def share_zero(self) -> float:
        return float((self.counts == 0).mean())

    def share_above(self, factor: float) -> float:
        """Fracción de ensayos que dan más de `factor` veces la ley real."""
        return float((self.grades_gpt > factor * self.true_grade_gpt).mean())


def simulate(grade_gpt: float, aliquot_g: float, particle_g: float, trials: int = TRIALS,
             seed: int = SEED) -> GoldSimulation:  # fmt: skip
    """`trials` ensayos: granos ~ Poisson(λ) y ley = granos × m_p ÷ alícuota."""
    lam = expected_particles(grade_gpt, aliquot_g, particle_g)
    counts = np.random.default_rng(seed).poisson(lam, trials)
    grades = counts * particle_g / aliquot_g * 1e6
    return GoldSimulation(lam, grade_gpt, counts, grades)


def poisson_p0(lam: float) -> float:
    """Probabilidad de que la alícuota no lleve ningún grano."""
    return math.exp(-lam)


def poisson_median_particles(lam: float) -> float:
    return float(poisson.ppf(0.5, lam))


def recommend_screen_fire_assay(lam: float) -> bool:
    """Conviene el screen fire assay cuando se esperan menos de 20 granos por alícuota."""
    return lam < PARTICLES_CRITERION


# ------------------------------------------------------------------ límites de Clifton
def clifton_limits(n: float) -> tuple[float, float]:
    """(E−, E+): errores relativos al 95 % para n partículas, ecuaciones (11) y (12) de Clifton
    et al. 1969: E± = z²/(2n) ± z/√n, con el signo menos para el límite inferior."""
    if not n > 0:
        raise GyError("las partículas esperadas deben ser positivas")
    half = Z95**2 / (2.0 * n)
    spread = Z95 / math.sqrt(n)
    return half - spread, half + spread


def poisson_exact_limits(n: float) -> tuple[float, float]:
    """(E−, E+) con el intervalo exacto de Poisson (Garwood) al 95 % para `n` granos contados."""
    lower = chi2.ppf(0.025, 2 * n) / 2.0 / n - 1.0
    upper = chi2.ppf(0.975, 2 * (n + 1)) / 2.0 / n - 1.0
    return float(lower), float(upper)
