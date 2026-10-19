"""Sedimentación: Coe y Clevenger (1916), la tabla de Vale (Torquato y Luz, 2011), Kynch sobre una
curva sintética exacta y la construcción de Talmage-Fitch. Los cortes se fijaron ANTES de correr
(ver `muestreo/sedimentacion_datos.py`)."""

import math

import numpy as np
import pytest

from muestreo import sedimentacion as sd
from muestreo import sedimentacion_datos as dd

LUZ = (0.4, 0.035, 1.591, 203.0)


@pytest.fixture(scope="module")
def sintetica():
    return dd.curva_sintetica()


@pytest.fixture(scope="module")
def luz():
    return sd.curva_luz(*LUZ, 86400.0, 300)


# ------------------------------------------------------------------ Coe y Clevenger (1916)
def test_el_ejemplo_de_nipissing_da_4_31_431_y_23_4():
    a = sd.coe_clevenger_pies2_ton_dia(4.0, 1.12, 0.893)
    assert round(a, 2) == 4.31 and round(a * 100) == 431
    assert round(sd.diametro_pies(431.0), 1) == 23.4 and round(sd.diametro_pies(a * 100), 1) == 23.4
    assert all(c.ok for c in dd.coe_checks() if c.kind != "ensayo")


def test_la_formula_de_coe_clevenger_es_la_de_la_pagina_372():
    # A = 2000 (F − D) / (24 · 62,35 · R) = 2000 / (24 (62,35 R / (F − D)))
    f, d, r = 4.0, 1.12, 0.893
    assert sd.coe_clevenger_pies2_ton_dia(f, d, r) == pytest.approx(
        2000.0 / (24.0 * (62.35 * r / (f - d))), rel=1e-12
    )
    assert sd.coe_clevenger_pies2_ton_dia(f, d, r) == pytest.approx(4.3105, abs=1e-3)


def test_las_unidades_si_coinciden_con_las_de_1916_salvo_la_densidad_del_agua():
    ft2_por_ton_corta_dia = sd.coe_clevenger_pies2_ton_dia(4.0, 1.12, 0.893)
    si = sd.coe_clevenger_m2_t_dia(4.0, 1.12, 0.893 * 0.3048)
    convertida = ft2_por_ton_corta_dia * 0.09290304 / 0.90718474
    assert si == pytest.approx(convertida, rel=2e-3)  # 62,35 lb/pie³ frente a 1000 kg/m³
    assert si == pytest.approx(0.441, abs=1e-3)


@pytest.mark.parametrize(
    "args",
    [(1.0, 1.12, 0.5), (4.0, 4.0, 0.5), (4.0, 1.12, 0.0), (4.0, -1.0, 0.5),
     (float("nan"), 1.0, 0.5), (4.0, 1.0, True)],
)  # fmt: skip
def test_coe_clevenger_rechaza_datos_imposibles(args):
    with pytest.raises(sd.SedimentacionError) as err:
        sd.coe_clevenger_pies2_ton_dia(*args)
    assert err.value.code == "coe"


def test_de_los_cinco_ensayos_de_nipissing_cuadran_2_y_3_y_los_otros_se_listan():
    rows = {c.label: c for c in dd.coe_checks() if c.kind == "ensayo"}
    assert [rows[str(i)].ok for i in range(1, 6)] == [False, True, True, False, False]
    assert [round(rows[str(i)].calculated, 3) for i in (1, 4, 5)] == [2.992, 4.214, 4.188]
    assert all(rows[k].note == "cc_d" for k in ("1", "4", "5"))


# ------------------------------------------------------------------ Vale
def test_los_31_diametros_de_la_tabla_1_salen_al_metro():
    assert len(dd.VALE_T1) == 31
    for _m, _q, _a, tph, _d, _c1, _c2, au, diam in dd.VALE_T1:
        assert round(sd.diametro_desde_area_unitaria(au, tph)) == diam


def test_29_de_31_areas_unitarias_salen_y_las_dos_de_alegria_se_listan():
    bad = [c for c in dd.vale_t1_checks() if c.kind == "area" and not c.ok]
    assert [c.label for c in bad] == ["12", "13"]  # las dos filas de lama de Alegría
    assert [(c.published, round(c.calculated, 4)) for c in bad] == [
        (0.987, 0.9784),
        (0.521, 0.5167),
    ]
    assert dd.summary()["v1"] == (60, 62)


def test_el_area_unitaria_es_pi_d2_sobre_4_entre_t_h_por_24():
    assert sd.area_unitaria_m2_t_dia(73, 143) == pytest.approx(1.2195, abs=1e-4)  # Cauê, lama
    assert round(sd.area_unitaria_m2_t_dia(100, 190), 3) == 1.722  # Conceição, lama
    assert sd.area_circulo_m2(30.0) == pytest.approx(706.86, abs=0.005)


def test_la_tabla_2_da_0_573_y_el_factor_es_0_64():
    assert round(sd.area_unitaria_m2_t_dia(30.0, 51.4), 3) == 0.573
    assert all(c.ok for c in dd.vale_t2_checks())
    assert round(dd.factor_vale(), 2) == 0.64 and dd.factor_vale() == pytest.approx(
        0.6381, abs=1e-4
    )
    assert dd.factor_inverso() == pytest.approx(1.567, abs=1e-3)  # el texto lo divide al revés
    assert (sd.FACTOR_VALE_LAMAS, sd.FACTOR_VALE_PELLET) == (0.64, 1.3)


def test_la_tabla_3_da_los_diametros_la_media_y_el_factor():
    checks = dd.vale_t3_checks()
    assert len(checks) == 10 and all(c.ok for c in checks)
    assert [round(sd.diametro_desde_area_unitaria(r[5], 157)) for r in dd.VALE_T3] == [
        71, 66, 66, 61, 56, 68, 65,
    ]  # fmt: skip


def test_dimensionar_aplica_el_factor_al_area_y_da_el_diametro():
    area, d = sd.dimensionar(0.898, 157.0)
    assert area == pytest.approx(0.898 * 157 * 24) and d == pytest.approx(65.637, abs=0.001)
    area2, d2 = sd.dimensionar(0.898, 157.0, sd.FACTOR_VALE_LAMAS)
    assert area2 == pytest.approx(area * 0.64) and d2 == pytest.approx(d * 0.8)
    for bad in ((0.0, 1, 1), (1, 0, 1), (1, 1, -1), (float("nan"), 1, 1)):
        with pytest.raises(sd.SedimentacionError):
            sd.dimensionar(*bad)


def test_la_concentracion_en_t_m3_sale_de_la_densidad_de_la_pulpa():
    assert sd.concentracion_t_m3(0.30, 4.0) == pytest.approx(0.30 / (0.30 / 4.0 + 0.70), rel=1e-12)
    assert sd.concentracion_t_m3(0.5, 1.0) == pytest.approx(0.5)  # solo agua en el medio
    for bad in (0.0, 1.0, -0.1, float("nan")):
        with pytest.raises(sd.SedimentacionError):
            sd.concentracion_t_m3(bad, 4.0)


# ------------------------------------------------------------------ Luz y la curva
def test_la_ecuacion_1_de_luz_y_su_derivada():
    z0, zi, a, b = LUZ
    assert sd.luz_altura(0.0, z0, zi, a, b) == z0
    assert sd.luz_altura(b, z0, zi, a, b) == pytest.approx((z0 + zi) / 2)  # b: la mitad del camino
    assert sd.luz_altura(1e9, z0, zi, a, b) == pytest.approx(zi, abs=1e-6)
    for t in (100.0, 420.0, 900.0):
        h = 1e-4
        num = (sd.luz_altura(t + h, z0, zi, a, b) - sd.luz_altura(t - h, z0, zi, a, b)) / (2 * h)
        assert sd.luz_velocidad_m_s(t, z0, zi, a, b) == pytest.approx(num, rel=1e-6)


def test_el_interpolante_da_la_velocidad_de_luz_con_menos_de_1_por_ciento(luz):
    for t in (200.0, 420.0, 800.0):
        exacta = -sd.luz_velocidad_m_s(t, *LUZ) * 3600
        assert luz.velocidad_m_h(t) == pytest.approx(exacta, rel=0.01)
    assert luz.altura(0) == 0.4 and luz.altura(1e9) == luz.h_m[-1]  # fuera del rango, se acota


@pytest.mark.parametrize(
    ("t", "h", "code"),
    [
        ((0, 1, 2), (1, 0.9, 0.8), "filas"),
        ((0, 1, 2, 3), (1, 0.9, 0.8), "filas"),
        ((0, 1, 2, float("nan")), (1, 0.9, 0.8, 0.7), "numero"),
        ((0, 1, 2, 3), (1, 0.9, float("inf"), 0.7), "numero"),
        ((0, 1, 2, 3), (1, 0.9, -0.1, 0.7), "numero"),
        ((1, 2, 3, 4), (1, 0.9, 0.8, 0.7), "origen"),
        ((0, 2, 1, 3), (1, 0.9, 0.8, 0.7), "orden"),
        ((0, 1, 1, 3), (1, 0.9, 0.8, 0.7), "orden"),
        ((0, 1, 2, 3), (1, 0.9, 0.95, 0.7), "sube"),
    ],
)
def test_una_curva_imposible_se_rechaza_con_su_codigo(t, h, code):
    with pytest.raises(sd.SedimentacionError) as err:
        sd.CurvaSed(tuple(float(x) for x in t), tuple(float(x) for x in h))
    assert err.value.code == code


def test_los_parametros_de_luz_se_validan():
    for bad in ((0.4, 0.5, 1.5, 200.0), (0.4, 0.035, 0.0, 200.0), (0.4, 0.035, 1.5, -1.0)):
        with pytest.raises(sd.SedimentacionError):
            sd.curva_luz(*bad, 1000.0)


# ------------------------------------------------------------------ Kynch sobre la curva sintética
def test_la_curva_sintetica_es_la_exacta_del_metodo_de_las_caracteristicas(sintetica):
    v0, cmax, n, c0, h0 = dd.SINT_V0, dd.SINT_CMAX, dd.SINT_N, dd.SINT_C0, dd.SINT_H0
    assert sintetica.h0 == h0 and sintetica.h_m[-1] > c0 * h0 / cmax  # la asíntota es C0 H0 / Cmax
    v_c0 = sd.v_richardson_zaki(c0, v0, cmax, n)
    assert sintetica.velocidad_m_h(30.0) == pytest.approx(v_c0, rel=1e-9)  # velocidad constante
    # t(C) y h(C) de las características: en C = 0,45, t = C0 H0 / (C² (−v'))
    c = 0.45
    t = c0 * h0 * cmax / (v0 * n * c**2 * (1 - c / cmax) ** (n - 1)) * 3600.0
    h = c0 * h0 / c - sd.v_richardson_zaki(c, v0, cmax, n) * t / 3600.0
    assert sintetica.altura(t) == pytest.approx(h, rel=1e-4)


def test_corte_kynch_recupera_v_de_c_a_2_por_ciento_en_c0_a_0_8_cmax():
    err, n, c_lo, c_hi = dd.kynch_error()
    assert err <= dd.SINT_CORTE and dd.kynch_checks()[0].ok
    assert err < 1e-3 and n > 500  # y con mucho margen (pinned: ~1e-5)
    assert c_lo == pytest.approx(dd.SINT_C0, rel=1e-6)
    assert c_hi <= 0.8 * dd.SINT_CMAX + 1e-12


def test_las_tangentes_dan_c_g_y_la_ordenada_de_kynch(sintetica):
    k = sd.kynch(sintetica, dd.SINT_C0)
    cols = (k.t_s, k.h_m, k.v_m_h, k.h_tangente_m, k.c_t_m3, k.g_t_m2_h)
    for t, h, v, htan, c, g in zip(*(x[::200] for x in cols), strict=True):
        assert htan == pytest.approx(h + v / 3600.0 * t, rel=1e-12)
        assert c == pytest.approx(dd.SINT_C0 * dd.SINT_H0 / htan, rel=1e-12)
        assert g == pytest.approx(v * c, rel=1e-12)
        assert c >= dd.SINT_C0 * (1 - 1e-6)


def test_la_sintetica_rechaza_parametros_fuera_de_la_teoria():
    for bad in ((8.0, 0.6, 4.0, 0.10, 0.4, 3600.0), (8.0, 0.6, 1.0, 0.3, 0.4, 3600.0),
                (8.0, 0.6, 4.0, 0.7, 0.4, 3600.0)):  # fmt: skip
        with pytest.raises(sd.SedimentacionError):
            sd.sintetica_kynch(*bad)


def test_el_flujo_limite_de_kynch_coincide_con_el_exacto_de_la_funcion_conocida(sintetica):
    k = sd.kynch(sintetica, dd.SINT_C0)
    gl, c_crit = sd.flujo_limite(k.c_t_m3, k.g_t_m2_h, dd.SINT_CU)
    area = sd.area_flujo_limite_m2_t_dia(gl)
    assert area == pytest.approx(dd.yoshioka_exacto_m2_t_dia(), rel=1e-6)
    assert dd.yoshioka_exacto_m2_t_dia() == pytest.approx(0.11867, abs=1e-5)
    assert dd.SINT_C0 < c_crit < dd.SINT_CU


def test_talmage_fitch_sin_compresion_coincide_en_hu_y_queda_abajo_antes():
    ty = dd.talmage_vs_yoshioka()
    assert abs(ty["dif_0.999"]) < 1e-3  # con la tangente donde la interfase llega a Hu
    assert ty["dif_0.9"] == pytest.approx(-1.08, abs=0.01)
    assert ty["dif_0.5"] == pytest.approx(-21.97, abs=0.01)  # y antes, menos área: no conservador
    assert ty["yoshioka_kynch"] == pytest.approx(ty["yoshioka"], rel=1e-6)


# ------------------------------------------------------------------ Talmage-Fitch
def _luz_conc():
    return sd.concentracion_t_m3(0.049, 4.0), sd.concentracion_t_m3(0.30, 4.0)


def test_talmage_fitch_de_la_fig_1_clasico(luz):
    c0, cu = _luz_conc()
    tf = sd.talmage_fitch(luz, c0, cu, 420.0)
    assert tf.hu_m == pytest.approx(0.4 * c0 / cu, rel=1e-12) and round(tf.hu_m, 4) == 0.0526
    assert round(tf.hc_m, 4) == 0.1223 and round(tf.v_c_m_h, 3) == 0.908
    assert round(tf.tu_s) == 697 and round(tf.area_unitaria_m2_t_dia, 3) == 0.396
    # la tangente pasa por (tc, hc) y por (tu, Hu)
    assert tf.tangente(tf.tc_s) == pytest.approx(tf.hc_m)
    assert tf.tangente(tf.tu_s) == pytest.approx(tf.hu_m, abs=1e-12)
    assert tf.area_unitaria_m2_t_dia == pytest.approx(tf.tu_s / 3600 / (c0 * 0.4) / 24)


def test_talmage_fitch_de_vale_usa_la_cota_a_24_h_y_da_mas_area(luz):
    c0, cu = _luz_conc()
    vale = sd.talmage_fitch(luz, c0, cu, 420.0, "vale", 0.035)
    clasico = sd.talmage_fitch(luz, c0, cu, 420.0)
    assert vale.hu_m == 0.035 and vale.tu_s > clasico.tu_s
    assert round(vale.area_unitaria_m2_t_dia, 3) == 0.436


@pytest.mark.parametrize(
    ("kw", "code"),
    [({"tc_s": 0.0}, "compresion"), ({"tc_s": 1e9}, "compresion"), ({"tc_s": 5000.0}, "tangente"),
     ({"tc_s": 420.0, "cu": 0.04}, "numero"), ({"tc_s": 420.0, "modo": "x"}, "numero")],
)  # fmt: skip
def test_talmage_fitch_rechaza_lo_imposible(luz, kw, code):
    c0, cu = _luz_conc()
    args = dict(curva=luz, c0=c0, cu=cu) | kw
    with pytest.raises(sd.SedimentacionError) as err:
        sd.talmage_fitch(**args)
    assert err.value.code == code


def test_roberts_encuentra_el_quiebre_de_dos_rectas_en_ln_h_menos_h_inf():
    h_inf, t_break = 0.1, 400.0
    ts = np.arange(0.0, 1201.0, 20.0)
    y = np.where(ts <= t_break, -ts / 100.0, -t_break / 100.0 - (ts - t_break) / 400.0)
    curva = sd.CurvaSed(tuple(float(x) for x in ts), tuple(float(h_inf + math.exp(v)) for v in y))
    assert sd.roberts_punto_compresion(curva, h_inf) == pytest.approx(t_break, abs=20.0)
    corta = sd.CurvaSed((0.0, 1.0, 2.0, 3.0), (1.0, 0.9, 0.8, 0.7))
    with pytest.raises(sd.SedimentacionError):
        sd.roberts_punto_compresion(corta, 0.1)


def test_la_curva_de_flujo_de_kynch_de_luz_arranca_en_la_velocidad_maxima(luz):
    c0, _ = _luz_conc()
    k = sd.kynch(luz, c0)
    assert c0 <= k.c_t_m3[0] < 1.05 * c0  # sin el arranque lento: empieza en la velocidad máxima
    assert k.v_m_h[0] == pytest.approx(max(k.v_m_h), rel=1e-3)
    assert min(k.c_t_m3) >= c0 * (1 - 1e-6) and max(k.v_m_h) == pytest.approx(3.03, abs=0.01)
    with pytest.raises(sd.SedimentacionError):
        sd.flujo_limite([0.5], [0.1], 0.3)  # ninguna concentración bajo Cu
    with pytest.raises(sd.SedimentacionError):
        sd.kynch(luz, 0.0)


def test_constantes_literales_del_metodo_y_de_los_cortes():
    assert (sd.LB_POR_PIE3_AGUA, sd.LB_POR_TON_CORTA, sd.HORAS_DIA) == (62.35, 2000.0, 24.0)
    assert (sd.FACTOR_VALE_LAMAS, sd.FACTOR_VALE_PELLET, sd.RHO_AGUA_T_M3) == (0.64, 1.3, 1.0)
    assert (dd.VALE_FACTOR, dd.SINT_CORTE, dd.SINT_RANGO) == (0.64, 0.02, 0.8)
    assert (dd.SINT_V0, dd.SINT_CMAX, dd.SINT_N, dd.SINT_C0) == (8.0, 0.60, 4.0, 0.30)
    assert (dd.CC_F, dd.CC_D, dd.CC_R, dd.CC_TON_DIA) == (4.0, 1.12, 0.893, 100.0)
