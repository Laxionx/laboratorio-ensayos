"""Pestaña «Copelación» sin levantar Streamlit: la animación sale del cálculo (masa del botón y de
la perla en cada cuadro, radio = (volumen / volumen inicial)^(1/3), color de la mufla =
temperatura), los gráficos llevan las tablas de Bugbee y los controles salen de una sola
definición."""

import itertools
import re
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
pytest.importorskip("plotly")

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import controles  # noqa: E402
import cop_calculo as cc  # noqa: E402
import cop_estado  # noqa: E402
import cop_graficos as cg  # noqa: E402
import cop_svg as cs  # noqa: E402
import cop_tab  # noqa: E402
import i18n  # noqa: E402
from calculo import FusionUIParams  # noqa: E402
from colores import temperature_color  # noqa: E402
from dibujo import as_images, es  # noqa: E402

from muestreo import copelacion as cp  # noqa: E402
from muestreo import copelacion_datos as cd  # noqa: E402

SPANISH = re.compile(
    r"[áéíóúñ¿¡]|\b(de|del|la|las|los|el|con|para|por|una|sin|que|se|más|muy)\b", re.IGNORECASE
)


def view(boton: float | None = 28.0, **kw) -> cc.CopView:
    return cc.run_cop(cc.CopParams(**kw), boton)


def _keyframes(svg: str, name: str) -> list[tuple[float, str]]:
    body = re.search(rf"@keyframes {name}\{{(.*?)\}}\}}", svg, re.S).group(1) + "}"
    return [(float(p), v) for p, v in re.findall(r"([\d.]+)%\{([^}]*)\}", body)]


def _values(svg: str, name: str, pattern: str) -> list[float]:
    return [float(re.search(pattern, v).group(1)) for p, v in _keyframes(svg, name) if p < 100.0]


def _strip(svg: str) -> list[str]:
    return re.findall(r'<text x="0.0" y="[\d.]+"[^>]*>([^<]+)</text>', svg)


def _volume(pb_mg: float, au_mg: float, ag_mg: float, rho_pb: float) -> float:
    """Volumen del botón calculado aquí, con las constantes escritas de nuevo (no las del módulo)"""
    return pb_mg / 1000 / rho_pb + au_mg / 1000 / 19.32 + ag_mg / 1000 / 10.49


# ------------------------------------------------------------------ el botón sale del cálculo
def test_la_masa_del_boton_en_cada_cuadro_es_plomo_mas_oro_mas_plata_del_calculo():
    v = view()
    r = v.res
    mass = _strip(cs.copelacion_svg(v))[cc.FRAMES : 2 * cc.FRAMES]
    assert len(mass) == cc.FRAMES == 49
    cuadros = v.cuadros
    assert mass == [es(c.masa_mg, 1) for c in cuadros]
    # el primero es el botón entero (28 g de la fusión + oro + plata total), sin tocar el modelo
    assert mass[0] == es(28000.0 + 1.0 + r.plata_total_mg, 1)
    # el último es la perla: oro y plata que quedan tras las pérdidas de las tablas
    perla = 1.0 * (1 - r.perdida_au.frac) + r.plata_total_mg * (1 - r.perdida_ag.frac)
    assert mass[-1] == es(perla, 1) and cuadros[-1].masa_mg == pytest.approx(perla)
    assert all(a.masa_mg >= b.masa_mg for a, b in itertools.pairwise(cuadros))


def test_la_perla_dibujada_es_la_perla_del_calculo_a_escala_de_volumen():
    v = view()
    svg = cs.copelacion_svg(v)
    scales = _values(svg, "lb-btn", r"scale\(([\d.]+)\)")
    assert len(scales) == cc.FRAMES and scales[0] == 1.0
    r = v.res
    v0 = _volume(28000.0, 1.0, r.plata_total_mg, v.rho_plomo)
    vf = _volume(0.0, r.oro_final_mg, r.plata_final_mg, v.rho_plomo)
    assert scales[-1] == pytest.approx((vf / v0) ** (1 / 3), abs=2e-5)
    assert all(a >= b for a, b in itertools.pairwise(scales))
    for i in (10, 24, 40):
        c = v.cuadros[i]
        vi = _volume(c.plomo_mg, c.oro_mg, c.plata_mg, v.rho_plomo)
        assert scales[i] == pytest.approx((vi / v0) ** (1 / 3), abs=2e-5)


def test_el_plomo_de_la_fusion_cambia_el_boton_y_el_dibujo():
    a, b = view(28.0), view(20.0)
    assert a.plomo_g == 28.0 and b.plomo_g == 20.0 and a.plomo_de_fusion
    assert cs.clock_values(a)[1][0] != cs.clock_values(b)[1][0]
    assert cs.clock_values(b)[1][0] == es(20000.0 + 1.0 + b.res.plata_total_mg, 1)
    assert cs.clock_values(b)[2][0] == es(20.0, 2) and cs.clock_values(b)[2][-1] == es(0.0, 2)


def test_el_color_de_la_mufla_es_el_de_la_temperatura():
    for temp in (700.0, 800.0, 950.0, 1075.0):
        svg = cs.copelacion_svg(view(temp_c=temp))
        assert f'fill="{temperature_color(temp)}" fill-opacity="0.9"' in svg
    assert temperature_color(800.0) == "#CD4216"
    colors = {temperature_color(t) for t in (700.0, 800.0, 950.0)}
    assert len(colors) == 3


def test_el_color_del_boton_va_del_gris_plomo_al_color_de_la_perla_segun_la_composicion():
    v = view()
    frames = _keyframes(cs.copelacion_svg(v), "lb-btnc")
    colors = [c.removeprefix("fill:") for _, c in frames if _ < 100.0]
    assert colors[0] == cs.frame_color(v.cuadros[0]) and colors[0] != colors[-1]
    ley = v.cuadros[-1].ley_oro
    assert colors[-1] == cs.mix(cs.GOLD, cs.SILVER, ley)
    assert ley == pytest.approx(v.res.oro_en_perla)
    # más oro en los preciosos: la perla se ve más dorada
    rico = cs.frame_color(view(oro_mg=50.0, plata_mg=5.0).cuadros[-1])
    pobre = cs.frame_color(view(oro_mg=0.1, plata_mg=5.0).cuadros[-1])
    assert cs.hex_rgb(rico)[2] < cs.hex_rgb(pobre)[2]  # el dorado tiene menos azul


def test_la_copela_se_oscurece_con_el_plomo_absorbido():
    v = view()
    soak = _values(cs.copelacion_svg(v), "lb-soak", r"opacity:([\d.]+)")
    assert soak[0] == 0.0 and soak[-1] == pytest.approx(cs.SOAK_MAX, abs=1e-4)
    assert soak == sorted(soak)
    pb = [c.plomo_mg for c in v.cuadros]
    assert soak[24] == pytest.approx(cs.SOAK_MAX * (1 - pb[24] / pb[0]), abs=1e-4)


def test_el_tiempo_es_ilustrativo_y_asi_se_rotula_en_los_dos_idiomas():
    v = view()
    for lang, needle in (("es", "ilustrativos"), ("en", "illustrative")):
        with i18n.use(lang):
            svg = cs.copelacion_svg(v)
        assert needle in svg and "Fig. 40" in svg and "12 s" in svg
    with i18n.use("es"):
        svg = cs.copelacion_svg(v)
    assert "Esquema, no a escala: las cantidades sí son del cálculo" in svg
    assert "Avance (ilustrativo)" in svg
    css = svg.split("</style>")[0]
    assert "animation:lb-btn 14s linear infinite" in css
    assert (cs.RUN_S, cs.HOLD_S) == (12.0, 2.0)


def test_los_relojes_usan_el_formato_del_idioma():
    v = view()
    for lang, sep in (("es", ","), ("en", ".")):
        with i18n.use(lang):
            progress, mass, lead = cs.clock_values(v)
            expected = [es(c.masa_mg, 1) for c in v.cuadros]
        assert progress[0] == "0" and progress[-1] == "100" and progress[24] == "50"
        assert lead[0] == f"28{sep}00" and lead[-1] == f"0{sep}00"
        assert mass == expected and mass[-1] == expected[-1] and f"{sep}" in mass[0]
    with i18n.use("en"):
        assert re.fullmatch(r"28,\d{3}\.\d", cs.clock_values(v)[1][0])
    with i18n.use("es"):
        assert re.fullmatch(r"28 \d{3},\d", cs.clock_values(v)[1][0])


def test_quieta_no_hay_animacion_y_con_movimiento_si():
    v = view()
    moving, still = cs.copelacion_svg(v), cs.copelacion_svg(v, paused=True)
    assert "animation:lb-btn" in moving and "@keyframes" in moving
    assert "animation" not in still.split("</style>")[1] and "@keyframes" not in still
    last = v.escalas[-1]
    assert f"scale({last:.5f})" in still and "transform-origin:50% 100%" in still
    assert f"fill:{cs.frame_color(v.cuadros[-1])}" in still
    assert f"opacity:{cs.SOAK_MAX * (1 - 0.0):.4f}" in still
    both, one = as_images(moving, still, "alt"), as_images(still, still, "alt")
    assert both.count("<img") == 2 and one.count("<img") == 1


def test_el_esquema_en_ingles_no_lleva_espanol():
    v = view()
    with i18n.use("en"):
        svg = cs.copelacion_svg(v)
    texts = re.findall(r">([^<]+)</text>", svg) + re.findall(r'aria-label="([^"]+)"', svg)
    assert not [x for x in texts if SPANISH.search(x)], texts
    assert any("Cupellation" in x for x in texts)


def test_el_texto_de_los_datos_no_entra_al_svg_y_los_numeros_son_del_calculo():
    v = view(oro_mg=2.5, plata_mg=7.0)
    svg = cs.copelacion_svg(v)
    assert "<script" not in svg.lower() and "javascript" not in svg.lower()
    r = v.res
    assert f"Perla: {es(r.perla_mg, 2)} mg" in svg
    assert f"pérdida {es(r.perdida_ag.pct, 2)} %" in svg


# ------------------------------------------------------------------ el cálculo de la pestaña
def test_la_fuente_del_plomo_la_fusion_o_la_propia_con_aviso_si_la_fusion_falla():
    own = view(boton=28.0, plomo_fuente=cc.FUENTES_PLOMO[1], plomo_g=18.0)
    assert own.plomo_g == 18.0 and not own.plomo_de_fusion and not own.fusion_no_sirve
    broken = view(boton=None)
    assert broken.plomo_g == 28.0 and broken.fusion_no_sirve and not broken.plomo_de_fusion
    bad = FusionUIParams(minerals=(("pirita", 150.0),))
    assert cc.boton_de_fusion(bad) is None
    assert cc.boton_de_fusion(FusionUIParams()) == pytest.approx(28.0, abs=0.5)


def test_la_ley_corregida_usa_la_perdida_de_oro_del_calculo():
    v = view(ley_gpt=5.0)
    assert v.ley_au_corregida == pytest.approx(5.0 / (1 - v.res.perdida_au.frac))
    assert v.ley_au_corregida > 5.0


def test_los_modos_de_la_razon_y_sus_rotulos():
    assert list(cc.MODO_CLAVE.values()) == list(cp.MODOS_RAZON)
    assert view(modo=cc.MODOS[1]).res.razon_objetivo == 3.0
    assert view(modo=cc.MODOS[2], razon=12.0).res.razon_objetivo == 12.0
    assert view().res.razon_objetivo == pytest.approx(cp.razon_rose(1.0)) == 6.0


@pytest.mark.parametrize("malo", [float("nan"), float("inf"), -float("inf"), -1.0])
def test_datos_manipulados_se_rechazan_con_error_de_la_pestana(malo):
    own = {"plomo_fuente": cc.FUENTES_PLOMO[1], "plomo_g": malo}
    for kw, boton in (({"temp_c": malo}, 28.0), ({"oro_mg": malo}, 28.0), (own, None),
                      ({"plata_mg": malo}, 28.0), ({"ley_gpt": malo}, 28.0)):  # fmt: skip
        with pytest.raises(cp.CopelacionError):
            cc.run_cop(cc.CopParams(**kw), boton)


def test_ceros_la_ley_cero_es_valida_pero_no_la_temperatura_ni_el_oro_ni_el_plomo():
    assert (
        view(ley_gpt=0.0).ley_au_corregida == 0.0 and view(plata_mg=0.0).res.plata_agregada_mg > 0
    )
    for kw in ({"temp_c": 0.0}, {"oro_mg": 0.0}, {"plomo_fuente": "Valor propio", "plomo_g": 0.0}):
        with pytest.raises(cp.CopelacionError):
            cc.run_cop(cc.CopParams(**kw), None)


def test_cada_error_y_cada_aviso_tiene_texto_en_los_dos_idiomas():
    for code in ("temp", "plomo", "plata", "oro", "ley", "perdida", "razon", "modo", "cuadros"):
        assert f"cp.err.{code}" in i18n.TEXTS["es"] and f"cp.err.{code}" in i18n.TEXTS["en"]
    for code in ("temp", "plomo", "plata", "congelado", "fusion"):
        assert f"cp.warn.{code}" in i18n.TEXTS["es"] and f"cp.warn.{code}" in i18n.TEXTS["en"]
    for lang in ("es", "en"):
        with i18n.use(lang):
            for code in ("temp", "plomo", "plata", "congelado"):
                assert "{" not in cop_estado.range_text(code)
            for code in ("temp", "plomo", "plata", "oro", "ley", "perdida", "razon", "modo"):
                assert "{" not in cop_tab._error_text(cp.CopelacionError(code))


# ------------------------------------------------------------------ los controles
GROUP = [d for d in controles.DATOS if d.group == controles.COP]


def test_los_ocho_controles_salen_de_una_sola_definicion():
    assert [d.key for d in GROUP] == ["k_temp", "k_pb_src", "k_pb", "k_au", "k_ag", "k_modo",
                                      "k_razon", "k_ley"]  # fmt: skip
    table = controles.data_table(controles.COP)
    assert (
        len(table) == len(GROUP) and table.iloc[0][i18n.t("col.dato")] == "Temperatura de la copela"
    )
    params = cc.CopParams()
    defaults = {d.key: d.default for d in GROUP}
    assert (params.temp_c, params.plomo_fuente, params.plomo_g, params.oro_mg, params.plata_mg,
            params.modo, params.razon, params.ley_gpt) == tuple(defaults.values())  # fmt: skip
    assert controles.BY_KEY["k_pb_src"].options == cc.FUENTES_PLOMO
    assert controles.BY_KEY["k_modo"].options == cc.MODOS


def test_todas_las_opciones_de_las_listas_tienen_rotulo_en_los_dos_idiomas():
    for lang in ("es", "en"):
        with i18n.use(lang):
            for d in GROUP:
                for option in d.options:
                    assert i18n.TEXTS[lang]["opt." + option] == i18n.opt(option)


# ------------------------------------------------------------------ los gráficos
def test_el_grafico_de_temperatura_lleva_las_tablas_ix_y_xii_y_el_punto_del_calculo():
    v = view(temp_c=900.0)
    fig = cg.temperature_figure(v)
    by_name = {tr.name: tr for tr in fig.data}
    ix = by_name[i18n.t("cp.plot.ix")]
    assert list(ix.x) == [700.0, 775.0, 850.0, 925.0, 1000.0]
    assert list(ix.y) == [1.02, 1.30, 1.73, 3.65, 4.88]
    xii = by_name[i18n.t("cp.plot.xii")]
    assert list(xii.x) == [775.0, 850.0, 925.0, 1000.0, 1075.0]
    assert list(xii.y) == [0.155, 0.385, 0.460, 1.435, 2.990]
    mine = by_name[i18n.t("cp.plot.you.ag")]
    assert list(mine.x) == [900.0] and mine.y[0] == pytest.approx(v.res.perdida_ag.pct)
    model = by_name[i18n.t("cp.plot.model.ag")]
    for x, y in zip(model.x, model.y, strict=True):
        assert y == pytest.approx(cp.perdida_plata(x, 10.0, 200.0).pct)


def test_el_grafico_del_plomo_y_el_de_la_plata_llevan_las_tablas_x_y_xi_y_a_godshall():
    v = view()
    pb = {tr.name: tr for tr in cg.lead_figure(v).data}
    assert list(pb[i18n.t("cp.plot.x")].x) == [10.0, 15.0, 20.0, 25.0]
    assert list(pb[i18n.t("cp.plot.x")].y) == [1.39, 1.38, 1.52, 1.85]
    god = pb[i18n.t("cp.plot.god200")]
    assert list(god.y) == [1.51, 1.77, 1.92, 2.10]
    assert list(god.x) == pytest.approx([7.291675, 14.58335, 21.875025, 29.1667])
    ag = {tr.name: tr for tr in cg.silver_figure(v).data}
    xi = ag[i18n.t("cp.plot.xi")]
    assert list(xi.x) == [200.0, 100.0, 50.0, 20.0, 10.0, 5.0, 2.0]
    assert list(xi.y) == pytest.approx([p / 1.73 for _, p in cd.TABLA_XI])
    model = ag[i18n.t("cp.plot.model.ag.rel")]
    assert min(model.y) == 1.0 and max(model.y) == pytest.approx(6.90 / 1.73)
    reps = [ag[i18n.t(f"cp.plot.rep.{k}")] for k in ("primera", "tercera")]
    assert all(len(tr.y) == 7 and tr.y[-1] == 1.0 for tr in reps)


def test_los_graficos_en_ingles_no_llevan_espanol():
    import json

    v = view()
    for lang in ("es", "en"):
        with i18n.use(lang):
            figs = [cg.temperature_figure(v), cg.lead_figure(v), cg.silver_figure(v)]
            blob = " ".join(json.dumps(f.to_plotly_json(), ensure_ascii=False) for f in figs)
        if lang == "en":
            texts = re.findall(r'"(?:text|title|name|annotation_text)": "([^"]+)"', blob)
            texts += re.findall(r'"title": \{"text": "([^"]+)"', blob)
            assert texts and not [x for x in texts if SPANISH.search(x)], texts[:6]
        else:
            assert "Pérdida contra temperatura" in blob


def test_el_cuadro_de_la_mitad_sigue_la_formula_de_la_perdida_acumulada_escrita_aparte():
    """Cuadro 24 de 48 (avance 0,5): la masa, con la fórmula de Rose escrita de nuevo."""
    import math

    v = view()
    r = v.res
    m, pb = 1.0 + r.plata_total_mg, 28000.0
    acum = math.log((m + pb) / (m + pb * 0.5)) / math.log((m + pb) / m)
    esperada = (
        pb * 0.5
        + 1.0 * (1 - r.perdida_au.frac * acum)
        + r.plata_total_mg * (1 - r.perdida_ag.frac * acum)
    )
    c = v.cuadros[24]
    assert c.avance == 0.5 and c.perdida_acum == pytest.approx(acum)
    assert c.masa_mg == pytest.approx(esperada) and acum == pytest.approx(
        0.0839, abs=1e-4
    )  # convexa: con la mitad del plomo, 8 %


def test_la_densidad_del_plomo_es_la_de_la_ecuacion_de_la_fusion_a_la_temperatura_de_copela():
    assert view(temp_c=800.0).rho_plomo == pytest.approx(10.08522964)
    assert view(temp_c=1000.0).rho_plomo == pytest.approx(9.84634964)
    assert view(temp_c=800.0).escalas[-1] != view(temp_c=1000.0).escalas[-1]
