from __future__ import annotations

from datetime import date
from decimal import Decimal

from domain.calculations import gross_profit, installment_status, loan_irr
from domain.entities import Installment, Loan
from domain.enums import InstallmentStatus

ZERO = Decimal("0")


def _group_by_loan(installments: list[Installment]) -> dict[int, list[Installment]]:
    grouped: dict[int, list[Installment]] = {}
    for installment in installments:
        grouped.setdefault(installment.loan_id, []).append(installment)
    return grouped


def _collected_for_loan(loan_installments: list[Installment]) -> Decimal:
    return sum(
        (p.amount_paid for i in loan_installments for p in i.payments),
        ZERO,
    )


def _capital_recovered(loan: Loan, collected: Decimal) -> Decimal:
    # Un abono no distingue cuanto es capital y cuanto es ganancia; se
    # prorratea según la proporcion principal/total_due del prestamo.
    if loan.total_due == ZERO:
        return ZERO
    ratio = loan.principal / loan.total_due
    return min(collected * ratio, loan.principal)


def capital_outstanding(loans: list[Loan], installments: list[Installment]) -> Decimal:
    by_loan = _group_by_loan(installments)
    total = ZERO
    for loan in loans:
        collected = _collected_for_loan(by_loan.get(loan.id, []))
        recovered = _capital_recovered(loan, collected)
        total += loan.principal - recovered
    return total


def projected_gross_profit(loans: list[Loan]) -> Decimal:
    return sum((gross_profit(loan) for loan in loans), ZERO)


def realized_profit(loans: list[Loan], installments: list[Installment]) -> Decimal:
    by_loan = _group_by_loan(installments)
    total = ZERO
    for loan in loans:
        collected = _collected_for_loan(by_loan.get(loan.id, []))
        recovered = _capital_recovered(loan, collected)
        total += collected - recovered
    return total


def expected_collections(installments: list[Installment]) -> Decimal:
    return sum((i.scheduled_amount for i in installments), ZERO)


def actual_collections(
    installments: list[Installment], start_date: date, end_date: date
) -> Decimal:
    total = ZERO
    for installment in installments:
        for payment in installment.payments:
            if start_date <= payment.payment_date <= end_date:
                total += payment.amount_paid
    return total


def delinquency_rate(installments: list[Installment], reference_date: date) -> Decimal:
    if not installments:
        return ZERO
    overdue = sum(
        1
        for i in installments
        if installment_status(i, reference_date) == InstallmentStatus.ATRASADO
    )
    return Decimal(overdue) / Decimal(len(installments))


def portfolio_irr(loans: list[Loan]) -> float:
    total_principal = sum((loan.principal for loan in loans), ZERO)
    if total_principal == ZERO:
        return 0.0
    weighted_sum = sum(
        (float(loan.principal) * loan_irr(loan) for loan in loans),
        0.0,
    )
    return weighted_sum / float(total_principal)
