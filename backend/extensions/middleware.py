"""Extension guard middleware/dependency."""

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, get_tenant_id
from shared.extensions import TenantExtensionStatus, extension_service


def require_active_extension(extension_id: str):
    async def _guard(
        db: AsyncSession = Depends(get_db),
        tenant_id=Depends(get_tenant_id),
    ) -> None:
        tenant_extension = await extension_service.get_tenant_extension(
            db, tenant_id, extension_id
        )
        if tenant_extension.status != TenantExtensionStatus.active:
            raise HTTPException(status_code=403, detail="Extension not active for this tenant")

    return _guard
