"""Inventory API endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, get_current_user, get_db, get_tenant_id
from domain.inventory.schemas import (
	ItemCreateRequest,
	ItemFilters,
	ItemResponse,
	ItemUpdateRequest,
	StockAdjustmentRequest,
)
from domain.inventory.services import inventory_service
from shared.audit import AuditAction, log_action
from shared.pagination import PaginatedResponse, PageParams

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


def _request_context(request: Request) -> tuple[str, str]:
	ip_address = request.client.host if request.client else "unknown"
	user_agent = request.headers.get("user-agent", "unknown")
	return ip_address, user_agent


@router.get("/items", response_model=PaginatedResponse[ItemResponse])
async def list_items(
	request: Request,
	filters: ItemFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await inventory_service.list_items(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
	request: Request,
	data: ItemCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	item = await inventory_service.create_item(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="inventory",
		entity="items",
		entity_id=item.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(item)
	return item


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
	item_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await inventory_service.get_item(db, tenant_id, item_id)


@router.patch("/items/{item_id}", response_model=ItemResponse)
async def update_item(
	request: Request,
	item_id: UUID,
	data: ItemUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	item = await inventory_service.update_item(db, tenant_id, item_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="inventory",
		entity="items",
		entity_id=item.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(item)
	return item


@router.post("/stock-adjustments", status_code=status.HTTP_204_NO_CONTENT)
async def adjust_stock(
	request: Request,
	data: StockAdjustmentRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	adjustment = await inventory_service.adjust_stock(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="inventory",
		entity="stock_adjustments",
		entity_id=adjustment.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
