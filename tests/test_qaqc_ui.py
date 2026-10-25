"""La pestaña «Control de calidad» dentro de la app: humo en los dos idiomas, las cuatro secciones,
tablas pegadas con entradas malas, cifras idénticas en español e inglés y un fuzz de 30
combinaciones por idioma (30 % extremas)."""

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
import qaqc_calculo as qcalc  # noqa: E402
import qaqc_tab  # noqa: E402
from i18n import TEXTS  # noqa: E402

from muestreo import qaqc as qc  # noqa: E402

SEED, N_FUZZ, EXTREME_SHARE = 20261025, 30, 0.30
GROUP = [d for d in controles.DATOS if d.group == controles.QC]
NUMBERS = [d for d in GROUP if d.widget == "number"]
TABLA = {"es": "Tabla editable", "en": "Editable table"}
TAB_INDEX = 7


def run(lang: str = "es") -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    at.query_params["lang"] = lang
    return at.run()


def widget(at: AppTest, key: str):
    return next(
        w for w in [*at.sidebar.number_input, *at.sidebar.selectbox] if w.key == "dato_" + key
    )


def con_tablas(lang: str = "es") -> AppTest:
    """Las tres series (CRM, duplicados y blancos) en tablas editables."""
    at = run(lang)
    for key in ("q_crm_fuente", "q_dup_fuente", "q_blk_fuente"):
        widget(at, key).set_value(TABLA[lang])
    return at.run()


def edit(at: AppTest, key: str, edited=None, added=None, deleted=None) -> AppTest:
    at.session_state[key] = {
        "edited_rows": edited or {},
        "added_rows": added or [],
        "deleted_rows": deleted or [],
    }
    return at.run()


def texts(at: AppTest) -> list[str]:
    return [*(m.value for m in at.markdown), *(c.value for c in at.caption)]


def md(at: AppTest, needle: str) -> str:
    return next((m.value for m in at.markdown if needle in m.value), "")


def alerts(at: AppTest) -> list[str]:
    return [a.value for a in (*at.success, *at.info, *at.warning, *at.error)]


def said(at: AppTest, needle: str) -> bool:
    return any(needle in a for a in alerts(at))


# ------------------------------------------------------------------ humo
@pytest.mark.parametrize(
    ("lang", "tab", "crm", "cdn"),
    [
        ("es", "Control de calidad", "valor certificado **0,248 g/t**", "**2,388 ± 0,232 g/t**"),
        ("en", "Quality control", "certified value **0.248 g/t**", "**2.388 ± 0.232 g/t**"),
    ],
)
def test_humo_de_la_pestana_en_cada_idioma(lang, tab, crm, cdn):
    at = run(lang)
    assert not at.exception and not at.error
    assert [t.label for t in at.tabs][TAB_INDEX] == tab
    assert any(crm in m.value for m in at.markdown)
    assert any(cdn in m.value for m in at.markdown)
    assert len(at.metric) == 30  # 16 de siempre y 14 del control de calidad
    assert len(at.sidebar.expander) == 8


def test_los_veredictos_de_la_serie_de_ejemplo_son_los_del_calculo():
    at = run()
    assert said(at, "Ninguna regla de rechazo ni de re-ensayo se dispara. 1 de 30 resultados")
    assert said(at, "**Thompson-Howarth con P = 10 %: no pasa.** 64,4 % de los pares")
    assert said(at, "**Duplicados (duplicado de campo): pasa.** 86,5 %")
    assert said(at, "**Alerta.** 1 blanco(s) superan 3 × LD (3,3 %)")


def test_el_valor_certificado_de_cdn_gs_2x_sale_de_los_150_resultados():
    at = run()
    res = md(at, "Con los 150 resultados")
    assert "media 2,3868 g/t y SD 0,1293 g/t" in res and "descarta 7 resultados" in res
    assert "**2,388 ± 0,232 g/t**" in res and "coinciden al redondeo publicado" in res


def test_las_cifras_de_oreas_se_muestran_con_la_sd_sin_redondear():
    at = run()
    intro = md(at, "valor certificado **0,248 g/t**")
    assert "SD **0,00952 g/t**" in intro and "la SD publicada es 0,010" in intro
    assert "**0,229 a 0,267 g/t**" in intro and "**0,219 a 0,277 g/t**" in intro


# ------------------------------------------------------------------ los controles
def test_los_controles_de_la_barra_lateral_son_los_de_la_definicion():
    at = run()
    for d in GROUP:
        w = widget(at, d.key)
        if d.widget == "number":
            assert (w.min, w.max, w.value) == (d.lo, d.hi, d.default)
        else:
            assert list(w.options) == list(d.options) and w.value == d.default


def test_cada_opcion_de_las_listas_carga_sin_errores():
    at = run()
    for d in GROUP:
        if d.widget != "select":
            continue
        for option in widget(at, d.key).options:
            widget(at, d.key).set_value(option)
            at.run()
            assert not at.exception and not at.error, (d.key, option)


@pytest.mark.parametrize(
    ("crm", "esperado"),
    [("OREAS 501b", "0,248"), ("OREAS 501c", "0,221"), ("OREAS 503c", "0,698"),
     ("OREAS 200", "0,340"), ("CRM propio", "1,000")],
)  # fmt: skip
def test_el_crm_elegido_cambia_el_valor_certificado(crm, esperado):
    at = run()
    widget(at, "q_crm").set_value(crm).run()
    assert not at.exception
    assert any(f"valor certificado **{esperado} g/t**" in m.value for m in at.markdown)


def test_un_sesgo_grande_dispara_el_rechazo_del_lote_y_se_lee_en_la_carta():
    at = run()
    widget(at, "q_sesgo").set_value(4.0).run()
    assert not at.exception
    expected = qcalc.run_crm(qcalc.QaqcParams(sesgo=4.0))
    assert expected.veredicto.veredicto in (qc.RECHAZAR, qc.REENSAYAR)
    assert said(at, "**Rechazo del lote.**") or said(at, "**Re-ensayo del lote.**")


def test_un_pico_de_blancos_sobre_10_ld_es_falla():
    at = run()
    widget(at, "q_pico").set_value(12.0).run()
    assert said(at, "**Falla.** 1 blanco(s) superan 10 × LD")
    widget(at, "q_pico").set_value(0.0).run()
    assert said(at, "Ningún blanco supera 3 veces el límite de detección")


def test_el_tipo_de_duplicado_y_la_precision_cambian_el_veredicto():
    at = run()
    widget(at, "q_dup_tipo").set_value("Pulpa").run()
    assert said(at, "**Duplicados (pulpa): no pasa.**")
    widget(at, "q_dup_p").set_value("20").run()
    assert said(at, "Thompson-Howarth con P = 20 %")


def test_los_dos_elementos_de_gemas_tienen_su_rotulo_no_es_oro():
    at = run()
    assert any(
        "GEMAS, plata (Ag): 104 pares de duplicados de campo" in m.value for m in at.markdown
    )
    assert any("**No es oro**" in m.value for m in at.markdown)
    widget(at, "q_dup_fuente").set_value(qcalc.DUP_FUENTES[1]).run()
    assert any("GEMAS, germanio (Ge): 104 pares" in m.value for m in at.markdown)
    assert said(at, "13 pares con media no positiva") or any(
        "13 pares con media no positiva" in c.value for c in at.caption
    )


# ------------------------------------------------------------------ tablas pegadas
def test_con_las_tablas_precargadas_el_resultado_es_el_de_la_serie_de_ejemplo():
    at = con_tablas()
    assert not at.exception and not at.error
    assert said(at, "Ninguna regla de rechazo ni de re-ensayo se dispara. 1 de 30 resultados")
    assert any("tabla del usuario" in m.value for m in at.markdown)


def test_editar_la_tabla_del_crm_cambia_el_veredicto():
    at = edit(con_tablas(), qaqc_tab.KEY_CRM, {3: {"res": 0.4}})  # muy por encima de 3 SD
    assert not at.exception and said(at, "**Rechazo del lote.** 1 de 30")


def test_el_rechazo_cuenta_las_fallas_fuera_de_3_sd_y_no_las_de_2_sd():
    # un resultado a 16 SD y otro a 2,3 SD: 1 de 30 fuera de ±3 SD (3,3 %), 2 de 30 fuera de ±2 SD
    at = edit(con_tablas(), qaqc_tab.KEY_CRM, {3: {"res": 0.4}, 10: {"res": 0.27}})
    assert said(at, "**Rechazo del lote.** 1 de 30 resultados (3,3 %)")


def test_dos_resultados_seguidos_fuera_de_2_sd_piden_re_ensayo_desde_la_tabla():
    at = edit(con_tablas(), qaqc_tab.KEY_CRM, {5: {"res": 0.27}, 6: {"res": 0.27}})
    assert said(at, "**Re-ensayo del lote.**")


MALAS = [None, float("nan"), float("inf"), -5.0, 1e12, "texto", "<script>alert(1)</script>"]


@pytest.mark.parametrize("key", [qaqc_tab.KEY_CRM, qaqc_tab.KEY_BLK])
@pytest.mark.parametrize("bad", MALAS)
def test_una_celda_mala_de_una_serie_avisa_sin_caerse_ni_llegar_al_html(key, bad):
    at = edit(con_tablas(), key, {3: {"res": bad}})
    assert not at.exception
    blob = json.dumps(texts(at) + alerts(at))
    assert "<script" not in blob.lower() and "alert(1)" not in blob


@pytest.mark.parametrize("col", ["a", "b"])
@pytest.mark.parametrize("bad", MALAS)
def test_una_celda_mala_de_los_duplicados_avisa_sin_caerse_ni_llegar_al_html(col, bad):
    at = edit(con_tablas(), qaqc_tab.KEY_DUP, {3: {col: bad}})
    assert not at.exception
    blob = json.dumps(texts(at) + alerts(at))
    assert "<script" not in blob.lower() and "alert(1)" not in blob


def test_las_celdas_que_no_son_numeros_se_avisan_y_las_negativas_tambien():
    for bad, needle in ((float("inf"), "números finitos"), (-5.0, "no puede ser negativo")):
        at = edit(con_tablas(), qaqc_tab.KEY_CRM, {3: {"res": bad}})
        assert said(at, needle), (bad, alerts(at)[:3])


def test_un_texto_en_una_columna_numerica_lo_descarta_streamlit_y_la_fila_queda_vacia():
    at = edit(con_tablas(), qaqc_tab.KEY_CRM, {3: {"res": "texto"}})
    assert not at.exception and said(at, "1 de 29 resultados")  # la celda vacía no cuenta


def test_una_fila_con_una_sola_celda_llena_en_los_duplicados_se_avisa():
    at = edit(con_tablas(), qaqc_tab.KEY_DUP, {2: {"b": None}})
    assert said(at, "una sola celda llena")


def test_las_filas_vacias_se_ignoran_y_la_tabla_sin_filas_avisa():
    vacias = [{"res": None}] * 5
    at = edit(con_tablas(), qaqc_tab.KEY_CRM, added=vacias)
    assert not at.exception and said(at, "Ninguna regla de rechazo")  # las vacías no cuentan
    at = edit(con_tablas(), qaqc_tab.KEY_CRM, deleted=list(range(30)))
    assert not at.exception and said(at, "entre 1 y 2 000 filas")
    at = edit(con_tablas(), qaqc_tab.KEY_DUP, deleted=list(range(20)))
    assert said(at, "entre 1 y 2 000 filas")


def test_el_tope_de_2000_filas_se_declara_y_se_aplica():
    ok = [{"res": 0.248}] * (qc.MAX_FILAS - 30)
    at = edit(con_tablas(), qaqc_tab.KEY_CRM, added=ok)
    assert not at.exception and not said(at, "entre 1 y 2 000 filas")
    de_mas = [{"res": 0.248}] * (qc.MAX_FILAS - 29)
    at = edit(con_tablas(), qaqc_tab.KEY_CRM, added=de_mas)
    assert not at.exception and said(at, "entre 1 y 2 000 filas")
    miles = [{"a": 1.0, "b": 1.1}] * 5000
    at = edit(con_tablas(), qaqc_tab.KEY_DUP, added=miles)
    assert not at.exception and said(at, "entre 1 y 2 000 filas")


def test_volver_a_la_serie_de_ejemplo_restaura_la_tabla():
    at = edit(con_tablas(), qaqc_tab.KEY_CRM, {3: {"res": 0.4}})
    assert said(at, "**Rechazo del lote.**")
    next(b for b in at.button if b.key == qaqc_tab.KEY_CRM + "_reset").click().run()
    assert not at.exception and not said(at, "**Rechazo del lote.**")


def test_un_crm_propio_sin_sd_valida_se_avisa_en_vez_de_caerse():
    at = run()
    widget(at, "q_crm").set_value("CRM propio")
    widget(at, "q_sd").set_value(0.0005).run()
    assert not at.exception and not at.error


# ------------------------------------------------------------------ español e inglés
_NUMBER = {
    "es": re.compile(r"-?\d+(?: \d{3})*(?:[.,]\d+)?(?:e-?\d+)?"),
    "en": re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?(?:e-?\d+)?"),
}


def _numbers(text: str, lang: str) -> list[float]:
    out = []
    for item in _NUMBER[lang].findall(text.replace(" ", " ")):
        item = item.replace(",", "") if lang == "en" else item.replace(" ", "").replace(",", ".")
        out.append(float(item))
    return out


def _qc_numbers(at: AppTest, lang: str) -> list[list[float]]:
    """Los números de cada texto de la pestaña, de su primer encabezado a su último."""
    seq = [m.value for m in at.markdown]
    start = seq.index(TEXTS[lang]["qc.crm.h"])
    stop = seq.index(TEXTS[lang]["qc.cert.h"]) + 3  # hasta el texto de la certificación
    cap = [c.value for c in at.caption if c.value.startswith(TEXTS[lang]["qc.blk.rules"][:12])]
    return [_numbers(x, lang) for x in seq[start:stop]] + [_numbers(x, lang) for x in cap]


def test_la_pestana_tiene_las_mismas_cifras_en_los_dos_idiomas():
    es_, en = run("es"), run("en")
    a, b = _qc_numbers(es_, "es"), _qc_numbers(en, "en")
    assert len(a) == len(b) > 10 and a == b
    for fig in (2.388, 0.232, 143.0, 2.3868, 0.1293):
        assert any(fig in x for x in a), fig
    assert [_numbers(m.value, "es") for m in es_.metric] == [
        _numbers(m.value, "en") for m in en.metric
    ]
    assert [_numbers(m.delta or "", "es") for m in es_.metric] == [
        _numbers(m.delta or "", "en") for m in en.metric
    ]


def test_los_numeros_cambian_de_formato_pero_no_de_valor():
    es_, en = run("es"), run("en")
    assert any("Con los 150 resultados: media 2,3868 g/t" in m.value for m in es_.markdown)
    assert any("With the 150 results: mean 2.3868 g/t" in m.value for m in en.markdown)


def test_el_selector_de_idioma_conserva_los_datos_del_control_de_calidad():
    at = run()
    widget(at, "q_sesgo").set_value(2.0).run()
    widget(at, "q_dup_tipo").set_value("Pulpa").run()
    at.sidebar.radio[0].set_value("en").run()
    assert not at.exception and widget(at, "q_sesgo").value == 2.0
    assert widget(at, "q_dup_tipo").value == "Pulp"
    assert at.tabs[TAB_INDEX].label == "Quality control"


def test_los_textos_de_error_de_la_interfaz_existen_en_los_dos_idiomas():
    codes = {"filas", "numero", "negativo", "incompleta", "crm", "precision", "sin_pares", "ld",
             "tipo", "recorte"}  # fmt: skip
    for code in codes:
        assert f"qc.err.{code}" in TEXTS["es"] and f"qc.err.{code}" in TEXTS["en"]


def test_apagar_el_movimiento_no_rompe_la_pestana():
    at = run()
    at.toggle[0].set_value(False).run()
    assert not at.exception


# ------------------------------------------------------------------ el servidor y el fuzz
FUERA_DE_RANGO = [(d.key, 1e12) for d in NUMBERS] + [
    ("q_sd", float("nan")), ("q_ld", float("inf")), ("q_n", -5), ("q_sesgo", 100.0),
]  # fmt: skip


@pytest.mark.parametrize(("key", "value"), FUERA_DE_RANGO)
def test_el_servidor_devuelve_al_valor_por_defecto_un_campo_fuera_de_rango(key, value):
    at = run()
    widget(at, key).set_value(value).run()
    assert not at.exception
    assert widget(at, key).value == controles.BY_KEY[key].default


def _fuzz_cases(rng: random.Random):
    """30 combinaciones, ~30 % extremas: límites, fuera de rango y celdas rotas."""
    cases = []
    junk = [None, float("nan"), float("inf"), 0.0, -3.0, 1e12, "x", "<b>"]
    for i in range(N_FUZZ):
        extreme = i < round(N_FUZZ * EXTREME_SHARE)
        side = {}
        for d in NUMBERS:
            if extreme and rng.random() < 0.6:
                side[d.key] = rng.choice([d.lo, d.hi, d.hi * 10, -1.0, float("nan")])
            else:
                side[d.key] = round(rng.uniform(d.lo, d.hi), 3)
        selects = {d.key: rng.randrange(len(d.options)) for d in GROUP if d.widget == "select"}
        tables = {}
        if extreme or rng.random() < 0.3:
            n = rng.choice([0, 1, 3, 5000]) if extreme else rng.randint(5, 20)
            tables = {
                qaqc_tab.KEY_CRM: {
                    "edited_rows": {j: {"res": rng.choice(junk)} for j in rng.sample(range(10), 3)},
                    "added_rows": [{"res": 0.248}] * n,
                    "deleted_rows": list(range(rng.choice([0, 0, 5, 30]))),
                },
                qaqc_tab.KEY_DUP: {
                    "edited_rows": {j: {rng.choice("ab"): rng.choice(junk)}
                                    for j in rng.sample(range(10), 3)},
                    "added_rows": [{"a": 1.0, "b": 1.2}] * n,
                    "deleted_rows": list(range(rng.choice([0, 0, 5, 20]))),
                },
                qaqc_tab.KEY_BLK: {
                    "edited_rows": {j: {"res": rng.choice(junk)} for j in rng.sample(range(10), 3)},
                    "added_rows": [{"res": 0.002}] * n,
                    "deleted_rows": list(range(rng.choice([0, 0, 5, 30]))),
                },
            }  # fmt: skip
        cases.append((side, selects, tables, rng.random() < 0.5))
    rng.shuffle(cases)
    return cases


@pytest.mark.parametrize("lang", ["es", "en"])
def test_fuzz_de_30_combinaciones_no_tira_excepciones(lang):
    at = run(lang)
    for side, selects, tables, move in _fuzz_cases(random.Random(SEED)):
        for key, value in side.items():
            widget(at, key).set_value(value)
        for key, index in selects.items():
            w = widget(at, key)
            w.set_value(w.options[index])
        at.toggle[0].set_value(move)
        for key, state in tables.items():
            at.session_state[key] = state
        at.run()
        assert not at.exception, (side, selects, tables)
        # un rechazo del lote es un veredicto (st.error): lo que no puede haber es una traza
        blob = json.dumps(texts(at) + alerts(at))
        assert not re.search(r"Traceback|nan g/t|inf g/t|NaN|<script", blob)
