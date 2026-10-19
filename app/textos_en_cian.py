"""English texts of the "Bottle roll" tab, its inputs, data sheet, guide, diagram and validation
(keys `cn.*`, `cv.*`, `svg.c.*`, `dato.c_*`, `ficha.cianuracion.*`)."""

T = {
    "tab.cian": "Bottle roll",
    "group.Cianuración": "Bottle-roll cyanidation",
    # ------------------------------------------------------------ sidebar inputs
    "opt.Potencial (Ec. 3 de los autores)": "Power law (authors' Eq. 3)",
    "opt.Primer orden con meseta (nuestro)": "First order with plateau (ours)",
    "opt.Difusión (L)": "Diffusion (L)",
    "opt.Reacción (M)": "Reaction (M)",
    "opt.Mixto (N)": "Mixed (N)",
    "dato.c_model.label": "Model that moves the gauge",
    "dato.c_model.meaning": (
        "Which kinetic model moves the recovery gauge of the animated bottle. The curves of all "
        "models are always shown in the charts."
    ),
    "dato.c_model.source": "it is not measured: it only picks which curve is seen advancing",
    "dato.c_rpm.label": "Bottle speed",
    "dato.c_rpm.meaning": (
        "Revolutions per minute of the rollers. The standard bottle-roll procedure uses 30 to 32; "
        "it moves the bottle in the drawing and does not change the calculation."
    ),
    "dato.c_rpm.source": "it is set on the laboratory roller (Cetin et al., 2017: 30 to 32 rpm)",
    "dato.c_head.label": "Head grade S0",
    "dato.c_head.meaning": (
        "Gold in the ore before leaching, in ppb. With it the recovery is R = (1 − residue / S0)."
    ),
    "dato.c_head.source": (
        "fire assay of the head sample (the value 1,070 was deduced from Table 4 of the paper)"
    ),
    "dato.c_factor.label": "Solid per solution, F",
    "dato.c_factor.meaning": (
        "Converts gold in the solution into ppb of the solid for the balance: head = residue + F "
        "· solution."
    ),
    "dato.c_factor.source": (
        "it is the ratio of solution volume to solid mass of the test (the value 1.935 was "
        "deduced from Table 4; the paper does not publish it)"
    ),
    "dato.c_split.label": "Cut between stretches",
    "dato.c_split.meaning": (
        "Time that separates fast from slow dissolution: each stretch is fitted on its own, and "
        "the point at the cut belongs to both."
    ),
    "dato.c_split.source": "it is chosen by looking at the recovery chart (the authors cut at 7 h)",
    # ------------------------------------------------------------ data sheet and guide
    "ficha.cianuracion.hace": (
        "Reads a cyanidation test (gold in solution and in the residue at several times): it "
        "computes the recovery and the head grade by balance, warns when rows are not coherent "
        "and compares which kinetic model truly describes the dissolution and which only looks "
        "good in the fit. An animated bottle turns at the procedure speed while a gauge follows "
        "the curve of the chosen model."
    ),
    "ficha.cianuracion.entra": (
        "The table of times, gold in solution and gold in residue (preloaded with Table 4 of the "
        "paper), the head grade, the solid-per-solution factor, the cut between stretches, the "
        "gauge model and the bottle rpm."
    ),
    "ficha.cianuracion.sale": (
        "The recovery of each row, the head grade by balance and the warnings; the unreacted-core "
        "terms (L, M, N) with their lines, R² and intercepts per stretch; the power-law model and "
        "a first order with plateau; the error of each model in recovery points and the bottle "
        "diagram."
    ),
    "ficha.cianuracion.autores": (
        "Roostaei, Kordparijaei and Mesroghli (2026), “Cyanide dissolution of gold-bearing iron "
        "oxide minerals: kinetic studies and optimization using response surface methodology”, "
        "*Discover Applied Sciences* (doi 10.1007/s42452-026-08420-8, open access CC BY-NC-ND; "
        "only its quoted figures and equations are used here). Bottle speed: Cetin, Altun, Atalay "
        "and Büyüktanır (2017), “Bottle Roll Testing for Cyanidation of Gold Ores”, MCM'17, "
        "paper MMME 148, doi 10.11159/mmme17.148 (30 to 32 rpm)."
    ),
    "ficha.cianuracion.limit.1": (
        "The Table 4 data come from tests in a stirred 2 L beaker, not a bottle: the bottle and "
        "its rpm illustrate the test, and neither its size nor its load is published, so the "
        "drawing does not invent them."
    ),
    "ficha.cianuracion.limit.2": (
        "It describes only this ore and these seven points: it does not predict the recovery of "
        "another mineral. It has no cyanide chemistry (consumption, speciation) or activated "
        "carbon."
    ),
    "ficha.cianuracion.limit.3": (
        "What the paper does not publish and was deduced here, and is declared: the constant B of "
        "the mixed term (0.7033 and 0.75), the head grade (1,070 ppb) and the solid-per-solution "
        "factor (1.935). The first order with plateau, the rule that leaves out the 2 h point and "
        "the 5 % head tolerance are ours."
    ),
    "ficha.cianuracion.limit.4": (
        "The line of each stretch uses 3 or 4 points (1 or 2 degrees of freedom): a high R² with "
        "so few points does not prove the mechanism."
    ),
    "guide.h.cian": "### Bottle-roll cyanidation: which model describes the dissolution",
    "guide.cian.1": (
        "In a cyanidation test the ore is ground, mixed with cyanide solution and sampled at "
        "several times. The recovery comes from the gold left in the residue (S_t) against the "
        "head grade (S_0):"
    ),
    "guide.cian.2": (
        "The unreacted-core model assumes the particle dissolves from the outside in and that a "
        "term (diffusion L, reaction M or mixed N) grows as a straight line in time through the "
        "origin. Here the lines miss the origin: none explains the fast dissolution of the first "
        "hour, and the power-law model describes the data better but is empirical. The **Bottle "
        "roll** tab shows it with the numbers."
    ),
    # ------------------------------------------------------------ calculator
    "cn.cal.h": "#### Calculator: recovery and head grade",
    "cn.cal.intro": (
        "Each row is a sample: time, gold in the solution and gold in the residue (ppb). The "
        "recovery is R = (1 − residue / S0) with S0 = {head} ppb; the head grade by balance is "
        "residue + F · solution with F = {factor}. Both values are changed in the sidebar, and "
        "the table comes loaded with Table 4 of the paper."
    ),
    "cn.reset": "Back to the Table 4 example",
    "cn.col.t": "Time (h)",
    "cn.col.sol": "Au in solution (ppb)",
    "cn.col.res": "Au in residue (ppb)",
    "cn.col.rec": "Recovery (%)",
    "cn.col.sold": "Dissolved gold (ppb of solid)",
    "cn.col.head": "Head grade by balance (ppb)",
    "cn.col.dev": "Head deviation (%)",
    "cn.err.filas": "The table must have between {lo} and {hi} rows.",
    "cn.err.numero": "Some cells are empty, text or invalid numbers: all must be positive numbers.",
    "cn.err.rango": "A value is out of bounds: times up to {t_max} h and ppb up to {ppb_max}.",
    "cn.err.orden": "Times must be in increasing order, with no repeats.",
    "cn.err.residuo_mayor": "The gold in the residue must be below the head grade ({cabeza} ppb).",
    "cn.err.pocos_puntos": "There are not enough points to fit this model.",
    "cn.err.recuperacion": "The recovery cannot reach 100 %.",
    "cn.warn.no_monotona": (
        "At {t} h the recovery ({v} %) is above that of a later row: in a normal test gold is not "
        "deposited again. That point stays out of the lines, as the authors leave out the 2 h "
        "one."
    ),
    "cn.warn.cabeza": (
        "At {t} h the head grade by balance is {v} % away from the stated one: solution and "
        "residue do not match the head grade."
    ),
    "cn.cal.res": "Last row: **{r} %** recovery at {t} h with S0 = {head} ppb.",
    # ------------------------------------------------------------ models
    "cn.mod.h": "#### Kinetic models: which one describes and which one only fits",
    "cn.mod.intro": (
        "The three unreacted-core terms are fitted by stretches (up to {cut} h and from {cut} h), "
        "plus the authors' power-law model and a first order with plateau, *R = R∞ (1 − e^(−k "
        "t))*, which is ours. With X the dissolved fraction: L = 1 − 3(1−X)^(2/3) + 2(1−X), M = "
        "1 − (1−X)^(1/3) and N = (1 − 2X/3) − (1−X)^(2/3) + B·M."
    ),
    "cn.stretch.0": "whole test",
    "cn.stretch.1": "up to {cut} h",
    "cn.stretch.2": "from {cut} h",
    "cn.m.model": "Model",
    "cn.m.stretch": "Stretch",
    "cn.m.n": "Points",
    "cn.m.r2": "R²",
    "cn.m.a": "Intercept",
    "cn.m.b": "Slope (1/h)",
    "cn.m.r0": "Recovery at t = 0 (%)",
    "cn.m.rmse": "Mean error (% points)",
    "cn.msg.origin": (
        "**The unreacted-core lines do not go through the origin.** In the first stretch their "
        "intercepts are {i1} (diffusion), {i2} (reaction) and {i3} (mixed); if the model held, "
        "they would be 0 at t = 0. With them the models would already give {z1} %, {z2} % and "
        "{z3} % dissolved gold before starting: they do not explain the fast dissolution of the "
        "first hour (the measurement gives {r1} % at {t1} h). Besides, each line rests on {n} "
        "points: an R² of {r2} with so few points fits well in appearance, but does not prove "
        "the mechanism."
    ),
    "cn.msg.fewpoints": "These data have too few points: each stretch needs at least {n} used rows.",
    "cn.msg.models": (
        "The power-law model is empirical: it describes the residue (St ∝ t^−{b}) with R² {r2p} "
        "and a mean error of {rmse} recovery points, but it does not say what controls the "
        "reaction. The first order with plateau fits poorly (R² {r2o}; R∞ = {rinf} %, k = {k} "
        "1/h): a single constant is not enough for a two-stage dissolution."
    ),
    "cn.mod.caption": (
        "B (inferred, the paper does not publish it): {b1} for the stretch up to the cut and {b2} "
        "for the next. At t = 0 the power law does not exist and is drawn at 0 on the bottle. "
        "Lines are drawn dotted back to t = 0 to show their intercept."
    ),
    "cn.plot.used": "Used point",
    "cn.plot.excluded": "Excluded point",
    "cn.plot.rec.title": "Gold recovery against time: measured and models",
    "cn.plot.t": "Time (h)",
    "cn.plot.rec.y": "Recovery (%)",
    "cn.plot.origin": "Origin (0, 0)",
    "cn.plot.line": "Line",
    "cn.plot.tramo1": "first stretch",
    "cn.plot.tramo2": "second stretch",
    "cn.plot.intercept": "intercept {a}",
    "cn.plot.terms.title": "Linearized terms against time, with the line of each stretch",
    "cn.plot.terms.y": "Term value",
    # ------------------------------------------------------------ animation
    "cn.ani.h": "#### The bottle turning",
    "cn.ani.alt": "Laboratory bottle in section, turning, with a recovery gauge",
    "cn.ani.caption": (
        "The gauge follows the “{model}” model with compressed time (declared in the "
        "drawing); the red marks are the measured recoveries."
    ),
    "svg.c.title": "Cyanidation bottle, in section",
    "svg.c.rpm": "Speed: {rpm} rpm, one turn every {period} s",
    "svg.c.model": "Model: {model}",
    "svg.c.time": "Compressed time: {tmax} h in {run} s",
    "svg.c.clock": "Test time:",
    "svg.c.recovery": "Model recovery:",
    "svg.c.measured": "Red marks: measured recovery (with its hour)",
    "svg.c.legend": (
        "Diagram, not to scale: the quantities are from the calculation (rotation, model recovery "
        "at each instant and the {n} measured points). The bottle, its size and the pulp level "
        "are illustrative: the paper does not publish them. Time is compressed: the {tmax} h of "
        "the test pass in {run} s."
    ),
    "svg.c.label": "Animated diagram of a cyanidation bottle in section with a recovery gauge",
    # ------------------------------------------------------------ validation
    "cv.h": "### Bottle-roll cyanidation: figures of Roostaei et al. (2026)",
    "cv.intro": (
        "Cuts fixed before running. Head grade of each Table 4 row: S0 = residue / (1 − R) must "
        "fall in the interval that the rounding of that row allows, with S0 = 1,070 ppb. Table 6: "
        "L and M to 3 decimals; N with the inferred B. Table 7: R², intercept and slope at the "
        "published rounding, with the same points (without the 2 h one) and on the terms rounded "
        "to 3 decimals as the paper tabulated them. Eq. 3: 228.046, 0.332 and 0.937."
    ),
    "cv.summary": (
        "Match: Table 4, {t4} of {n4}; Table 6, {t6} of {n6}; Table 7, {t7} of {n7}; Eq. 3, {e3} "
        "of {n3}."
    ),
    "cv.h.t4": "**Table 4: head grade and recovery of each row**",
    "cv.h.t6": "**Table 6: the terms L, M and N**",
    "cv.h.t7": "**Table 7: the six regressions by stretch**",
    "cv.h.e3": "**Eq. 3: the power-law model**",
    "cv.kind.cabeza": "Head grade (ppb), row at",
    "cv.kind.recuperacion": "Recovery (%), row at",
    "cv.kind.L": "L",
    "cv.kind.M": "M",
    "cv.kind.N1": "N1",
    "cv.kind.N2": "N2",
    "cv.kind.r2": "R²",
    "cv.kind.intercepto": "Intercept",
    "cv.kind.pendiente": "Slope",
    "cv.kind.a": "a (ppb)",
    "cv.kind.b": "b",
    "cv.col.concept": "Item",
    "cv.col.published": "Published",
    "cv.col.calculated": "Calculated",
    "cv.col.fits": "Match?",
    "cv.col.note": "Note",
    "cv.note.m1": "does not match: see the finding below",
    "cv.b": (
        "**Inferred B.** The paper does not publish the constant B of N. Since N − L/3 = B·M, its "
        "cells give B = {b1} for the stretch up to 7 h (any value from {lo1} to {hi1} reproduces "
        "the four cells) and B = {b2} for the 7 to 48 h one ({lo2} to {hi2}). The head grade {s0} "
        "ppb and the solid-per-solution factor {f} were also deduced from Table 4: the per-row "
        "head grades fall between {h0} and {h1} ppb."
    ),
    "cv.m1": (
        "**Finding: row M1 of Table 7 does not come out of the data.** With the M terms of Table "
        "6 ({m1}, {m3} and {m7}) it gives R² {c2}, intercept {ci} and slope {cs}, and the paper "
        "prints {p2}, {pi} and {ps}. Its own F ({f}) and R² agree with each other (an F of {f} "
        "implies R² {r2}) and the other five rows do match: it looks like a typo in that row, and "
        "it was neither corrected nor dressed up."
    ),
    "cv.rows": (
        "The 2 h row is left out of the regressions, as in the paper: its recovery (85.70 %) is "
        "above that of 3 h (82.34 %), and gold is not deposited again."
    ),
}
