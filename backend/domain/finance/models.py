"""Finance ORM models."""

from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SqlEnum, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared import Base, IdMixin, TenantMixin, TimestampMixin


class AccountStatus(str, Enum):
	active = "active"
	inactive = "inactive"


class AccountType(str, Enum):
	asset = "asset"
	liability = "liability"
	income = "income"
	expense = "expense"


class CompanyStatus(str, Enum):
	active = "active"
	inactive = "inactive"


class PaymentStatus(str, Enum):
	pending = "pending"
	confirmed = "confirmed"
	failed = "failed"
	canceled = "canceled"


class PaymentMethod(str, Enum):
	pix = "pix"
	card = "card"
	bank_transfer = "bank_transfer"
	cash = "cash"


class PayableStatus(str, Enum):
	pending = "pending"
	approved = "approved"
	paid = "paid"
	overdue = "overdue"
	canceled = "canceled"


class ReceivableStatus(str, Enum):
	pending = "pending"
	confirmed = "confirmed"
	received = "received"
	overdue = "overdue"
	canceled = "canceled"


class Company(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "finance_companies"

	name: Mapped[str] = mapped_column(String, nullable=False)
	cnpj: Mapped[str] = mapped_column(String, nullable=False)
	trading_name: Mapped[str] = mapped_column(String, nullable=False)
	address: Mapped[str] = mapped_column(String, nullable=False)
	status: Mapped[CompanyStatus] = mapped_column(
		SqlEnum(CompanyStatus), default=CompanyStatus.active, nullable=False
	)


class Account(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "finance_accounts"

	name: Mapped[str] = mapped_column(String, nullable=False)
	type: Mapped[AccountType] = mapped_column(SqlEnum(AccountType), nullable=False)
	currency: Mapped[str] = mapped_column(String, nullable=False, default="BRL")
	status: Mapped[AccountStatus] = mapped_column(
		SqlEnum(AccountStatus), default=AccountStatus.active, nullable=False
	)


class Payment(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "finance_payments"

	account_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	company_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
	currency: Mapped[str] = mapped_column(String, nullable=False, default="BRL")
	method: Mapped[PaymentMethod] = mapped_column(
		SqlEnum(PaymentMethod), default=PaymentMethod.pix, nullable=False
	)
	status: Mapped[PaymentStatus] = mapped_column(
		SqlEnum(PaymentStatus), default=PaymentStatus.pending, nullable=False
	)


class Payable(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "finance_payables"

	company_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	account_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	description: Mapped[str] = mapped_column(String, nullable=False)
	amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
	currency: Mapped[str] = mapped_column(String, nullable=False, default="BRL")
	due_date: Mapped[Date] = mapped_column(Date, nullable=False)
	category: Mapped[str] = mapped_column(String, nullable=False)
	status: Mapped[PayableStatus] = mapped_column(
		SqlEnum(PayableStatus), default=PayableStatus.pending, nullable=False
	)
	paid_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Receivable(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "finance_receivables"

	company_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	account_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	description: Mapped[str] = mapped_column(String, nullable=False)
	amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
	currency: Mapped[str] = mapped_column(String, nullable=False, default="BRL")
	due_date: Mapped[Date] = mapped_column(Date, nullable=False)
	category: Mapped[str] = mapped_column(String, nullable=False)
	source_domain: Mapped[str] = mapped_column(String, nullable=False)
	source_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	status: Mapped[ReceivableStatus] = mapped_column(
		SqlEnum(ReceivableStatus), default=ReceivableStatus.pending, nullable=False
	)
	received_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
