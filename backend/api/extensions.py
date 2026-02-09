"""Extensions API endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, get_current_user, get_db, get_tenant_id
from shared.audit import AuditAction, log_action
from shared.extensions import (
	ExtensionConfigUpdateRequest,
	ExtensionResponse,
	TenantExtensionResponse,
	extension_service,
)
from shared.pagination import PaginatedResponse, PageParams

router = APIRouter(prefix="/api/v1/extensions", tags=["extensions"])


def _request_context(request: Request) -> tuple[str, str]:
	ip_address = request.client.host if request.client else "unknown"
	user_agent = request.headers.get("user-agent", "unknown")
	return ip_address, user_agent


@router.get("", response_model=PaginatedResponse[ExtensionResponse])
async def list_extensions(
	params: PageParams = Depends(),
	db: AsyncSession = Depends(get_db),
):
	items = await extension_service.list_extensions(db)
	total = len(items)
	page_items = items[(params.page - 1) * params.page_size : params.page * params.page_size]
	return PaginatedResponse(
		items=page_items,
		page=params.page,
		page_size=params.page_size,
		total=total,
		has_next=total > params.page * params.page_size,
	)


@router.get("/{extension_id}", response_model=ExtensionResponse)
async def get_extension(
	extension_id: str,
	db: AsyncSession = Depends(get_db),
):
	try:
		return await extension_service.get_extension(db, extension_id)
	except ValueError as exc:
		raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{extension_id}/activate", response_model=TenantExtensionResponse)
async def activate_extension(
	request: Request,
	extension_id: str,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	tenant_extension = await extension_service.activate_extension(
		db, tenant_id, extension_id, current_user.id
	)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.activate_extension,
		domain="extensions",
		entity=extension_id,
		entity_id=tenant_extension.id,
		changes={"status": {"old": "inactive", "new": "active"}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(tenant_extension)
	return tenant_extension


@router.post("/{extension_id}/deactivate", response_model=TenantExtensionResponse)
async def deactivate_extension(
	request: Request,
	extension_id: str,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	tenant_extension = await extension_service.deactivate_extension(db, tenant_id, extension_id)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.deactivate_extension,
		domain="extensions",
		entity=extension_id,
		entity_id=tenant_extension.id,
		changes={"status": {"old": "active", "new": "inactive"}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(tenant_extension)
	return tenant_extension


@router.patch("/{extension_id}/config", response_model=TenantExtensionResponse)
async def update_config(
	request: Request,
	extension_id: str,
	data: ExtensionConfigUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	tenant_extension = await extension_service.update_config(
		db, tenant_id, extension_id, data.config
	)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="extensions",
		entity=extension_id,
		entity_id=tenant_extension.id,
		changes={"config": data.config},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(tenant_extension)
	return tenant_extension


@router.get("/tenant", response_model=PaginatedResponse[TenantExtensionResponse])
async def list_tenant_extensions(
	params: PageParams = Depends(),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	items = await extension_service.list_tenant_extensions(db, tenant_id)
	total = len(items)
	page_items = items[(params.page - 1) * params.page_size : params.page * params.page_size]
	return PaginatedResponse(
		items=page_items,
		page=params.page,
		page_size=params.page_size,
		total=total,
		has_next=total > params.page * params.page_size,
	)


@router.get("/tenant/{extension_id}", response_model=TenantExtensionResponse)
async def get_tenant_extension(
	extension_id: str,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	try:
		return await extension_service.get_tenant_extension(db, tenant_id, extension_id)
	except ValueError as exc:
		raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/tenant/{extension_id}/config")
async def get_tenant_config(
	extension_id: str,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	tenant_extension = await extension_service.get_tenant_extension(db, tenant_id, extension_id)
	return {"config": tenant_extension.config}
