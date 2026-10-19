"""App del laboratorio de ensayos al fuego: humo con AppTest, controles y tabla de datos desde UNA
definición, y valores manipulados que no deben tumbar el servidor."""

import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app" / "streamlit_app.py")
sys.path.insert(0, str(ROOT / "app"))

import controles  # noqa: E402


def _widgets(at: AppTest) -> list:
    return [*at.sidebar.number_input, *at.sidebar.selectbox, *at.sidebar.checkbox]


def _run() -> AppTest:
    return AppTest.from_file(APP, default_timeout=180).run()


def test_las_seis_pestanas_cargan_sin_excepciones():
    at = _run()
    assert not at.exception and not at.error
    assert [t.label for t in at.tabs] == [
        "Guía", "Protocolo", "Oro grueso", "Fusión", "Ensayo de cianuración", "Validación"
    ]  # fmt: skip
    values = {m.label: m.value for m in at.metric}
    assert values["Error total del protocolo"] == "56,0 %"  # PREP-31, alícuota de 30 g, DSA
    assert values["Granos esperados en la alícuota"] == "3,38"
    assert values["Mediana de los 1 000 ensayos"] == "3,41 g/t"


def test_la_pestana_de_oro_recomienda_screen_fire_assay_con_pocos_granos():
    at = _run()
    assert any("screen fire assay" in w.value for w in at.warning)
    assert any("errata" not in w.value and "ℓ = 0,000035" in w.value for w in at.warning)


def test_los_controles_salen_de_la_misma_definicion_que_la_tabla():
    at = _run()
    widgets = {w.key: w for w in _widgets(at)}
    assert set(widgets) == {controles.PREFIX + d.key for d in controles.DATOS}
    for d in controles.DATOS:  # el widget de la barra lateral es lo que dice la definición
        w = widgets[controles.PREFIX + d.key]
        if d.widget == "number":
            assert (w.min, w.max, w.value) == (d.lo, d.hi, d.default), d.key
        elif d.widget == "select":
            assert (list(w.options), w.value) == (list(d.options), d.default), d.key
        else:
            assert w.value == d.default, d.key
    table = controles.data_table()
    assert list(table["Dato"]) == [d.label for d in controles.DATOS]
    text = " ".join(m.value for m in at.markdown)  # y la guía muestra la misma tabla
    for d in controles.DATOS:
        assert d.label in text


def test_la_tabla_recoge_un_dato_nuevo_sola(monkeypatch):
    extra = controles.Dato(controles.PROT, "nuevo", "Dato nuevo", "", 0, 1, 0.5, 0.1, "x", "y")
    monkeypatch.setattr(controles, "DATOS", (*controles.DATOS, extra))
    assert "Dato nuevo" in list(controles.data_table()["Dato"])


def test_el_mineral_por_defecto_es_el_calibrado_de_minnitt_2017_con_su_fuente():
    from calculo import DSA_ALPHA, DSA_K, MINERALS, SOURCE_NOTE

    assert (DSA_K, DSA_ALPHA) == (167.4, 1.123)
    assert controles.BY_KEY["form"].default == MINERALS[0]
    assert "Minnitt (2017)" in SOURCE_NOTE and "calibrar" in SOURCE_NOTE
    at = _run()
    assert any("Minnitt (2017)" in c.value for c in at.caption)


@pytest.mark.parametrize("preset", ["PREP-31", "PREP-31B", "Minnitt 2017, Tabla VIII"])
@pytest.mark.parametrize("aliquot", ["30", "50"])
def test_los_tres_protocolos_con_las_dos_alicuotas_cargan(preset, aliquot):
    at = _run()
    at.sidebar.selectbox[0].set_value(preset)
    at.sidebar.selectbox[1].set_value(aliquot).run()
    assert not at.exception and not at.error


@pytest.mark.parametrize("form_index", [0, 1, 2, 3])
def test_las_cuatro_formas_de_mineral_cargan(form_index):
    from calculo import MINERALS

    at = _run()
    form = next(s for s in at.sidebar.selectbox if s.key == controles.PREFIX + "form")
    form.set_value(MINERALS[form_index]).run()
    assert not at.exception and not at.error


@pytest.mark.parametrize("extreme", ["min", "max"])
@pytest.mark.parametrize("lot_correction", [False, True])
def test_controles_en_los_extremos_no_tumban_la_app(extreme, lot_correction):
    at = _run()
    for w in at.sidebar.number_input:
        w.set_value(w.min if extreme == "min" else w.max)
    for s in at.sidebar.selectbox:
        s.set_value(s.options[0] if extreme == "min" else s.options[-1])
    at.sidebar.checkbox[0].set_value(lot_correction).run()
    assert not at.exception


@pytest.mark.parametrize("value", [10_000_000, -5, float("inf"), float("nan")])
def test_el_servidor_rechaza_valores_fuera_de_rango(value):
    # Un cliente puede mandar valores sin pasar por el navegador: Streamlit (versión fijada en
    # requirements.txt) los devuelve al valor por defecto en el servidor.
    at = _run()
    for w in at.sidebar.number_input:
        w.set_value(value)
    at.run()
    assert not at.exception
    assert [w.value for w in at.sidebar.number_input] == [
        d.default for d in controles.DATOS if d.widget == "number"
    ]


def test_un_protocolo_imposible_se_muestra_sin_traza():
    at = _run()
    lot = next(w for w in at.sidebar.number_input if w.key == controles.PREFIX + "lot")
    lot.set_value(500.0)  # 500 g de lote y PREP-31B pide dividir 1 000 g
    at.sidebar.selectbox[0].set_value("PREP-31B").run()
    assert not at.exception
    assert any("menor que" in e.value for e in at.error)


def test_un_fallo_del_modelo_se_muestra_sin_traza(monkeypatch):
    import calculo

    from muestreo.gy import GyError

    def fails(*args, **kwargs):
        raise GyError("el tamaño debe ser positivo")

    monkeypatch.setattr(calculo, "run_protocol", fails)
    monkeypatch.setattr(calculo, "run_gold", fails)
    at = _run()
    assert not at.exception
    assert sum("debe ser positivo" in e.value for e in at.error) == 2


def test_la_app_usa_conminucion_y_no_necesita_pycalphad():
    code = "\n".join(
        [
            f"import sys; sys.path[:0] = [{str(ROOT)!r}, {str(ROOT / 'app')!r}]",
            "import calculo, nomograma, oro_graficos, validacion_graficos, controles, guia",
            "import conminucion.sizes",
            "calculo.run_protocol(calculo.ProtocolParams(), calculo.MineralParams())",
            "assert 'pycalphad' not in sys.modules",
        ]
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr[-500:]
