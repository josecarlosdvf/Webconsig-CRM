"""Alembic environment configuration."""

from __future__ import annotations

from logging.config import fileConfig
import asyncio
import os
import sys

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

from config import get_settings
from shared import Base

# Import all models to register metadata
from domain.auth import models as auth_models  # noqa: F401
from domain.billing import models as billing_models  # noqa: F401
from domain.crm import models as crm_models  # noqa: F401
from domain.finance import models as finance_models  # noqa: F401
from domain.hr import models as hr_models  # noqa: F401
from domain.inventory import models as inventory_models  # noqa: F401
from domain.sales import models as sales_models  # noqa: F401
from shared import audit as audit_models  # noqa: F401

config = context.config
if config.config_file_name is not None:
	fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
	settings = get_settings()
	return settings.database_url


def run_migrations_offline() -> None:
	url = get_url()
	context.configure(
		url=url,
		target_metadata=target_metadata,
		literal_binds=True,
		dialect_opts={"paramstyle": "named"},
		compare_type=True,
	)

	with context.begin_transaction():
		context.run_migrations()


async def run_migrations_online() -> None:
	configuration = config.get_section(config.config_ini_section)
	if configuration is None:
		raise RuntimeError("Missing Alembic configuration")
	configuration["sqlalchemy.url"] = get_url()

	connectable = async_engine_from_config(
		configuration,
		prefix="sqlalchemy.",
		poolclass=pool.NullPool,
	)

	def do_run_migrations(sync_connection) -> None:
		context.configure(
			connection=sync_connection,
			target_metadata=target_metadata,
			compare_type=True,
		)
		with context.begin_transaction():
			context.run_migrations()

	async with connectable.connect() as connection:
		await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
	run_migrations_offline()
else:
	asyncio.run(run_migrations_online())
