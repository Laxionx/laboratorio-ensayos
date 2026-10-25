"""Control de calidad (`muestreo/qaqc.py`): cada regla contra su cita, con casos que la disparan
y casos que no; la certificación por recorte; Thompson-Howarth; HARD; blancos; las tablas pegadas
con entradas malas; y los cortes de validación fijados antes de correr."""

import math

import pytest

from muestreo import qaqc as q
from muestreo import qaqc_datos as d
from muestreo import qaqc_gemas as g
from muestreo import qaqc_validacion as v

MU, SD = 1.0, 0.25  # 2 SD = 0,5 y 3 SD = 0,75: exactos en binario


def estados(valores):
    return [p.estado for p in q.clasificar_crm(valores, MU, SD)]


# ------------------------------------------------------------------ CRM: reglas de un punto
def test_dentro_de_2_sd_incluido_el_borde_es_aceptable():
    assert estados([1.0, 1.5, 0.5, 1.2]) == [q.OK] * 4  # |X − μ| ≤ 2σ (Abzalov, Eq. 21)


def test_fuera_de_2_sd_es_advertencia_a_los_dos_lados():
    assert estados([1.51]) == [q.FUERA_2SD] and estados([0.49]) == [q.FUERA_2SD]
    assert estados([1.51, 1.0, 0.49]) == [q.FUERA_2SD, q.OK, q.FUERA_2SD]


def test_fuera_de_3_sd_es_rechazo_y_el_borde_no_lo_es():
    assert estados([1.75]) == [q.FUERA_2SD]  # 3 SD exactos: no es «fuera de 3 SD»
    assert estados([1.76]) == [q.FUERA_3SD] and estados([0.24]) == [q.FUERA_3SD]


def test_dos_seguidos_fuera_de_2_sd_disparan_la_regla_en_el_segundo():
    assert estados([1.6, 1.6]) == [q.FUERA_2SD, q.DOS_SEGUIDOS]
    assert estados([1.6, 0.4]) == [q.FUERA_2SD, q.DOS_SEGUIDOS]  # Rainy River: sin exigir un lado
    assert estados([1.6, 1.0, 1.6]) == [q.FUERA_2SD, q.OK, q.FUERA_2SD]  # no son consecutivos


def test_el_rechazo_a_3_sd_tambien_cuenta_como_fuera_de_2_sd_para_el_siguiente():
    assert estados([1.9, 1.6]) == [q.FUERA_3SD, q.DOS_SEGUIDOS]


def test_la_clasificacion_calcula_z_con_el_valor_y_la_sd():
    p = q.clasificar_crm([1.75], MU, SD)[0]
    assert (p.n, p.valor, p.z) == (1, 1.75, 3.0)


@pytest.mark.parametrize(("mu", "sd"), [(1.0, 0.0), (1.0, -0.1), (1.0, math.nan), (math.inf, 1.0)])
def test_un_crm_sin_sd_valida_no_se_evalua(mu, sd):
    with pytest.raises(q.QaqcError) as err:
        q.clasificar_crm([1.0], mu, sd)
    assert err.value.code == "crm"


# ------------------------------------------------------------------ CRM: veredicto del lote
def veredicto(valores):
    return q.veredicto_crm(q.clasificar_crm(valores, MU, SD), MU)


def test_un_resultado_fuera_de_3_sd_rechaza_el_lote():
    r = veredicto([1.0] * 29 + [1.8])
    assert (r.veredicto, r.n_fuera_3sd, r.tasa_3sd) == (q.RECHAZAR, 1, 1 / 30)


def test_dos_seguidos_fuera_de_2_sd_piden_re_ensayo():
    r = veredicto([1.0] * 28 + [1.6, 1.6])
    assert (r.veredicto, r.n_pares, r.n_fuera_2sd) == (q.REENSAYAR, 1, 2)


def test_con_mas_del_5_por_ciento_fuera_de_2_sd_hay_aviso_y_con_menos_pasa():
    assert veredicto([1.0] * 29 + [1.6]).veredicto == q.PASA  # 1/30 = 3,3 %
    assert veredicto([1.0] * 9 + [1.6]).veredicto == q.AVISO  # 1/10 = 10 %
    assert veredicto([1.0] * 19 + [1.6]).veredicto == q.PASA  # 1/20 = 5 % exacto: no más del 5 %


def test_el_rechazo_manda_sobre_el_re_ensayo_y_este_sobre_el_aviso():
    assert veredicto([1.6, 1.6, 1.9]).veredicto == q.RECHAZAR
    assert veredicto([1.6, 1.6]).veredicto == q.REENSAYAR


def test_la_media_y_el_sesgo_del_lote():
    r = veredicto([1.0, 1.02, 0.98, 1.04])
    assert r.media == pytest.approx(1.01) and r.sesgo_pct == pytest.approx(1.0)
    assert q.sesgo_pct(0.978, 0.989) == pytest.approx(-1.1122, abs=1e-3)


def test_un_lote_sin_resultados_no_se_califica():
    with pytest.raises(q.QaqcError):
        q.veredicto_crm([], MU)


# ------------------------------------------------------------------ certificar por recorte
def test_el_recorte_quita_lo_que_cae_fuera_de_media_mas_menos_2_sd_y_recalcula():
    x = [10.0] * 20 + [30.0]
    c = q.certificar_recorte(x)
    assert c.n_total == 21 and c.n == 20 and c.media == 10.0 and c.sd == 0.0
    assert c.retenidos[-1] is False and all(c.retenidos[:-1])


def test_el_limite_del_recorte_es_media_mas_menos_k_sd():
    x = [-1.0, 1.0] * 5  # media 0 y SD = √(10/9) = 1,054
    assert q.certificar_recorte(x, k=1.0).n == 10  # |1| < 1,054: se conservan
    with pytest.raises(q.QaqcError) as err:
        q.certificar_recorte(x, k=0.9)  # |1| > 0,949: se descartan todos
    assert err.value.code == "recorte"
    assert q.certificar_recorte(x, k=3.0).alto == pytest.approx(
        3 * q.certificar_recorte(x).sd_total
    )


def test_el_recorte_es_de_una_sola_pasada_y_dos_sd_es_el_doble_de_la_sd():
    c = q.certificar_recorte(d.CDN_RESULTADOS)
    assert c.dos_sd == 2 * c.sd and c.media_total != c.media
    assert c.n == sum(c.retenidos)


def test_certificar_pide_resultados_finitos_y_suficientes():
    for malo in ([1.0] * 4, [1.0] * 5 + [math.nan], [1.0] * 5 + [math.inf]):
        with pytest.raises(q.QaqcError):
            q.certificar_recorte(malo)
    with pytest.raises(q.QaqcError):
        q.certificar_recorte([1.0] * (q.MAX_FILAS + 1))


# ------------------------------------------------------------------ Thompson-Howarth y HARD
def test_los_coeficientes_de_las_lineas_son_los_de_la_hoja_del_tutorial():
    assert q.coeficiente_th(q.Z_P90, 10) == pytest.approx(0.11631, rel=1e-4)
    assert q.coeficiente_th(q.Z_P99, 10) == pytest.approx(0.182135, rel=1e-4)
    assert q.coeficiente_th(q.Z_P90, 20) == pytest.approx(2 * q.coeficiente_th(q.Z_P90, 10))
    assert q.linea_th(5.0, 10, q.Z_P90) == pytest.approx(5 * 0.11631, rel=1e-4)


def test_un_par_dentro_o_fuera_de_las_lineas_a_p_10():
    # media 10: línea 90 = 1,1631 y línea 99 = 1,82135
    dentro = (9.5, 10.5)  # |d| = 1,0
    entre = (9.3, 10.7)  # |d| = 1,4: fuera de la 90, dentro de la 99
    fuera = (8.5, 11.5)  # |d| = 3,0: fuera de las dos
    r = q.evaluar_th([dentro, entre, fuera], 10)
    assert (r.n, r.dentro90, r.dentro99) == (3, 1, 2)
    assert r.pct90 == pytest.approx(100 / 3) and not r.pasa


def test_con_p_20_las_lineas_se_abren():
    # media 10: línea 90 = 2,3262 y línea 99 = 3,6427
    r = q.evaluar_th([(9.3, 10.7), (8.5, 11.5)], 20)  # |d| = 1,4 y 3,0
    assert (r.dentro90, r.dentro99) == (1, 2)


def test_un_par_con_media_cero_no_tiene_linea_y_cuenta_fuera():
    r = q.evaluar_th([(0.0, 0.0), (-0.1, 0.1), (1.0, 1.0)], 10)
    assert (r.n, r.sin_media, r.dentro90, r.dentro99) == (3, 2, 1, 1)


def test_el_tutorial_pide_90_y_99_por_ciento_a_la_vez():
    ok = q.evaluar_th([(10.0, 10.0)] * 100, 10)
    assert ok.pasa and ok.pct90 == ok.pct99 == 100.0
    casi = q.evaluar_th([(10.0, 10.0)] * 89 + [(8.0, 12.0)] * 11, 10)
    assert casi.pct90 == 89.0 and not casi.pasa
    entre = q.evaluar_th([(10.0, 10.0)] * 92 + [(9.3, 10.7)] * 8, 10)  # |d| = 1,4: entre las dos
    assert (entre.pct90, entre.pct99) == (92.0, 100.0) and entre.pasa
    solo_90 = q.evaluar_th([(10.0, 10.0)] * 95 + [(8.0, 12.0)] * 5, 10)  # |d| = 4: fuera de ambas
    assert (solo_90.pct90, solo_90.pct99) == (95.0, 95.0) and not solo_90.pasa


def test_th_pide_pares_y_una_precision_valida():
    with pytest.raises(q.QaqcError):
        q.evaluar_th([], 10)
    for p in (0, -5, math.nan):
        with pytest.raises(q.QaqcError):
            q.evaluar_th([(1.0, 1.0)], p)


def test_hard_es_la_mitad_de_la_diferencia_relativa_y_sale_de_la_formula_de_abzalov():
    assert q.hard_pct(10.0, 12.0) == pytest.approx(100 * 2 / 22)
    assert q.rpd_pct(10.0, 12.0) == pytest.approx(2 * q.hard_pct(10.0, 12.0))
    assert q.hard_pct(0.0, 0.0) is None and q.rpd_pct(0.0, 0.0) is None
    a, b = 3.0, 4.0  # HARD = CV% / √2 con CV% = (|a − b| / √2) / media (Abzalov, Eq. 22)
    cv = 100 * (abs(a - b) / math.sqrt(2)) / ((a + b) / 2)
    assert q.hard_pct(a, b) == pytest.approx(cv / math.sqrt(2))


def test_el_borde_del_umbral_de_duplicados_sigue_el_texto_de_cada_regla():
    # campo y rechazo: «menos de 20 %» (RPD = 20 exacto no cuenta); pulpa: «dentro de 10 %» (sí)
    assert q.evaluar_duplicados([(9.0, 11.0)], "campo").n_bajo == 0
    assert q.evaluar_duplicados([(9.0, 11.0)], "rechazo").n_bajo == 0
    assert q.evaluar_duplicados([(95.0, 105.0)], "pulpa").n_bajo == 1
    assert q.evaluar_duplicados([(94.0, 106.0)], "pulpa").n_bajo == 0


def test_el_lote_de_duplicados_pasa_con_80_por_ciento_bajo_el_umbral():
    bien = [(10.0, 10.5)] * 8 + [(10.0, 15.0)] * 2  # 80 % bajo 20 %
    mal = [(10.0, 10.5)] * 79 + [(10.0, 15.0)] * 21  # 79 %
    assert q.evaluar_duplicados(bien, "campo").pasa and not q.evaluar_duplicados(mal, "campo").pasa
    assert q.evaluar_duplicados(bien, "campo").pct_bajo == 80.0


def test_los_pares_sin_suma_positiva_no_entran_en_el_porcentaje():
    r = q.evaluar_duplicados([(0.0, 0.0), (10.0, 10.0)], "campo")
    assert (r.n, r.n_evaluables, r.n_bajo) == (2, 1, 1)
    with pytest.raises(q.QaqcError):
        q.evaluar_duplicados([(0.0, 0.0)], "campo")
    with pytest.raises(q.QaqcError):
        q.evaluar_duplicados([(1.0, 1.0)], "otro")


# ------------------------------------------------------------------ blancos
def test_un_blanco_sobre_3_ld_es_alerta_y_sobre_10_ld_es_falla_y_el_borde_no_cuenta():
    ld = 0.5
    assert q.evaluar_blancos([0.1, 1.5], ld).veredicto == q.BLANCO_OK  # 3 × LD exacto: no supera
    r = q.evaluar_blancos([0.1, 1.6], ld)
    assert (r.veredicto, r.n_sobre_3, r.n_sobre_10) == (q.BLANCO_ALERTA, 1, 0)
    assert q.evaluar_blancos([0.1, 5.0], ld).veredicto == q.BLANCO_ALERTA  # 10 × LD exacto
    r = q.evaluar_blancos([0.1, 5.1, 2.0], ld)
    assert (r.veredicto, r.n_sobre_3, r.n_sobre_10) == (q.BLANCO_FALLA, 2, 1)
    assert r.pct_sobre_3 == pytest.approx(200 / 3) and r.pct_sobre_10 == pytest.approx(100 / 3)


def test_los_porcentajes_de_rainy_river_salen_de_558_blancos_con_uno_sobre_3_ld():
    ld = 0.005
    r = q.evaluar_blancos([0.001] * 557 + [0.02], ld)  # 1 de 558 sobre 3 × LD (0,015)
    assert round(r.pct_sobre_3, 2) == 0.18 and r.pct_sobre_10 == 0.0  # Tabla 11-13


def test_los_blancos_piden_un_limite_de_deteccion_valido():
    for ld in (0, -1, math.nan, math.inf):
        with pytest.raises(q.QaqcError):
            q.evaluar_blancos([0.1], ld)
    with pytest.raises(q.QaqcError):
        q.evaluar_blancos([], 0.005)


# ------------------------------------------------------------------ tablas pegadas malas
MALAS = [
    ([math.nan, math.nan], "filas"),  # todo vacío: sin resultados
    ([math.inf], "numero"),
    ([-math.inf], "numero"),
    (["1,5"], "numero"),
    (["<script>alert(1)</script>"], "numero"),
    ([True], "numero"),
    ([-0.1], "negativo"),
    ([[1.0]], "numero"),
]


@pytest.mark.parametrize(("filas", "codigo"), MALAS)
def test_las_series_malas_se_rechazan_con_un_codigo_y_sin_eco_del_texto(filas, codigo):
    with pytest.raises(q.QaqcError) as err:
        q.leer_serie(filas)
    assert err.value.code == codigo and "script" not in str(err.value)


def test_las_celdas_vacias_se_descartan_y_el_resto_se_conserva():
    assert q.leer_serie([None, 1, math.nan, 2.5, 0]) == [1.0, 2.5, 0.0]
    with pytest.raises(q.QaqcError):
        q.leer_serie([])
    with pytest.raises(q.QaqcError):
        q.leer_serie([1.0, 2.0], minimo=3)


def test_el_tope_de_filas_esta_declarado_y_se_aplica():
    assert q.MAX_FILAS == 2000
    assert len(q.leer_serie([1.0] * q.MAX_FILAS)) == q.MAX_FILAS
    with pytest.raises(q.QaqcError) as err:
        q.leer_serie([1.0] * (q.MAX_FILAS + 1))
    assert err.value.args_ == {"lo": 1, "hi": q.MAX_FILAS}
    with pytest.raises(q.QaqcError):
        q.leer_serie([None] * (3 * q.MAX_FILAS))
    with pytest.raises(q.QaqcError):
        q.leer_pares([[1.0, 1.0]] * (q.MAX_FILAS + 1))


def test_los_pares_pegados_se_validan_fila_por_fila():
    pares = q.leer_pares([[1, 2], [None, None], [math.nan, None], [3.5, 4]])
    assert pares == [(1.0, 2.0), (3.5, 4.0)]
    for filas, codigo in (
        ([[1.0, None]], "incompleta"),
        ([[None, 2.0]], "incompleta"),
        ([[1.0, "x"]], "numero"),
        ([[1.0, math.inf]], "numero"),
        ([[1.0, -2.0]], "negativo"),
        ([[None, None]], "filas"),
        ([], "filas"),
    ):
        with pytest.raises(q.QaqcError) as err:
            q.leer_pares(filas)
        assert err.value.code == codigo, filas


# ------------------------------------------------------------------ los datos copiados
def test_los_150_resultados_de_cdn_traen_15_laboratorios_por_fila_y_las_medias_publicadas():
    assert len(d.CDN_GS2X) == 10 and all(len(f) == 15 for f in d.CDN_GS2X)
    assert len(d.CDN_RESULTADOS) == 150
    impresas = (2.37, 2.44, 2.50, 2.45, 2.50, 2.40, 2.31, 2.390, 2.39, 2.276, 2.281, 2.25, 2.53,
                2.47, 2.262)  # fila «Mean» del certificado  # fmt: skip
    for lab, impresa in enumerate(impresas):
        media = sum(f[lab] for f in d.CDN_GS2X) / 10
        assert abs(media - impresa) <= 0.0051, (lab + 1, media, impresa)


def test_los_104_pares_de_gemas_estan_completos():
    assert len(g.AG_PARES) == len(g.GE_PARES) == 104
    assert min(min(p) for p in g.AG_PARES) > 0
    assert sum(sum(p) <= 0 for p in g.GE_PARES) == 13  # bajo el límite de detección


def test_la_certificacion_de_cdn_gs_2x_reproduce_el_valor_publicado():
    c = q.certificar_recorte(d.CDN_RESULTADOS)
    assert (c.n_total, c.n) == (150, 143)
    assert round(c.media, 3) == 2.388 and round(c.dos_sd, 3) == 0.232
    assert round(c.media_total, 4) == 2.3868 and round(c.sd_total, 4) == 0.1293


# ------------------------------------------------------------------ OREAS
@pytest.mark.parametrize("o", d.OREAS, ids=lambda o: o.nombre)
def test_las_puertas_de_oreas_salen_de_valor_y_1rsd_a_un_milesimo(o):
    lo2, hi2 = q.limites(o.valor, o.sd_sin_redondear, 2)
    lo3, hi3 = q.limites(o.valor, o.sd_sin_redondear, 3)
    for calc, pub in zip((lo2, hi2, lo3, hi3), o.puertas, strict=True):
        assert abs(calc - pub) <= 0.001 + 1e-9


def test_la_sd_publicada_es_la_sd_calculada_redondeada():
    for o in d.OREAS:
        assert round(o.sd_sin_redondear, 3) == o.sd


# ------------------------------------------------------------------ validación (cortes previos)
def test_todos_los_cortes_de_validacion_cuadran():
    s = v.summary()
    assert s == {"cdn": (2, 2), "oreas": (16, 16), "gemas": (5, 5), "th": (4, 4),
                 "rr": (8, 8), "ll": (3, 3)}  # fmt: skip


def test_los_conteos_de_gemas_son_los_que_se_esperan():
    por = {(c.label, c.kind): (c.published, c.calculated) for c in v.gemas_checks()}
    assert por[("Ag ±20 %", "p99")] == (99, 99) and por[("Ag ±20 %", "p90")] == (95, 94)
    assert por[("Ag ±10 %", "p99")] == (88, 86) and por[("Ag ±10 %", "p90")] == (68, 67)
    assert por[("Ge ±10 %", "p90")] == (15, 15)


def test_con_la_sd_redondeada_del_certificado_cuatro_puertas_no_cuadran():
    ok = [c.ok for c in v.oreas_checks(redondeada=True)]
    assert (sum(ok), len(ok)) == (12, 16)


def test_un_corte_se_rompe_si_la_cifra_se_desplaza():
    c = v.cdn_checks()[0]
    assert c.ok
    assert not v.QaqcCheck(c.source, c.label, c.kind, c.published + 0.001, c.calculated,
                           c.tol, 4).ok  # fmt: skip


def test_los_sesgos_publicados_estan_leidos_de_la_imagen_y_cuadran_con_la_formula():
    nombres = [r[0] for r in d.RAINY_RIVER]
    assert nombres == [f"OREAS {n}" for n in (294, 230, 231, 233, 236, 238, 240, 242)]
    assert [r[1] for r in d.RAINY_RIVER] == [78, 127, 128, 124, 23, 100, 14, 46]
    # las cifras de la Tabla 11-12 tal como se leen en la imagen de la página 107
    assert [r[2] for r in d.RAINY_RIVER] == [0.207, 0.337, 0.542, 1.050, 1.850, 3.080, 5.510, 8.670]
    assert [r[3] for r in d.RAINY_RIVER] == [0.205, 0.331, 0.533, 1.042, 1.827, 3.059, 5.377, 8.629]
    assert [r[4] for r in d.RAINY_RIVER] == [-1.0, -1.8, -1.7, -0.8, -1.3, -0.7, -2.5, -0.5]
    assert [r[5] for r in d.RAINY_RIVER] == [6.5, 3.2, 3.4, 4.6, 2.7, 3.3, 3.6, 4.1]
    assert [r[6] for r in d.RAINY_RIVER] == [3, 0, 2, 5, 0, 1, 14, 4]
    assert sum(r[1] for r in d.LOMA_LARGA) == 74  # los 74 CRM de Au de 2013
    # Tabla 11-3 de Loma Larga, página 87 del estudio
    assert [r[4] for r in d.LOMA_LARGA] == [0.989, 1.805, 8.367]
    assert [r[2] for r in d.LOMA_LARGA] == [0.978, 1.748, 8.631]
    assert [r[6] for r in d.LOMA_LARGA] == [-1.11, -3.17, 3.15]
