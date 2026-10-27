"""La carga de CSV y Excel en las tablas editables: la lectura pura (`carga.leer_tabla`), la
plantilla y los rechazos. La subida de punta a punta no se prueba con AppTest (no maneja
`st.file_uploader`): va con Playwright contra un servidor real."""

import io
import re
import sys
import zipfile
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("streamlit")
openpyxl = pytest.importorskip("openpyxl")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

import carga  # noqa: E402
import cian_calculo  # noqa: E402
import cian_tab  # noqa: E402
import qaqc_calculo as qcalc  # noqa: E402
import qaqc_tab  # noqa: E402
import sed_calculo  # noqa: E402
import sed_tab  # noqa: E402
from i18n import TEXTS, use  # noqa: E402

P = qcalc.QaqcParams()
TABLAS = {
    "cian": (cian_tab.COLUMNAS, cian_tab.example_table()),
    "sed": (sed_tab.COLUMNAS, sed_tab.example_table()),
    "crm": (qaqc_tab.COL_RES, pd.DataFrame({"res": qcalc.tabla_crm(P)})),
    "dup": (qaqc_tab.COL_DUP, pd.DataFrame(qcalc.tabla_duplicados(), columns=["a", "b"])),
    "blk": (qaqc_tab.COL_RES, pd.DataFrame({"res": qcalc.tabla_blancos(P)})),
}
BOM = "﻿"


def _csv(columnas, ejemplo, sep, decimal, rotulos="es") -> bytes:
    cab = sep.join(c.rotulo(rotulos) for c in columnas)
    filas = [sep.join(repr(float(x)).replace(".", decimal) for x in f) for f in ejemplo.values]
    return (BOM + "\r\n".join([cab, *filas]) + "\r\n").encode("utf-8")


def _xlsx(filas: list[list]) -> bytes:
    libro = openpyxl.Workbook()
    for fila in filas:
        libro.active.append(fila)
    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()


def _xlsx_de(columnas, ejemplo) -> bytes:
    return _xlsx([[c.rotulo("es") for c in columnas], *ejemplo.values.tolist()])


def _reescribir(base: bytes, hoja_fn) -> bytes:
    """Copia el .xlsx cambiando el XML de la primera hoja con `hoja_fn(bytes) -> bytes`."""
    salida = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(base)) as z, zipfile.ZipFile(salida, "w") as w:
        for item in z.infolist():
            datos = z.read(item)
            if item.filename == "xl/worksheets/sheet1.xml":
                datos = hoja_fn(datos)
            w.writestr(item, datos, zipfile.ZIP_DEFLATED)
    return salida.getvalue()


def _vistas(nombre: str, df: pd.DataFrame):
    """Lo que calcula la pestaña con esta tabla: debe ser idéntico para el ejemplo y lo leído."""
    filas = df.values.tolist()
    if nombre == "cian":
        t, sol, res = cian_calculo.leer_tabla(filas)
        return cian_calculo.run_cian(cian_calculo.CianParams(), t, sol, res).balance
    if nombre == "sed":
        p = sed_calculo.SedParams(fuente=sed_calculo.FUENTES[1])
        v = sed_calculo.run_sed(p, filas)
        return v.tf, v.diametro_m
    own = replace(P, crm_fuente=qcalc.FUENTES[1], blk_fuente=qcalc.FUENTES[1])
    if nombre == "crm":
        return qcalc.run_crm(own, [x[0] for x in filas])
    if nombre == "blk":
        return qcalc.run_blk(own, [x[0] for x in filas])
    return qcalc.run_dup(replace(P, dup_fuente=qcalc.DUP_FUENTES[-1]), filas)


FORMATOS = {
    "csv_punto_y_coma": lambda c, e: ("a.csv", _csv(c, e, ";", ",")),
    "csv_coma": lambda c, e: ("a.CSV", _csv(c, e, ",", ".", "en")),
    "xlsx": lambda c, e: ("a.xlsx", _xlsx_de(c, e)),
}


@pytest.mark.parametrize("formato", FORMATOS)
@pytest.mark.parametrize("tabla", TABLAS)
def test_el_ejemplo_exportado_se_lee_identico(tabla, formato):
    columnas, ejemplo = TABLAS[tabla]
    nombre, contenido = FORMATOS[formato](columnas, ejemplo)
    leido = carga.leer_tabla(nombre, contenido, columnas)
    pd.testing.assert_frame_equal(leido, ejemplo, check_exact=True)
    assert _vistas(tabla, leido) == _vistas(tabla, ejemplo)


@pytest.mark.parametrize("idioma", ["es", "en"])
@pytest.mark.parametrize("tabla", TABLAS)
def test_la_plantilla_descargada_se_lee_identica(tabla, idioma):
    columnas, ejemplo = TABLAS[tabla]
    with use(idioma):
        contenido = carga.plantilla_csv(columnas, ejemplo, idioma)
        leido = carga.leer_tabla("plantilla.csv", contenido, columnas)
    pd.testing.assert_frame_equal(leido, ejemplo, check_exact=True)
    assert contenido.startswith(b"\xef\xbb\xbf")
    primera = contenido.decode("utf-8-sig").splitlines()[0]
    assert primera.split(";" if idioma == "es" else ",")[0] == columnas[0].rotulo(idioma)


def test_acepta_encabezados_en_ingles_o_con_la_clave_y_cualquier_orden():
    columnas = TABLAS["dup"][0]
    df = carga.leer_tabla("x.csv", b"Duplicate;ORIGINAL\n2,5;1,5\n", columnas)
    assert df.to_dict("list") == {"a": [1.5], "b": [2.5]}
    df = carga.leer_tabla("x.csv", b"b,a\n2.5,1.5\n", columnas)
    assert df.to_dict("list") == {"a": [1.5], "b": [2.5]}


def test_latin1_como_respaldo_y_utf8_sin_bom():
    col = (carga.Columna("res", "qc.col.res"),)
    for cod in ("latin-1", "utf-8"):
        df = carga.leer_tabla("x.csv", "Resultado (g/t)\n1,5\n".encode(cod), col)
        assert df["res"].tolist() == [1.5]
    otra = (carga.Columna("a", "qc.col.a"),)
    df = carga.leer_tabla("x.csv", "Original;nota \xf1\n3,5;\xe1\n".encode("latin-1"), otra)
    assert df["a"].tolist() == [3.5]


def test_celdas_vacias_son_nan_y_filas_vacias_se_saltan():
    columnas = TABLAS["dup"][0]
    df = carga.leer_tabla("x.csv", b"Original;Duplicado\n1,5;\n;;\n\n2;3\n", columnas)
    assert df["a"].tolist() == [1.5, 2.0]
    assert pd.isna(df["b"][0]) and df["b"][1] == 3.0


# ------------------------------------------------------------------ rechazos
@pytest.mark.parametrize("nombre", ["a.xls", "a.xlsm", "a.txt", "a", "a.csv.exe", "a.xlsx.xls"])
def test_rechaza_otras_extensiones(nombre):
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla(nombre, b"Resultado (g/t)\n1\n", TABLAS["crm"][0])
    assert e.value.code == "ext"


def test_rechaza_mas_de_1_mb_en_el_codigo():
    grande = b"Resultado (g/t)\n" + b"1\n" * (carga.MAX_BYTES // 2)
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.csv", grande, TABLAS["crm"][0])
    assert e.value.code == "tam"


@pytest.mark.parametrize("formato", ["csv", "xlsx"])
def test_acepta_500_filas_y_rechaza_501(formato):
    col = TABLAS["crm"][0]

    def archivo(n):
        if formato == "csv":
            return "a.csv", ("Resultado (g/t)\n" + "1,5\n" * n).encode()
        return "a.xlsx", _xlsx([["Resultado (g/t)"], *[[1.5]] * n])

    assert len(carga.leer_tabla(*archivo(500), col)) == 500
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla(*archivo(501), col)
    assert e.value.code == "filas"


def test_rechaza_columnas_faltantes_y_dice_cuales():
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.csv", b"Original;Otra\n1;2\n", TABLAS["dup"][0])
    assert e.value.code == "cols"
    assert e.value.args_["faltan"] == "Duplicado"


@pytest.mark.parametrize(
    "contenido", [b"", b"\n\n", b"Original;Duplicado\n", b"Original;Duplicado\n;\n"]
)
def test_rechaza_archivos_sin_datos(contenido):
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.csv", contenido, TABLAS["dup"][0])
    assert e.value.code == "vacio"


@pytest.mark.parametrize("malo", ["abc", "1,2,3", "nan", "inf", "1e999", "1_0", "0x10", "1 2.5.1"])
def test_celda_no_numerica_indica_fila_y_columna(malo):
    csv = f"Original;Duplicado\n1;2\n3;4\n5;{malo}\n".encode()
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.csv", csv, TABLAS["dup"][0])
    assert (e.value.code, e.value.args_) == ("num", {"fila": 4, "col": "Duplicado"})
    with use("es"):
        assert "fila 4" in e.value.texto() and "Duplicado" in e.value.texto()
    with use("en"):
        assert "Row 4" in e.value.texto()


def test_celda_no_numerica_en_xlsx():
    contenido = _xlsx([["Original", "Duplicado"], [1, 2], ["x", 4]])
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.xlsx", contenido, TABLAS["dup"][0])
    assert e.value.args_ == {"fila": 3, "col": "Original"}
    contenido = _xlsx([["Original", "Duplicado"], [1, 2], [1, True]])
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.xlsx", contenido, TABLAS["dup"][0])
    assert e.value.args_ == {"fila": 3, "col": "Duplicado"}


def test_el_mensaje_no_cita_texto_del_archivo():
    malo = "<script>alert(1)</script>"
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.csv", f"Original;Duplicado\n{malo};1\n".encode(), TABLAS["dup"][0])
    assert "script" not in e.value.texto()
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.csv", f"{malo};otra\n1;2\n".encode(), TABLAS["dup"][0])
    assert "script" not in e.value.texto()


@pytest.mark.parametrize(
    ("nombre", "contenido"),
    [
        ("a.xlsx", b"esto no es un zip"),
        ("a.xlsx", b"PK\x03\x04roto"),
        ("a.csv", b"Resultado (g/t)\x00\x01\n1\n"),
    ],
)
def test_archivo_ilegible(nombre, contenido):
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla(nombre, contenido, TABLAS["crm"][0])
    assert e.value.code == "ilegible"


def test_xlsx_descomprimido_enorme_se_rechaza():
    base = _xlsx([["Resultado (g/t)"], [1]])
    salida = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(base)) as z, zipfile.ZipFile(salida, "w") as w:
        for item in z.infolist():
            w.writestr(item, z.read(item))
        w.writestr("relleno.bin", b"\0" * (carga.MAX_DESCOMPRIMIDO + 1), zipfile.ZIP_DEFLATED)
    assert len(salida.getvalue()) < carga.MAX_BYTES
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.xlsx", salida.getvalue(), TABLAS["crm"][0])
    assert e.value.code == "ilegible"


def test_xlsx_con_cien_mil_filas_vacias_y_dimension_enorme_no_cuelga():
    def enorme(datos: bytes) -> bytes:
        nuevo = re.sub(rb'<dimension ref="[^"]*"\s*/>', b'<dimension ref="A1:A1048576"/>', datos)
        assert nuevo != datos
        filas = "".join(f'<row r="{n}"/>' for n in range(3, 100_000))
        return nuevo.replace(b"</sheetData>", filas.encode() + b"</sheetData>")

    contenido = _reescribir(_xlsx([["Resultado (g/t)"], [1]]), enorme)
    assert len(contenido) < carga.MAX_BYTES
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.xlsx", contenido, TABLAS["crm"][0])
    assert e.value.code == "filas"


def test_defusedxml_esta_activo_en_openpyxl():
    from openpyxl.xml import DEFUSEDXML

    assert DEFUSEDXML is True


def test_xlsx_con_entidades_xml_se_bloquea():
    bomba = b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;&a;">]>'

    def con_entidades(datos: bytes) -> bytes:
        return bomba + re.sub(rb"^<\?xml[^>]*\?>", b"", datos)

    contenido = _reescribir(_xlsx([["Resultado (g/t)"], [1]]), con_entidades)
    with pytest.raises(carga.CargaError) as e:
        carga.leer_tabla("a.xlsx", contenido, TABLAS["crm"][0])
    assert e.value.code == "ilegible"


def test_xlsx_con_formula_devuelve_el_valor_guardado():
    def con_valor(datos: bytes) -> bytes:
        assert b"<f>20+22</f>" in datos
        nuevo = re.sub(
            rb"<f>20\+22</f>\s*<v\s*/>|<f>20\+22</f>\s*<v></v>", b"<f>20+22</f><v>7.5</v>", datos
        )
        assert b"<v>7.5</v>" in nuevo
        return nuevo

    contenido = _reescribir(_xlsx([["Resultado (g/t)"], ["=20+22"], [3]]), con_valor)
    df = carga.leer_tabla("a.xlsx", contenido, TABLAS["crm"][0])
    assert df["res"].tolist() == [7.5, 3.0]  # el guardado (7,5), no el recalculado (42)


def test_los_textos_existen_en_los_dos_idiomas():
    llaves = {k for k in TEXTS["es"] if k.startswith("ld.")}
    assert llaves == {k for k in TEXTS["en"] if k.startswith("ld.")}
    for cod in ("ext", "tam", "filas", "vacio", "ilegible", "cols", "num"):
        assert f"ld.err.{cod}" in llaves
