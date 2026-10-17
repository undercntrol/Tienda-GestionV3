"""HU-07 — Pantalla de inicio de sesión.

Si aún no hay usuarios, pide crear la cuenta del administrador.
(La pregunta de seguridad y "¿Olvidaste tu clave?" llegan en el Sprint 5.)
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .. import config as C
from ..errores import ErrorDeNegocio
from ..servicios_usuarios import ServicioUsuarios


class PantallaLogin:
    def __init__(self, root: tk.Tk, servicio: ServicioUsuarios, al_entrar):
        self.root = root
        self.servicio = servicio
        self.al_entrar = al_entrar  # recibe el Usuario que inició sesión
        root.title(f"{C.APP_NOMBRE} — Inicio de sesión")
        self.frame = tk.Frame(root, bg="white")
        self.frame.pack(fill="both", expand=True)
        tk.Frame(self.frame, bg=C.COLOR_PRIMARIO, height=8).pack(fill="x")

        card = tk.Frame(self.frame, bg="white")
        card.place(relx=0.5, rely=0.42, anchor="center")

        self.primera_vez = not servicio.hay_usuarios()
        titulo = "Crear cuenta de administrador" if self.primera_vez else "Iniciar sesión"
        sub = ("Es la primera vez que abres el programa.\nCrea el usuario administrador."
               if self.primera_vez else "Ingresa con tu usuario y clave.")
        tk.Label(card, text="🏪", font=("Segoe UI Emoji", 30), bg="white").pack()
        tk.Label(card, text=titulo, font=("Segoe UI", 15, "bold"), bg="white",
                 fg=C.COLOR_TEXTO_VERDE).pack(pady=(2, 2))
        tk.Label(card, text=sub, font=("Segoe UI", 9), bg="white", fg="gray",
                 justify="center").pack(pady=(0, 12))

        form = tk.Frame(card, bg="white")
        form.pack()
        tk.Label(form, text="Usuario:", bg="white", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky="w", pady=4)
        self.ent_usuario = ttk.Entry(form, width=24, font=("Segoe UI", 10))
        self.ent_usuario.grid(row=0, column=1, pady=4, padx=6)
        tk.Label(form, text="Clave:", bg="white", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky="w", pady=4)
        self.ent_clave = ttk.Entry(form, width=24, show="•", font=("Segoe UI", 10))
        self.ent_clave.grid(row=1, column=1, pady=4, padx=6)
        self.ent_confirma = None
        if self.primera_vez:
            tk.Label(form, text="Confirmar clave:", bg="white", font=("Segoe UI", 10)).grid(
                row=2, column=0, sticky="w", pady=4)
            self.ent_confirma = ttk.Entry(form, width=24, show="•", font=("Segoe UI", 10))
            self.ent_confirma.grid(row=2, column=1, pady=4, padx=6)

        self.lbl_error = tk.Label(card, text="", bg="white", fg=C.COLOR_ERROR,
                                  font=("Segoe UI", 9), wraplength=300)
        self.lbl_error.pack(pady=(6, 0))
        tk.Button(card, text="Crear cuenta e ingresar" if self.primera_vez else "Ingresar",
                  command=self.aceptar, bg=C.COLOR_TEXTO_VERDE, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=20, pady=6, cursor="hand2").pack(
            pady=10, fill="x")

        root.bind("<Return>", lambda _e: self.aceptar())
        self.ent_usuario.focus_set()

    def aceptar(self):
        try:
            if self.primera_vez:
                usuario = self.servicio.crear_primer_admin(
                    self.ent_usuario.get(), self.ent_clave.get(), self.ent_confirma.get())
            else:
                usuario = self.servicio.autenticar(self.ent_usuario.get(), self.ent_clave.get())
        except ErrorDeNegocio as error:
            self.lbl_error.config(text=str(error))
            self.ent_clave.delete(0, "end")
            return
        self.root.unbind("<Return>")
        self.frame.destroy()
        self.al_entrar(usuario)
