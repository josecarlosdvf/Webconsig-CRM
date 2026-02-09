"""Import API endpoints."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, get_current_user, get_db, get_tenant_id
from shared.audit import AuditAction, log_action
from shared.importer import (
	ImportErrorResponse,
	ImportFileFormat,
	ImportJobCreateRequest,
	ImportJobResponse,
	ImportMappingUpdateRequest,
	ImportPreviewResponse,
	import_service,
)
from shared.pagination import PaginatedResponse, PageParams

router = APIRouter(prefix="/api/v1/import", tags=["import"])


def _request_context(request: Request) -> tuple[str, str]:
	ip_address = request.client.host if request.client else "unknown"
	user_agent = request.headers.get("user-agent", "unknown")
	return ip_address, user_agent


def _format_from_filename(filename: str) -> ImportFileFormat:
	suffix = Path(filename).suffix.lower().lstrip(".")
	try:
		return ImportFileFormat(suffix)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail="Unsupported file format") from exc


@router.get("/templates/{domain}/{entity}")
async def download_template(domain: str, entity: str) -> Response:
	content = "".encode("utf-8")
	return Response(content=content, media_type="text/csv")


@router.get("/jobs", response_model=PaginatedResponse[ImportJobResponse])
async def list_jobs(
	params: PageParams = Depends(),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	items = await import_service.list_jobs(db, tenant_id)
	total = len(items)
	page_items = items[(params.page - 1) * params.page_size : params.page * params.page_size]
	return PaginatedResponse(
		items=page_items,
		page=params.page,
		page_size=params.page_size,
		total=total,
		has_next=total > params.page * params.page_size,
	)


@router.post("/jobs", response_model=ImportJobResponse, status_code=201)
async def create_job(
	request: Request,
	data: ImportJobCreateRequest = Depends(),
	file: UploadFile = File(...),
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	file_format = _format_from_filename(file.filename)
	job = await import_service.create_job(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		domain=data.domain,
		entity=data.entity,
		file_name=file.filename,
		file_url=f"storage://{file.filename}",
		file_format=file_format,
	)
	ip_address, user_agent = _request_context(request)
	await log_action(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		actor_email=current_user.email,
		action=AuditAction.import_,
		domain="import",
		entity=data.entity,
		entity_id=job.id,
		changes={"imported": 0, "errors": 0, "duplicates": 0},
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=str(request.url.path),
		occurred_at=datetime.now(timezone.utc),
		metadata={"job_id": str(job.id)},
	)
	await db.commit()
	await db.refresh(job)
	return job


@router.get("/jobs/{job_id}", response_model=ImportJobResponse)
async def get_job(
	job_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	return await import_service.get_job(db, tenant_id, job_id)


@router.post("/jobs/{job_id}/preview", response_model=ImportPreviewResponse)
async def preview_job(
	job_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	job = await import_service.get_job(db, tenant_id, job_id)
	return ImportPreviewResponse(
		job_id=job.id,
		file_columns=[],
		schema_fields=[],
		suggested_mapping={},
		sample_rows=[],
		total_rows=job.total_rows,
	)


@router.patch("/jobs/{job_id}/mapping", response_model=ImportJobResponse)
async def update_mapping(
	job_id: UUID,
	data: ImportMappingUpdateRequest,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	job = await import_service.get_job(db, tenant_id, job_id)
	job = await import_service.update_mapping(db, job, data.column_mapping)
	await db.commit()
	await db.refresh(job)
	return job


@router.post("/jobs/{job_id}/validate", response_model=ImportJobResponse)
async def validate_job(
	job_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	job = await import_service.get_job(db, tenant_id, job_id)
	job = await import_service.start_validation(db, job)
	job = await import_service.complete_job(
		db,
		job,
		success_count=0,
		error_count=0,
		duplicate_count=0,
		errors=[],
	)
	await db.commit()
	await db.refresh(job)
	return job


@router.post("/jobs/{job_id}/execute", response_model=ImportJobResponse)
async def execute_job(
	job_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	job = await import_service.get_job(db, tenant_id, job_id)
	job = await import_service.start_processing(db, job)
	job = await import_service.complete_job(
		db,
		job,
		success_count=0,
		error_count=0,
		duplicate_count=0,
		errors=[],
	)
	await db.commit()
	await db.refresh(job)
	return job


@router.get("/jobs/{job_id}/errors", response_model=list[ImportErrorResponse])
async def list_errors(
	job_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	job = await import_service.get_job(db, tenant_id, job_id)
	return [ImportErrorResponse(**error) for error in job.errors]


@router.post("/jobs/{job_id}/cancel", response_model=ImportJobResponse)
async def cancel_job(
	job_id: UUID,
	db: AsyncSession = Depends(get_db),
	tenant_id: UUID = Depends(get_tenant_id),
	current_user: CurrentUser = Depends(get_current_user),
):
	job = await import_service.get_job(db, tenant_id, job_id)
	job = await import_service.cancel_job(db, job)
	await db.commit()
	await db.refresh(job)
	return job
