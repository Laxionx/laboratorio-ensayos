"""Textos en español de la pestaña «Cianuración en botella», de sus datos, su ficha, su guía, su
esquema y su validación (claves `cn.*`, `cv.*`, `svg.c.*`, `dato.c_*`, `ficha.cianuracion.*`)."""

T = {
    "tab.cian": "Cianuración en botella",
    "group.Cianuración": "Cianuración en botella",
    # ------------------------------------------------------------ datos de la barra lateral
    "opt.Potencial (Ec. 3 de los autores)": "Potencial (Ec. 3 de los autores)",
    "opt.Primer orden con meseta (nuestro)": "Primer orden con meseta (nuestro)",
    "opt.Difusión (L)": "Difusión (L)",
    "opt.Reacción (M)": "Reacción (M)",
    "opt.Mixto (N)": "Mixto (N)",
    "dato.c_model.label": "Modelo que mueve el indicador",
    "dato.c_model.meaning": (
        "Qué modelo cinético mueve el indicador de recuperación de la botella animada. Las curvas "
        "de todos los modelos se ven siempre en los gráficos."
    ),
    "dato.c_model.source": "no se mide: solo elige qué curva se ve avanzar",
    "dato.c_rpm.label": "Giro de la botella",
    "dato.c_rpm.meaning": (
        "Vueltas por minuto de los rodillos. El procedimiento estándar de botella usa de 30 a 32; "
        "mueve la botella del dibujo, no cambia el cálculo."
    ),
    "dato.c_rpm.source": "se fija en el rodillo del laboratorio (Cetin et al., 2017: 30 a 32 rpm)",
    "dato.c_head.label": "Ley de cabeza S0",
    "dato.c_head.meaning": (
        "Oro del mineral antes de lixiviar, en ppb. Con ella la recuperación es "
        "R = (1 − residuo / S0)."
    ),
    "dato.c_head.source": (
        "análisis al fuego de la muestra de cabeza (el valor 1 070 se dedujo de la Tabla 4 del "
        "artículo)"
    ),
    "dato.c_factor.label": "Sólido por solución, F",
    "dato.c_factor.meaning": (
        "Pasa el oro de la solución a ppb del sólido para el balance: cabeza = residuo + F · "
        "solución."
    ),
    "dato.c_factor.source": (
        "es la razón entre el volumen de solución y la masa de sólido del ensayo (el valor 1,935 "
        "se dedujo de la Tabla 4; el artículo no la publica)"
    ),
    "dato.c_split.label": "Corte entre tramos",
    "dato.c_split.meaning": (
        "Tiempo que separa la disolución rápida de la lenta: cada tramo se ajusta aparte, y el "
        "punto del corte entra en los dos."
    ),
    "dato.c_split.source": "se elige mirando el gráfico de recuperación (los autores cortan en 7 h)",
    # ------------------------------------------------------------ ficha y guía
    "ficha.cianuracion.hace": (
        "Lee un ensayo de cianuración (oro en la solución y en el residuo a distintos tiempos): "
        "calcula la recuperación y la ley de cabeza por balance, avisa si las filas no son "
        "coherentes y compara qué modelo cinético describe la disolución de verdad y cuál solo "
        "ajusta bien en apariencia. Una botella animada gira a las rpm del procedimiento mientras "
        "un indicador sigue la curva del modelo elegido."
    ),
    "ficha.cianuracion.entra": (
        "La tabla de tiempos, oro en solución y oro en residuo (precargada con la Tabla 4 del "
        "artículo), la ley de cabeza, el factor sólido por solución, el corte entre tramos, el "
        "modelo del indicador y las rpm de la botella."
    ),
    "ficha.cianuracion.sale": (
        "La recuperación de cada fila, la cabeza por balance y los avisos; los términos del "
        "núcleo sin reaccionar (L, M, N) con sus rectas, R² e interceptos por tramo; el modelo "
        "potencial y un primer orden con meseta; el error de cada modelo en puntos de "
        "recuperación y el esquema de la botella."
    ),
    "ficha.cianuracion.autores": (
        "Roostaei, Kordparijaei y Mesroghli (2026), «Cyanide dissolution of gold-bearing iron "
        "oxide minerals: kinetic studies and optimization using response surface methodology», "
        "*Discover Applied Sciences* (doi 10.1007/s42452-026-08420-8, acceso abierto CC BY-NC-ND; "
        "aquí solo se usan sus cifras citadas y sus ecuaciones). Giro de la botella: Cetin, Altun, "
        "Atalay y Büyüktanır (2017), «Bottle Roll Testing for Cyanidation of Gold Ores», MCM'17, "
        "paper MMME 148, doi 10.11159/mmme17.148 (30 a 32 rpm)."
    ),
    "ficha.cianuracion.limit.1": (
        "Los datos de la Tabla 4 vienen de ensayos en un vaso agitado de 2 L, no de una botella: la "
        "botella y sus rpm ilustran el ensayo, y no se publica su tamaño ni su carga, así que el "
        "dibujo no los inventa."
    ),
    "ficha.cianuracion.limit.2": (
        "Solo describe esta mena y estos siete puntos: no predice la recuperación de otro "
        "mineral. No incluye química del cianuro (consumo, especiación) ni carbón activado."
    ),
    "ficha.cianuracion.limit.3": (
        "Lo que el artículo no publica y aquí se dedujo, y se declara: la constante B del término "
        "mixto (0,7033 y 0,75), la ley de cabeza (1 070 ppb) y el factor sólido por solución "
        "(1,935). El primer orden con meseta, la regla que deja fuera el punto de 2 h y la "
        "tolerancia de 5 % de la cabeza son nuestros."
    ),
    "ficha.cianuracion.limit.4": (
        "Las rectas de cada tramo usan 3 o 4 puntos (con 1 o 2 grados de libertad): un R² alto con "
        "tan pocos puntos no prueba el mecanismo."
    ),
    "guide.h.cian": "### Cianuración en botella: qué modelo describe la disolución",
    "guide.cian.1": (
        "En un ensayo de cianuración se muele el mineral, se mezcla con solución de cianuro y se "
        "toman muestras a distintos tiempos. La recuperación sale del oro que queda en el residuo "
        "(S_t) frente a la ley de cabeza (S_0):"
    ),
    "guide.cian.2": (
        "El modelo del núcleo sin reaccionar supone que la partícula se disuelve de afuera hacia "
        "adentro y que un término (difusión L, reacción M o mixto N) crece como una recta con el "
        "tiempo que pasa por el origen. Aquí las rectas no pasan por el origen: la disolución "
        "rápida de la primera hora no la explica ninguno, y el modelo potencial describe mejor los "
        "datos pero es empírico. La pestaña **Cianuración en botella** lo muestra con las cifras."
    ),
    # ------------------------------------------------------------ calculadora
    "cn.cal.h": "#### Calculadora: recuperación y ley de cabeza",
    "cn.cal.intro": (
        "Cada fila es una muestra: tiempo, oro en la solución y oro en el residuo (ppb). La "
        "recuperación es R = (1 − residuo / S0) con S0 = {head} ppb; la cabeza por balance es "
        "residuo + F · solución con F = {factor}. Los dos datos se cambian en la barra lateral, y "
        "la tabla viene cargada con la Tabla 4 del artículo."
    ),
    "cn.reset": "Volver al ejemplo de la Tabla 4",
    "cn.col.t": "Tiempo (h)",
    "cn.col.sol": "Au en solución (ppb)",
    "cn.col.res": "Au en residuo (ppb)",
    "cn.col.rec": "Recuperación (%)",
    "cn.col.sold": "Oro disuelto (ppb del sólido)",
    "cn.col.head": "Cabeza por balance (ppb)",
    "cn.col.dev": "Desvío de la cabeza (%)",
    "cn.err.filas": "La tabla debe tener entre {lo} y {hi} filas.",
    "cn.err.numero": "Hay celdas vacías, con texto o con números no válidos: todos deben ser números positivos.",
    "cn.err.rango": "Un valor se sale de los límites: tiempos hasta {t_max} h y ppb hasta {ppb_max}.",
    "cn.err.orden": "Los tiempos deben ir en orden creciente, sin repetirse.",
    "cn.err.residuo_mayor": "El oro del residuo debe ser menor que la ley de cabeza ({cabeza} ppb).",
    "cn.err.pocos_puntos": "Faltan puntos para ajustar este modelo.",
    "cn.err.recuperacion": "La recuperación no puede llegar a 100 %.",
    "cn.warn.no_monotona": (
        "A las {t} h la recuperación ({v} %) supera la de una fila posterior: en un ensayo normal "
        "el oro no se vuelve a depositar. Ese punto no entra en las rectas, como los autores "
        "dejan el de 2 h."
    ),
    "cn.warn.cabeza": (
        "A las {t} h la cabeza por balance se aparta {v} % de la declarada: solución y residuo no "
        "cuadran con la ley de cabeza."
    ),
    "cn.cal.res": "Última fila: **{r} %** de recuperación a las {t} h con S0 = {head} ppb.",
    # ------------------------------------------------------------ modelos
    "cn.mod.h": "#### Modelos cinéticos: cuál describe y cuál solo ajusta",
    "cn.mod.intro": (
        "Se ajustan los tres términos del núcleo sin reaccionar por tramos (hasta {cut} h y desde "
        "{cut} h), el modelo potencial de los autores y un primer orden con meseta, "
        "*R = R∞ (1 − e^(−k t))*, que es nuestro. Con X la fracción disuelta: L = 1 − 3(1−X)^(2/3) "
        "+ 2(1−X), M = 1 − (1−X)^(1/3) y N = (1 − 2X/3) − (1−X)^(2/3) + B·M."
    ),
    "cn.stretch.0": "todo el ensayo",
    "cn.stretch.1": "hasta {cut} h",
    "cn.stretch.2": "desde {cut} h",
    "cn.m.model": "Modelo",
    "cn.m.stretch": "Tramo",
    "cn.m.n": "Puntos",
    "cn.m.r2": "R²",
    "cn.m.a": "Intercepto",
    "cn.m.b": "Pendiente (1/h)",
    "cn.m.r0": "Recuperación en t = 0 (%)",
    "cn.m.rmse": "Error medio (puntos de %)",
    "cn.msg.origin": (
        "**Las rectas del núcleo sin reaccionar no pasan por el origen.** En el primer tramo sus "
        "interceptos son {i1} (difusión), {i2} (reacción) y {i3} (mixto); si el modelo valiera, "
        "valdrían 0 en t = 0. Con ellos los modelos ya darían {z1} %, {z2} % y {z3} % de oro "
        "disuelto antes de empezar: no explican la disolución rápida de la primera hora (la "
        "medición da {r1} % a las {t1} h). Además cada recta se apoya en {n} puntos: un R² de {r2} "
        "con tan pocos puntos ajusta bien en apariencia, pero no prueba el mecanismo."
    ),
    "cn.msg.fewpoints": "Con estos datos faltan puntos: cada tramo necesita al menos {n} filas usadas.",
    "cn.msg.models": (
        "El modelo potencial es empírico: describe el residuo (St ∝ t^−{b}) con R² {r2p} y un "
        "error medio de {rmse} puntos de recuperación, pero no dice qué controla la reacción. El "
        "primer orden con meseta ajusta mal (R² {r2o}; R∞ = {rinf} %, k = {k} 1/h): una sola "
        "constante no alcanza para una disolución en dos etapas."
    ),
    "cn.mod.caption": (
        "B (inferida, el artículo no la publica): {b1} para el tramo hasta el corte y {b2} para el "
        "siguiente. En t = 0 el potencial no existe y se dibuja en 0 en la botella. Las rectas se "
        "dibujan punteadas hasta t = 0 para ver su intercepto."
    ),
    "cn.plot.used": "Punto usado",
    "cn.plot.excluded": "Punto excluido",
    "cn.plot.rec.title": "Recuperación de oro contra tiempo: medido y modelos",
    "cn.plot.t": "Tiempo (h)",
    "cn.plot.rec.y": "Recuperación (%)",
    "cn.plot.origin": "Origen (0, 0)",
    "cn.plot.line": "Recta",
    "cn.plot.tramo1": "primer tramo",
    "cn.plot.tramo2": "segundo tramo",
    "cn.plot.intercept": "intercepto {a}",
    "cn.plot.terms.title": "Términos linealizados contra el tiempo, con las rectas por tramo",
    "cn.plot.terms.y": "Valor del término",
    # ------------------------------------------------------------ animación
    "cn.ani.h": "#### La botella girando",
    "cn.ani.alt": "Botella de laboratorio en corte, girando, con un indicador de recuperación",
    "cn.ani.caption": (
        "El indicador sigue el modelo «{model}» con el tiempo comprimido (se declara en el "
        "dibujo); las marcas rojas son las recuperaciones medidas."
    ),
    "svg.c.title": "Botella de cianuración, en corte",
    "svg.c.rpm": "Giro: {rpm} rpm, una vuelta cada {period} s",
    "svg.c.model": "Modelo: {model}",
    "svg.c.time": "Tiempo comprimido: {tmax} h en {run} s",
    "svg.c.clock": "Tiempo del ensayo:",
    "svg.c.recovery": "Recuperación del modelo:",
    "svg.c.measured": "Marcas rojas: recuperación medida (con su hora)",
    "svg.c.legend": (
        "Esquema, no a escala: las cantidades sí son del cálculo (giro, recuperación del modelo en "
        "cada instante y los {n} puntos medidos). La botella, su tamaño y el nivel de pulpa son "
        "ilustrativos: el artículo no los publica. El tiempo está comprimido: las {tmax} h del "
        "ensayo pasan en {run} s."
    ),
    "svg.c.label": "Esquema animado de una botella de cianuración en corte con un indicador de recuperación",
    # ------------------------------------------------------------ validación
    "cv.h": "### Cianuración en botella: cifras del artículo de Roostaei et al. (2026)",
    "cv.intro": (
        "Cortes fijados antes de correr. Ley de cabeza de cada fila de la Tabla 4: S0 = residuo / "
        "(1 − R) debe caer en el intervalo que deja el redondeo de esa fila, con S0 = 1 070 ppb. "
        "Tabla 6: L y M a 3 decimales; N con la B inferida. Tabla 7: R², intercepto y pendiente al "
        "redondeo publicado, con los mismos puntos (sin el de 2 h) y sobre los términos redondeados "
        "a 3 decimales como los tabuló el artículo. Ec. 3: 228,046, 0,332 y 0,937."
    ),
    "cv.summary": (
        "Cuadran: Tabla 4, {t4} de {n4}; Tabla 6, {t6} de {n6}; Tabla 7, {t7} de {n7}; Ec. 3, {e3} "
        "de {n3}."
    ),
    "cv.h.t4": "**Tabla 4: ley de cabeza y recuperación de cada fila**",
    "cv.h.t6": "**Tabla 6: los términos L, M y N**",
    "cv.h.t7": "**Tabla 7: las seis regresiones por tramo**",
    "cv.h.e3": "**Ec. 3: el modelo potencial**",
    "cv.kind.cabeza": "Cabeza (ppb), fila de",
    "cv.kind.recuperacion": "Recuperación (%), fila de",
    "cv.kind.L": "L",
    "cv.kind.M": "M",
    "cv.kind.N1": "N1",
    "cv.kind.N2": "N2",
    "cv.kind.r2": "R²",
    "cv.kind.intercepto": "Intercepto",
    "cv.kind.pendiente": "Pendiente",
    "cv.kind.a": "a (ppb)",
    "cv.kind.b": "b",
    "cv.col.concept": "Concepto",
    "cv.col.published": "Publicado",
    "cv.col.calculated": "Calculado",
    "cv.col.fits": "¿Cuadra?",
    "cv.col.note": "Nota",
    "cv.note.m1": "no cuadra: ver el hallazgo de abajo",
    "cv.b": (
        "**B inferida.** El artículo no publica la constante B de N. Como N − L/3 = B·M, sus "
        "celdas dan B = {b1} para el tramo hasta 7 h (cualquier valor de {lo1} a {hi1} "
        "reproduce las cuatro celdas) y B = {b2} para el de 7 a 48 h ({lo2} a {hi2}). La ley de "
        "cabeza {s0} ppb y el factor sólido por solución {f} también se dedujeron de la Tabla 4: "
        "las cabezas por fila quedan entre {h0} y {h1} ppb."
    ),
    "cv.m1": (
        "**Hallazgo: la fila M1 de la Tabla 7 no sale de los datos.** Con los términos M de la "
        "Tabla 6 ({m1}, {m3} y {m7}) da R² {c2}, intercepto {ci} y pendiente {cs}, y el "
        "artículo imprime {p2}, {pi} y {ps}. Sus propios F ({f}) y R² son coherentes entre sí "
        "(un F de {f} implica R² {r2}) y las otras cinco filas sí cuadran: parece una errata de "
        "esa fila, y no se corrigió ni se maquilló."
    ),
    "cv.rows": (
        "La fila de 2 h queda fuera de las regresiones, como en el artículo: su recuperación "
        "(85,70 %) supera la de las 3 h (82,34 %), y el oro no se vuelve a depositar."
    ),
}
