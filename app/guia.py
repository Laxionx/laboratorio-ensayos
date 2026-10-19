"""Pestaña «Guía» y fichas de las pestañas de cálculo: qué es el error fundamental, qué dato pide
cada factor, qué se calibra y qué errores de muestreo NO se modelan. Los textos están en
`textos_es_guia.py` y `textos_en_guia.py`."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from controles import CIA, FUS, GOLD, MIN, PROT, SED, data_table
from i18n import current, t

REPO = "https://github.com/Laxionx/laboratorio-ensayos"
CONMINUCION = "https://simulador-conminucion-mtxoolyzuvvcxrq8rce3el.streamlit.app/"
PLANTA = "https://simulador-procesos-ntfmuyhlnqc9d73kkqljzk.streamlit.app/"

# cuántos «límites del modelo» tiene cada ficha
N_LIMITS = {"protocolo": 3, "oro": 2, "fusion": 5, "cianuracion": 4, "sedimentacion": 5}
N_REACTIONS, N_LIMITES = 4, 4
DATA_GROUPS = {
    "protocolo": (PROT, MIN),
    "oro": (GOLD, MIN),
    "fusion": (FUS,),
    "cianuracion": (CIA,),
    "sedimentacion": (SED,),
}


def minnitt_2007_note() -> str:
    return t("minnitt2007.note")


def markdown_table(df: pd.DataFrame) -> str:
    """Tabla en Markdown: el texto largo se ajusta a la columna en vez de cortarse."""

    def cell(v: object) -> str:
        return str(v).replace("|", "\\|").replace("\n", " ")

    head = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "\n".join("| " + " | ".join(cell(v) for v in row) + " |" for row in df.values)


def _app_link(url: str) -> str:
    """El enlace a otra app del autor, en el mismo idioma (`?lang=` solo vale es o en)."""
    return url + "?lang=en" if current() == "en" else url


def ficha(name: str) -> None:
    """Ficha de una pestaña, arriba de ella: qué hace, qué entra, qué sale, de quién sale."""
    st.markdown(t("ficha.label.hace", text=t(f"ficha.{name}.hace")))
    st.markdown(t("ficha.label.entra", text=t(f"ficha.{name}.entra")))
    st.markdown(t("ficha.label.sale", text=t(f"ficha.{name}.sale")))
    with st.expander(t("ficha.expander.datos")):
        for group in DATA_GROUPS[name]:
            st.markdown(f"**{t('group.' + group)}**")
            st.markdown(markdown_table(data_table(group).drop(columns=t("col.group"))))
    with st.expander(t("ficha.expander.limites")):
        for n in range(1, N_LIMITS[name] + 1):
            st.markdown(f"- {t(f'ficha.{name}.limit.{n}')}")
    st.caption(t("ficha.autores", text=t(f"ficha.{name}.autores")))


def guide_tab() -> None:
    st.markdown(t("guide.h.simula"))
    st.markdown(t("guide.simula"))
    st.markdown(t("guide.h.gy"))
    st.latex(r"\sigma^2 = c\,f\,g\,\ell\,d_N^3\left(\frac{1}{M_S} - \frac{1}{M_L}\right) = "
             r"K\,d_N^{\alpha}\left(\frac{1}{M_S} - \frac{1}{M_L}\right)")  # fmt: skip
    st.markdown(t("guide.gy"))
    st.markdown(t("guide.h.calibrar"))
    st.markdown(t("guide.calibrar"))
    st.markdown(t("guide.h.oro"))
    st.markdown(t("guide.oro"))
    st.markdown(t("guide.h.fusion"))
    st.markdown(t("guide.fusion.1"))
    for n in range(1, N_REACTIONS + 1):
        st.markdown(f"- {t(f'react.{n}')}")
    st.markdown(t("guide.fusion.2"))
    st.markdown(t("guide.h.cian"))
    st.markdown(t("guide.cian.1"))
    st.latex(r"R = \left(1 - \frac{S_t}{S_0}\right) \times 100")
    st.latex(r"L = 1 - 3(1-X)^{2/3} + 2(1-X)\qquad M = 1 - (1-X)^{1/3}")
    st.markdown(t("guide.cian.2"))
    st.markdown(t("guide.h.sed"))
    st.markdown(t("guide.sed.1"))
    st.latex(
        r"A = \frac{2000\,(F - D)}{24 \cdot 62{,}35 \cdot R}\qquad "
        r"A_u = \frac{t_u}{C_0 H_0}"
    )
    st.markdown(t("guide.sed.2"))
    st.markdown(t("guide.h.minnitt"))
    st.markdown(t("guide.minnitt", note=minnitt_2007_note()))
    st.markdown(t("guide.h.datos"))
    group_col = t("col.group")
    for group, rows in data_table().groupby(group_col, sort=False):
        st.markdown(f"**{group}**")
        st.markdown(markdown_table(rows.drop(columns=group_col)))
    st.markdown(t("guide.h.limites"))
    for n in range(1, N_LIMITES + 1):
        st.markdown(f"- {t(f'limits.{n}')}")
    st.markdown(t("guide.h.otras"))
    st.markdown(
        t("guide.otras", conminucion=_app_link(CONMINUCION), planta=_app_link(PLANTA), repo=REPO)
    )
