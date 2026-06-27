from datetime import date
from decimal import Decimal

from domain.calculations import (
    apply_payment,
    gross_profit,
    installment_status,
    loan_outstanding_balance,
    outstanding_balance,
)
from domain.entities import Installment, Loan, Payment
from domain.enums import Frequency, InstallmentStatus, LoanStatus


def make_installment(amount="1000.00", due_date=date(2026, 1, 8)):
    return Installment(
        loan_id=1,
        number=1,
        due_date=due_date,
        scheduled_amount=Decimal(amount),
    )


def test_exact_payment_marks_installment_as_paid():
    installment = make_installment()
    payment = Payment(
        installment_id=None, payment_date=date(2026, 1, 8), amount_paid=Decimal("1000.00")
    )

    apply_payment(installment, payment)

    assert outstanding_balance(installment) == Decimal("0")
    assert installment.status == InstallmentStatus.PAGADO


def test_partial_payment_marks_installment_as_parcial():
    installment = make_installment()
    payment = Payment(
        installment_id=None, payment_date=date(2026, 1, 8), amount_paid=Decimal("400.00")
    )

    apply_payment(installment, payment)

    assert outstanding_balance(installment) == Decimal("600.00")
    assert installment.status == InstallmentStatus.PARCIAL


def test_late_unpaid_installment_is_atrasado():
    installment = make_installment(due_date=date(2026, 1, 8))

    status = installment_status(installment, reference_date=date(2026, 1, 20))

    assert status == InstallmentStatus.ATRASADO


def test_on_time_unpaid_installment_is_pendiente():
    installment = make_installment(due_date=date(2026, 1, 8))

    status = installment_status(installment, reference_date=date(2026, 1, 5))

    assert status == InstallmentStatus.PENDIENTE


def test_loan_fully_paid_has_zero_outstanding_balance():
    installments = [
        make_installment(amount="1000.00", due_date=date(2026, 1, 8)),
        make_installment(amount="1000.00", due_date=date(2026, 1, 15)),
    ]
    for installment in installments:
        apply_payment(
            installment,
            Payment(
                installment_id=None,
                payment_date=installment.due_date,
                amount_paid=Decimal("1000.00"),
            ),
        )

    assert loan_outstanding_balance(installments) == Decimal("0")


def test_gross_profit_for_10k_to_14k_example():
    loan = Loan(
        borrower_id=1,
        principal=Decimal("10000"),
        total_due=Decimal("14000"),
        start_date=date(2026, 1, 1),
        num_installments=14,
        frequency=Frequency.SEMANAL,
        installment_amount=Decimal("1000.00"),
        status=LoanStatus.ACTIVO,
    )

    assert gross_profit(loan) == Decimal("4000")
