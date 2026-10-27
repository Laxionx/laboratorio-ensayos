"""English texts of the Protocol, Coarse gold and Validation tabs (phase 1), of their charts and
of the aliquot diagram."""

T = {
    "page.title": "Metallurgical test and fire-assay laboratory",
    "app.title": "Metallurgical test and fire-assay laboratory",
    "app.caption": "Laboratory metallurgical tests besides the fire assay: sampling error, the flux charge, cyanide leaching, the settling test that sizes a thickener and the laboratory's quality control (CRMs, duplicates and blanks). How much sampling error each preparation stage adds and how many gold grains fall in the aliquot, using Gy's equation validated against published figures. Includes the fusion flux charge (phase 2) and cupellation with parting (phase 3). Start with the **Guide**; change the inputs in the sidebar. Public ALS preparation codes; no affiliation.",
    "err.generic": "Something went wrong. Try other inputs or reload the page.",
    "toggle.label": "Animate",
    "toggle.help": 'Turns off the crucible animation (Fusion tab) and the cupel animation (Cupellation tab), the beaker animation (Cyanide leach test tab) and the cylinder and thickener animation (Settling test tab). It also turns off on its own if the system has "reduce motion" enabled. Drawing only: no number depends on it.',
    "tab.guide": "Guide",
    "tab.protocol": "Protocol",
    "tab.gold": "Coarse gold",
    "tab.fusion": "Fusion",
    "tab.validation": "Validation",
    "err.protocol": "The protocol could not be calculated with these inputs: {exc}",
    "err.gold": "The gold could not be calculated with these inputs: {exc}",
    "p.total": "Total protocol error",
    "p.worst": "Largest contributing stage",
    "p.worst.value": "Stage {n}",
    "p.worst.delta": "{pct} of the variance",
    "p.last": "Last split error",
    "p.safe": "All splits within safety",
    "p.safe.delta": "safety limit {pct} %",
    "p.info": "This protocol uses its own masses and sizes (Minnitt 2017, Table VIII); the received mass, the aliquot and the slope m have no effect.",
    "p.mineral": "Mineral: {name}. ",
    "p.mineral.note": "K and α are the values Minnitt (2017) calibrated for a Witwatersrand gold ore; they do not apply to other minerals.",
    "p.nomo.caption": 'Each horizontal leg reduces size (constant mass); each vertical leg splits (constant size). The straight lines are constant-error lines: the route must stay above the safety line. "Play" walks through the stages. The initial size only draws the first leg.',
    "p.col.stage": "Stage",
    "p.col.dn": "dN (cm)",
    "p.col.mass": "Mass in → out (g)",
    "p.col.var": "Relative variance",
    "p.col.err": "Stage error (%)",
    "p.col.cum": "Cumulative error (%)",
    "p.col.share": "Share of variance (%)",
    "p.cum.caption": "The cumulative error is the square root of the sum of the relative variances. Lot-mass correction: {corr}.",
    "p.corr.yes": "yes",
    "p.corr.no": "no (as in Minnitt's Table VIII)",
    "p.slope.caption": "The Rosin-Rammler slope m is an assumption. Between m = 0.5 and 3 the total error changes a lot because d95 enters cubed.",
    "g.grains": "Expected grains in the aliquot",
    "g.p0": "Probability of no grain",
    "g.median": "Median of the 1,000 assays",
    "g.median.delta": "true grade {grade} g/t",
    "g.above": "Assays above 2× the true grade",
    "g.sfa": "{lam} grains expected per aliquot, fewer than {n} (Clifton's criterion): use **screen fire assay** (about {mass} g sieved at {screen} µm, fines in duplicate and the coarse fraction whole).",
    "g.ok": "{lam} grains expected per aliquot: meets Clifton's criterion of {n} particles.",
    "g.caption1": "For {n} grains, {mass} g of sample would be needed. With {lam} grains, Clifton's 95 % limits are {lo} % and +{hi} % (exact Poisson: {elo} % and +{ehi} %; with few grains Clifton's equations only hold approximately).",
    "g.caption2": 'The true grade (green) and the median of the simulated assays (red) differ: with few grains, most assays give less than the true grade and a few give much more. "Play" accumulates from 10 to 1,000 assays.',
    "g.alt": "Three aliquots with gold grains",
    "g.grain": "{size} µm grain ({shape}): {mass} µg.",
    "v.intro": "Each source is calculated with Gy's equation and compared with what it publishes. Mismatches are shown as they are.",
    "v.col.source": "Source",
    "v.col.concept": "Item",
    "v.col.published": "Published",
    "v.col.calculated": "Calculated",
    "v.col.unit": "Unit",
    "v.col.fits": "Matches?",
    "v.col.note": "Note",
    "v.yes": "yes",
    "v.no": "no",
    "v.s1": "Minnitt 2017, Table VIII",
    "v.s2": "Chieregati 2017, Table 2",
    "v.s3": "Clifton 1969, Fig. 4",
    "v.s4": "Minnitt 2007, problems 1 to 3 and appendix",
    "v.s5": "Minnitt 2007 with c·f·g·ℓ = 448",
    "v.s6": "Minnitt 2007, appendix (dℓ)",
    "v.p1": "19 variances per stage (DSA and SFA)",
    "v.p2": "variance and error of 4 stages",
    "v.p3": "95 % limits for 7, 20, 75 and 400 particles",
    "v.p4": "29.58 %, ≈16 kg and 0.9 cm",
    "v.p5": "the same",
    "v.p6": "dℓ = 0.001337 cm and 0.0011977 cm",
    "v.f1": "{n} of {m} rows",
    "v.f2": "{n} of {m}",
    "v.f3": "{n} of {m} limits (±2 points)",
    "v.f4": "{n} of 4 with the printed data (erratum in the paper)",
    "v.f5": "{n} of {m}",
    "v.f6": "{n} of {m}",
    "v.h.m17": "#### Minnitt (2017), Table VIII: variance per stage",
    "v.h.chi": "#### Chieregati (2017), Table 2: copper protocol",
    "v.h.cli": "#### Clifton and co-authors (1969), Fig. 4: 95 % limits",
    "v.h.m07": "#### Minnitt, Rice and Spangenberg (2007): a finding, not a validation",
    "v.m07.printed": "**With the printed data** (c = 16,000,000, f = 0.5, g = 0.25, ℓ = 0.000035):",
    "v.m07.implied": "**With c·f·g·ℓ = 448**, the value implied by the published results (documents the erratum; does not validate the formula):",
    "v.m07.lib": "**The part of the appendix that does match:**",
    "plot.play": "▶ Play",
    "plot.pause": "⏸ Pause",
    "plot.nomo.error": "error {level} %",
    "plot.nomo.safety": " (safety)",
    "plot.nomo.route": "protocol route",
    "plot.nomo.current": "current point",
    "plot.nomo.hover": "dN %{x:.3g} cm, mass %{y:.3g} g<extra></extra>",
    "plot.nomo.note": "{k} of {n}: {label} (dN {d} cm, {m} g)",
    "plot.nomo.title": "Sampling nomogram (Gy): protocol route",
    "plot.nomo.x": "Nominal top size dN (cm)",
    "plot.nomo.y": "Sample mass (g)",
    "plot.stage.err": "stage error",
    "plot.stage.cum": "cumulative",
    "plot.stage.safety": "safety {pct} %",
    "plot.stage.title": "Error by stage and cumulative",
    "plot.stage.y": "Relative standard deviation (%)",
    "plot.sens.total": "total error",
    "plot.sens.chosen": "chosen m",
    "plot.sens.title": "Error depends on the slope m (assumption)",
    "plot.sens.x": "Rosin-Rammler slope m",
    "plot.sens.y": "Total protocol error (%)",
    "plot.gran.d95": "d95 = {mm} mm",
    "plot.gran.spec": "specification",
    "plot.gran.title": "Size distribution curves of the specifications (assumed shape)",
    "plot.gran.x": "Size (µm)",
    "plot.gran.y": "Cumulative passing (%)",
    "plot.hist.sim": "simulated assays",
    "plot.hist.hover": "%{x:.3g} g/t: %{y} assays<extra></extra>",
    "plot.hist.true": "true grade {grade} g/t",
    "plot.hist.median": "simulated median {median} g/t",
    "plot.hist.poisson": "analytical Poisson",
    "plot.hist.note": "{n} assays: median {median} g/t, maximum {max} g/t",
    "plot.hist.title": "Repeated assays of the same aliquot (Poisson, fixed seed)",
    "plot.hist.x": "Grade the assay would give (g/t)",
    "plot.hist.y": "Number of assays",
    "plot.val.exact": "exact match",
    "plot.val.fits": "matches the published rounding",
    "plot.val.nofit": "does not match",
    "plot.val.hover": "%{text}<br>published %{x}<br>calculated %{y:.5f}<extra></extra>",
    "plot.val.title": "Published vs calculated variance (Minnitt 2017 and Chieregati 2017)",
    "plot.val.x": "Published",
    "plot.val.y": "Calculated",
    "plot.cli.published": "published (Fig. 4)",
    "plot.cli.eqs": "equations (11) and (12)",
    "plot.cli.exact": "exact Poisson (Garwood)",
    "plot.cli.lower": "lower",
    "plot.cli.upper": "upper",
    "plot.cli.title": "95 % limits by particles per sample (Clifton 1969)",
    "plot.cli.x": "Particles per sample",
    "plot.cli.y": "Relative error (%)",
    "plot.m07.published": "published",
    "plot.m07.printed": "printed data (c·f·g·ℓ = 70)",
    "plot.m07.implied": "implied (c·f·g·ℓ = 448)",
    "plot.m07.title": "Minnitt 2007, problem 1: relative error (%)",
    "scheme.note": "illustrative diagram: grain counts come from the calculation",
    "svg.gold.title": "The same {mass} g aliquot, three simulated assays",
    "svg.gold.low": "low assay (10th percentile)",
    "svg.gold.median": "median assay",
    "svg.gold.high": "high assay (99th percentile)",
    "svg.gold.grain1": "{n} gold grain",
    "svg.gold.grains": "{n} gold grains",
    "svg.gold.grade": "implied grade: {grade} g/t (true {real} g/t)",
    "svg.gold.shown": "({n} drawn)",
    "svg.gold.foot": "{note}; the position of each grain is illustrative.",
    "svg.gold.label": "Three aliquots with different numbers of gold grains",
    # ------------------------------------------------------------ status, cases and "Try this"
    "estado.h": "#### Operation status",
    "estado.nivel.ok": "In range",
    "estado.nivel.aviso": "Warning",
    "estado.nivel.mal": "Problem",
    "estado.todo_ok": "Operation within range.",
    "estado.ver": "Show the {n} checks in range",
    "estado.ver1": "Show the check in range",
    "prueba.h": "#### Try this",
    "prueba.intro": (
        "Experiments that start from the **sidebar example**; the model computes the numbers live. "
        'The button puts the change into the inputs and "Back to the example" resets them.'
    ),
    "prueba.aplicar": "Apply this change to the controls",
    "prueba.restablecer": "Back to the example",
    "caso.h": "Published cases",
    "caso.intro": (
        "Each button puts the data of a published case in the sidebar and, while they are set, "
        "the tab shows the published value next to the calculated one (Δ = calculated − "
        "published)."
    ),
    "caso.activo": " (set)",
    "caso.col.pub": "Published",
    "caso.col.calc": "Calculated",
    "caso.col.delta": "Δ",
    # ------------------------------------------------------------ protocol: status and tests
    "prot.chk.seg.ok": (
        "All {n} splits are under the {seg} % safety error (the largest gives {max})."
    ),
    "prot.chk.seg.una": "stage {n} ({rsd})",
    "prot.chk.seg.mal": "Over the {seg} % safety error: {etapas}.",
    "prot.crit.seg": (
        "App criterion, not a standard: each split must give a relative error no larger than the "
        '"Nomogram safety error" control (the safety line of the nomogram).'
    ),
    "prot.chk.masas": "Each of the {n} splits takes less mass than it receives.",
    "prot.crit.masas": (
        "Definition of the calculation: a split takes MS from a larger mass ML (σ² = "
        "IHL·(1/MS − 1/ML)); otherwise the protocol is not computed and the tab says so."
    ),
    "prot.chk.kalpha.dado": (
        "K = {k} and α = {alpha} are the ones Minnitt (2017) calibrated for a Witwatersrand gold "
        "ore: they do not hold for another mineral."
    ),
    "prot.chk.kalpha.propio": "K = {k} and α = {alpha} are yours: they are calibrated per mineral.",
    "prot.crit.kalpha": (
        "Source: Minnitt (2017), J. SAIMM 117(2), for that ore; K and α are calibrated per "
        "mineral and never assumed (docstring of `gy.py` and the tab sheet)."
    ),
    "prot.chk.lote": (
        "Minnitt's (2017) Table VIII does not use the lot-mass correction: with it, the error "
        "comes out lower than the published one."
    ),
    "prot.crit.lote": (
        "Source: `gy.py` (Minnitt 2017 omits the correction in his Table VIII) and this app's "
        "validation, which reproduces it without the correction."
    ),
    "prot.caso.minnitt": "Minnitt (2017), Table VIII, DSA method",
    "prot.caso.res": (
        "**Minnitt (2017), Table VIII, DSA method.** Relative variance of each split against the "
        "printed one (K = 167.4 and α = 1.123, no lot-mass correction)."
    ),
    "prot.exp.division.titulo": "Split more mass after crushing",
    "prot.exp.division.texto": (
        "With PREP-31B ({m1} g are split instead of {m0} g after crushing to 2 mm) the total "
        "error drops from {t0} % to {t1} %, and stage 1 from {e0} % to {e1} %. Even so, the "
        "protocol still misses the {seg} % safety."
    ),
    "prot.exp.alicuota.titulo": "Move to a 50 g aliquot",
    "prot.exp.alicuota.texto": (
        "With {a1} g instead of {a0} g, the error of the last split drops from {l0} % to {l1} %, "
        "but the total hardly moves ({t0} % to {t1} %): stage 1 already contributes {s0} % of the "
        "variance and, with the larger aliquot, {s1} %. The bottleneck is before the aliquot."
    ),
    "prot.exp.lote.titulo": "Drop the lot-mass correction",
    "prot.exp.lote.texto": (
        "Without the 1/ML term, the total error rises from {t0} % to {t1} %: that is what "
        "Minnitt's (2017) Table VIII does. The correction is always on, except to reproduce that "
        "table."
    ),
    # ------------------------------------------------------------ coarse gold: status and tests
    "oro.crit.clifton": (
        "Source: Clifton, Hunter, Swanson and Phillips (1969), USGS Professional Paper 625-C: "
        "about {n} particles per sample for ±50 % at 95 %."
    ),
    "oro.chk.fig4.ok": (
        "With {lam} grains expected, the calculation is inside the range of {lo} to {hi} "
        "particles against which this app checks the Clifton equations."
    ),
    "oro.chk.fig4.mal": (
        "With {lam} grains expected, the calculation is outside the range of {lo} to {hi} "
        "particles against which this app checks the Clifton equations: read it next to the "
        "exact Poisson."
    ),
    "oro.crit.fig4": (
        "Source: the Validation tab checks the Clifton limits against the 1969 Fig. 4 for {lo} "
        "to {hi} particles (`validacion.py`, CLIFTON_PUBLISHED); outside that range there is no "
        "check."
    ),
    "oro.exp.grano100.titulo": "Grind the gold to 100 µm grains",
    "oro.exp.grano100.texto": (
        "With {g100} µm grains instead of {g0} µm, each grain weighs much less and the expected "
        "grains rise from {lam0} to {lam1} (×{ratio}): the probability of getting none drops from "
        "{p0} % to {p1} %. It is still under {n} grains and the panel keeps the warning."
    ),
    "oro.exp.alicuota.titulo": "Move to a 50 g aliquot",
    "oro.exp.alicuota.texto": (
        "With {a50} g instead of {a0} g, the expected grains rise from {lam0} to {lam1} (×{ratio}, "
        "proportional to the mass) and the probability of none drops from {p0} % to {p1} %. It is "
        "still under {n} grains: the panel keeps the warning."
    ),
    "oro.exp.grano50.titulo": "Grind the gold to 50 µm grains",
    "oro.exp.grano50.texto": (
        "With {g50} µm grains you expect {lam1} grains per aliquot: the {n}-particle criterion is "
        "met, the panel is in range, the probability of none falls to {p1} % and the median of "
        "the assays goes from {med0} to {med1} g/t, closer to the true grade ({ley} g/t)."
    ),
    "vi.ok": "Match the published",
    "vi.ok.help": (
        "Checks that match the published figure, summed over all the areas of this tab. In the "
        'flux charge only the "matches" verdict counts.'
    ),
    "vi.no": "Do not match",
    "vi.no.help": "Those that do not match; each table below says which and why.",
    "vi.areas": "Areas validated",
    "vi.areas.help": (
        "Gy equation, flux charge, cyanide leaching, settling, cupellation and quality control."
    ),
}
