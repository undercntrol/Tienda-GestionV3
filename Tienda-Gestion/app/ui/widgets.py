"""Controles reutilizables: calendario, campo de fecha, caja de dinero,
autocompletar y diálogos de edición. Solo tkinter, sin librerías externas.
"""

from __future__ import annotations

import calendar
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from .. import config as C
from ..errores import ErrorDeNegocio
from ..formato import fmt_money_entry, solo_digitos


class CalendarioPopup(tk.Toplevel):
    """Calendario pequeño para elegir una fecha con el mouse."""

    def __init__(self, parent, fecha_inicial: date, on_pick, anchor=None):
        super().__init__(parent)
        self.on_pick = on_pick
        self.title("Elegir fecha")
        self.resizable(False, False)
        self.transient(parent)
        self.configure(bg=C.COLOR_PANEL)
        self.anio, self.mes = fecha_inicial.year, fecha_inicial.month
        self.hoy = date.today()
        self.sel = fecha_inicial

        cab = tk.Frame(self, bg=C.COLOR_TEXTO_VERDE)
        cab.pack(fill="x")
        estilo_btn = dict(bg=C.COLOR_TEXTO_VERDE, fg="white", relief="flat", bd=0,
                          font=("Segoe UI", 11, "bold"), cursor="hand2", width=3,
                          activebackground=C.COLOR_VERDE_HOVER, activeforeground="white")
        tk.Button(cab, text="◀", command=lambda: self._cambiar_mes(-1), **estilo_btn).pack(side="left")
        self.lbl_mes = tk.Label(cab, text="", bg=C.COLOR_TEXTO_VERDE, fg="white",
                                font=("Segoe UI", 11, "bold"), width=16)
        self.lbl_mes.pack(side="left", expand=True)
        tk.Button(cab, text="▶", command=lambda: self._cambiar_mes(1), **estilo_btn).pack(side="right")

        self.grilla = tk.Frame(self, bg=C.COLOR_PANEL, padx=8, pady=8)
        self.grilla.pack()
        pie = tk.Frame(self, bg=C.COLOR_PANEL)
        pie.pack(fill="x", pady=(0, 8))
        tk.Button(pie, text="Hoy", command=self._ir_hoy, bg="#e8e8e8", relief="flat",
                  cursor="hand2", padx=12, pady=2).pack()

        self._dibujar()
        self.grab_set()
        self.update_idletasks()
        if anchor is not None:
            try:
                self.geometry(f"+{anchor.winfo_rootx()}+"
                              f"{anchor.winfo_rooty() + anchor.winfo_height() + 2}")
            except tk.TclError:
                pass
        self.bind("<Escape>", lambda _e: self.destroy())

    def _cambiar_mes(self, delta):
        m = self.mes - 1 + delta
        self.anio += m // 12
        self.mes = m % 12 + 1
        self._dibujar()

    def _ir_hoy(self):
        self.anio, self.mes = self.hoy.year, self.hoy.month
        self._dibujar()

    def _dibujar(self):
        for w in self.grilla.winfo_children():
            w.destroy()
        self.lbl_mes.config(text=f"{C.MESES[self.mes - 1]} {self.anio}")
        for i, d in enumerate("LMMJVSD"):
            tk.Label(self.grilla, text=d, bg=C.COLOR_PANEL, fg=C.COLOR_TENUE,
                     font=("Segoe UI", 9, "bold"), width=3).grid(row=0, column=i, pady=(0, 2))
        for r, semana in enumerate(calendar.Calendar(0).monthdayscalendar(self.anio, self.mes), 1):
            for c, dia in enumerate(semana):
                if not dia:
                    continue
                d = date(self.anio, self.mes, dia)
                if d == self.sel:
                    bg, fg = C.COLOR_TEXTO_VERDE, "white"
                elif d == self.hoy:
                    bg, fg = C.COLOR_PRIMARIO, "#063b06"
                else:
                    bg, fg = C.COLOR_PANEL, C.COLOR_TEXTO
                tk.Button(self.grilla, text=str(dia), width=3, relief="flat", bd=0, bg=bg, fg=fg,
                          cursor="hand2", font=("Segoe UI", 9),
                          activebackground=C.COLOR_PRIMARIO, activeforeground="#063b06",
                          command=lambda dd=d: self._elegir(dd)).grid(row=r, column=c, padx=1, pady=1)

    def _elegir(self, d):
        self.on_pick(d)
        self.destroy()


def campo_fecha(parent, root, valor: str = ""):
    """Devuelve (contenedor, entry): una caja de fecha con botón 📅."""
    cont = ttk.Frame(parent)
    ent = ttk.Entry(cont, width=12)
    if valor:
        ent.insert(0, valor)
    ent.pack(side="left")

    def abrir():
        try:
            ini = datetime.strptime(ent.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            ini = date.today()

        def elegido(d):
            ent.delete(0, "end")
            ent.insert(0, d.isoformat())
        CalendarioPopup(root, ini, elegido, anchor=ent)

    ttk.Button(cont, text="📅", width=3, takefocus=False, command=abrir).pack(side="left", padx=(2, 0))
    return cont, ent


def poner_fecha(entry: ttk.Entry, iso: str) -> None:
    entry.delete(0, "end")
    entry.insert(0, iso)


def caja_dinero(entry: ttk.Entry) -> None:
    """Mientras se escribe, muestra el valor como $2.500."""
    def on_key(_e=None):
        d = solo_digitos(entry.get())
        entry.delete(0, "end")
        entry.insert(0, fmt_money_entry(d) if d else "")
    entry.bind("<KeyRelease>", on_key)


def sin_resaltado(widget) -> None:
    """Al entrar con Tab no deja todo el texto seleccionado en azul."""
    def limpiar(_e=None):
        def hacer():
            try:
                widget.selection_clear()
                widget.icursor("end")
            except tk.TclError:
                pass
        widget.after_idle(hacer)
    widget.bind("<FocusIn>", limpiar, add="+")


def autocompletar(root, combo: ttk.Combobox, get_todos, on_select=None) -> None:
    """Lista de coincidencias DEBAJO del campo mientras se escribe.

    Se elige con clic o con ↑/↓ y Enter, sin bloquear la escritura.
    Evita crear productos o clientes duplicados por escribirlos distinto.
    """
    est = {"pop": None, "lb": None}
    combo._ac = est  # referencia para pruebas

    def cerrar(_e=None):
        if est["pop"] is not None:
            try:
                est["pop"].destroy()
            except tk.TclError:
                pass
        est["pop"] = est["lb"] = None

    def elegir(valor):
        combo.set(valor)
        combo.icursor("end")
        cerrar()
        if on_select:
            on_select()

    def mostrar(coincidencias):
        cerrar()
        pop = tk.Toplevel(root)
        pop.overrideredirect(True)
        try:
            pop.attributes("-topmost", True)
        except tk.TclError:
            pass
        lb = tk.Listbox(pop, height=min(7, len(coincidencias)), exportselection=False,
                        font=("Segoe UI", 10), activestyle="none", bd=1, relief="solid",
                        bg=C.COLOR_ENTRY_BG, fg=C.COLOR_TEXTO, highlightthickness=1,
                        highlightbackground=C.COLOR_TEXTO_VERDE,
                        selectbackground=C.COLOR_TEXTO_VERDE, selectforeground="white")
        for v in coincidencias:
            lb.insert("end", v)
        lb.selection_set(0)
        lb.pack(fill="both", expand=True)

        def click(_e=None):
            sel = lb.curselection()
            if sel:
                elegir(lb.get(sel[0]))
        lb.bind("<ButtonRelease-1>", click)
        est["pop"], est["lb"] = pop, lb
        combo.update_idletasks()
        pop.update_idletasks()
        pop.geometry(f"{max(combo.winfo_width(), 160)}x{lb.winfo_reqheight()}"
                     f"+{combo.winfo_rootx()}+{combo.winfo_rooty() + combo.winfo_height()}")

    def mover(delta):
        lb = est["lb"]
        if lb is None:
            return
        cur = lb.curselection()
        idx = (cur[0] + delta) if cur else (0 if delta > 0 else lb.size() - 1)
        idx = max(0, min(idx, lb.size() - 1))
        lb.selection_clear(0, "end")
        lb.selection_set(idx)
        lb.see(idx)

    def con_lista(accion):
        def handler(_e):
            if est["lb"] is not None:
                accion()
                return "break"
            return None
        return handler

    def on_return(_e):
        if est["lb"] is not None:
            sel = est["lb"].curselection()
            if sel:
                elegir(est["lb"].get(sel[0]))
            return "break"
        return None

    def filtrar(event):
        if event.keysym in ("Down", "Up", "Return", "Escape", "Left", "Right", "Tab", "Home",
                            "End", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"):
            return
        texto = combo.get().strip().lower()
        todos = list(get_todos())
        if not texto:
            combo["values"] = todos
            cerrar()
            return
        coincidencias = [v for v in todos if texto in v.lower()]
        combo["values"] = coincidencias or todos
        exacto = len(coincidencias) == 1 and coincidencias[0].lower() == texto
        if coincidencias and not exacto:
            mostrar(coincidencias)
        else:
            cerrar()

    combo.bind("<KeyRelease>", filtrar)
    combo.bind("<Down>", con_lista(lambda: mover(1)))
    combo.bind("<Up>", con_lista(lambda: mover(-1)))
    combo.bind("<Tab>", con_lista(lambda: mover(1)))
    combo.bind("<Shift-Tab>", con_lista(lambda: mover(-1)))
    combo.bind("<ISO_Left_Tab>", con_lista(lambda: mover(-1)))
    combo.bind("<Return>", on_return)
    combo.bind("<Escape>", lambda _e: cerrar())
    combo.bind("<FocusOut>", lambda _e: combo.after(200, cerrar))


def dialogo_campos(root, titulo: str, campos, on_save) -> tk.Toplevel:
    """Diálogo genérico de edición.

    campos = [(etiqueta, valor_inicial, es_dinero), ...]
    on_save(*valores) se llama al guardar; si lanza ErrorDeNegocio, se
    muestra el mensaje y el diálogo sigue abierto.
    """
    dlg = tk.Toplevel(root)
    dlg.title(titulo)
    dlg.transient(root)
    dlg.grab_set()
    dlg.resizable(False, False)
    dlg.configure(bg=C.COLOR_PANEL)
    entradas = []
    for i, (etiqueta, valor, dinero) in enumerate(campos):
        ttk.Label(dlg, text=etiqueta).grid(row=i, column=0, sticky="w", padx=10, pady=8)
        e = ttk.Entry(dlg, width=28)
        e.insert(0, valor)
        e.grid(row=i, column=1, padx=10, pady=8)
        if dinero:
            caja_dinero(e)
        entradas.append(e)

    def guardar():
        try:
            on_save(*[e.get() for e in entradas])
        except ErrorDeNegocio as error:
            messagebox.showwarning(titulo, str(error), parent=dlg)
            return
        dlg.destroy()

    ttk.Button(dlg, text="Guardar", style="Accent.TButton", command=guardar).grid(
        row=len(campos), column=0, columnspan=2, sticky="ew", padx=10, pady=10)
    entradas[0].focus_set()
    dlg.bind("<Return>", lambda _e: guardar())
    return dlg


def avisar_error(error: Exception, titulo: str = "Revisa los datos", parent=None) -> None:
    messagebox.showwarning(titulo, str(error), parent=parent)
