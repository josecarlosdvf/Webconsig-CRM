"""HR business rules."""

from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.hr import repository
from domain.hr.models import (
	Benefit,
	BenefitStatus,
	Candidate,
	CandidateStatus,
	Employee,
	EmployeeStatus,
	LeaveRequestStatus,
	RecruitmentStatus,
	LeaveRequestStatus,
	TimeEntryStatus,
)
from domain.hr.schemas import (
	AbsenceCreateRequest,
	AbsenceFilters,
	BenefitAssignRequest,
	BenefitCreateRequest,
	BenefitFilters,
	CandidateCreateRequest,
	CandidateFilters,
	CandidateUpdateRequest,
	ContractCreateRequest,
	ContractFilters,
	DocumentCreateRequest,
	DocumentFilters,
	EmployeeCreateRequest,
	EmployeeFilters,
	EmployeeTerminateRequest,
	EmployeeUpdateRequest,
	LeaveRequestCreateRequest,
	LeaveRequestFilters,
	RecruitmentCreateRequest,
	RecruitmentFilters,
	RecruitmentUpdateRequest,
	TimeEntryCreateRequest,
	TimeEntryFilters,
)
from domain.hr.models import Absence, Contract, Document, LeaveRequest, Recruitment, TimeEntry
from domain.hr import events
from domain.finance.models import Company
from shared.exceptions import not_found, validation_error
from shared.pagination import PaginatedResponse
from shared.validators import validate_fk_same_tenant


VALID_EMPLOYEE_STATUS_TRANSITIONS = {
	EmployeeStatus.active: {EmployeeStatus.inactive, EmployeeStatus.terminated},
	EmployeeStatus.inactive: {EmployeeStatus.active, EmployeeStatus.terminated},
	EmployeeStatus.terminated: set(),
}

VALID_RECRUITMENT_STATUS_TRANSITIONS = {
	RecruitmentStatus.open: {RecruitmentStatus.on_hold, RecruitmentStatus.closed},
	RecruitmentStatus.on_hold: {RecruitmentStatus.open, RecruitmentStatus.closed},
	RecruitmentStatus.closed: set(),
}

VALID_CANDIDATE_STATUS_TRANSITIONS = {
	CandidateStatus.applied: {CandidateStatus.screening, CandidateStatus.rejected},
	CandidateStatus.screening: {CandidateStatus.interview, CandidateStatus.rejected},
	CandidateStatus.interview: {CandidateStatus.offer, CandidateStatus.rejected},
	CandidateStatus.offer: {CandidateStatus.hired, CandidateStatus.rejected},
	CandidateStatus.hired: set(),
	CandidateStatus.rejected: set(),
}

VALID_TIME_ENTRY_STATUS_TRANSITIONS = {
	TimeEntryStatus.pending: {TimeEntryStatus.approved, TimeEntryStatus.rejected},
	TimeEntryStatus.approved: set(),
	TimeEntryStatus.rejected: set(),
}

VALID_LEAVE_REQUEST_STATUS_TRANSITIONS = {
	LeaveRequestStatus.requested: {
		LeaveRequestStatus.approved,
		LeaveRequestStatus.rejected,
		LeaveRequestStatus.canceled,
	},
	LeaveRequestStatus.approved: set(),
	LeaveRequestStatus.rejected: set(),
	LeaveRequestStatus.canceled: set(),
}

VALID_BENEFIT_STATUS_TRANSITIONS = {
	BenefitStatus.active: {BenefitStatus.suspended, BenefitStatus.canceled},
	BenefitStatus.suspended: {BenefitStatus.active, BenefitStatus.canceled},
	BenefitStatus.canceled: set(),
}


class HrService:
	async def list_employees(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: EmployeeFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Employee]:
		return await repository.list_employees(session, tenant_id, filters, page, page_size, sort)

	async def create_employee(
		self, session: AsyncSession, tenant_id: UUID, data: EmployeeCreateRequest
	) -> Employee:
		# Validate company belongs to same tenant
		await validate_fk_same_tenant(
			session, Company, data.company_id, tenant_id, "company_id"
		)
		
		employee = Employee(tenant_id=tenant_id, **data.model_dump())
		result = await repository.create_employee(session, employee)
		
		# Emit event
		await events.emit_employee_created(tenant_id, result.id, actor_id)
		
		return result

	async def get_employee(
		self, session: AsyncSession, tenant_id: UUID, employee_id: UUID
	) -> Employee:
		employee = await repository.get_employee(session, tenant_id, employee_id)
		if not employee:
			raise not_found("Employee not found")
		return employee

	async def update_employee(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		employee_id: UUID,
		data: EmployeeUpdateRequest,
	) -> Employee:
		employee = await self.get_employee(session, tenant_id, employee_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "status" and value is not None and value != employee.status:
				self._validate_employee_status(employee.status, value)
			setattr(employee, key, value)
		return await repository.update_employee(session, employee)

	async def terminate_employee(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		employee_id: UUID,
		data: EmployeeTerminateRequest,
		actor_id: UUID | None = None,
	) -> Employee:
		employee = await self.get_employee(session, tenant_id, employee_id)
		self._validate_employee_status(employee.status, EmployeeStatus.terminated)
		employee.status = EmployeeStatus.terminated
		employee.terminated_at = date.today()
		employee.termination_reason = data.reason
		return await repository.update_employee(session, employee)

	async def list_recruitments(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: RecruitmentFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
		actor_id: UUID | None = None,
	) -> PaginatedResponse[Recruitment]:
		return await repository.list_recruitments(session, tenant_id, filters, page, page_size, sort)

	async def create_recruitment(
		self, session: AsyncSession, tenant_id: UUID, data: RecruitmentCreateRequest,
		actor_id: UUID | None = None,
	) -> Recruitment:
		recruitment = Recruitment(tenant_id=tenant_id, **data.model_dump())
		result = await repository.create_recruitment(session, recruitment)
		
		# Emit event
		await events.emit_recruitment_created(tenant_id, result.id, actor_id)
		
		return result

	async def get_recruitment(
		self, session: AsyncSession, tenant_id: UUID, recruitment_id: UUID,
		actor_id: UUID | None = None,
	) -> Recruitment:
		recruitment = await repository.get_recruitment(session, tenant_id, recruitment_id)
		if not recruitment:
			raise not_found("Recruitment not found")
		return recruitment

	async def update_recruitment(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		recruitment_id: UUID,
		data: RecruitmentUpdateRequest,
		actor_id: UUID | None = None,
	) -> Recruitment:
		recruitment = await self.get_recruitment(session, tenant_id, recruitment_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "status" and value is not None and value != recruitment.status:
				self._validate_recruitment_status(recruitment.status, value)
			setattr(recruitment, key, value)
		return await repository.update_recruitment(session, recruitment)

	async def list_candidates(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: CandidateFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
		actor_id: UUID | None = None,
	) -> PaginatedResponse[Candidate]:
		return await repository.list_candidates(session, tenant_id, filters, page, page_size, sort)

	async def create_candidate(
		self, session: AsyncSession, tenant_id: UUID, data: CandidateCreateRequest,
		actor_id: UUID | None = None,
	) -> Candidate:
		# Validate recruitment belongs to same tenant
		await validate_fk_same_tenant(
			session, Recruitment, data.recruitment_id, tenant_id, "recruitment_id"
		)
		
		candidate = Candidate(tenant_id=tenant_id, **data.model_dump())
		result = await repository.create_candidate(session, candidate)
		
		# Emit event
		await events.emit_candidate_created(tenant_id, result.id, actor_id)
		
		return result

	async def get_candidate(
		self, session: AsyncSession, tenant_id: UUID, candidate_id: UUID,
		actor_id: UUID | None = None,
	) -> Candidate:
		candidate = await repository.get_candidate(session, tenant_id, candidate_id)
		if not candidate:
			raise not_found("Candidate not found")
		return candidate

	async def update_candidate(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		candidate_id: UUID,
		data: CandidateUpdateRequest,
		actor_id: UUID | None = None,
	) -> Candidate:
		candidate = await self.get_candidate(session, tenant_id, candidate_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "status" and value is not None and value != candidate.status:
				self._validate_candidate_status(candidate.status, value)
			setattr(candidate, key, value)
		result = await repository.update_candidate(session, candidate)
		
		# Emit event
		await events.emit_candidate_stage_changed(tenant_id, candidate_id, candidate.status.value, new_status.value, actor_id)
		
		return result

	async def advance_candidate(
		self, session: AsyncSession, tenant_id: UUID, candidate_id: UUID, stage: CandidateStatus,
		actor_id: UUID | None = None,
	) -> Candidate:
		candidate = await self.get_candidate(session, tenant_id, candidate_id)
		if stage != candidate.status:
			self._validate_candidate_status(candidate.status, stage)
		candidate.status = stage
		return await repository.update_candidate(session, candidate)

	async def list_absences(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: AbsenceFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
		actor_id: UUID | None = None,
	) -> PaginatedResponse[Absence]:
		return await repository.list_absences(session, tenant_id, filters, page, page_size, sort)

	async def create_absence(
		self, session: AsyncSession, tenant_id: UUID, data: AbsenceCreateRequest,
		actor_id: UUID | None = None,
	) -> Absence:
		# Validate employee belongs to same tenant
		await validate_fk_same_tenant(
			session, Employee, data.employee_id, tenant_id, "employee_id"
		)
		
		absence = Absence(tenant_id=tenant_id, **data.model_dump())
		result = await repository.create_absence(session, absence)
		
		# Emit event
		await events.emit_absence_recorded(tenant_id, result.id, actor_id)
		
		return result

	async def list_time_entries(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: TimeEntryFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
		actor_id: UUID | None = None,
	) -> PaginatedResponse[TimeEntry]:
		return await repository.list_time_entries(session, tenant_id, filters, page, page_size, sort)

	async def create_time_entry(
		self, session: AsyncSession, tenant_id: UUID, data: TimeEntryCreateRequest,
		actor_id: UUID | None = None,
	) -> TimeEntry:
		# Validate employee belongs to same tenant
		await validate_fk_same_tenant(
			session, Employee, data.employee_id, tenant_id, "employee_id"
		)
		
		time_entry = TimeEntry(tenant_id=tenant_id, **data.model_dump())
		result = await repository.create_time_entry(session, time_entry)
		
		# Emit event
		await events.emit_time_entry_created(tenant_id, result.id, actor_id)
		
		return result

	async def approve_time_entry(
		self, session: AsyncSession, tenant_id: UUID, time_entry_id: UUID,
		actor_id: UUID | None = None,
	) -> TimeEntry:
		time_entry = await repository.get_time_entry(session, tenant_id, time_entry_id)
		if not time_entry:
			raise not_found("Time entry not found")
		self._validate_time_entry_status(time_entry.status, TimeEntryStatus.approved)
		time_entry.status = TimeEntryStatus.approved
		result = await repository.update_time_entry(session, time_entry)
		
		# Emit event
		await events.emit_time_entry_approved(tenant_id, time_entry_id, actor_id)
		
		return result

	async def list_leave_requests(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: LeaveRequestFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
		actor_id: UUID | None = None,
	) -> PaginatedResponse[LeaveRequest]:
		return await repository.list_leave_requests(
			session, tenant_id, filters, page, page_size, sort
		)

	async def create_leave_request(
		self, session: AsyncSession, tenant_id: UUID, data: LeaveRequestCreateRequest,
		actor_id: UUID | None = None,
	) -> LeaveRequest:
		# Validate employee belongs to same tenant
		await validate_fk_same_tenant(
			session, Employee, data.employee_id, tenant_id, "employee_id"
		)
		
		leave_request = LeaveRequest(tenant_id=tenant_id, **data.model_dump())
		result = await repository.create_leave_request(session, leave_request)
		
		# Emit event
		await events.emit_leave_requested(tenant_id, result.id, actor_id)
		
		return result

	async def approve_leave_request(
		self, session: AsyncSession, tenant_id: UUID, leave_request_id: UUID,
		actor_id: UUID | None = None,
	) -> LeaveRequest:
		leave_request = await repository.get_leave_request(session, tenant_id, leave_request_id)
		if not leave_request:
			raise not_found("Leave request not found")
		self._validate_leave_request_status(
			leave_request.status, LeaveRequestStatus.approved
		)
		leave_request.status = LeaveRequestStatus.approved
		result = await repository.update_leave_request(session, leave_request)
		
		# Emit event
		await events.emit_leave_approved(tenant_id, leave_request_id, actor_id)
		
		return result

	async def list_documents(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: DocumentFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
		actor_id: UUID | None = None,
	) -> PaginatedResponse[Document]:
		return await repository.list_documents(session, tenant_id, filters, page, page_size, sort)

	async def create_document(
		self, session: AsyncSession, tenant_id: UUID, data: DocumentCreateRequest,
		actor_id: UUID | None = None,
	) -> Document:
		# Validate employee belongs to same tenant
		await validate_fk_same_tenant(
			session, Employee, data.employee_id, tenant_id, "employee_id"
		)
		
		document = Document(tenant_id=tenant_id, **data.model_dump())
		result = await repository.create_document(session, document)
		
		# Emit event
		await events.emit_document_uploaded(tenant_id, result.id, data.employee_id, data.type.value, actor_id)
		
		return result

	async def list_contracts(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: ContractFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
		actor_id: UUID | None = None,
	) -> PaginatedResponse[Contract]:
		return await repository.list_contracts(session, tenant_id, filters, page, page_size, sort)

	async def create_contract(
		self, session: AsyncSession, tenant_id: UUID, data: ContractCreateRequest,
		actor_id: UUID | None = None,
	) -> Contract:
		# Validate FKs belong to same tenant
		await validate_fk_same_tenant(
			session, Employee, data.employee_id, tenant_id, "employee_id"
		)
		await validate_fk_same_tenant(
			session, Company, data.company_id, tenant_id, "company_id"
		)
		
		contract = Contract(tenant_id=tenant_id, **data.model_dump())
		result = await repository.create_contract(session, contract)
		
		# Emit event
		await events.emit_contract_created(tenant_id, result.id, actor_id)
		
		return result

	async def list_benefits(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: BenefitFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
		actor_id: UUID | None = None,
	) -> PaginatedResponse[Benefit]:
		return await repository.list_benefits(session, tenant_id, filters, page, page_size, sort)

	async def create_benefit(
		self, session: AsyncSession, tenant_id: UUID, data: BenefitCreateRequest,
		actor_id: UUID | None = None,
	) -> Benefit:
		benefit = Benefit(tenant_id=tenant_id, **data.model_dump())
		result = await repository.create_benefit(session, benefit)
		
		# Emit event
		await events.emit_benefit_created(tenant_id, result.id, actor_id)
		
		return result

	async def assign_benefit(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		benefit_id: UUID,
		data: BenefitAssignRequest,
		actor_id: UUID | None = None,
	) -> Benefit:
		benefit = await repository.get_benefit(session, tenant_id, benefit_id)
		if not benefit:
			raise not_found("Benefit not found")
		benefit.employee_id = data.employee_id
		result = await repository.update_benefit(session, benefit)
		
		# Emit event
		await events.emit_benefit_assigned(tenant_id, benefit_id, data.employee_id, actor_id)
		
		return result

	def _validate_employee_status(
		self, current_status: EmployeeStatus, new_status: EmployeeStatus,
		actor_id: UUID | None = None,
	) -> None:
		allowed = VALID_EMPLOYEE_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	def _validate_recruitment_status(
		self, current_status: RecruitmentStatus, new_status: RecruitmentStatus
	) -> None:
		allowed = VALID_RECRUITMENT_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	def _validate_candidate_status(
		self, current_status: CandidateStatus, new_status: CandidateStatus
	) -> None:
		allowed = VALID_CANDIDATE_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	def _validate_time_entry_status(
		self, current_status: TimeEntryStatus, new_status: TimeEntryStatus
	) -> None:
		allowed = VALID_TIME_ENTRY_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	def _validate_leave_request_status(
		self, current_status: LeaveRequestStatus, new_status: LeaveRequestStatus
	) -> None:
		allowed = VALID_LEAVE_REQUEST_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	def _validate_benefit_status(
		self, current_status: BenefitStatus, new_status: BenefitStatus
	) -> None:
		allowed = VALID_BENEFIT_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)


hr_service = HrService()
