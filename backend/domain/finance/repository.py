"""Finance data access layer."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.finance.models import Account, Company, Payable, Payment, Receivable
from domain.finance.schemas import (
	AccountFilters,
	CompanyFilters,
	PayableFilters,
	PaymentFilters,
	ReceivableFilters,
)
from shared import utcnow
from shared.filters import (
	apply_date_range_filter,
	apply_enum_filter,
	apply_sorting,
	apply_text_filter,
	apply_text_search,
)
from shared.pagination import (
	PaginatedResponse,
	build_paginated_response,
	get_total_count,
	paginate_query,
)


async def create_company(session: AsyncSession, company: Company) -> Company:
	session.add(company)
	await session.flush()
	return company


async def list_companies(
	session: AsyncSession,
	tenant_id: UUID,
	filters: CompanyFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Company]:
	query = select(Company).where(Company.tenant_id == tenant_id, Company.deleted_at.is_(None))

	query = apply_text_filter(query, Company.name, filters.name)
	query = apply_text_filter(query, Company.cnpj, filters.cnpj)
	query = apply_enum_filter(query, Company.status, filters.status)
	query = apply_text_search(query, [Company.name, Company.cnpj, Company.trading_name], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"name": Company.name,
		"cnpj": Company.cnpj,
		"status": Company.status,
		"created_at": Company.created_at,
		"updated_at": Company.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_company(
	session: AsyncSession, tenant_id: UUID, company_id: UUID
) -> Company | None:
	result = await session.execute(
		select(Company).where(
			Company.tenant_id == tenant_id,
			Company.id == company_id,
			Company.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_company(session: AsyncSession, company: Company) -> Company:
	session.add(company)
	await session.flush()
	return company


async def create_account(session: AsyncSession, account: Account) -> Account:
	session.add(account)
	await session.flush()
	return account


async def list_accounts(
	session: AsyncSession,
	tenant_id: UUID,
	filters: AccountFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Account]:
	query = select(Account).where(Account.tenant_id == tenant_id, Account.deleted_at.is_(None))

	query = apply_enum_filter(query, Account.type, filters.type)
	query = apply_enum_filter(query, Account.status, filters.status)
	query = apply_text_filter(query, Account.currency, filters.currency)
	query = apply_text_search(query, [Account.name], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"name": Account.name,
		"type": Account.type,
		"status": Account.status,
		"created_at": Account.created_at,
		"updated_at": Account.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_account(
	session: AsyncSession, tenant_id: UUID, account_id: UUID
) -> Account | None:
	result = await session.execute(
		select(Account).where(
			Account.tenant_id == tenant_id,
			Account.id == account_id,
			Account.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_account(session: AsyncSession, account: Account) -> Account:
	session.add(account)
	await session.flush()
	return account


async def create_payment(session: AsyncSession, payment: Payment) -> Payment:
	session.add(payment)
	await session.flush()
	return payment


async def list_payments(
	session: AsyncSession,
	tenant_id: UUID,
	filters: PaymentFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Payment]:
	query = select(Payment).where(Payment.tenant_id == tenant_id, Payment.deleted_at.is_(None))

	query = apply_enum_filter(query, Payment.account_id, filters.account_id)
	query = apply_enum_filter(query, Payment.company_id, filters.company_id)
	query = apply_enum_filter(query, Payment.status, filters.status)
	query = apply_enum_filter(query, Payment.method, filters.method)
	query = apply_date_range_filter(
		query, Payment.created_at, filters.created_from, filters.created_to
	)
	query = apply_text_search(query, [Payment.currency], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"amount": Payment.amount,
		"status": Payment.status,
		"method": Payment.method,
		"created_at": Payment.created_at,
		"updated_at": Payment.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_payment(
	session: AsyncSession, tenant_id: UUID, payment_id: UUID
) -> Payment | None:
	result = await session.execute(
		select(Payment).where(
			Payment.tenant_id == tenant_id,
			Payment.id == payment_id,
			Payment.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_payment(session: AsyncSession, payment: Payment) -> Payment:
	session.add(payment)
	await session.flush()
	return payment


async def create_payable(session: AsyncSession, payable: Payable) -> Payable:
	session.add(payable)
	await session.flush()
	return payable


async def list_payables(
	session: AsyncSession,
	tenant_id: UUID,
	filters: PayableFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Payable]:
	query = select(Payable).where(Payable.tenant_id == tenant_id, Payable.deleted_at.is_(None))

	query = apply_enum_filter(query, Payable.company_id, filters.company_id)
	query = apply_enum_filter(query, Payable.account_id, filters.account_id)
	query = apply_enum_filter(query, Payable.status, filters.status)
	query = apply_text_filter(query, Payable.category, filters.category)
	query = apply_date_range_filter(query, Payable.due_date, filters.due_from, filters.due_to)
	query = apply_date_range_filter(
		query, Payable.created_at, filters.created_from, filters.created_to
	)
	query = apply_text_search(query, [Payable.description, Payable.category], filters.q)

	total = await get_total_count(session, query)

	column_map = {
		"amount": Payable.amount,
		"due_date": Payable.due_date,
		"status": Payable.status,
		"created_at": Payable.created_at,
		"updated_at": Payable.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_payable(
	session: AsyncSession, tenant_id: UUID, payable_id: UUID
) -> Payable | None:
	result = await session.execute(
		select(Payable).where(
			Payable.tenant_id == tenant_id,
			Payable.id == payable_id,
			Payable.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_payable(session: AsyncSession, payable: Payable) -> Payable:
	session.add(payable)
	await session.flush()
	return payable


async def create_receivable(session: AsyncSession, receivable: Receivable) -> Receivable:
	session.add(receivable)
	await session.flush()
	return receivable


async def list_receivables(
	session: AsyncSession,
	tenant_id: UUID,
	filters: ReceivableFilters,
	page: int,
	page_size: int,
	sort: str | None = None,
) -> PaginatedResponse[Receivable]:
	query = select(Receivable).where(
		Receivable.tenant_id == tenant_id, Receivable.deleted_at.is_(None)
	)

	query = apply_enum_filter(query, Receivable.company_id, filters.company_id)
	query = apply_enum_filter(query, Receivable.account_id, filters.account_id)
	query = apply_enum_filter(query, Receivable.status, filters.status)
	query = apply_text_filter(query, Receivable.category, filters.category)
	query = apply_text_filter(query, Receivable.source_domain, filters.source_domain)
	query = apply_date_range_filter(
		query, Receivable.due_date, filters.due_from, filters.due_to
	)
	query = apply_date_range_filter(
		query, Receivable.created_at, filters.created_from, filters.created_to
	)
	query = apply_text_search(
		query,
		[Receivable.description, Receivable.category, Receivable.source_domain],
		filters.q,
	)

	total = await get_total_count(session, query)

	column_map = {
		"amount": Receivable.amount,
		"due_date": Receivable.due_date,
		"status": Receivable.status,
		"created_at": Receivable.created_at,
		"updated_at": Receivable.updated_at,
	}
	query = apply_sorting(query, column_map, sort)
	query = paginate_query(query, page, page_size)

	result = await session.execute(query)
	items = list(result.scalars().all())
	return build_paginated_response(items, page, page_size, total)


async def get_receivable(
	session: AsyncSession, tenant_id: UUID, receivable_id: UUID
) -> Receivable | None:
	result = await session.execute(
		select(Receivable).where(
			Receivable.tenant_id == tenant_id,
			Receivable.id == receivable_id,
			Receivable.deleted_at.is_(None),
		)
	)
	return result.scalar_one_or_none()


async def update_receivable(session: AsyncSession, receivable: Receivable) -> Receivable:
	session.add(receivable)
	await session.flush()
	return receivable


async def soft_delete_payable(session: AsyncSession, payable: Payable) -> Payable:
	payable.deleted_at = utcnow()
	session.add(payable)
	await session.flush()
	return payable


async def soft_delete_receivable(session: AsyncSession, receivable: Receivable) -> Receivable:
	receivable.deleted_at = utcnow()
	session.add(receivable)
	await session.flush()
	return receivable


async def soft_delete_payment(session: AsyncSession, payment: Payment) -> Payment:
	payment.deleted_at = utcnow()
	session.add(payment)
	await session.flush()
	return payment


async def soft_delete_account(session: AsyncSession, account: Account) -> Account:
	account.deleted_at = utcnow()
	session.add(account)
	await session.flush()
	return account


async def soft_delete_company(session: AsyncSession, company: Company) -> Company:
	company.deleted_at = utcnow()
	session.add(company)
	await session.flush()
	return company
