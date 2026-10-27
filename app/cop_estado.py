"""«Estado de la operación», «Casos publicados» y «Prueba esto» de la pestaña Copelación. Los
chequeos son los rangos de las tablas de Bugbee (1922) en que se apoya el modelo (Tablas IX, X, XI
y XII: `copelacion_datos.py`), el aviso de que la pestaña Fusión no pudo dar el botón y el estado
de la partición (Bugbee p. 118, 121 y 122: `copelacion_datos.py`). Los casos publicados son las
Tablas IX y XII de Lodge, que el modelo reproduce en sus nudos. Los experimentos parten del ejemplo
de la barra lateral (los valores por defecto de `controles.DATOS`) y llevan números calculados en
vivo."""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache

import pandas as pd
import streamlit as st
from calculo import FusionUIParams
from controles import reset_to_example
from cop_calculo import FUENTES_PLOMO, MODOS, CopParams, CopView, boton_de_fusion, run_cop
from dibujo import es
from estado import Caso, Experimento, Fila, Prueba, casos, controles_de, panel, peor, pruebas
from i18n import decimal, t, use

from muestreo import copelacion as cp
from muestreo import copelacion_datos as cd

NIVEL_ESTADO = {"buena": "ok", "lenta": "aviso", "lamina": "aviso", "insuficiente": "mal"}


def range_text(code: str) -> str:
    """El texto del aviso de rango, con el rango de la tabla que se salió."""
    rango = {"temp": cp.T_AG_RANGO, "plomo": cp.PB_RANGO, "plata": cp.AG_RANGO}.get(code)
    if rango is None:
        return t(f"cp.warn.{code}", t0=es(cd.CONGELADO_C, 0), t1=es(cp.T_AU_RANGO[0], 0))
    return t(f"cp.warn.{code}", lo=es(rango[0], 0), hi=es(rango[1], 0))


def filas_cop(v: CopView) -> list[Fila]:
    """Los chequeos del panel de la pestaña Copelación."""
    r, avisos = v.res, v.res.avisos
    filas: list[Fila] = []
    if "congelado" in avisos or "temp" in avisos:
        code = "congelado" if "congelado" in avisos else "temp"
        filas.append(Fila("aviso", range_text(code), t("cp.src.temp")))
    else:
        filas.append(
            Fila(
                "ok",
                t(
                    "cp.chk.temp.ok",
                    temp=es(r.temp_c, 0),
                    lo=es(cp.T_AG_RANGO[0], 0),
                    hi=es(cp.T_AG_RANGO[1], 0),
                    alo=es(cp.T_AU_RANGO[0], 0),
                    ahi=es(cp.T_AU_RANGO[1], 0),
                ),
                t("cp.src.temp"),
            )
        )
    for code, valor, rango, fuente in (
        ("plomo", v.plomo_g, cp.PB_RANGO, "cp.src.plomo"),
        ("plata", r.plata_total_mg, cp.AG_RANGO, "cp.src.plata"),
    ):
        if code in avisos:
            filas.append(Fila("aviso", range_text(code), t(fuente)))
        else:
            filas.append(
                Fila(
                    "ok",
                    t(
                        f"cp.chk.{code}.ok",
                        value=es(valor, 1),
                        lo=es(rango[0], 0),
                        hi=es(rango[1], 0),
                    ),
                    t(fuente),
                )
            )
    if v.fusion_no_sirve:
        filas.append(Fila("aviso", t("cp.warn.fusion", pb=es(v.plomo_g, 1)), t("cp.src.fusion")))
    elif v.plomo_de_fusion:
        filas.append(Fila("ok", t("cp.chk.fusion.ok", pb=es(v.plomo_g, 1)), t("cp.src.fusion")))
    filas.append(
        Fila(
            NIVEL_ESTADO[r.estado],
            t(
                f"cp.enc.state.{r.estado}",
                ratio=es(r.razon_final, 1),
                min=es(cd.MINIMO_PARTIR, 0),
                rec=es(cd.RECOMENDADO_MIN, 0),
                low=es(cd.LINGOTE_RAZON[0], 0),
            ),
            t("cp.src.particion"),
        )
    )
    return filas


# ------------------------------------------------------------------ los casos publicados
@dataclass(frozen=True)
class CasoCop:
    clave: str
    temp_c: float


CASOS = (CasoCop("lodge925", 925.0), CasoCop("lodge1000", 1000.0))
PLOMO_TABLA_G, PLATA_TABLA_MG = cd.TABLA_IX[0][1], cd.TABLA_IX[0][0]  # 10 g de plomo, 200 mg


def _fila(tabla, temp_c: float):
    return next(r for r in tabla if r[2] == temp_c)


def parametros_caso(c: CasoCop) -> CopParams:
    """Plomo y plata de las tablas de Lodge; razón propia de 1 a 1 para que el encuarte no agregue
    plata (la tabla mide la pérdida de los 200 mg tal cual)."""
    return CopParams(c.temp_c, FUENTES_PLOMO[1], PLOMO_TABLA_G, 1.0, PLATA_TABLA_MG, MODOS[2], 1.0)


def casos_cop() -> list[Caso]:
    out = []
    for c in CASOS:
        p = parametros_caso(c)
        ctl = {
            "k_temp": p.temp_c,
            "k_pb_src": p.plomo_fuente,
            "k_pb": p.plomo_g,
            "k_au": p.oro_mg,
            "k_ag": p.plata_mg,
            "k_modo": p.modo,
            "k_razon": p.razon,
        }
        out.append(Caso(c.clave, t(f"cp.caso.{c.clave}"), controles_de(ctl)))
    return out


def caso_activo(p: CopParams, v: CopView) -> str | None:
    """El caso de Lodge que los controles tienen puesto: mismos datos y sin plata agregada."""
    for c in CASOS:
        e = parametros_caso(c)
        if (p.temp_c, p.plomo_fuente, p.plomo_g, p.plata_mg, p.modo, p.razon) == (
            e.temp_c,
            e.plomo_fuente,
            e.plomo_g,
            e.plata_mg,
            e.modo,
            e.razon,
        ) and v.res.plata_agregada_mg == 0.0:
            return c.clave
    return None


def comparar_publicado(v: CopView, clave: str) -> None:
    c = next(x for x in CASOS if x.clave == clave)
    ag_pub = _fila(cd.TABLA_IX, c.temp_c)[3]
    au_pub = _fila(cd.TABLA_XII, c.temp_c)[3]
    rows = [
        (t("cp.caso.ag", t=es(c.temp_c, 0)), ag_pub, v.res.perdida_ag.pct),
        (t("cp.caso.au", t=es(c.temp_c, 0)), au_pub, v.res.perdida_au.pct),
    ]
    table = pd.DataFrame(
        {
            t("cp.caso.col"): [r[0] for r in rows],
            t("caso.col.pub"): [decimal(r[1]) for r in rows],
            t("caso.col.calc"): [decimal(round(r[2], 3)) for r in rows],
            t("caso.col.delta"): [decimal(round(r[2] - r[1], 3) + 0.0) for r in rows],
        }
    )
    st.markdown(t("cp.caso.res"))
    st.dataframe(table, hide_index=True)


# ------------------------------------------------------------------ prueba esto
@dataclass(frozen=True)
class ResCop:
    perdida_ag: float  # %
    perdida_au: float  # %
    agregada: float  # mg
    razon_final: float
    estado: str
    avisos: tuple[str, ...]
    nivel: str


def evaluar_cop(**mod: object) -> ResCop:
    p = replace(CopParams(), **mod)  # type: ignore[arg-type]
    v = run_cop(p, boton_de_fusion(FusionUIParams()))
    r = v.res
    with use("es"):
        nivel = peor(filas_cop(v))
    return ResCop(
        r.perdida_ag.pct,
        r.perdida_au.pct,
        r.plata_agregada_mg,
        r.razon_final,
        r.estado,
        r.avisos,
        nivel,
    )


EXPERIMENTOS_COP: tuple[Experimento, ...] = (
    Experimento(
        "caliente",
        {"k_temp": 1000.0},
        {"temp_c": 1000.0},
        {"perdida_ag": +1, "perdida_au": +1, "agregada": +1},
        "aviso",
    ),
    Experimento("frio", {"k_temp": 700.0}, {"temp_c": 700.0}, {"perdida_ag": -1}, "aviso"),
    Experimento(
        "razon",
        {"k_modo": MODOS[2], "k_razon": 1.5},
        {"modo": MODOS[2], "razon": 1.5},
        {"agregada": -1, "razon_final": -1},
        "mal",
    ),
)


@lru_cache(maxsize=1)
def pares_cop() -> tuple[tuple[Experimento, ResCop, ResCop], ...]:
    base = evaluar_cop()
    return tuple((e, base, evaluar_cop(**e.mod)) for e in EXPERIMENTOS_COP)


def numeros_cop(a: ResCop, b: ResCop) -> dict[str, str]:
    p = CopParams()
    return {
        "ag0": es(a.perdida_ag, 2),
        "ag1": es(b.perdida_ag, 2),
        "au0": es(a.perdida_au, 2),
        "au1": es(b.perdida_au, 2),
        "add0": es(a.agregada, 2),
        "add1": es(b.agregada, 2),
        "r0": es(a.razon_final, 1),
        "r1": es(b.razon_final, 1),
        "t0": es(p.temp_c, 0),
        "t1": es(1000, 0),
        "t700": es(cd.CONGELADO_C, 0),
        "t775": es(cp.T_AU_RANGO[0], 0),
        "min": es(cd.MINIMO_PARTIR, 0),
        "low": es(cd.LINGOTE_RAZON[0], 0),
        "razon": es(1.5, 1),
    }


def pruebas_cop() -> list[Prueba]:
    return [
        Prueba(
            e.clave,
            t(f"cp.exp.{e.clave}.titulo"),
            t(f"cp.exp.{e.clave}.texto", **numeros_cop(a, b)),
            controles_de(e.ctl),
        )
        for e, a, b in pares_cop()
    ]


def prueba_cop() -> None:
    pruebas(pruebas_cop(), "cop_", reset_to_example)


def estado_cop(v: CopView) -> None:
    st.markdown(t("estado.h"))
    panel(filas_cop(v))
    activo = caso_activo(v.params, v)
    casos(casos_cop(), "cop_", activo)
    if activo:
        comparar_publicado(v, activo)
