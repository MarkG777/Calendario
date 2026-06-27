from __future__ import annotations

from datetime import date
from enum import StrEnum


class Frequency(StrEnum):
    SEMANAL = "semanal"
    QUINCENAL = "quincenal"
    MENSUAL = "mensual"

    def next_due_date(self, current: date) -> date:
        if self is Frequency.SEMANAL:
            return _add_days(current, 7)
        if self is Frequency.QUINCENAL:
            return _add_days(current, 14)
        return _add_months(current, 1)


def _add_days(d: date, days: int) -> date:
    from datetime import timedelta

    return d + timedelta(days=days)


def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, _days_in_month(year, month))
    return date(year, month, day)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month_first = date(year + 1, 1, 1)
    else:
        next_month_first = date(year, month + 1, 1)
    from datetime import timedelta

    return (next_month_first - timedelta(days=1)).day


class InstallmentStatus(StrEnum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    PARCIAL = "parcial"
    ATRASADO = "atrasado"


class LoanStatus(StrEnum):
    ACTIVO = "activo"
    LIQUIDADO = "liquidado"
