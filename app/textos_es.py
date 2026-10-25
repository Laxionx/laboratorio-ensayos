"""Todos los textos de la app en el idioma «es»: junta los de cada área y no deja que dos áreas
usen la misma clave."""

from __future__ import annotations

from textos_es_cian import T as CIAN
from textos_es_cop import T as COP
from textos_es_datos import T as DATOS
from textos_es_fusion import T as FUSION
from textos_es_guia import T as GUIA
from textos_es_qaqc import T as QAQC
from textos_es_qaqc_val import T as QAQC_VAL
from textos_es_sed import T as SED
from textos_es_ui import T as UI

TEXTS: dict[str, str] = {}
for _part in (UI, GUIA, DATOS, FUSION, CIAN, SED, COP, QAQC, QAQC_VAL):
    _repeated = TEXTS.keys() & _part.keys()
    if _repeated:
        raise ValueError(f"claves repetidas en textos_es: {sorted(_repeated)}")
    TEXTS.update(_part)
