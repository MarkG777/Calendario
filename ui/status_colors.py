from __future__ import annotations

from PySide6.QtGui import QColor

from domain.enums import InstallmentStatus
from ui.theme import palette_colors

_STATUS_KEYS: dict[InstallmentStatus, tuple[str, str]] = {
    InstallmentStatus.PAGADO: ("status_pagado_bg", "status_pagado_fg"),
    InstallmentStatus.PENDIENTE: ("status_pendiente_bg", "status_pendiente_fg"),
    InstallmentStatus.PARCIAL: ("status_parcial_bg", "status_parcial_fg"),
    InstallmentStatus.ATRASADO: ("status_atrasado_bg", "status_atrasado_fg"),
}

# Orden de urgencia: lo mas urgente manda al colorear un dia con varias cuotas.
_STATUS_PRIORITY = [
    InstallmentStatus.ATRASADO,
    InstallmentStatus.PARCIAL,
    InstallmentStatus.PENDIENTE,
    InstallmentStatus.PAGADO,
]


def status_colors() -> dict[InstallmentStatus, tuple[QColor, QColor]]:
    p = palette_colors()
    result: dict[InstallmentStatus, tuple[QColor, QColor]] = {}
    for status, (bg_key, fg_key) in _STATUS_KEYS.items():
        result[status] = (QColor(p[bg_key]), QColor(p[fg_key]))
    return result


def status_background(status: InstallmentStatus) -> QColor:
    p = palette_colors()
    return QColor(p[_STATUS_KEYS[status][0]])


def status_foreground(status: InstallmentStatus) -> QColor:
    p = palette_colors()
    return QColor(p[_STATUS_KEYS[status][1]])


def worst_status(statuses: list[InstallmentStatus]) -> InstallmentStatus:
    for candidate in _STATUS_PRIORITY:
        if candidate in statuses:
            return candidate
    return InstallmentStatus.PENDIENTE
