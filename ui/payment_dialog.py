from __future__ import annotations

import re
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
        self.setWindowTitle("💵 Registrar cobro")
        self._installment = installment

        balance = outstanding_balance(installment)

        self.scheduled_label = QLabel(str(installment.scheduled_amount))
        self.balance_label = QLabel(str(balance))
        self.amount_input = QLineEdit(str(balance))
        self.amount_input.setToolTip(
            "Monto a pagar. Puede ser un abono parcial o el saldo completo."
        )
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setToolTip("Fecha en que se realiza el pago")
        self.method_input = QLineEdit()
        self.method_input.setToolTip("Método de pago: efectivo, transferencia, etc.")
        self.notes_input = QLineEdit()
        self.notes_input.setToolTip("Notas internas sobre este pago")

        self.amount_input.textChanged.connect(self._validate_amount)
        self.amount_input.textChanged.connect(self._sanitize_amount)

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

    def _sanitize_amount(self, text: str) -> None:
        sender = self.sender()
        if not isinstance(sender, QLineEdit):
            return
        clean = re.sub(r"[^\d.]", "", text)
        parts = clean.split(".")
        if len(parts) > 2:
            clean = parts[0] + "." + "".join(parts[1:])
        if clean != text:
            sender.blockSignals(True)
            sender.setText(clean)
            sender.blockSignals(False)

    def _validate_amount(self) -> None:
        amount = self._parse_decimal(self.amount_input.text())
        if amount is None or amount <= 0:
            self.amount_input.setProperty("cssClass", "invalid")
        else:
            self.amount_input.setProperty("cssClass", "")
        self.amount_input.style().unpolish(self.amount_input)
        self.amount_input.style().polish(self.amount_input)

    def _on_accept(self) -> None:
        amount = self._parse_decimal(self.amount_input.text())
        if amount is None or amount <= 0:
            QMessageBox.warning(self, "Monto inválido", "Ingresa un monto numérico mayor a 0.")
            self.amount_input.setFocus()
            return
        self.accept()

    def payment(self) -> Payment:
        payment_date: date = self.date_input.date().toPython()
        if payment_date < self._installment.due_date:
            ptype = "Pago adelantado"
        elif payment_date > self._installment.due_date:
            ptype = "Pago atrasado"
        else:
            ptype = "Pago a tiempo"
        user_notes = self.notes_input.text().strip()
        notes = f"{ptype}" + (f" - {user_notes}" if user_notes else "")
        return Payment(
            installment_id=self._installment.id,
            payment_date=payment_date,
            amount_paid=self._parse_decimal(self.amount_input.text()),
            method=self.method_input.text().strip(),
            notes=notes,
        )
