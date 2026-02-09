"""Auth helpers."""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from config import get_settings

ALGORITHM = "HS256"


@dataclass
class PasswordPolicy:
	"""Password complexity policy configuration."""
	min_length: int = 8
	require_uppercase: bool = True
	require_lowercase: bool = True
	require_digit: bool = True
	require_special: bool = True
	special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
	
	def validate(self, password: str) -> tuple[bool, list[str]]:
		"""Validate password against policy.
		
		Returns:
			(is_valid, list_of_errors)
		"""
		errors = []
		
		if len(password) < self.min_length:
			errors.append(f"Password must be at least {self.min_length} characters long")
		
		if self.require_uppercase and not re.search(r'[A-Z]', password):
			errors.append("Password must contain at least one uppercase letter")
		
		if self.require_lowercase and not re.search(r'[a-z]', password):
			errors.append("Password must contain at least one lowercase letter")
		
		if self.require_digit and not re.search(r'\d', password):
			errors.append("Password must contain at least one digit")
		
		if self.require_special:
			if not any(char in self.special_chars for char in password):
				errors.append(f"Password must contain at least one special character ({self.special_chars})")
		
		return len(errors) == 0, errors


def get_password_policy() -> PasswordPolicy:
	"""Get password policy from settings."""
	settings = get_settings()
	return PasswordPolicy(
		min_length=settings.password_min_length,
		require_uppercase=settings.password_require_uppercase,
		require_lowercase=settings.password_require_lowercase,
		require_digit=settings.password_require_digit,
		require_special=settings.password_require_special,
	)


def validate_password(password: str) -> None:
	"""Validate password according to configured policy.
	
	Raises:
		ValueError: If password does not meet policy requirements.
	"""
	policy = get_password_policy()
	is_valid, errors = policy.validate(password)
	if not is_valid:
		raise ValueError("; ".join(errors))


def hash_password(password: str) -> str:
	"""Hash a password using bcrypt."""
	password_bytes = password.encode('utf-8')
	salt = bcrypt.gensalt()
	return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
	"""Verify a password against its hash."""
	password_bytes = password.encode('utf-8')
	hash_bytes = password_hash.encode('utf-8')
	return bcrypt.checkpw(password_bytes, hash_bytes)


def issue_token(user_id: UUID, tenant_id: UUID, email: str, scopes: list[str] | None = None) -> str:
	settings = get_settings()
	now = datetime.now(timezone.utc)
	payload = {
		"sub": str(user_id),
		"tenant_id": str(tenant_id),
		"email": email,
		"scopes": scopes or [],
		"iat": int(now.timestamp()),
		"exp": int((now + timedelta(seconds=settings.jwt_expires_in)).timestamp()),
	}
	return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
	settings = get_settings()
	return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])


def validate_token(token: str) -> dict:
	try:
		return decode_token(token)
	except JWTError as exc:
		raise ValueError("Invalid token") from exc
