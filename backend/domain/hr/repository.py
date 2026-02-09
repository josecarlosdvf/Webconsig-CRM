"""HR data access layer."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.hr.models import (
	Absence,
	Benefit,
	Candidate,
	Contract,
	Document,
	Employee,
	LeaveRequest,
	Recruitment,
	TimeEntry,
)
from domain.hr.schemas import (
	AbsenceFilters,
	BenefitFilters,
	CandidateFilters,
	ContractFilters,
	DocumentFilters,
	EmployeeFilters,
	LeaveRequestFilters,
	RecruitmentFilters,
	TimeEntryFilters,
)
from shared import utcnow
from shared.filters import (
	apply_date_range_filter,
	apply_enum_filter,
	apply_sorting,
	apply_text_filter,
	apply_text_search,
)
from shared.pagination import (
	PaginatedResponse,
	build_paginated_response,
	get_total_count,
	paginate_query,
)


async def create_employee(session: AsyncSession, employee: Employee) -> Employee:
	session.add(employee)
	await session.flush()
	return employee


async def list_employees(
	session: AsyncSession,
	tenant_id: UUID,
	filters: EmployeeFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Employee]:
	query = select(Employee).where(Employee.tenant_id == tenant_id, Employee.deleted_at.is_(None))

	query = apply_text_filter(query, Employee.name, filters.name)
	query = apply_enum_filter(query, Employee.status, filters.status)
	query = apply_text_filter(query, Employee.department, filters.department)
	query = apply_text_filter(query, Employee.role, filters.role)
	query = apply_date_range_filter(query, Employee.hired_at, filters.hired_from, filters.hired_to)
	query = apply_text_search(query, [Employee.name, Employee.email, Employee.document], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"name": Employee.name,
		"status": Employee.status,
		"hired_at": Employee.hired_at,
		"created_at": Employee.created_at,
		"updated_at": Employee.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_employee(
	session: AsyncSession, tenant_id: UUID, employee_id: UUID
) -> Employee | None:
	result = await session.execute(
		select(Employee).where(
			Employee.tenant_id == tenant_id,
			Employee.id == employee_id,
			Employee.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_employee(session: AsyncSession, employee: Employee) -> Employee:
	session.add(employee)
	await session.flush()
	return employee


async def create_recruitment(session: AsyncSession, recruitment: Recruitment) -> Recruitment:
	session.add(recruitment)
	await session.flush()
	return recruitment


async def list_recruitments(
	session: AsyncSession,
	tenant_id: UUID,
	filters: RecruitmentFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Recruitment]:
	query = select(Recruitment).where(
		Recruitment.tenant_id == tenant_id, Recruitment.deleted_at.is_(None)
	)

	query = apply_enum_filter(query, Recruitment.status, filters.status)
	query = apply_text_filter(query, Recruitment.position, filters.position)
	query = apply_date_range_filter(
		query, Recruitment.created_at, filters.created_from, filters.created_to
	)
	query = apply_text_search(query, [Recruitment.position, Recruitment.department], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"position": Recruitment.position,
		"status": Recruitment.status,
		"created_at": Recruitment.created_at,
		"updated_at": Recruitment.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_recruitment(
	session: AsyncSession, tenant_id: UUID, recruitment_id: UUID
) -> Recruitment | None:
	result = await session.execute(
		select(Recruitment).where(
			Recruitment.tenant_id == tenant_id,
			Recruitment.id == recruitment_id,
			Recruitment.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_recruitment(session: AsyncSession, recruitment: Recruitment) -> Recruitment:
	session.add(recruitment)
	await session.flush()
	return recruitment


async def create_candidate(session: AsyncSession, candidate: Candidate) -> Candidate:
	session.add(candidate)
	await session.flush()
	return candidate


async def list_candidates(
	session: AsyncSession,
	tenant_id: UUID,
	filters: CandidateFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Candidate]:
	query = select(Candidate).where(Candidate.tenant_id == tenant_id, Candidate.deleted_at.is_(None))

	query = apply_enum_filter(query, Candidate.status, filters.status)
	query = apply_enum_filter(query, Candidate.recruitment_id, filters.recruitment_id)
	query = apply_date_range_filter(
		query, Candidate.created_at, filters.created_from, filters.created_to
	)
	query = apply_text_search(query, [Candidate.name, Candidate.email, Candidate.phone], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"name": Candidate.name,
		"status": Candidate.status,
		"created_at": Candidate.created_at,
		"updated_at": Candidate.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_candidate(
	session: AsyncSession, tenant_id: UUID, candidate_id: UUID
) -> Candidate | None:
	result = await session.execute(
		select(Candidate).where(
			Candidate.tenant_id == tenant_id,
			Candidate.id == candidate_id,
			Candidate.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_candidate(session: AsyncSession, candidate: Candidate) -> Candidate:
	session.add(candidate)
	await session.flush()
	return candidate


async def create_absence(session: AsyncSession, absence: Absence) -> Absence:
	session.add(absence)
	await session.flush()
	return absence


async def list_absences(
	session: AsyncSession,
	tenant_id: UUID,
	filters: AbsenceFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Absence]:
	query = select(Absence).where(Absence.tenant_id == tenant_id, Absence.deleted_at.is_(None))

	query = apply_enum_filter(query, Absence.employee_id, filters.employee_id)
	query = apply_enum_filter(query, Absence.status, filters.status)
	query = apply_date_range_filter(query, Absence.date, filters.date_from, filters.date_to)
	query = apply_text_search(query, [Absence.reason], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"date": Absence.date,
		"status": Absence.status,
		"created_at": Absence.created_at,
		"updated_at": Absence.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def create_time_entry(session: AsyncSession, time_entry: TimeEntry) -> TimeEntry:
	session.add(time_entry)
	await session.flush()
	return time_entry


async def list_time_entries(
	session: AsyncSession,
	tenant_id: UUID,
	filters: TimeEntryFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[TimeEntry]:
	query = select(TimeEntry).where(TimeEntry.tenant_id == tenant_id, TimeEntry.deleted_at.is_(None))

	query = apply_enum_filter(query, TimeEntry.employee_id, filters.employee_id)
	query = apply_enum_filter(query, TimeEntry.type, filters.type)
	query = apply_enum_filter(query, TimeEntry.status, filters.status)
	query = apply_date_range_filter(query, TimeEntry.date, filters.date_from, filters.date_to)
	query = apply_text_search(query, [TimeEntry.description], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"date": TimeEntry.date,
		"type": TimeEntry.type,
		"status": TimeEntry.status,
		"created_at": TimeEntry.created_at,
		"updated_at": TimeEntry.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_time_entry(
	session: AsyncSession, tenant_id: UUID, time_entry_id: UUID
) -> TimeEntry | None:
	result = await session.execute(
		select(TimeEntry).where(
			TimeEntry.tenant_id == tenant_id,
			TimeEntry.id == time_entry_id,
			TimeEntry.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_time_entry(session: AsyncSession, time_entry: TimeEntry) -> TimeEntry:
	session.add(time_entry)
	await session.flush()
	return time_entry


async def create_leave_request(session: AsyncSession, leave_request: LeaveRequest) -> LeaveRequest:
	session.add(leave_request)
	await session.flush()
	return leave_request


async def list_leave_requests(
	session: AsyncSession,
	tenant_id: UUID,
	filters: LeaveRequestFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[LeaveRequest]:
	query = select(LeaveRequest).where(
		LeaveRequest.tenant_id == tenant_id, LeaveRequest.deleted_at.is_(None)
	)

	query = apply_enum_filter(query, LeaveRequest.employee_id, filters.employee_id)
	query = apply_enum_filter(query, LeaveRequest.status, filters.status)
	query = apply_date_range_filter(
		query, LeaveRequest.start_date, filters.date_from, filters.date_to
	)
	query = apply_text_search(query, [LeaveRequest.reason], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"start_date": LeaveRequest.start_date,
		"status": LeaveRequest.status,
		"created_at": LeaveRequest.created_at,
		"updated_at": LeaveRequest.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_leave_request(
	session: AsyncSession, tenant_id: UUID, leave_request_id: UUID
) -> LeaveRequest | None:
	result = await session.execute(
		select(LeaveRequest).where(
			LeaveRequest.tenant_id == tenant_id,
			LeaveRequest.id == leave_request_id,
			LeaveRequest.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_leave_request(session: AsyncSession, leave_request: LeaveRequest) -> LeaveRequest:
	session.add(leave_request)
	await session.flush()
	return leave_request


async def create_document(session: AsyncSession, document: Document) -> Document:
	session.add(document)
	await session.flush()
	return document


async def list_documents(
	session: AsyncSession,
	tenant_id: UUID,
	filters: DocumentFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Document]:
	query = select(Document).where(Document.tenant_id == tenant_id, Document.deleted_at.is_(None))

	query = apply_enum_filter(query, Document.employee_id, filters.employee_id)
	query = apply_enum_filter(query, Document.type, filters.type)
	query = apply_date_range_filter(
		query, Document.created_at, filters.created_from, filters.created_to
	)
	query = apply_text_search(query, [Document.description], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"type": Document.type,
		"created_at": Document.created_at,
		"updated_at": Document.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def create_contract(session: AsyncSession, contract: Contract) -> Contract:
	session.add(contract)
	await session.flush()
	return contract


async def list_contracts(
	session: AsyncSession,
	tenant_id: UUID,
	filters: ContractFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Contract]:
	query = select(Contract).where(Contract.tenant_id == tenant_id, Contract.deleted_at.is_(None))

	query = apply_enum_filter(query, Contract.employee_id, filters.employee_id)
	query = apply_enum_filter(query, Contract.type, filters.type)
	query = apply_enum_filter(query, Contract.status, filters.status)
	query = apply_date_range_filter(
		query, Contract.created_at, filters.created_from, filters.created_to
	)
	query = apply_text_search(query, [Contract.currency], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"type": Contract.type,
		"status": Contract.status,
		"created_at": Contract.created_at,
		"updated_at": Contract.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def create_benefit(session: AsyncSession, benefit: Benefit) -> Benefit:
	session.add(benefit)
	await session.flush()
	return benefit


async def list_benefits(
	session: AsyncSession,
	tenant_id: UUID,
	filters: BenefitFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Benefit]:
	query = select(Benefit).where(Benefit.tenant_id == tenant_id, Benefit.deleted_at.is_(None))

	query = apply_enum_filter(query, Benefit.employee_id, filters.employee_id)
	query = apply_enum_filter(query, Benefit.type, filters.type)
	query = apply_enum_filter(query, Benefit.status, filters.status)
	query = apply_date_range_filter(
		query, Benefit.created_at, filters.created_from, filters.created_to
	)
	query = apply_text_search(query, [Benefit.description], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"type": Benefit.type,
		"status": Benefit.status,
		"created_at": Benefit.created_at,
		"updated_at": Benefit.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_benefit(
	session: AsyncSession, tenant_id: UUID, benefit_id: UUID
) -> Benefit | None:
	result = await session.execute(
		select(Benefit).where(
			Benefit.tenant_id == tenant_id,
			Benefit.id == benefit_id,
			Benefit.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_benefit(session: AsyncSession, benefit: Benefit) -> Benefit:
	session.add(benefit)
	await session.flush()
	return benefit


async def soft_delete_employee(session: AsyncSession, employee: Employee) -> Employee:
	employee.deleted_at = utcnow()
	session.add(employee)
	await session.flush()
	return employee
