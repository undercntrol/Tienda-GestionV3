"""Usuarios y cuentas — HU-04 Usuarios · HU-07 Login y roles · HU-05 Fiar · HU-06 Saldos · HU-08 Cobrar.

    python -m unittest discover -s tests -v
"""

import unittest
from datetime import date

from apoyo import base_con_admin

from app import config, db, permisos
from app.errores import AccesoDenegado, DatoInvalido, Duplicado
from app.servicios_cuentas import ServicioCuentas
from app.servicios_usuarios import ServicioUsuarios
from app.servicios_ventas import ServicioVentas


class PruebasDeLogin(unittest.TestCase):
    """HU-04 y HU-07 · condición técnica 2."""

    def setUp(self):
        self.conn = db.conectar(":memory:")
        self.addCleanup(self.conn.close)
        self.usuarios = ServicioUsuarios(self.conn)

    def test_primera_vez_se_crea_el_administrador(self):
        self.assertFalse(self.usuarios.hay_usuarios())
        admin = self.usuarios.crear_primer_admin("dueno", "1234", "1234")
        self.assertEqual(admin.rol, config.ROL_ADMIN)
        with self.assertRaises(AccesoDenegado):
            self.usuarios.crear_primer_admin("otro", "1234", "1234")

    def test_claves_que_no_coinciden_o_cortas(self):
        with self.assertRaises(DatoInvalido):
            self.usuarios.crear_primer_admin("dueno", "1234", "4321")
        with self.assertRaises(DatoInvalido):
            self.usuarios.crear_primer_admin("dueno", "12", "12")

    def test_login_y_mismo_mensaje_si_falla(self):
        self.usuarios.crear_primer_admin("dueno", "1234", "1234")
        self.assertEqual(self.usuarios.autenticar("dueno", "1234").nombre, "dueno")
        with self.assertRaises(AccesoDenegado) as e1:
            self.usuarios.autenticar("dueno", "mala")
        with self.assertRaises(AccesoDenegado) as e2:
            self.usuarios.autenticar("nadie", "mala")
        self.assertEqual(str(e1.exception), str(e2.exception))

    def test_la_clave_no_se_guarda_en_texto(self):
        self.usuarios.crear_primer_admin("dueno", "1234", "1234")
        guardada = self.conn.execute("SELECT password FROM usuarios").fetchone()[0]
        self.assertNotIn("1234", guardada)
        self.assertIn("$", guardada)  # formato sal$hash, igual al producto final


class PruebasDeRoles(unittest.TestCase):
    def setUp(self):
        self.conn, self.admin, self.cajero = base_con_admin()
        self.addCleanup(self.conn.close)
        self.usuarios = ServicioUsuarios(self.conn)

    def test_permisos_del_cajero(self):
        self.assertTrue(permisos.puede(self.cajero, permisos.VENDER))
        self.assertTrue(permisos.puede(self.cajero, permisos.CUENTAS))
        self.assertTrue(permisos.puede(self.cajero, permisos.REPORTES))
        self.assertFalse(permisos.puede(self.cajero, permisos.CONFIGURACION))
        self.assertFalse(permisos.puede(self.cajero, permisos.CORREGIR_VENTAS))

    def test_cajero_no_crea_usuarios(self):
        with self.assertRaises(AccesoDenegado):
            self.usuarios.crear(self.cajero, "pepe", "1234", "cajero")

    def test_usuario_repetido(self):
        with self.assertRaises(Duplicado):
            self.usuarios.crear(self.admin, "ana", "1234", "cajero")

    def test_no_se_elimina_a_si_mismo_ni_al_ultimo_admin(self):
        with self.assertRaises(DatoInvalido):
            self.usuarios.eliminar(self.admin, self.admin.id)
        otro = self.usuarios.crear(self.admin, "jefe2", "1234", "administrador")
        self.usuarios.eliminar(otro, self.admin.id)  # quedan dos admins → se puede
        with self.assertRaises(DatoInvalido):
            # ahora 'jefe2' es el único admin y no se puede eliminar a sí mismo
            self.usuarios.eliminar(otro, otro.id)


class PruebasDeFiado(unittest.TestCase):
    """HU-05, HU-06 y HU-08."""

    def setUp(self):
        self.conn, self.admin, self.cajero = base_con_admin()
        self.addCleanup(self.conn.close)
        self.ventas = ServicioVentas(self.conn)
        self.cuentas = ServicioCuentas(self.conn)

    def _id(self, nombre):
        return self.conn.execute("SELECT id FROM clientes WHERE nombre = ?", (nombre,)).fetchone()[0]

    def test_fiar_a_un_pasajero_lo_crea_solo(self):
        v = self.ventas.registrar("Pan", "4800", cliente="Don Pedro")
        self.assertTrue(v.fiada)
        c = self.cuentas.obtener(self._id("Don Pedro"))
        self.assertEqual(c["tipo"], "pasajero")

    def test_lo_fiado_queda_pendiente_sin_metodo(self):
        v = self.ventas.registrar("Pan", "4800", "Efectivo", cliente="Don Pedro")
        fila = self.ventas.obtener(v.id)
        self.assertEqual((fila["pagada"], fila["metodo_id"], fila["fecha_pago"]), (0, None, None))
        self.assertEqual(self.cuentas.saldo(self._id("Don Pedro")), 4800.0)

    def test_cliente_fijo_y_nombre_reservado(self):
        self.cuentas.crear_cliente("Doña Rosa", "3001234567")
        with self.assertRaises(Duplicado):
            self.cuentas.crear_cliente("doña rosa")
        with self.assertRaises(DatoInvalido):
            self.cuentas.crear_cliente("cliente general")

    def test_cobrar_salda_todo_y_arma_el_comprobante(self):
        self.ventas.registrar("Pan", "4800", cliente="Doña Rosa", fecha="2026-10-01")
        self.ventas.registrar("Leche", "4200", cliente="Doña Rosa", fecha="2026-10-03")
        cid = self._id("Doña Rosa")
        cobro = self.cuentas.cobrar(cid, "Nequi", "2026-10-05")
        self.assertEqual((cobro.total, len(cobro.items), cobro.metodo), (9000.0, 2, "Nequi"))
        self.assertEqual(self.cuentas.saldo(cid), 0.0)
        html = ServicioCuentas.comprobante_html(cobro)
        self.assertIn("TOTAL PAGADO", html)
        self.assertIn("$9.000", html)

    def test_no_se_cobra_a_quien_no_debe_ni_sin_metodo(self):
        cid = self.cuentas.crear_cliente("Doña Rosa")
        with self.assertRaises(DatoInvalido):
            self.cuentas.cobrar(cid, "Efectivo")
        self.ventas.registrar("Pan", "500", cliente="Doña Rosa")
        with self.assertRaises(DatoInvalido):
            self.cuentas.cobrar(cid, "")

    def test_no_se_quita_a_quien_debe_y_se_conserva_el_historial(self):
        self.ventas.registrar("Pan", "500", cliente="Doña Rosa")
        cid = self._id("Doña Rosa")
        with self.assertRaises(DatoInvalido):
            self.cuentas.quitar_cliente(cid)
        self.cuentas.cobrar(cid, "Efectivo")
        self.assertFalse(self.cuentas.quitar_cliente(cid))  # tenía historial: se oculta
        self.assertEqual(self.cuentas.listar(), [])
        sin_historial = self.cuentas.crear_cliente("Nuevo")
        self.assertTrue(self.cuentas.quitar_cliente(sin_historial))  # se borra del todo

    def test_volver_a_fiar_a_un_cliente_oculto_lo_reactiva(self):
        self.ventas.registrar("Pan", "500", cliente="Doña Rosa")
        cid = self._id("Doña Rosa")
        self.cuentas.cobrar(cid, "Efectivo")
        self.cuentas.quitar_cliente(cid)
        self.ventas.registrar("Pan", "500", cliente="doña rosa")
        self.assertEqual([c["nombre"] for c in self.cuentas.listar()], ["Doña Rosa"])

    def test_total_por_cobrar_de_la_tienda(self):
        self.ventas.registrar("Pan", "500", cliente="A")
        self.ventas.registrar("Pan", "700", cliente="B")
        self.assertEqual(self.cuentas.total_por_cobrar(), 1200.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
