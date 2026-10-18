"""Oro grueso: partículas por alícuota, simulación de Poisson y límites de Clifton.

Cortes fijados antes de correr: media y desviación de los 1 000 ensayos simulados dentro de 3σ del
valor analítico de Poisson (error de Monte Carlo), con semilla fija.
"""

import math

import numpy as np
import pytest

from muestreo import oro
from muestreo.gy import GyError

GRADE, ALIQUOT, GRAIN_UM = 3.84, 30.0, 150.0  # g/t, g y µm: el ejemplo de la app


def test_masa_del_grano_esferico_de_oro():
    assert oro.grain_mass_g(100.0) == pytest.approx(19.3 * math.pi / 6 * 1e-6, rel=1e-12)
    assert oro.grain_mass_g(100.0, "cubo") == pytest.approx(19.3e-6, rel=1e-12)
    assert oro.grain_mass_g(200.0) == pytest.approx(8 * oro.grain_mass_g(100.0))  # al cubo
    with pytest.raises(GyError):
        oro.grain_mass_g(100.0, "estrella")


def test_particulas_esperadas_y_masa_para_20():
    m_p = oro.grain_mass_g(GRAIN_UM)
    lam = oro.expected_particles(GRADE, ALIQUOT, m_p)
    assert lam == pytest.approx(GRADE * 1e-6 * ALIQUOT / m_p)
    assert lam == pytest.approx(3.378, abs=0.001)
    mass20 = oro.mass_for_particles(GRADE, m_p, 20)
    assert oro.expected_particles(GRADE, mass20, m_p) == pytest.approx(20.0)
    assert mass20 == pytest.approx(177.6, abs=0.1)


@pytest.mark.parametrize(
    "grain_um, aliquot", [(150.0, 30.0), (150.0, 50.0), (50.0, 30.0), (400.0, 50.0)]
)
def test_monte_carlo_coincide_con_poisson_dentro_de_3_sigma(grain_um, aliquot):
    m_p = oro.grain_mass_g(grain_um)
    sim = oro.simulate(GRADE, aliquot, m_p)
    n, lam = len(sim.counts), sim.lam
    assert n == oro.TRIALS == 1000
    assert abs(sim.counts.mean() - lam) <= 3 * math.sqrt(lam / n)  # σ de la media: √(λ/n)
    s2_sd = math.sqrt((lam + 2 * lam**2) / n)  # σ de la varianza muestral de una Poisson
    assert abs(sim.counts.var(ddof=1) - lam) <= 3 * s2_sd
    p0 = oro.poisson_p0(lam)
    assert abs(sim.share_zero - p0) <= 3 * math.sqrt(p0 * (1 - p0) / n)


def test_la_simulacion_es_reproducible_con_semilla_fija():
    m_p = oro.grain_mass_g(GRAIN_UM)
    a = oro.simulate(GRADE, ALIQUOT, m_p)
    b = oro.simulate(GRADE, ALIQUOT, m_p)
    c = oro.simulate(GRADE, ALIQUOT, m_p, seed=1)
    assert np.array_equal(a.counts, b.counts) and not np.array_equal(a.counts, c.counts)
    assert oro.SEED == 2017


def test_la_ley_de_cada_ensayo_es_granos_por_masa_del_grano_sobre_la_alicuota():
    m_p = oro.grain_mass_g(GRAIN_UM)
    sim = oro.simulate(GRADE, ALIQUOT, m_p)
    assert np.allclose(sim.grades_gpt, sim.counts * m_p / ALIQUOT * 1e6)
    assert sim.mean_gpt == pytest.approx(GRADE, rel=0.1)  # insesgado en promedio


def test_con_pocos_granos_la_mediana_cae_bajo_la_ley_real_y_hay_ensayos_muy_altos():
    m_p = oro.grain_mass_g(GRAIN_UM)
    sim = oro.simulate(GRADE, ALIQUOT, m_p)
    assert sim.lam < 5
    assert sim.median_gpt < GRADE
    assert sim.share_above(2.0) > 0.05  # unos pocos ensayos salen muy altos
    assert sim.grades_gpt.max() > 3 * GRADE
    assert oro.poisson_median_particles(sim.lam) == np.median(sim.counts)
    assert sim.share_zero > 0.02 and sim.grades_gpt.min() == 0.0


def test_con_muchos_granos_la_mediana_se_acerca_a_la_ley():
    sim = oro.simulate(GRADE, 50.0, oro.grain_mass_g(20.0))
    assert sim.lam > 100
    assert sim.median_gpt == pytest.approx(GRADE, rel=0.1)


def test_screen_fire_assay_se_recomienda_bajo_20_granos():
    assert oro.recommend_screen_fire_assay(19.9) and not oro.recommend_screen_fire_assay(20.0)
    assert oro.recommend_screen_fire_assay(
        oro.simulate(GRADE, ALIQUOT, oro.grain_mass_g(150.0)).lam
    )


# ------------------------------------------------------------------ Clifton 1969
@pytest.mark.parametrize(
    "n, lower, upper", [(20, -34.2, 53.4), (75, -20.1, 25.2), (400, -9.3, 10.3)]
)
def test_limites_de_clifton_con_sus_ecuaciones_11_y_12(n, lower, upper):
    e_lo, e_hi = oro.clifton_limits(n)
    assert 100 * e_lo == pytest.approx(lower, abs=0.05)
    assert 100 * e_hi == pytest.approx(upper, abs=0.05)


def test_regla_de_20_particulas_es_el_menor_n_con_error_superior_de_unos_55_por_ciento():
    first = next(n for n in range(1, 200) if oro.clifton_limits(n)[1] <= 0.55)
    assert first == oro.PARTICLES_CRITERION == 20
    assert oro.clifton_limits(20)[1] == pytest.approx(0.54, abs=0.01)  # «E+95 = 0,54»
    assert oro.clifton_limits(20)[0] == pytest.approx(-0.34, abs=0.01)  # «E−95 = −0,34»


def test_el_intervalo_exacto_de_poisson_es_mas_ancho_en_pocos_granos():
    lo, hi = oro.poisson_exact_limits(7)
    assert lo < oro.clifton_limits(7)[0] and hi > oro.clifton_limits(7)[1]
    lo, hi = oro.poisson_exact_limits(400)
    assert lo == pytest.approx(oro.clifton_limits(400)[0], abs=0.01)


@pytest.mark.parametrize("bad", [0.0, -3.0])
def test_datos_invalidos_del_oro(bad):
    with pytest.raises(GyError):
        oro.expected_particles(bad, 30.0, 1e-5)
    with pytest.raises(GyError):
        oro.mass_for_particles(1.0, bad)
    with pytest.raises(GyError):
        oro.clifton_limits(bad)
