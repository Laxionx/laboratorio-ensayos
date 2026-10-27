"""English texts of the CSV and Excel upload into the editable tables (keys `ld.*`)."""

T = {
    "ld.label": "Upload a file (CSV or Excel .xlsx)",
    "ld.formato": 'Columns: {cols}. Up to {max} rows and 1 MB. CSV with ";" and decimal comma, or with "," and decimal point; in Excel the first sheet is read, with the headers in the first row. What you upload goes into the table below and can still be edited.',
    "ld.aviso": 'What you upload travels to the Streamlit servers and is not stored; for company data, run the app locally: `pip install -e ".[dev,app]"` and `streamlit run app/streamlit_app.py`.',
    "ld.plantilla": "Download template (CSV)",
    "ld.ok": "File loaded: {n} rows.",
    "ld.err.ext": 'Only .csv and .xlsx files are loaded (not .xls or .xlsm): save the Excel file as "Excel Workbook (.xlsx)" or as CSV.',
    "ld.err.tam": "The file is larger than 1 MB.",
    "ld.err.filas": "The file has more than {max} data rows.",
    "ld.err.vacio": "The file has no data rows.",
    "ld.err.ilegible": "The file could not be read: it does not look like a valid CSV or .xlsx.",
    "ld.err.cols": "Columns missing from the header (first row): {faltan}.",
    "ld.err.num": 'Row {fila}, column "{col}", is not a number (with ";" the decimal is a comma; with ",", a point).',
}
