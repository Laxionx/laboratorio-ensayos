"""Ensayo de sedimentación: las cifras publicadas y los cortes de validación, fijados ANTES de
correr.

- Coe y Clevenger (1916), ejemplo del tercer ensayo de Nipissing (página impresa 372): con F = 4,
  D = 1,12 y R = 0,893 pies/h, A = 4,31 pies² por tonelada corta por día; para 100 t/d, 431 pies²
  y un tanque de 23,4 pies. Cortes: al redondeo publicado. La tabla de los cinco ensayos se
  lista aparte (sin corte previo): 3 de sus 5 áreas no salen con D = 1,12.
- Torquato, Luz y coautores (2011), REM 64(1):91-96: Tabla 1 (31 espesadores): el diámetro
  publicado sale de (área unitaria, t/h por espesador) al metro, y el área unitaria sale de
  (π D²/4)/(t/h · 24) a 3 decimales. Tabla 2: 706,86 m² y 51,4 t/h dan 0,573. Tabla 3: el diámetro
  de cada ensayo sale de (área unitaria, 157 t/h) al metro. Factor: 0,573/0,898 = 0,64 (el texto
  lo escribe dividido al revés: 0,898 / 0,573 = 1,57).
- Kynch sintético: una curva de probeta EXACTA de v(C) = v0 (1 − C/Cmax)^n (por el método de las
  características, sin compresión) debe devolver v(C) por tangentes a ±2 % en C de C0 a 0,8 Cmax.
- Talmage-Fitch frente a Yoshioka sobre esa curva: informativo, sin corte.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import sedimentacion as sd

# ------------------------------------------------------------------ Coe y Clevenger (1916)
CC_F, CC_D, CC_R = 4.0, 1.12, 0.893
CC_AREA_PUB, CC_PIES2_PUB, CC_DIAM_PUB, CC_TON_DIA = 4.31, 431.0, 23.4, 100.0
# los cinco ensayos de Nipissing: (partes de fluido, pies/h, área publicada), p. 372
CC_ENSAYOS = (
    (6.00, 2.180, 3.00), (4.94, 1.190, 4.29), (4.00, 0.893, 4.31),
    (3.51, 0.758, 4.22), (3.00, 0.600, 4.05),
)  # fmt: skip

# ------------------------------------------------------------------ Vale: Tabla 1
# (mina, qtd, aplicación, t/h por espesador, d50 mm, cma %, cmu %, área unitaria, diámetro m)
VALE_T1: tuple[tuple, ...] = (
    ("Cauê", 2, "lama", 143, 0.0061, 3.5, 40, 1.220, 73),
    ("Cauê", 2, "pellet feed", 55, 0.0550, 15, 60, 0.535, 30),
    ("Conceição", 1, "lama", 190, 0.0064, 4.2, 35, 1.722, 100),
    ("Conceição", 2, "pellet feed", 600, 0.0520, 45, 65, 0.049, 30),
    ("Água Limpa", 1, "lama", 42, 0.0048, 2.3, 25, 0.344, 21),
    ("Brucutu", 1, "lama", 250, 0.0043, 0.93, 25, 1.309, 100),
    ("Brucutu", 2, "pellet feed", 1100, 0.0670, 47, 65, 0.034, 34),
    ("Gongo Soco", 1, "lama", 100, 0.0067, 6, 40, 0.131, 20),
    ("Gongo Soco", 1, "pellet feed", 120, 0.0610, 47, 65, 0.027, 10),
    ("Alegria", 1, "alim. flotación", 500, 0.0440, 52, 60, 0.008, 11),
    ("Alegria", 2, "pellet feed", 370, 0.0490, 43, 65, 0.011, 11),
    ("Alegria", 1, "lama", 59, 0.0045, 3.2, 35, 0.987, 42),
    ("Alegria", 1, "lama", 57, 0.0048, 3.2, 35, 0.521, 30),
    ("Fábrica Nova", 1, "lama", 220, 0.0056, 5.1, 45, 0.553, 61),
    ("Fábrica Nova", 1, "pellet feed", 800, 0.0450, 48, 65, 0.037, 30),
    ("Timbopeba", 1, "pellet feed", 520, 0.0510, 45, 65, 0.016, 16),
    ("Fábrica", 2, "lama", 180, 0.0039, 4.5, 48, 0.654, 60),
    ("Fábrica", 1, "pellet feed", 560, 0.0390, 40, 70, 0.053, 30),
    ("Pico ITMA, B y D", 1, "lama", 230, 0.0044, 3, 30, 0.288, 45),
    ("Pico ITMA y B", 1, "pellet feed", 192, 0.0460, 50, 70, 0.029, 13),
    ("Pico ITMD", 1, "pellet feed", 350, 0.0460, 50, 70, 0.115, 35),
    ("Pico ITMI", 1, "lama", 180, 0.0051, 3.9, 40, 0.455, 50),
    ("Pico ITMI", 1, "pellet feed", 670, 0.0460, 38.8, 70, 0.060, 35),
    ("Mutuca", 1, "lama", 340, 0.0047, None, 55, 0.060, 25),
    ("Vargem Grande", 1, "alim. flotación", 550, 0.0430, 66, 60, 0.029, 22),
    ("Vargem Grande", 1, "lama", 450, 0.0067, 2.5, 55, 0.147, 45),
    ("Vargem Grande", 1, "pellet feed", 410, 0.0480, 42, 70, 0.039, 22),
    ("Carajás", 2, "lama", 750, 0.0010, 18, 50, 0.279, 80),
    ("Carajás", 1, "lama", 450, 0.0010, 18, 50, 0.182, 50),
    ("Carajás", 1, "lama", 75, 0.0010, 18, 40, 0.504, 34),
    ("Carajás", 2, "pellet feed", 295, 0.0348, 3, 60, 0.075, 26),
)  # fmt: skip
VALE_T2_AREA, VALE_T2_D, VALE_T2_TPH, VALE_T2_AU = 706.86, 30.0, 51.4, 0.573
# Tabla 3: (ensayo, floculante g/t, % sólidos inicial y final, vel. m/h, área unitaria, t/h, Ø m)
VALE_T3: tuple[tuple, ...] = (
    (1, None, 3.53, 44.02, 1.34, 1.040, 157, 71), (2, 20, 3.60, 42.00, 1.77, 0.901, 157, 66),
    (3, 20, 4.16, 42.97, 1.63, 0.898, 157, 66), (4, 28, 3.43, 40.54, 1.98, 0.765, 157, 61),
    (5, 40, 4.03, 38.03, 2.23, 0.654, 157, 56), (6, None, 3.87, 43.80, 1.22, 0.968, 157, 68),
    (7, 27, 3.11, 41.70, 1.68, 0.880, 157, 65),
)  # fmt: skip
VALE_T3_MEDIA_AU, VALE_T3_MEDIA_D, VALE_T3_ENSAYO = 0.872, 65, 3
VALE_FACTOR = 0.64

# ------------------------------------------------------------------ Kynch sintético
SINT_V0, SINT_CMAX, SINT_N, SINT_C0, SINT_H0, SINT_CU = 8.0, 0.60, 4.0, 0.30, 0.40, 0.45
SINT_T_MAX_S = 3 * 3600.0
SINT_RANGO = 0.8  # el rango analizado es C de C0 a 0,8 Cmax
SINT_CORTE = 0.02


@dataclass(frozen=True)
class SedCheck:
    source: str  # cc, v1, v2, v3, kn
    kind: str
    label: str
    published: float
    calculated: float
    ok: bool
    note: str = ""
    decimals: int = 3


def cc_area() -> float:
    return sd.coe_clevenger_pies2_ton_dia(CC_F, CC_D, CC_R)


def coe_checks() -> list[SedCheck]:
    a = cc_area()
    pies2 = a * CC_TON_DIA
    diam = sd.diametro_pies(pies2)
    out = [
        SedCheck("cc", "area", "A", CC_AREA_PUB, a, round(a, 2) == CC_AREA_PUB, "", 2),
        SedCheck(
            "cc", "pies2", "100 t/d", CC_PIES2_PUB, pies2, round(pies2) == CC_PIES2_PUB, "", 1
        ),
        SedCheck("cc", "diam", "100 t/d", CC_DIAM_PUB, diam, round(diam, 1) == CC_DIAM_PUB, "", 2),
    ]
    for i, (f, r, pub) in enumerate(CC_ENSAYOS, start=1):
        calc = sd.coe_clevenger_pies2_ton_dia(f, CC_D, r)
        out.append(SedCheck("cc", "ensayo", str(i), pub, calc, round(calc, 2) == pub,
                            "cc_d" if round(calc, 2) != pub else "", 2))  # fmt: skip
    return out


def vale_t1_checks() -> list[SedCheck]:
    out = []
    for i, (_mina, _q, _app, tph, _d50, _cma, _cmu, au, diam) in enumerate(VALE_T1, start=1):
        calc_au = sd.area_unitaria_m2_t_dia(diam, tph)
        calc_d = sd.diametro_desde_area_unitaria(au, tph)
        out.append(SedCheck("v1", "diametro", f"{i}", diam, calc_d, round(calc_d) == diam, "", 2))
        ok = round(calc_au, 3) == au
        out.append(SedCheck("v1", "area", f"{i}", au, calc_au, ok, "" if ok else "v1_au", 4))
    return out


def vale_t2_checks() -> list[SedCheck]:
    area = sd.area_circulo_m2(VALE_T2_D)
    au = sd.area_unitaria_m2_t_dia(VALE_T2_D, VALE_T2_TPH)
    return [
        SedCheck("v2", "area", "30 m", VALE_T2_AREA, area, round(area, 2) == VALE_T2_AREA, "", 3),
        SedCheck("v2", "au", "51,4 t/h", VALE_T2_AU, au, round(au, 3) == VALE_T2_AU, "", 4),
    ]


def factor_vale() -> float:
    """El factor 0,64: área unitaria industrial (0,573) entre la de probeta (0,898)."""
    au3 = next(r[5] for r in VALE_T3 if r[0] == VALE_T3_ENSAYO)
    return sd.area_unitaria_m2_t_dia(VALE_T2_D, VALE_T2_TPH) / au3


def vale_t3_checks() -> list[SedCheck]:
    out = []
    for ens, _f, _c0, _cu, _v, au, tph, diam in VALE_T3:
        calc = sd.diametro_desde_area_unitaria(au, tph)
        out.append(SedCheck("v3", "diametro", str(ens), diam, calc, round(calc) == diam, "", 2))
    media = float(np.mean([r[5] for r in VALE_T3]))
    d_media = sd.diametro_desde_area_unitaria(media, 157)
    out.append(SedCheck("v3", "media_au", "7", VALE_T3_MEDIA_AU, media,
                        round(media, 3) == VALE_T3_MEDIA_AU, "", 4))  # fmt: skip
    out.append(SedCheck("v3", "media_d", "7", VALE_T3_MEDIA_D, d_media,
                        round(d_media) == VALE_T3_MEDIA_D, "", 2))  # fmt: skip
    f = factor_vale()
    out.append(SedCheck("v3", "factor", "0,573 / 0,898", VALE_FACTOR, f,
                        round(f, 2) == VALE_FACTOR, "v3_factor", 3))  # fmt: skip
    return out


# ------------------------------------------------------------------ Kynch sintético
def curva_sintetica() -> sd.CurvaSed:
    return sd.sintetica_kynch(SINT_V0, SINT_CMAX, SINT_N, SINT_C0, SINT_H0, SINT_T_MAX_S)


def kynch_error() -> tuple[float, int, float, float]:
    """(error relativo máximo de v(C), puntos analizados, C mínima, C máxima) en el rango
    declarado, con la curva sintética exacta."""
    k = sd.kynch(curva_sintetica(), SINT_C0)
    c = np.asarray(k.c_t_m3)
    v = np.asarray(k.v_m_h)
    sel = (c >= SINT_C0 * 0.999999) & (c <= SINT_RANGO * SINT_CMAX)
    vt = np.array([sd.v_richardson_zaki(x, SINT_V0, SINT_CMAX, SINT_N) for x in c[sel]])
    return (
        float(np.max(np.abs(v[sel] / vt - 1.0))),
        int(sel.sum()),
        float(c[sel].min()),
        float(c[sel].max()),
    )


def kynch_checks() -> list[SedCheck]:
    err, n, *_ = kynch_error()
    return [SedCheck("kn", "error_v", f"{n}", SINT_CORTE * 100.0, err * 100.0,
                     err <= SINT_CORTE, "", 6)]  # fmt: skip


def yoshioka_exacto_m2_t_dia() -> float:
    """El área del flujo límite de la MISMA función de flujo conocida (sin pasar por la curva)."""
    cs = np.linspace(SINT_C0, SINT_CU * (1 - 1e-6), 20001)
    g = cs * np.array([sd.v_richardson_zaki(x, SINT_V0, SINT_CMAX, SINT_N) for x in cs])
    return sd.area_flujo_limite_m2_t_dia(float(np.min(g / (1 - cs / SINT_CU))))


def talmage_vs_yoshioka() -> dict[str, float]:
    """Informativo: el área de Talmage-Fitch con la tangente en distintos puntos de la curva
    sintética frente al flujo límite exacto. Sin compresión, tu = t + (h − Hu)/v es máximo justo
    cuando la interfase llega a Hu: con la tangente ahí coincide con Yoshioka, y en cualquier
    punto anterior sale MENOR (no conservador). Con compresión real (underflow más denso que lo
    que sedimenta en zona) la tangente de Talmage-Fitch cae más tarde y el área es mayor."""
    curva = curva_sintetica()
    y = yoshioka_exacto_m2_t_dia()
    k = sd.kynch(curva, SINT_C0)
    gl, c_crit = sd.flujo_limite(k.c_t_m3, k.g_t_m2_h, SINT_CU)
    hu = SINT_C0 * SINT_H0 / SINT_CU
    t_hu = float(np.interp(-hu, -np.asarray(curva.h_m), curva.t_s))  # h decrece: t en que h = Hu
    out = {"yoshioka": y, "yoshioka_kynch": sd.area_flujo_limite_m2_t_dia(gl), "c_critica": c_crit,
           "t_hu_s": t_hu}  # fmt: skip
    for frac in (0.5, 0.9, 0.999):
        tf = sd.talmage_fitch(curva, SINT_C0, SINT_CU, t_hu * frac)
        out[f"tf_{frac:g}"] = tf.area_unitaria_m2_t_dia
        out[f"dif_{frac:g}"] = 100.0 * (tf.area_unitaria_m2_t_dia / y - 1.0)
    return out


def all_checks() -> list[SedCheck]:
    return [*coe_checks(), *vale_t1_checks(), *vale_t2_checks(), *vale_t3_checks(), *kynch_checks()]


def summary(checks: list[SedCheck] | None = None) -> dict[str, tuple[int, int]]:
    checks = checks or all_checks()
    out = {}
    for src in ("cc", "v1", "v2", "v3", "kn"):
        rows = [x for x in checks if x.source == src]
        out[src] = (sum(x.ok for x in rows), len(rows))
    return out


def factor_inverso() -> float:
    """Lo que el texto del artículo escribe (bancada / industrial): 0,898 / 0,573."""
    return 1.0 / factor_vale()
