from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticFinding, DiagnosticSummary
from pytest_diagnostics.rules.base import DiagnosticRule
from pytest_diagnostics.signals.models import DiagnosticSignal


class DiagnosticMatcher:
    def __init__(self, rules: list[DiagnosticRule]) -> None:
        self._rules = rules

    def match(self, signals: list[DiagnosticSignal], *, step_sequence=None) -> DiagnosticSummary:
        findings: list[DiagnosticFinding] = []
        for rule in self._rules:
            finding = rule.match(signals)
            if finding is not None:
                findings.append(finding)
        findings.sort(key=lambda item: item.confidence, reverse=True)
        return DiagnosticSummary(findings=findings, raw_signals=signals, step_sequence=step_sequence)
