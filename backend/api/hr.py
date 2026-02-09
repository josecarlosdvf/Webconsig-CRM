"""HR API endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, get_current_user, get_db, get_tenant_id
from domain.hr.schemas import (
	AbsenceCreateRequest,
	AbsenceFilters,
	AbsenceResponse,
	BenefitAssignRequest,
	BenefitCreateRequest,
	BenefitFilters,
	BenefitResponse,
	CandidateCreateRequest,
	CandidateFilters,
	CandidateResponse,
	CandidateStageRequest,
	CandidateUpdateRequest,
	ContractCreateRequest,
	ContractFilters,
	ContractResponse,
	DocumentCreateRequest,
	DocumentFilters,
	DocumentResponse,
	EmployeeCreateRequest,
	EmployeeFilters,
	EmployeeResponse,
	EmployeeTerminateRequest,
	EmployeeUpdateRequest,
	LeaveRequestCreateRequest,
	LeaveRequestFilters,
	LeaveRequestResponse,
	RecruitmentCreateRequest,
	RecruitmentFilters,
	RecruitmentResponse,
	RecruitmentUpdateRequest,
	TimeEntryCreateRequest,
	TimeEntryFilters,
	TimeEntryResponse,
)
from domain.hr.services import hr_service
from shared.audit import AuditAction, log_action
from shared.pagination import PaginatedResponse, PageParams

router = APIRouter(prefix="/api/v1/hr", tags=["hr"])


def _request_context(request: Request) -> tuple[str, str]:
	ip_address = request.client.host if request.client else "unknown"
	user_agent = request.headers.get("user-agent", "unknown")
	return ip_address, user_agent


@router.get("/employees", response_model=PaginatedResponse[EmployeeResponse])
async def list_employees(
	request: Request,
	filters: EmployeeFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.list_employees(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
	request: Request,
	data: EmployeeCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	employee = await hr_service.create_employee(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="hr",
		entity="employees",
		entity_id=employee.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(employee)
	return employee


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
	employee_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.get_employee(db, tenant_id, employee_id)


@router.patch("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
	request: Request,
	employee_id: UUID,
	data: EmployeeUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	employee = await hr_service.update_employee(db, tenant_id, employee_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="hr",
		entity="employees",
		entity_id=employee.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(employee)
	return employee


@router.post("/employees/{employee_id}/terminate", response_model=EmployeeResponse)
async def terminate_employee(
	request: Request,
	employee_id: UUID,
	data: EmployeeTerminateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	employee = await hr_service.terminate_employee(db, tenant_id, employee_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.terminate,
		domain="hr",
		entity="employees",
		entity_id=employee.id,
		changes={"status": {"old": "active", "new": "terminated"}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(employee)
	return employee


@router.get("/recruitments", response_model=PaginatedResponse[RecruitmentResponse])
async def list_recruitments(
	request: Request,
	filters: RecruitmentFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.list_recruitments(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post(
	"/recruitments",
	response_model=RecruitmentResponse,
	status_code=status.HTTP_201_CREATED,
)
async def create_recruitment(
	request: Request,
	data: RecruitmentCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	recruitment = await hr_service.create_recruitment(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="hr",
		entity="recruitments",
		entity_id=recruitment.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(recruitment)
	return recruitment


@router.get("/recruitments/{recruitment_id}", response_model=RecruitmentResponse)
async def get_recruitment(
	recruitment_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.get_recruitment(db, tenant_id, recruitment_id)


@router.patch("/recruitments/{recruitment_id}", response_model=RecruitmentResponse)
async def update_recruitment(
	request: Request,
	recruitment_id: UUID,
	data: RecruitmentUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	recruitment = await hr_service.update_recruitment(db, tenant_id, recruitment_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="hr",
		entity="recruitments",
		entity_id=recruitment.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(recruitment)
	return recruitment


@router.get("/candidates", response_model=PaginatedResponse[CandidateResponse])
async def list_candidates(
	request: Request,
	filters: CandidateFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.list_candidates(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
	request: Request,
	data: CandidateCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	candidate = await hr_service.create_candidate(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="hr",
		entity="candidates",
		entity_id=candidate.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(candidate)
	return candidate


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
	candidate_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.get_candidate(db, tenant_id, candidate_id)


@router.patch("/candidates/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
	request: Request,
	candidate_id: UUID,
	data: CandidateUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	candidate = await hr_service.update_candidate(db, tenant_id, candidate_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.update,
		domain="hr",
		entity="candidates",
		entity_id=candidate.id,
		changes=data.model_dump(exclude_unset=True),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(candidate)
	return candidate


@router.post("/candidates/{candidate_id}/advance", response_model=CandidateResponse)
async def advance_candidate(
	request: Request,
	candidate_id: UUID,
	data: CandidateStageRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	candidate = await hr_service.advance_candidate(db, tenant_id, candidate_id, data.stage)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.stage_change,
		domain="hr",
		entity="candidates",
		entity_id=candidate.id,
		changes={"status": {"old": None, "new": data.stage}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(candidate)
	return candidate


@router.get("/absences", response_model=PaginatedResponse[AbsenceResponse])
async def list_absences(
	request: Request,
	filters: AbsenceFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.list_absences(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/absences", response_model=AbsenceResponse, status_code=status.HTTP_201_CREATED)
async def create_absence(
	request: Request,
	data: AbsenceCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	absence = await hr_service.create_absence(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="hr",
		entity="absences",
		entity_id=absence.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(absence)
	return absence


@router.get("/time-entries", response_model=PaginatedResponse[TimeEntryResponse])
async def list_time_entries(
	request: Request,
	filters: TimeEntryFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.list_time_entries(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/time-entries", response_model=TimeEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_time_entry(
	request: Request,
	data: TimeEntryCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	time_entry = await hr_service.create_time_entry(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="hr",
		entity="time_entries",
		entity_id=time_entry.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(time_entry)
	return time_entry


@router.post("/time-entries/{time_entry_id}/approve", response_model=TimeEntryResponse)
async def approve_time_entry(
	request: Request,
	time_entry_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	time_entry = await hr_service.approve_time_entry(db, tenant_id, time_entry_id)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.approve,
		domain="hr",
		entity="time_entries",
		entity_id=time_entry.id,
		changes={"status": {"old": "pending", "new": "approved"}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(time_entry)
	return time_entry


@router.get("/leave-requests", response_model=PaginatedResponse[LeaveRequestResponse])
async def list_leave_requests(
	request: Request,
	filters: LeaveRequestFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.list_leave_requests(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/leave-requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_request(
	request: Request,
	data: LeaveRequestCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	leave_request = await hr_service.create_leave_request(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="hr",
		entity="leave_requests",
		entity_id=leave_request.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(leave_request)
	return leave_request


@router.post("/leave-requests/{leave_request_id}/approve", response_model=LeaveRequestResponse)
async def approve_leave_request(
	request: Request,
	leave_request_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	leave_request = await hr_service.approve_leave_request(db, tenant_id, leave_request_id)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.approve,
		domain="hr",
		entity="leave_requests",
		entity_id=leave_request.id,
		changes={"status": {"old": "requested", "new": "approved"}},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(leave_request)
	return leave_request


@router.get("/documents", response_model=PaginatedResponse[DocumentResponse])
async def list_documents(
	request: Request,
	filters: DocumentFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.list_documents(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
	request: Request,
	data: DocumentCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	document = await hr_service.create_document(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="hr",
		entity="documents",
		entity_id=document.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(document)
	return document


@router.get("/contracts", response_model=PaginatedResponse[ContractResponse])
async def list_contracts(
	request: Request,
	filters: ContractFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.list_contracts(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/contracts", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
	request: Request,
	data: ContractCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	contract = await hr_service.create_contract(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="hr",
		entity="contracts",
		entity_id=contract.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(contract)
	return contract


@router.get("/benefits", response_model=PaginatedResponse[BenefitResponse])
async def list_benefits(
	request: Request,
	filters: BenefitFilters = Depends(),
	params: PageParams = Depends(),
	sort: str | None = Query(None, description="Sort (e.g., 'created_at:desc')"),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await hr_service.list_benefits(
		db, tenant_id, filters, params.page, params.page_size, sort
	)


@router.post("/benefits", response_model=BenefitResponse, status_code=status.HTTP_201_CREATED)
async def create_benefit(
	request: Request,
	data: BenefitCreateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	benefit = await hr_service.create_benefit(db, tenant_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.create,
		domain="hr",
		entity="benefits",
		entity_id=benefit.id,
		changes=data.model_dump(),
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(benefit)
	return benefit


@router.post("/benefits/{benefit_id}/assign", response_model=BenefitResponse)
async def assign_benefit(
	request: Request,
	benefit_id: UUID,
	data: BenefitAssignRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	benefit = await hr_service.assign_benefit(db, tenant_id, benefit_id, data)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.assign,
		domain="hr",
		entity="benefits",
		entity_id=benefit.id,
		changes={"employee_id": data.employee_id},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
	)
	await db.commit()
	await db.refresh(benefit)
	return benefit
