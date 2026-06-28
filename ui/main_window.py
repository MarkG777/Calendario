from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QToolBar,
)

from data.repositories import (
    BorrowerRepository,
    InstallmentRepository,
    LoanRepository,
    PaymentRepository,
)
from ui.borrowers_tab import BorrowersTab
from ui.collections_tab import CollectionsTab
from ui.dashboard_tab import DashboardTab
from ui.loans_tab import LoansTab
from ui.theme import toggle_theme


class MainWindow(QMainWindow):
    def __init__(
        self,
        borrower_repository: BorrowerRepository,
        loan_repository: LoanRepository,
        installment_repository: InstallmentRepository,
        payment_repository: PaymentRepository,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Control de Cobros")
        self.resize(1100, 720)
        self.setMinimumSize(800, 500)

        self._borrower_repository = borrower_repository
        self._loan_repository = loan_repository
        self._installment_repository = installment_repository
        self._payment_repository = payment_repository

        self._tabs = QTabWidget()
        self._borrowers_tab = BorrowersTab(borrower_repository)
        self._loans_tab = LoansTab(loan_repository, borrower_repository)
        self._collections_tab = CollectionsTab(
            installment_repository, loan_repository, borrower_repository, payment_repository
        )
        self._dashboard_tab = DashboardTab(
            loan_repository, installment_repository, borrower_repository
        )

        self._tabs.addTab(self._borrowers_tab, "👤 Clientes")
        self._tabs.addTab(self._loans_tab, "💰 Préstamos")
        self._tabs.addTab(self._collections_tab, "📅 Calendario de cobros")
        self._tabs.addTab(self._dashboard_tab, "📊 Dashboard")
        self._tabs.currentChanged.connect(self._on_tab_changed)

        self.setCentralWidget(self._tabs)

        self._build_toolbar()
        self._build_statusbar()
        self._build_shortcuts()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Barra principal")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(toolbar.iconSize())
        self.addToolBar(toolbar)

        self._theme_action = QAction("☀️ Modo oscuro", self)
        self._theme_action.setToolTip("Cambiar entre modo claro y oscuro")
        self._theme_action.triggered.connect(self._toggle_theme)
        toolbar.addAction(self._theme_action)

        toolbar.addSeparator()

        refresh_action = QAction("🔄 Refrescar (F5)", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self._refresh_current_tab)
        toolbar.addAction(refresh_action)

    def _build_statusbar(self) -> None:
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status_label = QLabel("Listo")
        self._status.addWidget(self._status_label, 1)
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._reset_status)

    def _build_shortcuts(self) -> None:
        new_borrower = QAction(self)
        new_borrower.setShortcut(QKeySequence("Ctrl+N"))
        new_borrower.triggered.connect(self._new_borrower)
        self.addAction(new_borrower)

        new_loan = QAction(self)
        new_loan.setShortcut(QKeySequence("Ctrl+P"))
        new_loan.triggered.connect(self._new_loan)
        self.addAction(new_loan)

    def _toggle_theme(self) -> None:
        app = QApplication.instance()
        if app is None:
            return
        new_mode = toggle_theme(app)
        if new_mode == "dark":
            self._theme_action.setText("🌙 Modo claro")
        else:
            self._theme_action.setText("☀️ Modo oscuro")
        # Re-apply calendar colors with new theme palette
        self._collections_tab.refresh()
        self.show_status(f"Tema cambiado a {new_mode}", "info")

    def _on_tab_changed(self, _index: int) -> None:
        self._refresh_current_tab()

    def _refresh_current_tab(self) -> None:
        widget = self._tabs.currentWidget()
        if hasattr(widget, "refresh"):
            widget.refresh()
        self.show_status("Datos actualizados", "success")

    def _new_borrower(self) -> None:
        self._tabs.setCurrentWidget(self._borrowers_tab)
        self._borrowers_tab.open_new_borrower_dialog()

    def _new_loan(self) -> None:
        self._tabs.setCurrentWidget(self._loans_tab)
        self._loans_tab.open_new_loan_dialog()

    def show_status(self, message: str, kind: str = "info") -> None:
        self._status.setProperty("cssClass", kind if kind in ("error", "success") else "")
        self._status_label.setText(message)
        self._status.style().unpolish(self._status)
        self._status.style().polish(self._status)
        self._status_timer.start(4000)

    def _reset_status(self) -> None:
        self._status.setProperty("cssClass", "")
        self._status.style().unpolish(self._status)
        self._status.style().polish(self._status)
        self._status_label.setText("Listo")
