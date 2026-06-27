from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from domain.entities import Installment
from domain.enums import Frequency

CENTS = Decimal("0.01")


def calculate_installment_amount(total_due: Decimal, num_installments: int) -> Decimal:
    return (total_due / num_installments).quantize(CENTS, rounding=ROUND_HALF_UP)


def generate_schedule(
    principal: Decimal,
    total_due: Decimal,
    num_installments: int,
    frequency: Frequency,
    start_date: date,
    loan_id: int | None = None,
) -> list[Installment]:
    del principal  # not needed for the schedule itself, kept for callers' clarity
    installment_amount = calculate_installment_amount(total_due, num_installments)

    installments: list[Installment] = []
    due_date = frequency.next_due_date(start_date)
    for number in range(1, num_installments + 1):
        amount = installment_amount
        if number == num_installments:
            amount = total_due - installment_amount * (num_installments - 1)
        installments.append(
            Installment(
                loan_id=loan_id,
                number=number,
                due_date=due_date,
                scheduled_amount=amount,
            )
        )
        due_date = frequency.next_due_date(due_date)

    return installments
