from datetime import date
from decimal import Decimal

from domain.dashboard import (
    actual_collections,
    capital_outstanding,
    delinquency_rate,
    expected_collections,
    portfolio_irr,
    projected_gross_profit,
    realized_profit,
)
from domain.entities import Installment, Loan, Payment
from domain.enums import Frequency, LoanStatus


def make_loan(loan_id=1, principal="10000", total_due="14000", num_installments=14):
    return Loan(
        id=loan_id,
        borrower_id=1,
        principal=Decimal(principal),
        total_due=Decimal(total_due),
        start_date=date(2026, 1, 1),
        num_installments=num_installments,
        frequency=Frequency.SEMANAL,
        installment_amount=Decimal(total_due) / num_installments,
        status=LoanStatus.ACTIVO,
    )


def make_installment(loan_id, due_date, amount="1000.00", payments=None):
    return Installment(
        loan_id=loan_id,
        number=1,
        due_date=due_date,
        scheduled_amount=Decimal(amount),
        payments=payments or [],
    )


def test_capital_outstanding_no_payments_equals_principal():
    loan = make_loan()
    installments = [make_installment(loan.id, date(2026, 1, 8))]

    assert capital_outstanding([loan], installments) == Decimal("10000")


def test_capital_outstanding_fully_paid_loan_is_zero():
    loan = make_loan()
    payment = Payment(
        installment_id=None, payment_date=date(2026, 1, 8), amount_paid=Decimal("14000")
    )
    installments = [make_installment(loan.id, date(2026, 1, 8), amount="14000", payments=[payment])]

    assert capital_outstanding([loan], installments) == Decimal("0")


def test_capital_outstanding_partial_payment_is_proportional():
    loan = make_loan()
    payment = Payment(
        installment_id=None, payment_date=date(2026, 1, 8), amount_paid=Decimal("1000")
    )
    installments = [make_installment(loan.id, date(2026, 1, 8), payments=[payment])]

    recovered = Decimal("1000") * Decimal("10000") / Decimal("14000")
    expected = Decimal("10000") - recovered
    assert capital_outstanding([loan], installments) == expected


def test_projected_and_realized_profit_for_10k_to_14k_example():
    loan = make_loan()
    installments_no_payments = [make_installment(loan.id, date(2026, 1, 8))]

    assert projected_gross_profit([loan]) == Decimal("4000")
    assert realized_profit([loan], installments_no_payments) == Decimal("0")

    payment = Payment(
        installment_id=None, payment_date=date(2026, 1, 8), amount_paid=Decimal("14000")
    )
    installments_fully_paid = [
        make_installment(loan.id, date(2026, 1, 8), amount="14000", payments=[payment])
    ]
    assert realized_profit([loan], installments_fully_paid) == Decimal("4000")


def test_expected_and_actual_collections():
    loan = make_loan()
    payment_in_range = Payment(
        installment_id=None, payment_date=date(2026, 1, 10), amount_paid=Decimal("400")
    )
    payment_out_of_range = Payment(
        installment_id=None, payment_date=date(2026, 2, 1), amount_paid=Decimal("600")
    )
    installments = [
        make_installment(
            loan.id, date(2026, 1, 8), payments=[payment_in_range, payment_out_of_range]
        )
    ]

    assert expected_collections(installments) == Decimal("1000.00")
    assert actual_collections(installments, date(2026, 1, 1), date(2026, 1, 31)) == Decimal("400")


def test_delinquency_rate_counts_overdue_installments():
    loan = make_loan()
    overdue = make_installment(loan.id, date(2026, 1, 1))
    on_time = make_installment(loan.id, date(2027, 1, 1))
    paid_payment = Payment(
        installment_id=None, payment_date=date(2026, 1, 1), amount_paid=Decimal("1000.00")
    )
    paid = make_installment(loan.id, date(2026, 1, 1), payments=[paid_payment])

    rate = delinquency_rate([overdue, on_time, paid], reference_date=date(2026, 6, 25))

    assert rate == Decimal("1") / Decimal("3")


def test_portfolio_irr_weighted_by_principal():
    small_loan = make_loan(loan_id=1, principal="1000", total_due="1200", num_installments=12)
    big_loan = make_loan(loan_id=2, principal="9000", total_due="11700", num_installments=12)

    small_irr = portfolio_irr([small_loan])
    big_irr = portfolio_irr([big_loan])
    weighted_avg = portfolio_irr([small_loan, big_loan])
    unweighted_avg = (small_irr + big_irr) / 2

    assert small_irr != big_irr
    assert weighted_avg != unweighted_avg
    assert weighted_avg > 0
