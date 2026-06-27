from __future__ import annotations

from datetime import date
from decimal import Decimal

import numpy_financial as npf

from domain.entities import Installment, Loan, Payment
from domain.enums import InstallmentStatus

ZERO = Decimal("0")


def outstanding_balance(installment: Installment) -> Decimal:
    paid = sum((p.amount_paid for p in installment.payments), ZERO)
    return installment.scheduled_amount - paid


def apply_payment(installment: Installment, payment: Payment) -> None:
    installment.payments.append(payment)
    balance = outstanding_balance(installment)
    if balance <= ZERO:
        installment.status = InstallmentStatus.PAGADO
    else:
        installment.status = InstallmentStatus.PARCIAL


def installment_status(installment: Installment, reference_date: date) -> InstallmentStatus:
    balance = outstanding_balance(installment)
    if balance <= ZERO:
        return InstallmentStatus.PAGADO
    if reference_date > installment.due_date:
        return InstallmentStatus.ATRASADO
    if installment.payments:
        return InstallmentStatus.PARCIAL
    return InstallmentStatus.PENDIENTE


def loan_outstanding_balance(installments: list[Installment]) -> Decimal:
    return sum((outstanding_balance(i) for i in installments), ZERO)


def gross_profit(loan: Loan) -> Decimal:
    return loan.total_due - loan.principal


def loan_irr(loan: Loan) -> float:
    cashflows = [float(-loan.principal)] + [float(loan.installment_amount)] * loan.num_installments
    return npf.irr(cashflows)
