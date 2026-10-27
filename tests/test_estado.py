"""«Estado de la operación», «Casos publicados» y «Prueba esto» de las pestañas de cálculo: cada
experimento hace lo que dice su texto (dirección de cada magnitud y nivel del panel), cada chequeo
lleva su fuente, los casos publicados reproducen lo impreso y los botones ponen el cambio en la
barra lateral. Las pruebas del modelo son rápidas; las que abren la app llevan `app`."""

import math
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app" / "streamlit_app.py")
sys.path.insert(0, str(ROOT / "app"))

import cian_estado as ce  # noqa: E402
import cop_estado as pe_cop  # noqa: E402
import fusion_estado as fe  # noqa: E402
import i18n  # noqa: E402
import prot_estado as pe  # noqa: E402
import qaqc_estado as qe  # noqa: E402
import sed_estado as se  # noqa: E402
import val_estado as ve  # noqa: E402
from calculo import FusionUIParams, run_fusion, run_protocol  # noqa: E402
from controles import BY_KEY, PREFIX  # noqa: E402
from estado import Fila, controles_de, peor  # noqa: E402

from muestreo import copelacion_datos as cd  # noqa: E402
from muestreo import fusion_datos as fd  # noqa: E402
from muestreo import validacion as val  # noqa: E402

# prefijo de los botones → (índice de la pestaña, experimentos, pares, nivel del ejemplo)
SUITES = {
    "prot": (1, pe.EXPERIMENTOS_PROT, pe.pares_prot, "aviso"),
    "oro": (2, pe.EXPERIMENTOS_ORO, pe.pares_oro, "aviso"),
    "fus": (3, fe.EXPERIMENTOS_FUS, fe.pares_fus, "ok"),
    "cop": (4, pe_cop.EXPERIMENTOS_COP, pe_cop.pares_cop, "aviso"),
    "cian": (5, ce.EXPERIMENTOS_CIAN, ce.pares_cian, "aviso"),
    "sed": (6, se.EXPERIMENTOS_SED, se.pares_sed, "ok"),
    "qc": (7, qe.EXPERIMENTOS_QC, qe.pares_qaqc, "aviso"),
}
TODOS = [(k, e.clave) for k, (_, exps, _, _) in SUITES.items() for e in exps]


def run(lang: str = "es") -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    at.query_params["lang"] = lang
    return at.run()


def widget(at: AppTest, key: str):
    return next(
        w
        for w in [*at.sidebar.number_input, *at.sidebar.selectbox, *at.sidebar.checkbox]
        if w.key == key
    )


def badges(at: AppTest, tab: int) -> list[str]:
    return [m.value for m in at.tabs[tab].markdown if "-badge[" in m.value]


# ---------------------------------------------------------------- cada experimento hace lo dicho
@pytest.mark.parametrize(("suite", "clave"), TODOS)
def test_cada_experimento_mueve_las_magnitudes_en_la_direccion_de_su_texto(suite, clave):
    _, exps, pares, _ = SUITES[suite]
    e = next(x for x in exps if x.clave == clave)
    _, a, b = next(p for p in pares() if p[0] is e)
    for nombre, signo in e.direcciones.items():
        delta = getattr(b, nombre) - getattr(a, nombre)
        if signo == 0:
            assert math.isclose(getattr(b, nombre), getattr(a, nombre), rel_tol=1e-9), nombre
        else:
            assert delta * signo > 0, (clave, nombre, getattr(a, nombre), getattr(b, nombre))
    assert e.nivel is None or b.nivel == e.nivel, (clave, b.nivel)


@pytest.mark.parametrize("suite", list(SUITES))
def test_el_panel_del_ejemplo_tiene_el_nivel_que_dice_la_prueba(suite):
    _, _, pares, nivel = SUITES[suite]
    _, base, _ = pares()[0]
    assert base.nivel == nivel


@pytest.mark.parametrize("lang", ["es", "en"])
@pytest.mark.parametrize("suite", list(SUITES))
def test_cada_prueba_trae_titulo_texto_con_cifras_y_cambios_en_claves_de_la_barra(suite, lang):
    _, exps, _, _ = SUITES[suite]
    funcion = {
        "prot": pe.pruebas_prot,
        "oro": pe.pruebas_oro,
        "fus": fe.pruebas_fus,
        "cop": pe_cop.pruebas_cop,
        "cian": ce.pruebas_cian,
        "sed": se.pruebas_sed,
        "qc": qe.pruebas_qaqc,
    }[suite]
    with i18n.use(lang):
        items = funcion()
    assert [p.clave for p in items] == [e.clave for e in exps]
    for p in items:
        assert p.titulo and any(ch.isdigit() for ch in p.texto), p.clave
        assert "{" not in p.texto and p.cambios
        assert all(k.startswith(PREFIX) and k[len(PREFIX) :] in BY_KEY for k in p.cambios)


# ------------------------------------------------------------------ lo que afirma cada texto
def test_las_pruebas_de_protocolo_dicen_lo_que_el_modelo_cumple():
    pares = {e.clave: (a, b) for e, a, b in pe.pares_prot()}
    a, b = pares["division"]
    assert not b.seguridad and b.rsd < a.rsd  # sigue sin cumplir la seguridad
    a, b = pares["alicuota"]
    assert b.rsd_ult < a.rsd_ult and a.rsd - b.rsd < 0.05 * a.rsd  # el total casi no se mueve
    assert b.parte1 > a.parte1  # la etapa 1 pesa más
    a, b = pares["lote"]
    assert b.rsd > a.rsd


def test_las_pruebas_de_oro_dicen_lo_que_el_modelo_cumple():
    pares = {e.clave: (a, b) for e, a, b in pe.pares_oro()}
    assert math.isclose(pares["grano100"][1].lam / pares["grano100"][0].lam, 1.5**3, rel_tol=1e-9)
    assert pares["grano100"][1].nivel == "aviso" and pares["grano100"][1].lam < 20
    assert math.isclose(pares["alicuota"][1].lam / pares["alicuota"][0].lam, 50 / 30, rel_tol=1e-9)
    a, b = pares["grano50"]
    assert b.lam >= 20 and b.nivel == "ok"
    assert abs(b.mediana - pe.GRADO_BASE) < abs(a.mediana - pe.GRADO_BASE)  # más cerca de la ley


def test_las_pruebas_de_fusion_dicen_lo_que_el_modelo_cumple():
    pares = {e.clave: (a, b) for e, a, b in fe.pares_fus()}
    a, b = pares["harina"]
    assert b.boton < fe.BUTTON_RANGE[0] <= a.boton and b.grado < a.grado
    a, b = pares["litargirio"]
    assert math.isclose(b.litargirio / a.litargirio, 0.6, rel_tol=1e-9)
    assert b.grado > 2.0 > 1.0 and b.escoria < a.escoria
    a, b = pares["mono"]
    assert a.polvo < fe.CRUCIBLE.fill_limit_cm3 < b.polvo  # pasa de los 2/3 del crisol
    assert math.isclose(b.grado, 1.0, rel_tol=1e-9)


def test_las_pruebas_de_copelacion_dicen_lo_que_el_modelo_cumple():
    pares = {e.clave: (a, b) for e, a, b in pe_cop.pares_cop()}
    assert "congelado" in pares["frio"][1].avisos and "congelado" not in pares["frio"][0].avisos
    assert pares["razon"][1].estado == "insuficiente" and pares["razon"][1].agregada == 0.0
    assert pares["razon"][1].razon_final < cd.LINGOTE_RAZON[0] < pares["razon"][0].razon_final
    assert pares["caliente"][0].estado == "lenta"


def test_las_pruebas_de_cianuracion_dicen_lo_que_el_modelo_cumple():
    pares = {e.clave: (a, b) for e, a, b in ce.pares_cian()}
    a, b = pares["cabeza"]
    assert a.lejos == 0 and b.lejos == 7  # las 7 filas de la Tabla 4
    a, b = pares["factor"]
    assert b.lejos == 7 and b.cabeza > a.cabeza


def test_las_pruebas_de_sedimentacion_dicen_lo_que_el_modelo_cumple():
    pares = {e.clave: (a, b) for e, a, b in se.pares_sed()}
    a, b = pares["caudal"]
    assert math.isclose(b.au, a.au, rel_tol=1e-9)  # el área unitaria no depende del caudal
    assert math.isclose(b.area / a.area, 2.0, rel_tol=1e-9)
    assert math.isclose(b.diametro / a.diametro, math.sqrt(2.0), rel_tol=1e-9)
    a, b = pares["vale"]
    assert math.isclose(b.au / a.au, se.sd.FACTOR_VALE_LAMAS, rel_tol=1e-9)


def test_las_pruebas_de_control_de_calidad_dicen_lo_que_el_modelo_cumple():
    pares = {e.clave: (a, b) for e, a, b in qe.pares_qaqc()}
    a, b = pares["sesgo"]
    assert a.veredicto == "pasa" and b.veredicto == "rechazar" and b.n_fuera_3sd == 1
    a, b = pares["precision"]
    assert b.pct99 < 99.0 <= 100.0 and b.pct90 > a.pct90  # mejora, pero no pasa
    a, b = pares["pico"]
    assert a.veredicto_blk == "alerta" and b.veredicto_blk == "falla"


# ------------------------------------------------------------------ cada chequeo lleva su fuente
def _filas_del_ejemplo() -> dict[str, list[Fila]]:
    from calculo import GoldParams, MineralParams, ProtocolParams, run_gold
    from cop_calculo import CopParams, boton_de_fusion, run_cop
    from qaqc_calculo import QaqcParams, run_blk, run_cert, run_crm, run_dup
    from sed_calculo import SedParams, run_sed

    p, mp, f = ProtocolParams(), MineralParams(), FusionUIParams()
    cian = ce.run_cian(ce.CianParams(), *ce._tabla4())
    qp = QaqcParams()
    return {
        "prot": pe.filas_protocolo(run_protocol(p, mp), p, mp),
        "oro": pe.filas_oro(run_gold(GoldParams(), pe.GRADO_BASE, pe.ALICUOTA_BASE)),
        "fus": fe.filas_fusion(run_fusion(f), f),
        "cop": pe_cop.filas_cop(run_cop(CopParams(), boton_de_fusion(f))),
        "cian": ce.filas_cian(cian),
        "sed": se.filas_sed(run_sed(SedParams())),
        "qc": qe.filas_qaqc(qp, run_crm(qp), run_dup(qp), run_blk(qp), run_cert()),
    }


@pytest.mark.parametrize("lang", ["es", "en"])
def test_todos_los_chequeos_del_ejemplo_llevan_texto_y_fuente(lang):
    with i18n.use(lang):
        todas = _filas_del_ejemplo()
    for suite, filas in todas.items():
        assert filas, suite
        for f in filas:
            assert f.texto and f.ayuda and "{" not in f.texto + f.ayuda, (suite, f)


def test_los_niveles_de_fusion_son_los_avisos_del_modelo():
    """Una fila de fusión está en rango si y solo si el modelo no emitió el aviso que resume."""
    casos = [
        FusionUIParams(),
        FusionUIParams(x_flour=0.0),
        FusionUIParams(x_litharge=0.6),
        FusionUIParams(degree="mono"),
        FusionUIParams(x_silica=3.0),
        FusionUIParams(minerals=(("cuarzo", 50.0), ("pirita", 25.0))),
    ]
    for f in casos:
        view = run_fusion(f)
        codigos = {w.code for w in view.result.warnings}
        with i18n.use("es"):
            filas = fe.filas_fusion(view, f)
        malas = [x for x in filas if x.nivel != "ok"]
        emitidos = codigos - {"button_low", "button_high"}
        assert len(malas) == len(emitidos) + (not 25 <= view.result.button_g <= 30), (f, codigos)
        assert all(x.ayuda for x in filas)


# ------------------------------------------------------------------ los casos publicados
def test_el_caso_de_minnitt_reproduce_la_tabla_viii_al_redondeo_impreso():
    p, mp = pe.ProtocolParams(), pe.MineralParams()
    from dataclasses import replace

    p = replace(p, preset=pe.PRESETS[2], lot_correction=False)
    assert pe.caso_activo(p, mp) == pe.CLAVE_MINNITT
    assert pe.caso_activo(replace(p, lot_correction=True), mp) is None
    rows = pe.filas_publicadas(run_protocol(p, mp))
    assert len(rows) == 4  # las 4 divisiones del protocolo están en la tabla
    for s in run_protocol(p, mp).result.stages:
        printed = pe.publicada(s.mass_out_g, s.d_n_cm)
        assert printed is not None and val.matches_rounding(s.variance, printed), s.name


@pytest.mark.parametrize(("clave", "etiqueta", "minerales"), fe.CASOS)
def test_el_caso_de_bugbee_da_lo_mismo_que_la_validacion(clave, etiqueta, minerales):
    f = fe.parametros_caso(minerales)
    assert fe.caso_activo(f) == clave
    d = run_fusion(f).designed
    for key, nombre, _ in fe.REACTIVOS:
        check = fe.publicado(etiqueta, nombre)
        assert math.isclose(getattr(d, key + "_g"), check.calculated, rel_tol=1e-9), (clave, key)
    assert fe.caso_activo(FusionUIParams()) is None


def test_los_casos_de_copelacion_reproducen_las_tablas_ix_y_xii_en_sus_nudos():
    for c in pe_cop.CASOS:
        p = pe_cop.parametros_caso(c)
        v = pe_cop.run_cop(p, None)
        assert pe_cop.caso_activo(p, v) == c.clave and not v.res.avisos
        assert math.isclose(
            v.res.perdida_ag.pct, pe_cop._fila(cd.TABLA_IX, c.temp_c)[3], abs_tol=1e-9
        )
        assert math.isclose(
            v.res.perdida_au.pct, pe_cop._fila(cd.TABLA_XII, c.temp_c)[3], abs_tol=1e-9
        )


def test_la_tabla_4_de_cianuracion_es_el_caso_del_ejemplo():
    view = ce.run_cian(ce.CianParams(), *ce._tabla4())
    assert ce.es_tabla4(view)
    for calc, pub in zip(view.balance.recuperacion_pct, ce.cd.RECUPERACION_PUB, strict=True):
        assert round(calc, 2) == pub
    assert not ce.es_tabla4(ce.run_cian(ce.CianParams(head=900.0), *ce._tabla4()))


def test_el_resumen_de_validacion_suma_lo_que_cada_area_ya_calcula():
    from muestreo import cianuracion_datos as cian
    from muestreo import copelacion_validacion as cop
    from muestreo import qaqc_validacion as qaqc
    from muestreo import sedimentacion_datos as sed

    r = ve.resumen()
    total = (
        len(val.minnitt_2017_checks())
        + len(val.chieregati_checks())
        + len(val.clifton_checks())
        + len(fd.all_checks())
        + len(cian.all_checks())
        + len(sed.all_checks())
        + len(cop.celdas_cuantitativas())
        + len(qaqc.all_checks())
    )
    assert r.total == total and 0 < r.ok <= r.total and r.fallan == r.total - r.ok


def test_peor_nivel_de_un_panel():
    assert peor([Fila("ok", "a"), Fila("aviso", "b")]) == "aviso"
    assert peor([Fila("aviso", "a"), Fila("mal", "b")]) == "mal"
    assert peor([Fila("ok", "a")]) == "ok"
    with pytest.raises(ValueError):
        Fila("rojo", "x")


# ---------------------------------------------------------------- la app: botones y paneles
def _aplicado(at: AppTest, suite: str, clave: str) -> None:
    exps = SUITES[suite][1]
    e = next(x for x in exps if x.clave == clave)
    with i18n.use(at.session_state["lang"]):
        esperado = controles_de(e.ctl)
    for key, value in esperado.items():
        w = widget(at, key)
        if isinstance(value, float):
            assert math.isclose(w.value, value, rel_tol=1e-9), key
        else:
            assert w.value == value, key


def _nivel_de(at: AppTest, tab: int) -> str:
    lineas = badges(at, tab)
    if any(x.startswith(":red-badge[") for x in lineas):
        return "mal"
    return "aviso" if any(x.startswith(":orange-badge[") for x in lineas) else "ok"


@pytest.mark.app
@pytest.mark.parametrize(("suite", "clave"), TODOS)
def test_los_botones_ponen_el_cambio_y_el_panel_lo_refleja(suite, clave):
    tab, exps, _, _ = SUITES[suite]
    e = next(x for x in exps if x.clave == clave)
    at = run()
    assert _nivel_de(at, tab) == SUITES[suite][3]
    next(b for b in at.button if b.key == f"{suite}_prueba_{clave}").click().run()
    assert not at.exception and not at.error
    _aplicado(at, suite, clave)
    if e.nivel is not None:
        assert _nivel_de(at, tab) == e.nivel
    next(b for b in at.button if b.key == f"{suite}_prueba_reset").click().run()
    assert not at.exception and _nivel_de(at, tab) == SUITES[suite][3]


@pytest.mark.app
@pytest.mark.parametrize("suite", list(SUITES))
def test_los_botones_funcionan_tambien_en_ingles(suite):
    tab, exps, _, _ = SUITES[suite]
    e = exps[-1]
    at = run("en")
    assert not at.exception
    next(b for b in at.button if b.key == f"{suite}_prueba_{e.clave}").click().run()
    assert not at.exception and not at.error
    _aplicado(at, suite, e.clave)
    if e.nivel is not None:
        assert _nivel_de(at, tab) == e.nivel
    assert any("Warning" in x or "Problem" in x or "In range" in x for x in badges(at, tab))


@pytest.mark.app
def test_el_boton_del_caso_de_minnitt_pone_los_datos_y_muestra_publicado_y_delta():
    at = run()
    assert not any("Publicado" in df.value.columns for df in at.tabs[1].dataframe)
    next(b for b in at.button if b.key == "prot_caso_minnitt").click().run()
    assert not at.exception
    frames = [df.value for df in at.tabs[1].dataframe if "Publicado" in df.value.columns]
    assert len(frames) == 1 and len(frames[0]) == 4
    assert widget(at, PREFIX + "lot_correction").value is False


@pytest.mark.app
@pytest.mark.parametrize("clave", ["bugbee50", "bugbee100"])
def test_el_boton_del_caso_de_bugbee_deja_la_carga_exacta(clave):
    at = run()
    next(b for b in at.button if b.key == f"fus_caso_{clave}").click().run()
    assert not at.exception and not at.error
    frames = [df.value for df in at.tabs[3].dataframe if "Publicado" in df.value.columns]
    assert len(frames) == 1 and len(frames[0]) == 3
    assert any("(puesto)" in b.label for b in at.button if b.key == f"fus_caso_{clave}")


@pytest.mark.app
@pytest.mark.parametrize("clave", ["lodge925", "lodge1000"])
def test_el_boton_del_caso_de_lodge_muestra_delta_cero(clave):
    at = run()
    next(b for b in at.button if b.key == f"cop_caso_{clave}").click().run()
    assert not at.exception and not at.error
    frames = [df.value for df in at.tabs[4].dataframe if "Publicado" in df.value.columns]
    assert len(frames) == 1
    assert set(frames[0]["Δ"]) == {"0"}


@pytest.mark.app
def test_la_tabla_4_de_cianuracion_muestra_publicado_y_delta_solo_con_sus_datos():
    at = run()
    assert [df for df in at.tabs[5].dataframe if "Publicado" in df.value.columns]
    widget(at, PREFIX + "c_head").set_value(900.0).run()
    assert not [df for df in at.tabs[5].dataframe if "Publicado" in df.value.columns]


@pytest.mark.app
def test_los_indicadores_nuevos_estan_en_filas_de_3_con_ayuda():
    at = run()
    por_label = {m.label: m for m in at.metric}
    for label in (
        "Recuperación final",
        "Área unitaria",
        "Lote del CRM",
        "Cuadran con lo publicado",
    ):
        assert label in por_label and por_label[label].help, label
    assert all(
        len(m.label) <= 24
        for k, m in por_label.items()
        if k
        in {
            "Recuperación final",
            "Cabeza por balance (ppb)",
            "R² potencial",
            "Área unitaria",
            "Área requerida (m²)",
            "Diámetro (m)",
            "Lote del CRM",
            "Duplicados bajo umbral",
            "Blancos sobre 3 × LD",
            "Cuadran con lo publicado",
            "No cuadran",
            "Áreas validadas",
        }
    )
