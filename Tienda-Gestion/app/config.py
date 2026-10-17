"""Configuración central de Tienda Gestión.

Rutas, constantes del negocio y colores. Todo lo que pueda cambiar
entre el computador de desarrollo y el de la tienda vive aquí.
"""

import sys
from pathlib import Path

APP_NOMBRE = "Tienda Gestión"
APP_VERSION = "0.3.0"  # cierre del Sprint 3

# Cuando el programa se empaquete como .exe (Sprint 6), los datos quedan
# junto al ejecutable; mientras tanto, junto al proyecto.
if getattr(sys, "frozen", False):
    DIR_BASE = Path(sys.executable).resolve().parent
else:
    DIR_BASE = Path(__file__).resolve().parent.parent

CARPETA_DATOS = DIR_BASE / "datos"
RUTA_BD = CARPETA_DATOS / "tienda.db"
CARPETA_SALIDAS = DIR_BASE / "salidas"   # reportes HTML/Excel y comprobantes

# ---------------- Reglas del negocio ----------------
# Métodos de pago con los que arranca la tienda (se pueden escribir otros al vender).
METODOS_PAGO_INICIALES = ("Efectivo", "Nequi", "Daviplata", "Tarjeta")

# La venta de contado se registra a nombre de este cliente "virtual".
# Cualquier otro cliente significa FIADO: se cobra después en Cuentas.
CLIENTE_GENERAL = "Cliente general"

# Roles (Sprint 2). Qué puede hacer cada uno está en permisos.py.
ROL_ADMIN = "administrador"
ROL_CAJERO = "cajero"
ROLES = (ROL_ADMIN, ROL_CAJERO)
CLAVE_MINIMA = 4

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# ---------------- Colores (tema verde) ----------------
# El tema oscuro llega en el Sprint 5; por ahora solo la paleta clara.
COLOR_PRIMARIO = "#3EFF3F"      # verde brillante del login
COLOR_TEXTO_VERDE = "#0a7a0a"   # verde de acento
COLOR_VERDE_HOVER = "#0c8f0c"
COLOR_FONDO = "#eaf1ea"
COLOR_PANEL = "#ffffff"
COLOR_TEXTO = "#1b241f"
COLOR_TENUE = "#5a6b62"
COLOR_RAYA = "#eef6ef"
COLOR_BORDE = "#d4e4d4"
COLOR_HEADER = "#3EFF3F"
COLOR_HEADER_TXT = "#063b06"
COLOR_HEADER_SUB = "#1a5c1a"
COLOR_ENTRY_BG = "#ffffff"
COLOR_ENTRY_FG = "#1b241f"
COLOR_FIADO = "#b06a00"         # ámbar: ventas fiadas y saldos pendientes
COLOR_ERROR = "#b00020"
