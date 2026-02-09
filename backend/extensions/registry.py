"""Extension registry."""

from collections import defaultdict
from typing import Callable

from extensions.base import Extension


class ExtensionRegistry:
    def __init__(self) -> None:
        self._extensions: dict[str, Extension] = {}
        self._event_handlers: dict[str, list[Callable]] = defaultdict(list)

    def register(self, extension: Extension) -> None:
        extension_id = extension.get_id()
        self._extensions[extension_id] = extension
        for event_name, handler in extension.get_event_handlers().items():
            self._event_handlers[event_name].append(handler)

    def get(self, extension_id: str) -> Extension | None:
        return self._extensions.get(extension_id)

    def list_all(self) -> list[Extension]:
        return list(self._extensions.values())

    def get_event_handlers(self, event_name: str) -> list[Callable]:
        return list(self._event_handlers.get(event_name, []))


registry = ExtensionRegistry()
