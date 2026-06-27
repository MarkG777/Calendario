from datetime import date
from decimal import Decimal

from domain.calculations import loan_irr
from domain.entities import Loan
from domain.enums import Frequency, LoanStatus


def test_loan_irr_for_10k_to_14k_weekly_example():
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

    irr = loan_irr(loan)

    assert abs(irr - 0.048) < 0.002
