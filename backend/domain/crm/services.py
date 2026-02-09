"""CRM business rules."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.crm import repository
from domain.crm.models import Client, ClientStatus, Lead, LeadStatus
from domain.crm.schemas import (
	ClientCreateRequest,
	ClientFilters,
	ClientUpdateRequest,
	LeadCreateRequest,
	LeadFilters,
	LeadUpdateRequest,
)
from domain.crm import events
from shared.exceptions import conflict, not_found, validation_error
from shared.pagination import PaginatedResponse


# State transition rules
VALID_CLIENT_STATUS_TRANSITIONS = {
	ClientStatus.active: {ClientStatus.inactive},
	ClientStatus.inactive: {ClientStatus.active},
}

VALID_LEAD_STATUS_TRANSITIONS = {
	LeadStatus.new: {LeadStatus.contacted, LeadStatus.disqualified},
	LeadStatus.contacted: {LeadStatus.qualified, LeadStatus.disqualified},
	LeadStatus.qualified: {LeadStatus.converted, LeadStatus.disqualified},
	LeadStatus.disqualified: set(),  # Terminal state
	LeadStatus.converted: set(),  # Terminal state
}


class CrmService:
	# ====================
	# Client methods
	# ====================
	
	async def list_clients(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: ClientFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Client]:
		"""List clients with pagination and filtering."""
		return await repository.list_clients(session, tenant_id, filters, page, page_size, sort)

	async def create_client(
		self, session: AsyncSession, tenant_id: UUID, data: ClientCreateRequest, actor_id: UUID | None = None
	) -> Client:
		"""Create a new client."""
		client = Client(tenant_id=tenant_id, **data.model_dump())
		client = await repository.create_client(session, client)
		
		# Emit event
		await events.emit_client_created(tenant_id, client.id, actor_id)
		
		return client

	async def get_client(
		self, session: AsyncSession, tenant_id: UUID, client_id: UUID
	) -> Client:
		"""Get a client by ID."""
		client = await repository.get_client(session, tenant_id, client_id)
		if not client:
			raise not_found("Client not found")
		return client

	async def update_client(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		client_id: UUID,
		data: ClientUpdateRequest,
		actor_id: UUID | None = None,
	) -> Client:
		"""Update a client with state transition validation."""
		client = await self.get_client(session, tenant_id, client_id)
		
		old_status = client.status
		
		# Validate status transition if status is being changed
		if data.status is not None and data.status != client.status:
			self._validate_client_status_transition(client.status, data.status)
		
		# Apply updates
		for key, value in data.model_dump(exclude_unset=True).items():
			setattr(client, key, value)
		
		client = await repository.update_client(session, client)
		
		# Emit event if status changed
		if data.status is not None and data.status != old_status:
			await events.emit_client_status_changed(tenant_id, client.id, old_status.value, data.status.value, actor_id)
		
		return client

	async def delete_client(
		self, session: AsyncSession, tenant_id: UUID, client_id: UUID
	) -> None:
		"""Soft-delete a client."""
		client = await self.get_client(session, tenant_id, client_id)
		await repository.soft_delete_client(session, client)

	def _validate_client_status_transition(
		self, current_status: ClientStatus, new_status: ClientStatus
	) -> None:
		"""Validate client status transition."""
		allowed_transitions = VALID_CLIENT_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed_transitions:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	# ====================
	# Lead methods
	# ====================

	async def list_leads(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: LeadFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Lead]:
		"""List leads with pagination and filtering."""
		return await repository.list_leads(session, tenant_id, filters, page, page_size, sort)

	async def create_lead(
		self, session: AsyncSession, tenant_id: UUID, data: LeadCreateRequest, actor_id: UUID | None = None
	) -> Lead:
		"""Create a new lead."""
		lead = Lead(tenant_id=tenant_id, **data.model_dump())
		lead = await repository.create_lead(session, lead)
		
		# Emit event
		await events.emit_lead_created(tenant_id, lead.id, actor_id)
		
		return lead

	async def get_lead(
		self, session: AsyncSession, tenant_id: UUID, lead_id: UUID
	) -> Lead:
		"""Get a lead by ID."""
		lead = await repository.get_lead(session, tenant_id, lead_id)
		if not lead:
			raise not_found("Lead not found")
		return lead

	async def update_lead(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		lead_id: UUID,
		data: LeadUpdateRequest,
		actor_id: UUID | None = None,
	) -> Lead:
		"""Update a lead with state transition validation."""
		lead = await self.get_lead(session, tenant_id, lead_id)
		
		old_status = lead.status
		
		# Validate status transition if status is being changed
		if data.status is not None and data.status != lead.status:
			self._validate_lead_status_transition(lead.status, data.status)
		
		# Apply updates
		for key, value in data.model_dump(exclude_unset=True).items():
			setattr(lead, key, value)
		
		lead = await repository.update_lead(session, lead)
		
		# Emit event if status changed
		if data.status is not None and data.status != old_status:
			await events.emit_lead_status_changed(tenant_id, lead.id, old_status.value, data.status.value, actor_id)
		
		return lead

	async def delete_lead(self, session: AsyncSession, tenant_id: UUID, lead_id: UUID) -> None:
		"""Soft-delete a lead."""
		lead = await self.get_lead(session, tenant_id, lead_id)
		await repository.soft_delete_lead(session, lead)

	def _validate_lead_status_transition(
		self, current_status: LeadStatus, new_status: LeadStatus
	) -> None:
		"""Validate lead status transition."""
		allowed_transitions = VALID_LEAD_STATUS_TRANSITIONS.get(current_status, set())
		if new_status not in allowed_transitions:
			raise validation_error(
				f"Invalid status transition from {current_status.value} to {new_status.value}"
			)

	async def convert_lead(
		self, session: AsyncSession, tenant_id: UUID, lead_id: UUID, actor_id: UUID | None = None
	) -> Client:
		"""Convert a lead to a client.
		
		Business rules:
		- Lead must not already be converted
		- Lead status transitions to 'converted'
		- New client is created with lead data
		"""
		lead = await self.get_lead(session, tenant_id, lead_id)
		
		# Validate lead is not already converted
		if lead.status == LeadStatus.converted:
			raise conflict("Lead already converted")
		
		# Validate lead can transition to converted status
		self._validate_lead_status_transition(lead.status, LeadStatus.converted)
		
		# Create client from lead data
		# Note: Client requires document field but Lead doesn't have it.
		# Business rule: document must be collected separately before conversion
		client = Client(
			tenant_id=tenant_id,
			name=lead.name,
			email=lead.email,
			phone=lead.phone,
			document="",  # Will be updated after client creation with proper document
		)
		await repository.create_client(session, client)
		
		# Update lead status to converted
		lead.status = LeadStatus.converted
		await repository.update_lead(session, lead)
		
		# Emit events
		await events.emit_client_converted(tenant_id, client.id, lead.id, actor_id)
		await events.emit_lead_status_changed(tenant_id, lead.id, LeadStatus.qualified.value, LeadStatus.converted.value, actor_id)
		
		return client


crm_service = CrmService()
