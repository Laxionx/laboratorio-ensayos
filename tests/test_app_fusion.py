"""Pestaña Fusión (fase 2): el crisol animado, el balance de plomo y los controles salen del
cálculo de `muestreo.fusion`, que aquí se vuelve a ejecutar por otro camino."""

import math
import re
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app" / "streamlit_app.py")
sys.path.insert(0, str(ROOT / "app"))

import calculo  # noqa: E402
import colores  # noqa: E402
import controles  # noqa: E402
import fusion_graficos  # noqa: E402
import fusion_svg  # noqa: E402
import fusion_tab  # noqa: E402

from muestreo import fusion as fu  # noqa: E402

F = calculo.FusionUIParams


def _heights(svg_text: str, cls: str) -> float:
    return float(re.search(rf'class="lb-{cls}" [^>]*? height="([\d.]+)"', svg_text).group(1))


def _count(svg_text: str, cls: str) -> int:
    return svg_text.count(f'class="lb-{cls}"')


# ------------------------------------------------------------------ crisol
@pytest.mark.parametrize(
    "params", [F(), F(x_flour=0.5), F(x_silica=2.0), F(sample="30 g", degree="mono")]
)
def test_altura_de_la_escoria_es_su_volumen_sobre_la_seccion_del_crisol(params):
    view = calculo.run_fusion(params)
    svg_text = fusion_svg.crucible_svg(view)
    mass = view.result.slag.mass_g
    expected_cm = mass / 3.0 / (math.pi * 3.0**2)  # masa ÷ ρ supuesta ÷ π R²
    assert fusion_svg.slag_height_cm(mass) == pytest.approx(expected_cm, rel=1e-12)
    assert _heights(svg_text, "slag") == pytest.approx(
        expected_cm * fusion_svg.PX_PER_CM, abs=0.006
    )


def test_la_altura_de_la_escoria_es_proporcional_a_su_masa():
    a = calculo.run_fusion(F())
    b = calculo.run_fusion(F(x_silica=2.5))
    ratio_mass = b.result.slag.mass_g / a.result.slag.mass_g
    ratio_height = _heights(fusion_svg.crucible_svg(b), "slag") / _heights(
        fusion_svg.crucible_svg(a), "slag"
    )
    assert ratio_mass > 1.05 and ratio_height == pytest.approx(ratio_mass, rel=1e-3)


def test_la_escoria_se_corta_en_el_alto_del_crisol():
    assert fusion_svg.slag_height_px(10_000.0) == fusion_svg.interior_px()[1]


def test_el_boton_es_una_esfera_de_volumen_masa_sobre_11_34():
    view = calculo.run_fusion(F())
    svg_text = fusion_svg.crucible_svg(view)
    volume = view.result.button_g / 11.34
    radius_cm = (3 * volume / (4 * math.pi)) ** (1 / 3)
    radius_px = float(re.search(r'class="lb-button" [^>]*? r="([\d.]+)"', svg_text).group(1))
    assert radius_px == pytest.approx(radius_cm * fusion_svg.PX_PER_CM, abs=0.006)
    assert (4 / 3) * math.pi * radius_cm**3 == pytest.approx(view.result.button_cm3, rel=1e-12)
    assert view.result.button_cm3 == pytest.approx(28.0 / 11.34)


def test_un_boton_mas_chico_se_dibuja_mas_chico_y_con_menos_gotas():
    full = calculo.run_fusion(F())
    small = calculo.run_fusion(F(x_flour=0.5))
    assert small.result.button_g < full.result.button_g
    r_full = fusion_svg.button_radius_cm(full.result.button_g)
    r_small = fusion_svg.button_radius_cm(small.result.button_g)
    assert r_small < r_full
    assert _count(fusion_svg.crucible_svg(small), "drop") < _count(
        fusion_svg.crucible_svg(full), "drop"
    )


@pytest.mark.parametrize(
    "params", [F(), F(x_flour=1.8), F(minerals=calculo.FusionUIParams().minerals, button_g=35.0)]
)
def test_las_gotas_son_proporcionales_a_los_gramos_de_plomo(params):
    view = calculo.run_fusion(params)
    svg_text = fusion_svg.crucible_svg(view)
    assert _count(svg_text, "drop") == round(0.5 * view.result.button_g)
    assert fusion_svg.drop_count(view.result.button_g) == _count(svg_text, "drop")
    assert fusion_svg.DROPS_PER_G == 0.5


def test_las_burbujas_son_las_de_los_moles_de_gas_del_calculo():
    view = calculo.run_fusion(F())
    svg_text = fusion_svg.crucible_svg(view)
    expected = min(30, round(60.0 * sum(view.result.gas_mol.values())))
    assert _count(svg_text, "bubble") == expected == fusion_svg.bubble_count(view.result.gas_mol)
    so2 = calculo.run_fusion(F(minerals=(("cuarzo", 60.0), ("pirita", 20.0)), sulfur="SO2"))
    assert so2.result.gas_mol["SO2"] > 0


def test_el_color_es_el_de_1050_grados_y_el_boton_es_plomo_solido():
    svg_text = fusion_svg.crucible_svg(calculo.run_fusion(F()))
    assert f'fill="{colores.temperature_color(1050.0)}"' in svg_text
    assert fu.FUSION_TEMP_C == 1050.0 and fu.PB_DENSITY == 11.34
    assert "11,34" in svg_text and "color ilustrativo de la temperatura" in svg_text
    assert "ilustrativ" in svg_text and "no a escala" in svg_text


def test_el_esquema_trae_la_carga_el_boton_y_la_escoria():
    view = calculo.run_fusion(F())
    svg_text = fusion_svg.crucible_svg(view)
    r = view.result
    assert f"Botón de plomo: {str(round(r.button_g, 1)).replace('.', ',')} g" in svg_text
    assert f"grado {r.slag.label}" in svg_text
    for grams in (view.used.soda_g, view.used.litharge_g, view.used.flour_g):
        assert f"{grams:.1f}".replace(".", ",") in svg_text
    changed = fusion_svg.crucible_svg(calculo.run_fusion(F(x_flour=0.5)))
    assert "calculada" in changed and "calculada" not in svg_text


def test_la_version_quieta_no_se_mueve_y_la_animada_si():
    view = calculo.run_fusion(F())
    moving, still = fusion_svg.crucible_svg(view), fusion_svg.crucible_svg(view, paused=True)
    assert "@keyframes lb-rise" in moving and "prefers-reduced-motion" in moving
    assert "animation" not in still and "@keyframes" not in still
    assert _count(still, "drop") == _count(moving, "drop")
    assert _heights(still, "slag") == _heights(moving, "slag")
    durations = {float(d) for d in re.findall(r"animation-duration:([\d.]+)s", moving)}
    assert durations == {fusion_svg.FALL_S, fusion_svg.BUBBLE_S}
    assert "<script" not in moving.lower() and "javascript:" not in moving.lower()


# ------------------------------------------------------------------ balance y calculo
def test_el_balance_del_plomo_suma_el_boton():
    view = calculo.run_fusion(F())
    rows = dict(fusion_graficos.balance_rows(view))
    assert rows["muestra"] + rows["harina"] + rows["nitro"] == pytest.approx(rows["botón"])
    fig = fusion_graficos.balance_figure(view)
    assert list(fig.data[0].y) == pytest.approx(
        [rows[k] for k in ("muestra", "harina", "nitro", "botón")]
    )
    assert fig.layout.shapes[0].y0 == 25.0 and fig.layout.shapes[0].y1 == 30.0


def test_con_mucho_sulfuro_el_balance_resta_el_nitro():
    view = calculo.run_fusion(F(minerals=(("cuarzo", 50.0), ("pirita", 30.0))))
    rows = dict(fusion_graficos.balance_rows(view))
    assert rows["muestra"] > 28.0 and rows["nitro"] < 0 and rows["harina"] == 0.0
    assert rows["botón"] == pytest.approx(28.0)


def test_las_filas_de_mineralogia_son_porcentaje_gramos_y_poder_reductor():
    view = calculo.run_fusion(F())
    by_name = {r[0]: r for r in view.rows}
    _, pct, grams, rp, pb = by_name["Pirita"]
    assert (pct, grams) == (3.0, pytest.approx(0.03 * fu.AT_G))
    assert rp == pytest.approx(fu.reducing_power("pirita", "SO3")) and pb == pytest.approx(
        grams * rp
    )
    assert by_name["Hematita"][4] < 0  # la hematita oxida
    assert "Cuarzo" in by_name and "Galena" not in by_name  # solo los minerales presentes


def test_la_muestra_puede_ser_30_g_en_vez_de_un_assay_ton():
    at_view = calculo.run_fusion(F())
    g30 = calculo.run_fusion(F(sample="30 g"))
    assert at_view.params.sample_g == fu.AT_G and g30.params.sample_g == 30.0
    assert g30.designed.soda_g > at_view.designed.soda_g


# ------------------------------------------------------------------ controles y app
def _run() -> AppTest:
    return AppTest.from_file(APP, default_timeout=180).run()


def test_los_controles_de_fusion_salen_de_la_misma_definicion():
    keys = {d.key for d in controles.DATOS if d.group == controles.FUS}
    assert {"m_" + m.key for m in fu.MINERALS} <= keys  # los 9 minerales vienen de fusion.MINERALS
    assert len(fu.MINERALS) == 9
    assert {"f_sample", "f_sulfur", "f_button", "f_degree", "f_flour", "f_niter", "f_soda",
            "f_lith", "x_flour", "x_silica", "x_lith"} <= keys  # fmt: skip
    at = _run()
    widget_keys = {w.key for w in [*at.sidebar.number_input, *at.sidebar.selectbox]}
    assert {controles.PREFIX + k for k in keys} <= widget_keys
    table = controles.data_table(controles.FUS)
    assert list(table["Dato"]) == [d.label for d in controles.DATOS if d.group == controles.FUS]
    assert (
        controles.BY_KEY["f_flour"].default == 11 and "10 a 12" in controles.BY_KEY["f_flour"].help
    )
    assert "Bugbee" in controles.BY_KEY["f_niter"].help


def test_la_pestana_de_fusion_carga_con_la_carga_calculada_sin_avisos_de_boton():
    at = _run()
    assert not at.exception and not at.error
    values = {m.label: m.value for m in at.metric}
    assert values["Botón de plomo"] == "28,0 g"
    assert values["Grado de silicato"] == "bi (2,00)"
    assert not any("Botón de" in w.value or "fuera de" in w.value for w in at.warning)


def test_una_carga_con_la_harina_a_la_mitad_avisa_boton_chico():
    at = _run()
    flour = next(w for w in at.sidebar.number_input if w.key == controles.PREFIX + "x_flour")
    flour.set_value(0.5).run()
    assert not at.exception
    assert any("fuera de 25 a 30 g" in w.value for w in at.warning)
    assert any("carga cambiada" in i.value for i in at.info)


def test_mucha_sílice_avisa_escoria_acida_y_riesgo_de_mata_con_sulfuros():
    at = _run()
    sets = {"m_pirita": 25.0, "m_cuarzo": 50.0, "x_silica": 3.0}
    for w in at.sidebar.number_input:
        key = w.key.removeprefix(controles.PREFIX)
        if key in sets:
            w.set_value(sets[key])
    at.run()
    assert not at.exception
    texts = " ".join(w.value for w in at.warning)
    assert "Riesgo" in texts and "Fuente:" in texts


def test_los_minerales_que_suman_mas_de_100_se_avisan_sin_traza():
    at = _run()
    for w in at.sidebar.number_input:
        if w.key in (controles.PREFIX + "m_cuarzo", controles.PREFIX + "m_pirita"):
            w.set_value(90.0)
    at.run()
    assert not at.exception
    assert any("no pueden pasar de 100 %" in e.value for e in at.error)


def test_un_fallo_del_modelo_de_fusion_se_muestra_sin_traza(monkeypatch):
    def fails(params):
        raise fu.FusionError("la masa de la muestra debe ser positiva")

    monkeypatch.setattr(fusion_tab, "run_fusion", fails)
    at = _run()
    assert not at.exception
    assert any("debe ser positiva" in e.value for e in at.error)


def test_la_validacion_incluye_la_seccion_de_fusion_con_el_resumen():
    at = _run()
    text = " ".join(m.value for m in at.markdown)
    assert "Fase 2: carga fundente" in text
    assert "67 cifras publicadas" in text and "43" in text
    assert "Poderes reductores medidos por Bugbee" in text and "no son corte" in text
    assert "Cargas del USGS 1445" in text


def test_la_guia_explica_las_reacciones_y_que_dato_pide_cada_reactivo():
    at = _run()
    text = " ".join(m.value for m in at.markdown)
    for fragment in ("2PbO + C = 2Pb + CO₂", "4KNO₃ + 5C", "Qué dato pide cada reactivo",
                     "grado de silicato"):  # fmt: skip
        assert fragment in text
