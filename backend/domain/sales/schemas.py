"""Sales schemas/contracts."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain.sales.models import OpportunityStage


class BaseSchema(BaseModel):
	model_config = ConfigDict(from_attributes=True)


class OpportunityCreateRequest(BaseSchema):
	title: str
	client_id: UUID
	value: float
	currency: str = "BRL"


class OpportunityUpdateRequest(BaseSchema):
	title: Optional[str] = None
	client_id: Optional[UUID] = None
	value: Optional[float] = None
	currency: Optional[str] = None
	stage: Optional[OpportunityStage] = None


class OpportunityStageChangeRequest(BaseSchema):
	stage: OpportunityStage


class OpportunityResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	title: str
	client_id: UUID
	value: float
	currency: str
	stage: OpportunityStage
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class OpportunityFilters(BaseModel):
	"""Filter parameters for listing opportunities."""
	client_id: Optional[UUID] = Field(None, description="Filter by client ID")
	stage: Optional[OpportunityStage] = Field(None, description="Opportunity stage")
	value_min: Optional[float] = Field(None, description="Minimum value (inclusive)")
	value_max: Optional[float] = Field(None, description="Maximum value (inclusive)")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across title")
