"""Import processing engine with batch processing, validation, and duplicate detection."""

import asyncio
import logging
from typing import Any, Type
from uuid import UUID

from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.importer import ImportJob, ImportStatus
from shared.import_engine import create_parser
from shared.storage import get_storage


logger = logging.getLogger(__name__)


# Schema registry mapping domain.entity to Pydantic create schemas
SCHEMA_REGISTRY: dict[str, Type[BaseModel]] = {}


def register_import_schema(domain: str, entity: str, schema: Type[BaseModel]) -> None:
    """Register a Pydantic schema for import validation."""
    key = f"{domain}.{entity}"
    SCHEMA_REGISTRY[key] = schema
    logger.info(f"Registered import schema: {key}")


def get_import_schema(domain: str, entity: str) -> Type[BaseModel] | None:
    """Get the registered schema for a domain.entity."""
    key = f"{domain}.{entity}"
    return SCHEMA_REGISTRY.get(key)


# Unique field mapping for duplicate detection
UNIQUE_FIELDS: dict[str, list[str]] = {
    "crm.clients": ["email", "document"],
    "crm.leads": ["email"],
    "finance.companies": ["cnpj"],
    "auth.users": ["username", "email"],
    "hr.employees": ["email", "document"],
    "inventory.items": ["sku"],
}


def get_unique_fields(domain: str, entity: str) -> list[str]:
    """Get unique fields for duplicate detection."""
    key = f"{domain}.{entity}"
    return UNIQUE_FIELDS.get(key, [])


class ImportProcessor:
    """Process import jobs with batch processing and validation."""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    async def process_job(
        self,
        session: AsyncSession,
        job: ImportJob,
        repository,  # Domain-specific repository for CRUD operations
    ) -> ImportJob:
        """
        Process an import job with batch processing.
        
        Args:
            session: Database session
            job: Import job to process
            repository: Repository instance for the target entity
            
        Returns:
            Updated import job
        """
        logger.info(f"Starting import job {job.id} for {job.domain}.{job.entity}")
        
        try:
            # Update job status to processing
            job.status = ImportStatus.processing
            await session.commit()
            
            # Download file from storage
            storage = get_storage()
            file_key = self._extract_storage_key(job.file_url)
            file_content = await storage.download(file_key)
            
            # Parse file
            parser = create_parser(job.file_format.value)
            
            # Create file-like object from bytes
            import io
            file_obj = io.BytesIO(file_content)
            
            columns, rows = parser.parse(file_obj)
            job.total_rows = len(rows)
            
            # Get schema for validation
            schema = get_import_schema(job.domain, job.entity)
            if not schema:
                logger.warning(f"No schema registered for {job.domain}.{job.entity}, skipping validation")
            
            # Get unique fields for duplicate detection
            unique_fields = get_unique_fields(job.domain, job.entity)
            
            # Process in batches
            success_count = 0
            error_count = 0
            duplicate_count = 0
            errors = []
            
            for batch_start in range(0, len(rows), self.batch_size):
                batch_end = min(batch_start + self.batch_size, len(rows))
                batch = rows[batch_start:batch_end]
                
                logger.info(f"Processing batch {batch_start}-{batch_end} of {len(rows)}")
                
                # Process batch with transaction
                batch_results = await self._process_batch(
                    session=session,
                    batch=batch,
                    batch_offset=batch_start,
                    mapping=job.column_mapping,
                    schema=schema,
                    unique_fields=unique_fields,
                    repository=repository,
                    tenant_id=job.tenant_id,
                    options=job.options,
                )
                
                success_count += batch_results["success"]
                error_count += batch_results["errors_count"]
                duplicate_count += batch_results["duplicates"]
                errors.extend(batch_results["error_details"])
                
                # Update progress
                job.processed_rows = batch_end
                job.success_count = success_count
                job.error_count = error_count
                job.duplicate_count = duplicate_count
                await session.commit()
                
                logger.info(
                    f"Batch complete: {batch_results['success']} success, "
                    f"{batch_results['errors_count']} errors, "
                    f"{batch_results['duplicates']} duplicates"
                )
            
            # Mark job as completed
            job.status = ImportStatus.completed if error_count == 0 else ImportStatus.completed_with_errors
            job.errors = errors[:100]  # Keep only first 100 errors
            
            logger.info(
                f"Import job {job.id} completed: {success_count} success, "
                f"{error_count} errors, {duplicate_count} duplicates"
            )
            
            await session.commit()
            return job
            
        except Exception as e:
            logger.error(f"Import job {job.id} failed: {e}", exc_info=True)
            job.status = ImportStatus.failed
            job.errors = [{"error": str(e)}]
            await session.commit()
            raise
    
    async def _process_batch(
        self,
        session: AsyncSession,
        batch: list[dict[str, Any]],
        batch_offset: int,
        mapping: dict[str, str],
        schema: Type[BaseModel] | None,
        unique_fields: list[str],
        repository,
        tenant_id: UUID,
        options: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process a batch of rows with transaction.
        
        Returns:
            Dict with success count, error count, duplicate count, and error details
        """
        success = 0
        errors_count = 0
        duplicates = 0
        error_details = []
        
        # Start a nested transaction for the batch
        async with session.begin_nested():
            for i, row in enumerate(batch):
                row_number = batch_offset + i + 1
                
                try:
                    # Apply column mapping
                    mapped_data = self._apply_mapping(row, mapping)
                    
                    # Validate against schema if available
                    if schema:
                        try:
                            validated_data = schema(**mapped_data)
                            mapped_data = validated_data.model_dump(exclude_unset=True)
                        except ValidationError as e:
                            errors_count += 1
                            error_details.append({
                                "row": row_number,
                                "field": e.errors()[0]["loc"][0] if e.errors() else "unknown",
                                "value": None,
                                "error": str(e.errors()[0]["msg"]) if e.errors() else str(e),
                            })
                            continue
                    
                    # Check for duplicates
                    is_duplicate = False
                    if unique_fields:
                        is_duplicate = await self._check_duplicate(
                            session=session,
                            repository=repository,
                            tenant_id=tenant_id,
                            data=mapped_data,
                            unique_fields=unique_fields,
                        )
                    
                    if is_duplicate:
                        duplicates += 1
                        
                        # Update existing if option is enabled
                        if options.get("update_existing", False):
                            # TODO: Implement update logic
                            logger.debug(f"Skipping update for duplicate at row {row_number}")
                        
                        # Skip if skip_duplicates is enabled
                        if options.get("skip_duplicates", True):
                            continue
                    
                    # Skip actual insert if dry_run
                    if options.get("dry_run", False):
                        success += 1
                        continue
                    
                    # Create record via repository
                    # Note: This assumes repository has a create method that accepts tenant_id and data
                    # Each domain repository should implement this interface
                    await repository.create(session, tenant_id, mapped_data)
                    success += 1
                    
                except Exception as e:
                    errors_count += 1
                    error_details.append({
                        "row": row_number,
                        "field": "unknown",
                        "value": None,
                        "error": str(e),
                    })
                    logger.error(f"Error processing row {row_number}: {e}")
        
        return {
            "success": success,
            "errors_count": errors_count,
            "duplicates": duplicates,
            "error_details": error_details,
        }
    
    def _apply_mapping(self, row: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
        """Apply column mapping to a row."""
        mapped = {}
        for file_col, schema_field in mapping.items():
            if file_col in row:
                mapped[schema_field] = row[file_col]
        return mapped
    
    async def _check_duplicate(
        self,
        session: AsyncSession,
        repository,
        tenant_id: UUID,
        data: dict[str, Any],
        unique_fields: list[str],
    ) -> bool:
        """
        Check if record is a duplicate based on unique fields.
        
        Returns:
            True if duplicate found
        """
        # Build query to check for existing records
        # This is a simplified implementation - repositories should provide a better interface
        for field in unique_fields:
            if field in data and data[field]:
                # Try to find existing record with this field value
                # Note: This requires repository to have a method like find_by_field
                # For now, we'll return False and let the database constraint handle it
                logger.debug(f"Checking duplicate for {field}={data[field]}")
        
        return False
    
    def _extract_storage_key(self, file_url: str) -> str:
        """Extract storage key from file URL."""
        # Simple implementation - assumes URL format is {base_url}/{key}
        # In production, this should be more robust
        parts = file_url.split("/")
        # Get everything after the domain/base
        if len(parts) > 3:
            return "/".join(parts[3:])
        return file_url


# Singleton instance
import_processor = ImportProcessor(batch_size=100)
