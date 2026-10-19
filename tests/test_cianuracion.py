"""Cianuración en botella: el cálculo contra las cifras de Roostaei, Kordparijaei y Mesroghli
(2026) (Tablas 4, 6 y 7, Ec. 3) y contra soluciones exactas. Los cortes se fijaron ANTES de correr
(ver `muestreo/cianuracion_datos.py`)."""

import numpy as np
import pytest

from muestreo import cianuracion as c
from muestreo import cianuracion_datos as cd

T, SOL, RES = list(cd.T_H), list(cd.SOLUCION_PPB), list(cd.RESIDUO_PPB)
REC = list(cd.RECUPERACION_PUB)


# ------------------------------------------------------------------ Tabla 4: recuperación y cabeza
def test_la_ley_de_cabeza_de_cada_fila_de_la_tabla_4_es_1070_ppb_al_redondeo_publicado():
    heads = [c.cabeza_desde_recuperacion(r, p) for r, p in zip(RES, REC, strict=True)]
    assert min(heads) == pytest.approx(1069.59, abs=0.01)
    assert max(heads) == pytest.approx(1070.75, abs=0.01)
    checks = cd.table4_checks()
    assert all(x.ok for x in checks if x.kind == "cabeza") and len(checks) == 14


def test_la_recuperacion_con_s0_1070_es_la_publicada_a_dos_decimales():
    for res, pub in zip(RES, REC, strict=True):
        assert round(c.recuperacion_pct(res, 1070.0), 2) == pub
    assert all(x.ok for x in cd.table4_checks() if x.kind == "recuperacion")


def test_el_balance_de_la_tabla_4_da_la_recuperacion_y_avisa_solo_del_punto_de_2_h():
    b = c.balance(T, SOL, RES)
    assert [round(x, 2) for x in b.recuperacion_pct] == REC
    assert [(a.code, a.t_h) for a in b.avisos] == [("no_monotona", 2.0)]
    # la cabeza por balance (residuo + F·solución) queda a ~1 % de 1 070 en las 7 filas
    assert all(abs(h / 1070.0 - 1) < 0.015 for h in b.cabeza_ppb)
    assert b.au_solucion_ppb[0] == pytest.approx(1.935 * 446)


def test_el_balance_avisa_cuando_la_cabeza_no_cuadra():
    b = c.balance(T, SOL, RES, cabeza=1070.0, factor=1.5)  # F distinto: las cabezas se apartan
    assert {a.code for a in b.avisos} >= {"cabeza"}
    assert all(a.value < 0 for a in b.avisos if a.code == "cabeza")


def test_una_serie_creciente_no_da_avisos():
    b = c.balance([1, 2, 3], [400, 450, 480], [300, 200, 150], cabeza=1070.0, factor=1.935)
    assert [a.code for a in b.avisos if a.code == "no_monotona"] == []


@pytest.mark.parametrize(
    ("args", "code"),
    [
        (([], [], []), "filas"),
        (([1, 2], [1], [1, 2]), "filas"),
        (([1, 2], [1, 2], [float("nan"), 1]), "numero"),
        (([1, 2], [float("inf"), 2], [1, 2]), "numero"),
        (([1, -2], [1, 2], [1, 2]), "numero"),
        (([0, 2], [1, 2], [1, 2]), "numero"),
        (([1, 2], ["1", 2], [1, 2]), "numero"),
        (([1, 2], [True, 2], [1, 2]), "numero"),
        (([2, 1], [1, 2], [1, 2]), "orden"),
        (([1, 1], [1, 2], [1, 2]), "orden"),
        (([1, 2], [1, 2], [5000, 2]), "residuo_mayor"),
    ],
)
def test_una_serie_imposible_se_rechaza_con_su_codigo(args, code):
    with pytest.raises(c.SerieInvalida) as err:
        c.balance(*args)
    assert err.value.code == code


def test_cabeza_o_factor_no_validos_se_rechazan():
    for kw in ({"cabeza": 0.0}, {"cabeza": float("nan")}, {"factor": -1.0}):
        with pytest.raises(c.SerieInvalida):
            c.balance(T, SOL, RES, **kw)


# ------------------------------------------------------------------ Tabla 6: L, M y N
def test_tabla_6_l_y_m_a_tres_decimales_y_n_con_la_b_inferida():
    checks = cd.table6_checks()
    assert len(checks) == 22 and all(x.ok for x in checks)
    t = c.terminos(REC)
    assert [round(float(x), 3) for x in t["difusion"]] == list(cd.L_PUB.values())
    assert [round(float(x), 3) for x in t["reaccion"]] == list(cd.M_PUB.values())


def test_n_menos_l_sobre_3_es_b_por_m_y_la_b_inferida_cae_en_el_rango_publicado():
    t = c.terminos(REC)
    n = (1 - 2 * np.array(REC) / 300) - (1 - np.array(REC) / 100) ** (2 / 3)
    np.testing.assert_allclose(n, t["difusion"] / 3, atol=1e-12)  # N − B·M = L/3
    iv = cd.b_intervals()
    assert iv["N1"][0] <= c.B_N1 <= iv["N1"][1]
    assert iv["N2"][0] <= c.B_N2 <= iv["N2"][1]
    assert iv["N1"] == pytest.approx((0.7028, 0.7039), abs=1e-4)
    assert iv["N2"] == pytest.approx((0.7500, 0.7505), abs=1e-4)


def test_terminos_rechaza_recuperaciones_fuera_de_0_a_100():
    for bad in ([0.0], [100.0], [-1.0], [float("nan")], [120.0]):
        with pytest.raises(c.SerieInvalida):
            c.terminos(bad)


def test_el_termino_y_su_inversa_son_inversas():
    for model in c.MODELOS_LINEALES:
        for x in (0.05, 0.4, 0.795, 0.95):
            y = c.termino_de_x(model, x, c.B_N2)
            assert c.x_de_termino(model, y, c.B_N2) == pytest.approx(x, abs=1e-10)
        assert c.x_de_termino(model, -1.0, c.B_N1) == 0.0
        assert c.x_de_termino(model, 99.0, c.B_N1) == 1.0


# ------------------------------------------------------------------ Tabla 7: regresiones
def test_tabla_7_cinco_de_seis_regresiones_cuadran_y_la_m1_no():
    checks = cd.table7_checks()
    assert len(checks) == 18
    bad = [(x.label, x.kind) for x in checks if not x.ok]
    assert bad == [("M1", "r2"), ("M1", "intercepto"), ("M1", "pendiente")]
    for x in checks:
        if x.label != "M1":
            assert x.ok, (x.label, x.kind)


def test_la_fila_m1_no_sale_de_los_datos_y_sus_propios_f_y_r2_son_coherentes():
    m1 = cd.regressions()["M1"]
    assert (round(m1.r2, 4), round(m1.intercepto, 4), round(m1.pendiente, 5)) == (
        0.9957, 0.3894, 0.01789
    )  # fmt: skip
    assert cd.m1_implied_r2() == pytest.approx(0.99419, abs=1e-5)  # el F impreso, 171,04
    assert m1.f == pytest.approx(231.8, abs=0.5)  # el F que dan los datos
    # las demás filas: el F impreso sí cuadra con su R² (SPSS)
    for name, f_pub, df2 in (("L1", 209.446, 1), ("L2", 143.765, 2), ("M2", 166.276, 2),
                             ("N1", 230.640, 1), ("N2", 154.014, 2)):  # fmt: skip
        assert cd.regressions()[name].f == pytest.approx(f_pub, rel=0.01), (name, df2)


def test_las_regresiones_coinciden_con_numpy_polyfit():
    x = np.array([1.0, 3.0, 7.0, 11.0])
    y = np.array([0.3, 0.45, 0.52, 0.6])
    reg = c.regresion(x, y)
    slope, intercept = np.polyfit(x, y, 1)
    assert reg.pendiente == pytest.approx(slope) and reg.intercepto == pytest.approx(intercept)
    assert reg.r2 == pytest.approx(np.corrcoef(x, y)[0, 1] ** 2)
    assert reg.f == pytest.approx(reg.r2 / (1 - reg.r2) * 2)
    assert reg.en(5.0) == pytest.approx(intercept + slope * 5)
    assert reg.n == 4


def test_una_regresion_necesita_al_menos_tres_puntos_y_tiempos_distintos():
    with pytest.raises(c.SerieInvalida):
        c.regresion([1.0, 2.0], [1.0, 2.0])
    with pytest.raises(c.SerieInvalida):
        c.regresion([2.0, 2.0, 2.0], [1.0, 2.0, 3.0])


def test_la_seleccion_de_puntos_deja_fuera_solo_el_de_2_h():
    assert c.puntos_usados(REC) == [True, False, True, True, True, True, True]
    assert c.puntos_usados([10, 20, 30]) == [True, True, True]
    assert c.puntos_usados([50, 40, 30]) == [False, False, True]
    a = c.ajustar_lineal("difusion", T, REC)
    assert (a.indices1, a.indices2) == ((0, 2, 3), (3, 4, 5, 6))  # 1, 3, 7 h y 7, 11, 24, 48 h


def test_un_tramo_con_menos_de_tres_puntos_queda_sin_ajustar():
    a = c.ajustar_lineal("reaccion", T, REC, corte_h=2.0)
    assert a.tramo1 is None and a.tramo2 is not None
    assert c.recuperacion_en_cero(a) is None
    with pytest.raises(ValueError):
        c.ajustar_lineal("potencial", T, REC)


# ------------------------------------------------------------------ Ec. 3: potencial
def test_ec_3_a_b_y_r2_con_los_siete_puntos():
    p = c.ajustar_potencial(T, RES)
    assert round(p.a_ppb, 3) == 228.046 and round(p.b, 3) == 0.332 and round(p.r2, 3) == 0.937
    assert all(x.ok for x in cd.equation3_checks())


def test_ec_3_sin_el_punto_de_2_h_no_reproduce_lo_publicado():
    keep = [0, 2, 3, 4, 5, 6]
    p = c.ajustar_potencial([T[i] for i in keep], [RES[i] for i in keep])
    assert (round(p.a_ppb, 1), round(p.b, 3), round(p.r2, 3)) == (246.5, 0.356, 0.965)


def test_el_potencial_recupera_los_parametros_de_datos_exactos():
    t = np.array([1.0, 2.0, 5.0, 10.0, 40.0])
    p = c.ajustar_potencial(t, 300.0 * t**-0.4)
    assert (p.a_ppb, p.b, p.r2) == pytest.approx((300.0, 0.4, 1.0), rel=1e-12)
    assert p.residuo(10.0) == pytest.approx(300.0 * 10.0**-0.4)
    with pytest.raises(c.SerieInvalida):
        c.ajustar_potencial([1.0, 2.0], [5.0, 4.0])


# ------------------------------------------------------------------ primer orden con meseta
def test_el_primer_orden_recupera_los_parametros_de_datos_exactos():
    t = np.array([0.5, 1.0, 2.0, 5.0, 10.0, 30.0])
    fit = c.ajustar_primer_orden(t, 90.0 * (1 - np.exp(-0.3 * t)))
    assert (fit.r_inf, fit.k_por_h, fit.r2) == pytest.approx((90.0, 0.3, 1.0), rel=1e-6)
    assert fit.recuperacion(0.0) == 0.0
    assert fit.recuperacion(1e6) == pytest.approx(90.0, rel=1e-9)


def test_el_primer_orden_ajusta_mal_la_tabla_4_resultado_declarado():
    fit = c.ajustar_primer_orden(T, REC)
    assert fit.r_inf == pytest.approx(89.24, abs=0.01)
    assert fit.k_por_h == pytest.approx(2.127, abs=0.005)
    assert fit.r2 == pytest.approx(0.480, abs=0.005)  # una constante no alcanza (dos etapas)
    # y es la solución de mínimos cuadrados: moverla empeora el error
    sse = lambda r, k: float(np.sum((r * (1 - np.exp(-k * np.array(T))) - REC) ** 2))  # noqa: E731
    best = sse(fit.r_inf, fit.k_por_h)
    assert all(
        sse(fit.r_inf * a, fit.k_por_h * b) >= best for a in (0.99, 1.01) for b in (0.9, 1.1)
    )


# ------------------------------------------------------------------ todos los modelos
@pytest.fixture(scope="module")
def modelos():
    return c.ajustar_modelos(T, RES, 1070.0)


def test_los_interceptos_del_primer_tramo_no_pasan_por_el_origen(modelos):
    got = {m: modelos.lineales[m].tramo1 for m in c.MODELOS_LINEALES}
    assert round(got["difusion"].intercepto, 3) == 0.335
    assert round(got["reaccion"].intercepto, 3) == 0.389
    assert round(got["mixto"].intercepto, 3) == 0.385
    assert all(r.r2 > 0.995 for r in got.values())  # R² alto con 3 puntos
    assert all(r.n == 3 for r in got.values())
    zeros = [c.recuperacion_en_cero(modelos.lineales[m]) for m in c.MODELOS_LINEALES]
    assert zeros == pytest.approx([77.1, 77.2, 77.1], abs=0.1)  # ya "disuelto" en t = 0
    second = [modelos.lineales[m].tramo2.intercepto for m in c.MODELOS_LINEALES]
    assert min(second) > 0.5 and max(second) < 0.55


def test_cada_modelo_reproduce_sus_puntos_y_el_potencial_gana_en_error(modelos):
    rmse = {m: c.rmse_recuperacion(modelos, m, T, REC) for m in c.MODELOS}
    assert rmse["potencial"] == pytest.approx(1.56, abs=0.01)
    assert rmse["primer_orden"] == pytest.approx(3.61, abs=0.01)
    for m in c.MODELOS_LINEALES:
        assert rmse[m] == pytest.approx(1.8, abs=0.05)
    assert rmse["potencial"] < min(rmse[m] for m in c.MODELOS_LINEALES) < rmse["primer_orden"]


def test_la_curva_de_un_modelo_pasa_por_la_recta_ajustada(modelos):
    # la recuperación del modelo mixto en un punto del tramo 1 sale de invertir N en su recta
    a = modelos.lineales["mixto"]
    t = 3.0
    x = c.recuperacion_modelo(modelos, "mixto", t) / 100.0
    assert c.termino_de_x("mixto", x, c.B_N1) == pytest.approx(a.tramo1.en(t), abs=1e-9)
    t = 24.0
    x = c.recuperacion_modelo(modelos, "mixto", t) / 100.0
    assert c.termino_de_x("mixto", x, c.B_N2) == pytest.approx(a.tramo2.en(t), abs=1e-9)
    pot = c.recuperacion_modelo(modelos, "potencial", 48.0)
    assert pot == pytest.approx(100 * (1 - 228.046 * 48**-0.332 / 1070), abs=0.01)


def test_pocos_datos_dan_modelos_sin_ajustar():
    m = c.ajustar_modelos([1.0, 2.0], [200.0, 150.0], 1070.0)
    assert m.potencial is None and m.primer_orden is None
    assert c.recuperacion_modelo(m, "potencial", 1.0) is None
    assert c.recuperacion_modelo(m, "primer_orden", 1.0) is None
    assert c.recuperacion_modelo(m, "difusion", 1.0) is None
    assert c.rmse_recuperacion(m, "potencial", [1.0, 2.0], [80.0, 85.0]) is None


def test_la_curva_potencial_baja_a_cero_en_cero_y_es_creciente(modelos):
    ts = np.linspace(0.5, 48.0, 50)
    ys = np.array(c.curva(modelos, "potencial", ts))
    assert np.all(np.diff(ys) > 0)
