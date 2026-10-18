"""Cortes de validación de la ecuación de Gy contra números publicados, fijados ANTES de correr.

1. Minnitt (2017), J. SAIMM 117(2), Tabla VIII: las 19 varianzas por etapa del protocolo de una
   mina de oro (DSA: K = 167,4 y α = 1,123; SFA: K = 2539 y α = 1,03), con σ² = K·dN^α/MS (sin
   corrección de lote). Corte: igual al redondeo publicado (media unidad del último decimal).
2. Chieregati (2017), Mining Engineering, nov., Tabla 2: varianza y desviación relativa por etapa
   de un protocolo de cobre con IHL = 3,9787·d^1,6689 y corrección de lote. Corte: al redondeo
   publicado.
3. Clifton, Hunter, Swanson y Phillips (1969), USGS Professional Paper 625-C, Fig. 4: errores
   relativos al 95 % para 7, 20, 75 y 400 partículas. Corte: ±2 puntos porcentuales (su lectura es
   de un gráfico).
4. Minnitt, Rice y Spangenberg (2007), J. SAIMM 107(8) 505-511: sus problemas resueltos NO se
   reproducen con los datos impresos (hallazgo documentado: errata del artículo); aquí se
   registra qué da la fórmula con esos datos y qué factor implican los resultados publicados.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import gy, oro

# ------------------------------------------------------------------ Minnitt 2017, Tabla VIII
MINNITT_2017_CONSTANTS = {"DSA": (167.4, 1.123), "SFA": (2539.0, 1.03)}
# (masa g, dN cm, varianza publicada como se imprime)
MINNITT_2017_ROWS = {
    "DSA": (
        (4_629_629.6, 60.0, "0.00359"), (4_629_629.6, 20.0, "0.00105"),
        (462_963.0, 20.0, "0.0105"), (462_963.0, 1.0, "0.00036"),
        (23_148.1, 1.0, "0.00723"), (23_148.1, 0.0300, "0.00014"),
        (694.4, 0.0300, "0.00470"), (694.4, 0.0030, "0.00035"),
        (48.61, 0.0030, "0.00506"),
    ),
    "SFA": (
        (4_629_629.6, 60.0, "0.03721"), (4_629_629.6, 1.0, "0.00055"),
        (694_444.4, 1.0, "0.00366"), (694_444.4, 0.1, "0.00034"),
        (55_555.6, 0.1, "0.00427"), (55_555.6, 0.0030, "0.00012"),
        (2055.6, 0.0030, "0.00311"), (2055.6, 0.0030, "0.00311"),
        (2055.56, 0.0001, "0.00005"), (61.7, 0.0001, "0.00312"),
    ),
}  # fmt: skip

ROW_NOTE = (
    "no cuadra: con K y α impresos sale 0,000094; para 0,00005 haría falta dN ≈ 0,000054 cm, y la "
    "fila siguiente (61,7 g, dN 0,0001 cm) sí cuadra con 0,0001"
)

# ------------------------------------------------------------------ Chieregati 2017, Tabla 2
CHIEREGATI_K, CHIEREGATI_ALPHA = 3.9787, 1.6689  # IHL = K·d^α (Fig. 4 del artículo)
# etapa: (masa inicial g, masa final g, d cm, IHL, varianza, desviación %)
CHIEREGATI_ROWS = (
    ("1. Muestreo primario en la mina", 2_000_000.0, 20_000.0, 1.2, 5.39, "0.0003", "1.6"),
    ("2. Primera división", 20_000.0, 1_000.0, 1.2, 5.39, "0.0051", "7.2"),
    ("3. Segunda división", 1_000.0, 50.0, 1.2, 5.39, "0.1025", "32.0"),
    ("4. Pulverizado", 50.0, 50.0, 0.0106, 0.002, "0.0000", "0.0"),
)
CHIEREGATI_TOTAL = ("0.1079", "32.8")

# ------------------------------------------------------------------ Clifton 1969, Fig. 4
CLIFTON_PUBLISHED = {7: (-50.0, 100.0), 20: (-34.0, 54.0), 75: (-20.0, 25.0), 400: (-9.0, 10.0)}
CLIFTON_TOLERANCE = 2.0  # puntos porcentuales

# ------------------------------------------------------------------ Minnitt 2007
MINNITT_2007_C, MINNITT_2007_F, MINNITT_2007_G = 16_000_000.0, 0.5, 0.25
MINNITT_2007_ELL_PRINTED = 0.000035
MINNITT_2007_PRODUCT_IMPLIED = 448.0  # c·f·g·ℓ que reproduce los resultados publicados
MINNITT_2007_PRINTED = {"sigma2": 0.0875, "sigma_pct": 29.58, "mass_g": 16_015.0, "d_n_cm": 0.91}
MINNITT_2007_APPENDIX = {"sigma2": 0.105555, "sigma_pct": 32.49}


@dataclass(frozen=True)
class Check:
    source: str
    item: str
    published: float
    calculated: float
    unit: str
    ok: bool
    note: str = ""

    @property
    def difference(self) -> float:
        return self.calculated - self.published


def decimals_of(printed: str) -> int:
    """Decimales con que se imprime un valor publicado."""
    return len(printed.split(".")[1]) if "." in printed else 0


def matches_rounding(calculated: float, printed: str) -> bool:
    """¿El valor calculado cae en el redondeo del publicado (media unidad del último decimal)?"""
    half_unit = 0.5 * 10.0 ** (-decimals_of(printed))
    return abs(calculated - float(printed)) <= half_unit * (1 + 1e-9)


def minnitt_2017_checks() -> list[Check]:
    checks = []
    for method, rows in MINNITT_2017_ROWS.items():
        k, alpha = MINNITT_2017_CONSTANTS[method]
        for mass, d_n, printed in rows:
            calc = gy.variance_calibrated(k, alpha, d_n, mass)
            mass_text = f"{mass:,.2f}".replace(",", " ").rstrip("0").rstrip(".")
            item = f"{method}: {mass_text} g, dN {d_n:g} cm"
            ok = matches_rounding(calc, printed)
            note = "" if ok else ROW_NOTE
            checks.append(Check("Minnitt 2017, Tabla VIII", item, float(printed), calc,
                                "varianza relativa", ok, note))  # fmt: skip
    return checks


def chieregati_mineral() -> gy.Mineral:
    return gy.Mineral("Chieregati 2017 (cobre)", k=CHIEREGATI_K, alpha=CHIEREGATI_ALPHA)


def _chieregati(item: str, printed: str, calc: float, unit: str) -> Check:
    return Check("Chieregati 2017, Tabla 2", item, float(printed), calc, unit,
                 matches_rounding(calc, printed))  # fmt: skip


def chieregati_checks() -> list[Check]:
    mineral, total, checks = chieregati_mineral(), 0.0, []
    for name, m_in, m_out, d, ih_pub, var_printed, rsd_printed in CHIEREGATI_ROWS:
        ih = mineral.ih_l(d)
        variance = mineral.variance(d, m_out, m_in) if m_out < m_in else 0.0
        total += variance
        ih_printed = f"{ih_pub:.{3 if ih_pub < 1 else 2}f}"
        checks.append(_chieregati(f"{name}: IHL", ih_printed, ih, "g"))
        checks.append(_chieregati(f"{name}: varianza", var_printed, variance, "varianza relativa"))
        checks.append(
            _chieregati(f"{name}: desviación", rsd_printed, 100 * math.sqrt(variance), "%")
        )
    checks.append(_chieregati("Total: varianza", CHIEREGATI_TOTAL[0], total, "varianza relativa"))
    checks.append(
        _chieregati("Total: desviación", CHIEREGATI_TOTAL[1], 100 * math.sqrt(total), "%")
    )
    return checks


def clifton_checks() -> list[Check]:
    """Límites al 95 % con las ecuaciones (11) y (12) de Clifton frente a Fig. 4 (±2 puntos)."""
    checks = []
    for n, (lo, hi) in CLIFTON_PUBLISHED.items():
        e_lo, e_hi = (100 * v for v in oro.clifton_limits(n))
        x_lo, x_hi = (100 * v for v in oro.poisson_exact_limits(n))
        for label, pub, calc, exact in (("límite inferior", lo, e_lo, x_lo),
                                        ("límite superior", hi, e_hi, x_hi)):  # fmt: skip
            ok = abs(calc - pub) <= CLIFTON_TOLERANCE
            note = f"Poisson exacto (Garwood): {exact:+.1f} %"
            if not ok:
                note += "; la etiqueta de la Fig. 4 está redondeada"
            checks.append(Check("Clifton 1969, Fig. 4", f"{n} partículas, {label}", pub, calc,
                                "%", ok, note))  # fmt: skip
    return checks


def minnitt_2007_findings() -> list[Check]:
    """El hallazgo: con los datos impresos las cifras publicadas no salen (salen con 448)."""
    printed = gy.variance_classic(MINNITT_2007_C, MINNITT_2007_F, MINNITT_2007_G,
                                  MINNITT_2007_ELL_PRINTED, 1.25, 10_000.0)  # fmt: skip
    product = MINNITT_2007_C * MINNITT_2007_F * MINNITT_2007_G * MINNITT_2007_ELL_PRINTED
    ih = product
    mass_2 = gy.sample_mass(ih * 0.93**3, 0.0225)
    d_3 = gy.nominal_size(product, 3.0, 15_000.0, 0.0225)
    pub = MINNITT_2007_PRINTED
    note = "datos impresos: c = 16 000 000, f = 0,5, g = 0,25, ℓ = 0,000035"
    return [
        Check(
            "Minnitt 2007, problema 1",
            "varianza (dN 1,25 cm, 10 kg)",
            pub["sigma2"],
            printed,
            "varianza relativa",
            False,
            note,
        ),
        Check(
            "Minnitt 2007, problema 1",
            "error relativo",
            pub["sigma_pct"],
            100 * math.sqrt(printed),
            "%",
            False,
            note,
        ),
        Check(
            "Minnitt 2007, problema 2", "masa para 15 %", pub["mass_g"], mass_2, "g", False, note
        ),
        Check(
            "Minnitt 2007, problema 3",
            "dN para 15 % con 15 kg",
            pub["d_n_cm"],
            d_3,
            "cm",
            False,
            note,
        ),
        Check(
            "Minnitt 2007, factor implícito",
            "c·f·g·ℓ",
            MINNITT_2007_PRODUCT_IMPLIED,
            product,
            "g/cm³",
            False,
            "los resultados publicados implican 448 (ℓ efectivo 0,000224), 6,4 veces el impreso",
        ),
    ]


def minnitt_2007_implied() -> list[Check]:
    """Con c·f·g·ℓ = 448 (lo que implican los resultados) se reproducen los tres problemas: así
    se documenta la errata. No es una validación de la fórmula."""
    k448 = MINNITT_2007_PRODUCT_IMPLIED
    sigma2 = k448 * 1.25**3 / 10_000.0
    pub = MINNITT_2007_PRINTED
    note = "con c·f·g·ℓ = 448 (no es el valor impreso)"
    return [
        Check(
            "Minnitt 2007, problema 1",
            "varianza",
            pub["sigma2"],
            sigma2,
            "varianza relativa",
            abs(sigma2 - pub["sigma2"]) < 5e-5,
            note,
        ),
        Check(
            "Minnitt 2007, problema 1",
            "error relativo",
            pub["sigma_pct"],
            100 * math.sqrt(sigma2),
            "%",
            abs(100 * math.sqrt(sigma2) - pub["sigma_pct"]) < 0.01,
            note,
        ),
        Check(
            "Minnitt 2007, problema 2",
            "masa para 15 %",
            pub["mass_g"],
            k448 * 0.93**3 / 0.0225,
            "g",
            abs(k448 * 0.93**3 / 0.0225 - pub["mass_g"]) < 1.0,
            note,
        ),
        Check(
            "Minnitt 2007, problema 3",
            "dN para 15 % con 15 kg",
            pub["d_n_cm"],
            (15_000.0 * 0.0225 / k448) ** (1 / 3),
            "cm",
            abs((15_000.0 * 0.0225 / k448) ** (1 / 3) - pub["d_n_cm"]) < 0.005,
            note,
        ),
    ]


def minnitt_2007_liberation() -> list[Check]:
    """La parte del Apéndice que SÍ cuadra: dℓ = dN·ℓ^(1/b) = 1,25·(3,5e-5)^(1/1,5) y el
    despeje con 1 % de error."""
    d_lib = gy.liberation_size(1.25, MINNITT_2007_ELL_PRINTED, 1.5)
    c = 19_300_000.0
    second = (0.01 / (c * 0.5 * 0.25 / 10_000.0)) ** (1.0 / 1.5)
    return [
        Check(
            "Minnitt 2007, Apéndice",
            "dℓ = 1,25·(3,5e-5)^(1/1,5)",
            0.001337,
            d_lib,
            "cm",
            abs(d_lib - 0.001337) < 5e-7,
        ),
        Check(
            "Minnitt 2007, Apéndice",
            "dℓ para σ² = 0,01 con 10 kg",
            0.0011977,
            second,
            "cm",
            abs(second - 0.0011977) < 5e-7,
        ),
    ]
