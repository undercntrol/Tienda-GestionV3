"""Objetos del dominio que viajan entre servicios y pantallas.

Son dataclasses sin lógica de base de datos: se pueden crear en una
prueba sin conexión.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Usuario:
    id: int
    nombre: str
    rol: str


@dataclass(frozen=True)
class VentaRegistrada:
    id: int
    producto: str
    monto: float
    fecha: str
    metodo: str | None      # None cuando es fiada
    cliente: str            # "Cliente general" si es de contado
    fiada: bool


@dataclass(frozen=True)
class ItemCuenta:
    fecha: str
    producto: str
    monto: float


@dataclass(frozen=True)
class Cobro:
    """Lo que se cobró al saldar una cuenta: alimenta el comprobante."""

    cliente: str
    items: list[ItemCuenta]
    total: float
    metodo: str
    fecha_pago: str


@dataclass(frozen=True)
class Periodo:
    ini: str        # "2026-10-01"
    fin: str        # "2026-10-31"
    etiqueta: str   # "Mes de Octubre 2026"


@dataclass
class Reporte:
    """Ingresos de un periodo (HU-03 y HU-09)."""

    periodo: Periodo
    filtros: str
    filas: list = field(default_factory=list)               # ventas pagadas
    por_producto: list = field(default_factory=list)        # [(nombre, n, total)] mayor a menor
    por_dia: list = field(default_factory=list)             # [(fecha_iso, total)] por fecha
    por_metodo: list = field(default_factory=list)          # [(metodo, total)]
    ingresos: float = 0.0


@dataclass
class ResultadoImportacion:
    """Qué pasó al importar una lista de precios (HU-10)."""

    creados: int = 0
    actualizados: int = 0
    errores: list[str] = field(default_factory=list)
