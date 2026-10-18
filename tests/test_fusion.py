"""Fusión, fase 2 (carga fundente): poderes reductores, neutralización de bases, diseño y
evaluación de la carga, avisos y validación contra Bugbee (1922) y USGS Bulletin 1445.

Cortes fijados antes de correr (ver el docstring de muestreo/fusion_datos.py): cifras de Bugbee
iguales al redondeo publicado; lo que no llega se marca «a una unidad» o «no» y se fija aquí tal
cual (no se oculta ni se marca xfail)."""

import math

import pytest

from muestreo import fusion as fu
from muestreo import fusion_datos as fd
from muestreo import fusion_pesos as fp
from muestreo.fusion_avisos import BUTTON_RANGE
from muestreo.quimica import PB, M, molar_mass

AT = fu.AT_G
P = fu.FusionParams
BASE = {"cuarzo": 80, "calcita": 8, "hematita": 3, "pirita": 3, "calcopirita": 1}


def _texts(result):
    return [w.text for w in result.warnings]


# ------------------------------------------------------------------ química y poderes teóricos
def test_masas_molares():
    assert molar_mass("SiO2") == pytest.approx(60.083, abs=0.01)
    assert molar_mass("Na2B4O7") == pytest.approx(201.22, abs=0.05)
    assert molar_mass("FeS2") == pytest.approx(119.98, abs=0.02)
    with pytest.raises(fu.FusionError):
        molar_mass("Xx2")
    with pytest.raises(fu.FusionError):
        molar_mass("fe")


def test_poderes_reductores_teoricos_de_bugbee_exactos_al_redondeo():
    assert 2 * PB / molar_mass("C") == pytest.approx(34.5, abs=0.05)  # 2PbO + C
    assert 2 * PB / molar_mass("S") == pytest.approx(12.9, abs=0.05)  # S a SO2
    assert 3 * PB / molar_mass("S") == pytest.approx(19.4, abs=0.05)  # S a SO3
    assert fu.reducing_power("pirita", "SO2") == pytest.approx(8.6, abs=0.05)
    assert fu.reducing_power("galena", "SO2") == pytest.approx(2.6, abs=0.05)
    assert fu.reducing_power("galena", "SO3") == pytest.approx(3.46, abs=0.005)
    assert fu.reducing_power("calcocita", "SO2") == pytest.approx(3.9, abs=0.05)
    assert fu.reducing_power("calcocita", "SO3") == pytest.approx(5.2, abs=0.05)
    assert fu.reducing_power("arsenopirita", "SO2") == pytest.approx(5.7, abs=0.05)
    assert fu.reducing_power("estibina", "SO2") == pytest.approx(5.5, abs=0.05)
    assert fu.reducing_power("calcopirita", "SO2") == pytest.approx(6.2, abs=0.05)
    assert fu.reducing_power("esfalerita", "SO3") == pytest.approx(8.5, abs=0.05)
    assert fu.reducing_power("pirrotita", "SO3") == pytest.approx(9.9, abs=0.05)
    assert 10 * PB / (4 * M["KNO3"]) == pytest.approx(5.12, abs=0.005)  # nitro


def test_los_electrones_dan_los_atomos_de_plomo_de_las_reacciones_de_bugbee():
    assert fu.pb_reduced_per_mol(2, -1, 0, "SO2") == 5  # FeS2 + 5PbO + SiO2
    assert fu.pb_reduced_per_mol(2, -1, 0, "SO3") == 7  # 2FeS2 + 14PbO + 4Na2CO3 + SiO2
    assert fu.pb_reduced_per_mol(1, 0, 0, "SO2") == 2  # 2PbO + S
    assert fu.pb_reduced_per_mol(1, 0, 0, "SO3") == 3  # 3PbO + S + Na2CO3
    assert fu.pb_reduced_per_mol(0, 0, -2, "SO3") == -1  # Fe2O3 + Pb = 2FeO + PbO
    with pytest.raises(fu.FusionError):
        fu.pb_reduced_per_mol(1, 0, 0, "SO4")


def test_la_tabla_xx_se_reproduce_con_los_veredictos_documentados():
    fits = {c.item: c.fit for c in fd.theoretical_checks() if c.source.endswith("Tabla XX")}
    assert len(fits) == 16
    assert sum(f == "cuadra" for f in fits.values()) == 10  # 10 de 16 con pesos actuales
    assert sorted(i for i, f in fits.items() if f == "cuadra con los pesos de Bugbee") == [
        "Calcopirita: S a SO3", "Esfalerita: S a SO2", "Pirita: S a SO3", "Pirrotita: S a SO2",
    ]  # fmt: skip
    assert sorted(i for i, f in fits.items() if f == "no cuadra") == [
        "Arsenopirita: S a SO3",
        "Estibina: S a SO3",
    ]


def test_lo_que_no_cuadra_en_la_tabla_xx_es_pequeno_y_viene_del_libro():
    worst = max(abs(c.difference) for c in fd.theoretical_checks() if c.source.endswith("XX"))
    assert worst < 0.04  # los 5 «no» se alejan de 0,01 a 0,04 de su propia estequiometría


def test_el_poder_oxidante_de_la_hematita_es_negativo_y_cuarzo_y_calcita_no_reducen():
    assert fu.reducing_power("hematita") == pytest.approx(-1.2975, abs=1e-3)
    assert fu.reducing_power("cuarzo") == 0 == fu.reducing_power("calcita")
    with pytest.raises(fu.FusionError):
        fu.reducing_power("oro")


# ------------------------------------------------------------------ neutralización
def test_neutralizacion_de_bases_de_bugbee():
    assert fu.silica_per_base("FeO") == pytest.approx(0.84, abs=0.005)
    assert fu.silica_per_base("CaCO3") == pytest.approx(0.60, abs=0.005)
    assert fu.borax_per_base("FeO") == pytest.approx(1.4, abs=0.05)
    assert fu.borax_per_base("CaCO3") == pytest.approx(1.0, abs=0.05)
    assert AT / fu.silica_per_base("PbO") == pytest.approx(108, abs=0.5)  # Tabla XXI


def test_el_grado_de_silicato_escala_la_sílice_que_neutraliza_una_base():
    mono, sesqui, bi = (fu.silica_per_base("CaCO3", d) for d in (1.0, 1.5, 2.0))
    assert sesqui == pytest.approx(0.75 * bi) and mono == pytest.approx(0.5 * bi)
    # Bugbee: sesqui-silicato = tres cuartos de la sílice (un tercio más de base)


@pytest.mark.parametrize(
    "degree, name",
    [(0.5, "sub"), (1.0, "mono"), (1.6, "sesqui"), (2.0, "bi"), (2.9, "tri"), (3.4, "tri")],
)
def test_clasificacion_de_silicatos(degree, name):
    assert fu.classify(degree) == name


# ------------------------------------------------------------------ diseño de la carga
@pytest.mark.parametrize(
    "minerals",
    [
        BASE,
        {"cuarzo": 100},
        {"calcita": 100},
        {"cuarzo": 50, "pirita": 25, "hematita": 10},
        {"cuarzo": 20, "calcopirita": 30, "calcita": 20},
        {"cuarzo": 60, "esfalerita": 15, "galena": 5},
    ],
)
@pytest.mark.parametrize("degree", [1.0, 1.5, 2.0])
def test_la_carga_calculada_da_el_boton_y_el_grado_pedidos(minerals, degree):
    params = P(AT, minerals, degree=degree)
    result = fu.evaluate_charge(params, fu.design_charge(params))
    assert result.button_g == pytest.approx(28.0, abs=1e-9)
    assert result.slag.degree == pytest.approx(degree, rel=1e-9)
    assert result.slag.label == {1.0: "mono", 1.5: "sesqui", 2.0: "bi"}[degree]


def test_la_muestra_que_reduce_poco_pide_harina_y_la_que_reduce_de_mas_pide_nitro():
    light = fu.design_charge(P(AT, BASE))
    assert light.flour_g > 0 == light.niter_g
    heavy = fu.design_charge(P(AT, {"cuarzo": 50, "pirita": 30, "calcopirita": 10}))
    assert heavy.niter_g > 0 == heavy.flour_g
    params = P(AT, {"cuarzo": 50, "pirita": 30, "calcopirita": 10})
    result = fu.evaluate_charge(params, heavy)
    assert result.ore_pb_g + result.niter_pb_g == pytest.approx(28.0)  # el nitro baja el botón


def test_harina_y_nitro_salen_del_balance_de_plomo():
    params = P(AT, BASE, flour_rp=12.0)
    ore = sum(AT * v / 100 * fu.reducing_power(k, "SO3") for k, v in BASE.items())
    assert fu.design_charge(params).flour_g == pytest.approx((28.0 - ore) / 12.0)
    assert fu.design_charge(P(AT, {"cuarzo": 100}, flour_rp=12.0)).flour_g == pytest.approx(28 / 12)
    heavy = P(AT, {"pirita": 50, "cuarzo": 50}, niter_op=4.2)
    ore = AT * 0.5 * fu.reducing_power("pirita", "SO3")
    assert fu.design_charge(heavy).niter_g == pytest.approx((ore - 28.0) / 4.2)


def test_la_hematita_oxida_y_pide_mas_harina():
    plain = fu.design_charge(P(AT, {"cuarzo": 90}))
    rusty = fu.design_charge(P(AT, {"cuarzo": 80, "hematita": 10}))
    assert rusty.flour_g > plain.flour_g
    extra = AT * 0.10 * 1.2975 / 11.0
    assert rusty.flour_g - plain.flour_g == pytest.approx(extra, rel=1e-3)


def test_litargirio_para_el_boton_mas_el_de_la_escoria():
    params = P(AT, {"calcita": 100}, lodge_excess=0.2)
    reagents = fu.design_charge(params)
    button_pbo = 28.0 * M["PbO"] / PB
    assert reagents.litharge_g == pytest.approx(button_pbo + 1.4 * AT)
    galena = P(AT, {"cuarzo": 30, "calcita": 50, "galena": 10})
    lead_in_ore = AT * 0.10 * PB / molar_mass("PbS")
    pbo = fu.design_charge(galena).litharge_g
    assert pbo == pytest.approx((28.0 - lead_in_ore) * M["PbO"] / PB + 1.4 * AT, rel=1e-9)


def test_lodge_pide_quince_a_veinticinco_por_ciento_mas_litargirio_con_sulfuros():
    params = P(AT, {"cuarzo": 40, "pirita": 40}, litharge_slag_per_g=0.0, lodge_excess=0.25)
    reagents = fu.design_charge(params)
    assert reagents.litharge_g == pytest.approx(28.0 * M["PbO"] / PB * 1.25)


def test_el_azufre_oxidado_a_so3_gasta_soda_y_a_so2_no():
    params = P(AT, {"cuarzo": 80, "pirita": 10}, sulfur="SO3")
    so3 = fu.design_charge(params)
    so2 = fu.design_charge(P(AT, {"cuarzo": 80, "pirita": 10}, sulfur="SO2"))
    s_mol = AT * 0.10 * 2 / molar_mass("FeS2")
    assert so3.soda_g - so2.soda_g == pytest.approx(s_mol * M["Na2CO3"], rel=0.02)
    result = fu.evaluate_charge(params, so3)
    assert result.slag.components_g["Na2SO4"] == pytest.approx(s_mol * M["Na2SO4"])
    assert result.sulfur_mol == pytest.approx(s_mol)


def test_el_borax_tiene_minimo_y_reemplaza_un_tercio_de_la_silice():
    reagents = fu.design_charge(P(AT, {"calcita": 100}))
    silica_total = reagents.silica_g + reagents.borax_g * fu.BORAX_SILICA_EQUIVALENT
    assert reagents.borax_g * fu.BORAX_SILICA_EQUIVALENT / silica_total == pytest.approx(1 / 3)
    assert fu.design_charge(P(AT, {"cuarzo": 100})).borax_g == 5.0  # el mínimo de Bugbee


def test_una_muestra_muy_silicea_sube_soda_y_litargirio_en_tres_a_dos():
    params = P(AT, {"cuarzo": 100}, soda_per_g=0, litharge_slag_per_g=0, borax_min_g=0,
               borax_fraction=0)  # fmt: skip
    reagents = fu.design_charge(params)
    soda_mol = reagents.soda_g / M["Na2CO3"]
    pbo_mol = (reagents.litharge_g - 28.0 * M["PbO"] / PB) / M["PbO"]
    assert soda_mol / (soda_mol + pbo_mol) == pytest.approx(0.6)
    assert reagents.silica_g == 0.0


# ------------------------------------------------------------------ evaluar una carga
def test_el_boton_es_el_efecto_de_la_muestra_mas_la_harina_menos_el_nitro():
    params = P(AT, BASE, flour_rp=11.0, niter_op=4.1)
    reagents = fu.Reagents(40.0, 80.0, 5.0, 5.0, 2.0, 1.5)
    result = fu.evaluate_charge(params, reagents)
    ore = sum(AT * v / 100 * fu.reducing_power(k, "SO3") for k, v in BASE.items())
    assert result.ore_pb_g == pytest.approx(ore)
    assert result.flour_pb_g == pytest.approx(22.0) and result.niter_pb_g == pytest.approx(-6.15)
    assert result.button_g == pytest.approx(ore + 22.0 - 6.15)


def test_el_boton_no_puede_pasar_del_plomo_que_da_el_litargirio():
    params = P(AT, {"cuarzo": 100}, flour_rp=12.0)
    reagents = fu.Reagents(30.0, 20.0, 5.0, 0.0, 5.0, 0.0)  # 60 g de Pb pedidos, 20 g de PbO
    result = fu.evaluate_charge(params, reagents)
    assert result.button_g == pytest.approx(20.0 * PB / M["PbO"])
    assert any("mata" in t for t in _texts(result))


def test_sin_reductor_no_hay_boton():
    result = fu.evaluate_charge(P(AT, {"cuarzo": 100}), fu.Reagents(30.0, 60.0, 5.0, 5.0, 0.0, 0.0))
    assert result.button_g == 0.0
    assert any("menor de 25" in t for t in _texts(result))


def test_el_volumen_del_boton_es_masa_sobre_11_34_y_el_de_la_escoria_sobre_su_densidad():
    result = fu.design_and_evaluate(P(AT, BASE))
    assert result.button_cm3 == pytest.approx(28.0 / 11.34)
    assert fu.PB_DENSITY == 11.34
    assert result.slag_cm3 == pytest.approx(result.slag.mass_g / fu.SLAG_DENSITY)
    assert fu.SLAG_DENSITY == 3.0 and fu.FUSION_TEMP_C == 1050.0


def test_composicion_de_la_escoria_cierra_con_los_reactivos_y_el_mineral():
    params = P(AT, BASE)
    reagents = fu.design_charge(params)
    result = fu.evaluate_charge(params, reagents)
    comps = result.slag.components_g
    assert sum(comps.values()) == pytest.approx(result.slag.mass_g)
    assert comps["Na2B4O7"] == reagents.borax_g
    assert comps["SiO2"] == pytest.approx(reagents.silica_g + AT * 0.80)
    assert comps["CaO"] == pytest.approx(AT * 0.08 / molar_mass("CaCO3") * M["CaO"])
    # el litargirio que queda libre es el cargado menos el que se redujo a plomo
    assert comps["PbO"] == pytest.approx(reagents.litharge_g - 28.0 * M["PbO"] / PB)
    assert result.gas_mol["CO2"] > 0 and result.gas_mol["SO2"] == 0.0


def test_con_so2_el_azufre_sale_como_gas():
    params = P(AT, {"cuarzo": 80, "pirita": 10}, sulfur="SO2")
    result = fu.design_and_evaluate(params)
    assert result.gas_mol["SO2"] == pytest.approx(AT * 0.10 * 2 / molar_mass("FeS2"))
    assert "Na2SO4" not in result.slag.components_g


# ------------------------------------------------------------------ avisos
def test_boton_chico_y_boton_grande_avisan_con_su_cita():
    params = P(AT, BASE)
    reagents = fu.design_charge(params)
    small = fu.evaluate_charge(params, reagents.scaled(flour=0.5))
    big = fu.evaluate_charge(params, reagents.scaled(flour=2.0))
    lo, hi = BUTTON_RANGE
    assert (lo, hi) == (25.0, 30.0)
    assert small.button_g < lo and any("menor de 25" in t for t in _texts(small))
    assert big.button_g > hi and any("escorificarlo" in t for t in _texts(big))
    assert all(w.source for w in small.warnings + big.warnings)
    assert not fu.design_and_evaluate(params).warnings or all(
        "mata" not in t and "botón" not in t.lower() for t in _texts(fu.design_and_evaluate(params))
    )


def test_escoria_demasiado_acida_o_demasiado_basica():
    params = P(AT, BASE)
    reagents = fu.design_charge(params)
    acid = fu.evaluate_charge(params, reagents.scaled(silica=40.0))
    basic = fu.evaluate_charge(params, reagents.scaled(silica=0.0))
    assert acid.slag.degree > 3.0 and any("tri-silicato" in t for t in _texts(acid))
    assert basic.slag.degree < 2.0
    sub = fu.evaluate_charge(P(AT, {"calcita": 100}), fu.Reagents(60.0, 70.0, 5.0, 0.0, 2.3, 0.0))
    assert sub.slag.degree < 1.0 and any("ataca el crisol" in t for t in _texts(sub))


def test_riesgo_de_mata_con_mucho_azufre_y_escoria_acida():
    params = P(AT, {"cuarzo": 40, "pirita": 60})
    result = fu.design_and_evaluate(params)
    texts = _texts(result)
    assert result.ore_pb_g > 28.0
    assert any("mono-silicato" in t and "riesgo de mata" in t for t in texts)
    assert any("25 % de azufre" in t for t in texts)
    mono = fu.design_and_evaluate(P(AT, {"cuarzo": 40, "pirita": 60}, degree=1.0))
    assert not any("mono-silicato" in t for t in _texts(mono))


def test_poco_litargirio_con_sulfuros_avisa_el_exceso_de_lodge():
    params = P(AT, {"cuarzo": 60, "pirita": 20})
    reagents = fu.design_charge(params)
    short = fu.evaluate_charge(params, reagents.scaled(litharge=0.45))
    assert any("15 al 25" in t or "reductor pide más" in t for t in _texts(short))


def test_cobre_alto_pide_mas_fundente_y_mas_litargirio_libre():
    two = fu.design_and_evaluate(P(AT, {"cuarzo": 90, "calcopirita": 6}))  # 2,1 % de Cu
    assert 2.0 <= two.copper_pct < 5.0 and any("Cu de 2 a 5" in w.source for w in two.warnings)
    high = P(AT, {"cuarzo": 50, "calcopirita": 30})  # 10 % de Cu
    reagents = fu.design_charge(high)
    result = fu.evaluate_charge(high, reagents.scaled(litharge=0.55))
    assert result.copper_pct == pytest.approx(30 * 63.546 / molar_mass("CuFeS2"), rel=1e-9)
    assert any("Perkins" in t for t in _texts(result))
    assert any("umbral supuesto" in w.source for w in result.warnings)


def test_fundente_activo_menor_de_dos_y_medio_veces_la_muestra():
    params = P(AT, {"cuarzo": 100})
    reagents = fu.Reagents(10.0, 40.0, 0.0, 0.0, 28 / 11, 0.0)
    result = fu.evaluate_charge(params, reagents)
    assert any("2,5" in w.source or "2.5" in w.text for w in result.warnings)


# ------------------------------------------------------------------ datos inválidos
@pytest.mark.parametrize(
    "bad",
    [
        dict(minerals={"cuarzo": 90, "pirita": 20}),
        dict(minerals={"cuarzo": -5}),
        dict(minerals={"oro": 10}),
        dict(minerals={"cuarzo": float("nan")}),
        dict(sample_g=0.0),
        dict(button_g=-1.0),
        dict(degree=0.0),
        dict(flour_rp=0.0),
        dict(niter_op=-1.0),
        dict(sulfur="SO4"),
    ],
)
def test_datos_invalidos_fallan_con_mensaje(bad):
    args = dict(sample_g=AT, minerals=BASE)
    args.update(bad)
    with pytest.raises(fu.FusionError):
        fu.design_charge(P(**args))


def test_el_nitro_del_usgs_10_7_g():
    assert fu.niter_for_button(15 * 5.00, 30.0, 4.2) == pytest.approx(10.7, abs=0.05)
    assert fu.niter_for_button(10.0, 28.0, 4.2) == 0.0
    with pytest.raises(fu.FusionError):
        fu.niter_for_button(50.0, 28.0, 0.0)


# ------------------------------------------------------------------ validación (datos publicados)
def test_neutralizaciones_de_bugbee_exactas_al_redondeo():
    checks = {c.item: c for c in fd.neutralization_checks()}
    for item in ("1 g de FeO neutraliza (g de SiO2, bi-silicato)",
                 "1 g de FeO requiere (g de bórax vidrio)",
                 "1 g de CaCO3 neutraliza (g de SiO2)",
                 "1 g de CaCO3 requiere (g de bórax vidrio)",
                 "Tabla XXI, 1 A.T. de SiO2: PbO (bi-silicato)",
                 "Tabla XXI, 10 g de SiO2: Na2CO3 (bi-silicato)",
                 "Tabla XXII, sílice que piden 10 g de PbO",
                 "Tabla XXII, sílice que piden 1 A.T. de MgCO3"):  # fmt: skip
        assert checks[item].ok, item


def test_el_17_4_de_la_tabla_xxii_no_cuadra_con_su_propio_0_60():
    check = next(
        c for c in fd.neutralization_checks() if "1 A.T. de CaCO3" in c.item and "XXII" in c.item
    )
    assert not check.ok and check.calculated == pytest.approx(17.51, abs=0.01)
    assert 0.60 * AT == pytest.approx(17.50, abs=0.01)  # su 0,60 g por g da 17,5, no 17,4
    assert "redondeo" in check.note


def test_el_ejemplo_de_50_por_ciento_con_los_factores_de_la_tabla_es_exacto():
    t = fd.bugbee_table_example()
    assert round(t["CaCO3"], 1) == 8.7 and t["soda"] == 17.0 and round(t["litharge"], 1) == 8.1
    assert round(t["total"], 1) == 33.8 and round(t["ore_silica"], 1) == 14.6
    assert round(t["needed"], 1) == 19.2 and round(t["silica"], 1) == 12.8
    assert round(t["remainder"], 1) == 6.4 and round(t["borax"], 1) == 10.7
    exact = [
        c for c in fd.example_checks() if c.item.startswith("50 % CaCO3:") and "carga" not in c.item
    ]
    assert len(exact) == 9 and all(c.ok for c in exact)


def test_la_calculadora_reproduce_las_cargas_de_los_ejemplos_a_una_unidad():
    checks = {c.item: c for c in fd.example_checks() if "carga calculada" in c.item}
    assert len(checks) == 6
    for c in checks.values():
        assert abs(c.difference) < 0.2, c.item  # con estequiometría actual, no con su tabla
        assert abs(c.difference_bugbee) < 0.2, c.item  # ni con sus pesos
    assert checks["50 % CaCO3: carga calculada, bórax vidrio"].ok
    assert checks["50 % CaCO3: carga calculada, sílice"].ok
    assert checks["50 % CaCO3: carga calculada, litargirio"].ok


def test_sílice_pura_soda_y_litargirio_de_un_assay_ton():
    checks = {c.item: c for c in fd.example_checks() if "sílice pura" in c.item}
    soda = checks["1 A.T. de sílice pura: soda (3/5 de la sílice)"]
    lith = checks["1 A.T. de sílice pura: litargirio para la escoria"]
    assert soda.calculated == pytest.approx(30.7, abs=0.2)
    assert lith.calculated == pytest.approx(43.2, abs=0.2)
    assert checks["1 A.T. de sílice pura: harina (R.P. 12)"].ok  # 2⅓ g


def test_la_mezcla_3_5_0_5_6_da_bisilicato_con_100_g_y_sesquisilicato_con_125_g():
    checks = fd.mixture_checks()
    assert all(c.ok for c in checks)
    deg100, deg125 = (fd.mixture_example(f).slag.degree for f in (100.0, 125.0))
    assert abs(deg100 - 2.0) <= 0.35 and abs(deg125 - 1.5) <= 0.35
    assert deg125 < deg100  # 125 g es menos ácida
    assert fd.mixture_example(100.0).button_g == pytest.approx(28.0)
    assert math.isclose(fd.mixture_example(125.0).slag.degree, 1.785, abs_tol=0.01)


def test_resumen_de_la_validacion_de_bugbee_y_usgs():
    checks = fd.all_checks()
    assert fd.summary(checks) == {
        "total": 67, "cuadra": 43, "cuadra con los pesos de Bugbee": 14,
        "truncamiento de Bugbee": 3, "no cuadra": 7,
    }  # fmt: skip
    assert fd.usgs_niter_example().ok


def test_poderes_medidos_de_bugbee_se_muestran_con_su_diferencia_y_no_son_corte():
    rows = {r[0]: r for r in fd.measured_rows()}
    assert len(rows) == 8 and rows["Calcocita"][3] is None
    assert rows["Galena"][3] == 3.41 and rows["Pirita"][3] == 11.05
    assert rows["Pirita"][4] == pytest.approx(11.05 - rows["Pirita"][2])
    assert rows["Arsenopirita"][4] == pytest.approx(8.18 - fu.reducing_power("arsenopirita", "SO3"))
    assert fd.ARGOLS == {"sub": 11.04, "mono": 10.93, "bi": 10.62, "tri": 9.26}


def test_cargas_del_usgs_evaluadas_con_la_calculadora_solo_informativo():
    rows = {r["carga"]: r for r in fd.usgs_load_rows()}
    assert len(rows) == 3
    quartz = rows["Cuarzo (15 g)"]
    assert quartz["botón (g)"] == pytest.approx(3.0 * 10.5)  # harina de R.P. medio del USGS
    assert quartz["grado"] > rows["Calcita (15 g)"]["grado"]  # el cuarzo es más ácido
    mixed = rows["Mitad calcita, mitad cuarzo (15 g)"]
    assert quartz["grado"] > mixed["grado"] > rows["Calcita (15 g)"]["grado"]


def test_el_umbral_de_perkins_es_137_partes_de_pbo_por_parte_de_cobre():
    params = P(AT, {"cuarzo": 60, "calcopirita": 16})  # 5,5 % de Cu
    reagents = fu.design_charge(params)
    cu_g = AT * 0.16 * 63.546 / molar_mass("CuFeS2")
    short = fu.evaluate_charge(
        params, reagents.scaled(litharge=3.0)
    )  # PbO libre entre 100 y 137 × Cu
    assert 100 * cu_g < short.slag.components_g["PbO"] < 137 * cu_g
    assert any("Perkins" in t for t in _texts(short))
    plenty = fu.evaluate_charge(params, reagents.scaled(litharge=4.0))  # sobre 137 × Cu: sin aviso
    assert plenty.slag.components_g["PbO"] > 137 * cu_g
    assert not any("Perkins" in t for t in _texts(plenty))


# ------------------------------------------------------------------ pesos de Bugbee
def test_los_pesos_de_bugbee_estan_declarados_y_son_enteros_o_de_uso_comun():
    w = fp.BUGBEE_WEIGHTS
    assert (w["Pb"], w["Fe"], w["S"], w["C"], w["O"]) == (207.1, 56.0, 32.06, 12.0, 16.0)
    assert w["Si"] == 28.3 and w["Cu"] == 64.0 and set(w) == set(fp.ATOMIC_WEIGHTS)
    assert fp.BUGBEE_WEIGHTS != fp.ATOMIC_WEIGHTS  # la app usa SIEMPRE los actuales
    assert "infiere" in fp.__doc__.lower()


def test_con_207_56_y_32_el_hierro_da_3_696_y_la_pirita_12_075_que_bugbee_trunca():
    assert 207 / 56 == pytest.approx(3.696, abs=0.001)  # Bugbee imprime 3,70
    assert 14 * 207 / (2 * 120) == pytest.approx(12.075)  # imprime 12,07: truncó
    assert fp.truncated_equals(12.075, "12.07") and not fp.truncated_equals(12.075, "12.08")
    assert fp.matches_rounding(3.696, "3.70")


def test_el_motor_con_pesos_actuales_es_el_mismo_calculo_que_la_app():
    cur = fp.CURRENT
    for key in ("pirita", "calcopirita", "galena", "hematita", "arsenopirita", "estibina"):
        spec = {m.key: m for m in (*fu.MINERALS, *fu.EXTRA_MINERALS)}[key]
        for mode in ("SO2", "SO3"):
            assert cur.rp(spec, mode) == pytest.approx(fu.reducing_power(key, mode), rel=1e-12)
    for base in ("FeO", "CaCO3", "PbO", "Na2CO3", "NaHCO3"):
        assert cur.silica_per_base(base) == pytest.approx(fu.silica_per_base(base), rel=1e-12)
        assert cur.borax_per_base(base) == pytest.approx(fu.borax_per_base(base), rel=1e-12)
    soda = cur.design({"cuarzo": 100}, 0, 0, pure_split=True)
    pure = fu.design_charge(P(AT, {"cuarzo": 100}, soda_per_g=0, litharge_slag_per_g=0,
                              borax_min_g=0, borax_fraction=0, flour_rp=12.0))  # fmt: skip
    assert soda["soda"] == pytest.approx(pure.soda_g, rel=1e-9)
    assert soda["litharge slag"] == pytest.approx(pure.litharge_g - 28 * M["PbO"] / PB, rel=1e-9)
    for minerals in ({"cuarzo": 50, "calcita": 50}, {"calcita": 100}):
        mixed = cur.design(minerals, 30.0, 30.0)
        charge = fu.design_charge(P(AT, minerals, soda_per_g=30 / AT, litharge_slag_per_g=30 / AT,
                                    flour_rp=12.0))  # fmt: skip
        assert mixed["borax"] == pytest.approx(charge.borax_g, rel=1e-9)
        assert mixed["silica"] == pytest.approx(charge.silica_g, rel=1e-9)
        assert mixed["litharge"] == pytest.approx(charge.litharge_g, rel=1e-9)


def test_el_veredicto_distingue_las_cuatro_categorias():
    assert fp.verdict("3.70", 3.701, 3.5) == fp.CUADRA
    assert fp.verdict("3.70", 3.71, 3.698) == fp.CON_PESOS
    assert fp.verdict("51.2", 51.45, 51.271) == fp.TRUNCA  # 51,271 truncado da 51,2
    assert fp.verdict("51.2", 51.45, 51.31) == fp.NO_CUADRA  # truncado da 51,3
    assert fp.verdict("6.96", 6.999, 6.985) == fp.NO_CUADRA
    assert fp.verdict("1.0", 2.0, None) == fp.NO_CUADRA
    assert fp.truncated_equals(51.271, "51.2") and not fp.truncated_equals(51.31, "51.2")


def test_conteo_exacto_por_categoria_de_las_cifras_que_dependen_de_pesos():
    weighted = [c for c in fd.all_checks() if c.bugbee is not None]
    assert len(weighted) == 55  # 67 menos las 12 que no dependen de pesos atómicos
    counts = {v: sum(c.fit == v for c in weighted) for v in fp.VERDICTS}
    assert counts == {fp.CUADRA: 31, fp.CON_PESOS: 14, fp.TRUNCA: 3, fp.NO_CUADRA: 7}
    # con los pesos de Bugbee quedan a media unidad: las que cuadran con ellos y no con los actuales
    assert sum(c.fit == fp.CON_PESOS for c in weighted) == 14
    assert 55 - counts[fp.NO_CUADRA] == 48  # 48 de 55 se explican con la aritmética de Bugbee


def test_lo_que_queda_como_no_cuadra_va_con_su_diferencia_sin_maquillar():
    bad = {c.item: c for c in fd.all_checks() if c.fit == fp.NO_CUADRA}
    assert set(bad) == {
        "Arsenopirita: S a SO3", "Estibina: S a SO3", "Fe2O3 (Fe2O3 + Pb)",
        "Tabla XXII, sílice que piden 1 A.T. de FeO",
        "Tabla XXII, sílice que piden 1 A.T. de CaCO3",
        "CaCO3 puro: carga calculada, bórax vidrio", "CaCO3 puro: carga calculada, sílice",
    }  # fmt: skip
    assert bad["Estibina: S a SO3"].difference_bugbee == pytest.approx(7.3837 - 7.35, abs=1e-3)
    assert abs(bad["Tabla XXII, sílice que piden 1 A.T. de CaCO3"].difference_bugbee) > 0.1
    assert all(abs(c.difference_bugbee) > 0.01 for c in bad.values())


def test_las_cifras_sin_pesos_no_tienen_columna_de_bugbee():
    plain = [c for c in fd.all_checks() if c.bugbee is None]
    assert len(plain) == 12 and all(c.fit in (fp.CUADRA, fp.NO_CUADRA) for c in plain)
