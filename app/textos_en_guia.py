"""English texts of the Guide and of the sheet at the top of each tab."""

T = {
    "minnitt2007.note": (
        "The paper prints ℓ = 0.000035, but its results imply a value 6.4 times larger; here the "
        "formula is used with the printed data."
    ),
    "ficha.label.hace": "**What it does.** {text}",
    "ficha.label.entra": "**What goes in.** {text}",
    "ficha.label.sale": "**What comes out.** {text}",
    "ficha.expander.datos": "What data it needs",
    "ficha.expander.limites": "Model limits",
    "ficha.autores": "**Where the equations come from.** {text}",
    "ficha.protocolo.hace": (
        "Calculates how much sampling error each stage of a laboratory sample preparation adds "
        "(reducing the size and splitting down to a smaller mass) with Gy's fundamental sampling "
        "error equation, and how much accumulates. It draws the protocol's route on the sampling "
        "nomogram."
    ),
    "ficha.protocolo.entra": (
        "The protocol (received mass, size of each stage and mass of each split), the 30 or 50 g "
        "fire-assay aliquot and the mineral (calibrated K and α, or the factors c, f, g, ℓ). The "
        "size of each stage comes from its specification («70 % under 2 mm») plus an assumed "
        "slope m."
    ),
    "ficha.protocolo.sale": (
        "The relative variance and the error (relative standard deviation) of each split and the "
        "cumulative one, which stage dominates, whether each split stays below the safety line "
        "and how the error changes with the slope m."
    ),
    "ficha.protocolo.autores": (
        "Gy (1982), *Sampling of Particulate Materials*; calibrated form: François-Bongarçon; "
        "Minnitt, Rice and Spangenberg (2007), *J. SAIMM* 107(8) 505-511; Minnitt (2017), «A "
        "version of Gy's equation for gold-bearing ores», *J. SAIMM* 117(2) 121-128 (K and α of "
        "the example); Chieregati (2017), *Mining Engineering*, Nov. Preparation codes PREP-31 "
        "and PREP-31B: public ALS codes (alsglobal.com), no affiliation."
    ),
    "ficha.protocolo.limit.1": (
        "K and α are calibrated per mineral and those of the example belong to a Witwatersrand "
        "gold ore: they do not apply to another mineral."
    ),
    "ficha.protocolo.limit.2": (
        "The size of each stage depends on the slope m of the Rosin-Rammler curve, an "
        "assumption: since dN is cubed, the error changes a lot with m."
    ),
    "ficha.protocolo.limit.3": (
        "Only the fundamental error: there are no delimitation, extraction, preparation or "
        "analytical errors."
    ),
    "ficha.oro.hace": (
        "Counts how many gold grains fall in the 30 or 50 g aliquot when the gold is coarse and "
        "simulates 1,000 repeated assays of that same aliquot: with few grains, the median of "
        "the assays falls below the true grade and a few come out very high."
    ),
    "ficha.oro.entra": "The gold grade, the size and shape of the gold grain and the aliquot mass.",
    "ficha.oro.sale": (
        "Expected grains per aliquot (λ), probability of receiving none, the Poisson simulation "
        "with a fixed seed, the mass that would hold 20 grains and the screen fire assay "
        "recommendation if fewer than 20 are expected."
    ),
    "ficha.oro.autores": (
        "Clifton, Hunter, Swanson and Phillips (1969), *USGS Professional Paper* 625-C (20-particle "
        "criterion and 95 % limits); Poisson distribution of the number of grains. Screen fire "
        "assay: public ALS procedure (alsglobal.com), no affiliation."
    ),
    "ficha.oro.limit.1": (
        "The grains are assumed to have the same size and shape (sphere or cube), free and "
        "randomly distributed; real gold is irregular and comes in a size distribution."
    ),
    "ficha.oro.limit.2": "A Poisson model: it includes no segregation or clustering of the grains.",
    "ficha.fusion.hace": (
        "Calculates the flux charge of a fire assay: litharge, sodium carbonate, borax, silica "
        "and flour or niter. With it the crucible gives a lead button of 25 to 30 g and a slag of "
        "the chosen silicate degree. It also evaluates a changed charge: small or large button, "
        "slag too acid or too basic and risk of matte."
    ),
    "ficha.fusion.entra": (
        "The aliquot (1 assay-ton or 30 g), the mineralogy of 9 minerals in %, the requested "
        "button, the silicate degree (mono, sesqui or bi) and two laboratory data: the reducing "
        "power of the flour and the oxidizing power of the niter."
    ),
    "ficha.fusion.sale": (
        "The charge in g, the expected button, the composition and silicate degree of the slag, "
        "the lead balance and the warnings, each with the citation of its threshold or labeled "
        "«assumed threshold»."
    ),
    "ficha.fusion.autores": (
        "Reducing and oxidizing power, silicate degrees, slag factors and worked examples: "
        "Bugbee (1922), *A Textbook of Fire Assaying* (public domain). Charges by rock type, "
        "preliminary fusion at 1,050 °C and powers of some minerals: Haffty, Riley and Goss "
        "(1977), USGS Bulletin 1445, *A Manual on Fire Assaying* (public domain). Density of "
        "liquid lead at 1,050 °C: OECD/NEA (2007), eq. 2.23; of solid lead (cold button), "
        "11.34 g/cm³: CRC Handbook. Crucible capacity: Bugbee, Table IV. It is not any "
        "laboratory's recipe."
    ),
    "ficha.fusion.limit.1": (
        "No cupellation or gold and silver losses, no slag thermodynamics and no platinoid assay."
    ),
    "ficha.fusion.limit.2": (
        "The reducing power of the flour and the oxidizing power of the niter are laboratory "
        "data: Bugbee gives ranges (10 to 12 and 4.0 to 4.2) and the real value is measured in a "
        "test fusion."
    ),
    "ficha.fusion.limit.3": (
        "The reducing power of a sulfide depends on how the sulfur leaves (SO2 or SO3); the real "
        "one lies between the two and is measured in a preliminary fusion."
    ),
    "ficha.fusion.limit.4": (
        "The slag density, 3.0 g/cm³, is an illustrative assumption (Bugbee does not give it); "
        "the crucible drawing is illustrative."
    ),
    "ficha.fusion.limit.5": (
        "The thresholds of the warnings come from Bugbee or the USGS with their citation; those "
        "without a published citation are labeled «assumed threshold»."
    ),
    "react.1": "2PbO + C = 2Pb + CO₂: 1 g of carbon reduces 34.5 g of lead; flour, 10 to 12.",
    "react.2": (
        "2PbO + S = 2Pb + SO₂ (without alkali carbonate) or 3PbO + S + Na₂CO₃ = 3Pb + Na₂SO₄ + "
        "CO₂ (with it): sulfur reduces 12.9 or 19.4 g of lead per gram; sulfides, in between."
    ),
    "react.3": (
        "Fe₂O₃ + Pb = 2FeO + PbO: hematite oxidizes (1.3 g of lead per gram) and calls for more "
        "flour."
    ),
    "react.4": (
        "4KNO₃ + 5C = 2K₂O + 5CO₂ + 2N₂: niter oxidizes 5.12 g of lead per gram in theory (4.0 "
        "to 4.2 in practice); it is added when the sample reduces too much."
    ),
    "limits.1": (
        "Only Gy's fundamental sampling error (FSE). NOT modeled: delimitation and extraction "
        "errors (how the sample is cut from the lot), preparation errors (contamination, losses "
        "and alterations), weighting errors, segregation and clustering, nor the analytical "
        "error of the assay."
    ),
    "limits.2": (
        "K and α are not assumed: they are calibrated per mineral. Those of the example are "
        "from Minnitt (2017)."
    ),
    "limits.3": "There is no fusion, flux or fire-assay chemistry: that belongs to a later phase.",
    "limits.4": (
        "The preparation equipment (jaw crushers, pulverizers) is not simulated: the size of "
        "each stage comes from the protocol specification."
    ),
    "guide.h.simula": "### What it simulates",
    "guide.simula": (
        "The **sample preparation** of a fire-assay laboratory: crushing, splitting, pulverizing "
        "and taking the 30 or 50 g aliquot that is fused. Every time a sample is split, a "
        "sampling error is added; the simulator calculates how much each stage adds and how much "
        "accumulates. And with coarse gold, how many grains fall in the aliquot and when the "
        "screen fire assay is advisable."
    ),
    "guide.h.gy": "### The fundamental error (Gy)",
    "guide.gy": (
        "σ² is the relative variance of splitting a mass M_L down to a subsample M_S with "
        "fragments of nominal top size d_N (the d95: the size at which 95 % passes). Each factor "
        "asks for one datum:\n\n"
        "- **c, mineralogical factor:** the grade and the densities of the mineral and the "
        "gangue (at low grade, c ≈ mineral density ÷ grade).\n"
        "- **f, fragment shape:** 0.5 for most ores (0.2 to 0.5 in practice).\n"
        "- **g, size distribution:** 0.25 with a wide range of sizes; 1 if all are equal.\n"
        "- **ℓ, liberation:** ℓ = (dℓ/d_N)^b, 1 when the mineral is already liberated "
        "(d_N ≤ dℓ); it asks for the liberation size dℓ and the exponent b.\n"
        "- **d_N:** it comes from the protocol specification. Since it enters **cubed**, it is "
        "the most sensitive datum; the app shows how much the error changes with the slope m."
    ),
    "guide.h.calibrar": "### K and α are calibrated, never assumed",
    "guide.calibrar": (
        "With ℓ = (dℓ/d_N)^b, the equation becomes σ² = K·d_N^α/M_S with α = 3 − b and "
        "K = c·f·g·dℓ^b. K and α belong to **each mineral**: they are calibrated with a "
        "heterogeneity test or a sampling tree. Those of the example are the ones Minnitt (2017) "
        "calibrated for a Witwatersrand gold ore (DSA: K = 167.4, α = 1.123; SFA: K = 2,539, "
        "α = 1.03) and they do not apply to another mineral."
    ),
    "guide.h.oro": "### Coarse gold and screen fire assay",
    "guide.oro": (
        "If the gold comes in grains, the number of grains in an aliquot is Poisson: with few "
        "grains almost all assays give less than the true grade (or zero) and a few give very "
        "high, so the **median falls below the true grade**. Clifton and co-authors (1969) ask "
        "for about **20 particles** per sample for an error of about ±50 % at 95 %; with fewer, "
        "the **screen fire assay** is advisable: a larger sample (about 1,000 g) is sieved at "
        "100 µm, the fines are assayed in duplicate and the coarse fraction whole."
    ),
    "guide.h.fusion": "### The flux charge (Fusion tab)",
    "guide.fusion.1": (
        "The fusion melts the sample with **litharge** (PbO, which is reduced to the lead of the "
        "button), **sodium carbonate** and **borax** (bases and fluxes), **silica** (acid) and a "
        "**reducer** (flour) or an **oxidizer** (niter) depending on what the sample already "
        "reduces. Bugbee's (1922) reactions:"
    ),
    "guide.fusion.2": (
        "The **silicate degree** is the oxygen of the acid over that of the base: mono 1, sesqui "
        "1.5, bi 2. 1 g of FeO neutralizes 0.84 g of silica and 1 g of CaCO₃, 0.60 g. 1 g of "
        "borax glass is equivalent to 0.6 g of silica. **What datum each reagent asks for:** "
        "the flour, its reducing power; the niter, its oxidizing power; the soda and the slag "
        "litharge, the laboratory's practice; the silica and the borax come from the acid-base "
        "balance of the mineralogy. In the drawing the lead is liquid (9.79 g/cm³ at 1,050 °C) "
        "in a pool at the bottom of the conical crucible, with the slag on top; the cold button "
        "(11.34 g/cm³) is given separately."
    ),
    "guide.h.minnitt": "### What the Minnitt (2007) paper says",
    "guide.minnitt": "_{note}_ The table is below, in the **Validation** tab.",
    "guide.h.datos": "### What data it needs",
    "guide.h.limites": "### What it does not do",
    "guide.h.otras": "### Other apps by the same author",
    "guide.otras": (
        "- [Comminution simulator]({conminucion}): grinding, animated.\n"
        "- [«Full plant»]({planta}): flotation, flash furnace, converter and electrowinning, "
        "animated.\n"
        "- Code of this app: [repository]({repo})."
    ),
}
