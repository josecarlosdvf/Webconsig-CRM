"""HR schemas/contracts."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain.hr.models import (
	AbsenceStatus,
	BenefitStatus,
	BenefitType,
	CandidateStatus,
	ContractStatus,
	ContractType,
	DocumentType,
	EmployeeStatus,
	LeaveRequestStatus,
	RecruitmentStatus,
	TimeEntryStatus,
	TimeEntryType,
)


class BaseSchema(BaseModel):
	model_config = ConfigDict(from_attributes=True)


class EmployeeCreateRequest(BaseSchema):
	name: str
	email: str
	phone: str
	document: str
	department: str
	role: str
	company_id: UUID
	hired_at: date


class EmployeeUpdateRequest(BaseSchema):
	name: Optional[str] = None
	email: Optional[str] = None
	phone: Optional[str] = None
	document: Optional[str] = None
	department: Optional[str] = None
	role: Optional[str] = None
	company_id: Optional[UUID] = None
	hired_at: Optional[date] = None
	terminated_at: Optional[date] = None
	termination_reason: Optional[str] = None
	status: Optional[EmployeeStatus] = None


class EmployeeResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	name: str
	email: str
	phone: str
	document: str
	department: str
	role: str
	company_id: UUID
	hired_at: date
	terminated_at: date | None
	termination_reason: str | None
	status: EmployeeStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class EmployeeFilters(BaseModel):
	"""Filter parameters for listing employees."""
	name: Optional[str] = Field(None, description="Exact name match")
	status: Optional[EmployeeStatus] = Field(None, description="Employee status")
	department: Optional[str] = Field(None, description="Department")
	role: Optional[str] = Field(None, description="Role")
	hired_from: Optional[date] = Field(None, description="Hired after date (inclusive)")
	hired_to: Optional[date] = Field(None, description="Hired before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across name, email, document")


class EmployeeTerminateRequest(BaseSchema):
	reason: str


class RecruitmentCreateRequest(BaseSchema):
	position: str
	department: str
	description: str
	vacancies: int = 1


class RecruitmentUpdateRequest(BaseSchema):
	position: Optional[str] = None
	department: Optional[str] = None
	description: Optional[str] = None
	vacancies: Optional[int] = None
	status: Optional[RecruitmentStatus] = None


class RecruitmentResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	position: str
	department: str
	description: str
	vacancies: int
	status: RecruitmentStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class RecruitmentFilters(BaseModel):
	"""Filter parameters for listing recruitments."""
	status: Optional[RecruitmentStatus] = Field(None, description="Recruitment status")
	position: Optional[str] = Field(None, description="Position")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across position and department")


class CandidateCreateRequest(BaseSchema):
	recruitment_id: UUID
	name: str
	email: str
	phone: str
	resume_url: str | None = None


class CandidateUpdateRequest(BaseSchema):
	recruitment_id: Optional[UUID] = None
	name: Optional[str] = None
	email: Optional[str] = None
	phone: Optional[str] = None
	resume_url: Optional[str] = None
	status: Optional[CandidateStatus] = None


class CandidateStageRequest(BaseSchema):
	stage: CandidateStatus


class CandidateResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	recruitment_id: UUID
	name: str
	email: str
	phone: str
	resume_url: str | None
	status: CandidateStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class CandidateFilters(BaseModel):
	"""Filter parameters for listing candidates."""
	status: Optional[CandidateStatus] = Field(None, description="Candidate status")
	recruitment_id: Optional[UUID] = Field(None, description="Recruitment ID")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across name, email, phone")


class AbsenceCreateRequest(BaseSchema):
	employee_id: UUID
	date: date
	reason: str | None = None


class AbsenceResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	employee_id: UUID
	date: date
	reason: str | None
	status: AbsenceStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class AbsenceFilters(BaseModel):
	"""Filter parameters for listing absences."""
	employee_id: Optional[UUID] = Field(None, description="Employee ID")
	status: Optional[AbsenceStatus] = Field(None, description="Absence status")
	date_from: Optional[date] = Field(None, description="Date from (inclusive)")
	date_to: Optional[date] = Field(None, description="Date to (inclusive)")
	q: Optional[str] = Field(None, description="Search across reason")


class TimeEntryCreateRequest(BaseSchema):
	employee_id: UUID
	date: date
	type: TimeEntryType
	minutes: int
	description: str | None = None


class TimeEntryResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	employee_id: UUID
	date: date
	type: TimeEntryType
	minutes: int
	description: str | None
	status: TimeEntryStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class TimeEntryFilters(BaseModel):
	"""Filter parameters for listing time entries."""
	employee_id: Optional[UUID] = Field(None, description="Employee ID")
	type: Optional[TimeEntryType] = Field(None, description="Entry type")
	status: Optional[TimeEntryStatus] = Field(None, description="Entry status")
	date_from: Optional[date] = Field(None, description="Date from (inclusive)")
	date_to: Optional[date] = Field(None, description="Date to (inclusive)")
	q: Optional[str] = Field(None, description="Search across description")


class TimeEntryApproveRequest(BaseSchema):
	approved: bool = True


class LeaveRequestCreateRequest(BaseSchema):
	employee_id: UUID
	start_date: date
	end_date: date
	type: str = "vacation"
	reason: str | None = None


class LeaveRequestResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	employee_id: UUID
	start_date: date
	end_date: date
	type: str
	reason: str | None
	status: LeaveRequestStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class LeaveRequestFilters(BaseModel):
	"""Filter parameters for listing leave requests."""
	employee_id: Optional[UUID] = Field(None, description="Employee ID")
	status: Optional[LeaveRequestStatus] = Field(None, description="Request status")
	date_from: Optional[date] = Field(None, description="Start date from (inclusive)")
	date_to: Optional[date] = Field(None, description="End date to (inclusive)")
	q: Optional[str] = Field(None, description="Search across reason")


class DocumentCreateRequest(BaseSchema):
	employee_id: UUID
	type: DocumentType
	description: str
	file_url: str


class DocumentResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	employee_id: UUID
	type: DocumentType
	description: str
	file_url: str
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class DocumentFilters(BaseModel):
	"""Filter parameters for listing documents."""
	employee_id: Optional[UUID] = Field(None, description="Employee ID")
	type: Optional[DocumentType] = Field(None, description="Document type")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across description")


class ContractCreateRequest(BaseSchema):
	employee_id: UUID
	company_id: UUID
	type: ContractType
	start_date: date
	end_date: date | None = None
	salary: float
	currency: str = "BRL"


class ContractResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	employee_id: UUID
	company_id: UUID
	type: ContractType
	start_date: date
	end_date: date | None
	salary: float
	currency: str
	status: ContractStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class ContractFilters(BaseModel):
	"""Filter parameters for listing contracts."""
	employee_id: Optional[UUID] = Field(None, description="Employee ID")
	type: Optional[ContractType] = Field(None, description="Contract type")
	status: Optional[ContractStatus] = Field(None, description="Contract status")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across currency")


class BenefitCreateRequest(BaseSchema):
	type: BenefitType
	description: str
	value: float
	currency: str = "BRL"


class BenefitResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	type: BenefitType
	description: str
	value: float
	currency: str
	employee_id: UUID | None
	status: BenefitStatus
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class BenefitFilters(BaseModel):
	"""Filter parameters for listing benefits."""
	employee_id: Optional[UUID] = Field(None, description="Employee ID")
	type: Optional[BenefitType] = Field(None, description="Benefit type")
	status: Optional[BenefitStatus] = Field(None, description="Benefit status")
	created_from: Optional[date] = Field(None, description="Created after date (inclusive)")
	created_to: Optional[date] = Field(None, description="Created before date (inclusive)")
	q: Optional[str] = Field(None, description="Search across description")


class BenefitAssignRequest(BaseSchema):
	employee_id: UUID
