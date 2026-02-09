"""Sales API endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, get_current_user, get_db, get_tenant_id
from domain.sales.schemas import (
	OpportunityCreateRequest,
	OpportunityFilters,
	OpportunityResponse,
	OpportunityStageChangeRequest,
	OpportunityUpdateRequest,
)
from domain.sales.services import sales_service
from shared.audit import AuditAction, log_action
from shared.pagination import PaginatedResponse, PageParams

router = APIRouter(prefix="/api/v1/sales", tags=["sales"])


def _request_context(request: Request) -> tuple[str, str]:
	ip_address = request.client.host if request.client else "unknown"
	user_agent = request.headers.get("user-agent", "unknown")
	return ip_address, user_agent


@router.get("/opportunities", response_model=PaginatedResponse[OpportunityResponse])
async def list_opportunities(
	request: Request,
	filters: OpportunityFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await sales_service.list_opportunities(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post(
	"/opportunities",
	response_model=OpportunityResponse,
	status_code=status.HTTP_201_CREATED,
)
async def create_opportunity(
	request: Request,
	data: OpportunityCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	opportunity = await sales_service.create_opportunity(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="sales",
		entity="opportunities",
		entity_id=opportunity.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(opportunity)
	return opportunity


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
	opportunity_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await sales_service.get_opportunity(db, tenant_id, opportunity_id)


@router.patch("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
	request: Request,
	opportunity_id: UUID,
	data: OpportunityUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	opportunity = await sales_service.update_opportunity(db, tenant_id, opportunity_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="sales",
		entity="opportunities",
		entity_id=opportunity.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(opportunity)
	return opportunity


@router.post("/opportunities/{opportunity_id}/stage", response_model=OpportunityResponse)
async def change_stage(
	request: Request,
	opportunity_id: UUID,
	data: OpportunityStageChangeRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	opportunity = await sales_service.change_stage(db, tenant_id, opportunity_id, data.stage)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.stage_change,
		domain="sales",
		entity="opportunities",
		entity_id=opportunity.id,
		changes={"stage": {"old": None, "new": data.stage}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(opportunity)
	return opportunity
