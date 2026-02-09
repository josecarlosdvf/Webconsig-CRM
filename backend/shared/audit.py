"""Audit logging."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SqlEnum, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from shared import Base


class AuditAction(str, Enum):
	create = "create"
	update = "update"
	delete = "delete"
	restore = "restore"
	login = "login"
	logout = "logout"
	password_change = "password_change"
	stage_change = "stage_change"
	approve = "approve"
	reject = "reject"
	assign = "assign"
	convert = "convert"
	confirm = "confirm"
	terminate = "terminate"
	export = "export"
	import_ = "import"
	activate_extension = "activate_extension"
	deactivate_extension = "deactivate_extension"


class AuditLog(Base):
	__tablename__ = "shared_audit_logs"

	id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
	tenant_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), index=True)
	actor_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), index=True)
	actor_email: Mapped[str] = mapped_column(String, nullable=False)
	action: Mapped[AuditAction] = mapped_column(SqlEnum(AuditAction), nullable=False)
	domain: Mapped[str] = mapped_column(String, nullable=False)
	entity: Mapped[str] = mapped_column(String, nullable=False)
	entity_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
	changes: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
	ip_address: Mapped[str] = mapped_column(String, nullable=False)
	user_agent: Mapped[str] = mapped_column(String, nullable=False)
	endpoint: Mapped[str] = mapped_column(String, nullable=False)
	occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
	metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)


async def log_action(
	session: AsyncSession,
	*,
	tenant_id: UUID,
	actor_id: UUID,
	actor_email: str,
	action: AuditAction,
	domain: str,
	entity: str,
	entity_id: UUID,
	changes: dict[str, Any],
	ip_address: str,
	user_agent: str,
	endpoint: str,
	occurred_at: datetime,
	metadata: dict[str, Any] | None = None,
) -> AuditLog:
	audit_log = AuditLog(
		tenant_id=tenant_id,
		actor_id=actor_id,
		actor_email=actor_email,
		action=action,
		domain=domain,
		entity=entity,
		entity_id=entity_id,
		changes=changes,
		ip_address=ip_address,
		user_agent=user_agent,
		endpoint=endpoint,
		occurred_at=occurred_at,
		metadata_=metadata or {},
	)
	session.add(audit_log)
	await session.flush()
	return audit_log
