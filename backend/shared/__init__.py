"""Shared cross-cutting modules."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
	return datetime.now(timezone.utc)


class Base(DeclarativeBase):
	pass


class TenantMixin:
	tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True)


class TimestampMixin:
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=utcnow, onupdate=utcnow
	)
	deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class IdMixin:
	id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
