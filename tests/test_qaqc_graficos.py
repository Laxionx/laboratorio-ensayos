"""Los gráficos de «Control de calidad» salen del cálculo: la carta del CRM se arma punto a punto
(cuadros, estados y reglas del cálculo), Thompson-Howarth y la curva de diferencias llevan los
conteos y umbrales del cálculo, los blancos y el histograma de CDN-GS-2X también; y en inglés no
queda español."""

import json
import math
import re
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
pytest.importorskip("plotly")

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import i18n  # noqa: E402
import qaqc_calculo as qcalc  # noqa: E402
import qaqc_graficos as qg  # noqa: E402

from muestreo import qaqc as qc  # noqa: E402
from muestreo import qaqc_datos as dd  # noqa: E402

SPANISH = re.compile(
    r"[áéíóúñ¿¡]|\b(de|del|la|las|los|el|con|para|por|una|sin|que|se|más|muy)\b", re.IGNORECASE
)
ESTADO_TRAZO = dict(zip(qc.ESTADOS, range(1, 5), strict=True))  # el trazo 0 es la línea


def crm(**kw) -> qcalc.CrmView:
    return qcalc.run_crm(qcalc.QaqcParams(**kw))


def con_rechazo() -> qcalc.CrmView:
    """Una serie de tabla con de todo: advertencia, par seguido y rechazo."""
    o = dd.OREAS[0]
    s = o.sd_sin_redondear
    valores = [o.valor] * 6 + [o.valor + 2.5 * s, o.valor, o.valor - 2.5 * s, o.valor + 2.2 * s]
    valores += [o.valor, o.valor + 3.5 * s, o.valor]
    return qcalc.run_crm(qcalc.QaqcParams(crm_fuente=qcalc.FUENTES[1]), valores)


def frame_xy(frame, trace: int) -> tuple[list, list]:
    d = frame.data[trace]
    return list(d.x), list(d.y)


# ------------------------------------------------------------------ la carta del CRM
def test_la_figura_inicial_es_la_serie_completa_del_calculo():
    v = con_rechazo()
    fig = qg.crm_figure(v)
    for state, k in ESTADO_TRAZO.items():
        mine = [p for p in v.puntos if p.estado == state]
        assert list(fig.data[k].x) == [p.n for p in mine]
        assert list(fig.data[k].y) == [p.valor for p in mine]
    assert list(fig.data[0].y) == [p.valor for p in v.puntos]


def test_cada_cuadro_agrega_un_resultado_y_conserva_los_estados_del_calculo():
    v = con_rechazo()
    fig = qg.crm_figure(v)
    n = len(v.puntos)
    assert [f.name for f in fig.frames] == [str(k) for k in range(1, n + 1)]
    for k, frame in enumerate(fig.frames, start=1):
        assert list(frame.traces) == [0, 1, 2, 3, 4]
        assert frame_xy(frame, 0)[0] == list(range(1, k + 1))
        total = sum(len(frame.data[i].x) for i in range(1, 5))
        assert total == k
        for state, tr in ESTADO_TRAZO.items():
            assert frame_xy(frame, tr)[0] == [p.n for p in v.puntos[:k] if p.estado == state]


def test_la_regla_que_se_dispara_se_rotula_en_cada_cuadro():
    v = con_rechazo()
    fig = qg.crm_figure(v)
    estados = [p.estado for p in v.puntos]
    assert qc.FUERA_2SD in estados and qc.DOS_SEGUIDOS in estados and qc.FUERA_3SD in estados
    for frame, p in zip(fig.frames, v.puntos, strict=True):
        note = frame.layout.annotations[0].text
        assert f"{p.n}" in note and i18n.t(f"qc.crm.rule.{p.estado}") in note
    assert fig.layout.annotations[0].text == fig.frames[-1].layout.annotations[0].text


def test_las_lineas_de_limite_son_las_del_cruce_de_certificado_y_sd():
    v = crm()
    fig = qg.crm_figure(v)
    ys = sorted({round(d.y[0], 9) for d in fig.data[5:]})
    esperado = sorted(round(x, 9) for x in (v.certificado, *v.lim2, *v.lim3))
    assert ys == esperado
    assert math.isclose(v.lim3[1] - v.certificado, 3 * v.sd) and v.sd == v.sd


def test_cambiar_un_resultado_cambia_la_figura_y_su_regla():
    base = con_rechazo()
    o = dd.OREAS[0]
    valores = [p.valor for p in base.puntos]
    valores[11] = o.valor  # el rechazo desaparece
    nuevo = qcalc.run_crm(qcalc.QaqcParams(crm_fuente=qcalc.FUENTES[1]), valores)
    assert qc.FUERA_3SD not in [p.estado for p in nuevo.puntos]
    f0, f1 = qg.crm_figure(base), qg.crm_figure(nuevo)
    assert list(f0.data[4].x) == [12] and list(f1.data[4].x) == []


def test_el_reproductor_no_arranca_solo_y_tiene_botones_y_deslizador_en_cada_idioma():
    v = crm()
    for lang, play, pause in (("es", "Reproducir", "Pausa"), ("en", "Play", "Pause")):
        with i18n.use(lang):
            fig = qg.crm_figure(v)
        labels = [b.label for b in fig.layout.updatemenus[0].buttons]
        assert [x.split()[-1] for x in labels] == [play, pause]
        slider = fig.layout.sliders[0]
        assert slider.active == len(slider.steps) - 1  # arranca en el último cuadro
        assert [s.label for s in slider.steps] == [f.name for f in fig.frames]
        assert not fig.layout.updatemenus[0].buttons[0].args[1].get("autoplay", False)


def test_con_muchos_resultados_los_cuadros_son_a_lo_mas_100_y_terminan_en_el_ultimo():
    assert qcalc.cuadros(30) == list(range(1, 31))
    assert qcalc.cuadros(100) == list(range(1, 101))
    for n in (101, 250, 1999, 2000):
        ks = qcalc.cuadros(n)
        assert len(ks) <= qcalc.MAX_CUADROS + 1 and ks[-1] == n and ks == sorted(set(ks))
        assert ks[0] >= 1
    v = crm(crm_fuente=qcalc.FUENTES[0], n=200)
    assert len(qg.crm_figure(v).frames) == 100


def test_la_serie_sintetica_es_la_misma_cada_vez_y_viene_rotulada():
    a = dd.serie_crm_sintetica(0.248, 0.00952, 30)
    assert a == dd.serie_crm_sintetica(0.248, 0.00952, 30)
    assert (
        dd.serie_crm_sintetica(0.248, 0.00952, 20) == a[:20]
    )  # semilla fija: el prefijo es el mismo
    v = crm()
    assert v.sintetica
    assert "serie sintética de ejemplo" in qg.crm_figure(v).layout.title.text
    own = qcalc.run_crm(qcalc.QaqcParams(crm_fuente=qcalc.FUENTES[1]), [0.25] * 5)
    assert "tabla del usuario" in qg.crm_figure(own).layout.title.text


def test_el_sesgo_del_ejemplo_desplaza_la_media_de_la_serie():
    base = dd.serie_crm_sintetica(1.0, 0.01, 50)
    sesgada = dd.serie_crm_sintetica(1.0, 0.01, 50, sesgo_pct=3.0)
    delta = sum(b - a for a, b in zip(base, sesgada, strict=True)) / 50
    assert delta == pytest.approx(0.03, abs=1e-4)


# ------------------------------------------------------------------ Thompson-Howarth y diferencias
def dup(**kw) -> qcalc.DupView:
    return qcalc.run_dup(qcalc.QaqcParams(**kw))


def test_th_dibuja_cada_par_con_media_positiva_en_su_grupo_y_con_los_conteos_del_calculo():
    v = dup()
    fig = qg.th_figure(v)
    drawn = [sum(len(fig.data[i].x) for i in range(3))][0]
    assert drawn == v.th.n - v.th.sin_media == 104
    names = [fig.data[i].name for i in range(3)]
    assert f"({v.th.dentro90})" in names[0]
    assert f"({v.th.dentro99 - v.th.dentro90})" in names[1]
    assert f"({v.th.n - v.th.dentro99})" in names[2]
    assert len(fig.data[0].x) == v.th.dentro90


def test_las_lineas_de_th_tienen_la_pendiente_del_calculo():
    v = dup(dup_p="20")
    fig = qg.th_figure(v)
    for trace, z in ((fig.data[3], qc.Z_P90), (fig.data[4], qc.Z_P99)):
        slope = trace.y[1] / trace.x[1]
        assert slope == pytest.approx(qc.coeficiente_th(z, 20.0))
    assert fig.data[3].name == "Línea 90, P = 20 %"


def test_los_pares_con_media_no_positiva_no_se_dibujan_y_se_dice():
    v = dup(dup_fuente=qcalc.DUP_FUENTES[1])
    fig = qg.th_figure(v)
    assert v.th.sin_media == 13
    assert sum(len(fig.data[i].x) for i in range(3)) == 91
    assert "13 pares con media no positiva no se dibujan" in fig.layout.annotations[0].text


def test_la_curva_de_diferencias_es_la_ordenada_del_calculo_y_el_umbral_el_de_su_tipo():
    for tipo, umbral in (("Duplicado de campo", 20.0), ("Pulpa", 10.0)):
        v = dup(dup_tipo=tipo)
        fig = qg.rpd_figure(v)
        assert list(fig.data[0].y) == sorted(r for r in v.rpd if r is not None)
        assert list(fig.data[1].y) == [umbral, umbral]
        assert list(fig.data[2].x) == [80.0, 80.0]
        assert f"{v.dup.pct_bajo:.1f}".replace(".", ",") in fig.layout.annotations[0].text


# ------------------------------------------------------------------ blancos y certificación
def test_los_blancos_se_clasifican_como_en_el_calculo():
    for pico in (0.0, 4.0, 12.0):
        v = qcalc.run_blk(qcalc.QaqcParams(pico=pico))
        fig = qg.blk_figure(v)
        assert [len(fig.data[i].x) for i in range(3)] == [
            v.res.n - v.res.n_sobre_3,
            v.res.n_sobre_3 - v.res.n_sobre_10,
            v.res.n_sobre_10,
        ]
        ys = {round(d.y[0], 9) for d in fig.data[3:]}
        assert ys == {round(x, 9) for x in (v.res.ld, 3 * v.res.ld, 10 * v.res.ld)}


def test_la_serie_de_blancos_sintetica_lleva_el_pico_donde_se_dice():
    v = qcalc.run_blk(qcalc.QaqcParams(pico=12.0, n=30))
    assert v.valores[int(0.7 * 30)] == pytest.approx(12.0 * 0.005)
    sin = qcalc.run_blk(qcalc.QaqcParams(pico=0.0, n=30))
    assert max(sin.valores) <= 1.5 * 0.005 + 1e-9 and sin.res.veredicto == qc.BLANCO_OK


def test_el_histograma_de_cdn_lleva_los_150_resultados_y_las_lineas_del_calculo():
    v = qcalc.run_cert()
    fig = qg.cert_figure(v)
    keep, drop = list(fig.data[0].x), list(fig.data[1].x)
    assert len(keep) == 143 and len(drop) == 7 and sorted(keep + drop) == sorted(v.resultados)
    c = v.cert
    xs = [d.x[0] for d in fig.data[2:]]
    assert xs == pytest.approx([c.media, c.media - c.dos_sd, c.media + c.dos_sd, c.bajo, c.alto])
    assert all(c.bajo <= x <= c.alto for x in keep) and all(
        not (c.bajo <= x <= c.alto) for x in drop
    )


# ------------------------------------------------------------------ idiomas
def _figures(lang: str):
    with i18n.use(lang):
        return [
            qg.crm_figure(con_rechazo()),
            qg.th_figure(dup()),
            qg.rpd_figure(dup()),
            qg.blk_figure(qcalc.run_blk(qcalc.QaqcParams())),
            qg.cert_figure(qcalc.run_cert()),
        ]


def test_los_graficos_en_ingles_no_llevan_espanol():
    blob = " ".join(json.dumps(f.to_plotly_json(), ensure_ascii=False) for f in _figures("en"))
    texts = re.findall(r'"(?:text|title|name|label)": "([^"]+)"', blob)
    texts += re.findall(r'"title": \{"text": "([^"]+)"', blob)
    assert texts and not [x for x in texts if SPANISH.search(x)], [
        x for x in texts if SPANISH.search(x)
    ][:5]
    assert "Play" in blob and "Pause" in blob and "Reproducir" not in blob


def test_los_graficos_en_espanol_siguen_en_espanol_y_las_cifras_no_cambian():
    es_ = [json.dumps(f.to_plotly_json(), ensure_ascii=False) for f in _figures("es")]
    en = [json.dumps(f.to_plotly_json(), ensure_ascii=False) for f in _figures("en")]
    assert "Reproducir" in es_[0] and "Pausa" in es_[0]
    # los datos numéricos de cada trazo son idénticos en los dos idiomas
    for a, b in zip(_figures("es"), _figures("en"), strict=True):
        for ta, tb in zip(a.data, b.data, strict=True):
            assert list(ta.x if ta.x is not None else []) == list(tb.x if tb.x is not None else [])
            assert list(ta.y if ta.y is not None else []) == list(tb.y if tb.y is not None else [])
    assert len(es_) == len(en) == 5


# ------------------------------------------------------------------ lo que se calcula aparte
def test_la_diferencia_relativa_de_cada_par_es_200_por_la_diferencia_entre_la_suma():
    v = dup()
    for (a, b), r in zip(v.pares, v.rpd, strict=True):
        assert r == pytest.approx(200 * abs(a - b) / (a + b))
    figura = qg.rpd_figure(v).data[0].y
    assert max(figura) == pytest.approx(max(200 * abs(a - b) / (a + b) for a, b in v.pares))


def test_la_coincidencia_con_lo_publicado_es_al_redondeo_de_3_decimales():
    c = qcalc.run_cert().cert
    assert qcalc.coincide(c, (2.388, 0.232))
    assert not qcalc.coincide(c, (2.389, 0.232)) and not qcalc.coincide(c, (2.388, 0.233))
    assert not qcalc.coincide(c, (2.37, 0.232))
