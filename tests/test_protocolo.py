"""Protocolos de preparación: varianza por etapa y acumulada, presets y sensibilidad a m."""

import math

import pytest

from muestreo import Mineral, evaluate
from muestreo.granulometria import d95_from_mm, d95_from_um
from muestreo.gy import GyError
from muestreo.protocolo import (
    PRESETS,
    Protocol,
    SizeSpec,
    Stage,
    path_points,
    preset,
    safety_mass,
    sensibilidad_a_m,
)

DSA = Mineral("DSA (Minnitt 2017)", k=167.4, alpha=1.123)
SFA = Mineral("SFA (Minnitt 2017)", k=2539.0, alpha=1.03)


def test_prep_31_con_el_mineral_dsa():
    result = evaluate(preset("PREP-31", 3000.0, 30.0), DSA, 1.0, True)
    first, second = result.stages
    assert (first.mass_in_g, first.mass_out_g) == (3000.0, 250.0)
    assert (second.mass_in_g, second.mass_out_g) == (250.0, 30.0)
    assert first.d_n_cm == pytest.approx(d95_from_mm(70.0, 2.0, 1.0))
    assert second.d_n_cm == pytest.approx(d95_from_um(85.0, 75.0, 1.0))
    assert first.variance == pytest.approx(167.4 * first.d_n_cm**1.123 * (1 / 250 - 1 / 3000))
    assert second.variance == pytest.approx(167.4 * second.d_n_cm**1.123 * (1 / 30 - 1 / 250))


def test_el_error_total_es_la_raiz_de_la_suma_de_varianzas():
    result = evaluate(preset("PREP-31B", 3000.0, 50.0), DSA, 1.2, True)
    total = sum(s.variance for s in result.stages)
    assert result.variance == pytest.approx(total)
    assert result.rsd == pytest.approx(math.sqrt(total))
    assert result.stages[-1].cum_variance == pytest.approx(total)
    assert result.stages[0].cum_variance == pytest.approx(result.stages[0].variance)
    assert sum(s.share for s in result.stages) == pytest.approx(1.0)
    assert result.stages[-1].cum_rsd == pytest.approx(result.rsd)


def test_el_error_total_supera_al_de_cada_etapa():
    result = evaluate(preset("PREP-31", 3000.0, 30.0), DSA, 1.0)
    assert result.rsd > max(s.rsd for s in result.stages)


def test_mas_masa_en_la_alicuota_baja_el_error_y_el_riffle_de_1_kg_tambien():
    a30 = evaluate(preset("PREP-31", 3000.0, 30.0), DSA).rsd
    a50 = evaluate(preset("PREP-31", 3000.0, 50.0), DSA).rsd
    b30 = evaluate(preset("PREP-31B", 3000.0, 30.0), DSA).rsd
    assert a50 < a30 and b30 < a30


def test_apagar_la_correccion_de_lote_sube_el_error():
    on = evaluate(preset("PREP-31", 3000.0, 30.0), DSA, 1.0, True)
    off = evaluate(preset("PREP-31", 3000.0, 30.0), DSA, 1.0, False)
    assert off.variance > on.variance
    assert off.stages[0].variance == pytest.approx(167.4 * off.stages[0].d_n_cm ** 1.123 / 250.0)
    assert not off.lot_correction and on.lot_correction


def test_el_preset_de_minnitt_2017_reproduce_las_varianzas_de_la_tabla_viii():
    result = evaluate(preset(PRESETS[2], 0.0, 50.0), DSA, 1.0, False)
    published = (0.0105, 0.00723, 0.00470, 0.00506)  # filas de división de la Tabla VIII (DSA)
    for stage, value in zip(result.stages, published, strict=True):
        assert stage.variance == pytest.approx(value, abs=5e-5 if value > 0.01 else 5e-6)
    assert result.rsd == pytest.approx(math.sqrt(sum(published)), abs=2e-3)


def test_el_error_depende_del_mineral_calibrado():
    protocol = preset("PREP-31", 3000.0, 30.0)
    assert evaluate(protocol, SFA).rsd > 3 * evaluate(protocol, DSA).rsd  # K 15 veces mayor


def test_mineral_clasico_en_un_protocolo():
    mineral = Mineral(
        "clásico", a=3.84e-6, rho_m=16.0, rho_g=2.75, d_lib=0.0082, f=0.5, g=0.25, b=1.5
    )
    result = evaluate(preset("PREP-31", 3000.0, 30.0), mineral, 1.0)
    assert result.rsd > 0
    # la pulpa (dN 0,0118 cm) está sobre la liberación (0,0082 cm): ℓ < 1, no 1
    ih = mineral.ih_l(0.0118)
    c = (1 - 3.84e-6) / 3.84e-6 * ((1 - 3.84e-6) * 16.0 + 3.84e-6 * 2.75)
    assert ih == pytest.approx(c * 0.5 * 0.25 * (0.0082 / 0.0118) ** 1.5 * 0.0118**3, rel=1e-9)


def test_la_sensibilidad_a_m_es_monotona_y_grande():
    protocol = preset("PREP-31", 3000.0, 30.0)
    rows = sensibilidad_a_m(protocol, DSA, (0.7, 1.0, 1.5, 2.5))
    errors = [rsd for _, rsd, _ in rows]
    assert errors == sorted(errors, reverse=True)
    assert errors[0] / errors[-1] > 1.5
    assert all(len(d) == 2 for _, _, d in rows)


def test_la_ruta_del_nomograma_alterna_reducir_y_dividir():
    result = evaluate(preset("PREP-31", 3000.0, 30.0, d_n0_cm=5.0), DSA, 1.0)
    points = path_points(result)
    assert len(points) == 1 + 2 * len(result.stages)
    assert points[0][1:] == (5.0, 3000.0)
    (_, d0, m0), (_, d1, m1), (_, d2, m2) = points[0], points[1], points[2]
    assert m1 == m0 and d1 < d0  # reducir: horizontal, masa constante
    assert d2 == d1 and m2 < m1  # dividir: vertical, tamaño constante
    assert points[-1][1:] == (result.stages[-1].d_n_cm, 30.0)


def test_la_masa_de_seguridad_da_la_varianza_pedida():
    mass = safety_mass(DSA, 0.5, 0.01)
    assert DSA.variance(0.5, mass) == pytest.approx(0.01)
    assert safety_mass(DSA, 1.0, 0.01) > mass  # más tamaño pide más masa


def test_protocolos_invalidos():
    with pytest.raises(GyError, match="menor que"):
        evaluate(preset("PREP-31", 100.0, 30.0), DSA)  # 250 g de un lote de 100 g
    with pytest.raises(GyError):
        evaluate(Protocol("vacío", 100.0, 5.0, ()), DSA)
    with pytest.raises(GyError):
        Stage("sin tamaño", 10.0).d_n(1.0)
    with pytest.raises(GyError):
        preset("PREP-99", 100.0, 30.0)
    assert Stage("directo", 10.0, d_n_cm=0.2).d_n(9.9) == 0.2
    assert Stage("espec", 10.0, SizeSpec(70.0, 2000.0)).d_n(1.0) > 0
