"""Estilo visual (tema verde) y utilidades de tablas."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .. import config as C


def configurar_estilo(root: tk.Misc) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    root.configure(bg=C.COLOR_FONDO)

    style.configure("TNotebook", background=C.COLOR_FONDO, borderwidth=0, tabmargins=(8, 6, 8, 0))
    style.configure("TNotebook.Tab", padding=(18, 9), font=("Segoe UI", 10, "bold"),
                    background="#cfe3cf", foreground=C.COLOR_TENUE, borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", C.COLOR_PANEL)],
              foreground=[("selected", C.COLOR_TEXTO_VERDE)],
              expand=[("selected", (1, 1, 1, 0))])

    style.configure("TFrame", background=C.COLOR_PANEL)
    style.configure("TLabel", background=C.COLOR_PANEL, foreground=C.COLOR_TEXTO)
    style.configure("TLabelframe", background=C.COLOR_PANEL, borderwidth=1, relief="solid",
                    bordercolor=C.COLOR_BORDE)
    style.configure("TLabelframe.Label", background=C.COLOR_PANEL,
                    foreground=C.COLOR_TEXTO_VERDE, font=("Segoe UI", 10, "bold"))
    style.configure("TCheckbutton", background=C.COLOR_PANEL)

    style.configure("Titulo.TLabel", font=("Segoe UI", 14, "bold"), foreground=C.COLOR_TEXTO_VERDE)
    style.configure("Sub.TLabel", font=("Segoe UI", 10, "bold"), foreground=C.COLOR_TEXTO)
    style.configure("Total.TLabel", font=("Segoe UI", 12, "bold"))

    style.configure("TButton", font=("Segoe UI", 9), padding=(8, 5))
    style.map("TButton", background=[("active", C.COLOR_BORDE)])
    style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"),
                    background=C.COLOR_TEXTO_VERDE, foreground="white",
                    borderwidth=0, padding=(12, 6))
    style.map("Accent.TButton",
              background=[("active", C.COLOR_VERDE_HOVER), ("pressed", C.COLOR_VERDE_HOVER),
                          ("disabled", C.COLOR_BORDE)])

    style.configure("TEntry", padding=4, fieldbackground=C.COLOR_ENTRY_BG,
                    foreground=C.COLOR_ENTRY_FG, insertcolor=C.COLOR_ENTRY_FG,
                    selectbackground=C.COLOR_TEXTO_VERDE, selectforeground="white")
    style.configure("TCombobox", padding=4, fieldbackground=C.COLOR_ENTRY_BG,
                    foreground=C.COLOR_ENTRY_FG, background=C.COLOR_ENTRY_BG,
                    selectbackground=C.COLOR_TEXTO_VERDE, selectforeground="white")
    style.map("TCombobox",
              fieldbackground=[("readonly", C.COLOR_ENTRY_BG)],
              foreground=[("readonly", C.COLOR_ENTRY_FG)])
    root.option_add("*TCombobox*Listbox.background", C.COLOR_ENTRY_BG)
    root.option_add("*TCombobox*Listbox.foreground", C.COLOR_ENTRY_FG)
    root.option_add("*TCombobox*Listbox.selectBackground", C.COLOR_TEXTO_VERDE)
    root.option_add("*TCombobox*Listbox.selectForeground", "white")

    style.configure("Treeview", rowheight=27, font=("Segoe UI", 10),
                    background=C.COLOR_PANEL, fieldbackground=C.COLOR_PANEL,
                    foreground=C.COLOR_TEXTO, borderwidth=0)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                    background=C.COLOR_TEXTO_VERDE, foreground="white",
                    relief="flat", padding=(6, 6))
    style.map("Treeview.Heading", background=[("active", C.COLOR_VERDE_HOVER)])
    style.map("Treeview", background=[("selected", C.COLOR_TEXTO_VERDE)],
              foreground=[("selected", "white")])


def rayar(tree: ttk.Treeview) -> None:
    """Filas alternadas (cebra). Respeta las filas marcadas como fiada/debe."""
    tree.tag_configure("par", background=C.COLOR_PANEL, foreground=C.COLOR_TEXTO)
    tree.tag_configure("impar", background=C.COLOR_RAYA, foreground=C.COLOR_TEXTO)
    idx = 0
    for iid in tree.get_children():
        tags = tree.item(iid, "tags")
        if "fiada" in tags or "debe" in tags:
            continue
        tree.item(iid, tags=("par" if idx % 2 == 0 else "impar",))
        idx += 1


def limpiar(tree: ttk.Treeview) -> None:
    for iid in tree.get_children():
        tree.delete(iid)


def tabla(padre, columnas, height=12) -> ttk.Treeview:
    """columnas = [(id, titulo, ancho, anclaje), ...]"""
    tree = ttk.Treeview(padre, columns=[c[0] for c in columnas], show="headings", height=height)
    for col, titulo, ancho, anclaje in columnas:
        tree.heading(col, text=titulo)
        tree.column(col, width=ancho, anchor=anclaje)
    return tree
