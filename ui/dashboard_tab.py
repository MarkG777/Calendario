from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data.repositories import BorrowerRepository, InstallmentRepository, LoanRepository
from domain.calculations import loan_irr
from domain.dashboard import (
    actual_collections,
    capital_outstanding,
    delinquency_rate,
    expected_collections,
    portfolio_irr,
    projected_gross_profit,
    realized_profit,
)


class DashboardTab(QWidget):
    def __init__(
        self,
        loan_repository: LoanRepository,
        installment_repository: InstallmentRepository,
        borrower_repository: BorrowerRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._loan_repository = loan_repository
        self._installment_repository = installment_repository
        self._borrower_repository = borrower_repository

        today = QDate.currentDate()
        week_start = today.addDays(-(today.dayOfWeek() - 1))
        week_end = week_start.addDays(6)

        self.from_date_input = QDateEdit(week_start)
        self.from_date_input.setCalendarPopup(True)
        self.to_date_input = QDateEdit(week_end)
        self.to_date_input.setCalendarPopup(True)

        refresh_button = QPushButton("Actualizar")
        refresh_button.clicked.connect(self.refresh)

        filters_row = QHBoxLayout()
        filters_row.addWidget(QLabel("Semana del:"))
        filters_row.addWidget(self.from_date_input)
        filters_row.addWidget(QLabel("al:"))
        filters_row.addWidget(self.to_date_input)
        filters_row.addWidget(refresh_button)
        filters_row.addStretch()

        self.capital_label = QLabel("—")
        self.expected_label = QLabel("—")
        self.actual_label = QLabel("—")
        self.delinquency_label = QLabel("—")
        self.projected_profit_label = QLabel("—")
        self.realized_profit_label = QLabel("—")
        self.portfolio_irr_label = QLabel("—")

        metrics_form = QFormLayout()
        metrics_form.addRow("Capital en la calle:", self.capital_label)
        metrics_form.addRow("Cobranza esperada (semana):", self.expected_label)
        metrics_form.addRow("Cobranza real (semana):", self.actual_label)
        metrics_form.addRow("Morosidad (cartera vencida):", self.delinquency_label)
        metrics_form.addRow("Ganancia proyectada:", self.projected_profit_label)
        metrics_form.addRow("Ganancia realizada:", self.realized_profit_label)
        metrics_form.addRow("TIR de la cartera:", self.portfolio_irr_label)

        metrics_box = QGroupBox("Métricas")
        metrics_box.setLayout(metrics_form)

        self.irr_table = QTableWidget(0, 2)
        self.irr_table.setHorizontalHeaderLabels(["Préstamo", "TIR del préstamo"])
        self.irr_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.irr_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.irr_table.setAlternatingRowColors(True)
        self.irr_table.verticalHeader().setVisible(False)

        irr_box = QGroupBox("TIR por préstamo")
        irr_layout = QVBoxLayout()
        irr_layout.addWidget(self.irr_table)
        irr_box.setLayout(irr_layout)

        layout = QVBoxLayout(self)
        layout.addLayout(filters_row)
        layout.addWidget(metrics_box)
        layout.addWidget(irr_box)

        self.refresh()

    def refresh(self) -> None:
        loans = self._loan_repository.list_all()
        all_installments = self._installment_repository.list_all()
        start_date = self.from_date_input.date().toPython()
        end_date = self.to_date_input.date().toPython()
        due_this_week = self._installment_repository.list_due_between(start_date, end_date)
        today = date.today()

        self.capital_label.setText(str(capital_outstanding(loans, all_installments)))
        self.expected_label.setText(str(expected_collections(due_this_week)))
        self.actual_label.setText(
            str(actual_collections(all_installments, start_date, end_date))
        )
        rate = delinquency_rate(all_installments, today) * 100
        self.delinquency_label.setText(f"{rate:.2f}%")
        self.projected_profit_label.setText(str(projected_gross_profit(loans)))
        self.realized_profit_label.setText(str(realized_profit(loans, all_installments)))
        self.portfolio_irr_label.setText(f"{portfolio_irr(loans) * 100:.2f}%")

        borrower_name_by_id = {b.id: b.name for b in self._borrower_repository.list_all()}
        self.irr_table.setRowCount(len(loans))
        for row, loan in enumerate(loans):
            borrower_name = borrower_name_by_id.get(loan.borrower_id, "—")
            self.irr_table.setItem(row, 0, QTableWidgetItem(borrower_name))
            self.irr_table.setItem(row, 1, QTableWidgetItem(f"{loan_irr(loan) * 100:.2f}%"))
