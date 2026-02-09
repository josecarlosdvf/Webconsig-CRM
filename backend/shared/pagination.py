"""Pagination utilities for SQL queries."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PageParams(BaseModel):
	"""Query parameters for pagination."""
	page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
	page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class SortParams(BaseModel):
	"""Query parameters for sorting."""
	sort: str | None = Field(
		default=None,
		description="Sort field and direction (e.g., 'created_at:desc' or 'name:asc')",
		pattern=r"^[a-z_]+:(asc|desc)$",
	)


class PaginatedResponse(BaseModel, Generic[T]):
	"""Paginated response wrapper."""
	items: list[T]
	page: int
	page_size: int
	total: int
	has_next: bool


def paginate_query(query: Select, page: int, page_size: int) -> Select:
	"""Apply LIMIT and OFFSET to SQLAlchemy query.
	
	Args:
		query: Base SQLAlchemy Select query
		page: Page number (1-indexed)
		page_size: Number of items per page
		
	Returns:
		Query with LIMIT/OFFSET applied
	"""
	offset = (page - 1) * page_size
	return query.limit(page_size).offset(offset)


async def get_total_count(session: AsyncSession, query: Select) -> int:
	"""Get total count for a query (without LIMIT/OFFSET).
	
	Args:
		session: Async database session
		query: Base SQLAlchemy Select query (without pagination)
		
	Returns:
		Total number of records matching the query
	"""
	# Remove order_by, limit, offset for count query
	count_query = query.with_only_columns(func.count()).order_by(None).limit(None).offset(None)
	result = await session.execute(count_query)
	return result.scalar_one()


def build_paginated_response(
	items: list[T],
	page: int,
	page_size: int,
	total: int,
) -> PaginatedResponse[T]:
	"""Build PaginatedResponse from query results.
	
	Args:
		items: List of items for current page
		page: Current page number
		page_size: Items per page
		total: Total number of items across all pages
		
	Returns:
		PaginatedResponse object
	"""
	has_next = (page * page_size) < total
	return PaginatedResponse(
		items=items,
		page=page,
		page_size=page_size,
		total=total,
		has_next=has_next,
	)
