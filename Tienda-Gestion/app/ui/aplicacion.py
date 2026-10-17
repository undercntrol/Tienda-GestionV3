"""Ventana principal: encabezado y pestañas según el rol del usuario.

Cada pestaña vive en su propio archivo (tab_*.py). Esta clase arma el
contexto compartido (servicios, usuario, listas de productos, métodos y
clientes) y refresca todas las pestañas cuando algo cambia.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .. import config as C
from .. import permisos
from ..modelos import Usuario
from ..servicios_catalogo import ServicioCatalogo
from ..servicios_cuentas import ServicioCuentas
from ..servicios_reportes import ServicioReportes
from ..servicios_usuarios import ServicioUsuarios
from ..servicios_ventas import ServicioVentas
from .estilo import configurar_estilo
from .tab_config import TabConfiguracion
from .tab_cuentas import TabCuentas
from .tab_reportes import TabReportes
from .tab_ventas import TabVentas


class Aplicacion:
    def __init__(self, root: tk.Tk, conn, usuario: Usuario, al_cerrar_sesion):
        self.root = root
        self.conn = conn
        self.usuario = usuario
        self.es_admin = usuario.rol == C.ROL_ADMIN
        self.al_cerrar_sesion = al_cerrar_sesion

        # Servicios compartidos por todas las pestañas
        self.catalogo = ServicioCatalogo(conn)
        self.ventas = ServicioVentas(conn)
        self.cuentas = ServicioCuentas(conn)
        self.reportes = ServicioReportes(conn)
        self.usuarios = ServicioUsuarios(conn)

        # Listas que usan los combos (se llenan en refrescar_todo)
        self.prod_map: dict[str, dict] = {}
        self.prod_por_id: dict[int, dict] = {}
        self.metodo_map: dict[str, int] = {}
        self.metodo_por_id: dict[int, str] = {}
        self.cliente_map: dict[str, int] = {}

        root.title(f"{C.APP_NOMBRE} — Gestión")
        configurar_estilo(root)
        self._encabezado()

        self.notebook = ttk.Notebook(root)
        self.pestanas = []
        for clase, texto, permiso in (
            (TabVentas, "  🛒  Ventas  ", permisos.VENDER),
            (TabCuentas, "  👥  Cuentas  ", permisos.CUENTAS),
            (TabReportes, "  📄  Reportes  ", permisos.REPORTES),
            (TabConfiguracion, "  ⚙  Configuración  ", permisos.CONFIGURACION),
        ):
            if permisos.puede(usuario, permiso):
                frame = ttk.Frame(self.notebook, padding=10)
                self.notebook.add(frame, text=texto)
                self.pestanas.append(clase(frame, self))
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        self.refrescar_todo()

    def _encabezado(self):
        self.header = tk.Frame(self.root, bg=C.COLOR_HEADER)
        self.header.pack(fill="x")
        ses = tk.Frame(self.header, bg=C.COLOR_HEADER)
        ses.pack(side="right", padx=12)
        rol_txt = "Administrador" if self.es_admin else "Cajero"
        tk.Label(ses, text=f"👤 {self.usuario.nombre} · {rol_txt}", bg=C.COLOR_HEADER,
                 fg=C.COLOR_HEADER_TXT, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8))
        tk.Button(ses, text="Cerrar sesión", command=self.cerrar_sesion, relief="flat",
                  bg=C.COLOR_TEXTO_VERDE, fg="white", font=("Segoe UI", 9, "bold"),
                  padx=10, cursor="hand2").pack(side="left")
        tk.Label(self.header, text="🏪", bg=C.COLOR_HEADER, fg=C.COLOR_HEADER_TXT,
                 font=("Segoe UI Emoji", 17)).pack(side="left", padx=(14, 0), pady=8)
        titulo = tk.Frame(self.header, bg=C.COLOR_HEADER)
        titulo.pack(side="left", padx=(6, 14), pady=6)
        tk.Label(titulo, text=C.APP_NOMBRE, bg=C.COLOR_HEADER, fg=C.COLOR_HEADER_TXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(titulo, text="Gestión de ventas", bg=C.COLOR_HEADER, fg=C.COLOR_HEADER_SUB,
                 font=("Segoe UI", 8)).pack(anchor="w")

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar la sesión actual?"):
            self.root.unbind("<Return>")
            self.al_cerrar_sesion()

    def refrescar_todo(self):
        """Recarga las listas compartidas y avisa a cada pestaña."""
        productos = self.catalogo.listar()
        metodos = self.ventas.metodos_pago()
        self.prod_map = {p["nombre"]: {"id": p["id"], "precio": p["precio"]} for p in productos}
        self.prod_por_id = {p["id"]: {"nombre": p["nombre"], "precio": p["precio"]} for p in productos}
        self.metodo_map = {m["nombre"]: m["id"] for m in metodos}
        self.metodo_por_id = {m["id"]: m["nombre"] for m in metodos}
        self.cliente_map = {c["nombre"]: c["id"] for c in self.cuentas.listar()}
        for pestana in self.pestanas:
            pestana.refrescar()

    @staticmethod
    def set_combo(cmb: ttk.Combobox, valores, defecto):
        """Cambia las opciones de un combo conservando la selección si sigue existiendo."""
        actual = cmb.get()
        cmb["values"] = valores
        cmb.set(actual if actual in valores else defecto)
