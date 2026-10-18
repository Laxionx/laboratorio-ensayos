"""Cada gráfico y animación de la app sale del cálculo: las rectas y la ruta del nomograma, los
cuadros del histograma, los granos del esquema y los puntos de la validación se vuelven a deducir
aquí de `muestreo` (y de las densidades de la literatura) por otro camino."""

import re
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import poisson

pytest.importorskip("streamlit")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

import calculo  # noqa: E402
import nomograma  # noqa: E402
import oro_graficos  # noqa: E402
import validacion_graficos  # noqa: E402
from dibujo import es  # noqa: E402

from muestreo import oro  # noqa: E402
from muestreo import validacion as val  # noqa: E402
from muestreo.granulometria import d95_from_um  # noqa: E402

P = calculo.ProtocolParams
M = calculo.MineralParams
LEYENDA = "esquema ilustrativo: las cantidades de granos sí son del cálculo"


def _trace(fig, prefix: str):
    return next(t for t in fig.data if str(t.name).startswith(prefix))


# ------------------------------------------------------------------ nomograma
@pytest.mark.parametrize("safety", [5.0, 10.0, 25.0])
def test_las_rectas_de_gy_son_masa_igual_a_k_dn_alfa_sobre_la_varianza(safety):
    view = calculo.run_protocol(P(safety_pct=safety), M())
    fig = nomograma.nomogram_figure(view)
    lines = [t for t in fig.data if str(t.name).startswith("error ")]
    assert {float(re.search(r"error (\d+) %", t.name).group(1)) for t in lines} == {
        1.0, 3.0, 10.0, 30.0, 100.0, safety
    }  # fmt: skip
    for t in lines:
        level = float(re.search(r"error (\d+) %", t.name).group(1)) / 100.0
        x, y = np.array(t.x), np.array(t.y)
        assert np.allclose(y, 167.4 * x**1.123 / level**2, rtol=1e-12)  # DSA: K = 167,4, α = 1,123
    assert _trace(fig, f"error {safety:.0f} % (seguridad)").line.width > 3  # la elegida, gruesa


def test_la_linea_de_seguridad_da_exactamente_el_error_elegido():
    view = calculo.run_protocol(P(safety_pct=10.0), M())
    mass = view.safety_mass(0.5)
    assert view.mineral.variance(0.5, mass) == pytest.approx(0.10**2, rel=1e-12)
    assert view.safety_variance == pytest.approx(0.01)


def test_cada_cuadro_agrega_un_punto_de_la_ruta_calculada():
    view = calculo.run_protocol(P(), M())
    fig = nomograma.nomogram_figure(view)
    points = view.result.stages
    assert len(fig.frames) == 1 + 2 * len(points) == len(view.path)
    for k, frame in enumerate(fig.frames):
        route = next(t for t in frame.data if t.name == "ruta del protocolo")
        assert list(route.x) == [d for _, d, _ in view.path[: k + 1]]
        assert list(route.y) == [m for _, _, m in view.path[: k + 1]]
    final = _trace(fig, "ruta")
    assert (final.x[-1], final.y[-1]) == (points[-1].d_n_cm, points[-1].mass_out_g)


def test_los_tramos_de_la_ruta_son_horizontales_al_reducir_y_verticales_al_dividir():
    view = calculo.run_protocol(P(), M())
    xs, ys = nomograma.path_prefix(view, len(view.path) - 1)
    for i in range(1, len(xs)):
        if i % 2 == 1:  # reducir el tamaño: la masa no cambia
            assert ys[i] == ys[i - 1] and xs[i] < xs[i - 1]
        else:  # dividir: el tamaño no cambia
            assert xs[i] == xs[i - 1] and ys[i] < ys[i - 1]


def test_el_tamano_de_las_etapas_es_el_d95_de_su_especificacion():
    view = calculo.run_protocol(P(m=1.4), M())
    first, second = view.result.stages
    assert first.d_n_cm == pytest.approx(d95_from_um(70.0, 2000.0, 1.4))
    assert second.d_n_cm == pytest.approx(d95_from_um(85.0, 75.0, 1.4))
    assert [d for _, d, _ in view.path][1:3] == [first.d_n_cm] * 2


def test_las_barras_de_etapa_son_la_raiz_de_la_varianza_y_el_acumulado_es_la_suma():
    view = calculo.run_protocol(P(), M())
    fig = nomograma.stage_figure(view)
    bars, cumulative = fig.data[0], fig.data[1]
    variances = []
    for stage, bar in zip(view.result.stages, bars.y, strict=True):
        variances.append(stage.variance)
        assert bar == pytest.approx(100 * stage.variance**0.5, rel=1e-12)
    assert list(cumulative.y) == pytest.approx(
        [100 * np.cumsum(variances)[i] ** 0.5 for i in range(2)]
    )
    assert fig.layout.shapes[0].y0 == pytest.approx(10.0)  # la línea de seguridad


def test_la_sensibilidad_a_m_usa_el_error_de_cada_pendiente():
    view = calculo.run_protocol(P(m=1.0), M())
    fig = nomograma.sensitivity_figure(view)
    line, marker = fig.data
    assert list(line.x) == list(calculo.SLOPES)
    for m, y in zip(line.x, line.y, strict=True):
        other = calculo.run_protocol(P(m=m), M())
        assert y == pytest.approx(100 * other.result.rsd, rel=1e-12)
    assert marker.y[0] == pytest.approx(100 * view.result.rsd)
    assert list(line.y) == sorted(line.y, reverse=True)  # más m, menos error


def test_las_curvas_granulometricas_pasan_por_su_especificacion_y_su_d95():
    view = calculo.run_protocol(P(m=1.2), M())
    fig = nomograma.granulometry_figure(view)
    d95 = [t for t in fig.data if str(t.name).startswith("d95")]
    for trace, stage in zip(d95, view.result.stages, strict=True):
        assert trace.x[0] == pytest.approx(stage.d_n_cm * 1e4) and trace.y[0] == 95.0
    assert (
        nomograma.granulometry_figure(
            calculo.run_protocol(P(preset="Minnitt 2017, Tabla VIII"), M())
        )
        is None
    )


def test_el_preset_de_minnitt_2017_dibuja_las_masas_y_tamanos_de_la_tabla():
    view = calculo.run_protocol(P(preset="Minnitt 2017, Tabla VIII", lot_correction=False), M())
    assert [round(d, 3) for _, d, _ in view.path[1:3]] == [20.0, 20.0]
    assert [m for _, _, m in view.path][-1] == 48.61
    assert view.result.rsd == pytest.approx(0.16565, abs=1e-4)


def test_el_mineral_calibrado_propio_y_el_clasico_cambian_el_nomograma():
    base = calculo.run_protocol(P(), M())
    own = calculo.run_protocol(P(), M(form=calculo.MINERALS[2], k=300.0, alpha=1.2))
    classic = calculo.run_protocol(P(), M(form=calculo.MINERALS[3]))
    assert own.mineral.ih_l(0.5) == pytest.approx(300.0 * 0.5**1.2)
    assert classic.result.rsd != base.result.rsd and not classic.mineral.calibrated
    line_own = _trace(nomograma.nomogram_figure(own), "error 10 %")
    assert line_own.y[0] == pytest.approx(300.0 * line_own.x[0] ** 1.2 / 0.01)


# ------------------------------------------------------------------ oro: histograma
def _gold(grain=150.0, aliquot=30.0, grade=3.84):
    return calculo.run_gold(calculo.GoldParams(grain), grade, aliquot)


def test_el_histograma_final_es_el_conteo_de_los_1000_ensayos():
    view = _gold()
    fig = oro_graficos.histogram_figure(view)
    bars = fig.data[0]
    edges = np.arange(-0.5, view.simulation.counts.max() + 1.5)
    expected, _ = np.histogram(view.simulation.counts, bins=edges)
    assert list(bars.y) == list(expected) and sum(bars.y) == 1000
    per_grain = view.grain_g / view.aliquot_g * 1e6
    assert list(bars.x) == pytest.approx([k * per_grain for k in range(len(expected))])


def test_cada_cuadro_acumula_los_primeros_n_ensayos_con_su_mediana():
    view = _gold()
    fig = oro_graficos.histogram_figure(view)
    assert [f.name for f in fig.frames][-1] == "1000"
    assert [int(f.name) for f in fig.frames] == oro_graficos.frame_sizes(1000)
    for frame in fig.frames:
        n = int(frame.name)
        assert sum(frame.data[0].y) == n
        median_line = next(t for t in frame.data if str(t.name).startswith("mediana"))
        assert median_line.x[0] == pytest.approx(np.median(view.simulation.grades_gpt[:n]))
        assert str(n) in frame.layout.annotations[0].text


def test_la_ley_real_esta_marcada_y_la_mediana_cae_bajo_ella():
    view = _gold()
    fig = oro_graficos.histogram_figure(view)
    real = _trace(fig, "ley real")
    median_line = _trace(fig, "mediana")
    assert list(real.x) == [3.84, 3.84]
    assert median_line.x[0] < real.x[0]  # lo que hay que ver: la mediana bajo la ley real
    assert view.simulation.grades_gpt.max() > 2 * 3.84  # y unos pocos ensayos muy altos


def test_los_puntos_de_poisson_son_n_por_la_probabilidad():
    view = _gold()
    fig = oro_graficos.histogram_figure(view)
    analytic = _trace(fig, "Poisson")
    ks = np.arange(len(analytic.x))
    assert list(analytic.y) == pytest.approx(list(1000 * poisson.pmf(ks, view.lam)))
    assert view.lam == pytest.approx(oro.expected_particles(3.84, 30.0, oro.grain_mass_g(150.0)))


def test_con_muchos_granos_el_histograma_agrupa_en_barras():
    view = _gold(grain=30.0, aliquot=50.0)
    assert view.lam > 100
    edges, unit = oro_graficos.bin_edges(view)
    assert not unit and len(edges) == oro_graficos.BINS + 1
    fig = oro_graficos.histogram_figure(view)
    assert sum(fig.data[0].y) == 1000 and not any(
        str(t.name).startswith("Poisson") for t in fig.data
    )


# ------------------------------------------------------------------ oro: esquema
def test_el_esquema_dibuja_los_granos_de_tres_ensayos_simulados():
    view = _gold()
    runs = oro_graficos.representative_runs(view)
    counts = view.simulation.counts
    assert runs[0][1] == int(np.percentile(counts, 10, method="lower"))
    assert runs[1][1] == int(np.median(counts))
    assert runs[2][1] == int(np.percentile(counts, 99, method="higher"))
    assert runs[0][1] <= runs[1][1] <= runs[2][1]
    svg_text = oro_graficos.aliquot_svg(view)
    assert svg_text.count('class="grain"') == sum(min(c, oro_graficos.MAX_DOTS) for _, c in runs)
    per_grain = view.grain_g / view.aliquot_g * 1e6
    for _, count in runs:
        assert f"ley que daría: {es(count * per_grain, 2)} g/t" in svg_text
    assert LEYENDA.split(";")[0] in svg_text and "ilustrativa" in svg_text
    assert "<script" not in svg_text.lower()


def test_con_un_solo_grano_el_rotulo_va_en_singular():
    view = _gold(grain=100.0, aliquot=30.0, grade=0.3)  # λ ≪ 1: el ensayo bajo trae 0 granos
    text = oro_graficos.aliquot_svg(view)
    assert "0 granos de oro" in text


# ------------------------------------------------------------------ validación
def test_el_grafico_de_varianzas_trae_los_puntos_de_las_tablas():
    checks = val.minnitt_2017_checks() + val.chieregati_checks()
    fig = validacion_graficos.variance_figure(checks)
    plotted = sum(len(t.x) for t in fig.data if t.mode == "markers")
    expected = [c for c in checks if c.unit == "varianza relativa" and c.published > 0]
    assert plotted == len(expected)
    bad = _trace(fig, "no cuadra")
    assert list(bad.x) == [0.00005] and bad.y[0] == pytest.approx(9.4e-5, rel=0.01)
    ok = _trace(fig, "cuadra")
    assert len(ok.x) == len(expected) - 1


def test_el_grafico_de_clifton_trae_publicado_ecuaciones_y_poisson_exacto():
    fig = validacion_graficos.clifton_figure()
    published = [t for t in fig.data if str(t.name).startswith("publicado")]
    assert list(published[0].y) == [-50.0, -34.0, -20.0, -9.0]
    assert list(published[1].y) == [100.0, 54.0, 25.0, 10.0]
    eq = [t for t in fig.data if str(t.name).startswith("ecuaciones")]
    for n, y in zip((7, 20, 75, 400), eq[0].y, strict=True):
        assert y == pytest.approx(100 * oro.clifton_limits(n)[0])
    exact = [t for t in fig.data if str(t.name).startswith("Poisson exacto")]
    assert exact[1].y[0] == pytest.approx(100 * oro.poisson_exact_limits(7)[1])


def test_el_grafico_de_minnitt_2007_muestra_publicado_impreso_e_implicito():
    findings, implied = val.minnitt_2007_findings(), val.minnitt_2007_implied()
    printed = next(c for c in findings if c.item == "error relativo").calculated
    implied_pct = next(c for c in implied if c.item == "error relativo").calculated
    fig = validacion_graficos.minnitt_2007_figure(printed, implied_pct)
    assert list(fig.data[0].y) == [29.58, printed, implied_pct]
    assert printed == pytest.approx(11.69, abs=0.005) and implied_pct == pytest.approx(
        29.58, abs=0.01
    )


def test_los_puntos_de_poisson_de_cada_cuadro_son_n_por_la_probabilidad():
    view = _gold()
    for frame in oro_graficos.histogram_figure(view).frames:
        n = int(frame.name)
        analytic = next(t for t in frame.data if str(t.name).startswith("Poisson"))
        ks = np.arange(len(analytic.x))
        assert list(analytic.y) == pytest.approx(list(n * poisson.pmf(ks, view.lam)))


def test_la_forma_del_grano_cambia_su_masa_y_los_granos_esperados():
    sphere = calculo.run_gold(calculo.GoldParams(150.0, "esfera"), 3.84, 30.0)
    cube = calculo.run_gold(calculo.GoldParams(150.0, "cubo"), 3.84, 30.0)
    assert cube.grain_g == pytest.approx(19.3 * (150e-4) ** 3)
    assert cube.grain_g / sphere.grain_g == pytest.approx(6 / np.pi)
    assert cube.lam == pytest.approx(sphere.lam * np.pi / 6)
