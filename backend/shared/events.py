"""Event bus for domain events with WebSocket and Webhook dispatching."""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class Event(BaseModel):
    """Base event structure following OpenAPI spec."""
    
    id: UUID = Field(default_factory=uuid4)
    type: str
    version: int = 1
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: UUID
    idempotency_key: str
    actor: Dict[str, Any] = Field(default_factory=dict)
    source: str = "api"
    trace_id: str | None = None
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=lambda: {"schema_version": 1})


class EventBus:
    """
    Event bus for publishing and subscribing to domain events.
    
    Features:
    - In-memory pub/sub for synchronous handlers
    - WebSocket broadcasting for real-time updates
    - Webhook dispatching for external integrations
    - Event deduplication via idempotency_key
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._websocket_connections: Dict[UUID, List[Any]] = {}  # tenant_id -> [websockets]
        self._webhook_urls: Dict[UUID, str] = {}  # tenant_id -> webhook_url
        self._processed_events: set = set()  # idempotency_key cache
        
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe a handler to an event type.
        
        Args:
            event_type: Event type pattern (e.g., "crm.lead.created", "sales.*")
            handler: Async callable that receives Event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type}")
        
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            
    async def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers, WebSocket connections, and webhooks.
        
        Args:
            event: Event to publish
        """
        # Deduplicate by idempotency_key
        if event.idempotency_key in self._processed_events:
            logger.debug(f"Skipping duplicate event {event.idempotency_key}")
            return
            
        self._processed_events.add(event.idempotency_key)
        
        # Log event
        logger.info(f"Publishing event {event.type} (id={event.id}, tenant={event.tenant_id})")
        
        # Execute synchronous handlers
        await self._execute_handlers(event)
        
        # Broadcast to WebSocket connections
        await self._broadcast_websocket(event)
        
        # Dispatch to webhook
        await self._dispatch_webhook(event)
        
    async def _execute_handlers(self, event: Event) -> None:
        """Execute all registered handlers for the event type."""
        # Exact match handlers
        handlers = self._handlers.get(event.type, [])
        
        # Wildcard handlers (e.g., "crm.*")
        domain = event.type.split(".")[0]
        wildcard_pattern = f"{domain}.*"
        handlers.extend(self._handlers.get(wildcard_pattern, []))
        
        # Execute all handlers concurrently
        if handlers:
            await asyncio.gather(
                *[self._safe_execute_handler(handler, event) for handler in handlers],
                return_exceptions=True
            )
            
    async def _safe_execute_handler(self, handler: Callable, event: Event) -> None:
        """Execute handler with error handling."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error executing handler for {event.type}: {e}", exc_info=True)
            
    async def _broadcast_websocket(self, event: Event) -> None:
        """Broadcast event to WebSocket connections for the tenant."""
        connections = self._websocket_connections.get(event.tenant_id, [])
        if not connections:
            return
            
        # Serialize event
        payload = json.dumps(event.model_dump(mode="json"), default=str)
        
        # Send to all connections concurrently
        await asyncio.gather(
            *[self._send_websocket(ws, payload) for ws in connections],
            return_exceptions=True
        )
        
    async def _send_websocket(self, websocket: Any, payload: str) -> None:
        """Send event to a WebSocket connection with error handling."""
        try:
            await websocket.send_text(payload)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            # TODO: Remove closed connections from registry
            
    async def _dispatch_webhook(self, event: Event) -> None:
        """Dispatch event to webhook URL for the tenant."""
        webhook_url = self._webhook_urls.get(event.tenant_id)
        if not webhook_url:
            return
            
        # TODO: Implement webhook dispatch with retry logic
        # For now, this is a placeholder
        logger.info(f"Would dispatch webhook to {webhook_url} for event {event.type}")
        
    def register_websocket(self, tenant_id: UUID, websocket: Any) -> None:
        """Register a WebSocket connection for a tenant."""
        if tenant_id not in self._websocket_connections:
            self._websocket_connections[tenant_id] = []
        self._websocket_connections[tenant_id].append(websocket)
        logger.info(f"Registered WebSocket for tenant {tenant_id}")
        
    def unregister_websocket(self, tenant_id: UUID, websocket: Any) -> None:
        """Unregister a WebSocket connection for a tenant."""
        if tenant_id in self._websocket_connections:
            try:
                self._websocket_connections[tenant_id].remove(websocket)
            except ValueError:
                pass
                
    def register_webhook(self, tenant_id: UUID, webhook_url: str) -> None:
        """Register a webhook URL for a tenant."""
        self._webhook_urls[tenant_id] = webhook_url
        logger.info(f"Registered webhook for tenant {tenant_id}: {webhook_url}")
        
    def unregister_webhook(self, tenant_id: UUID) -> None:
        """Unregister webhook URL for a tenant."""
        self._webhook_urls.pop(tenant_id, None)


# Global event bus instance
event_bus = EventBus()


def create_event(
    event_type: str,
    tenant_id: UUID,
    actor_id: UUID | None = None,
    data: Dict[str, Any] | None = None,
    idempotency_key: str | None = None,
) -> Event:
    """
    Helper to create a standardized event.
    
    Args:
        event_type: Event type (e.g., "crm.lead.created")
        tenant_id: Tenant ID
        actor_id: User ID who triggered the event
        data: Event payload
        idempotency_key: Unique key for deduplication (auto-generated if not provided)
    
    Returns:
        Event instance
    """
    if idempotency_key is None:
        idempotency_key = f"{event_type}:{tenant_id}:{uuid4()}"
        
    actor = {"id": str(actor_id), "type": "user"} if actor_id else {}
    
    return Event(
        type=event_type,
        tenant_id=tenant_id,
        idempotency_key=idempotency_key,
        actor=actor,
        data=data or {},
    )

