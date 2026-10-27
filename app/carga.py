"""Carga de CSV y Excel (.xlsx) en las tablas editables.

`leer_tabla` es una función pura: recibe el nombre y los bytes del archivo, y devuelve un
DataFrame de floats con las columnas de la tabla, o lanza `CargaError` con la clave del texto del
problema. `panel` dibuja el cargador y el botón de la plantilla y devuelve el DataFrame que se le
pasa a `st.data_editor`: lo cargado, o el ejemplo si no se cargó nada.

Lo que se sube nunca se guarda en disco ni se dibuja como HTML: solo se leen números, y los
mensajes de error citan los rótulos de las columnas de la app, jamás texto del archivo.
Excel: se lee el valor guardado de cada celda (no se evalúan fórmulas) con openpyxl en modo de solo
lectura, y `defusedxml` instalado para que el XML del archivo no pueda expandir entidades.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

import pandas as pd
import streamlit as st
from i18n import TEXTS, current, int_num, t

MAX_BYTES = 1024 * 1024  # 1 MB, el mismo tope que `server.maxUploadSize`
MAX_FILAS = 500  # filas de datos de una tabla cargada
MAX_ESCANEO = 5000  # filas leídas en total (con las vacías): una hoja casi vacía no cuelga la app
MAX_DESCOMPRIMIDO = 20 * 1024 * 1024  # lo que puede ocupar un .xlsx ya descomprimido
MAX_COLUMNAS = 50  # celdas por fila que se miran; el resto se ignora
EXTENSIONES = ("csv", "xlsx")
SUFIJO_ESTADO = "__carga"
SUFIJO_SUBIDA = "__subir"
_NUMERO = re.compile(r"[+-]?(\d+([.,]\d*)?|[.,]\d+)([eE][+-]?\d+)?")


@dataclass(frozen=True)
class Columna:
    """Una columna de una tabla editable: su clave interna y la clave del texto de su rótulo."""

    clave: str
    texto: str

    def rotulo(self, idioma: str | None = None) -> str:
        if idioma is None:
            return t(self.texto)
        return TEXTS[idioma][self.texto]


class CargaError(Exception):
    """Un archivo que no se puede cargar. `code` elige el texto `ld.err.<code>`."""

    def __init__(self, code: str, **args: object) -> None:
        super().__init__(code)
        self.code = code
        self.args_ = args

    def texto(self) -> str:
        return t(f"ld.err.{self.code}", **self.args_)


# ------------------------------------------------------------------ lectura
def _normal(x: object) -> str:
    return " ".join(str(x).split()).casefold()


def _vacia(x: object) -> bool:
    return x is None or (isinstance(x, str) and not x.strip())


def _numero(x: object) -> float:
    """El valor de una celda: NaN si está vacía; `ValueError` si no es un número finito."""
    if _vacia(x):
        return float("nan")
    if isinstance(x, bool):
        raise ValueError(x)
    if isinstance(x, int | float):
        valor = float(x)
    elif isinstance(x, str):
        texto = x.replace(" ", "").strip()
        if not _NUMERO.fullmatch(texto):
            raise ValueError(texto)
        valor = float(texto.replace(",", "."))
    else:
        raise ValueError(x)
    if valor != valor or valor in (float("inf"), float("-inf")):
        raise ValueError(x)
    return valor


def _tabla(filas: Iterable[tuple[int, list]], columnas: tuple[Columna, ...]) -> pd.DataFrame:
    """Arma el DataFrame desde (número de fila, celdas): la primera fila con algo es el
    encabezado; las filas totalmente vacías se saltan."""
    it = iter(filas)
    encabezado = next((celdas for _, celdas in it if not all(_vacia(c) for c in celdas)), None)
    if encabezado is None:
        raise CargaError("vacio")
    nombres = [_normal(c) for c in encabezado]
    posicion: dict[str, int] = {}
    faltan = []
    for col in columnas:
        validos = {_normal(col.clave), _normal(col.rotulo("es")), _normal(col.rotulo("en"))}
        idx = next((i for i, n in enumerate(nombres) if n in validos), None)
        if idx is None:
            faltan.append(col.rotulo())
        else:
            posicion[col.clave] = idx
    if faltan:
        raise CargaError("cols", faltan=", ".join(faltan))
    datos: dict[str, list[float]] = {col.clave: [] for col in columnas}
    for n, celdas in it:
        if all(_vacia(c) for c in celdas):
            continue
        if len(datos[columnas[0].clave]) >= MAX_FILAS:
            raise CargaError("filas", max=MAX_FILAS)
        for col in columnas:
            i = posicion[col.clave]
            try:
                valor = _numero(celdas[i] if i < len(celdas) else None)
            except ValueError:
                raise CargaError("num", fila=n, col=col.rotulo()) from None
            datos[col.clave].append(valor)
    if not datos[columnas[0].clave]:
        raise CargaError("vacio")
    return pd.DataFrame(datos, dtype="float64")


def _decodificar(contenido: bytes) -> str:
    try:
        return contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        return contenido.decode("latin-1")


def _filas_csv(contenido: bytes) -> Iterator[tuple[int, list]]:
    texto = _decodificar(contenido)
    if "\x00" in texto:
        raise CargaError("ilegible")
    primera = next((ln for ln in texto.splitlines() if ln.strip()), "")
    # Con «;» el decimal es coma (Excel en español); con «,» solo como separador, punto decimal.
    # Si el encabezado no tiene ninguno (tabla de una columna) cada línea es una sola celda.
    sep = "," if "," in primera and ";" not in primera else ";"
    try:
        for n, fila in enumerate(csv.reader(io.StringIO(texto), delimiter=sep), start=1):
            if n > MAX_ESCANEO:
                raise CargaError("filas", max=MAX_FILAS)
            yield n, fila[:MAX_COLUMNAS]
    except csv.Error:
        raise CargaError("ilegible") from None


def _filas_xlsx(contenido: bytes) -> Iterator[tuple[int, list]]:
    import openpyxl  # tarda en importar: solo si se sube un Excel

    try:
        with zipfile.ZipFile(io.BytesIO(contenido)) as z:
            if sum(i.file_size for i in z.infolist()) > MAX_DESCOMPRIMIDO:
                raise CargaError("ilegible")
        libro = openpyxl.load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
    except CargaError:
        raise
    except Exception:  # archivo ajeno: zip roto, XML malformado o bloqueado por defusedxml
        raise CargaError("ilegible") from None
    try:
        if not libro.worksheets:
            raise CargaError("ilegible")
        hoja = libro.worksheets[0]
        for n, fila in enumerate(hoja.iter_rows(values_only=True), start=1):
            if n > MAX_ESCANEO:
                raise CargaError("filas", max=MAX_FILAS)
            yield n, list(fila[:MAX_COLUMNAS])
    except CargaError:
        raise
    except Exception:
        raise CargaError("ilegible") from None
    finally:
        libro.close()


def leer_tabla(nombre: str, contenido: bytes, columnas: tuple[Columna, ...]) -> pd.DataFrame:
    """Lee un CSV o un .xlsx a un DataFrame de floats con una columna por cada `Columna` (por su
    clave interna). Acepta los encabezados en español, en inglés o con la clave. Lanza
    `CargaError` si la extensión, el tamaño, las filas, las columnas o las celdas no sirven. Las
    celdas vacías quedan como NaN: las valida cada pestaña con sus reglas."""
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if ext not in EXTENSIONES:
        raise CargaError("ext")
    if len(contenido) > MAX_BYTES:
        raise CargaError("tam")
    filas = _filas_csv(contenido) if ext == "csv" else _filas_xlsx(contenido)
    return _tabla(filas, columnas)


# ------------------------------------------------------------------ plantilla
def plantilla_csv(columnas: tuple[Columna, ...], ejemplo: pd.DataFrame, idioma: str) -> bytes:
    """El ejemplo como CSV listo para Excel: en español `;` con coma decimal, en inglés `,` con
    punto; UTF-8 con BOM para que Excel respete los acentos. Los números van completos."""
    es = idioma == "es"
    salida = io.StringIO()
    w = csv.writer(salida, delimiter=";" if es else ",", lineterminator="\r\n")
    w.writerow([c.rotulo(idioma) for c in columnas])
    for fila in ejemplo[[c.clave for c in columnas]].itertuples(index=False):
        celdas = ["" if pd.isna(x) else repr(float(x)) for x in fila]
        w.writerow([c.replace(".", ",") for c in celdas] if es else celdas)
    return salida.getvalue().encode("utf-8-sig")


# ------------------------------------------------------------------ interfaz
def reiniciar(key: str) -> None:
    """Vuelve la tabla `key` al ejemplo: borra lo cargado, lo editado y el archivo del cargador."""
    st.session_state.pop(key, None)
    st.session_state.pop(key + SUFIJO_ESTADO, None)
    st.session_state[key + SUFIJO_SUBIDA] = st.session_state.get(key + SUFIJO_SUBIDA, 0) + 1


def panel(
    key: str, columnas: tuple[Columna, ...], ejemplo: pd.DataFrame, archivo: str
) -> pd.DataFrame:
    """Dibuja el cargador y la plantilla de la tabla `key` y devuelve lo que va al editor."""
    estado = st.session_state.setdefault(key + SUFIJO_ESTADO, {"id": None, "df": None, "err": None})
    st.caption(
        t(
            "ld.formato",
            cols=", ".join(f"«{c.rotulo()}»" for c in columnas),
            max=int_num(MAX_FILAS),
        )
    )
    st.caption(t("ld.aviso"))
    # Sin `type=`: el filtro de Streamlit rechaza un .xls en el navegador con un mensaje en inglés
    # que no se puede traducir. La extensión se valida en `leer_tabla`, con mensaje es/en.
    subido = st.file_uploader(
        t("ld.label"),
        key=f"{key}{SUFIJO_SUBIDA}{st.session_state.get(key + SUFIJO_SUBIDA, 0)}",
    )
    if subido is not None and subido.file_id != estado["id"]:
        estado["id"] = subido.file_id
        try:
            estado["df"] = leer_tabla(subido.name, subido.getvalue(), columnas)
            estado["err"] = None
            st.session_state.pop(key, None)  # lo editado era sobre otros datos
        except CargaError as exc:
            estado["err"] = exc
    if subido is not None and estado["err"] is not None:
        st.error(estado["err"].texto())
    elif subido is not None and estado["df"] is not None:
        st.success(t("ld.ok", n=int_num(len(estado["df"]))))
    st.download_button(
        t("ld.plantilla"),
        data=plantilla_csv(columnas, ejemplo, current()),
        file_name=archivo,
        mime="text/csv",
        key=key + "__plantilla",
        on_click="ignore",
    )
    return ejemplo if estado["df"] is None else estado["df"]
