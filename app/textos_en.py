"""Todos los textos de la app en el idioma «en»: junta los de cada área y no deja que dos áreas
usen la misma clave."""

from __future__ import annotations

from textos_en_carga import T as CARGA
from textos_en_cian import T as CIAN
from textos_en_cop import T as COP
from textos_en_datos import T as DATOS
from textos_en_fusion import T as FUSION
from textos_en_guia import T as GUIA
from textos_en_qaqc import T as QAQC
from textos_en_qaqc_val import T as QAQC_VAL
from textos_en_sed import T as SED
from textos_en_ui import T as UI

TEXTS: dict[str, str] = {}
for _part in (UI, GUIA, DATOS, FUSION, CIAN, SED, COP, QAQC, QAQC_VAL, CARGA):
    _repeated = TEXTS.keys() & _part.keys()
    if _repeated:
        raise ValueError(f"claves repetidas en textos_en: {sorted(_repeated)}")
    TEXTS.update(_part)
