"""Punto de entrada de Tienda Gestión.

    python main.py

Abre la base de datos, muestra el inicio de sesión y, al entrar, la
ventana principal con las pestañas que permite el rol del usuario.
"""

from __future__ import annotations

import sys
import tkinter as tk
import traceback
from tkinter import messagebox

from app import db
from app.servicios_usuarios import ServicioUsuarios
from app.ui.aplicacion import Aplicacion
from app.ui.login import PantallaLogin


def iniciar_sesion(root: tk.Tk, conn) -> None:
    for w in root.winfo_children():
        w.destroy()
    PantallaLogin(root, ServicioUsuarios(conn),
                  al_entrar=lambda usuario: Aplicacion(root, conn, usuario,
                                                       al_cerrar_sesion=lambda: iniciar_sesion(root, conn)))


def main() -> int:
    try:
        conn = db.conectar()
    except Exception as error:  # sin base de datos no se puede arrancar
        traceback.print_exc()
        print(f"\nNo se pudo abrir la base de datos.\nRevisa que la carpeta 'datos' "
              f"se pueda escribir.\nDetalle: {error}")
        return 1

    root = tk.Tk()
    root.geometry("1200x800")
    root.minsize(900, 600)
    try:
        root.state("zoomed")  # pantalla completa en Windows
    except tk.TclError:
        pass

    # Condición 5: un error inesperado se muestra, no deja la ventana en blanco.
    def error_inesperado(tipo, valor, rastro):
        traceback.print_exception(tipo, valor, rastro)
        messagebox.showerror("Ocurrió un problema",
                             "La acción no se pudo completar.\n\n"
                             f"Detalle técnico: {valor}\n\n"
                             "Puedes seguir trabajando. Si vuelve a pasar, avísale al equipo.")
    root.report_callback_exception = error_inesperado

    def al_cerrar():
        conn.close()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", al_cerrar)

    iniciar_sesion(root, conn)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
