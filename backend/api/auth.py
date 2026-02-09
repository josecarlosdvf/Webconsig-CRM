"""Auth API endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, get_current_user, get_db, get_tenant_id
from domain.auth.schemas import (
	ChangePasswordRequest,
	LoginRequest,
	LoginResponse,
	RoleCreateRequest,
	RoleFilters,
	RoleResponse,
	UserCreateRequest,
	UserFilters,
	UserResponse,
	UserUpdateRequest,
)
from domain.auth.services import auth_service
from shared.audit import AuditAction, log_action
from shared.pagination import PaginatedResponse, PageParams

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _request_context(request: Request) -> tuple[str, str]:
	ip_address = request.client.host if request.client else "unknown"
	user_agent = request.headers.get("user-agent", "unknown")
	return ip_address, user_agent


@router.post("/login", response_model=LoginResponse)
async def login(
	request: Request,
	data: LoginRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
):
	token, expires_in, user_id, user_email = await auth_service.login(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=user_id,
		actor_email=user_email,
		action=AuditAction.login,
		domain="auth",
		entity="users",
		entity_id=user_id,
		changes={},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	return LoginResponse(access_token=token, expires_in=expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
	request: Request,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.logout,
		domain="auth",
		entity="users",
		entity_id=current_user.id,
		changes={},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()


@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
	request: Request,
	filters: UserFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await auth_service.list_users(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
	request: Request,
	data: UserCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	user = await auth_service.create_user(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="auth",
		entity="users",
		entity_id=user.id,
		changes={"username": data.username, "email": data.email},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(user)
	return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
	user_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await auth_service.get_user(db, tenant_id, user_id)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
	request: Request,
	user_id: UUID,
	data: UserUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	user = await auth_service.update_user(db, tenant_id, user_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="auth",
		entity="users",
		entity_id=user.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(user)
	return user


@router.post("/users/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
	request: Request,
	user_id: UUID,
	data: ChangePasswordRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	await auth_service.change_password(db, tenant_id, user_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.password_change,
		domain="auth",
		entity="users",
		entity_id=user_id,
		changes={},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()


@router.get("/roles", response_model=PaginatedResponse[RoleResponse])
async def list_roles(
	request: Request,
	filters: RoleFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await auth_service.list_roles(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
	request: Request,
	data: RoleCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	role = await auth_service.create_role(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="auth",
		entity="roles",
		entity_id=role.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(role)
	return role
