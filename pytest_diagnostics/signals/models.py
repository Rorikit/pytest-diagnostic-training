from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class DiagnosticSignal:
    """Small normalized runtime observation used by diagnostic rules."""

    type: str
    value: Any
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    severity: str | None = None

    def describe(self) -> str:
        return f"{self.type}={self.value} from {self.source}"

