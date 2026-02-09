"""Sales business rules."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.sales import repository
from domain.sales.models import Opportunity, OpportunityStage
from domain.sales.schemas import (
	OpportunityCreateRequest,
	OpportunityFilters,
	OpportunityUpdateRequest,
)
from domain.crm.models import Client
from shared.exceptions import not_found, validation_error
from shared.pagination import PaginatedResponse
from shared.validators import validate_fk_same_tenant


VALID_OPPORTUNITY_STAGE_TRANSITIONS = {
	OpportunityStage.prospecting: {OpportunityStage.proposal, OpportunityStage.lost},
	OpportunityStage.proposal: {OpportunityStage.negotiation, OpportunityStage.lost},
	OpportunityStage.negotiation: {OpportunityStage.won, OpportunityStage.lost},
	OpportunityStage.won: set(),
	OpportunityStage.lost: set(),
}


class SalesService:
	async def list_opportunities(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		filters: OpportunityFilters,
		page: int,
		page_size: int,
		sort: str | None = None,
	) -> PaginatedResponse[Opportunity]:
		return await repository.list_opportunities(
			session, tenant_id, filters, page, page_size, sort
		)

	async def create_opportunity(
		self, session: AsyncSession, tenant_id: UUID, data: OpportunityCreateRequest
	) -> Opportunity:
		# Validate client belongs to same tenant
		await validate_fk_same_tenant(
			session, Client, data.client_id, tenant_id, "client_id"
		)
		
		opportunity = Opportunity(tenant_id=tenant_id, **data.model_dump())
		return await repository.create_opportunity(session, opportunity)

	async def get_opportunity(
		self, session: AsyncSession, tenant_id: UUID, opportunity_id: UUID
	) -> Opportunity:
		opportunity = await repository.get_opportunity(session, tenant_id, opportunity_id)
		if not opportunity:
			raise not_found("Opportunity not found")
		return opportunity

	async def update_opportunity(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		opportunity_id: UUID,
		data: OpportunityUpdateRequest,
	) -> Opportunity:
		opportunity = await self.get_opportunity(session, tenant_id, opportunity_id)
		
		# Validate client_id if being updated
		if data.client_id is not None:
			await validate_fk_same_tenant(
				session, Client, data.client_id, tenant_id, "client_id"
			)
		
		for key, value in data.model_dump(exclude_unset=True).items():
			if key == "stage" and value is not None and value != opportunity.stage:
				self._validate_stage_transition(opportunity.stage, value)
			setattr(opportunity, key, value)
		return await repository.update_opportunity(session, opportunity)

	async def delete_opportunity(
		self, session: AsyncSession, tenant_id: UUID, opportunity_id: UUID
	) -> None:
		opportunity = await self.get_opportunity(session, tenant_id, opportunity_id)
		await repository.soft_delete_opportunity(session, opportunity)

	async def change_stage(
		self,
		session: AsyncSession,
		tenant_id: UUID,
		opportunity_id: UUID,
		stage: OpportunityStage,
	) -> Opportunity:
		opportunity = await self.get_opportunity(session, tenant_id, opportunity_id)
		if stage != opportunity.stage:
			self._validate_stage_transition(opportunity.stage, stage)
		opportunity.stage = stage
		return await repository.update_opportunity(session, opportunity)

	def _validate_stage_transition(
		self, current_stage: OpportunityStage, new_stage: OpportunityStage
	) -> None:
		allowed = VALID_OPPORTUNITY_STAGE_TRANSITIONS.get(current_stage, set())
		if new_stage not in allowed:
			raise validation_error(
				f"Invalid stage transition from {current_stage.value} to {new_stage.value}"
			)


sales_service = SalesService()
