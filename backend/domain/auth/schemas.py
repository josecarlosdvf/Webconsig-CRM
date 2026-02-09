"""Auth schemas/contracts."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain.auth.models import UserStatus


class BaseSchema(BaseModel):
	model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseSchema):
	username: str
	password: str


class LoginResponse(BaseSchema):
	access_token: str
	token_type: str = "bearer"
	expires_in: int


class UserCreateRequest(BaseSchema):
	username: str
	email: str
	password: str
	role_ids: list[UUID]


class UserUpdateRequest(BaseSchema):
	username: Optional[str] = None
	email: Optional[str] = None
	status: Optional[UserStatus] = None
	role_ids: Optional[list[UUID]] = None


class UserResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	username: str
	email: str
	status: UserStatus
	role_ids: list[UUID]
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class UserFilters(BaseModel):
	"""Filter parameters for listing users."""
	username: Optional[str] = Field(None, description="Exact username match")
	email: Optional[str] = Field(None, description="Exact email match")
	status: Optional[UserStatus] = Field(None, description="User status")
	role_id: Optional[UUID] = Field(None, description="Filter by role ID")
	q: Optional[str] = Field(None, description="Search across username and email")


class RoleCreateRequest(BaseSchema):
	name: str
	scopes: list[str] = []


class RoleUpdateRequest(BaseSchema):
	name: Optional[str] = None
	scopes: Optional[list[str]] = None


class RoleResponse(BaseSchema):
	id: UUID
	tenant_id: UUID
	name: str
	scopes: list[str]
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class RoleFilters(BaseModel):
	"""Filter parameters for listing roles."""
	name: Optional[str] = Field(None, description="Exact role name match")
	q: Optional[str] = Field(None, description="Search across name")


class ChangePasswordRequest(BaseSchema):
	password: str
