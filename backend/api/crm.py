"""CRM API endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, get_current_user, get_db, get_tenant_id, require_scopes
from domain.crm.schemas import (
    ClientCreateRequest,
    ClientFilters,
    ClientResponse,
    ClientUpdateRequest,
    LeadCreateRequest,
    LeadFilters,
    LeadResponse,
    LeadUpdateRequest,
)
from domain.crm.services import crm_service
from shared.audit import AuditAction, log_action
from shared.pagination import PageParams, PaginatedResponse
from shared.scopes import CRM_READ, CRM_WRITE

router = APIRouter(prefix="/api/v1/crm", tags=["crm"])


def _request_context(request: Request) -> tuple[str, str]:
    """Extract IP address and user agent from request."""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    return ip_address, user_agent


# ====================
# Client endpoints
# ====================


@router.get(
    "/clients",
    response_model=PaginatedResponse[ClientResponse],
    dependencies=[Depends(require_scopes(CRM_READ))]
)
async def list_clients(
    request: Request,
    filters: ClientFilters = Depends(),
    params: PageParams = Depends(),
    sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """List clients with SQL-level pagination, filtering, and sorting.
    
    Requires: crm:read scope
    """
    result = await crm_service.list_clients(
        db, tenant_id, filters, params.page, params.page_size, sort
    )
    return result


@router.post(
    "/clients",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_scopes(CRM_WRITE))]
)
async def create_client(
    request: Request,
    data: ClientCreateRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a new client.
    
    Requires: crm:write scope
    """
    client = await crm_service.create_client(db, tenant_id, data)
    ip_address, user_agent = _request_context(request)
    await log_action(
        db,
        tenant_id=tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        action=AuditAction.create,
        domain="crm",
        entity="clients",
        entity_id=client.id,
        changes=data.model_dump(),
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint=str(request.url.path),
        occurred_at=datetime.now(timezone.utc),
    )
    return client


@router.get(
    "/clients/{client_id}",
    response_model=ClientResponse,
    dependencies=[Depends(require_scopes(CRM_READ))]
)
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Get a single client by ID.
    
    Requires: crm:read scope
    """
    return await crm_service.get_client(db, tenant_id, client_id)


@router.patch(
    "/clients/{client_id}",
    response_model=ClientResponse,
    dependencies=[Depends(require_scopes(CRM_WRITE))]
)
async def update_client(
    request: Request,
    client_id: UUID,
    data: ClientUpdateRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update a client (with state transition validation).
    
    Requires: crm:write scope
    """
    old_client = await crm_service.get_client(db, tenant_id, client_id)
    updated_client = await crm_service.update_client(db, tenant_id, client_id, data)
    ip_address, user_agent = _request_context(request)
    await log_action(
        db,
        tenant_id=tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        action=AuditAction.update,
        domain="crm",
        entity="clients",
        entity_id=client_id,
        changes=_compute_changes(old_client, updated_client, data),
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint=str(request.url.path),
        occurred_at=datetime.now(timezone.utc),
    )
    return updated_client


@router.delete(
    "/clients/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_scopes(CRM_WRITE))]
)
async def delete_client(
    request: Request,
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Soft-delete a client.
    
    Requires: crm:write scope
    """
    old_client = await crm_service.get_client(db, tenant_id, client_id)
    await crm_service.delete_client(db, tenant_id, client_id)
    ip_address, user_agent = _request_context(request)
    await log_action(
        db,
        tenant_id=tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        action=AuditAction.delete,
        domain="crm",
        entity="clients",
        entity_id=client_id,
        changes={"deleted_at": {"old": None, "new": datetime.now(timezone.utc).isoformat()}},
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint=str(request.url.path),
        occurred_at=datetime.now(timezone.utc),
    )


# ====================
# Lead endpoints
# ====================


@router.get(
    "/leads",
    response_model=PaginatedResponse[LeadResponse],
    dependencies=[Depends(require_scopes(CRM_READ))]
)
async def list_leads(
    request: Request,
    filters: LeadFilters = Depends(),
    params: PageParams = Depends(),
    sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """List leads with SQL-level pagination, filtering, and sorting.
    
    Requires: crm:read scope
    """
    result = await crm_service.list_leads(
        db, tenant_id, filters, params.page, params.page_size, sort
    )
    return result


@router.post(
    "/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_scopes(CRM_WRITE))]
)
async def create_lead(
    request: Request,
    data: LeadCreateRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a new lead.
    
    Requires: crm:write scope
    """
    lead = await crm_service.create_lead(db, tenant_id, data)
    ip_address, user_agent = _request_context(request)
    await log_action(
        db,
        tenant_id=tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        action=AuditAction.create,
        domain="crm",
        entity="leads",
        entity_id=lead.id,
        changes=data.model_dump(),
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint=str(request.url.path),
        occurred_at=datetime.now(timezone.utc),
    )
    return lead


@router.get(
    "/leads/{lead_id}",
    response_model=LeadResponse,
    dependencies=[Depends(require_scopes(CRM_READ))]
)
async def get_lead(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Get a single lead by ID.
    
    Requires: crm:read scope
    """
    return await crm_service.get_lead(db, tenant_id, lead_id)


@router.patch(
    "/leads/{lead_id}",
    response_model=LeadResponse,
    dependencies=[Depends(require_scopes(CRM_WRITE))]
)
async def update_lead(
    request: Request,
    lead_id: UUID,
    data: LeadUpdateRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update a lead (with state transition validation).
    
    Requires: crm:write scope
    """
    old_lead = await crm_service.get_lead(db, tenant_id, lead_id)
    updated_lead = await crm_service.update_lead(db, tenant_id, lead_id, data)
    ip_address, user_agent = _request_context(request)
    await log_action(
        db,
        tenant_id=tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        action=AuditAction.update,
        domain="crm",
        entity="leads",
        entity_id=lead_id,
        changes=_compute_changes(old_lead, updated_lead, data),
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint=str(request.url.path),
        occurred_at=datetime.now(timezone.utc),
    )
    return updated_lead


@router.delete(
    "/leads/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_scopes(CRM_WRITE))]
)
async def delete_lead(
    request: Request,
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Soft-delete a lead.
    
    Requires: crm:write scope
    """
    old_lead = await crm_service.get_lead(db, tenant_id, lead_id)
    await crm_service.delete_lead(db, tenant_id, lead_id)
    ip_address, user_agent = _request_context(request)
    await log_action(
        db,
        tenant_id=tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        action=AuditAction.delete,
        domain="crm",
        entity="leads",
        entity_id=lead_id,
        changes={"deleted_at": {"old": None, "new": datetime.now(timezone.utc).isoformat()}},
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint=str(request.url.path),
        occurred_at=datetime.now(timezone.utc),
    )


@router.post(
    "/leads/{lead_id}/convert",
    response_model=ClientResponse,
    dependencies=[Depends(require_scopes(CRM_WRITE))]
)
async def convert_lead(
    request: Request,
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Convert a lead to a client (with validation).
    
    Requires: crm:write scope
    """
    client = await crm_service.convert_lead_to_client(db, tenant_id, lead_id)
    ip_address, user_agent = _request_context(request)
    await log_action(
        db,
        tenant_id=tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        action=AuditAction.convert,
        domain="crm",
        entity="leads",
        entity_id=lead_id,
        changes={"converted_to_client_id": str(client.id)},
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint=str(request.url.path),
        occurred_at=datetime.now(timezone.utc),
    )
    return client


def _compute_changes(old_entity, new_entity, update_request) -> dict:
    """Compute changes between old and new entity based on update request."""
    changes = {}
    for field in update_request.model_dump(exclude_unset=True).keys():
        old_value = getattr(old_entity, field, None)
        new_value = getattr(new_entity, field, None)
        if old_value != new_value:
            changes[field] = {"old": old_value, "new": new_value}
    return changes
