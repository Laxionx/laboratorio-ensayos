"""Pestaña «Guía» y fichas de las pestañas de cálculo: qué es el error fundamental, qué dato pide
cada factor, qué se calibra y qué errores de muestreo NO se modelan."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from controles import FUS, GOLD, MIN, PROT, data_table

REPO = "https://github.com/Laxionx/laboratorio-ensayos"
CONMINUCION = "https://simulador-conminucion-mtxoolyzuvvcxrq8rce3el.streamlit.app/"
PLANTA = "https://simulador-procesos-ntfmuyhlnqc9d73kkqljzk.streamlit.app/"
MINNITT_2007_NOTE = (
    "El artículo imprime ℓ = 0,000035, pero sus resultados implican un valor 6,4 veces mayor; "
    "aquí se usa la fórmula con los datos impresos."
)

FICHAS = {
    "protocolo": {
        "hace": "Calcula cuánto error de muestreo mete cada etapa de la preparación de una "
        "muestra de laboratorio (reducir el tamaño y dividir hasta una masa menor) con la "
        "ecuación del error fundamental de Gy, y cuánto se acumula. Dibuja la ruta del "
        "protocolo en el nomograma de muestreo.",
        "entra": "El protocolo (masa recibida, tamaño de cada etapa y masa de cada división), la "
        "alícuota de fuego de 30 o 50 g y el mineral (K y α calibrados, o los factores c, f, g, "
        "ℓ). El tamaño de cada etapa sale de su especificación («70 % bajo 2 mm») más una "
        "pendiente m supuesta.",
        "sale": "La varianza relativa y el error (desviación estándar relativa) de cada división "
        "y el acumulado, qué etapa domina, si cada división queda bajo la línea de seguridad y "
        "cómo cambia el error con la pendiente m.",
        "autores": "Gy (1982), *Sampling of Particulate Materials*; forma calibrada: "
        "François-Bongarçon; Minnitt, Rice y Spangenberg (2007), *J. SAIMM* 107(8) 505-511; "
        "Minnitt (2017), «A version of Gy's equation for gold-bearing ores», *J. SAIMM* 117(2) "
        "121-128 (K y α del ejemplo); Chieregati (2017), *Mining Engineering*, nov. Códigos de "
        "preparación PREP-31 y PREP-31B: públicos de ALS (alsglobal.com), sin afiliación.",
        "limites": (
            "K y α se calibran por mineral y los del ejemplo son los de una mena de oro de "
            "Witwatersrand: no valen para otro mineral.",
            "El tamaño de cada etapa depende de la pendiente m de la curva Rosin-Rammler, un "
            "supuesto: como dN pesa al cubo, el error cambia mucho con m.",
            "Solo el error fundamental: no hay errores de delimitación, extracción, preparación "
            "ni de análisis.",
        ),
    },
    "oro": {
        "hace": "Cuenta cuántos granos de oro caen en la alícuota de 30 o 50 g cuando el oro es "
        "grueso y simula 1 000 ensayos repetidos de esa misma alícuota: con pocos granos, la "
        "mediana de los ensayos queda bajo la ley real y unos pocos salen muy altos.",
        "entra": "La ley de oro, el tamaño y la forma del grano de oro y la masa de la alícuota.",
        "sale": "Granos esperados por alícuota (λ), probabilidad de no recibir ninguno, la "
        "simulación de Poisson con semilla fija, la masa que llevaría 20 granos y la "
        "recomendación de screen fire assay si se esperan menos de 20.",
        "autores": "Clifton, Hunter, Swanson y Phillips (1969), *USGS Professional Paper* "
        "625-C (criterio de 20 partículas y límites al 95 %); distribución de Poisson del "
        "número de granos. Screen fire assay: procedimiento público de ALS (alsglobal.com), "
        "sin afiliación.",
        "limites": (
            "Los granos se suponen del mismo tamaño y forma (esfera o cubo), libres y repartidos "
            "al azar; el oro real es irregular y viene en una distribución de tamaños.",
            "Un modelo de Poisson: no incluye segregación ni agrupamiento de los granos.",
        ),
    },
}


FICHAS["fusion"] = {
    "hace": "Calcula la carga fundente de un ensayo al fuego: litargirio, carbonato de sodio, "
    "bórax, sílice y harina o nitro. Con ella el crisol da un botón de plomo de 25 a 30 g y una "
    "escoria del grado de silicato elegido. También evalúa una carga cambiada: botón chico o "
    "grande, escoria demasiado ácida o básica y riesgo de mata.",
    "entra": "La alícuota (1 assay-ton o 30 g), la mineralogía de 9 minerales en %, el botón "
    "pedido, el grado de silicato (mono, sesqui o bi) y dos datos del laboratorio: el poder "
    "reductor de la harina y el poder oxidante del nitro.",
    "sale": "La carga en g, el botón esperado, la composición y el grado de silicato de la "
    "escoria, el balance del plomo y los avisos, cada uno con la cita de su umbral o rotulado "
    "«umbral supuesto».",
    "autores": "Poder reductor y oxidante, grados de silicato, factores de escoria y ejemplos "
    "resueltos: Bugbee (1922), *A Textbook of Fire Assaying* (dominio público). Cargas por tipo "
    "de roca, fusión preliminar a 1 050 °C y poderes de algunos minerales: Haffty, Riley y Goss "
    "(1977), USGS Bulletin 1445, *A Manual on Fire Assaying* (dominio público). Densidad del "
    "plomo líquido a 1 050 °C: OECD/NEA (2007), ec. 2.23; del sólido (botón frío), 11,34 g/cm³: "
    "CRC Handbook. Capacidad del crisol: Bugbee, Tabla IV. No es la receta de ningún "
    "laboratorio.",
    "limites": (
        "Sin copelación ni pérdidas de oro y plata, sin termodinámica de escorias y sin ensayo de "
        "platinoides.",
        "El poder reductor de la harina y el oxidante del nitro son datos del laboratorio: Bugbee "
        "da rangos (10 a 12 y 4,0 a 4,2) y el valor real se mide en una fusión de prueba.",
        "El poder reductor de un sulfuro depende de cómo sale el azufre (SO2 o SO3); el real "
        "queda entre los dos y se mide en una fusión preliminar.",
        "La densidad de la escoria, 3,0 g/cm³, es un supuesto ilustrativo (Bugbee no la da); el "
        "dibujo del crisol es ilustrativo.",
        "Los umbrales de los avisos salen de Bugbee o del USGS con su cita; los que no tienen "
        "cita publicada están rotulados «umbral supuesto».",
    ),
}

DATA_GROUPS = {"protocolo": (PROT, MIN), "oro": (GOLD, MIN), "fusion": (FUS,)}

FUSION_REACTIONS = (
    "2PbO + C = 2Pb + CO₂: 1 g de carbono reduce 34,5 g de plomo; la harina, 10 a 12.",
    "2PbO + S = 2Pb + SO₂ (sin carbonato alcalino) o 3PbO + S + Na₂CO₃ = 3Pb + Na₂SO₄ + CO₂ "
    "(con él): el azufre reduce 12,9 o 19,4 g de plomo por gramo; los sulfuros, entre los dos.",
    "Fe₂O₃ + Pb = 2FeO + PbO: la hematita oxida (1,3 g de plomo por gramo) y pide más harina.",
    "4KNO₃ + 5C = 2K₂O + 5CO₂ + 2N₂: el nitro oxida 5,12 g de plomo por gramo en teoría "
    "(4,0 a 4,2 en la práctica); se agrega cuando la muestra reduce de más.",
)

LIMITES = (
    "Solo el error fundamental de muestreo (FSE) de Gy. NO se modelan los errores de "
    "delimitación y de extracción (cómo se corta la muestra del lote), los de preparación "
    "(contaminación, pérdidas y alteraciones), los de ponderación, la segregación y el "
    "agrupamiento, ni el error analítico del ensayo.",
    "K y α no se suponen: se calibran por mineral. Los del ejemplo son de Minnitt (2017).",
    "No hay fusión, fundente ni química del ensayo al fuego: eso es de una fase posterior.",
    "Los equipos de preparación (chancadoras de mandíbula, pulverizadores) no se simulan: el "
    "tamaño de cada etapa sale de la especificación del protocolo.",
)


def markdown_table(df: pd.DataFrame) -> str:
    """Tabla en Markdown: el texto largo se ajusta a la columna en vez de cortarse."""

    def cell(v: object) -> str:
        return str(v).replace("|", "\\|").replace("\n", " ")

    head = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "\n".join("| " + " | ".join(cell(v) for v in row) + " |" for row in df.values)


def ficha(name: str) -> None:
    """Ficha de una pestaña, arriba de ella: qué hace, qué entra, qué sale, de quién sale."""
    f = FICHAS[name]
    st.markdown(f"**Qué hace.** {f['hace']}")
    st.markdown(f"**Qué entra.** {f['entra']}")
    st.markdown(f"**Qué devuelve.** {f['sale']}")
    with st.expander("Qué datos necesita"):
        for group in DATA_GROUPS[name]:
            st.markdown(f"**{group}**")
            st.markdown(markdown_table(data_table(group).drop(columns="Grupo")))
    with st.expander("Límites del modelo"):
        for item in f["limites"]:
            st.markdown(f"- {item}")
    st.caption(f"**De dónde salen las ecuaciones.** {f['autores']}")


def guide_tab() -> None:
    st.markdown("### Qué simula")
    st.markdown(
        "La **preparación de muestras** de un laboratorio de ensayos al fuego: chancar, dividir, "
        "pulverizar y tomar la alícuota de 30 o 50 g que se funde. Cada vez que se divide una "
        "muestra se mete un error de muestreo; el simulador calcula cuánto mete cada etapa y "
        "cuánto se acumula. Y con oro grueso, cuántos granos caen en la alícuota y cuándo "
        "conviene el screen fire assay."
    )
    st.markdown("### El error fundamental (Gy)")
    st.latex(r"\sigma^2 = c\,f\,g\,\ell\,d_N^3\left(\frac{1}{M_S} - \frac{1}{M_L}\right) = "
             r"K\,d_N^{\alpha}\left(\frac{1}{M_S} - \frac{1}{M_L}\right)")  # fmt: skip
    st.markdown(
        "σ² es la varianza relativa de dividir una masa M_L hasta una submuestra M_S con "
        "fragmentos de tamaño máximo nominal d_N (el d95: el tamaño al que pasa el 95 %). "
        "Cada factor pide un dato:\n\n"
        "- **c, factor mineralógico:** la ley y las densidades del mineral y de la ganga "
        "(con ley baja, c ≈ densidad del mineral ÷ ley).\n"
        "- **f, forma de los fragmentos:** 0,5 para la mayoría de las menas (0,2 a 0,5 en la "
        "práctica).\n"
        "- **g, granulométrico:** 0,25 con un rango amplio de tamaños; 1 si son todos iguales.\n"
        "- **ℓ, liberación:** ℓ = (dℓ/d_N)^b, 1 cuando el mineral ya está liberado (d_N ≤ dℓ); "
        "pide el tamaño de liberación dℓ y el exponente b.\n"
        "- **d_N:** sale de la especificación del protocolo. Como entra **al cubo**, es el "
        "dato más sensible; la app muestra cuánto cambia el error con la pendiente m."
    )
    st.markdown("### K y α se calibran, nunca se suponen")
    st.markdown(
        "Con ℓ = (dℓ/d_N)^b, la ecuación queda σ² = K·d_N^α/M_S con α = 3 − b y K = c·f·g·dℓ^b. "
        "K y α son propios de **cada mineral**: se calibran con un ensayo de heterogeneidad o un "
        "árbol de muestreo. Los del ejemplo son los que Minnitt (2017) calibró para una mena de "
        "oro de Witwatersrand (DSA: K = 167,4, α = 1,123; SFA: K = 2 539, α = 1,03) y no valen "
        "para otro mineral."
    )
    st.markdown("### Oro grueso y screen fire assay")
    st.markdown(
        "Si el oro viene en granos, el número de granos en una alícuota es de Poisson: con "
        "pocos granos casi todos los ensayos dan menos que la ley real (o cero) y unos pocos "
        "dan muy alto, así que la **mediana queda bajo la ley real**. Clifton y colaboradores "
        "(1969) piden unas **20 partículas** por muestra para un error de unos ±50 % al 95 %; "
        "con menos conviene el **screen fire assay**: se tamiza una muestra mayor (unos 1 000 g) "
        "a 100 µm, el fino se ensaya en duplicado y el grueso, entero."
    )
    st.markdown("### La carga fundente (pestaña Fusión)")
    st.markdown(
        "La fusión funde la muestra con **litargirio** (PbO, que se reduce al plomo del botón), "
        "**carbonato de sodio** y **bórax** (bases y fundentes), **sílice** (ácido) y un "
        "**reductor** (harina) o un **oxidante** (nitro) según lo que ya reduzca la muestra. "
        "Reacciones de Bugbee (1922):"
    )
    for line in FUSION_REACTIONS:
        st.markdown(f"- {line}")
    st.markdown(
        "El **grado de silicato** es el oxígeno del ácido entre el de la base: mono 1, sesqui "
        "1,5, bi 2. 1 g de FeO neutraliza 0,84 g de sílice y 1 g de CaCO₃, 0,60 g. 1 g de "
        "bórax vidrio equivale a 0,6 g de sílice. **Qué dato pide cada reactivo:** la harina, "
        "su poder reductor; el nitro, su poder oxidante; la soda y el litargirio de la escoria, "
        "la práctica del laboratorio; la sílice y el bórax salen del balance ácido-base de la "
        "mineralogía. En el dibujo el plomo está líquido (9,79 g/cm³ a 1 050 °C) en un charco al "
        "fondo del crisol cónico, con la escoria encima; el botón ya frío (11,34 g/cm³) va aparte."
    )
    st.markdown("### Lo que dice el artículo de Minnitt (2007)")
    st.markdown(f"_{MINNITT_2007_NOTE}_ La tabla de abajo, en la pestaña **Validación**.")
    st.markdown("### Qué datos necesita")
    for group, rows in data_table().groupby("Grupo", sort=False):
        st.markdown(f"**{group}**")
        st.markdown(markdown_table(rows.drop(columns="Grupo")))
    st.markdown("### Lo que no hace")
    for item in LIMITES:
        st.markdown(f"- {item}")
    st.markdown("### Otras apps del mismo autor")
    st.markdown(
        f"- [Simulador de conminución]({CONMINUCION}): la molienda, animada.\n"
        f"- [«Planta completa»]({PLANTA}): flotación, horno flash, convertidor y "
        "electroobtención, animados.\n"
        f"- Código de esta app: [repositorio]({REPO})."
    )
