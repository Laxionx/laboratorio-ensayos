"""Avisos de una carga de fusión. Cada umbral lleva su cita (Bugbee 1922 o USGS Bulletin 1445);
si no hay umbral publicado, se rotula «umbral supuesto»."""

from __future__ import annotations

from dataclasses import dataclass

from .quimica import PB, M

BUTTON_RANGE = (25.0, 30.0)  # g: no menos de 25 (Bugbee); sobre 30 se escorifica antes de copelar
SULFIDE_SLAG_LIMIT = 1.5  # umbral supuesto: «cerca del mono-silicato» (Bugbee) para sulfuros
ACTIVE_FLUX_RATIO = 2.5  # Bugbee: al menos 2,5 veces de fundente activo que de muestra
HIGH_SULFUR_FRACTION = 0.25  # umbral supuesto de azufre alto en la muestra (en masa)
COPPER_INCREASE_PCT = 2.0  # USGS 1445: Cu de 2 a 5 % ⇒ aumentar todo el fundente
COPPER_HIGH_PCT = 5.0  # umbral supuesto de cobre alto para el criterio de Perkins
PERKINS_MIN_RATIO = 137.0  # Perkins (en Bugbee): 137 a 300 partes de PbO por parte de Cu
S_MOLAR = 32.06


@dataclass(frozen=True)
class Warning:
    level: str  # "aviso" | "riesgo"
    text: str
    source: str  # cita, o «umbral supuesto»
    code: str = ""  # clave estable del aviso: la app lo traduce con sus argumentos
    args: tuple[tuple[str, float], ...] = ()  # (nombre, valor) de los números del texto


def charge_warnings(
    sample_g: float,
    lodge_excess: float,
    litharge_g: float,
    soda_g: float,
    borax_g: float,
    ore: dict,
    class2: bool,
    potential: float,
    cap: float,
    button: float,
    degree: float,
    from_litharge: float,
    pbo_left: float,
) -> list[Warning]:
    """Avisos de botón, escoria y mata para una carga ya evaluada."""
    warns: list[Warning] = []
    lo, hi = BUTTON_RANGE
    if button < lo:
        warns.append(
            Warning("aviso", f"Botón de {button:.1f} g: menor de {lo:g} g, colector chico.",
                    "Bugbee 1922: «no menos de 25 g» de plomo",
                    "button_low", (("button", button), ("lo", lo)))
        )  # fmt: skip
    elif button > hi:
        warns.append(
            Warning("aviso", f"Botón de {button:.1f} g: mayor de {hi:g} g; conviene escorificarlo "
                    "antes de copelar.", "Bugbee 1922, notas del ensayo",
                    "button_high", (("button", button), ("hi", hi)))
        )  # fmt: skip
    if degree < 1.0 - 1e-9:
        warns.append(
            Warning("aviso", f"Escoria más básica que mono-silicato ({degree:.2f}): ataca el "
                    "crisol.", "Bugbee 1922, Tabla XIX y texto",
                    "slag_basic", (("degree", degree),))
        )  # fmt: skip
    elif degree > 3.0 + 1e-9:
        warns.append(
            Warning("aviso", f"Escoria más ácida que tri-silicato ({degree:.2f}): viscosa y fuera "
                    "de los límites de las escorias de ensayo.", "Bugbee 1922, Tabla XIX",
                    "slag_acid", (("degree", degree),))
        )  # fmt: skip
    if class2 and degree > SULFIDE_SLAG_LIMIT:
        warns.append(
            Warning("riesgo", f"Con tanto sulfuro la escoria conviene cerca del mono-silicato y "
                    f"esta es de grado {degree:.2f}: riesgo de mata.",
                    f"Bugbee 1922: mono-silicato; umbral supuesto {SULFIDE_SLAG_LIMIT}",
                    "matte_slag", (("degree", degree), ("limit", SULFIDE_SLAG_LIMIT)))
        )  # fmt: skip
    if potential > cap + 1e-9:
        warns.append(
            Warning("riesgo", "El reductor pide más litargirio del que hay: queda azufre o "
                    "reductor sin oxidar y se forma una mata.", "Bugbee 1922, notas del ensayo",
                    "reductant_excess")
        )  # fmt: skip
    needed = from_litharge * M["PbO"] / PB
    if ore["sulfur_mol"] > 0 and needed > 0 and litharge_g < needed * (1.0 + lodge_excess - 0.05):
        warns.append(
            Warning("riesgo", "Litargirio sin el exceso del 15 al 25 % que piden los sulfuros: "
                    "riesgo de mata.", "Lodge, citado por Bugbee 1922", "lodge_excess")
        )  # fmt: skip
    active = soda_g + borax_g + pbo_left
    if active < ACTIVE_FLUX_RATIO * sample_g:
        warns.append(
            Warning("aviso", f"Fundente activo de {active:.0f} g: menos de {ACTIVE_FLUX_RATIO:g} "
                    "veces la muestra.", "Bugbee 1922: al menos 2,5 veces de fundente activo",
                    "active_flux", (("active", active), ("ratio", ACTIVE_FLUX_RATIO)))
        )  # fmt: skip
    copper_pct = ore["copper_g"] / sample_g * 100.0
    if copper_pct >= COPPER_INCREASE_PCT:
        warns.append(
            Warning("aviso", f"Cobre de {copper_pct:.1f} %: conviene aumentar todos los "
                    "componentes del fundente.", "USGS Bulletin 1445: Cu de 2 a 5 %",
                    "copper", (("copper", copper_pct),))
        )  # fmt: skip
    if copper_pct >= COPPER_HIGH_PCT and pbo_left < PERKINS_MIN_RATIO * ore["copper_g"]:
        warns.append(
            Warning("riesgo", "Poco litargirio libre para tanto cobre (Perkins pide 137 a 300 "
                    "partes de PbO por parte de Cu).",
                    f"Perkins, citado por Bugbee 1922; umbral supuesto de cobre alto: "
                    f"{COPPER_HIGH_PCT:g} %", "perkins", (("limit", COPPER_HIGH_PCT),))
        )  # fmt: skip
    if ore["sulfur_mol"] * S_MOLAR / sample_g > HIGH_SULFUR_FRACTION:
        warns.append(
            Warning("riesgo", "Más de 25 % de azufre: mucha mata posible y mucho nitro.",
                    "umbral supuesto", "high_sulfur")
        )  # fmt: skip
    return warns
