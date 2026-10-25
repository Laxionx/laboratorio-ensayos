"""Textos en español de la Guía y de las fichas de cada pestaña."""

T = {
    "minnitt2007.note": (
        "El artículo imprime ℓ = 0,000035, pero sus resultados implican un valor 6,4 veces mayor; "
        "aquí se usa la fórmula con los datos impresos."
    ),
    "ficha.label.hace": "**Qué hace.** {text}",
    "ficha.label.entra": "**Qué entra.** {text}",
    "ficha.label.sale": "**Qué devuelve.** {text}",
    "ficha.expander.datos": "Qué datos necesita",
    "ficha.expander.limites": "Límites del modelo",
    "ficha.autores": "**De dónde salen las ecuaciones.** {text}",
    "ficha.protocolo.hace": (
        "Calcula cuánto error de muestreo mete cada etapa de la preparación de una "
        "muestra de laboratorio (reducir el tamaño y dividir hasta una masa menor) con la "
        "ecuación del error fundamental de Gy, y cuánto se acumula. Dibuja la ruta del "
        "protocolo en el nomograma de muestreo."
    ),
    "ficha.protocolo.entra": (
        "El protocolo (masa recibida, tamaño de cada etapa y masa de cada división), la "
        "alícuota de fuego de 30 o 50 g y el mineral (K y α calibrados, o los factores c, f, g, "
        "ℓ). El tamaño de cada etapa sale de su especificación («70 % bajo 2 mm») más una "
        "pendiente m supuesta."
    ),
    "ficha.protocolo.sale": (
        "La varianza relativa y el error (desviación estándar relativa) de cada división "
        "y el acumulado, qué etapa domina, si cada división queda bajo la línea de seguridad y "
        "cómo cambia el error con la pendiente m."
    ),
    "ficha.protocolo.autores": (
        "Gy (1982), *Sampling of Particulate Materials*; forma calibrada: "
        "François-Bongarçon; Minnitt, Rice y Spangenberg (2007), *J. SAIMM* 107(8) 505-511; "
        "Minnitt (2017), «A version of Gy's equation for gold-bearing ores», *J. SAIMM* 117(2) "
        "121-128 (K y α del ejemplo); Chieregati (2017), *Mining Engineering*, nov. Códigos de "
        "preparación PREP-31 y PREP-31B: públicos de ALS (alsglobal.com), sin afiliación."
    ),
    "ficha.protocolo.limit.1": (
        "K y α se calibran por mineral y los del ejemplo son los de una mena de oro de "
        "Witwatersrand: no valen para otro mineral."
    ),
    "ficha.protocolo.limit.2": (
        "El tamaño de cada etapa depende de la pendiente m de la curva Rosin-Rammler, un "
        "supuesto: como dN pesa al cubo, el error cambia mucho con m."
    ),
    "ficha.protocolo.limit.3": (
        "Solo el error fundamental: no hay errores de delimitación, extracción, preparación "
        "ni de análisis."
    ),
    "ficha.oro.hace": (
        "Cuenta cuántos granos de oro caen en la alícuota de 30 o 50 g cuando el oro es "
        "grueso y simula 1 000 ensayos repetidos de esa misma alícuota: con pocos granos, la "
        "mediana de los ensayos queda bajo la ley real y unos pocos salen muy altos."
    ),
    "ficha.oro.entra": "La ley de oro, el tamaño y la forma del grano de oro y la masa de la alícuota.",
    "ficha.oro.sale": (
        "Granos esperados por alícuota (λ), probabilidad de no recibir ninguno, la "
        "simulación de Poisson con semilla fija, la masa que llevaría 20 granos y la "
        "recomendación de screen fire assay si se esperan menos de 20."
    ),
    "ficha.oro.autores": (
        "Clifton, Hunter, Swanson y Phillips (1969), *USGS Professional Paper* "
        "625-C (criterio de 20 partículas y límites al 95 %); distribución de Poisson del "
        "número de granos. Screen fire assay: procedimiento público de ALS (alsglobal.com), "
        "sin afiliación."
    ),
    "ficha.oro.limit.1": (
        "Los granos se suponen del mismo tamaño y forma (esfera o cubo), libres y repartidos "
        "al azar; el oro real es irregular y viene en una distribución de tamaños."
    ),
    "ficha.oro.limit.2": "Un modelo de Poisson: no incluye segregación ni agrupamiento de los granos.",
    "ficha.fusion.hace": (
        "Calcula la carga fundente de un ensayo al fuego: litargirio, carbonato de sodio, "
        "bórax, sílice y harina o nitro. Con ella el crisol da un botón de plomo de 25 a 30 g y "
        "una escoria del grado de silicato elegido. También evalúa una carga cambiada: botón "
        "chico o grande, escoria demasiado ácida o básica y riesgo de mata."
    ),
    "ficha.fusion.entra": (
        "La alícuota (1 assay-ton o 30 g), la mineralogía de 9 minerales en %, el botón "
        "pedido, el grado de silicato (mono, sesqui o bi) y dos datos del laboratorio: el poder "
        "reductor de la harina y el poder oxidante del nitro."
    ),
    "ficha.fusion.sale": (
        "La carga en g, el botón esperado, la composición y el grado de silicato de la "
        "escoria, el balance del plomo y los avisos, cada uno con la cita de su umbral o rotulado "
        "«umbral supuesto»."
    ),
    "ficha.fusion.autores": (
        "Poder reductor y oxidante, grados de silicato, factores de escoria y ejemplos "
        "resueltos: Bugbee (1922), *A Textbook of Fire Assaying* (dominio público). Cargas por "
        "tipo de roca, fusión preliminar a 1 050 °C y poderes de algunos minerales: Haffty, Riley "
        "y Goss (1977), USGS Bulletin 1445, *A Manual on Fire Assaying* (dominio público). "
        "Densidad del plomo líquido a 1 050 °C: OECD/NEA (2007), ec. 2.23; del sólido (botón "
        "frío), 11,34 g/cm³: CRC Handbook. Capacidad del crisol: Bugbee, Tabla IV. No es la "
        "receta de ningún laboratorio."
    ),
    "ficha.fusion.limit.1": (
        "La copelación y las pérdidas de oro y plata están en la pestaña Copelación; aquí no hay "
        "termodinámica de escorias ni ensayo de platinoides."
    ),
    "ficha.fusion.limit.2": (
        "El poder reductor de la harina y el oxidante del nitro son datos del laboratorio: "
        "Bugbee da rangos (10 a 12 y 4,0 a 4,2) y el valor real se mide en una fusión de prueba."
    ),
    "ficha.fusion.limit.3": (
        "El poder reductor de un sulfuro depende de cómo sale el azufre (SO2 o SO3); el real "
        "queda entre los dos y se mide en una fusión preliminar."
    ),
    "ficha.fusion.limit.4": (
        "La densidad de la escoria, 3,0 g/cm³, es un supuesto ilustrativo (Bugbee no la da); el "
        "dibujo del crisol es ilustrativo."
    ),
    "ficha.fusion.limit.5": (
        "Los umbrales de los avisos salen de Bugbee o del USGS con su cita; los que no tienen "
        "cita publicada están rotulados «umbral supuesto»."
    ),
    "react.1": "2PbO + C = 2Pb + CO₂: 1 g de carbono reduce 34,5 g de plomo; la harina, 10 a 12.",
    "react.2": (
        "2PbO + S = 2Pb + SO₂ (sin carbonato alcalino) o 3PbO + S + Na₂CO₃ = 3Pb + Na₂SO₄ + CO₂ "
        "(con él): el azufre reduce 12,9 o 19,4 g de plomo por gramo; los sulfuros, entre los dos."
    ),
    "react.3": (
        "Fe₂O₃ + Pb = 2FeO + PbO: la hematita oxida (1,3 g de plomo por gramo) y pide más harina."
    ),
    "react.4": (
        "4KNO₃ + 5C = 2K₂O + 5CO₂ + 2N₂: el nitro oxida 5,12 g de plomo por gramo en teoría "
        "(4,0 a 4,2 en la práctica); se agrega cuando la muestra reduce de más."
    ),
    "limits.1": (
        "Solo el error fundamental de muestreo (FSE) de Gy. NO se modelan los errores de "
        "delimitación y de extracción (cómo se corta la muestra del lote), los de preparación "
        "(contaminación, pérdidas y alteraciones), los de ponderación, la segregación y el "
        "agrupamiento, ni el error analítico del ensayo."
    ),
    "limits.2": "K y α no se suponen: se calibran por mineral. Los del ejemplo son de Minnitt (2017).",
    "limits.3": "No hay fusión, fundente ni química del ensayo al fuego: eso es de una fase posterior.",
    "limits.4": (
        "Los equipos de preparación (chancadoras de mandíbula, pulverizadores) no se simulan: el "
        "tamaño de cada etapa sale de la especificación del protocolo."
    ),
    "guide.h.simula": "### Qué simula",
    "guide.simula": (
        "La **preparación de muestras** de un laboratorio de ensayos al fuego: chancar, dividir, "
        "pulverizar y tomar la alícuota de 30 o 50 g que se funde. Cada vez que se divide una "
        "muestra se mete un error de muestreo; el simulador calcula cuánto mete cada etapa y "
        "cuánto se acumula. Y con oro grueso, cuántos granos caen en la alícuota y cuándo "
        "conviene el screen fire assay."
    ),
    "guide.h.gy": "### El error fundamental (Gy)",
    "guide.gy": (
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
    ),
    "guide.h.calibrar": "### K y α se calibran, nunca se suponen",
    "guide.calibrar": (
        "Con ℓ = (dℓ/d_N)^b, la ecuación queda σ² = K·d_N^α/M_S con α = 3 − b y K = c·f·g·dℓ^b. "
        "K y α son propios de **cada mineral**: se calibran con un ensayo de heterogeneidad o un "
        "árbol de muestreo. Los del ejemplo son los que Minnitt (2017) calibró para una mena de "
        "oro de Witwatersrand (DSA: K = 167,4, α = 1,123; SFA: K = 2 539, α = 1,03) y no valen "
        "para otro mineral."
    ),
    "guide.h.oro": "### Oro grueso y screen fire assay",
    "guide.oro": (
        "Si el oro viene en granos, el número de granos en una alícuota es de Poisson: con "
        "pocos granos casi todos los ensayos dan menos que la ley real (o cero) y unos pocos "
        "dan muy alto, así que la **mediana queda bajo la ley real**. Clifton y colaboradores "
        "(1969) piden unas **20 partículas** por muestra para un error de unos ±50 % al 95 %; "
        "con menos conviene el **screen fire assay**: se tamiza una muestra mayor (unos 1 000 g) "
        "a 100 µm, el fino se ensaya en duplicado y el grueso, entero."
    ),
    "guide.h.fusion": "### La carga fundente (pestaña Fusión)",
    "guide.fusion.1": (
        "La fusión funde la muestra con **litargirio** (PbO, que se reduce al plomo del botón), "
        "**carbonato de sodio** y **bórax** (bases y fundentes), **sílice** (ácido) y un "
        "**reductor** (harina) o un **oxidante** (nitro) según lo que ya reduzca la muestra. "
        "Reacciones de Bugbee (1922):"
    ),
    "guide.fusion.2": (
        "El **grado de silicato** es el oxígeno del ácido entre el de la base: mono 1, sesqui "
        "1,5, bi 2. 1 g de FeO neutraliza 0,84 g de sílice y 1 g de CaCO₃, 0,60 g. 1 g de "
        "bórax vidrio equivale a 0,6 g de sílice. **Qué dato pide cada reactivo:** la harina, "
        "su poder reductor; el nitro, su poder oxidante; la soda y el litargirio de la escoria, "
        "la práctica del laboratorio; la sílice y el bórax salen del balance ácido-base de la "
        "mineralogía. En el dibujo el plomo está líquido (9,79 g/cm³ a 1 050 °C) en un charco al "
        "fondo del crisol cónico, con la escoria encima; el botón ya frío (11,34 g/cm³) va aparte."
    ),
    "guide.h.minnitt": "### Lo que dice el artículo de Minnitt (2007)",
    "guide.minnitt": "_{note}_ La tabla de abajo, en la pestaña **Validación**.",
    "guide.h.datos": "### Qué datos necesita",
    "guide.h.limites": "### Lo que no hace",
    "guide.h.otras": "### Otras apps del mismo autor",
    "guide.otras": (
        "- [Simulador de conminución]({conminucion}): la molienda, animada.\n"
        "- [«Planta completa»]({planta}): flotación, horno flash, convertidor y "
        "electroobtención, animados.\n"
        "- Código de esta app: [repositorio]({repo})."
    ),
}
