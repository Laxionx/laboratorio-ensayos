"""Error fundamental de muestreo (FE) de Gy, en las unidades de la literatura: masa en g y tamaño
en cm.

Forma clásica (Gy 1982; Minnitt, Rice y Spangenberg 2007, J. SAIMM 107(8) 505-511):

    σ² = c·f·g·ℓ·dN³ · (1/MS − 1/ML)

con c el factor mineralógico, f la forma, g la granulométrica, ℓ la de liberación y dN el tamaño
máximo nominal (el d95). Forma calibrada (François-Bongarçon; Minnitt 2017, J. SAIMM 117(2)
121-128; Chieregati 2017, Mining Engineering):

    σ² = K·dN^α · (1/MS − 1/ML)

Las dos son la misma ecuación: IHL = c·f·g·ℓ·dN³ = K·dN^α es la heterogeneidad de constitución
del lote. Con ℓ = (dℓ/dN)^b bajo el tamaño de liberación dℓ, α = 3 − b y K = c·f·g·dℓ^b. K y α
se CALIBRAN por mineral (ensayo de heterogeneidad o árbol de muestreo): nunca se suponen.

El término (1/MS − 1/ML) es la corrección por masa del lote; con ML → ∞ queda 1/MS. Minnitt 2017
la omite en su Tabla VIII; Chieregati 2017 la incluye en su Tabla 2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

AU_DENSITY = 19.3  # g/cm³, oro puro (Minnitt et al. 2007)


class GyError(ValueError):
    """Datos de entrada fuera del dominio de la ecuación."""


def _positive(**values: float) -> None:
    for name, value in values.items():
        if not (math.isfinite(value) and value > 0):
            raise GyError(f"{name} debe ser positivo y finito: {value}")


# ------------------------------------------------------------------ factores
def c_factor(a: float, rho_m: float, rho_g: float) -> float:
    """Factor mineralógico c = ((1 − a)/a)·[(1 − a)·ρm + a·ρg] (g/cm³).

    `a` es la proporción decimal del mineral valioso; con a << 1 se reduce a ρm/a (≈ ρm/ley)."""
    if not 0 < a < 1:
        raise GyError(f"la proporción a debe estar entre 0 y 1: {a}")
    _positive(rho_m=rho_m, rho_g=rho_g)
    return (1.0 - a) / a * ((1.0 - a) * rho_m + a * rho_g)


def liberation_factor(d_n: float, d_lib: float, b: float) -> float:
    """ℓ = (dℓ/dN)^b, igual a 1 cuando dN ≤ dℓ (liberación completa)."""
    _positive(d_n=d_n, d_lib=d_lib)
    if not 0 <= b <= 3:
        raise GyError(f"el exponente b debe estar entre 0 y 3: {b}")
    return min(1.0, (d_lib / d_n) ** b)


def liberation_size(d_n: float, ell: float, b: float) -> float:
    """dℓ = dN·ℓ^(1/b): el tamaño de liberación que da un ℓ medido a dN."""
    _positive(d_n=d_n, ell=ell, b=b)
    return d_n * ell ** (1.0 / b)


# ------------------------------------------------------------------ varianza
def lot_term(mass_s: float, mass_l: float | None = None) -> float:
    """1/MS − 1/ML (1/g); con `mass_l` None el lote es infinito y queda 1/MS."""
    _positive(mass_s=mass_s)
    if mass_l is None:
        return 1.0 / mass_s
    _positive(mass_l=mass_l)
    if mass_s > mass_l:
        raise GyError(f"la muestra ({mass_s:g} g) no puede pesar más que el lote ({mass_l:g} g)")
    return 1.0 / mass_s - 1.0 / mass_l


def variance_classic(c: float, f: float, g: float, ell: float, d_n: float, mass_s: float,
                     mass_l: float | None = None) -> float:  # fmt: skip
    """σ² = c·f·g·ℓ·dN³·(1/MS − 1/ML), dN en cm y masas en g."""
    _positive(c=c, f=f, g=g, ell=ell, d_n=d_n)
    return c * f * g * ell * d_n**3 * lot_term(mass_s, mass_l)


def variance_calibrated(k: float, alpha: float, d_n: float, mass_s: float,
                        mass_l: float | None = None) -> float:  # fmt: skip
    """σ² = K·dN^α·(1/MS − 1/ML), dN en cm y masas en g."""
    _positive(k=k, alpha=alpha, d_n=d_n)
    return k * d_n**alpha * lot_term(mass_s, mass_l)


def sample_mass(ih_l: float, rel_variance: float, mass_l: float | None = None) -> float:
    """Masa (g) que da la varianza relativa pedida: 1/MS = σ²/IHL + 1/ML."""
    _positive(ih_l=ih_l, rel_variance=rel_variance)
    inverse = rel_variance / ih_l + (0.0 if mass_l is None else 1.0 / mass_l)
    return 1.0 / inverse


def nominal_size(k: float, alpha: float, mass_s: float, rel_variance: float) -> float:
    """dN (cm) que da la varianza pedida con esa masa (lote infinito): (σ²·MS/K)^(1/α)."""
    _positive(k=k, alpha=alpha, mass_s=mass_s, rel_variance=rel_variance)
    return (rel_variance * mass_s / k) ** (1.0 / alpha)


def rsd(variance: float) -> float:
    """Desviación estándar relativa (fracción): √σ²."""
    return math.sqrt(variance)


# ------------------------------------------------------------------ mineral
@dataclass(frozen=True)
class Mineral:
    """Cómo se calcula la heterogeneidad IHL(dN) del lote: calibrada (K, α) o clásica."""

    name: str
    k: float | None = None  # calibrada: σ² = K·dN^α·(...)
    alpha: float | None = None
    a: float | None = None  # clásica: proporción decimal del mineral valioso
    rho_m: float | None = None  # g/cm³
    rho_g: float | None = None
    f: float = 0.5
    g: float = 0.25
    d_lib: float | None = None  # cm
    b: float = 1.5

    @property
    def calibrated(self) -> bool:
        return self.k is not None

    def ih_l(self, d_n: float) -> float:
        """Heterogeneidad de constitución del lote a ese tamaño (g)."""
        _positive(d_n=d_n)
        if self.calibrated:
            _positive(k=self.k, alpha=self.alpha)
            return self.k * d_n**self.alpha
        missing = [n for n in ("a", "rho_m", "rho_g", "d_lib") if getattr(self, n) is None]
        if missing:
            raise GyError(f"faltan datos del mineral: {', '.join(missing)}")
        _positive(f=self.f, g=self.g)
        c = c_factor(self.a, self.rho_m, self.rho_g)
        return c * self.f * self.g * liberation_factor(d_n, self.d_lib, self.b) * d_n**3

    def variance(self, d_n: float, mass_s: float, mass_l: float | None = None) -> float:
        return self.ih_l(d_n) * lot_term(mass_s, mass_l)
