"""FastAPI application entrypoint."""

from fastapi import FastAPI

import importlib

from api import audit, auth, billing, crm, extensions, finance, hr, inventory, sales

import_api = importlib.import_module("api.import")


def create_app() -> FastAPI:
    app = FastAPI(title="Webconsig CRM/ERP", version="1.0.0")

    app.include_router(crm.router)
    app.include_router(sales.router)
    app.include_router(finance.router)
    app.include_router(billing.router)
    app.include_router(inventory.router)
    app.include_router(auth.router)
    app.include_router(hr.router)
    app.include_router(audit.router)
    app.include_router(import_api.router)
    app.include_router(extensions.router)

    return app


app = create_app()
