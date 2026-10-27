"""«Estado de la operación», «Casos publicados» y «Prueba esto» de la pestaña Fusión. Los chequeos
son los avisos que el modelo ya emite (`muestreo.fusion_avisos` y `muestreo.crisol`, cada uno con su
cita: Bugbee 1922, USGS Bulletin 1445, Lodge y Perkins citados por Bugbee), más su contraparte «en
rango» con los números de la carga; los umbrales rotulados «umbral supuesto» en el modelo siguen
rotulados así. Los experimentos parten del ejemplo de la barra lateral (los valores por defecto de
`controles.DATOS`) y llevan números calculados en vivo."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from functools import lru_cache

import pandas as pd
import streamlit as st
from calculo import FUSION_SAMPLE_G, FUSION_SAMPLES, FusionUIParams, FusionView, run_fusion
from controles import reset_to_example
from dibujo import es
from estado import Caso, Experimento, Fila, Prueba, casos, controles_de, panel, peor, pruebas
from i18n import decimal, num_g, t, tm, use

from muestreo import fusion
from muestreo import fusion_datos as fd
from muestreo.crisol import CRUCIBLE, DRY_BULK_DENSITY
from muestreo.fusion_avisos import (
    ACTIVE_FLUX_RATIO,
    BUTTON_RANGE,
    COPPER_INCREASE_PCT,
    Warning,
)

BUTTON_CODES = ("button_low", "button_high")  # los cubre la fila del botón
# los avisos del modelo, por la condición que cada fila resume
GRUPOS = {
    "escoria": ("slag_basic", "slag_acid"),
    "fundente": ("active_flux",),
    "crisol": (
        "dry_over_capacity",
        "melt_over_capacity",
        "dry_over_two_thirds",
        "melt_over_two_thirds",
    ),
    "cobre": ("copper", "perkins"),
    "reductor": ("reductant_excess",),
    "lodge": ("lodge_excess",),
}
# cómo se muestra cada número de un aviso: «g» = el menor número de cifras; si no, los decimales
_G_FIELDS = {"lo", "hi", "ratio", "limit", "density"}
_DECIMALS = {"degree": 2, "button": 1, "copper": 1}  # el resto, sin decimales


def warning_text(w: Warning) -> tuple[str, str]:
    """(texto, cita) de un aviso del modelo, en el idioma de la app, con sus números."""
    args = {k: num_g(v) if k in _G_FIELDS else es(v, _DECIMALS.get(k, 0)) for k, v in w.args}
    source_key = w.code.replace("dry_", "").replace("melt_", "")
    if source_key in ("over_capacity", "over_two_thirds"):
        source = t(f"warn.{source_key}.source")
    else:
        source = t(f"warn.{w.code}.source", **args)
    return t(f"warn.{w.code}.text", **args), source


def _nivel(w: Warning) -> str:
    return "mal" if w.level == "riesgo" else "aviso"


def _fila_aviso(w: Warning) -> Fila:
    text, source = warning_text(w)
    return Fila(_nivel(w), text, source)


def _activo_g(view: FusionView) -> float:
    """Fundente activo (g): soda, bórax y el litargirio que queda libre en la escoria."""
    u = view.used
    return u.soda_g + u.borax_g + view.result.slag.components_g.get("PbO", 0.0)


def filas_fusion(view: FusionView, f: FusionUIParams) -> list[Fila]:
    """Los chequeos del panel de la pestaña Fusión."""
    r = view.result
    lo, hi = BUTTON_RANGE
    filas: list[Fila] = []
    if lo <= r.button_g <= hi:
        filas.append(
            Fila(
                "ok",
                t("fe.chk.boton.ok", button=es(r.button_g, 1), lo=es(lo, 0), hi=es(hi, 0)),
                t("fe.src.boton"),
            )
        )
    else:
        filas.append(
            Fila(
                "aviso",
                t("f.warn.range", button=es(r.button_g, 1), lo=es(lo, 0), hi=es(hi, 0)),
                t("fe.src.boton"),
            )
        )
    por_codigo = {w.code: w for w in r.warnings}
    dry_cm3 = r.dry_charge_g / DRY_BULK_DENSITY
    ok = {
        "escoria": t("fe.chk.escoria.ok", degree=es(r.slag.degree, 2), label=tm(r.slag.label)),
        "fundente": t(
            "fe.chk.fundente.ok",
            active=es(_activo_g(view), 0),
            ratio=es(_activo_g(view) / f_sample_g(f), 1),
            min=num_g(ACTIVE_FLUX_RATIO),
        ),
        "crisol": t(
            "fe.chk.crisol.ok",
            dry=es(dry_cm3, 0),
            melt=es(r.lead_hot_cm3 + r.slag_cm3, 0),
            lim=es(CRUCIBLE.fill_limit_cm3, 0),
            cap=es(CRUCIBLE.capacity_cm3, 0),
        ),
        "cobre": t("fe.chk.cobre.ok", copper=es(r.copper_pct, 1), lim=num_g(COPPER_INCREASE_PCT)),
        "reductor": t("fe.chk.reductor.ok"),
        "lodge": t("fe.chk.lodge.ok"),
    }
    for grupo, codigos in GRUPOS.items():
        disparados = [por_codigo[c] for c in codigos if c in por_codigo]
        if disparados:
            filas += [_fila_aviso(w) for w in disparados]
        elif grupo != "lodge" or r.sulfur_mol > 0:
            filas.append(Fila("ok", ok[grupo], t(f"fe.src.{grupo}")))
    cubiertos = {c for codigos in GRUPOS.values() for c in codigos} | set(BUTTON_CODES)
    filas += [_fila_aviso(w) for w in r.warnings if w.code not in cubiertos]
    return filas


def f_sample_g(f: FusionUIParams) -> float:
    return FUSION_SAMPLE_G[f.sample]


# ------------------------------------------------------------------ el caso publicado
AT_G = fusion.AT_G
SODA_LITARGIRIO_G = 30.0  # g de soda y de PbO para la escoria por assay-ton (`fusion_pesos.design`)
# (clave, etiqueta de la comprobación en fusion_datos, minerales en %)
CASOS = (
    ("bugbee50", "50 % CaCO3", {"cuarzo": 50.0, "calcita": 50.0}),
    ("bugbee100", "CaCO3 puro", {"calcita": 100.0}),
)
REACTIVOS = (
    ("borax", "bórax vidrio", "r.borax"),
    ("silica", "sílice", "r.silica"),
    ("litharge", "litargirio", "r.litharge"),
)


def parametros_caso(minerales: dict[str, float]) -> FusionUIParams:
    """Los controles del ejemplo de Bugbee: 1 assay-ton, botón de 28 g, bi-silicato, harina de
    R.P. 12 y 30 g de soda y de litargirio de escoria por assay-ton, sin cambios a la carga."""
    return FusionUIParams(
        sample=FUSION_SAMPLES[0],
        minerals=tuple((m.key, minerales.get(m.key, 0.0)) for m in fusion.MINERALS),
        sulfur="SO3",
        button_g=28.0,
        degree="bi",
        flour_rp=12.0,
        soda_per_g=SODA_LITARGIRIO_G / AT_G,
        litharge_per_g=SODA_LITARGIRIO_G / AT_G,
        x_flour=1.0,
        x_silica=1.0,
        x_litharge=1.0,
    )


def _controles_caso(p: FusionUIParams) -> dict[str, object]:
    ctl: dict[str, object] = {"f_sample": p.sample, "f_sulfur": p.sulfur, "f_degree": "bi"}
    ctl.update({"m_" + k: v for k, v in p.minerals})
    ctl.update(
        f_button=p.button_g,
        f_flour=p.flour_rp,
        f_soda=p.soda_per_g,
        f_lith=p.litharge_per_g,
        x_flour=p.x_flour,
        x_silica=p.x_silica,
        x_lith=p.x_litharge,
    )
    return ctl


def casos_fusion() -> list[Caso]:
    return [
        Caso(k, t(f"fe.caso.{k}"), controles_de(_controles_caso(parametros_caso(m))))
        for k, _, m in CASOS
    ]


def caso_activo(f: FusionUIParams) -> str | None:
    """El caso de Bugbee que los controles tienen puesto (la harina y el nitro no cuentan: el
    nitro no entra en un ejemplo sin sulfuros)."""
    for clave, _, minerales in CASOS:
        e = parametros_caso(minerales)
        mismo = (
            f.sample == e.sample
            and f.minerals == e.minerals
            and f.sulfur == e.sulfur
            and f.degree == e.degree
            and f.x_flour == e.x_flour
            and f.x_silica == e.x_silica
            and f.x_litharge == e.x_litharge
            and all(
                math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
                for a, b in (
                    (f.button_g, e.button_g),
                    (f.flour_rp, e.flour_rp),
                    (f.soda_per_g, e.soda_per_g),
                    (f.litharge_per_g, e.litharge_per_g),
                )
            )
        )
        if mismo:
            return clave
    return None


def publicado(etiqueta: str, reactivo: str) -> fd.FusionCheck:
    """La comprobación de la validación (Bugbee 1922, ejemplos resueltos) de un reactivo."""
    item = f"{etiqueta}: carga calculada, {reactivo}"
    return next(c for c in fd.example_checks() if c.item == item)


def comparar_publicado(view: FusionView, clave: str) -> None:
    etiqueta = next(e for k, e, _ in CASOS if k == clave)
    d = view.designed
    calc = {"borax": d.borax_g, "silica": d.silica_g, "litharge": d.litharge_g}
    rows = []
    for key, nombre, texto in REACTIVOS:
        c = publicado(etiqueta, nombre)
        rows.append((t(texto), c.published, calc[key], t("verdict." + c.fit)))
    table = pd.DataFrame(
        {
            t("f.col.reagent"): [r[0] for r in rows],
            t("caso.col.pub"): [decimal(r[1]) for r in rows],
            t("caso.col.calc"): [decimal(round(r[2], 3)) for r in rows],
            t("caso.col.delta"): [decimal(round(r[2] - r[1], 3) + 0.0) for r in rows],
            t("fv.col.verdict"): [r[3] for r in rows],
        }
    )
    st.markdown(t("fe.caso.res", caso=etiqueta))
    st.dataframe(table, hide_index=True)


# ------------------------------------------------------------------ prueba esto
@dataclass(frozen=True)
class ResFus:
    boton: float  # g
    escoria: float  # g
    grado: float
    litargirio: float  # g
    polvo: float  # cm³ de la carga en polvo
    nivel: str


def evaluar_fus(**mod: object) -> ResFus:
    f = replace(FusionUIParams(), **mod)  # type: ignore[arg-type]
    view = run_fusion(f)
    r = view.result
    with use("es"):
        nivel = peor(filas_fusion(view, f))
    return ResFus(
        r.button_g,
        r.slag.mass_g,
        r.slag.degree,
        view.used.litharge_g,
        r.dry_charge_g / DRY_BULK_DENSITY,
        nivel,
    )


EXPERIMENTOS_FUS: tuple[Experimento, ...] = (
    Experimento("harina", {"x_flour": 0.0}, {"x_flour": 0.0}, {"boton": -1}, "aviso"),
    Experimento(
        "litargirio",
        {"x_lith": 0.6},
        {"x_litharge": 0.6},
        {"grado": +1, "escoria": -1, "boton": 0},
        "aviso",
    ),
    Experimento(
        "mono",
        {"f_degree": "mono"},
        {"degree": "mono"},
        {"grado": -1, "escoria": +1, "polvo": +1},
        "aviso",
    ),
)


@lru_cache(maxsize=1)
def pares_fus() -> tuple[tuple[Experimento, ResFus, ResFus], ...]:
    base = evaluar_fus()
    return tuple((e, base, evaluar_fus(**e.mod)) for e in EXPERIMENTOS_FUS)


def numeros_fus(a: ResFus, b: ResFus) -> dict[str, str]:
    lo, hi = BUTTON_RANGE
    return {
        "b0": es(a.boton, 1),
        "b1": es(b.boton, 1),
        "s0": es(a.escoria, 1),
        "s1": es(b.escoria, 1),
        "d0": es(a.grado, 2),
        "d1": es(b.grado, 2),
        "l0": es(a.litargirio, 1),
        "l1": es(b.litargirio, 1),
        "p0": es(a.polvo, 0),
        "p1": es(b.polvo, 0),
        "lim": es(CRUCIBLE.fill_limit_cm3, 0),
        "cap": es(CRUCIBLE.capacity_cm3, 0),
        "lo": es(lo, 0),
        "hi": es(hi, 0),
        "x": es(60, 0),
        "ratio": num_g(ACTIVE_FLUX_RATIO),
    }


def pruebas_fus() -> list[Prueba]:
    return [
        Prueba(
            e.clave,
            t(f"fe.exp.{e.clave}.titulo"),
            t(f"fe.exp.{e.clave}.texto", **numeros_fus(a, b)),
            controles_de(e.ctl),
        )
        for e, a, b in pares_fus()
    ]


def prueba_fusion() -> None:
    pruebas(pruebas_fus(), "fus_", reset_to_example)


def estado_fusion(view: FusionView, f: FusionUIParams) -> None:
    st.markdown(t("estado.h"))
    panel(filas_fusion(view, f))
    activo = caso_activo(f)
    casos(casos_fusion(), "fus_", activo)
    if activo:
        comparar_publicado(view, activo)
