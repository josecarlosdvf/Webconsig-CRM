"""HR ORM models."""

from enum import Enum

from sqlalchemy import Date, Enum as SqlEnum, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared import Base, IdMixin, TenantMixin, TimestampMixin


class EmployeeStatus(str, Enum):
	active = "active"
	inactive = "inactive"
	terminated = "terminated"


class RecruitmentStatus(str, Enum):
	open = "open"
	on_hold = "on_hold"
	closed = "closed"


class CandidateStatus(str, Enum):
	applied = "applied"
	screening = "screening"
	interview = "interview"
	offer = "offer"
	hired = "hired"
	rejected = "rejected"


class AbsenceStatus(str, Enum):
	pending = "pending"
	justified = "justified"
	unexcused = "unexcused"


class TimeEntryType(str, Enum):
	late = "late"
	overtime = "overtime"
	regular = "regular"


class TimeEntryStatus(str, Enum):
	pending = "pending"
	approved = "approved"
	rejected = "rejected"


class LeaveRequestStatus(str, Enum):
	requested = "requested"
	approved = "approved"
	rejected = "rejected"
	canceled = "canceled"


class DocumentType(str, Enum):
	medical_certificate = "medical_certificate"
	proof = "proof"
	contract = "contract"
	other = "other"


class ContractType(str, Enum):
	clt = "clt"
	pj = "pj"
	intern = "intern"
	temp = "temp"


class ContractStatus(str, Enum):
	active = "active"
	expired = "expired"
	terminated = "terminated"


class BenefitType(str, Enum):
	vr = "vr"
	va = "va"
	vt = "vt"


class BenefitStatus(str, Enum):
	active = "active"
	suspended = "suspended"
	canceled = "canceled"


class Employee(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "hr_employees"

	name: Mapped[str] = mapped_column(String, nullable=False)
	email: Mapped[str] = mapped_column(String, nullable=False)
	phone: Mapped[str] = mapped_column(String, nullable=False)
	document: Mapped[str] = mapped_column(String, nullable=False)
	department: Mapped[str] = mapped_column(String, nullable=False)
	role: Mapped[str] = mapped_column(String, nullable=False)
	company_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	hired_at: Mapped[Date] = mapped_column(Date, nullable=False)
	terminated_at: Mapped[Date | None] = mapped_column(Date, nullable=True)
	termination_reason: Mapped[str | None] = mapped_column(String, nullable=True)
	status: Mapped[EmployeeStatus] = mapped_column(
		SqlEnum(EmployeeStatus), default=EmployeeStatus.active, nullable=False
	)


class Recruitment(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "hr_recruitments"

	position: Mapped[str] = mapped_column(String, nullable=False)
	department: Mapped[str] = mapped_column(String, nullable=False)
	description: Mapped[str] = mapped_column(String, nullable=False)
	vacancies: Mapped[int] = mapped_column(nullable=False, default=1)
	status: Mapped[RecruitmentStatus] = mapped_column(
		SqlEnum(RecruitmentStatus), default=RecruitmentStatus.open, nullable=False
	)


class Candidate(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "hr_candidates"

	recruitment_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	name: Mapped[str] = mapped_column(String, nullable=False)
	email: Mapped[str] = mapped_column(String, nullable=False)
	phone: Mapped[str] = mapped_column(String, nullable=False)
	resume_url: Mapped[str | None] = mapped_column(String, nullable=True)
	status: Mapped[CandidateStatus] = mapped_column(
		SqlEnum(CandidateStatus), default=CandidateStatus.applied, nullable=False
	)


class Absence(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "hr_absences"

	employee_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	date: Mapped[Date] = mapped_column(Date, nullable=False)
	reason: Mapped[str | None] = mapped_column(String, nullable=True)
	status: Mapped[AbsenceStatus] = mapped_column(
		SqlEnum(AbsenceStatus), default=AbsenceStatus.pending, nullable=False
	)


class TimeEntry(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "hr_time_entries"

	employee_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	date: Mapped[Date] = mapped_column(Date, nullable=False)
	type: Mapped[TimeEntryType] = mapped_column(SqlEnum(TimeEntryType), nullable=False)
	minutes: Mapped[int] = mapped_column(nullable=False, default=0)
	description: Mapped[str | None] = mapped_column(String, nullable=True)
	status: Mapped[TimeEntryStatus] = mapped_column(
		SqlEnum(TimeEntryStatus), default=TimeEntryStatus.pending, nullable=False
	)


class LeaveRequest(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "hr_leave_requests"

	employee_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	start_date: Mapped[Date] = mapped_column(Date, nullable=False)
	end_date: Mapped[Date] = mapped_column(Date, nullable=False)
	type: Mapped[str] = mapped_column(String, nullable=False, default="vacation")
	reason: Mapped[str | None] = mapped_column(String, nullable=True)
	status: Mapped[LeaveRequestStatus] = mapped_column(
		SqlEnum(LeaveRequestStatus), default=LeaveRequestStatus.requested, nullable=False
	)


class Document(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "hr_documents"

	employee_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	type: Mapped[DocumentType] = mapped_column(SqlEnum(DocumentType), nullable=False)
	description: Mapped[str] = mapped_column(String, nullable=False)
	file_url: Mapped[str] = mapped_column(String, nullable=False)


class Contract(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "hr_contracts"

	employee_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	company_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	type: Mapped[ContractType] = mapped_column(SqlEnum(ContractType), nullable=False)
	start_date: Mapped[Date] = mapped_column(Date, nullable=False)
	end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
	salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
	currency: Mapped[str] = mapped_column(String, nullable=False, default="BRL")
	status: Mapped[ContractStatus] = mapped_column(
		SqlEnum(ContractStatus), default=ContractStatus.active, nullable=False
	)


class Benefit(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "hr_benefits"

	type: Mapped[BenefitType] = mapped_column(SqlEnum(BenefitType), nullable=False)
	description: Mapped[str] = mapped_column(String, nullable=False)
	value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
	currency: Mapped[str] = mapped_column(String, nullable=False, default="BRL")
	employee_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
	status: Mapped[BenefitStatus] = mapped_column(
		SqlEnum(BenefitStatus), default=BenefitStatus.active, nullable=False
	)
