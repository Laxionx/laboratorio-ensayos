"""English texts of the Fusion tab: metrics, warnings, crucible and phase-2 validation."""

T = {
    "f.err.sum": "The minerals add up to {total} %: they cannot exceed 100 %. Lower one.",
    "f.err.calc": "The charge could not be calculated with these data: {exc}",
    "f.minerals": "Minerals: {total} % (the remaining {rest} % is inert). ",
    "f.codes": (
        "The charge is a reagent calculation from the mineralogy and the texts of Bugbee (1922) "
        "and the USGS (1977): it is not any laboratory's recipe."
    ),
    "f.m.button": "Lead button",
    "f.m.button.delta": "requested {x} g",
    "f.m.slag": "Slag",
    "f.m.degree": "Silicate degree",
    "f.m.flour": "Flour in the charge",
    "f.m.niter": "Niter in the charge",
    "f.info.changed": (
        "You are trying a changed charge: the button and the slag are those of the changed "
        "charge, not of the calculated one."
    ),
    "f.warn.range": "The {button} g button falls outside {lo} to {hi} g.",
    "f.warn.line": "**{level}:** {text} _(Source: {source})_",
    "f.level.aviso": "Warning",
    "f.level.riesgo": "Risk",
    "f.alt": "Conical crucible with the liquid lead at the bottom and the slag on top",
    "f.caption": (
        "The lead is liquid during the fusion: {lead} cm³ at {rho} g/cm³ (1,050 °C), a pool at "
        "the bottom of the cone; on top, the slag with {slag} cm³ (assumed density of {slag_rho} "
        "g/cm³, Bugbee does not give it). The cold button measures {cold} cm³ (solid, 11.34 "
        "g/cm³). The crucible dimensions are illustrative; its capacity, 190 cm³, is that of "
        "Bugbee's 20 g crucible. The drops and the bubbles are illustrative too."
    ),
    "r.soda": "Soda (Na₂CO₃)",
    "r.litharge": "Litharge (PbO)",
    "r.borax": "Borax glass",
    "r.borax.formula": "Borax glass (Na₂B₄O₇)",
    "r.silica": "Silica (SiO₂)",
    "r.flour": "Flour",
    "r.niter": "Niter (KNO₃)",
    "f.col.reagent": "Reagent",
    "f.col.calc": "Calculated (g)",
    "f.col.used": "Used (g)",
    "f.min.mineral": "Mineral",
    "f.min.rp": "R.P. (g Pb/g)",
    "f.min.pb": "Pb (g)",
    "f.rp.head": "**Reducing power of the sample**",
    "f.rp.caption": "Sulfur oxidized to {sulfur}. Negative: it oxidizes (subtracts lead).",
    "f.slag.head": "**Slag composition**",
    "f.slag.component": "Component",
    "bal.muestra": "sample",
    "bal.harina": "flour",
    "bal.nitro": "niter",
    "bal.botón": "button",
    "bal.band": "25 to 30 g button",
    "bal.title": "Lead balance: what each part reduces or oxidizes (g of Pb)",
    "bal.y": "g of lead",
    "warn.button_low.text": "{button} g button: below {lo} g, a small collector.",
    "warn.button_low.source": "Bugbee 1922: «not less than 25 g» of lead",
    "warn.button_high.text": (
        "{button} g button: above {hi} g; it should be scorified before cupelling."
    ),
    "warn.button_high.source": "Bugbee 1922, notes on the assay",
    "warn.slag_basic.text": "Slag more basic than monosilicate ({degree}): it attacks the crucible.",
    "warn.slag_basic.source": "Bugbee 1922, Table XIX and text",
    "warn.slag_acid.text": (
        "Slag more acid than trisilicate ({degree}): viscous and outside the limits of assay slags."
    ),
    "warn.slag_acid.source": "Bugbee 1922, Table XIX",
    "warn.matte_slag.text": (
        "With this much sulfide the slag should be close to monosilicate and this one has "
        "degree {degree}: risk of matte."
    ),
    "warn.matte_slag.source": "Bugbee 1922: monosilicate; assumed threshold {limit}",
    "warn.reductant_excess.text": (
        "The reducer asks for more litharge than there is: unoxidized sulfur or reducer is left "
        "and a matte forms."
    ),
    "warn.reductant_excess.source": "Bugbee 1922, notes on the assay",
    "warn.lodge_excess.text": (
        "Litharge without the 15 to 25 % excess that sulfides call for: risk of matte."
    ),
    "warn.lodge_excess.source": "Lodge, cited by Bugbee 1922",
    "warn.active_flux.text": "Active flux of {active} g: less than {ratio} times the sample.",
    "warn.active_flux.source": "Bugbee 1922: at least 2.5 times as much active flux",
    "warn.copper.text": "Copper of {copper} %: all the flux components should be increased.",
    "warn.copper.source": "USGS Bulletin 1445: Cu from 2 to 5 %",
    "warn.perkins.text": (
        "Too little free litharge for this much copper (Perkins asks for 137 to 300 parts of "
        "PbO per part of Cu)."
    ),
    "warn.perkins.source": "Perkins, cited by Bugbee 1922; assumed high-copper threshold: {limit} %",
    "warn.high_sulfur.text": "More than 25 % sulfur: a lot of matte possible and a lot of niter.",
    "warn.high_sulfur.source": "assumed threshold",
    "warn.dry_over_capacity.text": (
        "The powder charge takes {vol} cm³ ({grams} g at {density} g/cm³): it exceeds the "
        "crucible capacity ({cap} cm³); it spills over. Use a larger crucible or a smaller "
        "charge."
    ),
    "warn.melt_over_capacity.text": (
        "The melt (lead and slag) takes {vol} cm³ (liquid lead plus slag): it exceeds the "
        "crucible capacity ({cap} cm³); it spills over. Use a larger crucible or a smaller "
        "charge."
    ),
    "warn.over_capacity.source": (
        "capacity: Bugbee 1922, Table IV (20 g = 190 cm³); powder density: assumed"
    ),
    "warn.dry_over_two_thirds.text": (
        "The powder charge takes {vol} cm³ ({grams} g at {density} g/cm³): it exceeds 2/3 of "
        "the crucible ({two_thirds} of {cap} cm³)."
    ),
    "warn.melt_over_two_thirds.text": (
        "The melt (lead and slag) takes {vol} cm³ (liquid lead plus slag): it exceeds 2/3 of "
        "the crucible ({two_thirds} of {cap} cm³)."
    ),
    "warn.over_two_thirds.source": (
        "Bugbee 1922: «never more than two-thirds full» (the 2/3 is by volume)"
    ),
    "svg.f.title": "Crucible in section during the fusion",
    "svg.f.label": "Conical crucible with the liquid lead at the bottom and the slag on top",
    "svg.f.charge": "Charge (g)",
    "svg.f.calc": "  (calculated {x})",
    "svg.f.lead": "Liquid lead: {mass} g · {vol} cm³ at {rho} g/cm³",
    "svg.f.cold": "Cold button: {mass} g · {vol} cm³ (solid, 11.34 g/cm³)",
    "svg.f.slag": "Slag: {mass} g · degree {label} ({degree})",
    "svg.f.slagvol": "Slag volume: {vol} cm³ (assumed density {rho} g/cm³)",
    "svg.f.dry": "Powder charge: {mass} g ≈ {vol} cm³ (assumed {rho} g/cm³); capacity {cap} cm³",
    "svg.f.drops": "Drops drawn: {drops} · bubbles: {bubbles}",
    "svg.f.limit": "2/3 of the capacity ({v} cm³)",
    "svg.f.legend": (
        "Illustrative conical crucible: radius of {r0} cm at the bottom and {r1} cm at the top, "
        "{h} cm high; its capacity, {cap} cm³, is that of Bugbee's 20 g crucible (Table IV). The "
        "lead is LIQUID and forms a pool at the bottom: volume = mass ÷ density of liquid lead "
        "at {temp} °C (OECD/NEA 2007). The slag fills the cone above it: volume = mass ÷ "
        "{slag_rho} g/cm³ (assumed). Lead drops: {per_g} per g reduced; CO₂ and SO₂ bubbles "
        "and their position: illustrative. Slag with the {note} at {temp} °C."
    ),
    "svg.f.foot": "diagram, not to scale: the quantities do come from the calculation",
    "scheme.temp": "illustrative color of the temperature",
    "fv.h": "### Phase 2: flux charge (Bugbee 1922 and USGS Bulletin 1445)",
    "fv.summary": (
        "{total} published figures: **{ok}** match with current atomic weights, **{weights}** "
        "match with Bugbee's weights, **{trunc}** are truncations of his and **{no}** do not "
        "match. They differ because Bugbee calculated by hand with rounded atomic weights (207 "
        "for Pb, 56 for Fe) and sometimes truncated instead of rounding; the Bugbee weights in "
        "this table are inferred from his own figures (the set that best reproduces them, "
        "declared in `fusion_pesos.py`) and the app always calculates with current weights. The "
        "figures of Table XX and Table XXI were also read on the scan image."
    ),
    "fv.h1": "#### Theoretical reducing and oxidizing powers",
    "fv.h2": "#### Neutralization of bases and flux tables",
    "fv.h3": "#### Bugbee's worked examples",
    "fv.h4": "#### Reducing powers measured by Bugbee (not a pass/fail threshold)",
    "fv.h5": "#### USGS 1445 charges evaluated with the calculator (informative)",
    "fv.h6": "#### USGS niter",
    "fv.col.concept": "Item",
    "fv.col.published": "Published",
    "fv.col.current": "Current weights",
    "fv.col.bugbee": "Bugbee's weights",
    "fv.col.verdict": "Verdict",
    "fv.col.diff": "Diff. (Bugbee)",
    "fv.col.unit": "Unit",
    "fv.col.note": "Note",
    "fv.m.mineral": "Mineral",
    "fv.m.so2": "Theoretical, S to SO₂",
    "fv.m.so3": "Theoretical, S to SO₃",
    "fv.m.measured": "Measured",
    "fv.m.diff": "Measured − SO₃",
    "fv.m.caption": (
        "Bugbee's test charge: 5 g of Na₂CO₃, 80 g of PbO, 2 g of SiO₂ and mineral for a button "
        "of about 25 g. Argols: 11.04 (subsilicate), 10.93 (mono), 10.62 (bi) and 9.26 (tri)."
    ),
    "fv.u.load": "Charge",
    "fv.u.button": "Button (g)",
    "fv.u.degree": "Degree",
    "fv.u.slag": "Slag",
    "fv.u.slag_g": "Slag (g)",
    "fv.u.caption": (
        "Flour of R.P. 10.5 (the USGS midpoint) and no sulfur. These are charges from the USGS "
        "manual (1977), not recipes; the USGS adds 0 to 12 g of CaF₂ that is not modeled here."
    ),
    "verdict.cuadra": "matches",
    "verdict.cuadra con los pesos de Bugbee": "matches with Bugbee's weights",
    "verdict.truncamiento de Bugbee": "Bugbee's truncation",
    "verdict.no cuadra": "does not match",
}
