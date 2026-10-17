"""HU-05 — Clientes a los que se fía · HU-06 — Saldos · HU-08 — Cobrar la cuenta con comprobante.

Regla clave: lo fiado NO es plata que entró. La venta queda pendiente
(pagada = 0) y solo cuenta como ingreso el día que se cobra la cuenta
(fecha_pago). Al cobrar se salda TODO lo pendiente del cliente.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from . import config
from .errores import DatoInvalido, Duplicado, NoEncontrado
from .formato import esc, fmt_money
from .modelos import Cobro, ItemCuenta
from .repositorios import RepositorioClientes, RepositorioMetodos
from .servicios_catalogo import limpiar_nombre
from .servicios_ventas import limpiar_fecha


class ServicioCuentas:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.clientes = RepositorioClientes(conn)
        self.metodos = RepositorioMetodos(conn)

    # ---------------- clientes ----------------
    def crear_cliente(self, nombre: str, telefono: str = "") -> int:
        nombre = limpiar_nombre(nombre, "del cliente")
        if nombre.lower() == config.CLIENTE_GENERAL.lower():
            raise DatoInvalido("Ese nombre está reservado para las ventas de contado.")
        if self.clientes.por_nombre(nombre):
            raise Duplicado("Ya existe un cliente con ese nombre.")
        return self.clientes.crear(nombre, (telefono or "").strip(), "fijo")

    def editar_cliente(self, cid: int, nombre: str, telefono: str = "") -> None:
        self.obtener(cid)
        nombre = limpiar_nombre(nombre, "del cliente")
        if nombre.lower() == config.CLIENTE_GENERAL.lower():
            raise DatoInvalido("Ese nombre está reservado para las ventas de contado.")
        otro = self.clientes.por_nombre(nombre)
        if otro and otro["id"] != cid:
            raise Duplicado("Ya existe un cliente con ese nombre.")
        self.clientes.editar(cid, nombre, (telefono or "").strip())

    def quitar_cliente(self, cid: int) -> bool:
        """No se quita a quien debe. Si tiene historial, se oculta (se conserva).

        Devuelve True si se borró del todo, False si solo se desactivó.
        """
        self.obtener(cid)
        if self.clientes.saldo(cid) > 0:
            raise DatoInvalido("Este cliente todavía debe dinero. Cobra su cuenta antes de quitarlo.")
        if self.clientes.contar_movimientos(cid) == 0:
            self.clientes.borrar(cid)
            return True
        self.clientes.desactivar(cid)
        return False

    def obtener(self, cid: int):
        fila = self.clientes.obtener(cid)
        if fila is None:
            raise NoEncontrado("Ese cliente no existe.")
        return fila

    def listar(self):
        return self.clientes.listar()

    def con_saldo(self):
        return self.clientes.con_saldo()

    def total_por_cobrar(self) -> float:
        return sum(c["saldo"] for c in self.clientes.con_saldo())

    def saldo(self, cid: int) -> float:
        return self.clientes.saldo(cid)

    def movimientos(self, cid: int):
        return self.clientes.movimientos(cid)

    # ---------------- HU-08 · cobrar ----------------
    def cobrar(self, cid: int, metodo: str, fecha_pago=None) -> Cobro:
        cliente = self.obtener(cid)
        pendientes = self.clientes.movimientos(cid, solo_pendientes=True)
        if not pendientes:
            raise DatoInvalido(f"{cliente['nombre']} no tiene nada pendiente por cobrar.")
        metodo = (metodo or "").strip()
        if not metodo:
            raise DatoInvalido("Elige el método de pago.")
        fila_metodo = self.metodos.por_nombre(metodo)
        mid = fila_metodo["id"] if fila_metodo else self.metodos.crear(metodo)
        dia = limpiar_fecha(fecha_pago)

        # El detalle se arma ANTES de marcar como pagadas.
        cobro = Cobro(
            cliente=cliente["nombre"],
            items=[ItemCuenta(r["fecha"], r["producto"], float(r["monto"])) for r in pendientes],
            total=float(sum(r["monto"] for r in pendientes)),
            metodo=fila_metodo["nombre"] if fila_metodo else metodo,
            fecha_pago=dia,
        )
        self.clientes.cobrar(cid, mid, dia)
        return cobro

    @staticmethod
    def comprobante_html(cobro: Cobro, nombre_local: str = config.APP_NOMBRE) -> str:
        filas = "".join(
            f"<tr><td>{i.fecha[8:10]}/{i.fecha[5:7]}</td><td>{esc(i.producto)}</td>"
            f"<td class='n'>{fmt_money(i.monto)}</td></tr>" for i in cobro.items)
        verde = config.COLOR_TEXTO_VERDE
        return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Cuenta de {esc(cobro.cliente)} — {esc(nombre_local)}</title>
<style>
 body{{font-family:'Segoe UI',Arial,sans-serif;background:#f2f2f2;margin:0;padding:24px;
      display:flex;flex-direction:column;align-items:center;color:#222}}
 .hoja{{background:#fff;width:420px;padding:26px 30px;box-shadow:0 2px 12px rgba(0,0,0,.15)}}
 h1{{font-size:17px;margin:0;color:{verde}}}
 .sub{{color:#666;font-size:12px;margin:2px 0 14px}}
 table{{width:100%;border-collapse:collapse;margin:10px 0;font-size:13px}}
 th,td{{padding:6px 8px;border-bottom:1px solid #e2e2e2;text-align:left}}
 th{{background:{verde};color:#fff}} td.n,th.n{{text-align:right}}
 .pago{{display:flex;justify-content:space-between;padding:12px 0;margin-top:6px;
        border-top:2px solid {verde};font-size:18px;font-weight:bold;color:{verde}}}
 .meta{{font-size:12px;color:#555;margin:2px 0}}
 button{{margin-top:16px;padding:9px 20px;font-size:13px;cursor:pointer}}
 @media print{{body{{background:#fff;padding:0}}.hoja{{box-shadow:none}}button{{display:none}}}}
</style></head><body>
<div class="hoja">
 <h1>{esc(nombre_local)}</h1>
 <p class="sub">Comprobante de pago de cuenta</p>
 <p class="meta">Cliente: <b>{esc(cobro.cliente)}</b></p>
 <p class="meta">Fecha de pago: {cobro.fecha_pago} &nbsp;·&nbsp; Pago con: {esc(cobro.metodo)}</p>
 <table><thead><tr><th>Fecha</th><th>Producto</th><th class="n">Valor</th></tr></thead>
 <tbody>{filas}</tbody></table>
 <div class="pago"><span>TOTAL PAGADO:</span><span>{fmt_money(cobro.total)}</span></div>
 <p class="meta" style="text-align:center;margin-top:10px">¡Cuenta saldada! Gracias.</p>
</div>
<button onclick="window.print()">🖨 Imprimir</button>
</body></html>"""

    def guardar_comprobante(self, cobro: Cobro, carpeta: Path | None = None) -> Path:
        carpeta = Path(carpeta or config.CARPETA_SALIDAS)
        carpeta.mkdir(parents=True, exist_ok=True)
        ruta = carpeta / f"cuenta_{datetime.now():%Y%m%d%H%M%S}.html"
        ruta.write_text(self.comprobante_html(cobro), encoding="utf-8")
        return ruta
