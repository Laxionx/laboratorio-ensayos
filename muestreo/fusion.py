"""Fusión del ensayo al fuego, fase 2: la carga fundente.

Dada la mineralogía de la muestra y la alícuota, calcula qué carga (litargirio, carbonato de
sodio, bórax, sílice, harina o nitro) da un botón de plomo de 25 a 30 g y una escoria del grado de
silicato pedido, y evalúa una carga dada: el botón que daría, la escoria y los avisos (botón fuera
de 25-30 g, escoria demasiado ácida o básica, riesgo de mata).

Fuentes (dominio público): Bugbee (1922), *A Textbook of Fire Assaying*, cap. «The Crucible
Assay» (poder reductor y oxidante, grados de silicato, factores de escoria), y Haffty, Riley y
Goss (1977), USGS Bulletin 1445, *A Manual on Fire Assaying*. No es la receta de un laboratorio.

Reacciones (poder reductor = g de Pb que reduce 1 g de la sustancia con litargirio en exceso):
    2PbO + C = 2Pb + CO2            34,5 g/g de C; la harina trae menos (dato del laboratorio)
    2PbO + S = 2Pb + SO2            S → SO2 (sin carbonato alcalino)
    3PbO + S + Na2CO3 = 3Pb + Na2SO4 + CO2     S → SO3 (con carbonato alcalino)
    4KNO3 + 5C = 2K2O + 5CO2 + 2N2    poder oxidante teórico del nitro: 5,12 g de Pb por g
El poder reductor de un mineral sale de los electrones que entrega: cada átomo de Pb reducido
recibe 2 e⁻ (Pb²⁺ → Pb), así que Pb reducido = e⁻ del mineral / 2.

Grado de silicato = oxígeno del ácido / oxígeno de la base: mono 1, sesqui 1,5, bi 2, tri 3 (Tabla
XIX de Bugbee). 1 g de bórax vidrio equivale a 0,6 g de sílice (Bugbee, Tabla XXII).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from .fusion_avisos import Warning, charge_warnings
from .quimica import ATOMIC_WEIGHTS, PB, FusionError, M, molar_mass

AT_G = 29.1667  # 1 assay-ton, g
PB_DENSITY = 11.34  # g/cm³, plomo sólido (CRC Handbook)
FUSION_TEMP_C = 1050.0  # USGS Bulletin 1445: fusión preliminar a 1 050 °C
SLAG_DENSITY = 3.0  # g/cm³, SUPUESTO ilustrativo: Bugbee no da la densidad de la escoria
BORAX_SILICA_EQUIVALENT = 0.6  # g de SiO2 por g de bórax vidrio (Bugbee, Tabla XXII)
BUTTON_TARGET = 28.0  # g: «un botón de 28 g es suficiente como colector» (Bugbee)
SODA_SHARE = 0.6  # Bugbee: 3/5 de la sílice se funde con soda y 2/5 con litargirio
DEGREES = {"mono": 1.0, "sesqui": 1.5, "bi": 2.0}
DEGREE_NAMES = {0.5: "sub", 1.0: "mono", 1.5: "sesqui", 2.0: "bi", 3.0: "tri"}
SULFUR_MODES = ("SO2", "SO3")


# ------------------------------------------------------------------ poder reductor teórico
def pb_reduced_per_mol(s_atoms: float, s_state: float, extra_e: float, sulfur: str) -> float:
    """Átomos de Pb que reduce una unidad de fórmula: (S·(estado final − inicial) + e⁻ extra)/2.
    El estado final del azufre es +4 (SO2) o +6 (SO3)."""
    if sulfur not in SULFUR_MODES:
        raise FusionError(f"el azufre sale como SO2 o SO3: {sulfur!r}")
    final = 4 if sulfur == "SO2" else 6
    return (s_atoms * (final - s_state) + extra_e) / 2.0


@dataclass(frozen=True)
class MineralSpec:
    """Un mineral: fórmula, azufre y electrones, y qué deja en la escoria por unidad de fórmula."""

    key: str
    name: str
    formula: str
    s_atoms: float = 0.0
    s_state: float = 0.0  # estado de oxidación inicial del azufre
    extra_e: float = 0.0  # e⁻ que entregan (+) o reciben (−) los demás elementos
    slag: tuple[tuple[str, float], ...] = ()  # (óxido, moles) que quedan en la escoria
    lead: float = 0.0  # átomos de Pb metálico que ya trae (galena)
    copper: float = 0.0  # átomos de Cu por unidad de fórmula
    carbonate: float = 0.0  # moles de CO2 que suelta

    def reducing_power(self, sulfur: str) -> float:
        """g de Pb por g de mineral (negativo si oxida)."""
        n = pb_reduced_per_mol(self.s_atoms, self.s_state, self.extra_e, sulfur)
        return n * PB / molar_mass(self.formula)


MINERALS = (
    MineralSpec("cuarzo", "Cuarzo", "SiO2", slag=(("SiO2", 1.0),)),
    MineralSpec("calcita", "Calcita", "CaCO3", slag=(("CaO", 1.0),), carbonate=1.0),
    MineralSpec("hematita", "Hematita", "Fe2O3", extra_e=-2.0, slag=(("FeO", 2.0),)),
    MineralSpec("pirita", "Pirita", "FeS2", s_atoms=2, s_state=-1, slag=(("FeO", 1.0),)),
    MineralSpec(
        "pirrotita", "Pirrotita", "Fe7S8", s_atoms=8, s_state=-2, extra_e=-2.0, slag=(("FeO", 7.0),)
    ),
    MineralSpec(
        "calcopirita",
        "Calcopirita",
        "CuFeS2",
        s_atoms=2,
        s_state=-2,
        extra_e=-1.0,
        slag=(("FeO", 1.0), ("Cu2O", 0.5)),
        copper=1.0,
    ),
    MineralSpec("esfalerita", "Esfalerita", "ZnS", s_atoms=1, s_state=-2, slag=(("ZnO", 1.0),)),
    MineralSpec("galena", "Galena", "PbS", s_atoms=1, s_state=-2, lead=1.0),
    MineralSpec(
        "arsenopirita",
        "Arsenopirita",
        "FeAsS",
        s_atoms=1,
        s_state=-1,
        extra_e=4.0,
        slag=(("FeO", 1.0),),
    ),
)
BY_KEY = {m.key: m for m in MINERALS}
EXTRA_MINERALS = (  # solo para la tabla de poderes reductores de Bugbee
    MineralSpec(
        "calcocita", "Calcocita", "Cu2S", s_atoms=1, s_state=-2, slag=(("Cu2O", 1.0),), copper=2.0
    ),
    MineralSpec("estibina", "Estibina", "Sb2S3", s_atoms=3, s_state=-2),
)


def reducing_power(formula_key: str, sulfur: str = "SO3") -> float:
    spec = {m.key: m for m in (*MINERALS, *EXTRA_MINERALS)}.get(formula_key)
    if spec is None:
        raise FusionError(f"mineral desconocido: {formula_key!r}")
    return spec.reducing_power(sulfur)


# ------------------------------------------------------------------ neutralización de bases
def silica_per_base(base: str, degree: float = 2.0) -> float:
    """g de SiO2 que neutraliza 1 g de una base (óxido o carbonato de un metal bivalente o de
    Na2CO3, K2CO3: un O básico por fórmula) para el grado de silicato dado."""
    moles_o = {"NaHCO3": 0.5}.get(base, 1.0)  # 2 NaHCO3 dan un Na2O
    return moles_o * degree / 2.0 * M["SiO2"] / molar_mass(base)


def borax_per_base(base: str, degree: float = 2.0) -> float:
    """g de bórax vidrio que neutraliza 1 g de la base (equivalencia 0,6 g de SiO2 por g)."""
    return silica_per_base(base, degree) / BORAX_SILICA_EQUIVALENT


def classify(degree: float) -> str:
    """Nombre del grado de silicato más cercano (sub, mono, sesqui, bi, tri)."""
    nearest = min(DEGREE_NAMES, key=lambda d: abs(d - degree))
    return DEGREE_NAMES[nearest]


# ------------------------------------------------------------------ carga y resultado
@dataclass(frozen=True)
class FusionParams:
    sample_g: float
    minerals: dict[str, float]  # % en masa por mineral (suma ≤ 100; el resto es inerte)
    sulfur: str = "SO3"
    button_g: float = BUTTON_TARGET
    degree: float = DEGREES["bi"]
    flour_rp: float = 11.0  # DATO del laboratorio: Bugbee 10-12 (en sus ejemplos usa 12)
    niter_op: float = 4.1  # DATO del laboratorio: Bugbee 4,0-4,2 con su tipo de carga
    soda_per_g: float = 1.0  # Bugbee: la soda pesa al menos lo que la muestra
    # Bugbee, carga de 1 A.T.: 70 g de litargirio en total, 30 para el botón
    litharge_slag_per_g: float = 1.4
    borax_fraction: float = 1.0 / 3.0  # Bugbee: reemplazar 1/4 a 1/3 de la sílice por bórax
    borax_min_g: float = 5.0  # Bugbee: mínimo de 5 g de bórax vidrio
    lodge_excess: float = 0.20  # Lodge (en Bugbee): 15 a 25 % de litargirio sobre el del reductor


@dataclass(frozen=True)
class Reagents:
    soda_g: float
    litharge_g: float
    borax_g: float
    silica_g: float
    flour_g: float
    niter_g: float

    def scaled(self, flour: float = 1.0, silica: float = 1.0, litharge: float = 1.0) -> Reagents:
        return replace(
            self,
            flour_g=self.flour_g * flour,
            silica_g=self.silica_g * silica,
            litharge_g=self.litharge_g * litharge,
        )


@dataclass(frozen=True)
class SlagResult:
    components_g: dict[str, float]
    acid_o: float  # moles de O del ácido (SiO2 y bórax equivalente)
    base_o: float  # moles de O de la base

    @property
    def mass_g(self) -> float:
        return sum(self.components_g.values())

    @property
    def degree(self) -> float:
        return self.acid_o / self.base_o if self.base_o > 0 else math.inf

    @property
    def label(self) -> str:
        return classify(self.degree) if math.isfinite(self.degree) else "sin base"


@dataclass(frozen=True)
class ChargeResult:
    params: FusionParams
    reagents: Reagents
    ore_pb_g: float  # g de Pb que reduce (+) u oxida (−) la muestra por sí sola
    flour_pb_g: float
    niter_pb_g: float  # negativo: lo que oxida
    potential_pb_g: float
    button_g: float
    lead_from_litharge_g: float
    slag: SlagResult
    gas_mol: dict[str, float]
    warnings: tuple[Warning, ...]
    sulfur_mol: float
    copper_pct: float
    soda_for_sulfate_g: float = field(default=0.0)

    @property
    def reduced_pb_g(self) -> float:
        """g de Pb que se reducen de la litharge o del mineral: lo que se dibuja como gotas."""
        return self.button_g

    @property
    def button_cm3(self) -> float:
        return self.button_g / PB_DENSITY

    @property
    def slag_cm3(self) -> float:
        return self.slag.mass_g / SLAG_DENSITY


def _check(p: FusionParams) -> dict[str, float]:
    if not (math.isfinite(p.sample_g) and p.sample_g > 0):
        raise FusionError("la masa de la muestra debe ser positiva")
    unknown = sorted(set(p.minerals) - set(BY_KEY))
    if unknown:
        raise FusionError(f"minerales desconocidos: {', '.join(unknown)}")
    pct = {k: float(v) for k, v in p.minerals.items()}
    if any(not math.isfinite(v) or v < 0 for v in pct.values()):
        raise FusionError("los porcentajes deben ser números no negativos")
    total = sum(pct.values())
    if total > 100.0 + 1e-9:
        raise FusionError(f"los minerales suman {total:.1f} %: no pueden pasar de 100 %")
    if not (math.isfinite(p.button_g) and p.button_g > 0):
        raise FusionError("el botón pedido debe ser positivo")
    if p.degree <= 0 or p.flour_rp <= 0 or p.niter_op <= 0:
        raise FusionError(
            "el grado de silicato y los poderes de la harina y del nitro deben ser > 0"
        )
    if p.sulfur not in SULFUR_MODES:
        raise FusionError(f"el azufre sale como SO2 o SO3: {p.sulfur!r}")
    return pct


def _grams(p: FusionParams, pct: dict[str, float]) -> dict[str, float]:
    return {k: p.sample_g * v / 100.0 for k, v in pct.items() if v > 0}


def _ore_summary(p: FusionParams, pct: dict[str, float]) -> dict:
    """Lo que la muestra aporta: Pb que reduce, óxidos que deja, azufre, Pb propio y CO2."""
    grams = _grams(p, pct)
    oxides: dict[str, float] = {}
    out = {"pb": 0.0, "sulfur_mol": 0.0, "lead_g": 0.0, "co2_mol": 0.0, "copper_g": 0.0}
    for key, g in grams.items():
        spec = BY_KEY[key]
        moles = g / molar_mass(spec.formula)
        out["pb"] += g * spec.reducing_power(p.sulfur)
        out["sulfur_mol"] += moles * spec.s_atoms
        out["lead_g"] += moles * spec.lead * PB
        out["co2_mol"] += moles * spec.carbonate
        out["copper_g"] += moles * spec.copper * ATOMIC_WEIGHTS["Cu"]
        for oxide, n in spec.slag:
            oxides[oxide] = oxides.get(oxide, 0.0) + moles * n
    inert = p.sample_g * max(0.0, 100.0 - sum(pct.values())) / 100.0
    out["oxides_mol"] = oxides
    out["inert_g"] = inert
    return out


def design_charge(p: FusionParams) -> Reagents:
    """Carga que da el botón pedido y una escoria del grado de silicato pedido."""
    pct = _check(p)
    ore = _ore_summary(p, pct)
    need = p.button_g - ore["pb"]  # Pb que debe reducir (+) o impedir (−) el resto de la carga
    flour = max(0.0, need) / p.flour_rp
    niter = max(0.0, -need) / p.niter_op
    pbo_reduced = max(0.0, p.button_g - ore["lead_g"]) * M["PbO"] / PB
    pbo_slag = p.litharge_slag_per_g * p.sample_g
    litharge = pbo_reduced + pbo_slag
    if ore["sulfur_mol"] > 0:  # Lodge: 15 a 25 % de litargirio sobre el que pide el reductor
        litharge = max(litharge, pbo_reduced * (1.0 + p.lodge_excess))
    sulfate_soda = ore["sulfur_mol"] * M["Na2CO3"] if p.sulfur == "SO3" else 0.0
    soda_flux = p.soda_per_g * p.sample_g
    quartz = ore["oxides_mol"].get("SiO2", 0.0)  # moles de SiO2 de la muestra
    mineral_base = sum(n for ox, n in ore["oxides_mol"].items() if ox != "SiO2")

    def silica_needed(soda_g: float) -> float:
        base_mol = mineral_base + soda_g / M["Na2CO3"] + (litharge - pbo_reduced) / M["PbO"]
        return base_mol * p.degree / 2.0 * M["SiO2"]  # g de SiO2 (o equivalente) que pide

    borax = p.borax_min_g
    for _ in range(3):  # el bórax depende de la sílice y la sílice, del bórax
        need_g = silica_needed(soda_flux)
        add = need_g - quartz * M["SiO2"]
        borax = max(p.borax_min_g, p.borax_fraction * max(0.0, add) / BORAX_SILICA_EQUIVALENT)
    silica = silica_needed(soda_flux) - quartz * M["SiO2"] - borax * BORAX_SILICA_EQUIVALENT
    if silica < 0:  # muestra muy silícea: primero menos bórax y, si no alcanza, más soda
        borax_cut = min(borax - p.borax_min_g, -silica / BORAX_SILICA_EQUIVALENT)
        borax -= borax_cut
        silica += borax_cut * BORAX_SILICA_EQUIVALENT
    if silica < 0:  # falta base: Bugbee reparte la sílice 3/5 con soda y 2/5 con litargirio
        extra_mol = -silica / (M["SiO2"] * p.degree / 2.0)
        soda_flux += SODA_SHARE * extra_mol * M["Na2CO3"]
        litharge += (1.0 - SODA_SHARE) * extra_mol * M["PbO"]
        silica = 0.0
    return Reagents(soda_flux + sulfate_soda, litharge, borax, max(0.0, silica), flour, niter)


def evaluate_charge(p: FusionParams, r: Reagents) -> ChargeResult:
    """Botón, escoria y avisos de una carga dada (la calculada o una cambiada)."""
    pct = _check(p)
    ore = _ore_summary(p, pct)
    ore_pb, flour_pb, niter_pb = ore["pb"], r.flour_g * p.flour_rp, -r.niter_g * p.niter_op
    potential = ore_pb + flour_pb + niter_pb
    cap = ore["lead_g"] + r.litharge_g * PB / M["PbO"]  # el plomo que puede dar la carga
    button = min(max(potential, 0.0), cap)
    from_litharge = max(0.0, button - ore["lead_g"])
    pbo_left = r.litharge_g - from_litharge * M["PbO"] / PB
    sulfate_soda = ore["sulfur_mol"] * M["Na2CO3"] if p.sulfur == "SO3" else 0.0
    soda_flux = max(0.0, r.soda_g - sulfate_soda)
    ox = ore["oxides_mol"]
    comps = {
        "SiO2": r.silica_g + ox.get("SiO2", 0.0) * M["SiO2"],
        "Na2B4O7": r.borax_g,
        "Na2O": soda_flux / M["Na2CO3"] * M["Na2O"],
        "PbO": pbo_left,
        "Na2SO4": min(r.soda_g, sulfate_soda) / M["Na2CO3"] * M["Na2SO4"],
        "inerte": ore["inert_g"],
    }
    for oxide in ("CaO", "FeO", "ZnO", "Cu2O"):
        if oxide in ox:
            comps[oxide] = ox[oxide] * M[oxide]
    acid_o = 2.0 * (comps["SiO2"] / M["SiO2"] + r.borax_g * BORAX_SILICA_EQUIVALENT / M["SiO2"])
    base_o = (
        soda_flux / M["Na2CO3"] + pbo_left / M["PbO"] + sum(n for o, n in ox.items() if o != "SiO2")
    )
    slag = SlagResult({k: v for k, v in comps.items() if v > 0}, acid_o, base_o)
    carbon_mol = max(0.0, flour_pb) / (2 * PB) if r.flour_g > 0 else 0.0  # 2 Pb por cada C
    gas = {}
    gas["CO2"] = ore["co2_mol"] + r.soda_g / M["Na2CO3"] + carbon_mol
    gas["SO2"] = ore["sulfur_mol"] if p.sulfur == "SO2" else 0.0
    class2 = ore["pb"] >= p.button_g  # sulfuros de sobra: hace falta nitro (ensayo de la clase 2)
    warns = charge_warnings(
        p.sample_g,
        p.lodge_excess,
        r.litharge_g,
        r.soda_g,
        r.borax_g,
        ore,
        class2,
        potential,
        cap,
        button,
        slag.degree,
        from_litharge,
        pbo_left,
    )
    copper = ore["copper_g"] / p.sample_g * 100.0
    return ChargeResult(
        p,
        r,
        ore_pb,
        flour_pb,
        niter_pb,
        potential,
        button,
        from_litharge,
        slag,
        gas,
        tuple(warns),
        ore["sulfur_mol"],
        copper,
        sulfate_soda,
    )


def niter_for_button(ore_pb_g: float, button_g: float, niter_op: float) -> float:
    """g de nitro que impiden el plomo de más: (Pb de la muestra − botón) / poder oxidante."""
    if niter_op <= 0:
        raise FusionError("el poder oxidante del nitro debe ser positivo")
    return max(0.0, ore_pb_g - button_g) / niter_op


def design_and_evaluate(p: FusionParams) -> ChargeResult:
    return evaluate_charge(p, design_charge(p))
