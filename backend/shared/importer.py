"""Import engine and contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Enum as SqlEnum, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select

from shared import Base, IdMixin, TenantMixin, TimestampMixin


class ImportStatus(str, Enum):
	pending = "pending"
	validating = "validating"
	processing = "processing"
	completed = "completed"
	completed_with_errors = "completed_with_errors"
	failed = "failed"
	canceled = "canceled"


class ImportFileFormat(str, Enum):
	csv = "csv"
	xlsx = "xlsx"
	json = "json"


class ImportJob(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "shared_import_jobs"

	actor_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
	domain: Mapped[str] = mapped_column(String, nullable=False)
	entity: Mapped[str] = mapped_column(String, nullable=False)
	file_name: Mapped[str] = mapped_column(String, nullable=False)
	file_url: Mapped[str] = mapped_column(String, nullable=False)
	file_format: Mapped[ImportFileFormat] = mapped_column(
		SqlEnum(ImportFileFormat), nullable=False
	)
	column_mapping: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
	total_rows: Mapped[int] = mapped_column(Integer, default=0)
	processed_rows: Mapped[int] = mapped_column(Integer, default=0)
	success_count: Mapped[int] = mapped_column(Integer, default=0)
	error_count: Mapped[int] = mapped_column(Integer, default=0)
	duplicate_count: Mapped[int] = mapped_column(Integer, default=0)
	status: Mapped[ImportStatus] = mapped_column(
		SqlEnum(ImportStatus), default=ImportStatus.pending, nullable=False
	)
	errors: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
	options: Mapped[dict[str, Any]] = mapped_column(
		JSONB,
		default=lambda: {
			"skip_duplicates": True,
			"update_existing": False,
			"dry_run": False,
		},
	)
	started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ImportJobResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	tenant_id: UUID
	actor_id: UUID
	domain: str
	entity: str
	file_name: str
	file_url: str
	file_format: ImportFileFormat
	column_mapping: dict[str, Any]
	total_rows: int
	processed_rows: int
	success_count: int
	error_count: int
	duplicate_count: int
	status: ImportStatus
	errors: list[dict[str, Any]]
	options: dict[str, Any]
	started_at: datetime | None
	completed_at: datetime | None
	created_at: datetime
	updated_at: datetime


class ImportPreviewResponse(BaseModel):
	job_id: UUID
	file_columns: list[str]
	schema_fields: list[str]
	suggested_mapping: dict[str, str]
	sample_rows: list[dict[str, Any]]
	total_rows: int


class ImportErrorResponse(BaseModel):
	row: int
	field: str
	value: str | None
	error: str


class ImportMappingUpdateRequest(BaseModel):
	column_mapping: dict[str, str]


class ImportJobCreateRequest(BaseModel):
	domain: str
	entity: str


class ImportJobOptions(BaseModel):
	skip_duplicates: bool = True
	update_existing: bool = False
	dry_run: bool = False


class ImportRepository:
	async def create_job(self, session: AsyncSession, job: ImportJob) -> ImportJob:
		session.add(job)
		await session.flush()
		return job

	async def list_jobs(self, session: AsyncSession, tenant_id: UUID) -> list[ImportJob]:
		result = await session.execute(
			select(ImportJob).where(ImportJob.tenant_id == tenant_id).order_by(ImportJob.created_at)
		)
		return list(result.scalars().all())

	async def get_job(
		self, session: AsyncSession, tenant_id: UUID, job_id: UUID
	) -> ImportJob | None:
		result = await session.execute(
			select(ImportJob).where(
				ImportJob.tenant_id == tenant_id,
				ImportJob.id == job_id,
			)
		)
		return result.scalar_one_or_none()

	async def update_job(self, session: AsyncSession, job: ImportJob) -> ImportJob:
		session.add(job)
		await session.flush()
		return job


class ImportService:
	def __init__(self, repository: ImportRepository) -> None:
		self.repository = repository

	async def list_jobs(self, session: AsyncSession, tenant_id: UUID) -> list[ImportJob]:
		return await self.repository.list_jobs(session, tenant_id)

	async def create_job(
		self,
		session: AsyncSession,
		*,
		tenant_id: UUID,
		actor_id: UUID,
		domain: str,
		entity: str,
		file_name: str,
		file_url: str,
		file_format: ImportFileFormat,
	) -> ImportJob:
		job = ImportJob(
			tenant_id=tenant_id,
			actor_id=actor_id,
			domain=domain,
			entity=entity,
			file_name=file_name,
			file_url=file_url,
			file_format=file_format,
		)
		return await self.repository.create_job(session, job)

	async def get_job(
		self, session: AsyncSession, tenant_id: UUID, job_id: UUID
	) -> ImportJob:
		job = await self.repository.get_job(session, tenant_id, job_id)
		if not job:
			raise ValueError("Import job not found")
		return job

	async def update_mapping(
		self, session: AsyncSession, job: ImportJob, mapping: dict[str, str]
	) -> ImportJob:
		job.column_mapping = mapping
		return await self.repository.update_job(session, job)

	async def start_validation(self, session: AsyncSession, job: ImportJob) -> ImportJob:
		job.status = ImportStatus.validating
		job.started_at = datetime.now(timezone.utc)
		return await self.repository.update_job(session, job)

	async def start_processing(self, session: AsyncSession, job: ImportJob) -> ImportJob:
		job.status = ImportStatus.processing
		job.started_at = datetime.now(timezone.utc)
		return await self.repository.update_job(session, job)

	async def complete_job(
		self,
		session: AsyncSession,
		job: ImportJob,
		*,
		success_count: int,
		error_count: int,
		duplicate_count: int,
		errors: list[dict[str, Any]] | None = None,
	) -> ImportJob:
		job.success_count = success_count
		job.error_count = error_count
		job.duplicate_count = duplicate_count
		job.errors = errors or []
		job.status = (
			ImportStatus.completed_with_errors if error_count else ImportStatus.completed
		)
		job.completed_at = datetime.now(timezone.utc)
		return await self.repository.update_job(session, job)

	async def cancel_job(self, session: AsyncSession, job: ImportJob) -> ImportJob:
		job.status = ImportStatus.canceled
		job.completed_at = datetime.now(timezone.utc)
		return await self.repository.update_job(session, job)


import_repository = ImportRepository()
import_service = ImportService(import_repository)
