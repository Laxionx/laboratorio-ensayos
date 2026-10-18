"""Pesos atómicos (IUPAC) y masas molares de las sustancias del ensayo al fuego."""

from __future__ import annotations

import re


class FusionError(ValueError):
    """Datos de fusión fuera del dominio del cálculo."""


ATOMIC_WEIGHTS = {
    "H": 1.008,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "Na": 22.990,
    "Mg": 24.305,
    "Si": 28.086,
    "S": 32.06,
    "K": 39.098,
    "Ca": 40.078,
    "Mn": 54.938,
    "Fe": 55.845,
    "Cu": 63.546,
    "Zn": 65.38,
    "As": 74.922,
    "Sb": 121.760,
    "Pb": 207.2,
}


def molar_mass(formula: str) -> float:
    """Masa molar (g/mol) de una fórmula sin paréntesis, como «Na2B4O7»."""
    parts = re.findall(r"([A-Z][a-z]?)(\d*)", formula)
    if not parts or "".join(e + n for e, n in parts) != formula:
        raise FusionError(f"fórmula no válida: {formula!r}")
    try:
        return sum(ATOMIC_WEIGHTS[e] * (int(n) if n else 1) for e, n in parts)
    except KeyError as exc:
        raise FusionError(f"elemento sin peso atómico: {exc}") from exc


PB = ATOMIC_WEIGHTS["Pb"]
M = {
    f: molar_mass(f)
    for f in (
        "PbO",
        "Na2CO3",
        "K2CO3",
        "NaHCO3",
        "Na2B4O7",
        "SiO2",
        "CaCO3",
        "MgCO3",
        "FeO",
        "CaO",
        "ZnO",
        "Cu2O",
        "Na2O",
        "Na2SO4",
        "KNO3",
        "CO2",
        "SO2",
    )
}
