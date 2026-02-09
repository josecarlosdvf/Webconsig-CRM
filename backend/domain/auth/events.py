"""Auth domain events."""

from uuid import UUID

from shared.events import create_event, event_bus


# Event type constants
USER_CREATED = "auth.user.created"
USER_STATUS_CHANGED = "auth.user.status_changed"
USER_PASSWORD_CHANGED = "auth.user.password_changed"
USER_LOGIN = "auth.user.login"
USER_LOGOUT = "auth.user.logout"
USER_LOGIN_FAILED = "auth.user.login_failed"
ROLE_CREATED = "auth.role.created"
ROLE_ASSIGNED = "auth.role.assigned"
ROLE_REVOKED = "auth.role.revoked"


async def emit_user_created(tenant_id: UUID, user_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new user is created."""
    event = create_event(
        event_type=USER_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"user_id": str(user_id)},
    )
    await event_bus.publish(event)


async def emit_user_status_changed(
    tenant_id: UUID,
    user_id: UUID,
    old_status: str,
    new_status: str,
    actor_id: UUID | None = None
) -> None:
    """Emit event when user status changes."""
    event = create_event(
        event_type=USER_STATUS_CHANGED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "user_id": str(user_id),
            "old_status": old_status,
            "new_status": new_status,
        },
    )
    await event_bus.publish(event)


async def emit_user_password_changed(tenant_id: UUID, user_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when user password is changed."""
    event = create_event(
        event_type=USER_PASSWORD_CHANGED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"user_id": str(user_id)},
    )
    await event_bus.publish(event)


async def emit_user_login(tenant_id: UUID, user_id: UUID, ip_address: str | None = None) -> None:
    """Emit event when user logs in."""
    event = create_event(
        event_type=USER_LOGIN,
        tenant_id=tenant_id,
        actor_id=user_id,
        data={
            "user_id": str(user_id),
            "ip_address": ip_address,
        },
    )
    await event_bus.publish(event)


async def emit_user_logout(tenant_id: UUID, user_id: UUID) -> None:
    """Emit event when user logs out."""
    event = create_event(
        event_type=USER_LOGOUT,
        tenant_id=tenant_id,
        actor_id=user_id,
        data={"user_id": str(user_id)},
    )
    await event_bus.publish(event)


async def emit_user_login_failed(tenant_id: UUID, username: str, ip_address: str | None = None) -> None:
    """Emit event when login attempt fails."""
    event = create_event(
        event_type=USER_LOGIN_FAILED,
        tenant_id=tenant_id,
        actor_id=None,
        data={
            "username": username,
            "ip_address": ip_address,
        },
    )
    await event_bus.publish(event)


async def emit_role_created(tenant_id: UUID, role_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a new role is created."""
    event = create_event(
        event_type=ROLE_CREATED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={"role_id": str(role_id)},
    )
    await event_bus.publish(event)


async def emit_role_assigned(tenant_id: UUID, user_id: UUID, role_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a role is assigned to a user."""
    event = create_event(
        event_type=ROLE_ASSIGNED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "user_id": str(user_id),
            "role_id": str(role_id),
        },
    )
    await event_bus.publish(event)


async def emit_role_revoked(tenant_id: UUID, user_id: UUID, role_id: UUID, actor_id: UUID | None = None) -> None:
    """Emit event when a role is revoked from a user."""
    event = create_event(
        event_type=ROLE_REVOKED,
        tenant_id=tenant_id,
        actor_id=actor_id,
        data={
            "user_id": str(user_id),
            "role_id": str(role_id),
        },
    )
    await event_bus.publish(event)

