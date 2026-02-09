"""Sales ORM models."""

from enum import Enum

from sqlalchemy import Enum as SqlEnum, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared import Base, IdMixin, TenantMixin, TimestampMixin


class OpportunityStage(str, Enum):
	prospecting = "prospecting"
	proposal = "proposal"
	negotiation = "negotiation"
	won = "won"
	lost = "lost"


class Opportunity(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "sales_opportunities"

	title: Mapped[str] = mapped_column(String, nullable=False)
	client_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
	currency: Mapped[str] = mapped_column(String, nullable=False, default="BRL")
	stage: Mapped[OpportunityStage] = mapped_column(
		SqlEnum(OpportunityStage), default=OpportunityStage.prospecting, nullable=False
	)
