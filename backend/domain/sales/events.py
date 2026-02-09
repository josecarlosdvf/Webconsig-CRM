"""Sales domain events."""

from uuid import UUID

from shared.events import create_event, event_bus


# Event type constants
OPPORTUNITY_CREATED = "sales.opportunity.created"
OPPORTUNITY_STAGE_CHANGED = "sales.opportunity.stage_changed"
OPPORTUNITY_WON = "sales.opportunity.won"
OPPORTUNITY_LOST = "sales.opportunity.lost"


async def emit_opportunity_created(tenant_id: UUID, opportunity_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new opportunity is created."""
    event = create_event(
        event_type=OPPORTUNITY_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"opportunity_id": str(opportunity_id)},
    )
    await event_bus.publish(event)


async def emit_opportunity_stage_changed(
    tenant_id: UUID,
    opportunity_id: UUID,
    old_stage: str,
    new_stage: str,
    actor_id: UUID | None = None
) -> None:
    """Emit event when opportunity stage changes."""
    event = create_event(
        event_type=OPPORTUNITY_STAGE_CHANGED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "opportunity_id": str(opportunity_id),
            "old_stage": old_stage,
            "new_stage": new_stage,
        },
    )
    await event_bus.publish(event)
    
    # Emit specific events for won/lost
    if new_stage == "won":
        await emit_opportunity_won(tenant_id, opportunity_id, actor_id)
    elif new_stage == "lost":
        await emit_opportunity_lost(tenant_id, opportunity_id, actor_id)


async def emit_opportunity_won(tenant_id: UUID, opportunity_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when opportunity is won."""
    event = create_event(
        event_type=OPPORTUNITY_WON,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"opportunity_id": str(opportunity_id)},
    )
    await event_bus.publish(event)


async def emit_opportunity_lost(tenant_id: UUID, opportunity_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when opportunity is lost."""
    event = create_event(
        event_type=OPPORTUNITY_LOST,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"opportunity_id": str(opportunity_id)},
    )
    await event_bus.publish(event)

