"""Gráficos de la pestaña «Control de calidad»: la carta de control del CRM que se arma punto a
punto (con la regla que se dispara en cada uno), el gráfico de Thompson-Howarth, la curva de
diferencias relativas, los blancos contra 3 × y 10 × LD y el histograma de CDN-GS-2X.

Nada arranca solo: «Reproducir» agrega los resultados de uno en uno en el navegador. Cada
cuadro solo reemplaza los trazos que cambian (los límites quedan fijos)."""

from __future__ import annotations

import math

import plotly.graph_objects as go
from dibujo import INK, es
from i18n import opt, t
from nomograma import _layout, _note, _player
from qaqc_calculo import BlkView, CertView, CrmView, DupView, cuadros

from muestreo import qaqc as qc

OK_C, W2_C, PAIR_C, R3_C = "#1F7A6F", "#B7791F", "#C0462B", "#7A1F2B"
STATE_COLOR = {qc.OK: OK_C, qc.FUERA_2SD: W2_C, qc.DOS_SEGUIDOS: PAIR_C, qc.FUERA_3SD: R3_C}
STATE_SYMBOL = {
    qc.OK: "circle",
    qc.FUERA_2SD: "diamond",
    qc.DOS_SEGUIDOS: "square",
    qc.FUERA_3SD: "x",
}
CERT_C, LINE_C, MUTED = "#3B82A6", "#8E979C", "#B7B0A0"
PAD = 0.22  # holgura vertical de la carta (deja lugar a la nota de la regla)


def _marker(state: str) -> dict:
    return dict(
        size=11,
        color=STATE_COLOR[state],
        symbol=STATE_SYMBOL[state],
        line=dict(width=1.5, color=INK),
    )


def _hline(
    fig: go.Figure, y: float, name: str, color: str, dash: str, x1: float, show: bool = True
) -> None:
    fig.add_trace(
        go.Scatter(
            x=[0, x1],
            y=[y, y],
            mode="lines",
            name=name,
            showlegend=show,
            line=dict(color=color, width=2, dash=dash),
            hoverinfo="skip",
        )
    )


# ------------------------------------------------------------------ carta de control del CRM
def _state_traces(view: CrmView, k: int) -> list[go.Scatter]:
    """Los trazos que cambian: la línea que une los resultados y un trazo por estado."""
    sub = view.puntos[:k]
    out = [
        go.Scatter(
            x=[p.n for p in sub],
            y=[p.valor for p in sub],
            mode="lines",
            line=dict(color=MUTED, width=1.5),
            showlegend=False,
            hoverinfo="skip",
        )
    ]
    for state in qc.ESTADOS:
        mine = [p for p in sub if p.estado == state]
        out.append(
            go.Scatter(
                x=[p.n for p in mine],
                y=[p.valor for p in mine],
                mode="markers",
                name=t(f"qc.crm.state.{state}"),
                marker=_marker(state),
                customdata=[p.z for p in mine],
                hovertemplate="n = %{x}<br>%{y}<br>z = %{customdata:.2f}<extra></extra>",
            )
        )
    return out


def _crm_note(view: CrmView, k: int) -> dict:
    p = view.puntos[k - 1]
    text = t(
        "qc.crm.note", n=p.n, v=es(p.valor, 4), z=es(p.z, 2), rule=t(f"qc.crm.rule.{p.estado}")
    )
    return _note(text.replace(" → ", "<br>→ "))  # en dos líneas: a 1 000 px no cabe en una


def crm_figure(view: CrmView) -> go.Figure:
    """Los resultados contra el certificado, ±2 SD y ±3 SD; el reproductor los agrega de uno en
    uno y rotula qué regla dispara cada uno. Arranca mostrando la serie completa."""
    n = len(view.puntos)
    ks = cuadros(n)
    names = [str(k) for k in ks]
    frames = [
        go.Frame(
            data=_state_traces(view, k),
            traces=list(range(5)),
            name=str(k),
            layout=_crm_note(view, k),
        )
        for k in ks
    ]
    fig = go.Figure(data=_state_traces(view, n), frames=frames, layout=_crm_note(view, n))
    x1 = n + 1
    (lo2, hi2), (lo3, hi3) = view.lim2, view.lim3
    _hline(fig, view.certificado, t("qc.crm.cert"), INK, "solid", x1)
    for y, name, dash, show in (
        (hi2, t("qc.crm.2sd"), "dash", True),
        (lo2, "", "dash", False),
        (hi3, t("qc.crm.3sd"), "dot", True),
        (lo3, "", "dot", False),
    ):
        _hline(fig, y, name, W2_C if dash == "dash" else R3_C, dash, x1, show)
    ys = [p.valor for p in view.puntos] + [lo3, hi3]
    pad = PAD * (max(ys) - min(ys))
    fig.update_xaxes(range=[0.5, n + 0.5], dtick=None)
    fig.update_yaxes(range=[min(ys) - pad, max(ys) + pad])
    title = t(
        "qc.crm.title",
        name=opt(view.nombre),
        src=t("qc.src.synth" if view.sintetica else "qc.src.table"),
    )
    _layout(fig, title, 480, x=dict(title=t("qc.crm.x")), y=dict(title=t("qc.crm.y")), bottom=130)
    return _player(fig, names, ms=250)


# ------------------------------------------------------------------ Thompson-Howarth
def _th_class(c: float, d: float, p_pct: float) -> str:
    if c > 0 and d <= qc.linea_th(c, p_pct, qc.Z_P90):
        return "in90"
    if c > 0 and d <= qc.linea_th(c, p_pct, qc.Z_P99):
        return "in99"
    return "out"


def th_dibujables(view: DupView) -> list[tuple[float, float]]:
    """(media, |a − b|) de los pares que se pueden dibujar en escala logarítmica: media > 0 y
    diferencia > 0. Los demás se omiten SOLO del dibujo: siguen en los conteos y el veredicto."""
    out = []
    for a, b in view.pares:
        c, d = (a + b) / 2.0, abs(a - b)
        if c > 0 and d > 0:
            out.append((c, d))
    return out


def th_omitidos(view: DupView) -> int:
    """Cuántos pares no se dibujan (media ≤ 0 o diferencia 0); dibujados + omitidos = pares."""
    return len(view.pares) - len(th_dibujables(view))


def th_figure(view: DupView) -> go.Figure:
    """|a − b| contra la media del par, con las líneas de percentil 90 y 99 de la precisión P,
    en ejes logarítmicos (las líneas quedan rectas y paralelas)."""
    groups: dict[str, list[tuple[float, float]]] = {"in90": [], "in99": [], "out": []}
    pts_all = th_dibujables(view)
    for c, d in pts_all:
        groups[_th_class(c, d, view.p_pct)].append((c, d))
    cs = [c for c, _ in pts_all]
    x0, x1 = (min(cs) / 1.6, max(cs) * 1.6) if cs else (1e-3, 1.0)
    fig = go.Figure()
    th = view.th
    for key, color, symbol, count in (
        ("in90", OK_C, "circle", th.dentro90),
        ("in99", W2_C, "diamond", th.dentro99 - th.dentro90),
        ("out", R3_C, "x", th.n - th.dentro99),
    ):
        pts = groups[key]
        fig.add_trace(
            go.Scatter(
                x=[c for c, _ in pts],
                y=[d for _, d in pts],
                mode="markers",
                name=t(f"qc.th.{key}", n=count),
                marker=dict(size=9, color=color, symbol=symbol, line=dict(width=1, color=INK)),
            )
        )
    for z, name, dash, color in (
        (qc.Z_P90, t("qc.th.l90", p=es(view.p_pct, 0)), "dash", W2_C),
        (qc.Z_P99, t("qc.th.l99", p=es(view.p_pct, 0)), "dot", R3_C),
    ):
        coef = qc.coeficiente_th(z, view.p_pct)
        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[coef * x0, coef * x1],
                mode="lines",
                name=name,
                line=dict(color=color, width=2, dash=dash),
                hoverinfo="skip",
            )
        )
    _layout(fig, t("qc.th.title"), 460, x=dict(title=t("qc.th.x")), y=dict(title=t("qc.th.y")))
    # potencias de 10 en vez del prefijo SI de Plotly («100µ» se leería como micro-unidades)
    fig.update_xaxes(type="log", range=[math.log10(x0), math.log10(x1)], exponentformat="power")
    fig.update_yaxes(type="log", exponentformat="power")
    return fig


def rpd_figure(view: DupView) -> go.Figure:
    """Las diferencias relativas de los pares, de menor a mayor, contra el umbral de su tipo."""
    vals = sorted(r for r in view.rpd if r is not None)
    m = len(vals)
    u = view.dup.umbral
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[100.0 * (i + 1) / m for i in range(m)],
            y=vals,
            mode="lines+markers",
            name=t("qc.rpd.curve"),
            line=dict(color=CERT_C, width=2),
            marker=dict(size=5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 100],
            y=[u.rpd_max, u.rpd_max],
            mode="lines",
            name=t("qc.rpd.limit", u=es(u.rpd_max, 0)),
            line=dict(color=W2_C, width=2, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[u.minimo_pct, u.minimo_pct],
            y=[0, max(vals[-1], u.rpd_max)],
            mode="lines",
            name=t("qc.rpd.min", m=es(u.minimo_pct, 0)),
            line=dict(color=R3_C, width=2, dash="dot"),
        )
    )
    fig.update_xaxes(range=[0, 100])
    fig.update_yaxes(rangemode="tozero")
    _layout(fig, t("qc.rpd.title"), 420, x=dict(title=t("qc.rpd.x")), y=dict(title=t("qc.rpd.y")))
    fig.update_layout(**_note(t("qc.rpd.note", pct=es(view.dup.pct_bajo, 1), u=es(u.rpd_max, 0))))
    return fig


# ------------------------------------------------------------------ blancos
def blk_figure(view: BlkView) -> go.Figure:
    """Cada blanco en el orden de análisis, con 3 × LD (alerta) y 10 × LD (falla)."""
    r = view.res
    n = len(view.valores)
    fig = go.Figure()
    classes = (
        ("ok", OK_C, "circle", lambda x: x <= qc.K_ALERTA * r.ld),
        ("alert", W2_C, "diamond", lambda x: qc.K_ALERTA * r.ld < x <= qc.K_FALLA * r.ld),
        ("fail", R3_C, "x", lambda x: x > qc.K_FALLA * r.ld),
    )
    for key, color, symbol, test in classes:
        pts = [(i + 1, x) for i, x in enumerate(view.valores) if test(x)]
        fig.add_trace(
            go.Scatter(
                x=[i for i, _ in pts],
                y=[x for _, x in pts],
                mode="markers",
                name=t(f"qc.blk.{key}"),
                marker=dict(size=10, color=color, symbol=symbol, line=dict(width=1, color=INK)),
            )
        )
    x1 = n + 1
    _hline(fig, r.ld, t("qc.blk.ld", ld=es(r.ld, 4)), LINE_C, "solid", x1)
    _hline(fig, qc.K_ALERTA * r.ld, t("qc.blk.l3"), W2_C, "dash", x1)
    _hline(fig, qc.K_FALLA * r.ld, t("qc.blk.l10"), R3_C, "dot", x1)
    top = max(max(view.valores), qc.K_FALLA * r.ld) * 1.1
    fig.update_xaxes(range=[0.5, n + 0.5])
    fig.update_yaxes(range=[0, top])
    src = t("qc.src.synth" if view.sintetica else "qc.src.table")
    _layout(
        fig,
        t("qc.blk.title", src=src),
        420,
        x=dict(title=t("qc.blk.x")),
        y=dict(title=t("qc.blk.y")),
    )
    return fig


# ------------------------------------------------------------------ certificar un estándar
def cert_figure(view: CertView) -> go.Figure:
    """Los 150 resultados de CDN-GS-2X: los que quedan tras el recorte y los que se descartan."""
    c = view.cert
    keep = [x for x, k in zip(view.resultados, c.retenidos, strict=True) if k]
    drop = [x for x, k in zip(view.resultados, c.retenidos, strict=True) if not k]
    xbins = dict(start=2.08, end=2.80, size=0.04)
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=keep,
            xbins=xbins,
            marker=dict(color=CERT_C, line=dict(width=1, color=INK)),
            name=t("qc.cert.keep", n=len(keep)),
        )
    )
    fig.add_trace(
        go.Histogram(
            x=drop,
            xbins=xbins,
            marker=dict(color=R3_C, line=dict(width=1, color=INK)),
            name=t("qc.cert.drop", n=len(drop)),
        )
    )
    top = 1.0
    for x, name, dash, color in (
        (c.media, t("qc.cert.mean", m=es(c.media, 3)), "solid", INK),
        (c.media - c.dos_sd, t("qc.cert.band", s=es(c.dos_sd, 3)), "dash", W2_C),
        (c.media + c.dos_sd, "", "dash", W2_C),
        (c.bajo, t("qc.cert.cut", k=es(c.k, 0)), "dot", R3_C),
        (c.alto, "", "dot", R3_C),
    ):
        fig.add_trace(
            go.Scatter(
                x=[x, x],
                y=[0, top],
                mode="lines",
                name=name,
                showlegend=bool(name),
                yaxis="y2",
                line=dict(color=color, width=2, dash=dash),
                hoverinfo="skip",
            )
        )
    fig.update_layout(barmode="stack", yaxis2=dict(overlaying="y", range=[0, 1], visible=False))
    _layout(
        fig,
        t("qc.cert.title", n=es(c.n_total, 0)),
        460,
        x=dict(title=t("qc.cert.x")),
        y=dict(title=t("qc.cert.y")),
    )
    return fig
