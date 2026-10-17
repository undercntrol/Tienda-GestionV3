"""Repositorios: TODO el SQL del proyecto vive aquí.

Reciben la conexión por parámetro para que las pruebas usen una base en
memoria. No validan nada: las reglas están en los servicios.
Los valores siempre van como parámetros (?), nunca pegados al SQL.
"""

from __future__ import annotations

import sqlite3

from . import config


class RepositorioProductos:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def listar(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT id, nombre, precio FROM productos ORDER BY nombre COLLATE NOCASE"
        ).fetchall()

    def obtener(self, pid: int) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT id, nombre, precio FROM productos WHERE id = ?", (pid,)
        ).fetchone()

    def por_nombre(self, nombre: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT id, nombre, precio FROM productos WHERE nombre = ? COLLATE NOCASE",
            (nombre.strip(),),
        ).fetchone()

    def crear(self, nombre: str, precio: float) -> int:
        cur = self.conn.execute(
            "INSERT INTO productos (nombre, precio) VALUES (?, ?)", (nombre, precio)
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def editar(self, pid: int, nombre: str, precio: float) -> None:
        self.conn.execute(
            "UPDATE productos SET nombre = ?, precio = ? WHERE id = ?", (nombre, precio, pid)
        )
        self.conn.commit()

    def eliminar(self, pid: int) -> None:
        """Las ventas se conservan: quedan con producto '(eliminado)'."""
        self.conn.execute("DELETE FROM productos WHERE id = ?", (pid,))
        self.conn.commit()


class RepositorioMetodos:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def listar(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT id, nombre FROM metodos_pago ORDER BY nombre COLLATE NOCASE"
        ).fetchall()

    def por_nombre(self, nombre: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT id, nombre FROM metodos_pago WHERE nombre = ? COLLATE NOCASE",
            (nombre.strip(),),
        ).fetchone()

    def crear(self, nombre: str) -> int:
        cur = self.conn.execute("INSERT INTO metodos_pago (nombre) VALUES (?)", (nombre,))
        self.conn.commit()
        return int(cur.lastrowid)


# Consulta base de la lista de ventas (fecha de VENTA, contado y fiadas).
_SELECT_VENTAS = """
    SELECT tr.id, tr.fecha, tr.monto, tr.producto_id, tr.metodo_id,
           tr.cliente_id, tr.pagada, tr.fecha_pago,
           COALESCE(p.nombre, '(eliminado)') AS producto,
           COALESCE(m.nombre, '—')           AS metodo,
           COALESCE(cl.nombre, ?)            AS cliente
      FROM transacciones tr
      LEFT JOIN productos    p  ON p.id  = tr.producto_id
      LEFT JOIN metodos_pago m  ON m.id  = tr.metodo_id
      LEFT JOIN clientes     cl ON cl.id = tr.cliente_id
"""

# Valor especial del filtro de cliente: solo ventas de contado.
SOLO_CONTADO = 0


class RepositorioVentas:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def registrar(self, producto_id: int, metodo_id: int | None, monto: float,
                  fecha: str, cliente_id: int | None = None, pagada: bool = True,
                  fecha_pago: str | None = None) -> int:
        if pagada and fecha_pago is None:
            fecha_pago = fecha  # de contado: se pagó el día de la venta
        cur = self.conn.execute(
            "INSERT INTO transacciones (producto_id, metodo_id, monto, fecha, "
            "cliente_id, pagada, fecha_pago) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (producto_id, metodo_id, monto, fecha, cliente_id, int(pagada), fecha_pago),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def obtener(self, tid: int) -> sqlite3.Row | None:
        return self.conn.execute(
            _SELECT_VENTAS + " WHERE tr.id = ?", (config.CLIENTE_GENERAL, tid)
        ).fetchone()

    def editar(self, tid: int, producto_id: int, metodo_id: int | None,
               monto: float, fecha: str) -> None:
        """En una venta de contado la fecha de pago se mueve con la de venta."""
        fila = self.conn.execute(
            "SELECT pagada, cliente_id FROM transacciones WHERE id = ?", (tid,)
        ).fetchone()
        if fila and fila["pagada"] and fila["cliente_id"] is None:
            self.conn.execute(
                "UPDATE transacciones SET producto_id = ?, metodo_id = ?, monto = ?, "
                "fecha = ?, fecha_pago = ? WHERE id = ?",
                (producto_id, metodo_id, monto, fecha, fecha, tid))
        else:
            self.conn.execute(
                "UPDATE transacciones SET producto_id = ?, metodo_id = ?, monto = ?, "
                "fecha = ? WHERE id = ?",
                (producto_id, metodo_id, monto, fecha, tid))
        self.conn.commit()

    def eliminar(self, tid: int) -> None:
        self.conn.execute("DELETE FROM transacciones WHERE id = ?", (tid,))
        self.conn.commit()

    def filtradas(self, ini: str, fin: str, producto_id: int | None = None,
                  metodo_id: int | None = None,
                  cliente_id: int | None = None) -> list[sqlite3.Row]:
        """Ventas por fecha de VENTA, con filtros opcionales (HU-02).

        cliente_id = None → todos; SOLO_CONTADO (0) → solo Cliente general.
        """
        sql = _SELECT_VENTAS + " WHERE tr.fecha >= ? AND tr.fecha <= ?"
        params: list[object] = [config.CLIENTE_GENERAL, ini, fin]
        if producto_id is not None:
            sql += " AND tr.producto_id = ?"
            params.append(producto_id)
        if metodo_id is not None:
            sql += " AND tr.metodo_id = ?"
            params.append(metodo_id)
        if cliente_id == SOLO_CONTADO:
            sql += " AND tr.cliente_id IS NULL"
        elif cliente_id is not None:
            sql += " AND tr.cliente_id = ?"
            params.append(cliente_id)
        sql += " ORDER BY tr.fecha, tr.id"
        return self.conn.execute(sql, params).fetchall()

    def ingresos(self, ini: str, fin: str, producto_id: int | None = None,
                 metodo_id: int | None = None) -> list[sqlite3.Row]:
        """Ventas YA PAGADAS ubicadas por su fecha de PAGO (HU-03 y HU-09).

        Lo fiado entra al reporte el día que se cobra, no el día que se fió.
        """
        sql = """SELECT tr.id, tr.fecha_pago AS fecha, tr.monto,
                        COALESCE(p.nombre, '(eliminado)') AS producto,
                        COALESCE(m.nombre, '—')           AS metodo
                   FROM transacciones tr
                   LEFT JOIN productos    p ON p.id = tr.producto_id
                   LEFT JOIN metodos_pago m ON m.id = tr.metodo_id
                  WHERE tr.pagada = 1 AND tr.fecha_pago IS NOT NULL
                    AND tr.fecha_pago >= ? AND tr.fecha_pago <= ?"""
        params: list[object] = [ini, fin]
        if producto_id is not None:
            sql += " AND tr.producto_id = ?"
            params.append(producto_id)
        if metodo_id is not None:
            sql += " AND tr.metodo_id = ?"
            params.append(metodo_id)
        sql += " ORDER BY tr.fecha_pago, tr.id"
        return self.conn.execute(sql, params).fetchall()


class RepositorioClientes:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def listar(self, solo_activos: bool = True) -> list[sqlite3.Row]:
        sql = "SELECT * FROM clientes"
        if solo_activos:
            sql += " WHERE activo = 1"
        return self.conn.execute(sql + " ORDER BY nombre COLLATE NOCASE").fetchall()

    def obtener(self, cid: int) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM clientes WHERE id = ?", (cid,)).fetchone()

    def por_nombre(self, nombre: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM clientes WHERE nombre = ? COLLATE NOCASE", (nombre.strip(),)
        ).fetchone()

    def crear(self, nombre: str, telefono: str = "", tipo: str = "fijo") -> int:
        cur = self.conn.execute(
            "INSERT INTO clientes (nombre, telefono, tipo, activo) VALUES (?, ?, ?, 1)",
            (nombre, telefono or None, tipo),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def reactivar(self, cid: int) -> None:
        self.conn.execute("UPDATE clientes SET activo = 1 WHERE id = ?", (cid,))
        self.conn.commit()

    def editar(self, cid: int, nombre: str, telefono: str) -> None:
        self.conn.execute("UPDATE clientes SET nombre = ?, telefono = ? WHERE id = ?",
                          (nombre, telefono or None, cid))
        self.conn.commit()

    def contar_movimientos(self, cid: int) -> int:
        return int(self.conn.execute(
            "SELECT COUNT(*) FROM transacciones WHERE cliente_id = ?", (cid,)
        ).fetchone()[0])

    def borrar(self, cid: int) -> None:
        self.conn.execute("DELETE FROM clientes WHERE id = ?", (cid,))
        self.conn.commit()

    def desactivar(self, cid: int) -> None:
        self.conn.execute("UPDATE clientes SET activo = 0 WHERE id = ?", (cid,))
        self.conn.commit()

    def saldo(self, cid: int) -> float:
        return float(self.conn.execute(
            "SELECT COALESCE(SUM(monto), 0) FROM transacciones "
            "WHERE cliente_id = ? AND pagada = 0", (cid,)
        ).fetchone()[0])

    def con_saldo(self) -> list[sqlite3.Row]:
        """Clientes activos con lo que deben y cuántas compras tienen pendientes."""
        return self.conn.execute("""
            SELECT cl.id, cl.nombre, cl.telefono, cl.tipo,
                   COALESCE(SUM(CASE WHEN tr.pagada = 0 THEN tr.monto ELSE 0 END), 0) AS saldo,
                   COALESCE(SUM(CASE WHEN tr.pagada = 0 THEN 1 ELSE 0 END), 0)         AS pendientes
              FROM clientes cl
              LEFT JOIN transacciones tr ON tr.cliente_id = cl.id
             WHERE cl.activo = 1
             GROUP BY cl.id
             ORDER BY cl.nombre COLLATE NOCASE""").fetchall()

    def movimientos(self, cid: int, solo_pendientes: bool = False) -> list[sqlite3.Row]:
        sql = """SELECT tr.id, tr.fecha, tr.monto, tr.pagada, tr.fecha_pago,
                        COALESCE(p.nombre, '(eliminado)') AS producto
                   FROM transacciones tr
                   LEFT JOIN productos p ON p.id = tr.producto_id
                  WHERE tr.cliente_id = ?"""
        if solo_pendientes:
            sql += " AND tr.pagada = 0"
        return self.conn.execute(sql + " ORDER BY tr.fecha, tr.id", (cid,)).fetchall()

    def cobrar(self, cid: int, metodo_id: int, fecha_pago: str) -> int:
        """Marca como pagado TODO lo pendiente del cliente. Devuelve cuántas ventas."""
        cur = self.conn.execute(
            "UPDATE transacciones SET pagada = 1, metodo_id = ?, fecha_pago = ? "
            "WHERE cliente_id = ? AND pagada = 0", (metodo_id, fecha_pago, cid))
        self.conn.commit()
        return cur.rowcount


class RepositorioUsuarios:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def hay_usuarios(self) -> bool:
        return self.conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] > 0

    def listar(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT id, nombre, rol FROM usuarios ORDER BY nombre COLLATE NOCASE"
        ).fetchall()

    def por_nombre(self, nombre: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM usuarios WHERE nombre = ?", (nombre.strip(),)
        ).fetchone()

    def obtener(self, uid: int) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM usuarios WHERE id = ?", (uid,)).fetchone()

    def crear(self, nombre: str, password_hash: str, rol: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO usuarios (nombre, password, rol) VALUES (?, ?, ?)",
            (nombre, password_hash, rol),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def eliminar(self, uid: int) -> None:
        self.conn.execute("DELETE FROM usuarios WHERE id = ?", (uid,))
        self.conn.commit()

    def contar_admins(self) -> int:
        return int(self.conn.execute(
            "SELECT COUNT(*) FROM usuarios WHERE rol = ?", (config.ROL_ADMIN,)
        ).fetchone()[0])
