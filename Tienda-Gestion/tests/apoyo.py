"""Utilidades compartidas por las pruebas."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db  # noqa: E402
from app.servicios_usuarios import ServicioUsuarios  # noqa: E402


def base_con_admin():
    """Base en memoria con un administrador y un cajero creados."""
    conn = db.conectar(":memory:")
    usuarios = ServicioUsuarios(conn)
    admin = usuarios.crear_primer_admin("dueno", "1234", "1234")
    cajero = usuarios.crear(admin, "ana", "1234", "cajero")
    return conn, admin, cajero
