from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticFinding
from pytest_diagnostics.rules.base import DiagnosticRule, has_signal
from pytest_diagnostics.signals.models import DiagnosticSignal


class AssertionMismatchRule(DiagnosticRule):
    name = "assertion_mismatch"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        if not has_signal(signals, "exception_type", "AssertionError"):
            return None
        return DiagnosticFinding(
            area="Data comparison",
            title="Assertion mismatch",
            explanation="Test failed with AssertionError.",
            confidence=0.45,
            facts=["test failed with AssertionError"],
            assumptions=[
                "actual and expected values are different",
                "values may differ by ordering",
                "stale data may be involved",
            ],
            recommended_checks=[
                "inspect compared values",
                "check ordering",
                "check whether data was updated during test",
            ],
            rule_name=self.name,
        )


class MissingFieldRule(DiagnosticRule):
    name = "missing_field"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        if not has_signal(signals, "exception_type", "KeyError"):
            return None
        return DiagnosticFinding(
            area="Data/schema",
            title="Missing expected field",
            explanation="Test failed with KeyError.",
            confidence=0.65,
            facts=["test failed with KeyError"],
            assumptions=[
                "expected field is missing",
                "response structure may have changed",
            ],
            recommended_checks=[
                "inspect response payload",
                "verify schema or fixture version",
                "check producer contract changes",
            ],
            rule_name=self.name,
        )

