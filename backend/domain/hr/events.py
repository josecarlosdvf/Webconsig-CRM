"""HR domain events."""

from uuid import UUID

from shared.events import create_event, event_bus


# Event type constants
RECRUITMENT_CREATED = "hr.recruitment.created"
RECRUITMENT_STATUS_CHANGED = "hr.recruitment.status_changed"
CANDIDATE_CREATED = "hr.candidate.created"
CANDIDATE_STAGE_CHANGED = "hr.candidate.stage_changed"
CANDIDATE_HIRED = "hr.candidate.hired"
CANDIDATE_REJECTED = "hr.candidate.rejected"
EMPLOYEE_CREATED = "hr.employee.created"
EMPLOYEE_HIRED = "hr.employee.hired"
EMPLOYEE_TERMINATED = "hr.employee.terminated"
ABSENCE_RECORDED = "hr.absence.recorded"
TIME_ENTRY_CREATED = "hr.time_entry.created"
TIME_ENTRY_APPROVED = "hr.time_entry.approved"
LEAVE_REQUESTED = "hr.leave.requested"
LEAVE_APPROVED = "hr.leave.approved"
LEAVE_REJECTED = "hr.leave.rejected"
DOCUMENT_UPLOADED = "hr.document.uploaded"
CONTRACT_CREATED = "hr.contract.created"
CONTRACT_ENDED = "hr.contract.ended"
BENEFIT_CREATED = "hr.benefit.created"
BENEFIT_ASSIGNED = "hr.benefit.assigned"


async def emit_recruitment_created(tenant_id: UUID, recruitment_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new recruitment is created."""
    event = create_event(
        event_type=RECRUITMENT_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"recruitment_id": str(recruitment_id)},
    )
    await event_bus.publish(event)


async def emit_recruitment_status_changed(
    tenant_id: UUID,
    recruitment_id: UUID,
    old_status: str,
    new_status: str,
    actor_id: UUID | None = None
) -> None:
    """Emit event when recruitment status changes."""
    event = create_event(
        event_type=RECRUITMENT_STATUS_CHANGED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "recruitment_id": str(recruitment_id),
            "old_status": old_status,
            "new_status": new_status,
        },
    )
    await event_bus.publish(event)


async def emit_candidate_created(tenant_id: UUID, candidate_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new candidate is created."""
    event = create_event(
        event_type=CANDIDATE_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"candidate_id": str(candidate_id)},
    )
    await event_bus.publish(event)


async def emit_candidate_stage_changed(
    tenant_id: UUID,
    candidate_id: UUID,
    old_stage: str,
    new_stage: str,
    actor_id: UUID | None = None
) -> None:
    """Emit event when candidate stage changes."""
    event = create_event(
        event_type=CANDIDATE_STAGE_CHANGED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "candidate_id": str(candidate_id),
            "old_stage": old_stage,
            "new_stage": new_stage,
        },
    )
    await event_bus.publish(event)
    
    # Emit specific events
    if new_stage == "hired":
        await emit_candidate_hired(tenant_id, candidate_id, actor_id)
    elif new_stage == "rejected":
        await emit_candidate_rejected(tenant_id, candidate_id, actor_id)


async def emit_candidate_hired(tenant_id: UUID, candidate_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a candidate is hired."""
    event = create_event(
        event_type=CANDIDATE_HIRED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"candidate_id": str(candidate_id)},
    )
    await event_bus.publish(event)


async def emit_candidate_rejected(tenant_id: UUID, candidate_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a candidate is rejected."""
    event = create_event(
        event_type=CANDIDATE_REJECTED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"candidate_id": str(candidate_id)},
    )
    await event_bus.publish(event)


async def emit_employee_created(tenant_id: UUID, employee_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new employee is created."""
    event = create_event(
        event_type=EMPLOYEE_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"employee_id": str(employee_id)},
    )
    await event_bus.publish(event)


async def emit_employee_hired(tenant_id: UUID, employee_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when an employee is hired."""
    event = create_event(
        event_type=EMPLOYEE_HIRED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"employee_id": str(employee_id)},
    )
    await event_bus.publish(event)


async def emit_employee_terminated(
    tenant_id: UUID,
    employee_id: UUID,
    reason: str,
    actor_id: UUID | None = None
) -> None:
    """Emit event when an employee is terminated."""
    event = create_event(
        event_type=EMPLOYEE_TERMINATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "employee_id": str(employee_id),
            "reason": reason,
        },
    )
    await event_bus.publish(event)


async def emit_absence_recorded(tenant_id: UUID, absence_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when an absence is recorded."""
    event = create_event(
        event_type=ABSENCE_RECORDED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"absence_id": str(absence_id)},
    )
    await event_bus.publish(event)


async def emit_time_entry_created(tenant_id: UUID, time_entry_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a time entry is created."""
    event = create_event(
        event_type=TIME_ENTRY_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"time_entry_id": str(time_entry_id)},
    )
    await event_bus.publish(event)


async def emit_time_entry_approved(tenant_id: UUID, time_entry_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a time entry is approved."""
    event = create_event(
        event_type=TIME_ENTRY_APPROVED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"time_entry_id": str(time_entry_id)},
    )
    await event_bus.publish(event)


async def emit_leave_requested(tenant_id: UUID, leave_request_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a leave is requested."""
    event = create_event(
        event_type=LEAVE_REQUESTED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"leave_request_id": str(leave_request_id)},
    )
    await event_bus.publish(event)


async def emit_leave_approved(tenant_id: UUID, leave_request_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a leave is approved."""
    event = create_event(
        event_type=LEAVE_APPROVED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"leave_request_id": str(leave_request_id)},
    )
    await event_bus.publish(event)


async def emit_leave_rejected(tenant_id: UUID, leave_request_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a leave is rejected."""
    event = create_event(
        event_type=LEAVE_REJECTED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"leave_request_id": str(leave_request_id)},
    )
    await event_bus.publish(event)


async def emit_document_uploaded(
    tenant_id: UUID,
    document_id: UUID,
    employee_id: UUID,
    document_type: str,
    actor_id: UUID | None = None
) -> None:
    """Emit event when a document is uploaded."""
    event = create_event(
        event_type=DOCUMENT_UPLOADED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "document_id": str(document_id),
            "employee_id": str(employee_id),
            "document_type": document_type,
        },
    )
    await event_bus.publish(event)


async def emit_contract_created(tenant_id: UUID, contract_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a contract is created."""
    event = create_event(
        event_type=CONTRACT_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"contract_id": str(contract_id)},
    )
    await event_bus.publish(event)


async def emit_contract_ended(tenant_id: UUID, contract_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a contract ends."""
    event = create_event(
        event_type=CONTRACT_ENDED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"contract_id": str(contract_id)},
    )
    await event_bus.publish(event)


async def emit_benefit_created(tenant_id: UUID, benefit_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a benefit is created."""
    event = create_event(
        event_type=BENEFIT_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"benefit_id": str(benefit_id)},
    )
    await event_bus.publish(event)


async def emit_benefit_assigned(
    tenant_id: UUID,
    benefit_id: UUID,
    employee_id: UUID,
    actor_id: UUID | None = None
) -> None:
    """Emit event when a benefit is assigned to an employee."""
    event = create_event(
        event_type=BENEFIT_ASSIGNED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "benefit_id": str(benefit_id),
            "employee_id": str(employee_id),
        },
    )
    await event_bus.publish(event)

