"""Finance domain events."""

from uuid import UUID

from shared.events import create_event, event_bus


# Event type constants
PAYMENT_CREATED = "finance.payment.created"
PAYMENT_CONFIRMED = "finance.payment.confirmed"
PAYMENT_FAILED = "finance.payment.failed"
RECEIVABLE_CREATED = "finance.receivable.created"
RECEIVABLE_CONFIRMED = "finance.receivable.confirmed"
RECEIVABLE_RECEIVED = "finance.receivable.received"
PAYABLE_CREATED = "finance.payable.created"
PAYABLE_APPROVED = "finance.payable.approved"
PAYABLE_PAID = "finance.payable.paid"
RECONCILIATION_COMPLETED = "finance.reconciliation.completed"
COMPANY_CREATED = "finance.company.created"
ACCOUNT_CREATED = "finance.account.created"


async def emit_payment_created(tenant_id: UUID, payment_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new payment is created."""
    event = create_event(
        event_type=PAYMENT_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"payment_id": str(payment_id)},
    )
    await event_bus.publish(event)


async def emit_payment_confirmed(tenant_id: UUID, payment_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a payment is confirmed."""
    event = create_event(
        event_type=PAYMENT_CONFIRMED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"payment_id": str(payment_id)},
    )
    await event_bus.publish(event)


async def emit_payment_failed(tenant_id: UUID, payment_id: UUID, reason: str, actor_id: UUID | None = None) -> None:
    """Emit event when a payment fails."""
    event = create_event(
        event_type=PAYMENT_FAILED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"payment_id": str(payment_id), "reason": reason},
    )
    await event_bus.publish(event)


async def emit_receivable_created(tenant_id: UUID, receivable_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new receivable is created."""
    event = create_event(
        event_type=RECEIVABLE_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"receivable_id": str(receivable_id)},
    )
    await event_bus.publish(event)


async def emit_receivable_confirmed(tenant_id: UUID, receivable_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a receivable is confirmed."""
    event = create_event(
        event_type=RECEIVABLE_CONFIRMED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"receivable_id": str(receivable_id)},
    )
    await event_bus.publish(event)


async def emit_receivable_received(tenant_id: UUID, receivable_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a receivable is received."""
    event = create_event(
        event_type=RECEIVABLE_RECEIVED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"receivable_id": str(receivable_id)},
    )
    await event_bus.publish(event)


async def emit_payable_created(tenant_id: UUID, payable_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new payable is created."""
    event = create_event(
        event_type=PAYABLE_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"payable_id": str(payable_id)},
    )
    await event_bus.publish(event)


async def emit_payable_approved(tenant_id: UUID, payable_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a payable is approved."""
    event = create_event(
        event_type=PAYABLE_APPROVED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"payable_id": str(payable_id)},
    )
    await event_bus.publish(event)


async def emit_payable_paid(tenant_id: UUID, payable_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a payable is paid."""
    event = create_event(
        event_type=PAYABLE_PAID,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"payable_id": str(payable_id)},
    )
    await event_bus.publish(event)


async def emit_reconciliation_completed(
    tenant_id: UUID,
    account_id: UUID,
    reconciled_count: int,
    actor_id: UUID | None = None
) -> None:
    """Emit event when bank reconciliation is completed."""
    event = create_event(
        event_type=RECONCILIATION_COMPLETED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "account_id": str(account_id),
            "reconciled_count": reconciled_count,
        },
    )
    await event_bus.publish(event)


async def emit_company_created(tenant_id: UUID, company_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new company is created."""
    event = create_event(
        event_type=COMPANY_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"company_id": str(company_id)},
    )
    await event_bus.publish(event)


async def emit_account_created(tenant_id: UUID, account_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new account is created."""
    event = create_event(
        event_type=ACCOUNT_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"account_id": str(account_id)},
    )
    await event_bus.publish(event)

