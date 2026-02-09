"""Auth data access layer."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.auth.models import Role, User
from domain.auth.schemas import RoleFilters, UserFilters
from shared import utcnow
from shared.filters import apply_enum_filter, apply_sorting, apply_text_filter, apply_text_search
from shared.pagination import (
	PaginatedResponse,
	build_paginated_response,
	get_total_count,
	paginate_query,
)


async def create_user(session: AsyncSession, user: User) -> User:
	session.add(user)
	await session.flush()
	return user


async def list_users(
	session: AsyncSession,
	tenant_id: UUID,
	filters: UserFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[User]:
	query = select(User).where(User.tenant_id == tenant_id, User.deleted_at.is_(None))

	query = apply_text_filter(query, User.username, filters.username)
	query = apply_text_filter(query, User.email, filters.email)
	query = apply_enum_filter(query, User.status, filters.status)
	query = apply_text_search(query, [User.username, User.email], filters.q)
	if filters.role_id:
		query = query.where(User.role_ids.contains([str(filters.role_id)]))

	total = await get_total_count(session, query)

	column_map = {
		"username": User.username,
		"email": User.email,
		"status": User.status,
		"created_at": User.created_at,
		"updated_at": User.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_user(session: AsyncSession, tenant_id: UUID, user_id: UUID) -> User | None:
	result = await session.execute(
		select(User).where(
			User.tenant_id == tenant_id,
			User.id == user_id,
			User.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def get_user_by_username(
	session: AsyncSession, tenant_id: UUID, username: str
) -> User | None:
	result = await session.execute(
		select(User).where(
			User.tenant_id == tenant_id,
			User.username == username,
			User.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_user(session: AsyncSession, user: User) -> User:
	session.add(user)
	await session.flush()
	return user


async def soft_delete_user(session: AsyncSession, user: User) -> User:
	user.deleted_at = utcnow()
	session.add(user)
	await session.flush()
	return user


async def create_role(session: AsyncSession, role: Role) -> Role:
	session.add(role)
	await session.flush()
	return role


async def list_roles(
	session: AsyncSession,
	tenant_id: UUID,
	filters: RoleFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Role]:
	query = select(Role).where(Role.tenant_id == tenant_id, Role.deleted_at.is_(None))

	query = apply_text_filter(query, Role.name, filters.name)
	query = apply_text_search(query, [Role.name], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"name": Role.name,
		"created_at": Role.created_at,
		"updated_at": Role.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_role(session: AsyncSession, tenant_id: UUID, role_id: UUID) -> Role | None:
	result = await session.execute(
		select(Role).where(
			Role.tenant_id == tenant_id,
			Role.id == role_id,
			Role.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_role(session: AsyncSession, role: Role) -> Role:
	session.add(role)
	await session.flush()
	return role


async def get_user_scopes(session: AsyncSession, tenant_id: UUID, role_ids: list[str]) -> list[str]:
	"""Get aggregated scopes from user roles."""
	if not role_ids:
		return []
	
	# Convert string UUIDs to UUID objects
	role_uuid_list = [UUID(rid) for rid in role_ids]
	
	result = await session.execute(
		select(Role).where(
			Role.tenant_id == tenant_id,
			Role.id.in_(role_uuid_list),
			Role.deleted_at.is_(None),
		)
	)
	roles = result.scalars().all()
	
	# Aggregate all unique scopes from all roles
	all_scopes = set()
	for role in roles:
		if role.scopes:
			all_scopes.update(role.scopes)
	
	return sorted(list(all_scopes))
