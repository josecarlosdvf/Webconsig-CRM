"""Inventory ORM models."""

from enum import Enum

from sqlalchemy import Enum as SqlEnum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared import Base, IdMixin, TenantMixin, TimestampMixin


class ItemStatus(str, Enum):
	active = "active"
	inactive = "inactive"


class ItemUnit(str, Enum):
	unit = "unit"
	kg = "kg"
	g = "g"
	l = "l"
	ml = "ml"
	m = "m"
	cm = "cm"


class Item(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "inventory_items"

	sku: Mapped[str] = mapped_column(String, nullable=False)
	name: Mapped[str] = mapped_column(String, nullable=False)
	unit: Mapped[ItemUnit] = mapped_column(SqlEnum(ItemUnit), nullable=False)
	status: Mapped[ItemStatus] = mapped_column(
		SqlEnum(ItemStatus), default=ItemStatus.active, nullable=False
	)


class StockAdjustment(Base, IdMixin, TenantMixin, TimestampMixin):
	__tablename__ = "inventory_stock_adjustments"

	item_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	reason: Mapped[str] = mapped_column(String, nullable=False)
