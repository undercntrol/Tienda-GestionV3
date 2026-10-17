"""Acceso a SQLite: conexión, esquema y migraciones.

El esquema es el mismo que usa el producto final (cigarreria.py), para
que una base creada aquí la abra el producto final y al revés.

Es la única parte del programa que crea o altera tablas.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from . import config

ESQUEMA = (
    # ---------------- Sprint 1 ----------------
    """CREATE TABLE IF NOT EXISTS productos (
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        precio REAL NOT NULL DEFAULT 0)""",
    """CREATE TABLE IF NOT EXISTS metodos_pago (
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE)""",
    """CREATE TABLE IF NOT EXISTS transacciones (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER,
        metodo_id   INTEGER,
        monto       REAL NOT NULL,
        fecha       TEXT NOT NULL,
        FOREIGN KEY(producto_id) REFERENCES productos(id)   ON DELETE SET NULL,
        FOREIGN KEY(metodo_id)   REFERENCES metodos_pago(id) ON DELETE SET NULL)""",
    "CREATE INDEX IF NOT EXISTS idx_transacciones_fecha ON transacciones(fecha)",
    # ---------------- Sprint 2 ----------------
    # La clave se guarda como 'sal$hash' (PBKDF2), nunca en texto.
    """CREATE TABLE IF NOT EXISTS usuarios (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre   TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        rol      TEXT NOT NULL DEFAULT 'cajero')""",
    # tipo: 'fijo' (lo crea el tendero en Cuentas) o 'pasajero' (se crea
    # solo al fiarle a alguien que no estaba en la lista).
    """CREATE TABLE IF NOT EXISTS clientes (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre   TEXT NOT NULL UNIQUE,
        telefono TEXT,
        tipo     TEXT NOT NULL DEFAULT 'fijo',
        activo   INTEGER NOT NULL DEFAULT 1)""",
)

# Migraciones: (tabla, columna, definición). Agregan columnas sin romper
# una base que ya está en uso. Para un campo nuevo se agrega una línea aquí.
MIGRACIONES = (
    # Sprint 2 · fiado: a quién se le fió, si ya pagó y CUÁNDO pagó.
    ("transacciones", "cliente_id", "INTEGER"),
    ("transacciones", "pagada", "INTEGER NOT NULL DEFAULT 1"),
    ("transacciones", "fecha_pago", "TEXT"),
)


def conectar(ruta: Path | str | None = None) -> sqlite3.Connection:
    """Abre la base, crea el esquema y la migra. ':memory:' sirve para pruebas."""
    if ruta is None:
        config.CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
        ruta = config.RUTA_BD
    elif str(ruta) != ":memory:":
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(ruta))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    for sentencia in ESQUEMA:
        conn.execute(sentencia)
    _migrar(conn)
    _sembrar_metodos_pago(conn)
    conn.commit()
    return conn


def _columnas(conn: sqlite3.Connection, tabla: str) -> set[str]:
    return {f["name"] for f in conn.execute(f"PRAGMA table_info({tabla})")}


def _migrar(conn: sqlite3.Connection) -> None:
    for tabla, columna, definicion in MIGRACIONES:
        if columna not in _columnas(conn, tabla):
            conn.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")

    # La versión 0.1 guardaba fecha y hora ("2026-09-12 14:32:05"); desde el
    # Sprint 2 se guarda solo la fecha, que es lo que el tendero escoge.
    conn.execute("UPDATE transacciones SET fecha = substr(fecha, 1, 10) "
                 "WHERE length(fecha) > 10")
    # Las ventas anteriores al fiado son de contado: se pagaron el mismo día.
    # Sin esto no aparecerían en los reportes de ingresos.
    conn.execute("UPDATE transacciones SET fecha_pago = fecha "
                 "WHERE pagada = 1 AND fecha_pago IS NULL")


def _sembrar_metodos_pago(conn: sqlite3.Connection) -> None:
    """Para poder vender desde el minuto uno."""
    if conn.execute("SELECT COUNT(*) FROM metodos_pago").fetchone()[0] == 0:
        conn.executemany("INSERT INTO metodos_pago (nombre) VALUES (?)",
                         [(m,) for m in config.METODOS_PAGO_INICIALES])
