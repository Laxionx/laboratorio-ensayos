"""Copelación y partición (módulo `muestreo`): las tablas de Bugbee y de Godshall con sus cifras
literales y su página, el modelo, la corrección de la ley, el encuarte, la trayectoria del botón
y los datos manipulados. La validación contra Godshall tiene sus cortes fijados antes de correr
(ver `muestreo/copelacion_validacion.py`)."""

import itertools
import math

import pytest

from muestreo import copelacion as cp
from muestreo import copelacion_datos as cd
from muestreo import copelacion_validacion as cv


# ------------------------------------------------------------------ las tablas, exactas
def test_tabla_ix_p100_cifras_literales():
    assert cd.PAGINA_IMPRESA["IX"] == 100 and cd.PAGINA_ESCANEO["IX"] == 116
    assert cd.TABLA_IX == (
        (200.0, 10.0, 700.0, 1.02), (200.0, 10.0, 775.0, 1.30), (200.0, 10.0, 850.0, 1.73),
        (200.0, 10.0, 925.0, 3.65), (200.0, 10.0, 1000.0, 4.88),
    )  # fmt: skip


def test_tabla_x_p102_cifras_literales():
    assert cd.PAGINA_IMPRESA["X"] == 102 and cd.PAGINA_ESCANEO["X"] == 118
    assert cd.TABLA_X == (
        (200.0, 10.0, 685.0, 1.39), (200.0, 15.0, 685.0, 1.38), (200.0, 20.0, 685.0, 1.52),
        (200.0, 25.0, 685.0, 1.85),
    )  # fmt: skip


def test_tabla_xi_p102_cifras_literales_y_su_origen_en_godshall():
    assert cd.TABLA_XI == (
        (200.0, 1.73), (100.0, 2.03), (50.0, 2.65), (20.0, 2.82), (10.0, 3.44), (5.0, 4.46),
        (2.0, 6.90),
    )  # fmt: skip
    assert cd.PLOMO_TABLA_XI_G == pytest.approx(14.58335)  # ½ A.T.
    # es la fila de ½ A.T. de la segunda serie del artículo original, salvo una cifra: en 50 mg
    # Bugbee imprime 2,65 y Godshall (p. 483) imprime 2,67
    difieren = [(ag, b, g) for ag, b, g in cv.cita_tabla_xi() if b != g]
    assert difieren == [(50.0, 2.65, 2.67)]


def test_tabla_xii_p102_cifras_literales():
    assert cd.TABLA_XII == (
        (200.0, 10.0, 700.0, None), (200.0, 10.0, 775.0, 0.155), (200.0, 10.0, 850.0, 0.385),
        (200.0, 10.0, 925.0, 0.460), (200.0, 10.0, 1000.0, 1.435), (200.0, 10.0, 1075.0, 2.990),
    )  # fmt: skip


def test_smith_p103_rose_p121_y_particion_p118_cifras_literales():
    assert (cd.SMITH_CON_TELURIO, cd.SMITH_SIN_TELURIO) == ((94.9, 97.0), (98.2, 99.5))
    assert cd.ROSE == ((0.1, 25.0), (0.2, 10.0), (1.0, 6.0), (10.0, 4.0), (50.0, 2.5))
    assert cd.ROSE_BAJO == (20.0, 30.0) and cd.LINGOTE_RAZON == (2.0, 2.5)
    assert cd.MINIMO_PARTIR == 3.0 and (cd.RECOMENDADO_MIN, cd.RECOMENDADO_MAX) == (8.0, 10.0)
    assert cd.MAX_ORO_FRACCION == 0.25
    assert (cd.PAGINA_IMPRESA["rose"], cd.PAGINA_IMPRESA["parting"]) == (121, 118)
    assert cd.PAGINA_IMPRESA["smith"] == 103 and cd.PAGINA_ESCANEO["rose"] == 137


# promedios («Av.») que Godshall imprime en la p. 483 al lado de los cuatro de plomo
AV_IMPRESO = {
    "primera": (6.49, 3.82, 4.97, 4.80, 3.02, 2.30, 1.78),
    "segunda": (7.11, 5.04, 4.31, 3.40, 2.74, 2.23, 1.82),
    "tercera": (4.85, 3.94, 3.80, 3.07, 2.96, 2.54, 1.87),
    "final": (5.92, 4.28, 4.36, 3.73, 2.83, 2.36, 1.82),
}


@pytest.mark.parametrize("serie", ["primera", "segunda", "tercera", "final"])
def test_godshall_p483_cada_fila_promedia_a_su_av_impreso(serie):
    """Control de la transcripción: el «Av.» impreso es el promedio de los cuatro plomos."""
    filas = cd.GODSHALL_SERIES[serie]
    assert len(filas) == 7 and all(len(f) == 4 for f in filas)
    for fila, av in zip(filas, AV_IMPRESO[serie], strict=True):
        assert sum(fila) / 4 == pytest.approx(av, abs=0.006), (serie, fila)
    assert cd.PAGINA_IMPRESA["godshall"] == 483


def test_godshall_celdas_literales_de_la_fila_de_200_mg_y_de_2_mg():
    assert [f[-1] for f in cd.GODSHALL_FINAL] == [7.60, 5.30, 5.11, 4.24, 3.37, 2.80, 2.10]
    assert cd.GODSHALL_FINAL[-1] == (1.51, 1.77, 1.92, 2.10)
    assert cd.GODSHALL_SEGUNDA[0] == (3.73, 6.90, 8.43, 9.39)
    assert cd.GODSHALL_PLATA_MG == (2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)


# ------------------------------------------------------------------ el modelo
@pytest.mark.parametrize(("t", "pct"), [(r[2], r[3]) for r in cd.TABLA_IX])
def test_el_modelo_devuelve_la_tabla_ix_en_sus_nodos(t, pct):
    assert 100 * cp.perdida_plata(t, 10.0, 200.0).frac == pytest.approx(pct)


def test_entre_nodos_la_interpolacion_es_log_lineal_y_creciente():
    a = cp.factor_temperatura_plata(812.5)[0]
    assert a == pytest.approx(math.sqrt(1.30 * 1.73))  # punto medio de 775 a 850
    ts = [700, 725, 775, 800, 850, 900, 925, 960, 1000]
    ys = [cp.factor_temperatura_plata(t)[0] for t in ts]
    assert ys == sorted(ys)


def test_los_factores_de_plomo_y_de_plata_son_relativos_a_10_g_y_a_200_mg():
    assert cp.factor_plomo(10.0)[0] == 1.0 and cp.factor_plata(200.0)[0] == 1.0
    assert cp.factor_plomo(25.0)[0] == pytest.approx(1.85 / 1.39)
    assert cp.factor_plomo(17.5)[0] == pytest.approx((1.38 + 0.5 * (1.52 - 1.38)) / 1.39)
    for ag, pct in cd.TABLA_XI:
        assert cp.factor_plata(ag)[0] == pytest.approx(pct / 1.73)
    assert cp.factor_plata(2.0)[0] == pytest.approx(6.90 / 1.73)


def test_fuera_de_las_tablas_no_se_extrapola_y_se_avisa():
    dentro = cp.perdida_plata(800.0, 15.0, 100.0)
    assert dentro.avisos == ()
    assert cp.perdida_plata(1200.0, 15.0, 100.0).frac == cp.perdida_plata(1000.0, 15.0, 100.0).frac
    assert cp.perdida_plata(1200.0, 15.0, 100.0).avisos == ("temp",)
    assert cp.perdida_plata(800.0, 40.0, 100.0).avisos == ("plomo",)
    assert cp.perdida_plata(800.0, 15.0, 900.0).avisos == ("plata",)
    assert cp.perdida_plata(800.0, 28.0, 0.5).avisos == ("plomo", "plata")
    assert cp.perdida_plata(800.0, 15.0, 0.0).frac == 0.0


@pytest.mark.parametrize(("t", "pct"), [(r[2], r[3]) for r in cd.TABLA_XII if r[3] is not None])
def test_el_oro_devuelve_la_tabla_xii_en_sus_nodos(t, pct):
    p = cp.perdida_oro(t)
    assert 100 * p.frac == pytest.approx(pct)
    assert p.avisos == (("congelado",) if t <= cd.CONGELADO_C else ())


def test_el_oro_a_700_grados_o_menos_es_boton_congelado():
    for t in (700.0, 650.0):
        p = cp.perdida_oro(t)
        assert p.avisos == ("congelado",) and 100 * p.frac == pytest.approx(0.155)
    assert cp.perdida_oro(1200.0).avisos == ("temp",)


def test_la_banda_es_la_dispersion_de_las_tres_series_de_godshall():
    esperado = []
    for i in range(7):
        v = [math.log(s[i][1]) for s in (cd.GODSHALL_PRIMERA, cd.GODSHALL_SEGUNDA,
                                         cd.GODSHALL_TERCERA)]  # fmt: skip
        m = sum(v) / 3
        esperado.append(sum((x - m) ** 2 for x in v) / 2)
    assert cp.SD_LN == pytest.approx(math.sqrt(sum(esperado) / 7))
    p = cp.perdida_plata(850.0, 10.0, 200.0)
    assert p.bajo == pytest.approx(p.frac / cp.FACTOR_BANDA) and p.bajo < p.frac < p.alto


def test_la_ley_corregida_es_la_medida_entre_uno_menos_la_perdida():
    assert cp.ley_corregida(3.84, 0.05) == pytest.approx(3.84 / 0.95)
    assert cp.ley_corregida(0.0, 0.2) == 0.0
    for malo in (-0.01, 1.0, float("nan"), float("inf"), True):
        with pytest.raises(cp.CopelacionError):
            cp.ley_corregida(3.0, malo)


# ------------------------------------------------------------------ encuarte
def test_rose_en_sus_filas_entre_ellas_y_en_los_extremos():
    for mg, r in cd.ROSE:
        assert cp.razon_rose(mg) == pytest.approx(r)
    assert cp.razon_rose(0.01) == 25.0 and cp.razon_rose(500.0) == 2.5
    assert cp.razon_rose(math.sqrt(0.2 * 1.0)) == pytest.approx(math.sqrt(10.0 * 6.0))
    xs = [0.1, 0.15, 0.3, 0.7, 2, 5, 20, 40, 50]
    ys = [cp.razon_rose(x) for x in xs]
    assert ys == sorted(ys, reverse=True)


def test_estado_de_la_particion_en_los_umbrales_de_bugbee():
    assert cp.estado_particion(2.99) == "insuficiente"
    assert cp.estado_particion(3.0) == "lenta" and cp.estado_particion(7.99) == "lenta"
    assert cp.estado_particion(8.0) == "buena" and cp.estado_particion(30.0) == "buena"


def test_la_plata_agregada_deja_la_razon_pedida_tras_copelar():
    for modo, razon in (("rose", 8.0), ("minimo", 8.0), ("propia", 8.0), ("propia", 12.5)):
        c = cp.copelar(800.0, 28.0, 1.0, 2.0, modo, razon)
        assert c.plata_agregada_mg > 0
        assert c.razon_final == pytest.approx(c.razon_objetivo, rel=1e-9)
        assert c.plata_total_mg == pytest.approx(2.0 + c.plata_agregada_mg)


def test_si_ya_hay_plata_de_sobra_no_se_agrega_nada():
    c = cp.copelar(800.0, 28.0, 1.0, 50.0, "minimo")
    assert c.plata_agregada_mg == 0.0 and c.razon_final > 40 and c.estado == "buena"


def test_la_plata_agregada_crece_con_la_temperatura_porque_se_pierde_mas():
    a = cp.copelar(780.0, 28.0, 1.0, 0.0, "propia", 8.0).plata_agregada_mg
    b = cp.copelar(950.0, 28.0, 1.0, 0.0, "propia", 8.0).plata_agregada_mg
    assert b > a > 8.0 * 0.99  # más que 8·Au, porque pierde plata y algo de oro


def test_la_perla_es_oro_mas_plata_tras_las_perdidas():
    c = cp.copelar(850.0, 28.0, 2.0, 5.0, "rose")
    assert c.perla_mg == pytest.approx(
        2.0 * (1 - c.perdida_au.frac) + c.plata_total_mg * (1 - c.perdida_ag.frac)
    )
    assert 0 < c.oro_en_perla < 1 and c.avisos != ()


# ------------------------------------------------------------------ la trayectoria del botón
def test_la_trayectoria_va_del_boton_de_plomo_a_la_perla_sin_subir():
    c = cp.copelar(800.0, 28.0, 1.0, 2.0, "rose")
    tr = cp.trayectoria(c, 49)
    assert len(tr) == 49 and tr[0].avance == 0.0 and tr[-1].avance == 1.0
    assert tr[0].masa_mg == pytest.approx(28000.0 + 1.0 + c.plata_total_mg)
    assert tr[-1].plomo_mg == 0.0 and tr[-1].masa_mg == pytest.approx(c.perla_mg)
    assert tr[-1].oro_mg == pytest.approx(c.oro_final_mg)
    assert tr[-1].plata_mg == pytest.approx(c.plata_final_mg)
    masas = [x.masa_mg for x in tr]
    assert all(b <= a + 1e-12 for a, b in itertools.pairwise(masas))
    acum = [x.perdida_acum for x in tr]
    assert acum[0] == 0.0 and acum[-1] == pytest.approx(1.0) and acum == sorted(acum)


def test_la_perdida_acumulada_es_convexa_pequena_al_principio_y_grande_al_final():
    # forma cualitativa de Rose: con plomo de sobra el botón casi no pierde preciosos
    c = [cp.perdida_acumulada(s / 20, 28.0, 10.0) for s in range(21)]
    assert c[0] == 0.0 and c[-1] == pytest.approx(1.0) and c[10] < 0.15
    pasos = [b - a for a, b in itertools.pairwise(c)]
    assert pasos == sorted(pasos) and all(c[i] < i / 20 for i in range(1, 20))


def test_el_volumen_usa_la_densidad_del_plomo_y_las_de_manual():
    assert cp.volumen_cm3(10_000.0, 0.0, 0.0, 10.0) == pytest.approx(1.0)
    assert cp.volumen_cm3(0.0, 19_320.0, 10_490.0, 10.0) == pytest.approx(2.0)


# ------------------------------------------------------------------ datos manipulados
MALOS = [float("nan"), float("inf"), -float("inf"), -1.0, 0.0, True, "800", None]


@pytest.mark.parametrize("malo", MALOS)
def test_temperatura_plomo_y_oro_invalidos_se_rechazan(malo):
    with pytest.raises(cp.CopelacionError):
        cp.copelar(malo, 28.0, 1.0, 2.0)
    with pytest.raises(cp.CopelacionError):
        cp.copelar(800.0, malo, 1.0, 2.0)
    with pytest.raises(cp.CopelacionError):
        cp.copelar(800.0, 28.0, malo, 2.0)
    with pytest.raises(cp.CopelacionError):
        cp.perdida_oro(malo)


@pytest.mark.parametrize("malo", [x for x in MALOS if x != 0.0])
def test_plata_invalida_se_rechaza_pero_cero_es_valido(malo):
    with pytest.raises(cp.CopelacionError):
        cp.copelar(800.0, 28.0, 1.0, malo)
    assert cp.copelar(800.0, 28.0, 1.0, 0.0).plata_agregada_mg > 0


def test_modo_y_razon_propia_invalidos_y_pocos_cuadros():
    with pytest.raises(cp.CopelacionError):
        cp.copelar(800.0, 28.0, 1.0, 2.0, "otro")
    for malo in (float("nan"), 0.0, -3.0, float("inf")):
        with pytest.raises(cp.CopelacionError):
            cp.copelar(800.0, 28.0, 1.0, 2.0, "propia", malo)
    with pytest.raises(cp.CopelacionError):
        cp.trayectoria(cp.copelar(800.0, 28.0, 1.0, 2.0), 1)


def test_valores_extremos_validos_no_dan_nan_ni_infinito():
    for t in (0.1, 700.0, 1075.0, 1e6):
        for pb in (1e-3, 28.0, 1e4):
            for au in (1e-6, 200.0, 1e6):
                c = cp.copelar(t, pb, au, 1e5, "rose")
                vals = (c.perla_mg, c.plata_agregada_mg, c.perdida_ag.frac, c.perdida_au.frac,
                        c.razon_final)  # fmt: skip
                assert all(math.isfinite(v) for v in vals), (t, pb, au)


# ------------------------------------------------------------------ validación contra Godshall
def test_solapan_solo_dos_celdas_y_las_demas_se_informan_como_tendencia():
    cells = cv.celdas_finales()
    assert len(cells) == 28
    solapan = [(c.plata_mg, c.plomo_at) for c in cells if c.solapa]
    assert solapan == [(200.0, 0.5), (200.0, 0.75)]
    assert [c.publicada for c in cv.celdas_cuantitativas()] == [1.77, 1.92]


def test_la_temperatura_de_la_validacion_se_fijo_antes_y_es_el_centro_de_700_a_775():
    assert cv.T_VALIDACION_C == 740.0 and cv.CORTE_RELATIVO == 0.25
    assert 700.0 < cv.T_VALIDACION_C < cd.CRISTALES_HASTA_C


def test_resultado_cuantitativo_documentado_el_modelo_de_lodge_queda_corto_con_godshall():
    err = [c.error_relativo for c in cv.celdas_cuantitativas()]
    assert err == pytest.approx([-0.348, -0.285], abs=0.001)
    assert not any(c.cuadra for c in cv.celdas_cuantitativas())
    # diagnóstico, no validación: Godshall se parece a Lodge a 830-850 °C, no a 740 °C
    assert [round(c.temp_implicita_c) for c in cv.celdas_cuantitativas()] == [853, 833]


@pytest.mark.xfail(
    strict=True,
    reason="con T = 740 °C (fijada antes) el modelo ajustado con Lodge predice 1,15 y 1,37 % "
    "contra 1,77 y 1,92 % de Godshall: -34,8 y -28,5 %, fuera de ±25 %. Otro laboratorio, otra "
    "copela, y Godshall no midió la temperatura; no se ajusta nada para que pase",
)
def test_corte_cuantitativo_mas_menos_25_por_ciento_contra_godshall():
    assert all(c.cuadra for c in cv.celdas_cuantitativas())


def test_las_tendencias_de_godshall_las_cumple_el_modelo():
    t = cv.tendencias()
    assert t.plata_mas_pierde == (4, 4)  # NO independiente: la plata sale de la Tabla XI
    assert t.plomo_mas_pierde == (7, 7)
    assert t.orden_de_magnitud == (28, 28)


def test_replica_de_la_plata_con_las_series_primera_y_tercera_cuenta_informativa():
    r = cv.razones_de_plata()
    assert len(r) == 12 and sum(x.cuadra for x in r) == 7  # informativo, sin corte previo
    assert {x.plata_mg for x in r if not x.cuadra} == {2.0, 5.0, 20.0}
