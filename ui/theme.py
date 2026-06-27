from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

# ---------------------------------------------------------------------------
# Color palettes
# ---------------------------------------------------------------------------

_LIGHT = {
    "accent": "#3b82f6",
    "accent_hover": "#2563eb",
    "accent_pressed": "#1d4ed8",
    "accent_text": "#1e40af",
    "bg": "#f1f5f9",
    "surface": "#ffffff",
    "surface_alt": "#f8fafc",
    "border": "#e2e8f0",
    "border_focus": "#3b82f6",
    "text": "#1e293b",
    "text_secondary": "#64748b",
    "table_alt": "#f8fafc",
    "header_bg": "#f1f5f9",
    "hover": "#e0e7ef",
    "disabled_bg": "#cbd5e1",
    "disabled_text": "#f1f5f9",
    "error": "#ef4444",
    "error_bg": "#fef2f2",
    "success": "#22c55e",
    "success_bg": "#f0fdf4",
    "warning": "#f59e0b",
    "warning_bg": "#fffbeb",
    "card_shadow": "rgba(0,0,0,0.06)",
    "scrollbar": "#cbd5e1",
    "scrollbar_hover": "#94a3b8",
    # Status colors for calendar and tables (light mode: pastel backgrounds, dark text)
    "status_pagado_bg": "#86efac",
    "status_pagado_fg": "#14532d",
    "status_pendiente_bg": "#fde047",
    "status_pendiente_fg": "#713f12",
    "status_parcial_bg": "#fdba74",
    "status_parcial_fg": "#7c2d12",
    "status_atrasado_bg": "#fca5a5",
    "status_atrasado_fg": "#7f1d1d",
    # Calendar grid
    "calendar_grid": "#e2e8f0",
    "calendar_weekend": "#f1f5f9",
    "calendar_header_text": "#1e293b",
}

_DARK = {
    "accent": "#60a5fa",
    "accent_hover": "#3b82f6",
    "accent_pressed": "#2563eb",
    "accent_text": "#93c5fd",
    "bg": "#0f172a",
    "surface": "#1e293b",
    "surface_alt": "#334155",
    "border": "#334155",
    "border_focus": "#60a5fa",
    "text": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "table_alt": "#1e293b",
    "header_bg": "#334155",
    "hover": "#334155",
    "disabled_bg": "#475569",
    "disabled_text": "#64748b",
    "error": "#f87171",
    "error_bg": "#450a0a",
    "success": "#4ade80",
    "success_bg": "#052e16",
    "warning": "#fbbf24",
    "warning_bg": "#451a03",
    "card_shadow": "rgba(0,0,0,0.3)",
    "scrollbar": "#475569",
    "scrollbar_hover": "#64748b",
    # Status colors for calendar and tables (dark mode: vivid backgrounds, white text)
    "status_pagado_bg": "#16a34a",
    "status_pagado_fg": "#ffffff",
    "status_pendiente_bg": "#eab308",
    "status_pendiente_fg": "#ffffff",
    "status_parcial_bg": "#ea580c",
    "status_parcial_fg": "#ffffff",
    "status_atrasado_bg": "#dc2626",
    "status_atrasado_fg": "#ffffff",
    # Calendar grid
    "calendar_grid": "#334155",
    "calendar_weekend": "#1e293b",
    "calendar_header_text": "#e2e8f0",
}

_current_palette: dict[str, str] = _LIGHT
_current_mode: str = "light"


def _build_stylesheet(p: dict[str, str]) -> str:
    return f"""
    /* ---- Base ---- */
    QMainWindow, QWidget {{
        background-color: {p["bg"]};
        color: {p["text"]};
        font-family: "Segoe UI", "SF Pro Display", "Inter", sans-serif;
        font-size: 10pt;
    }}

    /* ---- Tabs ---- */
    QTabWidget::pane {{
        border: 1px solid {p["border"]};
        border-radius: 8px;
        background-color: {p["surface"]};
        top: -1px;
    }}

    QTabBar::tab {{
        background-color: {p["bg"]};
        border: 1px solid {p["border"]};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 10px 20px;
        margin-right: 3px;
        color: {p["text_secondary"]};
        font-size: 10pt;
    }}

    QTabBar::tab:selected {{
        background-color: {p["surface"]};
        color: {p["accent"]};
        font-weight: 600;
    }}

    QTabBar::tab:hover:!selected {{
        background-color: {p["hover"]};
        color: {p["text"]};
    }}

    /* ---- Buttons ---- */
    QPushButton {{
        background-color: {p["accent"]};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 18px;
        font-weight: 500;
        font-size: 10pt;
    }}

    QPushButton:hover {{
        background-color: {p["accent_hover"]};
    }}

    QPushButton:pressed {{
        background-color: {p["accent_pressed"]};
    }}

    QPushButton:disabled {{
        background-color: {p["disabled_bg"]};
        color: {p["disabled_text"]};
    }}

    /* Secondary / flat button style via property */
    QPushButton[cssClass="secondary"] {{
        background-color: transparent;
        color: {p["accent"]};
        border: 1px solid {p["accent"]};
    }}

    QPushButton[cssClass="secondary"]:hover {{
        background-color: {p["surface_alt"]};
    }}

    /* ---- Tables ---- */
    QTableWidget {{
        background-color: {p["surface"]};
        alternate-background-color: {p["table_alt"]};
        gridline-color: {p["border"]};
        border: 1px solid {p["border"]};
        border-radius: 8px;
        selection-background-color: {p["accent"]};
        selection-color: white;
        font-size: 10pt;
    }}

    QHeaderView::section {{
        background-color: {p["header_bg"]};
        color: {p["text"]};
        padding: 8px 6px;
        border: none;
        border-bottom: 2px solid {p["border"]};
        font-weight: 600;
        font-size: 10pt;
    }}

    /* ---- Inputs ---- */
    QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit, QPlainTextEdit {{
        background-color: {p["surface"]};
        border: 1px solid {p["border"]};
        border-radius: 6px;
        padding: 6px 8px;
        color: {p["text"]};
        selection-background-color: {p["accent"]};
        selection-color: white;
    }}

    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus,
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 2px solid {p["border_focus"]};
        padding: 5px 7px;
    }}

    /* Invalid input — set via dynamic property */
    QLineEdit[cssClass="invalid"] {{
        border: 2px solid {p["error"]};
        background-color: {p["error_bg"]};
    }}

    /* ---- GroupBox ---- */
    QGroupBox {{
        border: 1px solid {p["border"]};
        border-radius: 8px;
        margin-top: 12px;
        padding: 16px 8px 8px 8px;
        font-weight: 600;
        font-size: 10pt;
        color: {p["text"]};
        background-color: {p["surface"]};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: {p["accent_text"]};
    }}

    /* ---- Labels ---- */
    QLabel {{
        color: {p["text"]};
        background: transparent;
    }}

    QLabel[cssClass="card-title"] {{
        color: {p["text_secondary"]};
        font-size: 9pt;
        font-weight: 500;
    }}

    QLabel[cssClass="card-value"] {{
        color: {p["text"]};
        font-size: 18pt;
        font-weight: 700;
    }}

    QLabel[cssClass="card-value-accent"] {{
        color: {p["accent"]};
        font-size: 18pt;
        font-weight: 700;
    }}

    QLabel[cssClass="card-value-success"] {{
        color: {p["success"]};
        font-size: 18pt;
        font-weight: 700;
    }}

    QLabel[cssClass="card-value-error"] {{
        color: {p["error"]};
        font-size: 18pt;
        font-weight: 700;
    }}

    /* ---- Calendar ---- */
    QCalendarWidget QToolButton {{
        background-color: {p["surface"]};
        color: {p["text"]};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 10pt;
        font-weight: 500;
    }}

    QCalendarWidget QToolButton:hover {{
        background-color: {p["hover"]};
        color: {p["accent"]};
    }}

    QCalendarWidget QToolButton::menu-indicator {{
        image: none;
    }}

    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {p["surface"]};
        border-bottom: 1px solid {p["border"]};
    }}

    QCalendarWidget QAbstractItemView {{
        background-color: {p["surface"]};
        color: {p["text"]};
        selection-background-color: {p["accent"]};
        selection-color: white;
        border: 1px solid {p["border"]};
        gridline-color: {p["calendar_grid"]};
    }}

    /* Calendar day header (row of day names) */
    QCalendarWidget QAbstractItemView::item {{
        padding: 2px;
        border: none;
    }}

    /* QDateEdit dropdown calendar — inherits QCalendarWidget styles */
    QDateEdit QCalendarWidget QAbstractItemView {{
        background-color: {p["surface"]};
        color: {p["text"]};
    }}

    /* ---- Scroll bars ---- */
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {p["scrollbar"]};
        border-radius: 5px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {p["scrollbar_hover"]};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
        margin: 0;
    }}

    QScrollBar::handle:horizontal {{
        background: {p["scrollbar"]};
        border-radius: 5px;
        min-width: 30px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {p["scrollbar_hover"]};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ---- StatusBar ---- */
    QStatusBar {{
        background-color: {p["surface"]};
        color: {p["text_secondary"]};
        border-top: 1px solid {p["border"]};
        font-size: 9pt;
    }}

    QStatusBar[cssClass="error"] {{
        color: {p["error"]};
    }}

    QStatusBar[cssClass="success"] {{
        color: {p["success"]};
    }}

    /* ---- Menu ---- */
    QMenu {{
        background-color: {p["surface"]};
        border: 1px solid {p["border"]};
        border-radius: 8px;
        padding: 4px;
    }}

    QMenu::item {{
        padding: 6px 24px;
        border-radius: 4px;
    }}

    QMenu::item:selected {{
        background-color: {p["accent"]};
        color: white;
    }}

    /* ---- Tooltips ---- */
    QToolTip {{
        background-color: {p["surface_alt"]};
        color: {p["text"]};
        border: 1px solid {p["border"]};
        border-radius: 6px;
        padding: 6px 8px;
        font-size: 9pt;
    }}

    /* ---- ComboBox dropdown ---- */
    QComboBox QAbstractItemView {{
        background-color: {p["surface"]};
        border: 1px solid {p["border"]};
        border-radius: 6px;
        selection-background-color: {p["accent"]};
        selection-color: white;
        padding: 4px;
    }}

    /* ---- Frame for cards ---- */
    QFrame[cssClass="card"] {{
        background-color: {p["surface"]};
        border: 1px solid {p["border"]};
        border-radius: 10px;
    }}
    """


def _apply_palette(app: QApplication, p: dict[str, str]) -> None:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(p["bg"]))
    palette.setColor(QPalette.WindowText, QColor(p["text"]))
    palette.setColor(QPalette.Base, QColor(p["surface"]))
    palette.setColor(QPalette.AlternateBase, QColor(p["table_alt"]))
    palette.setColor(QPalette.Text, QColor(p["text"]))
    palette.setColor(QPalette.Button, QColor(p["surface"]))
    palette.setColor(QPalette.ButtonText, QColor(p["text"]))
    palette.setColor(QPalette.Highlight, QColor(p["accent"]))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipBase, QColor(p["surface_alt"]))
    palette.setColor(QPalette.ToolTipText, QColor(p["text"]))
    palette.setColor(QPalette.PlaceholderText, QColor(p["text_secondary"]))
    app.setPalette(palette)


def apply_theme(app: QApplication, mode: str = "light") -> None:
    global _current_palette, _current_mode
    if mode == "dark":
        _current_palette = _DARK
        _current_mode = "dark"
    else:
        _current_palette = _LIGHT
        _current_mode = "light"

    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(_build_stylesheet(_current_palette))
    _apply_palette(app, _current_palette)


def toggle_theme(app: QApplication) -> str:
    new_mode = "dark" if _current_mode == "light" else "light"
    apply_theme(app, new_mode)
    return new_mode


def current_mode() -> str:
    return _current_mode


def palette_colors() -> dict[str, str]:
    return _current_palette
