"""CRM ORM models."""

from enum import Enum

from sqlalchemy import Enum as SqlEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from shared import Base, IdMixin, TenantMixin, TimestampMixin


class ClientStatus(str, Enum):
	active = "active"
	inactive = "inactive"


class LeadStatus(str, Enum):
	new = "new"
	contacted = "contacted"
	qualified = "qualified"
	disqualified = "disqualified"
	converted = "converted"


class Client(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "crm_clients"

	name: Mapped[str] = mapped_column(String, nullable=False)
	email: Mapped[str] = mapped_column(String, nullable=False)
	phone: Mapped[str] = mapped_column(String, nullable=False)
	document: Mapped[str] = mapped_column(String, nullable=False)
	status: Mapped[ClientStatus] = mapped_column(
		SqlEnum(ClientStatus), default=ClientStatus.active, nullable=False
	)


class Lead(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "crm_leads"

	name: Mapped[str] = mapped_column(String, nullable=False)
	email: Mapped[str] = mapped_column(String, nullable=False)
	phone: Mapped[str] = mapped_column(String, nullable=False)
	source: Mapped[str] = mapped_column(String, nullable=False)
	status: Mapped[LeadStatus] = mapped_column(
		SqlEnum(LeadStatus), default=LeadStatus.new, nullable=False
	)
