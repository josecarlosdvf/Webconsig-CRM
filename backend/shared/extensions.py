"""Extensions models, schemas, and services."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Enum as SqlEnum, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select

from shared import Base, IdMixin, TenantMixin, TimestampMixin


class ExtensionStatus(str, Enum):
    available = "available"
    deprecated = "deprecated"
    disabled = "disabled"


class TenantExtensionStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    error = "error"


class ExtensionDefinition(Base, TimestampMixin):
    __tablename__ = "shared_extensions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    domain: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ExtensionStatus] = mapped_column(
        SqlEnum(ExtensionStatus), default=ExtensionStatus.available, nullable=False
    )
    manifest: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class TenantExtension(Base, IdMixin, TenantMixin, TimestampMixin):
    __tablename__ = "shared_tenant_extensions"

    extension_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TenantExtensionStatus] = mapped_column(
        SqlEnum(TenantExtensionStatus), default=TenantExtensionStatus.inactive, nullable=False
    )
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)


class ExtensionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    version: str
    description: str
    author: str
    domain: str
    status: ExtensionStatus
    manifest: dict[str, Any]


class TenantExtensionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    extension_id: str
    status: TenantExtensionStatus
    config: dict[str, Any]
    activated_at: datetime | None
    deactivated_at: datetime | None
    activated_by: UUID | None
    created_at: datetime
    updated_at: datetime


class ExtensionConfigUpdateRequest(BaseModel):
    config: dict[str, Any]


class ExtensionRepository:
    async def list_extensions(self, session: AsyncSession) -> list[ExtensionDefinition]:
        result = await session.execute(select(ExtensionDefinition))
        return list(result.scalars().all())

    async def get_extension(
        self, session: AsyncSession, extension_id: str
    ) -> ExtensionDefinition | None:
        result = await session.execute(
            select(ExtensionDefinition).where(ExtensionDefinition.id == extension_id)
        )
        return result.scalar_one_or_none()

    async def list_tenant_extensions(
        self, session: AsyncSession, tenant_id: UUID
    ) -> list[TenantExtension]:
        result = await session.execute(
            select(TenantExtension).where(TenantExtension.tenant_id == tenant_id)
        )
        return list(result.scalars().all())

    async def get_tenant_extension(
        self, session: AsyncSession, tenant_id: UUID, extension_id: str
    ) -> TenantExtension | None:
        result = await session.execute(
            select(TenantExtension).where(
                TenantExtension.tenant_id == tenant_id,
                TenantExtension.extension_id == extension_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_tenant_extension(
        self, session: AsyncSession, tenant_extension: TenantExtension
    ) -> TenantExtension:
        session.add(tenant_extension)
        await session.flush()
        return tenant_extension

    async def update_tenant_extension(
        self, session: AsyncSession, tenant_extension: TenantExtension
    ) -> TenantExtension:
        session.add(tenant_extension)
        await session.flush()
        return tenant_extension


class ExtensionService:
    def __init__(self, repository: ExtensionRepository) -> None:
        self.repository = repository

    async def list_extensions(self, session: AsyncSession) -> list[ExtensionDefinition]:
        return await self.repository.list_extensions(session)

    async def get_extension(
        self, session: AsyncSession, extension_id: str
    ) -> ExtensionDefinition:
        extension = await self.repository.get_extension(session, extension_id)
        if not extension:
            raise ValueError("Extension not found")
        return extension

    async def list_tenant_extensions(
        self, session: AsyncSession, tenant_id: UUID
    ) -> list[TenantExtension]:
        return await self.repository.list_tenant_extensions(session, tenant_id)

    async def get_tenant_extension(
        self, session: AsyncSession, tenant_id: UUID, extension_id: str
    ) -> TenantExtension:
        tenant_extension = await self.repository.get_tenant_extension(
            session, tenant_id, extension_id
        )
        if not tenant_extension:
            raise ValueError("Tenant extension not found")
        return tenant_extension

    async def activate_extension(
        self, session: AsyncSession, tenant_id: UUID, extension_id: str, actor_id: UUID
    ) -> TenantExtension:
        tenant_extension = await self.repository.get_tenant_extension(
            session, tenant_id, extension_id
        )
        if not tenant_extension:
            tenant_extension = TenantExtension(
                tenant_id=tenant_id,
                extension_id=extension_id,
                status=TenantExtensionStatus.active,
                activated_at=datetime.utcnow(),
                activated_by=actor_id,
            )
            return await self.repository.create_tenant_extension(session, tenant_extension)
        tenant_extension.status = TenantExtensionStatus.active
        tenant_extension.activated_at = datetime.utcnow()
        tenant_extension.deactivated_at = None
        tenant_extension.activated_by = actor_id
        return await self.repository.update_tenant_extension(session, tenant_extension)

    async def deactivate_extension(
        self, session: AsyncSession, tenant_id: UUID, extension_id: str
    ) -> TenantExtension:
        tenant_extension = await self.get_tenant_extension(session, tenant_id, extension_id)
        tenant_extension.status = TenantExtensionStatus.inactive
        tenant_extension.deactivated_at = datetime.utcnow()
        return await self.repository.update_tenant_extension(session, tenant_extension)

    async def update_config(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        extension_id: str,
        config: dict[str, Any],
    ) -> TenantExtension:
        tenant_extension = await self.get_tenant_extension(session, tenant_id, extension_id)
        tenant_extension.config = config
        return await self.repository.update_tenant_extension(session, tenant_extension)


extension_repository = ExtensionRepository()
extension_service = ExtensionService(extension_repository)
