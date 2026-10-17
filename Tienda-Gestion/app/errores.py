"""Errores propios del dominio.

Se separan de las excepciones de sqlite3 a propósito: la interfaz solo
le muestra al tendero mensajes que él entiende. Cualquier otro error es
técnico y se muestra en la ventana de "Ocurrió un problema".
"""


class ErrorDeNegocio(Exception):
    """Algo que el usuario hizo mal y puede corregir."""


class DatoInvalido(ErrorDeNegocio):
    """Un campo llegó vacío, con letras donde van números, o fuera de rango."""


class Duplicado(ErrorDeNegocio):
    """Ya existe un registro con ese nombre."""


class NoEncontrado(ErrorDeNegocio):
    """Se pidió un registro que no está en la base de datos."""


class AccesoDenegado(ErrorDeNegocio):
    """Usuario o clave incorrectos, o el rol no permite la acción."""
