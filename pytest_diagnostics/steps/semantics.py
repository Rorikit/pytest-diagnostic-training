from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pytest_diagnostics.signals.models import DiagnosticSignal
import pytest_diagnostics.steps.patterns as patterns


@dataclass(slots=True, frozen=True)
class StepSemanticInfo:
    title: str
    kind: str | None
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_signals(self) -> list[DiagnosticSignal]:
        signals: list[DiagnosticSignal] = []
        base_metadata = {"title": self.title}
        if self.kind is not None:
            signals.append(
                DiagnosticSignal(
                    type="step_kind",
                    value=self.kind,
                    source="step_semantics",
                    metadata=base_metadata,
                )
            )
        for key in ("endpoint", "http_method", "resource", "domain", "role", "data_entity", "http_status"):
            if key in self.metadata and self.metadata[key] is not None:
                signals.append(
                    DiagnosticSignal(
                        type=key,
                        value=self.metadata[key],
                        source="step_semantics",
                        metadata=base_metadata,
                    )
                )
        compared_sources = self.metadata.get("compared_sources")
        if compared_sources:
            signals.append(
                DiagnosticSignal(
                    type="compared_sources",
                    value=tuple(compared_sources),
                    source="step_semantics",
                    metadata=base_metadata,
                )
            )
        return signals


class StepSemanticAnalyzer:
    def analyze(self, title: str) -> StepSemanticInfo:
        metadata: dict[str, Any] = {}
        tags: list[str] = []
        kind = self._kind(title)

        request_match = patterns.HTTP_REQUEST_RE.search(title)
        if request_match:
            method = request_match.group("method").upper()
            endpoint = request_match.group("endpoint")
            metadata["http_method"] = method
            metadata["endpoint"] = endpoint
            metadata["domain"] = patterns.endpoint_domain(endpoint)
            metadata["resource"] = patterns.endpoint_resource(endpoint)
            tags.extend(["api", "http"])
            kind = "api_request"

        status_match = patterns.HTTP_STATUS_RE.search(title)
        if status_match:
            metadata["http_status"] = int(status_match.group("status"))

        role_match = patterns.ROLE_RE.search(title)
        if role_match:
            metadata["role"] = role_match.group("role").lower()

        entity_match = patterns.DATA_ENTITY_RE.search(title)
        if entity_match:
            metadata["data_entity"] = patterns.normalize_entity(entity_match.group("entity"))

        if patterns.AUTH_RE.search(title):
            tags.append("auth")
            kind = kind or "auth"
        if patterns.UI_RE.search(title):
            tags.append("ui")
            kind = kind or "ui"
        if patterns.COMPARISON_RE.search(title):
            tags.append("comparison")
            kind = "comparison"
        if patterns.TIMEOUT_RE.search(title):
            tags.append("timeout")
            kind = kind or "timeout"
        if patterns.DEPENDENCY_RE.search(title):
            tags.append("dependency")
            kind = kind or "dependency"
        if patterns.CACHE_RE.search(title):
            tags.append("cache")

        compared_sources = self._compared_sources(title)
        if compared_sources:
            metadata["compared_sources"] = compared_sources
            kind = "comparison"
            tags.append("comparison")
            tags.extend(compared_sources)

        return StepSemanticInfo(
            title=title,
            kind=kind,
            tags=tuple(dict.fromkeys(tags)),
            metadata=metadata,
        )

    def _kind(self, title: str) -> str | None:
        if patterns.HTTP_REQUEST_RE.search(title):
            return "api_request"
        return None

    def _compared_sources(self, title: str) -> tuple[str, ...]:
        lower = title.lower()
        sources = []
        if "api" in lower:
            sources.append("api")
        if "ui" in lower or "web" in lower:
            sources.append("ui")
        return tuple(sources) if len(sources) >= 2 else ()
