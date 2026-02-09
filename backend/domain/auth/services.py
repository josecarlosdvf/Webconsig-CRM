"""Auth business rules."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.auth import repository
from domain.auth.models import Role, User, UserStatus
from domain.auth.schemas import (
	ChangePasswordRequest,
	LoginRequest,
	RoleFilters,
	UserCreateRequest,
	UserFilters,
	UserUpdateRequest,
	RoleCreateRequest,
	RoleUpdateRequest,
)
from shared.auth import hash_password, issue_token, verify_password, validate_password
from shared.exceptions import conflict, not_found, validation_error
from shared.pagination import PaginatedResponse


VALID_USER_STATUS_TRANSITIONS = {
	UserStatus.active: {UserStatus.blocked},
	UserStatus.blocked: {UserStatus.active},
}


class AuthService:
	async def login(
		self, session: AsyncSession, tenant_id: UUID, data: LoginRequest
	) -> tuple[str, int, UUID, str]:
		user = await repository.get_user_by_username(session, tenant_id, data.username)
		if not user or not verify_password(data.password, user.password_hash):
			raise conflict("Invalid credentials")
		
		# Get user scopes from roles
		scopes = await repository.get_user_scopes(session, tenant_id, user.role_ids)
		
		# Issue token with scopes
		token = issue_token(user.id, tenant_id, user.email, scopes)
		return token, 3600, user.id, user.email

	async def list_users(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: UserFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[User]:
		return await repository.list_users(session, tenant_id, filters, page, page_size, sort)

	async def create_user(
		self, session: AsyncSession, tenant_id: UUID, data: UserCreateRequest
	) -> User:
		# Validate password against policy
		try:
			validate_password(data.password)
		except ValueError as exc:
			raise validation_error(str(exc))
		
		user = User(
			tenant_id=tenant_id,
			username=data.username,
			email=data.email,
			password_hash=hash_password(data.password),
			role_ids=[str(role_id) for role_id in data.role_ids],
			status=UserStatus.active,
		)
		return await repository.create_user(session, user)

	async def get_user(self, session: AsyncSession, tenant_id: UUID, user_id: UUID) -> User:
		user = await repository.get_user(session, tenant_id, user_id)
		if not user:
			raise not_found("User not found")
		return user

	async def update_user(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		user_id: UUID,
		data: UserUpdateRequest,
	) -> User:
		user = await self.get_user(session, tenant_id, user_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "role_ids" and value is not None:
				setattr(user, key, [str(role_id) for role_id in value])
			elif key == "status" and value is not None and value != user.status:
				self._validate_user_status(user.status, value)
				setattr(user, key, value)
			else:
				setattr(user, key, value)
		return await repository.update_user(session, user)

	async def change_password(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		user_id: UUID,
		data: ChangePasswordRequest,
	) -> None:
		# Validate new password against policy
		try:
			validate_password(data.password)
		except ValueError as exc:
			raise validation_error(str(exc))
		
		user = await self.get_user(session, tenant_id, user_id)
		user.password_hash = hash_password(data.password)
		await repository.update_user(session, user)

	async def list_roles(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: RoleFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Role]:
		return await repository.list_roles(session, tenant_id, filters, page, page_size, sort)

	async def create_role(
		self, session: AsyncSession, tenant_id: UUID, data: RoleCreateRequest
	) -> Role:
		role = Role(
			tenant_id=tenant_id,
			name=data.name,
			scopes=data.scopes
		)
		return await repository.create_role(session, role)

	async def get_role(
		self, session: AsyncSession, tenant_id: UUID, role_id: UUID
	) -> Role:
		role = await repository.get_role(session, tenant_id, role_id)
		if not role:
			raise not_found("Role not found")
		return role

	async def update_role(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		role_id: UUID,
		data: "RoleUpdateRequest",
	) -> Role:
		role = await self.get_role(session, tenant_id, role_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			setattr(role, key, value)
		return await repository.update_role(session, role)

	def _validate_user_status(self, current_status: UserStatus, new_status: UserStatus) -> None:
		allowed = VALID_USER_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)


auth_service = AuthService()
