"""CRM domain events."""

from uuid import UUID

from shared.events import create_event, event_bus, Event


# Event type constants
LEAD_CREATED = "crm.lead.created"
LEAD_STATUS_CHANGED = "crm.lead.status_changed"
CLIENT_CREATED = "crm.client.created"
CLIENT_CONVERTED = "crm.client.converted"
CLIENT_STATUS_CHANGED = "crm.client.status_changed"


async def emit_lead_created(tenant_id: UUID, lead_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new lead is created."""
    event = create_event(
        event_type=LEAD_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"lead_id": str(lead_id)},
    )
    await event_bus.publish(event)


async def emit_lead_status_changed(
    tenant_id: UUID,
    lead_id: UUID,
    old_status: str,
    new_status: str,
    actor_id: UUID | None = None
) -> None:
    """Emit event when lead status changes."""
    event = create_event(
        event_type=LEAD_STATUS_CHANGED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "lead_id": str(lead_id),
            "old_status": old_status,
            "new_status": new_status,
        },
    )
    await event_bus.publish(event)


async def emit_client_created(tenant_id: UUID, client_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new client is created."""
    event = create_event(
        event_type=CLIENT_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"client_id": str(client_id)},
    )
    await event_bus.publish(event)


async def emit_client_converted(
    tenant_id: UUID,
    client_id: UUID,
    lead_id: UUID,
    actor_id: UUID | None = None
) -> None:
    """Emit event when a lead is converted to a client."""
    event = create_event(
        event_type=CLIENT_CONVERTED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "client_id": str(client_id),
            "lead_id": str(lead_id),
        },
    )
    await event_bus.publish(event)


async def emit_client_status_changed(
    tenant_id: UUID,
    client_id: UUID,
    old_status: str,
    new_status: str,
    actor_id: UUID | None = None
) -> None:
    """Emit event when client status changes."""
    event = create_event(
        event_type=CLIENT_STATUS_CHANGED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "client_id": str(client_id),
            "old_status": old_status,
            "new_status": new_status,
        },
    )
    await event_bus.publish(event)

