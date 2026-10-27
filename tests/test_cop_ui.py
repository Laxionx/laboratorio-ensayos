"""La pestaña «Copelación» dentro de la app: humo en los dos idiomas, encadenada con la fusión,
valores manipulados, un fuzz de 30 combinaciones por idioma (30 % extremas), las mismas cifras en
los dos idiomas y su sección de la pestaña Validación."""

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
pytestmark = pytest.mark.app  # corren la app entera con AppTest: son las lentas
sys.path.insert(0, str(ROOT / "app"))

import controles  # noqa: E402
import i18n  # noqa: E402

SEED, N_FUZZ, EXTREME_SHARE = 20261024, 30, 0.30
GROUP = [d for d in controles.DATOS if d.group == controles.COP]
NUMBERS = [d for d in GROUP if d.widget == "number"]
TAB = {"es": "Copelación", "en": "Cupellation"}
OWN = {"es": "Valor propio", "en": "Own value"}
MODOS = {"es": ["Razón de Rose (según el oro)", "Mínimo de Bugbee (3 a 1)", "Razón propia"],
         "en": ["Rose ratio (by gold weight)", "Bugbee minimum (3 to 1)", "Own ratio"]}  # fmt: skip


def run(lang: str = "es") -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    at.query_params["lang"] = lang
    return at.run()


def widget(at: AppTest, key: str):
    return next(w for w in [*at.sidebar.number_input, *at.sidebar.selectbox]
                if w.key == "dato_" + key)  # fmt: skip


def md(at: AppTest, needle: str) -> str:
    return next((m.value for m in at.markdown if needle in m.value), "")


def metrics(at: AppTest) -> dict[str, tuple[str, str]]:
    return {m.label: (m.value, m.delta) for m in at.metric[12:16]}


def warned(at: AppTest, needle: str) -> bool:
    badges = (m for m in at.markdown if m.value.startswith(":"))
    return any(needle in w.value for w in [*at.warning, *badges])


# ------------------------------------------------------------------ humo
@pytest.mark.parametrize(
    ("lang", "ag", "add", "pearl", "text"),
    [
        (
            "es",
            "Pérdida de plata",
            "Plata que se agrega",
            "Perla",
            "se pierde **4,51 %** de la plata",
        ),
        ("en", "Silver loss", "Silver to add", "Bead", "**4.51 %** of the silver"),
    ],
)
def test_humo_de_la_pestana_en_cada_idioma(lang, ag, add, pearl, text):
    at = run(lang)
    assert not at.exception and not at.error
    assert [t.label for t in at.tabs][4] == TAB[lang]
    values = metrics(at)
    assert list(values) == [ag, values_label(lang, "au"), add, pearl]
    sep = "," if lang == "es" else "."
    assert values[ag] == (f"4{sep}51 %", values[ag][1])
    assert values[add][0] == f"4{sep}27 mg" and values[pearl][0] == f"6{sep}99 mg"
    assert any(text in m.value for m in at.markdown)
    assert len(at.metric) == 42 and len(at.sidebar.expander) == 8


def values_label(lang: str, key: str) -> str:
    return {"es": {"au": "Pérdida de oro"}, "en": {"au": "Gold loss"}}[lang][key]


def test_por_defecto_el_plomo_es_el_de_la_fusion_y_avisa_que_sale_de_la_tabla_x():
    at = run()
    assert "con **28,0 g** de plomo (el botón de la pestaña Fusión)" in md(at, "A **800 °C**")
    assert warned(at, "El plomo sale del rango de la Tabla X (10 a 25 g)")
    assert "6,0 a 1" in metrics(at)["Plata que se agrega"][1]
    assert not warned(at, "congela") and not warned(at, "La temperatura sale")


def test_la_ficha_y_la_guia_incluyen_la_copelacion_en_los_dos_idiomas():
    casos = (
        ("es", "Calcula cuánto oro y plata se pierde", "### Copelación y partición"),
        ("en", "Calculates how much gold and silver", "### Cupellation and parting"),
    )
    for lang, hace, h in casos:
        at = run(lang)
        assert any(hace in m.value for m in at.markdown)
        assert any(m.value.startswith(h) for m in at.markdown)
        assert sum("Rose" in m.value for m in at.markdown) >= 1


# ------------------------------------------------------------------ encadenada con la fusión
def test_cambiar_el_boton_de_la_fusion_cambia_el_plomo_de_la_copelacion():
    at = run()
    widget(at, "f_button").set_value(24.0).run()
    assert not at.exception
    assert "con **24,0 g** de plomo (el botón de la pestaña Fusión)" in md(at, "A **800 °C**")


def test_con_plomo_propio_se_usa_ese_valor_y_no_el_de_la_fusion():
    at = run()
    widget(at, "k_pb_src").set_value(OWN["es"])
    at.run()
    widget(at, "k_pb").set_value(15.0).run()
    assert "con **15,0 g** de plomo (valor propio)" in md(at, "A **800 °C**")
    assert not warned(at, "El plomo sale del rango")  # 15 g está dentro de 10 a 25 g
    widget(at, "f_button").set_value(32.0).run()  # la fusión ya no mueve la copelación
    assert "con **15,0 g** de plomo (valor propio)" in md(at, "A **800 °C**")


def test_si_la_fusion_no_se_puede_calcular_la_copelacion_usa_el_plomo_propio_y_avisa():
    at = run()
    widget(at, "m_pirita").set_value(60.0)
    widget(at, "m_cuarzo").set_value(60.0)
    at.run()
    assert not at.exception
    assert warned(at, "La pestaña Fusión no pudo calcular el botón")
    assert "con **28,0 g** de plomo (valor propio)" in md(at, "A **800 °C**")


# ------------------------------------------------------------------ los datos mueven el resultado
def test_la_temperatura_alta_pierde_mas_y_fuera_de_la_tabla_avisa():
    base = metrics(run())["Pérdida de plata"][0]
    at = run()
    widget(at, "k_temp").set_value(1000.0).run()
    assert not at.exception and not warned(at, "La temperatura sale")
    assert metrics(at)["Pérdida de plata"][0] != base
    widget(at, "k_temp").set_value(1075.0).run()
    assert warned(at, "La temperatura sale del rango de la tabla (700 a 1 000 °C)")


def test_a_700_grados_el_boton_se_congela_para_el_oro():
    at = run()
    widget(at, "k_temp").set_value(700.0).run()
    assert warned(at, "el botón se congela en la Tabla XII")


def test_los_tres_modos_de_la_razon_y_el_veredicto_de_la_particion():
    at = run()
    widget(at, "k_modo").set_value(MODOS["es"][1]).run()
    assert "**3,00 a 1**" in md(at, "Modo:") and warned(at, "parte, pero con más ácido")
    widget(at, "k_modo").set_value(MODOS["es"][2]).run()
    widget(at, "k_razon").set_value(1.0).run()
    assert warned(at, "insuficiente") and not at.exception
    widget(at, "k_razon").set_value(2.5).run()
    assert warned(at, "solo parte si la aleación se lamina fina")
    widget(at, "k_razon").set_value(12.0).run()
    assert warned(at, "buena para partir")


def test_mas_oro_cambia_la_razon_de_rose_y_la_plata_a_agregar():
    at = run()
    antes = metrics(at)["Plata que se agrega"][0]
    widget(at, "k_au").set_value(10.0).run()
    assert "**4,00 a 1**" in md(at, "Modo:") and metrics(at)["Plata que se agrega"][0] != antes


def test_la_ley_corregida_se_muestra():
    at = run()
    widget(at, "k_ley").set_value(5.0).run()
    assert "Ley medida 5,00 g/t, ley corregida **5,01 g/t**" in md(at, "Ley medida")


# ------------------------------------------------------------------ valores manipulados
FUERA_DE_RANGO = [(d.key, 1e12) for d in NUMBERS] + [
    ("k_temp", float("nan")), ("k_temp", float("inf")), ("k_au", -5.0), ("k_ag", -1.0),
    ("k_pb", float("nan")), ("k_ley", float("inf")),
]  # fmt: skip


@pytest.mark.parametrize(("key", "value"), FUERA_DE_RANGO)
def test_el_servidor_devuelve_al_valor_por_defecto_un_campo_fuera_de_rango(key, value):
    at = run()
    widget(at, key).set_value(value).run()
    assert not at.exception
    assert widget(at, key).value == controles.BY_KEY[key].default


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
    for key in ("k_pb_src", "k_modo"):
        for option in widget(at, key).options:
            widget(at, key).set_value(option)
            at.run()
            assert not at.exception, (key, option)


def test_el_selector_de_idioma_conserva_los_datos_de_la_copelacion():
    at = run()
    widget(at, "k_temp").set_value(900.0).run()
    widget(at, "k_modo").set_value(MODOS["es"][1]).run()
    at.sidebar.radio[0].set_value("en").run()
    assert not at.exception and widget(at, "k_temp").value == 900.0
    assert widget(at, "k_modo").value == "Bugbee minimum (3 to 1)"
    assert at.tabs[4].label == "Cupellation"


def test_apagar_el_movimiento_no_rompe_la_pestana():
    at = run()
    at.toggle[0].set_value(False).run()
    assert not at.exception


# ------------------------------------------------------------------ fuzz
def _fuzz_cases(rng: random.Random):
    """30 combinaciones, ~30 % extremas: límites, fuera de rango, NaN, infinito y negativos."""
    cases = []
    for i in range(N_FUZZ):
        extreme = i < round(N_FUZZ * EXTREME_SHARE)
        side = {}
        for d in NUMBERS:
            if extreme and rng.random() < 0.6:
                side[d.key] = rng.choice([d.lo, d.hi, d.hi * 10, -1.0, float("nan"), float("inf")])
            else:
                side[d.key] = round(rng.uniform(d.lo, d.hi), 3)
        selects = {k: rng.randrange(2 if k == "k_pb_src" else 3) for k in ("k_pb_src", "k_modo")}
        fusion = {
            "f_button": rng.choice([20.0, 28.0, 35.0, 1e9]),
            "m_pirita": rng.choice([0.0, 95.0, 80.0]),
        }
        cases.append((side, selects, fusion, rng.random() < 0.5))
    rng.shuffle(cases)
    return cases


@pytest.mark.parametrize("lang", ["es", "en"])
def test_fuzz_de_30_combinaciones_no_tira_excepciones(lang):
    at = run(lang)
    for side, selects, fusion, move in _fuzz_cases(random.Random(SEED)):
        for key, value in {**side, **fusion}.items():
            widget(at, key).set_value(value)
        for key, index in selects.items():
            w = widget(at, key)
            w.set_value(w.options[index])
        at.toggle[0].set_value(move)
        at.run()
        assert not at.exception, (side, selects, fusion)
        # el único error esperado es el veredicto «insuficiente» de una razón propia bajo 2 a 1
        assert all(
            re.search("insuficiente|insufficient|minerales suman|minerals add", e.value)
            for e in at.error
        )
        blob = json.dumps([m.value for m in at.markdown] + [w.value for w in at.warning])
        assert not re.search(r"Traceback|nan mg|inf mg|NaN|nan %|inf %", blob)


# ------------------------------------------------------------------ mismas cifras
_NUMBER = {
    "es": re.compile(r"-?\d+(?: \d{3})*(?:[.,]\d+)?(?:e-?\d+)?"),
    "en": re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?(?:e-?\d+)?"),
}


def _numbers(text: str, lang: str) -> list[float]:
    out = []
    for item in _NUMBER[lang].findall(text.replace(" ", " ").replace("\xa0", " ")):
        item = item.replace(",", "") if lang == "en" else item.replace(" ", "").replace(",", ".")
        out.append(float(item))
    return out


def _tab_numbers(at: AppTest, lang: str) -> list[list[float]]:
    texts = [m.value for m in at.markdown]
    start = texts.index(i18n.TEXTS[lang]["cp.cal.h"])
    stop = texts.index(i18n.TEXTS[lang]["cp.ani.h"])
    out = [_numbers(x, lang) for x in texts[start:stop]]
    out += [_numbers(c.value, lang) for c in at.caption if "Bugbee" in c.value][-2:]
    for m in at.metric[12:16]:
        out += [_numbers(m.value, lang), _numbers(m.delta or "", lang)]
    for df in at.dataframe[4:6]:
        for row in df.value.values.tolist():
            out.append([x for x in row if isinstance(x, int | float)])
    return out


def test_la_pestana_tiene_las_mismas_cifras_en_los_dos_idiomas():
    es_, en = run("es"), run("en")
    a, b = _tab_numbers(es_, "es"), _tab_numbers(en, "en")
    assert len(a) == len(b) > 10 and a == b
    assert any(4.51 in x for x in a) and any(3.85 in x for x in a)


def test_los_numeros_cambian_de_formato_pero_no_de_valor():
    es_, en = run("es"), run("en")
    assert any("Ley medida 3,84 g/t, ley corregida **3,85 g/t**" in m.value for m in es_.markdown)
    assert any("Measured grade 3.84 g/t, corrected grade **3.85 g/t**" in m.value
               for m in en.markdown)  # fmt: skip


def _validation_numbers(at: AppTest, lang: str) -> list[list[float]]:
    texts = [m.value for m in at.markdown]
    start = texts.index(i18n.TEXTS[lang]["cp.v.h"])
    out = []
    for text in texts[start:]:
        if text.startswith("| "):
            for line in text.splitlines()[2:]:
                out.append([_numbers(c, lang) for c in line.strip("| ").split(" | ")
                            if re.search(r"\d", c)])  # fmt: skip
        else:
            out.append(_numbers(text, lang))
    return out


def test_la_validacion_de_copelacion_tiene_las_mismas_cifras_en_los_dos_idiomas():
    a, b = _validation_numbers(run("es"), "es"), _validation_numbers(run("en"), "en")
    assert len(a) == len(b) > 10
    pairs = [(x, y) for x, y in zip(a, b, strict=True) if len(x) == len(y)]
    assert len(pairs) > 10 and all(x == y for x, y in pairs)


def test_la_pestana_validacion_dice_con_honestidad_que_no_cuadra_y_por_que():
    at = run()
    assert "**Veredicto: cuadran 0 de 2.**" in md(at, "Veredicto: cuadran")
    assert "Solapan **2 de 28** celdas" in md(at, "Solapan")
    assert "-34,8" in md(at, "| Plata (mg)") and "-28,5" in md(at, "| Plata (mg)")
    en = run("en")
    assert "**Verdict: 0 of 2 fit.**" in md(en, "Verdict: 0 of 2")
    assert "-34.8" in md(en, "| Silver (mg)")
