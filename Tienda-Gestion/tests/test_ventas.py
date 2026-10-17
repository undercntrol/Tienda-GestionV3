"""Ventas — HU-01 Registrar venta · HU-02 Ventas del día · HU-10 Productos · persistencia.

    python -m unittest discover -s tests -v
"""

import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

from apoyo import base_con_admin

from app import config, db
from app.errores import AccesoDenegado, DatoInvalido, Duplicado
from app.formato import fmt_money, parse_numero
from app.servicios_catalogo import ServicioCatalogo
from app.servicios_ventas import ServicioVentas


class PruebasDeFormato(unittest.TestCase):
    def test_dinero_en_formato_colombiano(self):
        self.assertEqual(fmt_money(2500), "$2.500")
        self.assertEqual(fmt_money(1234567), "$1.234.567")

    def test_lee_lo_que_escribe_el_tendero(self):
        for texto in ("2500", "2.500", "$ 2.500", "$2.500"):
            self.assertEqual(parse_numero(texto), 2500.0, texto)
        self.assertEqual(parse_numero(""), 0.0)


class PruebasDeProductos(unittest.TestCase):
    """HU-10 (administración de productos)."""

    def setUp(self):
        self.conn, self.admin, self.cajero = base_con_admin()
        self.addCleanup(self.conn.close)
        self.cat = ServicioCatalogo(self.conn)

    def test_crear_con_y_sin_precio(self):
        self.cat.crear(self.admin, "Gaseosa", "$2.500")
        self.cat.crear(self.admin, "Bolsa")  # el precio es opcional
        precios = {p["nombre"]: p["precio"] for p in self.cat.listar()}
        self.assertEqual(precios, {"Bolsa": 0.0, "Gaseosa": 2500.0})

    def test_no_duplica_aunque_cambien_las_mayusculas(self):
        self.cat.crear(self.admin, "Gaseosa")
        with self.assertRaises(Duplicado):
            self.cat.crear(self.admin, "GASEOSA")

    def test_nombre_vacio_o_precio_con_letras(self):
        with self.assertRaises(DatoInvalido):
            self.cat.crear(self.admin, "   ")
        with self.assertRaises(DatoInvalido):
            self.cat.crear(self.admin, "Pan", "dos mil")

    def test_eliminar_conserva_las_ventas(self):
        pid = self.cat.crear(self.admin, "Chicle", "300")
        ventas = ServicioVentas(self.conn)
        ventas.registrar("Chicle", "300", "Efectivo")
        self.cat.eliminar(self.admin, pid)
        filas, total = ventas.del_dia()
        self.assertEqual((filas[0]["producto"], total), ("(eliminado)", 300.0))

    def test_cajero_no_administra_productos(self):
        with self.assertRaises(AccesoDenegado):
            self.cat.crear(self.cajero, "Pan", "500")


class PruebasDeVentas(unittest.TestCase):
    """HU-01 y HU-02."""

    def setUp(self):
        self.conn, self.admin, self.cajero = base_con_admin()
        self.addCleanup(self.conn.close)
        self.ventas = ServicioVentas(self.conn)

    def test_venta_de_contado_queda_pagada_hoy(self):
        v = self.ventas.registrar("Gaseosa", "$2.500", "Efectivo")
        self.assertFalse(v.fiada)
        fila = self.ventas.obtener(v.id)
        self.assertEqual((fila["pagada"], fila["fecha"], fila["fecha_pago"]),
                         (1, date.today().isoformat(), date.today().isoformat()))

    def test_producto_y_metodo_nuevos_se_crean_solos(self):
        self.ventas.registrar("Empanada", "2000", "Bancolombia")
        self.assertEqual(self.ventas.precio_sugerido("empanada"), 2000.0)
        nombres = [m["nombre"] for m in self.ventas.metodos_pago()]
        self.assertIn("Bancolombia", nombres)

    def test_no_duplica_producto_escrito_distinto(self):
        self.ventas.registrar("Gaseosa", "2500", "Efectivo")
        self.ventas.registrar("gaseosa", "2500", "Efectivo")
        n = self.conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
        self.assertEqual(n, 1)

    def test_validaciones(self):
        for producto, monto, metodo in (("", "100", "Efectivo"), ("Pan", "", "Efectivo"),
                                        ("Pan", "0", "Efectivo"), ("Pan", "500", "")):
            with self.assertRaises(DatoInvalido):
                self.ventas.registrar(producto, monto, metodo)

    def test_fecha_elegida_en_el_calendario(self):
        v = self.ventas.registrar("Pan", "500", "Efectivo", fecha="2026-10-01")
        self.assertEqual(v.fecha, "2026-10-01")
        with self.assertRaises(DatoInvalido):
            self.ventas.registrar("Pan", "500", "Efectivo", fecha="31/02/2026")

    def test_ventas_del_dia_con_total(self):
        self.ventas.registrar("Gaseosa", "2500", "Efectivo")
        self.ventas.registrar("Pan", "4800", "Nequi")
        self.ventas.registrar("Pan", "4800", "Nequi", fecha="2026-01-01")  # otro día
        filas, total = self.ventas.del_dia()
        self.assertEqual((len(filas), total), (2, 7300.0))

    def test_metodos_de_pago_vienen_sembrados(self):
        nombres = {m["nombre"] for m in self.ventas.metodos_pago()}
        self.assertTrue(set(config.METODOS_PAGO_INICIALES) <= nombres)


class PruebasDePersistencia(unittest.TestCase):
    """Condición técnica 1: los datos sobreviven al cierre."""

    def test_los_datos_siguen_ahi_despues_de_cerrar(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "tienda.db"
            conn = db.conectar(ruta)
            ServicioVentas(conn).registrar("Arepa", "1500", "Efectivo")
            conn.close()
            conn = db.conectar(ruta)
            self.assertEqual(ServicioVentas(conn).del_dia()[1], 1500.0)
            conn.close()

    def test_base_de_la_version_0_1_se_migra_sin_perder_ventas(self):
        """La 0.1 guardaba fecha con hora y no tenía columnas de fiado."""
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "vieja.db"
            vieja = sqlite3.connect(ruta)
            vieja.executescript("""
                CREATE TABLE productos (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE, precio REAL NOT NULL DEFAULT 0,
                    activo INTEGER NOT NULL DEFAULT 1);
                CREATE TABLE metodos_pago (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE);
                CREATE TABLE transacciones (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id INTEGER, metodo_id INTEGER,
                    cantidad INTEGER NOT NULL DEFAULT 1, monto REAL NOT NULL, fecha TEXT NOT NULL);
                INSERT INTO productos (nombre, precio) VALUES ('Pan', 500);
                INSERT INTO metodos_pago (nombre) VALUES ('Efectivo');
                INSERT INTO transacciones (producto_id, metodo_id, monto, fecha)
                     VALUES (1, 1, 500, '2026-09-12 10:15:00');""")
            vieja.commit()
            vieja.close()
            conn = db.conectar(ruta)
            fila = conn.execute("SELECT fecha, pagada, fecha_pago FROM transacciones").fetchone()
            self.assertEqual(tuple(fila), ("2026-09-12", 1, "2026-09-12"))
            conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
