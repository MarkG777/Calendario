from __future__ import annotations

from data.models import BorrowerModel, InstallmentModel, LoanModel, PaymentModel
from domain.entities import Borrower, Installment, Loan, Payment
from domain.enums import Frequency, InstallmentStatus, LoanStatus


def borrower_to_domain(model: BorrowerModel) -> Borrower:
    return Borrower(
        id=model.id,
        name=model.name,
        phone=model.phone,
        address=model.address,
        notes=model.notes,
        latitude=model.latitude,
        longitude=model.longitude,
        active=model.active,
        created_at=model.created_at,
    )


def borrower_to_model(borrower: Borrower) -> BorrowerModel:
    return BorrowerModel(
        id=borrower.id,
        name=borrower.name,
        phone=borrower.phone,
        address=borrower.address,
        notes=borrower.notes,
        latitude=borrower.latitude,
        longitude=borrower.longitude,
        active=borrower.active,
        created_at=borrower.created_at,
    )


def payment_to_domain(model: PaymentModel) -> Payment:
    return Payment(
        id=model.id,
        installment_id=model.installment_id,
        payment_date=model.payment_date,
        amount_paid=model.amount_paid,
        method=model.method,
        notes=model.notes,
    )


def payment_to_model(payment: Payment) -> PaymentModel:
    return PaymentModel(
        id=payment.id,
        installment_id=payment.installment_id,
        payment_date=payment.payment_date,
        amount_paid=payment.amount_paid,
        method=payment.method,
        notes=payment.notes,
    )


def installment_to_domain(model: InstallmentModel) -> Installment:
    return Installment(
        id=model.id,
        loan_id=model.loan_id,
        number=model.number,
        due_date=model.due_date,
        scheduled_amount=model.scheduled_amount,
        status=InstallmentStatus(model.status),
        payments=[payment_to_domain(p) for p in model.payments],
    )


def installment_to_model(installment: Installment) -> InstallmentModel:
    return InstallmentModel(
        id=installment.id,
        loan_id=installment.loan_id,
        number=installment.number,
        due_date=installment.due_date,
        scheduled_amount=installment.scheduled_amount,
        status=installment.status.value,
        payments=[payment_to_model(p) for p in installment.payments],
    )


def loan_to_domain(model: LoanModel) -> Loan:
    return Loan(
        id=model.id,
        borrower_id=model.borrower_id,
        principal=model.principal,
        total_due=model.total_due,
        start_date=model.start_date,
        num_installments=model.num_installments,
        frequency=Frequency(model.frequency),
        installment_amount=model.installment_amount,
        status=LoanStatus(model.status),
    )


def loan_to_model(loan: Loan) -> LoanModel:
    return LoanModel(
        id=loan.id,
        borrower_id=loan.borrower_id,
        principal=loan.principal,
        total_due=loan.total_due,
        start_date=loan.start_date,
        num_installments=loan.num_installments,
        frequency=loan.frequency.value,
        installment_amount=loan.installment_amount,
        status=loan.status.value,
    )
