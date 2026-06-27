from __future__ import annotations

from datetime import date
from decimal import Decimal

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QGridLayout,
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
from ui.icons import icon

ZERO = Decimal("0")


class MetricCard(QFrame):
    def __init__(
        self,
        title: str,
        value: str = "—",
        value_class: str = "card-value",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("cssClass", "card")
        self.setFixedHeight(110)

        self._title_label = QLabel(title)
        self._title_label.setProperty("cssClass", "card-title")
        self._title_label.setAlignment(Qt.AlignLeft)

        self._value_label = QLabel(value)
        self._value_label.setProperty("cssClass", value_class)
        self._value_label.setAlignment(Qt.AlignLeft)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        layout.addWidget(self._title_label)
        layout.addWidget(self._value_label)
        layout.addStretch()

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)

    def set_value_class(self, css_class: str) -> None:
        self._value_label.setProperty("cssClass", css_class)
        self._value_label.style().unpolish(self._value_label)
        self._value_label.style().polish(self._value_label)


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
        self.from_date_input.setToolTip("Fecha de inicio del período a analizar")
        self.to_date_input = QDateEdit(week_end)
        self.to_date_input.setCalendarPopup(True)
        self.to_date_input.setToolTip("Fecha de fin del período a analizar")

        refresh_button = QPushButton(icon("refresh", "#ffffff"), "Actualizar")
        refresh_button.setToolTip("Recalcular métricas con el rango de fechas seleccionado")
        refresh_button.clicked.connect(self.refresh)

        filters_row = QHBoxLayout()
        filters_row.addWidget(QLabel("Período del:"))
        filters_row.addWidget(self.from_date_input)
        filters_row.addWidget(QLabel("al:"))
        filters_row.addWidget(self.to_date_input)
        filters_row.addWidget(refresh_button)
        filters_row.addStretch()

        self._capital_card = MetricCard("Capital en la calle")
        self._expected_card = MetricCard("Cobranza esperada (período)")
        self._actual_card = MetricCard("Cobranza real (período)")
        self._delinquency_card = MetricCard("Morosidad (cartera vencida)")
        self._projected_card = MetricCard("Ganancia proyectada", value_class="card-value-success")
        self._realized_card = MetricCard("Ganancia realizada", value_class="card-value-accent")
        self._irr_card = MetricCard("TIR de la cartera", value_class="card-value-accent")

        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.addWidget(self._capital_card, 0, 0)
        cards_layout.addWidget(self._expected_card, 0, 1)
        cards_layout.addWidget(self._actual_card, 0, 2)
        cards_layout.addWidget(self._delinquency_card, 0, 3)
        cards_layout.addWidget(self._projected_card, 1, 0)
        cards_layout.addWidget(self._realized_card, 1, 1)
        cards_layout.addWidget(self._irr_card, 1, 2)

        cards_container = QWidget()
        cards_container_layout = QVBoxLayout(cards_container)
        cards_container_layout.setContentsMargins(0, 0, 0, 0)
        cards_container_layout.addLayout(cards_layout)

        self.irr_table = QTableWidget(0, 2)
        self.irr_table.setHorizontalHeaderLabels(["Deudor", "TIR del préstamo"])
        self.irr_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.irr_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.irr_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.irr_table.setAlternatingRowColors(True)
        self.irr_table.verticalHeader().setVisible(False)

        irr_box = QGroupBox("TIR por préstamo")
        irr_layout = QVBoxLayout()
        irr_layout.addWidget(self.irr_table)
        irr_box.setLayout(irr_layout)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addLayout(filters_row)
        layout.addWidget(cards_container)
        layout.addWidget(irr_box)
        layout.addStretch()

        self.refresh()

    def refresh(self) -> None:
        loans = self._loan_repository.list_all()
        all_installments = self._installment_repository.list_all()
        start_date = self.from_date_input.date().toPython()
        end_date = self.to_date_input.date().toPython()
        due_in_period = self._installment_repository.list_due_between(start_date, end_date)
        today = date.today()

        capital = capital_outstanding(loans, all_installments)
        expected = expected_collections(due_in_period)
        actual = actual_collections(all_installments, start_date, end_date)
        rate = delinquency_rate(all_installments, today) * 100
        projected = projected_gross_profit(loans)
        realized = realized_profit(loans, all_installments)
        irr = portfolio_irr(loans)

        self._capital_card.set_value(f"${capital:,.2f}")
        self._expected_card.set_value(f"${expected:,.2f}")
        self._actual_card.set_value(f"${actual:,.2f}")

        if rate > 20:
            self._delinquency_card.set_value_class("card-value-error")
        elif rate > 10:
            self._delinquency_card.set_value_class("card-value")
        else:
            self._delinquency_card.set_value_class("card-value-success")
        self._delinquency_card.set_value(f"{rate:.2f}%")

        self._projected_card.set_value(f"${projected:,.2f}")
        self._realized_card.set_value(f"${realized:,.2f}")
        self._irr_card.set_value(f"{irr * 100:.2f}%")

        borrower_name_by_id = {b.id: b.name for b in self._borrower_repository.list_all()}
        self.irr_table.setRowCount(len(loans))
        for row, loan in enumerate(loans):
            borrower_name = borrower_name_by_id.get(loan.borrower_id, "—")
            self.irr_table.setItem(row, 0, QTableWidgetItem(borrower_name))
            self.irr_table.setItem(row, 1, QTableWidgetItem(f"{loan_irr(loan) * 100:.2f}%"))
