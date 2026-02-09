"""Filter utilities for SQL queries."""

from datetime import date, datetime
from typing import Any

from sqlalchemy import Select, and_, or_


def apply_text_filter(query: Select, column: Any, value: str | None) -> Select:
	"""Apply exact text match filter.
	
	Args:
		query: Base SQLAlchemy Select query
		column: SQLAlchemy column to filter
		value: Text value to match (case-sensitive)
		
	Returns:
		Query with filter applied (if value is not None)
	"""
	if value is not None:
		query = query.where(column == value)
	return query


def apply_text_search(query: Select, columns: list[Any], search: str | None) -> Select:
	"""Apply case-insensitive text search across multiple columns.
	
	Args:
		query: Base SQLAlchemy Select query
		columns: List of SQLAlchemy columns to search
		search: Search text (case-insensitive, partial match)
		
	Returns:
		Query with OR search filter applied (if search is not None)
	"""
	if search is not None and search.strip():
		search_pattern = f"%{search.strip()}%"
		conditions = [col.ilike(search_pattern) for col in columns]
		query = query.where(or_(*conditions))
	return query


def apply_enum_filter(query: Select, column: Any, value: Any | None) -> Select:
	"""Apply enum filter.
	
	Args:
		query: Base SQLAlchemy Select query
		column: SQLAlchemy enum column
		value: Enum value to match
		
	Returns:
		Query with filter applied (if value is not None)
	"""
	if value is not None:
		query = query.where(column == value)
	return query


def apply_uuid_filter(query: Select, column: Any, value: Any | None) -> Select:
	"""Apply UUID filter.
	
	Args:
		query: Base SQLAlchemy Select query
		column: SQLAlchemy UUID column
		value: UUID value to match
		
	Returns:
		Query with filter applied (if value is not None)
	"""
	if value is not None:
		query = query.where(column == value)
	return query


def apply_date_range_filter(
	query: Select,
	column: Any,
	date_from: date | datetime | None,
	date_to: date | datetime | None,
) -> Select:
	"""Apply date range filter (inclusive).
	
	Args:
		query: Base SQLAlchemy Select query
		column: SQLAlchemy date/datetime column
		date_from: Start date (inclusive, optional)
		date_to: End date (inclusive, optional)
		
	Returns:
		Query with date range filter applied
	"""
	conditions = []
	if date_from is not None:
		conditions.append(column >= date_from)
	if date_to is not None:
		conditions.append(column <= date_to)
	if conditions:
		query = query.where(and_(*conditions))
	return query


def apply_numeric_range_filter(
	query: Select,
	column: Any,
	min_value: int | float | None,
	max_value: int | float | None,
) -> Select:
	"""Apply numeric range filter (inclusive).
	
	Args:
		query: Base SQLAlchemy Select query
		column: SQLAlchemy numeric column
		min_value: Minimum value (inclusive, optional)
		max_value: Maximum value (inclusive, optional)
		
	Returns:
		Query with numeric range filter applied
	"""
	conditions = []
	if min_value is not None:
		conditions.append(column >= min_value)
	if max_value is not None:
		conditions.append(column <= max_value)
	if conditions:
		query = query.where(and_(*conditions))
	return query


def apply_sorting(query: Select, column_map: dict[str, Any], sort: str | None) -> Select:
	"""Apply sorting to query.
	
	Args:
		query: Base SQLAlchemy Select query
		column_map: Dict mapping field names to SQLAlchemy columns
		sort: Sort string in format "field:direction" (e.g., "created_at:desc")
		
	Returns:
		Query with ORDER BY applied
		
	Note:
		If sort is None or invalid, no sorting is applied.
		Valid directions: "asc", "desc"
	"""
	if sort is None:
		return query
		
	parts = sort.split(":")
	if len(parts) != 2:
		return query
		
	field, direction = parts
	if field not in column_map:
		return query
		
	column = column_map[field]
	if direction == "desc":
		query = query.order_by(column.desc())
	elif direction == "asc":
		query = query.order_by(column.asc())
		
	return query
