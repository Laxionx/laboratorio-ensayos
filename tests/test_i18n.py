"""Español e inglés: mismas claves, mismos números, sin restos de un idioma en el otro, y el
parámetro `?lang=` validado."""

import ast
import json
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
import fusion_graficos  # noqa: E402
import fusion_svg  # noqa: E402
import guia  # noqa: E402
import i18n  # noqa: E402
import modelo_en  # noqa: E402
import nomograma  # noqa: E402
import oro_graficos  # noqa: E402
import validacion_graficos  # noqa: E402
from i18n import TEXTS  # noqa: E402

from muestreo import fusion as fu  # noqa: E402
from muestreo import fusion_datos as fd  # noqa: E402
from muestreo import validacion as val  # noqa: E402

ES, EN = TEXTS["es"], TEXTS["en"]
# restos de español que no deben aparecer en un texto en inglés
SPANISH = re.compile(
    r"[áéíóúñ¿¡]|\b(de|del|la|las|los|el|con|para|por|una|sin|que|se|más|muy)\b", re.IGNORECASE
)


def run(lang: str | None = None, **values) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    if lang is not None:
        at.query_params["lang"] = lang
    at.run()
    for key, value in values.items():
        for w in [*at.sidebar.number_input, *at.sidebar.selectbox, *at.sidebar.checkbox]:
            if w.key == "dato_" + key:
                if isinstance(value, str):
                    with i18n.use(lang or "es"):
                        value = i18n.opt(value)  # las listas muestran el rótulo del idioma
                w.set_value(value)
    if values:
        at.run()
    return at


# ------------------------------------------------------------------ las claves
def test_los_dos_idiomas_tienen_las_mismas_claves():
    assert set(ES) == set(EN), sorted(set(ES) ^ set(EN))


def test_cada_texto_tiene_los_mismos_campos_en_los_dos_idiomas():
    for key in ES:
        assert i18n.fields(ES[key]) == i18n.fields(EN[key]), key


def test_ningun_texto_esta_vacio_y_solo_los_cognados_son_iguales_en_los_dos_idiomas():
    assert not {k for k in ES if not ES[k].strip() or not EN[k].strip()}
    same = {k for k in ES if ES[k] == EN[k]}
    # palabras que se escriben igual (mineral, no), fórmulas, unidades y fuentes citadas
    assert same == {"f.min.mineral", "f.min.pb", "f.min.rp", "fv.m.mineral", "group.Mineral",
                    "no", "p.col.dn", "p.mineral", "plot.gran.d95", "plot.nomo.error",
                    "r.soda", "v.no", "v.s3",
                    # símbolos de la cianuración (R², L, M, N, a, b)
                    "cn.m.r2", "cv.kind.L", "cv.kind.M", "cv.kind.N1", "cv.kind.N2",
                    "cv.kind.a", "cv.kind.b", "cv.kind.r2",
                    # símbolos y unidades de la sedimentación
                    "sd.app.pellet", "sd.cc.f", "sd.no", "sd.plot.c", "sd.plot.u", "sd.v.cma",
                    "sd.v.cmu", "sd.v.tph", "sv.kind.factor", "svg.s.bar", "svg.s.cyl",
                    "svg.s.tu"}  # fmt: skip


def _source_files() -> list[Path]:
    return [p for p in (ROOT / "app").glob("*.py") if not p.name.startswith("textos_")]


def _literals_and_prefixes() -> tuple[set[str], set[str]]:
    literals, prefixes = set(), set()
    for path in _source_files():
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                literals.add(node.value)
            if isinstance(node, ast.JoinedStr) and node.values:
                first = node.values[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    prefixes.add(first.value)
            if (
                isinstance(node, ast.BinOp)
                and isinstance(node.op, ast.Add)
                and isinstance(node.left, ast.Constant)
                and isinstance(node.left.value, str)
            ):
                prefixes.add(node.left.value)
    return literals, prefixes


def test_no_hay_claves_sin_usar():
    literals, prefixes = _literals_and_prefixes()
    prefixes = {p for p in prefixes if "." in p and len(p) >= 3}
    unused = [k for k in ES if k not in literals and not any(k.startswith(p) for p in prefixes)]
    assert not unused, unused


def test_las_familias_dinamicas_estan_completas():
    from controles import DATOS

    for d in DATOS:
        if d.mineral:
            continue
        for field in ("label", "meaning", "source"):
            assert f"dato.{d.key}.{field}" in ES, (d.key, field)
        for option in d.options:
            assert i18n.opt(option) is not None
    for name, n in guia.N_LIMITS.items():
        for part in ("hace", "entra", "sale", "autores"):
            assert f"ficha.{name}.{part}" in ES
        assert all(f"ficha.{name}.limit.{i}" in ES for i in range(1, n + 1))
        assert f"ficha.{name}.limit.{n + 1}" not in ES  # ningún límite queda fuera de la ficha
    assert all(f"react.{i}" in ES for i in range(1, guia.N_REACTIONS + 1))
    assert f"react.{guia.N_REACTIONS + 1}" not in ES
    assert all(f"limits.{i}" in ES for i in range(1, guia.N_LIMITES + 1))
    assert f"limits.{guia.N_LIMITES + 1}" not in ES
    for part in ("muestra", "harina", "nitro", "botón"):
        assert "bal." + part in ES
    from muestreo import fusion_pesos as fp

    assert all("verdict." + v in ES for v in fp.VERDICTS)


def test_las_opciones_de_las_listas_estan_traducidas():
    from controles import DATOS

    for d in DATOS:
        for option in d.options:
            if option.startswith(("Calibrado", "Clásico", "1 assay", "esfera", "cubo")):
                assert "opt." + option in ES and "opt." + option in EN, option


def test_los_textos_en_ingles_no_llevan_palabras_en_espanol():
    bad = {}
    for key, text in EN.items():
        clean = re.sub(r"\{[^}]*\}|`[^`]*`|\*[^*]+\* ", "", text)
        if SPANISH.search(clean):
            bad[key] = text[:80]
    assert not bad, bad


# ------------------------------------------------------------------ el idioma y la URL
@pytest.mark.parametrize("value", ["fr", "EN", "es ", "", "en;alert(1)", "<script>", "../en"])
def test_un_parametro_lang_invalido_es_espanol_sin_error(value):
    at = run(value)
    assert not at.exception
    assert at.tabs[0].label == "Guía"
    assert at.sidebar.radio[0].value == "es"
    assert at.query_params["lang"] == ["es"] or at.query_params["lang"] == "es"


def test_parse_lang_solo_acepta_es_y_en():
    assert [i18n.parse_lang(v) for v in ("es", "en")] == ["es", "en"]
    assert {i18n.parse_lang(v) for v in ("fr", None, 3, ["en"], "EN", " en")} == {"es"}


def test_lang_en_en_la_url_abre_en_ingles_y_el_selector_cambia_el_idioma():
    en = run("en")
    assert [t.label for t in en.tabs] == [
        "Guide",
        "Protocol",
        "Coarse gold",
        "Fusion",
        "Cyanide leach test",
        "Settling test",
        "Validation",
    ]
    assert en.sidebar.radio[0].value == "en"
    en.sidebar.radio[0].set_value("es").run()
    assert en.tabs[0].label == "Guía"
    assert en.query_params["lang"] == ["es"] or en.query_params["lang"] == "es"
    es_ = run()
    es_.sidebar.radio[0].set_value("en").run()
    assert es_.tabs[0].label == "Guide" and not es_.exception


def test_el_valor_de_lang_nunca_llega_al_html_ni_al_svg():
    at = run("en<script>alert(1)</script>")
    blob = json.dumps([m.value for m in at.markdown] + [c.value for c in at.caption])
    assert "alert(1)" not in blob and "<script" not in blob.lower()


def test_los_datos_se_conservan_al_cambiar_de_idioma():
    at = run("es", lot=5000.0)
    at.sidebar.radio[0].set_value("en").run()
    lot = next(w for w in at.sidebar.number_input if w.key == "dato_lot")
    assert lot.value == 5000.0


# ------------------------------------------------------------------ humo de todas las pestañas
@pytest.mark.parametrize("lang", ["es", "en"])
def test_humo_de_todas_las_pestanas(lang):
    at = run(lang)
    assert not at.exception and not at.error
    assert len(at.tabs) == 7 and len(at.metric) == 12
    assert len(at.sidebar.expander) == 6


@pytest.mark.parametrize("lang", ["es", "en"])
def test_humo_con_cambios_que_disparan_avisos(lang):
    at = run(lang, x_flour=0.5, x_silica=3.0, f_sulfur="SO2", m_pirita=30.0, m_cuarzo=50.0)
    assert not at.exception
    warnings = [w.value for w in at.warning]
    assert warnings  # botón fuera de rango y avisos de mata o de crisol


# ------------------------------------------------------------------ mismas cifras
_NUMBER = {
    "es": re.compile(r"-?\d+(?: \d{3})*(?:[.,]\d+)?(?:e-?\d+)?"),
    "en": re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?(?:e-?\d+)?"),
}


def _numbers(text: str, lang: str) -> list[float]:
    """Los números de un texto, leídos con el formato de su idioma."""
    out = []
    for item in _NUMBER[lang].findall(text.replace(" ", " ")):
        item = item.replace(",", "") if lang == "en" else item.replace(" ", "").replace(",", ".")
        out.append(float(item))
    return out


def _figures(at: AppTest, lang: str) -> list[list[float]]:
    parts = [m.value for m in at.metric] + [m.delta for m in at.metric]
    out = [_numbers(p or "", lang) for p in parts]
    for df in at.dataframe:
        for row in df.value.values.tolist():
            out.append([x for x in row if isinstance(x, int | float)])
    return out


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"lot": 8000.0, "m": 2.0, "safety": 5.0},
        {"form": "Clásico (c·f·g·ℓ)", "grade": 12.5, "grain": 300.0, "shape": "cubo"},
        {"x_flour": 0.5, "x_silica": 2.0, "f_sulfur": "SO2", "f_degree": "sesqui"},
    ],
)
def test_las_cifras_son_identicas_en_los_dos_idiomas(values):
    es_, en = run("es", **values), run("en", **values)
    assert not es_.exception and not en.exception
    assert _figures(es_, "es") == _figures(en, "en")
    assert len(es_.metric) == len(en.metric) == 12


def test_las_tablas_de_validacion_tienen_las_mismas_cifras_en_los_dos_idiomas():
    def table_numbers(at, lang):
        rows = []
        for md in at.markdown:
            if md.value.startswith("| "):
                for line in md.value.splitlines()[2:]:
                    cells = line.strip("| ").split(" | ")
                    rows.append([_numbers(c, lang) for c in cells if re.search(r"\d", c)])
        return rows

    es_, en = run("es"), run("en")
    a, b = table_numbers(es_, "es"), table_numbers(en, "en")
    assert len(a) == len(b) > 100
    # solo se comparan las celdas con cifras que no son parte de un rótulo (concepto o nota)
    pairs = [(x, y) for x, y in zip(a, b, strict=True) if len(x) == len(y)]
    assert len(pairs) > 100
    assert all(x == y for x, y in pairs)


def _bottle_numbers(at: AppTest, lang: str) -> list[list[float]]:
    """Los números de cada texto de la pestaña «Ensayo de cianuración» (de su calculadora a su
    vaso) y de la tabla de modelos."""
    texts = [m.value for m in at.markdown]
    start = texts.index(TEXTS[lang]["cn.cal.h"])
    stop = texts.index(TEXTS[lang]["cn.ani.h"])
    out = [_numbers(x, lang) for x in texts[start:stop]]
    for df in at.dataframe:
        for row in df.value.values.tolist():
            out.append(
                [_numbers(x, lang)[0] for x in row if isinstance(x, str) and re.search(r"\d", x)]
            )
    return out


def test_la_pestana_de_cianuracion_tiene_las_mismas_cifras_en_los_dos_idiomas():
    es_, en = run("es"), run("en")
    a, b = _bottle_numbers(es_, "es"), _bottle_numbers(en, "en")
    assert len(a) == len(b) > 10 and a == b
    assert any(94.77 in x for x in a) and any(0.335 in x for x in a)


def test_los_numeros_de_la_pestana_de_cianuracion_cambian_de_formato_pero_no_de_valor():
    es_, en = run("es"), run("en")
    assert any("Última fila: **94,77 %**" in m.value for m in es_.markdown)
    assert any("Last row: **94.77 %**" in m.value for m in en.markdown)
    assert any("R² 0,937" in m.value for m in es_.markdown)
    assert any("R² 0.937" in m.value for m in en.markdown)


def _sed_numbers(at: AppTest, lang: str) -> list[list[float]]:
    """Los números de cada texto de la pestaña «Ensayo de sedimentación» (de su curva a su
    animación)."""
    texts = [m.value for m in at.markdown]
    start = texts.index(TEXTS[lang]["sd.cur.h"])
    stop = texts.index(TEXTS[lang]["sd.ani.h"])
    return [_numbers(x, lang) for x in texts[start:stop]]


def test_la_pestana_de_sedimentacion_tiene_las_mismas_cifras_en_los_dos_idiomas():
    es_, en = run("es"), run("en")
    a, b = _sed_numbers(es_, "es"), _sed_numbers(en, "en")
    assert len(a) == len(b) > 8 and a == b
    assert any(43.6 in x for x in a) and any(0.396 in x for x in a) and any(1.57 in x for x in a)


def test_los_numeros_de_la_pestana_de_sedimentacion_cambian_de_formato_pero_no_de_valor():
    es_, en = run("es"), run("en")
    assert any("diámetro de **43,6 m**" in m.value for m in es_.markdown)
    assert any("diameter of **43.6 m**" in m.value for m in en.markdown)
    assert any("= **0,396 m² por t/d**" in m.value for m in es_.markdown)
    assert any("= **0.396 m² per t/d**" in m.value for m in en.markdown)


# ------------------------------------------------------------------ los gráficos y el esquema
def _fig_text(fig) -> str:
    return json.dumps(fig.to_plotly_json(), ensure_ascii=False)


def _views():
    protocol = calculo.run_protocol(calculo.ProtocolParams(), calculo.MineralParams())
    gold = calculo.run_gold(calculo.GoldParams(), 3.84, 30.0)
    fusion = calculo.run_fusion(calculo.FusionUIParams())
    return protocol, gold, fusion


def test_los_graficos_en_ingles_no_llevan_espanol_y_en_espanol_siguen_igual():
    protocol, gold, fusion = _views()
    m17, chi = val.minnitt_2017_checks(), val.chieregati_checks()
    for lang in ("es", "en"):
        with i18n.use(lang):
            figs = [
                nomograma.nomogram_figure(protocol), nomograma.stage_figure(protocol),
                nomograma.sensitivity_figure(protocol), nomograma.granulometry_figure(protocol),
                oro_graficos.histogram_figure(gold), fusion_graficos.balance_figure(fusion),
                validacion_graficos.variance_figure(m17 + chi),
                validacion_graficos.clifton_figure(),
                validacion_graficos.minnitt_2007_figure(29.6, 9.2),
            ]  # fmt: skip
            blob = " ".join(_fig_text(f) for f in figs)
        if lang == "en":
            texts = re.findall(r'"(?:text|title|name|label|annotation_text)": "([^"]+)"', blob)
            texts += re.findall(r'"title": \{"text": "([^"]+)"', blob)
            bad = [x for x in texts if SPANISH.search(x)]
            assert not bad, bad[:5]
            assert "Play" in blob and "Pause" in blob and "Reproducir" not in blob
        else:
            assert "Reproducir" in blob and "Pausa" in blob


def test_los_esquemas_en_ingles_no_llevan_espanol():
    _, gold, fusion = _views()
    for lang in ("es", "en"):
        with i18n.use(lang):
            texts = re.findall(
                r">([^<]+)</text>",
                oro_graficos.aliquot_svg(gold) + fusion_svg.crucible_svg(fusion),
            )
            label = re.findall(r'aria-label="([^"]+)"', fusion_svg.crucible_svg(fusion))
        if lang == "en":
            assert not [x for x in texts + label if SPANISH.search(x)], texts
            assert any("Liquid lead" in x for x in texts)
        else:
            assert any("Plomo líquido" in x for x in texts)


def test_los_numeros_de_los_esquemas_cambian_de_formato_pero_no_de_valor():
    _, _, fusion = _views()
    with i18n.use("es"):
        es_svg = fusion_svg.crucible_svg(fusion)
    with i18n.use("en"):
        en_svg = fusion_svg.crucible_svg(fusion)
    r = fusion.result
    assert f"{r.lead_hot_cm3:.2f}".replace(".", ",") in es_svg
    assert (
        f"{r.lead_hot_cm3:.2f}" in en_svg
        and f"{r.lead_hot_cm3:.2f}".replace(".", ",") not in en_svg
    )


# ------------------------------------------------------------------ el formato de los números
def test_formato_de_numeros_por_idioma():
    with i18n.use("es"):
        assert i18n.num(1234.5, 1) == "1 234,5" and i18n.num(0.5, 2) == "0,50"
        assert i18n.int_num(20000) == "20 000" and i18n.num_g(2.5) == "2,5"
        assert i18n.decimal(0.000094) == "9,4e-05"
    with i18n.use("en"):
        assert i18n.num(1234.5, 1) == "1,234.5" and i18n.num(0.5, 2) == "0.50"
        assert i18n.int_num(20000) == "20,000" and i18n.num_g(2.5) == "2.5"
        assert i18n.decimal(0.000094) == "9.4e-05"


# ------------------------------------------------------------------ lo que sale del modelo
def _model_labels() -> set[str]:
    out: set[str] = set()
    checks = [
        *val.minnitt_2017_checks(), *val.chieregati_checks(), *val.clifton_checks(),
        *val.minnitt_2007_findings(), *val.minnitt_2007_implied(),
        *val.minnitt_2007_liberation(), *fd.all_checks(),
    ]  # fmt: skip
    for c in checks:
        out.update({c.source, c.item, c.unit, c.note})
    out.update(n for n, *_ in fd.measured_rows())
    out.update(r["carga"] for r in fd.usgs_load_rows())
    out.update(m.name for m in fu.MINERALS)
    from muestreo.protocolo import PRESETS, preset

    for name in PRESETS:
        protocol = preset(name, 3000.0, 30.0, 5.0)
        out.update(s.name for s in protocol.stages)
    out.update({"Inicio", "Chancado y riffle: reducir a dN", "Chancado y riffle: dividir"})
    out.update({"sin base", "mono", "sesqui", "bi", "tri", "sub"})
    return {x for x in out if x}


def test_ningun_rotulo_del_modelo_queda_en_espanol_en_ingles():
    leftovers = {}
    for label in sorted(_model_labels()):
        out = modelo_en.translate(label)
        if SPANISH.search(re.sub(r"\bde\b(?= (?:silicato|CaCO3))", "", out)):
            leftovers[label] = out
    assert not leftovers, leftovers


def test_los_rotulos_del_modelo_siguen_igual_en_espanol():
    with i18n.use("es"):
        assert i18n.tm("Pirita: S a SO3") == "Pirita: S a SO3"
    with i18n.use("en"):
        assert i18n.tm("Pirita: S a SO3") == "Pyrite: S to SO3"
        assert i18n.tm("DSA: 23 148.1 g, dN 0.03 cm") == "DSA: 23,148.1 g, dN 0.03 cm"
        assert i18n.tm("datos impresos: c = 16 000 000, f = 0,5") == (
            "printed data: c = 16,000,000, f = 0.5"
        )


def test_los_errores_conocidos_del_modelo_se_traducen():
    with i18n.use("en"):
        assert i18n.tr_error("el protocolo necesita al menos una etapa") == (
            "the protocol needs at least one stage"
        )
        msg = (
            "«Chancado y riffle»: la masa dividida (1000 g) debe ser menor que la de entrada "
            "(500 g)"
        )
        out = i18n.tr_error(msg)
        assert "must be smaller" in out and "Crushing and riffle splitting" in out
        assert i18n.tr_error("un error que no se conoce") == "un error que no se conoce"
    with i18n.use("es"):
        assert i18n.tr_error("el protocolo necesita al menos una etapa") == (
            "el protocolo necesita al menos una etapa"
        )


def test_un_error_del_modelo_se_muestra_en_ingles_sin_traza():
    at = run("en", preset="PREP-31B", lot=500.0)
    assert not at.exception
    assert any("must be smaller than the input mass" in e.value for e in at.error)
    es_ = run("es", preset="PREP-31B", lot=500.0)
    assert any("debe ser menor que la de entrada" in e.value for e in es_.error)


def test_cada_aviso_del_modelo_tiene_su_texto_y_su_cita_en_los_dos_idiomas():
    sources = [
        (ROOT / "muestreo" / "fusion_avisos.py").read_text(encoding="utf-8"),
        (ROOT / "muestreo" / "crisol.py").read_text(encoding="utf-8"),
    ]
    codes = set(re.findall(r'"([a-z_]+)"(?:, \(\(|\)|,\s*\()', "".join(sources)))
    codes |= {"dry_over_capacity", "melt_over_capacity", "dry_over_two_thirds",
              "melt_over_two_thirds"}  # fmt: skip
    known = {k.split(".")[1] for k in ES if k.startswith("warn.") and k.endswith(".text")}
    assert {"button_low", "button_high", "slag_basic", "slag_acid", "matte_slag",
            "reductant_excess", "lodge_excess", "active_flux", "copper", "perkins",
            "high_sulfur"} <= known  # fmt: skip
    for code in known:
        for table in (ES, EN):
            assert f"warn.{code}.text" in table
            source = code.replace("dry_", "").replace("melt_", "")
            assert f"warn.{code}.source" in table or f"warn.{source}.source" in table
    assert codes >= {"button_low"}


def test_todos_los_avisos_posibles_se_dibujan_en_los_dos_idiomas():
    """Dispara todos los avisos que el modelo puede dar y los pasa por la app en los dos idiomas."""
    from fusion_tab import warning_text

    scenarios = [
        dict(x_flour=0.5), dict(x_flour=2.0), dict(x_silica=3.0), dict(x_silica=0.0),
        dict(x_litharge=0.3), dict(x_litharge=2.0, x_silica=3.0),
        dict(minerals=(("cuarzo", 50.0), ("pirita", 30.0))),
        dict(minerals=(("calcopirita", 40.0), ("cuarzo", 20.0))),
        dict(minerals=(("galena", 60.0), ("pirrotita", 30.0)), degree="bi"),
        dict(sample="30 g", x_silica=3.0, x_litharge=2.0),
    ]  # fmt: skip
    seen = set()
    for kw in scenarios:
        view = calculo.run_fusion(calculo.FusionUIParams(**kw))
        for w in view.result.warnings:
            seen.add(w.code)
            assert w.code, w
            for lang in ("es", "en"):
                with i18n.use(lang):
                    text, source = warning_text(w)
                    assert text and source and "{" not in text
                    if lang == "en":
                        assert not SPANISH.search(text), text
    assert {"button_low", "matte_slag"} <= seen and len(seen) >= 5, seen


# ------------------------------------------------------------------ README y GIF
def test_los_readme_se_enlazan_entre_si_y_los_gif_existen_y_pesan_menos_de_3_mb():
    es_, en = (ROOT / "README.md").read_text("utf-8"), (ROOT / "README.en.md").read_text("utf-8")
    assert es_.splitlines()[0] == "[English version](README.en.md)"
    assert en.splitlines()[0] == "[Versión en español](README.md)"
    assert "?lang=en" in en and "?lang=en" not in es_.split("`?lang=en`")[0]
    for readme, name in ((es_, "fusion-crisol.es.gif"), (en, "fusion-crucible.en.gif")):
        assert f"docs/img/{name}" in readme
        gif = ROOT / "docs" / "img" / name
        assert gif.read_bytes()[:6] in (b"GIF89a", b"GIF87a")
        assert 0 < gif.stat().st_size < 3_000_000


def test_el_ingles_usa_comillas_inglesas_y_no_las_espanolas():
    bad = [k for k, v in EN.items() if "«" in v or "»" in v]
    assert not bad, bad
    assert not [x for x in _model_labels() if "«" in modelo_en.translate(x)]
