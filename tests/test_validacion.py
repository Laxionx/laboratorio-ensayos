"""Validación de la ecuación de Gy contra números publicados. Cortes fijados antes de correr
(ver el docstring de muestreo/validacion.py). Lo que NO cuadra se registra tal cual, sin xfail:
- Minnitt 2007 (errata del artículo): con los datos impresos no salen sus cifras.
- Minnitt 2017, Tabla VIII, una fila de SFA (2055,56 g, dN 0,0001 cm).
- Clifton 1969, 7 partículas, límite inferior (3,4 puntos; la etiqueta de la figura es redonda).
"""

import pytest

from muestreo import gy
from muestreo import validacion as v


def test_minnitt_2017_tabla_viii_18_de_19_filas_al_redondeo_publicado():
    checks = v.minnitt_2017_checks()
    assert len(checks) == 19
    failing = [c for c in checks if not c.ok]
    assert [c.item for c in failing] == ["SFA: 2 055.56 g, dN 0.0001 cm"]  # la única que no cuadra
    assert failing[0].published == 0.00005
    assert failing[0].calculated == pytest.approx(9.4e-5, rel=0.01)
    assert "no cuadra" in failing[0].note
    for c in checks:
        if c.ok:
            assert abs(c.calculated - c.published) <= 5.1e-5


def test_minnitt_2017_las_filas_dsa_cuadran_todas_y_las_de_sfa_9_de_10():
    checks = v.minnitt_2017_checks()
    assert all(c.ok for c in checks if c.item.startswith("DSA"))
    sfa = [c for c in checks if c.item.startswith("SFA")]
    assert sum(c.ok for c in sfa) == 9 and len(sfa) == 10


def test_el_redondeo_se_mide_con_los_decimales_impresos():
    assert v.decimals_of("0.0105") == 4 and v.decimals_of("0.00105") == 5
    assert v.decimals_of("32") == 0
    assert v.matches_rounding(0.0104536, "0.0105")  # 4,6e-5 < 5e-5
    assert not v.matches_rounding(0.0104, "0.0105")
    assert v.matches_rounding(0.000115178, "0.00012")


def test_chieregati_2017_tabla_2_al_redondeo_publicado():
    checks = v.chieregati_checks()
    assert len(checks) == 14
    assert all(c.ok for c in checks), [c.item for c in checks if not c.ok]
    total = [c for c in checks if c.item.startswith("Total")]
    assert total[0].calculated == pytest.approx(0.1079, abs=5e-5)
    assert total[1].calculated == pytest.approx(32.8, abs=0.05)


def test_clifton_1969_cuadra_a_2_puntos_salvo_el_limite_inferior_de_7_particulas():
    checks = v.clifton_checks()
    assert len(checks) == 8
    failing = [c for c in checks if not c.ok]
    assert [c.item for c in failing] == ["7 partículas, límite inferior"]
    assert failing[0].difference == pytest.approx(3.36, abs=0.05)  # −46,6 frente a −50
    assert "redondeada" in failing[0].note
    for c in checks:
        if c.ok:
            assert abs(c.difference) <= v.CLIFTON_TOLERANCE


def test_minnitt_2007_con_los_datos_impresos_no_sale_lo_publicado():
    f = {c.item: c for c in v.minnitt_2007_findings()}
    assert not any(c.ok for c in f.values())
    assert f["varianza (dN 1,25 cm, 10 kg)"].calculated == pytest.approx(0.01367, abs=1e-5)
    assert f["error relativo"].calculated == pytest.approx(11.69, abs=0.005)
    assert f["masa para 15 %"].calculated == pytest.approx(2502.0, abs=1.0)
    assert f["dN para 15 % con 15 kg"].calculated == pytest.approx(1.69, abs=0.005)
    assert f["c·f·g·ℓ"].calculated == pytest.approx(70.0) and f["c·f·g·ℓ"].published == 448.0
    assert 448.0 / 70.0 == pytest.approx(6.4)  # el factor implícito


def test_minnitt_2007_con_448_se_reproduce_lo_publicado_documenta_la_errata():
    checks = v.minnitt_2007_implied()
    assert all(c.ok for c in checks)
    by_item = {c.item: c for c in checks}
    assert by_item["error relativo"].calculated == pytest.approx(29.58, abs=0.01)  # ±0,01 punto
    assert by_item["masa para 15 %"].calculated == pytest.approx(16.0e3, rel=0.002)  # ≈ 16 kg
    assert by_item["dN para 15 % con 15 kg"].calculated == pytest.approx(0.91, abs=0.005)
    printed = v.MINNITT_2007_C * v.MINNITT_2007_F * v.MINNITT_2007_G * v.MINNITT_2007_ELL_PRINTED
    assert v.MINNITT_2007_PRODUCT_IMPLIED / printed == pytest.approx(6.4)


def test_minnitt_2007_apendice_la_parte_que_si_cuadra_es_el_tamano_de_liberacion():
    checks = v.minnitt_2007_liberation()
    assert all(c.ok for c in checks)
    assert checks[0].calculated == pytest.approx(0.001337, abs=1e-6)


def test_el_ejemplo_del_apendice_tambien_falla_por_el_mismo_factor():
    printed = gy.variance_classic(19_300_000.0, 0.5, 0.25, 0.000035, 1.25, 10_000.0)
    assert printed == pytest.approx(0.016493, abs=1e-5)  # el artículo publica 0,105555
    assert v.MINNITT_2007_APPENDIX["sigma2"] / printed == pytest.approx(6.4, rel=1e-3)
