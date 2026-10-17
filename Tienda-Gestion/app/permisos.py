"""Qué puede hacer cada rol (HU-07 · condición técnica 2).

Administrador: todo. Cajero: registra ventas, fía, cobra cuentas y ve
reportes, pero no edita ni elimina ventas ni entra a Configuración.
Está en una sola tabla para que cambiar un permiso sea cambiar una línea.
"""

from __future__ import annotations

from . import config
from .errores import AccesoDenegado
from .modelos import Usuario

VENDER = "vender"
CUENTAS = "cuentas"
REPORTES = "reportes"
CORREGIR_VENTAS = "corregir_ventas"    # editar y eliminar ventas
CONFIGURACION = "configuracion"        # productos, importar precios, usuarios

PERMISOS_POR_ROL: dict[str, set[str]] = {
    config.ROL_ADMIN: {VENDER, CUENTAS, REPORTES, CORREGIR_VENTAS, CONFIGURACION},
    config.ROL_CAJERO: {VENDER, CUENTAS, REPORTES},
}


def puede(usuario: Usuario | None, permiso: str) -> bool:
    return usuario is not None and permiso in PERMISOS_POR_ROL.get(usuario.rol, set())


def exigir(usuario: Usuario | None, permiso: str) -> None:
    if not puede(usuario, permiso):
        raise AccesoDenegado("Solo el administrador puede realizar esta acción.")
