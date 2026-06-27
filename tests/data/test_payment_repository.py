from datetime import date
from decimal import Decimal

from data.repositories import (
    BorrowerRepository,
    InstallmentRepository,
    LoanRepository,
    PaymentRepository,
)
from domain.entities import Borrower, Loan, Payment
from domain.enums import Frequency, InstallmentStatus, LoanStatus
from domain.schedule import calculate_installment_amount, generate_schedule


def _create_loan(session):
    borrower = BorrowerRepository(session).add(Borrower(name="Juan Perez"))
    total_due = Decimal("2000")
    num_installments = 2
    installment_amount = calculate_installment_amount(total_due, num_installments)
    loan = Loan(
        borrower_id=borrower.id,
        principal=Decimal("1700"),
        total_due=total_due,
        start_date=date(2026, 1, 1),
        num_installments=num_installments,
        frequency=Frequency.SEMANAL,
        installment_amount=installment_amount,
        status=LoanStatus.ACTIVO,
    )
    installments = generate_schedule(
        principal=loan.principal,
        total_due=total_due,
        num_installments=num_installments,
        frequency=Frequency.SEMANAL,
        start_date=loan.start_date,
    )
    saved_loan = LoanRepository(session).add(loan, installments)
    return saved_loan, InstallmentRepository(session).list_by_loan(saved_loan.id)


def test_partial_payment_marks_installment_parcial(session):
    _, installments = _create_loan(session)
    first = installments[0]

    payment = Payment(
        installment_id=first.id,
        payment_date=first.due_date,
        amount_paid=Decimal("400.00"),
    )
    PaymentRepository(session).add(payment)

    updated = InstallmentRepository(session).list_by_loan(first.loan_id)[0]
    assert updated.status == InstallmentStatus.PARCIAL
    assert len(updated.payments) == 1
    assert updated.payments[0].amount_paid == Decimal("400.00")


def test_full_payment_marks_installment_pagado(session):
    _, installments = _create_loan(session)
    first = installments[0]

    payment = Payment(
        installment_id=first.id,
        payment_date=first.due_date,
        amount_paid=first.scheduled_amount,
    )
    PaymentRepository(session).add(payment)

    updated = InstallmentRepository(session).list_by_loan(first.loan_id)[0]
    assert updated.status == InstallmentStatus.PAGADO
