"""Formato de dinero y fechas en la convención colombiana.

No depende de la interfaz: lo usan las pantallas, los reportes HTML y
las pruebas.
"""

from __future__ import annotations

from datetime import date, timedelta

from .config import DIAS_SEMANA, MESES


def fmt_money(v) -> str:
    """1500 -> '$1.500'."""
    try:
        return "$" + "{:,.0f}".format(float(v)).replace(",", ".")
    except (ValueError, TypeError):
        return "$0"


def fmt_money_entry(v) -> str:
    """Lo que se ve dentro de una caja de dinero mientras se escribe."""
    try:
        n = int(round(float(v)))
    except (ValueError, TypeError):
        n = 0
    return "$" + f"{n:,}".replace(",", ".")


def parse_numero(txt) -> float:
    """'$ 2.500' -> 2500.0. Vacío -> 0."""
    limpio = (str(txt).strip().replace(".", "").replace(",", "")
              .replace("$", "").replace("%", "").replace(" ", ""))
    return float(limpio) if limpio else 0.0


def solo_digitos(txt) -> str:
    return "".join(ch for ch in str(txt) if ch.isdigit())


def esc(s) -> str:
    """Escapa texto para meterlo en un HTML."""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def lunes_de(d: date) -> date:
    return d - timedelta(days=d.weekday())


def dia_semana(iso: str) -> str:
    return DIAS_SEMANA[date.fromisoformat(iso).weekday()]


def fecha_larga(iso: str) -> str:
    """'2026-10-17' -> 'Sábado 17 de Octubre de 2026'."""
    d = date.fromisoformat(iso)
    return f"{DIAS_SEMANA[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}"


def dia_corto(iso: str) -> str:
    """'2026-10-17' -> 'Sábado 17/10'."""
    d = date.fromisoformat(iso)
    return f"{DIAS_SEMANA[d.weekday()]} {d.day}/{d.month}"
