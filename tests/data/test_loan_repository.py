from datetime import date
from decimal import Decimal

from data.repositories import BorrowerRepository, InstallmentRepository, LoanRepository
from domain.entities import Borrower, Loan
from domain.enums import Frequency, LoanStatus
from domain.schedule import calculate_installment_amount, generate_schedule


def test_add_loan_persists_full_schedule(session):
    borrower = BorrowerRepository(session).add(Borrower(name="Juan Perez"))

    principal = Decimal("10000")
    total_due = Decimal("14000")
    num_installments = 14
    installment_amount = calculate_installment_amount(total_due, num_installments)

    loan = Loan(
        borrower_id=borrower.id,
        principal=principal,
        total_due=total_due,
        start_date=date(2026, 1, 1),
        num_installments=num_installments,
        frequency=Frequency.SEMANAL,
        installment_amount=installment_amount,
        status=LoanStatus.ACTIVO,
    )
    installments = generate_schedule(
        principal=principal,
        total_due=total_due,
        num_installments=num_installments,
        frequency=Frequency.SEMANAL,
        start_date=loan.start_date,
    )

    saved_loan = LoanRepository(session).add(loan, installments)

    assert saved_loan.id is not None
    assert isinstance(saved_loan.principal, Decimal)
    assert saved_loan.principal == Decimal("10000")
    assert saved_loan.total_due == Decimal("14000")

    fetched_installments = InstallmentRepository(session).list_by_loan(saved_loan.id)
    assert len(fetched_installments) == 14
    assert all(isinstance(i.scheduled_amount, Decimal) for i in fetched_installments)
    assert sum((i.scheduled_amount for i in fetched_installments), Decimal("0")) == Decimal("14000")
