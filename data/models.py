from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from data.types import DecimalAsString


class Base(DeclarativeBase):
    pass


class BorrowerModel(Base):
    __tablename__ = "borrowers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, default="")
    address: Mapped[str] = mapped_column(String, default="")
    notes: Mapped[str] = mapped_column(String, default="")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    loans: Mapped[list[LoanModel]] = relationship(back_populates="borrower")


class LoanModel(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    borrower_id: Mapped[int] = mapped_column(ForeignKey("borrowers.id"), nullable=False)
    principal: Mapped[object] = mapped_column(DecimalAsString, nullable=False)
    total_due: Mapped[object] = mapped_column(DecimalAsString, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    num_installments: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency: Mapped[str] = mapped_column(String, nullable=False)
    installment_amount: Mapped[object] = mapped_column(DecimalAsString, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)

    borrower: Mapped[BorrowerModel] = relationship(back_populates="loans")
    installments: Mapped[list[InstallmentModel]] = relationship(
        back_populates="loan", cascade="all, delete-orphan", order_by="InstallmentModel.number"
    )


class InstallmentModel(Base):
    __tablename__ = "installments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    scheduled_amount: Mapped[object] = mapped_column(DecimalAsString, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)

    loan: Mapped[LoanModel] = relationship(back_populates="installments")
    payments: Mapped[list[PaymentModel]] = relationship(
        back_populates="installment", cascade="all, delete-orphan"
    )


class PaymentModel(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    installment_id: Mapped[int] = mapped_column(ForeignKey("installments.id"), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount_paid: Mapped[object] = mapped_column(DecimalAsString, nullable=False)
    method: Mapped[str] = mapped_column(String, default="")
    notes: Mapped[str] = mapped_column(String, default="")

    installment: Mapped[InstallmentModel] = relationship(back_populates="payments")
