from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from data.repositories import BorrowerRepository
from domain.entities import Loan
from domain.enums import Frequency, LoanStatus
from domain.schedule import calculate_installment_amount, generate_schedule

_FREQUENCY_LABELS = {
    Frequency.SEMANAL: "Semanal",
    Frequency.QUINCENAL: "Quincenal",
    Frequency.MENSUAL: "Mensual",
}


class NewLoanDialog(QDialog):
    def __init__(
        self, borrower_repository: BorrowerRepository, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nuevo préstamo")

        self._borrowers = borrower_repository.list_all()

        self.borrower_combo = QComboBox()
        self.borrower_combo.setToolTip("Selecciona el deudor al que se le otorga el préstamo")
        for borrower in self._borrowers:
            self.borrower_combo.addItem(borrower.name, borrower.id)

        self.principal_input = QLineEdit("10000")
        self.principal_input.setToolTip("Capital que se entrega al deudor (debe ser mayor a 0)")
        self.total_due_input = QLineEdit("14000")
        self.total_due_input.setToolTip(
            "Total a cobrar: capital + ganancia. Debe ser mayor al capital."
        )

        self.num_installments_input = QSpinBox()
        self.num_installments_input.setRange(1, 520)
        self.num_installments_input.setValue(14)
        self.num_installments_input.setToolTip("Número de cuotas en las que se divide el préstamo")

        self.frequency_combo = QComboBox()
        self.frequency_combo.setToolTip(
            "Frecuencia de pago: semanal (cada 7 días), "
            "quincenal (cada 14 días), mensual (cada mes)"
        )
        for frequency, label in _FREQUENCY_LABELS.items():
            self.frequency_combo.addItem(label, frequency.value)

        self.start_date_input = QDateEdit(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setToolTip(
            "Fecha en que se otorga el préstamo. "
            "Las cuotas empiezan a contar desde aquí."
        )

        self.quota_label = QLabel("Cuota calculada: —")

        self.total_due_input.textChanged.connect(self._update_quota_preview)
        self.num_installments_input.valueChanged.connect(self._update_quota_preview)
        self.principal_input.textChanged.connect(self._validate_principal)
        self.total_due_input.textChanged.connect(self._validate_total_due)

        form = QFormLayout()
        form.addRow("Deudor*:", self.borrower_combo)
        form.addRow("Capital:", self.principal_input)
        form.addRow("Total a cobrar:", self.total_due_input)
        form.addRow("Número de cuotas:", self.num_installments_input)
        form.addRow("Frecuencia:", self.frequency_combo)
        form.addRow("Fecha de inicio:", self.start_date_input)
        form.addRow(self.quota_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self._update_quota_preview()

    def _validate_principal(self) -> None:
        value = self._parse_decimal(self.principal_input.text())
        if value is None or value <= 0:
            self.principal_input.setProperty("cssClass", "invalid")
        else:
            self.principal_input.setProperty("cssClass", "")
        self.principal_input.style().unpolish(self.principal_input)
        self.principal_input.style().polish(self.principal_input)

    def _validate_total_due(self) -> None:
        value = self._parse_decimal(self.total_due_input.text())
        principal = self._parse_decimal(self.principal_input.text())
        if value is None or value <= 0 or (principal and value < principal):
            self.total_due_input.setProperty("cssClass", "invalid")
        else:
            self.total_due_input.setProperty("cssClass", "")
        self.total_due_input.style().unpolish(self.total_due_input)
        self.total_due_input.style().polish(self.total_due_input)

    def _update_quota_preview(self) -> None:
        total_due = self._parse_decimal(self.total_due_input.text())
        num_installments = self.num_installments_input.value()
        if total_due is None or num_installments <= 0:
            self.quota_label.setText("Cuota calculada: —")
            return
        quota = calculate_installment_amount(total_due, num_installments)
        self.quota_label.setText(f"Cuota calculada: {quota}")

    @staticmethod
    def _parse_decimal(text: str) -> Decimal | None:
        try:
            return Decimal(text.strip())
        except (InvalidOperation, ValueError):
            return None

    def _on_accept(self) -> None:
        if self.borrower_combo.currentIndex() < 0:
            QMessageBox.warning(
                self,
                "Falta un deudor",
                "Primero debes dar de alta un deudor en la pestaña \"Deudores\" "
                "antes de poder crear un préstamo.",
            )
            return
        principal = self._parse_decimal(self.principal_input.text())
        if principal is None or principal <= 0:
            QMessageBox.warning(self, "Capital inválido", "Ingresa un capital numérico mayor a 0.")
            self.principal_input.setFocus()
            return
        total_due = self._parse_decimal(self.total_due_input.text())
        if total_due is None or total_due <= 0:
            QMessageBox.warning(
                self, "Total a cobrar inválido", "Ingresa un total a cobrar numérico mayor a 0."
            )
            self.total_due_input.setFocus()
            return
        self.accept()

    def build_loan_and_schedule(self) -> tuple[Loan, list]:
        principal = self._parse_decimal(self.principal_input.text())
        total_due = self._parse_decimal(self.total_due_input.text())
        num_installments = self.num_installments_input.value()
        frequency = Frequency(self.frequency_combo.currentData())
        start_date: date = self.start_date_input.date().toPython()
        borrower_id = self.borrower_combo.currentData()

        installment_amount = calculate_installment_amount(total_due, num_installments)
        loan = Loan(
            borrower_id=borrower_id,
            principal=principal,
            total_due=total_due,
            start_date=start_date,
            num_installments=num_installments,
            frequency=frequency,
            installment_amount=installment_amount,
            status=LoanStatus.ACTIVO,
        )
        installments = generate_schedule(
            principal=principal,
            total_due=total_due,
            num_installments=num_installments,
            frequency=frequency,
            start_date=start_date,
        )
        return loan, installments
