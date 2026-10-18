"""Cada dato de entrada se define una sola vez: arma la barra lateral y la tabla «Qué datos
necesita» de la guía, así las dos no se pueden desfasar."""

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

from muestreo import fusion
from muestreo.protocolo import PRESETS

PREFIX = "dato_"
PROT, MIN, GOLD, FUS = "Protocolo", "Mineral", "Oro grueso", "Fusión"
ALIQUOTS = ("30", "50")  # Au-AA23 y Au-AA24
SHAPES = ("esfera", "cubo")


@dataclass(frozen=True)
class Dato:
    group: str
    key: str
    label: str
    unit: str
    lo: float
    hi: float
    default: float | bool | str
    step: float
    meaning: str
    source: str
    widget: str = "number"  # number | select | check
    options: tuple[str, ...] = ()

    @property
    def range_text(self) -> str:
        if self.widget == "select":
            return " o ".join(self.options)
        if self.widget == "check":
            return "sí o no"
        return f"{_num(self.lo)} a {_num(self.hi)}"

    @property
    def default_text(self) -> str:
        if self.widget == "check":
            return "sí" if self.default else "no"
        return self.default if isinstance(self.default, str) else _num(self.default)

    @property
    def help(self) -> str:
        unit = f" ({self.unit})" if self.unit else ""
        return f"{self.meaning} Rango{unit}: {self.range_text}. En planta: {self.source}"


def _num(x: float) -> str:
    """Número en español: «1 000», «2,7»."""
    if float(x).is_integer():
        return f"{int(x):,}".replace(",", " ")
    return f"{x:g}".replace(".", ",")


DATOS: tuple[Dato, ...] = (
    Dato(PROT, "preset", "Protocolo de preparación", "", 0, 0, PRESETS[0], 0,
         "PREP-31: chancar al 70 % bajo 2 mm, dividir 250 g y pulverizar al 85 % bajo 75 µm. "
         "PREP-31B: igual con 1 kg. La tercera es la tabla de una mina de oro de Minnitt (2017). "
         "Códigos públicos de ALS; sin afiliación.",
         "el procedimiento de preparación del laboratorio.", widget="select", options=PRESETS),
    Dato(PROT, "aliquot", "Alícuota de ensayo al fuego", "g", 0, 0, "30", 0,
         "Masa que se funde: 30 g (Au-AA23) o 50 g (Au-AA24).", "el método de ensayo pedido.",
         widget="select", options=ALIQUOTS),
    Dato(PROT, "lot", "Masa de la muestra recibida", "g", 500, 20_000, 3000, 100,
         "Masa que entra a la chancadora. Dato supuesto: depende de cada envío.",
         "la balanza de recepción de muestras."),
    Dato(PROT, "d_n0", "Tamaño de la muestra recibida", "cm", 1, 15, 5, 0.5,
         "Solo dibuja el primer tramo del nomograma; no entra al error.",
         "inspección de la muestra recibida."),
    Dato(PROT, "m", "Pendiente m de Rosin-Rammler", "", 0.5, 3.0, 1.0, 0.1,
         "Forma de la curva granulométrica que completa «70 % bajo 2 mm». Es un supuesto: el "
         "d95 (y con él el error, que lo lleva al cubo) cambia con m.",
         "el análisis granulométrico del producto chancado y pulverizado."),
    Dato(PROT, "safety", "Error de seguridad del nomograma", "%", 1, 50, 10, 1,
         "Línea del nomograma bajo la cual el error de una división se considera aceptable.",
         "el objetivo de calidad del laboratorio."),
    Dato(PROT, "lot_correction", "Corrección por masa del lote (1/MS − 1/ML)", "", 0, 1, True, 0,
         "Gy la incluye; Minnitt (2017) la omite en su Tabla VIII. Apagada, el error sube.",
         "se activa siempre, salvo para reproducir esa tabla.", widget="check"),
    Dato(MIN, "form", "Forma de la ecuación y mineral", "", 0, 0, MINERALS[0], 0,
         "Calibrada: σ² = K·dN^α/MS con K y α de un mineral (Minnitt 2017, DSA o SFA, de una mena "
         "de Witwatersrand) o propios. Clásica: c·f·g·ℓ·dN³/MS con los factores de abajo. K y α "
         "se calibran por mineral; nunca se suponen.",
         "ensayo de heterogeneidad o árbol de muestreo del propio mineral.",
         widget="select", options=MINERALS),
    Dato(MIN, "k", "K propio", "", 0.01, 10_000, 167.4, 1,
         "Constante de la forma calibrada, con dN en cm y masas en g. Solo si eliges «Calibrado "
         "propio»; el valor inicial es el DSA de Minnitt (2017).",
         "el intercepto de la recta de calibración del mineral."),
    Dato(MIN, "alpha", "α propio", "", 0.5, 3.0, 1.123, 0.01,
         "Exponente de la forma calibrada. Solo con «Calibrado propio».",
         "la pendiente de la recta de calibración del mineral."),
    Dato(MIN, "grade", "Ley de oro", "g/t", 0.1, 100, 3.84, 0.1,
         "Ley del lote. Fija la proporción a (factor c, forma clásica) y el número de granos en "
         "la alícuota (pestaña Oro grueso). El valor inicial es el promedio de Minnitt (2017).",
         "ensayos del lote."),
    Dato(MIN, "rho_m", "Densidad del mineral valioso", "g/cm³", 1, 20, 16, 0.1,
         "Solo forma clásica. 16 es la de una amalgama oro-plata (Minnitt 2017); 19,3, el oro "
         "puro.", "tablas de densidades del mineral."),
    Dato(MIN, "rho_g", "Densidad de la ganga", "g/cm³", 2, 4, 2.75, 0.05,
         "Solo forma clásica.", "picnómetro del laboratorio."),
    Dato(MIN, "d_lib", "Tamaño de liberación dℓ", "µm", 10, 5000, 82, 1,
         "Solo forma clásica: tamaño bajo el cual el mineral está liberado. 82 µm es el del DSA "
         "de Minnitt (2017).", "estudio de liberación (mineralogía)."),
    Dato(MIN, "f", "Factor de forma f", "", 0.1, 1.0, 0.5, 0.05,
         "Solo forma clásica: 0,5 para la mayoría de las menas; 0,2 a 0,5 en la práctica.",
         "valor del ejemplo de Minnitt; no se mide."),
    Dato(MIN, "g", "Factor granulométrico g", "", 0.1, 1.0, 0.25, 0.05,
         "Solo forma clásica: 0,25 con un amplio rango de tamaños; 1 si son todos iguales.",
         "valor del ejemplo de Minnitt; depende del equipo de reducción."),
    Dato(MIN, "b", "Exponente b de la liberación", "", 0.0, 3.0, 1.5, 0.1,
         "Solo forma clásica: ℓ = (dℓ/dN)^b; 1,5 en la mayoría de las menas de oro (Minnitt 2007).",
         "calibración por mineral."),
    Dato(GOLD, "grain", "Tamaño del grano de oro", "µm", 10, 1000, 150, 10,
         "Diámetro del grano de oro libre. Con forma de esfera o cubo, fija la masa del grano.",
         "mineralogía del oro (microscopio, concentrado gravimétrico)."),
    Dato(GOLD, "shape", "Forma del grano", "", 0, 0, "esfera", 0,
         "Esfera (π/6·d³) o cubo (d³). El oro real es irregular: la forma es un supuesto.",
         "observación del oro al microscopio.", widget="select", options=SHAPES),
    Dato(FUS, "f_sample", "Masa de la alícuota a fundir", "", 0, 0, FUSION_SAMPLES[0], 0,
         "Un assay-ton (29,1667 g) o 30 g. La fusión lleva la carga que se calcula para esta masa.",
         "la alícuota que pesa el laboratorio.", widget="select", options=FUSION_SAMPLES),
    *(
        Dato(FUS, "m_" + m.key, f"{m.name} ({m.formula})", "%", 0, 100,
             FUSION_DEFAULT_MINERALS.get(m.key, 0.0), 1,
             "Parte de la muestra en masa. Todos los minerales suman 100 % como máximo: lo que "
             "falta es material inerte (no ácido ni básico, solo pasa a la escoria).",
             "mineralogía de la muestra (microscopio, difracción de rayos X o análisis químico).")
        for m in fusion.MINERALS
    ),
    Dato(FUS, "f_sulfur", "Azufre oxidado a", "", 0, 0, "SO3", 0,
         "SO3: con carbonato alcalino, el azufre queda como sulfato (poder reductor mayor). SO2: "
         "sin carbonato alcalino. Bugbee: el real queda entre los dos; se mide en una fusión "
         "preliminar.", "fusión preliminar de reconocimiento.", widget="select",
         options=fusion.SULFUR_MODES),
    Dato(FUS, "f_button", "Botón de plomo pedido", "g", 20, 35, 28, 0.5,
         "Bugbee: 28 g bastan como colector; no menos de 25 g ni más de 30 g.",
         "el tamaño del botón que pide el laboratorio."),
    Dato(FUS, "f_degree", "Grado de silicato de la escoria", "", 0, 0, "bi", 0,
         "Oxígeno del ácido entre oxígeno de la base: mono 1, sesqui 1,5, bi 2. Bugbee: bi o "
         "sesqui para menas silíceas y básicas; cerca de mono para sulfuros.",
         "la práctica del laboratorio.", widget="select", options=FUSION_DEGREES),
    Dato(FUS, "f_flour", "Poder reductor de la harina", "g Pb/g", 8, 13, 11, 0.5,
         "Dato del laboratorio, no del modelo: g de plomo que reduce 1 g de harina. Bugbee da "
         "10 a 12 (usa 12 en sus ejemplos) y el USGS 10 a 11; el valor inicial es el medio.",
         "fusión de prueba con la harina del laboratorio (Bugbee, «Testing reagents»)."),
    Dato(FUS, "f_niter", "Poder oxidante del nitro", "g Pb/g", 3.0, 5.12, 4.1, 0.1,
         "Dato del laboratorio: g de plomo que oxida 1 g de nitro. El teórico es 5,12; Bugbee da "
         "4,0 a 4,2 con su tipo de carga (3,7 a 4,7 según la acidez) y el USGS 4,2.",
         "fusión preliminar con el nitro del laboratorio."),
    Dato(FUS, "f_soda", "Soda por gramo de muestra", "g/g", 0.5, 3.0, 1.0, 0.1,
         "Carbonato de sodio como fundente base. Bugbee: al menos el peso de la muestra.",
         "la práctica del laboratorio."),
    Dato(FUS, "f_lith", "Litargirio para la escoria por gramo de muestra", "g/g", 0.5, 3.0, 1.4,
         0.1, "Litargirio que se queda en la escoria, además del que se reduce a plomo. Bugbee, "
         "carga de 1 assay-ton: 70 g en total, 30 para el botón.",
         "la práctica del laboratorio."),
    Dato(FUS, "x_flour", "Probar: harina cambiada", "×", 0, 2, 1, 0.1,
         "Multiplica la harina calculada para ver qué pasa con una carga mal pesada (botón chico "
         "o grande). 1 deja la carga calculada.", "no es un dato de planta."),
    Dato(FUS, "x_silica", "Probar: sílice cambiada", "×", 0, 3, 1, 0.1,
         "Multiplica la sílice calculada: más sílice vuelve ácida la escoria y arriesga mata.",
         "no es un dato de planta."),
    Dato(FUS, "x_lith", "Probar: litargirio cambiado", "×", 0.3, 2, 1, 0.05,
         "Multiplica el litargirio calculado: poco litargirio también arriesga mata.",
         "no es un dato de planta."),
)  # fmt: skip
BY_KEY = {d.key: d for d in DATOS}
GROUPS = (PROT, MIN, GOLD, FUS)


def _ask(d: Dato) -> float | bool | str:
    key, label = PREFIX + d.key, f"{d.label} ({d.unit})" if d.unit else d.label
    sb = st  # dentro de `with sidebar.expander(...)`: st.* cae en el expander
    if d.widget == "select":
        return sb.selectbox(label, list(d.options), d.options.index(str(d.default)), key=key,
                            help=d.help)  # fmt: skip
    if d.widget == "check":
        return sb.checkbox(label, value=bool(d.default), key=key, help=d.help)
    lo, hi, v, step = (float(x) for x in (d.lo, d.hi, d.default, d.step))
    return sb.number_input(label, lo, hi, v, step, help=d.help, key=key)


def reset_to_example() -> None:
    """Vuelve todos los datos al ejemplo."""
    for k in [k for k in st.session_state if str(k).startswith(PREFIX)]:
        del st.session_state[k]


def sidebar_config() -> tuple[ProtocolParams, MineralParams, GoldParams, float, FusionUIParams]:
    """Lee la barra lateral. Devuelve el protocolo, el mineral, el oro y la alícuota (g)."""
    sb = st.sidebar
    sb.button("Cargar ejemplo", on_click=reset_to_example, width="stretch")
    v: dict[str, float | bool | str] = {}
    for group in GROUPS:
        with sb.expander(group, expanded=group == PROT):
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
    return protocol, mineral, gold, aliquot, fusion_ui


def data_table(group: str | None = None) -> pd.DataFrame:
    """La tabla «Qué datos necesita», hecha de las mismas definiciones que la barra lateral."""
    rows = [
        {
            "Grupo": d.group,
            "Dato": d.label,
            "Unidad": d.unit,
            "Rango": d.range_text,
            "Ejemplo": d.default_text,
            "Qué es": d.meaning,
            "Cómo se obtiene": d.source[0].upper() + d.source[1:],
        }
        for d in DATOS
        if group in (None, d.group)
    ]
    return pd.DataFrame(rows)
