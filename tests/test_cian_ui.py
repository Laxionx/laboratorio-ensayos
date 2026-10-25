"""La pestaña «Ensayo de cianuración» dentro de la app: humo en los dos idiomas, edición de la
tabla, valores manipulados y un fuzz de 30 combinaciones por idioma (30 % extremas)."""

import json
import random
import re
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app" / "streamlit_app.py")
sys.path.insert(0, str(ROOT / "app"))

import cian_tab  # noqa: E402
import controles  # noqa: E402
import i18n  # noqa: E402

TABLE = cian_tab.TABLE_KEY
SEED, N_FUZZ, EXTREME_SHARE = 20261018, 30, 0.30
GROUP = [d for d in controles.DATOS if d.group == controles.CIA]


def run(lang: str = "es") -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    at.query_params["lang"] = lang
    return at.run()


def edit(at: AppTest, edited=None, added=None, deleted=None) -> AppTest:
    at.session_state[TABLE] = {
        "edited_rows": edited or {},
        "added_rows": added or [],
        "deleted_rows": deleted or [],
    }
    return at.run()


def md(at: AppTest, needle: str) -> str:
    return next((m.value for m in at.markdown if needle in m.value), "")


def sidebar(at: AppTest, key: str):
    return next(w for w in [*at.sidebar.number_input, *at.sidebar.selectbox]
                if w.key == "dato_" + key)  # fmt: skip


def balance_table(at: AppTest):
    return max((d.value for d in at.dataframe if len(d.value.columns) == 7), key=len)


# ------------------------------------------------------------------ humo
@pytest.mark.parametrize(
    ("lang", "tab", "recovery", "model"),
    [
        ("es", "Ensayo de cianuración", "94,77", "Potencial (Ec. 3 de los autores)"),
        ("en", "Cyanide leach test", "94.77", "Power law (authors' Eq. 3)"),
    ],
)
def test_humo_de_la_pestana_en_cada_idioma(lang, tab, recovery, model):
    at = run(lang)
    assert not at.exception and not at.error
    assert [t.label for t in at.tabs][5] == tab
    assert len(at.metric) == 30  # 16 de siempre más 14 del control de calidad
    frame = balance_table(at)
    assert len(frame) == 7 and frame.iloc[:, 3].round(2).tolist()[-1] == 94.77
    assert any(recovery in m.value for m in at.markdown)
    assert sidebar(at, "c_model").value == model
    # un aviso por el punto de 2 h, el único que no cuadra con una recuperación creciente
    mine = [w.value for w in at.warning if re.search(r"(^|\s)2 h(\s|$)", w.value)]
    assert len(mine) == 1 and "94" not in mine[0]


def test_el_mensaje_central_lleva_las_cifras_de_los_interceptos():
    at = run()
    msg = md(at, "interceptos son")
    assert "0,335 (difusión), 0,389 (reacción) y 0,385 (mixto)" in msg
    assert "77 %" in msg and "79 % a las 1 h" in msg and "3 puntos" in msg
    en = md(run("en"), "intercepts are")
    assert "0.335 (diffusion), 0.389 (reaction) and 0.385 (mixed)" in en


def test_los_controles_de_la_barra_lateral_son_los_de_la_definicion():
    at = run()
    for d in GROUP:
        w = sidebar(at, d.key)
        if d.widget == "number":
            assert (w.min, w.max, w.value) == (d.lo, d.hi, d.default)
        else:
            assert w.options[0] == i18n.TEXTS["es"]["opt." + d.options[0]]


def test_cada_modelo_del_indicador_carga_sin_errores():
    at = run()
    for option in sidebar(at, "c_model").options:
        sidebar(at, "c_model").set_value(option)
        at.run()
        assert not at.exception and not at.error


def test_el_selector_de_idioma_conserva_los_datos_de_la_cianuracion():
    at = run()
    sidebar(at, "c_head").set_value(1200.0).run()
    at.sidebar.radio[0].set_value("en").run()
    assert not at.exception and sidebar(at, "c_head").value == 1200.0
    assert at.tabs[5].label == "Cyanide leach test"


def test_apagar_el_movimiento_no_rompe_la_pestana():
    at = run()
    at.toggle[0].set_value(False).run()
    assert not at.exception


# ------------------------------------------------------------------ la tabla editable
def test_editar_la_tabla_cambia_la_calculadora():
    at = run()
    at = edit(at, {6: {"res": 100.0}})  # el residuo de 48 h, de 56 a 100 ppb
    assert not at.exception
    frame = balance_table(at)
    assert frame.iloc[:, 3].round(2).tolist()[-1] == pytest.approx(90.65, abs=0.01)


def test_agregar_y_quitar_filas():
    at = run()
    at = edit(at, added=[{"t": 72.0, "sol": 530.0, "res": 50.0}])
    assert not at.exception and len(balance_table(at)) == 8
    at = edit(at, deleted=[0, 1, 2, 3])
    assert not at.exception and len(balance_table(at)) == 3  # 3 filas: ya no hay tramos ajustables
    assert any("faltan puntos" in m.value or "too few" in m.value.lower()
               for m in [*at.info, *at.markdown])  # fmt: skip


@pytest.mark.parametrize("col", ["t", "sol", "res"])
@pytest.mark.parametrize(
    "bad", [None, float("nan"), float("inf"), -5.0, 0.0, 1e12, "texto", "<script>x</script>"]
)
def test_una_celda_manipulada_avisa_sin_caerse_ni_llegar_al_html(col, bad):
    at = edit(run(), {3: {col: bad}})
    assert not at.exception
    blob = json.dumps([m.value for m in at.markdown] + [w.value for w in at.warning])
    assert "<script" not in blob.lower()
    assert at.warning or balance_table(at) is not None


def test_filas_desordenadas_o_repetidas_avisan():
    at = edit(run(), {1: {"t": 1.0}})  # dos filas con 1 h
    assert any("orden creciente" in w.value for w in at.warning)
    at = edit(run(), {0: {"t": 50.0}})  # la primera pasa de la última
    assert any("orden creciente" in w.value for w in at.warning)


def test_una_tabla_vacia_o_muy_larga_avisa():
    at = edit(run(), deleted=list(range(7)))
    assert any("entre 1 y 30 filas" in w.value for w in at.warning)
    rows = [{"t": 100.0 + i, "sol": 500.0, "res": 100.0} for i in range(30)]
    at = edit(run(), added=rows)
    assert any("entre 1 y 30 filas" in w.value for w in at.warning)


def test_un_residuo_mayor_que_la_cabeza_avisa():
    at = edit(run(), {0: {"res": 1100.0}})
    assert not at.exception and any("ley de cabeza" in w.value for w in at.warning)


def test_la_cabeza_distinta_da_aviso_de_balance():
    at = run()
    sidebar(at, "c_factor").set_value(1.0).run()
    assert not at.exception
    assert any("cabeza por balance" in w.value for w in at.warning)


def test_volver_al_ejemplo_restaura_la_tabla():
    at = edit(run(), {0: {"res": 500.0}})
    next(b for b in at.button if "Tabla 4" in b.label).click().run()
    assert not at.exception and len(balance_table(at)) == 7
    assert balance_table(at).iloc[:, 3].round(2).tolist()[0] == 79.44


@pytest.mark.parametrize("key", [d.key for d in GROUP if d.widget == "number"])
@pytest.mark.parametrize("value", [1e12, -5, float("inf"), float("nan")])
def test_el_servidor_devuelve_al_valor_por_defecto_un_campo_fuera_de_rango(key, value):
    at = run()
    sidebar(at, key).set_value(value).run()
    assert not at.exception
    assert sidebar(at, key).value == controles.BY_KEY[key].default


# ------------------------------------------------------------------ fuzz
def _fuzz_cases(rng: random.Random):
    """30 combinaciones, ~30 % extremas: límites, fuera de rango, celdas rotas, 0 o 31 filas."""
    cases = []
    numbers = [d for d in GROUP if d.widget == "number"]
    for i in range(N_FUZZ):
        extreme = i < round(N_FUZZ * EXTREME_SHARE)
        side = {}
        for d in numbers:
            if extreme and rng.random() < 0.6:
                side[d.key] = rng.choice([d.lo, d.hi, d.hi * 10, -1.0, float("nan")])
            else:
                side[d.key] = round(rng.uniform(d.lo, d.hi), 1)
        n = rng.choice([0, 1, 2, 31]) if extreme else rng.randint(3, 12)
        added = [{"t": 60.0 + k, "sol": rng.uniform(1, 900), "res": rng.uniform(1, 900)}
                 for k in range(max(n - 7, 0))]  # fmt: skip
        deleted = list(range(7 - n)) if n < 7 else []
        junk = [None, float("nan"), float("inf"), 0.0, -3.0, 1e12, "x", "<b>"]
        edited = {}
        if extreme:
            edited = {j: {rng.choice(("t", "sol", "res")): rng.choice(junk)}
                      for j in rng.sample(range(7), 3)}  # fmt: skip
        else:
            for j in rng.sample(range(7), 2):
                edited[j] = {"res": rng.uniform(20, 300)}
        cases.append((side, edited, added, deleted, rng.random() < 0.5, rng.randrange(5)))
    rng.shuffle(cases)
    return cases


@pytest.mark.parametrize("lang", ["es", "en"])
def test_fuzz_de_30_combinaciones_no_tira_excepciones(lang):
    at = run(lang)
    models = list(sidebar(at, "c_model").options)
    for side, edited, added, deleted, move, model_index in _fuzz_cases(random.Random(SEED)):
        for key, value in side.items():
            sidebar(at, key).set_value(value)
        sidebar(at, "c_model").set_value(models[model_index])
        at.toggle[0].set_value(move)
        at.session_state[TABLE] = {"edited_rows": edited, "added_rows": added,
                                   "deleted_rows": deleted}  # fmt: skip
        at.run()
        assert not at.exception, (side, edited, added, deleted)
        assert not at.error
        blob = json.dumps([m.value for m in at.markdown] + [w.value for w in at.warning])
        assert not re.search(r"Traceback|nan %|inf %|NaN", blob)
