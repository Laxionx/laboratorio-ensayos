"""Ecuación de Gy: factores, varianza (clásica y calibrada), despejes y granulometría."""

import math

import numpy as np
import pytest

from muestreo import gy
from muestreo.granulometria import (
    curve,
    d95_cm,
    d95_from_curve,
    d95_from_mm,
    d95_from_um,
    size_at,
    x63_from_spec,
)


def test_factor_mineralogico_con_ley_baja_es_densidad_sobre_ley():
    # Minnitt 2007, pág. 508: 1 ppm de oro (a = 1e-6) y ρm = 19,3 ⇒ c = 19,3e6 g/cm³
    assert gy.c_factor(1e-6, 19.3, 2.75) == pytest.approx(19.3e6, rel=1e-5)
    assert gy.c_factor(1e-6, 19.3, 2.75) == pytest.approx(
        0.999999 / 1e-6 * (0.999999 * 19.3 + 2.75e-6 * 1.0 * 1.0), rel=1e-12
    )


def test_factor_mineralogico_de_la_calcopirita_en_un_cobre_de_0_35_por_ciento():
    a = (63.55 + 55.85 + 2 * 32.06) / 63.55 * 0.35 / 100  # Minnitt 2007: a = 0,0101
    assert a == pytest.approx(0.0101, abs=5e-5)
    assert gy.c_factor(a, 4.2, 2.7) == pytest.approx((1 - a) / a * ((1 - a) * 4.2 + a * 2.7))


def test_la_liberacion_es_completa_bajo_dl_y_crece_el_error_arriba():
    assert gy.liberation_factor(0.005, 0.01, 1.5) == 1.0
    assert gy.liberation_factor(0.01, 0.01, 1.5) == 1.0
    assert gy.liberation_factor(0.04, 0.01, 1.5) == pytest.approx(0.125)  # (1/4)^1.5
    assert gy.liberation_size(1.25, 3.5e-5, 1.5) == pytest.approx(0.001337, abs=1e-6)


def test_las_dos_formas_de_gy_son_la_misma_ecuacion():
    # ℓ = (dℓ/dN)^b ⇒ σ² = c·f·g·dℓ^b·dN^(3−b)/MS = K·dN^α/MS con α = 3 − b y K = c·f·g·dℓ^b
    c, f, g, d_lib, b, d_n, mass = 4.2e6, 0.5, 0.25, 0.01, 1.5, 0.5, 250.0
    ell = gy.liberation_factor(d_n, d_lib, b)
    classic = gy.variance_classic(c, f, g, ell, d_n, mass)
    calibrated = gy.variance_calibrated(c * f * g * d_lib**b, 3 - b, d_n, mass)
    assert classic == pytest.approx(calibrated, rel=1e-12)
    mineral = gy.Mineral("x", a=1e-6 * 3.84, rho_m=16.0, rho_g=2.75, d_lib=d_lib, b=b)
    assert mineral.variance(d_n, mass) == pytest.approx(
        gy.variance_classic(mineral_c(mineral), 0.5, 0.25, ell, d_n, mass), rel=1e-12
    )


def mineral_c(m: gy.Mineral) -> float:
    return gy.c_factor(m.a, m.rho_m, m.rho_g)


def test_la_correccion_de_lote_resta_un_sobre_ml():
    k, alpha = 167.4, 1.123
    infinite = gy.variance_calibrated(k, alpha, 1.0, 100.0)
    finite = gy.variance_calibrated(k, alpha, 1.0, 100.0, 1000.0)
    assert infinite == pytest.approx(k / 100.0)
    assert finite == pytest.approx(k * (1 / 100 - 1 / 1000))
    assert finite < infinite
    with pytest.raises(gy.GyError):
        gy.variance_calibrated(k, alpha, 1.0, 2000.0, 1000.0)  # la muestra pesa más que el lote


def test_despejes_masa_y_tamano_cierran_con_la_varianza():
    k, alpha, d_n = 167.4, 1.123, 0.5
    mass = gy.sample_mass(k * d_n**alpha, 0.01)
    assert gy.variance_calibrated(k, alpha, d_n, mass) == pytest.approx(0.01, rel=1e-12)
    d = gy.nominal_size(k, alpha, 250.0, 0.01)
    assert gy.variance_calibrated(k, alpha, d, 250.0) == pytest.approx(0.01, rel=1e-12)
    with_lot = gy.sample_mass(k * d_n**alpha, 0.01, 5000.0)
    assert gy.variance_calibrated(k, alpha, d_n, with_lot, 5000.0) == pytest.approx(0.01)


def test_mas_masa_baja_el_error_y_mas_tamano_lo_sube():
    base = gy.variance_calibrated(167.4, 1.123, 1.0, 100.0)
    assert gy.variance_calibrated(167.4, 1.123, 1.0, 200.0) == pytest.approx(base / 2)
    assert gy.variance_calibrated(167.4, 1.123, 2.0, 100.0) == pytest.approx(base * 2**1.123)
    assert gy.rsd(0.04) == pytest.approx(0.2)


@pytest.mark.parametrize("bad", [0.0, -1.0, float("nan"), float("inf")])
def test_datos_invalidos_fallan_con_mensaje(bad):
    with pytest.raises(gy.GyError):
        gy.variance_calibrated(bad, 1.0, 1.0, 1.0)
    with pytest.raises(gy.GyError):
        gy.lot_term(bad)
    with pytest.raises(gy.GyError):
        gy.Mineral("x", k=167.4, alpha=1.1).ih_l(bad)


def test_mineral_clasico_sin_datos_pide_lo_que_falta():
    with pytest.raises(gy.GyError, match="faltan"):
        gy.Mineral("x", a=1e-6).ih_l(1.0)
    with pytest.raises(gy.GyError):
        gy.c_factor(1.5, 1.0, 1.0)
    with pytest.raises(gy.GyError):
        gy.liberation_factor(1.0, 0.1, 5.0)


# ------------------------------------------------------------------ granulometría
def test_el_d95_de_la_especificacion_con_m_igual_a_uno():
    # 70 % bajo 2 mm, m = 1: x63 = 2/(−ln 0,3) y d95 = x63·(−ln 0,05)
    x63 = x63_from_spec(70.0, 2.0, 1.0)
    assert x63 == pytest.approx(2.0 / -math.log(0.3))
    assert d95_from_mm(70.0, 2.0, 1.0) == pytest.approx(0.4976, abs=1e-4)
    assert d95_from_um(85.0, 75.0, 1.0) == pytest.approx(0.011843, abs=1e-6)
    assert size_at(x63, 1.0, 0.7) == pytest.approx(2.0)  # vuelve a la especificación


def test_el_d95_leido_en_la_curva_de_conminucion_coincide_con_el_analitico():
    for pct, size_um, m in ((70.0, 2000.0, 1.0), (70.0, 2000.0, 1.8), (85.0, 75.0, 0.8)):
        assert d95_from_curve(pct, size_um, m) == pytest.approx(
            d95_cm(pct, size_um * 1e-4, m) * 1e4, rel=2e-3
        )


def test_la_curva_pasa_por_la_especificacion():
    sieves, passing = curve(70.0, 2000.0, 1.3)
    assert passing[0] == pytest.approx(100.0, abs=0.1)
    below = float(np.interp(math.log(2000.0), np.log(sieves[::-1]), passing[::-1]))
    assert below == pytest.approx(70.0, abs=0.5)


def test_el_d95_baja_con_la_pendiente_y_pesa_al_cubo():
    slopes = (0.7, 1.0, 1.5, 2.5)
    d = [d95_from_mm(70.0, 2.0, m) for m in slopes]
    assert d == sorted(d, reverse=True)  # curvas más parejas, tamaño máximo más cerca de 2 mm
    assert (d[0] / d[-1]) ** 3 > 3.0  # dN³ cambia mucho: el error es sensible a m


@pytest.mark.parametrize(
    "pct, size, m", [(0, 1, 1), (100, 1, 1), (50, -1, 1), (50, 1, 0.1), (50, 1, 9)]
)
def test_especificacion_invalida(pct, size, m):
    with pytest.raises(gy.GyError):
        x63_from_spec(pct, size, m)
