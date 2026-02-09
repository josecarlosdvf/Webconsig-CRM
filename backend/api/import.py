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
	"""Download CSV template with headers for the specified domain/entity."""
	from shared.import_processor import get_import_schema
	
	# Get schema for the entity
	schema = get_import_schema(domain, entity)
	
	if not schema:
		raise HTTPException(status_code=404, detail=f"No schema found for {domain}.{entity}")
	
	# Extract field names from schema
	fields = list(schema.model_fields.keys())
	
	# Generate CSV header
	import csv
	import io
	
	output = io.StringIO()
	writer = csv.writer(output)
	writer.writerow(fields)
	
	content = output.getvalue().encode("utf-8")
	
	return Response(
		content=content,
		media_type="text/csv",
		headers={
			"Content-Disposition": f'attachment; filename="{domain}_{entity}_template.csv"'
		}
	)


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
	"""Create a new import job and upload file to storage."""
	from shared.storage import get_storage, generate_storage_key
	
	# Validate file format
	file_format = _format_from_filename(file.filename)
	
	# Upload file to storage
	storage = get_storage()
	storage_key = generate_storage_key(tenant_id, "import", file.filename)
	
	# Read and upload file
	file_content = await file.read()
	import io
	file_url = await storage.upload(
		file=io.BytesIO(file_content),
		key=storage_key,
		content_type=file.content_type,
	)
	
	# Create import job
	job = await import_service.create_job(
		db,
		tenant_id=tenant_id,
		actor_id=current_user.id,
		domain=data.domain,
		entity=data.entity,
		file_name=file.filename,
		file_url=file_url,
		file_format=file_format,
	)
	
	# Log action
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
		metadata={"job_id": str(job.id), "file_size": len(file_content)},
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
	"""Preview import job with file columns, schema fields, and suggested mapping."""
	from shared.storage import get_storage
	from shared.import_engine import create_parser, suggest_column_mapping
	from shared.import_processor import get_import_schema
	
	job = await import_service.get_job(db, tenant_id, job_id)
	
	# Download file from storage
	storage = get_storage()
	storage_key = job.file_url.split("/")[-1] if "/" in job.file_url else job.file_url
	
	# For local storage, extract key properly
	if "storage" in job.file_url:
		parts = job.file_url.split("/")
		storage_key = "/".join(parts[3:]) if len(parts) > 3 else storage_key
	
	try:
		file_content = await storage.download(storage_key)
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="Import file not found in storage")
	
	# Parse file
	parser = create_parser(job.file_format.value)
	import io
	file_obj = io.BytesIO(file_content)
	columns, rows = parser.parse(file_obj)
	
	# Get schema fields
	schema = get_import_schema(job.domain, job.entity)
	schema_fields = list(schema.model_fields.keys()) if schema else []
	
	# Suggest column mapping
	suggested_mapping = suggest_column_mapping(columns, schema_fields)
	
	# Get sample rows (first 5)
	sample_rows = rows[:5]
	
	# Update job total_rows
	job.total_rows = len(rows)
	await db.commit()
	
	return ImportPreviewResponse(
		job_id=job.id,
		file_columns=columns,
		schema_fields=schema_fields,
		suggested_mapping=suggested_mapping,
		sample_rows=sample_rows,
		total_rows=len(rows),
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
	"""
	Execute import job with batch processing.
	
	Note: This is a placeholder implementation. Full implementation requires:
	1. Repository mapping per domain/entity
	2. Background task processing (FastAPI BackgroundTasks or Celery)
	3. WebSocket notifications for progress updates
	
	For now, this validates the flow but doesn't actually insert data.
	"""
	from shared.import_processor import import_processor
	
	job = await import_service.get_job(db, tenant_id, job_id)
	
	# Start processing
	job = await import_service.start_processing(db, job)
	await db.commit()
	
	# TODO: In production, this should be a background task
	# For now, we'll use dry_run mode to validate without inserting
	job.options["dry_run"] = True
	
	try:
		# Process with mock repository (placeholder)
		# In production, this would map domain.entity to the appropriate repository
		class MockRepository:
			async def create(self, session, tenant_id, data):
				pass  # No-op for now
		
		repository = MockRepository()
		job = await import_processor.process_job(db, job, repository)
		
	except Exception as e:
		job.status = "failed"
		job.errors = [{"error": str(e)}]
		await db.commit()
		raise HTTPException(status_code=500, detail=f"Import failed: {e}")
	
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
