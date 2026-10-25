"""La pestaña «Ensayo de sedimentación» dentro de la app: humo en los dos idiomas, tabla editable,
valores manipulados y un fuzz de 30 combinaciones por idioma (30 % extremas)."""

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

import controles  # noqa: E402
import i18n  # noqa: E402
import sed_calculo as sc  # noqa: E402
import sed_tab  # noqa: E402

TABLE = sed_tab.TABLE_KEY
SEED, N_FUZZ, EXTREME_SHARE = 20261019, 30, 0.30
GROUP = [d for d in controles.DATOS if d.group == controles.SED]
NUMBERS = [d for d in GROUP if d.widget == "number"]
TABLA = {"es": "Tabla editable", "en": "Editable table"}


def run(lang: str = "es") -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    at.query_params["lang"] = lang
    return at.run()


def widget(at: AppTest, key: str):
    return next(w for w in [*at.sidebar.number_input, *at.sidebar.selectbox]
                if w.key == "dato_" + key)  # fmt: skip


def con_tabla(lang: str = "es") -> AppTest:
    at = run(lang)
    widget(at, "s_fuente").set_value(TABLA[lang])
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


def warned(at: AppTest, needle: str) -> bool:
    return any(needle in w.value for w in at.warning)


# ------------------------------------------------------------------ humo
@pytest.mark.parametrize(
    ("lang", "tab", "dim", "area"),
    [
        ("es", "Ensayo de sedimentación", "**43,6 m**", "**0,396 m² por t/d**"),
        ("en", "Settling test", "**43.6 m**", "**0.396 m² per t/d**"),
    ],
)
def test_humo_de_la_pestana_en_cada_idioma(lang, tab, dim, area):
    at = run(lang)
    assert not at.exception and not at.error
    assert [t.label for t in at.tabs][6] == tab
    assert (
        len(at.metric) == 16
    )  # la pestaña no agrega métricas a las de siempre (4 son de Copelación)
    assert any(dim in m.value for m in at.markdown) and any(area in m.value for m in at.markdown)
    assert max(len(d.value) for d in at.dataframe) == 31  # la tabla de Vale
    assert not [w for w in at.warning if "tangente" in w.value.lower() or "tangent" in w.value]


def test_el_escalamiento_dice_0_898_0_573_y_0_64_con_la_division_al_reves():
    es_ = md(run(), "El factor es")
    assert "0,573 / 0,898 = **0,64**" in es_ and "1,57" in es_ and "0,573 m² por t/d" in es_
    en = md(run("en"), "The factor is")
    assert "0.573 / 0.898 = **0.64**" in en and "1.57" in en


def test_el_ejemplo_de_coe_clevenger_se_muestra_en_pies_y_en_si():
    es_ = md(run(), "pies² por tonelada corta por día")
    assert "**4,31 pies² por tonelada corta por día**" in es_ and "431 pies²" in es_
    assert "**23,4 pies**" in es_ and "7,1 m" in es_
    en = md(run("en"), "ft² per short ton per day")
    assert "**4.31 ft² per short ton per day**" in en and "**23.4 ft**" in en


def test_la_validacion_incluye_la_seccion_de_sedimentacion_con_sus_hallazgos():
    at = run()
    resumen = md(at, "Cuadran: Coe y Clevenger")
    assert "Coe y Clevenger, 5 de 8; Vale Tabla 1, 60 de 62; Tabla 2, 2 de 2" in resumen
    assert "Tabla 3 y factor, 10 de 10; Kynch sintético, 1 de 1" in resumen
    assert "0,987" in md(at, "Hallazgos, sin maquillar")


def test_los_controles_de_la_barra_lateral_son_los_de_la_definicion():
    at = run()
    for d in GROUP:
        w = widget(at, d.key)
        if d.widget == "number":
            assert (w.min, w.max, w.value) == (d.lo, d.hi, d.default)
        else:
            assert w.options[0] == d.options[0] and w.value == d.default


def test_cada_opcion_de_las_listas_carga_sin_errores():
    at = run()
    for key in ("s_fuente", "s_comp", "s_modo", "s_factor"):
        for option in widget(at, key).options:
            widget(at, key).set_value(option)
            at.run()
            assert not at.exception and not at.error, (key, option)


def test_el_factor_de_vale_cambia_el_diametro_y_se_rotula_no_universal():
    at = run()
    widget(at, "s_factor").set_value(sc.FACTORES[1]).run()
    assert any("**34,9 m**" in m.value for m in at.markdown) or any(
        "**35" in m.value for m in at.markdown
    )
    assert warned(at, "no es universal")


def test_el_selector_de_idioma_conserva_los_datos_de_la_sedimentacion():
    at = run()
    widget(at, "s_tph").set_value(300.0).run()
    widget(at, "s_factor").set_value(sc.FACTORES[1]).run()
    at.sidebar.radio[0].set_value("en").run()
    assert not at.exception and widget(at, "s_tph").value == 300.0
    assert widget(at, "s_factor").value == "Vale iron-ore slimes (0.64)"
    assert at.tabs[6].label == "Settling test"


def test_apagar_el_movimiento_no_rompe_la_pestana():
    at = run()
    at.toggle[0].set_value(False).run()
    assert not at.exception


def test_el_titulo_de_la_app_cubre_los_ensayos_metalurgicos_en_los_dos_idiomas():
    assert run().title[0].value == "Laboratorio de ensayos metalúrgicos y de ensayo al fuego"
    assert run("en").title[0].value == "Metallurgical test and fire-assay laboratory"
    assert "etalúrgicos" in run().caption[0].value
    assert "metallurgical tests" in run("en").caption[0].value


# ------------------------------------------------------------------ la tabla editable
def test_con_la_tabla_precargada_el_resultado_es_el_del_modelo_de_luz():
    at = con_tabla()
    assert not at.exception and not at.warning[-1].value.startswith("La interfase")
    # la tabla está redondeada al 0,1 mm: el área unitaria sale 0,405 (la del modelo, 0,396)
    assert any("**0,405 m² por t/d**" in m.value for m in at.markdown)


def test_editar_la_tabla_cambia_el_dimensionamiento():
    antes = md(con_tabla(), "Para 157 t/h")
    at = edit(con_tabla(), {7: {"h": 0.15}})  # la cota de los 420 s sube de 0,1223 a 0,15
    assert not at.exception
    assert md(at, "Para 157 t/h") != antes


@pytest.mark.parametrize("col", ["t", "h"])
@pytest.mark.parametrize(
    "bad", [None, float("nan"), float("inf"), -5.0, 0.0, 1e12, "texto", "<script>x</script>"]
)
def test_una_celda_manipulada_avisa_sin_caerse_ni_llegar_al_html(col, bad):
    at = edit(con_tabla(), {3: {col: bad}})
    assert not at.exception
    blob = json.dumps([m.value for m in at.markdown] + [w.value for w in at.warning])
    assert "<script" not in blob.lower()


def test_alturas_que_suben_o_tiempos_desordenados_avisan():
    assert warned(edit(con_tabla(), {3: {"h": 0.5}}), "no puede subir")
    assert warned(edit(con_tabla(), {3: {"t": 30.0}}), "orden creciente")
    assert warned(edit(con_tabla(), {3: {"t": 120.0}}), "orden creciente")  # repetido
    assert warned(edit(con_tabla(), {0: {"t": 10.0}}), "tiempo 0")


def test_una_tabla_vacia_corta_o_muy_larga_avisa():
    assert warned(edit(con_tabla(), deleted=list(range(16))), "entre 4 y 60 filas")
    assert warned(edit(con_tabla(), deleted=list(range(14))), "entre 4 y 60 filas")
    rows = [{"t": 100000.0 + i, "h": 0.01} for i in range(60)]
    assert warned(edit(con_tabla(), added=rows), "entre 4 y 60 filas")


def test_agregar_filas_a_la_curva_sigue_funcionando():
    at = edit(con_tabla(), added=[{"t": 100000.0, "h": 0.0349}])
    assert not at.exception and not warned(at, "no puede subir")


def test_volver_a_la_curva_de_luz_restaura_la_tabla():
    at = edit(con_tabla(), {3: {"h": 0.5}})
    next(b for b in at.button if "curva de Luz" in b.label).click().run()
    assert not at.exception and not warned(at, "no puede subir")


def test_los_datos_imposibles_se_muestran_como_aviso_en_los_dos_idiomas():
    at = run()
    widget(at, "s_cma").set_value(60.0)
    widget(at, "s_cmu").set_value(5.0)
    at.run()
    assert not at.exception and warned(at, "menos que los del underflow")
    en = run("en")
    widget(en, "s_cma").set_value(60.0)
    widget(en, "s_cmu").set_value(5.0)
    en.run()
    assert not en.exception and warned(en, "below the underflow solids")


FUERA_DE_RANGO = [(d.key, 1e12) for d in NUMBERS] + [
    ("s_tc", float("nan")), ("s_tc", float("inf")), ("s_cma", -5), ("s_b", float("nan")),
]  # fmt: skip


@pytest.mark.parametrize(("key", "value"), FUERA_DE_RANGO)
def test_el_servidor_devuelve_al_valor_por_defecto_un_campo_fuera_de_rango(key, value):
    at = run()
    widget(at, key).set_value(value).run()
    assert not at.exception
    assert widget(at, key).value == controles.BY_KEY[key].default


# ------------------------------------------------------------------ fuzz
def _fuzz_cases(rng: random.Random):
    """30 combinaciones, ~30 % extremas: límites, fuera de rango, celdas rotas, 0 o 61 filas."""
    cases = []
    for i in range(N_FUZZ):
        extreme = i < round(N_FUZZ * EXTREME_SHARE)
        side = {}
        for d in NUMBERS:
            if extreme and rng.random() < 0.6:
                side[d.key] = rng.choice([d.lo, d.hi, d.hi * 10, -1.0, float("nan")])
            else:
                side[d.key] = round(rng.uniform(d.lo, d.hi), 3)
        n = rng.choice([0, 1, 3, 61]) if extreme else rng.randint(5, 20)
        added = [{"t": 100000.0 + k, "h": 0.0349} for k in range(max(n - 16, 0))]
        deleted = list(range(16 - n)) if n < 16 else []
        junk = [None, float("nan"), float("inf"), 0.0, -3.0, 1e12, "x", "<b>"]
        edited = {}
        if extreme:
            edited = {
                j: {rng.choice(("t", "h")): rng.choice(junk)} for j in rng.sample(range(16), 3)
            }
        selects = {k: rng.randrange(2) for k in ("s_fuente", "s_comp", "s_modo", "s_factor")}
        cases.append((side, selects, edited, added, deleted, rng.random() < 0.5))
    rng.shuffle(cases)
    return cases


@pytest.mark.parametrize("lang", ["es", "en"])
def test_fuzz_de_30_combinaciones_no_tira_excepciones(lang):
    at = run(lang)
    for side, selects, edited, added, deleted, move in _fuzz_cases(random.Random(SEED)):
        for key, value in side.items():
            widget(at, key).set_value(value)
        for key, index in selects.items():
            w = widget(at, key)
            w.set_value(w.options[index])
        at.toggle[0].set_value(move)
        at.session_state[TABLE] = {"edited_rows": edited, "added_rows": added,
                                   "deleted_rows": deleted}  # fmt: skip
        at.run()
        assert not at.exception, (side, selects, edited, added, deleted)
        assert not at.error
        blob = json.dumps([m.value for m in at.markdown] + [w.value for w in at.warning])
        assert not re.search(r"Traceback|nan m|inf m|NaN", blob)


def test_las_claves_de_error_de_la_interfaz_existen_en_los_dos_idiomas():
    for code in ("filas", "numero", "origen", "orden", "sube", "rango", "luz", "conc",
                 "compresion", "tangente", "roberts", "flujo", "coe"):  # fmt: skip
        assert f"sd.err.{code}" in i18n.TEXTS["es"] and f"sd.err.{code}" in i18n.TEXTS["en"]
