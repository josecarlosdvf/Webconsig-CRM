"""Billing ORM models."""

from enum import Enum

from sqlalchemy import Date, Enum as SqlEnum, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared import Base, IdMixin, TenantMixin, TimestampMixin


class InvoiceStatus(str, Enum):
	draft = "draft"
	issued = "issued"
	overdue = "overdue"
	paid = "paid"
	canceled = "canceled"


class Invoice(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "billing_invoices"

	client_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	company_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
	currency: Mapped[str] = mapped_column(String, nullable=False, default="BRL")
	due_date: Mapped[Date] = mapped_column(Date, nullable=False)
	status: Mapped[InvoiceStatus] = mapped_column(
		SqlEnum(InvoiceStatus), default=InvoiceStatus.draft, nullable=False
	)
