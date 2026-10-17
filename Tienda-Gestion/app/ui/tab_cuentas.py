"""Pestaña Cuentas (fiado).

HU-05 Clientes a los que se fía · HU-06 Saldos y movimientos · HU-08 Cobrar la cuenta con comprobante.
"""

from __future__ import annotations

import tkinter as tk
import webbrowser
from datetime import date
from tkinter import messagebox, ttk

from .. import config as C
from ..errores import ErrorDeNegocio
from ..formato import fmt_money
from .estilo import limpiar, rayar, tabla
from .widgets import campo_fecha, dialogo_campos


class TabCuentas:
    def __init__(self, cont: ttk.Frame, app):
        self.cont = cont
        self.app = app
        self.root = app.root
        self._construir()

    def _construir(self):
        cont = self.cont
        ttk.Label(cont, text="Cuentas de clientes (fiado)", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(cont, text="Crea clientes para fiarles. En una venta, elige el cliente (o escribe "
                             "un nombre nuevo para un pasajero) y la venta queda en su cuenta hasta "
                             "que la cobres aquí.", style="Sub.TLabel", foreground="#555"
                  ).pack(anchor="w", pady=(0, 8))

        alta = ttk.LabelFrame(cont, text=" Nuevo cliente ", padding=10)
        alta.pack(fill="x", pady=4)
        ttk.Label(alta, text="Nombre:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.ent_nombre = ttk.Entry(alta, width=24)
        self.ent_nombre.grid(row=0, column=1, sticky="w", padx=4, pady=4)
        ttk.Label(alta, text="Teléfono:").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        self.ent_tel = ttk.Entry(alta, width=18)
        self.ent_tel.grid(row=0, column=3, sticky="w", padx=4, pady=4)
        ttk.Button(alta, text="➕ Agregar cliente", style="Accent.TButton",
                   command=self.agregar).grid(row=0, column=4, padx=8)

        ttk.Label(cont, text="Clientes y lo que deben", style="Sub.TLabel").pack(anchor="w", pady=(12, 2))
        self.tree = tabla(cont, [
            ("nombre", "Cliente", 220, "w"), ("tel", "Teléfono", 130, "w"),
            ("tipo", "Tipo", 90, "center"), ("pendientes", "Ítems", 70, "center"),
            ("saldo", "Debe", 130, "e")], height=12)
        self.tree.tag_configure("debe", foreground=C.COLOR_FIADO)

        barra = ttk.Frame(cont)
        barra.pack(side="bottom", fill="x", pady=(6, 0))
        ttk.Button(barra, text="📋 Ver movimientos", command=self.ver_movimientos).pack(side="left", padx=2)
        ttk.Button(barra, text="💵 Cobrar cuenta", style="Accent.TButton",
                   command=self.cobrar).pack(side="left", padx=2)
        ttk.Button(barra, text="✏ Editar", command=self.editar).pack(side="left", padx=2)
        ttk.Button(barra, text="🗑 Quitar", command=self.quitar).pack(side="left", padx=2)
        self.lbl_total = ttk.Label(barra, text="Por cobrar: $0", style="Total.TLabel",
                                   foreground=C.COLOR_FIADO)
        self.lbl_total.pack(side="right", padx=6)
        self.tree.pack(side="top", fill="both", expand=True, pady=(2, 6))

    def refrescar(self):
        limpiar(self.tree)
        total = 0.0
        for c in self.app.cuentas.con_saldo():
            total += c["saldo"]
            self.tree.insert("", "end", iid=c["id"], tags=("debe",) if c["saldo"] > 0 else (),
                             values=(c["nombre"], c["telefono"] or "—", c["tipo"].capitalize(),
                                     c["pendientes"] or 0, fmt_money(c["saldo"])))
        rayar(self.tree)
        self.lbl_total.config(text=f"Total por cobrar: {fmt_money(total)}")

    def _seleccion(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sin selección", "Selecciona un cliente.")
            return None
        return int(sel[0])

    def agregar(self):
        try:
            self.app.cuentas.crear_cliente(self.ent_nombre.get(), self.ent_tel.get())
        except ErrorDeNegocio as error:
            messagebox.showwarning("Revisa el cliente", str(error))
            return
        self.ent_nombre.delete(0, "end")
        self.ent_tel.delete(0, "end")
        self.app.refrescar_todo()

    def editar(self):
        cid = self._seleccion()
        if cid is None:
            return
        cli = self.app.cuentas.obtener(cid)

        def guardar(nombre, tel):
            self.app.cuentas.editar_cliente(cid, nombre, tel)
            self.app.refrescar_todo()

        dialogo_campos(self.root, "Editar cliente",
                       [("Nombre:", cli["nombre"], False), ("Teléfono:", cli["telefono"] or "", False)],
                       guardar)

    def quitar(self):
        cid = self._seleccion()
        if cid is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Quitar este cliente de la lista?\n"
                                   "Si tiene historial, se conserva pero deja de aparecer."):
            return
        try:
            self.app.cuentas.quitar_cliente(cid)
        except ErrorDeNegocio as error:
            messagebox.showwarning("No se puede quitar", str(error))
            return
        self.app.refrescar_todo()

    def ver_movimientos(self):
        cid = self._seleccion()
        if cid is None:
            return
        cli = self.app.cuentas.obtener(cid)
        dlg = tk.Toplevel(self.root)
        dlg.title(f"Movimientos de {cli['nombre']}")
        dlg.transient(self.root)
        dlg.geometry("520x440")
        cont = ttk.Frame(dlg, padding=12)
        cont.pack(fill="both", expand=True)
        ttk.Label(cont, text=f"Cuenta de {cli['nombre']}", style="Titulo.TLabel").pack(anchor="w")
        tree = tabla(cont, [("fecha", "Fecha", 90, "center"), ("producto", "Producto", 200, "w"),
                            ("estado", "Estado", 90, "center"), ("monto", "Monto", 110, "e")], height=14)
        tree.pack(fill="both", expand=True, pady=8)
        pendiente = 0.0
        for r in self.app.cuentas.movimientos(cid):
            if not r["pagada"]:
                pendiente += r["monto"]
            tree.insert("", "end", values=(r["fecha"], r["producto"],
                                           "Pagada" if r["pagada"] else "Pendiente",
                                           fmt_money(r["monto"])))
        ttk.Label(cont, text=f"Saldo pendiente: {fmt_money(pendiente)}", style="Total.TLabel",
                  foreground=C.COLOR_FIADO).pack(anchor="e")

    def cobrar(self):
        cid = self._seleccion()
        if cid is None:
            return
        cli = self.app.cuentas.obtener(cid)
        saldo = self.app.cuentas.saldo(cid)
        if saldo <= 0:
            messagebox.showinfo("Sin saldo", f"{cli['nombre']} no tiene nada pendiente por cobrar.")
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Cobrar cuenta")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.resizable(False, False)
        c = ttk.Frame(dlg, padding=16)
        c.pack()
        ttk.Label(c, text=f"Cobrar la cuenta de {cli['nombre']}", style="Sub.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        ttk.Label(c, text="Total a cobrar:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(c, text=fmt_money(saldo), style="Total.TLabel",
                  foreground=C.COLOR_TEXTO_VERDE).grid(row=1, column=1, sticky="w", pady=4)
        ttk.Label(c, text="Pago con:").grid(row=2, column=0, sticky="w", pady=4)
        metodos = list(self.app.metodo_map)
        cmb = ttk.Combobox(c, values=metodos, width=20, state="readonly")
        cmb.set("Efectivo" if "Efectivo" in metodos else (metodos[0] if metodos else ""))
        cmb.grid(row=2, column=1, sticky="w", pady=4)
        ttk.Label(c, text="Fecha del pago:").grid(row=3, column=0, sticky="w", pady=4)
        cf, ent_fecha = campo_fecha(c, self.root, date.today().isoformat())
        cf.grid(row=3, column=1, sticky="w", pady=4)

        def confirmar():
            try:
                cobro = self.app.cuentas.cobrar(cid, cmb.get(), ent_fecha.get())
            except ErrorDeNegocio as error:
                messagebox.showwarning("Revisa el cobro", str(error), parent=dlg)
                return
            dlg.destroy()
            try:
                ruta = self.app.cuentas.guardar_comprobante(cobro)
                webbrowser.open(ruta.as_uri())
            except OSError:
                pass  # el cobro ya quedó; el comprobante es un extra
            self.app.refrescar_todo()
            messagebox.showinfo("Cuenta cobrada", f"Se cobró {fmt_money(cobro.total)} a {cobro.cliente}.")

        ttk.Button(c, text="Confirmar cobro", style="Accent.TButton", command=confirmar).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
