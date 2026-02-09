"""Finance API endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, get_current_user, get_db, get_tenant_id
from domain.finance.schemas import (
	AccountCreateRequest,
	AccountFilters,
	AccountResponse,
	AccountUpdateRequest,
	CompanyCreateRequest,
	CompanyFilters,
	CompanyResponse,
	CompanyUpdateRequest,
	PayableCreateRequest,
	PayableFilters,
	PayableResponse,
	PayableUpdateRequest,
	PaymentCreateRequest,
	PaymentFilters,
	PaymentResponse,
	ReceivableCreateRequest,
	ReceivableFilters,
	ReceivableResponse,
	ReceivableUpdateRequest,
)
from domain.finance.services import finance_service
from shared.audit import AuditAction, log_action
from shared.pagination import PaginatedResponse, PageParams

router = APIRouter(prefix="/api/v1/finance", tags=["finance"])


def _request_context(request: Request) -> tuple[str, str]:
	ip_address = request.client.host if request.client else "unknown"
	user_agent = request.headers.get("user-agent", "unknown")
	return ip_address, user_agent


@router.get("/companies", response_model=PaginatedResponse[CompanyResponse])
async def list_companies(
	request: Request,
	filters: CompanyFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await finance_service.list_companies(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
	request: Request,
	data: CompanyCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	company = await finance_service.create_company(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="finance",
		entity="companies",
		entity_id=company.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(company)
	return company


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
	company_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await finance_service.get_company(db, tenant_id, company_id)


@router.patch("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
	request: Request,
	company_id: UUID,
	data: CompanyUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	company = await finance_service.update_company(db, tenant_id, company_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="finance",
		entity="companies",
		entity_id=company.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(company)
	return company


@router.get("/accounts", response_model=PaginatedResponse[AccountResponse])
async def list_accounts(
	request: Request,
	filters: AccountFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await finance_service.list_accounts(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
	request: Request,
	data: AccountCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	account = await finance_service.create_account(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="finance",
		entity="accounts",
		entity_id=account.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(account)
	return account


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
	account_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await finance_service.get_account(db, tenant_id, account_id)


@router.patch("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
	request: Request,
	account_id: UUID,
	data: AccountUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	account = await finance_service.update_account(db, tenant_id, account_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="finance",
		entity="accounts",
		entity_id=account.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(account)
	return account


@router.get("/payments", response_model=PaginatedResponse[PaymentResponse])
async def list_payments(
	request: Request,
	filters: PaymentFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await finance_service.list_payments(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
	request: Request,
	data: PaymentCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	payment = await finance_service.create_payment(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="finance",
		entity="payments",
		entity_id=payment.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(payment)
	return payment


@router.post("/payments/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
	request: Request,
	payment_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	payment = await finance_service.confirm_payment(db, tenant_id, payment_id)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.confirm,
		domain="finance",
		entity="payments",
		entity_id=payment.id,
		changes={"status": {"old": "pending", "new": "confirmed"}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(payment)
	return payment


@router.get("/payables", response_model=PaginatedResponse[PayableResponse])
async def list_payables(
	request: Request,
	filters: PayableFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await finance_service.list_payables(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/payables", response_model=PayableResponse, status_code=status.HTTP_201_CREATED)
async def create_payable(
	request: Request,
	data: PayableCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	payable = await finance_service.create_payable(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="finance",
		entity="payables",
		entity_id=payable.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(payable)
	return payable


@router.get("/payables/{payable_id}", response_model=PayableResponse)
async def get_payable(
	payable_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await finance_service.get_payable(db, tenant_id, payable_id)


@router.patch("/payables/{payable_id}", response_model=PayableResponse)
async def update_payable(
	request: Request,
	payable_id: UUID,
	data: PayableUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	payable = await finance_service.update_payable(db, tenant_id, payable_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="finance",
		entity="payables",
		entity_id=payable.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(payable)
	return payable


@router.post("/payables/{payable_id}/pay", response_model=PayableResponse)
async def pay_payable(
	request: Request,
	payable_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	payable = await finance_service.pay_payable(db, tenant_id, payable_id)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.confirm,
		domain="finance",
		entity="payables",
		entity_id=payable.id,
		changes={"status": {"old": "pending", "new": "paid"}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(payable)
	return payable


@router.get("/receivables", response_model=PaginatedResponse[ReceivableResponse])
async def list_receivables(
	request: Request,
	filters: ReceivableFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await finance_service.list_receivables(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/receivables", response_model=ReceivableResponse, status_code=status.HTTP_201_CREATED)
async def create_receivable(
	request: Request,
	data: ReceivableCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	receivable = await finance_service.create_receivable(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="finance",
		entity="receivables",
		entity_id=receivable.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(receivable)
	return receivable


@router.get("/receivables/{receivable_id}", response_model=ReceivableResponse)
async def get_receivable(
	receivable_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await finance_service.get_receivable(db, tenant_id, receivable_id)


@router.patch("/receivables/{receivable_id}", response_model=ReceivableResponse)
async def update_receivable(
	request: Request,
	receivable_id: UUID,
	data: ReceivableUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	receivable = await finance_service.update_receivable(db, tenant_id, receivable_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="finance",
		entity="receivables",
		entity_id=receivable.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(receivable)
	return receivable


@router.post("/receivables/{receivable_id}/confirm", response_model=ReceivableResponse)
async def confirm_receivable(
	request: Request,
	receivable_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	receivable = await finance_service.confirm_receivable(db, tenant_id, receivable_id)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.confirm,
		domain="finance",
		entity="receivables",
		entity_id=receivable.id,
		changes={"status": {"old": "pending", "new": "confirmed"}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(receivable)
	return receivable
