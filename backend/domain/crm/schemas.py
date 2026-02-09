"""CRM schemas/contracts."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain.crm.models import ClientStatus, LeadStatus


class BaseSchema(BaseModel):
	model_config = ConfigDict(from_attributes=True)


# ====================
# Client schemas
# ====================


class ClientCreateRequest(BaseSchema):
	name: str
	email: str
	phone: str
	document: str


class ClientUpdateRequest(BaseSchema):
	name: Optional[str] = None
	email: Optional[str] = None
	phone: Optional[str] = None
	document: Optional[str] = None
	status: Optional[ClientStatus] = None


class ClientResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	name: str
	email: str
	phone: str
	document: str
	status: ClientStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class ClientFilters(BaseModel):
	"""Filter parameters for listing clients."""
	name: Optional[str] = Field(None, description="Exact name match")
	email: Optional[str] = Field(None, description="Exact email match")
	document: Optional[str] = Field(None, description="Exact document match")
	status: Optional[ClientStatus] = Field(None, description="Client status")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across name, email, document")


# ====================
# Lead schemas
# ====================


class LeadCreateRequest(BaseSchema):
	name: str
	email: str
	phone: str
	source: str


class LeadUpdateRequest(BaseSchema):
	name: Optional[str] = None
	email: Optional[str] = None
	phone: Optional[str] = None
	source: Optional[str] = None
	status: Optional[LeadStatus] = None


class LeadResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	name: str
	email: str
	phone: str
	source: str
	status: LeadStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class LeadFilters(BaseModel):
	"""Filter parameters for listing leads."""
	name: Optional[str] = Field(None, description="Exact name match")
	email: Optional[str] = Field(None, description="Exact email match")
	source: Optional[str] = Field(None, description="Exact source match")
	status: Optional[LeadStatus] = Field(None, description="Lead status")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across name, email, source")

