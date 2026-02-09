"""Billing API endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, get_current_user, get_db, get_tenant_id
from domain.billing.schemas import (
	InvoiceCreateRequest,
	InvoiceFilters,
	InvoiceResponse,
	InvoiceUpdateRequest,
)
from domain.billing.services import billing_service
from shared.audit import AuditAction, log_action
from shared.pagination import PaginatedResponse, PageParams

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


def _request_context(request: Request) -> tuple[str, str]:
	ip_address = request.client.host if request.client else "unknown"
	user_agent = request.headers.get("user-agent", "unknown")
	return ip_address, user_agent


@router.get("/invoices", response_model=PaginatedResponse[InvoiceResponse])
async def list_invoices(
	request: Request,
	filters: InvoiceFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await billing_service.list_invoices(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
	request: Request,
	data: InvoiceCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	invoice = await billing_service.create_invoice(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="billing",
		entity="invoices",
		entity_id=invoice.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(invoice)
	return invoice


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
	invoice_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await billing_service.get_invoice(db, tenant_id, invoice_id)


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
	request: Request,
	invoice_id: UUID,
	data: InvoiceUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	invoice = await billing_service.update_invoice(db, tenant_id, invoice_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="billing",
		entity="invoices",
		entity_id=invoice.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(invoice)
	return invoice


@router.post("/invoices/{invoice_id}/mark-paid", response_model=InvoiceResponse)
async def mark_paid(
	request: Request,
	invoice_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	invoice = await billing_service.mark_paid(db, tenant_id, invoice_id)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.confirm,
		domain="billing",
		entity="invoices",
		entity_id=invoice.id,
		changes={"status": {"old": "draft", "new": "paid"}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(invoice)
	return invoice
