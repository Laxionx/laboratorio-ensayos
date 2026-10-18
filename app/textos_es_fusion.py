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
    "f.warn.line": "**{level}:** {text} _(Fuente: {source})_",
    "f.level.aviso": "Aviso",
    "f.level.riesgo": "Riesgo",
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
}
