"""Textos en español de los datos de entrada (barra lateral y tabla «Qué datos necesita»)."""

T = {
    "group.Protocolo": "Protocolo",
    "group.Mineral": "Mineral",
    "group.Oro grueso": "Oro grueso",
    "group.Fusión": "Fusión",
    "dato.help": "{meaning} Rango{unit}: {range}. En planta: {source}",
    "dato.or": " o ",
    "dato.range": "{lo} a {hi}",
    "yes": "sí",
    "no": "no",
    "yesno": "sí o no",
    "col.group": "Grupo",
    "col.dato": "Dato",
    "col.unit": "Unidad",
    "col.range": "Rango",
    "col.example": "Ejemplo",
    "col.what": "Qué es",
    "col.how": "Cómo se obtiene",
    "sidebar.example": "Cargar ejemplo",
    # opciones de listas (el valor interno es el del modelo, en español)
    "opt.esfera": "esfera",
    "opt.cubo": "cubo",
    "opt.Calibrado DSA (Minnitt 2017)": "Calibrado DSA (Minnitt 2017)",
    "opt.Calibrado SFA (Minnitt 2017)": "Calibrado SFA (Minnitt 2017)",
    "opt.Calibrado propio (K y α)": "Calibrado propio (K y α)",
    "opt.Clásico (c·f·g·ℓ)": "Clásico (c·f·g·ℓ)",
    "opt.1 assay-ton (29,17 g)": "1 assay-ton (29,17 g)",
    "dato.preset.label": "Protocolo de preparación",
    "dato.preset.meaning": (
        "PREP-31: chancar al 70 % bajo 2 mm, dividir 250 g y pulverizar al 85 % bajo 75 µm. "
        "PREP-31B: igual con 1 kg. La tercera es la tabla de una mina de oro de Minnitt (2017). "
        "Códigos públicos de ALS; sin afiliación."
    ),
    "dato.preset.source": "el procedimiento de preparación del laboratorio.",
    "dato.aliquot.label": "Alícuota de ensayo al fuego",
    "dato.aliquot.meaning": "Masa que se funde: 30 g (Au-AA23) o 50 g (Au-AA24).",
    "dato.aliquot.source": "el método de ensayo pedido.",
    "dato.lot.label": "Masa de la muestra recibida",
    "dato.lot.meaning": "Masa que entra a la chancadora. Dato supuesto: depende de cada envío.",
    "dato.lot.source": "la balanza de recepción de muestras.",
    "dato.d_n0.label": "Tamaño de la muestra recibida",
    "dato.d_n0.meaning": "Solo dibuja el primer tramo del nomograma; no entra al error.",
    "dato.d_n0.source": "inspección de la muestra recibida.",
    "dato.m.label": "Pendiente m de Rosin-Rammler",
    "dato.m.meaning": (
        "Forma de la curva granulométrica que completa «70 % bajo 2 mm». Es un supuesto: el "
        "d95 (y con él el error, que lo lleva al cubo) cambia con m."
    ),
    "dato.m.source": "el análisis granulométrico del producto chancado y pulverizado.",
    "dato.safety.label": "Error de seguridad del nomograma",
    "dato.safety.meaning": (
        "Línea del nomograma bajo la cual el error de una división se considera aceptable."
    ),
    "dato.safety.source": "el objetivo de calidad del laboratorio.",
    "dato.lot_correction.label": "Corrección por masa del lote (1/MS − 1/ML)",
    "dato.lot_correction.meaning": (
        "Gy la incluye; Minnitt (2017) la omite en su Tabla VIII. Apagada, el error sube."
    ),
    "dato.lot_correction.source": "se activa siempre, salvo para reproducir esa tabla.",
    "dato.form.label": "Forma de la ecuación y mineral",
    "dato.form.meaning": (
        "Calibrada: σ² = K·dN^α/MS con K y α de un mineral (Minnitt 2017, DSA o SFA, de una mena "
        "de Witwatersrand) o propios. Clásica: c·f·g·ℓ·dN³/MS con los factores de abajo. K y α "
        "se calibran por mineral; nunca se suponen."
    ),
    "dato.form.source": "ensayo de heterogeneidad o árbol de muestreo del propio mineral.",
    "dato.k.label": "K propio",
    "dato.k.meaning": (
        "Constante de la forma calibrada, con dN en cm y masas en g. Solo si eliges «Calibrado "
        "propio»; el valor inicial es el DSA de Minnitt (2017)."
    ),
    "dato.k.source": "el intercepto de la recta de calibración del mineral.",
    "dato.alpha.label": "α propio",
    "dato.alpha.meaning": "Exponente de la forma calibrada. Solo con «Calibrado propio».",
    "dato.alpha.source": "la pendiente de la recta de calibración del mineral.",
    "dato.grade.label": "Ley de oro",
    "dato.grade.meaning": (
        "Ley del lote. Fija la proporción a (factor c, forma clásica) y el número de granos en "
        "la alícuota (pestaña Oro grueso). El valor inicial es el promedio de Minnitt (2017)."
    ),
    "dato.grade.source": "ensayos del lote.",
    "dato.rho_m.label": "Densidad del mineral valioso",
    "dato.rho_m.meaning": (
        "Solo forma clásica. 16 es la de una amalgama oro-plata (Minnitt 2017); 19,3, el oro puro."
    ),
    "dato.rho_m.source": "tablas de densidades del mineral.",
    "dato.rho_g.label": "Densidad de la ganga",
    "dato.rho_g.meaning": "Solo forma clásica.",
    "dato.rho_g.source": "picnómetro del laboratorio.",
    "dato.d_lib.label": "Tamaño de liberación dℓ",
    "dato.d_lib.meaning": (
        "Solo forma clásica: tamaño bajo el cual el mineral está liberado. 82 µm es el del DSA "
        "de Minnitt (2017)."
    ),
    "dato.d_lib.source": "estudio de liberación (mineralogía).",
    "dato.f.label": "Factor de forma f",
    "dato.f.meaning": "Solo forma clásica: 0,5 para la mayoría de las menas; 0,2 a 0,5 en la práctica.",
    "dato.f.source": "valor del ejemplo de Minnitt; no se mide.",
    "dato.g.label": "Factor granulométrico g",
    "dato.g.meaning": "Solo forma clásica: 0,25 con un amplio rango de tamaños; 1 si son todos iguales.",
    "dato.g.source": "valor del ejemplo de Minnitt; depende del equipo de reducción.",
    "dato.b.label": "Exponente b de la liberación",
    "dato.b.meaning": (
        "Solo forma clásica: ℓ = (dℓ/dN)^b; 1,5 en la mayoría de las menas de oro (Minnitt 2007)."
    ),
    "dato.b.source": "calibración por mineral.",
    "dato.grain.label": "Tamaño del grano de oro",
    "dato.grain.meaning": (
        "Diámetro del grano de oro libre. Con forma de esfera o cubo, fija la masa del grano."
    ),
    "dato.grain.source": "mineralogía del oro (microscopio, concentrado gravimétrico).",
    "dato.shape.label": "Forma del grano",
    "dato.shape.meaning": (
        "Esfera (π/6·d³) o cubo (d³). El oro real es irregular: la forma es un supuesto."
    ),
    "dato.shape.source": "observación del oro al microscopio.",
    "dato.f_sample.label": "Masa de la alícuota a fundir",
    "dato.f_sample.meaning": (
        "Un assay-ton (29,1667 g) o 30 g. La fusión lleva la carga que se calcula para esta masa."
    ),
    "dato.f_sample.source": "la alícuota que pesa el laboratorio.",
    "dato.mineral.meaning": (
        "Parte de la muestra en masa. Todos los minerales suman 100 % como máximo: lo que "
        "falta es material inerte (no ácido ni básico, solo pasa a la escoria)."
    ),
    "dato.mineral.source": (
        "mineralogía de la muestra (microscopio, difracción de rayos X o análisis químico)."
    ),
    "dato.f_sulfur.label": "Azufre oxidado a",
    "dato.f_sulfur.meaning": (
        "SO3: con carbonato alcalino, el azufre queda como sulfato (poder reductor mayor). SO2: "
        "sin carbonato alcalino. Bugbee: el real queda entre los dos; se mide en una fusión "
        "preliminar."
    ),
    "dato.f_sulfur.source": "fusión preliminar de reconocimiento.",
    "dato.f_button.label": "Botón de plomo pedido",
    "dato.f_button.meaning": "Bugbee: 28 g bastan como colector; no menos de 25 g ni más de 30 g.",
    "dato.f_button.source": "el tamaño del botón que pide el laboratorio.",
    "dato.f_degree.label": "Grado de silicato de la escoria",
    "dato.f_degree.meaning": (
        "Oxígeno del ácido entre oxígeno de la base: mono 1, sesqui 1,5, bi 2. Bugbee: bi o "
        "sesqui para menas silíceas y básicas; cerca de mono para sulfuros."
    ),
    "dato.f_degree.source": "la práctica del laboratorio.",
    "dato.f_flour.label": "Poder reductor de la harina",
    "dato.f_flour.meaning": (
        "Dato del laboratorio, no del modelo: g de plomo que reduce 1 g de harina. Bugbee da "
        "10 a 12 (usa 12 en sus ejemplos) y el USGS 10 a 11; el valor inicial es el medio."
    ),
    "dato.f_flour.source": "fusión de prueba con la harina del laboratorio (Bugbee, «Testing reagents»).",
    "dato.f_niter.label": "Poder oxidante del nitro",
    "dato.f_niter.meaning": (
        "Dato del laboratorio: g de plomo que oxida 1 g de nitro. El teórico es 5,12; Bugbee da "
        "4,0 a 4,2 con su tipo de carga (3,7 a 4,7 según la acidez) y el USGS 4,2."
    ),
    "dato.f_niter.source": "fusión preliminar con el nitro del laboratorio.",
    "dato.f_soda.label": "Soda por gramo de muestra",
    "dato.f_soda.meaning": "Carbonato de sodio como fundente base. Bugbee: al menos el peso de la muestra.",
    "dato.f_soda.source": "la práctica del laboratorio.",
    "dato.f_lith.label": "Litargirio para la escoria por gramo de muestra",
    "dato.f_lith.meaning": (
        "Litargirio que se queda en la escoria, además del que se reduce a plomo. Bugbee, "
        "carga de 1 assay-ton: 70 g en total, 30 para el botón."
    ),
    "dato.f_lith.source": "la práctica del laboratorio.",
    "dato.x_flour.label": "Probar: harina cambiada",
    "dato.x_flour.meaning": (
        "Multiplica la harina calculada para ver qué pasa con una carga mal pesada (botón chico "
        "o grande). 1 deja la carga calculada."
    ),
    "dato.x_flour.source": "no es un dato de planta.",
    "dato.x_silica.label": "Probar: sílice cambiada",
    "dato.x_silica.meaning": (
        "Multiplica la sílice calculada: más sílice vuelve ácida la escoria y arriesga mata."
    ),
    "dato.x_silica.source": "no es un dato de planta.",
    "dato.x_lith.label": "Probar: litargirio cambiado",
    "dato.x_lith.meaning": "Multiplica el litargirio calculado: poco litargirio también arriesga mata.",
    "dato.x_lith.source": "no es un dato de planta.",
}
