"""Billing business rules."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.billing import repository
from domain.billing.models import Invoice, InvoiceStatus
from domain.billing.schemas import InvoiceCreateRequest, InvoiceFilters, InvoiceUpdateRequest
from shared.exceptions import not_found, validation_error
from shared.pagination import PaginatedResponse


VALID_INVOICE_STATUS_TRANSITIONS = {
	InvoiceStatus.draft: {InvoiceStatus.issued, InvoiceStatus.canceled},
	InvoiceStatus.issued: {InvoiceStatus.paid, InvoiceStatus.overdue, InvoiceStatus.canceled},
	InvoiceStatus.overdue: {InvoiceStatus.paid, InvoiceStatus.canceled},
	InvoiceStatus.paid: set(),
	InvoiceStatus.canceled: set(),
}


class BillingService:
	async def list_invoices(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: InvoiceFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Invoice]:
		return await repository.list_invoices(session, tenant_id, filters, page, page_size, sort)

	async def create_invoice(
		self, session: AsyncSession, tenant_id: UUID, data: InvoiceCreateRequest
	) -> Invoice:
		invoice = Invoice(tenant_id=tenant_id, **data.model_dump())
		return await repository.create_invoice(session, invoice)

	async def get_invoice(
		self, session: AsyncSession, tenant_id: UUID, invoice_id: UUID
	) -> Invoice:
		invoice = await repository.get_invoice(session, tenant_id, invoice_id)
		if not invoice:
			raise not_found("Invoice not found")
		return invoice

	async def update_invoice(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		invoice_id: UUID,
		data: InvoiceUpdateRequest,
	) -> Invoice:
		invoice = await self.get_invoice(session, tenant_id, invoice_id)
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "status" and value is not None and value != invoice.status:
				self._validate_status_transition(invoice.status, value)
			setattr(invoice, key, value)
		return await repository.update_invoice(session, invoice)

	async def mark_paid(
		self, session: AsyncSession, tenant_id: UUID, invoice_id: UUID
	) -> Invoice:
		invoice = await self.get_invoice(session, tenant_id, invoice_id)
		if invoice.status != InvoiceStatus.paid:
			self._validate_status_transition(invoice.status, InvoiceStatus.paid)
		invoice.status = InvoiceStatus.paid
		return await repository.update_invoice(session, invoice)

	def _validate_status_transition(
		self, current_status: InvoiceStatus, new_status: InvoiceStatus
	) -> None:
		allowed = VALID_INVOICE_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)


billing_service = BillingService()
