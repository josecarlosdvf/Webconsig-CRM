"""Finance business rules."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.finance import repository
from domain.finance.models import (
	AccountStatus,
	CompanyStatus,
	PayableStatus,
	PaymentStatus,
	ReceivableStatus,
)
from domain.finance.schemas import (
	AccountCreateRequest,
	AccountFilters,
	AccountUpdateRequest,
	CompanyCreateRequest,
	CompanyFilters,
	CompanyUpdateRequest,
	PayableFilters,
	PayableCreateRequest,
	PayableUpdateRequest,
	PaymentFilters,
	PaymentCreateRequest,
	ReceivableFilters,
	ReceivableCreateRequest,
	ReceivableUpdateRequest,
)
from domain.finance.models import Account, Company, Payable, Payment, Receivable
from shared.exceptions import not_found, validation_error
from shared.pagination import PaginatedResponse
from shared.validators import validate_fk_same_tenant


VALID_COMPANY_STATUS_TRANSITIONS = {
	CompanyStatus.active: {CompanyStatus.inactive},
	CompanyStatus.inactive: {CompanyStatus.active},
}

VALID_ACCOUNT_STATUS_TRANSITIONS = {
	AccountStatus.active: {AccountStatus.inactive},
	AccountStatus.inactive: {AccountStatus.active},
}

VALID_PAYMENT_STATUS_TRANSITIONS = {
	PaymentStatus.pending: {
		PaymentStatus.confirmed,
		PaymentStatus.failed,
		PaymentStatus.canceled,
	},
	PaymentStatus.confirmed: set(),
	PaymentStatus.failed: set(),
	PaymentStatus.canceled: set(),
}

VALID_PAYABLE_STATUS_TRANSITIONS = {
	PayableStatus.pending: {
		PayableStatus.approved,
		PayableStatus.paid,
		PayableStatus.overdue,
		PayableStatus.canceled,
	},
	PayableStatus.approved: {
		PayableStatus.paid,
		PayableStatus.overdue,
		PayableStatus.canceled,
	},
	PayableStatus.overdue: {PayableStatus.paid, PayableStatus.canceled},
	PayableStatus.paid: set(),
	PayableStatus.canceled: set(),
}

VALID_RECEIVABLE_STATUS_TRANSITIONS = {
	ReceivableStatus.pending: {
		ReceivableStatus.confirmed,
		ReceivableStatus.received,
		ReceivableStatus.overdue,
		ReceivableStatus.canceled,
	},
	ReceivableStatus.confirmed: {
		ReceivableStatus.received,
		ReceivableStatus.overdue,
		ReceivableStatus.canceled,
	},
	ReceivableStatus.overdue: {ReceivableStatus.received, ReceivableStatus.canceled},
	ReceivableStatus.received: set(),
	ReceivableStatus.canceled: set(),
}


class FinanceService:
	async def list_companies(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: CompanyFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Company]:
		return await repository.list_companies(session, tenant_id, filters, page, page_size, sort)

	async def create_company(
		self, session: AsyncSession, tenant_id: UUID, data: CompanyCreateRequest
	) -> Company:
		company = Company(tenant_id=tenant_id, **data.model_dump())
		return await repository.create_company(session, company)

	async def get_company(
		self, session: AsyncSession, tenant_id: UUID, company_id: UUID
	) -> Company:
		company = await repository.get_company(session, tenant_id, company_id)
		if not company:
			raise not_found("Company not found")
		return company

	async def update_company(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		company_id: UUID,
		data: CompanyUpdateRequest,
	) -> Company:
		company = await self.get_company(session, tenant_id, company_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "status" and value is not None and value != company.status:
				self._validate_company_status(company.status, value)
			setattr(company, key, value)
		return await repository.update_company(session, company)

	async def list_accounts(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: AccountFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Account]:
		return await repository.list_accounts(session, tenant_id, filters, page, page_size, sort)

	async def create_account(
		self, session: AsyncSession, tenant_id: UUID, data: AccountCreateRequest
	) -> Account:
		account = Account(tenant_id=tenant_id, **data.model_dump())
		return await repository.create_account(session, account)

	async def get_account(
		self, session: AsyncSession, tenant_id: UUID, account_id: UUID
	) -> Account:
		account = await repository.get_account(session, tenant_id, account_id)
		if not account:
			raise not_found("Account not found")
		return account

	async def update_account(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		account_id: UUID,
		data: AccountUpdateRequest,
	) -> Account:
		account = await self.get_account(session, tenant_id, account_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "status" and value is not None and value != account.status:
				self._validate_account_status(account.status, value)
			setattr(account, key, value)
		return await repository.update_account(session, account)

	async def list_payments(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: PaymentFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Payment]:
		return await repository.list_payments(session, tenant_id, filters, page, page_size, sort)

	async def create_payment(
		self, session: AsyncSession, tenant_id: UUID, data: PaymentCreateRequest
	) -> Payment:
		# Validate FKs belong to same tenant
		await validate_fk_same_tenant(
			session, Account, data.account_id, tenant_id, "account_id"
		)
		await validate_fk_same_tenant(
			session, Company, data.company_id, tenant_id, "company_id"
		)
		
		payment = Payment(tenant_id=tenant_id, **data.model_dump())
		return await repository.create_payment(session, payment)

	async def get_payment(
		self, session: AsyncSession, tenant_id: UUID, payment_id: UUID
	) -> Payment:
		payment = await repository.get_payment(session, tenant_id, payment_id)
		if not payment:
			raise not_found("Payment not found")
		return payment

	async def confirm_payment(
		self, session: AsyncSession, tenant_id: UUID, payment_id: UUID
	) -> Payment:
		payment = await self.get_payment(session, tenant_id, payment_id)
		if payment.status != PaymentStatus.confirmed:
			self._validate_payment_status(payment.status, PaymentStatus.confirmed)
		payment.status = PaymentStatus.confirmed
		return await repository.update_payment(session, payment)

	async def list_payables(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: PayableFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Payable]:
		return await repository.list_payables(session, tenant_id, filters, page, page_size, sort)

	async def create_payable(
		self, session: AsyncSession, tenant_id: UUID, data: PayableCreateRequest
	) -> Payable:
		# Validate FKs belong to same tenant
		await validate_fk_same_tenant(
			session, Company, data.company_id, tenant_id, "company_id"
		)
		await validate_fk_same_tenant(
			session, Account, data.account_id, tenant_id, "account_id"
		)
		
		payable = Payable(tenant_id=tenant_id, **data.model_dump())
		return await repository.create_payable(session, payable)

	async def get_payable(
		self, session: AsyncSession, tenant_id: UUID, payable_id: UUID
	) -> Payable:
		payable = await repository.get_payable(session, tenant_id, payable_id)
		if not payable:
			raise not_found("Payable not found")
		return payable

	async def update_payable(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		payable_id: UUID,
		data: PayableUpdateRequest,
	) -> Payable:
		payable = await self.get_payable(session, tenant_id, payable_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "status" and value is not None and value != payable.status:
				self._validate_payable_status(payable.status, value)
			setattr(payable, key, value)
		return await repository.update_payable(session, payable)

	async def pay_payable(
		self, session: AsyncSession, tenant_id: UUID, payable_id: UUID
	) -> Payable:
		payable = await self.get_payable(session, tenant_id, payable_id)
		if payable.status != PayableStatus.paid:
			self._validate_payable_status(payable.status, PayableStatus.paid)
		payable.status = PayableStatus.paid
		payable.paid_at = datetime.now(timezone.utc)
		return await repository.update_payable(session, payable)

	async def list_receivables(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: ReceivableFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Receivable]:
		return await repository.list_receivables(
			session, tenant_id, filters, page, page_size, sort
		)

	async def create_receivable(
		self, session: AsyncSession, tenant_id: UUID, data: ReceivableCreateRequest
	) -> Receivable:
		# Validate FKs belong to same tenant
		await validate_fk_same_tenant(
			session, Company, data.company_id, tenant_id, "company_id"
		)
		await validate_fk_same_tenant(
			session, Account, data.account_id, tenant_id, "account_id"
		)
		
		receivable = Receivable(tenant_id=tenant_id, **data.model_dump())
		return await repository.create_receivable(session, receivable)

	async def get_receivable(
		self, session: AsyncSession, tenant_id: UUID, receivable_id: UUID
	) -> Receivable:
		receivable = await repository.get_receivable(session, tenant_id, receivable_id)
		if not receivable:
			raise not_found("Receivable not found")
		return receivable

	async def update_receivable(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		receivable_id: UUID,
		data: ReceivableUpdateRequest,
	) -> Receivable:
		receivable = await self.get_receivable(session, tenant_id, receivable_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "status" and value is not None and value != receivable.status:
				self._validate_receivable_status(receivable.status, value)
			setattr(receivable, key, value)
		return await repository.update_receivable(session, receivable)

	async def confirm_receivable(
		self, session: AsyncSession, tenant_id: UUID, receivable_id: UUID
	) -> Receivable:
		receivable = await self.get_receivable(session, tenant_id, receivable_id)
		if receivable.status != ReceivableStatus.confirmed:
			self._validate_receivable_status(receivable.status, ReceivableStatus.confirmed)
		receivable.status = ReceivableStatus.confirmed
		receivable.received_at = datetime.now(timezone.utc)
		return await repository.update_receivable(session, receivable)

	def _validate_company_status(
		self, current_status: CompanyStatus, new_status: CompanyStatus
	) -> None:
		allowed = VALID_COMPANY_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	def _validate_account_status(
		self, current_status: AccountStatus, new_status: AccountStatus
	) -> None:
		allowed = VALID_ACCOUNT_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	def _validate_payment_status(
		self, current_status: PaymentStatus, new_status: PaymentStatus
	) -> None:
		allowed = VALID_PAYMENT_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	def _validate_payable_status(
		self, current_status: PayableStatus, new_status: PayableStatus
	) -> None:
		allowed = VALID_PAYABLE_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	def _validate_receivable_status(
		self, current_status: ReceivableStatus, new_status: ReceivableStatus
	) -> None:
		allowed = VALID_RECEIVABLE_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)


finance_service = FinanceService()
