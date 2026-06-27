from datetime import date
from decimal import Decimal

from data.repositories import BorrowerRepository, InstallmentRepository, LoanRepository
from domain.entities import Borrower, Loan
from domain.enums import Frequency, LoanStatus
from domain.schedule import calculate_installment_amount, generate_schedule


def _create_loan(session):
    borrower = BorrowerRepository(session).add(Borrower(name="Juan Perez"))
    total_due = Decimal("14000")
    num_installments = 14
    installment_amount = calculate_installment_amount(total_due, num_installments)
    loan = Loan(
        borrower_id=borrower.id,
        principal=Decimal("10000"),
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
    return LoanRepository(session).add(loan, installments)


def test_list_due_between_filters_by_date_range(session):
    saved_loan = _create_loan(session)
    repo = InstallmentRepository(session)

    due_in_january = repo.list_due_between(date(2026, 1, 1), date(2026, 1, 31))

    assert len(due_in_january) == 4
    assert all(date(2026, 1, 1) <= i.due_date <= date(2026, 1, 31) for i in due_in_january)
    assert all(i.loan_id == saved_loan.id for i in due_in_january)


def test_list_all_returns_every_installment_in_the_portfolio(session):
    saved_loan = _create_loan(session)
    repo = InstallmentRepository(session)

    all_installments = repo.list_all()

    assert len(all_installments) == 14
    assert all(i.loan_id == saved_loan.id for i in all_installments)
