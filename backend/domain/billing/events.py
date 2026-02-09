"""Billing domain events."""

from uuid import UUID

from shared.events import create_event, event_bus


# Event type constants
INVOICE_CREATED = "billing.invoice.created"
INVOICE_ISSUED = "billing.invoice.issued"
INVOICE_PAID = "billing.invoice.paid"
INVOICE_OVERDUE = "billing.invoice.overdue"
INVOICE_CANCELED = "billing.invoice.canceled"


async def emit_invoice_created(tenant_id: UUID, invoice_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new invoice is created."""
    event = create_event(
        event_type=INVOICE_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"invoice_id": str(invoice_id)},
    )
    await event_bus.publish(event)


async def emit_invoice_issued(tenant_id: UUID, invoice_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when an invoice is issued."""
    event = create_event(
        event_type=INVOICE_ISSUED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"invoice_id": str(invoice_id)},
    )
    await event_bus.publish(event)


async def emit_invoice_paid(tenant_id: UUID, invoice_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when an invoice is paid."""
    event = create_event(
        event_type=INVOICE_PAID,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"invoice_id": str(invoice_id)},
    )
    await event_bus.publish(event)


async def emit_invoice_overdue(tenant_id: UUID, invoice_id: UUID) -> None:
    """Emit event when an invoice becomes overdue."""
    event = create_event(
        event_type=INVOICE_OVERDUE,
        tenant_id=tenant_id,
        actor_id=None,  # System-generated event
        data={"invoice_id": str(invoice_id)},
    )
    await event_bus.publish(event)


async def emit_invoice_canceled(tenant_id: UUID, invoice_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when an invoice is canceled."""
    event = create_event(
        event_type=INVOICE_CANCELED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"invoice_id": str(invoice_id)},
    )
    await event_bus.publish(event)

