from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

_ACCENT = "#2f6fed"
_ACCENT_DARK = "#2456bd"
_BG = "#f5f6fa"
_SURFACE = "#ffffff"
_BORDER = "#d7dbe3"
_TEXT = "#2b2f38"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {_BG};
    color: {_TEXT};
}}

QTabWidget::pane {{
    border: 1px solid {_BORDER};
    border-radius: 6px;
    background-color: {_SURFACE};
    top: -1px;
}}

QTabBar::tab {{
    background-color: {_BG};
    border: 1px solid {_BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {_SURFACE};
    color: {_ACCENT};
    font-weight: 600;
}}

QTabBar::tab:hover {{
    background-color: #e9edf5;
}}

QPushButton {{
    background-color: {_ACCENT};
    color: white;
    border: none;
    border-radius: 5px;
    padding: 6px 14px;
}}

QPushButton:hover {{
    background-color: {_ACCENT_DARK};
}}

QPushButton:pressed {{
    background-color: #1d4ba0;
}}

QPushButton:disabled {{
    background-color: #b7c2d6;
    color: #eef1f6;
}}

QTableWidget {{
    background-color: {_SURFACE};
    alternate-background-color: #eef1f8;
    gridline-color: {_BORDER};
    border: 1px solid {_BORDER};
    border-radius: 4px;
    selection-background-color: {_ACCENT};
    selection-color: white;
}}

QHeaderView::section {{
    background-color: #eef1f8;
    color: {_TEXT};
    padding: 6px;
    border: none;
    border-bottom: 1px solid {_BORDER};
    font-weight: 600;
}}

QLineEdit, QComboBox, QDateEdit, QSpinBox {{
    background-color: {_SURFACE};
    border: 1px solid {_BORDER};
    border-radius: 4px;
    padding: 4px 6px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {{
    border: 1px solid {_ACCENT};
}}

QGroupBox {{
    border: 1px solid {_BORDER};
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}

QCalendarWidget QToolButton {{
    background-color: {_SURFACE};
    border-radius: 4px;
    padding: 4px 8px;
}}

QCalendarWidget QToolButton:hover {{
    background-color: #e9edf5;
}}

QCalendarWidget QWidget#qt_calendar_navigationbar {{
    background-color: {_BG};
    border-bottom: 1px solid {_BORDER};
}}
"""


def apply_theme(app: QApplication) -> None:
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(STYLESHEET)
