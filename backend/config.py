"""Backend configuration."""

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class AppSettings:
    app_env: str = os.getenv("APP_ENV", "development")
    api_version: str = os.getenv("APP_API_VERSION", "v1")
    database_url: str = os.getenv(
        "APP_DATABASE_URL",
        "postgresql+asyncpg://postgres:Ti123%21%40%23@localhost:5433/webconsig",
    )
    jwt_secret: str = os.getenv("APP_JWT_SECRET", "change-me")
    jwt_expires_in: int = int(os.getenv("APP_JWT_EXPIRES_IN", "3600"))
    tenant_header: str = os.getenv("APP_TENANT_HEADER", "X-Tenant-Id")
    webhook_secret: str = os.getenv("APP_WEBHOOK_SECRET", "change-me")
    enable_tls: bool = os.getenv("APP_ENABLE_TLS", "false").lower() == "true"
    
    # Password policy settings
    password_min_length: int = int(os.getenv("APP_PASSWORD_MIN_LENGTH", "8"))
    password_require_uppercase: bool = os.getenv("APP_PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    password_require_lowercase: bool = os.getenv("APP_PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
    password_require_digit: bool = os.getenv("APP_PASSWORD_REQUIRE_DIGIT", "true").lower() == "true"
    password_require_special: bool = os.getenv("APP_PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
    
    # CORS settings
    cors_allowed_origins: list[str] = os.getenv("APP_CORS_ALLOWED_ORIGINS", "*").split(",")
    cors_allow_credentials: bool = os.getenv("APP_CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    cors_allow_methods: list[str] = os.getenv("APP_CORS_ALLOW_METHODS", "*").split(",")
    cors_allow_headers: list[str] = os.getenv("APP_CORS_ALLOW_HEADERS", "*").split(",")


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
