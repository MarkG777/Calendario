from datetime import date
from decimal import Decimal

from domain.enums import Frequency
from domain.schedule import calculate_installment_amount, generate_schedule


def test_calculate_installment_amount_exact_division():
    assert calculate_installment_amount(Decimal("14000"), 14) == Decimal("1000.00")


def test_generate_schedule_weekly_dates_and_count():
    schedule = generate_schedule(
        principal=Decimal("10000"),
        total_due=Decimal("14000"),
        num_installments=14,
        frequency=Frequency.SEMANAL,
        start_date=date(2026, 1, 1),
    )

    assert len(schedule) == 14
    assert schedule[0].due_date == date(2026, 1, 8)
    assert schedule[1].due_date == date(2026, 1, 15)
    assert schedule[-1].due_date == date(2026, 4, 9)
    assert [i.number for i in schedule] == list(range(1, 15))


def test_generate_schedule_sums_exactly_to_total_due_with_rounding():
    schedule = generate_schedule(
        principal=Decimal("1000"),
        total_due=Decimal("1000.01"),
        num_installments=3,
        frequency=Frequency.SEMANAL,
        start_date=date(2026, 1, 1),
    )

    assert sum((i.scheduled_amount for i in schedule), Decimal("0")) == Decimal("1000.01")
    assert schedule[0].scheduled_amount == Decimal("333.34")
    assert schedule[1].scheduled_amount == Decimal("333.34")
    assert schedule[2].scheduled_amount == Decimal("333.33")


def test_generate_schedule_monthly_advances_calendar_months():
    schedule = generate_schedule(
        principal=Decimal("5000"),
        total_due=Decimal("6000"),
        num_installments=3,
        frequency=Frequency.MENSUAL,
        start_date=date(2026, 1, 31),
    )

    assert schedule[0].due_date == date(2026, 2, 28)
    assert schedule[1].due_date == date(2026, 3, 28)
    assert schedule[2].due_date == date(2026, 4, 28)
