"""English texts of the "Cupellation" tab, its inputs, data sheet, guide, scheme and validation
(keys `cp.*`, `svg.k.*`, `dato.k_*`, `ficha.copelacion.*`, `guide.*cop*`)."""

T = {
    "tab.cop": "Cupellation",
    "group.Copelación": "Cupellation",
    # ------------------------------------------------------------ sidebar inputs
    "opt.Del botón de la fusión": "From the fusion button",
    "opt.Valor propio": "Own value",
    "opt.Razón de Rose (según el oro)": "Rose ratio (by gold weight)",
    "opt.Mínimo de Bugbee (3 a 1)": "Bugbee minimum (3 to 1)",
    "opt.Razón propia": "Own ratio",
    "dato.k_temp.label": "Cupel temperature",
    "dato.k_temp.meaning": "Temperature of the cupel in the muffle, in °C. It is what matters most for the silver and gold loss.",
    "dato.k_temp.source": "measured with a pyrometer next to the cupel; Bugbee gives 700 to 775 °C with litharge crystals on the cupel, and Table IX goes up to 1,000 °C (the gold table, to 1,075 °C)",
    "dato.k_pb_src.label": "Lead for cupellation",
    "dato.k_pb_src.meaning": "Where the lead of the button comes from: the one the Fusion tab calculates (chains fusion and cupellation) or an own value.",
    "dato.k_pb_src.source": "it is the fusion button, weighed before cupelling",
    "dato.k_pb.label": "Own lead",
    "dato.k_pb.meaning": 'Mass of the lead button, in g (only if "Own value" is chosen).',
    "dato.k_pb.source": "weigh the button; Lodge's tables cover 10 to 25 g and the Fusion tab aims at 28 g",
    "dato.k_au.label": "Gold in the button",
    "dato.k_au.meaning": "Gold the button carries before cupelling, in mg. It sets the silver that has to be added.",
    "dato.k_au.source": "comes from the assay (grade times sample mass); Table XII was measured with 200 mg",
    "dato.k_ag.label": "Silver in the button",
    "dato.k_ag.meaning": "Silver the button already carries, in mg, without what is added for parting.",
    "dato.k_ag.source": "comes from the assay; Table XI covers 2 to 200 mg",
    "dato.k_modo.label": "Silver:gold ratio for parting",
    "dato.k_modo.meaning": "How the target ratio is chosen: Rose's by gold weight, Bugbee's minimum (3 to 1) or an own one.",
    "dato.k_modo.source": "Rose (Metallurgy of Gold, 6th ed., p. 511) and Bugbee (p. 118 and 121)",
    "dato.k_razon.label": "Own ratio",
    "dato.k_razon.meaning": 'Silver:gold ratio wanted after cupelling (only if "Own ratio" is chosen).',
    "dato.k_razon.source": "Bugbee: at least 3 to 1, and 8 to 10 to 1 in ore beads",
    "dato.k_ley.label": "Measured gold grade",
    "dato.k_ley.meaning": "Grade the assay gave, in g/t. It is corrected with the gold loss in the cupel.",
    "dato.k_ley.source": "it is the assay result before the correction",
    # ------------------------------------------------------------ data sheet and guide
    "ficha.copelacion.hace": (
        "Calculates how much gold and silver is lost in the cupel as a function of temperature, "
        "button lead and the silver present, corrects the measured grade for that loss and says "
        "how much silver has to be added (inquartation) so that parting in nitric acid works. It "
        "plots Bugbee's tables with the model on top and animates the lead button shrinking "
        "until the bead is left."
    ),
    "ficha.copelacion.entra": (
        "The cupel temperature, the button lead (the one from the Fusion tab or an own one), the "
        "gold and silver in the button, how the silver:gold ratio is chosen (Rose, Bugbee's "
        "minimum or own) and the measured gold grade."
    ),
    "ficha.copelacion.sale": (
        "The silver loss (with its band) and the gold loss, the corrected grade, the silver to "
        "add, the ratio at parting with its verdict (insufficient, rolled sheet only, slow or good), the mass and "
        "composition of the bead and a warning whenever an input leaves a table's range."
    ),
    "ficha.copelacion.autores": (
        "Losses, temperatures and parting ratios: Bugbee (1922), *A Textbook of Fire Assaying*, "
        "Tables IX to XII (pp. 100 to 103) and pp. 118 to 122 (public domain); the data are from "
        "Lodge (*Assaying*), Godshall (1896, Trans. AIME 26:473-484), Smith and Rose "
        "(*Metallurgy of Gold*), as Bugbee quotes them. The validation uses Godshall's original "
        "paper (public domain, archive.org). The progress in the animation is not from any table."
    ),
    "ficha.copelacion.limit.1": (
        "A table-based model: the silver loss multiplies the effect of temperature (Lodge, 200 "
        "mg of silver and 10 g of lead), of lead (Lodge, 685 °C) and of the silver present "
        "(Godshall). That they multiply is an assumption, not a measurement. Outside each "
        "table's range nothing is extrapolated: the end value is used and a warning is shown."
    ),
    "ficha.copelacion.limit.2": (
        "The gold loss is Table XII's (200 mg of gold without silver and 10 g of lead) and does "
        "not depend on lead or silver. Bugbee says it grows as the gold decreases and that silver "
        "reduces it (Smith; Fig. 41) but gives no figures: with less gold the model "
        "underestimates and with silver present it overestimates."
    ),
    "ficha.copelacion.limit.3": (
        "The band is reproducibility only (the scatter of Godshall's three series); gold uses "
        "the same because its scatter is not published. The bias against another laboratory is "
        "larger than the band: Lodge's model falls short of Godshall and does not pass the cut "
        "(Validation tab)."
    ),
    "ficha.copelacion.limit.4": (
        "The progress of the animation and the shape of the cumulative loss are illustrative: "
        "Bugbee gives the minute-by-minute curve only as a figure (Fig. 40, with 30 g of lead and "
        "100 mg of silver) and it was not digitized. The size of the full button is fixed in the "
        "drawing; that of the other frames comes from the calculation."
    ),
    "ficha.copelacion.limit.5": (
        "It leaves out impurities (copper, tellurium, bismuth and others raise the loss; Bugbee, "
        "Table XIII), the type and condition of the cupel, the draft in the muffle and spitting. "
        "It also leaves out platinoid cupellation and instrumental cupellation."
    ),
    "ficha.copelacion.limit.6": (
        "Parting is judged only by the silver:gold ratio (Bugbee: at least 3 to 1; in ore beads, "
        "8 to 10 to 1; Rose, by gold weight). It does not model the acid, the time or gold that "
        "breaks into powder."
    ),
    "guide.h.cop": "### Cupellation and parting: from the bead to the gold",
    "guide.cop.1": (
        "Cupellation separates the precious metals from the lead: the lead oxidizes to litharge, "
        "the cupel absorbs it and a bead of gold and silver is left. Some of the silver and a "
        "little gold are lost, more with higher temperature, more lead and less silver (Bugbee, "
        "Tables IX to XII). The model multiplies three factors from those tables and the grade "
        "is corrected with the loss:"
    ),
    "guide.cop.2": (
        "Parting in nitric acid needs at least 3 times more silver than gold; in ore beads 8 to "
        "10 times is better (Bugbee), and Rose gives the ratio by gold weight. That silver is "
        "added before cupelling (inquartation) and it also loses some: the calculator adds what "
        "is needed so that, after the cupel, the requested ratio is left. The limits are in the "
        "tab's data sheet and the comparison with Godshall is in the Validation tab."
    ),
    # ------------------------------------------------------------ results
    "cp.err.temp": "The cupel temperature must be a positive number.",
    "cp.err.plomo": "The button lead must be a positive number.",
    "cp.err.plata": "The button silver must be a number, zero or more.",
    "cp.err.oro": "The button gold must be a positive number.",
    "cp.err.ley": "The measured grade must be a number, zero or more.",
    "cp.err.perdida": "The loss must be between 0 and 1 (not reaching 1).",
    "cp.err.razon": "The own silver:gold ratio must be a positive number.",
    "cp.err.modo": "That way of choosing the silver:gold ratio is not known.",
    "cp.err.cuadros": "The animation needs at least 2 frames.",
    "cp.warn.temp": "The temperature is outside the table's range ({lo} to {hi} °C): the end value is used, nothing is extrapolated.",
    "cp.warn.plomo": "The lead is outside Table X's range ({lo} to {hi} g): the end value is used, nothing is extrapolated.",
    "cp.warn.plata": "The total silver is outside Table XI's range ({lo} to {hi} mg): the end value is used, nothing is extrapolated.",
    "cp.warn.congelado": "At {t0} °C or less the button freezes in Table XII (Bugbee): there is no cupellation and the gold loss is the {t1} °C one.",
    "cp.warn.fusion": "The Fusion tab could not calculate the button with its current inputs; the own lead of {pb} g is used.",
    "cp.m.ag": "Silver loss",
    "cp.m.band": "band {lo} to {hi} %",
    "cp.m.au": "Gold loss",
    "cp.m.au.delta": "Table XII, no silver",
    "cp.m.add": "Silver to add",
    "cp.m.add.delta": "target ratio {ratio} to 1",
    "cp.m.pearl": "Bead",
    "cp.m.pearl.delta": "{au} % gold",
    "cp.cal.h": "#### Losses and corrected grade",
    "cp.cal.pb.fusion": "the Fusion tab button",
    "cp.cal.pb.own": "own value",
    "cp.cal.res": (
        "At **{temp} °C**, with **{pb} g** of lead ({source}), {au} mg of gold and {ag} mg of "
        "silver in total (with the inquartation): **{lag} %** of the silver and **{lau} %** of "
        "the gold are lost. Liquid lead is {rho} g/cm³ at that temperature (same equation as "
        "the fusion)."
    ),
    "cp.cal.ley": (
        "Measured grade {med} g/t, corrected grade **{cor} g/t** = measured / (1 − gold loss "
        "of {lau} %)."
    ),
    "cp.cal.caption": (
        "The silver band is the scatter of Godshall's three series (sd of ln of {sd} %, factor "
        "{f}): reproducibility, not bias. The gold loss is that of 200 mg of gold without "
        "silver: with less gold it is larger and with silver present, smaller (Bugbee, p. 103)."
    ),
    "cp.enc.h": "#### Inquartation and parting",
    "cp.enc.intro": (
        "Mode: {mode}. Target ratio after cupelling: **{ratio} to 1** (silver : gold). The silver "
        "added already counts what is lost in the cupel."
    ),
    "cp.enc.col.what": "Item (mg)",
    "cp.enc.au": "Gold in the button",
    "cp.enc.ag0": "Silver already there",
    "cp.enc.add": "Silver to add",
    "cp.enc.ag1": "Total silver before cupelling",
    "cp.enc.ag2": "Silver left in the bead",
    "cp.enc.au2": "Gold left in the bead",
    "cp.enc.pearl": "Bead",
    "cp.enc.state.buena": "Ratio at parting {ratio} to 1: good for parting ({rec} to 1 or more).",
    "cp.enc.state.lenta": "Ratio at parting {ratio} to 1: it parts, but with more acid and more time (between {min} and {rec} to 1).",
    "cp.enc.state.lamina": "Ratio at parting {ratio} to 1: it only parts if the alloy is rolled thin, as for bullion, and some silver stays undissolved; for a bead Bugbee asks for at least {min} to 1.",
    "cp.enc.state.insuficiente": "Ratio at parting {ratio} to 1: insufficient; even bullion does not part below {low} to 1 (Bugbee asks for at least {min} to 1 for a bead).",
    "cp.enc.caption": (
        "Bugbee (pp. 118 to 122): ore beads, {rec} to {hi} times more silver than gold; gold "
        "bullion, {bullion} or {bullion2} to 1 with the rolled alloy; the maximum gold is {gold} % "
        "(3 to 1)."
    ),
    "cp.rose.h": "Rose's ratio by gold weight (Bugbee, p. 121)",
    "cp.rose.au": "Gold (mg)",
    "cp.rose.ratio": "Ag:Au ratio",
    "cp.rose.lt": "less than 0.1",
    "cp.rose.gt": "more than {mg}",
    "cp.rose.caption": 'Between its rows it is interpolated on a logarithmic scale. "Less than 0.1 mg" is "20 or 30 to 1": the 0.1 mg point uses the average, {mid} (assumption).',
    "cp.or": "or",
    # ------------------------------------------------------------ charts
    "cp.plot.h": "#### Bugbee's tables and the model",
    "cp.plot.intro": "The points are the tables as printed; the dashed line is the model; the star, the calculation above. In gray, outside the table's range (there the model stays at the end value).",
    "cp.plot.caption": "First: Tables IX and XII (200 mg, 10 g of lead). Second: Table X (685 °C) and, in green, Godshall's final average with 200 mg of silver (another laboratory, temperature not measured). Third: Table XI and Godshall's other two series with 1/2 A.T. of lead, relative to the 200 mg loss.",
    "cp.plot.ix": "Silver, Table IX (Lodge)",
    "cp.plot.model.ag": "Model, silver (200 mg, 10 g)",
    "cp.plot.xii": "Gold, Table XII (Lodge)",
    "cp.plot.model.au": "Model, gold",
    "cp.plot.frozen": "button frozen",
    "cp.plot.you.ag": "Your silver (with band)",
    "cp.plot.you.au": "Your gold",
    "cp.plot.temp.title": "Loss against temperature",
    "cp.plot.temp.x": "Temperature (°C)",
    "cp.plot.loss.y": "Loss (%)",
    "cp.plot.x": "Silver, Table X (Lodge, 685 °C)",
    "cp.plot.model.pb": "Model (relative to 10 g)",
    "cp.plot.god200": "Godshall, 200 mg (another laboratory)",
    "cp.plot.clamped": "outside the table",
    "cp.plot.pb.title": "Silver loss against lead",
    "cp.plot.pb.x": "Lead (g)",
    "cp.plot.xi": "Table XI (Godshall, 1/2 A.T.)",
    "cp.plot.rep.primera": "Godshall, first series",
    "cp.plot.rep.tercera": "Godshall, third series",
    "cp.plot.model.ag.rel": "Model",
    "cp.plot.you.rel": "Your total silver",
    "cp.plot.ag.title": "Effect of the silver present",
    "cp.plot.ag.x": "Silver (mg)",
    "cp.plot.rel.y": "Loss relative to the 200 mg one",
    # ------------------------------------------------------------ animation
    "cp.ani.h": "#### The cupel and the bead",
    "cp.ani.alt": "Cross-section of a cupel inside the muffle: the lead button shrinks while the litharge is absorbed into the cupel and the gold and silver bead is left",
    "cp.ani.caption": "The button shrinks according to the mass that comes from the calculation (lead, gold and silver in each frame); the muffle color follows the temperature with an illustrative ramp.",
    "svg.k.muffle": "Muffle (schematic)",
    "svg.k.cupel": "Bone-ash cupel",
    "svg.k.bead": "bead",
    "svg.k.title": "Cupellation",
    "svg.k.cond": "{temp} °C · lead {pb} g",
    "svg.k.progress": "Progress (illustrative)",
    "svg.k.mass": "Button mass",
    "svg.k.lead": "Lead left",
    "svg.k.pearl": "Bead: {mg} mg ({au} % gold)",
    "svg.k.au": "Gold left: {mg} mg (loss {loss} %)",
    "svg.k.ag": "Silver left: {mg} mg (loss {loss} %)",
    "svg.k.ratio": "Silver:gold ratio at parting: {ratio} to 1",
    "svg.k.legend": "Schematic, not to scale: the quantities do come from the calculation (button and bead mass, gold and silver left, {pb} g of lead). The progress, from 0 to 100 % in {run} s, and the shape of the cumulative loss are illustrative, because Bugbee gives the minute-by-minute curve only as a figure (Fig. 40). Muffle color: illustrative temperature ramp. The size of the full button is fixed in the drawing.",
    "svg.k.label": "Animated cross-section of a cupel with a lead button that shrinks until the gold and silver bead is left",
    # ------------------------------------------------------------ validation
    "cp.v.h": "### Phase 3: cupellation and parting (Bugbee 1922 and Godshall 1896)",
    "cp.v.intro": "The model is fitted with the Lodge tables Bugbee prints (IX, X and XII; the silver present comes from Table XI, which is Godshall's) and compared with Godshall's original paper (another experimenter; 1 assay ton = {a} g; final average on p. 483). Cuts fixed before running: relative error within ±25 % in the silver loss, with Godshall's temperature, which he did not measure, assumed to be {t0} °C (the middle of 700 to 775 °C).",
    "cp.v.h.tables": "#### Transcribed tables (literal figures from the scan image)",
    "cp.v.col.table": "Table",
    "cp.v.col.page": "Printed page",
    "cp.v.col.scan": "Scan page",
    "cp.v.col.rows": "Rows",
    "cp.v.col.author": "Author",
    "cp.v.col.what": "What it measures",
    "cp.v.t.ix": "silver loss against temperature (200 mg, 10 g of lead)",
    "cp.v.t.x": "silver loss against lead (200 mg, 685 °C)",
    "cp.v.t.xi": "silver loss against silver present (1/2 A.T. of lead)",
    "cp.v.t.xii": "gold loss against temperature (200 mg, 10 g of lead)",
    "cp.v.xi.note": "Table XI is the 1/2 A.T. row of Godshall's second series. At {ag} mg Bugbee prints {b} and Godshall prints {g} (Bugbee's figure is kept).",
    "cp.v.h.overlap": "#### Overlap and quantitative validation",
    "cp.v.overlap": "Lodge's tables only have 200 mg of silver and 10 to 25 g of lead; Godshall has seven silver amounts (2 to 200 mg) and four lead amounts ({pbmin} to {pbmax} g), with the temperature not measured. **{n} of {total}** cells overlap (200 mg of silver and 1/2 and 3/4 A.T. of lead): only they are a quantitative comparison, with a cut of ±{cut} %. The others are reported as trend.",
    "cp.v.col.ag": "Silver (mg)",
    "cp.v.col.pb": "Lead (g)",
    "cp.v.col.pub": "Published (%)",
    "cp.v.col.pred": "Predicted (%)",
    "cp.v.col.err": "Relative error (%)",
    "cp.v.col.fits": "Fits?",
    "cp.v.col.timp": "T that would give the figure (°C, diagnostic)",
    "cp.v.verdict": "**Verdict: {ok} of {n} fit.** Lodge's model falls short of Godshall: another laboratory and another cupel, and Godshall did not measure the temperature. Nothing was adjusted to make it pass. The last column is a diagnostic, not a validation: Godshall looks like Lodge at about {tlo} to {thi} °C, not in the crystal range.",
    "cp.v.h.trend": "#### Trends (the 28 cells of Godshall's final average)",
    "cp.v.trend": "- The silver loss is larger with 2 mg than with 200 mg in {a} of {na} lead amounts (**not independent**: the silver effect comes from Godshall).\n- The loss with 1 A.T. exceeds that of 1/4 A.T. in {b} of {nb} silver amounts.\n- The predicted one is within a factor of {f} of the published one in {c} of {nc} cells.",
    "cp.v.rep": "Silver replication (informative, no pass cut): of {total} ratios loss(Ag) / loss(200 mg) from Godshall's first and third series with 1/2 A.T., {n} fall within ±{cut} % of the model; the ones at {fails} mg of silver fail, where Godshall's three series differ a lot from each other.",
    "cp.v.not": "This is not a validation of Bugbee or Godshall: it is a comparison of a table-based model with an 1896 paper. The gold loss figures have no second source.",
}
