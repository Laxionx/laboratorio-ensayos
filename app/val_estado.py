"""Fila de indicadores de resumen de la pestaña Validación: cuántas comprobaciones cuadran con lo
publicado, sumadas sobre todas las áreas que la pestaña ya tabula. No cambia ninguna cifra de las
tablas: solo cuenta lo que cada área ya calcula, una sola vez por proceso."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from estado import indicadores
from i18n import int_num, t

from muestreo import cianuracion_datos as cian
from muestreo import copelacion_validacion as cop
from muestreo import fusion_datos as fus
from muestreo import qaqc_validacion as qaqc
from muestreo import sedimentacion_datos as sed
from muestreo import validacion as gy


@dataclass(frozen=True)
class Resumen:
    ok: int
    total: int
    areas: int

    @property
    def fallan(self) -> int:
        return self.total - self.ok


@lru_cache(maxsize=1)
def resumen() -> Resumen:
    """Las comprobaciones que cuadran y el total, por área, sumadas. La carga fundente cuenta como
    «cuadra» solo el veredicto estricto (los de truncamiento o pesos de Bugbee cuentan aparte)."""
    gy_checks = gy.minnitt_2017_checks() + gy.chieregati_checks() + gy.clifton_checks()
    fusion = fus.summary(fus.all_checks())
    celdas = cop.celdas_cuantitativas()
    pares = [
        (sum(c.ok for c in gy_checks), len(gy_checks)),
        (fusion["cuadra"], fusion["total"]),
        *cian.summary().values(),
        *sed.summary().values(),
        (sum(c.cuadra for c in celdas), len(celdas)),
        *qaqc.summary().values(),
    ]
    return Resumen(sum(a for a, _ in pares), sum(b for _, b in pares), 6)


def estado_validacion() -> None:
    r = resumen()
    indicadores(
        [
            (t("vi.ok"), f"{int_num(r.ok)} / {int_num(r.total)}", t("vi.ok.help")),
            (t("vi.no"), int_num(r.fallan), t("vi.no.help")),
            (t("vi.areas"), int_num(r.areas), t("vi.areas.help")),
        ]
    )
