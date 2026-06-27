from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from domain.enums import Frequency, InstallmentStatus, LoanStatus


@dataclass
class Borrower:
    name: str
    phone: str = ""
    address: str = ""
    notes: str = ""
    created_at: date | None = None
    id: int | None = None


@dataclass
class Payment:
    installment_id: int | None
    payment_date: date
    amount_paid: Decimal
    method: str = ""
    notes: str = ""
    id: int | None = None


@dataclass
class Installment:
    loan_id: int | None
    number: int
    due_date: date
    scheduled_amount: Decimal
    status: InstallmentStatus = InstallmentStatus.PENDIENTE
    payments: list[Payment] = field(default_factory=list)
    id: int | None = None


@dataclass
class Loan:
    borrower_id: int | None
    principal: Decimal
    total_due: Decimal
    start_date: date
    num_installments: int
    frequency: Frequency
    installment_amount: Decimal
    status: LoanStatus = LoanStatus.ACTIVO
    id: int | None = None
