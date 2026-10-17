"""Consultas y reportes — HU-02 Consultar · HU-07 Corregir · HU-03/HU-09 Reportes · HU-10 Importar CSV.

    python -m unittest discover -s tests -v
"""

import tempfile
import unittest
import zipfile
from pathlib import Path

from apoyo import base_con_admin

from app.errores import AccesoDenegado, DatoInvalido, NoEncontrado
from app.servicios_catalogo import ServicioCatalogo
from app.servicios_cuentas import ServicioCuentas
from app.servicios_reportes import ServicioReportes, periodo
from app.servicios_ventas import ServicioVentas


class Base(unittest.TestCase):
    def setUp(self):
        self.conn, self.admin, self.cajero = base_con_admin()
        self.addCleanup(self.conn.close)
        self.ventas = ServicioVentas(self.conn)
        v = self.ventas
        v.registrar("Gaseosa", "2500", "Efectivo", fecha="2026-10-01")
        v.registrar("Pan", "4800", "Nequi", fecha="2026-10-05")
        v.registrar("Gaseosa", "5000", cliente="Doña Rosa", fecha="2026-10-10")  # fiada
        v.registrar("Pan", "4800", "Efectivo", fecha="2026-09-20")
        self.ids = {n: i for n, i in self.conn.execute("SELECT nombre, id FROM productos")}
        self.metodos = {n: i for n, i in self.conn.execute("SELECT nombre, id FROM metodos_pago")}

    def rosa(self):
        return self.conn.execute("SELECT id FROM clientes WHERE nombre='Doña Rosa'").fetchone()[0]


class PruebasDeConsulta(Base):
    """HU-02 · condición técnica 4."""

    def test_rango_incluye_ambos_extremos(self):
        filas, total = self.ventas.listar("2026-10-01", "2026-10-05")
        self.assertEqual((len(filas), total), (2, 7300.0))

    def test_fechas_al_reves_se_voltean(self):
        self.assertEqual(len(self.ventas.listar("2026-10-31", "2026-10-01")[0]), 3)

    def test_filtros_combinables(self):
        filas, _ = self.ventas.listar("2026-09-01", "2026-10-31", producto_id=self.ids["Pan"],
                                      metodo_id=self.metodos["Efectivo"])
        self.assertEqual([f["fecha"] for f in filas], ["2026-09-20"])

    def test_filtro_por_cliente_y_solo_contado(self):
        filas, _ = self.ventas.listar("2026-09-01", "2026-10-31", cliente_id=self.rosa())
        self.assertEqual([f["cliente"] for f in filas], ["Doña Rosa"])
        contado, _ = self.ventas.listar("2026-09-01", "2026-10-31",
                                        cliente_id=ServicioVentas.SOLO_CONTADO)
        self.assertEqual(len(contado), 3)
        self.assertTrue(all(f["cliente"] == "Cliente general" for f in contado))

    def test_sin_resultados_no_falla(self):
        self.assertEqual(self.ventas.listar("2020-01-01", "2020-01-31"), ([], 0))

    def test_fecha_invalida(self):
        with self.assertRaises(DatoInvalido):
            self.ventas.listar("hoy", "2026-10-31")


class PruebasDeCorreccion(Base):
    """HU-07 · solo el administrador corrige."""

    def test_editar_venta_de_contado_mueve_tambien_la_fecha_de_pago(self):
        tid = self.ventas.listar("2026-10-01", "2026-10-01")[0][0]["id"]
        self.ventas.editar(self.admin, tid, "Gaseosa", "Nequi", "$3.000", "2026-10-02")
        f = self.ventas.obtener(tid)
        self.assertEqual((f["monto"], f["metodo"], f["fecha"], f["fecha_pago"]),
                         (3000.0, "Nequi", "2026-10-02", "2026-10-02"))

    def test_cajero_no_edita_ni_elimina(self):
        tid = self.ventas.listar("2026-10-01", "2026-10-01")[0][0]["id"]
        with self.assertRaises(AccesoDenegado):
            self.ventas.editar(self.cajero, tid, "Gaseosa", "Efectivo", "1", "2026-10-01")
        with self.assertRaises(AccesoDenegado):
            self.ventas.eliminar(self.cajero, tid)

    def test_eliminar(self):
        tid = self.ventas.listar("2026-10-01", "2026-10-01")[0][0]["id"]
        self.ventas.eliminar(self.admin, tid)
        with self.assertRaises(NoEncontrado):
            self.ventas.obtener(tid)


class PruebasDeReportes(Base):
    """HU-03 y HU-09."""

    def test_periodos(self):
        def rango(p):
            return p.ini, p.fin
        self.assertEqual(rango(periodo("Día", "2026-10-17")), ("2026-10-17", "2026-10-17"))
        self.assertEqual(rango(periodo("Semana", "2026-10-17")), ("2026-10-12", "2026-10-18"))
        self.assertEqual(rango(periodo("Mes", mes="Febrero", anio=2028)), ("2028-02-01", "2028-02-29"))
        with self.assertRaises(DatoInvalido):
            periodo("Año", "2026-10-17")

    def test_lo_fiado_no_es_ingreso_hasta_que_se_cobra(self):
        rep = ServicioReportes(self.conn)
        octubre = periodo("Mes", mes="Octubre", anio=2026)
        self.assertEqual(rep.generar(octubre).ingresos, 7300.0)  # sin la fiada
        ServicioCuentas(self.conn).cobrar(self.rosa(), "Daviplata", "2026-10-15")
        r = rep.generar(octubre)
        self.assertEqual(r.ingresos, 12300.0)
        self.assertIn(("2026-10-15", 5000.0), r.por_dia)  # entra el día del cobro
        self.assertIn(("Daviplata", 5000.0), r.por_metodo)

    def test_por_producto_de_mayor_a_menor(self):
        r = ServicioReportes(self.conn).generar(periodo("Mes", mes="Octubre", anio=2026))
        self.assertEqual(r.por_producto[0][0], "Pan")

    def test_filtro_por_metodo(self):
        r = ServicioReportes(self.conn).generar(periodo("Mes", mes="Octubre", anio=2026),
                                                metodo_id=self.metodos["Nequi"])
        self.assertEqual(r.ingresos, 4800.0)

    def test_exporta_html_y_excel(self):
        servicio = ServicioReportes(self.conn)
        r = servicio.generar(periodo("Mes", mes="Octubre", anio=2026))
        with tempfile.TemporaryDirectory() as carpeta:
            html = servicio.guardar_html(r, carpeta).read_text(encoding="utf-8")
            self.assertIn("Ingresos totales: $7.300", html)
            xlsx = servicio.guardar_excel(r, carpeta)
            with zipfile.ZipFile(xlsx) as z:
                self.assertIn("xl/worksheets/sheet5.xml", z.namelist())
                self.assertIn("Pan", z.read("xl/worksheets/sheet2.xml").decode())


class PruebasDeImportacion(unittest.TestCase):
    """HU-10 · condición técnica 3 (archivo externo)."""

    def setUp(self):
        self.conn, self.admin, self.cajero = base_con_admin()
        self.addCleanup(self.conn.close)
        self.cat = ServicioCatalogo(self.conn)
        self.dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.dir.cleanup()

    def archivo(self, texto, encoding="utf-8"):
        ruta = Path(self.dir.name) / "lista.csv"
        ruta.write_text(texto, encoding=encoding)
        return ruta

    def test_crea_y_actualiza(self):
        self.cat.crear(self.admin, "Gaseosa", "2500")
        r = self.cat.importar_csv(self.admin, self.archivo("nombre;precio\ngaseosa;2.800\nPan;$ 4.800\n"))
        self.assertEqual((r.creados, r.actualizados, r.errores), (1, 1, []))
        self.assertEqual({p["nombre"]: p["precio"] for p in self.cat.listar()},
                         {"Gaseosa": 2800.0, "Pan": 4800.0})

    def test_comas_sin_encabezado_y_latin1(self):
        r = self.cat.importar_csv(self.admin, self.archivo("Café,1500\nHuevo,600\n", "latin-1"))
        self.assertEqual(r.creados, 2)
        self.assertIn("Café", [p["nombre"] for p in self.cat.listar()])

    def test_lineas_malas_se_reportan_y_no_detienen(self):
        r = self.cat.importar_csv(self.admin, self.archivo("Arepa;1500\nHuevo;abc\nSolo\nLeche;0\n"))
        self.assertEqual((r.creados, len(r.errores)), (1, 3))
        self.assertTrue(r.errores[0].startswith("Línea 2"))

    def test_archivo_vacio_inexistente_o_cajero(self):
        with self.assertRaises(DatoInvalido):
            self.cat.importar_csv(self.admin, self.archivo("  \n"))
        with self.assertRaises(NoEncontrado):
            self.cat.importar_csv(self.admin, Path(self.dir.name) / "no.csv")
        with self.assertRaises(AccesoDenegado):
            self.cat.importar_csv(self.cajero, self.archivo("Pan;500\n"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
