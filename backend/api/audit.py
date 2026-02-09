"""Audit API endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, get_current_user, get_db, get_tenant_id
from shared.audit import AuditLog
from shared.pagination import PaginatedResponse, PageParams

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


class AuditLogResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	tenant_id: UUID
	actor_id: UUID
	actor_email: str
	action: str
	domain: str
	entity: str
	entity_id: UUID
	changes: dict
	ip_address: str
	user_agent: str
	endpoint: str
	occurred_at: datetime
	metadata: dict


@router.get("/logs", response_model=PaginatedResponse[AuditLogResponse])
async def list_logs(
	params: PageParams = Depends(),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	result = await db.execute(
		select(AuditLog).where(AuditLog.tenant_id == tenant_id).order_by(AuditLog.occurred_at)
	)
	items = list(result.scalars().all())
	total = len(items)
	page_items = items[(params.page - 1) * params.page_size : params.page * params.page_size]
	return PaginatedResponse(
		items=page_items,
		page=params.page,
		page_size=params.page_size,
		total=total,
		has_next=total > params.page * params.page_size,
	)


@router.get("/logs/{entity}/{entity_id}", response_model=PaginatedResponse[AuditLogResponse])
async def entity_logs(
	entity: str,
	entity_id: UUID,
	params: PageParams = Depends(),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	result = await db.execute(
		select(AuditLog).where(
			AuditLog.tenant_id == tenant_id,
			AuditLog.entity == entity,
			AuditLog.entity_id == entity_id,
		)
	)
	items = list(result.scalars().all())
	total = len(items)
	page_items = items[(params.page - 1) * params.page_size : params.page * params.page_size]
	return PaginatedResponse(
		items=page_items,
		page=params.page,
		page_size=params.page_size,
		total=total,
		has_next=total > params.page * params.page_size,
	)
