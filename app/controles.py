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
from cop_calculo import FUENTES_PLOMO, CopParams
from cop_calculo import MODOS as COP_MODOS
from i18n import current, int_num, num_g, opt, t, tm, use
from qaqc_calculo import (
    CRMS,
    DUP_FUENTES,
    DUP_TIPOS,
    N_RANGO,
    PRECISIONES,
    QaqcParams,
)
from qaqc_calculo import FUENTES as QC_FUENTES
from sed_calculo import COMPRESIONES, FACTORES, FUENTES, MODOS, SedParams

from muestreo import cianuracion as cia
from muestreo import fusion
from muestreo.protocolo import PRESETS

PREFIX = "dato_"
PROT, MIN, GOLD, FUS = "Protocolo", "Mineral", "Oro grueso", "Fusión"
CIA = "Cianuración"
SED = "Sedimentación"
COP = "Copelación"
QC = "Control de calidad"
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
    Dato(SED, "s_fuente", "dato.s_fuente.label", "", 0, 0, FUENTES[0], 0,
         "dato.s_fuente.meaning", "dato.s_fuente.source", widget="select", options=FUENTES),
    Dato(SED, "s_z0", "dato.s_z0.label", "m", 0.05, 2, 0.4, 0.01,
         "dato.s_z0.meaning", "dato.s_z0.source"),
    Dato(SED, "s_zinf", "dato.s_zinf.label", "m", 0.005, 1, 0.035, 0.005,
         "dato.s_zinf.meaning", "dato.s_zinf.source"),
    Dato(SED, "s_a", "dato.s_a.label", "", 0.5, 6, 1.591, 0.01,
         "dato.s_a.meaning", "dato.s_a.source"),
    Dato(SED, "s_b", "dato.s_b.label", "s", 10, 3600, 203, 1,
         "dato.s_b.meaning", "dato.s_b.source"),
    Dato(SED, "s_cma", "dato.s_cma.label", "%", 0.5, 60, 4.9, 0.1,
         "dato.s_cma.meaning", "dato.s_cma.source"),
    Dato(SED, "s_cmu", "dato.s_cmu.label", "%", 5, 80, 30, 1,
         "dato.s_cmu.meaning", "dato.s_cmu.source"),
    Dato(SED, "s_rho", "dato.s_rho.label", "t/m³", 1.5, 8, 4.0, 0.1,
         "dato.s_rho.meaning", "dato.s_rho.source"),
    Dato(SED, "s_comp", "dato.s_comp.label", "", 0, 0, COMPRESIONES[0], 0,
         "dato.s_comp.meaning", "dato.s_comp.source", widget="select", options=COMPRESIONES),
    Dato(SED, "s_tc", "dato.s_tc.label", "s", 10, 7200, 420, 10,
         "dato.s_tc.meaning", "dato.s_tc.source"),
    Dato(SED, "s_modo", "dato.s_modo.label", "", 0, 0, MODOS[0], 0,
         "dato.s_modo.meaning", "dato.s_modo.source", widget="select", options=MODOS),
    Dato(SED, "s_tph", "dato.s_tph.label", "t/h", 1, 5000, 157, 1,
         "dato.s_tph.meaning", "dato.s_tph.source"),
    Dato(SED, "s_factor", "dato.s_factor.label", "", 0, 0, FACTORES[0], 0,
         "dato.s_factor.meaning", "dato.s_factor.source", widget="select", options=FACTORES),
    Dato(COP, "k_temp", "dato.k_temp.label", "°C", 700, 1075, 800, 5,
         "dato.k_temp.meaning", "dato.k_temp.source"),
    Dato(COP, "k_pb_src", "dato.k_pb_src.label", "", 0, 0, FUENTES_PLOMO[0], 0,
         "dato.k_pb_src.meaning", "dato.k_pb_src.source", widget="select",
         options=FUENTES_PLOMO),
    Dato(COP, "k_pb", "dato.k_pb.label", "g", 5, 60, 28, 0.5,
         "dato.k_pb.meaning", "dato.k_pb.source"),
    Dato(COP, "k_au", "dato.k_au.label", "mg", 0.01, 200, 1.0, 0.1,
         "dato.k_au.meaning", "dato.k_au.source"),
    Dato(COP, "k_ag", "dato.k_ag.label", "mg", 0, 2000, 2.0, 0.5,
         "dato.k_ag.meaning", "dato.k_ag.source"),
    Dato(COP, "k_modo", "dato.k_modo.label", "", 0, 0, COP_MODOS[0], 0,
         "dato.k_modo.meaning", "dato.k_modo.source", widget="select", options=COP_MODOS),
    Dato(COP, "k_razon", "dato.k_razon.label", "Ag:Au", 1, 30, 8, 0.5,
         "dato.k_razon.meaning", "dato.k_razon.source"),
    Dato(COP, "k_ley", "dato.k_ley.label", "g/t", 0.01, 1000, 3.84, 0.1,
         "dato.k_ley.meaning", "dato.k_ley.source"),
    Dato(QC, "q_crm", "dato.q_crm.label", "", 0, 0, CRMS[0], 0,
         "dato.q_crm.meaning", "dato.q_crm.source", widget="select", options=CRMS),
    Dato(QC, "q_val", "dato.q_val.label", "g/t", 0.01, 100, 1.0, 0.01,
         "dato.q_val.meaning", "dato.q_val.source"),
    Dato(QC, "q_sd", "dato.q_sd.label", "g/t", 0.0005, 10, 0.04, 0.001,
         "dato.q_sd.meaning", "dato.q_sd.source"),
    Dato(QC, "q_crm_fuente", "dato.q_crm_fuente.label", "", 0, 0, QC_FUENTES[0], 0,
         "dato.q_crm_fuente.meaning", "dato.q_crm_fuente.source", widget="select",
         options=QC_FUENTES),
    Dato(QC, "q_n", "dato.q_n.label", "", N_RANGO[0], N_RANGO[1], 30, 5,
         "dato.q_n.meaning", "dato.q_n.source"),
    Dato(QC, "q_sesgo", "dato.q_sesgo.label", "%", -4, 4, 0.0, 0.5,
         "dato.q_sesgo.meaning", "dato.q_sesgo.source"),
    Dato(QC, "q_dup_fuente", "dato.q_dup_fuente.label", "", 0, 0, DUP_FUENTES[0], 0,
         "dato.q_dup_fuente.meaning", "dato.q_dup_fuente.source", widget="select",
         options=DUP_FUENTES),
    Dato(QC, "q_dup_tipo", "dato.q_dup_tipo.label", "", 0, 0, DUP_TIPOS[0], 0,
         "dato.q_dup_tipo.meaning", "dato.q_dup_tipo.source", widget="select",
         options=DUP_TIPOS),
    Dato(QC, "q_dup_p", "dato.q_dup_p.label", "%", 0, 0, PRECISIONES[0], 0,
         "dato.q_dup_p.meaning", "dato.q_dup_p.source", widget="select", options=PRECISIONES),
    Dato(QC, "q_blk_fuente", "dato.q_blk_fuente.label", "", 0, 0, QC_FUENTES[0], 0,
         "dato.q_blk_fuente.meaning", "dato.q_blk_fuente.source", widget="select",
         options=QC_FUENTES),
    Dato(QC, "q_ld", "dato.q_ld.label", "g/t", 0.001, 1, 0.005, 0.001,
         "dato.q_ld.meaning", "dato.q_ld.source"),
    Dato(QC, "q_pico", "dato.q_pico.label", "× LD", 0, 30, 4.0, 0.5,
         "dato.q_pico.meaning", "dato.q_pico.source"),
)  # fmt: skip
BY_KEY = {d.key: d for d in DATOS}
GROUPS = (PROT, MIN, GOLD, FUS, CIA, SED, COP, QC)


def _ask(d: Dato) -> float | bool | str:
    key, label = PREFIX + d.key, f"{d.label} ({d.unit})" if d.unit else d.label
    sb = st  # dentro de `with sidebar.expander(...)`: st.* cae en el expander
    if d.widget == "select":
        labels = [opt(o) for o in d.options]  # el valor del modelo (en español) se rotula aquí
        chosen = sb.selectbox(label, labels, labels.index(opt(str(d.default))), key=key,
                              help=d.help)  # fmt: skip
        if chosen is None:  # con 1.66 el tipo admite None; con `index` dado no ocurre
            return d.default
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
    ProtocolParams,
    MineralParams,
    GoldParams,
    float,
    FusionUIParams,
    CianParams,
    SedParams,
    CopParams,
    QaqcParams,
]:
    """Lee la barra lateral. Devuelve el protocolo, el mineral, el oro, la alícuota (g), la fusión,
    la cianuración, la sedimentación, la copelación y el control de calidad."""
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
    sed = SedParams(
        str(v["s_fuente"]), float(v["s_z0"]), float(v["s_zinf"]), float(v["s_a"]),
        float(v["s_b"]), float(v["s_cma"]), float(v["s_cmu"]), float(v["s_rho"]),
        float(v["s_tc"]), str(v["s_comp"]), str(v["s_modo"]), float(v["s_tph"]),
        str(v["s_factor"]),
    )  # fmt: skip
    cop = CopParams(
        float(v["k_temp"]), str(v["k_pb_src"]), float(v["k_pb"]), float(v["k_au"]),
        float(v["k_ag"]), str(v["k_modo"]), float(v["k_razon"]), float(v["k_ley"]),
    )  # fmt: skip
    qaqc = QaqcParams(
        str(v["q_crm"]), float(v["q_val"]), float(v["q_sd"]), str(v["q_crm_fuente"]),
        int(v["q_n"]), float(v["q_sesgo"]), str(v["q_dup_fuente"]), str(v["q_dup_tipo"]),
        str(v["q_dup_p"]), str(v["q_blk_fuente"]), float(v["q_ld"]), float(v["q_pico"]),
    )  # fmt: skip
    return protocol, mineral, gold, aliquot, fusion_ui, cian, sed, cop, qaqc


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
