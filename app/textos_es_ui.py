"""Textos en español de las pestañas Protocolo, Oro grueso y Validación (fase 1), de sus gráficos y
del esquema de la alícuota."""

T = {
    "page.title": "Laboratorio de ensayos metalúrgicos y de ensayo al fuego",
    "app.title": "Laboratorio de ensayos metalúrgicos y de ensayo al fuego",
    "app.caption": (
        "Ensayos metalúrgicos de laboratorio, además del ensayo al fuego: el error de muestreo, la "
        "carga fundente, la cianuración, la sedimentación que dimensiona un espesador y el control "
        "de calidad del laboratorio (CRM, duplicados y blancos). Cuánto "
        "error de muestreo mete cada etapa de la preparación y cuántos granos de oro caen "
        "en la alícuota, con la ecuación de Gy validada contra números publicados. Con la carga "
        "fundente de la fusión (fase 2) y la copelación con la partición (fase 3). Empieza por la **Guía**; los datos se "
        "cambian en la barra lateral. Códigos de preparación públicos de ALS; sin afiliación."
    ),
    "err.generic": "Algo falló al calcular. Prueba con otros datos o recarga la página.",
    "toggle.label": "Mover la animación",
    "toggle.help": (
        "Apaga la animación del crisol (pestaña Fusión), la de la copela (pestaña Copelación), la del vaso (pestaña Ensayo de cianuración) y la de la probeta y el espesador (pestaña Ensayo de sedimentación). También se apaga sola si el "
        "sistema tiene activado «reducir movimiento». Solo cambia el dibujo: ningún número depende de él."
    ),
    "tab.guide": "Guía",
    "tab.protocol": "Protocolo",
    "tab.gold": "Oro grueso",
    "tab.fusion": "Fusión",
    "tab.validation": "Validación",
    "err.protocol": "No se pudo calcular el protocolo con estos datos: {exc}",
    "err.gold": "No se pudo calcular el oro con estos datos: {exc}",
    # ------------------------------------------------------------ protocolo
    "p.total": "Error total del protocolo",
    "p.worst": "Etapa que más aporta",
    "p.worst.value": "Etapa {n}",
    "p.worst.delta": "{pct} de la varianza",
    "p.last": "Error de la última división",
    "p.safe": "Cada división bajo la seguridad",
    "p.safe.delta": "seguridad {pct} %",
    "p.info": (
        "Este protocolo usa sus propias masas y tamaños (Minnitt 2017, Tabla VIII); la "
        "masa recibida, la alícuota y la pendiente m no cambian nada."
    ),
    "p.mineral": "Mineral: {name}. ",
    "p.mineral.note": (
        "K y α son los que Minnitt (2017) calibró para una mena de oro de Witwatersrand: no valen "
        "para otro mineral."
    ),
    "p.nomo.caption": (
        "Cada tramo horizontal reduce el tamaño (masa constante); cada tramo vertical divide "
        "(tamaño constante). Las rectas son de error constante: la ruta debe quedar por encima "
        "de la línea de seguridad. «Reproducir» recorre las etapas. El tamaño inicial solo "
        "dibuja el primer tramo."
    ),
    "p.col.stage": "Etapa",
    "p.col.dn": "dN (cm)",
    "p.col.mass": "Masa de entrada → salida (g)",
    "p.col.var": "Varianza relativa",
    "p.col.err": "Error de la etapa (%)",
    "p.col.cum": "Error acumulado (%)",
    "p.col.share": "Parte de la varianza (%)",
    "p.cum.caption": (
        "El error acumulado es la raíz de la suma de las varianzas relativas. Corrección por masa "
        "del lote: {corr}."
    ),
    "p.corr.yes": "sí",
    "p.corr.no": "no (como en la Tabla VIII de Minnitt)",
    "p.slope.caption": (
        "Pendiente m de Rosin-Rammler: es un supuesto. Entre m = 0,5 y 3 el error total cambia "
        "mucho porque el d95 entra al cubo."
    ),
    # ------------------------------------------------------------ oro grueso
    "g.grains": "Granos esperados en la alícuota",
    "g.p0": "Probabilidad de ningún grano",
    "g.median": "Mediana de los 1 000 ensayos",
    "g.median.delta": "ley real {grade} g/t",
    "g.above": "Ensayos con más de 2× la ley real",
    "g.sfa": (
        "Se esperan {lam} granos por alícuota, menos de {n} (criterio de Clifton): conviene el "
        "**screen fire assay** (unos {mass} g tamizados a {screen} µm, el fino en duplicado y el "
        "grueso entero)."
    ),
    "g.ok": "Se esperan {lam} granos por alícuota: cumple el criterio de {n} partículas de Clifton.",
    "g.caption1": (
        "Para {n} granos harían falta {mass} g de muestra. Con {lam} granos, los límites al 95 % "
        "de Clifton son {lo} % y +{hi} % (Poisson exacto: {elo} % y +{ehi} %; con pocos granos las "
        "ecuaciones de Clifton no valen del todo)."
    ),
    "g.caption2": (
        "La ley real (verde) y la mediana de lo simulado (rojo) no coinciden: con pocos granos, "
        "la mayoría de los ensayos da menos que la ley y unos pocos dan mucho más. «Reproducir» "
        "acumula de 10 a 1 000 ensayos."
    ),
    "g.alt": "Tres alícuotas con granos de oro",
    "g.grain": "Grano de {size} µm ({shape}): {mass} µg.",
    # ------------------------------------------------------------ validación
    "v.intro": (
        "Cada fuente se calcula con la ecuación de Gy y se compara con lo que publica. Lo que no "
        "cuadra se muestra tal cual."
    ),
    "v.col.source": "Fuente",
    "v.col.concept": "Concepto",
    "v.col.published": "Publicado",
    "v.col.calculated": "Calculado",
    "v.col.unit": "Unidad",
    "v.col.fits": "¿Cuadra?",
    "v.col.note": "Nota",
    "v.yes": "sí",
    "v.no": "no",
    "v.s1": "Minnitt 2017, Tabla VIII",
    "v.s2": "Chieregati 2017, Tabla 2",
    "v.s3": "Clifton 1969, Fig. 4",
    "v.s4": "Minnitt 2007, problemas 1 a 3 y apéndice",
    "v.s5": "Minnitt 2007 con c·f·g·ℓ = 448",
    "v.s6": "Minnitt 2007, apéndice (dℓ)",
    "v.p1": "19 varianzas por etapa (DSA y SFA)",
    "v.p2": "varianza y error de 4 etapas",
    "v.p3": "límites al 95 % de 7, 20, 75 y 400 partículas",
    "v.p4": "29,58 %, ≈16 kg y 0,9 cm",
    "v.p5": "los mismos",
    "v.p6": "dℓ = 0,001337 cm y 0,0011977 cm",
    "v.f1": "{n} de {m} filas",
    "v.f2": "{n} de {m}",
    "v.f3": "{n} de {m} límites (±2 puntos)",
    "v.f4": "{n} de 4 con los datos impresos (errata del artículo)",
    "v.f5": "{n} de {m}",
    "v.f6": "{n} de {m}",
    "v.h.m17": "#### Minnitt (2017), Tabla VIII: varianza por etapa",
    "v.h.chi": "#### Chieregati (2017), Tabla 2: protocolo de cobre",
    "v.h.cli": "#### Clifton y colaboradores (1969), Fig. 4: límites al 95 %",
    "v.h.m07": "#### Minnitt, Rice y Spangenberg (2007): un hallazgo, no una validación",
    "v.m07.printed": "**Con los datos impresos** (c = 16 000 000, f = 0,5, g = 0,25, ℓ = 0,000035):",
    "v.m07.implied": (
        "**Con c·f·g·ℓ = 448**, el valor que implican los resultados publicados "
        "(documenta la errata; no valida la fórmula):"
    ),
    "v.m07.lib": "**La parte del apéndice que sí cuadra:**",
    # ------------------------------------------------------------ gráficos
    "plot.play": "▶ Reproducir",
    "plot.pause": "⏸ Pausa",
    "plot.nomo.error": "error {level} %",
    "plot.nomo.safety": " (seguridad)",
    "plot.nomo.route": "ruta del protocolo",
    "plot.nomo.current": "punto actual",
    "plot.nomo.hover": "dN %{x:.3g} cm, masa %{y:.3g} g<extra></extra>",
    "plot.nomo.note": "{k} de {n}: {label} (dN {d} cm, {m} g)",
    "plot.nomo.title": "Nomograma de muestreo (Gy): la ruta del protocolo",
    "plot.nomo.x": "Tamaño máximo nominal dN (cm)",
    "plot.nomo.y": "Masa de la muestra (g)",
    "plot.stage.err": "error de la etapa",
    "plot.stage.cum": "acumulado",
    "plot.stage.safety": "seguridad {pct} %",
    "plot.stage.title": "Error por etapa y acumulado",
    "plot.stage.y": "Desviación estándar relativa (%)",
    "plot.sens.total": "error total",
    "plot.sens.chosen": "m elegida",
    "plot.sens.title": "El error depende de la pendiente m (supuesto)",
    "plot.sens.x": "Pendiente m de Rosin-Rammler",
    "plot.sens.y": "Error total del protocolo (%)",
    "plot.gran.d95": "d95 = {mm} mm",
    "plot.gran.spec": "especificación",
    "plot.gran.title": "Curvas granulométricas de las especificaciones (forma supuesta)",
    "plot.gran.x": "Tamaño (µm)",
    "plot.gran.y": "Pasante acumulado (%)",
    "plot.hist.sim": "ensayos simulados",
    "plot.hist.hover": "%{x:.3g} g/t: %{y} ensayos<extra></extra>",
    "plot.hist.true": "ley real {grade} g/t",
    "plot.hist.median": "mediana de lo simulado {median} g/t",
    "plot.hist.poisson": "Poisson analítico",
    "plot.hist.note": "{n} ensayos: mediana {median} g/t, máximo {max} g/t",
    "plot.hist.title": "Ensayos repetidos de la misma alícuota (Poisson, semilla fija)",
    "plot.hist.x": "Ley que daría el ensayo (g/t)",
    "plot.hist.y": "Número de ensayos",
    "plot.val.exact": "coincidencia exacta",
    "plot.val.fits": "cuadra al redondeo publicado",
    "plot.val.nofit": "no cuadra",
    "plot.val.hover": "%{text}<br>publicado %{x}<br>calculado %{y:.5f}<extra></extra>",
    "plot.val.title": "Varianza publicada frente a calculada (Minnitt 2017 y Chieregati 2017)",
    "plot.val.x": "Publicada",
    "plot.val.y": "Calculada",
    "plot.cli.published": "publicado (Fig. 4)",
    "plot.cli.eqs": "ecuaciones (11) y (12)",
    "plot.cli.exact": "Poisson exacto (Garwood)",
    "plot.cli.lower": "inferior",
    "plot.cli.upper": "superior",
    "plot.cli.title": "Límites al 95 % según las partículas por muestra (Clifton 1969)",
    "plot.cli.x": "Partículas por muestra",
    "plot.cli.y": "Error relativo (%)",
    "plot.m07.published": "publicado",
    "plot.m07.printed": "datos impresos (c·f·g·ℓ = 70)",
    "plot.m07.implied": "implícito (c·f·g·ℓ = 448)",
    "plot.m07.title": "Minnitt 2007, problema 1: error relativo (%)",
    # ------------------------------------------------------------ esquema de la alícuota
    "scheme.note": "esquema ilustrativo: las cantidades de granos sí son del cálculo",
    "svg.gold.title": "La misma alícuota de {mass} g, tres ensayos de la simulación",
    "svg.gold.low": "ensayo bajo (percentil 10)",
    "svg.gold.median": "ensayo mediano",
    "svg.gold.high": "ensayo alto (percentil 99)",
    "svg.gold.grain1": "{n} grano de oro",
    "svg.gold.grains": "{n} granos de oro",
    "svg.gold.grade": "ley que daría: {grade} g/t (real {real} g/t)",
    "svg.gold.shown": "(se dibujan {n})",
    "svg.gold.foot": "{note}; la posición de cada grano es ilustrativa.",
    "svg.gold.label": "Tres alícuotas con distinto número de granos de oro",
    # ------------------------------------------------------------ estado, casos y «Prueba esto»
    "estado.h": "#### Estado de la operación",
    "estado.nivel.ok": "En rango",
    "estado.nivel.aviso": "Aviso",
    "estado.nivel.mal": "Problema",
    "estado.todo_ok": "Operación dentro de rango.",
    "estado.ver": "Ver los {n} chequeos en rango",
    "prueba.h": "#### Prueba esto",
    "prueba.intro": (
        "Experimentos desde el **ejemplo de la barra lateral**; los números los calcula el modelo "
        "en vivo. El botón pone el cambio en los datos y «Volver al ejemplo» los restablece."
    ),
    "prueba.aplicar": "Aplicar este cambio a los controles",
    "prueba.restablecer": "Volver al ejemplo",
    "caso.h": "Casos publicados",
    "caso.intro": (
        "Cada botón pone en la barra lateral los datos de un caso publicado y, mientras estén "
        "puestos, la pestaña muestra lo publicado junto a lo calculado (Δ = calculado − publicado)."
    ),
    "caso.activo": " (puesto)",
    "caso.col.pub": "Publicado",
    "caso.col.calc": "Calculado",
    "caso.col.delta": "Δ",
    # ------------------------------------------------------------ protocolo: estado y pruebas
    "prot.chk.seg.ok": (
        "Las {n} divisiones quedan bajo el error de seguridad de {seg} % (la mayor da {max})."
    ),
    "prot.chk.seg.una": "etapa {n} ({rsd})",
    "prot.chk.seg.mal": "Sobre el error de seguridad de {seg} %: {etapas}.",
    "prot.crit.seg": (
        "Criterio de la app, no una norma: cada división debe dar un error relativo no mayor que "
        "el control «Error de seguridad del nomograma» (es la línea de seguridad del nomograma)."
    ),
    "prot.chk.masas": "Cada una de las {n} divisiones toma menos masa de la que recibe.",
    "prot.crit.masas": (
        "Definición del cálculo: una división toma MS de una masa ML mayor (σ² = IHL·(1/MS − 1/ML)); "
        "si no, el protocolo no se calcula y la pestaña lo dice."
    ),
    "prot.chk.kalpha.dado": (
        "K = {k} y α = {alpha} son los que Minnitt (2017) calibró para una mena de oro de "
        "Witwatersrand: no valen para otro mineral."
    ),
    "prot.chk.kalpha.propio": "K = {k} y α = {alpha} son los tuyos: se calibran por mineral.",
    "prot.crit.kalpha": (
        "Fuente: Minnitt (2017), J. SAIMM 117(2), para esa mena; K y α se calibran por mineral y "
        "nunca se suponen (docstring de `gy.py` y ficha de la pestaña)."
    ),
    "prot.chk.lote": (
        "La Tabla VIII de Minnitt (2017) no usa la corrección por masa del lote: con ella el "
        "error sale menor que el publicado."
    ),
    "prot.crit.lote": (
        "Fuente: `gy.py` (Minnitt 2017 omite la corrección en su Tabla VIII) y la validación de "
        "esta app, que la reproduce sin la corrección."
    ),
    "prot.caso.minnitt": "Minnitt (2017), Tabla VIII, método DSA",
    "prot.caso.res": (
        "**Tabla VIII de Minnitt (2017), método DSA.** Varianza relativa de cada división frente "
        "a la impresa (K = 167,4 y α = 1,123, sin corrección por masa del lote)."
    ),
    "prot.exp.division.titulo": "Dividir más masa tras el chancado",
    "prot.exp.division.texto": (
        "Con PREP-31B (se divide {m1} g en vez de {m0} g tras chancar a 2 mm) el error total baja "
        "de {t0} % a {t1} %, y el de la etapa 1 de {e0} % a {e1} %. Aun así, el protocolo sigue "
        "sin cumplir la seguridad de {seg} %."
    ),
    "prot.exp.alicuota.titulo": "Pasar a una alícuota de 50 g",
    "prot.exp.alicuota.texto": (
        "Con {a1} g en vez de {a0} g, el error de la última división baja de {l0} % a {l1} %, "
        "pero el total casi no se mueve ({t0} % a {t1} %): la etapa 1 ya aporta {s0} % de la "
        "varianza y con la alícuota mayor aporta {s1} %. El cuello está antes de la alícuota."
    ),
    "prot.exp.lote.titulo": "Quitar la corrección por masa del lote",
    "prot.exp.lote.texto": (
        "Sin el término 1/ML, el error total sube de {t0} % a {t1} %: es lo que hace la Tabla "
        "VIII de Minnitt (2017). La corrección se activa siempre, salvo para reproducir esa tabla."
    ),
    # ------------------------------------------------------------ oro grueso: estado y pruebas
    "oro.crit.clifton": (
        "Fuente: Clifton, Hunter, Swanson y Phillips (1969), USGS Professional Paper 625-C: unas "
        "{n} partículas por muestra para ±50 % al 95 %."
    ),
    "oro.chk.fig4.ok": (
        "Con {lam} granos esperados, el cálculo cae dentro del rango de {lo} a {hi} partículas "
        "con que esta app contrasta las ecuaciones de Clifton."
    ),
    "oro.chk.fig4.mal": (
        "Con {lam} granos esperados, el cálculo cae fuera del rango de {lo} a {hi} partículas con "
        "que esta app contrasta las ecuaciones de Clifton: léelo junto al Poisson exacto."
    ),
    "oro.crit.fig4": (
        "Fuente: la pestaña Validación contrasta los límites de Clifton con la Fig. 4 de 1969 para "
        "{lo} a {hi} partículas (`validacion.py`, CLIFTON_PUBLISHED); fuera de ese rango no hay "
        "contraste."
    ),
    "oro.exp.grano100.titulo": "Moler el oro a granos de 100 µm",
    "oro.exp.grano100.texto": (
        "Con granos de {g100} µm en vez de {g0} µm, cada grano pesa mucho menos y los granos "
        "esperados suben de {lam0} a {lam1} (×{ratio}): la probabilidad de no recibir ninguno "
        "baja de {p0} % a {p1} %. Sigue por debajo de {n} granos y el panel mantiene el aviso."
    ),
    "oro.exp.alicuota.titulo": "Pasar a una alícuota de 50 g",
    "oro.exp.alicuota.texto": (
        "Con {a50} g en vez de {a0} g, los granos esperados suben de {lam0} a {lam1} (×{ratio}, "
        "proporcional a la masa) y la probabilidad de ninguno baja de {p0} % a {p1} %. Sigue "
        "por debajo de {n} granos: el panel mantiene el aviso."
    ),
    "oro.exp.grano50.titulo": "Moler el oro a granos de 50 µm",
    "oro.exp.grano50.texto": (
        "Con granos de {g50} µm esperas {lam1} granos por alícuota: se cumple el criterio de {n} "
        "partículas, el panel queda en rango, la probabilidad de ninguno cae a {p1} % y la "
        "mediana de los ensayos pasa de {med0} a {med1} g/t, más cerca de la ley real "
        "({ley} g/t)."
    ),
    "vi.ok": "Cuadran con lo publicado",
    "vi.ok.help": (
        "Comprobaciones que cuadran con la cifra publicada, sumadas sobre todas las áreas de esta "
        "pestaña. En la carga fundente solo cuenta el veredicto «cuadra»."
    ),
    "vi.no": "No cuadran",
    "vi.no.help": "Las que no cuadran; cada tabla de abajo dice cuáles y por qué.",
    "vi.areas": "Áreas validadas",
    "vi.areas.help": (
        "Ecuación de Gy, carga fundente, cianuración, sedimentación, copelación y control de "
        "calidad."
    ),
}
