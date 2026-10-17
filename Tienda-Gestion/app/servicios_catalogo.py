"""HU-10 — Administrar productos e importar la lista de precios.

El precio es opcional: si un producto tiene precio, al venderlo se
autocompleta el monto. Los productos también se crean solos al vender
(ver servicios_ventas.py).
"""

from __future__ import annotations

import csv
import io
import sqlite3
from pathlib import Path

from . import permisos
from .errores import DatoInvalido, Duplicado, NoEncontrado
from .formato import parse_numero
from .modelos import ResultadoImportacion, Usuario
from .repositorios import RepositorioProductos

PRECIO_MAXIMO = 5_000_000


def limpiar_nombre(texto: str, de_que: str = "del producto") -> str:
    nombre = " ".join(str(texto).split())
    if not nombre:
        raise DatoInvalido(f"Escribe el nombre {de_que}.")
    if len(nombre) > 60:
        raise DatoInvalido(f"El nombre {de_que} no puede pasar de 60 caracteres.")
    return nombre


def limpiar_precio(texto, obligatorio: bool = False) -> float:
    """'$ 2.500' -> 2500. Vacío -> 0 si el precio es opcional."""
    bruto = str(texto).strip()
    if not bruto.replace("$", "").strip():
        if obligatorio:
            raise DatoInvalido("Escribe el precio.")
        return 0.0
    try:
        valor = parse_numero(bruto)
    except ValueError:
        raise DatoInvalido(f"“{texto}” no es un precio válido. Usa solo números, ej. 2500.") from None
    if valor < 0 or (obligatorio and valor == 0):
        raise DatoInvalido("El precio debe ser mayor que cero.")
    if valor > PRECIO_MAXIMO:
        raise DatoInvalido("El precio es demasiado alto. Revisa si sobra un cero.")
    return valor


class ServicioCatalogo:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.productos = RepositorioProductos(conn)

    def listar(self):
        return self.productos.listar()

    def crear(self, quien: Usuario, nombre: str, precio="") -> int:
        permisos.exigir(quien, permisos.CONFIGURACION)
        nombre = limpiar_nombre(nombre)
        valor = limpiar_precio(precio)
        if self.productos.por_nombre(nombre):
            raise Duplicado("Ese producto ya existe.")
        return self.productos.crear(nombre, valor)

    def editar(self, quien: Usuario, pid: int, nombre: str, precio="") -> None:
        permisos.exigir(quien, permisos.CONFIGURACION)
        if self.productos.obtener(pid) is None:
            raise NoEncontrado("Ese producto ya no existe.")
        nombre = limpiar_nombre(nombre)
        valor = limpiar_precio(precio)
        otro = self.productos.por_nombre(nombre)
        if otro and otro["id"] != pid:
            raise Duplicado("Ya existe un producto con ese nombre.")
        self.productos.editar(pid, nombre, valor)

    def eliminar(self, quien: Usuario, pid: int) -> None:
        """Las ventas ya registradas se conservan con producto '(eliminado)'."""
        permisos.exigir(quien, permisos.CONFIGURACION)
        self.productos.eliminar(pid)

    # ---------------- Sprint 3 · HU-10 (importación) ----------------
    def importar_csv(self, quien: Usuario, ruta: str | Path) -> ResultadoImportacion:
        """Carga la lista de precios del proveedor desde un archivo CSV externo.

        - Columnas: nombre y precio, con o sin encabezado, separadas por ; o ,
          (Excel en español guarda con ;, Google Sheets con ,).
        - Producto nuevo → se crea. Existente → se le actualiza el precio.
        - Una línea mala NO detiene la importación: se reporta con su número.
        """
        permisos.exigir(quien, permisos.CONFIGURACION)
        ruta = Path(ruta)
        if not ruta.exists():
            raise NoEncontrado(f"No se encontró el archivo {ruta.name}.")
        try:
            texto = ruta.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            texto = ruta.read_text(encoding="latin-1")  # CSV de Excel antiguo
        if not texto.strip():
            raise DatoInvalido("El archivo está vacío.")

        separador = ";" if ";" in texto.splitlines()[0] else ","
        resultado = ResultadoImportacion()
        for numero, fila in enumerate(csv.reader(io.StringIO(texto), delimiter=separador), 1):
            if not fila or not any(c.strip() for c in fila):
                continue
            if numero == 1 and fila[0].strip().lower() in ("nombre", "producto"):
                continue  # encabezado
            if len(fila) < 2:
                resultado.errores.append(f"Línea {numero}: falta el precio.")
                continue
            try:
                nombre = limpiar_nombre(fila[0])
                precio = limpiar_precio(fila[1], obligatorio=True)
            except DatoInvalido as error:
                resultado.errores.append(f"Línea {numero}: {error}")
                continue
            existente = self.productos.por_nombre(nombre)
            if existente:
                self.productos.editar(existente["id"], existente["nombre"], precio)
                resultado.actualizados += 1
            else:
                self.productos.crear(nombre, precio)
                resultado.creados += 1

        if not (resultado.creados or resultado.actualizados or resultado.errores):
            raise DatoInvalido("El archivo no tiene productos para importar.")
        return resultado
