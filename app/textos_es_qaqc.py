"""Textos en español de la pestaña «Control de calidad», de sus datos, ficha y guía (claves `qc.*`,
`dato.q_*`, `ficha.qaqc.*`, `guide.*qaqc*`); los de su validación están en `textos_es_qaqc_val.py`."""

T = {
    "tab.qaqc": "Control de calidad",
    "group.Control de calidad": "Control de calidad",
    # ------------------------------------------------------------ datos de la barra lateral
    "opt.CRM propio": "CRM propio",
    "opt.Serie sintética de ejemplo": "Serie sintética de ejemplo",
    "opt.GEMAS: plata (Ag), no es oro": "GEMAS: plata (Ag), no es oro",
    "opt.GEMAS: germanio (Ge), no es oro": "GEMAS: germanio (Ge), no es oro",
    "qc.dup.el.Ag": "plata (Ag)",
    "qc.dup.el.Ge": "germanio (Ge)",
    "opt.Duplicado de campo": "Duplicado de campo",
    "opt.Rechazo grueso": "Rechazo grueso",
    "opt.Pulpa": "Pulpa",
    "dato.q_crm.label": "Material de referencia (CRM)",
    "dato.q_crm.meaning": "El CRM contra el que se controla la serie: uno de los cuatro de OREAS con su valor y su SD precargados, o uno propio con el valor y la SD que se escriben abajo.",
    "dato.q_crm.source": "certificado de análisis del fabricante (OREAS: Au por ensayo al fuego, tabla de «performance gates»)",
    "dato.q_val.label": "Valor del CRM propio",
    "dato.q_val.meaning": "Valor certificado de Au del CRM propio, en g/t (solo con «CRM propio»).",
    "dato.q_val.source": "certificado del CRM",
    "dato.q_sd.label": "SD del CRM propio",
    "dato.q_sd.meaning": "Desviación estándar certificada del CRM propio, en g/t (solo con «CRM propio»). Los límites de ±2 SD y ±3 SD salen de ella.",
    "dato.q_sd.source": "certificado del CRM (la SD de un certificado suele ser la entre laboratorios)",
    "dato.q_crm_fuente.label": "Resultados del CRM",
    "dato.q_crm_fuente.meaning": "De dónde salen los resultados del CRM: una serie sintética de ejemplo (semilla fija) o la tabla editable de la sección, donde se pegan los propios.",
    "dato.q_crm_fuente.source": "los resultados del laboratorio, en el orden en que se ensayaron",
    "dato.q_n.label": "Largo de la serie de ejemplo",
    "dato.q_n.meaning": "Cuántos resultados tiene la serie sintética del CRM y la de blancos.",
    "dato.q_n.source": "a elección: es solo un ejemplo (30 resultados es un lote chico)",
    "dato.q_sesgo.label": "Sesgo del ejemplo",
    "dato.q_sesgo.meaning": "Desplaza la media de la serie sintética del CRM este porcentaje del valor certificado, para ver cuándo se disparan las reglas.",
    "dato.q_sesgo.source": "a elección: 0 % es un laboratorio sin sesgo; Rainy River informa sesgos de −0,5 % a −2,5 %",
    "dato.q_dup_fuente.label": "Pares de duplicados",
    "dato.q_dup_fuente.meaning": "Los 104 pares de duplicados de campo de GEMAS (plata o germanio de suelos, NO oro) o la tabla editable, donde se pegan los propios.",
    "dato.q_dup_fuente.source": "Demetriades y Argyraki (2025), tutorial con datos GEMAS, CC BY 4.0",
    "dato.q_dup_tipo.label": "Tipo de duplicado",
    "dato.q_dup_tipo.meaning": "Define el umbral: campo y rechazo grueso, 80 % de los pares con diferencia relativa menor de 20 %; pulpa, 80 % dentro de 10 %.",
    "dato.q_dup_tipo.source": "Stoker (2006), citado en el informe técnico de Rainy River (2025)",
    "dato.q_dup_p.label": "Precisión P de Thompson-Howarth",
    "dato.q_dup_p.meaning": "La precisión (a 95 % de confianza) cuyas líneas de percentil 90 y 99 se trazan: 10 % o 20 % de la concentración.",
    "dato.q_dup_p.source": "se fija con el objetivo del laboratorio; el tutorial muestra 10 % y 20 %",
    "dato.q_blk_fuente.label": "Resultados de blancos",
    "dato.q_blk_fuente.meaning": "De dónde salen los blancos: una serie sintética de ejemplo o la tabla editable de la sección.",
    "dato.q_blk_fuente.source": "los resultados del laboratorio, en el orden en que se ensayaron",
    "dato.q_ld.label": "Límite de detección (LD)",
    "dato.q_ld.meaning": "Límite de detección del método, en g/t: los blancos se comparan con 3 y 10 veces este valor.",
    "dato.q_ld.source": "el del método del laboratorio (el de Au por ensayo al fuego en Rainy River es 0,005 g/t)",
    "dato.q_pico.label": "Pico del ejemplo de blancos",
    "dato.q_pico.meaning": "Un blanco de la serie sintética vale este múltiplo del LD (0 = ninguno), para ver la alerta y la falla.",
    "dato.q_pico.source": "a elección: 4 × LD pasa el indicador de 3 × LD y 12 × LD pasa el de falla",
    # ------------------------------------------------------------ ficha y guía
    "ficha.qaqc.hace": "Califica un lote de ensayos con las reglas de control de calidad que publican los informes técnicos NI 43-101 y los fabricantes de materiales de referencia: la carta de control de un CRM con ±2 SD y ±3 SD, los duplicados con el gráfico de Thompson-Howarth y las diferencias relativas, y los blancos contra 3 y 10 veces el límite de detección. Cada regla se cita. Aparte muestra cómo se certifica un estándar: los 150 resultados crudos de CDN-GS-2X y el recorte que da su valor publicado.",
    "ficha.qaqc.entra": "Los resultados de un CRM en el orden en que se ensayaron, los pares original-duplicado y los blancos (cada uno, de ejemplo o pegado en una tabla editable), el CRM, el tipo de duplicado, la precisión P de Thompson-Howarth y el límite de detección.",
    "ficha.qaqc.sale": "Para cada serie, el veredicto del lote según las reglas citadas y de qué regla sale; la carta de control que se arma punto a punto y marca la regla que dispara cada resultado; el gráfico de Thompson-Howarth con sus líneas y el porcentaje de pares bajo el umbral; los blancos contra sus líneas; y el histograma de los 150 resultados de CDN-GS-2X con el recorte.",
    "ficha.qaqc.autores": "OREAS (certificados de análisis de los CRM 501b, 501c, 503c y 200). CDN Resource Laboratories (certificado CDN-GS-2X, 2021). Abzalov (2011), «Sampling errors and control of assay data quality in exploration and mining geology», en *Applications and Experiences of Quality Control*, InTech, cap. 29 (CC BY-SA 3.0). Demetriades y Argyraki (2025), tutorial de Thompson-Howarth, IUGS-CGGB n.º 2, DOI 10.5281/zenodo.15557648 (CC BY 4.0), con los datos de GEMAS (Reimann y otros, 2014). Informes técnicos NI 43-101 de Rainy River (New Gold, 2025) y Loma Larga (Dundee Precious Metals, 2021). Thompson y Howarth (1973), *Analyst* 98:153.",
    "ficha.qaqc.limit.1": "Las series de ejemplo (CRM, blancos y la tabla de duplicados con que arranca la tabla editable) son SINTÉTICAS, de semilla fija: muestran cómo actúan las reglas, no el desempeño de ningún laboratorio. Los únicos resultados reales son los 150 de CDN-GS-2X y los 104 pares de GEMAS.",
    "ficha.qaqc.limit.2": "Las reglas vienen de informes técnicos y de la literatura, no de una norma: la app no dice que un lote «cumple la norma», solo qué reglas citadas se disparan. Cada proyecto fija su propio protocolo (qué CRM, cuántos, qué hacer con una falla).",
    "ficha.qaqc.limit.3": "La SD de un certificado es la que sale del ensayo entre laboratorios (round robin): incluye la variación entre laboratorios, y una discusión de 2011 sobre prácticas de control de calidad (InTech, cap. 30) advierte que los límites de un laboratorio no deben fijarse con ella sino con su propia historia. Aquí se usa la del certificado porque es lo que las reglas citadas hacen.",
    "ficha.qaqc.limit.4": "GEMAS son duplicados de campo de suelos agrícolas de Europa (plata y germanio por agua regia e ICP): sirve para probar el algoritmo de Thompson-Howarth con datos abiertos, pero NO es oro y el umbral de 80 % bajo 20 % viene de duplicados de oro. Los 13 pares de germanio con media no positiva (bajo el límite de detección) no tienen línea y cuentan fuera, como en el recuento publicado.",
    "ficha.qaqc.limit.5": "El informe de Rainy River no da la fórmula de la diferencia relativa (RPD): se toma la diferencia absoluta sobre la media del par, que es el doble del HARD de Abzalov. De los rangos publicados (80-85 %) se usa el extremo bajo, 80 %.",
    "ficha.qaqc.limit.6": "Blancos: solo se aplican 10 veces el límite de detección (falla, de Rainy River y Loma Larga) y 3 veces (el indicador que Rainy River cuenta aparte). No hay una regla numérica abierta para el arrastre entre muestras, así que no se evalúa.",
    "ficha.qaqc.limit.7": "Las tablas pegadas se validan en el servidor (números finitos y no negativos, hasta 2 000 filas) y no se guardan en ningún lado: al cerrar la página se pierden. No hay sistema de gestión del laboratorio (LIMS).",
    "guide.h.qaqc": "Control de calidad: CRM, duplicados y blancos",
    "guide.qaqc.1": "Un laboratorio que ensaya oro no solo mide: controla lo que mide. Intercala **materiales de referencia certificados** (CRM, con un valor y una SD conocidos), **duplicados** (la misma muestra dos veces) y **blancos** (material sin oro). Las reglas más usadas en los informes técnicos son: un CRM fuera de ±3 SD rechaza el lote, dos seguidos fuera de ±2 SD piden re-ensayarlo (Rainy River); los duplicados deben coincidir (80 % de los pares con diferencia relativa menor de 20 % en campo y rechazo grueso, o dentro de 10 % en pulpa); y un blanco con más de 10 veces el límite de detección es una falla.",
    "guide.qaqc.2": "Dos fórmulas de la pestaña: el HARD de un par, que mide cuánto se parecen dos mediciones, y las líneas de Thompson-Howarth, que dicen cuánta diferencia entre duplicados es de esperar con una precisión P (z = 1,6449 para el percentil 90 y 2,5758 para el 99; C es la media del par). **Pasa el control** cuando el 90 % de los pares queda bajo la primera línea y el 99 % bajo la segunda. La pestaña reproduce el valor certificado de CDN-GS-2X (2,388 ± 0,232 g/t) desde sus 150 resultados, las tablas de ±2 SD y ±3 SD de OREAS y los recuentos publicados del tutorial.",
    # ------------------------------------------------------------ la pestaña
    "qc.intro": "Cuatro controles, de arriba abajo: un **CRM** contra sus límites, los **duplicados**, los **blancos** y **cómo se certifica un estándar**. Cada uno usa una serie sintética de ejemplo o los datos que se peguen en su tabla editable (se elige en la barra lateral), y termina en un veredicto con la regla que lo produce. Las reglas y sus fuentes están al pie de cada sección.",
    "qc.src.synth": "serie sintética de ejemplo",
    "qc.src.table": "tabla del usuario",
    "qc.reset": "Volver a la serie de ejemplo",
    "qc.col.res": "Resultado (g/t)",
    "qc.col.a": "Original",
    "qc.col.b": "Duplicado",
    "qc.table.hint": "Para controlar los resultados propios, elige «Tabla editable» en la barra lateral (grupo «Control de calidad»); se pega o se escribe una tabla de hasta {max} filas.",
    "qc.err.filas": "La tabla necesita entre {lo} y {hi} filas con datos.",
    "qc.err.numero": "La tabla solo admite números finitos: hay una celda con texto, infinito o un valor que no es número.",
    "qc.err.negativo": "Un resultado de ensayo no puede ser negativo: hay una celda con un valor menor que cero.",
    "qc.err.incompleta": "Hay una fila con una sola celda llena: cada par necesita el original y el duplicado.",
    "qc.err.crm": "El CRM necesita un valor y una SD positivos y finitos.",
    "qc.err.precision": "La precisión P debe ser un número positivo.",
    "qc.err.sin_pares": "Ningún par tiene una suma positiva: no hay diferencia relativa que calcular.",
    "qc.err.ld": "El límite de detección debe ser un número positivo y finito.",
    "qc.err.tipo": "El tipo de duplicado no es uno de los tres conocidos.",
    "qc.err.recorte": "El recorte deja menos de dos resultados.",
    # ------------------------------------------------------------ CRM
    "qc.crm.h": "#### Material de referencia (CRM): carta de control",
    "qc.crm.intro": "**{name}**: valor certificado **{v} g/t**, SD **{sd} g/t** ({sdnote}). Límites de ±2 SD: **{lo2} a {hi2} g/t**; de ±3 SD: **{lo3} a {hi3} g/t**.",
    "qc.crm.sdnote.pub": "la SD publicada es {sdpub}; los límites son los impresos en el certificado, que valor × 1RSD ({rsd} %) reproduce a ±0,001",
    "qc.crm.sdnote.own": "la que se escribió en la barra lateral",
    "qc.crm.m.n": "Resultados",
    "qc.crm.m.f2": "Fuera de ±2 SD",
    "qc.crm.m.f2.delta": "{pct} % de la serie",
    "qc.crm.m.f3": "Fuera de ±3 SD",
    "qc.crm.m.f3.delta": "tasa de fallas {pct} %",
    "qc.crm.m.bias": "Sesgo de la media",
    "qc.crm.m.bias.delta": "media {mean} g/t",
    "qc.crm.v.pasa": "Ninguna regla de rechazo ni de re-ensayo se dispara. {f2} de {n} resultados ({pct} %) caen fuera de ±2 SD (con buena calidad se espera hasta 5 %) y ninguno fuera de ±3 SD.",
    "qc.crm.v.aviso": "**Aviso.** {f2} de {n} resultados ({pct} %) caen fuera de ±2 SD, y con buena calidad se espera hasta 5 % (Abzalov). No hay resultados fuera de ±3 SD ni dos seguidos fuera de ±2 SD.",
    "qc.crm.v.reensayar": "**Re-ensayo del lote.** {pares} resultado(s) cierran un par de resultados seguidos fuera de ±2 SD: la regla de Rainy River pide re-ensayar el lote.",
    "qc.crm.v.rechazar": "**Rechazo del lote.** {f3} de {n} resultados ({pct} %) caen fuera de ±3 SD: la regla de Rainy River y de OREAS rechaza el lote, y lo aceptable es una tasa de fallas menor de 5 %.",
    "qc.crm.state.ok": "Dentro de ±2 SD",
    "qc.crm.state.fuera_2sd": "Fuera de ±2 SD (advertencia)",
    "qc.crm.state.dos_seguidos": "2.º seguido fuera de ±2 SD (re-ensayo)",
    "qc.crm.state.fuera_3sd": "Fuera de ±3 SD (rechazo)",
    "qc.crm.rule.ok": "dentro de ±2 SD: ninguna regla",
    "qc.crm.rule.fuera_2sd": "fuera de ±2 SD: advertencia",
    "qc.crm.rule.dos_seguidos": "segundo seguido fuera de ±2 SD: re-ensayo del lote",
    "qc.crm.rule.fuera_3sd": "fuera de ±3 SD: rechazo del lote",
    "qc.crm.note": "Resultado {n}: {v} g/t, z = {z} → {rule}",
    "qc.crm.cert": "Valor certificado",
    "qc.crm.2sd": "±2 SD",
    "qc.crm.3sd": "±3 SD",
    "qc.crm.title": "Carta de control de {name} ({src})",
    "qc.crm.x": "Orden de ensayo (n.º del resultado)",
    "qc.crm.y": "Au (g/t)",
    "qc.crm.caption": "«Reproducir» arma la carta resultado por resultado y rotula la regla que dispara cada uno; el deslizador la recorre a mano. Nada arranca solo.",
    "qc.crm.rules": "**Reglas aplicadas.** (1) Un resultado fuera de ±3 SD rechaza el lote, y dos resultados seguidos fuera de ±2 SD piden re-ensayarlo: Rainy River Mine, informe NI 43-101 (New Gold, 2025), sec. 11. OREAS lee igual sus intervalos: advertencia o rechazo si varios resultados caen fuera de 2 SD, rechazo si uno cae fuera de 3 SD. (2) Tasa de fallas menor de 5 % por CRM, contando fallas fuera de ±3 SD: Rainy River. (3) Con buena calidad, 95 % de los puntos cae dentro de ±2 SD, |X − μ| ≤ 2σ: Abzalov (2011), Eq. 21. (4) Sesgo = media medida / valor certificado − 1: Rainy River y Loma Larga. «Fuera» es estrictamente más allá del límite.",
    # ------------------------------------------------------------ duplicados
    "qc.dup.h": "#### Duplicados: Thompson-Howarth y diferencia relativa",
    "qc.dup.intro.gemas": "**GEMAS, {el}: 104 pares de duplicados de campo** (suelos agrícolas de Europa, agua regia e ICP, en mg/kg; datos del tutorial de Demetriades y Argyraki, 2025, CC BY 4.0). **No es oro**: sirve para probar el algoritmo, y los veredictos de abajo son una demostración, no una calificación de ningún laboratorio de oro.",
    "qc.dup.intro.table": "**{n} pares pegados por el usuario.** Tipo: {tipo}; precisión P de {p} %.",
    "qc.dup.m.pairs": "Pares",
    "qc.dup.m.in90": "Bajo la línea 90",
    "qc.dup.m.in99": "Bajo la línea 99",
    "qc.dup.m.pct": "Pares bajo el umbral",
    "qc.dup.m.pct.delta": "RPD {rule} {u} %",
    "qc.dup.m.cnt.delta": "{pct} % de {n}",
    "qc.dup.rule.lt": "menor de",
    "qc.dup.rule.le": "dentro de",
    "qc.dup.v.th.pasa": "**Thompson-Howarth con P = {p} %: pasa.** {pct90} % de los pares queda bajo la línea 90 (hace falta 90 %) y {pct99} % bajo la línea 99 (hace falta 99 %).",
    "qc.dup.v.th.falla": "**Thompson-Howarth con P = {p} %: no pasa.** {pct90} % de los pares queda bajo la línea 90 (hace falta 90 %) y {pct99} % bajo la línea 99 (hace falta 99 %).",
    "qc.dup.th.sin": "{n} pares con media no positiva no tienen línea y cuentan fuera.",
    "qc.dup.v.dup.pasa": "**Duplicados ({tipo}): pasa.** {pct} % de los {n} pares evaluables tiene una diferencia relativa {rule} {u} %; el mínimo es {min} %. HARD medio: {hard} %.",
    "qc.dup.v.dup.falla": "**Duplicados ({tipo}): no pasa.** {pct} % de los {n} pares evaluables tiene una diferencia relativa {rule} {u} %; el mínimo es {min} %. HARD medio: {hard} %.",
    "qc.dup.rules": "**Reglas aplicadas.** (1) Líneas de Thompson-Howarth: |a − b| ≤ z · √2 · (P / 2) · C, con z = 1,6449 (percentil 90) y 2,5758 (99) y C la media del par; con P = 10 % dan 0,11631 C y 0,182135 C: Thompson y Howarth (1973), Demetriades y Argyraki (2025). El 90 % de los pares debe quedar bajo la primera línea y el 99 % bajo la segunda. (2) HARD = |a − b| / (a + b) y diferencia relativa (RPD) = 2 HARD: Abzalov (2011), Tabla 3. (3) Campo y rechazo grueso, 80-85 % de los pares con RPD menor de 20 %; pulpa, 80 % dentro de 10 %: Stoker (2006), citado por Rainy River (2025); aquí se exige el extremo bajo, 80 %. El informe no da la fórmula del RPD.",
    "qc.th.title": "Thompson-Howarth: diferencia entre duplicados contra su media",
    "qc.th.x": "Media del par, C (escala logarítmica)",
    "qc.th.y": "Diferencia absoluta |a − b| (escala logarítmica)",
    "qc.th.in90": "Bajo la línea 90 ({n})",
    "qc.th.in99": "Entre la 90 y la 99 ({n})",
    "qc.th.out": "Sobre la línea 99 ({n})",
    "qc.th.l90": "Línea 90, P = {p} %",
    "qc.th.l99": "Línea 99, P = {p} %",
    "qc.th.hidden": "{n} de {tot} pares no se dibujan en la escala logarítmica (media no positiva o diferencia 0); cuentan igual en los conteos, los porcentajes y el veredicto.",
    "qc.rpd.title": "Diferencia relativa de los pares, de menor a mayor",
    "qc.rpd.x": "Porcentaje de pares",
    "qc.rpd.y": "RPD (%)",
    "qc.rpd.curve": "Pares ordenados",
    "qc.rpd.limit": "Umbral de RPD, {u} %",
    "qc.rpd.min": "Mínimo de pares, {m} %",
    "qc.rpd.note": "{pct} % de los pares bajo {u} %",
    "qc.dup.caption": "La curva debe cruzar el umbral de RPD (línea horizontal) a la derecha del mínimo de pares (línea vertical).",
    # ------------------------------------------------------------ blancos
    "qc.blk.h": "#### Blancos: contra 3 y 10 veces el límite de detección",
    "qc.blk.intro": "**{n} blancos** ({src}). Límite de detección {ld} g/t: la alerta es más de 3 × LD ({l3} g/t) y la falla, más de 10 × LD ({l10} g/t).",
    "qc.blk.m.n": "Blancos",
    "qc.blk.m.s3": "Sobre 3 × LD",
    "qc.blk.m.s10": "Sobre 10 × LD",
    "qc.blk.m.delta": "{pct} % de la serie",
    "qc.blk.v.pasa": "Ningún blanco supera 3 veces el límite de detección: no se ve contaminación.",
    "qc.blk.v.alerta": "**Alerta.** {s3} blanco(s) superan 3 × LD ({pct3} %), pero ninguno supera 10 × LD: Rainy River cuenta este indicador aparte y no lo trata como falla.",
    "qc.blk.v.falla": "**Falla.** {s10} blanco(s) superan 10 × LD ({pct10} %): Rainy River y Loma Larga lo consideran contaminación significativa.",
    "qc.blk.rules": "**Reglas aplicadas.** Falla si un blanco supera 10 veces el límite de detección: Rainy River (sec. 11, criterio de New Gold) y Loma Larga (sec. 11.3.2.2). Más de 3 veces es el indicador que Rainy River cuenta aparte (558 blancos de mármol en 2024: 1 sobre 3 × LD, 0 sobre 10 × LD). «Supera» es estrictamente más.",
    "qc.blk.ok": "Dentro de 3 × LD",
    "qc.blk.alert": "Entre 3 y 10 × LD (alerta)",
    "qc.blk.fail": "Sobre 10 × LD (falla)",
    "qc.blk.ld": "LD = {ld} g/t",
    "qc.blk.l3": "3 × LD",
    "qc.blk.l10": "10 × LD",
    "qc.blk.title": "Blancos ({src})",
    "qc.blk.x": "Orden de ensayo (n.º del blanco)",
    "qc.blk.y": "Au (g/t)",
    # ------------------------------------------------------------ certificar un estándar
    "qc.cert.h": "#### Cómo se certifica un estándar: CDN-GS-2X",
    "qc.cert.intro": "El certificado de CDN-GS-2X publica los **{n} resultados** de Au que 15 laboratorios dieron a 10 réplicas del estándar (30 g de ensayo al fuego, g/t). Su valor sale de ellos: se calcula la media y la SD de todos, se descarta lo que cae fuera de media ± 2 SD y se recalcula. La app lo hace en una sola pasada.",
    "qc.cert.m.keep": "Resultados que quedan",
    "qc.cert.m.keep.delta": "de {n}",
    "qc.cert.m.mean": "Media recortada",
    "qc.cert.m.mean.delta": "publicado {pub} g/t",
    "qc.cert.m.band": "2 SD",
    "qc.cert.m.band.delta": "publicado ± {pub} g/t",
    "qc.cert.res": "Con los {n} resultados: media {m0} g/t y SD {s0} g/t; el corte a ±2 SD es de {lo} a {hi} g/t y descarta {drop} resultados. Los {keep} restantes dan **{m} ± {band} g/t**, y el certificado publica **{pub} ± {pubband} g/t**: {fit}.",
    "qc.cert.fit.yes": "coinciden al redondeo publicado",
    "qc.cert.fit.no": "no coinciden",
    "qc.cert.note": "El certificado describe además una prueba t que descarta laboratorios cuya media difiere de la de los demás; no publica el detalle de esa prueba. La app NO la usa: el recorte a ±2 SD sin descartar laboratorios ya da la cifra publicada. Una SD que sale de varios laboratorios es la SD entre laboratorios, la misma con la que se fijan los límites de ±2 SD y ±3 SD de un CRM.",
    "qc.cert.keep": "Quedan ({n})",
    "qc.cert.drop": "Descartados ({n})",
    "qc.cert.mean": "Media recortada, {m} g/t",
    "qc.cert.band": "± 2 SD de la media recortada, {s} g/t",
    "qc.cert.cut": "Corte de media ± {k} SD (todos)",
    "qc.cert.title": "CDN-GS-2X: los {n} resultados y el recorte a ±2 SD",
    "qc.cert.x": "Au (g/t)",
    "qc.cert.y": "Resultados por intervalo",
    # ------------------------------------------------------------ indicadores, estado y pruebas
    "qc.verd.pasa": "Pasa",
    "qc.verd.aviso": "Aviso",
    "qc.verd.reensayar": "Re-ensayar",
    "qc.verd.rechazar": "Rechazar",
    "qc.i.crm": "Lote del CRM",
    "qc.i.crm.help": (
        "Veredicto de la carta de control del CRM: rechazo con un resultado fuera de ±3 SD, "
        "re-ensayo con dos seguidos fuera de ±2 SD y aviso si más de 5 % queda fuera de ±2 SD."
    ),
    "qc.i.dup": "Duplicados bajo umbral",
    "qc.i.dup.help": (
        "Porcentaje de pares evaluables con diferencia relativa bajo el umbral de su tipo (campo "
        "y rechazo grueso: 20 %; pulpa: 10 %); se pide al menos 80 %."
    ),
    "qc.i.blk": "Blancos sobre 3 × LD",
    "qc.i.blk.help": (
        "Blancos que superan 3 veces el límite de detección, sobre el total; más de 10 veces "
        "es una falla."
    ),
    "qc.src.crm": (
        "Rainy River Mine, NI 43-101 (2025), p. 97 y 108: fuera de ±3 SD se rechaza el lote y dos "
        "seguidos fuera de ±2 SD piden re-ensayo; OREAS usa esos mismos intervalos; Abzalov "
        "(2011), Eq. 21: con buena calidad, al menos 95 % queda dentro de ±2 SD."
    ),
    "qc.src.th": (
        "Thompson y Howarth (1973); Demetriades y Argyraki (2025): el 90 % de los pares debe "
        "quedar bajo la línea del percentil 90 y el 99 %, bajo la del 99, con la precisión P al "
        "95 % de confianza."
    ),
    "qc.src.dup": (
        "Stoker (2006), citado por Rainy River (2025), p. 103: campo y rechazo grueso, 80-85 % "
        "de los pares con RPD < 20 %; pulpa, 80 % dentro de 10 % (la app toma el extremo bajo)."
    ),
    "qc.src.blk": (
        "Rainy River (2025), p. 101, y Loma Larga, sec. 11.3.2.2: falla con más de 10 veces el "
        "límite de detección; más de 3 veces es el indicador que el informe cuenta aparte."
    ),
    "qc.src.cert": (
        "CDN Resource Laboratories, certificado CDN-GS-2X (2021): media y SD del round robin, se "
        "descarta lo que cae fuera de ±2 SD y se recalcula; el intervalo es 2 SD de esa media."
    ),
    "qc.chk.cert.ok": (
        "Certificación del estándar CDN-GS-2X: la media ({m} g/t) y las 2 SD recortadas "
        "({band} g/t) coinciden con lo publicado, al redondeo."
    ),
    "qc.chk.cert.mal": (
        "Certificación del estándar CDN-GS-2X: la media ({m} g/t) y las 2 SD recortadas "
        "({band} g/t) no coinciden con lo publicado."
    ),
    "qc.exp.sesgo.titulo": "Dar un sesgo de +4 % a la serie del CRM",
    "qc.exp.sesgo.texto": (
        "Con un sesgo de {sesgo} % en la serie de ejemplo, el sesgo medido pasa de {s0} % a "
        "{s1} %, los resultados fuera de ±3 SD pasan de {f30} a {f31} y el panel marca el "
        "rechazo del lote."
    ),
    "qc.exp.precision.titulo": "Pedir una precisión de 20 % a los duplicados",
    "qc.exp.precision.texto": (
        "Con P = {p1} % en vez de {p0} %, las líneas de Thompson-Howarth se abren: {b90} % de los "
        "pares queda bajo la línea 90 (antes {a90} %) y {b99} % bajo la 99 (antes {a99} %). Aun "
        "así el panel no lo da por bueno: hacen falta 90 % y 99 %."
    ),
    "qc.exp.pico.titulo": "Subir el pico de los blancos",
    "qc.exp.pico.texto": (
        "Con un pico de {pico1} × LD en vez de {pico0} × LD, los blancos sobre {k} × LD pasan de "
        "{x0} a {x1} y el panel marca la falla: contaminación significativa para Rainy River y "
        "Loma Larga."
    ),
}
