"""Textos en español de la carga de CSV y Excel en las tablas editables (claves `ld.*`)."""

T = {
    "ld.label": "Cargar un archivo (CSV o Excel .xlsx)",
    "ld.formato": "Columnas: {cols}. Hasta {max} filas y 1 MB. CSV con «;» y coma decimal, o con «,» y punto decimal; en Excel se lee la primera hoja, con los encabezados en la primera fila. Lo cargado queda en la tabla de abajo y se puede seguir editando.",
    "ld.aviso": 'Lo que subes viaja a los servidores de Streamlit y no se guarda; para datos de una empresa, usa la app en local: `pip install -e ".[dev,app]"` y `streamlit run app/streamlit_app.py`.',
    "ld.plantilla": "Descargar plantilla (CSV)",
    "ld.ok": "Archivo cargado: {n} filas.",
    "ld.err.ext": "Solo se cargan archivos .csv y .xlsx (no .xls ni .xlsm): guarda el Excel como «Libro de Excel (.xlsx)» o como CSV.",
    "ld.err.tam": "El archivo pesa más de 1 MB.",
    "ld.err.filas": "El archivo tiene más de {max} filas de datos.",
    "ld.err.vacio": "El archivo no tiene filas de datos.",
    "ld.err.ilegible": "No se pudo leer el archivo: no parece un CSV ni un .xlsx válido.",
    "ld.err.cols": "Faltan columnas en el encabezado (primera fila): {faltan}.",
    "ld.err.num": "La fila {fila}, columna «{col}», no es un número (con «;» el decimal es coma; con «,», punto).",
}
