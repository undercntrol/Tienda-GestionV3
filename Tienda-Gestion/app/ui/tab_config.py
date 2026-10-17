"""Pestaña Configuración (solo administrador).

HU-10 Productos e importar lista de precios CSV
HU-04 Usuarios (administrador / cajero).
Métodos de pago editables, nombre del negocio y respaldo llegan en el Sprint 4.
"""

from __future__ import annotations

from tkinter import filedialog, messagebox, ttk

from .. import config as C
from ..errores import ErrorDeNegocio
from ..formato import fmt_money, fmt_money_entry
from .estilo import limpiar, rayar, tabla
from .widgets import caja_dinero, dialogo_campos


class TabConfiguracion:
    def __init__(self, cont: ttk.Frame, app):
        self.cont = cont
        self.app = app
        self.root = app.root
        self._construir()

    def _construir(self):
        paneles = ttk.Frame(self.cont)
        paneles.pack(fill="both", expand=True)

        # ---------------- Productos ----------------
        izq = ttk.LabelFrame(paneles, text=" Productos ", padding=10)
        izq.pack(side="left", fill="both", expand=True, padx=(0, 6))
        ttk.Label(izq, text="El precio es opcional; al venderlo se autocompleta el monto.",
                  foreground="gray", wraplength=300).pack(anchor="w", pady=(0, 6))
        f1 = ttk.Frame(izq)
        f1.pack(fill="x")
        f1.columnconfigure(1, weight=1)
        ttk.Label(f1, text="Producto:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_prod = ttk.Entry(f1, width=16)
        self.ent_prod.grid(row=0, column=1, sticky="ew", padx=4, pady=2)
        ttk.Label(f1, text="Precio:").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_precio = ttk.Entry(f1, width=16)
        self.ent_precio.grid(row=1, column=1, sticky="ew", padx=4, pady=2)
        caja_dinero(self.ent_precio)
        ttk.Button(f1, text="Agregar", command=self.agregar_producto).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Button(f1, text="📥 Importar lista de precios (CSV)…", command=self.importar).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        self.tree_prod = tabla(izq, [("nombre", "Producto", 180, "w"), ("precio", "Precio", 90, "e")],
                               height=10)
        self.tree_prod.pack(fill="both", expand=True, pady=8)
        b1 = ttk.Frame(izq)
        b1.pack(fill="x")
        ttk.Button(b1, text="✏ Editar", command=self.editar_producto).pack(
            side="left", expand=True, fill="x", padx=2)
        ttk.Button(b1, text="🗑 Eliminar", command=self.eliminar_producto).pack(
            side="left", expand=True, fill="x", padx=2)

        # ---------------- Usuarios ----------------
        usu = ttk.LabelFrame(paneles, text=" Usuarios ", padding=10)
        usu.pack(side="left", fill="both", expand=True, padx=(6, 0))
        ttk.Label(usu, text="El administrador ve todo; el cajero registra ventas, fía y cobra, "
                            "pero no entra a Configuración ni edita/elimina ventas.",
                  foreground="gray", wraplength=300).pack(anchor="w", pady=(0, 6))
        f3 = ttk.Frame(usu)
        f3.pack(fill="x")
        f3.columnconfigure(1, weight=1)
        ttk.Label(f3, text="Usuario:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_usu = ttk.Entry(f3, width=14)
        self.ent_usu.grid(row=0, column=1, sticky="ew", padx=4, pady=2)
        ttk.Label(f3, text="Clave:").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_clave = ttk.Entry(f3, width=14, show="•")
        self.ent_clave.grid(row=1, column=1, sticky="ew", padx=4, pady=2)
        ttk.Label(f3, text="Rol:").grid(row=2, column=0, sticky="w", pady=2)
        self.cmb_rol = ttk.Combobox(f3, state="readonly", width=14, values=list(C.ROLES))
        self.cmb_rol.set(C.ROL_CAJERO)
        self.cmb_rol.grid(row=2, column=1, sticky="ew", padx=4, pady=2)
        ttk.Button(f3, text="Agregar usuario", command=self.agregar_usuario).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=4)
        self.tree_usu = tabla(usu, [("nombre", "Usuario", 140, "w"), ("rol", "Rol", 110, "center")],
                              height=7)
        self.tree_usu.pack(fill="both", expand=True, pady=8)
        ttk.Button(usu, text="🗑 Eliminar usuario", command=self.eliminar_usuario).pack(fill="x")

    def refrescar(self):
        limpiar(self.tree_prod)
        for nombre, info in self.app.prod_map.items():
            self.tree_prod.insert("", "end", iid=info["id"], values=(nombre, fmt_money(info["precio"])))
        limpiar(self.tree_usu)
        for u in self.app.usuarios.listar(self.app.usuario):
            self.tree_usu.insert("", "end", iid=u["id"], values=(u["nombre"], u["rol"]))
        rayar(self.tree_prod)
        rayar(self.tree_usu)

    # ---------------- productos ----------------
    def agregar_producto(self):
        try:
            self.app.catalogo.crear(self.app.usuario, self.ent_prod.get(), self.ent_precio.get())
        except ErrorDeNegocio as error:
            messagebox.showwarning("Revisa el producto", str(error))
            return
        self.ent_prod.delete(0, "end")
        self.ent_precio.delete(0, "end")
        self.app.refrescar_todo()

    def _sel(self, tree, que):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Sin selección", f"Selecciona un {que}.")
            return None
        return int(sel[0])

    def editar_producto(self):
        pid = self._sel(self.tree_prod, "producto")
        if pid is None:
            return
        actual = self.app.prod_por_id.get(pid, {"nombre": "", "precio": 0})

        def guardar(nombre, precio):
            self.app.catalogo.editar(self.app.usuario, pid, nombre, precio)
            self.app.refrescar_todo()

        dialogo_campos(self.root, "Editar producto", [
            ("Producto:", actual["nombre"], False),
            ("Precio:", fmt_money_entry(actual["precio"]), True)], guardar)

    def eliminar_producto(self):
        pid = self._sel(self.tree_prod, "producto")
        if pid is None:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto?\n"
                               "Las ventas ya registradas se conservan."):
            self.app.catalogo.eliminar(self.app.usuario, pid)
            self.app.refrescar_todo()

    def importar(self):
        ruta = filedialog.askopenfilename(
            title="Lista de precios", filetypes=[("Archivo CSV", "*.csv"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            res = self.app.catalogo.importar_csv(self.app.usuario, ruta)
        except ErrorDeNegocio as error:
            messagebox.showwarning("No se pudo importar", str(error))
            return
        self.app.refrescar_todo()
        resumen = f"Productos nuevos: {res.creados}\nPrecios actualizados: {res.actualizados}"
        if res.errores:
            resumen += "\n\nLíneas que no se cargaron:\n" + "\n".join(res.errores[:10])
            if len(res.errores) > 10:
                resumen += f"\n… y {len(res.errores) - 10} más."
            messagebox.showwarning("Importación con observaciones", resumen)
        else:
            messagebox.showinfo("Importación terminada", resumen)

    # ---------------- usuarios ----------------
    def agregar_usuario(self):
        try:
            self.app.usuarios.crear(self.app.usuario, self.ent_usu.get(),
                                    self.ent_clave.get(), self.cmb_rol.get())
        except ErrorDeNegocio as error:
            messagebox.showwarning("Revisa el usuario", str(error))
            return
        self.ent_usu.delete(0, "end")
        self.ent_clave.delete(0, "end")
        self.cmb_rol.set(C.ROL_CAJERO)
        self.app.refrescar_todo()

    def eliminar_usuario(self):
        uid = self._sel(self.tree_usu, "usuario")
        if uid is None:
            return
        nombre = self.tree_usu.item(uid, "values")[0]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar el usuario {nombre}?"):
            return
        try:
            self.app.usuarios.eliminar(self.app.usuario, uid)
        except ErrorDeNegocio as error:
            messagebox.showwarning("No permitido", str(error))
            return
        self.app.refrescar_todo()
