"""Billing data access layer."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.billing.models import Invoice
from domain.billing.schemas import InvoiceFilters
from shared import utcnow
from shared.filters import (
	apply_date_range_filter,
	apply_enum_filter,
	apply_sorting,
	apply_text_search,
)
from shared.pagination import (
	PaginatedResponse,
	build_paginated_response,
	get_total_count,
	paginate_query,
)


async def create_invoice(session: AsyncSession, invoice: Invoice) -> Invoice:
	session.add(invoice)
	await session.flush()
	return invoice


async def list_invoices(
	session: AsyncSession,
	tenant_id: UUID,
	filters: InvoiceFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Invoice]:
	query = select(Invoice).where(
		Invoice.tenant_id == tenant_id,
		Invoice.deleted_at.is_(None),
	)

	query = apply_enum_filter(query, Invoice.client_id, filters.client_id)
	query = apply_enum_filter(query, Invoice.status, filters.status)
	query = apply_date_range_filter(query, Invoice.due_date, filters.due_from, filters.due_to)
	query = apply_date_range_filter(
		query, Invoice.created_at, filters.created_from, filters.created_to
	)
	query = apply_text_search(query, [Invoice.currency], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"total": Invoice.total,
		"due_date": Invoice.due_date,
		"status": Invoice.status,
		"created_at": Invoice.created_at,
		"updated_at": Invoice.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_invoice(
	session: AsyncSession, tenant_id: UUID, invoice_id: UUID
) -> Invoice | None:
	result = await session.execute(
		select(Invoice).where(
			Invoice.tenant_id == tenant_id,
			Invoice.id == invoice_id,
			Invoice.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_invoice(session: AsyncSession, invoice: Invoice) -> Invoice:
	session.add(invoice)
	await session.flush()
	return invoice


async def soft_delete_invoice(session: AsyncSession, invoice: Invoice) -> Invoice:
	invoice.deleted_at = utcnow()
	session.add(invoice)
	await session.flush()
	return invoice
