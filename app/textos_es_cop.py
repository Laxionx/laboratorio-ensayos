"""Textos en español de la pestaña «Copelación», de sus datos, ficha, guía, esquema y validación
(claves `cp.*`, `svg.k.*`, `dato.k_*`, `ficha.copelacion.*`, `guide.*cop*`)."""

T = {
    "tab.cop": "Copelación",
    "group.Copelación": "Copelación",
    # ------------------------------------------------------------ datos de la barra lateral
    "opt.Del botón de la fusión": "Del botón de la fusión",
    "opt.Valor propio": "Valor propio",
    "opt.Razón de Rose (según el oro)": "Razón de Rose (según el oro)",
    "opt.Mínimo de Bugbee (3 a 1)": "Mínimo de Bugbee (3 a 1)",
    "opt.Razón propia": "Razón propia",
    "dato.k_temp.label": "Temperatura de la copela",
    "dato.k_temp.meaning": "Temperatura de la copela en la mufla, en °C. Es lo que más pesa en la pérdida de plata y de oro.",
    "dato.k_temp.source": "se mide con un pirómetro junto a la copela; Bugbee da 700 a 775 °C con cristales de litargirio en la copela, y la Tabla IX llega a 1 000 °C (la del oro, a 1 075 °C)",
    "dato.k_pb_src.label": "Plomo de la copelación",
    "dato.k_pb_src.meaning": "De dónde sale el plomo del botón: el que calcula la pestaña Fusión (encadena fusión y copelación) o un valor propio.",
    "dato.k_pb_src.source": "es el botón de la fusión, que se pesa antes de copelar",
    "dato.k_pb.label": "Plomo propio",
    "dato.k_pb.meaning": "Masa del botón de plomo, en g (solo si se elige «Valor propio»).",
    "dato.k_pb.source": "se pesa el botón; las tablas de Lodge cubren de 10 a 25 g y la pestaña Fusión apunta a 28 g",
    "dato.k_au.label": "Oro del botón",
    "dato.k_au.meaning": "Oro que trae el botón antes de copelar, en mg. Con él se calcula la plata que hay que agregar.",
    "dato.k_au.source": "sale del ensayo (ley por masa de la muestra); la Tabla XII se midió con 200 mg",
    "dato.k_ag.label": "Plata del botón",
    "dato.k_ag.meaning": "Plata que ya trae el botón, en mg, sin la que se agrega para partir.",
    "dato.k_ag.source": "sale del ensayo; la Tabla XI cubre de 2 a 200 mg",
    "dato.k_modo.label": "Razón plata:oro para partir",
    "dato.k_modo.meaning": "Cómo se elige la razón objetivo: la de Rose según el peso del oro, el mínimo de Bugbee (3 a 1) o una propia.",
    "dato.k_modo.source": "Rose (Metallurgy of Gold, 6.ª ed., p. 511) y Bugbee (p. 118 y 121)",
    "dato.k_razon.label": "Razón propia",
    "dato.k_razon.meaning": "Razón plata:oro que se quiere tras copelar (solo si se elige «Razón propia»).",
    "dato.k_razon.source": "Bugbee: al menos 3 a 1, y 8 a 10 a 1 en perlas de mena",
    "dato.k_ley.label": "Ley de oro medida",
    "dato.k_ley.meaning": "Ley que dio el ensayo, en g/t. Se corrige con la pérdida de oro de la copela.",
    "dato.k_ley.source": "es el resultado del ensayo antes de corregir",
    # ------------------------------------------------------------ ficha y guía
    "ficha.copelacion.hace": (
        "Calcula cuánto oro y plata se pierde en la copela según la temperatura, el plomo del "
        "botón y la plata presente, corrige la ley medida por esa pérdida y dice cuánta plata "
        "hay que agregar (encuarte) para que la partición en ácido nítrico funcione. Dibuja las "
        "tablas de Bugbee con el modelo encima y anima el botón de plomo que se achica hasta "
        "dejar la perla."
    ),
    "ficha.copelacion.entra": (
        "La temperatura de la copela, el plomo del botón (el de la pestaña Fusión o uno propio), "
        "el oro y la plata del botón, cómo se elige la razón plata:oro (Rose, mínimo de Bugbee o "
        "propia) y la ley de oro medida."
    ),
    "ficha.copelacion.sale": (
        "La pérdida de plata (con su banda) y la de oro, la ley corregida, la plata que se agrega, "
        "la razón al partir con su veredicto (insuficiente, solo en lámina, lenta o buena), la masa y la "
        "composición de la perla y un aviso cada vez que un dato sale del rango de una tabla."
    ),
    "ficha.copelacion.autores": (
        "Pérdidas, temperaturas y razones de partición: Bugbee (1922), *A Textbook of Fire "
        "Assaying*, Tablas IX a XII (p. 100 a 103) y p. 118 a 122 (dominio público); los datos son de "
        "Lodge (*Assaying*), Godshall (1896, Trans. AIME 26:473-484), Smith y Rose (*Metallurgy of "
        "Gold*), tal como los cita Bugbee. La validación usa el artículo original de Godshall "
        "(dominio público, archive.org). El avance de la animación no es de ninguna tabla."
    ),
    "ficha.copelacion.limit.1": (
        "Un modelo de tablas: la pérdida de plata multiplica el efecto de la temperatura (Lodge, "
        "200 mg de plata y 10 g de plomo), el del plomo (Lodge, 685 °C) y el de la plata presente "
        "(Godshall). Que se multipliquen es un supuesto, no una medida. Fuera del rango de cada "
        "tabla no se extrapola: se usa el extremo y se avisa."
    ),
    "ficha.copelacion.limit.2": (
        "La pérdida de oro es la de la Tabla XII (200 mg de oro sin plata y 10 g de plomo) y no "
        "depende del plomo ni de la plata. Bugbee dice que crece al bajar el oro y que la plata "
        "la reduce (Smith; Fig. 41) pero no da cifras: con menos oro el modelo subestima y con "
        "plata presente sobrestima."
    ),
    "ficha.copelacion.limit.3": (
        "La banda es solo de reproducibilidad (la dispersión de las tres series de Godshall); el "
        "oro usa la misma porque su dispersión no está publicada. El sesgo frente a otro "
        "laboratorio es mayor que la banda: el modelo de Lodge queda corto frente a Godshall y no "
        "pasa el corte (pestaña Validación)."
    ),
    "ficha.copelacion.limit.4": (
        "El avance de la animación y la forma de la pérdida acumulada son ilustrativos: Bugbee da "
        "la curva minuto a minuto solo como figura (Fig. 40, con 30 g de plomo y 100 mg de plata) "
        "y no se digitalizó. El tamaño del botón entero es fijo en el dibujo; el de los demás "
        "cuadros sale del cálculo."
    ),
    "ficha.copelacion.limit.5": (
        "No incluye las impurezas (cobre, telurio, bismuto y otras aumentan la pérdida; Bugbee, "
        "Tabla XIII), ni el tipo y el estado de la copela, la corriente de aire de la mufla o la "
        "salpicadura. Tampoco la copelación de platinoides ni la instrumental."
    ),
    "ficha.copelacion.limit.6": (
        "La partición se evalúa solo por la razón plata:oro (Bugbee: al menos 3 a 1; en perlas "
        "de mena, 8 a 10 a 1; Rose, según el oro). No modela el ácido, el tiempo ni el oro que "
        "se rompe en polvo."
    ),
    "guide.h.cop": "### Copelación y partición: de la perla al oro",
    "guide.cop.1": (
        "La copelación separa los metales preciosos del plomo: el plomo se oxida a litargirio, la "
        "copela lo absorbe y queda una perla de oro y plata. Una parte de la plata y algo de oro "
        "se pierden, más con más temperatura, más plomo y menos plata (Bugbee, Tablas IX a XII). "
        "El modelo multiplica tres factores de esas tablas y la ley se corrige con la pérdida:"
    ),
    "guide.cop.2": (
        "Para partir en ácido nítrico hace falta al menos 3 veces más plata que oro; en perlas de "
        "mena conviene de 8 a 10 veces (Bugbee), y Rose da la razón según el peso del oro. Esa "
        "plata se agrega antes de copelar (encuarte) y también pierde: la calculadora agrega la "
        "necesaria para que, tras la copela, quede la razón pedida. Los límites están en la "
        "ficha de la pestaña y la comparación con Godshall, en la pestaña Validación."
    ),
    # ------------------------------------------------------------ resultados
    "cp.err.temp": "La temperatura de la copela debe ser un número positivo.",
    "cp.err.plomo": "El plomo del botón debe ser un número positivo.",
    "cp.err.plata": "La plata del botón debe ser un número, cero o más.",
    "cp.err.oro": "El oro del botón debe ser un número positivo.",
    "cp.err.ley": "La ley medida debe ser un número, cero o más.",
    "cp.err.perdida": "La pérdida debe estar entre 0 y 1 (sin llegar a 1).",
    "cp.err.razon": "La razón plata:oro propia debe ser un número positivo.",
    "cp.err.modo": "No se conoce ese modo de elegir la razón plata:oro.",
    "cp.err.cuadros": "La animación necesita al menos 2 cuadros.",
    "cp.warn.temp": "La temperatura sale del rango de la tabla ({lo} a {hi} °C): se usa el valor del extremo, no se extrapola.",
    "cp.warn.plomo": "El plomo sale del rango de la Tabla X ({lo} a {hi} g): se usa el valor del extremo, no se extrapola.",
    "cp.warn.plata": "La plata total sale del rango de la Tabla XI ({lo} a {hi} mg): se usa el valor del extremo, no se extrapola.",
    "cp.warn.congelado": "A {t0} °C o menos el botón se congela en la Tabla XII (Bugbee): no hay copelación y la pérdida de oro es la de {t1} °C.",
    "cp.warn.fusion": "La pestaña Fusión no pudo calcular el botón con sus datos actuales; se usa el plomo propio de {pb} g.",
    "cp.m.ag": "Pérdida de plata",
    "cp.m.band": "banda {lo} a {hi} %",
    "cp.m.au": "Pérdida de oro",
    "cp.m.au.delta": "Tabla XII, sin plata",
    "cp.m.add": "Plata que se agrega",
    "cp.m.add.delta": "razón objetivo {ratio} a 1",
    "cp.m.pearl": "Perla",
    "cp.m.pearl.delta": "{au} % de oro",
    "cp.cal.h": "#### Pérdidas y ley corregida",
    "cp.cal.pb.fusion": "el botón de la pestaña Fusión",
    "cp.cal.pb.own": "valor propio",
    "cp.cal.res": (
        "A **{temp} °C**, con **{pb} g** de plomo ({source}), {au} mg de oro y {ag} mg de plata "
        "en total (con el encuarte): se pierde **{lag} %** de la plata y **{lau} %** del oro. "
        "El plomo líquido tiene {rho} g/cm³ a esa temperatura (misma ecuación que la fusión)."
    ),
    "cp.cal.ley": (
        "Ley medida {med} g/t, ley corregida **{cor} g/t** = medida / (1 − pérdida de oro de "
        "{lau} %)."
    ),
    "cp.cal.caption": (
        "La banda de la plata es la dispersión de las tres series de Godshall (sd de ln de {sd} %, "
        "factor {f}): reproducibilidad, no sesgo. La pérdida de oro es la de 200 mg de oro sin "
        "plata: con menos oro es mayor y con plata presente, menor (Bugbee, p. 103)."
    ),
    "cp.enc.h": "#### Encuarte y partición",
    "cp.enc.intro": (
        "Modo: {mode}. Razón objetivo tras copelar: **{ratio} a 1** (plata : oro). La plata que se "
        "agrega ya cuenta la que se pierde en la copela."
    ),
    "cp.enc.col.what": "Concepto (mg)",
    "cp.enc.au": "Oro del botón",
    "cp.enc.ag0": "Plata que ya trae",
    "cp.enc.add": "Plata que se agrega",
    "cp.enc.ag1": "Plata total antes de copelar",
    "cp.enc.ag2": "Plata que queda en la perla",
    "cp.enc.au2": "Oro que queda en la perla",
    "cp.enc.pearl": "Perla",
    "cp.enc.state.buena": "Razón al partir {ratio} a 1: buena para partir (a partir de {rec} a 1).",
    "cp.enc.state.lenta": "Razón al partir {ratio} a 1: parte, pero con más ácido y más tiempo (entre {min} y {rec} a 1).",
    "cp.enc.state.lamina": "Razón al partir {ratio} a 1: solo parte si la aleación se lamina fina, como en lingote, y queda plata sin disolver; para una perla Bugbee pide al menos {min} a 1.",
    "cp.enc.state.insuficiente": "Razón al partir {ratio} a 1: insuficiente; ni en lingote se parte con menos de {low} a 1 (Bugbee pide al menos {min} a 1 para una perla).",
    "cp.enc.caption": (
        "Bugbee (p. 118 a 122): perlas de mena, de {rec} a {hi} veces más plata que oro; lingote "
        "de oro, {bullion} o {bullion2} a 1 con la aleación laminada; el máximo de oro es {gold} % (3 a 1)."
    ),
    "cp.rose.h": "Razón de Rose según el peso del oro (Bugbee, p. 121)",
    "cp.rose.au": "Oro (mg)",
    "cp.rose.ratio": "Razón Ag:Au",
    "cp.rose.lt": "menos de 0,1",
    "cp.rose.gt": "más de {mg}",
    "cp.rose.caption": "Entre sus filas se interpola en escala logarítmica. «Menos de 0,1 mg» es «20 o 30 a 1»: el punto de 0,1 mg usa el promedio, {mid} (supuesto).",
    "cp.or": "o",
    # ------------------------------------------------------------ gráficos
    "cp.plot.h": "#### Las tablas de Bugbee y el modelo",
    "cp.plot.intro": "Los puntos son las tablas tal como están impresas; la línea discontinua es el modelo; la estrella, el cálculo de arriba. En gris, fuera del rango de la tabla (ahí el modelo se queda en el extremo).",
    "cp.plot.caption": "Primero: Tablas IX y XII (200 mg, 10 g de plomo). Segundo: Tabla X (685 °C) y, en verde, el promedio final de Godshall con 200 mg de plata (otro laboratorio, sin temperatura medida). Tercero: Tabla XI y las otras dos series de Godshall con ½ A.T. de plomo, relativas a la pérdida de 200 mg.",
    "cp.plot.ix": "Plata, Tabla IX (Lodge)",
    "cp.plot.model.ag": "Modelo, plata (200 mg, 10 g)",
    "cp.plot.xii": "Oro, Tabla XII (Lodge)",
    "cp.plot.model.au": "Modelo, oro",
    "cp.plot.frozen": "botón congelado",
    "cp.plot.you.ag": "Su plata (con banda)",
    "cp.plot.you.au": "Su oro",
    "cp.plot.temp.title": "Pérdida contra temperatura",
    "cp.plot.temp.x": "Temperatura (°C)",
    "cp.plot.loss.y": "Pérdida (%)",
    "cp.plot.x": "Plata, Tabla X (Lodge, 685 °C)",
    "cp.plot.model.pb": "Modelo (relativo a 10 g)",
    "cp.plot.god200": "Godshall, 200 mg (otro laboratorio)",
    "cp.plot.clamped": "fuera de la tabla",
    "cp.plot.pb.title": "Pérdida de plata contra plomo",
    "cp.plot.pb.x": "Plomo (g)",
    "cp.plot.xi": "Tabla XI (Godshall, ½ A.T.)",
    "cp.plot.rep.primera": "Godshall, primera serie",
    "cp.plot.rep.tercera": "Godshall, tercera serie",
    "cp.plot.model.ag.rel": "Modelo",
    "cp.plot.you.rel": "Su plata total",
    "cp.plot.ag.title": "Efecto de la plata presente",
    "cp.plot.ag.x": "Plata (mg)",
    "cp.plot.rel.y": "Pérdida relativa a la de 200 mg",
    # ------------------------------------------------------------ animación
    "cp.ani.h": "#### La copela y la perla",
    "cp.ani.alt": "Copela en corte dentro de la mufla: el botón de plomo se achica mientras el litargirio se absorbe en la copela y queda la perla de oro y plata",
    "cp.ani.caption": "El botón se achica según la masa que sale del cálculo (plomo, oro y plata en cada cuadro); el color de la mufla sigue la temperatura con una rampa ilustrativa.",
    "svg.k.muffle": "Mufla (esquema)",
    "svg.k.cupel": "Copela de ceniza de hueso",
    "svg.k.bead": "perla",
    "svg.k.title": "Copelación",
    "svg.k.cond": "{temp} °C · plomo {pb} g",
    "svg.k.progress": "Avance (ilustrativo)",
    "svg.k.mass": "Masa del botón",
    "svg.k.lead": "Plomo que queda",
    "svg.k.pearl": "Perla: {mg} mg ({au} % de oro)",
    "svg.k.au": "Oro que queda: {mg} mg (pérdida {loss} %)",
    "svg.k.ag": "Plata que queda: {mg} mg (pérdida {loss} %)",
    "svg.k.ratio": "Razón plata:oro al partir: {ratio} a 1",
    "svg.k.legend": "Esquema, no a escala: las cantidades sí son del cálculo (masa del botón y de la perla, oro y plata que quedan, plomo de {pb} g). El avance, de 0 a 100 % en {run} s, y la forma de la pérdida acumulada son ilustrativos, porque Bugbee da la curva minuto a minuto solo como figura (Fig. 40). Color de la mufla: rampa ilustrativa de temperatura. El tamaño del botón entero es fijo en el dibujo.",
    "svg.k.label": "Esquema animado de una copela en corte con un botón de plomo que se achica hasta dejar la perla de oro y plata",
    # ------------------------------------------------------------ validación
    "cp.v.h": "### Fase 3: copelación y partición (Bugbee 1922 y Godshall 1896)",
    "cp.v.intro": "El modelo se ajusta con las tablas de Lodge que imprime Bugbee (IX, X y XII; la plata presente sale de la Tabla XI, que es de Godshall) y se compara con el artículo original de Godshall (otro experimentador; 1 assay-ton = {a} g; promedio final de la p. 483). Cortes fijados antes de correr: error relativo dentro de ±25 % en la pérdida de plata, con la temperatura de Godshall, que no midió, supuesta en {t0} °C (centro de 700 a 775 °C).",
    "cp.v.h.tables": "#### Tablas transcritas (cifras literales de la imagen del escaneo)",
    "cp.v.col.table": "Tabla",
    "cp.v.col.page": "Página impresa",
    "cp.v.col.scan": "Página del escaneo",
    "cp.v.col.rows": "Filas",
    "cp.v.col.author": "Autor",
    "cp.v.col.what": "Qué mide",
    "cp.v.t.ix": "pérdida de plata contra temperatura (200 mg, 10 g de plomo)",
    "cp.v.t.x": "pérdida de plata contra plomo (200 mg, 685 °C)",
    "cp.v.t.xi": "pérdida de plata contra plata presente (½ A.T. de plomo)",
    "cp.v.t.xii": "pérdida de oro contra temperatura (200 mg, 10 g de plomo)",
    "cp.v.xi.note": "La Tabla XI es la fila de ½ A.T. de la segunda serie de Godshall. En {ag} mg Bugbee imprime {b} y Godshall imprime {g} (se conserva lo de Bugbee).",
    "cp.v.h.overlap": "#### Solapamiento y validación cuantitativa",
    "cp.v.overlap": "Las tablas de Lodge solo tienen 200 mg de plata y de 10 a 25 g de plomo; Godshall tiene siete cantidades de plata (2 a 200 mg) y cuatro de plomo ({pbmin} a {pbmax} g), con temperatura sin medir. Solapan **{n} de {total}** celdas (200 mg de plata y ½ y ¾ A.T. de plomo): solo ellas son una comparación cuantitativa, con corte de ±{cut} %. Las demás se informan como tendencia.",
    "cp.v.col.ag": "Plata (mg)",
    "cp.v.col.pb": "Plomo (g)",
    "cp.v.col.pub": "Publicada (%)",
    "cp.v.col.pred": "Predicha (%)",
    "cp.v.col.err": "Error relativo (%)",
    "cp.v.col.fits": "¿Cuadra?",
    "cp.v.col.timp": "T que daría la cifra (°C, diagnóstico)",
    "cp.v.verdict": "**Veredicto: cuadran {ok} de {n}.** El modelo de Lodge queda corto frente a Godshall: otro laboratorio y otra copela, y Godshall no midió la temperatura. No se ajustó nada para que pase. La última columna es un diagnóstico, no una validación: Godshall se parece a Lodge a unos {tlo} a {thi} °C, no al intervalo de cristales.",
    "cp.v.h.trend": "#### Tendencias (las 28 celdas del promedio final de Godshall)",
    "cp.v.trend": "- La pérdida de plata es mayor con 2 mg que con 200 mg en {a} de {na} plomos (**no es independiente**: el efecto de la plata sale de Godshall).\n- La pérdida con 1 A.T. supera a la de ¼ A.T. en {b} de {nb} cantidades de plata.\n- La predicha queda a menos de un factor {f} de la publicada en {c} de {nc} celdas.",
    "cp.v.rep": "Réplica de la plata (informativa, sin corte de aprobación): de {total} razones pérdida(Ag) / pérdida(200 mg) de las series primera y tercera de Godshall con ½ A.T., {n} de {total} caen a ±{cut} % del modelo; fallan las de {fails} mg de plata, donde las tres series de Godshall difieren mucho entre sí.",
    "cp.v.not": "No es validación de Bugbee ni de Godshall: es una comparación de un modelo de tablas con un artículo de 1896. Las cifras de la pérdida de oro no tienen segunda fuente.",
}
