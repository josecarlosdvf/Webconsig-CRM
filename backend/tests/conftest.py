"""Test configuration."""

import os
from typing import AsyncGenerator
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import get_settings
from main import create_app
from shared import Base
from shared.auth import issue_token


def _get_test_db_url() -> str | None:
	return os.getenv("TEST_DATABASE_URL") or os.getenv("APP_DATABASE_URL")


@pytest_asyncio.fixture(scope="session")
async def engine():
	db_url = _get_test_db_url()
	if not db_url:
		pytest.skip("TEST_DATABASE_URL or APP_DATABASE_URL must be set")
	engine = create_async_engine(db_url, future=True)
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	yield engine
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)
	await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
	session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
	async with session_factory() as session:
		yield session


@pytest_asyncio.fixture()
async def client(engine) -> AsyncGenerator[AsyncClient, None]:
	app = create_app()
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://test") as async_client:
		yield async_client


@pytest.fixture()
def tenant_id() -> UUID:
	return uuid4()


@pytest.fixture()
def actor_id() -> UUID:
	return uuid4()


@pytest.fixture()
def auth_headers(tenant_id: UUID, actor_id: UUID) -> dict[str, str]:
	token = issue_token(actor_id, tenant_id, "admin@example.com")
	return {
		"Authorization": f"Bearer {token}",
		"X-Tenant-Id": str(tenant_id),
	}
