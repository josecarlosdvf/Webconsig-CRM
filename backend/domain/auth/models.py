"""Auth ORM models."""

from enum import Enum

from sqlalchemy import Enum as SqlEnum, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared import Base, IdMixin, TenantMixin, TimestampMixin


class UserStatus(str, Enum):
	active = "active"
	blocked = "blocked"


class User(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "auth_users"

	username: Mapped[str] = mapped_column(String, nullable=False)
	email: Mapped[str] = mapped_column(String, nullable=False)
	password_hash: Mapped[str] = mapped_column(String, nullable=False)
	status: Mapped[UserStatus] = mapped_column(
		SqlEnum(UserStatus), default=UserStatus.active, nullable=False
	)
	role_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)


class Role(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "auth_roles"

	name: Mapped[str] = mapped_column(String, nullable=False)
	scopes: Mapped[list[str]] = mapped_column(JSONB, default=list)
