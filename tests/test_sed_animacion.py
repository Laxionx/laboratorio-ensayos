"""Pestaña «Ensayo de sedimentación» sin levantar Streamlit: la animación sale del cálculo (cota de
la interfase en cada cuadro = curva; diámetro dibujado = calculado × escala), la tabla se valida
en el servidor y los controles salen de una sola definición."""

import itertools
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("streamlit")
pytest.importorskip("plotly")

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import controles  # noqa: E402
import i18n  # noqa: E402
import sed_calculo as sc  # noqa: E402
import sed_graficos as sg  # noqa: E402
import sed_svg as ss  # noqa: E402
import sed_tab  # noqa: E402
from dibujo import as_images, es  # noqa: E402

from muestreo import sedimentacion as sd  # noqa: E402

SPANISH = re.compile(
    r"[áéíóúñ¿¡]|\b(de|del|la|las|los|el|con|para|por|una|sin|que|se|más|muy)\b", re.IGNORECASE
)


def view(**kw) -> sc.SedView:
    return sc.run_sed(sc.SedParams(**kw))


def _keyframes(svg: str, name: str) -> list[tuple[float, str]]:
    body = re.search(rf"@keyframes {name}\{{(.*?)\}}\}}", svg, re.S).group(1) + "}"
    return [(float(p), v) for p, v in re.findall(r"([\d.]+)%\{([^}]*)\}", body)]


def _scale_y(svg: str) -> list[float]:
    return [
        float(re.search(r"scaleY\(([\d.]+)\)", v).group(1))
        for p, v in _keyframes(svg, "lb-slurry")
        if p < 100.0
    ]


def _strip(svg: str) -> list[str]:
    return re.findall(r'<text x="0.0" y="[\d.]+"[^>]*>([^<]+)</text>', svg)


# ------------------------------------------------------------------ la probeta sale de la curva
def test_la_cota_de_la_interfase_en_cada_cuadro_es_la_de_la_curva():
    v = view()
    svg = ss.settling_svg(v)
    frames = _scale_y(svg)
    assert len(frames) == sc.FRAMES == 97
    t_max = v.t_animacion_s
    for i, f in enumerate(frames):
        t = t_max * i / (sc.FRAMES - 1)
        assert f * v.curva.h0 == pytest.approx(v.curva.altura(t), abs=2e-5)
        # y la curva interpolada es la de Luz (ec. 1), no un dibujo aparte
        assert f * 0.4 == pytest.approx(sd.luz_altura(t, *sc.LUZ_DEFECTO), abs=2e-4)
    assert frames[0] == 1.0 and all(b <= a + 1e-9 for a, b in itertools.pairwise(frames))


def test_el_ultimo_cuadro_es_la_cota_a_3_tc_y_el_tiempo_se_declara_comprimido():
    v = view(tc=420.0)
    assert v.t_animacion_s == 1260.0 == sc.ANIM_FACTOR * 420.0
    svg = ss.settling_svg(v)
    assert _scale_y(svg)[-1] * 0.4 == pytest.approx(v.curva.altura(1260.0), abs=2e-5)
    assert (
        "Tiempo comprimido: 0 a 1 260 s en 12 s" in svg
        and "de 0 a 1 260 s del ensayo en 12 s" in svg
    )
    assert "ilustrativos" in svg and "Esquema, no a escala" in svg
    assert (ss.RUN_S, ss.HOLD_S) == (12.0, 2.0)
    css = svg.split("</style>")[0]
    assert "animation:lb-slurry 14s linear infinite" in css
    assert "animation:lb-count 14s steps(1,end) infinite" in css


def test_la_tabla_editable_mueve_la_probeta_con_sus_propios_puntos():
    rows = [[0, 0.30], [100, 0.25], [300, 0.20], [600, 0.16], [1200, 0.13], [86400, 0.10]]
    v = sc.run_sed(sc.SedParams(fuente=sc.FUENTES[1], z0=0.9, tc=200.0, cma=3.0, cmu=30.0), rows)
    frames = _scale_y(ss.settling_svg(v))
    assert frames[0] == 1.0 and v.curva.h0 == 0.30  # la cota inicial sale de la tabla, no de z0
    for i in (10, 40, 96):
        t = v.t_animacion_s * i / 96
        assert frames[i] * 0.30 == pytest.approx(v.curva.altura(t), abs=2e-5)


def test_los_relojes_dicen_el_tiempo_y_la_cota_de_cada_cuadro_con_el_formato_del_idioma():
    v = view()
    for lang, sep in (("es", ","), ("en", ".")):
        with i18n.use(lang):
            texts = _strip(ss.settling_svg(v))
            expected = [es(h, 3) for h in v.alturas_animadas(96)]
            last, mid = es(v.t_animacion_s, 0), es(v.t_animacion_s / 2, 0)
        times, heights = texts[: sc.FRAMES], texts[sc.FRAMES :]
        assert times[0] == "0" and len(times) == sc.FRAMES
        assert times[-1] == last and times[48] == mid
        assert heights == expected and all(sep in h for h in heights)
        assert heights[0] == f"0{sep}400"


def test_quieta_no_hay_animacion_y_con_movimiento_si():
    v = view()
    moving, still = ss.settling_svg(v), ss.settling_svg(v, paused=True)
    assert "animation:lb-slurry" in moving and "animation:lb-rake" not in still
    assert "animation" not in still.split("</style>")[1] and "@keyframes" not in still
    final = _scale_y(moving)[-1]
    assert f"scaleY({final:.5f})" in still and "transform-origin:50% 100%" in still
    both = as_images(moving, still, "alt")
    one = as_images(still, still, "alt")
    assert both.count("<img") == 2 and one.count("<img") == 1


# ------------------------------------------------------------------ el espesador sale del diámetro
@pytest.mark.parametrize("tph", [20.0, 157.0, 600.0, 4000.0])
def test_el_diametro_dibujado_es_el_calculado_por_la_escala(tph):
    v = view(tph=tph)
    svg = ss.settling_svg(v)
    r = float(re.search(r'class="lb-tank" cx="[\d.]+" cy="[\d.]+" r="([\d.]+)"', svg)[1])
    scale = ss.thickener_scale_px_per_m(v.diametro_m)
    assert 2 * r == pytest.approx(v.diametro_m * scale, abs=0.02)
    assert 2 * r == pytest.approx(ss.drawn_diameter_px(v), abs=0.02)
    assert 2 * r <= ss.MAX_DIAMETER_PX + 0.02 and scale <= ss.MAX_SCALE_PX_M
    # el diámetro calculado es el del área de Talmage-Fitch × tonelaje × factor
    area = v.tf.area_unitaria_m2_t_dia * tph * 24 * v.factor
    assert v.diametro_m == pytest.approx(2 * np.sqrt(area / np.pi))
    assert f"Ø {es(v.diametro_m, 1)} m (calculado)" in svg
    legend = " ".join(re.findall(r">([^<]+)</text>", svg))  # la leyenda se parte en renglones
    assert f"a {es(scale, 2)} px por m" in legend


def test_el_factor_de_vale_reduce_el_diametro_dibujado_en_raiz_de_0_64():
    sin, con = view(), view(factor=sc.FACTORES[1])
    assert con.factor == 0.64 and con.area_m2 == pytest.approx(sin.area_m2 * 0.64)
    assert con.diametro_m == pytest.approx(sin.diametro_m * 0.8)
    assert ss.drawn_diameter_px(con) < ss.drawn_diameter_px(sin)


def test_la_barra_de_escala_mide_lo_que_dice():
    for tph in (157.0, 4000.0):
        v = view(tph=tph)
        svg = ss.settling_svg(v)
        bar_m = 10 if v.diametro_m < 100 else 50
        x1, x2 = (
            float(x) for x in re.findall(r'<line x1="([\d.]+)" y1="[\d.]+" x2="([\d.]+)"', svg)[-1]
        )
        assert x2 - x1 == pytest.approx(bar_m * ss.thickener_scale_px_per_m(v.diametro_m), abs=0.1)
        assert f">{bar_m} m</text>" in svg


def test_los_esquemas_son_xml_valido_y_en_ingles_no_llevan_espanol():
    v = view()
    for lang in ("es", "en"):
        with i18n.use(lang):
            for paused in (False, True):
                svg = ss.settling_svg(v, paused)
                ET.fromstring(svg)
                texts = re.findall(r">([^<]+)</text>", svg) + re.findall(
                    r'aria-label="([^"]+)"', svg
                )
                if lang == "en":
                    assert not [x for x in texts if SPANISH.search(x)], texts
                    assert any("Thickener: Ø 43.6 m (calculated)" in x for x in texts)
                    assert any("Compressed time" in x for x in texts)
                else:
                    assert any("Espesador: Ø 43,6 m (calculado)" in x for x in texts)


# ------------------------------------------------------------------ los gráficos
def test_la_construccion_de_talmage_fitch_esta_dibujada_con_las_cifras_del_calculo():
    v = view()
    fig = sg.curve_figure(v)
    by = {tr.name: tr for tr in fig.data}
    tf = v.tf
    assert list(by["Cota del underflow Hu"].y) == [tf.hu_m, tf.hu_m]
    tangent = by["Tangente en C"]
    assert tangent.y[0] == pytest.approx(tf.tangente(tangent.x[0]))
    assert np.interp(tf.tc_s, tangent.x, tangent.y) == pytest.approx(tf.hc_m, rel=1e-9)
    assert np.interp(tf.tu_s, tangent.x, tangent.y) == pytest.approx(tf.hu_m, rel=1e-9)
    points = by["Punto de compresión C y punto U"]
    assert (list(points.x), list(points.y)) == ([tf.tc_s, tf.tu_s], [tf.hc_m, tf.hu_m])
    curve = by["Cota de la interfase"]
    np.testing.assert_allclose(curve.y[0], 0.4)
    assert fig.layout.xaxis.range[1] >= tf.tu_s * 1.5


def test_la_curva_de_flujo_de_kynch_lleva_los_puntos_y_la_tangente_desde_cu():
    v = view()
    fig = sg.kynch_figure(v)
    flux = fig.data[0]
    assert list(flux.x) == list(v.kynch.c_t_m3) and list(flux.y) == list(v.kynch.g_t_m2_h)
    gl, cc = v.g_limite
    line = fig.data[1]
    assert (line.x[0], line.y[0], line.x[1], line.y[1]) == (0.0, gl, v.cu, 0.0)
    crit = fig.data[2]
    assert crit.x[0] == cc and crit.y[0] == pytest.approx(gl * (1 - cc / v.cu))


def test_los_graficos_en_ingles_no_llevan_espanol():
    v = view()
    with i18n.use("en"):
        figs = [sg.curve_figure(v), sg.kynch_figure(v)]
        blob = " ".join(str(f.to_plotly_json()) for f in figs)
    texts = re.findall(r"'(?:text|title|name)': '([^']+)'", blob)
    texts += re.findall(r"'title': \{'text': '([^']+)'", blob)
    assert not [x for x in texts if SPANISH.search(x)], [x for x in texts if SPANISH.search(x)]
    assert "Underflow height Hu" in blob and "Kynch solids flux curve" in blob


# ------------------------------------------------------------------ la tabla del visitante
def test_la_tabla_precargada_es_la_curva_de_luz():
    rows = sed_tab.example_table()
    assert rows["t"].tolist() == list(map(float, sc.TABLA_T_S)) and rows["h"][0] == 0.4
    z0, zi, a, b = sc.LUZ_DEFECTO
    for t, h in zip(rows["t"], rows["h"], strict=True):
        assert h == pytest.approx(sd.luz_altura(t, z0, zi, a, b), abs=5e-5)
    # y usada como tabla da el mismo trazo que el modelo (la tabla está redondeada al 0,1 mm)
    de_tabla = sc.run_sed(sc.SedParams(fuente=sc.FUENTES[1]), [list(r) for r in sc.tabla_de_luz()])
    assert de_tabla.tf.area_unitaria_m2_t_dia == pytest.approx(
        view().tf.area_unitaria_m2_t_dia, rel=0.05
    )


GOOD = [[0, 0.4], [60, 0.3], [120, 0.25], [300, 0.2], [900, 0.1]]


@pytest.mark.parametrize(
    ("rows", "code"),
    [
        ([], "filas"),
        (GOOD[:3], "filas"),
        ([[0, 0.4]] * (sc.MAX_FILAS + 1), "filas"),
        ([[None, 0.3], *GOOD[1:]], "numero"),
        ([[0, float("nan")], *GOOD[1:]], "numero"),
        ([[0, 0.4], [60, float("inf")], *GOOD[2:]], "numero"),
        ([["<script>alert(1)</script>", 0.4], *GOOD[1:]], "numero"),
        ([[0, "0,4"], *GOOD[1:]], "numero"),
        ([[0, True], *GOOD[1:]], "numero"),
        ([[0, 0.4], [60, -0.1], *GOOD[2:]], "rango"),
        ([[0, 0.4], [60, 0.0], *GOOD[2:]], "rango"),
        ([[-5, 0.4], *GOOD[1:]], "rango"),
        ([[0, 9.0], *GOOD[1:]], "rango"),
        ([*GOOD[:-1], [sc.T_MAX_S + 1, 0.1]], "rango"),
        ([[10, 0.4], *GOOD[1:]], "origen"),
        ([GOOD[0], GOOD[2], GOOD[1], GOOD[3], GOOD[4]], "orden"),
        ([GOOD[0], GOOD[1], GOOD[1], GOOD[3], GOOD[4]], "orden"),
        ([GOOD[0], GOOD[1], [120, 0.35], GOOD[3], GOOD[4]], "sube"),
    ],
)
def test_leer_tabla_rechaza_lo_manipulado_con_su_codigo(rows, code):
    with pytest.raises(sd.SedimentacionError) as err:
        sc.leer_tabla(rows)
    assert err.value.code == code
    assert f"sd.err.{code}" in i18n.TEXTS["es"] and f"sd.err.{code}" in i18n.TEXTS["en"]


def test_leer_tabla_acepta_una_curva_valida_y_devuelve_floats():
    curva = sc.leer_tabla(GOOD)
    assert curva.t_s == (0.0, 60.0, 120.0, 300.0, 900.0) and all(
        isinstance(x, float) for x in curva.h_m
    )


@pytest.mark.parametrize(
    ("kw", "code"),
    [
        ({"cma": 40.0, "cmu": 30.0}, "conc"),
        ({"tc": 1e9}, "compresion"),
        ({"tc": 8000.0}, "tangente"),
        ({"z_inf": 0.5}, "luz"),
    ],
)
def test_los_datos_imposibles_dan_su_codigo_y_su_texto_en_los_dos_idiomas(kw, code):
    with pytest.raises(sd.SedimentacionError) as err:
        view(**kw)
    assert err.value.code == code
    for lang in ("es", "en"):
        with i18n.use(lang):
            text = sed_tab._error_text(err.value)
            assert text and "{" not in text


def test_el_metodo_de_roberts_elige_el_punto_y_se_usa_en_la_construccion():
    rows = [[t, h] for t, h in sc.tabla_de_luz()]
    v = sc.run_sed(sc.SedParams(fuente=sc.FUENTES[1], compresion=sc.COMPRESIONES[1], cma=2.0,
                                cmu=20.0), rows)  # fmt: skip
    assert v.tc_s == sd.roberts_punto_compresion(v.curva, v.h_inf) and v.tf.tc_s == v.tc_s


def test_los_dos_modos_dan_areas_distintas_y_vale_usa_la_cota_a_24_h():
    clasico, vale = view(), view(modo=sc.MODOS[1])
    assert clasico.tf.modo == "clasico" and vale.tf.modo == "vale"
    assert (
        vale.tf.hu_m == pytest.approx(0.035)
        and vale.tf.area_unitaria_m2_t_dia > clasico.tf.area_unitaria_m2_t_dia
    )


# ------------------------------------------------------------------ una sola definición
def test_los_controles_de_la_sedimentacion_salen_de_la_definicion_unica():
    group = [d for d in controles.DATOS if d.group == controles.SED]
    keys = "s_fuente s_z0 s_zinf s_a s_b s_cma s_cmu s_rho s_comp s_tc s_modo s_tph s_factor"
    assert [d.key for d in group] == keys.split()
    table = controles.data_table(controles.SED)
    assert len(table) == len(group) and set(table["Dato"]) == {d.label for d in group}
    p = sc.SedParams()
    defaults = {d.key: d.default for d in group}
    assert (p.fuente, p.z0, p.z_inf, p.a, p.b, p.cma, p.cmu, p.rho_s) == (
        defaults["s_fuente"], defaults["s_z0"], defaults["s_zinf"], defaults["s_a"],
        defaults["s_b"], defaults["s_cma"], defaults["s_cmu"], defaults["s_rho"],
    )  # fmt: skip
    assert (p.compresion, p.tc, p.modo, p.tph, p.factor) == (
        defaults["s_comp"], defaults["s_tc"], defaults["s_modo"], defaults["s_tph"],
        defaults["s_factor"],
    )  # fmt: skip
    for d in group:
        assert d.widget == "select" or d.lo <= d.default <= d.hi


def test_los_valores_literales_de_la_fig_1_y_el_factor_de_vale():
    p = sc.SedParams()
    assert (p.a, p.b, p.tc, p.cma, p.cmu) == (1.591, 203.0, 420.0, 4.9, 30.0)  # Torquato y Luz
    assert (p.z0, p.z_inf, p.rho_s, p.tph) == (0.4, 0.035, 4.0, 157.0)
    assert sc.FACTOR_VALOR[sc.FACTORES[0]] == 1.0 and sc.FACTOR_VALOR[sc.FACTORES[1]] == 0.64
    assert sc.ANIM_FACTOR == 3.0 and sc.LUZ_T_MAX_S == 86400.0


# ------------------------------------------------------------------ las tablas de la pestaña
def test_la_tabla_de_vale_tiene_31_filas_y_solo_dos_no_cuadran():
    frame = sed_tab.vale_frame()
    assert len(frame) == 31
    ok = frame.iloc[:, -1].tolist()
    assert ok.count("no") == 2 and ok[11] == "no" and ok[12] == "no"
    auc = frame["Área unitaria calculada"].tolist()
    assert auc[0] == pytest.approx(1.2195, abs=1e-3) and auc[11] == pytest.approx(0.9784, abs=1e-3)
    with i18n.use("en"):
        assert "Calculated unit area" in sed_tab.vale_frame().columns


def test_la_tabla_de_coe_clevenger_marca_cuales_cuadran():
    frame = sed_tab.coe_frame()
    assert frame.iloc[:, -1].tolist() == ["no", "sí", "sí", "no", "no"]
    assert frame["A calculada"].tolist() == [2.99, 4.29, 4.31, 4.21, 4.19]


def test_valores_literales_de_la_escala_la_barra_y_el_factor():
    assert (ss.MAX_SCALE_PX_M, ss.MAX_DIAMETER_PX, ss.CYL_PX) == (5.0, 340.0, 280.0)
    assert view(tph=157.0).diametro_m == pytest.approx(43.60, abs=0.01)
    assert ss.thickener_scale_px_per_m(43.6) == 5.0 and ss.thickener_scale_px_per_m(680.0) == 0.5
    assert sc.FACTOR_VALOR[sc.FACTORES[1]] == 0.64 and sc.ANIM_FACTOR == 3.0
    sin_factor = view(factor=sc.FACTORES[0])
    assert sin_factor.factor == 1.0 and view(factor=sc.FACTORES[1]).factor == 0.64
