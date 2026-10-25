"""Copelación y partición: las tablas publicadas, transcritas CIFRA POR CIFRA y verificadas contra
la imagen del escaneo (no contra el texto OCR). Sin cálculo: solo datos y su cita.

Fuente principal: Bugbee (1922), *A Textbook of Fire Assaying*, Wiley, dominio público; la página
es la IMPRESA (la del escaneo `bugbee1922.pdf` es la impresa + 16).

- Tabla IX, p. 100: efecto de la temperatura en la pérdida de plata (Lodge, *Assaying*).
- Tabla X, p. 102: efecto del plomo en la pérdida de plata (Lodge).
- Tabla XI, p. 102: efecto de la plata presente (Godshall, Trans. AIME 26:473-484, 1896). Es la fila
  de ½ A.T. de plomo de la SEGUNDA serie del artículo original; en 50 mg Bugbee imprime 2,65 y el
  artículo original, 2,67 (aquí se guarda lo de Bugbee y la diferencia se declara en la validación).
- Tabla XII, p. 102: efecto de la temperatura en la pérdida de oro (Lodge).
- p. 103: Smith, oro recuperado con y sin plata (sin cuadro numerado).
- p. 118, 121 y 122: relación plata:oro para partir y encuarte (Rose, *Metallurgy of Gold*).

Segunda fuente (solo para VALIDAR, nunca para ajustar): Godshall (1896), «Silver-Losses in
Cupellation», Trans. AIME 26:473-484, p. 483, «Summary of Average Results» (archive.org,
`in.ernet.dli.2015.168586`, escaneo de la p. impresa 483, página 537 del PDF). Es el artículo
original; Bugbee reproduce solo una fila. Godshall NO midió la temperatura en grados (la describe
como «lo más uniforme posible», bajada a «calor bajo» al descubrirse el botón).

Lo que NO está en tablas (y por eso no se transcribe ni se digitaliza): la curva minuto a minuto
de la Fig. 40 (30 g de plomo, 100 mg de plata) y el efecto de la plata sobre el oro de la Fig. 41
(10 mg de oro, 25 g de plomo, cuatro temperaturas).
"""

from __future__ import annotations

PAGINA_ESCANEO = {"IX": 116, "X": 118, "XI": 118, "XII": 118, "smith": 119, "rose": 137,
                  "parting": 134, "godshall": 537}  # fmt: skip
PAGINA_IMPRESA = {"IX": 100, "X": 102, "XI": 102, "XII": 102, "smith": 103, "rose": 121,
                  "parting": 118, "godshall": 483}  # fmt: skip

# ------------------------------------------------------------------ Tabla IX (p. 100)
# (plata mg, plomo g, temperatura °C, pérdida de plata %); «promedio». Observación de Bugbee:
# cristales de PbO en todo el botón (700), en el lado frío de la copela (775) y ninguno (≥ 850).
TABLA_IX: tuple[tuple[float, float, float, float], ...] = (
    (200.0, 10.0, 700.0, 1.02),
    (200.0, 10.0, 775.0, 1.30),
    (200.0, 10.0, 850.0, 1.73),
    (200.0, 10.0, 925.0, 3.65),
    (200.0, 10.0, 1000.0, 4.88),
)
CRISTALES_HASTA_C = 775.0  # con cristales de PbO en la copela (observación de la Tabla IX)

# ------------------------------------------------------------------ Tabla X (p. 102)
# (plata mg, plomo g, temperatura °C, pérdida de plata %); «promedio de los dos más cercanos».
TABLA_X: tuple[tuple[float, float, float, float], ...] = (
    (200.0, 10.0, 685.0, 1.39),
    (200.0, 15.0, 685.0, 1.38),
    (200.0, 20.0, 685.0, 1.52),
    (200.0, 25.0, 685.0, 1.85),
)

# ------------------------------------------------------------------ Tabla XI (p. 102)
# (plata mg, pérdida de plata %) con ½ A.T. de plomo (Godshall, 1896)
A_T_G = 29.1667  # g por «assay ton» (29,1667 g): lo usa Godshall para pesar el plomo
PLOMO_TABLA_XI_G = A_T_G / 2.0
TABLA_XI: tuple[tuple[float, float], ...] = (
    (200.0, 1.73), (100.0, 2.03), (50.0, 2.65), (20.0, 2.82), (10.0, 3.44), (5.0, 4.46),
    (2.0, 6.90),
)  # fmt: skip

# ------------------------------------------------------------------ Tabla XII (p. 102)
# (oro mg, plomo g, temperatura °C, pérdida de oro %); «media de los dos resultados más cercanos».
# A 700 °C «el botón se congeló»: no hay copelación y no hay cifra.
TABLA_XII: tuple[tuple[float, float, float, float | None], ...] = (
    (200.0, 10.0, 700.0, None),
    (200.0, 10.0, 775.0, 0.155),
    (200.0, 10.0, 850.0, 0.385),
    (200.0, 10.0, 925.0, 0.460),
    (200.0, 10.0, 1000.0, 1.435),
    (200.0, 10.0, 1075.0, 2.990),
)
CONGELADO_C = 700.0

# ------------------------------------------------------------------ Smith, p. 103
# porcentaje del oro total recuperado: (sin plata, con plata) con telurio y sin telurio
SMITH_CON_TELURIO = (94.9, 97.0)
SMITH_SIN_TELURIO = (98.2, 99.5)

# ------------------------------------------------------------------ partición y encuarte
MINIMO_PARTIR = 3.0  # p. 118: «al menos tres veces más plata que oro»
RECOMENDADO_MIN, RECOMENDADO_MAX = 8.0, 10.0  # p. 118: «ocho o diez veces» para perlas de mena
LINGOTE_RAZON = (2.0, 2.5)  # p. 121: en lingote de oro, 2 o 2,5 a 1 (lámina laminada)
MAX_ORO_FRACCION = 0.25  # p. 122: «la razón máxima de 25 % de oro» (3 a 1)
# Rose (Metallurgy of Gold, 6.ª ed., p. 511), p. 121: (oro mg, razón Ag:Au). «Menos de 0,1 mg» da
# «20 o 30 a 1» (el punto de 0,1 mg usa el promedio, 25: SUPUESTO declarado) y «más de 50 mg», 2,5.
ROSE: tuple[tuple[float, float], ...] = (
    (0.1, 25.0), (0.2, 10.0), (1.0, 6.0), (10.0, 4.0), (50.0, 2.5),
)  # fmt: skip
ROSE_BAJO = (20.0, 30.0)

# ------------------------------------------------------------------ Godshall (1896), p. 483
# «Summary of Average Results», en %. Plomo en A.T.: ¼, ½, ¾ y 1. Cada fila es la plata en mg
# (2, 5, 10, 20, 50, 100, 200) y sus cuatro promedios de plomo; el quinto («Av.») se calcula.
GODSHALL_PLATA_MG = (2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)
GODSHALL_PLOMO_AT = (0.25, 0.5, 0.75, 1.0)
GODSHALL_PRIMERA = (
    (6.42, 4.54, 7.08, 7.93), (3.60, 3.16, 5.07, 3.46), (3.86, 4.09, 6.22, 5.73),
    (4.27, 5.52, 4.45, 4.95), (2.22, 3.42, 2.89, 3.54), (1.83, 2.10, 2.46, 2.81),
    (1.32, 1.68, 2.03, 2.11),
)  # fmt: skip
GODSHALL_SEGUNDA = (
    (3.73, 6.90, 8.43, 9.39), (3.72, 4.46, 4.68, 7.29), (3.01, 3.44, 5.37, 5.44),
    (1.86, 2.82, 4.41, 4.51), (2.00, 2.67, 3.02, 3.27), (1.87, 2.03, 2.40, 2.64),
    (1.46, 1.73, 1.85, 2.24),
)  # fmt: skip
GODSHALL_TERCERA = (
    (4.05, 4.33, 4.51, 6.49), (3.52, 3.15, 4.25, 4.84), (4.01, 3.19, 3.87, 4.15),
    (3.26, 2.80, 2.88, 3.33), (2.44, 2.71, 3.17, 3.50), (2.17, 2.35, 2.69, 2.95),
    (1.76, 1.91, 1.87, 1.96),
)  # fmt: skip
GODSHALL_FINAL = (
    (4.68, 4.93, 6.46, 7.60), (3.60, 3.53, 4.69, 5.30), (3.62, 3.57, 5.15, 5.11),
    (3.23, 3.54, 3.93, 4.24), (2.27, 2.68, 3.02, 3.37), (1.96, 2.16, 2.52, 2.80),
    (1.51, 1.77, 1.92, 2.10),
)  # fmt: skip
GODSHALL_SERIES = {"primera": GODSHALL_PRIMERA, "segunda": GODSHALL_SEGUNDA,
                   "tercera": GODSHALL_TERCERA, "final": GODSHALL_FINAL}  # fmt: skip
