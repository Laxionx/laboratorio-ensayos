"""«Estado de la operación», «Casos publicados» y «Prueba esto» de las pestañas Protocolo y Oro
grueso. Solo chequeos de definición o con fuente ya citada en el repo: la línea de seguridad del
protocolo (el control «Error máximo por división»), las constantes K y α de Minnitt (2017), la
corrección por masa del lote (Tabla VIII de Minnitt la omite), el criterio de 20 partículas de
Clifton et al. (1969) y el rango de partículas con que la app valida las ecuaciones de Clifton
(Fig. 4, `validacion.CLIFTON_PUBLISHED`). Los experimentos parten del ejemplo de la barra lateral
(los valores por defecto de `controles.DATOS`) y llevan números calculados en vivo."""

from __future__ import annotations

import math
from dataclasses import dataclass, fields, replace
from functools import lru_cache

import pandas as pd
import streamlit as st
from calculo import (
    MINERALS,
    GoldParams,
    GoldView,
    MineralParams,
    ProtocolParams,
    ProtocolView,
    run_gold,
    run_protocol,
)
from controles import reset_to_example
from dibujo import es
from estado import Caso, Experimento, Fila, Prueba, casos, controles_de, panel, peor, pruebas
from i18n import decimal, num_g, opt, t, tm, use

from muestreo import validacion as val
from muestreo.oro import PARTICLES_CRITERION, SFA_MASS_G, SFA_SCREEN_UM, recommend_screen_fire_assay
from muestreo.protocolo import PRESETS, preset

GRADO_BASE, ALICUOTA_BASE = 3.84, 30.0  # ley y alícuota del ejemplo (`controles.DATOS`)
RANGO_CLIFTON = (min(val.CLIFTON_PUBLISHED), max(val.CLIFTON_PUBLISHED))  # partículas de la Fig. 4


def _pct(x: float, d: int = 1) -> str:
    return f"{es(100 * x, d)} %"


# ------------------------------------------------------------------ protocolo: el panel
def filas_protocolo(view: ProtocolView, p: ProtocolParams, mp: MineralParams) -> list[Fila]:
    """Los chequeos del panel de la pestaña Protocolo."""
    stages = view.result.stages
    pasan = view.meets_safety
    if pasan:
        seguridad = Fila(
            "ok",
            t(
                "prot.chk.seg.ok",
                n=len(stages),
                seg=es(p.safety_pct, 0),
                max=_pct(max(s.rsd for s in stages)),
            ),
            t("prot.crit.seg"),
        )
    else:
        malas = ", ".join(
            t("prot.chk.seg.una", n=i, rsd=_pct(s.rsd))
            for i, s in enumerate(stages, start=1)
            if s.variance > view.safety_variance
        )
        seguridad = Fila(
            "aviso",
            t("prot.chk.seg.mal", seg=es(p.safety_pct, 0), etapas=malas),
            t("prot.crit.seg"),
        )
    filas = [
        seguridad,
        Fila("ok", t("prot.chk.masas", n=len(stages)), t("prot.crit.masas")),
    ]
    if mp.form in (MINERALS[0], MINERALS[1]):
        filas.append(
            Fila(
                "aviso",
                t(
                    "prot.chk.kalpha.dado",
                    k=num_g(view.mineral.k or 0.0),
                    alpha=num_g(view.mineral.alpha or 0.0),
                ),
                t("prot.crit.kalpha"),
            )
        )
    elif mp.form == MINERALS[2]:
        filas.append(
            Fila(
                "ok",
                t("prot.chk.kalpha.propio", k=num_g(mp.k), alpha=num_g(mp.alpha)),
                t("prot.crit.kalpha"),
            )
        )
    if p.preset == PRESETS[2] and p.lot_correction:
        filas.append(Fila("aviso", t("prot.chk.lote"), t("prot.crit.lote")))
    return filas


# ------------------------------------------------------------------ protocolo: el caso publicado
CLAVE_MINNITT = "minnitt"


def casos_protocolo() -> list[Caso]:
    cambios = controles_de({"preset": PRESETS[2], "form": MINERALS[0], "lot_correction": False})
    return [Caso(CLAVE_MINNITT, t("prot.caso.minnitt"), cambios)]


def caso_activo(p: ProtocolParams, mp: MineralParams) -> str | None:
    """El caso de Minnitt (2017, Tabla VIII, DSA) está puesto en los controles: su protocolo, su
    mineral y sin corrección por masa del lote."""
    ok = p.preset == PRESETS[2] and mp.form == MINERALS[0] and not p.lot_correction
    return CLAVE_MINNITT if ok else None


def publicada(mass_out_g: float, d_n_cm: float) -> str | None:
    """La varianza impresa en la Tabla VIII (DSA) de la división con esa masa y ese dN."""
    for mass, d_n, printed in val.MINNITT_2017_ROWS["DSA"]:
        if abs(mass - mass_out_g) <= 1e-6 * mass and abs(d_n - d_n_cm) <= 1e-9:
            return printed
    return None


def filas_publicadas(view: ProtocolView) -> list[tuple[str, float, float]]:
    """(etapa, varianza publicada, varianza calculada) de las divisiones de la Tabla VIII."""
    out = []
    for s in view.result.stages:
        printed = publicada(s.mass_out_g, s.d_n_cm)
        if printed is not None:
            out.append((s.name, float(printed), s.variance))
    return out


def comparar_publicado(view: ProtocolView) -> None:
    rows = filas_publicadas(view)
    table = pd.DataFrame(
        {
            t("p.col.stage"): [tm(n) for n, _, _ in rows],
            t("caso.col.pub"): [decimal(pub) for _, pub, _ in rows],
            t("caso.col.calc"): [decimal(round(calc, 5)) for _, _, calc in rows],
            t("caso.col.delta"): [decimal(round(calc - pub, 5) + 0.0) for _, pub, calc in rows],
        }
    )
    st.markdown(t("prot.caso.res"))
    st.dataframe(table, hide_index=True)


# ------------------------------------------------------------------ protocolo: prueba esto
@dataclass(frozen=True)
class ResProt:
    rsd: float  # error total, %
    rsd1: float  # error de la etapa 1, %
    rsd_ult: float  # error de la última división, %
    parte1: float  # parte de la varianza de la etapa 1, %
    seguridad: bool
    nivel: str


def _separar(mod: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    campos = {f.name for f in fields(ProtocolParams)}
    return (
        {k: v for k, v in mod.items() if k in campos},
        {k: v for k, v in mod.items() if k not in campos},
    )


def evaluar_prot(**mod: object) -> ResProt:
    pm, mm = _separar(mod)
    p, mp = replace(ProtocolParams(), **pm), replace(MineralParams(), **mm)  # type: ignore[arg-type]
    view = run_protocol(p, mp)
    st_ = view.result.stages
    with use("es"):
        nivel = peor(filas_protocolo(view, p, mp))
    return ResProt(
        100 * view.result.rsd,
        100 * st_[0].rsd,
        100 * st_[-1].rsd,
        100 * st_[0].share,
        view.meets_safety,
        nivel,
    )


EXPERIMENTOS_PROT: tuple[Experimento, ...] = (
    Experimento(
        "division", {"preset": PRESETS[1]}, {"preset": PRESETS[1]}, {"rsd": -1, "rsd1": -1}, "aviso"
    ),
    Experimento(
        "alicuota",
        {"aliquot": "50"},
        {"aliquot_g": 50.0},
        {"rsd_ult": -1, "rsd": -1, "parte1": +1},
        "aviso",
    ),
    Experimento("lote", {"lot_correction": False}, {"lot_correction": False}, {"rsd": +1}, "aviso"),
)


@lru_cache(maxsize=1)
def pares_prot() -> tuple[tuple[Experimento, ResProt, ResProt], ...]:
    base = evaluar_prot()
    return tuple((e, base, evaluar_prot(**e.mod)) for e in EXPERIMENTOS_PROT)


def _masa_riffle(nombre: str) -> float:
    return preset(nombre, ProtocolParams().lot_g, ALICUOTA_BASE).stages[0].mass_out_g


def numeros_prot(a: ResProt, b: ResProt) -> dict[str, str]:
    p = ProtocolParams()
    return {
        "t0": es(a.rsd, 1),
        "t1": es(b.rsd, 1),
        "e0": es(a.rsd1, 1),
        "e1": es(b.rsd1, 1),
        "l0": es(a.rsd_ult, 1),
        "l1": es(b.rsd_ult, 1),
        "s0": es(a.parte1, 1),
        "s1": es(b.parte1, 1),
        "seg": es(p.safety_pct, 0),
        "m0": es(_masa_riffle(PRESETS[0]), 0),
        "m1": es(_masa_riffle(PRESETS[1]), 0),
        "a0": es(p.aliquot_g, 0),
        "a1": es(50.0, 0),
    }


def pruebas_prot() -> list[Prueba]:
    out = []
    for e, a, b in pares_prot():
        out.append(
            Prueba(
                e.clave,
                t(f"prot.exp.{e.clave}.titulo"),
                t(f"prot.exp.{e.clave}.texto", **numeros_prot(a, b)),
                controles_de(e.ctl),
            )
        )
    return out


def prueba_protocolo() -> None:
    pruebas(pruebas_prot(), "prot_", reset_to_example)


def estado_protocolo(view: ProtocolView, p: ProtocolParams, mp: MineralParams) -> None:
    st.markdown(t("estado.h"))
    panel(filas_protocolo(view, p, mp))
    activo = caso_activo(p, mp)
    casos(casos_protocolo(), "prot_", activo)
    if activo:
        comparar_publicado(view)


# ------------------------------------------------------------------ oro grueso: el panel
def filas_oro(view: GoldView) -> list[Fila]:
    """Los chequeos del panel de la pestaña Oro grueso."""
    lam = view.lam
    if recommend_screen_fire_assay(lam):
        criterio = Fila(
            "aviso",
            t(
                "g.sfa",
                lam=es(lam, 1),
                n=PARTICLES_CRITERION,
                mass=es(SFA_MASS_G, 0),
                screen=es(SFA_SCREEN_UM, 0),
            ),
            t("oro.crit.clifton", n=PARTICLES_CRITERION),
        )
    else:
        criterio = Fila(
            "ok",
            t("g.ok", lam=es(lam, 0), n=PARTICLES_CRITERION),
            t("oro.crit.clifton", n=PARTICLES_CRITERION),
        )
    lo, hi = RANGO_CLIFTON
    dentro = lo <= lam <= hi
    cobertura = Fila(
        "ok" if dentro else "aviso",
        t("oro.chk.fig4.ok" if dentro else "oro.chk.fig4.mal", lam=es(lam, 1), lo=lo, hi=hi),
        t("oro.crit.fig4", lo=lo, hi=hi),
    )
    return [criterio, cobertura]


# ------------------------------------------------------------------ oro grueso: prueba esto
@dataclass(frozen=True)
class ResOro:
    lam: float
    p0: float  # probabilidad de ningún grano, %
    mediana: float  # g/t
    nivel: str


def evaluar_oro(**mod: object) -> ResOro:
    gp = replace(GoldParams(), **{k: v for k, v in mod.items() if k in ("grain_um", "shape")})  # type: ignore[arg-type]
    aliquot = float(mod.get("aliquot_g", ALICUOTA_BASE))  # type: ignore[arg-type]
    view = run_gold(gp, GRADO_BASE, aliquot)
    with use("es"):
        nivel = peor(filas_oro(view))
    return ResOro(view.lam, 100 * math.exp(-view.lam), view.simulation.median_gpt, nivel)


EXPERIMENTOS_ORO: tuple[Experimento, ...] = (
    Experimento("grano100", {"grain": 100.0}, {"grain_um": 100.0}, {"lam": +1, "p0": -1}, "aviso"),
    Experimento("alicuota", {"aliquot": "50"}, {"aliquot_g": 50.0}, {"lam": +1, "p0": -1}, "aviso"),
    Experimento("grano50", {"grain": 50.0}, {"grain_um": 50.0}, {"lam": +1, "p0": -1}, "ok"),
)
GRANO_BASE_UM = GoldParams().grain_um


@lru_cache(maxsize=1)
def pares_oro() -> tuple[tuple[Experimento, ResOro, ResOro], ...]:
    base = evaluar_oro()
    return tuple((e, base, evaluar_oro(**e.mod)) for e in EXPERIMENTOS_ORO)


def numeros_oro(a: ResOro, b: ResOro) -> dict[str, str]:
    return {
        "lam0": es(a.lam, 1),
        "lam1": es(b.lam, 1),
        "p0": es(a.p0, 1),
        "p1": es(b.p0, 1),
        "med0": es(a.mediana, 2),
        "med1": es(b.mediana, 2),
        "n": str(PARTICLES_CRITERION),
        "g0": es(GRANO_BASE_UM, 0),
        "a0": es(ALICUOTA_BASE, 0),
        "ley": es(GRADO_BASE, 2),
        "g100": es(100, 0),
        "g50": es(50, 0),
        "a50": es(50, 0),
        "ratio": es(b.lam / a.lam, 2),
        "opt": opt("esfera"),
    }


def pruebas_oro() -> list[Prueba]:
    out = []
    for e, a, b in pares_oro():
        out.append(
            Prueba(
                e.clave,
                t(f"oro.exp.{e.clave}.titulo"),
                t(f"oro.exp.{e.clave}.texto", **numeros_oro(a, b)),
                controles_de(e.ctl),
            )
        )
    return out


def prueba_oro() -> None:
    pruebas(pruebas_oro(), "oro_", reset_to_example)


def estado_oro(view: GoldView) -> None:
    st.markdown(t("estado.h"))
    panel(filas_oro(view))
