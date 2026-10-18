"""Cortes de validación de la fase 2 (carga fundente) contra números publicados, fijados ANTES de
correr. Fuentes de dominio público:

- Bugbee (1922), *A Textbook of Fire Assaying* (texto OCR y escaneo de archive.org). Las cifras
  de la Tabla XX (poderes reductores) y de la Tabla XXI (factores de escoria) se leyeron también en
  la imagen del escaneo: coinciden con el OCR.
- Haffty, Riley y Goss (1977), USGS Bulletin 1445, *A Manual on Fire Assaying*.

Cortes:
1. Poderes reductores y oxidantes TEÓRICOS de Bugbee (carbono 34,5; hierro 3,70; azufre; pirita;
   nitro 5,12; columnas teóricas de la Tabla XX) y las neutralizaciones y tablas de fundentes
   (0,84 y 0,60 g de SiO2; 1,4 y 1,0 g de bórax; Tablas XXI y XXII): iguales al redondeo publicado
   (media unidad del último dígito impreso). Bugbee calculó a mano con pesos atómicos redondeados
   y a veces truncó: lo que no llega a media unidad se marca «a una unidad» o «no».
2. Ejemplos resueltos de Bugbee: soda y litargirio de 1 assay-ton de sílice pura (30,7 y 43,2 g),
   el de 50 % CaCO3 y 50 % SiO2 y el de CaCO3 puro, y la mezcla 3,5 : 0,5 : 6 (100 g con un botón
   de 28 g ⇒ aproximadamente bi-silicato, grado 2 ± 0,35; 125 g ⇒ aproximadamente
   sesqui-silicato, grado 1,5 ± 0,35).
3. Poderes reductores MEDIDOS de Bugbee: se muestran junto a los teóricos; NO son corte.
4. Cargas del USGS 1445: se evalúan con la calculadora; solo informativo. El cálculo del nitro del
   USGS (15 g × 5,00 − 30 g de botón ⇒ 10,7 g con 4,2) sí es corte.
"""

from __future__ import annotations

from . import fusion as fu
from .fusion_pesos import (
    VERDICTS,
    FusionCheck,
    dual,
    make_check,
)
from .validacion import Check, decimals_of, matches_rounding  # noqa: F401

_check = make_check

# Tabla XX: mineral -> (S a SO2, S a SO3, medido) como se imprime
TABLE_XX = {
    "galena": ("2.6", "3.46", "3.41"),
    "calcocita": ("3.9", "5.2", None),
    "arsenopirita": ("5.7", "6.96", "8.18"),
    "estibina": ("5.5", "7.35", "6.75"),
    "calcopirita": ("6.2", "8.44", "7.85"),
    "esfalerita": ("6.37", "8.5", "7.87"),
    "pirrotita": ("7.35", "9.9", "10.00"),
    "pirita": ("8.6", "12.07", "11.05"),
}
ARGOLS = {"sub": 11.04, "mono": 10.93, "bi": 10.62, "tri": 9.26}  # R.P. de unos argoles (Bugbee)
AT = fu.AT_G


def _spec(key: str) -> fu.MineralSpec:
    return {m.key: m for m in (*fu.MINERALS, *fu.EXTRA_MINERALS)}[key]


def theoretical_checks() -> list[FusionCheck]:
    """Poderes reductores y oxidantes teóricos, con pesos actuales y con los de Bugbee."""
    s, pyrite = "Bugbee 1922, poder reductor", "FeS2"
    t = "g Pb/g"
    checks = [
        dual(s, "carbono (2PbO + C)", "34.5", t, lambda w: 2 * w.pb / w.mm("C")),
        dual(s, "hierro (PbO + Fe)", "3.70", t, lambda w: w.pb / w.mm("Fe")),
        dual(s, "azufre a SO2", "12.9", t, lambda w: 2 * w.pb / w.mm("S")),
        dual(s, "azufre a SO3", "19.4", t, lambda w: 3 * w.pb / w.mm("S")),
        dual(s, "pirita, 5PbO (a SO2)", "8.6", t, lambda w: 5 * w.pb / w.mm(pyrite)),
        dual(
            s, "pirita, férrica (15PbO por 2FeS2)", "12.9", t, lambda w: 7.5 * w.pb / w.mm(pyrite)
        ),
        dual(s, "pirita, ferrosa (14PbO por 2FeS2)", "12.07", t, lambda w: 7 * w.pb / w.mm(pyrite)),
    ]
    for key, (so2, so3, _measured) in TABLE_XX.items():
        name = fu.BY_KEY[key].name if key in fu.BY_KEY else key.capitalize()
        spec = _spec(key)
        for printed, mode in ((so2, "SO2"), (so3, "SO3")):
            checks.append(
                dual(
                    "Bugbee 1922, Tabla XX",
                    f"{name}: S a {mode}",
                    printed,
                    t,
                    lambda w, spec=spec, mode=mode: w.rp(spec, mode),
                )
            )
    o = "Bugbee 1922, poder oxidante"
    checks += [
        dual(o, "nitro (4KNO3 + 5C)", "5.12", t, lambda w: 10 * w.pb / (4 * w.mm("KNO3"))),
        dual(o, "Fe2O3 (Fe2O3 + Pb)", "1.31", t, lambda w: w.pb / w.mm("Fe2O3")),
        dual(o, "MnO2 (MnO2 + Pb)", "2.4", t, lambda w: w.pb / w.mm("MnO2")),
        dual(o, "minio (Pb3O4 + Pb = 4PbO)", "0.30", t, lambda w: w.pb / w.mm("Pb3O4")),
    ]
    return checks


def neutralization_checks() -> list[FusionCheck]:
    s = "Bugbee 1922, Tablas XXI y XXII"
    sp = lambda base: lambda w: w.silica_per_base(base)  # noqa: E731
    checks = [
        dual(s, "1 g de FeO neutraliza (g de SiO2, bi-silicato)", "0.84", "g", sp("FeO")),
        dual(
            s,
            "1 g de FeO requiere (g de bórax vidrio)",
            "1.4",
            "g",
            lambda w: w.borax_per_base("FeO"),
        ),
        dual(s, "1 g de CaCO3 neutraliza (g de SiO2)", "0.60", "g", sp("CaCO3")),
        dual(
            s,
            "1 g de CaCO3 requiere (g de bórax vidrio)",
            "1.0",
            "g",
            lambda w: w.borax_per_base("CaCO3"),
        ),
    ]
    for label, mass, rows in (
        (
            "1 A.T. de SiO2",
            AT,
            (("PbO", "108"), ("Na2CO3", "51.2"), ("K2CO3", "66.8"), ("NaHCO3", "81.2")),
        ),
        (
            "10 g de SiO2",
            10.0,
            (("PbO", "37.0"), ("Na2CO3", "17.6"), ("K2CO3", "22.9"), ("NaHCO3", "27.9")),
        ),
    ):
        for base, printed in rows:
            checks.append(
                dual(
                    s,
                    f"Tabla XXI, {label}: {base} (bi-silicato)",
                    printed,
                    "g",
                    lambda w, m=mass, b=base: m / w.silica_per_base(b),
                )
            )
    t22 = (
        ("1 A.T. de FeO", "24.5", lambda w: AT * w.silica_per_base("FeO")),
        ("1 A.T. de CaCO3", "17.4", lambda w: AT * w.silica_per_base("CaCO3")),
        ("1 A.T. de MgCO3", "20.8", lambda w: AT * w.silica_per_base("MgCO3")),
        ("10 g de PbO", "2.7", lambda w: 10 * w.silica_per_base("PbO")),
        ("30 g de NaHCO3", "10.8", lambda w: 30 * w.silica_per_base("NaHCO3")),
        ("30 g de Na2CO3", "17.0", lambda w: 30 * w.silica_per_base("Na2CO3")),
        ("10 g de K2CO3", "4.4", lambda w: 10 * w.silica_per_base("K2CO3")),
    )
    for label, printed, fn in t22:
        note = ""
        if label == "1 A.T. de CaCO3":
            note = "su propio 0,60 g por g da 17,5; el 17,4 de la tabla es un redondeo suyo"
        checks.append(dual(s, f"Tabla XXII, sílice que piden {label}", printed, "g SiO2", fn, note))
    return checks


# ------------------------------------------------------------------ ejemplos resueltos
def bugbee_table_example() -> dict[str, float]:
    """El ejemplo de 1 A.T. de 50 % CaCO3 y 50 % SiO2 con los factores TABULADOS de Bugbee
    (Tabla XXII: 17,4 por A.T. de CaCO3; 17,0 por 30 g de soda; 2,7 por 10 g de PbO)."""
    ca = 0.5 * 17.4
    soda = 17.0
    litharge = 30.0 / 10.0 * 2.7
    total = ca + soda + litharge
    ore_silica = round(AT / 2.0, 1)  # 14,6: la mitad de un A.T.
    needed = total - ore_silica
    silica = needed * 2.0 / 3.0
    remainder = needed - silica
    return {
        "CaCO3": ca,
        "soda": soda,
        "litharge": litharge,
        "total": total,
        "ore_silica": ore_silica,
        "needed": needed,
        "silica": silica,
        "remainder": remainder,
        "borax": remainder / fu.BORAX_SILICA_EQUIVALENT,
    }


def example_checks() -> list[FusionCheck]:
    s = "Bugbee 1922, ejemplos resueltos"
    t = bugbee_table_example()
    checks = [
        _check(s, "50 % CaCO3: sílice del CaCO3 (0,5 × 17,4)", "8.7", t["CaCO3"], "g"),
        _check(s, "50 % CaCO3: sílice de la soda", "17.0", t["soda"], "g"),
        _check(s, "50 % CaCO3: sílice del litargirio", "8.1", t["litharge"], "g"),
        _check(s, "50 % CaCO3: total", "33.8", t["total"], "g"),
        _check(s, "50 % CaCO3: menos la sílice del mineral", "14.6", t["ore_silica"], "g"),
        _check(s, "50 % CaCO3: sílice o bórax necesarios", "19.2", t["needed"], "g"),
        _check(s, "50 % CaCO3: sílice (dos tercios)", "12.8", t["silica"], "g"),
        _check(s, "50 % CaCO3: resto a bórax (como sílice)", "6.4", t["remainder"], "g"),
        _check(s, "50 % CaCO3: bórax vidrio", "10.7", t["borax"], "g"),
    ]
    note = "calculadora (estequiometría actual); Bugbee usa su Tabla XXII"
    pure = lambda key: lambda w: w.design({"cuarzo": 100}, 0.0, 0.0, pure_split=True)[key]  # noqa: E731
    checks += [
        dual(
            s,
            "1 A.T. de sílice pura: soda (3/5 de la sílice)",
            "30.7",
            "g",
            pure("soda"),
            "calculadora",
        ),
        dual(
            s,
            "1 A.T. de sílice pura: litargirio para la escoria",
            "43.2",
            "g",
            pure("litharge slag"),
            "calculadora",
        ),
        dual(s, "1 A.T. de sílice pura: harina (R.P. 12)", "2.33", "g", pure("flour")),
    ]
    for tag, minerals, vals in (
        ("50 % CaCO3", {"cuarzo": 50, "calcita": 50}, ("10.7", "12.8", "60")),
        ("CaCO3 puro", {"calcita": 100}, ("23.6", "28.3", "60")),
    ):
        for label, key, printed in zip(
            ("bórax vidrio", "sílice", "litargirio"),
            ("borax", "silica", "litharge"),
            vals,
            strict=True,
        ):
            checks.append(
                dual(
                    s,
                    f"{tag}: carga calculada, {label}",
                    printed,
                    "g",
                    lambda w, m=minerals, k=key: w.design(m, 30.0, 30.0)[k],
                    note,
                )
            )
    return checks


def mixture_example(flux_g: float) -> fu.ChargeResult:
    """100 o 125 g de la mezcla 3,5 : 0,5 : 6 (soda : bórax : litargirio) por A.T. de cuarzo, con
    un botón de 28 g (harina de R.P. 12)."""
    params = fu.FusionParams(AT, {"cuarzo": 100}, flour_rp=12.0)
    reagents = fu.Reagents(0.35 * flux_g, 0.6 * flux_g, 0.05 * flux_g, 0.0, 28.0 / 12.0, 0.0)
    return fu.evaluate_charge(params, reagents)


MIXTURE_WINDOWS = {100.0: (2.0, 0.35, "bi"), 125.0: (1.5, 0.35, "sesqui")}  # (grado, ±, nombre)


def mixture_checks() -> list[FusionCheck]:
    s = "Bugbee 1922, mezcla 3,5 : 0,5 : 6"
    out = []
    for flux, (target, window, name) in MIXTURE_WINDOWS.items():
        degree = mixture_example(flux).slag.degree
        ok = abs(degree - target) <= window
        out.append(
            FusionCheck(
                s,
                f"{flux:g} g por A.T. de cuarzo: grado de silicato (≈ {name}-silicato)",
                target,
                degree,
                "grado",
                ok,
                f"corte: {target} ± {window}",
                ok,
            )
        )
    return out


# ------------------------------------------------------------------ medidos (no son corte)
def measured_rows() -> list[tuple[str, float, float, float | None, float | None]]:
    """(mineral, teórico SO2, teórico SO3, medido por Bugbee, diferencia medido − SO3)."""
    rows = []
    for key, (_, _, measured) in TABLE_XX.items():
        name = fu.BY_KEY[key].name if key in fu.BY_KEY else key.capitalize()
        so2, so3 = fu.reducing_power(key, "SO2"), fu.reducing_power(key, "SO3")
        m = None if measured is None else float(measured)
        rows.append((name, so2, so3, m, None if m is None else m - so3))
    return rows


# ------------------------------------------------------------------ USGS 1445
USGS_NITER_OP = 4.2  # g de Pb que oxida 1 g de nitro (USGS 1445)
USGS_FLOUR_RP = (10.0, 11.0)  # g de Pb por g de harina (USGS 1445, rango)


def usgs_niter_example() -> FusionCheck:
    """15 g de muestra de R.P. 5,00, botón de 30 g, nitro de 4,2 ⇒ 10,7 g (USGS 1445)."""
    calc = fu.niter_for_button(15.0 * 5.00, 30.0, USGS_NITER_OP)
    return _check("USGS 1445", "nitro para un botón de 30 g (15 g de R.P. 5,00)", "10.7", calc, "g")


# cargas del USGS (g): (muestra, soda, litargirio, sílice, bórax, harina), todas con 15 g
USGS_LOADS = {
    "Calcita (15 g)": ({"calcita": 100}, 20.0, 50.0, 14.0, 12.0, 3.0),
    "Cuarzo (15 g)": ({"cuarzo": 100}, 20.0, 40.0, 0.0, 3.0, 3.0),
    "Mitad calcita, mitad cuarzo (15 g)": (
        {"calcita": 50, "cuarzo": 50},
        20.0,
        45.0,
        7.0,
        8.0,
        3.0,
    ),
}


def usgs_load_rows() -> list[dict]:
    """Botón y grado de silicato que darían las cargas del USGS con la calculadora (INFORMATIVO;
    la harina usa el R.P. medio del USGS, 10,5)."""
    rows = []
    for name, (minerals, soda, pbo, silica, borax, flour) in USGS_LOADS.items():
        params = fu.FusionParams(15.0, minerals, flour_rp=sum(USGS_FLOUR_RP) / 2)
        result = fu.evaluate_charge(params, fu.Reagents(soda, pbo, borax, silica, flour, 0.0))
        rows.append(
            {
                "carga": name,
                "botón (g)": result.button_g,
                "grado": result.slag.degree,
                "escoria": result.slag.label,
                "escoria (g)": result.slag.mass_g,
            }
        )
    return rows


def all_checks() -> list[FusionCheck]:
    return (
        theoretical_checks()
        + neutralization_checks()
        + example_checks()
        + mixture_checks()
        + [usgs_niter_example()]
    )


def summary(checks: list[FusionCheck]) -> dict[str, int]:
    """Conteo por veredicto (ver `fusion_pesos`)."""
    out = {"total": len(checks)}
    for v in VERDICTS:
        out[v] = sum(c.fit == v for c in checks)
    return out
