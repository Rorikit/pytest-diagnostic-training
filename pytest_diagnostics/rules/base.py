from __future__ import annotations

from abc import ABC, abstractmethod

from pytest_diagnostics.core.models import DiagnosticHypothesis, TestDiagnosticContext


class DiagnosticRule(ABC):
    rule_id: str

    @abstractmethod
    def evaluate(self, context: TestDiagnosticContext) -> DiagnosticHypothesis | None:
        """Return a hypothesis when enough supporting evidence exists."""


def clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, round(value, 2)))

