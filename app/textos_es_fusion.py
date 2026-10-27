"""Textos en español de la pestaña Fusión: métricas, avisos, crisol y validación de la fase 2."""

T = {
    "f.err.sum": "Los minerales suman {total} %: no pueden pasar de 100 %. Baja alguno.",
    "f.err.calc": "No se pudo calcular la carga con estos datos: {exc}",
    "f.minerals": "Minerales: {total} % (el {rest} % restante es inerte). ",
    "f.codes": (
        "La carga es un cálculo de reactivos a partir de la mineralogía y de los textos de "
        "Bugbee (1922) y del USGS (1977): no es la receta de ningún laboratorio."
    ),
    "f.m.button": "Botón de plomo",
    "f.m.button.delta": "pedido {x} g",
    "f.m.slag": "Escoria",
    "f.m.degree": "Grado de silicato",
    "f.m.flour": "Harina de la carga",
    "f.m.niter": "Nitro de la carga",
    "f.info.changed": (
        "Estás probando una carga cambiada: el botón y la escoria son los de la carga "
        "cambiada, no los de la calculada."
    ),
    "f.warn.range": "El botón de {button} g queda fuera de {lo} a {hi} g.",
    "f.alt": "Crisol cónico con el plomo líquido al fondo y la escoria encima",
    "f.caption": (
        "El plomo está líquido en la fusión: {lead} cm³ a {rho} g/cm³ (1 050 °C), un charco al "
        "fondo del cono; encima, la escoria con {slag} cm³ (densidad supuesta de {slag_rho} "
        "g/cm³, Bugbee no la da). El botón ya frío mide {cold} cm³ (sólido, 11,34 g/cm³). Las "
        "medidas del crisol son ilustrativas; su capacidad, 190 cm³, es la del crisol de 20 g de "
        "Bugbee. Las gotas y las burbujas también son ilustrativas."
    ),
    "r.soda": "Soda (Na₂CO₃)",
    "r.litharge": "Litargirio (PbO)",
    "r.borax": "Bórax vidrio",
    "r.borax.formula": "Bórax vidrio (Na₂B₄O₇)",
    "r.silica": "Sílice (SiO₂)",
    "r.flour": "Harina",
    "r.niter": "Nitro (KNO₃)",
    "f.col.reagent": "Reactivo",
    "f.col.calc": "Calculada (g)",
    "f.col.used": "Usada (g)",
    "f.min.mineral": "Mineral",
    "f.min.rp": "R.P. (g Pb/g)",
    "f.min.pb": "Pb (g)",
    "f.rp.head": "**Poder reductor de la muestra**",
    "f.rp.caption": "Azufre oxidado a {sulfur}. Negativo: oxida (resta plomo).",
    "f.slag.head": "**Composición de la escoria**",
    "f.slag.component": "Componente",
    "bal.muestra": "muestra",
    "bal.harina": "harina",
    "bal.nitro": "nitro",
    "bal.botón": "botón",
    "bal.band": "botón de 25 a 30 g",
    "bal.title": "Balance del plomo: qué reduce u oxida cada parte (g de Pb)",
    "bal.y": "g de plomo",
    # ------------------------------------------------------------ avisos (código → texto y cita)
    "warn.button_low.text": "Botón de {button} g: menor de {lo} g, colector chico.",
    "warn.button_low.source": "Bugbee 1922: «no menos de 25 g» de plomo",
    "warn.button_high.text": (
        "Botón de {button} g: mayor de {hi} g; conviene escorificarlo antes de copelar."
    ),
    "warn.button_high.source": "Bugbee 1922, notas del ensayo",
    "warn.slag_basic.text": "Escoria más básica que mono-silicato ({degree}): ataca el crisol.",
    "warn.slag_basic.source": "Bugbee 1922, Tabla XIX y texto",
    "warn.slag_acid.text": (
        "Escoria más ácida que tri-silicato ({degree}): viscosa y fuera de los límites de las "
        "escorias de ensayo."
    ),
    "warn.slag_acid.source": "Bugbee 1922, Tabla XIX",
    "warn.matte_slag.text": (
        "Con tanto sulfuro la escoria conviene cerca del mono-silicato y esta es de grado "
        "{degree}: riesgo de mata."
    ),
    "warn.matte_slag.source": "Bugbee 1922: mono-silicato; umbral supuesto {limit}",
    "warn.reductant_excess.text": (
        "El reductor pide más litargirio del que hay: queda azufre o reductor sin oxidar y se "
        "forma una mata."
    ),
    "warn.reductant_excess.source": "Bugbee 1922, notas del ensayo",
    "warn.lodge_excess.text": (
        "Litargirio sin el exceso del 15 al 25 % que piden los sulfuros: riesgo de mata."
    ),
    "warn.lodge_excess.source": "Lodge, citado por Bugbee 1922",
    "warn.active_flux.text": "Fundente activo de {active} g: menos de {ratio} veces la muestra.",
    "warn.active_flux.source": "Bugbee 1922: al menos 2,5 veces de fundente activo",
    "warn.copper.text": (
        "Cobre de {copper} %: conviene aumentar todos los componentes del fundente."
    ),
    "warn.copper.source": "USGS Bulletin 1445: Cu de 2 a 5 %",
    "warn.perkins.text": (
        "Poco litargirio libre para tanto cobre (Perkins pide 137 a 300 partes de PbO por parte "
        "de Cu)."
    ),
    "warn.perkins.source": "Perkins, citado por Bugbee 1922; umbral supuesto de cobre alto: {limit} %",
    "warn.high_sulfur.text": "Más de 25 % de azufre: mucha mata posible y mucho nitro.",
    "warn.high_sulfur.source": "umbral supuesto",
    "warn.dry_over_capacity.text": (
        "La carga en polvo ocupa {vol} cm³ ({grams} g a {density} g/cm³): pasa de la capacidad "
        "del crisol ({cap} cm³); se derrama. Usa un crisol mayor o una carga menor."
    ),
    "warn.melt_over_capacity.text": (
        "Lo fundido (plomo y escoria) ocupa {vol} cm³ (plomo líquido más escoria): pasa de la "
        "capacidad del crisol ({cap} cm³); se derrama. Usa un crisol mayor o una carga menor."
    ),
    "warn.over_capacity.source": (
        "capacidad: Bugbee 1922, Tabla IV (20 g = 190 cm³); densidad en polvo: supuesto"
    ),
    "warn.dry_over_two_thirds.text": (
        "La carga en polvo ocupa {vol} cm³ ({grams} g a {density} g/cm³): pasa de los 2/3 del "
        "crisol ({two_thirds} de {cap} cm³)."
    ),
    "warn.melt_over_two_thirds.text": (
        "Lo fundido (plomo y escoria) ocupa {vol} cm³ (plomo líquido más escoria): pasa de los "
        "2/3 del crisol ({two_thirds} de {cap} cm³)."
    ),
    "warn.over_two_thirds.source": (
        "Bugbee 1922: «nunca más de dos tercios llenos» (el 2/3 es del volumen)"
    ),
    # ------------------------------------------------------------ esquema del crisol
    "svg.f.title": "Crisol en corte durante la fusión",
    "svg.f.label": "Crisol cónico con el plomo líquido al fondo y la escoria encima",
    "svg.f.charge": "Carga (g)",
    "svg.f.calc": "  (calculada {x})",
    "svg.f.lead": "Plomo líquido: {mass} g · {vol} cm³ a {rho} g/cm³",
    "svg.f.cold": "Botón ya frío: {mass} g · {vol} cm³ (sólido, 11,34 g/cm³)",
    "svg.f.slag": "Escoria: {mass} g · grado {label} ({degree})",
    "svg.f.slagvol": "Volumen de la escoria: {vol} cm³ (densidad supuesta {rho} g/cm³)",
    "svg.f.dry": (
        "Carga en polvo: {mass} g ≈ {vol} cm³ (supuesto {rho} g/cm³); capacidad {cap} cm³"
    ),
    "svg.f.drops": "Gotas dibujadas: {drops} · burbujas: {bubbles}",
    "svg.f.limit": "2/3 de la capacidad ({v} cm³)",
    "svg.f.legend": (
        "Crisol cónico ilustrativo: radio de {r0} cm al fondo y {r1} cm arriba, {h} cm de alto; "
        "su capacidad, {cap} cm³, es la del crisol de 20 g de Bugbee (Tabla IV). El plomo está "
        "LÍQUIDO y forma un charco al fondo: volumen = masa ÷ densidad del plomo líquido a "
        "{temp} °C (OECD/NEA 2007). La escoria llena el cono encima: volumen = masa ÷ "
        "{slag_rho} g/cm³ (supuesto). Gotas de plomo: {per_g} por g reducido; burbujas de CO₂ y "
        "SO₂ y su posición: ilustrativas. Escoria con el {note} a {temp} °C."
    ),
    "svg.f.foot": "esquema, no a escala: las cantidades sí son del cálculo",
    "scheme.temp": "color ilustrativo de la temperatura",
    # ------------------------------------------------------------ validación de la fase 2
    "fv.h": "### Fase 2: carga fundente (Bugbee 1922 y USGS Bulletin 1445)",
    "fv.summary": (
        "{total} cifras publicadas: **{ok}** cuadran con pesos atómicos actuales, **{weights}** "
        "cuadran con los pesos de Bugbee, **{trunc}** son truncamientos suyos y **{no}** no "
        "cuadran. Difieren porque Bugbee calculó a mano con pesos atómicos redondeados (207 para "
        "el Pb, 56 para el Fe) y a veces truncó en vez de redondear; los pesos de Bugbee de esta "
        "tabla se infieren de sus propias cifras (el juego que mejor las reproduce, declarado en "
        "`fusion_pesos.py`) y la app calcula siempre con pesos actuales. Las cifras de la Tabla XX "
        "y de la Tabla XXI se leyeron también en la imagen del escaneo."
    ),
    "fv.h1": "#### Poderes reductores y oxidantes teóricos",
    "fv.h2": "#### Neutralización de bases y tablas de fundentes",
    "fv.h3": "#### Ejemplos resueltos de Bugbee",
    "fv.h4": "#### Poderes reductores medidos por Bugbee (no son corte)",
    "fv.h5": "#### Cargas del USGS 1445 evaluadas con la calculadora (informativo)",
    "fv.h6": "#### Nitro del USGS",
    "fv.col.concept": "Concepto",
    "fv.col.published": "Publicado",
    "fv.col.current": "Pesos actuales",
    "fv.col.bugbee": "Pesos de Bugbee",
    "fv.col.verdict": "Veredicto",
    "fv.col.diff": "Dif. (Bugbee)",
    "fv.col.unit": "Unidad",
    "fv.col.note": "Nota",
    "fv.m.mineral": "Mineral",
    "fv.m.so2": "Teórico, S a SO₂",
    "fv.m.so3": "Teórico, S a SO₃",
    "fv.m.measured": "Medido",
    "fv.m.diff": "Medido − SO₃",
    "fv.m.caption": (
        "Carga de prueba de Bugbee: 5 g de Na₂CO₃, 80 g de PbO, 2 g de SiO₂ y mineral para un "
        "botón de unos 25 g. Argoles: 11,04 (sub-silicato), 10,93 (mono), 10,62 (bi) y 9,26 (tri)."
    ),
    "fv.u.load": "Carga",
    "fv.u.button": "Botón (g)",
    "fv.u.degree": "Grado",
    "fv.u.slag": "Escoria",
    "fv.u.slag_g": "Escoria (g)",
    "fv.u.caption": (
        "Harina de R.P. 10,5 (medio del USGS) y azufre ausente. Son cargas del manual del USGS "
        "(1977), no recetas; el USGS agrega 0 a 12 g de CaF₂ que aquí no se modela."
    ),
    "verdict.cuadra": "cuadra",
    "verdict.cuadra con los pesos de Bugbee": "cuadra con los pesos de Bugbee",
    "verdict.truncamiento de Bugbee": "truncamiento de Bugbee",
    "verdict.no cuadra": "no cuadra",
    # ------------------------------------------------------------ estado, casos y pruebas
    "fe.chk.boton.ok": "Botón de {button} g, dentro del rango de {lo} a {hi} g.",
    "fe.chk.escoria.ok": (
        "Escoria de grado {degree} ({label}), entre mono-silicato (1) y tri-silicato (3)."
    ),
    "fe.chk.fundente.ok": (
        "Fundente activo de {active} g, {ratio} veces la muestra (mínimo {min} veces)."
    ),
    "fe.chk.crisol.ok": (
        "La carga en polvo ocupa {dry} cm³ y lo fundido, {melt} cm³: bajo los 2/3 del crisol "
        "({lim} de {cap} cm³)."
    ),
    "fe.chk.cobre.ok": "Cobre de {copper} %, bajo el {lim} % desde el que conviene más fundente.",
    "fe.chk.reductor.ok": "El reductor no pide más litargirio del que hay.",
    "fe.chk.lodge.ok": "Litargirio con el exceso del 15 al 25 % que piden los sulfuros.",
    "fe.src.boton": (
        "Bugbee 1922: «no menos de 25 g» de plomo; sobre 30 g conviene escorificar antes de "
        "copelar (`fusion_avisos.py`)."
    ),
    "fe.src.escoria": (
        "Bugbee 1922, Tabla XIX y texto: de mono-silicato (grado 1) a tri-silicato (grado 3)."
    ),
    "fe.src.fundente": (
        "Bugbee 1922: al menos 2,5 veces de fundente activo que de muestra (soda, bórax y "
        "litargirio libre)."
    ),
    "fe.src.crisol": (
        "Bugbee 1922: «nunca más de dos tercios llenos» (el 2/3 es del volumen); capacidad del "
        "crisol de 20 g: 190 cm³ (Tabla IV). La densidad de la carga en polvo y la de la escoria "
        "son supuestos del modelo."
    ),
    "fe.src.cobre": (
        "USGS Bulletin 1445: con Cu de 2 a 5 % conviene aumentar todo el fundente; Perkins "
        "(citado por Bugbee 1922) pide 137 a 300 partes de PbO por parte de Cu desde un cobre "
        "alto (umbral supuesto del modelo)."
    ),
    "fe.src.reductor": (
        "Bugbee 1922, notas del ensayo: si el reductor pide más litargirio del que hay, queda "
        "azufre o reductor sin oxidar y se forma una mata."
    ),
    "fe.src.lodge": "Lodge, citado por Bugbee 1922: 15 a 25 % de litargirio sobre el del reductor.",
    "fe.caso.bugbee50": "Bugbee (1922): 1 assay-ton de 50 % CaCO₃ y 50 % SiO₂",
    "fe.caso.bugbee100": "Bugbee (1922): 1 assay-ton de CaCO₃ puro",
    "fe.caso.res": (
        "**{caso}.** Carga calculada frente a la que imprime Bugbee (botón de 28 g, "
        "bi-silicato, harina de R.P. 12 y 30 g de soda y de litargirio de escoria). "
        "Δ = calculada − publicada; el veredicto es el de la pestaña Validación."
    ),
    "fe.exp.harina.titulo": "Quitar la harina",
    "fe.exp.harina.texto": (
        "Sin harina, solo reduce la muestra: el botón baja de {b0} g a {b1} g, bajo el rango de "
        "{lo} a {hi} g, y el panel lo marca. La escoria sube de {s0} g a {s1} g y su grado baja "
        "de {d0} a {d1}."
    ),
    "fe.exp.litargirio.titulo": "Bajar el litargirio",
    "fe.exp.litargirio.texto": (
        "Con el {x} % del litargirio calculado ({l0} g a {l1} g) el botón no cambia ({b1} g), "
        "pero la escoria se vuelve más ácida: grado {d0} a {d1}, y pesa {s1} g en vez de {s0} g. "
        "El panel marca el fundente activo por debajo de {ratio} veces la muestra."
    ),
    "fe.exp.mono.titulo": "Pedir una escoria mono-silicato",
    "fe.exp.mono.texto": (
        "Con grado 1 (mono-silicato) en vez de 2 (bi-silicato), la escoria pesa {s1} g en vez de "
        "{s0} g y la carga en polvo sube de {p0} a {p1} cm³, sobre los 2/3 del crisol ({lim} de "
        "{cap} cm³): el panel lo marca."
    ),
}
