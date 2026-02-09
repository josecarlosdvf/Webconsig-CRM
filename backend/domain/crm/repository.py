"""CRM data access layer."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.crm.models import Client, Lead
from domain.crm.schemas import ClientFilters, LeadFilters
from shared import utcnow
from shared.filters import (
	apply_date_range_filter,
	apply_enum_filter,
	apply_sorting,
	apply_text_filter,
	apply_text_search,
)
from shared.pagination import (
	PaginatedResponse,
	build_paginated_response,
	get_total_count,
	paginate_query,
)


# ====================
# Client repository
# ====================


async def create_client(session: AsyncSession, client: Client) -> Client:
	"""Create a new client."""
	session.add(client)
	await session.flush()
	return client


async def list_clients(
	session: AsyncSession,
	tenant_id: UUID,
	filters: ClientFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Client]:
	"""List clients with SQL-level pagination, filtering, and sorting.
	
	Args:
		session: Database session
		tenant_id: Tenant ID for row-level isolation
		filters: Filter parameters
		page: Page number (1-indexed)
		page_size: Items per page
		sort: Sort string (e.g., "created_at:desc")
		
	Returns:
		PaginatedResponse with clients for current page
	"""
	# Base query: tenant isolation + soft-delete filter
	query = select(Client).where(
		Client.tenant_id == tenant_id,
		Client.deleted_at.is_(None),
	)
	
	# Apply filters
	query = apply_text_filter(query, Client.name, filters.name)
	query = apply_text_filter(query, Client.email, filters.email)
	query = apply_text_filter(query, Client.document, filters.document)
	query = apply_enum_filter(query, Client.status, filters.status)
	query = apply_date_range_filter(query, Client.created_at, filters.created_from, filters.created_to)
	
	# Apply text search across multiple columns
	query = apply_text_search(query, [Client.name, Client.email, Client.document], filters.q)
	
	# Get total count BEFORE pagination
	total = await get_total_count(session, query)
	
	# Apply sorting
	column_map = {
		"name": Client.name,
		"email": Client.email,
		"created_at": Client.created_at,
		"updated_at": Client.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	
	# Apply pagination (LIMIT/OFFSET)
	query = paginate_query(query, page, page_size)
	
	# Execute query
	result = await session.execute(query)
	items = list(result.scalars().all())
	
	# Build paginated response
	return build_paginated_response(items, page, page_size, total)


async def get_client(
	session: AsyncSession, tenant_id: UUID, client_id: UUID
) -> Client | None:
	"""Get a single client by ID."""
	result = await session.execute(
		select(Client).where(
			Client.tenant_id == tenant_id,
			Client.id == client_id,
			Client.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_client(session: AsyncSession, client: Client) -> Client:
	"""Update an existing client."""
	session.add(client)
	await session.flush()
	return client


async def soft_delete_client(session: AsyncSession, client: Client) -> Client:
	"""Soft-delete a client (set deleted_at timestamp)."""
	client.deleted_at = utcnow()
	session.add(client)
	await session.flush()
	return client


# ====================
# Lead repository
# ====================


async def create_lead(session: AsyncSession, lead: Lead) -> Lead:
	"""Create a new lead."""
	session.add(lead)
	await session.flush()
	return lead


async def list_leads(
	session: AsyncSession,
	tenant_id: UUID,
	filters: LeadFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Lead]:
	"""List leads with SQL-level pagination, filtering, and sorting.
	
	Args:
		session: Database session
		tenant_id: Tenant ID for row-level isolation
		filters: Filter parameters
		page: Page number (1-indexed)
		page_size: Items per page
		sort: Sort string (e.g., "created_at:desc")
		
	Returns:
		PaginatedResponse with leads for current page
	"""
	# Base query: tenant isolation + soft-delete filter
	query = select(Lead).where(
		Lead.tenant_id == tenant_id,
		Lead.deleted_at.is_(None),
	)
	
	# Apply filters
	query = apply_text_filter(query, Lead.name, filters.name)
	query = apply_text_filter(query, Lead.email, filters.email)
	query = apply_text_filter(query, Lead.source, filters.source)
	query = apply_enum_filter(query, Lead.status, filters.status)
	query = apply_date_range_filter(query, Lead.created_at, filters.created_from, filters.created_to)
	
	# Apply text search across multiple columns
	query = apply_text_search(query, [Lead.name, Lead.email, Lead.source], filters.q)
	
	# Get total count BEFORE pagination
	total = await get_total_count(session, query)
	
	# Apply sorting
	column_map = {
		"name": Lead.name,
		"email": Lead.email,
		"created_at": Lead.created_at,
		"updated_at": Lead.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	
	# Apply pagination (LIMIT/OFFSET)
	query = paginate_query(query, page, page_size)
	
	# Execute query
	result = await session.execute(query)
	items = list(result.scalars().all())
	
	# Build paginated response
	return build_paginated_response(items, page, page_size, total)


async def get_lead(session: AsyncSession, tenant_id: UUID, lead_id: UUID) -> Lead | None:
	"""Get a single lead by ID."""
	result = await session.execute(
		select(Lead).where(
			Lead.tenant_id == tenant_id,
			Lead.id == lead_id,
			Lead.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_lead(session: AsyncSession, lead: Lead) -> Lead:
	"""Update an existing lead."""
	session.add(lead)
	await session.flush()
	return lead


async def soft_delete_lead(session: AsyncSession, lead: Lead) -> Lead:
	"""Soft-delete a lead (set deleted_at timestamp)."""
	lead.deleted_at = utcnow()
	session.add(lead)
	await session.flush()
	return lead

