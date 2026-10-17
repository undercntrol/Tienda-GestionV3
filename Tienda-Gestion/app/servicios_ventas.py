"""HU-01 — Registrar una venta · HU-05 — Fiar · HU-02 — Consultar · HU-07 — Corregir (admin).

Reglas que salieron de la observación en la tienda:
- El tendero anota el VALOR de la venta, no la cantidad × precio.
- Si el producto no existe, se crea solo (con ese valor como precio).
- "Cliente general" = venta de contado; exige método de pago.
- Cualquier otro cliente = FIADO: queda pendiente en su cuenta y el
  método de pago se define el día que la paga. Si el nombre no está en la
  lista, se crea como cliente "pasajero".
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime

from . import config, permisos
from .errores import DatoInvalido, NoEncontrado
from .formato import parse_numero
from .modelos import Usuario, VentaRegistrada
from .repositorios import (
    SOLO_CONTADO,
    RepositorioClientes,
    RepositorioMetodos,
    RepositorioProductos,
    RepositorioVentas,
)
from .servicios_catalogo import PRECIO_MAXIMO, limpiar_nombre


def limpiar_monto(texto) -> float:
    try:
        monto = parse_numero(texto)
    except ValueError:
        raise DatoInvalido("El monto solo puede tener números.") from None
    if monto <= 0:
        raise DatoInvalido("Escribe un monto mayor que cero.")
    if monto > PRECIO_MAXIMO:
        raise DatoInvalido("El monto es demasiado alto. Revisa si sobra un cero.")
    return monto


def limpiar_fecha(texto: str | date | None) -> str:
    """Acepta date o 'AAAA-MM-DD'. Vacío = hoy."""
    if texto in (None, ""):
        return date.today().isoformat()
    if isinstance(texto, date):
        return texto.isoformat()
    try:
        return datetime.strptime(str(texto).strip(), "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise DatoInvalido("Fecha inválida. Usa el formato AAAA-MM-DD o el 📅.") from None


def es_contado(cliente: str | None) -> bool:
    return (cliente or "").strip().lower() in (config.CLIENTE_GENERAL.lower(), "")


class ServicioVentas:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.ventas = RepositorioVentas(conn)
        self.productos = RepositorioProductos(conn)
        self.metodos = RepositorioMetodos(conn)
        self.clientes = RepositorioClientes(conn)

    # ---------------- apoyo ----------------
    def _producto_id(self, nombre: str, monto: float) -> int:
        fila = self.productos.por_nombre(nombre)
        return fila["id"] if fila else self.productos.crear(nombre, monto)

    def _metodo_id(self, nombre: str) -> int:
        fila = self.metodos.por_nombre(nombre)
        return fila["id"] if fila else self.metodos.crear(" ".join(nombre.split()))

    def _cliente_id(self, nombre: str) -> int:
        fila = self.clientes.por_nombre(nombre)
        if fila:
            if not fila["activo"]:
                self.clientes.reactivar(fila["id"])
            return fila["id"]
        return self.clientes.crear(limpiar_nombre(nombre, "del cliente"), "", "pasajero")

    # ---------------- HU-01 / HU-05 ----------------
    def registrar(self, producto: str, monto, metodo: str = "",
                  cliente: str = config.CLIENTE_GENERAL, fecha=None) -> VentaRegistrada:
        producto = limpiar_nombre(producto or "")
        valor = limpiar_monto(monto)
        dia = limpiar_fecha(fecha)

        if es_contado(cliente):
            metodo = (metodo or "").strip()
            if not metodo:
                raise DatoInvalido("Indica el método de pago.")
            pid = self._producto_id(producto, valor)
            mid = self._metodo_id(metodo)
            tid = self.ventas.registrar(pid, mid, valor, dia, cliente_id=None, pagada=True)
            return VentaRegistrada(tid, producto, valor, dia, metodo,
                                   config.CLIENTE_GENERAL, fiada=False)

        # Fiado: sin método de pago; se define al cobrar la cuenta.
        nombre_cliente = limpiar_nombre(cliente, "del cliente")
        pid = self._producto_id(producto, valor)
        cid = self._cliente_id(nombre_cliente)
        tid = self.ventas.registrar(pid, None, valor, dia, cliente_id=cid,
                                    pagada=False, fecha_pago=None)
        return VentaRegistrada(tid, producto, valor, dia, None, nombre_cliente, fiada=True)

    def metodos_pago(self):
        return self.metodos.listar()

    def precio_sugerido(self, producto: str) -> float:
        fila = self.productos.por_nombre(producto or "")
        return float(fila["precio"]) if fila else 0.0

    # ---------------- HU-02 / HU-07 ----------------
    def listar(self, desde, hasta, producto_id=None, metodo_id=None, cliente_id=None):
        """Devuelve (filas, total). Si las fechas vienen al revés, se voltean."""
        ini, fin = limpiar_fecha(desde), limpiar_fecha(hasta)
        if fin < ini:
            ini, fin = fin, ini
        filas = self.ventas.filtradas(ini, fin, producto_id, metodo_id, cliente_id)
        return filas, sum(f["monto"] for f in filas)

    def del_dia(self, dia=None):
        return self.listar(dia, dia)

    def obtener(self, tid: int):
        fila = self.ventas.obtener(tid)
        if fila is None:
            raise NoEncontrado("La venta ya no existe.")
        return fila

    def editar(self, quien: Usuario, tid: int, producto: str, metodo: str, monto, fecha) -> None:
        permisos.exigir(quien, permisos.CORREGIR_VENTAS)
        actual = self.obtener(tid)
        producto = limpiar_nombre(producto or "")
        valor = limpiar_monto(monto)
        dia = limpiar_fecha(fecha)
        metodo = (metodo or "").strip()
        if actual["pagada"] and not metodo:
            raise DatoInvalido("Una venta pagada necesita método de pago.")
        mid = self._metodo_id(metodo) if metodo else None
        self.ventas.editar(tid, self._producto_id(producto, valor), mid, valor, dia)

    def eliminar(self, quien: Usuario, tid: int) -> None:
        permisos.exigir(quien, permisos.CORREGIR_VENTAS)
        self.obtener(tid)
        self.ventas.eliminar(tid)

    # Re-exportado para que la pantalla no importe el repositorio.
    SOLO_CONTADO = SOLO_CONTADO
