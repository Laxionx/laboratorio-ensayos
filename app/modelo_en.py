"""Los rótulos que salen del modelo (`muestreo`) en español, vertidos al inglés para la app.

El modelo no cambia: sus cifras y sus textos siguen en español. Aquí se traducen, por reglas de
frases fijas, los nombres de las etapas, los conceptos y las notas de las tablas de validación.
Los números se vuelven al formato inglés (coma decimal → punto, espacio de miles → coma). Las citas
(autores, años, títulos) no se tocan. La prueba `test_i18n.py` recorre todos los rótulos que el
modelo produce y comprueba que ninguno queda con palabras en español.
"""

from __future__ import annotations

import re

# (frase en español, frase en inglés). Se aplican en este orden: las largas, antes que las cortas.
PHRASES: tuple[tuple[str, str], ...] = (
    # notas
    ("no cuadra: con K y α impresos sale", "does not match: with the printed K and α it gives"),
    ("para 0,00005 haría falta dN ≈", "for 0.00005 it would take dN ≈"),
    ("y la fila siguiente", "and the next row"),
    ("sí cuadra con", "does match with"),
    (
        "su propio 0,60 g por g da 17,5; el 17,4 de la tabla es un redondeo suyo",
        "his own 0.60 g per g gives 17.5; the 17.4 in the table is his own rounding",
    ),
    (
        "calculadora (estequiometría actual); Bugbee usa su Tabla XXII",
        "calculator (current stoichiometry); Bugbee uses his Table XXII",
    ),
    ("calculadora", "calculator"),
    ("con c·f·g·ℓ = 448 (no es el valor impreso)", "with c·f·g·ℓ = 448 (not the printed value)"),
    (
        "los resultados publicados implican 448 (ℓ efectivo 0,000224), 6,4 veces el impreso",
        "the published results imply 448 (effective ℓ 0,000224), 6,4 times the printed value",
    ),
    ("datos impresos:", "printed data:"),
    ("corte:", "threshold:"),
    ("Poisson exacto (Garwood)", "Exact Poisson (Garwood)"),
    ("; la etiqueta de la Fig. 4 está redondeada", "; the label in Fig. 4 is rounded"),
    # fuentes
    ("Tablas XXI y XXII", "Tables XXI and XXII"),
    ("Tabla XXII", "Table XXII"),
    ("Tabla XXI", "Table XXI"),
    ("Tabla XX", "Table XX"),
    ("Tabla VIII", "Table VIII"),
    ("Tabla 2", "Table 2"),
    ("ejemplos resueltos", "worked examples"),
    ("mezcla ", "mixture "),
    ("poder oxidante", "oxidizing power"),
    ("poder reductor", "reducing power"),
    ("Apéndice", "Appendix"),
    ("factor implícito", "implied factor"),
    ("problema ", "problem "),
    # unidades
    ("varianza relativa", "relative variance"),
    ("grado de silicato", "silicate degree"),
    ("grado", "degree"),
    # etapas y ruta del nomograma
    ("Muestreo primario en la mina", "Primary sampling at the mine"),
    ("Primera división", "First split"),
    ("Segunda división", "Second split"),
    ("Pulverizado y alícuota de fuego", "Pulverizing and fire-assay aliquot"),
    ("Pulverizado a", "Pulverizing to"),
    ("Chancado y riffle", "Crushing and riffle splitting"),
    ("Chancado a", "Crushing to"),
    ("y alícuota", "and aliquot"),
    ("y división", "and split"),
    ("Pulverizado", "Pulverizing"),
    ("reducir a dN", "reduce to dN"),
    ("dividir", "split"),
    ("Inicio", "Start"),
    # conceptos
    ("desviación", "deviation"),
    ("partículas, límite inferior", "particles, lower limit"),
    ("partículas, límite superior", "particles, upper limit"),
    ("error relativo", "relative error"),
    ("masa para", "mass for"),
    ("dN para 15 % con 15 kg", "dN for 15 % with 15 kg"),
    ("dℓ para σ² = 0,01 con 10 kg", "dℓ for σ² = 0,01 with 10 kg"),
    ("varianza", "variance"),
    ("Total", "Total"),
    # carga fundente
    (
        "nitro para un botón de 30 g (15 g de R.P. 5,00)",
        "niter for a 30 g button (15 g of R.P. 5,00)",
    ),
    ("1 A.T. de sílice pura", "1 A.T. of pure silica"),
    ("litargirio para la escoria", "litharge for the slag"),
    ("(3/5 de la sílice)", "(3/5 of the silica)"),
    ("neutraliza (g de SiO2", "neutralizes (g of SiO2"),
    ("requiere (g de bórax vidrio)", "requires (g of borax glass)"),
    ("sesqui-silicato", "sesquisilicate"),
    ("bi-silicato", "bisilicate"),
    ("mono-silicato", "monosilicate"),
    ("por A.T. de cuarzo", "per A.T. of quartz"),
    ("carga calculada", "calculated charge"),
    ("menos la sílice del mineral", "minus the ore silica"),
    ("resto a bórax (como sílice)", "rest as borax (as silica)"),
    ("sílice (dos tercios)", "silica (two thirds)"),
    ("sílice de la soda", "silica of the soda"),
    ("sílice del CaCO3", "silica of the CaCO3"),
    ("sílice del litargirio", "silica of the litharge"),
    ("sílice o bórax necesarios", "silica or borax needed"),
    ("sílice que piden", "silica required by"),
    ("bórax vidrio", "borax glass"),
    ("sílice", "silica"),
    ("harina", "flour"),
    ("litargirio", "litharge"),
    ("carbono (", "carbon ("),
    ("hierro (", "iron ("),
    ("minio (", "red lead ("),
    ("nitro (", "niter ("),
    ("pirita, 5PbO (a SO2)", "pyrite, 5PbO (to SO2)"),
    ("pirita, ferrosa (14PbO por 2FeS2)", "pyrite, ferrous (14PbO per 2FeS2)"),
    ("pirita, férrica (15PbO por 2FeS2)", "pyrite, ferric (15PbO per 2FeS2)"),
    ("azufre a", "sulfur to"),
    (": S a SO", ": S to SO"),
    ("de CaCO3", "of CaCO3"),
    ("CaCO3 puro", "Pure CaCO3"),
    ("Mitad calcita, mitad cuarzo", "Half calcite, half quartz"),
    ("sin base", "no base"),
    ("inerte", "inert"),
    ("muestra", "sample"),
    ("botón", "button"),
    ("nitro", "niter"),
    # minerales
    ("Arsenopirita", "Arsenopyrite"),
    ("Calcocita", "Chalcocite"),
    ("Calcopirita", "Chalcopyrite"),
    ("Esfalerita", "Sphalerite"),
    ("Estibina", "Stibnite"),
    ("Pirrotita", "Pyrrhotite"),
    ("Pirita", "Pyrite"),
    ("Cuarzo", "Quartz"),
    ("Calcita", "Calcite"),
    ("Hematita", "Hematite"),
    ("Galena", "Galena"),
)
_UNITS = (("g de ", "g of "), ("A.T. de ", "A.T. of "), ("kg de ", "kg of "))
_DECIMAL = re.compile(r"(?<=\d),(?=\d)")
_THOUSANDS = re.compile(r"(?<=\d) (?=\d{3}(?!\d))")


def translate(text: str) -> str:
    """El rótulo del modelo en inglés, con los números en formato inglés."""
    out = text
    for es_, en_ in PHRASES:
        out = out.replace(es_, en_)
    for es_, en_ in _UNITS:
        out = out.replace(es_, en_)
    out = _DECIMAL.sub(".", out)
    return _THOUSANDS.sub(",", out)


ERRORS: tuple[tuple[str, str], ...] = (
    (
        r"«(.+)»: la masa dividida \((.+) g\) debe ser menor que la de entrada \((.+) g\)",
        "«{0}»: the split mass ({1} g) must be smaller than the input mass ({2} g)",
    ),
    (
        r"la muestra \((.+) g\) no puede pesar más que el lote \((.+) g\)",
        "the sample ({0} g) cannot weigh more than the lot ({1} g)",
    ),
    (r"(\w+) debe ser positivo y finito: (.+)", "{0} must be positive and finite: {1}"),
    (r"el protocolo necesita al menos una etapa", "the protocol needs at least one stage"),
    (
        r"el porcentaje pasante debe estar entre 0 y 100: (.+)",
        "the passing percentage must be between 0 and 100: {0}",
    ),
    (r"el tamaño debe ser positivo y finito: (.+)", "the size must be positive and finite: {0}"),
    (
        r"la pendiente m debe estar entre (.+) y (.+): (.+)",
        "the slope m must be between {0} and {1}: {2}",
    ),
    (
        r"la proporción a debe estar entre 0 y 1: (.+)",
        "the proportion a must be between 0 and 1: {0}",
    ),
    (r"el exponente b debe estar entre 0 y 3: (.+)", "the exponent b must be between 0 and 3: {0}"),
    (r"faltan datos del mineral: (.+)", "mineral data missing: {0}"),
    (
        r"el tamaño del grano y la densidad deben ser positivos",
        "the grain size and the density must be positive",
    ),
    (
        r"la ley, la alícuota y la masa del grano deben ser positivas",
        "the grade, the aliquot and the grain mass must be positive",
    ),
    (
        r"la ley, la masa del grano y las partículas deben ser positivas",
        "the grade, the grain mass and the particles must be positive",
    ),
    (r"las partículas esperadas deben ser positivas", "the expected particles must be positive"),
    (r"forma desconocida (.+); use una de (.+)", "unknown shape {0}; use one of {1}"),
    (r"mineral desconocido: (.+)", "unknown mineral: {0}"),
    (r"minerales desconocidos: (.+)", "unknown minerals: {0}"),
    (r"la masa de la muestra debe ser positiva", "the sample mass must be positive"),
    (r"los porcentajes deben ser números no negativos", "the percentages must be non-negative"),
    (
        r"los minerales suman (.+) %: no pueden pasar de 100 %",
        "the minerals add up to {0} %: they cannot exceed 100 %",
    ),
    (r"el botón pedido debe ser positivo", "the requested button must be positive"),
    (
        r"el grado de silicato y los poderes de la harina y del nitro deben ser > 0",
        "the silicate degree and the flour and niter powers must be > 0",
    ),
    (r"el azufre sale como SO2 o SO3: (.+)", "the sulfur leaves as SO2 or SO3: {0}"),
    (
        r"el poder oxidante del nitro debe ser positivo",
        "the oxidizing power of the niter must be positive",
    ),
)


def translate_error(message: str) -> str:
    """Un mensaje de error del modelo en inglés; si no se conoce, el original."""
    for pattern, template in ERRORS:
        m = re.fullmatch(pattern, message, flags=re.S)
        if m:
            parts = [
                translate(p) if i == 0 and pattern.startswith("«") else p
                for i, p in enumerate(m.groups())
            ]
            return template.format(*parts)
    return message
