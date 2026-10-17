"""Pestaña Reportes — HU-03 Total de una fecha · HU-09 Ingresos por día, semana o mes (HTML y Excel)."""

from __future__ import annotations

import os
import webbrowser
from datetime import date
from tkinter import messagebox, ttk

from .. import config as C
from ..errores import ErrorDeNegocio
from ..formato import dia_corto, fmt_money
from ..servicios_reportes import TIPOS, periodo
from .estilo import limpiar, rayar, tabla
from .widgets import campo_fecha

TODOS = "Todos"


class TabReportes:
    def __init__(self, cont: ttk.Frame, app):
        self.cont = cont
        self.app = app
        self.root = app.root
        self.reporte = None
        self._construir()

    def _construir(self):
        cont = self.cont
        ttk.Label(cont, text="Reportes de ventas", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(cont, foreground="gray",
                  text="Muestra lo que realmente entró a la caja: lo fiado aparece el día en que se cobra."
                  ).pack(anchor="w")
        ctrl = ttk.LabelFrame(cont, text=" Período ", padding=10)
        ctrl.pack(fill="x", pady=6)

        hoy = date.today()
        ttk.Label(ctrl, text="Ver por:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.cmb_tipo = ttk.Combobox(ctrl, state="readonly", values=TIPOS, width=10)
        self.cmb_tipo.set("Día")
        self.cmb_tipo.grid(row=0, column=1, sticky="w", padx=4, pady=4)
        self.cmb_tipo.bind("<<ComboboxSelected>>", lambda _e: self._controles())
        self.lbl_fecha = ttk.Label(ctrl, text="Día:")
        self.lbl_fecha.grid(row=0, column=2, sticky="w", padx=4)
        self.cf_fecha, self.ent_fecha = campo_fecha(ctrl, self.root, hoy.isoformat())
        self.cf_fecha.grid(row=0, column=3, sticky="w", padx=4)
        self.lbl_mes = ttk.Label(ctrl, text="Mes:")
        self.lbl_mes.grid(row=0, column=4, sticky="w", padx=4)
        self.cmb_mes = ttk.Combobox(ctrl, state="readonly", values=C.MESES, width=12)
        self.cmb_mes.set(C.MESES[hoy.month - 1])
        self.cmb_mes.grid(row=0, column=5, sticky="w", padx=4)
        self.lbl_anio = ttk.Label(ctrl, text="Año:")
        self.lbl_anio.grid(row=0, column=6, sticky="w", padx=4)
        self.cmb_anio = ttk.Combobox(ctrl, state="readonly", width=6,
                                     values=[str(y) for y in range(hoy.year - 3, hoy.year + 3)])
        self.cmb_anio.set(str(hoy.year))
        self.cmb_anio.grid(row=0, column=7, sticky="w", padx=4)

        ttk.Label(ctrl, text="Producto:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.cmb_producto = ttk.Combobox(ctrl, state="readonly", width=18)
        self.cmb_producto.grid(row=1, column=1, columnspan=2, sticky="w", padx=4, pady=4)
        ttk.Label(ctrl, text="Pago:").grid(row=1, column=3, sticky="w", padx=4)
        self.cmb_metodo = ttk.Combobox(ctrl, state="readonly", width=16)
        self.cmb_metodo.grid(row=1, column=4, columnspan=2, sticky="w", padx=4)
        ttk.Button(ctrl, text="🔍 Ver", command=self.actualizar).grid(row=1, column=6, padx=4)
        ttk.Button(ctrl, text="📄 Imprimir (HTML)", style="Accent.TButton",
                   command=self.exportar_html).grid(row=1, column=7, padx=4)
        ttk.Button(ctrl, text="📊 Excel", command=self.exportar_excel).grid(row=1, column=8, padx=4)
        self._controles()

        self.lbl_periodo = ttk.Label(cont, text="", style="Sub.TLabel", foreground=C.COLOR_TEXTO_VERDE)
        self.lbl_periodo.pack(anchor="w", pady=(2, 6))

        tablas = ttk.Frame(cont)
        tablas.pack(fill="both", expand=True)
        izq = ttk.Frame(tablas)
        izq.pack(side="left", fill="both", expand=True, padx=(0, 6))
        ttk.Label(izq, text="Total por producto (lo más vendido primero)", style="Sub.TLabel").pack(anchor="w")
        self.tree_prod = tabla(izq, [("producto", "Producto", 200, "w"), ("n", "Ventas", 70, "center"),
                                     ("total", "Total", 120, "e")], height=14)
        self.tree_prod.pack(fill="both", expand=True)
        der = ttk.Frame(tablas)
        der.pack(side="left", fill="both", expand=True)
        ttk.Label(der, text="Total por día", style="Sub.TLabel").pack(anchor="w")
        self.tree_dia = tabla(der, [("dia", "Día", 160, "w"), ("total", "Total", 120, "e")], height=8)
        self.tree_dia.pack(fill="x")
        resumen = ttk.LabelFrame(der, text=" Totales del período ", padding=10)
        resumen.pack(fill="x", pady=(10, 0))
        self.lbl_ingresos = ttk.Label(resumen, text="Ingresos totales: $0", style="Total.TLabel",
                                      foreground=C.COLOR_TEXTO_VERDE)
        self.lbl_ingresos.pack(anchor="w", pady=2)
        self.lbl_metodos = ttk.Label(resumen, text="", justify="left", wraplength=380)
        self.lbl_metodos.pack(anchor="w", pady=2)

    def _controles(self):
        tipo = self.cmb_tipo.get()
        es_mes = tipo == "Mes"
        for w in (self.lbl_fecha, self.cf_fecha):
            (w.grid_remove if es_mes else w.grid)()
        for w in (self.lbl_mes, self.cmb_mes, self.lbl_anio, self.cmb_anio):
            (w.grid if es_mes else w.grid_remove)()
        self.lbl_fecha.config(text="Día:" if tipo == "Día" else "Semana del:")

    def refrescar(self):
        app = self.app
        app.set_combo(self.cmb_producto, [TODOS] + list(app.prod_map), TODOS)
        app.set_combo(self.cmb_metodo, [TODOS] + list(app.metodo_map), TODOS)
        self.actualizar()

    def _generar(self):
        app = self.app
        pv, mv = self.cmb_producto.get(), self.cmb_metodo.get()
        try:
            per = periodo(self.cmb_tipo.get(), self.ent_fecha.get(),
                          self.cmb_mes.get(), self.cmb_anio.get())
        except ErrorDeNegocio as error:
            messagebox.showwarning("Revisa el período", str(error))
            return None
        return app.reportes.generar(
            per,
            producto_id=None if pv in (TODOS, "") else app.prod_map.get(pv, {}).get("id"),
            metodo_id=None if mv in (TODOS, "") else app.metodo_map.get(mv),
            filtros_txt=f"Producto: {pv or TODOS} · Pago: {mv or TODOS}")

    def actualizar(self):
        rep = self._generar()
        if rep is None:
            return
        self.reporte = rep
        limpiar(self.tree_prod)
        for nombre, n, total in rep.por_producto:
            self.tree_prod.insert("", "end", values=(nombre, n, fmt_money(total)))
        limpiar(self.tree_dia)
        for f, total in rep.por_dia:
            self.tree_dia.insert("", "end", values=(dia_corto(f), fmt_money(total)))
        rayar(self.tree_prod)
        rayar(self.tree_dia)
        self.lbl_periodo.config(text=f"{rep.periodo.etiqueta} · {rep.filtros}")
        self.lbl_ingresos.config(text=f"Ingresos totales: {fmt_money(rep.ingresos)}  ·  "
                                      f"{len(rep.filas)} ventas")
        detalle = "   ".join(f"{m}: {fmt_money(v)}" for m, v in rep.por_metodo)
        self.lbl_metodos.config(text="Por método de pago →  " + (detalle or "Sin ventas en el período."))

    def exportar_html(self):
        rep = self._generar()
        if rep is None:
            return
        try:
            ruta = self.app.reportes.guardar_html(rep)
        except OSError as e:
            messagebox.showerror("Error", f"No se pudo crear el reporte:\n{e}")
            return
        webbrowser.open(ruta.as_uri())

    def exportar_excel(self):
        rep = self._generar()
        if rep is None:
            return
        try:
            ruta = self.app.reportes.guardar_excel(rep)
        except (ErrorDeNegocio, OSError) as e:
            messagebox.showerror("Error", str(e))
            return
        if messagebox.askyesno("Excel generado", f"Archivo creado:\n{ruta}\n\n¿Abrirlo ahora?"):
            try:
                os.startfile(ruta)  # Windows
            except AttributeError:
                webbrowser.open(ruta.as_uri())
