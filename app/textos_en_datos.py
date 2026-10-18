"""English texts of the input data (sidebar and the «What data it needs» table)."""

T = {
    "group.Protocolo": "Protocol",
    "group.Mineral": "Mineral",
    "group.Oro grueso": "Coarse gold",
    "group.Fusión": "Fusion",
    "dato.help": "{meaning} Range{unit}: {range}. In the plant: {source}",
    "dato.or": " or ",
    "dato.range": "{lo} to {hi}",
    "yes": "yes",
    "no": "no",
    "yesno": "yes or no",
    "col.group": "Group",
    "col.dato": "Input",
    "col.unit": "Unit",
    "col.range": "Range",
    "col.example": "Example",
    "col.what": "What it is",
    "col.how": "How it is obtained",
    "sidebar.example": "Load example",
    "opt.esfera": "sphere",
    "opt.cubo": "cube",
    "opt.Calibrado DSA (Minnitt 2017)": "Calibrated DSA (Minnitt 2017)",
    "opt.Calibrado SFA (Minnitt 2017)": "Calibrated SFA (Minnitt 2017)",
    "opt.Calibrado propio (K y α)": "Own calibration (K and α)",
    "opt.Clásico (c·f·g·ℓ)": "Classical (c·f·g·ℓ)",
    "opt.1 assay-ton (29,17 g)": "1 assay-ton (29.17 g)",
    "dato.preset.label": "Preparation protocol",
    "dato.preset.meaning": (
        "PREP-31: crush to 70 % under 2 mm, split 250 g and pulverize to 85 % under 75 µm. "
        "PREP-31B: the same with 1 kg. The third is the table of a gold mine from Minnitt (2017). "
        "Public ALS codes; no affiliation."
    ),
    "dato.preset.source": "the laboratory's preparation procedure.",
    "dato.aliquot.label": "Fire-assay aliquot",
    "dato.aliquot.meaning": "Mass that is fused: 30 g (Au-AA23) or 50 g (Au-AA24).",
    "dato.aliquot.source": "the assay method requested.",
    "dato.lot.label": "Mass of the received sample",
    "dato.lot.meaning": "Mass that enters the crusher. Assumed value: it depends on each shipment.",
    "dato.lot.source": "the sample-reception balance.",
    "dato.d_n0.label": "Size of the received sample",
    "dato.d_n0.meaning": "It only draws the first leg of the nomogram; it does not enter the error.",
    "dato.d_n0.source": "inspection of the received sample.",
    "dato.m.label": "Rosin-Rammler slope m",
    "dato.m.meaning": (
        "Shape of the size-distribution curve that completes «70 % under 2 mm». It is an "
        "assumption: the d95 (and with it the error, which cubes it) changes with m."
    ),
    "dato.m.source": "the size analysis of the crushed and pulverized product.",
    "dato.safety.label": "Nomogram safety error",
    "dato.safety.meaning": (
        "Line of the nomogram below which the error of a split is considered acceptable."
    ),
    "dato.safety.source": "the laboratory's quality target.",
    "dato.lot_correction.label": "Lot-mass correction (1/MS − 1/ML)",
    "dato.lot_correction.meaning": (
        "Gy includes it; Minnitt (2017) omits it in his Table VIII. Switched off, the error rises."
    ),
    "dato.lot_correction.source": "always on, except to reproduce that table.",
    "dato.form.label": "Form of the equation and mineral",
    "dato.form.meaning": (
        "Calibrated: σ² = K·dN^α/MS with K and α of a mineral (Minnitt 2017, DSA or SFA, from a "
        "Witwatersrand ore) or your own. Classical: c·f·g·ℓ·dN³/MS with the factors below. K and "
        "α are calibrated per mineral; they are never assumed."
    ),
    "dato.form.source": "heterogeneity test or sampling tree of the mineral itself.",
    "dato.k.label": "Own K",
    "dato.k.meaning": (
        "Constant of the calibrated form, with dN in cm and masses in g. Only if you choose "
        "«Own calibration»; the initial value is Minnitt's (2017) DSA."
    ),
    "dato.k.source": "the intercept of the mineral's calibration line.",
    "dato.alpha.label": "Own α",
    "dato.alpha.meaning": "Exponent of the calibrated form. Only with «Own calibration».",
    "dato.alpha.source": "the slope of the mineral's calibration line.",
    "dato.grade.label": "Gold grade",
    "dato.grade.meaning": (
        "Lot grade. It sets the proportion a (factor c, classical form) and the number of grains "
        "in the aliquot (Coarse gold tab). The initial value is the Minnitt (2017) average."
    ),
    "dato.grade.source": "assays of the lot.",
    "dato.rho_m.label": "Density of the valuable mineral",
    "dato.rho_m.meaning": (
        "Classical form only. 16 is that of a gold-silver amalgam (Minnitt 2017); 19.3, pure gold."
    ),
    "dato.rho_m.source": "mineral density tables.",
    "dato.rho_g.label": "Density of the gangue",
    "dato.rho_g.meaning": "Classical form only.",
    "dato.rho_g.source": "the laboratory's pycnometer.",
    "dato.d_lib.label": "Liberation size dℓ",
    "dato.d_lib.meaning": (
        "Classical form only: size below which the mineral is liberated. 82 µm is the DSA's in "
        "Minnitt (2017)."
    ),
    "dato.d_lib.source": "liberation study (mineralogy).",
    "dato.f.label": "Shape factor f",
    "dato.f.meaning": "Classical form only: 0.5 for most ores; 0.2 to 0.5 in practice.",
    "dato.f.source": "value of Minnitt's example; it is not measured.",
    "dato.g.label": "Size-distribution factor g",
    "dato.g.meaning": (
        "Classical form only: 0.25 with a wide range of sizes; 1 if they are all equal."
    ),
    "dato.g.source": "value of Minnitt's example; it depends on the size-reduction equipment.",
    "dato.b.label": "Liberation exponent b",
    "dato.b.meaning": ("Classical form only: ℓ = (dℓ/dN)^b; 1.5 in most gold ores (Minnitt 2007)."),
    "dato.b.source": "calibration per mineral.",
    "dato.grain.label": "Gold grain size",
    "dato.grain.meaning": (
        "Diameter of the free gold grain. With a sphere or cube shape, it sets the grain mass."
    ),
    "dato.grain.source": "gold mineralogy (microscope, gravity concentrate).",
    "dato.shape.label": "Grain shape",
    "dato.shape.meaning": (
        "Sphere (π/6·d³) or cube (d³). Real gold is irregular: the shape is an assumption."
    ),
    "dato.shape.source": "observation of the gold under the microscope.",
    "dato.f_sample.label": "Mass of the aliquot to fuse",
    "dato.f_sample.meaning": (
        "One assay-ton (29.1667 g) or 30 g. The fusion takes the charge calculated for this mass."
    ),
    "dato.f_sample.source": "the aliquot the laboratory weighs.",
    "dato.mineral.meaning": (
        "Share of the sample by mass. All minerals add up to 100 % at most: the rest is inert "
        "material (neither acid nor basic, it just goes to the slag)."
    ),
    "dato.mineral.source": (
        "mineralogy of the sample (microscope, X-ray diffraction or chemical analysis)."
    ),
    "dato.f_sulfur.label": "Sulfur oxidized to",
    "dato.f_sulfur.meaning": (
        "SO3: with alkali carbonate, the sulfur ends up as sulfate (higher reducing power). SO2: "
        "without alkali carbonate. Bugbee: the real one lies between the two; it is measured in "
        "a preliminary fusion."
    ),
    "dato.f_sulfur.source": "preliminary reconnaissance fusion.",
    "dato.f_button.label": "Requested lead button",
    "dato.f_button.meaning": (
        "Bugbee: 28 g is enough as a collector; not less than 25 g nor more than 30 g."
    ),
    "dato.f_button.source": "the button size the laboratory asks for.",
    "dato.f_degree.label": "Silicate degree of the slag",
    "dato.f_degree.meaning": (
        "Acid oxygen over base oxygen: mono 1, sesqui 1.5, bi 2. Bugbee: bi or sesqui for "
        "siliceous and basic ores; close to mono for sulfides."
    ),
    "dato.f_degree.source": "the laboratory's practice.",
    "dato.f_flour.label": "Reducing power of the flour",
    "dato.f_flour.meaning": (
        "Laboratory data, not a model output: g of lead that 1 g of flour reduces. Bugbee gives "
        "10 to 12 (he uses 12 in his examples) and the USGS 10 to 11; the initial value is the "
        "middle."
    ),
    "dato.f_flour.source": "test fusion with the laboratory's flour (Bugbee, «Testing reagents»).",
    "dato.f_niter.label": "Oxidizing power of the niter",
    "dato.f_niter.meaning": (
        "Laboratory data: g of lead that 1 g of niter oxidizes. The theoretical value is 5.12; "
        "Bugbee gives 4.0 to 4.2 for his type of charge (3.7 to 4.7 depending on acidity) and "
        "the USGS 4.2."
    ),
    "dato.f_niter.source": "preliminary fusion with the laboratory's niter.",
    "dato.f_soda.label": "Soda per gram of sample",
    "dato.f_soda.meaning": "Sodium carbonate as the base flux. Bugbee: at least the weight of the sample.",
    "dato.f_soda.source": "the laboratory's practice.",
    "dato.f_lith.label": "Litharge for the slag per gram of sample",
    "dato.f_lith.meaning": (
        "Litharge that stays in the slag, besides what is reduced to lead. Bugbee, 1 assay-ton "
        "charge: 70 g in total, 30 for the button."
    ),
    "dato.f_lith.source": "the laboratory's practice.",
    "dato.x_flour.label": "Try: changed flour",
    "dato.x_flour.meaning": (
        "Multiplies the calculated flour to see what happens with a badly weighed charge (small "
        "or large button). 1 keeps the calculated charge."
    ),
    "dato.x_flour.source": "not a plant datum.",
    "dato.x_silica.label": "Try: changed silica",
    "dato.x_silica.meaning": (
        "Multiplies the calculated silica: more silica makes the slag acid and risks matte."
    ),
    "dato.x_silica.source": "not a plant datum.",
    "dato.x_lith.label": "Try: changed litharge",
    "dato.x_lith.meaning": "Multiplies the calculated litharge: too little litharge also risks matte.",
    "dato.x_lith.source": "not a plant datum.",
}
