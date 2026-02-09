"""Dynamic extension loader."""

from extensions.registry import registry


def load_extensions() -> None:
    # Placeholder for dynamic discovery from installed packages or filesystem.
    return None


def register_extension(extension) -> None:
    registry.register(extension)
