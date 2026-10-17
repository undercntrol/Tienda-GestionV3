"""Pestaña Ventas.

HU-01 Registrar venta · HU-05 Fiar (cliente distinto de "Cliente general")
HU-02 Lista de ventas con filtros · HU-07 Editar y eliminar (solo administrador).
"""

from __future__ import annotations

import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from .. import config as C
from .. import permisos
from ..errores import ErrorDeNegocio
from ..formato import dia_semana, fmt_money, fmt_money_entry
from .estilo import limpiar, rayar, tabla
from .widgets import (CalendarioPopup, autocompletar, caja_dinero, campo_fecha,
                      dialogo_campos, poner_fecha, sin_resaltado)

TODOS = "Todos"


class TabVentas:
    def __init__(self, cont: ttk.Frame, app):
        self.cont = cont
        self.app = app
        self.root = app.root
        self.puede_corregir = permisos.puede(app.usuario, permisos.CORREGIR_VENTAS)
        self._fecha_venta = date.today().isoformat()
        self._formulario()
        self._lista()

    # ================= formulario de registro (HU-01 / HU-05) =================
    def _formulario(self):
        form = ttk.LabelFrame(self.cont, text=" Registrar venta ", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Producto:").grid(row=0, column=0, sticky="w", padx=4, pady=6)
        self.cmb_producto = ttk.Combobox(form, width=24)  # editable: permite escribir nuevos
        self.cmb_producto.grid(row=0, column=1, sticky="w", padx=4, pady=6)
        self.cmb_producto.bind("<<ComboboxSelected>>", lambda _e: self._producto_elegido())
        autocompletar(self.root, self.cmb_producto, lambda: list(self.app.prod_map),
                      on_select=self._producto_elegido)

        ttk.Label(form, text="Monto:").grid(row=0, column=2, sticky="w", padx=4, pady=6)
        self.ent_monto = ttk.Entry(form, width=14)
        self.ent_monto.grid(row=0, column=3, sticky="w", padx=4, pady=6)
        caja_dinero(self.ent_monto)

        ttk.Label(form, text="Pago:").grid(row=0, column=4, sticky="w", padx=4, pady=6)
        self.cmb_metodo = ttk.Combobox(form, width=14)  # editable: métodos nuevos al vuelo
        self.cmb_metodo.grid(row=0, column=5, sticky="w", padx=4, pady=6)

        self.btn_registrar = ttk.Button(form, text="➕  Registrar venta", style="Accent.TButton",
                                        command=self.registrar)
        self.btn_registrar.grid(row=0, column=6, padx=8, pady=6)

        ttk.Label(form, text="Cliente:").grid(row=1, column=0, sticky="w", padx=4, pady=6)
        self.cmb_cliente = ttk.Combobox(form, width=24)  # editable: crea pasajeros al vuelo
        self.cmb_cliente.set(C.CLIENTE_GENERAL)
        self.cmb_cliente.grid(row=1, column=1, sticky="w", padx=4, pady=6)
        self.cmb_cliente.bind("<<ComboboxSelected>>", lambda _e: self._cliente_cambiado())
        autocompletar(self.root, self.cmb_cliente,
                      lambda: [C.CLIENTE_GENERAL] + list(self.app.cliente_map),
                      on_select=self._cliente_cambiado)

        # La fecha es un botón (casi nunca se cambia y así Tab no se detiene ahí)
        ttk.Label(form, text="Fecha:").grid(row=1, column=2, sticky="w", padx=4, pady=6)
        self.btn_fecha = ttk.Button(form, width=18, takefocus=False, command=self._elegir_fecha)
        self.btn_fecha.grid(row=1, column=3, columnspan=2, sticky="w", padx=4, pady=6)
        self._refrescar_btn_fecha()

        ttk.Label(form, foreground="gray",
                  text="Producto nuevo: se guarda solo. Cliente distinto de «Cliente general» = "
                       "fiado (se cobra después en la pestaña Cuentas). Enter registra la venta."
                  ).grid(row=2, column=0, columnspan=9, sticky="w", padx=4, pady=(4, 0))

        def enter_registra(_e=None):
            self.registrar()
            return "break"
        for w in (self.ent_monto, self.cmb_metodo, self.btn_registrar):
            w.bind("<Return>", enter_registra)
        for w in (self.cmb_producto, self.cmb_cliente):  # después del autocompletar
            w.bind("<Return>", enter_registra, add="+")
        for w in (self.cmb_producto, self.ent_monto, self.cmb_metodo, self.cmb_cliente,
                  self.btn_registrar):
            w.lift()  # orden del Tab según lo que se ve
        for w in (self.cmb_producto, self.ent_monto, self.cmb_metodo, self.cmb_cliente):
            sin_resaltado(w)

    def _cliente_cambiado(self):
        if self.cmb_cliente.get().strip().lower() in (C.CLIENTE_GENERAL.lower(), ""):
            self.cmb_metodo.configure(state="normal")
            if not self.cmb_metodo.get().strip() and self.app.metodo_map:
                nombres = list(self.app.metodo_map)
                self.cmb_metodo.set("Efectivo" if "Efectivo" in nombres else nombres[0])
        else:
            # Fiado: el método de pago se define al cobrar la cuenta
            self.cmb_metodo.set("")
            self.cmb_metodo.configure(state="disabled")

    def _refrescar_btn_fecha(self):
        d = date.fromisoformat(self._fecha_venta)
        texto = "📅 Hoy" if d == date.today() else f"📅 {d.day} {C.MESES[d.month - 1][:3]} {d.year}"
        self.btn_fecha.config(text=texto)

    def _elegir_fecha(self):
        def elegido(d):
            self._fecha_venta = d.isoformat()
            self._refrescar_btn_fecha()
        CalendarioPopup(self.root, date.fromisoformat(self._fecha_venta), elegido,
                        anchor=self.btn_fecha)

    def _producto_elegido(self):
        """Autocompleta el precio y pasa al monto."""
        info = self.app.prod_map.get(self.cmb_producto.get().strip())
        if info and info["precio"] > 0 and not self.ent_monto.get().strip():
            self.ent_monto.insert(0, fmt_money_entry(info["precio"]))
        self.ent_monto.focus_set()
        self.ent_monto.icursor("end")

    def registrar(self):
        try:
            self.app.ventas.registrar(
                producto=self.cmb_producto.get(), monto=self.ent_monto.get(),
                metodo=self.cmb_metodo.get(), cliente=self.cmb_cliente.get(),
                fecha=self._fecha_venta)
        except ErrorDeNegocio as error:
            messagebox.showwarning("Revisa la venta", str(error))
            return
        # Listo para la siguiente: la mayoría de ventas son de contado y de hoy
        self.cmb_producto.set("")
        self.ent_monto.delete(0, "end")
        self.cmb_cliente.set(C.CLIENTE_GENERAL)
        self._cliente_cambiado()
        self._fecha_venta = date.today().isoformat()
        self._refrescar_btn_fecha()
        self.app.refrescar_todo()
        self.cmb_producto.focus_set()

    # ================= lista de ventas (HU-02 / HU-07) =================
    def _lista(self):
        ttk.Label(self.cont, text="Ventas registradas", style="Titulo.TLabel").pack(
            anchor="w", pady=(14, 2))
        filtros = ttk.Frame(self.cont)
        filtros.pack(fill="x", pady=4)
        hoy = date.today().isoformat()
        ttk.Label(filtros, text="Desde:").pack(side="left", padx=(0, 2))
        cf, self.ent_desde = campo_fecha(filtros, self.root, hoy)
        cf.pack(side="left", padx=(0, 8))
        ttk.Label(filtros, text="Hasta:").pack(side="left", padx=(0, 2))
        cf, self.ent_hasta = campo_fecha(filtros, self.root, hoy)
        cf.pack(side="left", padx=(0, 8))
        ttk.Label(filtros, text="Producto:").pack(side="left", padx=(0, 2))
        self.cmb_f_producto = ttk.Combobox(filtros, state="readonly", width=16)
        self.cmb_f_producto.pack(side="left", padx=(0, 8))
        ttk.Label(filtros, text="Pago:").pack(side="left", padx=(0, 2))
        self.cmb_f_metodo = ttk.Combobox(filtros, state="readonly", width=12)
        self.cmb_f_metodo.pack(side="left", padx=(0, 8))
        ttk.Label(filtros, text="Cliente:").pack(side="left", padx=(0, 2))
        self.cmb_f_cliente = ttk.Combobox(filtros, state="readonly", width=16)
        self.cmb_f_cliente.set(TODOS)
        self.cmb_f_cliente.pack(side="left", padx=(0, 8))
        ttk.Button(filtros, text="🔍 Ver", command=self.actualizar_lista).pack(side="left", padx=4)
        ttk.Button(filtros, text="Hoy", command=self.ventas_hoy).pack(side="left")

        self.tree = tabla(self.cont, [
            ("fecha", "Fecha", 86, "center"), ("dia", "Día", 70, "center"),
            ("producto", "Producto", 190, "w"), ("cliente", "Cliente", 130, "w"),
            ("metodo", "Pago", 90, "center"), ("estado", "Estado", 90, "center"),
            ("monto", "Monto", 110, "e")], height=14)
        self.tree.tag_configure("fiada", foreground=C.COLOR_FIADO)

        # Barra anclada abajo ANTES de expandir la tabla, para que nunca se oculte
        barra = ttk.Frame(self.cont)
        barra.pack(side="bottom", fill="x", pady=(6, 0))
        estado = "normal" if self.puede_corregir else "disabled"
        ttk.Button(barra, text="✏ Editar venta", state=estado, command=self.editar).pack(
            side="left", padx=2)
        ttk.Button(barra, text="🗑 Eliminar venta", state=estado, command=self.eliminar).pack(
            side="left", padx=2)
        self.lbl_total = ttk.Label(barra, text="Total: $0", style="Total.TLabel",
                                   foreground=C.COLOR_TEXTO_VERDE)
        self.lbl_total.pack(side="right", padx=6)
        self.tree.pack(side="top", fill="both", expand=True, pady=(4, 6))

    def refrescar(self):
        app = self.app
        nombres_met = list(app.metodo_map)
        self.cmb_producto["values"] = list(app.prod_map)
        self.cmb_metodo["values"] = nombres_met
        self.cmb_cliente["values"] = [C.CLIENTE_GENERAL] + list(app.cliente_map)
        if not self.cmb_cliente.get().strip():
            self.cmb_cliente.set(C.CLIENTE_GENERAL)
        if (not self.cmb_metodo.get().strip() and nombres_met
                and self.cmb_cliente.get().strip() == C.CLIENTE_GENERAL):
            self.cmb_metodo.set("Efectivo" if "Efectivo" in nombres_met else nombres_met[0])
        app.set_combo(self.cmb_f_producto, [TODOS] + list(app.prod_map), TODOS)
        app.set_combo(self.cmb_f_metodo, [TODOS] + nombres_met, TODOS)
        app.set_combo(self.cmb_f_cliente, [TODOS, C.CLIENTE_GENERAL] + list(app.cliente_map), TODOS)
        self.actualizar_lista()

    def ventas_hoy(self):
        hoy = date.today().isoformat()
        poner_fecha(self.ent_desde, hoy)
        poner_fecha(self.ent_hasta, hoy)
        for cmb in (self.cmb_f_producto, self.cmb_f_metodo, self.cmb_f_cliente):
            cmb.set(TODOS)
        self.actualizar_lista()

    def _filtro_cliente(self):
        valor = self.cmb_f_cliente.get()
        if valor in (TODOS, ""):
            return None
        if valor == C.CLIENTE_GENERAL:
            return self.app.ventas.SOLO_CONTADO
        return self.app.cliente_map.get(valor)

    def actualizar_lista(self):
        app = self.app
        pv, mv = self.cmb_f_producto.get(), self.cmb_f_metodo.get()
        try:
            filas, total = app.ventas.listar(
                self.ent_desde.get(), self.ent_hasta.get(),
                producto_id=None if pv in (TODOS, "") else app.prod_map.get(pv, {}).get("id"),
                metodo_id=None if mv in (TODOS, "") else app.metodo_map.get(mv),
                cliente_id=self._filtro_cliente())
        except ErrorDeNegocio as error:
            messagebox.showwarning("Fechas inválidas", str(error))
            self.ventas_hoy()
            return
        limpiar(self.tree)
        for r in filas:
            pagada = bool(r["pagada"])
            self.tree.insert("", "end", iid=r["id"], tags=() if pagada else ("fiada",),
                             values=(r["fecha"], dia_semana(r["fecha"]), r["producto"],
                                     r["cliente"], r["metodo"] if pagada else "—",
                                     "Pagada" if pagada else "Fiada", fmt_money(r["monto"])))
        rayar(self.tree)
        self.lbl_total.config(text=f"Total vendido: {fmt_money(total)}  ·  {len(filas)} ventas")

    def _seleccion(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sin selección", "Selecciona una venta de la lista.")
            return None
        return int(sel[0])

    def editar(self):
        tid = self._seleccion()
        if tid is None:
            return
        try:
            r = self.app.ventas.obtener(tid)
        except ErrorDeNegocio as error:
            messagebox.showwarning("No encontrada", str(error))
            self.app.refrescar_todo()
            return

        def guardar(producto, metodo, monto, fecha):
            self.app.ventas.editar(self.app.usuario, tid, producto, metodo, monto, fecha)
            self.app.refrescar_todo()

        metodo_actual = r["metodo"] if r["metodo_id"] is not None else ""
        producto_actual = "" if r["producto_id"] is None else r["producto"]
        dialogo_campos(self.root, "Editar venta", [
            ("Producto:", producto_actual, False), ("Pago:", metodo_actual, False),
            ("Monto:", fmt_money_entry(r["monto"]), True), ("Fecha (AAAA-MM-DD):", r["fecha"], False),
        ], guardar)

    def eliminar(self):
        tid = self._seleccion()
        if tid is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar la venta seleccionada?"):
            return
        try:
            self.app.ventas.eliminar(self.app.usuario, tid)
        except ErrorDeNegocio as error:
            messagebox.showwarning("No se pudo eliminar", str(error))
        self.app.refrescar_todo()
