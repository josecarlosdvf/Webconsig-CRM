"""Global dependency providers."""

from dataclasses import dataclass
from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import get_settings
from shared.auth import validate_token


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    email: str
    tenant_id: UUID
    scopes: list[str]


settings = get_settings()
engine = create_async_engine(settings.database_url, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


def _parse_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    if not authorization.lower().startswith("bearer "):
        return None
    return authorization.split(" ", 1)[1].strip()


def _tenant_from_token(token: str | None) -> UUID | None:
    if not token:
        return None
    payload = validate_token(token)
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        return None
    return UUID(tenant_id)


def get_tenant_id(
    authorization: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
) -> UUID:
    token = _parse_bearer(authorization)
    try:
        token_tenant_id = _tenant_from_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if token_tenant_id:
        return token_tenant_id
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing tenant header")
    try:
        return UUID(x_tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid tenant header") from exc


def get_current_user(
    authorization: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
) -> CurrentUser:
    token = _parse_bearer(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        payload = validate_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    user_id = payload.get("sub") or payload.get("user_id")
    email = payload.get("email")
    scopes = payload.get("scopes", [])
    if not user_id or not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    tenant_id = payload.get("tenant_id") or x_tenant_id
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Missing tenant context")
    try:
        return CurrentUser(
            id=UUID(user_id),
            email=email,
            tenant_id=UUID(tenant_id),
            scopes=scopes
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid token payload") from exc


def require_scopes(*required_scopes: str):
    """Dependency factory that checks if user has required scopes.
    
    Usage:
        @router.get("/clients", dependencies=[Depends(require_scopes("crm:read"))])
        async def list_clients(...):
            ...
    
    Or with multiple scopes (user must have ALL):
        @router.post("/clients", dependencies=[Depends(require_scopes("crm:write", "crm:read"))])
        async def create_client(...):
            ...
    """
    def _check_scopes(current_user: CurrentUser = Depends(get_current_user)):
        if not required_scopes:
            return current_user
        
        missing_scopes = [scope for scope in required_scopes if scope not in current_user.scopes]
        
        if missing_scopes:
            raise HTTPException(
                status_code=403,
                detail=f"Missing required scopes: {', '.join(missing_scopes)}"
            )
        
        return current_user
    
    return _check_scopes
