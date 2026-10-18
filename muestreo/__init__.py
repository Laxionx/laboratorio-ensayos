"""Muestreo de minerales: error fundamental de Gy en la preparación de muestras, oro grueso y
validación contra números publicados (laboratorio de ensayos al fuego, fase 1)."""

from .gy import GyError, Mineral, variance_calibrated, variance_classic
from .protocolo import Protocol, Stage, evaluate

__all__ = [
    "GyError",
    "Mineral",
    "Protocol",
    "Stage",
    "evaluate",
    "variance_calibrated",
    "variance_classic",
]
