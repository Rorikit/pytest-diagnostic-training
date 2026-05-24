from __future__ import annotations

from dataclasses import dataclass, field

from pytest_diagnostics.signals.models import DiagnosticSignal


@dataclass(slots=True, frozen=True)
class DiagnosticFinding:
    area: str
    title: str
    explanation: str
    confidence: float
    facts: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    recommended_checks: list[str] = field(default_factory=list)
    rule_name: str = "unknown"


@dataclass(slots=True, frozen=True)
class DiagnosticSummary:
    findings: list[DiagnosticFinding]
    raw_signals: list[DiagnosticSignal]

    @property
    def top_finding(self) -> DiagnosticFinding | None:
        if not self.findings:
            return None
        return self.findings[0]

