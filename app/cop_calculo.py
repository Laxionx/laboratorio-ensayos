"""Cálculo de la pestaña «Copelación», sin Streamlit: arma los números que muestran la calculadora,
el encuarte, los gráficos y la animación. Todo lo que se ve sale de `muestreo.copelacion`."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from calculo import FusionUIParams, run_fusion

from muestreo import copelacion as cp
from muestreo.fusion import FusionError, pb_liquid_density

FRAMES = 49  # cuadros de la animación (48 intervalos)

# Los valores de las listas de la barra lateral son rótulos en español (`opt` los traduce).
FUENTES_PLOMO = ("Del botón de la fusión", "Valor propio")
MODOS = ("Razón de Rose (según el oro)", "Mínimo de Bugbee (3 a 1)", "Razón propia")
MODO_CLAVE = dict(zip(MODOS, cp.MODOS_RAZON, strict=True))


@dataclass(frozen=True)
class CopParams:
    temp_c: float = 800.0
    plomo_fuente: str = FUENTES_PLOMO[0]
    plomo_g: float = 28.0
    oro_mg: float = 1.0
    plata_mg: float = 2.0
    modo: str = MODOS[0]
    razon: float = 8.0
    ley_gpt: float = 3.84  # ley de oro medida (g/t), solo para la corrección


@dataclass(frozen=True)
class CopView:
    params: CopParams
    plomo_g: float  # el que se usó
    plomo_de_fusion: bool  # salió del botón de la pestaña Fusión
    fusion_no_sirve: bool  # se pidió el de la fusión pero esa pestaña no lo pudo calcular
    res: cp.Copelacion
    ley_au_corregida: float
    rho_plomo: float  # g/cm³ a la temperatura de copelación (misma ecuación que la fusión)

    @cached_property
    def cuadros(self) -> list[cp.Cuadro]:
        return cp.trayectoria(self.res, FRAMES)

    def volumen(self, c: cp.Cuadro) -> float:
        return cp.volumen_cm3(c.plomo_mg, c.oro_mg, c.plata_mg, self.rho_plomo)

    @cached_property
    def escalas(self) -> list[float]:
        """Radio de cada cuadro relativo al del botón entero: (V / V0)^(1/3)."""
        cuadros = self.cuadros
        v0 = self.volumen(cuadros[0])
        return [(self.volumen(c) / v0) ** (1.0 / 3.0) for c in cuadros]


def boton_de_fusion(f: FusionUIParams) -> float | None:
    """Masa (g) del botón de plomo de la pestaña Fusión, o `None` si esa pestaña no la calcula."""
    try:
        return run_fusion(f).result.button_g
    except (FusionError, ValueError):
        return None


def run_cop(p: CopParams, boton_fusion_g: float | None = None) -> CopView:
    """Lanza `CopelacionError` si los datos no sirven."""
    pide_fusion = p.plomo_fuente == FUENTES_PLOMO[0]
    de_fusion = pide_fusion and boton_fusion_g is not None
    plomo = boton_fusion_g if de_fusion else p.plomo_g
    res = cp.copelar(p.temp_c, plomo, p.oro_mg, p.plata_mg, MODO_CLAVE[p.modo], p.razon)
    ley = cp.ley_corregida(p.ley_gpt, res.perdida_au.frac)
    return CopView(p, plomo, de_fusion, pide_fusion and not de_fusion, res, ley,
                   pb_liquid_density(p.temp_c))  # fmt: skip
