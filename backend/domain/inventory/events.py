"""Inventory domain events."""

from uuid import UUID

from shared.events import create_event, event_bus


# Event type constants
ITEM_CREATED = "inventory.item.created"
ITEM_STATUS_CHANGED = "inventory.item.status_changed"
STOCK_ADJUSTED = "inventory.stock.adjusted"
STOCK_LOW = "inventory.stock.low"


async def emit_item_created(tenant_id: UUID, item_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new item is created."""
    event = create_event(
        event_type=ITEM_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"item_id": str(item_id)},
    )
    await event_bus.publish(event)


async def emit_item_status_changed(
    tenant_id: UUID,
    item_id: UUID,
    old_status: str,
    new_status: str,
    actor_id: UUID | None = None
) -> None:
    """Emit event when item status changes."""
    event = create_event(
        event_type=ITEM_STATUS_CHANGED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "item_id": str(item_id),
            "old_status": old_status,
            "new_status": new_status,
        },
    )
    await event_bus.publish(event)


async def emit_stock_adjusted(
    tenant_id: UUID,
    item_id: UUID,
    adjustment_id: UUID,
    delta: int,
    reason: str,
    actor_id: UUID | None = None
) -> None:
    """Emit event when stock is adjusted."""
    event = create_event(
        event_type=STOCK_ADJUSTED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "item_id": str(item_id),
            "adjustment_id": str(adjustment_id),
            "delta": delta,
            "reason": reason,
        },
    )
    await event_bus.publish(event)


async def emit_stock_low(tenant_id: UUID, item_id: UUID, current_quantity: int, threshold: int) -> None:
    """Emit event when stock falls below threshold."""
    event = create_event(
        event_type=STOCK_LOW,
        tenant_id=tenant_id,
        actor_id=None,  # System-generated event
        data={
            "item_id": str(item_id),
            "current_quantity": current_quantity,
            "threshold": threshold,
        },
    )
    await event_bus.publish(event)

