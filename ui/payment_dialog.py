from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from domain.calculations import outstanding_balance
from domain.entities import Installment, Payment


class PaymentDialog(QDialog):
    def __init__(self, installment: Installment, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Registrar cobro")
        self._installment = installment

        balance = outstanding_balance(installment)

        self.scheduled_label = QLabel(str(installment.scheduled_amount))
        self.balance_label = QLabel(str(balance))
        self.amount_input = QLineEdit(str(balance))
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.method_input = QLineEdit()
        self.notes_input = QLineEdit()

        form = QFormLayout()
        form.addRow("Monto programado:", self.scheduled_label)
        form.addRow("Saldo pendiente:", self.balance_label)
        form.addRow("Monto a pagar*:", self.amount_input)
        form.addRow("Fecha de pago:", self.date_input)
        form.addRow("Método:", self.method_input)
        form.addRow("Notas:", self.notes_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    @staticmethod
    def _parse_decimal(text: str) -> Decimal | None:
        try:
            return Decimal(text.strip())
        except (InvalidOperation, ValueError):
            return None

    def _on_accept(self) -> None:
        amount = self._parse_decimal(self.amount_input.text())
        if amount is None or amount <= 0:
            QMessageBox.warning(self, "Monto inválido", "Ingresa un monto numérico mayor a 0.")
            self.amount_input.setFocus()
            return
        self.accept()

    def payment(self) -> Payment:
        payment_date: date = self.date_input.date().toPython()
        return Payment(
            installment_id=self._installment.id,
            payment_date=payment_date,
            amount_paid=self._parse_decimal(self.amount_input.text()),
            method=self.method_input.text().strip(),
            notes=self.notes_input.text().strip(),
        )
