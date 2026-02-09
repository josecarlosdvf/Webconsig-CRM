"""Sales data access layer."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.sales.models import Opportunity
from domain.sales.schemas import OpportunityFilters
from shared import utcnow
from shared.filters import (
	apply_date_range_filter,
	apply_enum_filter,
	apply_numeric_range_filter,
	apply_sorting,
	apply_text_search,
)
from shared.pagination import (
	PaginatedResponse,
	build_paginated_response,
	get_total_count,
	paginate_query,
)


async def create_opportunity(session: AsyncSession, opportunity: Opportunity) -> Opportunity:
	session.add(opportunity)
	await session.flush()
	return opportunity


async def list_opportunities(
	session: AsyncSession,
	tenant_id: UUID,
	filters: OpportunityFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Opportunity]:
	query = select(Opportunity).where(
		Opportunity.tenant_id == tenant_id,
		Opportunity.deleted_at.is_(None),
	)

	query = apply_enum_filter(query, Opportunity.client_id, filters.client_id)
	query = apply_enum_filter(query, Opportunity.stage, filters.stage)
	query = apply_numeric_range_filter(query, Opportunity.value, filters.value_min, filters.value_max)
	query = apply_date_range_filter(query, Opportunity.created_at, filters.created_from, filters.created_to)
	query = apply_text_search(query, [Opportunity.title], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"title": Opportunity.title,
		"value": Opportunity.value,
		"stage": Opportunity.stage,
		"created_at": Opportunity.created_at,
		"updated_at": Opportunity.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_opportunity(
	session: AsyncSession, tenant_id: UUID, opportunity_id: UUID
) -> Opportunity | None:
	result = await session.execute(
		select(Opportunity).where(
			Opportunity.tenant_id == tenant_id,
			Opportunity.id == opportunity_id,
			Opportunity.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_opportunity(session: AsyncSession, opportunity: Opportunity) -> Opportunity:
	session.add(opportunity)
	await session.flush()
	return opportunity


async def soft_delete_opportunity(session: AsyncSession, opportunity: Opportunity) -> Opportunity:
	opportunity.deleted_at = utcnow()
	session.add(opportunity)
	await session.flush()
	return opportunity
