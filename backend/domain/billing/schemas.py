"""Billing schemas/contracts."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain.billing.models import InvoiceStatus


class BaseSchema(BaseModel):
	model_config = ConfigDict(from_attributes=True)


class InvoiceCreateRequest(BaseSchema):
	client_id: UUID
	company_id: UUID
	total: float
	currency: str = "BRL"
	due_date: date


class InvoiceUpdateRequest(BaseSchema):
	client_id: Optional[UUID] = None
	company_id: Optional[UUID] = None
	total: Optional[float] = None
	currency: Optional[str] = None
	due_date: Optional[date] = None
	status: Optional[InvoiceStatus] = None


class InvoiceResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	client_id: UUID
	company_id: UUID
	total: float
	currency: str
	due_date: date
	status: InvoiceStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class InvoiceFilters(BaseModel):
	"""Filter parameters for listing invoices."""
	client_id: Optional[UUID] = Field(None, description="Filter by client ID")
	status: Optional[InvoiceStatus] = Field(None, description="Invoice status")
	due_from: Optional[date] = Field(None, description="Due date from (inclusive)")
	due_to: Optional[date] = Field(None, description="Due date to (inclusive)")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across currency")
