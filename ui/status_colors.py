from __future__ import annotations

from PySide6.QtGui import QColor

from domain.enums import InstallmentStatus

STATUS_COLORS: dict[InstallmentStatus, QColor] = {
    InstallmentStatus.PAGADO: QColor("#a8e6a1"),
    InstallmentStatus.PENDIENTE: QColor("#fff3a3"),
    InstallmentStatus.PARCIAL: QColor("#ffcc80"),
    InstallmentStatus.ATRASADO: QColor("#f5a3a3"),
}

# Orden de urgencia: lo mas urgente manda al colorear un dia con varias cuotas.
_STATUS_PRIORITY = [
    InstallmentStatus.ATRASADO,
    InstallmentStatus.PARCIAL,
    InstallmentStatus.PENDIENTE,
    InstallmentStatus.PAGADO,
]


def worst_status(statuses: list[InstallmentStatus]) -> InstallmentStatus:
    for candidate in _STATUS_PRIORITY:
        if candidate in statuses:
            return candidate
    return InstallmentStatus.PENDIENTE
