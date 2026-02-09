"""Inventory data access layer."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.inventory.models import Item, StockAdjustment
from domain.inventory.schemas import ItemFilters
from shared import utcnow
from shared.filters import apply_enum_filter, apply_sorting, apply_text_filter, apply_text_search
from shared.pagination import (
	PaginatedResponse,
	build_paginated_response,
	get_total_count,
	paginate_query,
)


async def create_item(session: AsyncSession, item: Item) -> Item:
	session.add(item)
	await session.flush()
	return item


async def list_items(
	session: AsyncSession,
	tenant_id: UUID,
	filters: ItemFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Item]:
	query = select(Item).where(Item.tenant_id == tenant_id, Item.deleted_at.is_(None))

	query = apply_text_filter(query, Item.sku, filters.sku)
	query = apply_text_filter(query, Item.name, filters.name)
	query = apply_enum_filter(query, Item.status, filters.status)
	query = apply_text_search(query, [Item.sku, Item.name], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"sku": Item.sku,
		"name": Item.name,
		"status": Item.status,
		"created_at": Item.created_at,
		"updated_at": Item.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_item(session: AsyncSession, tenant_id: UUID, item_id: UUID) -> Item | None:
	result = await session.execute(
		select(Item).where(
			Item.tenant_id == tenant_id,
			Item.id == item_id,
			Item.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_item(session: AsyncSession, item: Item) -> Item:
	session.add(item)
	await session.flush()
	return item


async def soft_delete_item(session: AsyncSession, item: Item) -> Item:
	item.deleted_at = utcnow()
	session.add(item)
	await session.flush()
	return item


async def create_stock_adjustment(
	session: AsyncSession, adjustment: StockAdjustment
) -> StockAdjustment:
	session.add(adjustment)
	await session.flush()
	return adjustment
