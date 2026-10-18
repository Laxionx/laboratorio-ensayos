"""Pestaña Fusión (fase 2): el crisol animado, el balance de plomo y los controles salen del
cálculo de `muestreo.fusion`, que aquí se vuelve a ejecutar por otro camino."""

import math
import re
import sys
from pathlib import Path

import numpy as np
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

from muestreo import crisol  # noqa: E402
from muestreo import fusion as fu  # noqa: E402

F = calculo.FusionUIParams


def _heights(svg_text: str, cls: str) -> float:
    return float(re.search(rf'class="lb-{cls}" [^>]*? height="([\d.]+)"', svg_text).group(1))


def _count(svg_text: str, cls: str) -> int:
    return svg_text.count(f'class="lb-{cls}"')


# ------------------------------------------------------------------ crisol
def _polygon(svg_text: str, cls: str) -> list[tuple[float, float]]:
    raw = re.search(rf'class="lb-{cls}" points="([^"]+)"', svg_text).group(1)
    return [tuple(map(float, pt.split(","))) for pt in raw.split()]


def _drawn_volume_cm3(points: list[tuple[float, float]]) -> float:
    """Volumen de revolución del trapecio dibujado, integrado por rebanadas (no con la fórmula
    del tronco): suma de π·semiancho(y)²·dy, con el semiancho leído del lado derecho."""
    y0, y1 = points[0][1], points[2][1]  # abajo y arriba del trozo, en px
    xr0, xr1 = points[1][0], points[2][0]
    n = 4000
    ys = y0 + (y1 - y0) * (np.arange(n) + 0.5) / n
    half_px = np.interp(ys, [y1, y0], [xr1, xr0]) - fusion_svg.CX
    dy_cm = abs(y1 - y0) / n / fusion_svg.PX_PER_CM
    return float(np.sum(math.pi * (half_px / fusion_svg.PX_PER_CM) ** 2 * dy_cm))


def _top_y(points: list[tuple[float, float]]) -> float:
    return min(y for _, y in points)


FUZZ = [  # combinaciones de la pestaña, con extremos
    F(), F(x_flour=0.5), F(x_flour=2.0), F(x_silica=0.0), F(x_silica=3.0), F(x_litharge=0.3),
    F(x_litharge=2.0), F(sample="30 g", degree="mono"),
    F(sample="30 g", x_silica=3.0, x_litharge=2.0),
    F(minerals=(("cuarzo", 50.0), ("pirita", 30.0))), F(minerals=(("galena", 90.0),)),
    F(minerals=(("cuarzo", 10.0),), x_flour=0.0), F(button_g=5.0), F(button_g=60.0),
    F(degree="sesqui", sulfur="SO2"),
]  # fmt: skip


def _view_or_skip(params):
    try:
        return calculo.run_fusion(params)
    except fu.FusionError:
        pytest.skip("combinación que el modelo rechaza")


@pytest.mark.parametrize("params", FUZZ)
def test_el_nivel_del_plomo_queda_siempre_bajo_el_de_la_escoria(params):
    view = _view_or_skip(params)
    svg_text = fusion_svg.crucible_svg(view)
    lead, slag = _polygon(svg_text, "button"), _polygon(svg_text, "slag")
    assert _top_y(lead) > _top_y(slag)  # en el SVG, y mayor = más abajo
    lay = fusion_svg.view_layers(view)
    assert (lay.lead_top > 0.0) == (view.result.button_g > 0.0)
    assert 0.0 <= lay.lead_top < lay.slag_top <= crisol.CRUCIBLE.height
    assert _top_y(slag) >= fusion_svg.y_of(crisol.CRUCIBLE.height) - 1e-3  # no pasa del borde


@pytest.mark.parametrize("params", FUZZ)
def test_el_volumen_dibujado_de_cada_capa_es_el_calculado(params):
    view = _view_or_skip(params)
    r = view.result
    if r.lead_hot_cm3 + r.slag_cm3 > crisol.CRUCIBLE.capacity_cm3:
        pytest.skip("se derrama: el dibujo se corta en el borde")
    svg_text = fusion_svg.crucible_svg(view)
    lead_cm3 = _drawn_volume_cm3(_polygon(svg_text, "button"))
    assert lead_cm3 == pytest.approx(r.lead_hot_cm3, rel=2e-3)
    assert _drawn_volume_cm3(_polygon(svg_text, "slag")) == pytest.approx(r.slag_cm3, rel=2e-3)


def test_las_capas_se_dibujan_pegadas_a_la_pared_del_cono():
    view = calculo.run_fusion(F())
    svg_text = fusion_svg.crucible_svg(view)
    lay = fusion_svg.view_layers(view)
    for cls, z0, z1 in (("button", 0.0, lay.lead_top), ("slag", lay.lead_top, lay.slag_top)):
        (xl0, yb), (xr0, _), (xr1, yt), (xl1, _) = _polygon(svg_text, cls)
        for x, y, z in ((xl0, yb, z0), (xr0, yb, z0), (xl1, yt, z1), (xr1, yt, z1)):
            assert abs(x - fusion_svg.CX) == pytest.approx(
                crisol.CRUCIBLE.radius_at(z) * fusion_svg.PX_PER_CM, abs=0.002
            )
            assert y == pytest.approx(fusion_svg.y_of(z), abs=0.002)
    assert fusion_svg.y_of(0.0) == fusion_svg.BOTTOM


def test_el_plomo_es_liquido_y_el_boton_frio_es_una_metrica_aparte():
    view = calculo.run_fusion(F())
    r = view.result
    rho = (11367.0 - 1.1944 * (1050.0 + 273.15)) / 1000.0
    assert fu.pb_liquid_density(1050.0) == pytest.approx(rho) == pytest.approx(9.7866, abs=5e-5)
    assert r.lead_hot_cm3 == pytest.approx(r.button_g / rho)
    assert r.button_cm3 == pytest.approx(r.button_g / 11.34) == pytest.approx(28.0 / 11.34)
    assert r.lead_hot_cm3 > r.button_cm3  # el plomo líquido pesa menos por cm³ que el frío
    svg_text = fusion_svg.crucible_svg(view)
    assert "Plomo líquido" in svg_text and "Botón ya frío" in svg_text
    assert f"{str(round(r.button_cm3, 2)).replace('.', ',')} cm³" in svg_text


def test_un_boton_mas_chico_se_dibuja_mas_chico_y_con_menos_gotas():
    full = calculo.run_fusion(F())
    small = calculo.run_fusion(F(x_flour=0.5))
    assert small.result.button_g < full.result.button_g
    assert fusion_svg.view_layers(small).lead_top < fusion_svg.view_layers(full).lead_top
    assert _count(fusion_svg.crucible_svg(small), "drop") < _count(
        fusion_svg.crucible_svg(full), "drop"
    )


def test_mas_escoria_sube_el_nivel_de_la_escoria():
    a, b = calculo.run_fusion(F()), calculo.run_fusion(F(x_silica=2.5))
    assert b.result.slag_cm3 > a.result.slag_cm3
    assert fusion_svg.view_layers(b).slag_top > fusion_svg.view_layers(a).slag_top


def test_si_lo_fundido_pasa_del_borde_el_dibujo_se_corta_y_hay_aviso(monkeypatch):
    monkeypatch.setitem(calculo.FUSION_SAMPLE_G, "30 g", 200.0)
    view = calculo.run_fusion(F(sample="30 g"))
    r = view.result
    assert r.lead_hot_cm3 + r.slag_cm3 > crisol.CRUCIBLE.capacity_cm3
    assert fusion_svg.view_layers(view).overflows
    svg_text = fusion_svg.crucible_svg(view)
    assert _top_y(_polygon(svg_text, "slag")) == pytest.approx(
        fusion_svg.y_of(crisol.CRUCIBLE.height), abs=1e-3
    )
    assert _top_y(_polygon(svg_text, "button")) > _top_y(_polygon(svg_text, "slag"))
    assert any(w.level == "riesgo" and "capacidad" in w.text for w in r.warnings)


def test_las_gotas_y_las_burbujas_van_entre_el_plomo_y_la_escoria_en_la_version_quieta():
    view = calculo.run_fusion(F())
    still = fusion_svg.crucible_svg(view, paused=True)
    lay = fusion_svg.view_layers(view)
    y_slag, y_lead = fusion_svg.y_of(lay.slag_top), fusion_svg.y_of(lay.lead_top)
    for cls in ("drop", "bubble"):
        found = re.findall(rf'translate\(([\d.]+) ([\d.]+)\)"><circle class="lb-{cls}"', still)
        assert len(found) == _count(still, cls) > 0
        for x, y in ((float(a), float(b)) for a, b in found):
            assert y_slag <= y <= y_lead
            assert abs(x - fusion_svg.CX) <= fusion_svg.half_width_px(lay.lead_top)


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


def test_el_color_es_el_de_1050_grados_y_se_rotula_el_plomo_liquido():
    svg_text = fusion_svg.crucible_svg(calculo.run_fusion(F()))
    assert f'fill="{colores.temperature_color(1050.0)}"' in svg_text
    assert fu.FUSION_TEMP_C == 1050.0 and fu.PB_DENSITY == 11.34
    assert "OECD/NEA" in svg_text and "color ilustrativo de la temperatura" in svg_text
    assert "190 cm³" in svg_text and "Bugbee" in svg_text
    assert "ilustrativ" in svg_text and "no a escala" in svg_text


def test_el_esquema_trae_la_carga_el_boton_y_la_escoria():
    view = calculo.run_fusion(F())
    svg_text = fusion_svg.crucible_svg(view)
    r = view.result
    assert f"Plomo líquido: {str(round(r.button_g, 1)).replace('.', ',')} g" in svg_text
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
    assert _polygon(still, "slag") == _polygon(moving, "slag")
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


def test_la_linea_de_los_dos_tercios_es_la_del_volumen_no_la_de_la_altura():
    svg_text = fusion_svg.crucible_svg(calculo.run_fusion(F()))
    y = float(re.search(r'class="lb-limit" x1="[\d.]+" y1="([\d.]+)"', svg_text).group(1))
    z = crisol.CRUCIBLE.level_for(2 / 3 * crisol.CRUCIBLE.capacity_cm3)
    assert y == pytest.approx(fusion_svg.y_of(z), abs=0.006)
    assert z != pytest.approx(2 / 3 * crisol.CRUCIBLE.height, abs=0.3)  # en el cono no coinciden
    assert "2/3 de la capacidad" in svg_text
