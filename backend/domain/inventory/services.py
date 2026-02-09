"""Inventory business rules."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.inventory import repository
from domain.inventory.models import Item, ItemStatus, StockAdjustment
from domain.inventory.schemas import (
	ItemCreateRequest,
	ItemFilters,
	ItemUpdateRequest,
	StockAdjustmentRequest,
)
from shared.exceptions import not_found, validation_error
from shared.pagination import PaginatedResponse


VALID_ITEM_STATUS_TRANSITIONS = {
	ItemStatus.active: {ItemStatus.inactive},
	ItemStatus.inactive: {ItemStatus.active},
}


class InventoryService:
	async def list_items(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: ItemFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Item]:
		return await repository.list_items(session, tenant_id, filters, page, page_size, sort)

	async def create_item(
		self, session: AsyncSession, tenant_id: UUID, data: ItemCreateRequest
	) -> Item:
		item = Item(tenant_id=tenant_id, **data.model_dump())
		return await repository.create_item(session, item)

	async def get_item(self, session: AsyncSession, tenant_id: UUID, item_id: UUID) -> Item:
		item = await repository.get_item(session, tenant_id, item_id)
		if not item:
			raise not_found("Item not found")
		return item

	async def update_item(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		item_id: UUID,
		data: ItemUpdateRequest,
	) -> Item:
		item = await self.get_item(session, tenant_id, item_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "status" and value is not None and value != item.status:
				self._validate_status_transition(item.status, value)
			setattr(item, key, value)
		return await repository.update_item(session, item)

	async def adjust_stock(
		self, session: AsyncSession, tenant_id: UUID, data: StockAdjustmentRequest
	) -> StockAdjustment:
		adjustment = StockAdjustment(tenant_id=tenant_id, **data.model_dump())
		return await repository.create_stock_adjustment(session, adjustment)

	def _validate_status_transition(
		self, current_status: ItemStatus, new_status: ItemStatus
	) -> None:
		allowed = VALID_ITEM_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)


inventory_service = InventoryService()
