from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from data.mappers import (
    borrower_to_domain,
    borrower_to_model,
    installment_to_domain,
    installment_to_model,
    loan_to_domain,
    loan_to_model,
    payment_to_domain,
    payment_to_model,
)
from data.models import BorrowerModel, InstallmentModel, LoanModel
from domain.calculations import installment_status
from domain.entities import Borrower, Installment, Loan, Payment


class BorrowerRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, borrower: Borrower) -> Borrower:
        model = borrower_to_model(borrower)
        self._session.add(model)
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return borrower_to_domain(model)

    def update(self, borrower: Borrower) -> Borrower:
        model = self._session.get(BorrowerModel, borrower.id)
        if model is None:
            raise ValueError(f"Borrower {borrower.id} not found")
        model.name = borrower.name
        model.phone = borrower.phone
        model.address = borrower.address
        model.notes = borrower.notes
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return borrower_to_domain(model)

    def get(self, borrower_id: int) -> Borrower | None:
        model = self._session.get(BorrowerModel, borrower_id)
        return borrower_to_domain(model) if model else None

    def list_all(self) -> list[Borrower]:
        models = self._session.scalars(select(BorrowerModel)).all()
        return [borrower_to_domain(m) for m in models]


class LoanRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, loan: Loan, installments: list[Installment]) -> Loan:
        model = loan_to_model(loan)
        model.installments = [installment_to_model(i) for i in installments]
        self._session.add(model)
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return loan_to_domain(model)

    def get(self, loan_id: int) -> Loan | None:
        model = self._session.get(LoanModel, loan_id)
        return loan_to_domain(model) if model else None

    def list_all(self) -> list[Loan]:
        models = self._session.scalars(select(LoanModel)).all()
        return [loan_to_domain(m) for m in models]


class InstallmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Installment]:
        models = self._session.scalars(select(InstallmentModel)).all()
        return [installment_to_domain(m) for m in models]

    def list_by_loan(self, loan_id: int) -> list[Installment]:
        stmt = (
            select(InstallmentModel)
            .where(InstallmentModel.loan_id == loan_id)
            .order_by(InstallmentModel.number)
        )
        models = self._session.scalars(stmt).all()
        return [installment_to_domain(m) for m in models]

    def list_due_between(self, start_date: date, end_date: date) -> list[Installment]:
        stmt = (
            select(InstallmentModel)
            .where(InstallmentModel.due_date >= start_date)
            .where(InstallmentModel.due_date <= end_date)
            .order_by(InstallmentModel.due_date)
        )
        models = self._session.scalars(stmt).all()
        return [installment_to_domain(m) for m in models]

    def update_status(self, installment: Installment) -> None:
        model = self._session.get(InstallmentModel, installment.id)
        if model is None:
            raise ValueError(f"Installment {installment.id} not found")
        model.status = installment.status.value
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise


class PaymentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, payment: Payment) -> Payment:
        model = payment_to_model(payment)
        self._session.add(model)
        self._session.flush()

        installment_model = self._session.get(InstallmentModel, payment.installment_id)
        if installment_model is not None:
            self._session.expire(installment_model, ["payments"])
            installment = installment_to_domain(installment_model)
            new_status = installment_status(installment, payment.payment_date)
            installment_model.status = new_status.value

        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return payment_to_domain(model)
