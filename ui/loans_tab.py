from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data.repositories import BorrowerRepository, LoanRepository
from ui.loan_dialog import NewLoanDialog


class LoansTab(QWidget):
    def __init__(
        self,
        loan_repository: LoanRepository,
        borrower_repository: BorrowerRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._loan_repository = loan_repository
        self._borrower_repository = borrower_repository

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Deudor", "Capital", "Total a cobrar", "Cuota", "Estado"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        new_button = QPushButton("Nuevo préstamo")
        new_button.clicked.connect(self._open_new_loan_dialog)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(new_button)
        buttons_row.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(buttons_row)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        borrowers_by_id = {b.id: b for b in self._borrower_repository.list_all()}
        loans = self._loan_repository.list_all()
        self.table.setRowCount(len(loans))
        for row, loan in enumerate(loans):
            borrower = borrowers_by_id.get(loan.borrower_id)
            borrower_name = borrower.name if borrower else "—"
            self.table.setItem(row, 0, QTableWidgetItem(borrower_name))
            self.table.setItem(row, 1, QTableWidgetItem(str(loan.principal)))
            self.table.setItem(row, 2, QTableWidgetItem(str(loan.total_due)))
            self.table.setItem(row, 3, QTableWidgetItem(str(loan.installment_amount)))
            self.table.setItem(row, 4, QTableWidgetItem(loan.status.value))

    def _open_new_loan_dialog(self) -> None:
        dialog = NewLoanDialog(self._borrower_repository, self)
        if dialog.exec() == QDialog.Accepted:
            try:
                loan, installments = dialog.build_loan_and_schedule()
                self._loan_repository.add(loan, installments)
            except Exception as error:
                QMessageBox.critical(self, "No se pudo guardar el préstamo", str(error))
                return
            self.refresh()
