"""Cross-cutting middleware."""

import logging
import time
from typing import Callable
from uuid import UUID

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests with timing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"{request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Log response time
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} "
            f"completed in {process_time:.3f}s with status {response.status_code}"
        )
        
        return response


class TenantResolutionMiddleware(BaseHTTPMiddleware):
    """Resolve tenant_id from host/subdomain and inject into request state."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract subdomain from host
        host = request.headers.get("host", "")
        
        # Simple subdomain extraction (eg: tenant.example.com -> tenant)
        # In production, use more robust logic with domain whitelist
        if "." in host:
            subdomain = host.split(".")[0]
            # Store in request state for later use
            request.state.subdomain = subdomain
            logger.debug(f"Resolved subdomain: {subdomain}")
        
        return await call_next(request)


def configure_cors(app) -> None:
    """Configure CORS middleware with settings from environment."""
    settings = get_settings()
    
    # Parse origins (handle wildcard vs specific origins)
    origins = settings.cors_allowed_origins
    if origins == ["*"]:
        allow_origins_list = ["*"]
    else:
        # Strip whitespace from each origin
        allow_origins_list = [origin.strip() for origin in origins]
    
    # Parse methods
    methods = settings.cors_allow_methods
    if methods == ["*"]:
        allow_methods_list = ["*"]
    else:
        allow_methods_list = [method.strip().upper() for method in methods]
    
    # Parse headers
    headers = settings.cors_allow_headers
    if headers == ["*"]:
        allow_headers_list = ["*"]
    else:
        allow_headers_list = [header.strip().lower() for header in headers]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=allow_methods_list,
        allow_headers=allow_headers_list,
    )
    
    logger.info(f"CORS configured: origins={allow_origins_list}, credentials={settings.cors_allow_credentials}")


def configure_middlewares(app) -> None:
    """Configure all application middlewares."""
    # Order matters: first added = outermost layer
    configure_cors(app)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(TenantResolutionMiddleware)
