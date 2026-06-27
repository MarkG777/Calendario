from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from openpyxl import Workbook

from domain.entities import Installment

COLUMN_HEADERS = [
    "Deudor",
    "Préstamo",
    "Número de cuota",
    "Fecha programada",
    "Monto programado",
    "Fecha de pago",
    "Monto pagado",
    "Método",
    "Notas",
]


@dataclass
class PaymentRecord:
    borrower_name: str
    loan_id: int | None
    installment_number: int
    scheduled_date: date
    scheduled_amount: Decimal
    payment_date: date
    amount_paid: Decimal
    method: str
    notes: str

    def as_row(self) -> list:
        return [
            self.borrower_name,
            self.loan_id,
            self.installment_number,
            self.scheduled_date.isoformat(),
            str(self.scheduled_amount),
            self.payment_date.isoformat(),
            str(self.amount_paid),
            self.method,
            self.notes,
        ]


def build_payment_records(
    installments: list[Installment], borrower_name_by_loan_id: dict[int, str]
) -> list[PaymentRecord]:
    records = [
        PaymentRecord(
            borrower_name=borrower_name_by_loan_id.get(installment.loan_id, "—"),
            loan_id=installment.loan_id,
            installment_number=installment.number,
            scheduled_date=installment.due_date,
            scheduled_amount=installment.scheduled_amount,
            payment_date=payment.payment_date,
            amount_paid=payment.amount_paid,
            method=payment.method,
            notes=payment.notes,
        )
        for installment in installments
        for payment in installment.payments
    ]
    records.sort(key=lambda r: r.payment_date, reverse=True)
    return records


def export_to_csv(records: list[PaymentRecord], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMN_HEADERS)
        for record in records:
            writer.writerow(record.as_row())


def export_to_excel(records: list[PaymentRecord], path: str) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Historial de cobros"
    sheet.append(COLUMN_HEADERS)
    for record in records:
        sheet.append(record.as_row())
    workbook.save(path)
