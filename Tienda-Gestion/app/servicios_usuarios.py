"""HU-04 — Tabla de usuarios · HU-07 — Iniciar sesión con usuario, clave y rol.

La clave se guarda como 'sal$hash' con PBKDF2-SHA256 (librería
estándar). La primera vez que se abre el programa se crea el
administrador. La recuperación de clave llega en el Sprint 5.
"""

from __future__ import annotations

import hashlib
import secrets
import sqlite3

from . import config, permisos
from .errores import AccesoDenegado, DatoInvalido, Duplicado, NoEncontrado
from .modelos import Usuario
from .repositorios import RepositorioUsuarios


def hash_password(pwd: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"), bytes.fromhex(salt), 100_000).hex()
    return f"{salt}${h}"


def verificar_password(pwd: str, almacenado: str) -> bool:
    try:
        salt, h = almacenado.split("$", 1)
    except (ValueError, AttributeError):
        return False
    return secrets.compare_digest(hash_password(pwd, salt).split("$", 1)[1], h)


def validar_clave(clave: str, confirmacion: str | None = None) -> None:
    if len(clave or "") < config.CLAVE_MINIMA:
        raise DatoInvalido(f"La clave debe tener al menos {config.CLAVE_MINIMA} caracteres.")
    if confirmacion is not None and clave != confirmacion:
        raise DatoInvalido("Las claves no coinciden.")


class ServicioUsuarios:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.usuarios = RepositorioUsuarios(conn)

    def hay_usuarios(self) -> bool:
        return self.usuarios.hay_usuarios()

    def autenticar(self, nombre: str, clave: str) -> Usuario:
        if not (nombre or "").strip() or not clave:
            raise DatoInvalido("Escribe el usuario y la clave.")
        fila = self.usuarios.por_nombre(nombre)
        # Mismo mensaje si no existe o si la clave está mal: no se revela
        # a un extraño qué usuarios existen.
        if fila is None or not verificar_password(clave, fila["password"]):
            raise AccesoDenegado("Usuario o clave incorrectos.")
        return Usuario(fila["id"], fila["nombre"], fila["rol"])

    def crear_primer_admin(self, nombre: str, clave: str, confirmacion: str) -> Usuario:
        if self.hay_usuarios():
            raise AccesoDenegado("Ya existe un administrador. Inicia sesión.")
        return self._crear(nombre, clave, config.ROL_ADMIN, confirmacion)

    def crear(self, quien: Usuario, nombre: str, clave: str, rol: str) -> Usuario:
        permisos.exigir(quien, permisos.CONFIGURACION)
        return self._crear(nombre, clave, rol)

    def _crear(self, nombre: str, clave: str, rol: str, confirmacion: str | None = None) -> Usuario:
        nombre = (nombre or "").strip()
        if not nombre:
            raise DatoInvalido("Escribe el nombre de usuario.")
        if rol not in config.ROLES:
            raise DatoInvalido("Elige el rol: administrador o cajero.")
        validar_clave(clave, confirmacion)
        if self.usuarios.por_nombre(nombre):
            raise Duplicado("Ese usuario ya existe.")
        uid = self.usuarios.crear(nombre, hash_password(clave), rol)
        return Usuario(uid, nombre, rol)

    def listar(self, quien: Usuario):
        permisos.exigir(quien, permisos.CONFIGURACION)
        return self.usuarios.listar()

    def eliminar(self, quien: Usuario, uid: int) -> None:
        permisos.exigir(quien, permisos.CONFIGURACION)
        fila = self.usuarios.obtener(uid)
        if fila is None:
            raise NoEncontrado("Ese usuario ya no existe.")
        if uid == quien.id:
            raise DatoInvalido("No puedes eliminar el usuario con el que iniciaste sesión.")
        if fila["rol"] == config.ROL_ADMIN and self.usuarios.contar_admins() <= 1:
            raise DatoInvalido("Debe existir al menos un administrador.")
        self.usuarios.eliminar(uid)
