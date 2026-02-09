"""Cross-tenant validation helpers."""

from uuid import UUID
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.exceptions import validation_error


async def validate_fk_same_tenant(
    session: AsyncSession,
    entity_model: type,
    entity_id: UUID,
    tenant_id: UUID,
    field_name: str = "id",
) -> None:
    """
    Validate that a foreign key entity exists and belongs to the same tenant.
    
    Args:
        session: Database session
        entity_model: The SQLAlchemy model class
        entity_id: The ID of the entity to check
        tenant_id: The expected tenant_id
        field_name: Name of the field being validated (for error messages)
    
    Raises:
        validation_error: If entity doesn't exist or belongs to different tenant
    """
    query = select(entity_model).where(
        entity_model.id == entity_id,
        entity_model.tenant_id == tenant_id
    )
    result = await session.execute(query)
    entity = result.scalar_one_or_none()
    
    if not entity:
        raise validation_error(
            f"Invalid {field_name}: entity not found or belongs to different tenant"
        )
