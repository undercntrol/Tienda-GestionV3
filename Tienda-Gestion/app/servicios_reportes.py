"""HU-03 — Total de una fecha · HU-09 — Reporte de ingresos por día, semana o mes (HTML y Excel).

Los reportes cuentan INGRESOS: ventas pagadas, ubicadas por la fecha en
que se pagaron. Una venta fiada el lunes y cobrada el viernes aparece el
viernes. Por eso el reporte puede no coincidir con la lista de ventas.
"""

from __future__ import annotations

import calendar
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

from . import config
from .config import MESES
from .errores import DatoInvalido
from .exportar_xlsx import exportar_xlsx
from .formato import dia_corto, dia_semana, esc, fmt_money, lunes_de
from .modelos import Periodo, Reporte
from .repositorios import RepositorioVentas
from .servicios_ventas import limpiar_fecha

TIPOS = ("Día", "Semana", "Mes")


def periodo(tipo: str, fecha=None, mes: str | None = None, anio: int | str | None = None) -> Periodo:
    """Arma el rango de fechas del reporte.

    Día → ese día. Semana → de lunes a domingo de la semana de esa fecha.
    Mes → del 1 al último día del mes (respeta febrero y bisiestos).
    """
    if tipo == "Mes":
        try:
            anio = int(anio)
            num_mes = MESES.index(mes) + 1
        except (TypeError, ValueError):
            raise DatoInvalido("Elige el mes y el año del reporte.") from None
        ini = date(anio, num_mes, 1)
        fin = date(anio, num_mes, calendar.monthrange(anio, num_mes)[1])
        return Periodo(ini.isoformat(), fin.isoformat(), f"Mes de {mes} {anio}")
    d = date.fromisoformat(limpiar_fecha(fecha))
    if tipo == "Día":
        return Periodo(d.isoformat(), d.isoformat(),
                       f"Día {d.day} de {MESES[d.month - 1]} de {d.year}")
    if tipo == "Semana":
        ini = lunes_de(d)
        fin = ini + timedelta(days=6)
        return Periodo(ini.isoformat(), fin.isoformat(),
                       f"Semana del {ini.day} de {MESES[ini.month - 1]} al "
                       f"{fin.day} de {MESES[fin.month - 1]} de {fin.year}")
    raise DatoInvalido("Elige Día, Semana o Mes.")


class ServicioReportes:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.ventas = RepositorioVentas(conn)

    def generar(self, per: Periodo, producto_id: int | None = None,
                metodo_id: int | None = None, filtros_txt: str = "") -> Reporte:
        filas = self.ventas.ingresos(per.ini, per.fin, producto_id, metodo_id)
        por_producto: dict[str, list] = {}
        por_dia: dict[str, float] = {}
        por_metodo: dict[str, float] = {}
        for r in filas:
            p = por_producto.setdefault(r["producto"], [0, 0.0])
            p[0] += 1
            p[1] += r["monto"]
            por_dia[r["fecha"]] = por_dia.get(r["fecha"], 0.0) + r["monto"]
            por_metodo[r["metodo"]] = por_metodo.get(r["metodo"], 0.0) + r["monto"]
        return Reporte(
            periodo=per,
            filtros=filtros_txt or "Producto: Todos · Pago: Todos",
            filas=list(filas),
            por_producto=sorted(((n, v[0], v[1]) for n, v in por_producto.items()),
                                key=lambda t: t[2], reverse=True),
            por_dia=sorted(por_dia.items()),
            por_metodo=sorted(por_metodo.items()),
            ingresos=float(sum(r["monto"] for r in filas)),
        )

    # ---------------- exportar ----------------
    @staticmethod
    def html(rep: Reporte, nombre_local: str = config.APP_NOMBRE) -> str:
        verde = config.COLOR_TEXTO_VERDE
        f_prod = "".join(f"<tr><td>{esc(n)}</td><td class='c'>{k}</td>"
                         f"<td class='n'>{fmt_money(t)}</td></tr>" for n, k, t in rep.por_producto)
        f_dia = "".join(f"<tr><td>{dia_corto(f)}</td><td class='n'>{fmt_money(t)}</td></tr>"
                        for f, t in rep.por_dia)
        f_met = "".join(f"<tr><td>{esc(m)}</td><td class='n'>{fmt_money(t)}</td></tr>"
                        for m, t in rep.por_metodo)
        vacio = "<tr><td colspan=3>Sin ventas</td></tr>"
        return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Reporte — {esc(nombre_local)}</title>
<style>
 body{{font-family:'Segoe UI',Arial,sans-serif;margin:0;padding:26px;color:#222}}
 h1{{color:{verde};margin:0}} .sub{{color:#666;margin:2px 0 18px}}
 h2{{font-size:15px;margin:20px 0 6px;color:#333}}
 table{{border-collapse:collapse;width:100%;max-width:560px;font-size:13px;margin-bottom:8px}}
 th,td{{padding:7px 9px;border-bottom:1px solid #e2e2e2;text-align:left}}
 th{{background:{verde};color:#fff}} td.n,th.n{{text-align:right}} td.c{{text-align:center}}
 .tot{{font-size:18px;font-weight:bold;color:{verde};margin-top:10px}}
 button{{margin-top:18px;padding:9px 20px;font-size:13px;cursor:pointer}}
 @media print{{button{{display:none}}}}
</style></head><body>
<h1>{esc(nombre_local)}</h1>
<p class="sub">Reporte de ventas · {esc(rep.periodo.etiqueta)} · {esc(rep.filtros)}<br>
Generado: {datetime.now():%Y-%m-%d %H:%M}</p>
<p class="tot">Ingresos totales: {fmt_money(rep.ingresos)} &nbsp; ({len(rep.filas)} ventas)</p>
<h2>Total por producto</h2>
<table><thead><tr><th>Producto</th><th class="c">Ventas</th><th class="n">Total</th></tr></thead>
<tbody>{f_prod or vacio}</tbody></table>
<h2>Total por día</h2>
<table><thead><tr><th>Día</th><th class="n">Total</th></tr></thead>
<tbody>{f_dia or vacio}</tbody></table>
<h2>Por método de pago</h2>
<table><thead><tr><th>Método</th><th class="n">Total</th></tr></thead>
<tbody>{f_met or vacio}</tbody></table>
<button onclick="window.print()">🖨 Imprimir</button>
</body></html>"""

    def guardar_html(self, rep: Reporte, carpeta: Path | None = None) -> Path:
        carpeta = Path(carpeta or config.CARPETA_SALIDAS)
        carpeta.mkdir(parents=True, exist_ok=True)
        ruta = carpeta / "reporte_ventas.html"
        ruta.write_text(self.html(rep), encoding="utf-8")
        return ruta

    @staticmethod
    def hojas_excel(rep: Reporte) -> list:
        return [
            ("Resumen", [["Concepto", "Valor"], ["Período", rep.periodo.etiqueta],
                         ["Filtros", rep.filtros], ["Ingresos totales", round(rep.ingresos)],
                         ["Número de ventas", len(rep.filas)],
                         ["Generado", f"{datetime.now():%Y-%m-%d %H:%M}"]]),
            ("Por producto", [["Producto", "Ventas", "Total"]]
             + [[n, k, round(t)] for n, k, t in rep.por_producto]),
            ("Por día", [["Día", "Total"]] + [[dia_corto(f), round(t)] for f, t in rep.por_dia]),
            ("Por pago", [["Método", "Total"]] + [[m, round(t)] for m, t in rep.por_metodo]),
            ("Ventas", [["Fecha", "Día", "Producto", "Pago", "Monto"]]
             + [[r["fecha"], dia_semana(r["fecha"]), r["producto"], r["metodo"], round(r["monto"])]
                for r in rep.filas]),
        ]

    def guardar_excel(self, rep: Reporte, carpeta: Path | None = None) -> Path:
        carpeta = Path(carpeta or config.CARPETA_SALIDAS)
        carpeta.mkdir(parents=True, exist_ok=True)
        ruta = carpeta / "reporte_ventas.xlsx"
        try:
            exportar_xlsx(ruta, self.hojas_excel(rep))
        except PermissionError:
            raise DatoInvalido("No se pudo crear el Excel. Si está abierto, ciérralo e "
                               "intenta de nuevo.") from None
        return ruta
