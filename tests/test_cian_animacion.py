"""Pestaña «Cianuración en botella» sin levantar Streamlit: la botella y los gráficos salen del
cálculo (rpm, avance de la recuperación = modelo), la tabla se valida en el servidor y los
controles salen de una sola definición."""

import base64
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

import cian_calculo as cc  # noqa: E402
import cian_graficos as cg  # noqa: E402
import cian_svg as cs  # noqa: E402
import cian_tab  # noqa: E402
import controles  # noqa: E402
import i18n  # noqa: E402
from dibujo import as_images  # noqa: E402

from muestreo import cianuracion as c  # noqa: E402
from muestreo import cianuracion_datos as cd  # noqa: E402

T, SOL, RES = list(cd.T_H), list(cd.SOLUCION_PPB), list(cd.RESIDUO_PPB)
SPANISH = re.compile(
    r"[áéíóúñ¿¡]|\b(de|del|la|las|los|el|con|para|por|una|sin|que|se|más|muy)\b", re.IGNORECASE
)


def view(**kw) -> cc.CianView:
    return cc.run_cian(cc.CianParams(**kw), T, SOL, RES)


def _keyframes(svg: str, name: str) -> list[tuple[float, str]]:
    body = re.search(rf"@keyframes {name}\{{(.*?)\}}\}}", svg, re.S).group(1) + "}"
    return [(float(p), v) for p, v in re.findall(r"([\d.]+)%\{([^}]*)\}", body)]


def _bar_values(svg: str) -> list[float]:
    return [
        float(re.search(r"scaleX\(([\d.]+)\)", v).group(1))
        for p, v in _keyframes(svg, "lb-bar")
        if p < 100.0
    ]


def _strip(svg: str, x: int) -> list[str]:
    """Los textos del reloj cuya ventana empieza en `x` (relativo al marco del reloj)."""
    return re.findall(r'<text x="0.0" y="[\d.]+"[^>]*>([^<]+)</text>', svg)


# ------------------------------------------------------------------ la botella gira a las rpm
@pytest.mark.parametrize("rpm", [30.0, 31.0, 32.0])
def test_la_botella_gira_con_un_periodo_de_60_sobre_rpm(rpm):
    svg = cs.bottle_svg(view(rpm=rpm))
    period = float(re.search(r'class="lb-spin" style="[^"]*animation-duration:([\d.]+)s', svg)[1])
    assert period == pytest.approx(60.0 / rpm, abs=5e-4)
    assert cs.rotation_period_s(rpm) == 60.0 / rpm
    assert f"{rpm:.1f}".replace(".", ",") + " rpm" in svg


def test_quieta_no_hay_animacion_y_con_movimiento_si():
    moving, still = cs.bottle_svg(view()), cs.bottle_svg(view(), paused=True)
    assert "animation:lb-spin" in moving and "@keyframes lb-bar" in moving
    assert "animation" not in still.split("</style>")[1] and "@keyframes" not in still
    assert "lb-spin" in still  # el grupo existe, solo que quieto


def test_la_pestana_entrega_las_dos_versiones_y_una_sola_sin_movimiento():
    v = view()
    both = as_images(cs.bottle_svg(v), cs.bottle_svg(v, paused=True), "alt")
    one = as_images(cs.bottle_svg(v, paused=True), cs.bottle_svg(v, paused=True), "alt")
    assert both.count("<img") == 2 and "lb-anim" in both and "lb-still" in both
    assert one.count("<img") == 1


# ------------------------------------------------------------------ el avance sale del modelo
@pytest.mark.parametrize("model", c.MODELOS)
def test_el_indicador_avanza_siguiendo_el_modelo_elegido(model):
    v = view(model=model)
    svg = cs.bottle_svg(v)
    bar = _bar_values(svg)
    assert len(bar) == cs.FRAMES
    expected = [min(max(r, 0.0), 100.0) / 100.0 for r in v.animada(model, cs.FRAMES - 1)]
    np.testing.assert_allclose(bar, expected, atol=1e-5)
    # y el modelo viene de cianuracion: el último cuadro es la recuperación del modelo en tmax
    last = c.recuperacion_modelo(v.modelos, model, v.tmax)
    assert bar[-1] == pytest.approx(min(last, 100.0) / 100.0, abs=1e-5)
    # la opacidad de la pulpa sigue la misma recuperación
    pulp = [
        float(re.search(r"fill-opacity:([\d.]+)", x).group(1))
        for p, x in _keyframes(svg, "lb-pulp")
        if p < 100.0
    ]
    np.testing.assert_allclose(pulp, [0.25 + 0.60 * b for b in bar], atol=1e-4)


def test_cada_modelo_mueve_el_indicador_distinto_y_los_instantes_son_parejos():
    bars = {m: _bar_values(cs.bottle_svg(view(model=m))) for m in c.MODELOS}
    assert len({tuple(round(x, 3) for x in b) for b in bars.values()}) == len(c.MODELOS)
    times = [p for p, _ in _keyframes(cs.bottle_svg(view()), "lb-bar") if p < 100.0]
    run = 100.0 * cs.RUN_S / (cs.RUN_S + cs.HOLD_S)
    assert times[0] == 0.0 and times[-1] == pytest.approx(run, abs=1e-3)
    assert np.allclose(np.diff(times), run / (cs.FRAMES - 1), atol=1e-3)


def test_el_potencial_arranca_en_cero_y_los_lineales_ya_traen_oro_disuelto_en_t_0():
    pot = _bar_values(cs.bottle_svg(view(model="potencial")))
    mix = _bar_values(cs.bottle_svg(view(model="mixto")))
    assert pot[0] == 0.0 and mix[0] == pytest.approx(0.771, abs=0.001)  # el intercepto, en el reloj
    assert all(b >= a for a, b in itertools.pairwise(pot))


def test_los_relojes_dicen_el_tiempo_y_la_recuperacion_de_cada_cuadro():
    v = view(model="potencial")
    texts = _strip(cs.bottle_svg(v), 0)
    hours, rec = texts[: cs.FRAMES], texts[cs.FRAMES :]
    assert hours[0] == "0" and hours[-1] == "48" and len(hours) == cs.FRAMES
    assert hours[cs.FRAMES // 2] == "24"
    expected = [i18n_num(r) for r in v.animada("potencial", cs.FRAMES - 1)]
    assert rec == expected


def i18n_num(x: float) -> str:
    from dibujo import es

    return es(x, 1)


def test_quieta_el_reloj_y_la_barra_quedan_en_el_ultimo_valor():
    v = view(model="mixto")
    still = cs.bottle_svg(v, paused=True)
    final = v.animada("mixto", cs.FRAMES - 1)[-1]
    assert f"scaleX({final / 100:.5f})" in still
    assert f"translateY({-(cs.FRAMES - 1) * cs.ROW_PX}px)" in still


def test_las_marcas_medidas_estan_donde_dice_la_recuperacion_medida():
    v = view()
    svg = cs.bottle_svg(v)
    xs = sorted(float(x) for x in re.findall(r'<line x1="([\d.]+)" y1="[\d.]+" x2="\1"', svg))
    expected = sorted(cs.GX + cs.GW * r / 100.0 for r in v.balance.recuperacion_pct)
    np.testing.assert_allclose(xs, expected, atol=0.06)
    assert len(xs) == 7


def test_la_leyenda_declara_la_compresion_del_tiempo():
    svg = cs.bottle_svg(view())
    assert "Tiempo comprimido: 48 h en 12 s" in svg and "las 48 h del" in svg
    assert "ilustrativos" in svg and "Esquema, no a escala" in svg


def test_los_esquemas_son_xml_valido_y_en_ingles_no_llevan_espanol():
    for lang in ("es", "en"):
        with i18n.use(lang):
            for paused in (False, True):
                svg = cs.bottle_svg(view(model="primer_orden"), paused)
                ET.fromstring(svg)
                texts = re.findall(r">([^<]+)</text>", svg)
                texts += re.findall(r'aria-label="([^"]+)"', svg)
                if lang == "en":
                    assert not [x for x in texts if SPANISH.search(x)], texts
                    assert any("Cyanidation bottle" in x for x in texts)
                    assert any("one turn every 1.94 s" in x for x in texts)


def test_los_numeros_del_esquema_cambian_de_formato_pero_no_de_valor():
    with i18n.use("es"):
        es_svg = cs.bottle_svg(view())
    with i18n.use("en"):
        en_svg = cs.bottle_svg(view())
    assert "31,0 rpm" in es_svg and "31.0 rpm" in en_svg
    assert _bar_values(es_svg) == _bar_values(en_svg)


# ------------------------------------------------------------------ los gráficos
def test_el_grafico_de_recuperacion_lleva_lo_medido_y_las_curvas_de_cada_modelo():
    v = view(model="reaccion")
    fig = cg.recovery_figure(v)
    names = [tr.name for tr in fig.data]
    assert names[:5] == [cc.model_name(m) for m in c.MODELOS]
    assert names[:5] == [cc.LABEL_OF[m] for m in c.MODELOS]  # en español, el rótulo es el valor
    for tr, m in zip(fig.data[:5], c.MODELOS, strict=True):
        got = np.array([np.nan if y is None else y for y in tr.y], dtype=float)
        want = np.array([np.nan if y is None else y for y in v.curva(m)], dtype=float)
        np.testing.assert_allclose(got, want)
        assert tr.line.width == (4.5 if m == "reaccion" else 2)
    used, excluded = fig.data[5], fig.data[6]
    assert list(used.x) == [1.0, 3.0, 7.0, 11.0, 24.0, 48.0] and list(excluded.x) == [2.0]
    np.testing.assert_allclose(excluded.y, [v.balance.recuperacion_pct[1]])


def test_las_rectas_de_los_terminos_no_pasan_por_el_origen_y_se_extienden_hasta_t_0():
    v = view()
    fig = cg.terms_figure(v)
    dotted = [
        tr for tr in fig.data if tr.mode == "lines" and tr.line.dash == "dot" and tr.x[0] == 0.0
    ]
    assert len(dotted) == 6  # dos tramos por tres términos
    intercepts = sorted(round(tr.y[0], 3) for tr in dotted)
    assert intercepts == [0.335, 0.385, 0.389, 0.501, 0.503, 0.543]
    assert all(tr.y[0] > 0.3 for tr in dotted)
    stars = [tr for tr in fig.data if tr.marker.symbol == "star"]
    assert len(stars) == 3 and all(list(s.y) == [0.0] for s in stars)
    texts = " ".join(a.text for a in fig.layout.annotations)
    assert "intercepto 0,335" in texts and "intercepto 0,543" in texts


def test_los_graficos_en_ingles_no_llevan_espanol():
    v = view()
    with i18n.use("en"):
        figs = [cg.recovery_figure(v), cg.terms_figure(v)]
        blob = " ".join(str(f.to_plotly_json()) for f in figs)
    texts = re.findall(r"'(?:text|title|name)': '([^']+)'", blob)
    texts += re.findall(r"'title': \{'text': '([^']+)'", blob)
    assert not [x for x in texts if SPANISH.search(x)], [x for x in texts if SPANISH.search(x)]
    assert "intercept 0.335" in blob and "Used point" in blob


# ------------------------------------------------------------------ la tabla del visitante
def test_leer_tabla_acepta_la_tabla_4_y_devuelve_floats():
    rows = [[a, b, d] for a, b, d in zip(T, SOL, RES, strict=True)]
    t, sol, res = cc.leer_tabla(rows)
    assert (t, sol, res) == (T, SOL, RES) and all(isinstance(x, float) for x in t)


@pytest.mark.parametrize(
    ("rows", "code"),
    [
        ([], "filas"),
        ([[1.0, 1.0, 1.0]] * (cc.MAX_FILAS + 1), "filas"),
        ([[None, 2.0, 3.0]], "numero"),
        ([[float("nan"), 2.0, 3.0]], "numero"),
        ([[1.0, float("inf"), 3.0]], "numero"),
        ([[1.0, 2.0, -3.0]], "numero"),
        ([[0.0, 2.0, 3.0]], "numero"),
        ([["<script>alert(1)</script>", 2.0, 3.0]], "numero"),
        ([[1.0, "2", 3.0]], "numero"),
        ([[True, 2.0, 3.0]], "numero"),
        ([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]], "orden"),
        ([[2.0, 2.0, 3.0], [1.0, 2.0, 3.0]], "orden"),
        ([[1.0, 2.0, 3.0], [cc.T_MAX_H + 1, 2.0, 3.0]], "rango"),
        ([[1.0, cc.PPB_MAX * 2, 3.0]], "rango"),
        ([[1.0, 150_000.0, 3.0]], "rango"),
        ([[1001.0, 100.0, 50.0]], "rango"),
        ([[1.0, 2.0, cc.PPB_MAX * 2]], "rango"),
    ],
)
def test_leer_tabla_rechaza_lo_manipulado_con_su_codigo(rows, code):
    with pytest.raises(c.SerieInvalida) as err:
        cc.leer_tabla(rows)
    assert err.value.code == code
    assert f"cn.err.{code}" in i18n.TEXTS["es"] and f"cn.err.{code}" in i18n.TEXTS["en"]


def test_los_mensajes_de_error_se_arman_en_los_dos_idiomas():
    for lang in ("es", "en"):
        with i18n.use(lang):
            for code, args in (
                ("filas", {"lo": 1, "hi": 30}),
                ("numero", {}),
                ("orden", {}),
                ("rango", {"t_max": 1000, "ppb_max": 100000}),
                ("residuo_mayor", {"cabeza": 1070}),
            ):
                text = cian_tab._error_text(c.SerieInvalida(code, **args))
                assert text and "{" not in text


def test_el_indicador_conserva_el_valor_donde_el_modelo_no_se_ajusta():
    v = view(model="reaccion", split=2.0)  # el primer tramo queda con 1 punto: sin ajustar
    bar = v.animada("reaccion", 96)
    assert all(0.0 <= x <= 100.0 for x in bar) and bar[0] == 0.0
    assert bar[1] == 0.0  # hasta que haya recta, el indicador no se mueve
    few = cc.run_cian(cc.CianParams(), [1.0, 2.0], [400.0, 450.0], [300.0, 200.0])
    assert few.modelos is None and few.animada("potencial", 10) == [0.0] * 11


# ------------------------------------------------------------------ una sola definición
def test_los_controles_de_la_cianuracion_salen_de_la_definicion_unica():
    group = [d for d in controles.DATOS if d.group == controles.CIA]
    assert [d.key for d in group] == ["c_model", "c_rpm", "c_head", "c_factor", "c_split"]
    table = controles.data_table(controles.CIA)
    assert len(table) == len(group) and set(table["Dato"]) == {d.label for d in group}
    rpm = controles.BY_KEY["c_rpm"]
    assert (rpm.lo, rpm.hi, rpm.default) == (30, 32, 31)  # procedimiento estándar: 30 a 32 rpm
    model = controles.BY_KEY["c_model"]
    assert model.options == tuple(cc.MODEL_LABELS) and set(cc.MODEL_LABELS.values()) == set(
        c.MODELOS
    )
    assert cc.MODEL_LABELS[model.default] == "potencial"
    for d in group:
        assert d.widget == "select" or d.lo <= d.default <= d.hi


def test_la_tabla_precargada_es_la_tabla_4():
    df = cian_tab.example_table()
    assert df["t"].tolist() == T and df["sol"].tolist() == SOL and df["res"].tolist() == RES


def test_los_valores_por_defecto_son_los_declarados():
    p = cc.CianParams()
    assert (p.head, p.factor, p.split, p.rpm, p.model) == (1070.0, 1.935, 7.0, 31.0, "potencial")
    assert (c.B_N1, c.B_N2) == (0.7033, 0.75)
    assert 30.0 <= p.rpm <= 32.0


def test_el_marco_del_esquema_codifica_las_imagenes_sin_html_del_visitante():
    html = as_images(cs.bottle_svg(view()), cs.bottle_svg(view(), True), "Botella")
    data = re.findall(r'src="data:image/svg\+xml;base64,([^"]+)"', html)
    assert len(data) == 2
    for blob in data:
        assert "<script" not in base64.b64decode(blob).decode("utf-8").lower()


def test_el_ciclo_dura_14_s_12_de_ensayo_y_2_de_pausa():
    css = cs.bottle_svg(view()).split("</style>")[0]
    assert (cs.RUN_S, cs.HOLD_S) == (12.0, 2.0)
    assert "animation:lb-bar 14s linear infinite" in css
    assert "animation:lb-count 14s steps(96,end) infinite" in css
    assert "animation:lb-pulp 14s linear infinite" in css


def test_el_indicador_no_baja_de_cero_aunque_el_modelo_si():
    v = cc.run_cian(
        cc.CianParams(), [1.0, 2.0, 3.0, 4.0], [400, 420, 450, 500], [1060, 1000, 800, 100]
    )
    assert c.recuperacion_modelo(v.modelos, "potencial", v.tmax / 96) < 0
    bar = v.animada("potencial", 96)
    assert min(bar) == 0.0 and max(bar) <= 100.0


def test_los_puntos_de_los_terminos_estan_en_su_tramo_con_la_b_de_su_tramo():
    fig = cg.terms_figure(view())
    third = [tr for tr in fig.data if tr.xaxis == "x3" and tr.mode == "markers"]
    by_name = {tr.name: tr for tr in third}
    first = by_name["Punto usado (primer tramo)"]
    second = by_name["Punto usado (segundo tramo)"]
    out = by_name["Punto excluido (primer tramo)"]
    assert list(first.x) == [1.0, 3.0, 7.0] and list(second.x) == [7.0, 11.0, 24.0, 48.0]
    np.testing.assert_allclose(first.y, [0.410, 0.445, 0.538], atol=0.002)  # N1, B = 0,7033
    np.testing.assert_allclose(second.y, [0.562, 0.578, 0.633, 0.698], atol=0.002)  # N2, B = 0,75
    assert list(out.x) == [2.0] and out.y[0] == pytest.approx(0.491, abs=0.002)
