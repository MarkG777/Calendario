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
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data.repositories import (
    BorrowerRepository,
    InstallmentRepository,
    LoanRepository,
    PaymentRepository,
)
from domain.calculations import installment_status, outstanding_balance
from domain.entities import Installment, Payment
from ui.status_colors import status_background, status_foreground


class BulkPaymentDialog(QDialog):
    def __init__(
        self,
        borrower_repository: BorrowerRepository,
        loan_repository: LoanRepository,
        installment_repository: InstallmentRepository,
        payment_repository: PaymentRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("💸 Registrar pagos multiples")
        self.resize(750, 500)
        self._borrower_repository = borrower_repository
        self._loan_repository = loan_repository
        self._installment_repository = installment_repository
        self._payment_repository = payment_repository

        self._installments: list[Installment] = []
        self._payment_inputs: dict[int, QLineEdit] = {}

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ["Cuota", "Fecha programada", "Monto", "Saldo", "Estado", "Pago a registrar"]
        )
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)

        self._borrower_combo = QComboBox()
        self._borrower_combo.setToolTip("Selecciona el cliente para ver sus cuotas")
        self._borrower_combo.currentIndexChanged.connect(self._load_installments)
        for borrower in borrower_repository.list_all():
            self._borrower_combo.addItem(borrower.name, borrower.id)

        self._date_input = QDateEdit(QDate.currentDate())
        self._date_input.setCalendarPopup(True)
        self._date_input.setToolTip("Fecha que se aplicara a todos los pagos registrados")

        self._method_input = QLineEdit()
        self._method_input.setToolTip("Metodo de pago: efectivo, transferencia, etc.")
        self._method_input.setPlaceholderText("ej. efectivo, transferencia...")

        self._summary_label = QLabel("Total a registrar: $0.00")

        pay_all_button = QPushButton("✅ Pagar todo el saldo")
        pay_all_button.setToolTip("Rellenar todos los campos con el saldo pendiente")
        pay_all_button.clicked.connect(self._fill_all_balances)

        clear_button = QPushButton("🧹 Limpiar")
        clear_button.setToolTip("Vaciar todos los campos de pago")
        clear_button.clicked.connect(self._clear_all)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        form = QFormLayout()
        form.addRow("Cliente*:", self._borrower_combo)
        form.addRow("Fecha de pago*:", self._date_input)
        form.addRow("Metodo:", self._method_input)

        actions_row = QHBoxLayout()
        actions_row.addWidget(pay_all_button)
        actions_row.addWidget(clear_button)
        actions_row.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(actions_row)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._summary_label)
        layout.addWidget(buttons)

        if self._borrower_combo.count() > 0:
            self._load_installments()

    def _load_installments(self) -> None:
        borrower_id = self._borrower_combo.currentData()
        if borrower_id is None:
            self._table.setRowCount(0)
            return

        loans = [
            loan for loan in self._loan_repository.list_all()
            if loan.borrower_id == borrower_id
        ]
        loan_ids = {loan.id for loan in loans}

        all_installments = self._installment_repository.list_all()
        self._installments = [
            i for i in all_installments if i.loan_id in loan_ids
        ]
        self._installments.sort(key=lambda i: i.due_date)

        today = date.today()
        self._payment_inputs.clear()
        self._table.setRowCount(len(self._installments))

        for row, installment in enumerate(self._installments):
            balance = outstanding_balance(installment)
            status = installment_status(installment, today)

            self._table.setItem(row, 0, QTableWidgetItem(f"#{installment.number}"))
            self._table.setItem(row, 1, QTableWidgetItem(installment.due_date.isoformat()))
            self._table.setItem(
                row, 2, QTableWidgetItem(str(installment.scheduled_amount))
            )
            self._table.setItem(row, 3, QTableWidgetItem(str(balance)))

            status_item = QTableWidgetItem(status.value)
            status_item.setBackground(status_background(status))
            status_item.setForeground(status_foreground(status))
            self._table.setItem(row, 4, status_item)

            payment_input = QLineEdit()
            payment_input.setPlaceholderText("0.00")
            if balance <= Decimal("0"):
                payment_input.setDisabled(True)
                payment_input.setText("PAGADA")
            else:
                payment_input.setText("")
                payment_input.textChanged.connect(self._update_summary)
            self._table.setCellWidget(row, 5, payment_input)
            self._payment_inputs[installment.id] = payment_input

        self._update_summary()

    def _fill_all_balances(self) -> None:
        for installment in self._installments:
            balance = outstanding_balance(installment)
            if balance > Decimal("0"):
                inp = self._payment_inputs.get(installment.id)
                if inp and inp.isEnabled():
                    inp.setText(str(balance))

    def _clear_all(self) -> None:
        for inp in self._payment_inputs.values():
            if inp.isEnabled():
                inp.setText("")

    def _update_summary(self) -> None:
        total = Decimal("0")
        for installment in self._installments:
            inp = self._payment_inputs.get(installment.id)
            if inp and inp.isEnabled():
                val = self._parse_decimal(inp.text())
                if val and val > 0:
                    total += val
        self._summary_label.setText(f"Total a registrar: ${total}")

    @staticmethod
    def _parse_decimal(text: str) -> Decimal | None:
        try:
            return Decimal(text.strip())
        except (InvalidOperation, ValueError):
            return None

    def _on_accept(self) -> None:
        if self._borrower_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Falta cliente", "Selecciona un cliente.")
            return

        payment_date: date = self._date_input.date().toPython()
        method = self._method_input.text().strip()
        payments_to_register: list[tuple[Installment, Decimal]] = []

        for installment in self._installments:
            inp = self._payment_inputs.get(installment.id)
            if not inp or not inp.isEnabled():
                continue
            val = self._parse_decimal(inp.text())
            if val is None or val <= 0:
                continue
            balance = outstanding_balance(installment)
            if val > balance:
                QMessageBox.warning(
                    self,
                    "Monto excedido",
                    f"El pago para la cuota #{installment.number} (${val}) "
                    f"excede el saldo pendiente (${balance}).",
                )
                return
            payments_to_register.append((installment, val))

        if not payments_to_register:
            QMessageBox.information(
                self,
                "Sin pagos",
                "No has ingresado ningun monto a registrar.",
            )
            return

        # Register all payments
        errors: list[str] = []
        count = 0
        for installment, amount in payments_to_register:
            # Determine payment type based on date vs due_date
            if payment_date < installment.due_date:
                ptype = "Pago adelantado"
            elif payment_date > installment.due_date:
                ptype = "Pago atrasado"
            else:
                ptype = "Pago a tiempo"

            notes = ptype
            if method:
                notes = f"{ptype} - {method}" if method else ptype

            payment = Payment(
                installment_id=installment.id,
                payment_date=payment_date,
                amount_paid=amount,
                method=method,
                notes=notes,
            )
            try:
                self._payment_repository.add(payment)
                count += 1
            except Exception as error:
                errors.append(f"Cuota #{installment.number}: {error}")

        if errors:
            QMessageBox.warning(
                self,
                "Pagos con errores",
                f"Se registraron {count} pago(s) correctamente.\n"
                f"Errores:\n" + "\n".join(errors),
            )
        else:
            QMessageBox.information(
                self,
                "Pagos registrados",
                f"Se registraron {count} pago(s) correctamente.",
            )
        self.accept()
