"""Finance schemas/contracts."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain.finance.models import (
	AccountStatus,
	AccountType,
	CompanyStatus,
	PayableStatus,
	PaymentMethod,
	PaymentStatus,
	ReceivableStatus,
)


class BaseSchema(BaseModel):
	model_config = ConfigDict(from_attributes=True)


class CompanyCreateRequest(BaseSchema):
	name: str
	cnpj: str
	trading_name: str
	address: str


class CompanyUpdateRequest(BaseSchema):
	name: Optional[str] = None
	cnpj: Optional[str] = None
	trading_name: Optional[str] = None
	address: Optional[str] = None
	status: Optional[CompanyStatus] = None


class CompanyResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	name: str
	cnpj: str
	trading_name: str
	address: str
	status: CompanyStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class CompanyFilters(BaseModel):
	"""Filter parameters for listing companies."""
	name: Optional[str] = Field(None, description="Exact name match")
	cnpj: Optional[str] = Field(None, description="Exact CNPJ match")
	status: Optional[CompanyStatus] = Field(None, description="Company status")
	q: Optional[str] = Field(None, description="Search across name, cnpj, trading_name")


class AccountCreateRequest(BaseSchema):
	name: str
	type: AccountType
	currency: str = "BRL"


class AccountUpdateRequest(BaseSchema):
	name: Optional[str] = None
	type: Optional[AccountType] = None
	currency: Optional[str] = None
	status: Optional[AccountStatus] = None


class AccountResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	name: str
	type: AccountType
	currency: str
	status: AccountStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class AccountFilters(BaseModel):
	"""Filter parameters for listing accounts."""
	type: Optional[AccountType] = Field(None, description="Account type")
	status: Optional[AccountStatus] = Field(None, description="Account status")
	currency: Optional[str] = Field(None, description="Currency code")
	q: Optional[str] = Field(None, description="Search across name")


class PaymentCreateRequest(BaseSchema):
	account_id: UUID
	company_id: UUID
	amount: float
	currency: str = "BRL"
	method: PaymentMethod = PaymentMethod.pix


class PaymentResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	account_id: UUID
	company_id: UUID
	amount: float
	currency: str
	method: PaymentMethod
	status: PaymentStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class PaymentFilters(BaseModel):
	"""Filter parameters for listing payments."""
	account_id: Optional[UUID] = Field(None, description="Filter by account ID")
	company_id: Optional[UUID] = Field(None, description="Filter by company ID")
	status: Optional[PaymentStatus] = Field(None, description="Payment status")
	method: Optional[PaymentMethod] = Field(None, description="Payment method")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across currency")


class PayableCreateRequest(BaseSchema):
	company_id: UUID
	account_id: UUID
	description: str
	amount: float
	currency: str = "BRL"
	due_date: date
	category: str


class PayableUpdateRequest(BaseSchema):
	company_id: Optional[UUID] = None
	account_id: Optional[UUID] = None
	description: Optional[str] = None
	amount: Optional[float] = None
	currency: Optional[str] = None
	due_date: Optional[date] = None
	category: Optional[str] = None
	status: Optional[PayableStatus] = None


class PayableResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	company_id: UUID
	account_id: UUID
	description: str
	amount: float
	currency: str
	due_date: date
	category: str
	status: PayableStatus
	paid_at: datetime | None
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class PayableFilters(BaseModel):
	"""Filter parameters for listing payables."""
	company_id: Optional[UUID] = Field(None, description="Filter by company ID")
	account_id: Optional[UUID] = Field(None, description="Filter by account ID")
	status: Optional[PayableStatus] = Field(None, description="Payable status")
	category: Optional[str] = Field(None, description="Category")
	due_from: Optional[date] = Field(None, description="Due date from (inclusive)")
	due_to: Optional[date] = Field(None, description="Due date to (inclusive)")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across description and category")


class ReceivableCreateRequest(BaseSchema):
	company_id: UUID
	account_id: UUID
	description: str
	amount: float
	currency: str = "BRL"
	due_date: date
	category: str
	source_domain: str
	source_id: UUID


class ReceivableUpdateRequest(BaseSchema):
	company_id: Optional[UUID] = None
	account_id: Optional[UUID] = None
	description: Optional[str] = None
	amount: Optional[float] = None
	currency: Optional[str] = None
	due_date: Optional[date] = None
	category: Optional[str] = None
	source_domain: Optional[str] = None
	source_id: Optional[UUID] = None
	status: Optional[ReceivableStatus] = None


class ReceivableResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	company_id: UUID
	account_id: UUID
	description: str
	amount: float
	currency: str
	due_date: date
	category: str
	source_domain: str
	source_id: UUID
	status: ReceivableStatus
	received_at: datetime | None
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class ReceivableFilters(BaseModel):
	"""Filter parameters for listing receivables."""
	company_id: Optional[UUID] = Field(None, description="Filter by company ID")
	account_id: Optional[UUID] = Field(None, description="Filter by account ID")
	status: Optional[ReceivableStatus] = Field(None, description="Receivable status")
	category: Optional[str] = Field(None, description="Category")
	source_domain: Optional[str] = Field(None, description="Source domain")
	due_from: Optional[date] = Field(None, description="Due date from (inclusive)")
	due_to: Optional[date] = Field(None, description="Due date to (inclusive)")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across description, category, source_domain")
