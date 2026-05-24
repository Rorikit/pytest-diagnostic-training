from __future__ import annotations

from dataclasses import dataclass, field

from pytest_diagnostics.signals.models import DiagnosticSignal
from pytest_diagnostics.steps.sequence import StepSequence


@dataclass(slots=True, frozen=True)
class DiagnosticEvidence:
    description: str
    weight: float
    signal: DiagnosticSignal | None = None


@dataclass(slots=True, frozen=True)
class DiagnosticFinding:
    area: str
    title: str
    explanation: str
    confidence: float
    facts: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    recommended_checks: list[str] = field(default_factory=list)
    evidence: list[DiagnosticEvidence] = field(default_factory=list)
    rule_name: str = "unknown"


@dataclass(slots=True, frozen=True)
class DiagnosticSummary:
    findings: list[DiagnosticFinding]
    raw_signals: list[DiagnosticSignal]
    step_sequence: StepSequence | None = None

    @property
    def top_finding(self) -> DiagnosticFinding | None:
        if not self.findings:
            return None
        return self.findings[0]
