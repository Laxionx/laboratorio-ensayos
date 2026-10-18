"""Geometría del crisol cónico (`muestreo.crisol`) y avisos de capacidad."""

import math

import numpy as np
import pytest

from muestreo import fusion as fu
from muestreo.crisol import (
    CRUCIBLE,
    DRY_BULK_DENSITY,
    FILL_LIMIT,
    Crucible,
    crucible_warnings,
    layers,
)


def _integral(c: Crucible, z: float, n: int = 20000) -> float:
    """∫ π r(z)² dz por rebanadas, sin la fórmula cerrada."""
    zs = (np.arange(n) + 0.5) * z / n
    return float(np.sum(math.pi * (c.r_bottom + c.slope * zs) ** 2 * (z / n)))


def test_el_crisol_es_un_cono_ancho_arriba_y_su_capacidad_es_la_del_de_20_g_de_bugbee():
    assert CRUCIBLE.r_top > CRUCIBLE.r_bottom > 0
    assert CRUCIBLE.capacity_cm3 == pytest.approx(190.0, abs=0.5)  # Bugbee 1922, Tabla IV
    assert CRUCIBLE.height <= 4 * 2.54  # los de mufla «no pasan de 4 pulgadas de alto»
    assert FILL_LIMIT == pytest.approx(2 / 3)
    assert CRUCIBLE.fill_limit_cm3 == pytest.approx(2 / 3 * CRUCIBLE.capacity_cm3)


@pytest.mark.parametrize("z", [0.1, 1.0, 3.3, 8.5])
def test_el_volumen_bajo_un_nivel_es_la_integral_del_cono(z):
    assert CRUCIBLE.volume_below(z) == pytest.approx(_integral(CRUCIBLE, z), rel=1e-6)


def test_el_volumen_es_el_de_un_cilindro_si_las_paredes_son_rectas():
    cyl = Crucible(2.0, 2.0, 5.0)
    assert cyl.volume_below(3.0) == pytest.approx(math.pi * 4.0 * 3.0)
    assert cyl.level_for(math.pi * 4.0 * 3.0) == pytest.approx(3.0)


@pytest.mark.parametrize("z", [0.0, 0.05, 0.28, 2.0, 5.5, 8.5])
def test_nivel_y_volumen_son_inversos(z):
    assert CRUCIBLE.level_for(CRUCIBLE.volume_below(z)) == pytest.approx(z, abs=1e-9)


def test_el_nivel_se_corta_en_el_fondo_y_en_el_borde():
    assert CRUCIBLE.level_for(0.0) == 0.0 and CRUCIBLE.level_for(-3.0) == 0.0
    assert CRUCIBLE.level_for(1e6) == CRUCIBLE.height
    assert CRUCIBLE.volume_below(-1.0) == 0.0
    assert CRUCIBLE.volume_below(99.0) == pytest.approx(CRUCIBLE.capacity_cm3)


def test_en_un_cono_la_misma_masa_sube_mas_en_el_fondo_que_arriba():
    """El fondo es angosto: 10 cm³ al fondo suben más que 10 cm³ cerca del borde."""
    low = CRUCIBLE.level_for(10.0)
    high = CRUCIBLE.level_for(CRUCIBLE.capacity_cm3 - 0.1) - CRUCIBLE.level_for(
        CRUCIBLE.capacity_cm3 - 10.1
    )
    assert low > high > 0


def test_el_plomo_queda_siempre_bajo_la_escoria_y_cada_capa_tiene_su_volumen():
    for lead, slag in [(0.5, 5.0), (2.86, 32.3), (10.0, 80.0), (0.01, 0.01), (30.0, 120.0)]:
        lay = layers(lead, slag)
        assert 0.0 < lay.lead_top < lay.slag_top < CRUCIBLE.height and not lay.overflows
        assert CRUCIBLE.volume_below(lay.lead_top) == pytest.approx(lead)
        assert CRUCIBLE.volume_below(lay.slag_top) - CRUCIBLE.volume_below(
            lay.lead_top
        ) == pytest.approx(slag)


def test_sin_plomo_no_hay_charco_y_si_se_derrama_se_marca():
    assert layers(0.0, 20.0).lead_top == 0.0
    over = layers(5.0, CRUCIBLE.capacity_cm3)
    assert over.overflows and over.slag_top == CRUCIBLE.height and over.lead_top < over.slag_top


def test_la_densidad_del_plomo_liquido_es_la_recta_de_oecd_nea():
    assert fu.pb_liquid_density(1050.0) == pytest.approx(9.7866, abs=5e-5)
    # a la fusión (600,6 K) coincide con los 10,656 g/cm³ que Assael da, a 0,1 %
    assert fu.pb_liquid_density(600.6 - 273.15) == pytest.approx(10.656, rel=1e-3)
    assert fu.pb_liquid_density(1050.0) < fu.pb_liquid_density(400.0) < fu.PB_DENSITY


def test_sin_exceso_no_hay_avisos():
    assert crucible_warnings(141.5, 2.9, 32.3) == []


def test_la_carga_en_polvo_sobre_los_dos_tercios_avisa_y_sobre_la_capacidad_es_riesgo():
    limit_g = CRUCIBLE.fill_limit_cm3 * DRY_BULK_DENSITY
    cap_g = CRUCIBLE.capacity_cm3 * DRY_BULK_DENSITY
    assert crucible_warnings(limit_g - 1.0, 1.0, 1.0) == []
    (w,) = crucible_warnings(limit_g + 1.0, 1.0, 1.0)
    assert w.level == "aviso" and "carga en polvo" in w.text.lower() and "2/3" in w.text
    (w,) = crucible_warnings(cap_g + 1.0, 1.0, 1.0)
    assert w.level == "riesgo" and "capacidad" in w.text and "Bugbee" in w.source


def test_lo_fundido_sobre_los_dos_tercios_avisa_y_sobre_la_capacidad_es_riesgo():
    assert crucible_warnings(50.0, 1.0, CRUCIBLE.fill_limit_cm3 - 2.0) == []
    (w,) = crucible_warnings(50.0, 1.0, CRUCIBLE.fill_limit_cm3)
    assert w.level == "aviso" and "fundido" in w.text
    (w,) = crucible_warnings(50.0, 1.0, CRUCIBLE.capacity_cm3)
    assert w.level == "riesgo" and "fundido" in w.text


def test_los_dos_excesos_dan_dos_avisos():
    ws = crucible_warnings(1000.0, 1.0, CRUCIBLE.capacity_cm3)
    assert [w.level for w in ws] == ["riesgo", "riesgo"]


def test_la_evaluacion_de_la_carga_trae_el_aviso_de_capacidad():
    p = fu.FusionParams(60.0, {"cuarzo": 80.0, "calcita": 8.0}, "SO3", 28.0, 2.0, 11.0, 4.1)
    r = fu.design_and_evaluate(p)
    assert r.dry_charge_g == pytest.approx(p.sample_g + r.reagents.total_g)
    assert any("capacidad" in w.text or "2/3" in w.text for w in r.warnings)
    normal = fu.design_and_evaluate(
        fu.FusionParams(fu.AT_G, {"cuarzo": 80.0, "calcita": 8.0}, "SO3", 28.0, 2.0, 11.0, 4.1)
    )
    assert not any("crisol" in w.text and "cm³" in w.text for w in normal.warnings)


def test_el_aviso_de_la_carga_en_polvo_cuenta_la_muestra_y_los_reactivos():
    limit_g = CRUCIBLE.fill_limit_cm3 * DRY_BULK_DENSITY
    straddles = 0
    for sample in range(20, 80, 2):
        p = fu.FusionParams(
            float(sample), {"cuarzo": 80.0, "calcita": 8.0}, "SO3", 28.0, 2.0, 11.0, 4.1
        )
        r = fu.design_and_evaluate(p)
        warned = any("carga en polvo" in w.text.lower() for w in r.warnings)
        assert warned == (sample + r.reagents.total_g > limit_g)
        straddles += sample + r.reagents.total_g > limit_g >= r.reagents.total_g
    assert straddles > 0  # hay cargas donde solo la muestra hace pasar el límite
