"""Extension base class (placeholder)."""

from abc import ABC, abstractmethod

from fastapi import APIRouter


class Extension(ABC):
    @abstractmethod
    def get_id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_router(self) -> APIRouter:
        raise NotImplementedError

    async def on_activate(self, tenant_id, db) -> None:
        return None

    async def on_deactivate(self, tenant_id, db) -> None:
        return None

    def get_event_handlers(self) -> dict:
        return {}
