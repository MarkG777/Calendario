from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

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
        self.resize(1000, 650)

        tabs = QTabWidget()
        tabs.addTab(BorrowersTab(borrower_repository), "Deudores")
        tabs.addTab(LoansTab(loan_repository, borrower_repository), "Préstamos")
        tabs.addTab(
            CollectionsTab(
                installment_repository, loan_repository, borrower_repository, payment_repository
            ),
            "Calendario de cobros",
        )
        tabs.addTab(
            DashboardTab(loan_repository, installment_repository, borrower_repository),
            "Dashboard",
        )
        self.setCentralWidget(tabs)
