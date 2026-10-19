"""Cada dato de entrada se define una sola vez: arma la barra lateral y la tabla «Qué datos
necesita» de la guía, así las dos no se pueden desfasar. Sus textos están en `textos_es_datos.py`
y `textos_en_datos.py`, con las claves `dato.<clave>.label|meaning|source`."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st
from calculo import (
    FUSION_DEFAULT_MINERALS,
    FUSION_DEGREES,
    FUSION_SAMPLES,
    MINERALS,
    FusionUIParams,
    GoldParams,
    MineralParams,
    ProtocolParams,
)
from cian_calculo import MODEL_LABELS, CianParams
from i18n import current, int_num, num_g, opt, t, tm, use

from muestreo import cianuracion as cia
from muestreo import fusion
from muestreo.protocolo import PRESETS

PREFIX = "dato_"
PROT, MIN, GOLD, FUS = "Protocolo", "Mineral", "Oro grueso", "Fusión"
CIA = "Cianuración"
ALIQUOTS = ("30", "50")  # Au-AA23 y Au-AA24
SHAPES = ("esfera", "cubo")


def _tx(text: str) -> str:
    """El texto de una clave de `textos_*`; si no es una clave, el propio texto."""
    try:
        return t(text)
    except KeyError:
        return text


@dataclass(frozen=True)
class Dato:
    group: str
    key: str
    label_k: str
    unit: str
    lo: float
    hi: float
    default: float | bool | str
    step: float
    meaning_k: str
    source_k: str
    widget: str = "number"  # number | select | check
    options: tuple[str, ...] = ()
    mineral: str = ""  # clave del mineral de la fusión: el rótulo es su nombre y su fórmula

    @property
    def label(self) -> str:
        if self.mineral:
            m = fusion.BY_KEY[self.mineral]
            return f"{tm(m.name)} ({m.formula})"
        return _tx(self.label_k)

    @property
    def meaning(self) -> str:
        return _tx(self.meaning_k)

    @property
    def source(self) -> str:
        return _tx(self.source_k)

    @property
    def range_text(self) -> str:
        if self.widget == "select":
            return t("dato.or").join(opt(o) for o in self.options)
        if self.widget == "check":
            return t("yesno")
        return t("dato.range", lo=_num(self.lo), hi=_num(self.hi))

    @property
    def default_text(self) -> str:
        if self.widget == "check":
            return t("yes") if self.default else t("no")
        return opt(self.default) if isinstance(self.default, str) else _num(self.default)

    @property
    def help(self) -> str:
        unit = f" ({self.unit})" if self.unit else ""
        return t("dato.help", meaning=self.meaning, unit=unit, range=self.range_text,
                 source=self.source)  # fmt: skip


def _num(x: float) -> str:
    """Número en el formato del idioma: «1 000», «2,7» (es) o «1,000», «2.7» (en)."""
    return int_num(x) if float(x).is_integer() else num_g(x)


DATOS: tuple[Dato, ...] = (
    Dato(PROT, "preset", "dato.preset.label", "", 0, 0, PRESETS[0], 0,
         "dato.preset.meaning", "dato.preset.source", widget="select", options=PRESETS),
    Dato(PROT, "aliquot", "dato.aliquot.label", "", 0, 0, "30", 0,
         "dato.aliquot.meaning", "dato.aliquot.source", widget="select", options=ALIQUOTS),
    Dato(PROT, "lot", "dato.lot.label", "g", 500, 20000, 3000, 100,
         "dato.lot.meaning", "dato.lot.source"),
    Dato(PROT, "d_n0", "dato.d_n0.label", "cm", 1, 15, 5, 0.5,
         "dato.d_n0.meaning", "dato.d_n0.source"),
    Dato(PROT, "m", "dato.m.label", "", 0.5, 3.0, 1.0, 0.1,
         "dato.m.meaning", "dato.m.source"),
    Dato(PROT, "safety", "dato.safety.label", "%", 1, 50, 10, 1,
         "dato.safety.meaning", "dato.safety.source"),
    Dato(PROT, "lot_correction", "dato.lot_correction.label", "", 0, 1, True, 0,
         "dato.lot_correction.meaning", "dato.lot_correction.source", widget="check"),
    Dato(MIN, "form", "dato.form.label", "", 0, 0, MINERALS[0], 0,
         "dato.form.meaning", "dato.form.source", widget="select", options=MINERALS),
    Dato(MIN, "k", "dato.k.label", "", 0.01, 10000, 167.4, 1,
         "dato.k.meaning", "dato.k.source"),
    Dato(MIN, "alpha", "dato.alpha.label", "", 0.5, 3.0, 1.123, 0.01,
         "dato.alpha.meaning", "dato.alpha.source"),
    Dato(MIN, "grade", "dato.grade.label", "g/t", 0.1, 100, 3.84, 0.1,
         "dato.grade.meaning", "dato.grade.source"),
    Dato(MIN, "rho_m", "dato.rho_m.label", "g/cm³", 1, 20, 16, 0.1,
         "dato.rho_m.meaning", "dato.rho_m.source"),
    Dato(MIN, "rho_g", "dato.rho_g.label", "g/cm³", 2, 4, 2.75, 0.05,
         "dato.rho_g.meaning", "dato.rho_g.source"),
    Dato(MIN, "d_lib", "dato.d_lib.label", "µm", 10, 5000, 82, 1,
         "dato.d_lib.meaning", "dato.d_lib.source"),
    Dato(MIN, "f", "dato.f.label", "", 0.1, 1.0, 0.5, 0.05,
         "dato.f.meaning", "dato.f.source"),
    Dato(MIN, "g", "dato.g.label", "", 0.1, 1.0, 0.25, 0.05,
         "dato.g.meaning", "dato.g.source"),
    Dato(MIN, "b", "dato.b.label", "", 0.0, 3.0, 1.5, 0.1,
         "dato.b.meaning", "dato.b.source"),
    Dato(GOLD, "grain", "dato.grain.label", "µm", 10, 1000, 150, 10,
         "dato.grain.meaning", "dato.grain.source"),
    Dato(GOLD, "shape", "dato.shape.label", "", 0, 0, "esfera", 0,
         "dato.shape.meaning", "dato.shape.source", widget="select", options=SHAPES),
    Dato(FUS, "f_sample", "dato.f_sample.label", "", 0, 0, FUSION_SAMPLES[0], 0,
         "dato.f_sample.meaning", "dato.f_sample.source", widget="select", options=FUSION_SAMPLES),
    *(
        Dato(FUS, "m_" + m.key, "", "%", 0, 100, FUSION_DEFAULT_MINERALS.get(m.key, 0.0), 1,
             "dato.mineral.meaning", "dato.mineral.source", mineral=m.key)
        for m in fusion.MINERALS
    ),
    Dato(FUS, "f_sulfur", "dato.f_sulfur.label", "", 0, 0, "SO3", 0,
         "dato.f_sulfur.meaning", "dato.f_sulfur.source", widget="select",
         options=fusion.SULFUR_MODES),
    Dato(FUS, "f_button", "dato.f_button.label", "g", 20, 35, 28, 0.5,
         "dato.f_button.meaning", "dato.f_button.source"),
    Dato(FUS, "f_degree", "dato.f_degree.label", "", 0, 0, "bi", 0,
         "dato.f_degree.meaning", "dato.f_degree.source", widget="select", options=FUSION_DEGREES),
    Dato(FUS, "f_flour", "dato.f_flour.label", "g Pb/g", 8, 13, 11, 0.5,
         "dato.f_flour.meaning", "dato.f_flour.source"),
    Dato(FUS, "f_niter", "dato.f_niter.label", "g Pb/g", 3.0, 5.12, 4.1, 0.1,
         "dato.f_niter.meaning", "dato.f_niter.source"),
    Dato(FUS, "f_soda", "dato.f_soda.label", "g/g", 0.5, 3.0, 1.0, 0.1,
         "dato.f_soda.meaning", "dato.f_soda.source"),
    Dato(FUS, "f_lith", "dato.f_lith.label", "g/g", 0.5, 3.0, 1.4, 0.1,
         "dato.f_lith.meaning", "dato.f_lith.source"),
    Dato(FUS, "x_flour", "dato.x_flour.label", "×", 0, 2, 1, 0.1,
         "dato.x_flour.meaning", "dato.x_flour.source"),
    Dato(FUS, "x_silica", "dato.x_silica.label", "×", 0, 3, 1, 0.1,
         "dato.x_silica.meaning", "dato.x_silica.source"),
    Dato(FUS, "x_lith", "dato.x_lith.label", "×", 0.3, 2, 1, 0.05,
         "dato.x_lith.meaning", "dato.x_lith.source"),
    Dato(CIA, "c_model", "dato.c_model.label", "", 0, 0, next(iter(MODEL_LABELS)), 0,
         "dato.c_model.meaning", "dato.c_model.source", widget="select",
         options=tuple(MODEL_LABELS)),
    Dato(CIA, "c_head", "dato.c_head.label", "ppb", 100, 10000, cia.S0_PPB, 10,
         "dato.c_head.meaning", "dato.c_head.source"),
    Dato(CIA, "c_factor", "dato.c_factor.label", "ppb/ppb", 0.5, 5, cia.F_SOLUCION, 0.005,
         "dato.c_factor.meaning", "dato.c_factor.source"),
    Dato(CIA, "c_split", "dato.c_split.label", "h", 2, 30, cia.T_CORTE_H, 1,
         "dato.c_split.meaning", "dato.c_split.source"),
)  # fmt: skip
BY_KEY = {d.key: d for d in DATOS}
GROUPS = (PROT, MIN, GOLD, FUS, CIA)


def _ask(d: Dato) -> float | bool | str:
    key, label = PREFIX + d.key, f"{d.label} ({d.unit})" if d.unit else d.label
    sb = st  # dentro de `with sidebar.expander(...)`: st.* cae en el expander
    if d.widget == "select":
        labels = [opt(o) for o in d.options]  # el valor del modelo (en español) se rotula aquí
        chosen = sb.selectbox(label, labels, labels.index(opt(str(d.default))), key=key,
                              help=d.help)  # fmt: skip
        return d.options[labels.index(chosen)]
    if d.widget == "check":
        return sb.checkbox(label, value=bool(d.default), key=key, help=d.help)
    lo, hi, v, step = (float(x) for x in (d.lo, d.hi, d.default, d.step))
    return sb.number_input(label, lo, hi, v, step, help=d.help, key=key)


def _relabel_selects(previous: str) -> None:
    """Al cambiar de idioma, cada lista conserva su elección: se pasa del rótulo del idioma
    anterior al del idioma actual (el valor guardado en la sesión es el rótulo)."""
    for d in DATOS:
        key = PREFIX + d.key
        if d.widget != "select" or key not in st.session_state:
            continue
        for raw in d.options:
            with use(previous):
                old = opt(raw)
            if old == st.session_state[key]:
                st.session_state[key] = opt(raw)
                break


def reset_to_example() -> None:
    """Vuelve todos los datos al ejemplo."""
    for k in [k for k in st.session_state if str(k).startswith(PREFIX)]:
        del st.session_state[k]


def sidebar_config() -> tuple[
    ProtocolParams, MineralParams, GoldParams, float, FusionUIParams, CianParams
]:
    """Lee la barra lateral. Devuelve el protocolo, el mineral, el oro, la alícuota (g), la fusión
    y la cianuración."""
    sb = st.sidebar
    seen = st.session_state.get("_lang_seen")
    if seen and seen != current():
        _relabel_selects(seen)
    st.session_state["_lang_seen"] = current()
    sb.button(t("sidebar.example"), on_click=reset_to_example, width="stretch")
    v: dict[str, float | bool | str] = {}
    for group in GROUPS:
        with sb.expander(t("group." + group), expanded=group == PROT):
            for d in DATOS:
                if d.group == group:
                    v[d.key] = _ask(d)
    aliquot = float(v["aliquot"])
    protocol = ProtocolParams(
        str(v["preset"]),
        aliquot,
        float(v["lot"]),
        float(v["d_n0"]),
        float(v["m"]),
        float(v["safety"]),
        bool(v["lot_correction"]),
    )
    mineral = MineralParams(
        str(v["form"]),
        float(v["k"]),
        float(v["alpha"]),
        float(v["grade"]),
        float(v["rho_m"]),
        float(v["rho_g"]),
        float(v["d_lib"]),
        float(v["f"]),
        float(v["g"]),
        float(v["b"]),
    )
    gold = GoldParams(float(v["grain"]), str(v["shape"]))
    fusion_ui = FusionUIParams(
        str(v["f_sample"]),
        tuple((m.key, float(v["m_" + m.key])) for m in fusion.MINERALS),
        str(v["f_sulfur"]),
        float(v["f_button"]),
        str(v["f_degree"]),
        float(v["f_flour"]),
        float(v["f_niter"]),
        float(v["f_soda"]),
        float(v["f_lith"]),
        float(v["x_flour"]),
        float(v["x_silica"]),
        float(v["x_lith"]),
    )
    cian = CianParams(
        MODEL_LABELS[str(v["c_model"])], float(v["c_head"]), float(v["c_factor"]),
        float(v["c_split"]),
    )  # fmt: skip
    return protocol, mineral, gold, aliquot, fusion_ui, cian


def data_table(group: str | None = None) -> pd.DataFrame:
    """La tabla «Qué datos necesita», hecha de las mismas definiciones que la barra lateral."""
    rows = [
        {
            t("col.group"): t("group." + d.group),
            t("col.dato"): d.label,
            t("col.unit"): d.unit,
            t("col.range"): d.range_text,
            t("col.example"): d.default_text,
            t("col.what"): d.meaning,
            t("col.how"): d.source[0].upper() + d.source[1:],
        }
        for d in DATOS
        if group in (None, d.group)
    ]
    return pd.DataFrame(rows)
