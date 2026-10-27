"""Componentes compartidos por las pestañas de cálculo: indicadores en filas de 3, el panel «Estado
de la operación» (una línea por chequeo, con el nivel escrito y en color, y su fuente en la ayuda),
«Prueba esto» (experimentos cuyo texto lleva números calculados en vivo, con un botón que los aplica
a los controles) y «Casos publicados» (botones que cargan un caso de la literatura y el valor
publicado junto al calculado, con su Δ).

Nada de lo que escribe el visitante entra aquí: solo textos de diccionarios fijos y números."""

from __future__ import annotations

from dataclasses import dataclass, field

import streamlit as st
from controles import BY_KEY, PREFIX
from i18n import current, opt, t

NIVELES = ("ok", "aviso", "mal")
COLORES = {"ok": "green", "aviso": "orange", "mal": "red"}
POR_FILA = 3


@dataclass(frozen=True)
class Fila:
    """Un chequeo ya traducido: su nivel, la línea con sus números y la fuente o criterio."""

    nivel: str
    texto: str
    ayuda: str = ""

    def __post_init__(self) -> None:
        if self.nivel not in NIVELES:
            raise ValueError(f"Nivel desconocido {self.nivel!r}")


@dataclass(frozen=True)
class Prueba:
    """Un experimento: título y texto ya traducidos, y los valores que el botón fija en los
    controles (clave de la sesión → valor)."""

    clave: str
    titulo: str
    texto: str
    cambios: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Experimento:
    """Un cambio al ejemplo, en términos del modelo. `ctl`: dato → valor del modelo que fija el
    botón; `mod`: lo mismo para el cálculo; `direcciones`: magnitud → +1 sube / −1 baja; `nivel`:
    el peor nivel del panel tras el cambio (None: el texto no lo afirma)."""

    clave: str
    ctl: dict[str, object]
    mod: dict[str, object]
    direcciones: dict[str, int]
    nivel: str | None = None


@dataclass(frozen=True)
class Caso:
    """Un caso publicado: su título ya traducido y los valores que el botón fija."""

    clave: str
    titulo: str
    cambios: dict[str, object] = field(default_factory=dict)


def cientifico(x: float) -> str:
    """Notación científica con el separador decimal del idioma."""
    out = f"{x:.1e}"
    return out.replace(".", ",") if current() == "es" else out


def etiqueta(nivel: str) -> str:
    return t("estado.nivel." + nivel)


def linea(f: Fila) -> str:
    """La línea Markdown de un chequeo: el nivel va escrito y en color, no solo en color."""
    return f":{COLORES[f.nivel]}-badge[{etiqueta(f.nivel)}] {f.texto}"


def _mostrar(f: Fila) -> None:
    st.markdown(linea(f), help=f.ayuda or None)


def indicadores(items: list[tuple[str, str, str]]) -> None:
    """Indicadores en filas de 3: (rótulo corto, valor, ayuda con el nombre completo)."""
    for i in range(0, len(items), POR_FILA):
        cols = st.columns(POR_FILA)
        for col, (rotulo, valor, ayuda) in zip(cols, items[i : i + POR_FILA], strict=False):
            col.metric(rotulo, valor, help=ayuda)


def peor(filas: list[Fila]) -> str:
    if any(f.nivel == "mal" for f in filas):
        return "mal"
    return "aviso" if any(f.nivel != "ok" for f in filas) else "ok"


def panel(filas: list[Fila]) -> str:
    """Dibuja el panel. Los chequeos con aviso o problema van uno por línea; los que están en rango
    se agrupan (y si todos lo están, una sola línea). Devuelve el peor nivel."""
    fuera = [f for f in filas if f.nivel != "ok"]
    dentro = [f for f in filas if f.nivel == "ok"]
    for f in fuera:
        _mostrar(f)
    if not fuera:
        st.markdown(f":green-badge[{etiqueta('ok')}] {t('estado.todo_ok')}")
    if dentro:
        with st.expander(t("estado.ver1") if len(dentro) == 1 else t("estado.ver", n=len(dentro))):
            for f in dentro:
                _mostrar(f)
    return peor(filas)


def controles_de(cambios: dict[str, object]) -> dict[str, object]:
    """Clave del dato → valor del modelo (p. ej. «PREP-31B»), a clave de la sesión → valor del
    widget: las listas guardan el rótulo del idioma actual."""
    out: dict[str, object] = {}
    for key, value in cambios.items():
        d = BY_KEY[key]
        out[PREFIX + key] = opt(str(value)) if d.widget == "select" else value
    return out


def aplicar(cambios: dict[str, object]) -> None:
    """Fija los controles (se llama como `on_click`, antes de que el script vuelva a correr)."""
    for k, v in cambios.items():
        st.session_state[k] = v


def pruebas(items: list[Prueba], prefijo: str, restablecer=None) -> None:
    """Dibuja los experimentos. `restablecer` (opcional) es el `on_click` del botón que vuelve al
    ejemplo."""
    st.markdown(t("prueba.h"))
    st.markdown(t("prueba.intro"))
    for p in items:
        with st.container(border=True):
            st.markdown(f"**{p.titulo}.** {p.texto}")
            st.button(
                t("prueba.aplicar"),
                key=f"{prefijo}prueba_{p.clave}",
                on_click=aplicar,
                args=(p.cambios,),
            )
    if restablecer is not None:
        st.button(t("prueba.restablecer"), key=f"{prefijo}prueba_reset", on_click=restablecer)


def casos(items: list[Caso], prefijo: str, activo: str | None) -> None:
    """Dibuja los botones de los casos publicados (en un expander que se abre si hay uno activo)."""
    with st.expander(t("caso.h"), expanded=activo is not None):
        st.markdown(t("caso.intro"))
        for c in items:
            marca = t("caso.activo") if c.clave == activo else ""
            st.button(
                f"{c.titulo}{marca}",
                key=f"{prefijo}caso_{c.clave}",
                on_click=aplicar,
                args=(c.cambios,),
            )


def delta(calculado: float, publicado: float) -> float:
    """Δ = calculado − publicado."""
    return calculado - publicado
