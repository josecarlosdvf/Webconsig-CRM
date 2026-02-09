"""WebSocket endpoint for real-time event streaming."""

import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.responses import JSONResponse

from dependencies import get_tenant_id
from shared.events import event_bus


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ws", tags=["websocket"])


@router.websocket("/{tenant_id}")
async def websocket_endpoint(websocket: WebSocket, tenant_id: UUID):
    """
    WebSocket endpoint for real-time event streaming.
    
    URL: wss://{host}/api/v1/ws/{tenant_id}
    
    Clients connect with their tenant_id and receive all events published
    for that tenant in real-time.
    
    Authentication should be handled via query params or headers in production.
    """
    await websocket.accept()
    
    # Register websocket connection
    event_bus.register_websocket(tenant_id, websocket)
    logger.info(f"WebSocket connected for tenant {tenant_id}")
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for messages from client (ping/pong, etc.)
            data = await websocket.receive_text()
            
            # Echo back for testing (can be removed in production)
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for tenant {tenant_id}")
    except Exception as e:
        logger.error(f"WebSocket error for tenant {tenant_id}: {e}", exc_info=True)
    finally:
        # Unregister websocket connection
        event_bus.unregister_websocket(tenant_id, websocket)
        logger.info(f"WebSocket cleaned up for tenant {tenant_id}")


@router.get("/health")
async def websocket_health():
    """Health check endpoint for WebSocket service."""
    return {"status": "ok", "service": "websocket"}
