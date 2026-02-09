"""Inventory schemas/contracts."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain.inventory.models import ItemStatus, ItemUnit


class BaseSchema(BaseModel):
	model_config = ConfigDict(from_attributes=True)


class ItemCreateRequest(BaseSchema):
	sku: str
	name: str
	unit: ItemUnit


class ItemUpdateRequest(BaseSchema):
	sku: Optional[str] = None
	name: Optional[str] = None
	unit: Optional[ItemUnit] = None
	status: Optional[ItemStatus] = None


class ItemResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	sku: str
	name: str
	unit: ItemUnit
	status: ItemStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class StockAdjustmentRequest(BaseSchema):
	item_id: UUID
	delta: int
	reason: str


class ItemFilters(BaseModel):
	"""Filter parameters for listing items."""
	sku: Optional[str] = Field(None, description="Exact SKU match")
	name: Optional[str] = Field(None, description="Exact name match")
	status: Optional[ItemStatus] = Field(None, description="Item status")
	q: Optional[str] = Field(None, description="Search across sku and name")
