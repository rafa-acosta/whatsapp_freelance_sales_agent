"""Secret handling (R-007). Secret values never appear in repr(), str(), or logs."""

from __future__ import annotations

_REGISTRY: list["SecretValue"] = []


class SecretValue:
    """Wraps a secret so that printing or logging it shows only a mask."""

    __slots__ = ("_value",)

    def __init__(self, value: str):
        self._value = value or ""
        _REGISTRY.append(self)

    def get(self) -> str:
        """Return the raw value. Call only where the secret is used."""
        return self._value

    def __repr__(self) -> str:
        return "<SecretValue ***>"

    def __str__(self) -> str:
        return "***"

    def __bool__(self) -> bool:
        return bool(self._value)


def registered_secret_values() -> list[str]:
    """Raw values of every SecretValue created in this process, for the log filter."""
    return [s.get() for s in _REGISTRY if s.get()]
